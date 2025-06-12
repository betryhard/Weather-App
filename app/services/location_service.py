import requests
from typing import Dict, List, Optional
from flask import current_app

class LocationService:
    """Service for location search using Nominatim OpenStreetMap API"""
    
    NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
    SEARCH_ENDPOINT = "/search"
    
    @staticmethod
    def search_location(query: str, country_code: str = None, limit: int = 5) -> Dict:
       
        try:
            url = f"{LocationService.NOMINATIM_BASE_URL}{LocationService.SEARCH_ENDPOINT}"
            
            params = {
                'q': query,
                'format': 'json',
                'limit': limit,
                'addressdetails': 1,
                'namedetails': 1
            }
            
            if country_code:
                params['countrycodes'] = country_code
            
            headers = {
                'User-Agent': 'WeatherApp/1.0 (contact@weatherapp.com)'
            }
            
            current_app.logger.info(f"Searching location: {query}")
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return {
                    'success': False,
                    'error': f'No location found: {query}',
                    'locations': []
                }
            
            # Format location data
            locations = []
            for item in data:
                location = {
                    'display_name': item.get('display_name', ''),
                    'name': item.get('name', ''),
                    'lat': float(item.get('lat', 0)),
                    'lon': float(item.get('lon', 0)),
                    'place_id': item.get('place_id', ''),
                    'type': item.get('type', ''),
                    'importance': item.get('importance', 0)
                }
                
                # Extract address components if available
                address = item.get('address', {})
                location['address'] = {
                    'city': address.get('city', address.get('town', address.get('village', ''))),
                    'state': address.get('state', address.get('province', '')),
                    'country': address.get('country', ''),
                    'country_code': address.get('country_code', '').upper()
                }
                
                locations.append(location)
            
            return {
                'success': True,
                'locations': locations,
                'total': len(locations)
            }
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error calling Nominatim API: {str(e)}")
            return {
                'success': False,
                'error': f'Connection error to search service: {str(e)}',
                'locations': []
            }
        except Exception as e:
            current_app.logger.error(f"Error in location search: {str(e)}")
            return {
                'success': False,
                'error': f'Location search error: {str(e)}',
                'locations': []
            }
    
    @staticmethod
    def reverse_geocode(lat: float, lon: float) -> Dict:
        """
        Get address from coordinates using Nominatim API
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dict with success status and address data
        """
        try:
            url = f"{LocationService.NOMINATIM_BASE_URL}/reverse"
            
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'WeatherApp/1.0 (contact@weatherapp.com)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return {
                    'success': False,
                    'error': 'No address found for these coordinates'
                }
            
            address = data.get('address', {})
            
            return {
                'success': True,
                'display_name': data.get('display_name', ''),
                'address': {
                    'city': address.get('city', address.get('town', address.get('village', ''))),
                    'state': address.get('state', address.get('province', '')),
                    'country': address.get('country', ''),
                    'country_code': address.get('country_code', '').upper()
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error in reverse geocoding: {str(e)}")
            return {
                'success': False,
                'error': f'Address lookup error: {str(e)}'
            } 