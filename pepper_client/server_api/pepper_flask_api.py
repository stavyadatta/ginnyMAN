
import requests
import base64
import io
import wave
from PIL import Image

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
        return pil_image

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


# Example usage
if __name__ == "__main__":
    client_api = PepperClientAPI(host="127.0.0.1", port=8069)

    # Test saying something
    result = client_api.say_text("Hello from Python 2!")
    print("Response from /say_text:", result)

    # Test image
    image = client_api.get_image()
    print("Retrieved image from server, size: {}".format(image.size))
    image.save("test_image.jpg")

    # Test audio
    audio_frames, sr = client_api.get_audio()
    print("Retrieved audio, samplerate: {}".format(sr))
    with open("test_audio.wav", "wb") as f:
        f.write(audio_frames)

    # Test make_img_compatible
    compatible_image = client_api.make_img_compatible()
    print("Retrieved make_img_compatible image from server, size: {}".format(compatible_image.size))
    compatible_image.save("test_image_compatible.jpg")

