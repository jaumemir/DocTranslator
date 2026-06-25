# resources/admin/auth.py
from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app import db
from app.models.user import User
from app.utils.response import APIResponse


class AdminLoginResource(Resource):
    def post(self):
        """Admin login"""
        data = request.json
        required_fields = ['email', 'password']
        if not all(field in data for field in required_fields):
            return APIResponse.error('Missing required parameters', 400)

        try:
            # Query admin user
            admin = User.query.filter_by(
                email=data['email'],
                deleted_flag='N'
            ).first()

            # Verify user exists
            if not admin:
                current_app.logger.warning(f"User does not exist: {data['email']}")
                return APIResponse.unauthorized('Incorrect account or password')

            # Direct plain text password comparison
            if admin.password != data['password']:
                current_app.logger.warning(f"Password error: {data['email']}")
                return APIResponse.error('Incorrect account or password')

            # Generate JWT token
            access_token = create_access_token(identity=str(admin.id))
            return APIResponse.success({
                'token': access_token,
                'email': admin.email,
                'name': admin.name
            })

        except Exception as e:
            current_app.logger.error(f"Login failed: {str(e)}")
            return APIResponse.error('Internal server error', 500)


class AdminChangePasswordResource(Resource):
    @jwt_required()
    def post(self):
        """Admin change email and password"""
        try:
            # Get current admin ID
            admin_id = get_jwt_identity()
            # Parse request body
            data = request.get_json()
            required_fields = ['old_password']
            if not all(field in data for field in required_fields):
                return APIResponse.error('Missing required parameters', 400)

            # Query admin user
            admin = User.query.get(admin_id)
            if not admin:
                return APIResponse.error('Admin does not exist', 404)

            # Verify old password
            if admin.password != data['old_password']:
                return APIResponse.error(message='Incorrect old password')

            # Update email (if user is not empty)
            if 'user' in data and data['user']:
                admin.email = data['user']

            # Update password (if new_password and confirm_password are not empty and match)
            if 'new_password' in data and 'confirm_password' in data:
                if data['new_password'] and data['confirm_password']:
                    if data['new_password'] != data['confirm_password']:
                        return APIResponse.error('New password and confirmation password do not match', 400)
                    admin.password = data['new_password']  # Plain text storage

            # Save to database
            db.session.commit()

            return APIResponse.success(message='Modified successfully')

        except Exception as e:
            current_app.logger.error(f"Modification failed: {str(e)}")
            return APIResponse.error('Internal server error', 500)
