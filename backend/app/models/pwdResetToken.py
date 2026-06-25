from app import db


class PasswordResetToken(db.Model):
    """ Password reset token table """
    __tablename__ = 'password_reset_tokens'
    email = db.Column(db.String(255), primary_key=True)            # User email (primary key)
    token = db.Column(db.String(255), nullable=False)              # Reset token
    created_at = db.Column(db.DateTime)                            # Token creation time