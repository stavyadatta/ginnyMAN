import cv2
import grpc
import traceback
import queue
import numpy as np
from concurrent import futures
from threading import Thread

from llama import Llama
from face_recognition import FaceRecognition
from media_manager import MediaManager
from whisper2text import WhisperSpeechToText
import grpc_communication.grpc_pb2 as pb2
import grpc_communication.grpc_pb2_grpc as pb2_grpc

def bytes2cv2(img):
    img_array = np.frombuffer(img, dtype=np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return image

def process_audio(audio_img_queue: queue.Queue, 
                  llama_response_queue: queue.Queue, 
                  whisper_model: WhisperSpeechToText, 
                  llama_handler: Llama,
                  face_recognition: FaceRecognition):
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
            transcription = whisper_model.speech2text(audio_img_item)
            print(f"Transcription: {transcription}")

            # Get the face information 
            image = audio_img_item.get("image_data")
            cv2.imwrite("/workspace/database/face_db/some.png", image)
            face_id = face_recognition.recognize_face(image)

            # Send transcription to llama.cpp and stream the response
            print("Llama response:")
            for response_chunk in llama_handler.send_to_llama(transcription, face_id):
                print(response_chunk, end='', flush=True)
                llama_response_queue.put({
                    'text': response_chunk,
                    'is_final': False
                })
            llama_response_queue.put({
                'text': '',
                'is_final': True
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
    whisper_model = WhisperSpeechToText(model_name="base")
    llama_handler = Llama()
    face_recognition = FaceRecognition()

    # Start the audio processing loop in a separate thread
    processing_thread = Thread(
        target=process_audio, 
        args=(
            audio_img_queue, 
            llama_response_queue, 
            whisper_model, 
            llama_handler, 
            face_recognition
        ), 
        daemon=True
    )
    processing_thread.start()

    # Start the gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_MediaServiceServicer_to_server(
        MediaManager(audio_img_queue, llama_response_queue), 
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
