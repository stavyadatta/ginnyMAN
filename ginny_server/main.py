import cv2
import grpc
import traceback
import queue
from collections import deque
from concurrent import futures
from threading import Thread

from core_api import FaceRecognition, WhisperSpeech2Text
from media_manager import MediaManager, IMAGE_QUEUE_LEN
from secondary_channel import SecondaryGRPC
from executor import Executor
from reasoner import Reasoner
import grpc_communication.grpc_pb2 as pb2
import grpc_communication.grpc_pb2_grpc as pb2_grpc

def process_audio(audio_img_queue: queue.Queue, 
                  llama_response_queue: queue.Queue, 
                  image_queue: deque):
    """
    Process audio data from the queue: transcribe and send to llama.cpp.
    :param audio_queue: Queue containing audio data.
    :param whisper_model: Instance of WhisperSpeechToText for transcription.
    :param llama_handler: Instance of Llama for sending text to llama.cpp.
    """
    while True:
        audio_img_item = audio_img_queue.get()
        if audio_img_item is None:  # Exit signal
            break
        try:
            # Transcribe the audio
            transcription = WhisperSpeech2Text(audio_img_item)
            if len(transcription) < 2:
                transcription= "You"
            print(f"Transcription: {transcription}")
            if len(transcription) < 2:
                transcription = "You"

            # Get the face information 
            image = audio_img_item.get("image_data")
            cv2.imwrite("/workspace/database/face_db/some.jpg", image)
            face_id = FaceRecognition.get_most_frequent_face_id(image_queue)

            person_details = Reasoner(transcription, face_id)
            if person_details.get_attribute("state") == "vision":
                person_details.set_image(image)

            print("Executor response:")
            response = Executor(person_details)
            mode = 'default'
            for response_chunk in response:
                mode = response_chunk.mode
                response_text = response_chunk.textchunk
                print(response_text, end='', flush=True)
                llama_response_queue.put({
                    'text': response_text,
                    'is_final': False,
                    'mode': mode
                })
            llama_response_queue.put({
                'text': '',
                'is_final': True,
                'mode': 'default'
            })
            print()  # Newline after streaming is complete
        except Exception as e:
            print(f"Error processing audio: {e}")
            traceback.print_exc()

def serve():
    """
    Start the gRPC server and processing loop.
    """
    audio_img_queue = queue.Queue()
    llama_response_queue = queue.Queue()
    image_queue = deque(maxlen=IMAGE_QUEUE_LEN)

    # Start the audio processing loop in a separate thread
    processing_thread = Thread(
        target=process_audio, 
        args=(
            audio_img_queue, 
            llama_response_queue, 
            image_queue
        ), 
        daemon=True
    )
    processing_thread.start()

    # Start the gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_MediaServiceServicer_to_server(
        MediaManager(audio_img_queue, llama_response_queue, image_queue), 
        server
    )
    pb2_grpc.add_SecondaryChannelServicer_to_server(
        SecondaryGRPC(),
        server
    )
    server.add_insecure_port("[::]:50051")
    print("gRPC server running on port 50051...")
    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down server...")
        audio_img_queue.put(None)  # Signal to stop the processing loop
        processing_thread.join()
        server.stop(0)

if __name__ == "__main__":
    serve()
