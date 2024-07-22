if "custom" not in globals():
    from mage_ai.data_preparation.decorators import custom
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test

import os
import sys

project_root = os.path.join(os.getcwd(), "mlops")
# Check if the project root is already in sys.path, and add it if not
if project_root not in sys.path:
    sys.path.append(project_root)


from typing import Dict

from mlops.utils.models.model_registry import (
    load_registered_model_mlflow,
    register_model_mlflow,
)
from sklearn.pipeline import Pipeline


@custom
def transform_custom(*args, **kwargs) -> Dict[str, Pipeline]:
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    os.environ["AWS_PROFILE"] = kwargs["AWS_PROFILE"]

    n_best_models = kwargs["N_BEST_MODELS"]

    tracking_server_host = kwargs["TRACKING_SERVER_HOST"]
    mlflow_experiment_name = kwargs["MLFLOW_EXPERIMENT_NAME"]
    name_to_register_with = kwargs["name_to_register_with"]
    mlflow_bucket_name = kwargs["MLFLOW_BUCKET_NAME"]

    if kwargs["IS_REGISTER_MODELS"].upper() in {"Y", "YES"}:
        for i in range(n_best_models):
            run_name = f"best_model_{i+1}"
            register_model_mlflow(
                tracking_server_host,
                mlflow_experiment_name,
                run_name,
                name_to_register_with,
            )
    else:
        print("No registration is required...")

    pipelines = load_registered_model_mlflow(
        model_name=name_to_register_with,
        n_latest_models=n_best_models,
        mlflow_experiment_name=mlflow_experiment_name,
        tracking_server_host=tracking_server_host,
        mlflow_bucket_name=mlflow_bucket_name,
    )

    return pipelines
