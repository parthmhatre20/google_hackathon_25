import firebase_admin
from firebase_admin import credentials, auth
from flask import Flask,render_template,request,redirect,url_for,session,jsonify

app = Flask('__name__',template_folder='templates')
app.secret_key = "super-secret-key"  # change later dont push in public repo
#dont push it in public repo
cred = credentials.Certificate("interviewflow-f23b4-firebase-adminsdk-fbsvc-8db576c916.json")
firebase_admin.initialize_app(cred)

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

@app.route("/session_login", methods=["POST"])
def session_login():
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