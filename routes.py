from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Quiz, Exam
from chat_request import generate_quiz_questions
import json
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/pdf_viewer')
@login_required
def pdf_viewer():
    return render_template('pdf_viewer.html')

@app.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html')

@app.route('/exam')
@login_required
def exam():
    return render_template('exam.html')

@app.route('/generate_quiz', methods=['POST'])
@login_required
def generate_quiz():
    content = request.json.get('content')
    questions = generate_quiz_questions(content)
    return jsonify(json.loads(questions))

@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    score = request.json.get('score')
    quiz = Quiz(user_id=current_user.id, score=score, date=datetime.utcnow())
    db.session.add(quiz)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/submit_exam', methods=['POST'])
@login_required
def submit_exam():
    score = request.json.get('score')
    exam = Exam(user_id=current_user.id, score=score, date=datetime.utcnow())
    db.session.add(exam)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/update_progress', methods=['POST'])
@login_required
def update_progress():
    progress = request.json.get('progress')
    current_user.progress = progress
    db.session.commit()
    return jsonify({'success': True})
