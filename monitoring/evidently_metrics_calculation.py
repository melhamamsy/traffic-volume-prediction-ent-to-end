import warnings; warnings.simplefilter("ignore")

import datetime
import time
import logging 
import pandas as pd
import psycopg
from psycopg.errors import UniqueViolation
from mlflow.sklearn import load_model

from utils.data_preparation.cleaning import correct_dtypes, remove_duplicates
from utils.data_preparation.feature_selector import select_features

import os

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metric_preset import TargetDriftPreset
from evidently.metrics import (
    ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 2
STATTEST_THRESHOLD = 1.5


########################################### Model pipeline ############################################
logged_model_s3 ="s3://mlflow-artifacts-melhamamsy/2/c6343316f0c64d0ea822e39d8820e3db/artifacts/models"
logged_model = "./models"
pipeline = load_model(logged_model)
#######################################################################################################


########################################### SQL statements ###########################################
create_table_statements = """
drop table if exists models cascade;
create table models(
    id serial primary key,
    creation_timestamp timestamp,
    name varchar(100),
    path varchar(200)
);

drop table if exists metrics;
create table metrics(
    timestamp timestamp,
    model_id int,
    prediction_drift float,
    target_drift float,
    num_drifted_columns integer,
    share_missing_values float,
    primary key (timestamp, model_id),
    foreign key (model_id) references models(id)
);
"""
insert_model_statements=f"""
insert into models (creation_timestamp, name, path)
values (
	'2017-01-01 00:00:00', 
	'traffic-volume-predictor', 
	'{logged_model_s3}'
);
"""
#######################################################################################################


########################################### Reference Data ############################################
dataframes = []
data_dir_path = os.path.join(os.getcwd(),"data/raw/")
for year in [2012, 2013, 2016]:
    file_path =\
		data_dir_path+\
			f"Metro_Interstate_Traffic_Volume_{year}.csv"
    dataframes.append(
		pd.read_csv(file_path)
	)
reference_data = pd.concat(dataframes, ignore_index=True)
del dataframes
#######################################################################################################


########################################### Current Data ############################################
dataframes = []
data_dir_path = os.path.join(os.getcwd(),"data/raw/")
for year in [2017, 2018]:
    file_path =\
		data_dir_path+\
			f"Metro_Interstate_Traffic_Volume_{year}.csv"
    dataframes.append(
		pd.read_csv(file_path)
	)
current_data_pool = pd.concat(dataframes, ignore_index=True)
del dataframes
#######################################################################################################


############################################# Prepare Data ############################################
COLUMNS = [
    'holiday', 'temp', 'rain_1h', 'snow_1h', 
    'clouds_all', 'weather_main','date_time', 'traffic_volume'
]
DATE_TIME_COLUMN = "date_time"
TARGET = "traffic_volume"
PREDICTION = "prediction"


def prepare_data(
    df,
) -> pd.DataFrame:
	df = select_features(df, COLUMNS)
	df = remove_duplicates(df)
	df = correct_dtypes(df, date_time_column=DATE_TIME_COLUMN)

	date_time_series = df[DATE_TIME_COLUMN]
	target_series = df[TARGET]
	pred_series =\
		pipeline.predict(df.drop(TARGET, axis=1))
	
	df = pipeline["feature_engineering"][0].transform(
		df.drop(TARGET, axis=1)
	)

	df[DATE_TIME_COLUMN] = date_time_series
	df[PREDICTION] = pred_series
	df[TARGET] = target_series
    
	return df

reference_data = prepare_data(reference_data)
current_data_pool = prepare_data(current_data_pool)
#######################################################################################################


########################################## Evidently Report ###########################################
num_features = ["temp", "rain_1h", "snow_1h", "clouds_all"]
cat_features = ["holiday", "hour", "month", "day_of_week"]

column_mapping = ColumnMapping(
    target=TARGET,
    prediction=PREDICTION,
    numerical_features=num_features,
    categorical_features=cat_features
)
#######################################################################################################


########################################### Prepare Database ##########################################
def prep_db():
	with psycopg.connect(
		"host=localhost port=5432 user=postgres password=example", autocommit=True) as conn:
		res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
		if len(res.fetchall()) == 0:
			conn.execute("create database test;")
			with psycopg.connect(
				"host=localhost port=5432 dbname=test user=postgres password=example") as conn:
				conn.execute(create_table_statements)
				conn.execute(insert_model_statements)
#######################################################################################################


########################################### Populate metrics ##########################################
def calculate_metrics_postgresql(curr, start_date, end_date, model_id):
	report = Report(
		metrics=[
			ColumnDriftMetric(column_name=PREDICTION, stattest_threshold=STATTEST_THRESHOLD),
			ColumnDriftMetric(column_name=TARGET, stattest_threshold=STATTEST_THRESHOLD),
			DatasetDriftMetric(stattest_threshold=STATTEST_THRESHOLD),
			DatasetMissingValuesMetric()
		]
	)
	
	current_data = current_data_pool.loc[
		current_data_pool[DATE_TIME_COLUMN].between(
			start_date, end_date, inclusive="left"
		)
	]


	report.run(reference_data = reference_data, current_data = current_data,
		column_mapping=column_mapping)

	result = report.as_dict()



	prediction_drift = result['metrics'][0]['result']['drift_score']
	target_drift = result['metrics'][1]['result']['drift_score']
	num_drifted_columns = result['metrics'][2]['result']['number_of_drifted_columns']
	share_missing_values = result['metrics'][3]['result']['current']['share_of_missing_values']


	preview_date = end_date + pd.DateOffset(years=5)
	end_date_str = preview_date.strftime('%Y-%m-%d %H:%M:%S')
	
	try:
		curr.execute(
		f"""insert into metrics(
			timestamp,
			model_id,
			prediction_drift,
			target_drift,
			num_drifted_columns,
			share_missing_values
		) 
		values (
			'{end_date_str}',
			'{model_id}',
			'{prediction_drift}',
			'{target_drift}',
			'{num_drifted_columns}',
			'{share_missing_values}'
		)
		"""
		)
	except UniqueViolation  as e:
		print(f"Unique constraint violation: {e}")
		print("Continuing...")

#######################################################################################################


########################################### Prepare Database ##########################################
START_DATE = pd.to_datetime('2017-01-01')
END_DATE = pd.to_datetime('2018-10-01')
REPORT_SPAN = 14 #days

def batch_monitoring_backfill():
	prep_db()
	last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
	start_date = START_DATE
	
	with psycopg.connect(
		"host=localhost port=5432 dbname=test user=postgres password=example", autocommit=True) as conn:
		
		## select model_id
		with conn.cursor() as curr:
			curr.execute(f"SELECT id FROM models WHERE path='{logged_model_s3}'")
			model_id = int(curr.fetchone()[0])


		while start_date < END_DATE:
			end_date = start_date + pd.Timedelta(days=REPORT_SPAN)
			if end_date > END_DATE:
				end_date = END_DATE

			with conn.cursor() as curr:
				calculate_metrics_postgresql(curr, start_date, end_date, model_id)

			start_date = end_date

			new_send = datetime.datetime.now()
			seconds_elapsed = (new_send - last_send).total_seconds()
			if seconds_elapsed < SEND_TIMEOUT:
				time.sleep(SEND_TIMEOUT - seconds_elapsed)
			while last_send < new_send:
				last_send = last_send + datetime.timedelta(seconds=10)


			logging.info("data sent")





#######################################################################################################


if __name__ == '__main__':
	batch_monitoring_backfill()