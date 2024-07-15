import os
from tempfile import TemporaryDirectory
from typing import Optional

from mlops.utils.deploy.github import copy_files, git_clone, remove_git_repository
from mlops.utils.deploy.terraform.constants import (
    ENV_VARS_KEY,
    TERRAFORM_AWS_FULL_PATH,
    TERRAFORM_AWS_NAME,
    TERRAFORM_REPO_URL,
)
from mlops.utils.deploy.terraform.env_vars import update_json_file
from mlops.utils.deploy.terraform.variables import update_variables

import re


def update_ecr_tf(
    file_path = os.path.join(TERRAFORM_AWS_FULL_PATH, "ecr.tf"),
    prevent_destroy_ecr = "false"  
):
    # Validate the prevent_destroy_ecr
    if prevent_destroy_ecr not in ['true', 'false']:
        raise ValueError("prevent_destroy_ecr must be 'true' or 'false'")

    # Read the contents of the file
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Regular expression to find and replace the prevent_destroy attribute
    pattern = r'(prevent_destroy\s*=\s*)(true|false)'
    replacement = r'\1' + prevent_destroy_ecr
    
    # Replace the prevent_destroy attribute
    updated_content = re.sub(pattern, replacement, content)
    
    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(updated_content)
    
    print(f"Updated {file_path} with prevent_destroy = false")


import re

def update_variables_tf(file_path, aws_region_default):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Define the new aws_region variable block
    new_aws_region_block = f'''
variable "aws_region" {{
  type        = string
  description = "AWS Region"
  default     = "{aws_region_default}"
}}
'''

    # Define the new availability_zones variable block
    new_availability_zones_block = f'''
variable "availability_zones" {{
  description = "List of availability zones"
  default     = ["{aws_region_default}a", "{aws_region_default}b"]
}}
'''

    # Define patterns to find or insert the variable blocks
    aws_region_pattern = r'variable\s+"aws_region"\s*{[^}]*}'
    availability_zones_pattern = r'variable\s+"availability_zones"\s*{[^}]*}'

    # Update or add the aws_region variable block
    if re.search(aws_region_pattern, content):
        content = re.sub(aws_region_pattern, new_aws_region_block, content, flags=re.DOTALL)
    else:
        content = content.strip() + '\n\n' + new_aws_region_block

    # Update or add the availability_zones variable block
    if re.search(availability_zones_pattern, content):
        content = re.sub(availability_zones_pattern, new_availability_zones_block, content, flags=re.DOTALL)
    else:
        content = content.strip() + '\n\n' + new_availability_zones_block
    
    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(content)
    
    print(f"Updated {file_path} with aws_region = {aws_region_default} and availability_zones")


def download_terraform_configurations():
    with TemporaryDirectory() as tmp_dir:
        git_clone(TERRAFORM_REPO_URL, tmp_dir)

        copy_files(
            os.path.join(tmp_dir, TERRAFORM_AWS_NAME),
            TERRAFORM_AWS_FULL_PATH,
        )


def setup_configurations(
    prevent_destroy_ecr: Optional[bool] = None,
    project_name: Optional[str] = None,
):
    if project_name:
        project_name = f'"{project_name}"'
    else:
        project_name = '"mlops"'

    docker_image = '"mageai/mageai:alpha"'

    print('Updating variables in variables.tf')
    print(f'  "app_name"            = {project_name}')
    print(f'  "docker_image"        = {docker_image}')
    print(f'  "enable_ci_cd"        = true')

    variables = dict(
        app_name=project_name,
        docker_image=docker_image,
        enable_ci_cd=True,
    )

    if prevent_destroy_ecr is not None:
        print(prevent_destroy_ecr)
        variables['prevent_destroy_ecr'] = prevent_destroy_ecr
        print(f'  "prevent_destroy_ecr" = {"true" if prevent_destroy_ecr else "false"}')

    update_variables(variables)

    update_json_file(
        os.path.join(TERRAFORM_AWS_FULL_PATH, f'{ENV_VARS_KEY}.json'),
        [
            dict(name='MAGE_PRESENTERS_DIRECTORY', value='mlops/presenters'),
        ],
    )

    ## update ecr.tf file prevent_destroy
    update_ecr_tf(
        file_path = os.path.join(TERRAFORM_AWS_FULL_PATH, "ecr.tf"),
        prevent_destroy_ecr = prevent_destroy_ecr 
    )


    # update variables.tf aws_region default   
    update_variables_tf(
        file_path = os.path.join(TERRAFORM_AWS_FULL_PATH, 'variables.tf'),
        aws_region_default = os.environ.get("AWS_REGION_NAME", "eu-north-1")
    )
