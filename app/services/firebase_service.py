from app.models import InterviewAttempt, UserProgress
from typing import List, Optional

class FirebaseService:
    def __init__(self):
        self.db = None
        print("⚠️  Firebase service initialized without credentials (will not work until configured)")
    
    async def save_attempt(self, attempt: InterviewAttempt) -> str:
        raise Exception("Firebase not configured. Please add Firebase credentials to use this feature.")
    
    async def get_user_attempts(self, user_id: str, limit: int = 10) -> List[InterviewAttempt]:
        return []
    
    async def get_user_progress(self, user_id: str) -> Optional[UserProgress]:
        return UserProgress(
            user_id=user_id,
            total_attempts=0,
            average_score=0.0,
            recent_attempts=[]
        )
    
    async def delete_attempt(self, attempt_id: str) -> bool:
        return False

firebase_service = FirebaseService()