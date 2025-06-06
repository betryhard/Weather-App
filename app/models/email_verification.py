from app import db
from datetime import datetime, timedelta
import secrets
import string
import json

class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    google_user_info = db.Column(db.Text)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailVerification {self.email}>'
    
    def get_google_user_info(self):
        if self.google_user_info:
            try:
                return json.loads(self.google_user_info)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_verified(self):
        return self.verified_at is not None
    
    def mark_as_verified(self):
        self.verified_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def generate_token():
        length = 32
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def create_verification(email, google_user_info, expires_minutes=30):
        from app.models.email_setting import EmailSetting
        
        # Get expiry minutes from settings
        expires_minutes = int(EmailSetting.get_setting('VERIFICATION_EXPIRES_MINUTES', expires_minutes))
        
        # Delete any existing verification for this email
        EmailVerification.query.filter_by(email=email, verified_at=None).delete()
        
        # Create new verification
        verification = EmailVerification(
            email=email,
            token=EmailVerification.generate_token(),
            google_user_info=google_user_info if isinstance(google_user_info, str) else json.dumps(google_user_info),
            expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes)
        )
        
        db.session.add(verification)
        db.session.commit()
        
        return verification
    
    @staticmethod
    def find_by_token(token):
        return EmailVerification.query.filter_by(token=token).first()
    
    @staticmethod
    def cleanup_expired():
        expired_tokens = EmailVerification.query.filter(
            EmailVerification.expires_at < datetime.utcnow()
        ).all()
        
        for token in expired_tokens:
            db.session.delete(token)
        
        db.session.commit()
        return len(expired_tokens) 