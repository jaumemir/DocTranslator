from datetime import  date

from app.extensions import db


class Prompt(db.Model):
    """Prompt template table"""
    __tablename__ = 'prompt'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)              # Prompt title
    share_flag = db.Column(db.Enum('N', 'Y'), default='N')         # Share status
    added_count = db.Column(db.Integer, default=0)                 # Number of times added
    content = db.Column(db.Text, nullable=False)                   # Prompt content
    customer_id = db.Column(db.Integer, default=0)                 # Creator user ID
    created_at = db.Column(db.Date,default=date.today)                            # Creation time
    updated_at = db.Column(db.Date,onupdate=date.today)                            # Update time
    deleted_flag = db.Column(db.Enum('N', 'Y'), default='N')       # Deletion flag

class PromptFav(db.Model):
    """Prompt favorite table"""
    __tablename__ = 'prompt_fav'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    prompt_id = db.Column(db.Integer, nullable=False)              # Prompt ID
    customer_id = db.Column(db.Integer, nullable=False)            # User ID
    created_at = db.Column(db.DateTime)                            # Favorite time
    updated_at = db.Column(db.DateTime)                            # Update time
