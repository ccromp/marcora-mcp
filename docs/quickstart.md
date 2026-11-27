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

Marcora is in Claude's directory, so there is no URL and no token to paste.

1. Open the [Marcora listing](https://claude.ai/directory/marcora) in Claude's directory (it opens under **Plugins**)
2. Select **Add** at the top right, then select **Connect** under **Connectors**, sign in to Marcora if asked, and select **Allow** on Marcora's authorization screen to finish the OAuth flow
3. Open a chat and ask — e.g., *"What's my brand foundation?"* Marcora should already be switched on in new chats (to check, click **+** then **Plugins**)
4. Whether Claude asks before using a Marcora tool depends on the chat's **Permission mode**, next to the model picker. New chats start in **Auto**: Claude runs on its own and pauses to ask if anything looks unsafe, so you may not see a prompt. In **Manual** mode Claude asks before using new tools. To set it tool by tool, open Marcora's listing, choose the **Permissions** tab, and pick **Always allow**, **Needs approval**, **Always ask**, or **Blocked** for each tool

> **Tip:** In **Auto** mode, Claude's safety check can still stop a Marcora call instead of pausing to ask — when that happens, the call just doesn't run. Name your Marcora team in the request, or switch that chat to **Manual**.

Manage the connection afterwards by opening **Plugins** in Claude ([claude.ai/plugins](https://claude.ai/plugins)) and opening Marcora's listing, where its **Connectors** section shows **Connected**. Anthropic's help articles may still call this page **Customize → Connectors**.

**Adding it by URL instead** — use this for a whole Team or Enterprise workspace, or simply by preference:

1. In Claude, open **Plugins** (in Settings, or at [claude.ai/plugins](https://claude.ai/plugins)), select **Add**, and choose **Add custom connector** (Anthropic's help articles may still call this page **Customize → Connectors**)
2. Enter a name and paste the Marcora connection URL (`https://mcp.marcora.ai`) into **MCP server URL**, then select **Continue**. Claude checks the server and moves to the next screen. Keep the sign-in settings Claude detects and select **Add** — Marcora doesn't need its own OAuth client ID or secret
3. Select **Connect** next to Marcora, sign in to Marcora if asked, and select **Allow** on Marcora's authorization screen

Then carry on from step 3 above. Note that Free Claude accounts are limited to one custom connector; connecting from the directory does not use that slot.

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
      "url": "https://mcp.marcora.ai/"
    }
  }
}
```

### Kiro

Click [![Add to Kiro](https://kiro.dev/images/add-to-kiro.svg)](https://kiro.dev/launch/mcp/add?name=marcora&config=%7B%22url%22%3A%22https%3A%2F%2Fmcp.marcora.ai%2F%22%7D) or add to `~/.kiro/settings/mcp.json` (user) or `.kiro/settings/mcp.json` (workspace):

```json
{
  "mcpServers": {
    "marcora": {
      "url": "https://mcp.marcora.ai/"
    }
  }
}
```

Kiro opens a browser login on first connection to complete OAuth 2.1 with PKCE.

### Hermes Agent

Install the Marcora Portable Agent Plugin v1 package (remote MCP server + companion `marcora-mcp` workflow skill):

```bash
hermes plugins install marcora
```

Or directly from GitHub:

```bash
hermes plugins install https://github.com/ccromp/marcora-mcp
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
