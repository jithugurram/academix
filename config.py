import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///academix.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email (for password reset)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # use app password, not real password

    # Stripe
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')

    # Free tier
    FREE_MINUTES_LIMIT = 60

    UPLOAD_FOLDER = 'static/videos'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB