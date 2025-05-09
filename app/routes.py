from flask import Blueprint, render_template, request, redirect, url_for
from .weather import get_current_weather, get_forecast
from flask_login import login_required, current_user
from .models import History, db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('weather.html')

@main_bp.route('/weather')
def weather():
    city = request.args.get('city')
    weather = get_current_weather(city)
    forecast = get_forecast(city)
    if current_user.is_authenticated:
        history = History(user_id=current_user.id, city=city, timestamp=datetime.utcnow())
        db.session.add(history)
        db.session.commit()
    return render_template('weather.html', weather=weather, forecast=forecast)