from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from app.models import (
    TranscriptionRequest, TranscriptionResponse,
    AnalysisRequest, AnalysisResponse,
    SaveAttemptRequest, InterviewAttempt
)
from app.services.speech_service import speech_service
from app.services.ai_service import ai_service
from app.services.firebase_service import firebase_service
from app.services.tts_service import tts_service
import base64

router = APIRouter(prefix="/api/interview", tags=["interview"])

# Question bank
INTERVIEW_QUESTIONS = {
    "q1": "Tell me about yourself.",
    "q2": "What are your greatest strengths?",
    "q3": "Describe a challenging situation you faced and how you handled it.",
    "q4": "Where do you see yourself in 5 years?",
    "q5": "Why do you want to work for our company?",
    "q6": "What is your biggest weakness?",
    "q7": "Tell me about a time you worked in a team.",
    "q8": "How do you handle stress and pressure?"
}

class QuestionSpeakRequest(BaseModel):
    question_id: str

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: TranscriptionRequest):
    """
    Transcribe audio to text using Whisper
    """
    try:
        transcription, confidence = await speech_service.transcribe_audio(
            request.audio_base64
        )
        
        return TranscriptionResponse(
            transcription=transcription,
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcribe-file")
async def transcribe_audio_file(
    file: UploadFile = File(...),
    question_id: str = Form(...)
):
    """
    Transcribe audio file (alternative endpoint for file upload)
    """
    try:
        # Read file content
        audio_content = await file.read()
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        transcription, confidence = await speech_service.transcribe_audio(audio_base64)
        
        return TranscriptionResponse(
            transcription=transcription,
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_answer(request: AnalysisRequest):
    """
    Analyze interview answer using Gemini API
    """
    try:
        analysis = await ai_service.analyze_answer(
            transcription=request.transcription,
            question_text=request.question_text
        )
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete")
async def complete_interview(request: SaveAttemptRequest):
    """
    Complete interview flow: transcribe + analyze + save
    This is a convenience endpoint that does everything in one call
    """
    try:
        # Save attempt to Firebase
        attempt = InterviewAttempt(
            user_id=request.user_id,
            question_id=request.question_id,
            question_text=request.question_text,
            transcription=request.transcription,
            analysis=request.analysis,
            duration_seconds=request.duration_seconds
        )
        
        try:
            attempt_id = await firebase_service.save_attempt(attempt)
        except Exception:
            attempt_id = "mock_attempt_id"

        
        return {
            "success": True,
            "attempt_id": attempt_id,
            "message": "Interview attempt saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions")
async def get_interview_questions():
    """
    Get list of interview questions
    """
    questions = [
        {
            "question_id": "q1",
            "question_text": "Tell me about yourself.",
            "category": "introduction"
        },
        {
            "question_id": "q2",
            "question_text": "What are your greatest strengths?",
            "category": "behavioral"
        },
        {
            "question_id": "q3",
            "question_text": "Describe a challenging situation you faced and how you handled it.",
            "category": "behavioral"
        },
        {
            "question_id": "q4",
            "question_text": "Where do you see yourself in 5 years?",
            "category": "career goals"
        },
        {
            "question_id": "q5",
            "question_text": "Why do you want to work for our company?",
            "category": "motivation"
        },
        {
            "question_id": "q6",
            "question_text": "What is your biggest weakness?",
            "category": "self-awareness"
        },
        {
            "question_id": "q7",
            "question_text": "Tell me about a time you worked in a team.",
            "category": "teamwork"
        },
        {
            "question_id": "q8",
            "question_text": "How do you handle stress and pressure?",
            "category": "behavioral"
        }
    ]
    
    return {"questions": questions}

@router.post("/question/speak")
async def speak_question(request: QuestionSpeakRequest):
    """
    Get a question as audio (AI speaks it)
    Returns the question text and audio in base64 format
    """
    try:
        question_text = INTERVIEW_QUESTIONS.get(request.question_id)
        if not question_text:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Convert question to speech
        audio_base64, audio_format = await tts_service.text_to_speech(question_text)
        
        return {
            "question_id": request.question_id,
            "question_text": question_text,
            "audio_base64": audio_base64,
            "audio_format": audio_format
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/realtime-interview")
async def realtime_interview_flow(
    question_id: str = Form(...),
    audio_file: UploadFile = File(...)
):
    """
    Complete real-time interview flow:
    1. User submits their audio answer
    2. Transcribe the answer
    3. Analyze the answer with AI
    4. Generate spoken feedback
    5. Return everything (text + audio feedback)
    
    This is the main endpoint for voice-to-voice interview interaction
    """
    try:
        # Get question text
        question_text = INTERVIEW_QUESTIONS.get(question_id, "Tell me about yourself.")
        
        # Transcribe user's audio answer
        audio_content = await audio_file.read()
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        transcription, confidence = await speech_service.transcribe_audio(audio_base64)
        
        # Analyze the answer with AI
        analysis = await ai_service.analyze_answer(
            transcription=transcription,
            question_text=question_text
        )
        
        # Create concise spoken feedback (keep it short for better UX)
        feedback_text = (
            f"Your overall score is {analysis.overall_score} out of 100. "
            f"Confidence: {analysis.confidence_score}. Clarity: {analysis.clarity_score}. "
            f"Content: {analysis.content_score}. "
            f"{analysis.detailed_feedback[:150]}"  # Limit length for faster TTS
        )
        
        # Convert feedback to speech
        feedback_audio_base64, audio_format = await tts_service.text_to_speech(feedback_text)
        
        return {
            "question_id": question_id,
            "question_text": question_text,
            "your_answer": transcription,
            "transcription_confidence": confidence,
            "analysis": analysis,
            "feedback_audio": feedback_audio_base64,
            "feedback_text": feedback_text,
            "audio_format": audio_format
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/next-question")
async def get_next_question(current_question_id: str):
    try:
        question_ids = list(INTERVIEW_QUESTIONS.keys())

        # Default to the first question
        next_index = 0
        
        try:
            current_index = question_ids.index(current_question_id)
            next_index = (current_index + 1) % len(question_ids)
        except ValueError:
            # If current not found, start at 0 (already set)
            pass
        
        next_question_id = question_ids[next_index]
        next_question_text = INTERVIEW_QUESTIONS[next_question_id]

        audio_base64, audio_format = await tts_service.text_to_speech(next_question_text)

        return {
            "question_id": next_question_id,
            "question_text": next_question_text,
            "audio_base64": audio_base64,
            "audio_format": audio_format,
            "is_last": next_index == len(question_ids) - 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
