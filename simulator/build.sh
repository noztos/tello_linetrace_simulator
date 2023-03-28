#!/bin/sh
cd `dirname $0`

unzip -o LinetraceWorld.zip -d bin

docker build -t simulator -f Dockerfile .
