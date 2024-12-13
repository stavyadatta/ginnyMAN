import qi
import cv2
import io
import sys
import grpc
import time
import argparse
import numpy as np
from PIL import Image
from io import BytesIO
from threading import Thread
from google.protobuf.empty_pb2 import Empty


from grpc_communication.grpc_pb2 import AudioImgRequest
from grpc_communication.grpc_pb2_grpc import MediaServiceStub
from pepper_api import CameraManager, AudioManager2, HeadManager, EyeLEDManager, \
    SpeechManager, SpeechProcessor


class Pepper():
    def __init__(self, pepper_connection_url, stub):
        self.stub = stub

        app = qi.Application(["AudioManager2", "--qi-url=" + pepper_connection_url])
        app.start()
        self.session = app.session

        print("Connected to the Pepper!")
        print("Subscribing to live service...")
        self.life_service = self.session.service("ALAutonomousLife")
        self.camera_manager = CameraManager(self.session, resolution=5, colorspace=11, fps=30)

        self.speech_manager = SpeechManager(self.session)
        self.audio_manager = AudioManager2(self.session)


        self.eye_led_manager = EyeLEDManager(self.session)
        self.session.registerService("AudioManager2", self.audio_manager)
        self.audio_manager.init_service(self.session)


        self.head_manager = HeadManager(self.session)

        self.session.registerService("CameraManager", self.camera_manager)
        self.life_service.setAutonomousAbilityEnabled("All", False)

    def get_image(self):
        return self.camera_manager.get_image(raw=True)

    def get_audio(self):
        audio_data, samplerate = self.audio_manager.startProcessing()
        return audio_data, samplerate

    def send_img(self):
        # Add your image sending gprc code here
        while True:
            raw_image = self.get_image()

            image_format = "JPEG"
            image_width = raw_image[0]
            image_height = raw_image[1]
            pil_image = Image.frombytes(
                "RGB", (image_width, image_height), bytes(raw_image[6])
            )
            print("The image is being developed here ", pil_image)
            buffer = BytesIO()
            pil_image.save(buffer, format=image_format)
            buffer.seek(0)
            
            request = ImageRequest(
                image_data=buffer.read(),
                format=image_format,
                width=image_width,
                height=image_height,
                description="Image captured by Pepper"
            )

            # Send the request to the gRPC server
            try:
                response = self.stub.SendImage(request)
                # print(f"Response from server: {response.status} - {response.message}")
            except grpc.RpcError as e:
                # print(f"gRPC error: {e.code()} - {e.details()}")
                print("some error")
            

    def make_img_compatible(self):
        raw_image = self.get_image()

        # Extract image dimensions and raw bytes
        image_width = raw_image[0]
        image_height = raw_image[1]
        pil_image = Image.frombytes(
            "RGB", (image_width, image_height), bytes(raw_image[6])
        )
        pil_image.save("image_pil_format.jpg")
        # Convert the PIL image to a NumPy array
        numpy_image = np.array(pil_image)

        # Convert the image from RGB (PIL) to BGR (OpenCV format)
        cv2_image = numpy_image[:, :, ::-1]  # Reverse the color channels
        cv2_image = cv2.flip(cv2_image, 0)
        cv2.imwrite("image_cv2_format.jpg", cv2_image)

        # Return the OpenCV-compatible NumPy array
        return cv2_image

    def send_audio(self):
        audio_data, sample_rate = self.get_audio()
        last_frame = self.make_img_compatible()
        height, width, _ = last_frame.shape
        _, image_data = cv2.imencode(".jpg", last_frame)

        request = AudioImgRequest(
            audio_data=audio_data,
            sample_rate=sample_rate,
            num_channels=1,  # Assuming mono audio
            audio_encoding="PCM_16",
            audio_description="Audio captured by Pepper",
            image_data=image_data.tobytes(),
            image_format="JPEG",
            image_width=width,
            image_height=height,
            image_description="Captured Pepper"
        )

        # Send the request to the gRPC server
        try:
            response = self.stub.SendAudioImg(request)
        except grpc.RpcError as e:
            print("gRPC in sending audio error: {} - " \
            "{}".format(e.code(), e.details()))

        time.sleep(1)  # Adjust delay as needed

    def receive_llm_response(self):
        speech_processor = SpeechProcessor(self.speech_manager)
        
        request = Empty()
        response_stream = stub.LLmResponse(request)


        builder_thread = Thread(
            target=speech_processor.build_sentences, 
            args=(response_stream,)
        )
        speaker_thread = Thread(target=speech_processor.say_sentences)

        builder_thread.start()
        speaker_thread.start()

        # Wait for threads to complete
        builder_thread.join()
        speech_processor.is_running = False
        speaker_thread.join()


    def close(self):
    # Shut down services and clean up resources
        print("Shutting down Pepper services...")
        del self.camera_manager
        del self.life_service
        del self.speech_manager
        del self.audio_manager
        del self.head_manager
        del self.eye_led_manager
        self.session.close()
        print("Pepper resources have been cleaned up.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Please enter Pepper's IP address (and optional port number)")
    parser.add_argument("--ip", type=str, nargs='?', default="192.168.0.52")
    parser.add_argument("--port", type=int, nargs='?', default=9559)
    args = parser.parse_args()

    pepper_connection_url = "tcp://" + args.ip + ":" + str(args.port)
    
    channel = grpc.insecure_channel("172.27.72.27:50051")
    stub = MediaServiceStub(channel)
    
    p = Pepper(pepper_connection_url, stub)
    try:
        while True:
            p.send_audio()
            p.receive_llm_response()
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        # Ensure resources are cleaned up
        p.close()
