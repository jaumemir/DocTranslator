# Azure Communication Services Email Setup

DocTranslator supports sending emails using Azure Communication Services (ACS) as an alternative to traditional SMTP.

## Prerequisites

1. An Azure subscription
2. An Azure Communication Services resource
3. An Email Communication Service connected to your ACS resource

## Setup Steps

### 1. Create Azure Communication Services Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new **Communication Services** resource
3. Once created, go to **Keys** and note:
   - **Endpoint** (e.g., `https://your-resource.communication.azure.com`)
   - **Primary key** (base64 encoded)

### 2. Setup Email Communication Services

1. In Azure Portal, create an **Email Communication Service**
2. Add a verified domain or use the free Azure subdomain
3. Link it to your Communication Services resource
4. Once linked, go to **MailFrom addresses** and note:
   - **MailFrom address** (e.g., `DoNotReply@xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.azurecomm.net`)

### 3. Configure DocTranslator

Update your `backend/.env` file with the following variables:

```bash
# Email Provider Configuration
EMAIL_PROVIDER=azure

# Azure Communication Services Configuration
ACS_ENDPOINT=https://your-resource.communication.azure.com
ACS_ACCESS_KEY=your_base64_access_key_from_azure_portal
ACS_SENDER_ADDRESS=DoNotReply@xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.azurecomm.net
ACS_SENDER_DISPLAY_NAME=DocTranslator
```

### 4. Install Dependencies

If you added Azure email support after initial installation:

```bash
cd backend
pip install -r requirements.txt
```

### 5. Restart the Application

```bash
# If using Docker
docker-compose restart backend

# If running locally
# Stop and restart your Flask application
```

## Switching Between SMTP and Azure

You can switch between email providers by changing the `EMAIL_PROVIDER` variable:

```bash
# Use traditional SMTP
EMAIL_PROVIDER=smtp

# Use Azure Communication Services
EMAIL_PROVIDER=azure
```

When set to `smtp`, the application will use the traditional SMTP configuration (`MAIL_SERVER`, `MAIL_PORT`, etc.).

## Troubleshooting

### Email not sending

1. **Check logs**: Look for error messages in your application logs
2. **Verify credentials**: Ensure your ACS endpoint and access key are correct
3. **Check sender address**: Make sure the sender address is properly configured in ACS
4. **Domain verification**: If using a custom domain, ensure it's verified in Azure

### Authentication errors

- Ensure the `ACS_ACCESS_KEY` is the base64-encoded key from Azure Portal
- Verify that your Communication Services resource has the Email service linked

### 202 but email not received

- Check your spam/junk folder
- Verify the recipient's email domain is allowed
- Check Azure Communication Services logs in the Azure Portal

## Benefits of Azure Communication Services

- **Reliability**: Enterprise-grade email delivery
- **Scalability**: Handle high email volumes
- **No SMTP configuration**: No need to manage SMTP credentials
- **Azure integration**: Seamlessly integrates with other Azure services
- **Monitoring**: Email delivery metrics in Azure Portal

## Cost

Azure Communication Services offers a free tier with limited email sends per month. For pricing details, visit:
https://azure.microsoft.com/pricing/details/communication-services/

## Support

For Azure-specific issues, consult:
- [Azure Communication Services Documentation](https://learn.microsoft.com/azure/communication-services/)
- [Email Communication Services](https://learn.microsoft.com/azure/communication-services/concepts/email/email-overview)

For DocTranslator issues, file an issue on the GitHub repository.
