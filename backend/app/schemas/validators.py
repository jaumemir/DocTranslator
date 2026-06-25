# app/schemas/validators.py
VALIDATION_RULES = {
    'register': {
        'email': {'required': True, 'type': 'email'},
        'password': {'required': True, 'min_length': 6},
        'code': {'required': True}
    },
    'find': {
        'code': {'required': True},
        'password': {
            'required': True,
            'min_length': 6,
            'confirmed': True
        }
    }
}

ERROR_MESSAGES = {
    'email_required': 'Email cannot be empty',
    'password_required': 'Password cannot be empty',
    'password_min': 'Password must be at least 6 characters',
    'code_required': 'Verification code cannot be empty',
    'password_confirmed': 'Passwords do not match'
}