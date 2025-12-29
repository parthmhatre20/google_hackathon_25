from datetime import datetime
from app.firebase_realtime import get_db

def save_interview_answer(
    session_id: str,
    question_id: str,
    question_text: str,
    transcription: str,
    confidence: float
):
    db = get_db()

    answers_ref = (
        db.child("interview_sessions")
          .child(session_id)
          .child("answers")
          .push()
    )

    answer_data = {
        "question_id": question_id,
        "question_text": question_text,
        "transcription": transcription,
        "confidence": confidence,
        "created_at": datetime.utcnow().isoformat()
    }

    answers_ref.set(answer_data)

    return answers_ref.key
