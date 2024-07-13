if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from utils.models.model_registry import register_model_mlflow

@custom
def transform_custom(*args, **kwargs) -> None:
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your custom logic here
    tracking_server_host = kwargs['TRACKING_SERVER_HOST']
    mlflow_experiment_name = kwargs['MLFLOW_EXPERIMENT_NAME']
    name_to_register_with = kwargs['name_to_register_with']
    n_best_models = kwargs['N_BEST_MODELS']


    if kwargs["IS_REGISTER_MODELS"].upper() in {"Y", "YES"}:
        for i in range(n_best_models):
            run_name = f"best_model_{i+1}"
            register_model_mlflow(
                tracking_server_host,
                mlflow_experiment_name,
                run_name,
                name_to_register_with
            )
    else:
        print("No registration is required...")



    return None