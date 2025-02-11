import cv2
import math
import logging
import traceback
import numpy as np

from pepper_auto_pb2 import ImageChunk, ExecuteParam, SentenceParam, ConfirmationChunk
from pepper_auto_pb2_grpc import PepperAutoServicer

# Configure logging
log_file = "/workspace/Documents/ginnyMAN/app.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PepperAutoController(PepperAutoServicer):
    def __init__(self, pepper) -> None:
        logging.info("Entering the PepperAutoController class")
        self.pepper = pepper

    def GetImg(self, request, context):
        try:
            logging.info("Processing GetImg request")
            cv2_image = self.pepper.make_img_compatible()
            _, image_data = cv2.imencode(".jpg", cv2_image)
            logging.info("Image successfully encoded")
            
            cv2.imwrite("/workspace/Documents/ginnyMAN/test.jpg", cv2_image)
            logging.info("Image successfully saved to /workspace/Documents/ginnyMAN/test.jpg")

            img_chunk = ImageChunk(image_data=image_data.tobytes())
            return img_chunk
        except Exception as e:
            logging.error("Error in GetImg: %s", traceback.format_exc())
            context.set_code(500)
            context.set_details(str(e))
            return ImageChunk()

    def ExecuteAction(self, request, context):
        try:
            logging.info("Processing ExecuteAction request with joint: %s, angle: %f, speed: %f", 
                         request.joint_name, request.angle, request.speed)
            joint_names = [request.joint_name]
            radian_angle = math.radians(request.angle)
            angles = [radian_angle]
            speeds = [request.speed]

            self.pepper.custom_movement.movement(joint_names, angles, speeds)
            logging.info("Action executed successfully")

            return ConfirmationChunk(confirmed=True)
        except Exception as e:
            logging.error("Error in ExecuteAction: %s", traceback.format_exc())
            context.set_code(500)
            context.set_details(str(e))
            return ConfirmationChunk(confirmed=False)

    def RobotSay(self, request, context):
        try:
            logging.info("Processing RobotSay request with sentence: '%s'", request.sentence_to_say)
            self.pepper.speech_manager.say(request.sentence_to_say)
            logging.info("Sentence spoken successfully")

            return ConfirmationChunk(confirmed=True)
        except Exception as e:
            logging.error("Error in RobotSay: %s", traceback.format_exc())
            context.set_code(500)
            context.set_details(str(e))
            return ConfirmationChunk(confirmed=False)

