import json
import os

import boto3


def get_s3_objects(bucket_name):
    """Get a list of objects in an S3 bucket."""
    s3 = boto3.client("s3")

    response = s3.list_objects_v2(Bucket=bucket_name)
    return [obj["Key"] for obj in response.get("Contents", [])]


def load_previous_state(state_file):
    """Load the previous state from a file."""
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            return json.load(f)
    return []


def save_current_state(state_file, current_state):
    """Save the current state to a file."""
    with open(state_file, "w") as f:
        json.dump(current_state, f)


def check_for_new_data(bucket_name, state_file):
    """Check if new data has been added to the S3 bucket."""

    current_objects = get_s3_objects(bucket_name)
    previous_objects = load_previous_state(state_file)

    new_objects = set(current_objects) - set(previous_objects)
    if new_objects:
        save_current_state(state_file, current_objects)
        print("New data available, retraining...")
        return True
    else:
        print("No new data, nothing to do.")
        return False
