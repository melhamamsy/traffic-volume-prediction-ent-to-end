import os
from typing import Dict

import mlflow
from flask import Flask, jsonify, request
from pandas import DataFrame, to_datetime

RUN_ID = "c6343316f0c64d0ea822e39d8820e3db"
MLFLOW_BUCKET_NAME = "mlflow-artifacts-melhamamsy"
EXPERIMENT_ID = "2"

os.environ["AWS_PROFILE"] = "test-mlops"

## Load model from s3
# logged_model = f"s3://{MLFLOW_BUCKET_NAME}/{EXPERIMENT_ID}/{RUN_ID}/artifacts/models"

## Load model from local dir after running download-model.sh
logged_model = "./models"


pipeline = mlflow.pyfunc.load_model(logged_model)


def correct_dtypes(traffic: Dict) -> Dict:
    """
    Correct dtypes of the columns of the DataFrame
    """
    traffic["date_time"] = to_datetime(traffic["date_time"])

    traffic["temp"] = float(traffic["temp"])
    traffic["rain_1h"] = float(traffic["rain_1h"])
    traffic["snow_1h"] = float(traffic["snow_1h"])
    traffic["clouds_all"] = float(traffic["clouds_all"])

    return DataFrame([traffic])


def prepare_features(traffic):
    features = correct_dtypes(traffic)
    return features


def predict(features):
    return float(pipeline.predict(features)[0].round(3))


app = Flask("traffic-volume-prediction")


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    traffic = request.get_json()

    pred = predict(prepare_features(traffic))

    result = {"traffic-volume": pred, "model_version": RUN_ID}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
