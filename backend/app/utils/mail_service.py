import os
from flask_mail import Message
from app.extensions import mail
from app.utils.mail_templates import generate_register_email, generate_reset_password_email
from flask import current_app


class EmailService:
    """
    Email service that supports both traditional SMTP and Azure Communication Services.

    Set EMAIL_PROVIDER environment variable to 'azure' to use Azure Communication Services,
    or 'smtp' (or leave unset) to use traditional SMTP.
    """

    @staticmethod
    def _get_email_provider():
        """Get the configured email provider"""
        return os.getenv('EMAIL_PROVIDER', 'smtp').lower()

    @staticmethod
    def _send_via_azure(email: str, subject: str, html_content: str) -> bool:
        """Send email via Azure Communication Services"""
        try:
            from app.utils.azure_email import AzureEmailService
            return AzureEmailService.send_email(
                to=email,
                subject=subject,
                html=html_content
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send email via Azure: {e}")
            return False

    @staticmethod
    def _send_via_smtp(email: str, subject: str, html_content: str) -> bool:
        """Send email via traditional SMTP"""
        try:
            msg = Message(
                subject=subject,
                recipients=[email],
                html=html_content,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            mail.send(msg)
            current_app.logger.info(f"Email sent successfully via SMTP to: {email}")
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send email via SMTP: {e}")
            return False

    @staticmethod
    def send_verification_code(email: str, code: str, user_name: str = None):
        """Send registration verification code email"""
        try:
            user_data = {'name': user_name or 'User'}
            html_content = generate_register_email(user_data, code)
            subject = "【DocTranslator】Registration Verification Code"

            provider = EmailService._get_email_provider()

            if provider == 'azure':
                return EmailService._send_via_azure(email, subject, html_content)
            else:
                return EmailService._send_via_smtp(email, subject, html_content)

        except Exception as e:
            current_app.logger.error(f"Failed to send verification code email: {e}")
            return False

    @staticmethod
    def send_forgot_password(email: str, code: str):
        """Send password reset verification code email"""
        try:
            user_data = {'email': email}
            html_content = generate_reset_password_email(user_data, code)
            subject = "【DocTranslator】Password Reset Verification Code"

            provider = EmailService._get_email_provider()

            if provider == 'azure':
                return EmailService._send_via_azure(email, subject, html_content)
            else:
                return EmailService._send_via_smtp(email, subject, html_content)

        except Exception as e:
            current_app.logger.error(f"Failed to send password reset email: {e}")
            return False
