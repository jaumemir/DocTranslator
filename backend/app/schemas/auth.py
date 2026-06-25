from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema
from flask import current_app


class SendCodeSchema(Schema):
    email = fields.Email(required=True, error_messages={
        "required": "Email is required",
        "invalid": "Invalid email format"
    })

    @validates("email")
    def validate_email_domain(self, value):
        allowed_domains = current_app.config.get('ALLOWED_EMAIL_DOMAINS', [])
        if allowed_domains:
            domain = value.split('@')[-1]
            if domain not in allowed_domains:
                raise ValidationError("Email domain not allowed")


class RegisterSchema(Schema):
    email = fields.Email(required=True, error_messages={
        "required": "Email cannot be empty",
        "invalid": "Invalid email format"
    })
    password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        error_messages={
            "required": "Password cannot be empty",
            "too_short": "Password must be at least 6 characters"
        }
    )
    code = fields.String(required=True, error_messages={"required": "Verification code cannot be empty"})
class LoginSchema(Schema):
    email = fields.Email(required=True, error_messages={
        "required": "Email cannot be empty",
        "invalid": "Invalid email format"
    })
    password = fields.String(required=True, error_messages={
        "required": "Password cannot be empty"
    })

class FindSendSchema(Schema):
    email = fields.Email(required=True, error_messages={
        "required": "Email cannot be empty",
        "invalid": "Invalid email format"
    })

class FindResetSchema(Schema):
    email = fields.Email(required=True)
    code = fields.String(required=True)
    password = fields.String(required=True, validate=lambda x: len(x) >= 6)
    password_confirmation = fields.String(required=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data['password'] != data['password_confirmation']:
            raise ValidationError("Passwords do not match", "password_confirmation")
