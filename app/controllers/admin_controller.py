from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models.user import User, db
from app.models.email_setting import EmailSetting
from app.models.email_verification import EmailVerification
from app.models.system_prompt import SystemPrompt
from app.services.email_service import EmailService
from app.utils.messages import msg

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash(msg('admin.error.access_required'), 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(role='admin').count()
    regular_users = User.query.filter_by(role='user').count()
    
    manageable_users = User.query.filter_by(role='user').count()
    active_regular_users = User.query.filter_by(role='user', is_active=True).count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'regular_users': regular_users,
        'manageable_users': manageable_users,
        'active_regular_users': active_regular_users
    }
    
    return render_template('admin/dashboard.html', title='Admin Dashboard', stats=stats)

@admin_bp.route('/api/users')
@login_required
@admin_required
def api_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit per_page to prevent abuse
    if per_page > 100:
        per_page = 100
    
    # Only get regular users, not admins
    users_pagination = User.query.filter_by(role='user').paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in users_pagination.items],
        'pagination': {
            'page': users_pagination.page,
            'pages': users_pagination.pages,
            'per_page': users_pagination.per_page,
            'total': users_pagination.total,
            'has_next': users_pagination.has_next,
            'has_prev': users_pagination.has_prev,
            'next_num': users_pagination.next_num,
            'prev_num': users_pagination.prev_num
        }
    })

@admin_bp.route('/api/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    try:
        data = request.get_json()
        
        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': msg('system.error.username_exists')}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': msg('system.error.email_exists')}), 400
        
        # Create new user (force role to be 'user')
        user = User(
            username=data['username'],
            email=data['email'],
            fullname=data['fullname'],
            phone=data.get('phone', ''),
            current_address=data.get('current_address', ''),
            role='user',  # Force role to user
            is_active=data.get('is_active', True)
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify(user.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Check for unique constraints
        if 'username' in data and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': msg('system.error.username_exists')}), 400
        
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': msg('system.error.email_exists')}), 400
        
        # Update user fields
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'fullname' in data:
            user.fullname = data['fullname']
        if 'phone' in data:
            user.phone = data['phone']
        if 'current_address' in data:
            user.current_address = data['current_address']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                return jsonify({'error': msg('system.error.delete_only_admin')}), 400
        
        if user.id == current_user.id:
            return jsonify({'error': msg('system.error.delete_self')}), 400
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': msg('admin.success.user_deleted', username)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        if user.role == 'admin' and user.is_active:
            admin_count = User.query.filter_by(role='admin', is_active=True).count()
            if admin_count <= 1:
                return jsonify({'error': msg('system.error.disable_only_admin')}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({
            'message': msg('system.success.user_status_changed', user.username, status),
            'user': user.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/email/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def email_settings():
    if request.method == 'POST':
        try:
            # Get form data
            smtp_server = request.form.get('smtp_server', '').strip()
            smtp_port = request.form.get('smtp_port', '587').strip()
            smtp_username = request.form.get('smtp_username', '').strip()
            smtp_password = request.form.get('smtp_password', '').strip()
            smtp_use_tls = request.form.get('smtp_use_tls') == 'on'
            sender_email = request.form.get('sender_email', '').strip()
            sender_name = request.form.get('sender_name', 'Weather Forecast').strip()
            verification_expires = request.form.get('verification_expires_minutes', '30').strip()
            
            if not all([smtp_server, smtp_port, smtp_username, sender_email]):
                flash(msg('admin.error.fill_required_fields'), 'error')
                return render_template('admin/email_settings.html', title='Email Settings')
            
            # Update settings
            EmailSetting.set_setting('SMTP_SERVER', smtp_server, 'SMTP server hostname')
            EmailSetting.set_setting('SMTP_PORT', smtp_port, 'SMTP server port')
            EmailSetting.set_setting('SMTP_USERNAME', smtp_username, 'SMTP username/email')
            
            # Only update password if provided
            if smtp_password:
                EmailSetting.set_setting('SMTP_PASSWORD', smtp_password, 'SMTP password/app password', True)
            
            EmailSetting.set_setting('SMTP_USE_TLS', 'true' if smtp_use_tls else 'false', 'Use TLS encryption')
            EmailSetting.set_setting('SENDER_EMAIL', sender_email, 'Sender email address')
            EmailSetting.set_setting('SENDER_NAME', sender_name, 'Sender display name')
            EmailSetting.set_setting('VERIFICATION_EXPIRES_MINUTES', verification_expires, 'Email verification expiry time')
            
            flash(msg('admin.success.email_settings_updated'), 'success')
            
        except Exception as e:
            flash(msg('admin.error.update_email_settings', str(e)), 'error')
    
    # Get current settings
    settings = {
        'smtp_server': EmailSetting.get_setting('SMTP_SERVER', ''),
        'smtp_port': EmailSetting.get_setting('SMTP_PORT', '587'),
        'smtp_username': EmailSetting.get_setting('SMTP_USERNAME', ''),
        'smtp_password': EmailSetting.get_setting('SMTP_PASSWORD', ''),
        'smtp_use_tls': EmailSetting.get_setting('SMTP_USE_TLS', 'true').lower() == 'true',
        'sender_email': EmailSetting.get_setting('SENDER_EMAIL', ''),
        'sender_name': EmailSetting.get_setting('SENDER_NAME', 'Weather Forecast'),
        'verification_expires_minutes': EmailSetting.get_setting('VERIFICATION_EXPIRES_MINUTES', '30')
    }
    
    return render_template('admin/email_settings.html', title='Email Settings', settings=settings)

@admin_bp.route('/email/test-connection', methods=['POST'])
@login_required
@admin_required
def test_email_connection():
    try:
        success, message = EmailService.test_smtp_connection()
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': msg('admin.error.connection_test_failed', str(e))})

@admin_bp.route('/email/send-test-email', methods=['POST'])
@login_required
@admin_required
def send_test_email():
    try:
        test_email = request.json.get('email')
        if not test_email:
            return jsonify({'success': False, 'message': msg('admin.error.email_required')})
        
        subject = "Test Email - Weather Forecast"
        html_body = """
        <h2>Test Email</h2>
        <p>This is a test email from Weather Forecast application.</p>
        <p>If you received this email, your SMTP configuration is working correctly!</p>
        <p>Best regards,<br>Weather Forecast Team</p>
        """
        text_body = """
Test Email

This is a test email from Weather Forecast application.
If you received this email, your SMTP configuration is working correctly!

Best regards,
Weather Forecast Team
        """
        
        success = EmailService._send_email(
            to_email=test_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        
        if success:
            return jsonify({'success': True, 'message': msg('admin.success.test_email_sent', test_email)})
        else:
            return jsonify({'success': False, 'message': msg('admin.error.send_test_email')})
    
    except Exception as e:
        return jsonify({'success': False, 'message': msg('admin.error.send_test_email_exception', str(e))})

@admin_bp.route('/email/verifications')
@login_required
@admin_required
def verification_logs():
    verifications = EmailVerification.query.order_by(EmailVerification.created_at.desc()).limit(50).all()
    
    cleaned_count = EmailVerification.cleanup_expired()
    if cleaned_count > 0:
        flash(msg('admin.info.cleanup_expired', cleaned_count), 'info')
    
    return render_template('admin/email_verifications.html', 
                         title='Email Verifications', 
                         verifications=verifications)

@admin_bp.route('/email/get-settings', methods=['GET'])
@login_required
@admin_required
def get_email_settings():
    try:
        settings = {
            'smtp_server': EmailSetting.get_setting('SMTP_SERVER', ''),
            'smtp_port': EmailSetting.get_setting('SMTP_PORT', '587'),
            'smtp_username': EmailSetting.get_setting('SMTP_USERNAME', ''),
            'smtp_password': EmailSetting.get_setting('SMTP_PASSWORD', ''),
            'smtp_use_tls': EmailSetting.get_setting('SMTP_USE_TLS', 'true').lower() == 'true',
            'sender_email': EmailSetting.get_setting('SENDER_EMAIL', ''),
            'sender_name': EmailSetting.get_setting('SENDER_NAME', 'Weather Forecast'),
            'verification_expires_minutes': EmailSetting.get_setting('VERIFICATION_EXPIRES_MINUTES', '30')
        }
        
        return jsonify({'success': True, 'settings': settings})
    
    except Exception as e:
        return jsonify({'success': False, 'message': msg('admin.error.get_settings', str(e))})

@admin_bp.route('/email/api/verifications', methods=['GET'])
@login_required
@admin_required
def api_verification_logs():
    try:
        verifications = EmailVerification.query.order_by(EmailVerification.created_at.desc()).limit(100).all()
        
        cleaned_count = EmailVerification.cleanup_expired()
        
        verification_data = []
        for v in verifications:
            google_info = v.get_google_user_info()
            verification_data.append({
                'id': v.id,
                'email': v.email,
                'token': v.token[:8] + '...' if v.token else 'N/A', 
                'google_name': google_info.get('name', 'N/A') if google_info else 'N/A',
                'google_picture': google_info.get('picture', '') if google_info else '',
                'created_at': v.created_at.strftime('%Y-%m-%d %H:%M:%S') if v.created_at else 'N/A',
                'expires_at': v.expires_at.strftime('%Y-%m-%d %H:%M:%S') if v.expires_at else 'N/A',
                'verified_at': v.verified_at.strftime('%Y-%m-%d %H:%M:%S') if v.verified_at else None,
                'is_expired': v.is_expired(),
                'status': 'Verified' if v.verified_at else ('Expired' if v.is_expired() else 'Pending')
            })
        
        return jsonify({
            'success': True, 
            'verifications': verification_data,
            'cleaned_count': cleaned_count,
            'total_count': len(verification_data)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': msg('admin.error.get_verification_logs', str(e))})

@admin_bp.route('/system-prompts')
@login_required
@admin_required
def system_prompts():
    return render_template('admin/system_prompts.html', title='System Prompt Management')

@admin_bp.route('/api/system-prompts')
@login_required
@admin_required
def api_system_prompts():
    """API endpoint for system prompts with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit per_page to prevent abuse
    if per_page > 100:
        per_page = 100
    
    prompts_pagination = SystemPrompt.query.order_by(SystemPrompt.created_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'prompts': [prompt.to_dict() for prompt in prompts_pagination.items],
        'pagination': {
            'page': prompts_pagination.page,
            'pages': prompts_pagination.pages,
            'per_page': prompts_pagination.per_page,
            'total': prompts_pagination.total,
            'has_next': prompts_pagination.has_next,
            'has_prev': prompts_pagination.has_prev,
            'next_num': prompts_pagination.next_num,
            'prev_num': prompts_pagination.prev_num
        }
    })

@admin_bp.route('/api/system-prompts', methods=['POST'])
@login_required
@admin_required
def create_system_prompt():
    try:
        data = request.get_json()
        
        if SystemPrompt.query.filter_by(name=data['name']).first():
            return jsonify({'error': msg('system.error.prompt_name_exists')}), 400
        
        prompt = SystemPrompt(
            name=data['name'],
            description=data.get('description', ''),
            prompt_content=data['prompt_content'],
            created_by=current_user.id
        )
        
        db.session.add(prompt)
        db.session.commit()
        
        return jsonify(prompt.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/api/system-prompts/<int:prompt_id>', methods=['PUT'])
@login_required
@admin_required
def update_system_prompt(prompt_id):
    try:
        prompt = SystemPrompt.query.get_or_404(prompt_id)
        data = request.get_json()
        
        if 'name' in data and data['name'] != prompt.name:
            if SystemPrompt.query.filter_by(name=data['name']).first():
                return jsonify({'error': msg('system.error.prompt_name_exists')}), 400
        
        # Update prompt fields
        if 'name' in data:
            prompt.name = data['name']
        if 'description' in data:
            prompt.description = data['description']
        if 'prompt_content' in data:
            prompt.prompt_content = data['prompt_content']
        
        db.session.commit()
        
        if prompt.is_active:
            try:
                from app.controllers.chatbot_controller import reload_chatbot_system_prompt
                reload_chatbot_system_prompt()
            except Exception as e:
                print(f"Error reloading system prompt in chatbot: {e}")
        
        return jsonify(prompt.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/api/system-prompts/<int:prompt_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_system_prompt(prompt_id):
    """Delete system prompt"""
    try:
        prompt = SystemPrompt.query.get_or_404(prompt_id)
        
        if SystemPrompt.query.count() <= 1:
            return jsonify({'error': msg('system.error.delete_only_prompt')}), 400
        
        if prompt.is_active:
            other_prompt = SystemPrompt.query.filter(SystemPrompt.id != prompt_id).first()
            if other_prompt:
                other_prompt.is_active = True
        
        name = prompt.name
        db.session.delete(prompt)
        db.session.commit()
        
        return jsonify({'message': msg('admin.success.system_prompt_deleted', name)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/api/system-prompts/<int:prompt_id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_system_prompt(prompt_id):
    """Activate a system prompt"""
    try:
        prompt = SystemPrompt.query.get_or_404(prompt_id)
        
        prompt.activate()
        
        try:
            from app.controllers.chatbot_controller import reload_chatbot_system_prompt
            reload_chatbot_system_prompt()
        except Exception as e:
            print(f"Error reloading system prompt in chatbot: {e}")
        
        return jsonify({
            'message': msg('admin.success.system_prompt_activated', prompt.name),
            'prompt': prompt.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/api/system-prompts/default', methods=['POST'])
@login_required
@admin_required
def create_default_prompt():
    """Create default system prompt if none exists"""
    try:
        if SystemPrompt.query.first():
            return jsonify({'error': msg('system.error.prompts_exist')}), 400
        
        default_prompt = SystemPrompt.create_default_prompt(current_user.id)
        if default_prompt:
            return jsonify({
                'message': msg('system.success.default_prompt_created'),
                'prompt': default_prompt.to_dict()
            }), 201
        else:
            return jsonify({'error': msg('system.error.create_default_failed')}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400 