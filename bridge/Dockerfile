FROM python:3.9.10-slim-buster

RUN apt-get update \
    &&  apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN pip install numpy --upgrade \
    &&  pip install msgpack-rpc-python \
    &&  pip install airsim==1.7.0

COPY bridge.py bridge.py
