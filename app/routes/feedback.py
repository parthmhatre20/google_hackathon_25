from fastapi import APIRouter, HTTPException
from app.services.firebase_service import firebase_service
from typing import List

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

@router.get("/user/{user_id}/attempts")
async def get_user_attempts(user_id: str, limit: int = 10):
    """
    Get user's interview attempts
    """
    try:
        attempts = await firebase_service.get_user_attempts(user_id, limit)
        return {"attempts": attempts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/progress")
async def get_user_progress(user_id: str):
    """
    Get user's overall progress and statistics
    """
    try:
        progress = await firebase_service.get_user_progress(user_id)
        
        if not progress:
            return {
                "user_id": user_id,
                "total_attempts": 0,
                "average_score": 0.0,
                "recent_attempts": []
            }
        
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/attempt/{attempt_id}")
async def delete_attempt(attempt_id: str):
    """
    Delete an interview attempt
    """
    try:
        success = await firebase_service.delete_attempt(attempt_id)
        
        if success:
            return {"success": True, "message": "Attempt deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Attempt not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))