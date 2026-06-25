# utils/file_utils.py
import uuid
from werkzeug.utils import secure_filename
import os
import hashlib
from pathlib import Path
from datetime import datetime
from flask import current_app


class FileManager:
    @staticmethod
    def get_upload_dir():
        """
        Get upload file storage directory
        :return: Absolute path of upload file storage directory
        """
        base_dir = Path(current_app.config['UPLOAD_BASE_DIR'])
        date_str = datetime.now().strftime('%Y-%m-%d')
        upload_dir = base_dir / 'uploads' / date_str
        upload_dir.mkdir(parents=True, exist_ok=True)
        return str(upload_dir)

    @staticmethod
    def generate_filename(filename):
        """
        Generate unique filename
        :param filename: Original filename
        :return: Unique filename
        """
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{name}_{timestamp}{ext}"

    @staticmethod
    def get_relative_path(full_path):
        """
        Get relative path to storage root directory
        :param full_path: Absolute path of file
        :return: Relative path
        """
        base_dir = Path(current_app.config['UPLOAD_BASE_DIR'])
        return str(Path(full_path).relative_to(base_dir)).replace('\\', '/')

    @staticmethod
    def exists(file_path):
        """
        Check if file exists
        :param file_path: Relative or absolute path of file
        :return: Whether file exists (True/False)
        """
        if not file_path:
            return False
        full_path = os.path.join(current_app.config['UPLOAD_BASE_DIR'], file_path.lstrip('/'))
        return os.path.exists(full_path)

    @staticmethod
    def calculate_md5(file_path):
        """
        Calculate MD5 value of file
        :param file_path: Absolute path of file
        :return: MD5 value of file
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def allowed_file(filename):
        """
        Validate whether file type is allowed
        :param filename: Filename
        :return: Whether file type is allowed (True/False)
        """
        ALLOWED_EXTENSIONS = {'docx', 'xlsx', 'pptx', 'pdf', 'txt', 'md', 'csv', 'xls', 'doc', 'html', 'htm'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def validate_file_size(file_stream):
        """
        Validate whether file size exceeds limit
        :param file_stream: File stream
        :return: Whether file size is valid (True/False)
        """
        MAX_FILE_SIZE = current_app.config['MAX_FILE_SIZE']#10 * 1024 * 1024  # 10MB
        file_stream.seek(0, os.SEEK_END)
        file_size = file_stream.tell()
        file_stream.seek(0)
        return file_size <= MAX_FILE_SIZE

    @staticmethod
    def get_translate_absolute_path(filename):
        """
        Get absolute path of translation result (keep original filename)
        :param filename: Original filename
        :return: Absolute path of translation result
        """
        base_dir = Path(current_app.config['UPLOAD_BASE_DIR'])
        date_str = datetime.now().strftime('%Y-%m-%d')
        translate_dir = base_dir / 'translate' / date_str
        translate_dir.mkdir(parents=True, exist_ok=True)
        return str(translate_dir / filename)




class FileManager11:
    @staticmethod
    def allowed_file(filename):
        """Validate whether file type is allowed"""
        ALLOWED_EXTENSIONS = {'docx', 'xlsx', 'pptx', 'pdf', 'txt', 'md', 'csv', 'xls', 'doc', 'html', 'htm'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def validate_file_size(file_stream):
        """Validate whether file size exceeds limit"""
        MAX_FILE_SIZE =current_app.config['MAX_FILE_SIZE'] #10 * 1024 * 1024  # 10MB
        file_stream.seek(0, os.SEEK_END)
        file_size = file_stream.tell()
        file_stream.seek(0)
        return file_size <= MAX_FILE_SIZE

    @staticmethod
    def get_upload_dir():
        """Get upload directory based on configuration"""
        upload_dir = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            datetime.now().strftime('%Y-%m-%d')
        )

        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    def get_upload_dir1111(self):
        """Get upload directory classified by date"""
        # Get project root directory and go up one level to required directory
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        print(base_dir)
        upload_dir = os.path.join(base_dir, 'uploads', datetime.now().strftime('%Y-%m-%d'))

        # Create directory if it doesn't exist
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        return upload_dir

    @staticmethod
    def generate_filename(filename):
        """Generate safe filename (with random suffix to prevent conflicts)"""
        safe_name = secure_filename(filename)
        name_part, ext_part = os.path.splitext(safe_name)
        random_str = uuid.uuid4().hex[:6]  # 6-digit random characters
        return f"{name_part}_{random_str}{ext_part}"

    @staticmethod
    def generate_filename111(filename):
        """Generate safe filename, append random string if file already exists"""
        safe_filename = secure_filename(filename)
        name, ext = os.path.splitext(safe_filename)
        return f"{name}_{str(uuid.uuid4())[:5]}{ext}"

    @staticmethod
    def safe_remove(filepath):
        """Safely delete file"""
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"File {filepath} has been deleted.")
            except Exception as e:
                print(f"Error occurred while deleting file {filepath}: {e}")
        else:
            print(f"File {filepath} does not exist.")

    @staticmethod
    def exists(file_path: str) -> bool:
        """Verify file exists and check path security
        Args:
            file_path: File path, supports relative and absolute paths
        Returns:
            bool: Whether file exists and path is valid
        """
        try:
            # Normalize path, prevent path traversal attacks
            normalized_path = Path(file_path).resolve(strict=False)

            # Verify path is within allowed directory
            upload_dir = Path(current_app.config['UPLOAD_FOLDER']).resolve()
            if not normalized_path.is_relative_to(upload_dir):
                return False

            return normalized_path.exists() and normalized_path.is_file()

        except Exception as e:
            current_app.logger.error(f"File path validation failed: {str(e)}")
            return False

    @staticmethod
    def get_storage_dir():
        """Get storage directory classified by date"""
        base_dir = Path(current_app.config['STORAGE_FOLDER'])
        storage_dir = base_dir / datetime.now().strftime('%Y-%m-%d')

        if not storage_dir.exists():
            storage_dir.mkdir(parents=True, exist_ok=True)

        return str(storage_dir)

    @staticmethod
    def is_secure_path(file_path: str, base_dir: str) -> bool:
        """Validate whether file path is secure
        Args:
            file_path: File path
            base_dir: Base directory
        Returns:
            bool: Whether path is secure
        """
        try:
            normalized_path = Path(file_path).resolve(strict=False)
            base_dir_path = Path(base_dir).resolve()
            return normalized_path.is_relative_to(base_dir_path)
        except Exception as e:
            current_app.logger.error(f"Path security validation failed: {str(e)}")
            return False

    @staticmethod
    def exists111xin(file_path: str, base_dir: str) -> bool:
        """Verify file exists and check path security
        Args:
            file_path: File path
            base_dir: Base directory
        Returns:
            bool: Whether file exists and path is valid
        """
        if not FileManager.is_secure_path(file_path, base_dir):
            return False

        normalized_path = Path(file_path).resolve(strict=False)
        return normalized_path.exists() and normalized_path.is_file()

    @staticmethod
    def calculate_md5(file_path):
        """Calculate MD5 value of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


def get_upload_dir():
    """Get upload directory classified by date"""
    # Get project root directory and go up one level to required directory
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    print(base_dir)
    upload_dir = os.path.join(base_dir, 'uploads', datetime.now().strftime('%Y-%m-%d'))

    # Create directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return upload_dir
