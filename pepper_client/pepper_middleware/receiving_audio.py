import os
import wave
import grpc
import time
from concurrent import futures
from grpc_communication.grpc_pb2 import AudioResponse
from grpc_communication.grpc_pb2_grpc import MediaServiceServicer, add_MediaServiceServicer_to_server

class MediaServer(MediaServiceServicer):
    def __init__(self, save_directory="received_audio"):
        self.save_directory = save_directory
        # Handle directory creation in Python 2
        try:
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)
        except OSError:
            pass  # Ignore if the directory already exists

    def SendAudio(self, request, context):
        # Save the audio data to a WAV file
        audio_path = os.path.join(self.save_directory, "audio_{}.wav".format(int(time.time())))
        print("Are there num_channels ", request.num_channels)
        # Write the audio data to a WAV file
        # try:
        print("Exception here 0?")
        with wave.open(audio_path, "wb") as wav_file:
            print("Exception here 1?")
            wav_file.setnchannels(request.num_channels)  # Number of audio channels
            print("Exception here 2?")
            wav_file.setsampwidth(2)  # PCM_16 -> 2 bytes per sample
            print("Exception here 3?")
            wav_file.setframerate(request.sample_rate)  # Sampling rate
            print("Exception here 4?")
            wav_file.writeframes(request.audio_data)
            print("Exception here 5?")
        # except Exception as e:
            # print("Error saving audio file: {}".format(e))
            # return AudioResponse(status="error", message="Failed to save audio file")

        print("Audio saved to {}".format(audio_path))

        # Respond to the client
        return AudioResponse(status="success", message="Audio saved at {}".format(audio_path))

    # def SendAudio(self, request, context):
    #     # Save the audio data to a file
    #     print("The audio print is coming here?")
    #     audio_path = os.path.join(self.save_directory, "audio_{}.wav".format(int(time.time())))
    #
    #     # Writing raw audio bytes to file
    #     with open(audio_path, "wb") as f:
    #         f.write(request.audio_data)
    #
    #     print "Audio saved to {}".format(audio_path)
    #
    #     # Respond to the client
    #     return AudioResponse(status="success", message="Audio saved at {}".format(audio_path))
    #
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MediaServiceServicer_to_server(MediaServer(), server)
    server.add_insecure_port("[::]:50051")
    print ("Server is running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

