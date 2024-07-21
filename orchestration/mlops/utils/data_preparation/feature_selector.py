from typing import List, Tuple, Union

from pandas import DataFrame, Series


def select_features(df: DataFrame, columns: List) -> Union[DataFrame, Series]:
    """
    Select only passed columns

    Parameters:
    -----------
    df : DataFrame
        dataframe of interest

    columns : List
        columns to keep

    Returns:
    --------
    DataFrame
        same dataframe with needed columns only
    """
    if len(columns) == 1:
        return df[columns[0]]

    return df[columns]
