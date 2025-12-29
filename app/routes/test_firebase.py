from fastapi import APIRouter
from app.firebase_realtime import get_db
from datetime import datetime

router = APIRouter(tags=["Firebase Test"])

@router.get("/test-realtime")
def test_realtime():
    ref = get_db().child("test_data")
    ref.push({
        "message": "Realtime database connected!",
        "timestamp": datetime.utcnow().isoformat()
    })
    return {"status": "success", "message": "Data written to realtime DB"}
