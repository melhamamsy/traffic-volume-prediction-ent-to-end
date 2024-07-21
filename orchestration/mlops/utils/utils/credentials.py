import os
from typing import Dict


def get_aws_credentials() -> Dict:
    """
    Get AWS credentails defined in github codespaces secrets
    and passed to the container by the docker-compose.yml file

    Returns: dictionary of credentials
    """
    return {
        "key": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
    }
