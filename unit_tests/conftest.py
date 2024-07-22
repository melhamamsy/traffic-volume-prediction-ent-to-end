import os
import sys

import mlflow
import pytest
from mlflow.tracking import MlflowClient

parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_path)
sys.path.append(os.path.join(parent_path, "orchestration"))
sys.path.append(os.path.join(parent_path, "orchestration/mlops"))
sys.path.append(os.path.join(parent_path, "deployment"))

tracking_server_host = "ec2-16-170-228-131.eu-north-1.compute.amazonaws.com"
experiment_name = "testing_experiment"


@pytest.fixture(scope="session")
def set_tracking_uri():
    os.environ["AWS_PROFILE"] = "test-mlops"

    mlflow.set_tracking_uri(f"http://{tracking_server_host}:5000")
    print("Tracking URI set to:", mlflow.get_tracking_uri())

    try:
        experiment_id = mlflow.create_experiment(experiment_name)
        print(f"Created experiment '{experiment_name}' with ID {experiment_id}")
    except mlflow.exceptions.MlflowException as e:
        if "RESOURCE_ALREADY_EXISTS" in str(e):
            print(f"Experiment '{experiment_name}' already exists.")
            experiment = mlflow.get_experiment_by_name(experiment_name)
            experiment_id = experiment.experiment_id
            print(f"Existing experiment ID: {experiment_id}")
        else:
            raise e

    mlflow.set_experiment(experiment_name)
    print(f"Set experiment to '{experiment_name}' with ID {experiment_id}")
    return experiment_id


@pytest.fixture(scope="function")
def cleanup_runs():
    os.environ["AWS_PROFILE"] = "test-mlops"

    mlflow.set_experiment(experiment_name)
    mlflow.set_tracking_uri(f"http://{tracking_server_host}:5000")

    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment:
        experiment_id = experiment.experiment_id
        runs = mlflow.search_runs(experiment_ids=[experiment_id])
        for _, run in runs.iterrows():
            run_id = run["run_id"]
            mlflow.delete_run(run_id)
            print(f"Deleted run with ID: {run_id}")


@pytest.fixture(scope="function")
def cleanup_registry():
    os.environ["AWS_PROFILE"] = "test-mlops"

    mlflow.set_experiment(experiment_name)
    mlflow.set_tracking_uri(f"http://{tracking_server_host}:5000")

    model_name = "test_model"
    client = MlflowClient(f"http://{tracking_server_host}:5000")

    # List all versions of the model
    try:
        versions = client.search_model_versions(f"name='{model_name}'")

        # Delete each version of the model
        for version in versions:
            client.delete_model_version(name=model_name, version=version.version)
            print(f"Deleted version {version.version} of model {model_name}")

        # Delete the registered model
        client.delete_registered_model(name=model_name)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
