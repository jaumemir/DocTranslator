import os
import platform
import re
import time
from flask import Flask
import pymysql
import logging
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

# Configure cross-platform compatible logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('db_init.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def safe_init_mysql(app: Flask, sql_file: str = 'init.sql') -> bool:

    if not app or not isinstance(app, Flask):
        logger.error("Invalid Flask application instance")
        return False

    with app.app_context():
        try:
            # Cross-platform path handling
            sql_path = get_platform_path(sql_file)
            if not sql_path.exists():
                logger.warning(f"SQL file {sql_path} does not exist, skipping initialization")
                return False

            # Get database configuration (compatible with environment variables)
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', os.getenv('PROD_DATABASE_URL'))
            if not db_url:
                logger.error("Database configuration not found")
                return False

            # Parse connection info (enhanced compatibility)
            conn_info = parse_db_url(db_url)
            if not conn_info:
                logger.error("Invalid database connection string")
                return False

            # Check if already initialized (with retry mechanism)
            if check_database_initialized(conn_info):
                logger.info("Database already initialized, skipping execution")
                return False

            logger.info("Starting safe MySQL database initialization...")
            return execute_with_retry(conn_info, sql_path)

        except Exception as e:
            logger.error(f"Database initialization exception: {str(e)}", exc_info=True)
            return False


def get_platform_path(file_path: str) -> Path:
    """Handle cross-platform file path issues"""
    # Convert to absolute path uniformly
    path = Path(file_path).absolute()

    # Check case sensitivity on Linux/macOS
    if platform.system() in ('Linux', 'Darwin'):
        try:
            # Try to find actual existing path (solve case issues)
            if path.exists():
                return path
            # Try to find case-insensitive matching path
            parent = path.parent
            for f in parent.iterdir():
                if f.name.lower() == path.name.lower():
                    return f
        except Exception as e:
            logger.warning(f"Path check exception: {str(e)}")

    return path


def parse_db_url(db_url: str) -> Optional[dict]:
    """Enhanced database URL parsing"""
    try:
        result = urlparse(db_url)
        # Handle special characters on Windows
        password = result.password.replace('%', '%%') if result.password else None

        return {
            'host': result.hostname,
            'port': result.port or 3306,
            'user': result.username,
            'password': password,
            'db': result.path[1:].split('?')[0],  # Remove leading / and query params
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
            'connect_timeout': 10,
            'read_timeout': 30
        }
    except Exception as e:
        logger.error(f"Failed to parse database URL: {str(e)}")
        return None


def check_database_initialized(conn_info: dict, retries: int = 3) -> bool:
    """Database initialization check with retry mechanism"""
    for attempt in range(retries):
        try:
            connection = None
            connection = pymysql.connect(**conn_info)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM information_schema.tables
                    WHERE table_schema = %s AND table_name = 'alembic_version'
                """, (conn_info['db'],))
                result = cursor.fetchone()
                return result['count'] > 0
        except pymysql.OperationalError as e:
            if attempt == retries - 1:
                logger.warning(f"Database connection failed ({retries} attempts): {str(e)}")
                return False
            logger.warning(f"Database connection exception, retrying... ({attempt + 1}/{retries})")
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logger.warning(f"Database check exception: {str(e)}")
            return False
        finally:
            if connection:
                connection.close()
    return False


def execute_with_retry(conn_info: dict, sql_path: Path, retries: int = 3) -> bool:
    """Database initialization with retry mechanism"""
    for attempt in range(retries):
        try:
            return execute_safe_init(conn_info, sql_path)
        except pymysql.OperationalError as e:
            if attempt == retries - 1:
                logger.error(f"Database operation failed after {retries} attempts: {str(e)}")
                return False
            logger.warning(f"Database operation exception, retrying... ({attempt + 1}/{retries})")
            time.sleep(2 ** attempt)
    return False


def execute_safe_init(conn_info: dict, sql_path: Path) -> bool:
    """Enhanced safe initialization execution"""
    connection = None
    try:
        # Create connection (set longer timeout)
        conn_info['connect_timeout'] = 20
        connection = pymysql.connect(**conn_info)

        with connection.cursor() as cursor:
            # Create database (compatible with various charsets)
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS `{conn_info['db']}`
                CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            cursor.execute(f"USE `{conn_info['db']}`")

            # Read SQL file (handle different platform line endings)
            with open(sql_path, 'r', encoding='utf-8-sig') as f:  # Handle BOM
                content = f.read().replace('\r\n', '\n')  # Normalize line endings

            # Execute SQL statements
            for statement in parse_sql_content(content):
                execute_safe_sql(cursor, statement)

        connection.commit()
        logger.info("Database initialization completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        if connection:
            connection.rollback()
        raise  # Re-raise exception for retry mechanism
    finally:
        if connection:
            connection.close()


def parse_sql_content(content: str) -> list:
    """Improved SQL content parsing"""
    # First remove MySQL conditional comments /*!digit ... */
    content = re.sub(r'/\*!\d+\s+.*?\*/', '', content, flags=re.DOTALL)

    # Remove normal block comments /* ... */
    content = re.sub(r'/\*[^!].*?\*/', '', content, flags=re.DOTALL)

    lines = []
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue

        # Filter transaction control statements
        upper = line.upper().rstrip(';').strip()
        if upper in ('START TRANSACTION', 'COMMIT', 'ROLLBACK', 'BEGIN'):
            continue

        # Handle inline -- comments (but preserve non-comment parts after -- in SET statements)
        comment_pos = line.find('--')
        if comment_pos > 0:
            line = line[:comment_pos].strip()

        if line:
            lines.append(line)

    # Merge statements (handle multi-line statements)
    statements = []
    current = ""
    for line in lines:
        current += " " + line if current else line
        if ';' in line:
            stmt, _, remaining = current.partition(';')
            stmt_stripped = stmt.strip()
            # Filter transaction control statements again (may be multi-line after merge)
            if stmt_stripped.upper() not in ('START TRANSACTION', 'COMMIT', 'ROLLBACK', 'BEGIN'):
                statements.append(stmt_stripped)
            current = remaining.strip()

    if current and current.upper() not in ('START TRANSACTION', 'COMMIT', 'ROLLBACK', 'BEGIN'):
        statements.append(current.strip())

    return statements


def execute_safe_sql(cursor, sql: str):
    """Enhanced safe SQL execution"""
    try:
        if sql.strip():  # Ignore empty statements
            cursor.execute(sql)
    except pymysql.Error as e:
        error_code = e.args[0]
        ignorable_errors = {
            1050: "Table already exists",
            1060: "Column already exists",
            1061: "Key already exists",
            1062: "Duplicate entry",
            1068: "Primary key already exists",
            1064: "Syntax warning",
            1054: "Unknown column",
            1146: "Table does not exist",
            2006: "MySQL server has gone away",
            2013: "Lost connection during query"
        }

        if error_code in ignorable_errors:
            logger.warning(f"Safely skipping SQL execution ({error_code}-{ignorable_errors[error_code]})")
        else:
            logger.error(f"SQL execution error ({error_code}): {str(e)}")
            raise



