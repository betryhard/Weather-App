from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models.user import User
from flask_login import login_required, current_user

# Create Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html', title='User Management System')

# @main_bp.route('/about')
# def about():
#     """About page route"""
#     return render_template('about.html', title='About Us')

# @main_bp.route('/users')
# def users():
#     """Users list route"""
#     users = User.get_all_users()
#     return render_template('users.html', title='Users', users=users)

# @main_bp.route('/api/users', methods=['GET'])
# def api_users():
#     """API endpoint for users"""
#     users = User.get_all_users()
#     return jsonify([user.to_dict() for user in users])

# @main_bp.route('/dashboard')
# @login_required
# def dashboard():
#     """User dashboard (requires login)"""
#     return render_template('dashboard.html', title='Dashboard', user=current_user) 