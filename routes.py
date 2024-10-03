from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Quiz, Exam, LearningItem, Flashcard, MatchingExercise, SortingExercise, FillInTheBlankExercise
from chat_request import generate_quiz_questions, generate_lesson
import json
from datetime import datetime
import os

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
    pdf_dir = os.path.join(app.static_folder, 'pdfs')
    pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    return render_template('pdf_viewer.html', pdfs=pdfs)

@app.route('/quiz')
@login_required
def quiz():
    pdf_dir = os.path.join(app.static_folder, 'pdfs')
    pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    return render_template('quiz.html', pdfs=pdfs)

@app.route('/exam')
@login_required
def exam():
    return render_template('exam.html')

@app.route('/generate_quiz', methods=['POST'])
@login_required
def generate_quiz():
    pdf_name = request.json.get('content')
    questions = generate_quiz_questions(pdf_name)
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

@app.route('/spaced_repetition')
@login_required
def spaced_repetition():
    return render_template('spaced_repetition.html')

@app.route('/get_due_items', methods=['GET'])
@login_required
def get_due_items():
    due_items = LearningItem.query.filter(
        LearningItem.user_id == current_user.id,
        LearningItem.next_review <= datetime.utcnow()
    ).all()
    return jsonify([{
        'id': item.id,
        'content': item.content,
        'difficulty': item.difficulty
    } for item in due_items])

@app.route('/update_learning_item', methods=['POST'])
@login_required
def update_learning_item():
    item_id = request.json.get('id')
    performance = request.json.get('performance')
    item = LearningItem.query.get(item_id)
    if item and item.user_id == current_user.id:
        item.update_review_schedule(performance)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/flashcards')
@login_required
def flashcards():
    return render_template('flashcards.html')

@app.route('/get_flashcards', methods=['GET'])
@login_required
def get_flashcards():
    flashcards = Flashcard.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': card.id,
        'front': card.front,
        'back': card.back,
        'difficulty': card.difficulty
    } for card in flashcards])

@app.route('/add_flashcard', methods=['POST'])
@login_required
def add_flashcard():
    front = request.json.get('front')
    back = request.json.get('back')
    flashcard = Flashcard(user_id=current_user.id, front=front, back=back)
    db.session.add(flashcard)
    db.session.commit()
    return jsonify({'success': True, 'id': flashcard.id})

@app.route('/update_flashcard', methods=['POST'])
@login_required
def update_flashcard():
    card_id = request.json.get('id')
    performance = request.json.get('performance')
    card = Flashcard.query.get(card_id)
    if card and card.user_id == current_user.id:
        card.update_review_schedule(performance)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/matching_exercises')
@login_required
def matching_exercises():
    return render_template('matching_exercises.html')

@app.route('/get_matching_exercises', methods=['GET'])
@login_required
def get_matching_exercises():
    exercises = MatchingExercise.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': exercise.id,
        'question': exercise.question,
        'pairs': exercise.pairs,
        'difficulty': exercise.difficulty
    } for exercise in exercises])

@app.route('/add_matching_exercise', methods=['POST'])
@login_required
def add_matching_exercise():
    question = request.json.get('question')
    pairs = request.json.get('pairs')
    exercise = MatchingExercise(user_id=current_user.id, question=question, pairs=pairs)
    db.session.add(exercise)
    db.session.commit()
    return jsonify({'success': True, 'id': exercise.id})

@app.route('/update_matching_exercise', methods=['POST'])
@login_required
def update_matching_exercise():
    exercise_id = request.json.get('id')
    performance = request.json.get('performance')
    exercise = MatchingExercise.query.get(exercise_id)
    if exercise and exercise.user_id == current_user.id:
        exercise.update_difficulty(performance)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/sorting_exercises')
@login_required
def sorting_exercises():
    return render_template('sorting_exercises.html')

@app.route('/get_sorting_exercises', methods=['GET'])
@login_required
def get_sorting_exercises():
    exercises = SortingExercise.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': exercise.id,
        'question': exercise.question,
        'items': exercise.items,
        'difficulty': exercise.difficulty
    } for exercise in exercises])

@app.route('/add_sorting_exercise', methods=['POST'])
@login_required
def add_sorting_exercise():
    question = request.json.get('question')
    items = request.json.get('items')
    correct_order = request.json.get('correct_order')
    exercise = SortingExercise(user_id=current_user.id, question=question, items=items, correct_order=correct_order)
    db.session.add(exercise)
    db.session.commit()
    return jsonify({'success': True, 'id': exercise.id})

@app.route('/update_sorting_exercise', methods=['POST'])
@login_required
def update_sorting_exercise():
    exercise_id = request.json.get('id')
    performance = request.json.get('performance')
    exercise = SortingExercise.query.get(exercise_id)
    if exercise and exercise.user_id == current_user.id:
        exercise.update_difficulty(performance)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/fill_in_the_blank_exercises')
@login_required
def fill_in_the_blank_exercises():
    return render_template('fill_in_the_blank.html')

@app.route('/get_fill_in_the_blank_exercises', methods=['GET'])
@login_required
def get_fill_in_the_blank_exercises():
    exercises = FillInTheBlankExercise.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': exercise.id,
        'question': exercise.question,
        'difficulty': exercise.difficulty
    } for exercise in exercises])

@app.route('/add_fill_in_the_blank_exercise', methods=['POST'])
@login_required
def add_fill_in_the_blank_exercise():
    question = request.json.get('question')
    answer = request.json.get('answer')
    exercise = FillInTheBlankExercise(user_id=current_user.id, question=question, answer=answer)
    db.session.add(exercise)
    db.session.commit()
    return jsonify({'success': True, 'id': exercise.id})

@app.route('/update_fill_in_the_blank_exercise', methods=['POST'])
@login_required
def update_fill_in_the_blank_exercise():
    exercise_id = request.json.get('id')
    performance = request.json.get('performance')
    exercise = FillInTheBlankExercise.query.get(exercise_id)
    if exercise and exercise.user_id == current_user.id:
        exercise.update_difficulty(performance)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/generate_lesson', methods=['GET', 'POST'])
@login_required
def generate_lesson_route():
    if request.method == 'POST':
        try:
            lesson_content = generate_lesson()
            return render_template('lesson.html', lesson_content=json.loads(lesson_content))
        except FileNotFoundError as e:
            return render_template('generate_lesson.html', error=str(e))
        except ValueError as e:
            return render_template('generate_lesson.html', error=str(e))
        except Exception as e:
            return render_template('generate_lesson.html', error="An unexpected error occurred. Please try again later.")
    
    return render_template('generate_lesson.html')