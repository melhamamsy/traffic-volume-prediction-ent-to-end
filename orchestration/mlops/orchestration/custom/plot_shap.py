if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from typing import Tuple
from utils.models.model_registry import load_registered_model_mlflow
from utils.utils.plotting import plot_shap_summary_plot


@custom
def transform_custom(
    data,
    _,
    *args, **kwargs
) -> None:
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your custom logic here
    n_best_models = kwargs['N_BEST_MODELS']
    
    registered_model_name = kwargs['name_to_register_with']
    model_version_ids = [str(i+1) for i in range(n_best_models)]
    mlflow_experiment_name = kwargs['MLFLOW_EXPERIMENT_NAME']
    tracking_server_host = kwargs['TRACKING_SERVER_HOST']
    mlflow_bucket_name = kwargs['MLFLOW_BUCKET_NAME']


    if kwargs['IS_PLOT_SHAP'].upper() in {"Y", "YES"}:
        pipelines = load_registered_model_mlflow(
            model_name = registered_model_name,
            model_version_ids = model_version_ids,
            mlflow_experiment_name = mlflow_experiment_name,
            tracking_server_host = tracking_server_host,
            mlflow_bucket_name = mlflow_bucket_name
        ) 

        
        df_train = data["export"][0]

        ## plotting in pipeline instead of dashboard because of issues faced in 
        ##  using dashboard
        plot_shap_summary_plot(
            df_train,
            pipelines,
            frac = 1
        )
    else:
        print("No shap plotting is required...")

    
    return None