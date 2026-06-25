from flask_mail import Message
from app.extensions import mail
from app.utils.mail_templates import generate_register_email
from flask import current_app


class EmailService:
    @staticmethod
    def send_verification_code(email: str, code: str, user_name: str = None):
        """Send registration verification code email"""
        try:
            user_data = {'name': user_name or '用户'}

            # Generate HTML email content
            html_content = generate_register_email(user_data, code)

            # Create email message
            msg = Message(
                subject="【DocTranslator】注册验证码",
                recipients=[email],
                html=html_content,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )

            # Send email
            mail.send(msg)
            current_app.logger.info(f"Verification code email sent successfully: {email}")
            return True

        except Exception as e:
            current_app.logger.error(f"Failed to send verification code email: {e}")
            return False


    @staticmethod
    def send_forgot_password(email: str, reset_link: str):
        """Send password reset email"""
        try:
            # Password reset template can be added here
            html_content = f"""
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>密码重置</h2>
                <p>请点击以下链接重置您的密码：</p>
                <a href="{reset_link}" style="background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    重置密码
                </a>
                <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    此链接有效期为30分钟，如非本人操作请忽略。
                </p>
            </div>
            """

            msg = Message(
                subject="【DocTranslator】密码重置",
                recipients=[email],
                html=html_content,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )

            mail.send(msg)
            return True

        except Exception as e:
            current_app.logger.error(f"Failed to send password reset email: {e}")
            return False
