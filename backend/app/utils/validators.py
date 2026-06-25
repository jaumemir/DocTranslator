# utils/validators.py
from datetime import datetime, timedelta

from app import APIResponse
from app.models import SendCode


def validate_verification_code(email: str, code: str, code_type: int):
    """Validate verification code validity"""
    expire_time = datetime.utcnow() - timedelta(minutes=10)
    send_code = SendCode.query.filter(
        SendCode.send_to == email,
        SendCode.code == code,
        SendCode.send_type == code_type,
        SendCode.created_at > expire_time
    ).order_by(SendCode.created_at.desc()).first()

    if not send_code:
        return False, '验证码已过期或无效'
    return True, None


def validate_password_confirmation(data: dict):
    """Validate password consistency"""
    if data['password'] != data.get('password_confirmation'):
        return False, '两次密码不一致'
    return True, None


def validate_password_complexity(password: str):
    """Password complexity validation"""
    if len(password) < 6:
        return False, "密码至少需要6位"
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        return False, "密码需包含字母和数字"
    return True, None


def validate_pagination_params(req):
    """Validate and get pagination parameters

    Returns:
        tuple: (page, limit)
    """
    try:
        page = int(req.args.get('page', 1))
        limit = int(req.args.get('limit', 20))

        if page < 1:
            raise ValueError('页码必须大于0')
        if limit < 1 or limit > 100:
            raise ValueError('每页数量必须在1到100之间')

        return page, limit
    except ValueError as e:
        raise APIResponse.error(str(e), 400)


def validate_date_range(start_date, end_date):
    """Validate date range parameters
    Args:
        start_date (str): Start date
        end_date (str): End date
    Returns:
        tuple: (start_date, end_date) converted datetime objects
    """
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        if start and end and start > end:
            raise ValueError('起始日期不能晚于结束日期')

        return start, end
    except ValueError as e:
        raise APIResponse.error('日期格式错误', 400)


def validate_id_list(ids):
    """Validate ID list parameters
    Args:
        ids (list): ID list
    Returns:
        list: Validated ID list
    """
    if not ids or not isinstance(ids, list):
        raise APIResponse.error('参数错误', 400)

    try:
        return [int(id) for id in ids]
    except ValueError:
        raise APIResponse.error('ID格式错误', 400)
