import cv2
import grpc
import motion

from grpc_communication.grpc_pb2 import SecondaryData, Image

from .base_secondary_communication import BaseSecondaryCommunication

LEFT_LIMIT = -100
RIGHT_LIMIT = 100

class _ObjectLookup(BaseSecondaryCommunication):
    def __init__(self):
        self.current_head_pitch = 0.0
        self.current_head_yaw = 0.0
        self.seen_all = False
        self.head_position = 0
        self.moving_right = False
        self.object_name = ""

    def move_head(self, speed=0.1):
        if self.seen_all:
            print('Has seen everything')
            return

        if not self.moving_right:
            new_position = self.head_position - 10

            if new_position < -100:
                self.head_position = 0
                self.moving_right = True
                self.head_position += 10
            else:
                self.head_position = new_position
        
        else:
            new_position = self.head_position + 10

            if new_position > 100:
                self.head_position = 100
                self.seen_all = True
                print("Moved the head to rightmost")
            else:
                self.head_position = new_position

        angle_in_radians = self.head_position * motion.TO_RAD
        self.pepper.head_manager.rotate_head(left=float(angle_in_radians))

    def is_object_found(self, response):
        if response.mode == "not done":
            self.move_head()
            return False
        elif response.mode == "done":
            self.pepper.speech_manager.say("Found the {}".format(self.object_name))
            return True
            
    def __call__(self, secondary_details, pepper):
        super().__call__(secondary_details, pepper)
        self.object_name = secondary_details.get("object_name")
        object_dict = {"object_name": self.object_name}
        api_details = self.develop_api_details(object_dict)
        grpc_task = self.develop_full_details("ObjectLookup", api_details)
        keep_going = True

        while keep_going:
            img = self.pepper.make_img_compatible()
            height, width, _ = img.shape
            _, image_data = cv2.imencode(".jpg", img)
            image_grpc = Image(
                image_data=image_data
            )
            secondary_data = SecondaryData(
                api_task=grpc_task,
                image=image_grpc
            )
            try:
                response = self.secondary_stub.Secondary_media_manager(secondary_data)
                keep_going = not self.is_object_found(response)
                
            except grpc.RpcError as e:
                print("gRPC in sending audio error: {} - " \
                "{}".format(e.code(), e.details()))
