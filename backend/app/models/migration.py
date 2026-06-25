from app import db


class Migration(db.Model):
    """ Database migration record table """
    __tablename__ = 'migrations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    migration = db.Column(db.String(255), nullable=False)          # Migration filename
    batch = db.Column(db.Integer, nullable=False)                  # Migration batch number