from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils.messages import msg

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html') 