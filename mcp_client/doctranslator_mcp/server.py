import os
import sys
import json
import base64
import logging
from typing import Optional

from fastmcp import FastMCP, Client
from fastmcp.client.transports import StreamableHttpTransport

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

REMOTE_URL = os.environ.get("DOCTRANSLATOR_URL", "").rstrip("/")
API_KEY = os.environ.get("DOCTRANSLATOR_API_KEY", "")

ENV_CONFIG = {
    "api_url": os.environ.get("API_URL", ""),
    "api_key": os.environ.get("API_KEY", ""),
    "model": os.environ.get("MODEL", ""),
    "type": os.environ.get("TYPE", "trans_all_only_inherit"),
    "prompt_id": int(os.environ.get("PROMPT_ID", "0")),
    "backup_model": os.environ.get("BACKUP_MODEL", ""),
    "threads": int(os.environ.get("THREADS", "5")),
    "lang": os.environ.get("LANG", "Chinese"),
    "comparison_id": os.environ.get("COMPARISON_ID") or None,
    "doc2x_flag": os.environ.get("DOC2X_FLAG", "N"),
    "doc2x_secret_key": os.environ.get("DOC2X_SECRET_KEY", ""),
}


def _has_env_config():
    return bool(ENV_CONFIG.get("api_url") and ENV_CONFIG.get("api_key") and ENV_CONFIG.get("model"))


mcp = FastMCP(
    "DocTranslator-Local",
    instructions=(
        "DocTranslator document translation local service. "
        "You can directly translate local files (just provide the file path) or translate files via URL, and also query translation progress and download translation results. "
        "Translation configuration comes from environment variables or the configuration saved in the MCP Key, no need to pass it every time."
    ),
)


async def _call_remote_tool(tool_name: str, arguments: dict) -> dict:
    transport = StreamableHttpTransport(
        url=f"{REMOTE_URL}/mcp/user",
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    client = Client(transport)

    async with client:
        result = await client.call_tool(tool_name, arguments)

    if hasattr(result, 'data') and result.data is not None:
        if isinstance(result.data, dict):
            return result.data
        try:
            parsed = json.loads(result.data)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass

    if hasattr(result, 'content') and result.content:
        for item in result.content:
            if hasattr(item, 'text') and item.text:
                try:
                    parsed = json.loads(item.text)
                    if isinstance(parsed, dict):
                        return parsed
                except (json.JSONDecodeError, TypeError):
                    return {"result": item.text}

    return {"result": str(result)}


@mcp.tool
async def translate_file(
    file_path: str,
    target_lang: str = "",
    origin_lang: str = "",
    translate_type: str = "",
    comparison_id: Optional[int] = None,
) -> dict:
    """
    Translate a local document file. Simply provide the local file path without manual encoding.

    Args:
        file_path: Local file absolute path, e.g., /Users/user/Documents/report.docx
        target_lang: Target translation language, e.g., "Chinese", "English", "Japanese", etc. Leave empty to use default configuration.
        origin_lang: Source language. Leave empty for auto-detection.
        translate_type: Translation type. Options: trans_all_only_inherit (full translation with format inheritance), trans_all_only (full translation without inheritance), trans_partial_only_inherit (partial translation with inheritance), trans_partial_only (partial translation without inheritance). Leave empty to use default configuration.
        comparison_id: Terminology database ID. Leave empty to use default configuration.
    """
    if not os.path.exists(file_path):
        return {"error": f"File does not exist: {file_path}"}

    with open(file_path, "rb") as f:
        file_content = base64.b64encode(f.read()).decode()

    file_name = os.path.basename(file_path)

    args = {
        "file_name": file_name,
        "file_content": file_content,
    }
    if target_lang:
        args["target_lang"] = target_lang
    if origin_lang:
        args["origin_lang"] = origin_lang
    if translate_type:
        args["translate_type"] = translate_type
    if comparison_id:
        args["comparison_id"] = comparison_id

    try:
        return await _call_remote_tool("translate_file", args)
    except Exception as e:
        logger.error(f"Translation call failed: {e}")
        return {"error": f"Translation call failed: {str(e)}"}


@mcp.tool
async def translate_by_url(
    file_url: str,
    file_name: str = "",
    target_lang: str = "",
    origin_lang: str = "",
    translate_type: str = "",
    comparison_id: Optional[int] = None,
) -> dict:
    """
    Download and translate a file via URL. Suitable for online documents or publicly accessible file links.

    Args:
        file_url: File download link URL
        file_name: File name (with extension), will be inferred from URL if not provided
        target_lang: Target translation language, e.g., "Chinese", "English", "Japanese", etc. Leave empty to use default configuration.
        origin_lang: Source language. Leave empty for auto-detection.
        translate_type: Translation type. Options: trans_all_only_inherit (full translation with format inheritance), trans_all_only (full translation without inheritance), trans_partial_only_inherit (partial translation with inheritance), trans_partial_only (partial translation without inheritance). Leave empty to use default configuration.
        comparison_id: Terminology database ID. Leave empty to use default configuration.
    """
    args = {
        "file_url": file_url,
        "file_name": file_name,
    }
    if target_lang:
        args["target_lang"] = target_lang
    if origin_lang:
        args["origin_lang"] = origin_lang
    if translate_type:
        args["translate_type"] = translate_type
    if comparison_id:
        args["comparison_id"] = comparison_id

    try:
        return await _call_remote_tool("translate_file", args)
    except Exception as e:
        logger.error(f"URL translation call failed: {e}")
        return {"error": f"Translation call failed: {str(e)}"}


@mcp.tool
async def query_translate_status(task_id: int) -> dict:
    """
    Query the status and progress of a translation task. Returns task ID, status, progress percentage, elapsed time, and other information.

    Args:
        task_id: Translation task ID (the task_id field value returned when starting the translation)
    """
    try:
        return await _call_remote_tool("query_translate_status", {"task_id": task_id})
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


@mcp.tool
async def list_translates(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
) -> dict:
    """
    List translation history records. Returns a task list containing task ID, file name, status, progress, etc.

    Args:
        page: Page number, starting from 1. Default is page 1.
        limit: Items per page. Default is 20.
        status: Filter by status. Options: none (not started), process (in progress), done (completed), failed. Leave empty to return all statuses.
        keyword: Search by file name keyword. Leave empty to not filter.
    """
    args = {"page": page, "limit": limit}
    if status:
        args["status"] = status
    if keyword:
        args["keyword"] = keyword
    try:
        return await _call_remote_tool("list_translates", args)
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


@mcp.tool
async def download_translate(task_id: int) -> dict:
    """
    Download the translation result file. Only tasks with status 'done' can be downloaded, returns Base64 encoded file content.

    Args:
        task_id: Translation task ID
    """
    try:
        return await _call_remote_tool("download_translate", {"task_id": task_id})
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}


@mcp.tool
async def delete_translate(task_id: int) -> dict:
    """
    Delete a translation record. Frees up storage space occupied by the file after deletion.

    Args:
        task_id: Translation task ID
    """
    try:
        return await _call_remote_tool("delete_translate", {"task_id": task_id})
    except Exception as e:
        return {"error": f"Delete failed: {str(e)}"}


@mcp.tool
async def restart_translate(task_id: int) -> dict:
    """
    Restart a failed or not-yet-started translation task. Only tasks with status 'failed' or 'none' can be restarted.

    Args:
        task_id: Translation task ID
    """
    try:
        return await _call_remote_tool("restart_translate", {"task_id": task_id})
    except Exception as e:
        return {"error": f"Restart failed: {str(e)}"}


@mcp.tool
async def list_comparisons() -> dict:
    """List all terminology databases of the current user. Returns terminology database ID, name, source language, target language, term count, and other information."""
    try:
        return await _call_remote_tool("list_comparisons", {})
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


@mcp.tool
async def list_prompts() -> dict:
    """List all prompt templates of the current user. Returns template ID, name, sharing status, and other information."""
    try:
        return await _call_remote_tool("list_prompts", {})
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


@mcp.tool
async def get_account_info() -> dict:
    """Get the current user's account information. Returns email, name, level, used storage space, total storage space, etc."""
    try:
        return await _call_remote_tool("get_account_info", {})
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


@mcp.tool
async def get_supported_formats() -> dict:
    """Get the list of file formats supported by the system and maximum file size limits. Supports docx, xlsx, pptx, pdf, and other formats."""
    try:
        return await _call_remote_tool("get_supported_formats", {})
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


def main():
    if not REMOTE_URL:
        sys.stderr.write("Error: Please set the DOCTRANSLATOR_URL environment variable (e.g., https://your-domain.com:5002)\n")
        sys.exit(1)
    if not API_KEY:
        sys.stderr.write("Error: Please set the DOCTRANSLATOR_API_KEY environment variable (e.g., dtk_xxxxx)\n")
        sys.exit(1)

    logger.info(f"Local MCP server starting, remote endpoint: {REMOTE_URL}/mcp/user")
    logger.info(f"API Key: {API_KEY[:12]}...")
    if _has_env_config():
        logger.info("Translation configuration source: Environment variables")
    else:
        logger.info("Translation configuration source: Configuration saved in MCP Key (translation parameters not set in environment variables)")

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
