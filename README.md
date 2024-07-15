# 1.    Problem Description
- Describe the problem


# 2.    Data
- source
- online: a record (each hour)
- Columns


# 3.    Exploratory Notebook
- path
- sections description
- pipfile


# 4.    AWS Setup

## 4.1    iam:CreatePolicy:

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
                            "iam:CreatePolicyVersion"
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
- In codespace create a profile "test-mlops":
    
        aws configure --profile test-mlops
        
        ## Insert AWS Access Key ID generated above
        ## Insert AWS Secret Access Key generated above




# 5.    Workflow

- Diagram

    ## 5.1  Data Location
    - Simulated an s3 bucket as the source of data since the data is static at path
    ## 5.2  Experiment Tracking (Mlflow)
    - Used mlflow, backend server: AWS EC2, database: postgresql on AWS, and artifacts store: AWS S3 bucket.
    ## 5.3  Orchestration (Mage)
    - Server: Github codespace

            cd && touch .gitconfig && cd /workspaces/traffic-volume-prediction-ent-to-end

            sudo pip install awscli --force-reinstall --upgrade
    - Cloned mage.ai.url into orchestration directory.

            cd orchestration && rm -rf .git
            ./scripts/start.sh

            
        ### 5.3.1   Pipelines
        - quick description
        ### 5.3.2   Triggers
        - API inference
        ### 5.3.3   Deploy

        #### 5.3.3.1    TerraformApplyDeployMage
        Used to deploy mage resources.

        _Credentials already defined as Environment Variables using codespace secrets._

            aws iam create-policy --policy-name TerraformApplyDeployMage --policy-document \
             "$(curl -s https://raw.githubusercontent.com/mage-ai/mage-ai-terraform-templates/master/aws/policies/TerraformApplyDeployMage.json)"

        #### 5.3.3.2    TerraformDestroyDeleteResources
        Used to delete resources.

        _Credentials already defined as Environment Variables using codespace secrets._

            aws iam create-policy --policy-name TerraformDestroyDeleteResources --policy-document \
            "$(curl -s https://raw.githubusercontent.com/mage-ai/mage-ai-terraform-templates/master/aws/policies/TerraformDestroyDeleteResources.json)"

        #### 5.3.3.3    Creating IAM User (MageDeployer) & Attach above policies

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







