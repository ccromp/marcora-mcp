# Overview

Marcora is the context layer for go-to-market teams — one source of truth for brand and company context, so your whole team produces consistent, on-brand content in any AI tool. It stores your brand context, manages reusable content templates (blueprints), and generates documents informed by your full company context.

The Marcora MCP Server exposes Marcora's tools directly inside AI assistants like Claude and ChatGPT, letting you create blueprints, generate content, manage context, share documents and see whether they were opened, and more — without leaving your AI chat. Available tools vary by client: ChatGPT doesn't include the six workflow tools (set workflows up in the Marcora app), and Slack hides the three blueprint-building tools (create blueprints in the Marcora app).

## Team Scoping (`team_id`)

Because you can belong to more than one Marcora team, there is no global active team on external MCP connections — selecting a `team_id` in one chat won't affect another app tab or client. Instead:

- **Call `get_current_user_info` first** (or read the server's `initialize` instructions) to inspect `teams[]`, which lists every enabled team you belong to (`team_id`, `team_name`, `your_role`, Studio Credit balances, subscription plan, and `members[]` rosters).
- **Pass `team_id` on every team-scoped tool call.** Almost all brand tools require an explicit positive integer `team_id`. Six non-team-scoped tools take no `team_id`: `get_current_user_info`, `learn_marcora_tools`, `list_community_blueprints`, `get_community_blueprint_details`, `list_marcora_collections`, and `add_marcora_collection`.
- **Share-link activity:** use `get_share_link_activity` with `team_id` to both list tracked share links in a team (omit `share_link`) and inspect open activity for one link (pass `share_link`).

## Connection URL

```
https://mcp.marcora.ai
```

This is the primary URL for connecting to the Marcora MCP Server. It uses **OAuth authentication**, making it ideal for use with Claude, ChatGPT, and other interactive AI clients.

## Alternative API Key Access

For MCP clients where supplying an API key directly is simpler than OAuth, connect to the same URL (`https://mcp.marcora.ai`) and pass your key in an `Authorization: Bearer <your-api-key>` header — the server negotiates the right transport automatically. You can create, rename, and manage your MCP connections and API keys in [Integration Settings](https://app.marcora.ai/integration-settings) (`Settings → Integrations → MCP`), which also shows which app connected (`Claude`, `ChatGPT`, `HubSpot`, `Cursor`, `Gong`, or `Other app`).

## Who Is This For?

- **Marketing teams** using AI assistants who want direct access to their Marcora context and content
- **Developers** building AI-powered workflows that integrate with Marcora
- **Agencies** managing multiple client accounts through AI tools

## What You Can Do

Through the MCP server, AI clients can:

- **Manage context** — Store and retrieve brand voice, product details, competitive intelligence, and other reference materials
- **Create blueprints** — Build reusable AI content templates with structure, tone, and style guidance
- **Generate content** — Produce marketing documents from scratch or from blueprints, informed by your full company context
- **Organize with projects** — Group related content and context into workstreams
- **Browse the community** — Discover and import blueprint templates shared by other Marcora users
- **Share and export** — Create public share links and export documents as Word files

## Architecture

The Marcora MCP Server is a hosted, remote MCP server. There is nothing to install or run locally — your AI client connects directly to Marcora's server over HTTPS.

| | |
|---|---|
| **Transport** | Streamable HTTP |
| **Authentication** | OAuth 2.0 or API token |
| **Status** | Production |
