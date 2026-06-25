from app import db


class Cache(db.Model):
    """ Cache table """
    __tablename__ = 'cache'
    key = db.Column(db.String(255), primary_key=True)
    value = db.Column(db.Text, nullable=False)  # Stores serialized cache value
    expiration = db.Column(db.Integer, nullable=False)  # Expiration time (Unix timestamp)

class CacheLock(db.Model):
    """ Cache lock table """
    __tablename__ = 'cache_locks'
    key = db.Column(db.String(255), primary_key=True)
    owner = db.Column(db.String(255), nullable=False)  # Lock owner identifier
    expiration = db.Column(db.Integer, nullable=False)  # Lock expiration time