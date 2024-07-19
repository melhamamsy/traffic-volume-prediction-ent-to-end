if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import os
from mlops.utils.utils.credentials import get_aws_credentials
import boto3
from pandas import DataFrame, read_csv, to_datetime, concat
from numpy import int64



@data_loader
def load_data(*args, **kwargs) -> DataFrame:
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    aws_profile = kwargs['AWS_PROFILE']
    os.environ['AWS_PROFILE'] = kwargs['AWS_PROFILE']
    
    bucket_name = kwargs["BUCKET_NAME"]
    file_path_prefix = kwargs["FILE_PATH_PREFIX"]
    
    dfs = []
    for year in [2012, 2013, 2014, 2015, 2016]:
        s3_file_url = f's3://{bucket_name}/{file_path_prefix}_{year}.csv'

        # Read the CSV file directly into a pandas DataFrame
        dfs.append(
            read_csv(
                s3_file_url
                , storage_options={'profile': aws_profile}
            )
        )

        print(f"Successfully loaded {year} data.")

    df = concat(dfs, ignore_index=True); del dfs
    
    # For plotting only, will be dropped in transformation step
    date_time_column = kwargs["DATE_TIME"]
    df[f'{date_time_column}_float'] = to_datetime(df[f'{date_time_column}']).astype(int64) // 10**9

    print(df[date_time_column].str[:4].value_counts())
    
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