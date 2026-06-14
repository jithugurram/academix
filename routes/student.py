from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from models import db, Video, Review, Purchase
from config import Config

student_bp = Blueprint('student', __name__)

@student_bp.route('/')
@login_required
def home():
    syllabus_videos = Video.query.filter_by(category='syllabus').all()
    premium_videos = Video.query.filter_by(category='premium').all()
    return render_template('home.html',
                            syllabus_videos=syllabus_videos,
                            premium_videos=premium_videos,
                            free_minutes_left=max(0, Config.FREE_MINUTES_LIMIT - current_user.free_minutes_used))


@student_bp.route('/watch/<int:video_id>')
@login_required
def watch(video_id):
    video = Video.query.get_or_404(video_id)

    if video.category == 'premium':
        purchased = Purchase.query.filter_by(
            user_id=current_user.id, video_id=video_id, status='completed'
        ).first()

        if not purchased:
            # check free hour quota
            if current_user.free_minutes_used + video.duration_minutes > Config.FREE_MINUTES_LIMIT:
                return render_template('paywall.html', video=video)

    reviews = Review.query.filter_by(video_id=video_id).all()
    return render_template('watch.html', video=video, reviews=reviews)


@student_bp.route('/track-watch/<int:video_id>', methods=['POST'])
@login_required
def track_watch(video_id):
    """Called via JS periodically while video plays to track free-tier usage."""
    video = Video.query.get_or_404(video_id)
    minutes = request.json.get('minutes', 1)

    if video.category != 'premium':
        current_user.free_minutes_used += minutes
        db.session.commit()

    remaining = max(0, Config.FREE_MINUTES_LIMIT - current_user.free_minutes_used)
    return jsonify({'remaining_minutes': remaining})


@student_bp.route('/review/<int:video_id>', methods=['POST'])
@login_required
def add_review(video_id):
    rating = int(request.form['rating'])
    comment = request.form.get('comment', '')

    review = Review(video_id=video_id, user_id=current_user.id,
                     rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    return jsonify({'status': 'success'})