"""
Azure Communication Services Email Utility
Provides email sending functionality using Azure Communication Services
"""

import os
import hmac
import hashlib
import base64
import json
import requests
from datetime import datetime
from uuid import uuid4
from flask import current_app
from typing import Dict, Optional


class AzureEmailService:
    """Azure Communication Services Email Service"""

    @staticmethod
    def _build_acs_headers(body_string: str) -> Dict[str, str]:
        """Build authentication headers for Azure Communication Services

        Args:
            body_string: JSON string of the request body

        Returns:
            Dictionary of HTTP headers including authentication
        """
        endpoint = os.getenv('ACS_ENDPOINT')
        access_key = os.getenv('ACS_ACCESS_KEY')

        if not endpoint or not access_key:
            raise ValueError('ACS_ENDPOINT and ACS_ACCESS_KEY must be set')

        # Calculate content hash
        content_hash = base64.b64encode(
            hashlib.sha256(body_string.encode('utf-8')).digest()
        ).decode('utf-8')

        # Build date and host
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        host = endpoint.replace('https://', '').replace('http://', '')
        path = '/emails:send?api-version=2023-03-31'

        # Build string to sign
        string_to_sign = f"POST\n{path}\n{date};{host};{content_hash}"

        # Decode access key from base64 and create HMAC signature
        key_buffer = base64.b64decode(access_key)
        signature = base64.b64encode(
            hmac.new(key_buffer, string_to_sign.encode('utf-8'), hashlib.sha256).digest()
        ).decode('utf-8')

        # Build headers
        return {
            'x-ms-date': date,
            'x-ms-content-sha256': content_hash,
            'Content-Type': 'application/json',
            'Authorization': f'HMAC-SHA256 SignedHeaders=x-ms-date;host;x-ms-content-sha256&Signature={signature}',
            'repeatability-request-id': str(uuid4()),
            'repeatability-first-sent': date,
        }

    @staticmethod
    def send_email(
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None
    ) -> bool:
        """Send an email using Azure Communication Services

        Args:
            to: Recipient email address
            subject: Email subject
            html: HTML content
            text: Plain text content (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        endpoint = os.getenv('ACS_ENDPOINT')
        sender_address = os.getenv('ACS_SENDER_ADDRESS')
        sender_display_name = os.getenv('ACS_SENDER_DISPLAY_NAME', 'DocTranslator')

        if not endpoint or not sender_address:
            current_app.logger.error(
                'ACS email configuration missing: ACS_ENDPOINT and ACS_SENDER_ADDRESS are required'
            )
            return False

        # Build request payload
        payload = {
            'senderAddress': sender_address,
            'displayName': sender_display_name,
            'content': {
                'subject': subject,
                'html': html,
            },
            'recipients': {
                'to': [{'address': to}]
            }
        }

        # Add plain text if provided
        if text:
            payload['content']['plainText'] = text

        # Convert to JSON string
        body_string = json.dumps(payload)

        # Build headers
        try:
            headers = AzureEmailService._build_acs_headers(body_string)
        except Exception as e:
            current_app.logger.error(f'Failed to build ACS headers: {e}')
            return False

        # Send request
        url = f'{endpoint}/emails:send?api-version=2023-03-31'

        try:
            response = requests.post(url, data=body_string, headers=headers, timeout=30)

            if response.status_code == 202:
                current_app.logger.info(f'Email sent successfully via ACS to {to}')
                return True
            else:
                current_app.logger.error(
                    f'ACS email API returned status {response.status_code}: {response.text}'
                )
                return False

        except Exception as e:
            current_app.logger.error(f'Error sending email via ACS: {e}')
            return False

    @staticmethod
    def send_verification_code(email: str, code: str, user_name: str = None) -> bool:
        """Send registration verification code email

        Args:
            email: Recipient email address
            code: Verification code
            user_name: User's name (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        from app.utils.mail_templates import generate_register_email

        user_data = {'name': user_name or 'User'}
        html_content = generate_register_email(user_data, code)

        return AzureEmailService.send_email(
            to=email,
            subject='【DocTranslator】Registration Verification Code',
            html=html_content
        )

    @staticmethod
    def send_password_reset(email: str, code: str) -> bool:
        """Send password reset verification code email

        Args:
            email: Recipient email address
            code: Reset verification code

        Returns:
            True if email sent successfully, False otherwise
        """
        from app.utils.mail_templates import generate_reset_password_email

        user_data = {'email': email}
        html_content = generate_reset_password_email(user_data, code)

        return AzureEmailService.send_email(
            to=email,
            subject='【DocTranslator】Password Reset Verification Code',
            html=html_content
        )
