import grpc
import traceback
import queue
from concurrent import futures
from threading import Thread

from llama import Llama
from media_manager import MediaManager
from whisper2text import WhisperSpeechToText
import grpc_communication.grpc_pb2 as pb2
import grpc_communication.grpc_pb2_grpc as pb2_grpc

def process_audio(audio_queue: queue.Queue, 
                  llama_response_queue: queue.Queue, 
                  whisper_model: WhisperSpeechToText, 
                  llama_handler: Llama):
    """
    Process audio data from the queue: transcribe and send to llama.cpp.
    :param audio_queue: Queue containing audio data.
    :param whisper_model: Instance of WhisperSpeechToText for transcription.
    :param llama_handler: Instance of Llama for sending text to llama.cpp.
    """
    while True:
        audio_item = audio_queue.get()
        if audio_item is None:  # Exit signal
            break
        try:
            # Transcribe the audio
            transcription = whisper_model.speech2text(audio_item)
            print(f"Transcription: {transcription}")

            # Send transcription to llama.cpp and stream the response
            print("Llama response:")
            for response_chunk in llama_handler.send_to_llama(transcription):
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
    audio_queue = queue.Queue()
    llama_response_queue = queue.Queue()
    whisper_model = WhisperSpeechToText(model_name="base")
    llama_handler = Llama()

    # Start the audio processing loop in a separate thread
    processing_thread = Thread(
        target=process_audio, 
        args=(audio_queue, llama_response_queue, whisper_model, llama_handler), 
        daemon=True
    )
    processing_thread.start()

    # Start the gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_MediaServiceServicer_to_server(
        MediaManager(audio_queue, llama_response_queue), 
        server
    )
    server.add_insecure_port("[::]:50051")
    print("gRPC server running on port 50051...")
    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down server...")
        audio_queue.put(None)  # Signal to stop the processing loop
        processing_thread.join()
        server.stop(0)

if __name__ == "__main__":
    serve()
