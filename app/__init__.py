from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import json

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '' 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.views.main import main_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.google_auth_controller import google_auth_bp, init_oauth
    from app.controllers.weather_controller import weather_bp
    from app.controllers.chatbot_controller import chatbot_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(google_auth_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    
    # Import message service
    from app.utils.messages import msg
    
    # Add custom template filters
    @app.template_filter('from_json')
    def from_json_filter(json_string):
        try:
            return json.loads(json_string) if json_string else {}
        except:
            return {}
    
    # Register user loader
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        from app.models.email_setting import EmailSetting
        from app.models.email_verification import EmailVerification
        from app.models.system_prompt import SystemPrompt
        
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            admin_user = User(
                username='admin',
                email='admin@example.com',
                fullname='System Administrator',
                phone='+1234567890',
                current_address='System Address',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
        
        # Initialize default email settings
        EmailSetting.initialize_default_settings()
        
        # Initialize default system prompt
        SystemPrompt.create_default_prompt(admin_user.id)
        
    # Initialize Google OAuth
    init_oauth(app)
    
    return app 
