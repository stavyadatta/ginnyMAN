import qi
import argparse
import sys
import time
import requests

class MovementManager:
    def __init__(self, session, connection_url):
        self.motion_service  = session.service("ALMotion")
        self.posture_service = session.service("ALRobotPosture")
        # Disable autonomous life
        self.alife_service = session.service("ALAutonomousLife")
        self.alife_service.setState("disabled")
        # Wake up the robot
        self.motion_service.wakeUp()
        self.reset_posture()
        # Enable body stiffness
        self.motion_service.setStiffnesses("Body", 1.0)
        print("MovementManager initialized.")
        self.address = connection_url

    def reset_posture(self, speed=0.5):
        """Makes the robot stand up straight. Used to reset posture."""
        self.posture_service.goToPosture("StandInit", speed)

    def walk_forward(self, distance=1.0):
        """Makes the robot walk forward a specified distance."""
        # Move the robot forward
        self.motion_service.moveTo(distance, 0.0, 0.0)
        print("Robot walked forward {} meter(s).".format(distance))

    def stop(self):
        """Stops the robot's movement."""
        self.motion_service.stopMove()
        print("Robot movement stopped.")

    def walkToward(self, x=0, y=0, theta=0, verbose=False):
        """Alternative method to make the robot walk."""
        # Ensure the 'requests' library is imported
        # Update 'self.address' with the correct robot address
        headers = {'content-type': "/locomotion/walkToward"}
        response = requests.post(
            self.address + headers["content-type"],
            params={
                'x': str(x),
                'y': str(y),
                'theta': str(theta),
                'verbose': str(1 if verbose else 0)
            }
        )
        if verbose:
            print("walkToward(x={}, y={}, theta={})".format(x, y, theta))
        if response.status_code != 200:
            print("Failed to send walkToward command.")


    def terminate(self, speed=0.5):
        """Puts the robot to rest upon termination."""
        self.posture_service.goToPosture("Sit", speed)
        self.motion_service.rest()
        print("Robot is now resting.")

    def __del__(self):
        self.terminate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.137.131",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    connection_url = str("tcp://" + args.ip + ":" + str(args.port))
    try:
        session.connect(connection_url)
    except RuntimeError:
        print("Can't connect to Naoqi at ip \"{}\" on port {}.\n"
              "Please check your script arguments. Run with -h option for help.".format(args.ip, args.port))
        sys.exit(1)

    manager = MovementManager(session, connection_url)
    # Make the robot walk forward 1 meter
    manager.walkToward(x=1)
    # Clean up
    del manager

