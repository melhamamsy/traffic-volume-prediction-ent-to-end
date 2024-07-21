from mlops.utils.deploy.aws import (
    IAM_USER_NAME, POLICY_NAME_TERRAFORM_APPLY_DEPLOY_MAGE,
    POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES, TERRAFORM_APPLY_URL,
    TERRAFORM_DESTROY_URL, attach_policy_to_user, create_access_key_for_user,
    create_policy, create_user, reset, save_credentials_to_file)

if "custom" not in globals():
    from mage_ai.data_preparation.decorators import custom

import configparser
import os

from mlops.utils.deploy.utils import (check_policy_action, get_aws_credentials,
                                      get_policy_arn,
                                      is_policy_attached_to_user,
                                      policy_exists_by_name, profile_exists,
                                      update_policy, user_exists)


@custom
def setup(*args, **kwargs):
    # reset(IAM_USER_NAME)
    aws_profile = kwargs["AWS_PROFILE"]

    # Create IAM Policies
    if not policy_exists_by_name(POLICY_NAME_TERRAFORM_APPLY_DEPLOY_MAGE, aws_profile):
        terraform_apply_policy_arn = create_policy(
            POLICY_NAME_TERRAFORM_APPLY_DEPLOY_MAGE, TERRAFORM_APPLY_URL
        )
        print(
            f"Successfully created the policy '{POLICY_NAME_TERRAFORM_APPLY_DEPLOY_MAGE}'."
        )
    else:
        print(f"The policy '{POLICY_NAME_TERRAFORM_APPLY_DEPLOY_MAGE}' already exists.")
    if not policy_exists_by_name(
        POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES, aws_profile
    ):
        terraform_destroy_policy_arn = create_policy(
            POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES, TERRAFORM_DESTROY_URL
        )
        print(
            f"Successfully created the policy '{POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES}'."
        )
    else:
        print(
            f"The policy '{POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES}' already exists."
        )

    # Update policy {POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES}
    policy_arn = get_policy_arn(
        POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES, aws_profile
    )
    new_action = "ecr:DeleteRepository"
    if not check_policy_action(aws_profile, policy_arn, new_action):
        update_policy(aws_profile, policy_arn, new_action)
        print(
            f"Successfully attached action {new_action} to policy "
            + f"{POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES}"
        )
    else:
        print(
            f"Action {new_action} is already attached to policy "
            + f"{POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES}"
        )

    # Create the user MageDeployer
    if not user_exists(IAM_USER_NAME, aws_profile):
        create_user(IAM_USER_NAME)
        print(f"Successfully created the user '{IAM_USER_NAME}'.")
    else:
        print(f"The user '{IAM_USER_NAME}' already exists.")

    # Attach policies to the user MageDeployer
    if not is_policy_attached_to_user(
        IAM_USER_NAME, POLICY_NAME_TERRAFORM_APPLY_DEPLOY_MAGE, aws_profile
    ):
        terraform_apply_policy_arn = get_policy_arn(
            POLICY_NAME_TERRAFORM_APPLY_DEPLOY_MAGE, aws_profile
        )
        attach_policy_to_user(IAM_USER_NAME, terraform_apply_policy_arn)
        print(
            f"Successfully attached policy '{POLICY_NAME_TERRAFORM_APPLY_DEPLOY_MAGE}'"
            + f"to the user '{IAM_USER_NAME}'."
        )
    else:
        print(
            f"Policy '{POLICY_NAME_TERRAFORM_APPLY_DEPLOY_MAGE}' is already attached"
            + f" to the user '{IAM_USER_NAME}'."
        )
    if not is_policy_attached_to_user(
        IAM_USER_NAME, POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES, aws_profile
    ):
        terraform_destroy_policy_arn = get_policy_arn(
            POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES, aws_profile
        )
        attach_policy_to_user(IAM_USER_NAME, terraform_destroy_policy_arn)
        print(
            f"Successfully attached policy '{POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES}'"
            + f"to the user '{IAM_USER_NAME}'."
        )
    else:
        print(
            f"Policy '{POLICY_NAME_TERRAFORM_DESTROY_DELETE_RESOURCES}' is already attached"
            + f" to the user '{IAM_USER_NAME}'."
        )

    # Create access key
    if not profile_exists(IAM_USER_NAME):
        access_key, secret_key = create_access_key_for_user(IAM_USER_NAME)
        save_credentials_to_file(IAM_USER_NAME, access_key, secret_key)
        print(f"Successfully created profile {IAM_USER_NAME}.")
    else:
        print(f"Profile {IAM_USER_NAME} already exists")

    # Set environment variable AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY
    aws_access_key_id, aws_secret_access_key = get_aws_credentials(IAM_USER_NAME)
    os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key
    print(
        "Successfully set AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY environment variables..."
    )

    # Set aws region
    os.environ["AWS_REGION_NAME"] = kwargs["AWS_REGION_NAME"]
    print(
        f"Successfully set AWS_REGION_NAME environment variable to {os.environ['AWS_REGION_NAME']}..."
    )


### test by creating sth then deleting it in unit tests
## create a function to remove profile from ~/.aws/credentials
