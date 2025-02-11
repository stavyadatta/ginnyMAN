import cv2
import json
import traceback
import numpy as np

from pepper_auto_pb2 import ImageChunk, ExecuteParam, SentenceParam, ConfirmationChunk
from pepper_auto_pb2_grpc import PepperAutoServicer

class PepperAutoController(PepperAutoServicer):
    def __init__(self, pepper) -> None:
        self.pepper = pepper


    def GetImg(self, request, context):
        cv2_image = self.pepper.make_img_compatible()
        _, image_data = cv2.imencode(".jpg", cv2_image)

        img_chunk = ImageChunk(
            image_data=image_data.tobytes()
        )

        return img_chunk

    def ExecuteAction(self, request, context):
        joint_names = [request.joint_name]
        angles = [request.angle]
        speeds = [request.speed]

        self.pepper.custom_movement.movement(joint_names, angles, speeds)

        confirm = True

        return ConfirmationChunk(
            confirmed=confirm
        )


    def RobotSay(self, request, context):
        sentence_to_say = request.sentence_to_say

        self.pepper.speech_manager.say(sentence_to_say)

        return ConfirmationChunk(
            confirmed=True
        )
