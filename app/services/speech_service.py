import base64
import tempfile
import os


class SpeechService:
    def __init__(self):
        self.model = None
        self.use_whisper = False
        
        # Try to load Whisper (only works locally with enough RAM)
        try:
            import whisper
            import torch
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"🎤 Whisper running on: {self.device}")
            
            # Use tiny model for speed (or disable on low-memory systems)
            self.model = whisper.load_model("tiny", device=self.device)
            self.use_whisper = True
            print("✅ Whisper model loaded (tiny - fast mode)!")
        except ImportError:
            print("ℹ️  Whisper not installed - using browser speech recognition")
        except Exception as e:
            print(f"ℹ️  Whisper disabled: {e}")
            print("   Browser speech recognition will be used instead")

    async def transcribe_audio(self, audio_base64: str):
        if not self.use_whisper or not self.model:
            # Return empty - browser will handle transcription
            return "", 0.0
            
        try:
            audio_bytes = base64.b64decode(audio_base64)
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"whisper_audio_{os.getpid()}_{id(audio_bytes)}.wav")
            
            with open(tmp_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Fast transcription settings
            result = self.model.transcribe(
                tmp_path,
                language='en',
                fp16=False,
                temperature=0.0
            )

            text = result.get("text", "").strip()
            confidence = 90.0

            return text, confidence
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return "", 0.0
        finally:
            try:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except:
                pass


speech_service = SpeechService()
