import qi
import io
import sys
import logging
import argparse
import numpy as np
from PIL import Image

from pepper_api import CameraManager, AudioManager2, HeadManager, EyeLEDManager, \
    SpeechManager, CustomMovement
from utils import SpeechProcessor

logging.basicConfig(filename="app.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Pepper():
    def __init__(self, pepper_connection_url):
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
        self.arm_manager = CustomMovement(self.session)

        self.session.registerService("CameraManager", self.camera_manager)
        self.life_service.setAutonomousAbilityEnabled("All", False)


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

    def say_text(self, text):
        self.speech_manager.say(text)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Please enter Pepper's IP address (and optional port number)")
    parser.add_argument("--ip", type=str, nargs='?', default="192.168.0.52")
    parser.add_argument("--port", type=int, nargs='?', default=9559)
    args = parser.parse_args()

    pepper_connection_url = "tcp://" + args.ip + ":" + str(args.port)
    
    channel = grpc.insecure_channel("172.27.72.27:50051")
