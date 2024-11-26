import whisper
import torch

class WhisperSpeechToText:
    def __init__(self, model_name="base"):
        """
        Initialize the Whisper model for speech-to-text.
        """
        self.model = whisper.load_model(model_name)

    def speech2text(self, audio_data, sample_rate):
        """
        Transcribe speech from audio data to text.
        :param audio_data: Raw audio bytes.
        :param sample_rate: Sample rate of the audio.
        :return: Transcribed text.
        """
        # Convert bytes to a torch audio tensor
        audio_tensor = torch.tensor(
            whisper.pad_or_trim(whisper.load_audio(audio_data, sample_rate))
        ).float()
        # Run Whisper to transcribe the audio
        result = self.model.transcribe(audio_tensor)
        return result["text"]

