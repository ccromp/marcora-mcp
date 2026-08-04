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

For environments where OAuth isn't practical, use an API key with the same connection URL:

```
https://mcp.marcora.ai
```

Pass the key in an `Authorization: Bearer <your-api-key>` header — the server negotiates the right transport automatically. Generate your API key at [Integration Settings](https://app.marcora.ai/integration-settings).

---

## Client Configuration Examples

### Claude

Marcora is in Claude's connector directory, so there is no URL and no token to paste.

1. Open the [Marcora listing](https://claude.ai/directory/connectors/marcora) in Claude's connector directory
2. Click **Connect**, then **Allow** on Marcora's authorization page to finish the OAuth flow
3. Start a chat and just ask — Marcora is enabled by default in every new conversation, so there is nothing to turn on in the composer
4. The first time Claude uses each Marcora tool it stops and asks — *"Claude wants to use **Get Brand Foundation** from Marcora: Brand Context & Writing"* — so click **Always allow**

Step 4 is easy to miss and it is load-bearing: **nothing reaches Marcora until you approve it.** The prompt is per tool rather than per connector, so expect it again the first time each new Marcora tool comes up; approvals then persist across your conversations.

Manage the connection afterwards under **Customize → Connectors**, where Marcora shows as **Connected**. It only appears in that list once connected — searching for it there beforehand returns nothing, which is why step 1 starts at the directory.

**Adding it by URL instead** — use this for a whole Team or Enterprise workspace, or simply by preference:

1. In Claude, go to **Customize → Connectors**, click **Add**, then choose **Add custom connector**
2. Give the connector a name and paste the Marcora MCP Server URL: `https://mcp.marcora.ai`
3. Click **Add**, then click **Connect** next to "Marcora" and approve access to finish the OAuth flow

Then carry on from step 3 above — the per-tool approval prompt works the same way. Note that Free Claude accounts are limited to one custom connector; connecting from the directory does not use that slot.

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

If your client requires an API key instead of OAuth, use the same connection URL with your API key in an `Authorization` header:

```json
{
  "mcpServers": {
    "marcora": {
      "url": "https://mcp.marcora.ai",
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

> "What's my brand foundation?"

If authentication was successful, the client will use the `get_brand_foundation` tool to retrieve your team's Brand Foundation.

Other things to try:

- "Show me my blueprints"
- "What plan am I on?"
- "List my projects"
