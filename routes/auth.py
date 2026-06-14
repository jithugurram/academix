from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from datetime import datetime, timedelta
from models import db, User, PasswordResetToken
from app import mail

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'student')  # student or teacher

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.signup'))

        user = User(
            name=name, email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created. Please login.')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            return redirect(url_for('student.home'))

        flash('Invalid credentials')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            token = PasswordResetToken.generate(user.id)
            reset_link = url_for('auth.reset_password', token=token, _external=True)

            msg = Message('Password Reset - EduTube',
                           sender='noreply@edutube.com',
                           recipients=[email])
            msg.body = f'Click here to reset your password: {reset_link}\nThis link expires in 30 minutes.'
            mail.send(msg)

        flash('If that email exists, a reset link has been sent.')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    rt = PasswordResetToken.query.filter_by(token=token).first()

    if not rt or rt.expires_at < datetime.utcnow():
        flash('Invalid or expired reset link')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        user = User.query.get(rt.user_id)
        user.password_hash = generate_password_hash(new_password)
        db.session.delete(rt)
        db.session.commit()
        flash('Password updated. Please login.')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)