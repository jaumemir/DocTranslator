import os
import requests
import time
from flask import current_app


class Doc2XService:
    BASE_URL = "https://v2.doc2x.noedgeai.com/api/v2"

    @staticmethod
    def _make_request(api_key, method, endpoint, data=None, files=None):
        """Unified request method"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if method != "upload" else {
            "Authorization": f"Bearer {api_key}"
        }

        url = f"{Doc2XService.BASE_URL}/{endpoint}"
        try:
            if method == "upload":
                response = requests.post(url, headers=headers, data=files)
            else:
                response = requests.request(
                    method.lower(),
                    url,
                    headers=headers,
                    json=data if data else None
                )

            result = response.json()
            if result.get("code") != "success":
                raise Exception(result.get("msg", "API 请求失败"))
            return result["data"]
        except Exception as e:
            current_app.logger.error(f"doc2x request failed: {str(e)}")
            raise

    @staticmethod
    def start_task(api_key: str, file_path: str) -> str:
        """Phase 1: Start task (parse/pdf)"""
        with open(file_path, 'rb') as f:
            return Doc2XService._make_request(
                api_key,
                "upload",
                "parse/pdf",
                files=f
            )["uid"]

    @staticmethod
    def check_parse_status(api_key: str, uid: str) -> dict:
        """Check parsing status"""
        data = Doc2XService._make_request(
            api_key,
            "GET",
            f"parse/status?uid={uid}"
        )

        # Ensure all possible statuses returned by doc2x are included
        if "status" not in data:
            raise Exception("无效的API响应：缺少status字段")

        return {
            "status": data["status"],  # processing/success/failed
            "progress": data.get("progress", 0),
            "detail": data.get("detail", "")
        }

    @staticmethod
    def trigger_export(api_key: str, uid: str, filename: str) -> bool:
        """Trigger export (return whether trigger was successful)"""
        data = {
            "uid": uid,
            "to": "docx",  # Export as Word document
            "formula_mode": "normal",
            "filename": f"{filename}.docx"  # Ensure extension is correct
        }
        result = Doc2XService._make_request(
            api_key,
            "POST",
            "convert/parse",
            data=data
        )
        return result.get("status") == "processing"

    @staticmethod
    def download_file(url: str, save_path: str) -> bool:
        """Download file and verify integrity"""
        try:
            # Create temporary file
            temp_path = f"{save_path}.tmp"

            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(temp_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            # Verify file size
            if os.path.getsize(temp_path) == 0:
                raise Exception("下载文件为空")

            # Rename to official file
            os.rename(temp_path, save_path)
            return True

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            current_app.logger.error(f"File download failed: {str(e)}")
            raise

    @staticmethod
    def check_export_status(api_key: str, uid: str, timeout=300) -> str:
        """Phase 4: Poll export result (convert/parse/result)"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            data = Doc2XService._make_request(
                api_key,
                "GET",
                f"convert/parse/result?uid={uid}"
            )
            if data["status"] == "success":
                return data["url"]
            elif data["status"] == "failed":
                raise Exception("导出任务失败")
            time.sleep(2)  # Reasonable polling interval
        raise TimeoutError("导出结果等待超时")
