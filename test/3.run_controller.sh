#!/bin/bash

xhost +
docker run \
  --rm \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  964246069091.dkr.ecr.us-east-1.amazonaws.com/linetrace_control python controller.py --tello_ip 127.0.0.1
