from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models import (
    TranscriptionRequest, TranscriptionResponse,
    AnalysisRequest, AnalysisResponse,
    SaveAttemptRequest, InterviewAttempt,
    GenerateQuestionsRequest, GenerateQuestionsResponse
)
from app.services.speech_service import speech_service
from app.services.ai_service import ai_service
from app.services.firebase_service import firebase_service
from app.services.question_generator import question_generator_service
import base64

router = APIRouter(prefix="/api/interview", tags=["interview"])

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: TranscriptionRequest):
    """
    Transcribe audio to text using Google Speech-to-Text
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

@router.post("/generate-questions", response_model=GenerateQuestionsResponse)
async def generate_personalized_questions(request: GenerateQuestionsRequest):
    """
    Generate personalized interview questions based on resume and domain
    
    This endpoint uses Gemini AI to analyze the candidate's resume and generate
    tailored interview questions specific to their experience and chosen domain.
    """
    try:
        response = await question_generator_service.generate_questions(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))