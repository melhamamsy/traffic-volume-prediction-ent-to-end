"""
Create a function to split on date_time
"""


from typing import Tuple, Union

from pandas import DataFrame, Index


def split_on_date_time(
    df: DataFrame,
    feature: str,
    year: Union[int, str],
    drop_feature: bool = True,
    return_indexes: bool = False,
) -> Union[Tuple[DataFrame, DataFrame], Tuple[Index, Index]]:
    df_train = df[
        (df[feature].apply(lambda x: x.year) < int(year))
    ]
    df_val = df[
        (df[feature].apply(lambda x: x.year) >= int(year))
    ]

    if return_indexes:
        return df_train.index, df_val.index

    if drop_feature:
        df_train = df_train.drop(columns=[feature])
        df_val = df_val.drop(columns=[feature])

    return df_train, df_val
