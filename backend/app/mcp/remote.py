import os
import logging
import asyncio
from typing import Optional
from contextlib import contextmanager
from fastmcp import FastMCP
from fastmcp.dependencies import CurrentAccessToken
from fastmcp.server.auth import AccessToken

from app.mcp.auth import McpApiKeyAuthProvider

logger = logging.getLogger(__name__)

_flask_app = None


def set_flask_app(app):
    global _flask_app
    _flask_app = app


def get_flask_app():
    if _flask_app:
        return _flask_app
    try:
        from flask import current_app
        return current_app._get_current_object()
    except RuntimeError:
        return None


@contextmanager
def flask_app_context():
    app = get_flask_app()
    if app is None:
        raise RuntimeError("Flask app not available")
    with app.app_context():
        yield app


def _run_sync(func):
    def wrapper(*args, **kwargs):
        with flask_app_context():
            return func(*args, **kwargs)
    return wrapper


async def _run_in_thread(func, *args):
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)
    except Exception as e:
        logger.error(f"MCP tool execution failed: {e}", exc_info=True)
        return {'error': str(e)}


user_mcp = FastMCP(
    "DocTranslator-User",
    stateless_http=True,
    auth=McpApiKeyAuthProvider(scope='user'),
    instructions=(
        "DocTranslator 文档翻译服务。"
        "你可以翻译文档、查询翻译进度、管理术语库和提示词模板。"
        "api_url/api_key/model 等翻译配置由 MCP 密钥自动提供，无需每次传入。"
    ),
)


@user_mcp.tool
async def translate_file(
    file_content: Optional[str] = None,
    file_url: Optional[str] = None,
    file_name: str = "",
    target_lang: str = "",
    origin_lang: str = "",
    translate_type: str = "",
    comparison_id: Optional[int] = None,
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """
    Translate document file.

    File transfer methods (choose one):
    - file_content: File Base64 encoding (recommended, suitable for Claude Desktop and other MCP clients)
    - file_url: File download URL (needs public network access)
    - If neither is provided, file_name is treated as server local absolute path

    api_url/api_key/model/prompt_id/threads and other configs are automatically provided by your MCP key, no need to pass in.

    Args:
        file_content: File content Base64 encoded
        file_url: File download link
        file_name: Original filename (with extension, e.g., report.docx)
        target_lang: Target language (Chinese/English/Japanese/Korean/French/German/Spanish/Russian, etc.), if not filled, uses default language from MCP key config
        origin_lang: Source language (auto-detect if not filled)
        translate_type: Translation type - trans_all_only_inherit(inherit layout, default), trans_all_both_inherit(bilingual inherit layout), trans_text_only(translation only), trans_text_only_new(translation only new layout)
        comparison_id: Terminology ID (can be obtained via list_comparisons)
    """
    from app.mcp.tools import translate_file as do_translate

    if not token:
        return {'error': 'Authentication failed'}

    customer_id = int(token.claims['customer_id'])
    config = token.claims['config']

    @_run_sync
    def _do():
        app = get_flask_app()
        return do_translate(config, customer_id, app,
                            file_content, file_url, file_name,
                            target_lang, origin_lang, translate_type,
                            comparison_id)

    return await _run_in_thread(_do)


@user_mcp.tool
async def query_translate_status(
    task_id: Optional[int] = None,
    uuid: Optional[str] = None,
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """
    Query translation task progress and status.

    Args:
        task_id: Translation task ID (returned when starting translation)
        uuid: Translation task UUID (recommended for queries)
    """
    from app.mcp.tools import query_translate_status as do_query

    if not token:
        return {'error': 'Authentication failed'}

    customer_id = int(token.claims['customer_id'])

    @_run_sync
    def _do():
        return do_query(customer_id, task_id, uuid)

    return await _run_in_thread(_do)


@user_mcp.tool
async def list_translates(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """
    Get translation history list.

    Args:
        page: Page number, default 1
        limit: Items per page, default 20
        status: Filter by status (none/process/done/failed)
    """
    from app.mcp.tools import list_translates as do_list

    if not token:
        return {'error': 'Authentication failed'}

    customer_id = int(token.claims['customer_id'])

    @_run_sync
    def _do():
        return do_list(customer_id, page, limit, status)

    return await _run_in_thread(_do)


@user_mcp.tool
async def download_translate(
    task_id: int,
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """
    Download completed translation file, returns Base64 encoded file content.

    Args:
        task_id: Translation task ID
    """
    from app.mcp.tools import download_translate as do_download

    if not token:
        return {'error': 'Authentication failed'}

    customer_id = int(token.claims['customer_id'])

    @_run_sync
    def _do():
        return do_download(customer_id, task_id)

    return await _run_in_thread(_do)


@user_mcp.tool
async def delete_translate(
    task_id: int,
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """
    Delete translation record.

    Args:
        task_id: Translation task ID
    """
    from app.mcp.tools import delete_translate as do_delete

    if not token:
        return {'error': 'Authentication failed'}

    customer_id = int(token.claims['customer_id'])

    @_run_sync
    def _do():
        return do_delete(customer_id, task_id)

    return await _run_in_thread(_do)


@user_mcp.tool
async def list_comparisons(
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """Get my terminology list. Returns ID, title, source language, target language, and term count for each terminology."""
    from app.mcp.tools import list_comparisons as do_list

    if not token:
        return {'error': 'Authentication failed'}

    customer_id = int(token.claims['customer_id'])

    @_run_sync
    def _do():
        return do_list(customer_id)

    return await _run_in_thread(_do)


@user_mcp.tool
async def list_prompts(
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """Get my prompt template list. Returns ID, title, and sharing status for each template."""
    from app.mcp.tools import list_prompts as do_list

    if not token:
        return {'error': 'Authentication failed'}

    customer_id = int(token.claims['customer_id'])

    @_run_sync
    def _do():
        return do_list(customer_id)

    return await _run_in_thread(_do)


@user_mcp.tool
async def get_account_info(
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """Get current account information, including email, membership level, and storage space usage."""
    from app.mcp.tools import get_account_info as do_get

    if not token:
        return {'error': 'Authentication failed'}

    customer_id = int(token.claims['customer_id'])

    @_run_sync
    def _do():
        return do_get(customer_id)

    return await _run_in_thread(_do)


@user_mcp.tool
async def get_supported_formats() -> dict:
    """Get list of file translation formats supported by the system."""
    from app.mcp.tools import get_supported_formats as do_get
    return do_get()


admin_mcp = FastMCP(
    "DocTranslator-Admin",
    stateless_http=True,
    auth=McpApiKeyAuthProvider(scope='admin'),
    instructions=(
        "DocTranslator admin backend MCP service."
        "You can view translation statistics, manage users, manage translation tasks, and modify system settings."
    ),
)


@admin_mcp.tool
async def get_statistics(
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """Get translation statistics: total count, completed count, processing count, failed count."""
    from app.models.translate import Translate

    @_run_sync
    def _do():
        total = Translate.query.count()
        done_count = Translate.query.filter_by(status='done').count()
        processing_count = Translate.query.filter_by(status='process').count()
        failed_count = Translate.query.filter_by(status='failed').count()
        return {
            'total': total,
            'done_count': done_count,
            'processing_count': processing_count,
            'failed_count': failed_count,
        }

    return await _run_in_thread(_do)


@admin_mcp.tool
async def list_customers(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """
    Get customer list.

    Args:
        page: Page number
        limit: Items per page
        search: Search by email
    """
    from app.models.customer import Customer

    @_run_sync
    def _do():
        query = Customer.query.filter_by(deleted_flag='N')
        if search:
            query = query.filter(Customer.email.ilike(f"%{search}%"))
        pagination = query.paginate(page=page, per_page=limit, error_out=False)

        data = [{
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'level': c.level,
            'status': c.status,
            'storage_mb': round(c.storage / (1024 * 1024), 2),
            'total_storage_mb': round(c.total_storage / (1024 * 1024), 2),
        } for c in pagination.items]

        return {'data': data, 'total': pagination.total}

    return await _run_in_thread(_do)


@admin_mcp.tool
async def update_customer(
    customer_id: int,
    level: Optional[str] = None,
    add_storage_mb: Optional[int] = None,
    status: Optional[str] = None,
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """
    Update customer information.

    Args:
        customer_id: Customer ID
        level: Membership level (common/vip)
        add_storage_mb: Add storage space (MB)
        status: Account status (enabled/disabled)
    """
    from app.extensions import db
    from app.models.customer import Customer

    @_run_sync
    def _do():
        customer = Customer.query.get(customer_id)
        if not customer:
            return {'error': 'Customer does not exist'}

        if level and level in ('common', 'vip'):
            customer.level = level
        if add_storage_mb:
            customer.total_storage += add_storage_mb * 1024 * 1024
        if status and status in ('enabled', 'disabled'):
            customer.status = status

        db.session.commit()
        return {'message': 'Updated successfully'}

    return await _run_in_thread(_do)


@admin_mcp.tool
async def admin_list_translates(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """
    Get all translation records (admin view).

    Args:
        page: Page number
        limit: Items per page
        status: Filter by status
        keyword: Search by filename
    """
    from app.models.translate import Translate
    from app.models.customer import Customer

    @_run_sync
    def _do():
        query = Translate.query.filter_by(deleted_flag='N')
        if status and status in ('none', 'process', 'done', 'failed'):
            query = query.filter_by(status=status)
        if keyword:
            query = query.filter(Translate.origin_filename.ilike(f"%{keyword}%"))

        pagination = query.order_by(Translate.created_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )

        status_map = {'none': 'Not started', 'process': 'In progress', 'done': 'Completed', 'failed': 'Failed'}
        data = []
        for t in pagination.items:
            customer = Customer.query.get(t.customer_id)
            data.append({
                'task_id': t.id,
                'file_name': t.origin_filename,
                'status': t.status,
                'status_name': status_map.get(t.status, 'Unknown'),
                'progress': float(t.process),
                'customer_email': customer.email if customer else 'Unknown',
                'target_lang': t.lang,
                'model': t.model,
            })

        return {'data': data, 'total': pagination.total}

    return await _run_in_thread(_do)


@admin_mcp.tool
async def admin_restart_translate(
    task_id: int,
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """
    Restart failed translation task.

    Args:
        task_id: Translation task ID
    """
    from app.extensions import db
    from app.models.translate import Translate

    @_run_sync
    def _do():
        record = Translate.query.get(task_id)
        if not record:
            return {'error': 'Translation record does not exist'}
        if record.status not in ('failed', 'done'):
            return {'error': f'Current status {record.status} cannot be restarted'}

        record.status = 'none'
        record.start_at = None
        record.end_at = None
        record.failed_reason = None
        db.session.commit()
        return {'message': 'Task has been restarted'}

    return await _run_in_thread(_do)


@admin_mcp.tool
async def admin_delete_translate(
    task_id: int,
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """
    Delete translation record.

    Args:
        task_id: Translation task ID
    """
    from app.extensions import db
    from app.models.translate import Translate

    @_run_sync
    def _do():
        record = Translate.query.get(task_id)
        if not record:
            return {'error': 'Translation record does not exist'}
        db.session.delete(record)
        db.session.commit()
        return {'message': 'Record deleted successfully'}

    return await _run_in_thread(_do)


@admin_mcp.tool
async def get_system_settings(
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """Get system settings: API configuration, default model, thread count, etc."""
    from app.models.setting import Setting

    @_run_sync
    def _do():
        settings = Setting.query.filter(
            Setting.group.in_(['api_setting', 'other_setting']),
            Setting.deleted_flag == 'N'
        ).all()

        result = {}
        for s in settings:
            result[s.alias] = s.value
        return result

    return await _run_in_thread(_do)


@admin_mcp.tool
async def get_storage_info(
    token: AccessToken = CurrentAccessToken(),
) -> dict:
    """Get system storage space usage details."""

    @_run_sync
    def _do():
        app = get_flask_app()
        base_dir = os.path.dirname(app.root_path)
        storage_path = os.path.join(base_dir, 'storage')

        if not os.path.exists(storage_path):
            return {'error': 'Storage directory does not exist'}

        result = {}
        for category in os.listdir(storage_path):
            category_path = os.path.join(storage_path, category)
            if not os.path.isdir(category_path):
                continue
            total_size = 0
            file_count = 0
            for root, _, files in os.walk(category_path):
                for f in files:
                    try:
                        total_size += os.path.getsize(os.path.join(root, f))
                        file_count += 1
                    except OSError:
                        continue
            result[category] = {
                'size_mb': round(total_size / (1024 * 1024), 2),
                'file_count': file_count,
            }
        return result

    return await _run_in_thread(_do)


def create_mcp_apps():
    user_app = user_mcp.streamable_http_app(streamable_http_path="/")
    admin_app = admin_mcp.streamable_http_app(streamable_http_path="/")
    return user_app, admin_app
