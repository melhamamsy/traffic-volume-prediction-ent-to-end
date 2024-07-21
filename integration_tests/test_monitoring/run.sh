#!/bin/bash


## make sure password and user are the same used in docker-compose.yml
dbname="test" 
user="postgres" 
password="example" 
host="localhost" 
port="5432" 
monitor_start_date="2017-01-01" 
monitor_end_date="2017-03-01"
monitor_report_span="14"


cd $(dirname "$(realpath "$0")")
cd ../../monitoring

docker-compose up -d

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs >> integration_test.log
    docker-compose down
    exit ${ERROR_CODE}
fi

pipenv run python evidently_metrics_calculation.py \
    --dbname $dbname \
    --user $user \
    --password $password \
    --host $host \
    --port $port \
    --monitor_start_date $monitor_start_date \
    --monitor_end_date $monitor_end_date\
    --monitor_report_span $monitor_report_span


ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs >> integration_test.log
    docker-compose down
    exit ${ERROR_CODE}
fi

pipenv run python ../integration_tests/test_monitoring/test_integration_monitoring.py \
    --dbname $dbname \
    --user $user \
    --password $password \
    --host $host \
    --port $port \
    --monitor_start_date $monitor_start_date \
    --monitor_end_date $monitor_end_date\
    --monitor_report_span $monitor_report_span

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs >> integration_test.log
    docker-compose down
    exit ${ERROR_CODE}
fi

docker-compose logs >> integration_test.log
docker-compose down