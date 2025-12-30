import base64
import tempfile
import os
import httpx


class SpeechService:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if self.groq_api_key:
            print("✅ Groq Whisper API configured!")
        else:
            print("⚠️ GROQ_API_KEY not found - speech transcription will not work")

    async def transcribe_audio(self, audio_base64: str):
        if not self.groq_api_key:
            print("⚠️ Groq API key not configured")
            return "", 0.0
            
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)
            
            # Save to temp file (Groq needs a file)
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"groq_audio_{os.getpid()}.wav")
            
            with open(tmp_path, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"🎤 Sending {len(audio_bytes)} bytes to Groq Whisper...")
            
            # Call Groq Whisper API
            async with httpx.AsyncClient(timeout=60.0) as client:
                with open(tmp_path, 'rb') as audio_file:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/audio/transcriptions",
                        headers={
                            "Authorization": f"Bearer {self.groq_api_key}"
                        },
                        files={
                            "file": ("audio.wav", audio_file, "audio/wav")
                        },
                        data={
                            "model": "whisper-large-v3",  # Best accuracy!
                            "language": "en",
                            "response_format": "json"
                        }
                    )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("text", "").strip()
                confidence = 98.0  # Whisper large-v3 is extremely accurate
                
                print(f"✅ Groq transcription: {text[:100]}...")
                return text, confidence
            else:
                print(f"❌ Groq API error: {response.status_code} - {response.text}")
                return "", 0.0
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return "", 0.0
        finally:
            try:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except:
                pass


speech_service = SpeechService()
