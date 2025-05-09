from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    from .auth import auth_bp
    from .routes import main_bp
    from .favorites import favorites_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(favorites_bp)

    with app.app_context():
        from . import models
        db.create_all()

    return app