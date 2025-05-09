from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user
from .models import Favorite, History, db

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    city = request.form.get('city')
    fav = Favorite(user_id=current_user.id, city=city)
    db.session.add(fav)
    db.session.commit()
    return redirect(url_for('main.home'))

@favorites_bp.route('/delete_favorite/<int:id>')
@login_required
def delete_favorite(id):
    fav = Favorite.query.get(id)
    if fav.user_id == current_user.id:
        db.session.delete(fav)
        db.session.commit()
    return redirect(url_for('main.home'))
