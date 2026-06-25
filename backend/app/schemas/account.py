from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True, error_messages={
        "required": "Old password cannot be empty"
    })
    new_password = fields.Str(required=True, validate=[
        validate.Length(min=6, error="New password must be at least 6 characters")
    ], error_messages={
        "required": "New password cannot be empty"
    })
    new_password_confirmation = fields.Str(required=True)

    @validates_schema
    def validate_password_confirmation(self, data, **kwargs):
        if data['new_password'] != data['new_password_confirmation']:
            raise ValidationError("New passwords do not match")


class EmailChangePasswordSchema(Schema):
    code = fields.Str(required=True, error_messages={
        "required": "Verification code cannot be empty"
    })
    new_password = fields.Str(required=True, validate=validate.Length(min=6))
    new_password_confirmation = fields.Str(required=True)
