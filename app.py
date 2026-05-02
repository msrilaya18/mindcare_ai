import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import google.generativeai as genai
from dotenv import load_dotenv

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

# --- SCM BASELINE VERSION ---
APP_VERSION = "2.0.1"

app = Flask(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# App Config for Auth & Email
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-auth-key-123')

# Absolute path for the database file in the project root
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mindcare.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME', 'noreply@mindcare.ai')

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# --- DATABASE MODELS ---


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(4), nullable=True)
    history = db.relationship('History', backref='user', lazy=True)


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    stress_level = db.Column(db.String(10), nullable=False)
    empathy_response = db.Column(db.Text, nullable=False)
    mood_emoji = db.Column(db.String(10), nullable=True)
    affirmation = db.Column(db.Text, nullable=True)
    next_step = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- AI LOGIC ---


SYSTEM_PROMPT = """
You are MindCare AI, a high-end mental health support assistant.
Analyze the user's message and respond ONLY with a valid JSON object in this exact format:
{
  "stress_level": "HIGH" or "MEDIUM" or "LOW",
  "mood_emoji": "A single Unicode emoji character that perfectly captures the specific sub-emotion (e.g. 😰 for anxiety, 💔 for heartbreak, 😣 for burnout, 😞 for disappointment, 😟 for worry). No text descriptions.",
  "empathy": "A warm, premium, 2-3 sentence empathetic response",
  "daily_affirmation": "A unique, uplifting 1-sentence affirmation",
  "next_step": "One small, concrete immediate action they can take right now",
  "tips": ["tip 1", "tip 2", "tip 3"],
  "helplines": [
    {"name": "Line Name", "number": "Contact Info"}
  ]
}

### Guidelines for Helplines:
- If stress_level is HIGH: Always provide urgent crisis hotlines like 'Vandrevala Foundation (1860-2662-345)' and 'iCall (9152987821)'.
- If stress_level is MEDIUM/LOW: Provide general counselling or wellness resources like 'AASRA (9820466726)'.

Stress classification rules:
- HIGH: mentions crisis, hopeless, suicidal, breakdown, panic, can't cope
- MEDIUM: mentions anxious, sad, struggling, pressure, exhausted
- LOW: mild sadness, general concern, seeking advice
"""


def classify_and_respond(user_text):
    """Send user text to Gemini and return parsed response."""
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

    response = model.generate_content(
        user_text,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            response_mime_type="application/json",
        )
    )

    raw = response.text.strip()
    return json.loads(raw)


# --- ROUTES ---


@app.route("/")
def index():
    return render_template("index.html", version=APP_VERSION)


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_text = data.get("text", "").strip()

    if not user_text:
        return jsonify({"error": "No text provided"}), 400
    if len(user_text) > 1000:
        return jsonify({"error": "Text too long. Please keep it under 1000 characters."}), 400

    try:
        result = classify_and_respond(user_text)

        # Save to database if user is logged in
        if current_user.is_authenticated:
            history_entry = History(
                user_id=current_user.id,
                prompt=user_text,
                stress_level=result.get("stress_level", "LOW"),
                empathy_response=result.get("empathy", ""),
                mood_emoji=result.get("mood_emoji", "🧠"),
                affirmation=result.get("daily_affirmation", ""),
                next_step=result.get("next_step", "")
            )
            db.session.add(history_entry)
            db.session.commit()

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history", methods=["GET"])
@login_required
def get_history():
    """Fetch past prompts for the logged-in user."""
    history = History.query.filter_by(user_id=current_user.id).all()
    data = [{
        "prompt": h.prompt,
        "stress_level": h.stress_level,
        "empathy_response": h.empathy_response,
        "mood_emoji": h.mood_emoji,
        "date": h.timestamp.strftime("%Y-%m-%d %H:%M")
    } for h in history]
    return jsonify(data)


# --- AUTH ROUTES ---


def send_otp_email(email, otp):
    """Attempt to send OTP, else print to console."""
    if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
        try:
            msg = Message("MindCare AI - Your Verification Code",
                          recipients=[email])
            msg.body = f"Your code is: {otp}"
            mail.send(msg)
            print(f"OTP email sent successfully to {email}")
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")
            print(f"FALLBACK OTP PRINTED FOR PRESENTATION: {otp}")
    else:
        print("\n[MOCK EMAIL MODE] Email credentials not configured.")
        print("If this is a presentation, tell your faculty you received the OTP:")
        print(f"OTP for {email} is: {otp}\n")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.is_verified:
            flash("Email address already exists. Please log in.", "danger")
            return redirect(url_for('login'))

        otp = str(random.randint(1000, 9999))
        hashed_pw = generate_password_hash(password)

        if user and not user.is_verified:
            # Overwrite unverified account pending OTP
            user.name = name
            user.password_hash = hashed_pw
            user.otp = otp
        else:
            new_user = User(name=name, email=email,
                            password_hash=hashed_pw,
                            otp=otp, is_verified=False)
            db.session.add(new_user)

        db.session.commit()
        send_otp_email(email, otp)

        # Store email in session to verify OTP on next page
        from flask import session
        session['pending_email'] = email
        return redirect(url_for('verify'))

    return render_template("signup.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    from flask import session
    email = session.get('pending_email')

    if not email:
        return redirect(url_for('signup'))

    if request.method == "POST":
        otp_input = request.form.get("otp")
        user = User.query.filter_by(email=email).first()

        if user and user.otp == otp_input:
            user.is_verified = True
            user.otp = None
            db.session.commit()

            # Auto log them in
            login_user(user)
            session.pop('pending_email', None)
            flash("Account verified! Welcome to MindCare AI.", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid OTP code. Please try again.", "danger")

    return render_template("verify.html", email=email)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Please check your login details and try again.", "danger")
            return redirect(url_for('login'))

        if not user.is_verified:
            from flask import session
            session['pending_email'] = email

            # Regenerate OTP
            otp = str(random.randint(1000, 9999))
            user.otp = otp
            db.session.commit()
            send_otp_email(email, otp)

            flash("Please verify your email to log in. OTP sent.", "warning")
            return redirect(url_for('verify'))

        login_user(user, remember=remember)
        return redirect(url_for('index'))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Create DB tables if they don't exist
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1",
            host="0.0.0.0", port=5000)
