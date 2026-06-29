# Authentication

All Marcora MCP server tools require authentication. Two methods are supported:

## OAuth 2.0 (Recommended)

Best for interactive AI clients like Claude, ChatGPT, and Cursor.

**Connection URL:**

```
https://mcp.marcora.ai
```

OAuth is handled automatically by the MCP client. When you add the connection URL, the client will redirect you to Marcora to authorize access. Once authorized, the client manages token refresh automatically.

**How it works:**
1. Add `https://mcp.marcora.ai` as an MCP server in your client
2. The client initiates the OAuth flow and redirects you to Marcora
3. Log in with your Marcora account and authorize the connection
4. The client receives and stores your access token
5. All subsequent tool calls are authenticated automatically

## API Token

Best for non-interactive environments, CI/CD pipelines, headless agent setups, or clients that support direct API key configuration.

**API Key URL:** `https://mcp.marcora.ai` — the same URL as OAuth. The server negotiates the right transport automatically; pass your key in the `Authorization` header (see below).

**How to get your API key:**
1. Log in to Marcora at [app.marcora.ai](https://app.marcora.ai)
2. Navigate to **Integration Settings** at [app.marcora.ai/integration-settings](https://app.marcora.ai/integration-settings)
3. Create a new MCP API key
4. Copy the key and add it to your MCP client configuration

**How to pass the API key:**

Include your API key as a Bearer token in the `Authorization` header. Most MCP clients handle this via their configuration file — see [Quickstart](quickstart.md) for examples.

## Permissions

Both authentication methods grant access to all tools within the scope of your Marcora account:

- You can access data belonging to your **active team**
- Your role on the team (e.g. owner, member) determines what actions you can perform
- Private content and collections are only visible to their creator
- Team-visible content is accessible to all team members

## Revoking Access

**OAuth connections:** Disconnect the MCP server from your AI client's settings. You can also revoke OAuth authorizations from your Marcora account settings.

**API keys:** Delete the key from [Integration Settings](https://app.marcora.ai/integration-settings). The key is immediately invalidated.
