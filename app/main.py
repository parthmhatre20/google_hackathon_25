from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from app.config import settings
from app.routes import interview_router, user_router

# Create FastAPI application
app = FastAPI(
    title="AI Interview Coach API",
    description="Backend API for AI-powered interview practice platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(interview_router)
app.include_router(user_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Interview Coach API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )