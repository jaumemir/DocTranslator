# resources/to_translate.py
import json
from pathlib import Path
from flask import request, send_file, current_app, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from io import BytesIO
import zipfile
import os
from app import db, Setting
from app.models import Customer
from app.models.translate import Translate
from app.resources.task.translate_service import TranslateEngine
from app.utils.response import APIResponse
from app.utils.check_utils import AIChecker

# Define translation configuration
TRANSLATE_SETTINGS = {
    "models": ["gpt-3.5-turbo", "gpt-4"],
    "default_model": "gpt-3.5-turbo",
    "max_threads": 5,
    "prompt_template": "请将以下内容翻译为{target_lang}"
}

# Baidu Translate language mapping dictionary
LANG_CODE_TO_CHINESE = {
    'zh': '中文',
    'en': '英语',
    'ja': '日语',
    'ko': '韩语',
    'fr': '法语',
    'de': '德语',
    'es': '西班牙语',
    'ru': '俄语',
    'ar': '阿拉伯语',
    'it': '意大利语',

    # Compatible with possible full names
    'chinese': '中文',
    'english': '英语',
    'japanese': '日语',
    'korean': '韩语',
    '中文': '中文',  # Prevent duplicate conversion
    '汉语': '中文'
}


def get_unified_lang_name(lang_code):
    """Return unified Chinese name of language
    """
    # Uniformly convert to lowercase
    lower_code = str(lang_code).lower()
    return LANG_CODE_TO_CHINESE.get(lower_code, lang_code)  # Return original value if not found


class TranslateStartResource(Resource):
    @jwt_required()
    def post(self):
        """Start translation task"""
        data = request.form
        required_fields = [
            'server', 'model', 'lang', 'uuid',
            'prompt', 'threads', 'file_name'
        ]

        # Parameter validation
        if not all(field in data for field in required_fields):
            return APIResponse.error("缺少必要参数", 400)

        # Validate OpenAI configuration
        if data['server'] == 'openai' and not all(k in data for k in ['api_url', 'api_key']):
            return APIResponse.error("AI翻译需要API地址和密钥", 400)

        # if data['server'] == 'openai':
        #     return APIResponse.error("Doc2x服务需要密钥", 400)
        # elif data['server'] == 'baidu':
        #     return APIResponse.error("Doc2x服务需要密钥", 400)
        try:
            # Get user information
            user_id = get_jwt_identity()
            customer = Customer.query.get(user_id)
            # # Check if user is VIP member, VIP members don't need to fill in API key
            # if customer.level != 'vip' and not data['api_key']:
            #     return APIResponse.error("缺少key !", 400)
            if customer.status == 'disabled':
                return APIResponse.error("用户状态异常", 403)

            # Generate absolute path (cross-platform compatible)
            def get_absolute_storage_path(filename):
                # Get parent directory of project root (assuming storage directory is at same level as project directory)
                base_dir = Path(current_app.root_path).parent.absolute()
                # Create subdirectory by date (e.g., storage/translate/2024-01-20)
                date_str = datetime.now().strftime('%Y-%m-%d')
                # Create target directory (if it doesn't exist)
                target_dir = base_dir / "storage" / "translate" / date_str
                target_dir.mkdir(parents=True, exist_ok=True)
                # Return absolute path (keep original filename)
                return str(target_dir / filename)

            origin_filename = data['file_name']

            # Generate absolute path for translation result
            target_abs_path = get_absolute_storage_path(origin_filename)

            # Get translation type (take last type value)
            translate_type = data.get('type[2]', 'trans_all_only_inherit')

            # Query or create translation record
            translate = Translate.query.filter_by(uuid=data['uuid']).first()
            if not translate:
                return APIResponse.error("未找到对应的翻译记录", 404)

            # Get api_setting group configuration from system
            api_settings = Setting.query.filter(
                Setting.group == 'api_setting',  # Only query api_setting group
                Setting.deleted_flag == 'N'
            ).all()
            # Convert to dictionary
            translate_settings = {}
            for setting in api_settings:
                translate_settings[setting.alias] = setting.value
            # Update translation record
            translate.server = data.get('server', 'openai')
            translate.origin_filename = data['file_name']
            translate.target_filepath = target_abs_path
            translate.model = data['model']
            translate.app_key = data.get('app_key', None)
            translate.app_id = data.get('app_id', None)
            translate.backup_model = data['backup_model']
            translate.type = translate_type
            translate.prompt = data['prompt']
            translate.threads = int(data['threads'])
            # VIP users use system api_url and api_key
            if customer.level == 'vip':
                translate.api_url = translate_settings.get('api_url', '').strip()
                translate.api_key = translate_settings.get('api_key', '').strip()
            else:
                translate.api_url = data.get('api_url', '')
                translate.api_key = data.get('api_key', '')
            translate.backup_model = data.get('backup_model', '')
            translate.origin_lang = data.get('origin_lang', '')
            translate.size = data.get('size', 0)  # Update file size
            # Get comparison_id and convert to integer
            comparison_id = data.get('comparison_id', 0)  # Default value is '0'
            translate.comparison_id = int(comparison_id) if comparison_id else None
            prompt_id = data.get('prompt_id', '0')
            translate.prompt_id = int(prompt_id) if prompt_id else None
            translate.doc2x_flag = data.get('doc2x_flag', 'N')
            translate.doc2x_secret_key = data.get('doc2x_secret_key', '')
            if data['server'] == 'baidu':
                translate.lang = data['to_lang']
                translate.comparison_id = 1 if data.get('needIntervene', False) else None  # Use terminology library
            else:
                translate.lang = data['lang']
            # Use UTC time and format
            # current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
            # translate.created_at = current_time
            # Save to database
            # Update user's used storage space
            customer.storage += int(translate.size)
            db.session.commit()
            # with current_app.app_context():  # Ensure running in application context
            # Start translation engine, pass current_app
            TranslateEngine(translate.id).execute()

            return APIResponse.success({
                "task_id": translate.id,
                "uuid": translate.uuid,
                "target_path": target_abs_path
            })

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Translation task startup failed: {str(e)}", exc_info=True)
            return APIResponse.error("任务启动失败", 500)


# Get translation record list
class TranslateListResource(Resource):
    @jwt_required()
    def get(self):
        """Get translation record list"""
        # Get query parameters
        page = request.args.get('page', '1')
        limit = request.args.get('limit', '100')
        status_filter = request.args.get('status')
        # Convert string parameters to integers
        try:
            page = int(page)
            limit = int(limit)
        except ValueError:
            return APIResponse.error("Invalid page or limit value"), 400
        # Build query conditions
        query = Translate.query.filter_by(
            customer_id=get_jwt_identity(),
            deleted_flag='N'
        )
        # Sort
        query = query.order_by(Translate.created_at.desc())
        # Check if status_filter is a valid value
        if status_filter:
            valid_statuses = {'none', 'process', 'done', 'failed'}
            if status_filter not in valid_statuses:
                return APIResponse.error(f"Invalid status value: {status_filter}"), 400
            query = query.filter_by(status=status_filter)

        # Execute paginated query
        pagination = query.paginate(page=page, per_page=limit, error_out=False)

        # Process each record
        data = []
        for t in pagination.items:
            # Calculate time spent (based on created_at and end_at)
            # Fix time calculation (force display minutes:seconds format)
            if t.start_at and t.end_at:
                spend_time = t.end_at - t.start_at
                total_seconds = spend_time.total_seconds()

                # Force minutes:seconds format (display 0 minutes xx seconds even if less than 1 minute)
                minutes = int(total_seconds // 60)
                seconds = int(total_seconds % 60)
                spend_time_str = f"{minutes}分{seconds}秒"
            else:
                spend_time_str = "--"

            # Get status Chinese description
            status_name_map = {
                'none': '未开始',
                'process': '进行中',
                'done': '已完成',
                'failed': '失败'
            }
            status_name = status_name_map.get(t.status, '未知状态')

            # Get file type
            file_type = self.get_file_type(t.origin_filename)

            # Format completion time (accurate to seconds)
            end_at_str = t.end_at.strftime('%Y-%m-%d %H:%M:%S') if t.end_at else "--"

            data.append({
                'id': t.id,
                'file_type': file_type,
                'origin_filename': t.origin_filename,
                'status': t.status,
                'status_name': status_name,
                'process': float(t.process),  # Convert Decimal to float
                'spend_time': spend_time_str,  # Time spent
                'end_at': end_at_str,  # Completion time
                'start_at': t.start_at.strftime('%Y-%m-%d %H:%M:%S') if t.start_at else "--",
                # Start time
                'lang': get_unified_lang_name(t.lang),  # Standard output language Chinese name
                'target_filepath': t.target_filepath,
                'uuid': t.uuid,
                'server': t.server,
            })

        # Return response data
        return APIResponse.success({
            'data': data,
            'total': pagination.total,
            'current_page': pagination.page
        })

    @staticmethod
    def get_file_type(filename):
        """Get file type based on filename"""
        if not filename:
            return "未知"
        ext = filename.split('.')[-1].lower()
        if ext in {'docx', 'doc'}:
            return "Word"
        elif ext in {'xlsx', 'xls'}:
            return "Excel"
        elif ext == 'pptx':
            return "PPT"
        elif ext == 'pdf':
            return "PDF"
        elif ext in {'txt', 'md'}:
            return "文本"
        elif ext in {'html', 'htm'}:
            return "HTML"
        else:
            return "其他"


# Get translation settings
class TranslateSettingResource(Resource):
    @jwt_required()
    def get(self):
        """Get translation configuration (dynamically loaded from database)"""
        try:
            # Get translation configuration from database
            settings = self._load_settings_from_db()
            return APIResponse.success(settings)
        except Exception as e:
            return APIResponse.error(f"获取配置失败: {str(e)}", 500)

    @staticmethod
    def _load_settings_from_db():
        """
        Load translation configuration from database
        :return: Translation configuration dictionary
        """
        # Query translation-related configurations (api_setting and other_setting groups)
        settings = Setting.query.filter(
            Setting.group.in_(['api_setting', 'other_setting']),
            Setting.deleted_flag == 'N'
        ).all()

        # Convert to configuration dictionary
        config = {}
        for setting in settings:
            # If serialized is True, deserialize value
            value = json.loads(setting.value) if setting.serialized else setting.value

            # Store configuration based on alias
            if setting.alias == 'models':
                config['models'] = value.split(',') if isinstance(value, str) else value
            elif setting.alias == 'default_model':
                config['default_model'] = value
            elif setting.alias == 'default_backup':
                config['default_backup'] = value
            elif setting.alias == 'api_url':
                config['api_url'] = value
            elif setting.alias == 'api_key':
                config['api_key'] = "sk-xxx"  # value
            elif setting.alias == 'prompt':
                config['prompt_template'] = value
            elif setting.alias == 'threads':
                config['max_threads'] = int(value) if value.isdigit() else 10  # Default 10 threads

        # Set default values (if there is no related configuration in the database)
        config.setdefault('models', ['gpt-3.5-turbo', 'gpt-4'])
        config.setdefault('default_model', 'gpt-3.5-turbo')
        config.setdefault('default_backup', 'gpt-3.5-turbo')
        config.setdefault('api_url', 'https://api.ezworkapi.top/v1')
        config.setdefault('api_key', '')
        config.setdefault('prompt_template', '请将以下内容翻译为{target_lang}')
        config.setdefault('max_threads', 5)

        return config


class TranslateProcessResource(Resource):
    @jwt_required()
    def post(self):
        """Query translation progress"""
        uuid = request.form.get('uuid')
        translate = Translate.query.filter_by(
            uuid=uuid,
            customer_id=get_jwt_identity()
        ).first_or_404()

        return APIResponse.success({
            'status': translate.status,
            'progress': float(translate.process),
        })


class TranslateDeleteResource(Resource):
    @jwt_required()
    def delete(self, id):
        """Soft delete translation record"""
        # Query translation record
        customer_id = get_jwt_identity()
        translate = Translate.query.filter_by(
            id=id,
            customer_id=customer_id
        ).first_or_404()
        customer = Customer.query.get(customer_id)
        # Update deleted_flag to 'Y'
        translate.deleted_flag = 'Y'
        # Update user storage space
        customer.storage -= translate.size
        db.session.commit()

        return APIResponse.success(message='删除成功!')


class TranslateDownloadResource(Resource):
    # @jwt_required()
    def get(self, id):
        """Download single translation result file by ID"""
        # Query translation record
        translate = Translate.query.filter_by(
            id=id,
            # customer_id=get_jwt_identity()
        ).first_or_404()

        # Ensure file exists
        if not translate.target_filepath or not os.path.exists(translate.target_filepath):
            return APIResponse.error('文件不存在', 404)

        # Return file
        response = make_response(send_file(
            translate.target_filepath,
            as_attachment=True,
            download_name=os.path.basename(translate.target_filepath)
        ))

        # Disable caching
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response


class TranslateDownloadAllResource(Resource):
    @jwt_required()
    def get(self):
        """Batch download all translation result files"""
        # Query all translation records for current user
        records = Translate.query.filter_by(
            customer_id=get_jwt_identity(),
            deleted_flag='N'  # Only download non-deleted records
        ).all()

        # Generate in-memory ZIP file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for record in records:
                if record.target_filepath and os.path.exists(record.target_filepath):
                    # Add file to ZIP
                    zip_file.write(
                        record.target_filepath,
                        os.path.basename(record.target_filepath)
                    )

        # Reset buffer pointer
        zip_buffer.seek(0)

        # Return ZIP file
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"translations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )


class OpenAICheckResource(Resource):
    @jwt_required()
    def post(self):
        """OpenAI API connection check"""
        data = request.form
        required = ['api_url', 'api_key', 'model']
        if not all(k in data for k in required):
            return APIResponse.error('缺少必要参数', 400)

        is_valid, msg = AIChecker.check_openai_connection(
            data['api_url'],
            data['api_key'],
            data['model']
        )

        return APIResponse.success({'valid': is_valid, 'message': msg})


class PDFCheckResource(Resource):
    @jwt_required()
    def post(self):
        """PDF scanned document detection"""
        if 'file' not in request.files:
            return APIResponse.error('请选择PDF文件', 400)

        file = request.files['file']
        if not file.filename.lower().endswith('.pdf'):
            return APIResponse.error('仅支持PDF文件', 400)

        try:
            file_stream = file.stream
            is_scanned = AIChecker.check_pdf_scanned(file_stream)
            return APIResponse.success({'scanned': is_scanned})
        except Exception as e:
            return APIResponse.error(f'检测失败: {str(e)}', 500)


class TranslateTestResource(Resource):
    def get(self):
        """Test translation service"""
        return APIResponse.success(message="测试服务正常")


class TranslateDeleteAllResource(Resource):
    @jwt_required()
    def delete(self):
        """Delete all user translation records and update storage space"""
        customer_id = get_jwt_identity()

        # First query the records to be deleted and their total size
        records_to_delete = Translate.query.filter_by(
            customer_id=customer_id,
            deleted_flag='N'
        ).all()

        total_size = sum(record.size for record in records_to_delete)

        # Execute batch deletion
        Translate.query.filter_by(
            customer_id=customer_id,
            deleted_flag='N'
        ).delete()

        # Update user storage space
        customer = Customer.query.get(customer_id)
        if customer:
            customer.storage = max(0, customer.storage - total_size)

        db.session.commit()
        return APIResponse.success(message="全部文件删除成功!")


class TranslateFinishCountResource(Resource):
    @jwt_required()
    def get(self):
        """Get count of completed translations"""
        count = Translate.query.filter_by(
            customer_id=get_jwt_identity(),
            status='done',
            deleted_flag='N'
        ).count()
        return APIResponse.success({'total': count})


class Doc2xCheckResource(Resource):
    def post(self):
        """Check Doc2x API"""
        secret_key = request.json.get('doc2x_secret_key')
        # Simulated validation logic, actual needs to connect to Doc2x service
        if secret_key == "valid_key_123":  # Example validation
            return APIResponse.success(message="接口正常")
        return APIResponse.error("无效密钥", 400)
