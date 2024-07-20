import os
import pytest
import mlflow
from sklearn.pipeline import Pipeline
from pandas import DataFrame, Series, to_datetime

from orchestration.mlops.utils.data_preparation.cleaning import correct_dtypes, remove_duplicates
from orchestration.mlops.utils.data_preparation.encoders import DictVectorizerTransformer
from orchestration.mlops.utils.data_preparation.feature_engineering import FeatureEngineeringTransformer
from orchestration.mlops.utils.data_preparation.feature_selector import select_features
from orchestration.mlops.utils.data_preparation.splitters import split_on_date_time

from orchestration.mlops.utils.hyperparameters.hyperparameters_tuning import XGBoostFinetuner

from orchestration.mlops.utils.models.model_registry import load_registered_model_mlflow, register_model_mlflow



### orchestration.mlops.utils.data_preparation
def test_correct_dtypes():
    """
        Testing returned dtypes of correct_dtypes function
    """
    expected_dtypes = {
        'holiday': 'object',
        'temp': 'float64',
        'rain_1h': 'float64',
        'snow_1h': 'float64',
        'clouds_all': 'float64',
        'weather_main': 'object',
        'date_time': 'datetime64[ns]',
        'traffic_volume': 'int64'
    }

    data_example = DataFrame([{
        'holiday': "None",
        'temp': "288.28",
        'rain_1h': "0.0",
        'snow_1h': "0.0",
        'clouds_all': "40",
        'weather_main': 'Clouds',
        'date_time': '2012-10-02 09:00:00',
        'traffic_volume': 5545
    }])

    corrected_example = correct_dtypes(data_example, date_time_column="date_time")
    actual_dtypes = {col: dtype.name for col, dtype in corrected_example.dtypes.items()}


    assert actual_dtypes == expected_dtypes, "Incorrect Input dtypes"

def test_remove_duplicates():
    """
        Test if there are any duplicates after applying remove_duplicates function
    """
    data_example = DataFrame([
        {
            'holiday': "None",
            'temp': "288.28",
            'rain_1h': "0.0",
            'snow_1h': "0.0",
            'clouds_all': "40",
            'weather_main': 'Clouds',
            'date_time': '2012-10-02 09:00:00',
            'traffic_volume': 5545
        },
        {
            'holiday': "None",
            'temp': "288.28",
            'rain_1h': "0.0",
            'snow_1h': "0.0",
            'clouds_all': "40",
            'weather_main': 'Clouds',
            'date_time': '2012-10-02 09:00:00',
            'traffic_volume': 5545
        }
    ])

    modified_example = remove_duplicates(data_example)

    assert not modified_example.duplicated().any(), "Duplicate rows are found."

def test_dict_vectorizer_transformer_in_pipeline():
    weather_main_examples = ['Clear', 'Clouds', 'Rain']
    data_example = DataFrame([
        {
            'holiday': "None",
            'temp': "288.28",
            'rain_1h': "0.0",
            'snow_1h': "0.0",
            'clouds_all': "40",
            'weather_main': weather_main_example,
            'date_time': '2012-10-02 09:00:00'
        } for weather_main_example in weather_main_examples
    ])

    pipeline = Pipeline([
        ('dict_vectorizer', DictVectorizerTransformer(sparse=False))
    ])
    
    pipeline.fit(data_example)
    transformed_df = pipeline.transform(data_example)
    
    expected_columns = [
        'holiday', 'temp', 'rain_1h', 'snow_1h', 'clouds_all', 'date_time',
        'weather_main=Clear', 'weather_main=Clouds', 'weather_main=Rain'
    ]
    actual_columns = transformed_df.columns.tolist()

    print(actual_columns)
    print(expected_columns)
    
    assert actual_columns == expected_columns

def test_feature_engineering_transformer_in_pipeline():
    data_example = DataFrame({
        'date_time': to_datetime(['2021-12-01 00:00:00', '2021-12-25 12:00:00', '2021-12-31 23:59:00']),
        'holiday': ['None', 'Christmas', 'None'],
        'weather_main': ['Clear', 'Clouds', 'Fog'],
        'temp': [25.0, 30.0, 28.0],
        'humidity': [45, 50, 48]
    })

    pipeline = Pipeline([
        ('feature_engineering', FeatureEngineeringTransformer())
    ])

    pipeline.fit(data_example)
    transformed_df = pipeline.transform(data_example)
    
    expected_columns = ['holiday', 'weather_main', 'temp', 'humidity', 'hour', 'month', 'day_of_week']
    actual_columns = transformed_df.columns.tolist()
    
    assert actual_columns == expected_columns
    
    # Check that 'date_time' column is dropped
    assert 'date_time' not in actual_columns
    
    # Check transformed values
    assert transformed_df['holiday'].tolist() == [0, 1, 0]
    assert transformed_df['weather_main'].tolist() == ['Clear', 'Clouds', 'Fog_Smoke_Squall']
    assert transformed_df['hour'].tolist() == [0, 12, 23]
    assert transformed_df['month'].tolist() == [12, 12, 12]
    assert transformed_df['day_of_week'].tolist() == [2, 5, 4]

def test_select_features():
    sample_dataframe = DataFrame({
        'col1': [1, 2, 3],
        'col2': [4, 5, 6],
        'col3': [7, 8, 9]
    })

    # Test with multiple columns
    columns_to_select = ['col1', 'col2']
    result = select_features(sample_dataframe, columns_to_select)
    expected_columns = ['col1', 'col2']
    actual_columns = result.columns.tolist()
    assert actual_columns == expected_columns
    assert result.shape == (3, 2)

    # Test with a single column
    columns_to_select = ['col1']
    result = select_features(sample_dataframe, columns_to_select)
    assert isinstance(result, Series)
    assert result.name == 'col1'
    assert result.tolist() == [1, 2, 3]

    # Test with no columns
    columns_to_select = []
    result = select_features(sample_dataframe, columns_to_select)
    assert result.empty

def test_split_on_date_time():
    sample_dataframe = DataFrame({
        'date_time': to_datetime(['2020-01-01', '2021-01-01', '2022-01-01']),
        'value': [10, 20, 30]
    })

    # Test split with dropping the feature
    df_train, df_val = split_on_date_time(sample_dataframe, 'date_time', 2021, drop_feature=True, return_indexes=False)
    assert df_train.equals(sample_dataframe[sample_dataframe['date_time'].dt.year < 2021].drop(columns=['date_time']))
    assert df_val.equals(sample_dataframe[sample_dataframe['date_time'].dt.year >= 2021].drop(columns=['date_time']))

    # Test split without dropping the feature
    df_train, df_val = split_on_date_time(sample_dataframe, 'date_time', 2021, drop_feature=False, return_indexes=False)
    assert df_train.equals(sample_dataframe[sample_dataframe['date_time'].dt.year < 2021])
    assert df_val.equals(sample_dataframe[sample_dataframe['date_time'].dt.year >= 2021])

    # Test split with returning indexes
    train_index, val_index = split_on_date_time(sample_dataframe, 'date_time', 2021, drop_feature=False, return_indexes=True)
    expected_train_index = sample_dataframe[sample_dataframe['date_time'].dt.year < 2021].index
    expected_val_index = sample_dataframe[sample_dataframe['date_time'].dt.year >= 2021].index
    assert train_index.equals(expected_train_index)
    assert val_index.equals(expected_val_index)

### orchestration.mlops.utils.hyperparameters_tuning
@pytest.mark.usefixtures("reset_tracking_uri")
def test_xgboost_finetuner_in_pipeline():
    """
    Test the XGBoostFinetuner class finetuner.
    mlflow attributes are defined in conftest.py
    """
    X_train = DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [5, 4, 3, 2, 1]
    })
    y_train = Series([1, 2, 3, 4, 5])
    X_val = DataFrame({
        'feature1': [6, 7, 8, 9, 10],
        'feature2': [10, 9, 8, 7, 6]
    })
    y_val = Series([6, 7, 8, 9, 10])


    max_evals = 2
    n_best_models = 1
    run_name = 'hyperopt_xgb'
    tracking_server_host = 'ec2-13-60-24-194.eu-north-1.compute.amazonaws.com'
    mlflow_experiment_name = 'testing_experiment'
    

    finetuner = XGBoostFinetuner(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        tracking_server_host=tracking_server_host,
        mlflow_experiment_name=mlflow_experiment_name,
        feature_engineering_pipeline='passthrough',
        max_evals=max_evals,
        n_best_models=n_best_models,
        run_name=run_name
    )

    finetuner.finetune()


    # Check if the best models list is populated
    assert len(finetuner.best_models) == n_best_models
    assert isinstance(finetuner.best_models[0][1], Pipeline)


    # tracking server and experiment
    os.environ['AWS_PROFILE'] = 'test-mlops'
    mlflow.set_tracking_uri(f"http://{tracking_server_host}:5000")
    mlflow.set_experiment(mlflow_experiment_name)

    # Additional assertions to check MLflow experiment and runs
    assert mlflow_experiment_name in [experiment.name for experiment in mlflow.search_experiments()]

    # Assert runs
    runs = mlflow.search_runs(experiment_ids=[mlflow.get_experiment_by_name(mlflow_experiment_name).experiment_id])
    run_names =\
        [run.get('tags.mlflow.runName', 'Unnamed run') for index, run in runs.iterrows()]
    best_run_names = [x for x in run_names if x[:10] == 'best_model']
    hyperopt_run_names = [x for x in run_names if x not in best_run_names and x != run_name]
    
    actual_best_model_count = len(best_run_names)
    expected_best_model_count = n_best_models

    actual_hyperopt_runs_count = len(hyperopt_run_names)
    expected_hyperopt_runs_count = max_evals

    assert actual_best_model_count == expected_best_model_count
    assert actual_hyperopt_runs_count == expected_hyperopt_runs_count

### orchestration.mlops.utils.hyperparameters_tuning
@pytest.mark.usefixtures("set_tracking_uri")
def test_register_load_model_mlflow():
    n_best_models = 1


    tracking_server_host = 'ec2-13-60-24-194.eu-north-1.compute.amazonaws.com'
    mlflow_experiment_name = 'testing_experiment'

    name_to_register_with = 'test_model'
    mlflow_bucket_name = "mlflow-artifacts-melhamamsy"

    for i in range(n_best_models):
        run_name = f"best_model_{i+1}"
        register_model_mlflow(
            tracking_server_host,
            mlflow_experiment_name,
            run_name,
            name_to_register_with
        )

    pipelines = load_registered_model_mlflow(
        model_name = name_to_register_with,
        n_latest_models = n_best_models,
        mlflow_experiment_name = mlflow_experiment_name,
        tracking_server_host = tracking_server_host,
        mlflow_bucket_name = mlflow_bucket_name
    ) 

    for i in range(n_best_models):
        assert isinstance(pipelines["i"], Pipeline)

    
