from flask import Blueprint, redirect, url_for, session
from app import oauth, db
from .models import User
from flask_login import login_user
import os


auth_bp = Blueprint('auth', __name__)

google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'}
)

@auth_bp.route('/login')
def login():
    redirect_uri = url_for('auth.callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback')
def callback():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    email = user_info['email']

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect('/')
