import os
import grpc
import time
from concurrent import futures
from PIL import Image
from io import BytesIO
from grpc_communication.grpc_pb2 import ImageResponse
from grpc_communication.grpc_pb2_grpc import MediaServiceStub, \
    add_MediaServiceServicer_to_server, MediaServiceServicer

class MediaServer(MediaServiceServicer):
    def __init__(self, save_directory="received_images"):
        self.save_directory = save_directory
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def SendImage(self, request, context):
        # Decode the raw image bytes using Pillow
        try:
            image = Image.open(BytesIO(request.image_data))
            image_format = request.format.upper() if request.format else "JPEG"

            # Ensure the image format is valid
            if image_format not in ["JPEG", "PNG", "BMP", "GIF", "TIFF"]:
                image_format = "JPEG"

            image_path = os.path.join(
                self.save_directory,
                "image_{}.{}".format(int(time.time()), image_format.lower())
            )
            
            # Save the image to the specified directory
            image.save(image_path, format=image_format)
            print("Image successfully saved at {}".format(image_path))

            # Respond to the client
            return ImageResponse(status="success", message="Image saved at {}".format(image_path))

        except Exception as e:
            print("Error while saving the image: {}".format(str(e)))
            return ImageResponse(status="failure", message="Error: {}".format(str(e)))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MediaServiceServicer_to_server(MediaServer(), server)
    server.add_insecure_port("[::]:50051")
    print("Server is running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

