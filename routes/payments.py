from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
import stripe
from models import db, Video, Purchase, TeacherPayout
from config import Config

stripe.api_key = Config.STRIPE_SECRET_KEY

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/create-checkout-session/<int:video_id>', methods=['POST'])
@login_required
def create_checkout_session(video_id):
    video = Video.query.get_or_404(video_id)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': video.title},
                'unit_amount': int(video.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('payments.success', video_id=video_id, _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('student.watch', video_id=video_id, _external=True),
    )
    return jsonify({'id': session.id})


@payments_bp.route('/payment-success/<int:video_id>')
@login_required
def success(video_id):
    session_id = request.args.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)
    video = Video.query.get_or_404(video_id)

    purchase = Purchase(
        user_id=current_user.id,
        video_id=video_id,
        amount=video.price,
        stripe_payment_id=session.payment_intent,
        status='completed'
    )
    db.session.add(purchase)

    # Track teacher payout (e.g. 70% revenue share)
    teacher_share = video.price * 0.70
    payout = TeacherPayout(teacher_id=video.teacher_id, amount=teacher_share, status='pending')
    db.session.add(payout)

    db.session.commit()
    return redirect(url_for('student.watch', video_id=video_id))