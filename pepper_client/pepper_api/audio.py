import os
import io
import argparse
import qi
import numpy as np
import time
import sys
import soundfile as sf

class AudioManager2(object):
    def __init__(self, session, recording_duration=2):
        super(AudioManager2, self).__init__()
        self.module_name = "AudioManager2"
        self.threshold = 1000
        self.is_recording = False
        self.last_sound_time = None
        self.sample_rate = 16000
        self.channels = 1  # Mono audio
        self.recording_duration = recording_duration  # Target duration in seconds
        self.target_frames = self.sample_rate * self.channels * self.recording_duration
        self.audio_data_buffer = io.BytesIO()
        print("Subscribed to audio service...")

    def init_service(self, session):
        self.audio_service = session.service("ALAudioDevice")
        self.audio_service.enableEnergyComputation()

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """
        Record the audio data and accumulate until the target duration is reached.
        """
        self.audio_data_buffer.write(inputBuffer)
        current_frames = len(self.audio_data_buffer.getvalue()) // 2  # Each sample is 2 bytes (PCM_16)

        if current_frames >= self.target_frames:
            self.isProcessingDone = True
            print("Reached target duration of {} seconds".format(self.recording_duration))

    def startProcessing(self):
        """
        Subscribe the service and return the accumulated audio data.
        """
        self.isProcessingDone = False
        self.audio_data_buffer = io.BytesIO()

        self.audio_service.setClientPreferences(self.module_name, 
                                                self.sample_rate, self.channels, 0)
        self.audio_service.subscribe(self.module_name)
        while not self.isProcessingDone:
            time.sleep(0.1)
        self.audio_service.unsubscribe(self.module_name)

        # Get accumulated audio data
        self.audio_data_buffer.seek(0)
        audio_data = self.audio_data_buffer.read()
        return audio_data, self.sample_rate

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.0.52",
                        help="Robot IP address. On robot or Local Naoqi: use '192.168.137.26'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    args = parser.parse_args()

    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["AudioManager2", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
                                                                                              "Please check your "
                                                                                              "script arguments. Run "
                                                                                              "with -h option for "
                                                                                              "help.")
