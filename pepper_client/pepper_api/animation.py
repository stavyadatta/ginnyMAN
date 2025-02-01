import qi
import time

class CustomMovement:
    def __init__(self, session):
        self.animation_service = session.service("ALMotion")
        print("Initialized ALMotion")

    def perform_animation(self, animation_name):
        self.animation_service.run(f"hapy_movement/{animation_name}")

