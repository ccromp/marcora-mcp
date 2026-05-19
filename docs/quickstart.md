# Quickstart

Get connected to Marcora's MCP server in under 2 minutes.

## Prerequisites

- A Marcora account ([sign up at marcora.ai](https://marcora.ai))
- An MCP-compatible AI client (Claude, ChatGPT, Cursor, VS Code, etc.)

## Option 1: OAuth (Recommended)

Use this method for interactive AI clients. The connection URL is:

```
https://mcp.marcora.ai
```

## Option 2: API Token

For environments where OAuth isn't practical, use an API key with one of these endpoints:

| Transport | URL |
|---|---|
| SSE | `https://api.marketcore.ai/x2/mcp/EbZaDl-X/mcp/sse` |
| Streamable HTTP | `https://api.marketcore.ai/x2/mcp/EbZaDl-X/mcp/stream` |

Generate your API key at [Integration Settings](https://app.marcora.ai/integration-settings).

---

## Client Configuration Examples

### Claude

1. Open [Add Custom Connector](https://claude.ai/settings/connectors?modal=add-custom-connector) in Claude's connection settings
2. Paste the Marcora MCP Server URL: `https://mcp.marcora.ai`
3. Click **Add**, then click **Connect** next to "Marcora" to complete OAuth setup
4. In a conversation, click the **+** in the message composer and enable **Marcora** under Connectors

### ChatGPT

1. Open [ChatGPT's Advanced Settings](https://chatgpt.com/#settings/Connectors/Advanced)
2. Turn **Developer mode** on, then click **Create app**
3. Enter the Marcora MCP Server URL: `https://mcp.marcora.ai`
4. In a conversation, open the Developer mode tool picker and select the **Marcora** app

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "marcora": {
      "url": "https://mcp.marcora.ai"
    }
  }
}
```

Claude Desktop will handle the OAuth flow on first connection.

### Cursor

Add to your Cursor MCP settings (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "marcora": {
      "url": "https://mcp.marcora.ai"
    }
  }
}
```

### VS Code (Copilot)

Add to your VS Code settings (`.vscode/mcp.json`):

```json
{
  "servers": {
    "marcora": {
      "url": "https://mcp.marcora.ai"
    }
  }
}
```

### API Token Configuration (Any Client)

If your client requires an API key instead of OAuth, use the SSE or Streamable HTTP URL with your API key:

```json
{
  "mcpServers": {
    "marcora": {
      "url": "https://api.marketcore.ai/x2/mcp/EbZaDl-X/mcp/stream",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

Replace `YOUR_API_KEY` with the key from [Integration Settings](https://app.marcora.ai/integration-settings).

---

## Verify Connection

After connecting, try asking your AI client:

> "What context do I have in Marcora?"

If authentication was successful, the client will use the `get_core_context` tool to retrieve your account's context.

Other things to try:

- "Show me my blueprints"
- "What plan am I on?"
- "List my projects"
