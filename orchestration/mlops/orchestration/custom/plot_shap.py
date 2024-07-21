if "custom" not in globals():
    from mage_ai.data_preparation.decorators import custom
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


from mlops.utils.utils.plotting import plot_shap_summary_plot


@custom
def transform_custom(data, pipelines, *args, **kwargs) -> None:
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    df_train = data["export"][0]

    if kwargs["IS_PLOT_SHAP"].upper() in {"Y", "YES"}:
        ## plotting in pipeline instead of dashboard because of issues faced in
        ##  using dashboard
        plot_shap_summary_plot(df_train, pipelines, frac=1)
    else:
        print("No shap plotting is required...")

    return None
