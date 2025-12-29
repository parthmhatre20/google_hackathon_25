from datetime import datetime
from app.firebase_realtime import get_db

def create_interview_session(user_id: str, domain: str):
    """
    Creates a new interview session in Firebase Realtime DB
    """
    db = get_db()

    # Create new session with auto-generated ID
    session_ref = db.child("interview_sessions").push()

    session_data = {
        "user_id": user_id,
        "domain": domain,
        "created_at": datetime.utcnow().isoformat(),
        "status": "in_progress"
    }

    session_ref.set(session_data)

    # Link session to user
    db.child("users").child(user_id).child("sessions").child(session_ref.key).set(True)

    return session_ref.key
