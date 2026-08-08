"""
models.py — Database Models (SQLAlchemy ORM)
=============================================
WHY THIS FILE EXISTS:
    Defines the STRUCTURE of your database tables as Python classes.
    Instead of writing raw SQL like "CREATE TABLE users (...)", you define
    a User class and SQLAlchemy translates it to SQL for you.

    This is the ORM (Object-Relational Mapping) layer.
    Each class = one database table.
    Each attribute = one column.

MODELS DEFINED HERE:
    1. User         — Stores registered users (login/signup)
    2. ChatHistory  — Stores every AI conversation message
    3. ResumeAnalysis — Stores resume analysis results
"""

from datetime import datetime
# pyrefly: ignore [missing-import]
from flask_sqlalchemy import SQLAlchemy
# pyrefly: ignore [missing-import]
from flask_login import UserMixin
# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy — this object is imported by app.py
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User table — stores account credentials.

    WHY UserMixin?
        Flask-Login requires certain methods (is_authenticated, get_id, etc.)
        UserMixin provides all of them automatically.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships — one user has many chats and resume analyses
    chats = db.relationship('ChatHistory', backref='user', lazy='dynamic')
    resumes = db.relationship('ResumeAnalysis', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Hash the password before storing — NEVER store plain text passwords."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class ChatHistory(db.Model):
    """
    ChatHistory table — stores every message in AI conversations.

    WHY store chat history?
        1. Users can revisit past conversations
        2. Dashboard can show usage statistics
        3. AI can use context from previous messages

    The 'feature' column tracks WHICH feature generated this chat:
        - 'chat'      → General AI chat
        - 'resume'    → Resume analyzer conversation
        - 'interview' → Interview question generation
        - 'roadmap'   → Career roadmap generation
    """
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)       # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)           # The actual message
    feature = db.Column(db.String(20), default='chat')     # Which feature area
    session_id = db.Column(db.String(36), nullable=True)   # Group messages into sessions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Chat {self.role}: {self.content[:30]}...>'


class ResumeAnalysis(db.Model):
    """
    ResumeAnalysis table — stores uploaded resume text and AI analysis.

    WHY a separate table?
        Resume data can be large (full text). Keeping it separate from
        chat history keeps queries fast and data organized.
    """
    __tablename__ = 'resume_analyses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_text = db.Column(db.Text, nullable=False)       # Raw resume content
    analysis_result = db.Column(db.Text, nullable=True)    # AI-generated analysis
    score = db.Column(db.Integer, nullable=True)           # Resume score (0-100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Resume Analysis #{self.id} by User {self.user_id}>'
