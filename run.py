"""
AI Mock Interview - Single Command Startup
Run: python run.py
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def setup_ffmpeg():
    """Add FFmpeg to PATH if not already present"""
    ffmpeg_path = Path.home() / "AppData/Local/Temp/ffmpeg/ffmpeg-8.0.1-essentials_build/bin"
    
    if ffmpeg_path.exists():
        ffmpeg_str = str(ffmpeg_path)
        if ffmpeg_str not in os.environ.get("PATH", ""):
            os.environ["PATH"] += os.pathsep + ffmpeg_str
            print("✅ FFmpeg added to PATH")
    else:
        print("⚠️  FFmpeg not found. Please install it first!")
        print(f"   Expected location: {ffmpeg_path}")
        print("\n   Download: https://ffmpeg.org/download.html")
        print("   Or continue without FFmpeg (transcription will fail)\n")

def main():
    print("🚀 Starting AI Mock Interview Application...\n")
    
    # Setup FFmpeg
    setup_ffmpeg()
    
    # Start backend
    print("🎤 Starting Backend (FastAPI) on http://localhost:8000")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=Path(__file__).parent
    )
    
    # Wait for backend to start
    time.sleep(3)
    
    # Start frontend
    print("🌐 Starting Frontend (Flask) on http://127.0.0.1:5000")
    frontend = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=Path(__file__).parent / "Frontend"
    )
    
    print("\n" + "="*60)
    print("✅ Application is running!")
    print("="*60)
    print("🌐 Main App:  http://127.0.0.1:5000")
    print("🧪 Test Page: http://127.0.0.1:5000/test")
    print("📡 API Docs:  http://localhost:8000/docs")
    print("="*60)
    print("\nPress Ctrl+C to stop both servers\n")
    
    try:
        # Wait for both processes
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print("✅ Servers stopped. Goodbye!")

if __name__ == "__main__":
    main()
