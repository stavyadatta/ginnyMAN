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

    def calculate_rms_energy(self, audio_data):
        """Calculate RMS energy for a specific mic."""
        # Extract the data for the specific microphone
        audio_array = np.array(audio_data, dtype=np.int16)  # Convert to NumPy array
        rms = np.sqrt(np.mean(audio_array**2))
        return rms

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """
        Record the audio data only when the frontMicEnergy crosses a threshold,
        and stop when it's below the threshold for 10 consecutive loops.
        """
        energy_threshold = 450
        max_below_thresh_loops = 10  # Stop recording after 10 loops below threshold


        # Get the front mic energy
        current_energy = self.audio_service.getFrontMicEnergy()
        print("The front mic energy is {}".format(current_energy))

        if current_energy > energy_threshold:
            # Reset the below-threshold counter when the energy crosses the threshold
            self.below_threshold_count = 0
            self.first_high_thresh = True
            
            # Start recording
            self.audio_data_buffer.write(inputBuffer)

        else:
            # Increment the below-threshold counter if energy is below the threshold
            if self.first_high_thresh:
                self.below_threshold_count += 1
                print("Below threshold count: {}".format(self.below_threshold_count))
                self.audio_data_buffer.write(inputBuffer)

                # Stop recording after 10 consecutive loops below the threshold
                if self.below_threshold_count >= max_below_thresh_loops:
                    self.isProcessingDone = True
                    self.first_high_thresh = False
                    print("Energy below threshold for {} loops".format(max_below_thresh_loops))
                    self.below_threshold_count = 0


    # def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
    #     """
    #     Record the audio data and accumulate until the target duration is reached.
    #     """
    #     print("The front mic energy is {}".format(self.audio_service.getFrontMicEnergy()))
    #
    #     self.audio_data_buffer.write(inputBuffer)
    #     current_frames = len(self.audio_data_buffer.getvalue()) // 2  # Each sample is 2 bytes (PCM_16)
    #
    #     if current_frames >= self.target_frames:
    #         self.isProcessingDone = True
    #         print("Reached target duration of {} seconds".format(self.recording_duration))

    def startProcessing(self):
        """
        Subscribe the service and return the accumulated audio data.
        """
        self.isProcessingDone = False
        self.audio_data_buffer = io.BytesIO()
        self.below_threshold_count = 0
        self.first_high_thresh = False

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
