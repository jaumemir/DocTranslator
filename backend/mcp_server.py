import os
import logging
import asyncio
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator

logging.basicConfig(level=logging.INFO)
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
        with flask_app_context() as app:
            import inspect
            sig = inspect.signature(func)
            if 'app' in sig.parameters and 'app' not in kwargs:
                kwargs['app'] = app
            return func(*args, **kwargs)
    return wrapper


async def _run_in_thread(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token, TokenClaim
from app.mcp.auth import McpApiKeyAuthProvider

user_mcp = FastMCP(
    "DocTranslator-User",
    auth=McpApiKeyAuthProvider(scope='user'),
    instructions=(
        "DocTranslator document translation service. "
        "You can translate documents, query translation progress, and manage terminology databases and prompt templates. "
        "Translation configuration such as api_url/api_key/model is automatically provided by the MCP key, no need to pass it every time."
    ),
)

admin_mcp = FastMCP(
    "DocTranslator-Admin",
    auth=McpApiKeyAuthProvider(scope='admin'),
    instructions=(
        "DocTranslator admin backend MCP service. "
        "You can view translation statistics, manage users, manage translation tasks, and modify system settings."
    ),
)


# ==================== User Tools ====================

@user_mcp.tool()
async def translate_file(
    file_name: str = "",
    file_content: str = "",
    file_url: str = "",
    target_lang: str = "",
    origin_lang: str = "",
    translate_type: str = "",
    comparison_id: int = 0,
) -> dict:
    """Translate a document file. Provide the file name and file content (Base64 encoded) or file download link to start a translation task.

    Args:
        file_name: File name (with extension), e.g., report.docx. Required when using file_content.
        file_content: Base64 encoded file content. At least one of file_content or file_url must be provided.
        file_url: File download link URL. At least one of file_content or file_url must be provided.
        target_lang: Target translation language, e.g., "Chinese", "English", "Japanese", etc. Leave empty to use the default language from key configuration.
        origin_lang: Source language. Leave empty for auto-detection.
        translate_type: Translation type. Options: trans_all_only_inherit (full translation with format inheritance), trans_all_only (full translation without inheritance), trans_partial_only_inherit (partial translation with inheritance), trans_partial_only (partial translation without inheritance). Leave empty to use the default type from key configuration.
        comparison_id: Terminology database ID. Leave empty to use the default terminology database from key configuration.
    """
    from app.mcp.tools import translate_file as _translate_file
    token = get_access_token()
    config = token.claims.get('config', {})
    customer_id = int(token.claims.get('customer_id', 0))
    if target_lang:
        config['lang'] = target_lang
    if origin_lang:
        config['origin_lang'] = origin_lang
    if translate_type:
        config['type'] = translate_type
    if comparison_id:
        config['comparison_id'] = comparison_id
    func = _run_sync(_translate_file)
    return await _run_in_thread(func, config=config, customer_id=customer_id,
                                 file_content=file_content, file_url=file_url,
                                 file_name=file_name, target_lang=target_lang,
                                 origin_lang=origin_lang, translate_type=translate_type,
                                 comparison_id=comparison_id)


@user_mcp.tool()
async def query_translate_status(task_id: int) -> dict:
    """Query the status and progress of a translation task. Returns task ID, status, progress percentage, elapsed time, and other information.

    Args:
        task_id: Translation task ID (the task_id field value returned when starting the translation)
    """
    from app.mcp.tools import query_translate_status as _query
    token = get_access_token()
    customer_id = int(token.claims.get('customer_id', 0))
    func = _run_sync(_query)
    return await _run_in_thread(func, customer_id=customer_id, task_id=task_id)


@user_mcp.tool()
async def list_translates(page: int = 1, limit: int = 20, status: str = "", keyword: str = "") -> dict:
    """List the current user's translation history records. Returns a task list containing task ID, file name, status, progress, etc.

    Args:
        page: Page number, starting from 1. Default is page 1.
        limit: Items per page. Default is 20.
        status: Filter by status. Options: none (not started), process (in progress), done (completed), failed. Leave empty to return all statuses.
        keyword: Search by file name keyword. Leave empty to not filter.
    """
    from app.mcp.tools import list_translates as _list
    token = get_access_token()
    customer_id = int(token.claims.get('customer_id', 0))
    func = _run_sync(_list)
    return await _run_in_thread(func, customer_id=customer_id, page=page, limit=limit, status=status, keyword=keyword)


@user_mcp.tool()
async def download_translate(task_id: int) -> dict:
    """Download the translation result file. Only tasks with status 'done' can be downloaded. Returns Base64 encoded file content.

    Args:
        task_id: Translation task ID
    """
    from app.mcp.tools import download_translate as _download
    token = get_access_token()
    customer_id = int(token.claims.get('customer_id', 0))
    func = _run_sync(_download)
    return await _run_in_thread(func, customer_id=customer_id, task_id=task_id)


@user_mcp.tool()
async def delete_translate(task_id: int) -> dict:
    """Delete a translation record. Frees up storage space occupied by the file after deletion.

    Args:
        task_id: Translation task ID
    """
    from app.mcp.tools import delete_translate as _delete
    token = get_access_token()
    customer_id = int(token.claims.get('customer_id', 0))
    func = _run_sync(_delete)
    return await _run_in_thread(func, customer_id=customer_id, task_id=task_id)


@user_mcp.tool()
async def restart_translate(task_id: int) -> dict:
    """Restart a failed or not-yet-started translation task. Only tasks with status 'failed' or 'none' can be restarted.

    Args:
        task_id: Translation task ID
    """
    from app.mcp.tools import restart_translate as _restart
    token = get_access_token()
    customer_id = int(token.claims.get('customer_id', 0))
    func = _run_sync(_restart)
    return await _run_in_thread(func, customer_id=customer_id, task_id=task_id)


@user_mcp.tool()
async def list_comparisons() -> dict:
    """List all terminology databases of the current user. Returns terminology database ID, name, source language, target language, term count, and other information."""
    from app.mcp.tools import list_comparisons as _list
    token = get_access_token()
    customer_id = int(token.claims.get('customer_id', 0))
    func = _run_sync(_list)
    return await _run_in_thread(func, customer_id=customer_id)


@user_mcp.tool()
async def list_prompts() -> dict:
    """List all prompt templates of the current user. Returns template ID, name, sharing status, and other information."""
    from app.mcp.tools import list_prompts as _list
    token = get_access_token()
    customer_id = int(token.claims.get('customer_id', 0))
    func = _run_sync(_list)
    return await _run_in_thread(func, customer_id=customer_id)


@user_mcp.tool()
async def get_account_info() -> dict:
    """Get the current user's account information. Returns email, name, level, used storage space, total storage space, etc."""
    from app.mcp.tools import get_account_info as _info
    token = get_access_token()
    customer_id = int(token.claims.get('customer_id', 0))
    func = _run_sync(_info)
    return await _run_in_thread(func, customer_id=customer_id)


@user_mcp.tool()
async def get_supported_formats() -> dict:
    """Get the list of file formats supported by the system and maximum file size limits. Supports docx, xlsx, pptx, pdf, and other formats."""
    from app.mcp.tools import get_supported_formats as _formats
    func = _run_sync(_formats)
    return await _run_in_thread(func)


# ==================== Admin Tools ====================

@admin_mcp.tool()
async def get_statistics() -> dict:
    """Get system translation statistics data. Returns total number of users, total number of translations, translation counts by status, total storage usage, etc."""
    from app.mcp.tools import get_statistics as _stats
    func = _run_sync(_stats)
    return await _run_in_thread(func)


@admin_mcp.tool()
async def list_customers(page: int = 1, limit: int = 20, search: str = "") -> dict:
    """List all customer information. Returns customer ID, email, name, level, storage usage, etc.

    Args:
        page: Page number, starting from 1. Default is page 1.
        limit: Items per page. Default is 20.
        search: Search by email or name keyword. Leave empty to return all.
    """
    from app.mcp.tools import list_customers as _list
    func = _run_sync(_list)
    return await _run_in_thread(func, page=page, limit=limit, search=search)


@admin_mcp.tool()
async def update_customer(customer_id: int, level: str = "", add_storage_mb: int = 0, status: str = "") -> dict:
    """Modify customer information. Can adjust level, add storage space, enable/disable account.

    Args:
        customer_id: Customer ID (required)
        level: Customer level. Options: common, vip. Leave empty to not modify.
        add_storage_mb: Storage space to add for the customer (MB). 0 means no modification.
        status: Customer status. Options: enabled, disabled. Leave empty to not modify.
    """
    from app.mcp.tools import update_customer as _update
    func = _run_sync(_update)
    return await _run_in_thread(func, customer_id=customer_id, level=level,
                                 add_storage_mb=add_storage_mb, status=status)


@admin_mcp.tool()
async def admin_list_translates(page: int = 1, limit: int = 20, status: str = "", keyword: str = "") -> dict:
    """Admin views all users' translation records. Returns translation number, customer ID, file name, status, progress, etc.

    Args:
        page: Page number, starting from 1. Default is page 1.
        limit: Items per page. Default is 20.
        status: Filter by status. Options: none (not started), process (in progress), done (completed), failed. Leave empty to return all statuses.
        keyword: Search by file name or translation number keyword. Leave empty to not filter.
    """
    from app.mcp.tools import admin_list_translates as _list
    func = _run_sync(_list)
    return await _run_in_thread(func, page=page, limit=limit, status=status, keyword=keyword)


@admin_mcp.tool()
async def admin_restart_translate(task_id: int) -> dict:
    """Restart a failed or not-yet-started translation task.

    Args:
        task_id: Translation task ID
    """
    from app.mcp.tools import admin_restart_translate as _restart
    func = _run_sync(_restart)
    return await _run_in_thread(func, task_id=task_id)


@admin_mcp.tool()
async def admin_delete_translate(task_id: int) -> dict:
    """Admin deletes any translation record. Frees up storage space occupied by the file after deletion.

    Args:
        task_id: Translation task ID
    """
    from app.mcp.tools import admin_delete_translate as _delete
    func = _run_sync(_delete)
    return await _run_in_thread(func, task_id=task_id)


@admin_mcp.tool()
async def get_system_settings() -> dict:
    """Get system global settings. Returns all configuration items organized by group."""
    from app.mcp.tools import get_system_settings as _settings
    func = _run_sync(_settings)
    return await _run_in_thread(func)


@admin_mcp.tool()
async def get_storage_info() -> dict:
    """Get system storage details. Returns total user storage usage, total number of translations, storage directory path, etc."""
    from app.mcp.tools import get_storage_info as _info
    func = _run_sync(_info)
    return await _run_in_thread(func)


# ==================== Create ASGI Application ====================

def create_mcp_starlette():
    from starlette.applications import Starlette
    from starlette.routing import Mount
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware

    user_app = user_mcp.http_app(path="/", stateless_http=True)
    admin_app = admin_mcp.http_app(path="/", stateless_http=True)

    user_lifespan = getattr(user_app, 'lifespan', None)
    admin_lifespan = getattr(admin_app, 'lifespan', None)

    mcp_lifespans = []
    if user_lifespan:
        mcp_lifespans.append(user_lifespan)
    if admin_lifespan:
        mcp_lifespans.append(admin_lifespan)

    @asynccontextmanager
    async def combined_lifespan(app: Starlette) -> AsyncGenerator[None, None]:
        import contextlib
        async with contextlib.AsyncExitStack() as stack:
            for lf in mcp_lifespans:
                try:
                    await stack.enter_async_context(lf(app))
                except Exception as e:
                    logger.warning(f"MCP lifespan startup failed: {e}")
            yield

    starlette_app = Starlette(
        routes=[
            Mount("/mcp/user", app=user_app),
            Mount("/mcp/admin", app=admin_app),
        ],
        lifespan=combined_lifespan if mcp_lifespans else None,
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
            ),
        ],
    )

    return starlette_app


if __name__ == "__main__":
    from app import create_app
    from app.mcp.auth import set_flask_app_for_auth

    flask_app = create_app()
    set_flask_app(flask_app)
    set_flask_app_for_auth(flask_app)

    import uvicorn
    port = int(os.environ.get("MCP_PORT", 5001))
    logger.info(f"MCP server starting on port {port}")
    logger.info(f"  User endpoint: http://0.0.0.0:{port}/mcp/user")
    logger.info(f"  Admin endpoint: http://0.0.0.0:{port}/mcp/admin")

    app = create_mcp_starlette()
    uvicorn.run(app, host="0.0.0.0", port=port)
