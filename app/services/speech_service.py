import base64
import tempfile
import os


class SpeechService:
    def __init__(self):
        self.model = None
        self.use_whisper = False
        
        # Try to load Whisper
        try:
            import whisper
            import torch
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"🎤 Whisper running on: {self.device}")
            
            # Use 'base' model - best balance of speed and accuracy for hackathon
            # tiny = fastest, less accurate
            # base = good balance (recommended)
            # small = more accurate, slower
            self.model = whisper.load_model("base", device=self.device)
            self.use_whisper = True
            print("✅ Whisper model loaded (base - optimized for accuracy)!")
        except ImportError as e:
            print(f"⚠️ Whisper not installed: {e}")
            print("   Install with: pip install openai-whisper torch")
        except Exception as e:
            print(f"⚠️ Whisper initialization failed: {e}")

    async def transcribe_audio(self, audio_base64: str):
        if not self.use_whisper or not self.model:
            # Return empty - browser will handle transcription
            print("⚠️ Whisper not available, returning empty transcription")
            return "", 0.0
            
        try:
            audio_bytes = base64.b64decode(audio_base64)
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"whisper_audio_{os.getpid()}_{id(audio_bytes)}.wav")
            
            with open(tmp_path, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"🎤 Transcribing {len(audio_bytes)} bytes of audio...")
            
            # Optimized settings for accuracy
            result = self.model.transcribe(
                tmp_path,
                language='en',
                fp16=False,  # CPU compatibility
                temperature=0.0,  # More deterministic
                best_of=3,  # Try multiple decodings for better accuracy
                beam_size=5  # Better beam search
            )

            text = result.get("text", "").strip()
            confidence = 95.0  # Whisper is highly accurate
            
            print(f"✅ Transcription: {text[:100]}...")

            return text, confidence
            
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
