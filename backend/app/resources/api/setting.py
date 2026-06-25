# resources/system.py
from flask_restful import Resource
from app.utils.response import APIResponse
from flask import current_app


class SystemVersionResource(Resource):
    def get(self):
        """Get system version information[^1]"""
        return APIResponse.success({
            'version': current_app.config['SYSTEM_VERSION'],
            'message': 'success'
        })


class SystemSettingsResource(Resource):
    def get(self):
        """Get full system configuration[^2]"""
        return APIResponse.success({
            'site_setting': {
                'version': current_app.config['SYSTEM_VERSION'],
                'site_name': current_app.config['SITE_NAME']
            },
            'api_setting': {
                'api_url': current_app.config['API_URL'],
                'models': current_app.config['TRANSLATE_MODELS']
            },
            'message': 'success'
        })
