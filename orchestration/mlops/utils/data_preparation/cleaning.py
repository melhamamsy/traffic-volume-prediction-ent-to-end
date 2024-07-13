from pandas import DataFrame, to_datetime


def correct_dtypes(
    df: DataFrame,
    **kwargs
) -> DataFrame:
    """
    Correct dtypes of the columns of the DataFrame
    """

    data_time_column = kwargs["date_time_column"]
    df[data_time_column] = to_datetime(df[data_time_column])

    df["temp"] = df["temp"].astype(float)
    df["rain_1h"] = df["temp"].astype(float)
    df["snow_1h"] = df["temp"].astype(float)
    df["clouds_all"] = df["temp"].astype(float)

    return df


def remove_duplicates(
    df: DataFrame,
) -> DataFrame:
    """
    Drops duplicates of the DataFrame
    """

    return df.drop_duplicates(keep='last').reset_index(drop=True)