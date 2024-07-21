from mage_ai.orchestration.triggers.api import trigger_pipeline

if "custom" not in globals():
    from mage_ai.data_preparation.decorators import custom
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


@custom
def retrain(*args, **kwargs) -> None:
    """
    Retrain xgboost pipeline if sensor output is true
    """

    variables = {
        "IS_RUN_FINE_TUNING": "Y",
        "IS_REGISTER_MODELS": "Y",
        "IS_PLOT_SHAP": "Y",
    }

    trigger_pipeline(
        "xgboost_training",
        variables=variables,
        check_status=True,
        error_on_failure=True,
        schedule_name="Automatic retraining for xgboost models",
        verbose=True,
    )

    return None
