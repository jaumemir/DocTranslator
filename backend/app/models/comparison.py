from datetime import datetime
from app import db


class Comparison(db.Model):
    """Terminology comparison table"""
    __tablename__ = 'comparison'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)               # Comparison table title
    origin_lang = db.Column(db.String(32), nullable=False)          # Source language code (e.g., en)
    target_lang = db.Column(db.String(32), nullable=False)          # Target language code (e.g., zh)
    share_flag = db.Column(db.Enum('N', 'Y'), default='N')          # Whether shared
    added_count = db.Column(db.Integer, default=0)                  # Number of times added (previously missing field)
    content = db.Column(db.Text, nullable=False)                    # Term content (source1,target1;source2,target2)
    customer_id = db.Column(db.Integer, default=0)                  # Creator user ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)                            # Update time
    deleted_flag = db.Column(db.Enum('N', 'Y'), default='N')        # Deletion flag

    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'origin_lang': self.origin_lang,
            'target_lang': self.target_lang,
            'share_flag': self.share_flag,
            'added_count': self.added_count,
            'content': self.content,
            'customer_id': self.customer_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,  # Format time
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else None,  # Format time
            'deleted_flag': self.deleted_flag
        }

class ComparisonFav(db.Model):
    """Comparison table favorite relationship"""
    __tablename__ = 'comparison_fav'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comparison_id = db.Column(db.Integer, nullable=False)           # Comparison table ID
    customer_id = db.Column(db.Integer, nullable=False)             # User ID
    created_at = db.Column(db.DateTime,default=datetime.utcnow)                             # Favorite time
    updated_at = db.Column(db.DateTime,onupdate=datetime.utcnow)                             # Update time


