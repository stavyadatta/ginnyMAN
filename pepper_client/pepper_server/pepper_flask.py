import qi
import cv2
import numpy as np
from PIL import Image

from pepper_api import CameraManager, AudioManager2, HeadManager, EyeLEDManager, \
    SpeechManager, CustomMovement


class PepperFlask(object):
    def __init__(self, pepper_connection_url):
        # Initialize the Qi Application
        app_qi = qi.Application(["AudioManager2", "--qi-url=" + pepper_connection_url])
        app_qi.start()
        self.session = app_qi.session

        print("Connected to Pepper at: {}".format(pepper_connection_url))
        print("Subscribing to live service...")

        # Example: If your environment has these managers defined elsewhere
        self.life_service = self.session.service("ALAutonomousLife")
        self.camera_manager = CameraManager(self.session, resolution=5, colorspace=11, fps=30)
        self.speech_manager = SpeechManager(self.session)
        self.audio_manager = AudioManager2(self.session)
        self.eye_led_manager = EyeLEDManager(self.session)
        self.head_manager = HeadManager(self.session)
        self.arm_manager = CustomMovement(self.session)

        # Registering services if needed
        self.session.registerService("AudioManager2", self.audio_manager)
        self.audio_manager.init_service(self.session)
        self.session.registerService("CameraManager", self.camera_manager)

        # Turn off autonomous abilities
        self.life_service.setAutonomousAbilityEnabled("All", False)

    def get_image(self):
        """
        Return the raw image data from Pepper's camera as provided by CameraManager.
        Usually: [width, height, number_of_layers, ..., raw_bytes_in_index_6].
        """
        return self.camera_manager.get_image(raw=True)

    def get_audio(self):
        """
        Capture audio data from Pepper. Returns (audio_data, samplerate).
        """
        self.eye_led_manager.set_eyes_blue()
        audio_data, samplerate = self.audio_manager.startProcessing()
        self.eye_led_manager.set_eyes_red()
        return audio_data, samplerate

    def make_img_compatible(self):
        """
        Convert the raw NAOqi image into a Pillow image, then into an OpenCV-compatible NumPy array in BGR.
        """
        raw_image = self.get_image()
        image_width = raw_image[0]
        image_height = raw_image[1]

        pil_image = Image.frombytes("RGB", (image_width, image_height), str(raw_image[6]))
        numpy_image = np.array(pil_image)

        cv2_image = numpy_image[:, :, ::-1]  # Convert from RGB to BGR
        cv2_image = cv2.flip(cv2_image, 0)
        return cv2_image

    def say_text(self, text):
        """
        Use Pepper's speech manager to speak out loud.
        """
        self.speech_manager.say(text)

    def rotate_head(self, vertical_ratio, horizontal_ratio):
        """
        Rotate Pepper's head using the head_manager.
        The manager expects two floats: forward=vertical_ratio, left=horizontal_ratio.
        """
        self.head_manager.rotate_head(forward=vertical_ratio, left=horizontal_ratio)

    def rotate_head_abs(self):
        self.head_manager.rotate_head_abs()

    def arm_movement(self, joint_names, joint_angles, speed):
       self.arm_manager.movement(joint_names, joint_angles, speed)


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

