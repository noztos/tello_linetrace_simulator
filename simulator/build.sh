#!/bin/sh
cd `dirname $0`

FILE_ID=1byZo6e2xhInRC_FknhRtpQIYriqKfy_L
FILE_NAME=bin/TelloLineTraceAirSim.linux.bin.zip
if [ ! -e $FILE_NAME ]; then
    mkdir -p bin
    curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${FILE_ID}" > /dev/null
    CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"
    curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&id=${FILE_ID}&confirm=${CODE}" -o ${FILE_NAME}
fi
if [ ! -d bin/TelloLineTraceAirSim.linux.bin ];then
    unzip -o $FILE_NAME -d bin
fi

#docker build -t simulator -f Dockerfile .
