#!/bin/bash

export AIRSIM_RECORDING_DIR=/tmp/airsim
mkdir -p $AIRSIM_RECORDING_DIR
chmod 777 $AIRSIM_RECORDING_DIR

docker-compose up -d
sleep 10
python3 recording.py start
python3 test.py
python3 recording.py stop
sleep 10
docker-compose down
