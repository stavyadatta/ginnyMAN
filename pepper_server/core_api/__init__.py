from .face_recognition import _FaceRecognition
from .whisper2text import _WhisperSpeech2Text
from .llama import _Llama

FaceRecognition = _FaceRecognition()
WhisperSpeech2Text = _WhisperSpeech2Text()
Llama = _Llama()

__all__ = ["FaceRecognition", "WhisperSpeech2Text", "Llama"]


