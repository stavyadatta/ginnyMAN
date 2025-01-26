import qi
import cv2
import traceback
import io
import sys
import logging
import grpc
import time
import argparse
import numpy as np
from PIL import Image
from io import BytesIO
from threading import Thread, Lock
from google.protobuf.empty_pb2 import Empty


from grpc_communication.grpc_pb2 import AudioImgRequest, ImageStreamRequest
from grpc_communication.grpc_pb2_grpc import MediaServiceStub, SecondaryChannelStub
from pepper_api import CameraManager, AudioManager2, HeadManager, EyeLEDManager, \
    SpeechManager, ArmManager
from utils import SpeechProcessor
from movement import MovementManager

logging.basicConfig(filename="app.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Pepper():
    def __init__(self, pepper_connection_url, stub, secondary_stub):
        self.stub = stub
        self.secondary_stub = secondary_stub

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
        self.arm_manager = ArmManager(self.session)

        self.session.registerService("CameraManager", self.camera_manager)
        self.life_service.setAutonomousAbilityEnabled("All", False)

        # Make img compatible thread lock 
        self._lock = Lock()

    def get_image(self):
        return self.camera_manager.get_image(raw=True)

    def get_audio(self):
        self.eye_led_manager.set_eyes_blue()
        audio_data, samplerate = self.audio_manager.startProcessing()
        self.eye_led_manager.set_eyes_red()
        return audio_data, samplerate

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
        # cv2.imwrite("image_cv2_format.jpg", cv2_image)

        # Return the OpenCV-compatible NumPy array
        return cv2_image
    
    def center_head(self):
        pass

    def capture_and_stream_images(self):
        try:
            while True:
                cv2_image = self.make_img_compatible()
                height, width, _ = cv2_image.shape
                _, image_data = cv2.imencode(".jpg", cv2_image)

                request = ImageStreamRequest(
                    image_data=image_data.tobytes(),
                    image_format="JPEG",
                    image_width=width,
                    image_height=height,
                    image_description="Captured pepper image"
                )

                # Send the image stream request
                try:
                    self.stub.StreamImages(iter([request]))
                except grpc.RpcError as e:
                    logger.error("Failed to stream image: {}".format(e.details()))
        except KeyboardInterrupt:
            logger.info("Stopping image streaming...")
            raise KeyboardInterrupt()
        except TypeError:
            print("Running the capture stream again")
            self.capture_and_stream_images()

    def get_vertical_and_horizontal_axis(self, box, img_shape, stop_threshold=0.5, vertical_offset=0.5):
        box_center = np.array([box[2] / 2 + box[0] / 2, box[1] * (1 - vertical_offset) + box[3] * vertical_offset])
        frame_center = np.array((img_shape[1] / 2, img_shape[0] / 2))
        diff = frame_center - box_center
        horizontal_ratio = diff[0] / img_shape[1]
        vertical_ratio = diff[1] / img_shape[0]

        if abs(horizontal_ratio) <= stop_threshold and abs(vertical_ratio) <= vertical_offset:
            return (-vertical_ratio * 0.4, horizontal_ratio * 0.6)
        else:
            return (0, 0)

    def is_zero_list(self, box):
        for i in box:
            if i == 0:
                return True
        return False

    def arm_movement(self, joint_names, joint_angles, speed):
        self.arm_manager.movement(joint_names, joint_angles, speed)

    def head_management(self):
        try:
            cv2_image = self.make_img_compatible()
            img_shape = cv2_image.shape
            request = Empty()
            person_missing = 0
            while True:
                time.sleep(1)
                bbox = self.stub.GetBbox(request)
                box = [bbox.x1, bbox.y1, bbox.x2, bbox.y2]
                if not self.is_zero_list(box):
                    person_missing += 1
                    vertical_ratio, horizontal_ratio = self.get_vertical_and_horizontal_axis(box, img_shape)

                    # self.head_manager.rotate_head(forward=float(vertical_ratio), left=float(horizontal_ratio))
                elif self.is_zero_list(box) and person_missing > 30:
                    person_missing = 0
                    self.head_manager.rotate_head_abs()
        except KeyboardInterrupt:
            logger.info("Stopping the head management")
            raise KeyboardInterrupt

        except Exception as e:
            print("Some error in head_management, donot know ", e)
            traceback.print_exc()


    def send_audio_video(self):
        audio_data, sample_rate = self.get_audio()
        try:
            last_frame = self.make_img_compatible()
        except TypeError:
            print("Send audio was not receiving last frame")
            self.send_audio_video()
        try:
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
                api_task="Captured Pepper"
            )

            # Send the request to the gRPC server
            try:
                response = self.stub.SendAudioImg(request)
            except grpc.RpcError as e:
                print("gRPC in sending audio error: {} - " \
                "{}".format(e.code(), e.details()))

            time.sleep(1)  # Adjust delay as needed
        except UnboundLocalError as e:
            print("Unbounded local error occuring")
            traceback.print_exc()
            self.send_audio_video()

    def receive_llm_response(self):
        speech_processor = SpeechProcessor(self.speech_manager.say)
        
        request = Empty()
        response_stream = stub.LLmResponse(request)


        builder_thread = Thread(
            target=speech_processor.build_sentences, 
            args=(response_stream,)
        )
        speaker_thread = Thread(
            target=speech_processor.execute_response,
            args=(self,)
        )

        builder_thread.start()
        speaker_thread.start()

        # Wait for threads to complete
        builder_thread.join()
        speech_processor.is_running = False
        speaker_thread.join()

        # if speech_processor.movement:
        #     print("Is this coming here, do you think its coming in the movement")
        #     MovementManager(speech_processor.json_text, self)
        #     speech_processor.json_text = ''

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
    secondary_stub = SecondaryChannelStub(channel)

    p = Pepper(pepper_connection_url, stub, secondary_stub)
    image_thread = Thread(target=p.capture_and_stream_images, args=()) 
    image_thread.daemon = True
    image_thread.start()

    head_thread = Thread(target=p.head_management, args=())
    head_thread.daemon = True
    head_thread.start()
    
    try:
        while True:
            p.send_audio_video()
            p.receive_llm_response()
    except KeyboardInterrupt:
        p.close()
        print("Program interrupted by user.")
        queue_response = stub.ClearQueue(Empty())
        if queue_response.removed:
            print("server queue is cleaned")
        else:
            print("Some issue in the cleaning the server queue")
        exit()
        image_thread.join()
        head_thread.join()
    except Exception as e:
        # Ensure resources are cleaned up
        print("the p close is getting called because of the following issues ", e)
        queue_response = stub.ClearQueue(Empty())
        if queue_response.removed:
            print("server queue is cleaned")
        else:
            print("Some issue in the cleaning the server queue")
        traceback.print_exc()
        p.close()
