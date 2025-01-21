#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import io
import base64
import logging
import argparse
import cv2
from PIL import Image
from flask import Flask, request, jsonify

# from pepper_client.pepper_server.pepper_flask import PepperFlask
from pepper_flask import PepperFlask
# from pepper_client.pepper_server import PepperFlask
# For Python 2 compatibility: from __future__ import print_function (if needed)
# import wave, struct, etc. as needed for audio
# from pepper_api import CameraManager, AudioManager2, HeadManager, EyeLEDManager, SpeechManager, ArmManager

logging.basicConfig(filename="app.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)


# -------------------- Flask Endpoints -------------------- #

@app.route('/get_image', methods=['GET'])
def flask_get_image():
    """
    Calls PepperFlask.get_image() and returns the image as base64-encoded JPEG.
    """
    image_data = pepper.get_image()
    image_width = image_data[0]
    image_height = image_data[1]

    # Convert to Pillow
    pil_image = Image.frombytes("RGB", (image_width, image_height), str(image_data[6]))

    # Convert Pillow image to base64
    buffered = io.BytesIO()
    pil_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    return jsonify({"image_base64": img_str.decode('utf-8')})


@app.route('/get_audio', methods=['GET'])
def flask_get_audio():
    """
    Calls PepperFlask.get_audio() and returns audio data as base64-encoded WAV + samplerate.
    """
    audio_data, samplerate = pepper.get_audio()
    print("Well I am comning to the get_audio part atleast")

    import wave
    import struct

    byte_io = io.BytesIO()
    wave_file = wave.open(byte_io, 'wb')
    wave_file.setnchannels(1)      # Adjust if your audio is stereo
    wave_file.setsampwidth(2)     # 16-bit audio
    wave_file.setframerate(samplerate)
    print("Am  icoming after the wave")

    # Write frames
    for sample in audio_data:
        wave_file.writeframes(struct.pack('<h', sample))
    wave_file.close()

    print("Wave 2")
    audio_base64 = base64.b64encode(byte_io.getvalue())
    print("Is it coming here for the json ", {
        "audio_base64": audio_base64.decode('utf-8'),
        "samplerate": samplerate
    })
    return jsonify({
        "audio_base64": audio_base64.decode('utf-8'),
        "samplerate": samplerate
    })


@app.route('/make_img_compatible', methods=['GET'])
def flask_make_img_compatible():
    """
    Calls PepperFlask.make_img_compatible(), which returns an OpenCV NumPy image in BGR.
    We re-encode it as base64 JPEG to send over HTTP.
    """
    cv2_image = pepper.make_img_compatible()

    # Convert BGR -> RGB for Pillow
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)

    buffered = io.BytesIO()
    pil_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    return jsonify({"image_base64": img_str.decode('utf-8')})


@app.route('/say_text', methods=['POST'])
def flask_say_text():
    """
    Calls PepperFlask.say_text() to have Pepper speak. 
    Expects JSON payload: {"text": "<something to say>"}
    """
    data = request.get_json(force=True) or {}
    text_to_speak = data.get('text', '')

    pepper.say_text(text_to_speak)

    return jsonify({
        "status": "ok",
        "spoken_text": text_to_speak
    })

@app.route('/rotate_head', methods=['POST'])
def flask_rotate_head():
    """
    Calls PepperFlask.rotate_head(vertical_ratio, horizontal_ratio).
    Expects JSON payload: { "vertical_ratio": float, "horizontal_ratio": float }
    """
    data = request.get_json(force=True) or {}
    vertical_ratio = float(data.get('vertical_ratio', 0.0))
    horizontal_ratio = float(data.get('horizontal_ratio', 0.0))

    pepper.rotate_head(vertical_ratio, horizontal_ratio)

    return jsonify({
        "status": "ok",
        "vertical_ratio": vertical_ratio,
        "horizontal_ratio": horizontal_ratio
    })

@app.route('/rotate_head_abs', methods=['POST'])
def flask_rotate_head_abs():
    """
    Calls PepperFlask.rotate_head_abs() with no parameters.
    This sets the head to some default position, e.g. forward=0, left=0.
    """
    pepper.rotate_head_abs()
    return jsonify({
        "status": "ok",
        "message": "Head rotated to absolute default position"
    })

@app.route('/move_arm', methods=['POST'])
def flask_move_arm():
    """
    Expects JSON with keys:
      "joint_names": list of strings
      "joint_angles": list of floats
      "speed": float
    """
    data = request.get_json(force=True) or {}
    joint_names = data.get('joint_names', [])
    joint_angles = data.get('joint_angles', [])
    speed = data.get('speed', 0.1)  # default speed if not provided

    # Optionally convert to correct types:
    # joint_names = [str(name) for name in joint_names]
    # joint_angles = [float(angle) for angle in joint_angles]
    # speed = float(speed)

    pepper.arm_movement(joint_names, joint_angles, speed)

    return jsonify({
        "status": "ok",
        "joint_names": joint_names,
        "joint_angles": joint_angles,
        "speed": speed
    })



# -------------------- Main Entry Point -------------------- #

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Please enter Pepper's IP address (and optional port number)")
    parser.add_argument("--ip", type=str, nargs='?', default="192.168.0.52")
    parser.add_argument("--port", type=int, nargs='?', default=9559)
    args = parser.parse_args()

    pepper_connection_url = "tcp://" + args.ip + ":" + str(args.port)

    # Instantiate the PepperFlask robot
    pepper = PepperFlask(pepper_connection_url)

    # Run the Flask server on 0.0.0.0:8069
    app.run(host='0.0.0.0', port=8069, debug=False)

