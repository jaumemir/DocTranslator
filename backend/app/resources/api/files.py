# resources/file.py
import hashlib
import uuid
import os
from app import db
from app.models.customer import Customer
from app.models.translate import Translate
from app.utils.response import APIResponse
from pathlib import Path
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, current_app
from datetime import datetime


class FileUploadResource(Resource):
    @jwt_required()
    def post(self):
        """File upload endpoint"""
        # Validate file exists
        if 'file' not in request.files:
            return APIResponse.error('未选择文件', 400)
        file = request.files['file']

        # Validate filename validity
        if file.filename == '':
            return APIResponse.error('无效文件名', 400)

        # Validate file type
        if not self.allowed_file(file.filename):
            return APIResponse.error(
                f"仅支持以下格式：{', '.join(current_app.config['ALLOWED_EXTENSIONS'])}", 400)

        # Validate file size
        if not self.validate_file_size(file.stream):
            return APIResponse.error(
                f"文件大小超过{current_app.config['MAX_FILE_SIZE'] // (1024 * 1024)}MB", 400)

        # Get user storage information
        user_id = get_jwt_identity()
        customer = Customer.query.get(user_id)
        file_size = request.content_length  # Use actual content length

        # Validate storage space (current_app.config['MAX_USER_STORAGE'])
        if customer.storage + file_size > customer.total_storage:
            return APIResponse.error('用户存储空间不足', 403)

        try:
            # Generate storage path
            save_dir = self.get_upload_dir()
            filename = file.filename  # Use original filename directly
            save_path = os.path.join(save_dir, filename)

            # Check path safety
            if not self.is_safe_path(save_dir, save_path):
                return APIResponse.error('文件名包含非法字符', 400)

            # Save file
            file.save(save_path)
            # Update user storage space
            customer.storage += file_size
            db.session.commit()
            # Generate UUID
            file_uuid = str(uuid.uuid4())
            # Calculate file MD5
            file_md5 = self.calculate_md5(save_path)

            # Create translation record
            translate_record = Translate(
                translate_no=f"TRANS{datetime.now().strftime('%Y%m%d%H%M%S')}",
                uuid=file_uuid,
                customer_id=user_id,
                origin_filename=filename,
                origin_filepath=os.path.abspath(save_path),  # Use absolute path
                target_filepath='',  # Target file path is empty initially
                status='none',  # Initial status is none
                origin_filesize=file_size,
                size=file_size,
                md5=file_md5,
                created_at=datetime.utcnow()
            )
            db.session.add(translate_record)
            db.session.commit()

            # Return response with filename, UUID, and translation record ID
            return APIResponse.success({
                'filename': filename,
                'uuid': file_uuid,
                'translate_id': translate_record.id,
                'save_path': os.path.abspath(save_path)  # Return absolute path
            })

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"File upload failed: {str(e)}")
            return APIResponse.error('文件上传失败', 500)

    @staticmethod
    def allowed_file(filename):
        # """Validate if file type is allowed"""# PDF not supported yet 'pdf',
        ALLOWED_EXTENSIONS = {'docx', 'xlsx','pdf', 'pptx', 'txt', 'md', 'csv', 'xls', 'doc', 'html', 'htm'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def validate_file_size(file_stream):
        """Validate if file size exceeds limit"""
        MAX_FILE_SIZE = current_app.config['MAX_FILE_SIZE']# 30 * 1024 * 1024  # 30MB
        file_stream.seek(0, os.SEEK_END)
        file_size = file_stream.tell()
        file_stream.seek(0)
        return file_size <= MAX_FILE_SIZE

    @staticmethod
    def get_upload_dir():
        """Get upload directory organized by date"""
        # Get upload root directory
        base_dir = Path(current_app.config['UPLOAD_BASE_DIR'])
        upload_dir = base_dir / 'uploads' / datetime.now().strftime('%Y-%m-%d')

        # Create directory if it doesn't exist
        if not upload_dir.exists():
            upload_dir.mkdir(parents=True, exist_ok=True)

        return str(upload_dir)

    @staticmethod
    def calculate_md5(file_path):
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def is_safe_path(base_dir, file_path):
        """Check if file path is safe to prevent path traversal attacks"""
        base_dir = Path(base_dir).resolve()
        file_path = Path(file_path).resolve()
        return file_path.is_relative_to(base_dir)


class FileDeleteResource11(Resource):
    @jwt_required()
    def post(self):
        """File deletion endpoint[^6]"""
        data = request.form
        if 'uuid' not in data:
            return APIResponse.error('缺少必要参数', 400)

        try:
            # Query file record
            translate = Translate.query.filter_by(
                uuid=data['uuid'],
                customer_id=get_jwt_identity(),
                deleted_flag='N'
            ).first_or_404()

            # Get full file path
            base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            uploads_dir = os.path.join(base_dir, 'uploads')
            file_path = os.path.join(uploads_dir, translate.origin_filepath)

            # Delete physical file
            if os.path.exists(file_path):
                os.remove(file_path)

                # Update user storage space
                customer = Customer.query.get(get_jwt_identity())
                customer.storage -= translate.origin_filesize

            # Delete database record (hard delete)
            db.session.delete(translate)  # Hard delete
            db.session.commit()

            return APIResponse.success(message='文件删除成功')

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"File deletion failed: {str(e)}")
            return APIResponse.error('文件删除失败', 500)


class FileDeleteResource(Resource):
    @jwt_required()
    def post(self):
        """File deletion endpoint[^1]"""
        data = request.form
        if 'uuid' not in data:
            return APIResponse.error('缺少必要参数', 400)

        try:
            # Query translation record by UUID
            translate_record = Translate.query.filter_by(uuid=data['uuid']).first()
            if not translate_record:
                return APIResponse.error('文件记录不存在', 404)

            # Get file absolute path
            file_path = translate_record.origin_filepath

            # Delete physical file
            if os.path.exists(file_path):
                os.remove(file_path)
                # Update user storage space
                customer = Customer.query.get(get_jwt_identity())
                customer.storage -= translate_record.origin_filesize
            else:
                current_app.logger.warning(f"File does not exist: {file_path}")

            # Delete database record
            db.session.delete(translate_record)
            db.session.commit()

            return APIResponse.success(message='文件删除成功')

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"File deletion failed: {str(e)}")
            return APIResponse.error('文件删除失败', 500)
