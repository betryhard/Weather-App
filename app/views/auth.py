from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models.user import User
from app import db
from app.utils.messages import msg

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(msg('auth.login.success'), 'success')
            return redirect(url_for('main.index'))
        else:
            flash(msg('auth.login.error'), 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        fullname = request.form['fullname']
        phone = request.form['phone']
        current_address = request.form['current_address']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash(msg('auth.register.password_mismatch'), 'error')
            return render_template('auth/register.html')
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash(msg('auth.register.username_exists'), 'error')
            return render_template('auth/register.html')
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash(msg('auth.register.email_exists'), 'error')
            return render_template('auth/register.html')
        
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
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(msg('auth.logout.message'), 'info')
    return redirect(url_for('main.index')) 