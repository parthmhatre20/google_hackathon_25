import firebase_admin
from firebase_admin import credentials, auth
from flask import Flask,render_template,request,redirect,url_for,session,jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask('__name__',template_folder='templates')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize Firebase only if credentials file exists
firebase_initialized = False
firebase_cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'interviewflow-f23b4-firebase-adminsdk-fbsvc-8db576c916.json')

if os.path.exists(firebase_cred_path):
    try:
        cred = credentials.Certificate(firebase_cred_path)
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        print("✅ Firebase initialized successfully!")
    except Exception as e:
        print(f"⚠️  Firebase initialization failed: {e}")
else:
    print("⚠️  Firebase credentials not found. Auth features will not work.")
    print(f"   Looking for: {firebase_cred_path}")

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

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/interview_section')
@login_required
def interview_section():
    return render_template("Interview_section.html")

@app.route('/test')
def test_interview():
    """Test page without authentication - DELETE BEFORE PRODUCTION"""
    return render_template("interview_test.html")

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