import uuid
from typing import List

import pandas as pd


def generate_uuid(
    row: pd.Series,
    namespace_uuid: uuid.UUID,
) -> uuid.UUID:
    """
    Takes a pd.DataFrame row and returns a unique uuid for that row
    """
    row_str = ",".join(map(str, row.values))
    return str(uuid.uuid5(namespace_uuid, row_str))


def create_uuid_col(df: pd.DataFrame, columns: List) -> pd.DataFrame:
    # Generate a namespace UUID dynamically based on column names
    namespace_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, "".join(columns))

    df["uuid"] = df.apply(generate_uuid, namespace_uuid=namespace_uuid, axis=1)

    return df
