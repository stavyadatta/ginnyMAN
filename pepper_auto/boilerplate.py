import cv2
import grpc
import traceback
import queue
import numpy as np

# When calling stub.GetImg use it like this self.stub.GetImg(Empty())
from google.protobuf.empty_pb2 import Empty
from ginny_server.core_api import Grok, YOLODetector

from grpc_communication.pepper_auto_pb2 import ImageChunk, ConfirmationChunk, ExecuteParam, SentenceParam
from grpc_communication.pepper_auto_pb2_grpc import PepperAutoStub
from ginny_server.core_api import ChatGPT, Grok, YOLODetector

class AutoPepper:
    def __init__(self, stub: PepperAutoStub):
        self.stub = stub

        # Grok, ChatGPT and YOLODetector are objects, not classes, no need to declare
        # Initialize YOLODetector, donot use self.yolo = YOLODetector()
        # Donot use self.grok = Grok()
        # Donot use self.chatgpt = ChatGPT()
        self.yolo = YOLODetector
        self.grok = Grok
        self.chatgpt = ChatGPT

    def __call__(self):
        # Write your code here
        # Hints, set classes in YOLODetector with self.yolo.set_classes(classes)
        # here class is a List[str] for example ["phone"] or ["person", "face"]
        pass


if __name__ == "__main__":
    channel = grpc.insecure_channel("172.27.92.157:50051")
    stub = PepperAutoStub(channel)
    auto_pepper = AutoPepper(stub)
    auto_pepper()
