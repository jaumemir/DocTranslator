from flask import Flask, jsonify
from flask_cors import CORS
from .config import get_config
from .extensions import init_extensions, db, api
from .models.setting import Setting
from .resources.task.translate_service import TranslateEngine
from .script.init_db import safe_init_mysql
from .script.insert_init_db import insert_initial_data, set_auto_increment, insert_initial_settings, insert_initial_admin
from .utils.response import APIResponse


def create_app(config_class=None):
    app = Flask(__name__)

    from .routes import register_routes
    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    # Initialize database (only for MySQL, SQLite uses db.create_all())
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('mysql'):
        safe_init_mysql(app,'app/init.sql')
    # Initialize extensions (routes not registered yet)
    init_extensions(app)
    register_routes(api)

    @app.errorhandler(404)
    def handle_404(e):
        return APIResponse.not_found()

    from jwt.exceptions import ExpiredSignatureError

    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_token_error(e):
        return jsonify({"message": "Authentication information has expired, please log in again"}), 401

    @app.errorhandler(500)
    def handle_500(e):
        return APIResponse.error(message='Server error', code=500)

    # Initialize database
    with app.app_context():
        db.create_all()
        # Call TranslateEngine here if needed
        # engine = TranslateEngine(task_id=1, app=app)
        # engine.execute()
        # Initialize default configuration
        # if not SystemSetting.query.filter_by(key='version').first():
        #     db.session.add(SystemSetting(key='version', value='business'))
        #     db.session.commit()
    insert_initial_data(app)
    set_auto_increment(app)
    insert_initial_settings(app)
    insert_initial_admin(app)

    return app