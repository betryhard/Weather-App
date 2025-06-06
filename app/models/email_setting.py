from app import db
from datetime import datetime

class EmailSetting(db.Model):
    __tablename__ = 'email_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    setting_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(500))
    is_encrypted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailSetting {self.setting_key}>'
    
    @staticmethod
    def get_setting(key, default=None):
        setting = EmailSetting.query.filter_by(setting_key=key).first()
        return setting.setting_value if setting else default
    
    @staticmethod
    def set_setting(key, value, description=None, is_encrypted=False):
        setting = EmailSetting.query.filter_by(setting_key=key).first()
        
        if setting:
            setting.setting_value = value
            setting.description = description or setting.description
            setting.is_encrypted = is_encrypted
            setting.updated_at = datetime.utcnow()
        else:
            setting = EmailSetting(
                setting_key=key,
                setting_value=value,
                description=description,
                is_encrypted=is_encrypted
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting
    
    @staticmethod
    def get_smtp_config():
        return {
            'smtp_server': EmailSetting.get_setting('SMTP_SERVER'),
            'smtp_port': int(EmailSetting.get_setting('SMTP_PORT', '587')),
            'smtp_username': EmailSetting.get_setting('SMTP_USERNAME'),
            'smtp_password': EmailSetting.get_setting('SMTP_PASSWORD'),
            'smtp_use_tls': EmailSetting.get_setting('SMTP_USE_TLS', 'true').lower() == 'true',
            'sender_email': EmailSetting.get_setting('SENDER_EMAIL'),
            'sender_name': EmailSetting.get_setting('SENDER_NAME', 'Weather Forecast')
        }
    
    @staticmethod
    def initialize_default_settings():
        defaults = [
            ('SMTP_SERVER', 'smtp.gmail.com', 'SMTP server hostname'),
            ('SMTP_PORT', '587', 'SMTP server port'),
            ('SMTP_USERNAME', '', 'SMTP username/email'),
            ('SMTP_PASSWORD', '', 'SMTP password/app password', True),
            ('SMTP_USE_TLS', 'true', 'Use TLS encryption'),
            ('SENDER_EMAIL', '', 'Sender email address'),
            ('SENDER_NAME', 'Weather Forecast', 'Sender display name'),
            ('VERIFICATION_EXPIRES_MINUTES', '30', 'Email verification link expiry time in minutes'),
        ]
        
        for key, value, desc, *encrypted in defaults:
            is_encrypted = encrypted[0] if encrypted else False
            existing = EmailSetting.query.filter_by(setting_key=key).first()
            if not existing:
                EmailSetting.set_setting(key, value, desc, is_encrypted) 