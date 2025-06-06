from flask import Blueprint, jsonify, request, current_app
import requests
from app.services.weather_service import WeatherService
from app.utils.constants import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, OPENWEATHER_GEOCODING_URL, OPENWEATHER_GEOCODING_REVERSE_ENDPOINT
from app.utils.messages import msg

weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')

@weather_bp.route('/current', methods=['GET'])
def get_current_weather():
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        if lat is None or lon is None:
            lat = DEFAULT_LATITUDE
            lon = DEFAULT_LONGITUDE
            current_app.logger.info(f"Using default coordinates: lat={lat}, lon={lon}")
        
        weather_data = WeatherService.get_current_and_forecast(lat, lon)
        
        if weather_data is None:
            return jsonify({
                'success': False,
                'message': msg('weather.error.fetch_failed')
            }), 500
        
        return jsonify({
            'success': True,
            'data': weather_data,
            'coordinates': {
                'latitude': lat,
                'longitude': lon
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in get_current_weather: {str(e)}")
        return jsonify({
            'success': False,
            'message': msg('weather.error.internal_server')
        }), 500

@weather_bp.route('/hourly', methods=['GET'])
def get_hourly_forecast():
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        hours = request.args.get('hours', 24, type=int)
        
        if lat is None or lon is None:
            lat = DEFAULT_LATITUDE
            lon = DEFAULT_LONGITUDE
            current_app.logger.info(f"Using default coordinates for hourly: lat={lat}, lon={lon}")
        
        if hours > 48:
            hours = 48
        elif hours < 1:
            hours = 24
        
        hourly_data = WeatherService.get_hourly_forecast(lat, lon, hours)
        
        if hourly_data is None:
            return jsonify({
                'success': False,
                'message': msg('weather.error.fetch_failed')
            }), 500
        
        return jsonify({
            'success': True,
            'data': hourly_data,
            'coordinates': {
                'latitude': lat,
                'longitude': lon
            },
            'hours_requested': hours
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in get_hourly_forecast: {str(e)}")
        return jsonify({
            'success': False,
            'message': msg('weather.error.internal_server')
        }), 500

@weather_bp.route('/location/reverse')
def reverse_geocode_location():
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        if lat is None or lon is None:
            return jsonify({
                'success': False,
                'message': msg('weather.error.coordinates_required')
            }), 400
        
        # Call OpenWeatherMap Geocoding API
        api_key = current_app.config['OPENWEATHERMAP_API_KEY']
        url = f"{OPENWEATHER_GEOCODING_URL}{OPENWEATHER_GEOCODING_REVERSE_ENDPOINT}"
        params = {
            'lat': lat,
            'lon': lon,
            'limit': 1,
            'appid': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                location = data[0]
                location_name = f"{location['name']}, {location['country']}"
                
                return jsonify({
                    'success': True,
                    'data': {
                        'name': location_name,
                        'city': location['name'],
                        'country': location['country'],
                        'state': location.get('state', ''),
                        'coordinates': f"{lat:.4f}, {lon:.4f}"
                    }
                })
            else:
                return jsonify({
                    'success': True,
                    'data': {
                        'name': f"{lat:.4f}, {lon:.4f}",
                        'coordinates': f"{lat:.4f}, {lon:.4f}"
                    }
                })
        else:
            return jsonify({
                'success': False,
                'message': msg('weather.error.location_failed')
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in reverse geocoding: {str(e)}")
        return jsonify({
            'success': False,
            'message': msg('weather.error.internal_server')
        }), 500 