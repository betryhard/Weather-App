from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models.favorite_location import FavoriteLocation
from app.utils.messages import msg

favorites_bp = Blueprint('favorites', __name__, url_prefix='/api/favorites')


@favorites_bp.route('', methods=['GET'])
@login_required
def get_user_favorites():
    """Get all favorite locations for current user"""
    try:
        favorites = FavoriteLocation.get_user_favorites(current_user.id)
        favorites_data = [fav.to_dict() for fav in favorites]
        
        return jsonify({
            'success': True,
            'data': favorites_data,
            'total': len(favorites_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user favorites: {str(e)}")
        return jsonify({
            'success': False,
            'message': msg('favorites.error.fetch_failed')
        }), 500


@favorites_bp.route('', methods=['POST'])
@login_required
def add_favorite():
    """Add a location to user's favorites"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': msg('favorites.error.invalid_data')
            }), 400
        
        # Validate required fields
        required_fields = ['location_name', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        try:
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': msg('favorites.error.invalid_coordinates')
            }), 400
        
        # Check if already favorited
        if FavoriteLocation.is_favorite(current_user.id, latitude, longitude):
            return jsonify({
                'success': False,
                'message': msg('favorites.error.already_exists')
            }), 409
        
        # Add to favorites
        favorite = FavoriteLocation.add_favorite(
            user_id=current_user.id,
            location_name=data['location_name'],
            latitude=latitude,
            longitude=longitude,
            country=data.get('country'),
            state=data.get('state')
        )
        
        if favorite:
            return jsonify({
                'success': True,
                'message': msg('favorites.success.added'),
                'data': favorite.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': msg('favorites.error.already_exists')
            }), 409
            
    except Exception as e:
        current_app.logger.error(f"Error adding favorite: {str(e)}")
        return jsonify({
            'success': False,
            'message': msg('favorites.error.add_failed')
        }), 500


@favorites_bp.route('', methods=['DELETE'])
@login_required
def remove_favorite():
    """Remove a location from user's favorites"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': msg('favorites.error.invalid_data')
            }), 400
        
        # Validate required fields
        if 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'success': False,
                'message': msg('favorites.error.coordinates_required')
            }), 400
        
        try:
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': msg('favorites.error.invalid_coordinates')
            }), 400
        
        # Remove from favorites
        removed = FavoriteLocation.remove_favorite(current_user.id, latitude, longitude)
        
        if removed:
            return jsonify({
                'success': True,
                'message': msg('favorites.success.removed')
            })
        else:
            return jsonify({
                'success': False,
                'message': msg('favorites.error.not_found')
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error removing favorite: {str(e)}")
        return jsonify({
            'success': False,
            'message': msg('favorites.error.remove_failed')
        }), 500


@favorites_bp.route('/check', methods=['GET'])
@login_required
def check_favorite():
    """Check if a location is in user's favorites"""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        if lat is None or lon is None:
            return jsonify({
                'success': False,
                'message': msg('favorites.error.coordinates_required')
            }), 400
        
        is_favorite = FavoriteLocation.is_favorite(current_user.id, lat, lon)
        
        return jsonify({
            'success': True,
            'is_favorite': is_favorite
        })
        
    except Exception as e:
        current_app.logger.error(f"Error checking favorite: {str(e)}")
        return jsonify({
            'success': False,
            'message': msg('favorites.error.check_failed')
        }), 500 