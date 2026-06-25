# ========== utils/auth_tools.py ==========
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


def generate_code(length=6):
    """Generate numeric verification code"""
    return ''.join(random.choices('0123456789', k=length))


def validate_code(code_record):
    """Verification code validity check"""
    if not code_record:
        return False
    return (datetime.utcnow() - code_record.created_at) < timedelta(seconds=1800)


def hash_password(password):
    """Password hash processing"""
    return generate_password_hash(password)


def check_password(hashed_password, password):
    """Password verification"""
    return check_password_hash(hashed_password, password)
