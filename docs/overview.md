# Overview

Marcora is the context layer for go-to-market teams — one source of truth for brand and company context, so your whole team produces consistent, on-brand content in any AI tool. It stores your brand context, manages reusable content templates (blueprints), and generates documents informed by your full company context.

The Marcora MCP Server exposes all of your Marcora tools directly inside AI assistants like Claude and ChatGPT, letting you create blueprints, generate content, manage context, and more — without leaving your AI chat.

## Connection URL

```
https://mcp.marcora.ai
```

This is the primary URL for connecting to the Marcora MCP Server. It uses **OAuth authentication**, making it ideal for use with Claude, ChatGPT, and other interactive AI clients.

## Alternative API Key Access

For MCP clients where supplying an API key directly is simpler than OAuth, connect to the same URL (`https://mcp.marcora.ai`) and pass your key in an `Authorization: Bearer <your-api-key>` header — the server negotiates the right transport automatically. You can create and manage your MCP API keys in [Integration Settings](https://app.marcora.ai/integration-settings).

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
