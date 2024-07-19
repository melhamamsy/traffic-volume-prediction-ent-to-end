from typing import List

import mlflow
from mlflow import register_model
from mlflow.sklearn import load_model
from mlflow.tracking import MlflowClient
from sklearn.pipeline import Pipeline


### implement register_model_mlflow
def register_model_mlflow(
    tracking_server_host: str,
    mlflow_experiment_name: str,
    run_name: str,
    name_to_register_with: str,
):

    client = MlflowClient(f"http://{tracking_server_host}:5000")
    experiment_id = client.get_experiment_by_name(mlflow_experiment_name).experiment_id
    

    run_id = client.search_runs(
        experiment_ids=[f'{experiment_id}'],
        filter_string = f'attribute.run_name = "{run_name}"'
    )[0].info.run_id

    ## TO implement read from s3 bucket directly instead
    model_uri = f"runs:/{run_id}/models"

    
    if not client.search_registered_models(
        filter_string=f"name='{name_to_register_with}'"
    ):
        print(f"Registering new model {name_to_register_with}")
        register_model(
            model_uri=model_uri,
            name=name_to_register_with
        )
    else:
        print(f"Model with name {name_to_register_with} is already registered...")
        print(f"Registering a new version to the model...")
        client.create_model_version(
            name=name_to_register_with, 
            source=model_uri, 
            run_id=run_id
        )


    print("Model was successfully registered...")


## return all models
def load_registered_model_mlflow(
    model_name: str,
    n_latest_models: int,
    mlflow_experiment_name: str,
    tracking_server_host: str,
    mlflow_bucket_name: str
) -> List[Pipeline]:

    client = MlflowClient(f"http://{tracking_server_host}:5000")

    versions = client.search_model_versions(f"name='{model_name}'")
    experiment_id = client.get_experiment_by_name(mlflow_experiment_name).experiment_id
    
    model_versions = []
    models = {}


    for version in versions:
        model_version = {
            "version": version.version,
            "run_id": version.run_id,
            "current_stage": version.current_stage,
            "status": version.status,
            "created_time": version.creation_timestamp,
            "last_updated_time": version.last_updated_timestamp
        }
        model_versions.append(model_version)

    model_versions = sorted(model_versions, key=lambda x: int(x['version']))[-n_latest_models:]

    for model_version in model_versions:
        model_uri = f"s3://{mlflow_bucket_name}/{experiment_id}/{model_version['run_id']}/artifacts/models"

        print("Model uri of version", model_version["version"], end=": ")
        print(model_uri)

        model = load_model(model_uri)
        models[model_version["version"]] = model

    return models


    
### implement remove_registered_model_mlflow