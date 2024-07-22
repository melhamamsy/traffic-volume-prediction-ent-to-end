import argparse

import pandas as pd
import psycopg
from psycopg.errors import UndefinedTable


def connect_to_db(dbname, user, password, host, port):
    try:
        conn = psycopg.connect(
            dbname=dbname, user=user, password=password, host=host, port=port
        )
        return conn
    except psycopg.OperationalError as e:
        print(f"Error: Unable to connect to the database {dbname}. {e}")
        return None


def check_table_exists(conn, table_name):
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM {table_name} LIMIT 1;")
            return True
    except UndefinedTable:
        return False


def query_models(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM models;")
        models = cur.fetchall()
    return models


def query_metrics(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 
                    model_id, 
                    MIN(timestamp) AS min_timestamp, 
                    MAX(timestamp) AS max_timestamp
            FROM metrics
            GROUP BY model_id;
        """
        )
        metrics = cur.fetchall()
    return metrics


def delete_database(dbname, user, password, host, port):
    try:
        conn = psycopg.connect(
            dbname="postgres", user=user, password=password, host=host, port=port
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE {dbname};")
        print(f"Database {dbname} deleted successfully.")
        conn.close()
    except Exception as e:
        print(f"Error: Unable to delete the database {dbname}. {e}")


def main(
    dbname,
    user,
    password,
    host,
    port,
    expected_monitor_start_date,
    expected_monitor_end_date,
    expected_monitor_report_span,
):
    conn = connect_to_db(dbname, user, password, host, port)

    assert conn is not None, "Issue in connection to db."

    assert check_table_exists(conn, "models"), "Models tables doesn't exist"
    assert check_table_exists(conn, "metrics"), "Models tables doesn't exist"

    models = query_models(conn)[0]
    assert models[1] == "traffic-volume-predictor"

    expected_monitor_report_span = int(expected_monitor_report_span)
    _, actual_monitor_start_date, actual_monitor_end_date = query_metrics(conn)[0]

    ## Grafana 5 years constraint
    actual_monitor_start_date = (
        actual_monitor_start_date
        - pd.DateOffset(years=5)
        - pd.DateOffset(days=expected_monitor_report_span)
    )
    actual_monitor_end_date = actual_monitor_end_date - pd.DateOffset(years=5)

    expected_monitor_start_date = pd.to_datetime(expected_monitor_start_date)
    expected_monitor_end_date = pd.to_datetime(expected_monitor_end_date)

    assert (
        actual_monitor_start_date == expected_monitor_start_date
    ), "Monitor start date mismatch."
    assert (
        actual_monitor_end_date == expected_monitor_end_date
    ), "Monitor end date mismatch."

    conn.close()

    # clean up
    delete_database(dbname, user, password, host, port)

    print("=" * 100)
    print("All db tests passed successfully")
    print("=" * 100)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check database tables and query models and metrics."
    )
    parser.add_argument("--dbname", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--monitor_start_date", required=True)
    parser.add_argument("--monitor_end_date", required=True)
    parser.add_argument("--monitor_report_span", required=True, type=int)

    args = parser.parse_args()
    main(
        args.dbname,
        args.user,
        args.password,
        args.host,
        args.port,
        args.monitor_start_date,
        args.monitor_end_date,
        args.monitor_report_span,
    )
