"""
DocTranslator Local MCP Server (stdio transport)

The local MCP server can directly read local files for translation without manual Base64 encoding.
Translation configuration comes from two sources:
1. Environment variables (priority): API_URL, API_KEY, MODEL, etc.
2. Remote MCP Key configuration: If environment variables are not set, uses configuration saved in MCP Key

Usage:
No need to manually install dependencies, they will be automatically installed on first run.
Add to claude_desktop_config.json in Claude Desktop:

{
  "mcpServers": {
    "doctranslator": {
      "command": "python",
      "args": ["mcp_local_server.py"],
      "env": {
        "DOCTRANSLATOR_URL": "https://your-domain.com:5002",
        "DOCTRANSLATOR_API_KEY": "dtk_xxxxx",
        "API_URL": "https://api.openai.com",
        "API_KEY": "sk-xxxx",
        "MODEL": "gpt-4o",
        "TYPE": "trans_all_only_inherit",
        "PROMPT_ID": "0",
        "BACKUP_MODEL": "",
        "THREADS": "5",
        "LANG": "Chinese",
        "COMPARISON_ID": "",
        "DOC2X_FLAG": "N",
        "DOC2X_SECRET_KEY": ""
      }
    }
  }
}

Note: If the MCP Key corresponding to DOCTRANSLATOR_API_KEY has already configured translation parameters,
      then API_URL/API_KEY/MODEL in environment variables can be left empty, and the configuration in the Key will be used automatically.
"""

import subprocess
import sys

def _ensure_deps():
    deps = ["fastmcp>=2.0.0", "requests>=2.28.0"]
    missing = []
    for dep in deps:
        pkg = dep.split(">=")[0].split("==")[0].split("[")[0]
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(dep)
    if missing:
        sys.stderr.write(f"Installing dependencies: {', '.join(missing)} ...\n")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

_ensure_deps()

import os
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
        "You can directly translate local files (just provide the file path), query translation progress, and download translation results. "
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

    if hasattr(result, 'data') and result.data:
        return result.data

    content_list = []
    if hasattr(result, 'content') and result.content:
        for item in result.content:
            if hasattr(item, 'text') and item.text:
                try:
                    parsed = json.loads(item.text)
                    if isinstance(parsed, dict):
                        return parsed
                    content_list.append(item.text)
                except (json.JSONDecodeError, TypeError):
                    content_list.append(item.text)

    if content_list:
        return {"result": "\n".join(content_list)}
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
        file_path: Local file absolute path
        target_lang: Target language (Chinese/English/Japanese, etc.), leave empty to use default configuration
        origin_lang: Source language, leave empty for auto-detection
        translate_type: Translation type, leave empty to use default configuration
        comparison_id: Terminology database ID
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
    Download and translate a file via URL.

    Args:
        file_url: File download link
        file_name: File name (optional, will be inferred from URL if not provided)
        target_lang: Target language
        origin_lang: Source language
        translate_type: Translation type
        comparison_id: Terminology database ID
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
    Query the status of a translation task.

    Args:
        task_id: Translation task ID
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
    List translation history records.

    Args:
        page: Page number
        limit: Items per page
        status: Filter by status
        keyword: Keyword search
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
    Download the translation result file, returns Base64 encoded content.

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
    Delete a translation record.

    Args:
        task_id: Translation task ID
    """
    try:
        return await _call_remote_tool("delete_translate", {"task_id": task_id})
    except Exception as e:
        return {"error": f"Delete failed: {str(e)}"}


@mcp.tool
async def list_comparisons() -> dict:
    """Get the list of terminology databases."""
    try:
        return await _call_remote_tool("list_comparisons", {})
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


@mcp.tool
async def list_prompts() -> dict:
    """Get the list of prompt templates."""
    try:
        return await _call_remote_tool("list_prompts", {})
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


@mcp.tool
async def get_account_info() -> dict:
    """Get current account information."""
    try:
        return await _call_remote_tool("get_account_info", {})
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


@mcp.tool
async def get_supported_formats() -> dict:
    """Get the list of supported file formats."""
    try:
        return await _call_remote_tool("get_supported_formats", {})
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


if __name__ == "__main__":
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