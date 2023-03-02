#!/bin/bash

docker run \
  --rm \
  --net=host \
  964246069091.dkr.ecr.us-east-1.amazonaws.com/bridge python bridge.py
