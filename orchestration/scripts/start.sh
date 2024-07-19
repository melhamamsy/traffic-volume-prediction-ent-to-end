#!/bin/bash

## codespace
# $@ in case of passing parameters
PROJECT_NAME=mlops \
  MAGE_CODE_PATH=/workspaces/traffic-volume-prediction-ent-to-end/orchestration \
  SMTP_EMAIL=$SMTP_EMAIL \
  SMTP_PASSWORD=$SMTP_PASSWORD \
  docker-compose up $@

