from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime
from app.services.question_generator import question_generator_service
from app.services.interview_store import create_interview_session
from app.services.answer_store import save_interview_answer
from app.firebase_realtime import get_db
from app.models import GenerateQuestionsRequest, GenerateQuestionsResponse

from app.models import (
    TranscriptionRequest, TranscriptionResponse,
    AnalysisRequest, AnalysisResponse,
    SaveAttemptRequest, InterviewAttempt
)
from app.services.speech_service import speech_service
from app.services.ai_service import ai_service
from app.services.tts_service import tts_service
import base64

router = APIRouter(prefix="/api/interview", tags=["interview"])

# Fallback question bank (used if AI generation fails)
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
    question_text: str = None  # Optional: provide question text directly

@router.post("/start-session")
async def start_interview_session(
    user_id: str = Form(...),
    domain: str = Form(...)
):
    """
    Phase 2: Start a new interview session and store it in Firebase
    """
    session_id = create_interview_session(user_id, domain)

    return {
        "message": "Interview session started",
        "session_id": session_id
    }


@router.post("/save-answer")
async def save_answer(
    session_id: str = Form(...),
    question_id: str = Form(...),
    question_text: str = Form(...),
    transcription: str = Form(...),
    confidence: float = Form(...)
):
    """
    Phase 3: Save spoken answer & transcript to Firebase
    """
    answer_id = save_interview_answer(
        session_id=session_id,
        question_id=question_id,
        question_text=question_text,
        transcription=transcription,
        confidence=confidence
    )

    return {
        "message": "Answer saved successfully",
        "answer_id": answer_id
    }


class CompleteSessionRequest(BaseModel):
    session_id: str
    average_score: float

@router.post("/complete-session")
async def complete_session(request: CompleteSessionRequest):
    """
    Mark interview session as completed and save average score
    """
    try:
        db = get_db()
        session_ref = db.child("interview_sessions").child(request.session_id)
        
        session_ref.update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "average_score": request.average_score
        })
        
        return {"message": "Session marked as completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

@router.post("/question/speak")
async def speak_question(request: QuestionSpeakRequest):
    """
    Get a question as audio (AI speaks it)
    Returns the question text and audio in base64 format
    """
    try:
        # Use provided question text or fallback to question bank
        question_text = request.question_text or INTERVIEW_QUESTIONS.get(request.question_id)
        
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

@router.post("/generate-questions", response_model=GenerateQuestionsResponse)
async def generate_questions(request: GenerateQuestionsRequest):
    """
    Generate personalized interview questions based on resume & domain
    """
    try:
        result = await question_generator_service.generate_questions(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_interview_history(user_id: str):
    """
    Get user's interview history from Firebase
    Returns last 30 days of interview sessions
    """
    try:
        from datetime import datetime, timedelta
        db = get_db()
        
        # Get all sessions for this user
        user_sessions_ref = db.child("users").child(user_id).child("sessions").get()
        
        if not user_sessions_ref:
            return {"sessions": []}
        
        session_ids = list(user_sessions_ref.keys()) if isinstance(user_sessions_ref, dict) else []
        
        sessions = []
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        for session_id in session_ids:
            session_data = db.child("interview_sessions").child(session_id).get()
            
            if session_data:
                created_at = datetime.fromisoformat(session_data.get("created_at", ""))
                
                # Only include sessions from last 30 days
                if created_at >= cutoff_date:
                    # Get answer count from correct location
                    answers_ref = db.child("interview_sessions").child(session_id).child("answers").get()
                    answer_count = len(answers_ref) if answers_ref else 0
                    
                    sessions.append({
                        "session_id": session_id,
                        "domain": session_data.get("domain", "Unknown"),
                        "created_at": session_data.get("created_at"),
                        "status": session_data.get("status", "completed"),
                        "questions_answered": answer_count
                    })
        
        # Sort by date (newest first)
        sessions.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {"sessions": sessions}
        
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_details(session_id: str):
    """
    Get full details of an interview session (read-only)
    """
    try:
        db = get_db()
        
        # Get session info
        session_data = db.child("interview_sessions").child(session_id).get()
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all answers for this session
        answers_ref = db.child("interview_sessions").child(session_id).child("answers").get()
        answers = []
        
        if answers_ref:
            for answer_id, answer_data in answers_ref.items():
                answers.append({
                    "answer_id": answer_id,
                    "question_id": answer_data.get("question_id"),
                    "question_text": answer_data.get("question_text"),
                    "transcription": answer_data.get("transcription"),
                    "confidence": answer_data.get("confidence"),
                    "created_at": answer_data.get("created_at")
                })
        
        # Sort answers by question_id
        answers.sort(key=lambda x: x.get("question_id", ""))
        
        return {
            "session_id": session_id,
            "domain": session_data.get("domain"),
            "created_at": session_data.get("created_at"),
            "status": session_data.get("status"),
            "average_score": session_data.get("average_score"),
            "answers": answers
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class RenameSessionRequest(BaseModel):
    new_name: str

@router.put("/session/{session_id}/rename")
async def rename_session(session_id: str, request: RenameSessionRequest):
    """
    Rename an interview session
    """
    try:
        db = get_db()
        
        # Check if session exists
        session_data = db.child("interview_sessions").child(session_id).get()
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update the domain/title
        db.child("interview_sessions").child(session_id).update({
            "domain": request.new_name
        })
        
        return {"message": "Session renamed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error renaming session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete an interview session and all its answers
    """
    try:
        db = get_db()
        
        # Get session to find user_id
        session_data = db.child("interview_sessions").child(session_id).get()
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        user_id = session_data.get("user_id")
        
        # Delete session from interview_sessions
        db.child("interview_sessions").child(session_id).delete()
        
        # Remove session reference from user's sessions
        if user_id:
            db.child("users").child(user_id).child("sessions").child(session_id).delete()
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Create a new router for user operations
user_router = APIRouter(prefix="/api/user", tags=["user"])

class DeleteAccountRequest(BaseModel):
    user_id: str

@user_router.delete("/delete-account")
async def delete_user_account(request: DeleteAccountRequest):
    """
    Delete user account and all associated interview data
    """
    try:
        db = get_db()
        user_id = request.user_id
        print(f"🗑️ Deleting account for user: {user_id}")
        
        # Get all user sessions
        user_sessions_ref = db.child("users").child(user_id).child("sessions").get()
        print(f"   User sessions found: {user_sessions_ref}")
        
        if user_sessions_ref:
            session_ids = list(user_sessions_ref.keys()) if isinstance(user_sessions_ref, dict) else []
            print(f"   Deleting {len(session_ids)} sessions...")
            
            # Delete each interview session and its answers
            for session_id in session_ids:
                try:
                    db.child("interview_sessions").child(session_id).delete()
                    print(f"   ✓ Deleted session: {session_id}")
                except Exception as e:
                    print(f"   ✗ Failed to delete session {session_id}: {e}")
        
        # Delete user data
        try:
            db.child("users").child(user_id).delete()
            print(f"   ✓ Deleted user node")
        except Exception as e:
            print(f"   ✗ Failed to delete user node: {e}")
        
        print(f"✅ Account deletion completed for: {user_id}")
        return {"message": "Account and all data deleted successfully"}
        
    except Exception as e:
        print(f"❌ Error deleting account: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
