from flask import Blueprint
from .main import main_bp
from .study import study_bp
from .email import email_bp
from .auth import auth_bp


def init_app(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(main_bp)
    app.register_blueprint(study_bp, url_prefix='/study')
    app.register_blueprint(email_bp, url_prefix='/email')
    app.register_blueprint(auth_bp, url_prefix='/auth')
