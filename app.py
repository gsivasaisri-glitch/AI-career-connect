"""
app.py — Main Flask Application (Entry Point)
===============================================
WHY THIS FILE EXISTS:
    This is the ENTRY POINT of the entire application.
    When you run `python app.py`, Flask starts HERE.

    It has THREE responsibilities:
        1. CREATE the Flask app and configure it
        2. DEFINE all routes (URL → function mapping)
        3. CONNECT all the pieces (database, AI service, login manager)

    Think of app.py as the CONDUCTOR of an orchestra:
        - models.py provides the data layer
        - ai_service.py provides the AI brain
        - templates/ provide the visual layer
        - app.py orchestrates them all together

ROUTE ORGANIZATION:
    Page Routes (return HTML):
        /                → Landing page
        /login           → Login form
        /register        → Registration form
        /logout          → Logout action
        /dashboard       → User dashboard
        /chat            → AI chat page
        /resume          → Resume analyzer page
        /interview       → Interview prep page
        /roadmap         → Career roadmap page

    API Routes (return JSON — called by JavaScript):
        /api/chat              → Send/receive chat messages
        /api/resume/analyze    → Analyze a resume
        /api/interview/generate → Generate interview questions
        /api/roadmap/generate  → Generate career roadmap
        /api/history           → Fetch chat history
        /api/dashboard/stats   → Dashboard statistics
"""

import uuid
# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
# pyrefly: ignore [missing-import]
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, ChatHistory, ResumeAnalysis
from ai_service import AIService

# ─── App Factory ─────────────────────────────────────────────────────────────

app = Flask(__name__)
app.config.from_object(Config)

def create_app(config_name='dev'):
    return app


# Initialize extensions
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'         # Redirect here if not logged in
login_manager.login_message_category = 'info'

# Initialize AI Service
ai = AIService(
    api_key=app.config['MISTRAL_API_KEY'],
    model=app.config['MISTRAL_MODEL']
)


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login requires this — tells it how to find a user by ID."""
    return User.query.get(int(user_id))


# ─── Create Database Tables ─────────────────────────────────────────────────

with app.app_context():
    db.create_all()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGE ROUTES — These return HTML pages
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/')
def index():
    """Landing page — the first thing users see."""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration — create a new account."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login — authenticate and start session."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Dynamic dashboard — shows user's activity and stats."""
    return render_template('dashboard.html')


@app.route('/chat')
@login_required
def chat():
    """AI Chat page — general career advice chatbot."""
    return render_template('chat.html')


@app.route('/resume')
@login_required
def resume():
    """Resume Analyzer page — upload and get AI feedback."""
    return render_template('resume.html')


@app.route('/interview')
@login_required
def interview():
    """Interview Prep page — generate role-specific questions."""
    return render_template('interview.html')


@app.route('/roadmap')
@login_required
def roadmap():
    """Career Roadmap page — generate a learning path."""
    return render_template('roadmap.html')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  API ROUTES — These return JSON (called by JavaScript via fetch/AJAX)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    """
    API: Send a message to the AI chatbot.

    Expects JSON: { "message": "...", "session_id": "...", "feature": "chat" }
    Returns JSON: { "response": "..." }
    """
    data = request.get_json()
    message = data.get('message', '')
    session_id = data.get('session_id', str(uuid.uuid4()))
    feature = data.get('feature', 'chat')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    # Save user message to database
    user_msg = ChatHistory(
        user_id=current_user.id,
        role='user',
        content=message,
        feature=feature,
        session_id=session_id
    )
    db.session.add(user_msg)

    # Get conversation history for context
    history = ChatHistory.query.filter_by(
        user_id=current_user.id,
        session_id=session_id
    ).order_by(ChatHistory.created_at.asc()).all()

    messages = [{'role': h.role, 'content': h.content} for h in history]

    # Get AI response
    ai_response = ai.chat(messages, feature=feature)

    # Save AI response to database
    ai_msg = ChatHistory(
        user_id=current_user.id,
        role='assistant',
        content=ai_response,
        feature=feature,
        session_id=session_id
    )
    db.session.add(ai_msg)
    db.session.commit()

    return jsonify({
        'response': ai_response,
        'session_id': session_id
    })


@app.route('/api/resume/analyze', methods=['POST'])
@login_required
def api_analyze_resume():
    """
    API: Analyze a resume with AI.

    Expects JSON: { "resume_text": "..." }
    Returns JSON: { "analysis": "...", "id": ... }
    """
    data = request.get_json()
    resume_text = data.get('resume_text', '')

    if not resume_text:
        return jsonify({'error': 'Resume text is required'}), 400

    # Get AI analysis
    analysis = ai.analyze_resume(resume_text)

    # Save to database
    resume_record = ResumeAnalysis(
        user_id=current_user.id,
        resume_text=resume_text,
        analysis_result=analysis
    )
    db.session.add(resume_record)
    db.session.commit()

    return jsonify({
        'analysis': analysis,
        'id': resume_record.id
    })


@app.route('/api/interview/generate', methods=['POST'])
@login_required
def api_generate_interview():
    """
    API: Generate interview questions for a role.

    Expects JSON: { "role": "...", "level": "mid", "count": 10 }
    Returns JSON: { "questions": "..." }
    """
    data = request.get_json()
    role = data.get('role', '')
    level = data.get('level', 'mid')
    count = data.get('count', 10)

    if not role:
        return jsonify({'error': 'Job role is required'}), 400

    questions = ai.generate_interview_questions(role, level, count)

    # Save to chat history
    chat_record = ChatHistory(
        user_id=current_user.id,
        role='assistant',
        content=questions,
        feature='interview',
        session_id=str(uuid.uuid4())
    )
    db.session.add(chat_record)
    db.session.commit()

    return jsonify({'questions': questions})


@app.route('/api/roadmap/generate', methods=['POST'])
@login_required
def api_generate_roadmap():
    """
    API: Generate a career roadmap.

    Expects JSON: { "current_role": "...", "target_role": "...", "experience": 0 }
    Returns JSON: { "roadmap": "..." }
    """
    data = request.get_json()
    current_role = data.get('current_role', '')
    target_role = data.get('target_role', '')
    experience = data.get('experience', 0)

    if not current_role or not target_role:
        return jsonify({'error': 'Current and target roles are required'}), 400

    roadmap_content = ai.generate_career_roadmap(current_role, target_role, experience)

    # Save to chat history
    chat_record = ChatHistory(
        user_id=current_user.id,
        role='assistant',
        content=roadmap_content,
        feature='roadmap',
        session_id=str(uuid.uuid4())
    )
    db.session.add(chat_record)
    db.session.commit()

    return jsonify({'roadmap': roadmap_content})


@app.route('/api/history')
@login_required
def api_history():
    """
    API: Get chat history for the current user.

    Query params: ?feature=chat&limit=50
    Returns JSON: { "history": [...] }
    """
    feature = request.args.get('feature', None)
    limit = request.args.get('limit', 50, type=int)

    query = ChatHistory.query.filter_by(user_id=current_user.id)

    if feature:
        query = query.filter_by(feature=feature)

    chats = query.order_by(ChatHistory.created_at.desc()).limit(limit).all()

    return jsonify({
        'history': [
            {
                'id': c.id,
                'role': c.role,
                'content': c.content,
                'feature': c.feature,
                'session_id': c.session_id,
                'created_at': c.created_at.isoformat()
            }
            for c in chats
        ]
    })


@app.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    """
    API: Get dashboard statistics for the current user.

    Returns JSON with counts and recent activity.
    """
    # pyrefly: ignore [missing-import]
    from sqlalchemy import func

    total_chats = ChatHistory.query.filter_by(user_id=current_user.id).count()
    total_resumes = ResumeAnalysis.query.filter_by(user_id=current_user.id).count()

    # Count by feature
    feature_counts = db.session.query(
        ChatHistory.feature,
        func.count(ChatHistory.id)
    ).filter_by(user_id=current_user.id).group_by(ChatHistory.feature).all()

    # Recent activity (last 10 messages)
    recent = ChatHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(ChatHistory.created_at.desc()).limit(10).all()

    return jsonify({
        'total_chats': total_chats,
        'total_resumes': total_resumes,
        'feature_counts': {f: c for f, c in feature_counts},
        'recent_activity': [
            {
                'content': r.content[:100],
                'feature': r.feature,
                'role': r.role,
                'created_at': r.created_at.isoformat()
            }
            for r in recent
        ]
    })


# ─── Error Handlers ─────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404


@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server Error: {e}", exc_info=True)
    return jsonify({'error': str(e) if app.debug else 'Internal server error'}), 500



# ─── Run the Application ────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5000)
