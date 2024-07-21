if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test

from mlops.utils.data_preparation.cleaning import (correct_dtypes,
                                                   remove_duplicates)
from mlops.utils.data_preparation.feature_selector import select_features
from mlops.utils.utils.uuid import create_uuid_col


@transformer
def transform(df, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """

    columns = kwargs["COLUMNS"].split(",")
    target = kwargs["TARGET"]
    date_time_column = kwargs["DATE_TIME"]
    columns_to_select = columns + [target, date_time_column]  # also used to create uuid

    # Correct dtypes
    df = correct_dtypes(df, date_time_column=date_time_column)

    # Select features
    df = select_features(df=df, columns=columns_to_select)

    # Remove duplicates
    df = remove_duplicates(df)

    # Create unique uuid
    df = create_uuid_col(df=df, columns=columns_to_select)

    return df


@test
def test_uuid_uniqueness(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output["uuid"].is_unique, "uuid is not unique"


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
