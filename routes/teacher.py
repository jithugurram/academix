import os
import subprocess
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Video, Purchase, TeacherPayout

teacher_bp = Blueprint('teacher', __name__)

def teacher_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'teacher':
            flash('Access denied')
            return redirect(url_for('student.home'))
        return f(*args, **kwargs)
    return decorated


@teacher_bp.route('/teacher/dashboard')
@login_required
@teacher_required
def dashboard():
    videos = Video.query.filter_by(teacher_id=current_user.id).all()
    payouts = TeacherPayout.query.filter_by(teacher_id=current_user.id).all()
    total_earnings = sum(p.amount for p in payouts if p.status == 'paid')

    # Calculate average rating per video
    video_data = []
    for v in videos:
        ratings = [r.rating for r in v.reviews]
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None
        video_data.append({
            'video': v,
            'avg_rating': avg_rating,
            'review_count': len(ratings),
            'reviews': v.reviews
        })

    return render_template('teacher_dashboard.html', video_data=video_data,
                            payouts=payouts, total_earnings=total_earnings)

@teacher_bp.route('/teacher/upload', methods=['GET', 'POST'])
@login_required
@teacher_required
def upload():
    if request.method == 'POST':
        file = request.files['video']
        filename = secure_filename(file.filename)
        name_no_ext = os.path.splitext(filename)[0]

        upload_dir = os.path.join(current_app.static_folder, 'videos')
        os.makedirs(upload_dir, exist_ok=True)

        original_path = os.path.join(upload_dir, filename)
        file.save(original_path)

        # Default/original quality
        relative_original = f'videos/{filename}'
        relative_480p = None
        relative_720p = None

        # Transcode to 480p and 720p using ffmpeg (optional - skip if ffmpeg unavailable)
        try:
            path_480 = os.path.join(upload_dir, f'{name_no_ext}_480p.mp4')
            path_720 = os.path.join(upload_dir, f'{name_no_ext}_720p.mp4')

            subprocess.run([
                'ffmpeg', '-i', original_path, '-vf', 'scale=-2:480',
                '-c:v', 'libx264', '-crf', '23', '-preset', 'fast',
                '-c:a', 'aac', path_480, '-y'
            ], check=True, capture_output=True)

            subprocess.run([
                'ffmpeg', '-i', original_path, '-vf', 'scale=-2:720',
                '-c:v', 'libx264', '-crf', '23', '-preset', 'fast',
                '-c:a', 'aac', path_720, '-y'
            ], check=True, capture_output=True)

            relative_480p = f'videos/{name_no_ext}_480p.mp4'
            relative_720p = f'videos/{name_no_ext}_720p.mp4'
        except Exception as e:
            print('ffmpeg transcoding skipped/failed:', e)

        video = Video(
            title=request.form['title'],
            description=request.form['description'],
            filepath=relative_original,
            filepath_480p=relative_480p,
            filepath_720p=relative_720p,
            duration_minutes=int(request.form.get('duration', 0)),
            category=request.form['category'],
            price=float(request.form.get('price', 0)),
            teacher_id=current_user.id
        )
        db.session.add(video)
        db.session.commit()
        flash('Video uploaded successfully')
        return redirect(url_for('teacher.dashboard'))

    return render_template('upload.html')