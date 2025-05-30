from flask import Blueprint, render_template
from app.models import User, Favorite, History
from flask_login import current_user

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated or not current_user.is_admin:
        return "Access Denied", 403
    users = User.query.all()
    return render_template('admin.html', users=users)
