from mlops.utils.deploy.terraform.cli import terraform_destroy

if "custom" not in globals():
    from mage_ai.data_preparation.decorators import custom

import os

from mlops.utils.deploy.aws import IAM_USER_NAME


@custom
def transform_custom(*args, **kwargs):
    os.environ["AWS_PROFILE"] = IAM_USER_NAME
    if kwargs.get("DESTROY").upper() in ["Y", "YES"]:
        terraform_destroy(kwargs["password"])
    else:
        print("Skipping Terraform destroy...")


# ISSUE:
## Had to manually delete below:
### 1. delete load balancer
### 2. delete mlops-efs (elastic file system)
### 3. delete database mlops-production-db
