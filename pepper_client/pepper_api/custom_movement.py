import qi
import sys
import time
import json
import math
import argparse

DEG_TO_RAD = math.pi / 100
class CustomMovement:
    def __init__(self, session, robot_posture):
        self.motion_service = session.service("ALMotion")
        # Wake up the robot
        self.robot_posture = robot_posture
        print("Initialized ArmManager and woke up the robot.")


    def extract_json_from_text(self, text):
        """
        Extracts and parses JSON embedded within a text string.
        
        :param text: The input string containing JSON and/or other text.
        :return: The parsed JSON as a Python dictionary if found.
        :raises ValueError: If no valid JSON is found in the text.
        """
        # Regular expression to find JSON-like structures in the text
        try:
            print("Well trying the json loads thingy")
            return json.loads(text)
        except json.JSONDecodeError:
            print("Entering the error")
            raise ValueError("Found a JSON-like structure, but it is not valid JSON.")
        

    def movement(self, joint_names, joint_angles, speed):
        for name, angle, sp in zip(joint_names, joint_angles, speed):
            radian_angle = angle * DEG_TO_RAD
            try:
                self.motion_service.angleInterpolationWithSpeed(name, radian_angle, sp)
            except Exception as e:
                print("An error occurred while moving the arm {}".format(e))

    def __call__(self, llm_response):
        action_json = self.extract_json_from_text(llm_response)
        print("The json action is \n \n \n \n ", action_json)
        action_items = action_json.get("action_list")
        joint_names = []
        angles = []
        speed = []

        for action in action_items:
            joint_names.append(action.get("joint_name"))
            angles.append(action.get("angle"))
            speed.append(action.get("speed"))

        self.movement(joint_names, angles, speed)
        self.robot_posture.goToPosture("StandInit", 0.2)
        time.sleep(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="Robot IP address")
    parser.add_argument("--port", type=int, default=9559, help="Robot port number")
    args = parser.parse_args()

    # Connect to the robot
    try:
        session = qi.Session()
        session.connect("tcp://{}:{}".format(args.ip, args.port))
        print("Connected to Pepper robot.")

        # Initialize the ArmManager and perform arm movement
        arm_manager = CustomMovement(session)
        arm_manager.raise_arm()

    except Exception as e:
        print("Cannot connect to Pepper robot at {}:{}. Error: {}".format(args.ip, args.port, e))
        sys.exit(1)

