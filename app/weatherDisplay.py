import requests
from flask import current_app

def get_current_weather(city):
    api_key = current_app.config['OPENWEATHER_API_KEY']
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    return requests.get(url).json()

def get_forecast(city):
    api_key = current_app.config['OPENWEATHER_API_KEY']
    url = f'https://api.openweathermap.org/data/2.5/forecast/daily?q={city}&cnt=7&appid={api_key}&units=metric'
    return requests.get(url).json()