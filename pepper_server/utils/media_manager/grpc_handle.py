import os
import cv2
import time
import wave
import traceback
import numpy as np

from grpc_pb2 import AudioImgResponse, TextChunk
from grpc_pb2_grpc import MediaServiceServicer

class MediaManager(MediaServiceServicer):
    def __init__(self, audio_img_queue, llama_response_queue, audio_save=False):
        super().__init__()
        self.audio_img_queue = audio_img_queue
        self.audio_save = audio_save
        self.llama_response_queue = llama_response_queue

        if self.audio_save:
            self.save_directory = "./recordings_stavya/"
            os.makedirs(self.save_directory, exist_ok=True)

    def save_audio_to_file(self, audio_data, sample_rate, num_channels, sample_width, file_name):
        file_path = os.path.join(self.save_directory, file_name)
        try:
            with wave.open(file_path, 'wb') as wave_file:
                wave_file.setnchannels(num_channels)
                wave_file.setsampwidth(sample_width)
                wave_file.setframerate(sample_rate)
                wave_file.writeframes(audio_data)
            print(f"Audio saved to {file_path} with header")
        except Exception as e:
            print(f"Error saving audio to file: {e}")
            raise

    def _decode_image_from_bytes(self, image_bytes):
        """
        Decode image bytes received in AudioImgRequest into a NumPy array usable by OpenCV.

        Args:
            image_bytes (bytes): The raw image data in bytes.

        Returns:
            np.ndarray: Decoded image as a NumPy array.
        """
        try:
            # Convert bytes to a 1D NumPy array
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            # Decode the image array into a format usable by OpenCV
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Failed to decode the image from bytes.")
            return image
        except Exception as e:
            print("Error decoding image: {}".format(e))
            return None

    def SendAudioImg(self, request, context):
        try:
            audio_data = request.audio_data
            sample_rate = request.sample_rate
            file_name = f"audio_{int(time.time())}.wav"  # Unique file name using timestamp
            encoding_map = {
                "PCM_8": 1,   # 8-bit audio
                "PCM_16": 2,  # 16-bit audio
                "PCM_24": 3,  # 24-bit audio
                "PCM_32": 4   # 32-bit audio
            }
            sample_width = encoding_map.get(request.audio_encoding)
            if self.audio_save:
                self.save_audio_to_file(
                    audio_data=request.audio_data,
                    sample_rate=request.sample_rate,
                    num_channels=request.num_channels,
                    sample_width=sample_width,
                    file_name=file_name
                )

            image_bytes = request.image_data
            image = self._decode_image_from_bytes(image_bytes)
            if image is None:
                return AudioImgResponse(
                    status="error",
                    message="The image came out as None"
                )

            self.audio_img_queue.put({
                "audio_data": request.audio_data,
                "sample_rate": request.sample_rate,
                "num_channels": request.num_channels,
                "encoding": request.audio_encoding,
                "description": request.audio_description,
                "image_data": image
            })

            return AudioImgResponse(
                status='success',
                message='Audio and Image data received successfully'
            ) 
        except Exception as e:
            error_trace = traceback.format_exc()
            print("Error occurred while processing data: {}".format(error_trace))

            return AudioImgResponse(
                status='error',
                message="An error occured: {}\nTraceback:\n{}".format(str(e), error_trace)
            )

    def LLmResponse(self, request, context):
        try:
            while True:
                chunk = self.llama_response_queue.get()
                if chunk is None:
                    break
                yield TextChunk(text=chunk['text'], is_final=chunk['is_final'])
                if chunk['is_final']:
                    break
        except Exception as e:
            print(f"Error in the LLmResponse: {e}")
            yield TextChunk(text="Error, no text received", is_final=True)
