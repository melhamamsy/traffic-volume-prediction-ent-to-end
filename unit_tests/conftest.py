import pytest
import mlflow
import os

@pytest.fixture(scope="session")
def set_tracking_uri():
    # Set AWS profile
    os.environ['AWS_PROFILE'] = 'test-mlops'

    tracking_server_host = 'ec2-13-60-24-194.eu-north-1.compute.amazonaws.com'
    mlflow.set_tracking_uri(f"http://{tracking_server_host}:5000")
    print("Tracking URI set to:", mlflow.get_tracking_uri())

    experiment_name = 'testing_experiment'
    
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

@pytest.fixture(scope="session")
def reset_tracking_uri():
    # Set AWS profile
    os.environ['AWS_PROFILE'] = 'test-mlops'

    tracking_server_host = 'ec2-13-60-24-194.eu-north-1.compute.amazonaws.com'
    mlflow.set_tracking_uri(f"http://{tracking_server_host}:5000")
    print("Tracking URI set to:", mlflow.get_tracking_uri())

    experiment_name = 'testing_experiment'
    
    try:
        experiment_id = mlflow.create_experiment(experiment_name)
        print(f"Created experiment '{experiment_name}' with ID {experiment_id}")
    except mlflow.exceptions.MlflowException as e:
        if "RESOURCE_ALREADY_EXISTS" in str(e):
            print(f"Experiment '{experiment_name}' already exists.")
            experiment = mlflow.get_experiment_by_name(experiment_name)
            experiment_id = experiment.experiment_id
            print(f"Existing experiment ID: {experiment_id}")
            runs = mlflow.search_runs(experiment_ids=[experiment_id])
            for _, run in runs.iterrows():
                run_id = run['run_id']
                mlflow.delete_run(run_id)
            print(f"Cleaned up experiment '{experiment_name}'.")
        else:
            raise e

    mlflow.set_experiment(experiment_name)
    print(f"Set experiment to '{experiment_name}' with ID {experiment_id}")
    return experiment_id