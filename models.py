from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import secrets

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    free_minutes_used = db.Column(db.Integer, default=0)  # tracks 1hr free quota
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    videos = db.relationship('Video', backref='uploader', lazy=True)
    purchases = db.relationship('Purchase', backref='user', lazy=True)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filepath = db.Column(db.String(300), nullable=False)  # default/original
    filepath_480p = db.Column(db.String(300), nullable=True)
    filepath_720p = db.Column(db.String(300), nullable=True)
    duration_minutes = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship('Review', backref='video', lazy=True)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    amount = db.Column(db.Float)
    stripe_payment_id = db.Column(db.String(200))
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TeacherPayout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    token = db.Column(db.String(100), unique=True)
    expires_at = db.Column(db.DateTime)

    @staticmethod
    def generate(user_id):
        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(minutes=30)
        rt = PasswordResetToken(user_id=user_id, token=token, expires_at=expiry)
        db.session.add(rt)
        db.session.commit()
        return token