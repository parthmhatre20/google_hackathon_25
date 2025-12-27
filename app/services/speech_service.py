import base64
import tempfile
import os


class SpeechService:
    def __init__(self):
        self.model = None
        try:
            import whisper
            import torch
            
            # Pick GPU if available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"🎤 Whisper running on: {self.device}")

            # Best balance of speed + accuracy for you
            self.model = whisper.load_model("small", device=self.device)
            print("✅ Whisper model loaded successfully!")
        except ImportError as e:
            print(f"⚠️  Whisper not installed. Run: pip install openai-whisper torch")
            print(f"   Error: {e}")
        except Exception as e:
            print(f"⚠️  Could not load Whisper model: {e}")

    async def transcribe_audio(self, audio_base64: str):
        if not self.model:
            raise Exception("Whisper model not loaded. Please install: pip install openai-whisper torch")
            
        try:
            # Decode base64 → audio bytes
            audio_bytes = base64.b64decode(audio_base64)

            # Write to a temporary file with explicit directory and mode for Windows
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"whisper_audio_{os.getpid()}_{id(audio_bytes)}.wav")
            
            # Write audio file
            with open(tmp_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Verify file exists
            if not os.path.exists(tmp_path):
                raise Exception(f"Failed to create temporary file at {tmp_path}")
            
            print(f"Transcribing audio file: {tmp_path} ({len(audio_bytes)} bytes)")
            
            # Transcribe with English language forced and better settings for accuracy
            result = self.model.transcribe(
                tmp_path,
                language='en',  # Force English
                fp16=False,  # CPU compatibility
                task='transcribe',  # Not translate
                temperature=0.0,  # More deterministic
                best_of=5,  # Try multiple decodings
                beam_size=5  # Better beam search
            )

            text = result.get("text", "").strip()
            
            print(f"Transcription result: {text}")

            # Whisper doesn't output confidence, so return a fixed estimate
            confidence = 90.0

            return text, confidence
            
        except FileNotFoundError as e:
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
                raise Exception("FFmpeg not found. Install from https://ffmpeg.org/download.html and add to PATH, or install via: winget install ffmpeg")
            raise Exception(f"File error: {error_msg}")
        except Exception as e:
            print(f"Transcription error: {type(e).__name__}: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            try:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception as e:
                print(f"Warning: Could not delete temp file: {e}")


speech_service = SpeechService()
