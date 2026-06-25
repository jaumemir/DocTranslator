from datetime import datetime
from decimal import Decimal

from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Customer(db.Model):
    """User table"""
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_no = db.Column(db.String(32))  # User number
    phone = db.Column(db.String(11))
    name = db.Column(db.String(255))
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    level = db.Column(db.Enum('common', 'vip'), default='common')  # Membership level
    status = db.Column(db.Enum('enabled', 'disabled'), default='enabled')  # Account status
    deleted_flag = db.Column(db.Enum('N', 'Y'), default='N')  # Deletion flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation time
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  # Update time
    storage = db.Column(db.BigInteger, default=0)  # Used storage space (bytes)
    total_storage = db.Column(db.BigInteger, default=104857600) # Default 100MB total storage space (bytes)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        """Convert model instance to dictionary, handling all fields that need serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'customer_no': self.customer_no,
            'email': self.email,
            'status': 'enabled' if self.deleted_flag == 'N'and self.status == 'enabled' else 'disabled',
            'level': self.level,
            'storage': int(self.storage),
            'total_storage': int(self.total_storage),
            # Handle Decimal
            'created_at': self.created_at.isoformat() if self.created_at else None,  # Registration time
            'updated_at': self.updated_at.isoformat() if self.updated_at else None  # Update time
        }
