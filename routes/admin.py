from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Video, Review, Purchase, TeacherPayout

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied')
            return redirect(url_for('student.home'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.filter_by(role='student').count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_videos = Video.query.count()
    total_revenue = sum(p.amount for p in Purchase.query.all())
    pending_payouts = TeacherPayout.query.filter_by(status='pending').all()
    reviews = Review.query.order_by(Review.created_at.desc()).limit(50).all()

    return render_template('admin_dashboard.html',
                            total_users=total_users,
                            total_teachers=total_teachers,
                            total_videos=total_videos,
                            total_revenue=total_revenue,
                            pending_payouts=pending_payouts,
                            reviews=reviews)


@admin_bp.route('/admin/payout/<int:payout_id>/mark-paid')
@login_required
@admin_required
def mark_paid(payout_id):
    payout = TeacherPayout.query.get_or_404(payout_id)
    payout.status = 'paid'
    db.session.commit()
    flash('Payout marked as paid')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)