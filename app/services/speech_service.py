import base64
from app.config import settings
import os

class SpeechService:
    def __init__(self):
        self.client = None
        print("⚠️  Speech service initialized without credentials (will not work until configured)")
    
    async def transcribe_audio(self, audio_base64: str):
        return "This is a mock transcription for development.", 0.85


speech_service = SpeechService()