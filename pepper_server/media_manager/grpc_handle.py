from grpc_pb2 import AudioResponse
from grpc_pb2_grpc import MediaServiceServicer

class MediaManager(MediaServiceServicer):
    def __init__(self, audio_queue):
        super().__init__()
        self.audio_queue = audio_queue

    def SendAudio(self, request, context):
        audio_data = request.audio_data
        sample_rate = request.sample_rate

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
