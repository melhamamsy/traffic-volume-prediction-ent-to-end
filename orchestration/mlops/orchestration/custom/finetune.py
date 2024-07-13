if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from pandas import DataFrame
from typing import List, Tuple
from sklearn.pipeline import Pipeline
from utils.hyperparameters.hyperparameters_tuning import XGBoostFinetuner


@custom
def transform(
    training_set: Tuple[DataFrame, DataFrame, Pipeline],
    *args, **kwargs) -> None:
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
    
    tracking_server_host = kwargs["TRACKING_SERVER_HOST"]
    mlflow_experiment_name = kwargs["MLFLOW_EXPERIMENT_NAME"]
    target_column = kwargs["TARGET"]

    
    df_train, df_val, feature_engineering_pipeline = training_set["export"]
    

    X_train = df_train.drop(
        ["uuid", target_column], axis = 1
    )
    y_train = df_train[target_column]

    X_val = df_val.drop(
        ["uuid", target_column], axis = 1
    )
    y_val = df_val[target_column]


    max_evals = kwargs["MAX_EVALS"]
    n_best_models = kwargs["N_BEST_MODELS"]

    
    if kwargs["IS_RUN_FINE_TUNING"].upper() in {"Y", "YES"}:
        xgboost_finetuner = XGBoostFinetuner(
            X_train, 
            y_train,
            X_val, 
            y_val,
            tracking_server_host,
            mlflow_experiment_name,
            feature_engineering_pipeline,
            max_evals,
            n_best_models
        )


        xgboost_finetuner.finetune()
        print("Successfully completed finetuning...")
    else:
        print("No finetuning is required...")

    return None
