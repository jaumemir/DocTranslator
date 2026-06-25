from datetime import datetime

from app import db


class Setting(db.Model):
    """ System configuration table """
    __tablename__ = 'setting'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alias = db.Column(db.String(64))  # Configuration field alias
    value = db.Column(db.Text)        # Configuration field value
    serialized = db.Column(db.Boolean, default=False)  # Whether serialized
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation time
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  # Update time
    deleted_flag = db.Column(db.Enum('N', 'Y'), default='N')  # Deletion flag
    group = db.Column(db.String(32))  # Group

    def to_dict(self):
        return {
            'id': self.id,
            'alias': self.alias,
            'value': self.value,
            'serialized': self.serialized,
            'group': self.group
        }
