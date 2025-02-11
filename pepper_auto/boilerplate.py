import cv2
import grpc
import traceback
import queue

from grpc_communication.pepper_auto_pb2 import ImageChunk, ConfirmationChunk, ExecuteParam, SentenceParam
from grpc_communication.pepper_auto_pb2_grpc import PepperAutoStub
from ginny_server.core_api import ChatGPT, Grok, YOLODetector

class AutoPepper:
    def __init__(self, stub: PepperAutoStub):
        self.stub = stub

    def __call__(self):
        # Write your code here
        pass


if __name__ == "__main__":
    channel = grpc.insecure_channel("172.27.92.157:50051")
    stub = PepperAutoStub(channel)
    auto_pepper = AutoPepper(stub)
    auto_pepper()
