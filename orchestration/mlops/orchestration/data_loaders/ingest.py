if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
# get_aws_credentials=None
import os
from utils.utils.credentials import get_aws_credentials
import boto3
from pandas import DataFrame, read_csv, to_datetime
from numpy import int64



@data_loader
def load_data(*args, **kwargs) -> DataFrame:
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    bucket_name = kwargs["BUCKET_NAME"]
    file_path = kwargs["FILE_PATH"]
    
    s3_file_url = f's3://{bucket_name}/{file_path}'

    # Read the CSV file directly into a pandas DataFrame
    df = read_csv(
        s3_file_url, storage_options=get_aws_credentials()
    )
    
    # For plotting only, will be dropped in transformation step
    date_time_column = kwargs["DATE_TIME"]
    df[f'{date_time_column}_float'] = to_datetime(df[f'{date_time_column}']).astype(int64) // 10**9

    
    return df


@test
def test_output(
    output: DataFrame, 
    *args
) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'