<div align="center">

# 🎯 AI Interview Coach

**Master your interviews with AI-powered practice sessions**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat-square&logo=firebase&logoColor=black)](https://firebase.google.com)
[![Gemini](https://img.shields.io/badge/Gemini_2.5-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[**Live Demo**](https://google-hackathon-25.onrender.com) · [**Features**](#-features) · [**Quick Start**](#-quick-start) · [**API Docs**](#-api-endpoints)

---

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [Team](#-team)
- [License](#-license)

---

## 🎯 Overview

AI Interview Coach is an intelligent interview practice platform that simulates real interview experiences. Practice answering questions tailored to your target role, receive instant AI-powered feedback, and track your improvement over time.

**Built for Google Hackathon December 2025**

### Why AI Interview Coach?

- 🎤 **Voice-first** — Speak naturally, just like a real interview
- 🤖 **Smart feedback** — Get actionable insights on every answer  
- 📈 **Track progress** — Review past sessions and see improvement
- 🎯 **Personalized** — Questions based on your role and experience level

---

## ✨ Features

### 🎙️ Voice Interaction
- **Groq Whisper API** — Industry-leading speech recognition (whisper-large-v3)
- **Edge TTS** — Natural text-to-speech for interview questions
- **Real-time processing** — Minimal latency voice-to-text conversion

### 🤖 AI-Powered Analysis
- **Google Gemini 2.5 Flash** — Dynamic question generation based on:
  - Target job role & company
  - Years of experience  
  - Interview type (behavioral, technical, situational)
- **Comprehensive feedback** including:
  - Content relevance scoring
  - Communication clarity analysis
  - Filler word detection (um, uh, like, basically...)
  - Specific improvement suggestions

### 📊 Session Management
- **Save & review** — All sessions stored in Firebase
- **Organize** — Rename and delete sessions with right-click context menu
- **History** — Browse and revisit past interviews

### 🔐 Authentication
- **Google OAuth** — Secure one-click sign-in
- **Firebase Auth** — Industry-standard authentication

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| **Backend** | FastAPI | Async API endpoints |
| **Frontend** | Flask + Tailwind CSS | Server-rendered UI |
| **AI** | Google Gemini 2.5 Flash | Question generation & analysis |
| **Speech-to-Text** | Groq Whisper API | Voice transcription |
| **Text-to-Speech** | Edge TTS | Question narration |
| **Database** | Firebase Realtime DB | Data persistence |
| **Auth** | Firebase Auth | Google OAuth |
| **Hosting** | Render | Cloud deployment |

---

## 🏗 Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         Client Browser                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Landing    │  │  Interview   │  │    Auth      │          │
│  │    Page      │  │   Session    │  │   Pages      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────┬──────────────────────────────────┘
                              │ HTTP/WebSocket
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                     Render Web Service                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    server.py                             │   │
│  │  ┌─────────────────────┐  ┌─────────────────────┐       │   │
│  │  │   FastAPI (/api)    │  │   Flask (/)         │       │   │
│  │  │  • /interview/*     │  │  • Template routes  │       │   │
│  │  │  • /transcribe      │  │  • Static files     │       │   │
│  │  │  • /analyze         │  │                     │       │   │
│  │  │  • /tts             │  │                     │       │   │
│  │  └─────────────────────┘  └─────────────────────┘       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬──────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Gemini     │    │    Groq      │    │   Firebase   │
│   2.5 Flash  │    │   Whisper    │    │   Realtime   │
│              │    │   large-v3   │    │      DB      │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Firebase project with Realtime Database
- API keys for Gemini and Groq

### Installation

```bash
# Clone the repository
git clone https://github.com/parthmhatre20/google_hackathon_25.git
cd google_hackathon_25

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (see next section)
cp .env.example .env

# Run the server
uvicorn server:app --reload --port 8000
```

Open http://localhost:8000 in your browser.

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```env
# Gemini API Keys (supports multiple for rate limit rotation)
GEMINI_API_KEY_1=your_gemini_api_key
GEMINI_API_KEY_2=your_second_key_optional
GEMINI_API_KEY_3=your_third_key_optional

# Groq API Key (for Whisper speech-to-text)
GROQ_API_KEY=your_groq_api_key

# Firebase
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
```

### Getting API Keys

| Service | Link | Notes |
|:--------|:-----|:------|
| **Gemini** | [Google AI Studio](https://aistudio.google.com/apikey) | Free tier available |
| **Groq** | [Groq Console](https://console.groq.com/keys) | Free tier with generous limits |
| **Firebase** | [Firebase Console](https://console.firebase.google.com) | Enable Realtime Database |

---

## 📡 API Endpoints

### Interview Routes (`/api/interview`)

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `POST` | `/start-session` | Start a new interview session |
| `POST` | `/generate-questions` | Generate AI questions for role |
| `POST` | `/transcribe` | Convert speech to text |
| `POST` | `/analyze` | Analyze answer with AI feedback |
| `POST` | `/question/speak` | Convert question to speech |
| `POST` | `/save-answer` | Save answer to session |
| `POST` | `/complete-session` | Mark session complete |
| `GET` | `/sessions/{user_id}` | Get user's session history |
| `PUT` | `/session/{id}/rename` | Rename a session |
| `DELETE` | `/session/{id}` | Delete a session |

### Health Check

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/health` | Service health status |
| `GET` | `/api/health` | API health status |

---

## 🚢 Deployment

### Deploy to Render

1. Fork this repository
2. Create a new **Web Service** on [Render](https://render.com)
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in dashboard
6. Deploy!

**Live URL:** https://google-hackathon-25.onrender.com

---

## 📁 Project Structure

```
google_hackathon_25/
├── app/
│   ├── routes/
│   │   ├── interview.py        # Interview & session endpoints
│   │   └── __init__.py
│   ├── services/
│   │   ├── ai_service.py       # Gemini integration
│   │   ├── speech_service.py   # Groq Whisper transcription
│   │   ├── tts_service.py      # Edge TTS synthesis
│   │   ├── question_generator.py
│   │   ├── interview_store.py
│   │   └── answer_store.py
│   ├── config.py               # App settings
│   ├── models.py               # Pydantic schemas
│   └── firebase_realtime.py    # Firebase connection
├── Frontend/
│   ├── Templates/
│   │   ├── index2.html         # Landing page
│   │   ├── Interview_section.html
│   │   ├── sign_in.html
│   │   └── sign_up2.html
│   ├── static/
│   │   ├── api.js
│   │   └── auth.js
│   └── app.py                  # Flask routes
├── server.py                   # Combined FastAPI + Flask
├── requirements.txt
└── README.md
```

---

## 👥 Team

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/parthmhatre20">
        <img src="https://github.com/parthmhatre20.png" width="80px;" alt=""/><br />
        <sub><b>Parth Mhatre</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/anshkoli19">
        <img src="https://github.com/anshkoli19.png" width="80px;" alt=""/><br />
        <sub><b>Ansh Koli</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/rohan-sanjay-kadam">
        <img src="https://github.com/rohan-sanjay-kadam.png" width="80px;" alt=""/><br />
        <sub><b>Rohan Kadam</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/khalidj291">
        <img src="https://github.com/khalidj291.png" width="80px;" alt=""/><br />
        <sub><b>Khalid J</b></sub>
      </a>
    </td>
  </tr>
</table>

---

<div align="center">

[⬆ Back to Top](#-ai-interview-coach)

</div>
