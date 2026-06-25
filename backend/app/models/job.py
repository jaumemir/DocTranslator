from datetime import datetime
from app import db


class FailedJob(db.Model):
    """ Failed job record table """
    __tablename__ = 'failed_jobs'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(255), unique=True)                   # Job UUID
    connection = db.Column(db.Text, nullable=False)                 # Connection information
    queue = db.Column(db.Text, nullable=False)                      # Queue name
    payload = db.Column(db.Text, nullable=False)                    # Job payload data
    exception = db.Column(db.Text, nullable=False)                  # Exception information
    failed_at = db.Column(db.DateTime, default=datetime.utcnow)     # Failure timestamp\


class JobBatch(db.Model):
    """ Job batch record table """
    __tablename__ = 'job_batches'
    id = db.Column(db.String(255), primary_key=True)  # Batch ID (UUID)
    name = db.Column(db.String(255), nullable=False)  # Batch name
    total_jobs = db.Column(db.Integer, nullable=False)  # Total job count
    pending_jobs = db.Column(db.Integer, nullable=False)  # Pending job count
    failed_jobs = db.Column(db.Integer, nullable=False)  # Failed job count
    failed_job_ids = db.Column(db.Text, nullable=False)  # Failed job ID list (JSON)
    options = db.Column(db.Text)  # Job options configuration
    cancelled_at = db.Column(db.Integer)  # Cancellation timestamp
    created_at = db.Column(db.Integer, nullable=False)  # Creation timestamp
    finished_at = db.Column(db.Integer)  # Completion timestamp

class Job(db.Model):
    """ Queue job table """
    __tablename__ = 'jobs'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    queue = db.Column(db.String(255), nullable=False)              # Queue name
    payload = db.Column(db.Text, nullable=False)                   # Job data (JSON)
    attempts = db.Column(db.SmallInteger, nullable=False)          # Attempt count
    reserved_at = db.Column(db.Integer)                            # Reserved timestamp
    available_at = db.Column(db.Integer, nullable=False)           # Available timestamp
    created_at = db.Column(db.Integer, nullable=False)             # Creation timestamp


