"""
Combined FastAPI + Flask server for Render deployment
Single service running both API and Frontend
"""
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.wsgi import WSGIMiddleware

# Import FastAPI app components
from app.config import settings
from app.routes import interview_router, user_router

# Import Flask app
from Frontend.app import app as flask_app

# Create main FastAPI application
app = FastAPI(
    title="AI Interview Coach",
    description="AI-powered interview practice platform",
    version="1.0.0"
)

# Configure CORS - allow all origins for Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check FIRST (before any mounts)
@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "service": "ai-interview-coach"}

@app.get("/api/health")
async def api_health_check():
    """API health check"""
    return {"status": "healthy", "api": "active"}

# Include API routers - they already have /api prefix in their definition
app.include_router(interview_router)
app.include_router(user_router)

# Mount static files from Frontend
app.mount("/static", StaticFiles(directory="Frontend/static"), name="static")

# Mount Flask app LAST - it catches everything else
app.mount("/", WSGIMiddleware(flask_app))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
