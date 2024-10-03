from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    progress = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

class LearningItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Float, default=0.5)
    last_reviewed = db.Column(db.DateTime, default=datetime.utcnow)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    interval = db.Column(db.Integer, default=1)  # interval in days

    @staticmethod
    def calculate_next_review(difficulty, interval):
        if difficulty < 0.3:
            interval = max(1, interval // 2)
        elif difficulty > 0.7:
            interval = interval * 2
        else:
            interval = interval + 1
        return datetime.utcnow() + timedelta(days=interval), interval

    def update_review_schedule(self, performance):
        self.difficulty = (self.difficulty + performance) / 2
        self.last_reviewed = datetime.utcnow()
        self.next_review, self.interval = self.calculate_next_review(self.difficulty, self.interval)

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime, default=datetime.utcnow)
    difficulty = db.Column(db.Float, default=0.5)
    interval = db.Column(db.Integer, default=1)  # interval in days

    def update_review_schedule(self, performance):
        self.difficulty = (self.difficulty + performance) / 2
        self.last_reviewed = datetime.utcnow()
        self.interval = LearningItem.calculate_next_review(self.difficulty, self.interval)[1]

class MatchingExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    pairs = db.Column(db.JSON, nullable=False)  # Store pairs as JSON: [{"left": "item1", "right": "item2"}, ...]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_attempted = db.Column(db.DateTime)
    difficulty = db.Column(db.Float, default=0.5)

    def update_difficulty(self, performance):
        self.difficulty = (self.difficulty + performance) / 2
        self.last_attempted = datetime.utcnow()

class SortingExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    items = db.Column(db.JSON, nullable=False)  # Store items as JSON: ["item1", "item2", "item3", ...]
    correct_order = db.Column(db.JSON, nullable=False)  # Store correct order as JSON: [0, 2, 1, ...]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_attempted = db.Column(db.DateTime)
    difficulty = db.Column(db.Float, default=0.5)

    def update_difficulty(self, performance):
        self.difficulty = (self.difficulty + performance) / 2
        self.last_attempted = datetime.utcnow()

class FillInTheBlankExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_attempted = db.Column(db.DateTime)
    difficulty = db.Column(db.Float, default=0.5)

    def update_difficulty(self, performance):
        self.difficulty = (self.difficulty + performance) / 2
        self.last_attempted = datetime.utcnow()
