if "sensor" not in globals():
    from mage_ai.data_preparation.decorators import sensor

import os

from mlops.utils.utils.data_state import check_for_new_data


@sensor
def check_condition(*args, **kwargs) -> bool:
    """
    Template code for checking if block or pipeline run completed.
    """
    os.environ["AWS_PROFILE"] = kwargs["AWS_PROFILE"]

    bucket_name = kwargs["BUCKET_NAME"]
    state_file = kwargs["STATE_FILE"]  ## File in orchestration dir to store last state

    return check_for_new_data(bucket_name, state_file)
