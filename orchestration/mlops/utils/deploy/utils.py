import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError, ProfileNotFound
import boto3
import json



def list_policy_versions(policy_arn):
    try:
        response = iam_client.list_policy_versions(PolicyArn=policy_arn)
        return response['Versions']
    except ClientError as e:
        print(f"Error listing policy versions: {e}")
        return []

# Function to delete the oldest version of a managed policy
def delete_oldest_policy_version(policy_arn):
    versions = list_policy_versions(policy_arn)
    if len(versions) >= 5:
        # Find the oldest non-default version
        non_default_versions = [v for v in versions if not v['IsDefaultVersion']]
        oldest_version = sorted(non_default_versions, key=lambda v: v['CreateDate'])[0]
        try:
            iam_client.delete_policy_version(
                PolicyArn=policy_arn,
                VersionId=oldest_version['VersionId']
            )
            print(f"Deleted oldest version: {oldest_version['VersionId']}")
        except ClientError as e:
            print(f"Error deleting policy version: {e}")



def check_policy_action(profile_name, policy_arn, action_to_check):
    # Create a boto3 session using the specified profile
    session = boto3.Session(profile_name=profile_name)
    iam_client = session.client('iam')

    try:
        # Get the existing policy document
        response = iam_client.get_policy(PolicyArn=policy_arn)
        
        policy_version_id = response['Policy']['DefaultVersionId']

        policy_version = iam_client.get_policy_version(
            PolicyArn=policy_arn,
            VersionId=policy_version_id
        )

        policy_document = policy_version['PolicyVersion']['Document']

        # Assuming the policy document is a dict and has 'Statement' as a list of statements
        for statement in policy_document['Statement']:
            if statement['Effect'] == 'Allow':
                actions = statement['Action']
                if isinstance(actions, str):
                    actions = [actions]
                if action_to_check in actions:
                    return True

        return False
    except iam_client.exceptions.NoSuchEntityException:
        print(f"Policy with ARN {policy_arn} does not exist.")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False


def update_policy(profile_name, policy_arn, new_action):
    # Create a boto3 session using the specified profile
    session = boto3.Session(profile_name=profile_name)
    iam_client = session.client('iam')

    # Get the existing policy document
    response = iam_client.get_policy(
        PolicyArn=policy_arn
    )
    
    policy_version_id = response['Policy']['DefaultVersionId']

    policy_version = iam_client.get_policy_version(
        PolicyArn=policy_arn,
        VersionId=policy_version_id
    )

    policy_document = policy_version['PolicyVersion']['Document']

    # Assuming the policy document is a dict and has 'Statement' as a list of statements
    updated = False
    for statement in policy_document['Statement']:
        if statement['Effect'] == 'Allow':
            if isinstance(statement['Action'], list):
                if new_action not in statement['Action']:
                    statement['Action'].append(new_action)
                    updated = True
            else:
                if statement['Action'] != new_action:
                    statement['Action'] = [statement['Action'], new_action]
                    updated = True
    
    if not updated:
        print(f"Action '{new_action}' is already present in the policy.")
        return
    
    # Convert the policy document to JSON
    updated_policy_document = json.dumps(policy_document)


    # Delete oldest version if versions go over 5
    delete_oldest_policy_version(policy_arn)
    # Create a new policy version with the updated document
    iam_client.create_policy_version(
        PolicyArn=policy_arn,
        PolicyDocument=updated_policy_document,
        SetAsDefault=True
    )

    print(f"Policy updated successfully with new action: {new_action}")


def user_exists(username, profile_name=None):
    # Initialize a session using Amazon IAM
    if profile_name:
        session = boto3.Session(profile_name=profile_name)
    else:
        session = boto3.Session()

    iam = session.client('iam')

    try:
        # Get the user details
        iam.get_user(UserName=username)
        return True
    except iam.exceptions.NoSuchEntityException:
        # If the user does not exist, a NoSuchEntityException is thrown
        return False
    except (NoCredentialsError, PartialCredentialsError):
        print("Credentials not available.")
        return False
    except ClientError as e:
        # Catch any other errors and print the error message
        print(f"Unexpected error: {e}")
        return False


def policy_exists_by_name(policy_name, profile_name=None):
    # Initialize a session using the specified profile, or default if not provided
    if profile_name:
        session = boto3.Session(profile_name=profile_name)
    else:
        session = boto3.Session()

    iam = session.client('iam')

    try:
        paginator = iam.get_paginator('list_policies')
        for page in paginator.paginate(Scope='Local'):
            for policy in page['Policies']:
                if policy['PolicyName'] == policy_name:
                    return True
        return False
    except (NoCredentialsError, PartialCredentialsError):
        print("Credentials not available.")
        return False
    except ClientError as e:
        # Catch any other errors and print the error message
        print(f"Unexpected error: {e}")
        return False


def get_policy_arn(policy_name, profile_name=None):
    # Initialize a session using the specified profile, or default if not provided
    if profile_name:
        session = boto3.Session(profile_name=profile_name)
    else:
        session = boto3.Session()

    iam = session.client('iam')

    try:
        paginator = iam.get_paginator('list_policies')
        for page in paginator.paginate(Scope='Local'):  # Scope='Local' includes only customer managed policies
            for policy in page['Policies']:
                if policy['PolicyName'] == policy_name:
                    return policy['Arn']
        return None
    except (NoCredentialsError, PartialCredentialsError):
        print("Credentials not available.")
        return None
    except ClientError as e:
        # Catch any other errors and print the error message
        print(f"Unexpected error: {e}")
        return None


def is_policy_attached_to_user(user_name, policy_name, profile_name=None):
    # Get the policy ARN from the policy name
    policy_arn = get_policy_arn(policy_name, profile_name)
    if not policy_arn:
        print(f"Policy '{policy_name}' not found.")
        return False

    # Initialize a session using the specified profile, or default if not provided
    if profile_name:
        session = boto3.Session(profile_name=profile_name)
    else:
        session = boto3.Session()

    iam = session.client('iam')

    try:
        # List policies attached to the user
        response = iam.list_attached_user_policies(UserName=user_name)
        for policy in response['AttachedPolicies']:
            if policy['PolicyArn'] == policy_arn:
                return True
        return False
    except (NoCredentialsError, PartialCredentialsError):
        print("Credentials not available.")
        return False
    except ClientError as e:
        # Catch any other errors and print the error message
        print(f"Unexpected error: {e}")
        return False


def profile_exists(profile_name):
    try:
        # Attempt to create a session using the specified profile
        session = boto3.Session(profile_name=profile_name)
        
        # Check if the session has valid credentials
        credentials = session.get_credentials()
        if credentials is None:
            raise NoCredentialsError
        
        return True
    except ProfileNotFound:
        print(f"Profile '{profile_name}' not found.")
        return False
    except (NoCredentialsError, PartialCredentialsError):
        print(f"Profile '{profile_name}' exists but credentials are not available or incomplete.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False



def get_aws_credentials(profile_name):
    try:
        # Initialize a session using the specified profile
        session = boto3.Session(profile_name=profile_name)
        
        # Get the credentials from the session
        credentials = session.get_credentials()
        
        # Access the individual components of the credentials
        access_key = credentials.access_key
        secret_key = credentials.secret_key
        
        return access_key, secret_key
    except (NoCredentialsError, PartialCredentialsError):
        print("Credentials not available or incomplete.")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None