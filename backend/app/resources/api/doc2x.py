import os
from datetime import datetime
from flask_restful import Resource
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from pathlib import Path

from app import APIResponse, db
from app.models import Customer
from app.models.translate import Translate
from app.utils.doc2x import Doc2XService


# Translation start API
class Doc2XTranslateStartResource(Resource):
    @jwt_required()
    def post(self):
        data = request.form
        required_fields = [
            'server', 'doc2x_secret_key', 'lang', 'file_name'
        ]

        # Parameter validation
        if not all(field in data for field in required_fields):
            return APIResponse.error("缺少必要参数", 400)
        customer = Customer.query.get(get_jwt_identity())
        if customer.status == 'disabled':
            return APIResponse.error("用户状态异常", 403)

        # 1. Validate translation record
        translate = Translate.query.filter_by(
            id=data.get('translate_id'),
            customer_id=get_jwt_identity()
        ).first_or_404()

        # if not Path(translate.origin_filepath).exists():
        #     return APIResponse.error("资源不存在", 404)

        # 2. Validate file type
        if not translate.origin_filename.lower().endswith('.pdf'):
            return APIResponse.error("doc2x 仅支持PDF文件", 400)
        # 3. Update key, server, doc2x_flag and other fields
        translate.doc2x_secret_key = data['doc2x_secret_key']
        translate.lang = '中文'  # data['lang']
        translate.origin_lang = data.get('origin_lang', '')
        translate.target_filepath = ''
        translate.doc2x_flag = 'Y'
        translate.server = data.get('server', 'doc2x')
        translate.start_at = datetime.now()

        if not data['doc2x_secret_key']:
            return APIResponse.error("未设置doc2x的Key！", 400)

        try:
            # 4. Start doc2x parsing
            uid = Doc2XService.start_task(
                api_key=data['doc2x_secret_key'],
                file_path=translate.origin_filepath
            )

            # 5. Update translation record
            translate.uuid = uid  # Update to UID returned by doc2x
            translate.status = "process"
            translate.model = "doc2x"
            customer.storage += int(data.get('size', 0))
            translate.size = data.get('size', 0)  # Update file size
            db.session.commit()

            return APIResponse.success({
                "task_id": translate.id,
                "uid": uid,
                "uuid": uid,
            })

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"doc2x translation failed: {str(e)}")
            translate.status = "failed"
            db.session.commit()
            return APIResponse.error(f"doc2x翻译失败: {str(e)}", 500)


# Status query API
class Doc2XTranslateStatusResource(Resource):
    @jwt_required()
    def post(self):
        data = request.form
        translate_id = data.get('translate_id')

        if not translate_id:
            return APIResponse.error("缺少translate_id参数", 400)

        # 1. Validate translation record
        translate = Translate.query.filter_by(
            id=translate_id,
            customer_id=get_jwt_identity()  # User isolation
        ).first_or_404()

        if translate.model != "doc2x":
            return APIResponse.error("非doc2x翻译任务", 400)

        try:
            # 2. Check parsing status
            status_data = Doc2XService.check_parse_status(
                api_key=translate.doc2x_secret_key,
                uid=translate.uuid
            )

            # 3. Construct response data (including all possible statuses)
            response_data = {
                "status": status_data["status"],  # doc2x original status
                "progress": status_data.get("progress", 0),
                "translate_status": translate.status  # Local task status
            }

            # 4. Handle different statuses
            current_status = status_data["status"]
            if current_status == "processing":
                # Processing status
                response_data["message"] = "任务处理中，请稍后刷新"

            elif current_status == "success":
                if not translate.target_filepath:
                    save_dir = self._get_save_dir()
                    filename = os.path.splitext(translate.origin_filename)[0]
                    save_filename = f"{filename}_doc2x.docx"
                    save_path = os.path.join(save_dir, save_filename)

                    # Clean up existing file
                    if os.path.exists(save_path):
                        os.remove(save_path)

                    # Trigger export and download
                    if not Doc2XService.trigger_export(
                            api_key=translate.doc2x_secret_key,
                            uid=translate.uuid,
                            filename=filename
                    ):
                        raise Exception("导出触发失败")

                    # Get download URL
                    download_url = Doc2XService.check_export_status(
                        api_key=translate.doc2x_secret_key,
                        uid=translate.uuid
                    )

                    Doc2XService.download_file(download_url, save_path)

                    # Update record
                    translate.target_filepath = save_path
                    translate.status = "done"
                    translate.process = 100
                    translate.updated_at = datetime.now()
                    translate.end_at = datetime.now()
                    db.session.commit()

                response_data.update({
                    "result_path": translate.target_filepath if translate.status == 'done' else None,
                    "message": "pdf翻译已完成！",
                    "progress": 100,
                    "translate_status": translate.status,
                    "status": translate.status

                })

            elif current_status == "failed":
                translate.status = "failed"
                db.session.commit()
                response_data.update({
                    "error": status_data.get("detail", "pdf翻译失败~"),
                    "message": "任务处理失败"
                })

            return APIResponse.success(response_data)

        except Exception as e:
            current_app.logger.error(f"Status query failed: {str(e)}")
            translate.status = "failed"
            db.session.commit()
            return APIResponse.error(f"状态查询失败: {str(e)}", 500)

    @staticmethod
    def _get_save_dir1():
        """Generate cross-platform save directory (reuse existing logic)"""
        base_dir = Path(current_app.root_path).parent.absolute()
        save_dir = base_dir / "storage" / "doc2x_results"
        save_dir.mkdir(parents=True, exist_ok=True)
        return str(save_dir)

    @staticmethod
    def _get_save_dir():
        """Generate save directory classified by date (cross-platform compatible)"""
        # Get base storage directory
        base_dir = Path(current_app.root_path).parent.absolute()

        # Create date subdirectory (format: YYYY-MM-DD)
        date_str = datetime.now().strftime('%Y-%m-%d')
        save_dir = base_dir / "storage" / "doc2x_results" / date_str

        # Ensure directory exists (recursively create)
        save_dir.mkdir(parents=True, exist_ok=True)

        return str(save_dir)

