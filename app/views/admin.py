from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models.user import User
from app import db
from app.utils.messages import msg

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash(msg('message.admin_required'), 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get user statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(role='admin').count()
    regular_users = User.query.filter_by(role='user').count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'regular_users': regular_users
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    users = User.query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.fullname = request.form['fullname']
        user.phone = request.form['phone']
        user.current_address = request.form['current_address']
        user.role = request.form['role']
        
        db.session.commit()
        flash(msg('message.user_updated'), 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/toggle_status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # Check if trying to disable the only admin
    if user.role == 'admin' and user.is_active:
        active_admins = User.query.filter_by(role='admin', is_active=True).count()
        if active_admins <= 1:
            flash(msg('message.cannot_disable_admin'), 'error')
            return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    if user.is_active:
        flash(msg('message.user_activated', user.username), 'success')
    else:
        flash(msg('message.user_deactivated', user.username), 'success')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deletion of the current user
    if user.id == current_user.id:
        flash(msg('message.cannot_delete_self'), 'error')
        return redirect(url_for('admin.users'))
    
    # Check if trying to delete the only admin
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash(msg('message.cannot_delete_admin'), 'error')
            return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(msg('message.user_deleted', username), 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/api/users')
@login_required
@admin_required
def api_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]) 