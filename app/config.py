import os

SECRET_KEY = os.getenv('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = 'sqlite:///weather.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
