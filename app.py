from flask import Flask
from flask_login import LoginManager, current_user
from flask_mail import Mail
from config import Config
from models import db, User
from flask_migrate import Migrate
from datetime import datetime

migrate = Migrate()

login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'

    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.teacher import teacher_bp
    from routes.admin import admin_bp
    from routes.payments import payments_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payments_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Make current_user available in all templates
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user, current_year=datetime.utcnow().year)

    with app.app_context():
        db.create_all()
        # create default admin
        if not User.query.filter_by(role='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(name='Admin', email='admin@edutube.com',
                          password_hash=generate_password_hash('admin123'),
                          role='admin')
            db.session.add(admin)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True))
