#!/bin/bash

########################################### In terminal ################################################
# chmod +x download-model.sh
# ./download-model.sh
########################################################################################################

### Champion
model_s3_path="s3://mlflow-artifacts-melhamamsy/2/c6343316f0c64d0ea822e39d8820e3db/artifacts/models"

### Challenger
# model_s3_path="s3://mlflow-artifacts-melhamamsy/2/f12fc678ffa3437cbe33b2e39400c9a1/artifacts/models"

### local-dir
model_local_path="/media/mohammed/workspace3/__ing/mlopsing/traffic-volume-prediction-ent-to-end/deployment/online-deployment-flask/model"

### Define aws profile
export AWS_PROFILE="test-mlops"

### Download the model from S3 to a local directory
mlflow artifacts download --artifact-uri "$model_s3_path" --dst-path "$model_local_path"