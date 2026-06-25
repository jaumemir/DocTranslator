# resources/admin/setting.py
import os
import shutil
from flask import request, current_app
from flask_restful import Resource

from app import db
from app.models import Setting
from app.utils.response import APIResponse
from app.utils.validators import validate_id_list


class AdminSettingNoticeResource(Resource):
    def get(self):
        """Get notification settings"""
        setting = Setting.query.filter_by(alias='notice_setting').first()
        if not setting:
            return APIResponse.success(data={'users': []})
        return APIResponse.success(data={'users': eval(setting.value)})

    def post(self):
        """Update notification settings"""
        data = request.json
        users = validate_id_list(data.get('users'))

        setting = Setting.query.filter_by(alias='notice_setting').first()
        if not setting:
            setting = Setting(alias='notice_setting')

        setting.value = str(users)
        setting.serialized = True
        db.session.add(setting)
        db.session.commit()
        return APIResponse.success(message='Notification settings updated')


class AdminSettingApiResource(Resource):
    def get(self):
        """Get API configuration"""
        settings = Setting.query.filter(Setting.group == 'api_setting').all()
        data = {
            'api_url': settings[0].value,
            'api_key': settings[1].value,
            'models': settings[2].value,
            'default_model': settings[3].value,
            'default_backup': settings[4].value
        }
        return APIResponse.success(data=data)

    def post(self):
        """Update API configuration"""
        data = request.json
        required_fields = ['api_url', 'api_key', 'models', 'default_model', 'default_backup']
        if not all(field in data for field in required_fields):
            return APIResponse.error('Missing required parameters', 400)

        for alias, value in data.items():
            setting = Setting.query.filter_by(alias=alias).first()
            if not setting:
                setting = Setting(alias=alias, group='api_setting')
            setting.value = value
            db.session.add(setting)
        db.session.commit()
        return APIResponse.success(message='API configuration updated')


class AdminInfoSettingOtherResource(Resource):
    def get(self):
        """Get other settings"""
        settings = Setting.query.filter(Setting.group == 'other_setting').all()
        data = {
            'prompt': settings[0].value,
            'threads': int(settings[1].value),
            'email_limit': settings[2].value
        }
        return APIResponse.success(data=data)


class AdminEditSettingOtherResource(Resource):
    def post(self):
        """Update other settings"""
        data = request.json
        required_fields = ['prompt', 'threads']
        if not all(field in data for field in required_fields):
            return APIResponse.error('Missing required parameters', 400)

        for alias, value in data.items():
            setting = Setting.query.filter_by(alias=alias).first()
            if not setting:
                setting = Setting(alias=alias, group='other_setting')
            setting.value = value
            db.session.add(setting)
        db.session.commit()
        return APIResponse.success(message='Other settings updated')


class AdminSettingSiteResource(Resource):
    def get(self):
        """Get site settings"""
        setting = Setting.query.filter_by(alias='version').first()
        if not setting:
            return APIResponse.success(data={'version': 'community'})
        return APIResponse.success(data={'version': setting.value})

    def post(self):
        """Update site version"""
        version = request.json.get('version')
        if not version or version not in ['business', 'community']:
            return APIResponse.error('Invalid version', 400)

        setting = Setting.query.filter_by(alias='version').first()
        if not setting:
            setting = Setting(alias='version', group='site_setting')
        setting.value = version
        db.session.add(setting)
        db.session.commit()
        return APIResponse.success(message='Site version updated')


# ---- System Storage Settings -----
# Get system storage file list
class SystemStorageResource(Resource):
    def get(self):
        """Get file list"""
        try:
            base_dir = os.path.dirname(current_app.root_path)
            storage_path = os.path.join(base_dir, 'storage')

            if not os.path.exists(storage_path):
                return APIResponse.not_found("Storage directory does not exist")

            result = {}

            for category in os.listdir(storage_path):
                category_path = os.path.join(storage_path, category)
                if not os.path.isdir(category_path):
                    continue

                category_data = {"size": 0, "dates": {}}

                for date_dir in os.listdir(category_path):
                    date_path = os.path.join(category_path, date_dir)
                    if not os.path.isdir(date_path):
                        continue

                    date_data = {"size": 0, "files": []}

                    # Keep native system path format
                    for root, _, files in os.walk(date_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                size = os.path.getsize(file_path)
                                date_data["files"].append({
                                    "path": file_path,  # Key point: keep native path
                                    "size": size,
                                    "name": file
                                })
                                date_data["size"] += size
                            except OSError:
                                continue

                    category_data["size"] += date_data["size"]
                    category_data["dates"][date_dir] = date_data

                result[category] = category_data

            return APIResponse.success(data=result)

        except Exception as e:
            current_app.logger.error(f"Failed to get file list: {str(e)}")
            return APIResponse.error("Failed to get file list")

    def delete(self):
        """Delete (with automatic empty directory cleanup)"""
        try:
            req = request.get_json()
            target = req.get("target")
            delete_type = req.get("type")

            if not target or not delete_type:
                return APIResponse.error("Missing required parameters")

            base_dir = os.path.dirname(current_app.root_path)
            target_path = os.path.join(base_dir, 'storage', *target.split('/'))

            # Security check
            storage_path = os.path.join(base_dir, 'storage')
            if not os.path.abspath(target_path).startswith(os.path.abspath(storage_path)):
                return APIResponse.error("Invalid path")

            # Execute deletion
            if delete_type == "file":
                if not os.path.exists(target_path):
                    return APIResponse.not_found("File does not exist")

                # Delete file
                os.remove(target_path)
                self._clean_empty_dirs(target_path)  # Auto cleanup empty directories

            elif delete_type == "date":
                if not os.path.exists(target_path):
                    return APIResponse.not_found("Date directory does not exist")
                shutil.rmtree(target_path)  # Delete entire date directory

            elif delete_type == "category":
                if not os.path.exists(target_path):
                    return APIResponse.not_found("Category directory does not exist")
                shutil.rmtree(target_path)  # Delete entire category directory

            else:
                return APIResponse.error("Invalid operation type")

            return APIResponse.success(message="Deleted successfully")

        except PermissionError:
            return APIResponse.error("Insufficient permissions")
        except Exception as e:
            current_app.logger.error(f"Deletion failed: {str(e)}")
            return APIResponse.error("Deletion operation failed")

    def _clean_empty_dirs(self, file_path):
        """Recursively clean up empty directories"""
        current_dir = os.path.dirname(file_path)
        storage_root = os.path.join(os.path.dirname(current_app.root_path), 'storage')

        # Clean up from file directory upwards to storage root
        while len(current_dir) > len(storage_root):
            try:
                if not os.listdir(current_dir):  # If empty directory
                    os.rmdir(current_dir)
                    current_dir = os.path.dirname(current_dir)  # Continue checking parent directory
                else:
                    break
            except OSError:
                break
