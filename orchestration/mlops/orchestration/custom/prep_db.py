if "custom" not in globals():
    from mage_ai.data_preparation.decorators import custom
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


import os
import sys

# Determine the root directory of your project
project_root = os.path.join(os.getcwd(), "mlops")
# Check if the project root is already in sys.path, and add it if not
if project_root not in sys.path:
    sys.path.append(project_root)

import psycopg


@custom
def prep_db(*args, **kwargs):
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """

    # Database connection parameters
    host = "<DB_NAME>.<ID>.eu-north-1.rds.amazonaws.com"
    port = "5432"  # Default port for PostgreSQL
    user = "<DB_USER>"  # Replace with your username
    password = "<DB_PASSWORD>"  # Replace with your password

    # Specify your custom logic here
    with psycopg.connect(
        f"host={host} port={port} user={user} password={password}", autocommit=True
    ) as conn:
        res = conn.execute("SELECT datname FROM pg_database")
    print(res.fetchall())

    ### ISSUE: Connectivity

    return {}
