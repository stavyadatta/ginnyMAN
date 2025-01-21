import cv2
import requests
import base64
import io
import wave
from PIL import Image
import numpy as np

class PepperClientAPI(object):
    def __init__(self, host="127.0.0.1", port=8069):
        self.base_url = "http://{}:{}".format(host, port)

    def get_image(self):
        url = self.base_url + "/get_image"
        response = requests.get(url)
        data = response.json()

        img_base64 = data["image_base64"]
        img_bytes = base64.b64decode(img_base64)
        pil_image = Image.open(io.BytesIO(img_bytes))
        return pil_image

    def get_audio(self):
        url = self.base_url + "/get_audio"
        response = requests.get(url)
        print("response is this")
        data = response.json()

        audio_base64 = data["audio_base64"]
        samplerate = data["samplerate"]

        audio_bytes = base64.b64decode(audio_base64)

        wave_file = wave.open(io.BytesIO(audio_bytes), 'rb')
        frames = wave_file.readframes(wave_file.getnframes())
        wave_file.close()

        return frames, samplerate

    def make_img_compatible(self):
        url = self.base_url + "/make_img_compatible"
        response = requests.get(url)
        data = response.json()

        img_base64 = data["image_base64"]
        img_bytes = base64.b64decode(img_base64)
        pil_image = Image.open(io.BytesIO(img_bytes))
        numpy_image = np.array(pil_image)
        cv2_image = numpy_image[:, :, ::-1]  # Reverse the color channels
        cv2_image = cv2.flip(cv2_image, 0)
        return cv2_image

    def say_text(self, text):
        """
        Calls the /say_text endpoint. Pepper will speak the given text.
        """
        url = self.base_url + "/say_text"
        response = requests.post(url, json={"text": text})
        return response.json()

    def rotate_head(self, vertical_ratio, horizontal_ratio):
        """
        Calls the /rotate_head endpoint.
        Sends two float values: vertical_ratio, horizontal_ratio.
        """
        url = self.base_url + "/rotate_head"
        payload = {
            "vertical_ratio": vertical_ratio,
            "horizontal_ratio": horizontal_ratio
        }
        response = requests.post(url, json=payload)
        return response.json()

    def rotate_head_abs(self):
        """
        Calls the /rotate_head_abs endpoint with no parameters.
        This sets Pepper's head to a default position (0.0, 0.0).
        """
        url = self.base_url + "/rotate_head_abs"
        # Since it doesn't take parameters, we just POST an empty JSON body or no data at all
        response = requests.post(url, json={})
        return response.json()

    def arm_movement(self, joint_names, joint_angles, speed):
        """
        Sends a POST request to /move_arm with the given parameters.
        :param joint_names: list of strings
        :param joint_angles: list of floats
        :param speed: float
        """
        url = self.base_url + "/move_arm"
        payload = {
            "joint_names": joint_names,
            "joint_angles": joint_angles,
            "speed": speed
        }
        response = requests.post(url, json=payload)
        return response.json()


