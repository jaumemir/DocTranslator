#!/usr/bin/env python3
"""
Email Configuration Test Script

This script tests your email configuration (SMTP or Azure Communication Services)
to ensure emails can be sent successfully.

Usage:
    python test_email.py <recipient_email>

Example:
    python test_email.py user@example.com
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv()

def test_azure_email(recipient: str):
    """Test Azure Communication Services email"""
    print("Testing Azure Communication Services email...")
    print(f"Endpoint: {os.getenv('ACS_ENDPOINT')}")
    print(f"Sender: {os.getenv('ACS_SENDER_ADDRESS')}")

    from app.utils.azure_email import AzureEmailService

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 30px; border-radius: 10px; }
            h1 { color: #3b82f6; }
            .code { background: #e0f2fe; padding: 15px; font-size: 24px; font-weight: bold; text-align: center; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>DocTranslator Email Test</h1>
            <p>This is a test email from DocTranslator using Azure Communication Services.</p>
            <p>If you received this email, your Azure email configuration is working correctly!</p>
            <div class="code">TEST-123456</div>
            <p style="color: #666; font-size: 12px; margin-top: 20px;">
                This is an automated test email. Please do not reply.
            </p>
        </div>
    </body>
    </html>
    """

    result = AzureEmailService.send_email(
        to=recipient,
        subject="【DocTranslator】Email Configuration Test",
        html=html_content
    )

    if result:
        print("✅ Email sent successfully via Azure Communication Services!")
        print(f"   Check the inbox for: {recipient}")
    else:
        print("❌ Failed to send email via Azure Communication Services")
        print("   Check the logs above for error details")

    return result


def test_smtp_email(recipient: str):
    """Test traditional SMTP email"""
    print("Testing SMTP email...")
    print(f"Server: {os.getenv('MAIL_SERVER')}")
    print(f"Port: {os.getenv('MAIL_PORT')}")
    print(f"Username: {os.getenv('MAIL_USERNAME')}")

    # We need Flask app context for SMTP
    from app import create_app
    app = create_app()

    with app.app_context():
        from app.utils.mail_service import EmailService

        # Create a simple test HTML
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .container { max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 30px; border-radius: 10px; }
                h1 { color: #3b82f6; }
                .code { background: #e0f2fe; padding: 15px; font-size: 24px; font-weight: bold; text-align: center; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>DocTranslator Email Test</h1>
                <p>This is a test email from DocTranslator using SMTP.</p>
                <p>If you received this email, your SMTP configuration is working correctly!</p>
                <div class="code">TEST-123456</div>
                <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    This is an automated test email. Please do not reply.
                </p>
            </div>
        </body>
        </html>
        """

        result = EmailService._send_via_smtp(
            email=recipient,
            subject="【DocTranslator】Email Configuration Test",
            html_content=html_content
        )

        if result:
            print("✅ Email sent successfully via SMTP!")
            print(f"   Check the inbox for: {recipient}")
        else:
            print("❌ Failed to send email via SMTP")
            print("   Check the logs above for error details")

        return result


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python test_email.py <recipient_email>")
        print("\nExample:")
        print("  python test_email.py user@example.com")
        sys.exit(1)

    recipient = sys.argv[1]

    # Validate email format (basic)
    if '@' not in recipient or '.' not in recipient:
        print(f"❌ Invalid email format: {recipient}")
        sys.exit(1)

    print("=" * 60)
    print("DocTranslator Email Configuration Test")
    print("=" * 60)
    print(f"Recipient: {recipient}")
    print()

    # Determine email provider
    provider = os.getenv('EMAIL_PROVIDER', 'smtp').lower()
    print(f"Configured provider: {provider}")
    print()

    if provider == 'azure':
        # Check required Azure variables
        required_vars = ['ACS_ENDPOINT', 'ACS_ACCESS_KEY', 'ACS_SENDER_ADDRESS']
        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            print(f"❌ Missing required environment variables: {', '.join(missing)}")
            print("\nPlease set these variables in your .env file:")
            print("  ACS_ENDPOINT=https://your-resource.communication.azure.com")
            print("  ACS_ACCESS_KEY=your_base64_access_key")
            print("  ACS_SENDER_ADDRESS=DoNotReply@xxxxx.azurecomm.net")
            sys.exit(1)

        success = test_azure_email(recipient)
    else:
        # Check required SMTP variables
        required_vars = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD']
        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            print(f"❌ Missing required environment variables: {', '.join(missing)}")
            print("\nPlease set these variables in your .env file:")
            print("  MAIL_SERVER=smtp.example.com")
            print("  MAIL_PORT=587")
            print("  MAIL_USERNAME=your_email@example.com")
            print("  MAIL_PASSWORD=your_password")
            sys.exit(1)

        success = test_smtp_email(recipient)

    print()
    print("=" * 60)
    if success:
        print("✅ Email configuration test PASSED")
    else:
        print("❌ Email configuration test FAILED")
        print("\nTroubleshooting tips:")
        print("1. Check your .env file has the correct values")
        print("2. Verify your email credentials are valid")
        print("3. Check firewall/network settings")
        print("4. Review application logs for detailed errors")
    print("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
