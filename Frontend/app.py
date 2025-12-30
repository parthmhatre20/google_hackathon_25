import firebase_admin
from firebase_admin import credentials, auth
from flask import Flask,render_template,request,redirect,url_for,session,jsonify
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask('__name__',template_folder='templates')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize Firebase only if not already initialized (combined server may init first)
firebase_initialized = False

if not firebase_admin._apps:
    cred = None
    
    # Option 1: JSON credentials from environment variable (for Render)
    cred_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
    if cred_json:
        try:
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            print("✅ Flask: Firebase credentials loaded from FIREBASE_CREDENTIALS_JSON")
        except json.JSONDecodeError as e:
            print(f"⚠️  Flask: Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")
    
    # Option 2: File path (for local development)
    if not cred:
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'interviewflow-f23b4-firebase-adminsdk-fbsvc-8db576c916.json')
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            print(f"✅ Flask: Firebase credentials loaded from file: {cred_path}")
    
    if cred:
        try:
            firebase_admin.initialize_app(cred)
            firebase_initialized = True
            print("✅ Flask: Firebase initialized successfully!")
        except Exception as e:
            print(f"⚠️  Flask: Firebase initialization failed: {e}")
    else:
        print("⚠️  Flask: Firebase credentials not found. Auth features will not work.")
else:
    firebase_initialized = True
    print("✅ Flask: Firebase already initialized")

from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return render_template("index2.html")


@app.route('/login')
def login():
    return render_template("sign_in.html")

@app.route('/signup')
def signup():
    return render_template('sign_up2.html')

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login")) if request.method == "GET" else jsonify({"message": "Logged out"})

@app.route('/interview_section')
@login_required
def interview_section():
    return render_template("Interview_section.html")

@app.route('/test')
def test_interview():
    """Test page without authentication - DELETE BEFORE PRODUCTION"""
    return render_template("interview_test.html")

@app.route('/settings')
def settings():
    return render_template("settings.html")

@app.route("/session_login", methods=["POST"])
def session_login():
    if not firebase_initialized:
        return jsonify({"error": "Firebase not configured"}), 500
    
    data = request.json
    token = data.get("token")

    try:
        decoded = auth.verify_id_token(token)
        session["user_id"] = decoded["uid"]
        session["email"] = decoded.get("email")
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 401


if __name__=='__main__':
    app.run(debug=True)