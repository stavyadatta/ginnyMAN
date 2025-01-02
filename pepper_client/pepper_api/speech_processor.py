import sys
import re
import grpc
from collections import deque


class SpeechProcessor:
    def __init__(self, speech_manager):
        self.sentence_queue = deque()  # Queue for sentences
        self.current_sentence = ""
        self.speech_manager = speech_manager  # Instance of Pepper's speech manager
        self.is_running = True  # Flag to control the threads
        self.movement = False

    def build_sentences(self, response_stream):
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
                self.movement = chunk.movement

                # Check for sentence-ending punctuation
                if re.search(r'[.!?]$', chunk.text.strip()):
                    # Join the words to form a complete sentence
                    self.sentence_queue.append(self.current_sentence.strip())  # Add to queue
                    self.current_sentence = ""

                # Exit if the flag is turned off
                if not self.is_running:
                    break
        except grpc.RpcError as e:
            print("gRPC LLM response error: {} - {}".format(e.code(), e.details()))

    def say_sentences(self):
        """
        Continuously retrieve sentences from the queue and make Pepper speak them.
        """
        while self.is_running or self.sentence_queue:
            if self.sentence_queue:
                sentence_to_say = self.sentence_queue.popleft()
                self.speech_manager.say(sentence_to_say)
