import os
import grpc
import time
from concurrent import futures
from grpc_communication.grpc_pb2_grpc import MediaServiceServicer, add_MediaServiceServicer_to_server

class MediaServer(MediaServiceServicer):
    def __init__(self, save_directory="received_audio"):
        self.save_directory = save_directory
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def SendAudio(self, request, context):
        # Save the audio data to a file
        audio_path = os.path.join(self.save_directory, f"audio_{int(time.time())}.wav")

        # Writing raw audio bytes to file
        with open(audio_path, "wb") as f:
            f.write(request.audio_data)

        print(f"Audio saved to {audio_path}")

        # Respond to the client
        return AudioResponse(status="success", message=f"Audio saved at {audio_path}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MediaServiceServicer_to_server(MediaServer(), server)
    server.add_insecure_port("[::]:50051")
    print("Server is running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

