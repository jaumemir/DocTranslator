from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.utils.jwt_utils import configure_jwt_callbacks

# Initialize extension instances

mail = Mail()
limiter = Limiter(key_func=get_remote_address)
# Create extension instances (not yet initialized)
api = Api()

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
def init_extensions(app):
    """Initialize all extensions"""
    db.init_app(app)
    api.init_app(app)
    jwt.init_app(app)
    # Configure JWT callbacks
    configure_jwt_callbacks(jwt)
    mail.init_app(app)
    migrate.init_app(app, db)
    # Delayed API initialization (avoid circular imports)
    from app.routes import register_routes
    # Register routes
    register_routes(api)
    api.init_app(app)

