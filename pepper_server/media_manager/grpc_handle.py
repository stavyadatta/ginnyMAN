import os
import time
import wave

from grpc_pb2 import AudioResponse, TextChunk
from grpc_pb2_grpc import MediaServiceServicer

class MediaManager(MediaServiceServicer):
    def __init__(self, audio_queue, llama_response_queue, audio_save=False):
        super().__init__()
        self.audio_queue = audio_queue
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

    def SendAudio(self, request, context):
        audio_data = request.audio_data
        sample_rate = request.sample_rate
        file_name = f"audio_{int(time.time())}.wav"  # Unique file name using timestamp
        encoding_map = {
            "PCM_8": 1,   # 8-bit audio
            "PCM_16": 2,  # 16-bit audio
            "PCM_24": 3,  # 24-bit audio
            "PCM_32": 4   # 32-bit audio
        }
        sample_width = encoding_map.get(request.encoding)

        if self.audio_save:
            self.save_audio_to_file(
                audio_data=request.audio_data,
                sample_rate=request.sample_rate,
                num_channels=request.num_channels,
                sample_width=sample_width,
                file_name=file_name
            )

        self.audio_queue.put({
            "audio_data": request.audio_data,
            "sample_rate": request.sample_rate,
            "num_channels": request.num_channels,
            "encoding": request.encoding,
            "description": request.description
        })

        return AudioResponse(
            status='success',
            message='Audio Data is received successfully'
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
