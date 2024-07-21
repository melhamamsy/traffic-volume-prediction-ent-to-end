import os
from typing import Callable, Dict, List, Tuple, Union

import boto3
import mlflow
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from numpy import sqrt
from pandas import DataFrame, Series
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor


class XGBoostFinetuner:
    def __init__(
        self,
        X_train: DataFrame,
        y_train: Series,
        X_val: DataFrame,
        y_val: Series,
        tracking_server_host: str,
        mlflow_experiment_name: str,
        feature_engineering_pipeline: Pipeline,
        max_evals: int,
        n_best_models: int,
        run_name: str = "hyperopt_xgb",
    ):

        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.space = {
            "n_estimators": hp.quniform("n_estimators", 100, 1000, 50),
            "max_depth": hp.quniform("max_depth", 3, 10, 1),
            "learning_rate": hp.loguniform("learning_rate", -3, 0),
            "subsample": hp.uniform("subsample", 0.5, 1),
            "colsample_bytree": hp.uniform("colsample_bytree", 0.5, 1),
            "gamma": hp.loguniform("gamma", -3, 0),
            "reg_alpha": hp.loguniform("reg_alpha", -3, 0),
            "reg_lambda": hp.loguniform("reg_lambda", -3, 0),
        }
        self.tracking_server_host = tracking_server_host
        self.mlflow_experiment_name = mlflow_experiment_name
        self.feature_engineering_pipeline = feature_engineering_pipeline
        self.n_best_models = n_best_models
        self.max_evals = max_evals
        self.best_models = []
        self.run_name = run_name

    # Define the objective function
    def objective(self, space):
        model = XGBRegressor(
            n_estimators=int(space["n_estimators"]),
            max_depth=int(space["max_depth"]),
            learning_rate=space["learning_rate"],
            subsample=space["subsample"],
            colsample_bytree=space["colsample_bytree"],
            gamma=space["gamma"],
            reg_alpha=space["reg_alpha"],
            reg_lambda=space["reg_lambda"],
            objective="reg:squarederror",
        )

        pipeline = Pipeline(
            steps=[
                ("feature_engineering", self.feature_engineering_pipeline),
                ("regressor", model),
            ]
        )

        pipeline.fit(self.X_train, self.y_train)
        preds = pipeline.predict(self.X_val)
        rmse = sqrt(mean_squared_error(self.y_val, preds))

        # Log parameters and metrics to MLflow
        with mlflow.start_run(nested=True):
            mlflow.log_params(space)
            mlflow.log_metric("rmse", rmse)

            # Save the model if it is one of the best
            if len(self.best_models) < self.n_best_models:
                self.best_models.append((rmse, pipeline, space))
            else:
                worst_rmse = max(self.best_models, key=lambda x: x[0])[0]
                if rmse < worst_rmse:
                    self.best_models.remove(max(self.best_models, key=lambda x: x[0]))
                    self.best_models.append((rmse, pipeline, space))

        return {"loss": rmse, "status": STATUS_OK}

    def finetune(
        self,
    ) -> Tuple[Pipeline, Pipeline, Pipeline]:

        mlflow.set_tracking_uri(f"http://{self.tracking_server_host}:5000")
        mlflow.set_experiment(self.mlflow_experiment_name)

        # Run the optimization
        trials = Trials()
        with mlflow.start_run(run_name=self.run_name) as run:
            best = fmin(
                fn=lambda space: self.objective(space),
                space=self.space,
                algo=tpe.suggest,
                max_evals=self.max_evals,
                trials=trials,
            )

        # Log the top {self.n_best_models} models
        for i, (rmse, pipeline, params) in enumerate(
            sorted(self.best_models, key=lambda x: x[0])
        ):
            with mlflow.start_run(run_name=f"best_model_{i+1}", nested=True):
                mlflow.log_params(params)
                mlflow.log_metric("rmse", rmse)
                mlflow.sklearn.log_model(pipeline, artifact_path=f"models")

        print("Best hyperparameters:", best)
        print(
            f"Access Top {self.n_best_models} performing models from object.best_models"
        )
