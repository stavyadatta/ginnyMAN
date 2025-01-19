import qi
import argparse
import sys
import time

class ArmManager:
    def __init__(self, session):
        self.motion_service = session.service("ALMotion")
        # Wake up the robot
        print("Initialized ArmManager and woke up the robot.")

    def movement(self, joint_names: list, joint_angles: list, speed: list):
        try:
            self.motion_service.setAngles(joint_names, joint_angles, speed)
        except Exception as e:
            print("An error occurred while moving the arm {}".format(e))

    def raise_arm(self, joint_name="LShoulderPitch", upward_angle=-1.0, downward_angle=1.5, speed=0.2):
        """
        Raises and then lowers the specified arm joint.

        Args:
            joint_name: str
                The name of the joint to move.
            upward_angle: float
                The angle in radians to move the joint upwards.
            downward_angle: float
                The angle in radians to move the joint downwards.
            speed: float
                The speed fraction for the movement (0 to 1).
        """
        try:
            # Move the arm upwards
            self.motion_service.setAngles(joint_name, upward_angle, speed)
            print("Moving {} upwards to angle {}.".format(joint_name, upward_angle))
            time.sleep(2)  # Wait for the movement to complete

            # Move the arm downwards
            self.motion_service.setAngles(joint_name, downward_angle, speed)
            print("Moving {} downwards to angle {}.".format(joint_name, downward_angle))
            time.sleep(2)  # Wait for the movement to complete

        except Exception as e:
            print("An error occurred while moving the arm: {}".format(e))

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
        arm_manager = ArmManager(session)
        arm_manager.raise_arm()

    except Exception as e:
        print("Cannot connect to Pepper robot at {}:{}. Error: {}".format(args.ip, args.port, e))
        sys.exit(1)

