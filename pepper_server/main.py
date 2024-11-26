from .llama import Llama
from .media_manager import MediaManager
from .whisper import WhisperSpeechToText

def process_audio(audio_queue, whisper_model, llama_handler):
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
            transcription = whisper_model.speech2text(
                audio_item["audio_data"],
                audio_item["sample_rate"]
            )
            print(f"Transcription: {transcription}")

            # Send transcription to llama.cpp
            llama_response = llama_handler.send_to_llama(transcription)
            print(f"Llama response: {llama_response}")
        except Exception as e:
            print(f"Error processing audio: {e}")

