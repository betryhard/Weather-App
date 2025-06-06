from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
import json
from app.models.user import User, db
from app.models.email_verification import EmailVerification
from app.utils.messages import msg

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            if not user.is_active:
                flash(msg('auth.error.account_locked'), 'error')
            elif user.check_password(password):
                login_user(user)
                flash(msg('auth.success.login'), 'success')
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                elif user.is_admin():
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('main.index'))
            else:
                flash(msg('auth.error.invalid_password'), 'error')
        else:
            flash(msg('auth.error.username_not_found'), 'error')
    
    return render_template('auth/login.html', title='Login')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        current_address = request.form.get('current_address')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if password != confirm_password:
            flash(msg('auth.register.password_mismatch'), 'error')
            return render_template('auth/register.html', title='Register')
        
        if User.query.filter_by(username=username).first():
            flash(msg('auth.register.username_exists'), 'error')
            return render_template('auth/register.html', title='Register')
        
        if User.query.filter_by(email=email).first():
            flash(msg('auth.register.email_exists'), 'error')
            return render_template('auth/register.html', title='Register')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            fullname=fullname,
            phone=phone,
            current_address=current_address
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(msg('auth.register.success'), 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register')

@auth_bp.route('/logout')
@login_required
def logout():
    # Clear chat history when logging out
    session.pop('chat_history', None)
    logout_user()
    flash(msg('auth.logout.message'), 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            # Get form data
            fullname = request.form.get('fullname', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            current_address = request.form.get('current_address', '').strip()
            
            # Validate required fields
            if not all([fullname, email, phone, current_address]):
                flash(msg('auth.profile.all_required'), 'error')
                return render_template('auth/profile.html', title='Profile Management', user=current_user)
            
            # Check if email is already taken by another user
            existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing_user:
                flash(msg('auth.profile.email_exists'), 'error')
                return render_template('auth/profile.html', title='Profile Management', user=current_user)
            
            # Update user information
            current_user.fullname = fullname
            current_user.email = email
            current_user.phone = phone
            current_user.current_address = current_address
            
            db.session.commit()
            flash(msg('auth.profile.update_success'), 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(msg('auth.profile.update_error'), 'error')
    
    return render_template('auth/profile.html', title='Profile Management', user=current_user)

@auth_bp.route('/verify-google-email/<token>')
def verify_google_email(token):
    try:
        verification = EmailVerification.find_by_token(token)
        
        if not verification:
            flash(msg('auth.error.invalid_verification_link'), 'error')
            return redirect(url_for('auth.login'))
        
        if verification.is_expired():
            flash(msg('auth.error.verification_expired'), 'error')
            return redirect(url_for('auth.login'))
        
        if verification.is_verified:
            flash(msg('auth.error.verification_already_used'), 'error')
            return redirect(url_for('auth.login'))
        
        existing_user = User.find_by_email(verification.email)
        if not existing_user:
            flash(msg('auth.error.account_not_found'), 'error')
            return redirect(url_for('auth.login'))
        
        google_user_info = json.loads(verification.google_user_info)
        
        existing_user.google_id = google_user_info['sub']
        existing_user.google_email = google_user_info['email']
        existing_user.profile_picture = google_user_info.get('picture')
        
        verification.mark_as_verified()
        
        db.session.commit()
        
        login_user(existing_user)
        
        flash(msg('auth.success.google_account_linked'), 'success')
        
        if existing_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    except Exception as e:
        flash(msg('auth.error.verification_failed'), 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': msg('auth.password.no_data')}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        # Validate required fields
        if not all([current_password, new_password, confirm_password]):
            return jsonify({'success': False, 'message': msg('auth.password.all_required')}), 400
        
        # Validate new passwords match
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': msg('auth.password.mismatch')}), 400
        
        # Validate password length
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': msg('auth.password.too_short')}), 400
        
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({'success': False, 'message': msg('auth.password.current_incorrect')}), 400
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'success': True, 'message': msg('auth.password.changed_success')})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': msg('auth.password.change_error')}), 500 