# utils/task_utils.py
import datetime


def generate_task_no():
    """Generate task number"""
    now = datetime.datetime.now()
    return f"T{now.strftime('%Y%m%d%H%M%S')}"
