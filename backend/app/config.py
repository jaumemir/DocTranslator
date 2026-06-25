import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (prioritize .env file in project root)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class Config:
    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=20)
    # JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)  # Refresh token expires in 7 days
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'token'
    JWT_HEADER_TYPE = ''
    # General base configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail configuration (common to all environments)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    MAIL_DEBUG = True  # Enable SMTP debugging
    # Business configuration
    CODE_EXPIRATION = 1800  # 30 minutes (in seconds)
    # File upload configuration
    # Allowed file types for upload
    UPLOAD_BASE_DIR='storage'
    UPLOAD_ROOT = os.path.join(os.path.dirname(__file__), 'uploads')
    DATE_FORMAT = "%Y-%m-%d"  # Date format
    ALLOWED_EXTENSIONS = {'docx', 'xlsx', 'pptx', 'pdf', 'txt', 'md', 'csv', 'xls', 'doc', 'html', 'htm'}
    # UPLOAD_FOLDER = '/uploads'  # Recommended to use absolute path
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50)) * 1024 * 1024  # 50MB
    MAX_USER_STORAGE = int(os.getenv('MAX_USER_STORAGE', 100 ))* 1024 * 1024  # Default 100MB
    # Translation result storage configuration
    STORAGE_FOLDER = '/app/storage'  # Translation result storage path
    STATIC_FOLDER = '/public/static'  # Static file path

    # System version configuration
    SYSTEM_VERSION = 'business'  # business/community
    SITE_NAME = '智能翻译平台'

    # API configuration
    API_URL = 'https://api.example.com'
    TRANSLATE_MODELS = ['gpt-3.5', 'gpt-4']

    # Timezone
    TIMEZONE = 'Asia/Shanghai'#'UTC' #'Asia/Shanghai'
    @property
    def allowed_domains(self):
        """Get formatted domain list"""
        domains = os.getenv('ALLOWED_DOMAINS', '')
        return [d.strip() for d in domains.split(',') if d.strip()]



class DevelopmentConfig(Config):
    DEBUG = True
    # SQLite configuration (development environment)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL',
        f'sqlite:///instance/dev.db'  # Explicit absolute path
    )
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///yourdatabase.db'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'echo': False  # Output SQL logs
    }


class TestingConfig(Config):
    TESTING = True
    # In-memory SQLite (testing environment)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF protection


class ProductionConfig(Config):
    # MySQL/PostgreSQL configuration (production environment)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'PROD_DATABASE_URL',
        'mysql://user:password@localhost/prod_db?charset=utf8mb4'
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 30,
        'pool_timeout': 10
    }


# Configuration mapping dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Factory method to safely retrieve configuration object"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])