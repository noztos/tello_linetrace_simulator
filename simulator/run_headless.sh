#!/bin/bash
BUS_ID=$(nvidia-xconfig --query-gpu-info | grep 'PCI BusID' | sed -r 's/\s*PCI BusID : PCI:(.*)/\1/')
sudo nvidia-xconfig -a --virtual=1280x960 --allow-empty-initial-configuration --enable-all-gpus --busid $BUS_ID
sudo Xorg :0 &
sleep 1
./bin/LinetraceWorld/LinetraceWorld.sh -env=/tmp/simulator_env.json -RenderOffscreen
