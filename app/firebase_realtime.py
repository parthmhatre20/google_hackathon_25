import firebase_admin
from firebase_admin import credentials, db
import os
import json
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Production Firebase setup
if not firebase_admin._apps:
    cred = None
    
    # Option 1: JSON credentials from environment variable (for Render/production)
    cred_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
    if cred_json:
        try:
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            print("✅ Firebase credentials loaded from FIREBASE_CREDENTIALS_JSON env var")
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")
    
    # Option 2: File path to credentials (for local development)
    if not cred:
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            print(f"✅ Firebase credentials loaded from file: {cred_path}")
    
    # Option 3: Fallback to Application Default Credentials
    if not cred:
        try:
            cred = credentials.ApplicationDefault()
            print("⚠️  Using Application Default Credentials")
        except Exception as e:
            print(f"❌ No Firebase credentials available: {e}")
            raise Exception("Firebase credentials not configured. Set FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_PATH")
    
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://interviewflow-f23b4-default-rtdb.firebaseio.com"
    })

def get_db():
    return db.reference("/")
