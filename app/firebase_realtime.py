import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Production Firebase setup
if not firebase_admin._apps:
    # Try to use service account credentials from .env
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        print(f"✅ Firebase credentials loaded from: {cred_path}")
    else:
        # Fallback to Application Default Credentials
        cred = credentials.ApplicationDefault()
        print("⚠️  Firebase service initialized without credentials (will not work until configured)")
    
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://interviewflow-f23b4-default-rtdb.firebaseio.com"
    })

def get_db():
    return db.reference("/")
