# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Description

**DocTranslator** is an open-source AI-powered document translation tool that supports multiple file formats and LLM providers. The system enables batch translation with multi-threaded processing and advanced terminology management.

## Architecture

### Technology Stack

- **Frontend (User)**: Vue 3 + Vite + Element Plus (port 1475)
- **Frontend (Admin)**: Vue 3 + Vite + Element Plus + TypeScript + UnoCSS (port 8081)
- **Backend**: Python 3 + Flask + SQLAlchemy + Gunicorn (port 5000)
- **Database**: MySQL (production) / SQLite (development)
- **Web Server**: Nginx (reverse proxy)
- **MCP Server**: FastMCP for Claude Desktop integration

### Directory Structure

```
DocTranslator/
├── frontend/           # End-user web application
├── admin/             # Administration panel
├── backend/           # Flask API
│   ├── app/
│   │   ├── models/    # SQLAlchemy models
│   │   ├── resources/ # REST endpoints (API + Admin + Task)
│   │   ├── translate/ # Translation engines by format
│   │   ├── schemas/   # Marshmallow schemas
│   │   ├── utils/     # Utilities
│   │   ├── mcp/       # MCP server integration
│   │   └── script/    # DB initialization scripts
│   ├── init.sql       # MySQL schema
│   └── requirements.txt
├── nginx/             # Nginx configuration
├── mcp_local_server.py # Local MCP server (stdio)
└── mcp_client/        # Example MCP client
```

## LLM Providers and Configuration

### Supported Providers

1. **OpenAI-Compatible API** (`server='openai'`)
   - Configurable endpoint (OpenAI, Azure OpenAI, intermediary APIs)
   - Configurable models: `gpt-3.5-turbo`, `gpt-4`, `gpt-4o`, etc.
   - Supports fallback model
   - Configuration: `api_url`, `api_key`, `model`, `backup_model`

2. **Baidu Translate** (`server='baidu'`)
   - Baidu Translate API
   - Configuration: `app_id`, `app_key`
   - Does not support fallback models

### Model Configuration

Models are configured per translation in the `translate` table:
- `model`: Primary model
- `backup_model`: Fallback model (OpenAI only)
- `api_url` / `api_key`: Provider credentials
- `threads`: Number of threads (1-10, default 5)
- `prompt`: Custom prompt template
- `server`: 'openai' or 'baidu'

### Adding New LLM Providers

To add support for new providers (Anthropic, Google, etc.):

1. Create function in `backend/app/translate/to_translate.py`:
```python
def _translate_<provider>(trans, text, model):
    """Call to provider API"""
    # Implement call logic
    return translated_text
```

2. Add case in `_try_translate_with_retries()`:
```python
if server == '<provider>':
    translated = _translate_<provider>(trans, original_text, model)
```

3. Update `backend/app/models/translate.py` if additional fields are required

4. Add validation in `backend/app/resources/api/translate.py`

## Multi-Language Support

### Supported Languages

The system supports translation between the following languages (mapping in `backend/app/translate/common.py:convert_language_name_to_code`):

| Language | Code | Accepted Variants |
|----------|------|-------------------|
| Chinese | zh | 中文 |
| English | en | 英语, 英文, english |
| Japanese | ja | 日语, 日文, japanese |
| Korean | ko | 韩语, 韩文, korean |
| French | fr | 法语, 法文 |
| German | de | 德语, 德文 |
| Russian | ru | 俄语, 俄文 |
| Spanish | es | 西班牙语, 西班牙文 |
| Arabic | ar | 阿拉伯语 |
| Portuguese | pt | 葡萄牙语 |
| Italian | it | 意大利语 |

### Adding New Languages

1. Update `language_mapping` in `backend/app/translate/common.py`
2. Update `LANG_CODE_TO_CHINESE` in `backend/app/resources/api/translate.py`
3. Update language options in frontend (`frontend/src/views/translate/index.vue`)

## Supported Document Formats

Each format has its own module in `backend/app/translate/`:

- **Word**: `.doc`, `.docx` - Module: `word.py` (uses `python-docx`)
- **Excel**: `.xls`, `.xlsx` - Module: `excel.py` (uses `openpyxl`)
- **PowerPoint**: `.pptx` - Module: `powerpoint.py` (uses `python-pptx`)
- **PDF**: `.pdf` (non-scanned) - Module: `pdf.py` (uses `PyMuPDF`, `pdf2docx`)
- **Markdown**: `.md` - Module: `md.py`
- **CSV**: `.csv` - Module: `csv_handle.py` (uses `pandas`)
- **Plain Text**: `.txt` - Module: `txt.py`
- **HTML**: `.html`, `.htm` - Module: `html.py` (uses `beautifulsoup4`)

## Data Persistence

### Database

**Production**: MySQL
```bash
SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:pwd@host/dbname
```

**Development**: SQLite
```bash
DEV_DATABASE_URL=sqlite:///instance/dev.db
```

### Main Models

| Table | Description |
|-------|-------------|
| `customer` | System users (email, password, storage) |
| `translate` | Translation tasks (status, files, progress) |
| `prompt` | Shareable prompt templates |
| `comparison` | Term tables (glossaries) |
| `setting` | System configuration (serialized key-value) |
| `mcp_api_key` | API keys for MCP server |
| `session` | User sessions |
| `translate_log` | Translation logs |

### File Storage

**Location**: `storage/translate/YYYY-MM-DD/`
- Original files: `origin_filepath`
- Translated files: `target_filepath`
- Limits: `MAX_FILE_SIZE` (default 50MB), `MAX_USER_STORAGE` (default 100MB per user)

## Development Commands

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit backend/.env with credentials

# Development (port 5000)
python run.py

# Production (Gunicorn)
gunicorn -b 0.0.0.0:5000 -w 4 -k gevent --timeout 120 run:app
```

### Frontend (User)

```bash
cd frontend

# Install
pnpm install

# Development (port 1475)
pnpm dev

# Build
pnpm build:prod      # Production
pnpm build:dev       # Development
pnpm build:com       # Community
```

### Admin (Administration Panel)

```bash
cd admin

# Install
pnpm install

# Development (port 8081)
pnpm dev

# Build
pnpm build           # Production
pnpm build:stage     # Staging
pnpm build:demo      # Demo
pnpm build:community # Community

# Tests
pnpm test            # Vitest
pnpm lint            # ESLint + Prettier
```

### Deploy with Docker

```bash
# Docker Compose (recommended)
docker-compose up -d

# Or use deploy script
chmod +x deploy.sh
./deploy.sh

# Update
./update.sh
```

## Translation Flow

1. **Upload**: User uploads file → `FileUploadResource` → stores in `storage/`
2. **Config**: User configures translation (language, model, prompt, terms)
3. **Start**: `TranslateStartResource` → creates record in `translate` table
4. **Engine**: `TranslateEngine` runs in background:
   - Reads file according to format (e.g. `word.py`, `pdf.py`)
   - Splits into text blocks
   - Filters empty/punctuation blocks (`is_all_punc`)
   - Applies custom terms (`_inject_matched_terms`)
   - Translates in parallel with ThreadPoolExecutor (`translate_batch`)
   - Handles retries and fallback model
   - Updates progress in DB (`update_progress`)
5. **Complete**: Generates translated file → stores in `target_filepath`
6. **Download**: User downloads translated file

### Advanced Features

- **Terminology**: `comparison` table stores source→target glossaries
- **Memory**: `cache` table for reusing translations
- **Batch**: Supports multiple files in parallel
- **Retries**: 3 attempts with 5s delay, then tries backup_model
- **Progress**: Incremental update every 15% (optimized for DB)

## Important Environment Variables

```bash
# Flask
FLASK_ENV=production|development
SECRET_KEY=your-secret-key

# Database
SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:pwd@host/dbname
DEV_DATABASE_URL=sqlite:///instance/dev.db

# JWT
JWT_SECRET_KEY=secret
JWT_ACCESS_TOKEN_EXPIRES=172800  # seconds

# Email (for verification codes)
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=user@example.com
MAIL_PASSWORD=password
ALLOWED_EMAIL_DOMAINS=qq.com,163.com,126.com

# Limits
MAX_FILE_SIZE=50          # MB
MAX_USER_STORAGE=100      # MB

# CORS
ALLOWED_DOMAINS=*  # Or comma-separated list
```

## Testing

The project includes testing configuration but currently has no implemented test suite:

```bash
# Admin has Vitest setup
cd admin
pnpm test

# To implement tests:
# - Use @vue/test-utils for Vue components
# - Use pytest for backend (add to requirements.txt)
```

## MCP Server

DocTranslator includes an MCP server for Claude Desktop integration:

**Configuration** (`claude_desktop_config.json`):
```json
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
        "LANG": "Chinese"
      }
    }
  }
}
```

**Features**:
- Local file translation without Base64 encoding
- Translation progress query
- Result download
- Inherited configuration from MCP Key or environment variables

## Special Notes

1. **Encoding**: All code uses UTF-8, especially important for multi-language texts
2. **Thread Safety**: Uses `threading.Lock` for progress updates (`_progress_lock`)
3. **Token Counting**: Uses `tiktoken` to estimate costs
4. **Prompt Injection**: Terms are dynamically injected into the prompt only if they appear in the text
5. **Markdown/HTML Format**: Special instructions are added to the prompt to preserve formatting
6. **Credentials**: API keys can be configured per user or per translation
7. **Version**: Currently v1.6.0
