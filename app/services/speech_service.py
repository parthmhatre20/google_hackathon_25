import base64
import tempfile
import whisper
import torch


class SpeechService:
    def __init__(self):
        # Pick GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🎤 Whisper running on: {self.device}")

        # Best balance of speed + accuracy for you
        self.model = whisper.load_model("small", device=self.device)

    async def transcribe_audio(self, audio_base64: str):
        # Decode base64 → audio bytes
        audio_bytes = base64.b64decode(audio_base64)

        # Write to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        # Transcribe
        result = self.model.transcribe(tmp_path, fp16=False)

        text = result.get("text", "").strip()

        # Whisper doesn't output confidence, so return a fixed estimate
        confidence = 90.0

        return text, confidence


speech_service = SpeechService()
