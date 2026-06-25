# doctranslator-local-mcp

DocTranslator local MCP server, supports translating local document files through MCP clients (such as Claude Desktop).

## Features

- 📄 Translate local files (just provide file path)
- 🔗 Translate online documents via URL
- 📊 Query translation progress and status
- 📥 Download translation results
- 📚 Manage terminology databases and prompt templates

## Quick Start

### uvx (recommended)


```json
{
  "mcpServers": {
    "doctranslator": {
      "command": "uvx",
      "args": ["doctranslator-local-mcp"],
      "env": {
        "DOCTRANSLATOR_URL": "https://your-domain.com",
        "DOCTRANSLATOR_API_KEY": "dtk_xxxxx"
      }
    }
  }
}
```

### pip

```bash
pip install doctranslator-local-mcp
doctranslator-local-mcp
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DOCTRANSLATOR_URL` | ✅ | Platform address, e.g. `https://your-domain.com` |
| `DOCTRANSLATOR_API_KEY` | ✅ | MCP Key generated on platform, e.g. `dtk_xxxxx` |
| `API_URL` | ❌ | Translation API address, e.g. `https://api.ezworkapi.top` |
| `API_KEY` | ❌ | Translation API Key |
| `MODEL` | ❌ | Translation model, e.g. `gpt-4o` |
| `LANG` | ❌ | Default target language, e.g. `Chinese` (default) |
| `TYPE` | ❌ | Default translation type (default `trans_all_only_inherit`) |
| `THREADS` | ❌ | Number of translation threads (default `5`) |
| `COMPARISON_ID` | ❌ | Default terminology database ID |
| `PROMPT_ID` | ❌ | Default prompt template ID |
| `DOC2X_FLAG` | ❌ | Enable Doc2X (default `N`) |
| `DOC2X_SECRET_KEY` | ❌ | Doc2X secret key |

> If the MCP Key has been configured with translation parameters on the platform, `API_URL`/`API_KEY`/`MODEL` etc. can be left blank, and the configuration from the Key will be used automatically.

## Supported File Formats

docx, xlsx, pptx, pdf, txt, md, csv, xls, doc, html, htm, etc.

