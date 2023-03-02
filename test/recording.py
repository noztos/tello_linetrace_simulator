import airsim
import argparse
import sys

airsim_client = airsim.MultirotorClient()
airsim_client.confirmConnection()
airsim_client.enableApiControl(True)

if sys.argv[1] == 'start':
    airsim_client.startRecording()
elif sys.argv[1] == 'stop':
    airsim_client.stopRecording()
