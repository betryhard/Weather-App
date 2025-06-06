from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

class User(UserMixin, db.Model):
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fullname = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True) 
    current_address = db.Column(db.Text, nullable=True)  
    role = db.Column(db.String(20), nullable=False, default='user')
    password_hash = db.Column(db.String(128), nullable=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Google OAuth fields
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    google_email = db.Column(db.String(120), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    auth_provider = db.Column(db.String(20), nullable=False, default='local')
    needs_profile_completion = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_google_user(self):
        return self.auth_provider == 'google'
    
    def needs_completion(self):
        return self.needs_profile_completion or not self.phone or not self.current_address
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'fullname': self.fullname,
            'phone': self.phone,
            'current_address': self.current_address,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_admin_user(cls):
        admin = cls.query.filter_by(role='admin').first()
        if not admin:
            admin = cls(
                username='admin',
                email='admin@example.com',
                fullname='System Administrator',
                phone='0000000000',
                current_address='System Address',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            return admin
        return admin
    
    @classmethod
    def create_from_google(cls, google_user_info):
        try:
            if not google_user_info.get('sub') or not google_user_info.get('email'):
                raise ValueError("Missing required Google user info: sub or email")
            
            base_username = google_user_info['email'].split('@')[0]
            
            import re
            base_username = re.sub(r'[^a-zA-Z0-9]', '', base_username)
            
            if not base_username:
                base_username = 'googleuser'
            
            username = base_username
            counter = 1
            
            while cls.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
                if counter > 1000:
                    username = f"googleuser{google_user_info['sub'][-6:]}"
                    break
            
            user = cls(
                username=username,
                email=google_user_info['email'],
                fullname=google_user_info.get('name', ''),
                google_id=google_user_info['sub'],
                google_email=google_user_info['email'],
                profile_picture=google_user_info.get('picture'),
                auth_provider='google',
                needs_profile_completion=True,
                role='user'
            )
            
            db.session.add(user)
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def find_by_google_id(cls, google_id):
        return cls.query.filter_by(google_id=google_id).first()
    
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    def update_from_google(self, google_user_info):
        self.google_email = google_user_info['email']
        self.fullname = google_user_info.get('name', self.fullname)
        self.profile_picture = google_user_info.get('picture', self.profile_picture)
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>' 