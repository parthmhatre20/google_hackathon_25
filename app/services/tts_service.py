import edge_tts
import base64
import tempfile
import os
from typing import Tuple

class TTSService:
    def __init__(self):
        """Initialize Edge TTS service"""
        # Professional voices
        self.voice = "en-US-GuyNeural"  # Professional male voice
        # Alternative voices you can use:
        # "en-US-JennyNeural" - Professional female
        # "en-US-AriaNeural" - Warm female
        # "en-GB-RyanNeural" - British male
        # "en-US-ChristopherNeural" - Deep male
        print("✅ Edge TTS service initialized successfully!")

    async def text_to_speech(self, text: str, language_code: str = "en-US") -> Tuple[str, str]:
        """
        Convert text to speech audio using Edge TTS
        
        Args:
            text: The text to convert to speech
            language_code: Language code (default: en-US)
        
        Returns:
            Tuple[str, str]: (audio_base64, audio_format)
        """
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_path = temp_file.name

            # Generate speech using Edge TTS
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(temp_path)

            # Read the generated audio file
            with open(temp_path, "rb") as audio_file:
                audio_content = audio_file.read()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            # Convert to base64 for easy transmission
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            return audio_base64, "mp3"
            
        except Exception as e:
            raise Exception(f"TTS error: {str(e)}")

# Create singleton instance
tts_service = TTSService()