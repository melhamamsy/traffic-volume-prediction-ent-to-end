# 1.    Problem Description & Data
The problem is to predict the traffic volume given information about weather and other significant independent variables. The data is hourly, that makes an online deployment of machine learning model as a web-service a good solution. An AWS S3 bucket is a de-facto storage for the data. The data files are of the format {FILE_PATH_PREFIX}_{year}.csv.

Data could be found at [Metro Interstate Traffic Volume](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume). You could also find the data separated by year in the repo at `./monitoring/data`.


| Variable Name        | Role    | Type        | Description                                           | Units  | Missing Values |
|----------------------|---------|-------------|-------------------------------------------------------|--------|----------------|
| holiday              | Feature | Categorical | US National holidays plus regional holiday, Minnesota State Fair |        | no             |
| temp                 | Feature | Continuous  | Average temp in kelvin                                | Kelvin | no             |
| rain_1h              | Feature | Continuous  | Amount in mm of rain that occurred in the hour        | mm     | no             |
| snow_1h              | Feature | Continuous  | Amount in mm of snow that occurred in the hour        | mm     | no             |
| clouds_all           | Feature | Integer     | Percentage of cloud cover                             | %      | no             |
| weather_main         | Feature | Categorical | Short textual description of the current weather      |        | no             |
| weather_description  | Feature | Categorical | Longer textual description of the current weather     |        | no             |
| date_time            | Feature | Date        | Hour of the data collected in local CST time          |        | no             |
| traffic_volume       | Target  | Integer     | Hourly I-94 ATR 301 reported westbound traffic volume |        | no             |


# 2.    Exploratory Notebook
`./notebooks` directory contains initial experiments, data exploration, feature engineering, and hyperparameter tuning of XGBoost using hyperopt with AWS servers as the backend. 

The resulting model should be a self-contained sklearn pipeline with all the feature-engineering steps needed and the XGBoost Regressor model at the end of the pipeline.

Custom classes were created to implement the feature engineering steps that are appended to the start of the pipeline.


# 3.    AWS Setup
In this section, I list the steps needed to be able to rely on AWS as backend to the project.

## 3.1  Main user and policies:

Here I create a user and name it `test-mlops`. This user is used for most of the activities needed except mage-deployment and mage-ci-cd.

- Sign in to the AWS Management Console.
- Navigate to the IAM service.
- In the navigation pane, choose Policies, then click Create policy.
- Choose the JSON tab, paste the policy below, and click Next: Tags.

            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "iam:CreatePolicy",
                            "iam:CreateUser",
                            "iam:ListPolicies",
                            "iam:CreateAccessKey",
                            "iam:AttachUserPolicy",
                            "iam:GetUser",
                            "iam:ListAttachedUserPolicies",
                            "iam:GetPolicy",
                            "iam:GetPolicyVersion",
                            "iam:CreatePolicyVersion",
                            "elasticbeanstalk:CreateApplication",
                            "elasticbeanstalk:ListPlatformBranches"
                        ],
                        "Resource": "*"
                    }
                ]
            }

- Add any tags if needed, then click Next: Review.
- Provide a name for your policy (e.g., AllowCreatePolicy) and click Create policy.
- In the navigation pane, choose Users.
- Select the user you want (test-mlops, in this case) to attach the policy to.
- On the user details page, choose the Permissions tab and then click Add permissions.
- Choose Attach policies directly.
- Search for your custom policy (e.g., AllowCreatePolicy), select it, and click Next: Review.
- Click Add permissions to attach the policy.
- Next: Attach AdministratorAccess-AWSElasticBeanstalk policy, as well, for deployment. This is important when we deploy the model as a web-service.
- Add Access Key:

    - On the user details page, select the "Security credentials" tab.
    - Scroll down to the "Access keys" section.
    - Click on the "Create access key" button.
    - Configure Access Key:
    - Choose the intended use case for the access key 
        (e.g., Command Line Interface (CLI), Software Development Kit (SDK), etc.).
    - Click on the "Next" button.
    - View and Download the Access Key:
        AWS will display the new access key ID and secret access key.
        Important: Download the key file or copy and securely save the access key ID and secret access key. You will not be able to see the secret access key again after this step.
    - After saving the access key, click on the "Done" button.
- In codespace (or local, depending on your setup) create a profile "test-mlops":
    
        aws configure --profile test-mlops
        
        ## Insert AWS Access Key ID generated above
        ## Insert AWS Secret Access Key generated above


## 3.2  Mlflow Backend:
Follow [mlflow_on_aws.md](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/02-experiment-tracking/mlflow_on_aws.md)
to create EC2 Server, Backend Postgres DB, and S3 artifacts store.

Make sure to save key-pair.pem in a safe directory and cd to that directory before ssh-ing to the EC2 machine.

Make sure to store the username and password of the postgres database as you will need it to launch the mlflow server after ssh-ing to the EC2 machine.

The DNS name of the machine will be needed as well, will be used later as the value of the `tracking_server_host` variable that's used to log the runs to the remote mlflow server.

# 4.    Workflow

- Diagram

    ## 4.1  Data Location
    - Simulated an s3 bucket as the source of data since the data is static. _Note: this is a different bucket than that used to store mlflow artifacts_. The name of the bucket is important as it'll be passed as a variable in `mage` pipelines.
    ## 4.2  Experiment Tracking (Mlflow)
    - Used mlflow, backend server: AWS EC2, database: postgresql on AWS, and artifacts store: AWS S3 bucket.
    ## 4.3  Orchestration (Mage)
    - Server: Github codespace (or localhost)

            cd && touch .gitconfig && cd /workspaces/traffic-volume-prediction-ent-to-end

            sudo pip install awscli --force-reinstall --upgrade
    - Cloned mage.ai.url into orchestration directory.

            <!-- cd orchestration && rm -rf .git -->
            ./scripts/start.sh

            
        ### 4.3.1   Pipelines
        - **data_preparation:** read the data from the s3 bucket, transform it, and export it (along with a feature engineering pipeline) as a temporarily-persistent global data product.
        
            Pipeline Variables:

                1. AWS_PROFILE: profile of the user (test-mlops) used to access the s3 bucket.
                2. BUCKET_NAME: name of the S3 bucket in which data resides.
                3. COLUMNS: comma-separated string of the names of the independent variables.
                4. DATE_TIME: name of the date_time column.
                5. FILE_PATH_PREFIX: the prefix of the files in s3 {FILE_PATH_PREFIX}_{year}.csv
                6. TARGET: name of the target variable.

        - **xgboost_training:** use the global data product from `data_preparation` to finetune an XGBoot Regressor using hyperopt, tracking experiments using mlflow running on AWS remote servers, register best models, plot shap explaining report to understand the impact of independent variables on the predicted target value, and finally pass best models as GDP to be used in subsequent pipelines.

            Pipeline Variables:

                1. AWS_PROFILE, COLUMNS, DATE_TIME, TARGET: same as 'data_preparation'.
                2. IS_PLOT_SHAP, IS_REGISTER_MODELS, IS_RUN_FINE_TUNING: booleans to indicate whether to perform that action, since the pipeline also loads registered models and pass them as GDP, and in prediction case, that's all what's needed.
                3. MLFLOW_BUCKET_NAME: name of the mlflow artifacts s3 store.
                4. MLFLOW_EXPERIMENT_NAME: name of the mlflow experiment.
                5. N_BEST_MODELS: number of best performing models to log, register, and pass as GDP.
                6. TRACKING_SERVER_HOST: DNS of the mlflow EC2 server.
                7. name_to_register_with: name to register the best models (pipelines) as; each model as a version.

        - **automatic_retraining:** check for new data by checking the state of the S3 data bucket using a json file `s3_state.json`. If new data is uploaded, rerun the `xgboost_training` pipeline which in turn triggers the `data_preparation` pipeline. _Note: this is just a simulation, the data\_preparation pipeline reads the same data each time_.
        
            Pipeline Variables:

                1. AWS_PROFILE, BUCKET_NAME: same as 'xgboost_training' pipeline.
                2. STATE_FILE: path of the 's3_state.json' file.

        - **predict:** receive on-spot requests using REST api calls to predict given the model.
        
                curl --location 'http://localhost:6789/api/runs' \
                --header 'Authorization: Bearer 8c097d3f177344128bee40a66210ce3b' \
                --header 'Content-Type: application/json' \
                --header 'Cookie: lng=en' \
                --data '{
                    "run": {
                        "pipeline_uuid": "predict",
                        "block_uuid": "inference",
                        "variables": {
                            "inputs": [
                                {
                                    "holiday": "None",
                                    "temp": "288.28",
                                    "rain_1h": "0",
                                    "snow_1h": "0",
                                    "clouds_all": "40",
                                    "weather_main": "Clouds",
                                    "date_time": "2024-10-02 09:00:00"
                                },
                                {
                                    "holiday": "Thanksgiving Day",
                                    "temp": "268.24",
                                    "rain_1h": "0",
                                    "snow_1h": "0",
                                    "clouds_all": "64",
                                    "weather_main": "Clouds",
                                    "date_time": "2024-11-28 00:00:00"
                                }
                            ]
                        }
                    }
                }'

        - **deploying_to_production:** using `terraform` as an `Iac` tool to create MageDeployer AWS user, create AWS resources to deploy mage, deploy/destroy resources, create `ci-cd` yml file to be used as a workflow in github actions, and create an AWS user to perform the ci/cd deployment action.

            Pipeline Variables:

                1. AWS_PROFILE: test-mlops, not MageDeployer, as this is used to create MageDeployer and attach required polices to it in the first place.
                2. AWS_REGION_NAME: name of the aws_region to deploy resources to, in my case: eu-north-1.
                3. DESTROY: boolean: whether or not to destroy resources.
                4. username, password: username and password of pgvector db used by mage (**I might be wrong here**).
                5. prevent_destroy_ecr: a boolean to indicate whether or not to destroy the elastic container registry deployed by terraform. _Warning: an issue here is that you need to manually empty this ecr before destroying the resources, this should be fixed later_.   

        ### 4.3.2   Triggers
        - **Retrain models daily:** triggers `automatic_training` pipeline daily to check for new data and decide on whether to retrain or not.
        - **Real-time predictions:** triggers `predict` pipeline to perform on-spot prediction.
        - **GLOBAL_DATA_PRODUCT_TRIGGER**(s): re-cache the output of the pipelines used to generate the GDPs.
       
        ### 4.3.3   Deploy
        This is another way to required aws user and policies required by terraform to deploy the pipeline. _Skip section 4.3.3 altogether if already used `permissions` block in the `deploying_to_production` pipeline_

        #### 4.3.3.1    TerraformApplyDeployMage policy
        Used to deploy mage resources.

        Use Either:
        _Credentials already defined as Environment Variables using codespace secrets_, or _export AWS_PROFILE=test-mlops_

            aws iam create-policy --policy-name TerraformApplyDeployMage --policy-document \
             "$(curl -s https://raw.githubusercontent.com/mage-ai/mage-ai-terraform-templates/master/aws/policies/TerraformApplyDeployMage.json)"

        #### 4.3.3.2    TerraformDestroyDeleteResources policy
        Used to delete resources.

        Use Either:
        _Credentials already defined as Environment Variables using codespace secrets_, or _export AWS_PROFILE=test-mlops_

            aws iam create-policy --policy-name TerraformDestroyDeleteResources --policy-document \
            "$(curl -s https://raw.githubusercontent.com/mage-ai/mage-ai-terraform-templates/master/aws/policies/TerraformDestroyDeleteResources.json)"

        #### 4.3.3.3    Creating IAM User (MageDeployer) & Attach above policies

            aws iam create-user --user-name MageDeployer


            aws iam attach-user-policy \
                --policy-arn $(aws iam list-policies \
                --query "Policies[?PolicyName==\`TerraformApplyDeployMage\`].Arn" \
                --output text) \
                --user-name MageDeployer    


            aws iam attach-user-policy \
                --policy-arn $(aws iam list-policies \
                --query "Policies[?PolicyName==\`TerraformDestroyDeleteResources\`].Arn" \
                --output text) \
                --user-name MageDeployer


            # Get access key and add it to the ~/.aws dir
            aws iam create-access-key \
                --user-name MageDeployer \
                --output json | jq -r '"[MageDeployer]\naws_access_key_id = \(.AccessKey.AccessKeyId)\naws_secret_access_key = \(.AccessKey.SecretAccessKey)"' >> ~/.aws/credentials
            echo "[profile MageDeployer]" >> ~/.aws/config
            export AWS_PROFILE="MageDeployer"

        Or could be done in python using `deploying_to_production` pipeline, block: `permissions`.

        ### 4.3.4   CI/CD workflow for github actions:
        - Manually moved the resulting .github dir from `./orchestration` where it's automatically created by the `deploying_to_production` pipeline to `./`.

        - Manually updated branch master to main to run the workflow when pushing to main.

        - Commented it and used NOT_A_BRANCH name to avoid rerunning the workflow, after destroying the resources, replace with main to re-use.
    
    ## 4.4 Deployment (AWS Elastic Beanstalk)
    Online deployment using AWS Elastic Beanstalk. Model is downloaded, stored in `models/`, and copied to the image.

    - Directory (./deployment/online-deployment-flask/):
            
            download-model.sh: used to download the model from s3 artifact store to models/
            models/: where model (pipeline) is stored
            utils/: scripts needed by the model (pipeline)
            Dockerfile: Used to create the image to be deployed
            predict.py: Application (Flask)

    - Steps to deploy:

            cd deployment/online-deployment-flask
            
            eb init -p docker -r eu-north-1 --profile test-mlops traffic-volume-prediction
            
            ## make sure it works locally
            eb local run --port 9696 --profile test-mlops
            ## In another terminal
            pipenv shell
            python test.py
            ^C

            ## create an environment (no need to --profile, in config.yml)
            eb create traffic-volume-prediction-env
            ## In another terminal
            pipenv shell
            python test.py
            ^C

            ## Do not forget to terminate everything and remove application:
            eb terminate --all --force

    ## 4.5 Monitoring (Evidently & Grafana)
    A stand-alone module (not part of the mage pipeline) to monitor the performance of the resulting model over time, and detect any possible drift. 
    - Using [evidently](https://www.evidentlyai.com/) to generate monitoring report of the drift of target, prediction, or independent variables, if any.
    - Populating `metrics` table in a postgres db with the resulting metrics, use `adminer` to visually inspect the data in the db.
    - Reading from the metrics table to a [grafana](https://grafana.com/) dashboard and saving the dashboard in `data_drift.json` file.
    - Using `localhost` as the backend. Using Cloud resources was complicated for me because I would have to publicly expose the server and db if I want to reach it from mage server, and thus monitoring is not added in the mage pipeline, as well. Another solution is to create security groups (future improvement). For now, monitoring is a stand-alone module.
    - Directory:
            
            data/: where data is located
            models/: where the model (pipeline) is located
            utils/: python scripts needed by the model (pipeline).
            dashboards/: where json files of the dashboards are saved.
            config/: where the grafana configurations are stored.
            docker-compose.yml: to pull and create images (db, adminer, and grafana).
            evidently_metrics_calculation.py: read reference and current data, load model, predict both, check drift using 'evidently', populated the 'metrics' table.

# 4.    Testing

- Unit tests using `pytest` and integration tests are used to ensure correctness, compactness, and integrity of the modules. Unit tests for the utilities of the `orchestration` module are created, and an integration test for the `monitoring` module is created. 

- `pylint` is used to assess the code quality.

- `black` & `isort` are used to fix the quality of the code.

- `pyproject.toml` is used to control the configurations of those tools.

- `Makefile` is used to run unit_tests, perform quality checks, and run integration_tests.

# 5. CI/CD

- Automatically generated by the `deploying_to_production` pipeline in the orchestration module, moved manually to the project root directory, and manually updated the on-push branch to main (was master).

- `git push origin main` should trigger github workflow, given that terraform resources are alive.









