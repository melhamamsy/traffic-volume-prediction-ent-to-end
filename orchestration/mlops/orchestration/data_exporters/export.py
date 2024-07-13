if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from pandas import DataFrame
from typing import List, Tuple
from sklearn.pipeline import Pipeline
from utils.data_preparation.feature_engineering import FeatureEngineeringTransformer
from utils.data_preparation.encoders import DictVectorizerTransformer
from utils.data_preparation.splitters import split_on_date_time



@data_exporter
def export_data(
    df, *args, **kwargs
) -> Tuple[DataFrame, DataFrame, Pipeline]:
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """

    # Create the feature engineering pipeline
    # Not required to fit here as it would be part of the whole pipeline & fit in 1 call
    feature_engineering_pipeline = Pipeline(steps=[
        ('feature_engineering', FeatureEngineeringTransformer()),
        ('vectorizer', DictVectorizerTransformer(False)),
    ])

    # Split into training & validation data
    df_train, df_val = split_on_date_time(
        df = df,
        feature = kwargs["DATE_TIME"],
        year = 2016,
        drop_feature = False, #required in feature engineering class
        return_indexes = False,
    ) 

    return df_train, df_val, feature_engineering_pipeline


@test
def test_returned_data_frames_lengths(
    df_train: DataFrame, 
    df_val: DataFrame, 
    *args, **kwargs
) -> None:
    assert df_train.__len__() + df_val.__len__() == 29426, "wrong total observations"

@test
def test_returned_data_frames_columns(
    df_train: DataFrame, 
    df_val: DataFrame, 
    *args, **kwargs
) -> None:

    columns = kwargs["COLUMNS"].split(",") + [kwargs["TARGET"]] + [kwargs["DATE_TIME"]]  + ["uuid"] 
    assert list(df_train.columns) == list(df_val.columns) == columns, "Wrong columns representation" 


@test
def test_feature_engineering_pipeline(
    df_train: DataFrame, 
    df_val: DataFrame, 
    feature_engineering_pipeline: Pipeline,
    *args, **kwargs
) -> None:
    
    # Fit the pipeline with the training data
    feature_engineering_pipeline.fit(
        df_train.drop(kwargs["TARGET"], axis=1), df_train[kwargs["TARGET"]]
    )

    columns = kwargs["COLUMNS"].split(",") + ["uuid"] + ['hour', 'month', 'day_of_week']
    weather_main_vals = [
        "Clear",
        "Clouds",
        "Drizzle",
        "Fog_Smoke_Squall",
        "Haze",
        "Mist",
        "Rain",
        "Snow",
        "Thunderstorm"
    ]  

    columns = columns + [
        f"weather_main={x}" for x in weather_main_vals
    ]
    columns.remove("weather_main")

    # Transform on the dev data
    x_val = feature_engineering_pipeline.transform(
        df_val.drop(kwargs["TARGET"], axis=1),
    )


    assert x_val.__len__() == df_val.__len__()
    assert list(x_val.columns) == columns, "after transformation column mismatch"