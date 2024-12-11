import grpc
import wave
import cv2
import time
import sys
import io
import numpy as np
import pyaudio
from google.protobuf.empty_pb2 import Empty
from grpc_communication.grpc_pb2 import AudioImgRequest
from grpc_communication.grpc_pb2_grpc import MediaServiceStub

THRESHOLD = 55000
SILENCE_FRAMES = 10
CHUNK = 1024
RATE = 16000
CHANNELS = 1

def wait_for_speech_start(stream):
    """
    Wait until the user starts speaking (energy > THRESHOLD).
    Returns True when speech detected.
    """
    print("Waiting for speech...")
    while True:
        data = stream.read(CHUNK)
        audio_samples = np.frombuffer(data, dtype=np.int16)
        energy = np.sum(audio_samples.astype(np.int32) ** 2) / len(audio_samples)
        if energy > THRESHOLD:
            print("Speech detected, starting recording...")
            return [data]  # Return the first chunk of speech data

def record_until_silence():
    """
    Record audio from the microphone starting when user speaks above threshold,
    and stop after detecting 10 consecutive silent frames (energy < THRESHOLD).
    Returns the recorded PCM data.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # Wait until user starts speaking
    frames = wait_for_speech_start(stream)

    silent_count = 0
    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        audio_samples = np.frombuffer(data, dtype=np.int16)
        energy = np.sum(audio_samples.astype(np.int32) ** 2) / len(audio_samples)

        if energy < THRESHOLD:
            silent_count += 1
        else:
            silent_count = 0
        
        if silent_count >= SILENCE_FRAMES:
            print("Silence detected. Stopping recording.")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    return b''.join(frames)

def convert_pcm_to_wav_bytes(pcm_data, sample_rate, num_channels, sample_width=2):
    """
    Convert raw PCM data to a WAV-formatted byte string.
    """
    wav_buffer = io.BytesIO()
    wf = wave.open(wav_buffer, 'wb')
    wf.setnchannels(num_channels)
    wf.setsampwidth(sample_width)  # 2 bytes (16-bit)
    wf.setframerate(sample_rate)
    wf.writeframes(pcm_data)
    # with wave.open(wav_buffer, 'wb') as wf:
    #     wf.setnchannels(num_channels)
    #     wf.setsampwidth(sample_width)  # 2 bytes (16-bit)
    #     wf.setframerate(sample_rate)
    #     wf.writeframes(pcm_data)
    
    wf.close()
    return wav_buffer.getvalue()

def capture_webcam_image():
    """
    Capture a single frame from the webcam.
    """
    cap = cv2.VideoCapture(0)  # Open default camera
    if not cap.isOpened():
        raise Exception("Could not open webcam")
    contador = 0
    while True:
        if contador == 50000:
            ret, frame = cap.read()
            break
        contador += 1
    cap.release()
    if not ret:
        raise Exception("Failed to capture image from webcam")

    return frame

def send_audio_image_to_grpc(audio_wav_data, sample_rate, num_channels, last_frame, stub):
    """Send the audio and image to the gRPC server."""
    try:
        # Encode the last frame as JPEG
        _, image_data = cv2.imencode('.jpg', last_frame)
        height, width, _ = last_frame.shape

        # Determine audio encoding (since we used 16-bit samples)
        audio_encoding = "PCM_16"

        # Create AudioImgRequest message
        print("Is the error here? like starting")
        request = AudioImgRequest(
            audio_data=audio_wav_data,
            sample_rate=sample_rate,
            num_channels=num_channels,
            audio_encoding=audio_encoding,
            audio_description="Recorded audio data",
            image_data=image_data.tobytes(),
            image_format="JPEG",
            image_width=width,
            image_height=height,
            image_description="Captured webcam image"
        )

        # Call the gRPC method
        response = stub.SendAudioImg(request)
        print("Is the error here? like ending")
        print("SendAudioImg response: {} - {}".format(response.status, response.message))
    except Exception as e:
        print("Error: Failed to send media via gRPC. Error: {}".format(e))

def receive_llm_response(stub):
    """Receive streamed LLM response from the gRPC server."""
    request = Empty()
    try:
        response_stream = stub.LLmResponse(request)
        print("Receiving streamed text chunks:")
        for chunk in response_stream:
            sys.stdout.write(chunk.text)
            sys.stdout.flush()
            if chunk.is_final:
                sys.stdout.write("\n[Final chunk received]\n")
                sys.stdout.flush()
                break
    except grpc.RpcError as e:
        print("gRPC error: {} - {}".format(e.code(), e.details()))

if __name__ == "__main__":
    # Set up gRPC channel and stub
    channel = grpc.insecure_channel("172.27.72.27:50051")
    stub = MediaServiceStub(channel)

    try:
        while True:
            # Record audio until silence after speech
            pcm_data = record_until_silence()

            # Convert to WAV format (in-memory)
            audio_wav_data = convert_pcm_to_wav_bytes(pcm_data, RATE, CHANNELS)

            # Capture image from webcam
            last_frame = capture_webcam_image()

            # Send data to gRPC pipeline
            send_audio_image_to_grpc(audio_wav_data, RATE, CHANNELS, last_frame, stub)

            # Receive LLM response
            receive_llm_response(stub)

            print("Finished one cycle. Waiting for next speech...")
    except KeyboardInterrupt:
        print("\nShutting down... Goodbye!")

