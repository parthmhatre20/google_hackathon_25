from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class InterviewQuestion(BaseModel):
    question_id: str
    question_text: str
    category: str = "general"

class TranscriptionRequest(BaseModel):
    audio_base64: str
    question_id: str

class TranscriptionResponse(BaseModel):
    transcription: str
    confidence: float

class AnalysisRequest(BaseModel):
    transcription: str
    question_text: str
    question_id: str

class FillerWordsAnalysis(BaseModel):
    count: int
    words: List[str]
    percentage: float

class AnalysisResponse(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    confidence_score: float = Field(..., ge=0, le=100)
    clarity_score: float = Field(..., ge=0, le=100)
    content_score: float = Field(..., ge=0, le=100)
    filler_words: FillerWordsAnalysis
    strengths: List[str]
    improvements: List[str]
    detailed_feedback: str

class InterviewAttempt(BaseModel):
    user_id: str
    question_id: str
    question_text: str
    transcription: str
    analysis: AnalysisResponse
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: Optional[float] = None

class SaveAttemptRequest(BaseModel):
    user_id: str
    question_id: str
    question_text: str
    transcription: str
    analysis: AnalysisResponse
    duration_seconds: Optional[float] = None

class UserProgress(BaseModel):
    user_id: str
    total_attempts: int
    average_score: float
    recent_attempts: List[InterviewAttempt]