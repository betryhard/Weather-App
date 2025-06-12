from datetime import datetime
from app import db


class FavoriteLocation(db.Model):
    __tablename__ = 'favorite_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    country = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('favorite_locations', lazy=True, cascade='all, delete-orphan'))
    
    # Unique constraint to prevent duplicate favorites for same user
    __table_args__ = (db.UniqueConstraint('user_id', 'latitude', 'longitude', name='unique_user_location'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'location_name': self.location_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'country': self.country,
            'state': self.state,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_user_favorites(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def is_favorite(cls, user_id, latitude, longitude):
        return cls.query.filter_by(
            user_id=user_id,
            latitude=round(latitude, 6),
            longitude=round(longitude, 6)
        ).first() is not None

    @classmethod
    def add_favorite(cls, user_id, location_name, latitude, longitude, country=None, state=None):
        try:
            lat_rounded = round(latitude, 6)
            lon_rounded = round(longitude, 6)
            
            existing = cls.query.filter_by(
                user_id=user_id,
                latitude=lat_rounded,
                longitude=lon_rounded
            ).first()
            
            if existing:
                return None
            
            favorite = cls(
                user_id=user_id,
                location_name=location_name,
                latitude=lat_rounded,
                longitude=lon_rounded,
                country=country,
                state=state
            )
            
            db.session.add(favorite)
            db.session.commit()
            return favorite
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def remove_favorite(cls, user_id, latitude, longitude):
        try:
            lat_rounded = round(latitude, 6)
            lon_rounded = round(longitude, 6)
            
            favorite = cls.query.filter_by(
                user_id=user_id,
                latitude=lat_rounded,
                longitude=lon_rounded
            ).first()
            
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def __repr__(self):
        return f'<FavoriteLocation {self.location_name} for User {self.user_id}>' 