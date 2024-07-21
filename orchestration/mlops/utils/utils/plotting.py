from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import shap
from pandas import DataFrame
from sklearn.pipeline import Pipeline


def plot_shap_summary_plot(
    x: DataFrame, pipelines: Dict[str, Pipeline], frac: float
) -> None:
    try:
        x = x.drop(["traffic_volume", "uuid"], axis=1)
    except:
        pass

    ## Shuffle df
    x = x.sample(frac=frac).reset_index(drop=True)

    x = pipelines["1"]["feature_engineering"].transform(x)

    # Create a SHAP explainer based on the model and the data
    for version, pipeline in pipelines.items():
        print(
            "\n" * 5,
            "=" * 30,
            f" Plotting Shap Values for model with version {version} ",
            "=" * 30,
            sep="",
        )

        explainer = shap.Explainer(pipeline["regressor"], x)
        shap_values = explainer(x)

        # Summary plot
        shap.summary_plot(shap_values, x)

        plt.close()
