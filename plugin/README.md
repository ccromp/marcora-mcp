# Marcora — Claude Code Plugin

Bundles the hosted **Marcora MCP server** with its companion skill so your
AI assistant can create on-brand marketing content, manage brand context and
blueprints, organize projects, plan and produce content on the plans board with
playbooks, and build reusable workflows — all without leaving your chat.

[marcora.ai](https://marcora.ai) · [MCP docs](https://marcora.ai/mcp)

## What's inside

| Component | What it does |
|---|---|
| **MCP server** (`marcora`) | Hosted, remote (streamable-HTTP) server at `https://mcp.marcora.ai`. Exposes the full Marcora toolset — content, projects, blueprints, Brand Foundation, Reference Library, community blueprints, content plans, playbooks, and workflows. |
| **Skill** `marcora-mcp` | The object model + the core product-marketing workflows; the content plans board and playbooks; building reusable multi-step workflows; applies Marcora's domain rules so the right artifact lands in the right place. |

Once installed, the skill invokes as `/marcora:marcora-mcp`, and Marcora's tools
appear as `mcp__marcora__*`. The skill is also model-invoked automatically when
your task calls for it.

## Install

```
/plugin marketplace add ccromp/marcora-mcp
/plugin install marcora@marcora
```

Then restart Claude Code (or run `/reload-plugins`).

## Authentication

The Marcora MCP server requires authentication. The plugin ships **OAuth-first**,
which needs no setup beyond a one-time browser login.

### OAuth (recommended — zero config)

On first connect the server returns `401`, and Claude Code flags it for
authentication. Run:

```
/mcp
```

…select **marcora**, and complete the browser login. Claude Code stores the
token **securely in your OS keychain** (or `~/.claude/.credentials.json` where a
keychain isn't available) and **refreshes it automatically**. Nothing is stored
in this repo or in plaintext config. To sign out later, use **Clear
authentication** in the `/mcp` menu (or `claude mcp logout marcora`).

### API token (for non-interactive / CI environments)

If you'd rather use a static API token, generate one at
[Integration Settings](https://app.marcora.ai/integration-settings) and add your
own server entry with an `Authorization` header — do **not** add the header to
the bundled plugin config, because a present `Authorization` header disables the
automatic OAuth fallback:

```bash
claude mcp add --transport http marcora https://mcp.marcora.ai \
  --header "Authorization: Bearer YOUR_API_TOKEN"
```

Or, to keep the token out of your shell history, reference an environment
variable in your `.mcp.json`:

```json
{
  "mcpServers": {
    "marcora": {
      "type": "http",
      "url": "https://mcp.marcora.ai",
      "headers": { "Authorization": "Bearer ${MARCORA_API_TOKEN}" }
    }
  }
}
```

## Companion skill

The skill is a meaningful upgrade over the bare tool definitions — install it
with the plugin and Claude will apply Marcora's operational patterns
automatically. See the
[MCP overview](https://marcora.ai/docs/mcp-overview#companion-anthropic-skills-recommended).

## Support

- Issues: https://github.com/ccromp/marcora-mcp/issues
- Docs: https://marcora.ai/mcp
