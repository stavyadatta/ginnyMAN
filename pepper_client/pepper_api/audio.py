import os
import io
import argparse
import qi
import numpy as np
import time
import sys
import soundfile as sf

class AudioManager2(object):
    def __init__(self,session):
        super(AudioManager2,self).__init__()      
        self.module_name = "AudioManager2"
        # Get the services
        # self.audio_service = session.service("ALAudioDevice")
        # Enable energy input compution 
        # Audio recording setting

        self.threshold = 1000
        self.silence_duration = 1
        self.is_recording = False
        self.last_sound_time = None
        self.sample_rate = 16000
        #self.channels = [0,0,1,0]  # use front microphone
        self.channels = 3  # use front microphone
        self.isProcessingDone = False
        # Audio file setting 
        self.tmppath = "./recordings/"
        self.recording_count = 0
        self.wavfile = self.tmppath + "recording" + str(self.recording_count) + ".wav"
        self.rawfile = self.tmppath + "rawrecording" + str(self.recording_count) + ".raw"
        self.framesCount = 0
        self.nbOfFramesToProcess =30
        self.isRecording = False
        self.sound_list = [3000]
        self.audio_data_buffer = io.BytesIO()

        print("Subscribed to audio service...")


    def init_service(self, session):
        services = session.services()
        for service in services:
            print(service)
        print("\n")
        self.audio_service = session.service("ALAudioDevice")
        self.audio_service.enableEnergyComputation()

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """
        Record the audio data from the front microphone depend on the sound threshold
        """

        front_energy = self.getSound()
        self.sound_list.append(front_energy)
        if len(self.sound_list) > 200:
            self.sound_list.pop(0)
        #self.threshold =  (np.sum(self.sound_list)/ len(self.sound_list))*1.2
        print("Front energy: ", front_energy)

        print("Statues before: ", self.isRecording)
        if self.isRecording: # If is recording:
            #print("count", self.framesCount)
            if front_energy < self.threshold:
                print("current frame", self.framesCount)
                self.framesCount += 1
            else:
                print("reset count")
                self.framesCount = 1
            # self.rawoutput.write(inputBuffer)
            self.audio_data_buffer.write(inputBuffer)
            self.last_sound_time = time.time()
        else:
            if front_energy > self.threshold:
                self.isRecording = True
                self.framesCount = 0
                print("start_processing status changed")
                #print("Front energy: ", front_energy)
        if self.framesCount > self.nbOfFramesToProcess:
            self.isProcessingDone = True
            self.rawoutput.close()
            self.framesCount = 0
            print("Recordng finished")


    def startProcessing(self):
        """
        Subscribe the service and return the audio data
        """
        self.isProcessingDone = False
        self.audio_data_buffer = io.BytesIO()

        self.audio_service.setClientPreferences("AudioManager2", 
                                                self.sample_rate, self.channels, 0)
        self.audio_service.subscribe("AudioManager2")
        while not self.isProcessingDone:
            time.sleep(0.1)
        self.audio_service.unsubscribe("AudioManager2")

        # Read the data from the buffer and save it as a numpy array
        self.audio_data_buffer.seek(0)
        data = self.audio_data_buffer.read()
        # with sf.SoundFile(self.audio_data_buffer, mode='r', samplerate=self.sample_rate,
        #                 channels=1, subtype='PCM_16', format='RAW') as f:
        #     data = f.read()
        #     samplerate = f.samplerate
        return data, self.sample_rate

    def getSound(self):
        return self.audio_service.getFrontMicEnergy()

    def exceed_threshold(self):
        return self.getSound() > self.threshold
    

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
        sys.exit(1)

    app.start() 
    MyAudioManager = AudioManager2(app.session)
    print("audioManager.module_name:" + MyAudioManager.module_name)
    #MyAudioManager.audio_service.unsubscribe(MyAudioManager.module_name)
    app.session.registerService(MyAudioManager.module_name, MyAudioManager)
    # Start processing the audio data
    print("Start processing the audio data...")
    count = 0
    while count < 10:
        audio_data = MyAudioManager.startProcessing()
        #print("Audio data: ", audio_data)
        count += 1
