from .face_recognition import _FaceRecognition
from .whisper2text import _WhisperSpeech2Text
from .llama import _Llama
from .claude import _ClaudeImageProcessor
from .yolo import _PersonDetectorCropper
from .chatgpt import _OpenAIHandler

FaceRecognition = _FaceRecognition()
WhisperSpeech2Text = _WhisperSpeech2Text()
Llama = _Llama()
PersonDetectionCropper = _PersonDetectorCropper()
Claude = _ClaudeImageProcessor()
ChatGPT = _OpenAIHandler()

__all__ = ["FaceRecognition", "WhisperSpeech2Text", "Llama", "PersonDetectionCropper", "Claude", "ChatGPT"]


