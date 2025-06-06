from flask import Blueprint, redirect, url_for, session, request, flash, current_app, render_template
from flask_login import login_user, current_user
from authlib.integrations.flask_client import OAuth
import json
import requests
import traceback
from app.models.user import User, db
from app.models.email_verification import EmailVerification
from app.services.email_service import EmailService
from app.utils.messages import msg

google_auth_bp = Blueprint('google_auth', __name__, url_prefix='/auth/google')

oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    return google

@google_auth_bp.route('/login')
def google_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    google = oauth.google
    redirect_uri = url_for('google_auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@google_auth_bp.route('/callback')
def google_callback():
    try:
        google = oauth.google
        token = google.authorize_access_token()
        
        if not token:
            current_app.logger.error("Google OAuth: No token received")
            flash(msg('auth.google.error.token'), 'error')
            return redirect(url_for('auth.login'))
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            resp = google.parse_id_token(token)
            user_info = resp
        
        if not user_info:
            current_app.logger.error("Google OAuth: No user info received")
            flash(msg('auth.google.error.userinfo'), 'error')
            return redirect(url_for('auth.login'))
        
        current_app.logger.info(f"Google OAuth: User info received for {user_info.get('email')}")
        
        # Check if user exists by Google ID
        user = User.find_by_google_id(user_info['sub'])
        
        if user:
            # Existing Google user - update info and login
            current_app.logger.info(f"Google OAuth: Existing user found - {user.email}")
            user.update_from_google(user_info)
            login_user(user)
            flash(msg('auth.login.success'), 'success')
            
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            # Check if user exists by email (potential account conflict)
            existing_user = User.find_by_email(user_info['email'])
            
            if existing_user:
                current_app.logger.info(f"Google OAuth: Email conflict detected - {user_info['email']}")
                
                # Send verification email for security
                if EmailService.send_verification_email(user_info['email'], user_info):
                    flash(msg('auth.google.verification_email_sent', user_info["email"]), 'info')
                else:
                    flash(msg('auth.google.verification_failed'), 'error')
                
                return redirect(url_for('auth.login'))
            else:
                # New user - create account
                current_app.logger.info(f"Google OAuth: Creating new user - {user_info['email']}")
                try:
                    new_user = User.create_from_google(user_info)
                    current_app.logger.info(f"Google OAuth: New user created successfully - {new_user.id}")
                    login_user(new_user)
                    flash(msg('auth.google.account_created'), 'success')
                    
                    # Redirect to profile completion
                    return redirect(url_for('google_auth.complete_profile'))
                except Exception as create_error:
                    current_app.logger.error(f"Google OAuth: Error creating user - {str(create_error)}")
                    current_app.logger.error(f"Google OAuth: Traceback - {traceback.format_exc()}")
                    flash(msg('auth.google.create_account_error'), 'error')
                    return redirect(url_for('auth.login'))
    
    except Exception as e:
        current_app.logger.error(f"Google OAuth error: {str(e)}")
        current_app.logger.error(f"Google OAuth traceback: {traceback.format_exc()}")
        flash(msg('auth.google.error.general'), 'error')
        return redirect(url_for('auth.login'))

@google_auth_bp.route('/verify/<token>')
def verify_google_email(token):
    try:
        # Find verification record
        verification = EmailVerification.find_by_token(token)
        
        if not verification:
            flash(msg('auth.error.invalid_verification_link'), 'error')
            return redirect(url_for('auth.login'))
        
        if verification.is_expired:
            flash(msg('auth.error.verification_expired'), 'error')
            return redirect(url_for('auth.login'))
        
        if verification.is_verified:
            flash(msg('auth.error.verification_already_used'), 'error')
            return redirect(url_for('auth.login'))
        
        # Get existing user and Google user info
        existing_user = User.find_by_email(verification.email)
        if not existing_user:
            flash(msg('auth.error.account_not_found'), 'error')
            return redirect(url_for('auth.login'))
        
        # Parse Google user info
        google_user_info = json.loads(verification.google_user_info)
        
        # Link Google account to existing user
        existing_user.google_id = google_user_info['sub']
        existing_user.google_email = google_user_info['email']
        existing_user.profile_picture = google_user_info.get('picture')
        
        # Mark verification as completed
        verification.mark_as_verified()
        
        # Commit changes
        db.session.commit()
        
        # Log in the user
        login_user(existing_user)
        
        flash(msg('auth.success.google_account_linked'), 'success')
        current_app.logger.info(f"Google account linked successfully for user: {existing_user.email}")
        
        if existing_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    except Exception as e:
        current_app.logger.error(f"Email verification error: {str(e)}")
        flash(msg('auth.error.verification_failed'), 'error')
        return redirect(url_for('auth.login'))

@google_auth_bp.route('/complete-profile', methods=['GET', 'POST'])
def complete_profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if not current_user.is_google_user() or not current_user.needs_completion():
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        current_address = request.form.get('current_address', '').strip()
        
        if not phone or not current_address:
            flash(msg('auth.google.complete.required'), 'error')
            return render_template('auth/complete_profile.html', title='Complete Profile')
        
        # Update user profile
        current_user.phone = phone
        current_user.current_address = current_address
        current_user.needs_profile_completion = False
        db.session.commit()
        
        flash(msg('auth.google.complete.success'), 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/complete_profile.html', title='Complete Profile') 