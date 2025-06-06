import requests
import os
from typing import Dict, Optional
from flask import current_app
from app.utils.constants import *
from app.utils.messages import msg

class WeatherService:
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        self.base_url = OPENWEATHER_BASE_URL_V2_5
    
    def get_current_weather(self, location: str) -> Dict:
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': msg('weather.service.error.api_key_missing')
                }
            
            url = f"{self.base_url}{OPENWEATHER_WEATHER_ENDPOINT}"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'vi'
            }
            
            print(f"Calling weather API for location: {location}")
            print(f"API Key present: {bool(self.api_key)}")
            
            response = requests.get(url, params=params, timeout=10)
            
            print(f"Weather API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Weather data received: {data.get('name', 'Unknown')}")
                
                return {
                    'success': True,
                    'location': f"{data['name']}, {data['sys']['country']}",
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'],
                    'wind_speed': data['wind']['speed'],
                    'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                    'icon': data['weather'][0]['icon']
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': msg('weather.service.error.api_key_invalid')
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': msg('weather.service.error.location_not_found', location)
                }
            else:
                print(f"Weather API error response: {response.text}")
                return {
                    'success': False,
                    'error': msg('weather.service.error.api_error', response.status_code)
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': msg('weather.service.error.timeout')
            }
        except requests.exceptions.RequestException as e:
            print(f"Weather API request error: {str(e)}")
            return {
                'success': False,
                'error': msg('weather.service.error.connection')
            }
        except Exception as e:
            print(f"Weather service error: {str(e)}")
            return {
                'success': False,
                'error': msg('weather.service.error.general', str(e))
            }
    
    def get_forecast(self, location: str, days: int = 5) -> Dict:
        """Get weather forecast for the next few days"""
        try:
            # Check API key
            if not self.api_key:
                return {
                    'success': False,
                    'error': msg('weather.service.error.api_key_missing')
                }
            
            url = f"{self.base_url}{OPENWEATHER_FORECAST_ENDPOINT}"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'vi'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                
                # Group by day and take the first forecast of each day
                seen_dates = set()
                for item in data['list'][:days * 8]:  
                    date = item['dt_txt'].split(' ')[0]
                    if date not in seen_dates:
                        seen_dates.add(date)
                        forecasts.append({
                            'date': item['dt_txt'],
                            'temperature': item['main']['temp'],
                            'description': item['weather'][0]['description'],
                            'icon': item['weather'][0]['icon'],
                            'humidity': item['main']['humidity'],
                            'wind_speed': item['wind']['speed']
                        })
                        
                        if len(forecasts) >= days:
                            break
                
                return {
                    'success': True,
                    'location': f"{data['city']['name']}, {data['city']['country']}",
                    'forecasts': forecasts
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': msg('weather.service.error.api_key_invalid')
                }
            else:
                return {
                    'success': False,
                    'error': msg('weather.service.error.forecast_failed', response.status_code)
                }
                
        except Exception as e:
            print(f"Weather forecast error: {str(e)}")
            return {
                'success': False,
                'error': msg('weather.service.error.forecast_general', str(e))
            }
    
    @staticmethod
    def get_api_key():
        return current_app.config.get('OPENWEATHERMAP_API_KEY')
    
    @staticmethod
    def get_current_and_forecast(lat, lon, exclude=None, units=DEFAULT_WEATHER_UNITS, lang=DEFAULT_WEATHER_LANG):
        
        try:
            api_key = WeatherService.get_api_key()
            if not api_key:
                current_app.logger.error("OpenWeatherMap API key not found in configuration")
                return None
            
            if exclude is None:
                exclude = [WEATHER_EXCLUDE_MINUTELY, WEATHER_EXCLUDE_HOURLY, WEATHER_EXCLUDE_ALERTS]
            
            url = f"{OPENWEATHER_BASE_URL}{OPENWEATHER_CURRENT_ENDPOINT}"
            
            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': units,
                'lang': lang,
                'exclude': ','.join(exclude) if exclude else ''
            }
            
            current_app.logger.info(f"Calling OpenWeatherMap API for lat={lat}, lon={lon}")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            formatted_data = WeatherService._format_weather_data(data)
            
            return formatted_data
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error calling OpenWeatherMap API: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error processing weather data: {str(e)}")
            return None
    
    @staticmethod
    def get_hourly_forecast(lat, lon, hours=24, units=DEFAULT_WEATHER_UNITS, lang=DEFAULT_WEATHER_LANG):
        try:
            api_key = WeatherService.get_api_key()
            if not api_key:
                current_app.logger.error("OpenWeatherMap API key not found in configuration")
                return None
            
            exclude = [WEATHER_EXCLUDE_MINUTELY, WEATHER_EXCLUDE_ALERTS]
            
            url = f"{OPENWEATHER_BASE_URL}{OPENWEATHER_CURRENT_ENDPOINT}"
            
            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': units,
                'lang': lang,
                'exclude': ','.join(exclude)
            }
            
            current_app.logger.info(f"Calling OpenWeatherMap API for hourly forecast: lat={lat}, lon={lon}, hours={hours}")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            formatted_data = WeatherService._format_hourly_data(data, hours)
            
            return formatted_data
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error calling OpenWeatherMap API for hourly data: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error processing hourly weather data: {str(e)}")
            return None

    @staticmethod
    def _format_weather_data(raw_data):
        try:
            formatted = {
                'current': {
                    'datetime': raw_data['current']['dt'],
                    'temperature': round(raw_data['current']['temp']),
                    'feels_like': round(raw_data['current']['feels_like']),
                    'humidity': raw_data['current']['humidity'],
                    'pressure': raw_data['current']['pressure'],
                    'wind_speed': raw_data['current']['wind_speed'],
                    'wind_deg': raw_data['current'].get('wind_deg', 0),
                    'visibility': raw_data['current'].get('visibility', 0),
                    'weather': {
                        'main': raw_data['current']['weather'][0]['main'],
                        'description': raw_data['current']['weather'][0]['description'].title(),
                        'icon': raw_data['current']['weather'][0]['icon'],
                        'icon_url': OPENWEATHER_ICON_URL.format(icon=raw_data['current']['weather'][0]['icon'])
                    }
                },
                'daily': []
            }
            
            for day in raw_data.get('daily', []):
                daily_data = {
                    'datetime': day['dt'],
                    'temp_min': round(day['temp']['min']),
                    'temp_max': round(day['temp']['max']),
                    'humidity': day['humidity'],
                    'wind_speed': day['wind_speed'],
                    'weather': {
                        'main': day['weather'][0]['main'],
                        'description': day['weather'][0]['description'].title(),
                        'icon': day['weather'][0]['icon'],
                        'icon_url': OPENWEATHER_ICON_URL.format(icon=day['weather'][0]['icon'])
                    }
                }
                formatted['daily'].append(daily_data)
            
            return formatted
            
        except KeyError as e:
            current_app.logger.error(f"Missing expected field in weather data: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error formatting weather data: {str(e)}")
            return None
    
    @staticmethod
    def _format_hourly_data(raw_data, hours_limit):
        try:
            formatted = {
                'current': {
                    'datetime': raw_data['current']['dt'],
                    'temperature': round(raw_data['current']['temp']),
                    'feels_like': round(raw_data['current']['feels_like']),
                    'humidity': raw_data['current']['humidity'],
                    'pressure': raw_data['current']['pressure'],
                    'wind_speed': raw_data['current']['wind_speed'],
                    'wind_deg': raw_data['current'].get('wind_deg', 0),
                    'visibility': raw_data['current'].get('visibility', 0),
                    'weather': {
                        'main': raw_data['current']['weather'][0]['main'],
                        'description': raw_data['current']['weather'][0]['description'].title(),
                        'icon': raw_data['current']['weather'][0]['icon'],
                        'icon_url': OPENWEATHER_ICON_URL.format(icon=raw_data['current']['weather'][0]['icon'])
                    }
                },
                'hourly': []
            }
            
            hourly_data = raw_data.get('hourly', [])[:hours_limit]
            
            for hour in hourly_data:
                hourly_item = {
                    'datetime': hour['dt'],
                    'temperature': round(hour['temp']),
                    'feels_like': round(hour['feels_like']),
                    'humidity': hour['humidity'],
                    'pressure': hour['pressure'],
                    'wind_speed': hour['wind_speed'],
                    'wind_deg': hour.get('wind_deg', 0),
                    'visibility': hour.get('visibility', 0),
                    'pop': hour.get('pop', 0),
                    'weather': {
                        'main': hour['weather'][0]['main'],
                        'description': hour['weather'][0]['description'].title(),
                        'icon': hour['weather'][0]['icon'],
                        'icon_url': OPENWEATHER_ICON_URL.format(icon=hour['weather'][0]['icon'])
                    }
                }
                formatted['hourly'].append(hourly_item)
            
            return formatted
            
        except KeyError as e:
            current_app.logger.error(f"Missing expected field in hourly weather data: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error formatting hourly weather data: {str(e)}")
            return None
    
    @staticmethod
    def get_location_by_city(city_name, limit=1):
    
        try:
            api_key = WeatherService.get_api_key()
            if not api_key:
                current_app.logger.error("OpenWeatherMap API key not found in configuration")
                return None
            
            url = f"{OPENWEATHER_GEOCODING_URL}{OPENWEATHER_GEOCODING_DIRECT_ENDPOINT}"
            
            params = {
                'q': city_name,
                'limit': limit,
                'appid': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error calling Geocoding API: {str(e)}")
            return None 

    def get_hourly_forecast_by_location(self, location: str, hours: int = 24) -> Dict:
        """Get hourly weather forecast by location name"""
        try:
            # Get coordinates for the location
            locations = self.get_location_by_city(location, limit=1)
            
            if not locations:
                return {
                    'success': False,
                    'error': f'Location "{location}" not found'
                }
            
            location_data = locations[0]
            lat = location_data['lat']
            lon = location_data['lon']
            
            # Get hourly forecast using coordinates
            forecast_data = self.get_hourly_forecast(lat, lon, hours)
            
            if forecast_data:
                return {
                    'success': True,
                    'location': f"{location_data.get('name', location)}, {location_data.get('country', '')}",
                    'data': forecast_data
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to get hourly forecast data'
                }
            
        except Exception as e:
            print(f"Error getting hourly forecast for {location}: {str(e)}")
            return {
                'success': False,
                'error': f'Error getting hourly forecast: {str(e)}'
            } 