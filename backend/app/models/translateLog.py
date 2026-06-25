from datetime import datetime

from app import db


class TranslateLog(db.Model):
    """ Translation log table """
    __tablename__ = 'translate_logs'

    id = db.Column(db.BigInteger, primary_key=True)
    md5_key = db.Column(db.String(100), nullable=False, unique=True)  # Source text MD5
    source = db.Column(db.Text, nullable=False)  # Source text content
    content = db.Column(db.Text)  # Translated text content
    target_lang = db.Column(db.String(32), default='zh')
    model = db.Column(db.String(255), nullable=False)  # Translation model used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Context parameters
    prompt = db.Column(db.String(1024), default='')  # Actual prompt used
    api_url = db.Column(db.String(255), default='')  # API endpoint URL
    api_key = db.Column(db.String(255), default='')  # API key
    word_count = db.Column(db.Integer, default=0)  # Word count
    backup_model = db.Column(db.String(64), default='')  # Backup model


