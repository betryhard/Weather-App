from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from ..models import db, Favorite, History
import re
import sqlite3
from app.utils.forecast import get_forecast_data

bp = Blueprint('user', __name__, url_prefix='/user')
def get_user_by_email(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)
        if user and user[2] == password:  # [2] là password trong DB
            session['user'] = user[1]     # [1] là email
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if get_user_by_email(email):
            return render_template('register.html', error='Email already registered')
        # Kiểm tra mật khẩu
        if not re.match(r'(?=.*[A-Z])(?=.*[\W_]).{6,}', password):
            return render_template('register.html', error='Password must be strong')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/register_page')
def register_page():
    return render_template('register.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')
@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@bp.route('/favorites/delete/<int:id>')
@login_required
def delete_favorite(id):
    Favorite.query.filter_by(id=id, user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for('user.settings'))

@bp.route('/history/delete/<int:id>')
@login_required
def delete_history(id):
    History.query.filter_by(id=id, user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for('user.settings'))

#  Thêm API trả về dữ liệu thời tiết (dùng cho fetch trong JavaScript)
@bp.route('/api/forecast')
@login_required
def api_forecast():
    location = request.args.get('location', default='Hanoi')
    forecast = get_forecast_data(location)
    return jsonify(forecast)
