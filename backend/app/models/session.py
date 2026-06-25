from app import db


class Session(db.Model):
    """ User session table """
    __tablename__ = 'sessions'
    id = db.Column(db.String(255), primary_key=True)               # Session ID
    user_id = db.Column(db.BigInteger)                             # Associated user ID
    ip_address = db.Column(db.String(45))                          # Client IP address
    user_agent = db.Column(db.Text)                                # User agent string
    payload = db.Column(db.Text, nullable=False)                   # Session data
    last_activity = db.Column(db.Integer, nullable=False)          # Last activity timestamp