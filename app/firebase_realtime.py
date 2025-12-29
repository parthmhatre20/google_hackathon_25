import firebase_admin
from firebase_admin import credentials, db
import os

# Connect to local emulator
os.environ["FIREBASE_DATABASE_EMULATOR_HOST"] = "localhost:9000"

if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        "databaseURL": "http://localhost:9000/?ns=interviewflow-f23b4"
    })

def get_db():
    return db.reference("/")
