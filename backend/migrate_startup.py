import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_startup():
    from app import create_app
    app = create_app()

    with app.app_context():
        from flask_migrate import upgrade, stamp
        from sqlalchemy import inspect

        inspector = inspect(app.extensions['migrate'].db.engine)
        existing_tables = inspector.get_table_names()

        has_alembic = 'alembic_version' in existing_tables
        has_translate = 'translate' in existing_tables

        if not has_alembic and not has_translate:
            logger.info("New database, executing init.sql to create tables...")
            from app.script.init_db import safe_init_mysql
            safe_init_mysql(app, 'app/init.sql')

            logger.info("Stamping migration version to latest...")
            stamp()

        elif not has_alembic and has_translate:
            logger.info("Database has tables but no migration record, stamping initial version...")
            stamp(revision='001_initial')

            logger.info("Executing incremental migration...")
            upgrade()

        else:
            logger.info("Executing incremental migration...")
            upgrade()

    logger.info("Database migration completed")
    return app


if __name__ == '__main__':
    run_startup()
