# resources/auth.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from datetime import datetime
from app import db
from app.models import Customer, SendCode
from app.utils.security import hash_password, verify_password
from app.utils.response import APIResponse
from app.utils.mail_service import EmailService
import random

from app.utils.validators import (
    validate_verification_code,
    validate_password_confirmation
)


class SendRegisterCodeResource(Resource):
    def post(self):
        """Send registration verification code"""
        email = request.form.get('email')
        if Customer.query.filter_by(email=email).first():
            return APIResponse.error('邮箱已存在', 400)

        code = ''.join(random.choices('0123456789', k=6))
        send_code = SendCode(
            send_type=1,
            send_to=email,
            code=code,
            created_at=datetime.utcnow()
        )
        db.session.add(send_code)
        try:
            EmailService.send_verification_code(email, code)
            db.session.commit()
            return APIResponse.success()
        except Exception as e:
            db.session.rollback()
            return APIResponse.error('邮件发送失败', 500)


class UserRegisterResource(Resource):
    def post(self):
        """User registration API"""
        data = request.form

        required_fields = ['email', 'password', 'code']
        if not all(field in data for field in required_fields):
            return APIResponse.error('缺少必要参数', 400)

        # Verification code validity check
        is_valid, msg = validate_verification_code(
            data['email'], data['code'], 1
        )
        if not is_valid:
            return APIResponse.error(msg, 400)

        customer = Customer(
            name=data.get('name', ''),
            email=data['email'],
            password=hash_password(data['password']),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(customer)
        db.session.commit()

        # Ensure identity is a string
        # access_token = create_access_token(identity=str(customer.id))
        return APIResponse.success(message='注册成功！', data={
            # 'token': access_token,
            'email': data['email']
        })


class UserLoginResource(Resource):
    def post(self):
        """User login API"""
        data = request.form
        customer = Customer.query.filter_by(email=data['email']).first()

        if not customer or not verify_password(customer.password, data['password']):
            return APIResponse.error('账号或密码错误')
        # Ensure identity is a string
        access_token = create_access_token(identity=str(customer.id))
        return APIResponse.success({
            'token': access_token,
            'email': data['email'],
            'name': customer.name,
            'level': customer.level
        })


class SendResetCodeResource(Resource):
    def post(self):
        """Send password reset verification code"""
        email = request.form.get('email')
        if not Customer.query.filter_by(email=email).first():
            return APIResponse.not_found('用户不存在')

        code = ''.join(random.choices('0123456789', k=6))
        send_code = SendCode(
            send_type=2,
            send_to=email,
            code=code,
            created_at=datetime.utcnow()
        )
        db.session.add(send_code)
        try:
            EmailService.send_verification_code(email, code)
            db.session.commit()
            return APIResponse.success()
        except Exception as e:
            db.session.rollback()
            return APIResponse.error('邮件发送失败', 500)


class ResetPasswordResource(Resource):
    def post(self):
        """Reset password API"""
        data = request.form

        # Password consistency verification
        is_valid, msg = validate_password_confirmation(data)
        if not is_valid:
            return APIResponse.error(msg, 400)

        # Verification code validity check
        is_valid, msg = validate_verification_code(
            data['email'], data['code'], 2
        )
        if not is_valid:
            return APIResponse.error(msg, 400)

        customer = Customer.query.filter_by(email=data['email']).first()
        customer.password = hash_password(data['password'])
        customer.updated_at = datetime.utcnow()
        db.session.commit()
        return APIResponse.success()
