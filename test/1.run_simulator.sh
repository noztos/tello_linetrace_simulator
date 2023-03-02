#!/bin/bash

docker run \
  --gpus all \
  -it \
  --rm \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  964246069091.dkr.ecr.us-east-1.amazonaws.com/simulator \
  ./bin/TelloLineTraceAirSim.linux.bin/TelloLineTraceAirSim.sh -RenderOffscreen
