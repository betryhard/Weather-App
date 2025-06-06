import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for, render_template
from app.models.email_setting import EmailSetting
from app.models.email_verification import EmailVerification

class EmailService:
    
    @staticmethod
    def send_verification_email(email, user_info):
        try:
            # Create verification token
            verification = EmailVerification.create_verification(
                email=email,
                google_user_info=json.dumps(user_info)
            )
            
            # Get SMTP configuration
            smtp_config = EmailSetting.get_smtp_config()
            
            # Validate SMTP configuration
            if not all([smtp_config['smtp_server'], smtp_config['smtp_username'], 
                       smtp_config['smtp_password'], smtp_config['sender_email']]):
                current_app.logger.error("SMTP configuration is incomplete")
                return False
            
            # Create verification URL
            verification_url = url_for('auth.verify_google_email', 
                                     token=verification.token, _external=True)
            
            subject = "Account Verification Required - Weather Forecast"
            
            expires_minutes = EmailSetting.get_setting('VERIFICATION_EXPIRES_MINUTES', '30')
            
            html_body = render_template('emails/verify_google_account.html',
                                      user_name=user_info.get('given_name', 'User'),
                                      verification_url=verification_url,
                                      expires_minutes=expires_minutes,
                                      existing_email=email)
            
            text_body = f"""
Hello {user_info.get('given_name', 'User')},

Someone attempted to link a Google account to an email address ({email}) that already exists in our system.

If this was you, please click the link below to verify and link your Google account:
{verification_url}

This link will expire in {expires_minutes} minutes.

If this wasn't you, please ignore this email. Your account remains secure.

Best regards,
Weather Forecast Team
            """
            
            # Send email
            return EmailService._send_email(
                to_email=email,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
                smtp_config=smtp_config
            )
            
        except Exception as e:
            current_app.logger.error(f"Error sending verification email: {str(e)}")
            return False
    
    @staticmethod
    def _send_email(to_email, subject, html_body=None, text_body=None, smtp_config=None):
        try:
            if not smtp_config:
                smtp_config = EmailSetting.get_smtp_config()
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{smtp_config['sender_name']} <{smtp_config['sender_email']}>"
            msg['To'] = to_email
            
            if text_body:
                text_part = MIMEText(text_body, 'plain')
                msg.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
                if smtp_config['smtp_use_tls']:
                    server.starttls()
                
                server.login(smtp_config['smtp_username'], smtp_config['smtp_password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def test_smtp_connection():
 
        try:
            smtp_config = EmailSetting.get_smtp_config()
            
            # Validate configuration
            required_fields = ['smtp_server', 'smtp_username', 'smtp_password', 'sender_email']
            missing_fields = [field for field in required_fields if not smtp_config.get(field)]
            
            if missing_fields:
                return False, f"Missing required fields: {', '.join(missing_fields)}"
            
            # Test connection
            with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
                if smtp_config['smtp_use_tls']:
                    server.starttls()
                server.login(smtp_config['smtp_username'], smtp_config['smtp_password'])
            
            return True, "SMTP connection successful"
            
        except Exception as e:
            return False, f"SMTP connection failed: {str(e)}" 