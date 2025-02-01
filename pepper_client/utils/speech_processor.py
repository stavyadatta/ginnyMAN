import re
import sys
import json
from google.protobuf.empty_pb2 import Empty

import grpc
from collections import deque

from movement import CustomMovementManager
from secondary_communication import SecondaryCommunication

def is_valid_json(text):
    try:
        json.loads(text)
        return True
    except Exception:
        return False

class SpeechProcessor:
    def __init__(self, speech_function):
        self.sentence_queue = deque()  # Queue for sentences
        self.current_sentence = ""
        self.speech_function = speech_function  # Instance of Pepper's speech manager
        self.is_running = True  # Flag to control the threads
        self.movement = False

    def build_sentences(self, response_stream, pepper):
        """
        Build sentences from streamed words and add them to the queue.
        :param response_stream: gRPC response stream from LLM.
        """
        try:
            for chunk in response_stream:
                sys.stdout.write(chunk.text + "")
                sys.stdout.flush()

                # Append chunk words to the current sentence
                self.current_sentence += chunk.text

                # Check for sentence-ending punctuation
                if is_valid_json(self.current_sentence):
                    self.sentence_queue.append((self.current_sentence, chunk.mode))
                elif re.search(r'[.!?]$', chunk.text.strip()):
                    # Join the words to form a complete sentence
                    self.sentence_queue.append((self.current_sentence.strip(), chunk.mode))  # Add to queue
                    self.current_sentence = ""

                # Exit if the flag is turned off
                if not self.is_running:
                    break
        except grpc.RpcError as e:
            print("gRPC LLM response error: {} - {}".format(e.code(), e.details()))

    def execute_response(self, pepper):
        """
        Continuously retrieve sentences from the queue and make Pepper speak them.
        """
        print("execute response first \n \n \n")
        while self.is_running or self.sentence_queue:
            if self.sentence_queue:
                sentence_tuple = self.sentence_queue.popleft()
                sentence_to_say = sentence_tuple[0]
                mode = sentence_tuple[1]
                if not is_valid_json(sentence_to_say):
                    self.speech_function(sentence_to_say)
                else:
                    print("Is it coming for the valid movement manager \n \n \n")
                    if mode == "secondary":
                        SecondaryCommunication(sentence_to_say, mode, pepper)
                    elif mode == "custom movement":
                        CustomMovementManager(sentence_to_say, pepper)
