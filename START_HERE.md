# 🎤 AI Mock Interview - Quick Start Guide

## Running the App (Super Simple!)

**Just run ONE command:**
```bash
python run.py
```

That's it! Everything starts automatically:
- ✅ FFmpeg setup
- ✅ Backend server (Port 8000)
- ✅ Frontend server (Port 5000)

**Access the app:**
- **Test Page (No Login):** http://127.0.0.1:5000/test
- **Main App:** http://127.0.0.1:5000
- **API Docs:** http://localhost:8000/docs

**Stop the app:**
Press `Ctrl+C` in the terminal

---

## First Time Setup

**1. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**2. Create `.env` file:**
```bash
GEMINI_API_KEY=your_api_key_here
```
Or use multiple API keys:
```bash
GEMINI_API_KEYS=key1,key2,key3,key4
```

**3. Install FFmpeg:**
- Download from: https://ffmpeg.org/download.html
- Extract to: `C:\Users\YOUR_USERNAME\AppData\Local\Temp\ffmpeg\ffmpeg-8.0.1-essentials_build`

**4. Run the app:**
```bash
python run.py
```

---

## What We Built

✅ **AI-Powered Interview Coach**
- Real-time speech-to-text with Whisper
- Google Gemini AI for feedback and scoring
- Role-specific technical questions (Frontend, Backend, ML, DevOps, etc.)
- Adaptive questions based on your skills/resume

✅ **Recent Improvements**
- Balanced, encouraging AI feedback (not overly harsh)
- Realistic scoring (40-90 range, not 8-15)
- Technical questions specific to job roles
- Background field for personalized questions
- Multi-API-key rotation for team quota management
- Better UI: clear buttons, processing indicators, scroll support

---

## Troubleshooting

**"File error" or "FFmpeg not found":**
- Make sure FFmpeg is installed
- Use `start_backend.ps1` instead of running Python directly

**"Quota exhausted":**
- Add more API keys to `.env` (GEMINI_API_KEYS=key1,key2,key3)
- System will rotate through all keys automatically

**"AI not giving real feedback":**
- Check backend terminal for API errors
- Verify your API key is valid and has quota

---

## Tech Stack

- **Backend:** FastAPI + Uvicorn (Port 8000)
- **Frontend:** Flask (Port 5000)
- **AI:** Google Gemini 2.5 Flash
- **Speech:** OpenAI Whisper (CPU)
- **TTS:** Edge-TTS
- **Auth:** Firebase (optional)

---

Good luck with your interviews! 🚀
