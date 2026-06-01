# Marcora MCP Server

> AI-powered product context management — connect your AI tools to [Marcora](https://marcora.ai) through the Model Context Protocol.

[![smithery badge](https://smithery.ai/badge/chris-2acp/marcora)](https://smithery.ai/servers/chris-2acp/marcora)

**Learn more:** [marcora.ai](https://marcora.ai) · **Smithery:** [smithery.ai/servers/chris-2acp/marcora](https://smithery.ai/servers/chris-2acp/marcora)

## About

This is the **public documentation repository** for Marcora's hosted MCP server. The server itself is a commercial, closed-source remote service. This repo provides metadata, connection instructions, tool documentation, and support resources.

| | |
|---|---|
| **Type** | Hosted remote MCP server |
| **Implementation** | Closed-source (commercial) |
| **Transport** | Streamable HTTP |
| **Authentication** | OAuth 2.0 or API token |
| **Status** | Production |

## What It Does

Marcora is a product context management platform for go-to-market teams. It stores your brand context, manages reusable content templates (blueprints), and generates marketing documents informed by your full product knowledge. The MCP server brings all of this into your AI assistant — create content, manage context, browse community templates, and organize projects without leaving your chat.

Marcora's MCP server enables AI clients to:

- Manage product context and reference materials
- Create and manage blueprints for content generation
- Generate marketing content from context and blueprints
- Organize work with projects and collections
- Browse and import community blueprints and templates
- Share content externally and export to Word

## Connection

**Server URL (OAuth):** `https://mcp.marcora.ai`

**Authentication options:**
- **OAuth 2.0** (recommended for interactive clients) — connect using `https://mcp.marcora.ai`
- **API Token** (for non-interactive environments) — generate a key at [Integration Settings](https://app.marcora.ai/integration-settings) and use one of the API key URLs below

**API Key URLs:**

| Transport | URL |
|---|---|
| SSE | `https://api.marketcore.ai/x2/mcp/EbZaDl-X/mcp/sse` |
| Streamable HTTP | `https://api.marketcore.ai/x2/mcp/EbZaDl-X/mcp/stream` |

## Quickstart

Add to your MCP client config:

```json
{
  "mcpServers": {
    "marcora": {
      "url": "https://mcp.marcora.ai"
    }
  }
}
```

See [docs/quickstart.md](docs/quickstart.md) for setup instructions for Claude, ChatGPT, Claude Desktop, Cursor, and VS Code.

## Companion Anthropic Skills (recommended)

Two companion **Anthropic Skills** ship alongside this server. Together they teach your AI client Marcora's mental model, the right tool sequencing, the questions to ask the user before acting, and the pitfalls to avoid — so the agent stops misfiring on tasks that look ambiguous from tool descriptions alone.

| Skill | What it covers | Source |
|---|---|---|
| **Marcora AI Workflows** (`marcora-mcp`) | Object model (content, blueprints, projects, context items), content-generation patterns, the 4-layer context model, project-brief mechanics, choosing between similar tools | [`skill/marcora-mcp/`](skill/marcora-mcp/) |
| **Marcora Workflow Builder** (`marcora-workflow-builder`) | The 6 workflow MCP tools (`create_workflow`, `update_workflow`, `run_workflow`, `get_workflow`, `list_workflows`, `get_workflow_runs`), output destinations, scheduling, deduplication patterns, runner-summary conventions | [`skill/marcora-workflow-builder/`](skill/marcora-workflow-builder/) |

The two skills are independent — your AI client picks them up on demand based on the task. Install both for the full experience.

### Download

Get the `.skill` files from the [latest release](https://github.com/ccromp/marcora-mcp/releases/latest):

- `marcora-mcp.skill` — the core Marcora skill
- `marcora-workflow-builder.skill` — the workflow-building skill

Each `.skill` file is a zip archive containing `SKILL.md` and any bundled reference files.

### Install

**Claude Code:**

```bash
# Download and unzip into your skills directory
mkdir -p ~/.claude/skills
unzip ~/Downloads/marcora-mcp.skill -d ~/.claude/skills/
unzip ~/Downloads/marcora-workflow-builder.skill -d ~/.claude/skills/
```

Restart Claude Code. The skills load automatically on any matching task.

**Claude Desktop:**

Import each `.skill` file via Claude Desktop's Skills folder. See [Anthropic's Skills documentation](https://support.anthropic.com/en/articles/agent-skills) for the current path on your platform.

**ChatGPT, Cursor, and other non-Anthropic clients:**

These clients don't directly support Anthropic Skills (yet). Workaround: unzip a `.skill` file and paste the contents of `SKILL.md` into your client's custom instructions or system-prompt slot. Bundled reference files can be pasted in too if your client supports longer context.

### Power-user install (clone and symlink)

If you'd rather track `main` directly:

```bash
git clone https://github.com/ccromp/marcora-mcp.git
ln -s "$(pwd)/marcora-mcp/skill/marcora-mcp" ~/.claude/skills/marcora-mcp
ln -s "$(pwd)/marcora-mcp/skill/marcora-workflow-builder" ~/.claude/skills/marcora-workflow-builder
```

The unbundled skill source lives under [`skill/`](skill/).

### Releases

Skill releases are tagged independently per skill:
- `marcora-mcp` skill: `skill-vX.Y.Z` (legacy prefix kept for continuity) — see [Releases](https://github.com/ccromp/marcora-mcp/releases).
- `marcora-workflow-builder` skill: `workflow-builder-vX.Y.Z`.

The current version of each skill is in the `metadata.version` field of its `SKILL.md`.

## Available Tools

| Category | Tool | Description |
|---|---|---|
| Account | `get_current_user_info` | Get profile, subscription, and usage info |
| Context & Resources | `get_brand_foundation` | Get team's Brand Foundation (company overview, voice, style, examples) |
| Context & Resources | `update_brand_foundation` | Overwrite one Brand Foundation element |
| Context & Resources | `get_context_collections` | List context collections |
| Context & Resources | `create_context_collection` | Create a new context collection |
| Context & Resources | `add_context` | Add a context item to your library |
| Context & Resources | `get_relevant_context` | Search context library by prompt |
| Reference | `get_content_categories` | List content categories |
| Reference | `get_targeting_dimensions` | List targeting dimensions and options |
| Blueprints | `get_blueprints` | List all blueprints |
| Blueprints | `get_blueprint` | Get blueprint details by UUID |
| Blueprints | `create_blueprint` | Create a reusable content template |
| Blueprints | `create_blueprint_draft` | Create an AI-assisted blueprint draft |
| Blueprints | `finalize_blueprint_draft` | Publish a blueprint draft |
| Community Blueprints | `get_community_blueprints` | Browse community templates |
| Community Blueprints | `get_community_blueprint_details` | Get community blueprint details |
| Community Blueprints | `import_community_blueprint` | Import a community blueprint |
| Content | `create_content` | Generate content (with or without blueprint) |
| Content | `get_generation_status` | Check async generation status |
| Content | `get_content_list` | List all content |
| Content | `get_content` | Get full content by ID |
| Sharing & Export | `create_external_share` | Create a public share link |
| Sharing & Export | `convert_markdown_to_word_doc` | Export markdown as Word doc |
| Projects | `get_projects` | List all projects |
| Projects | `get_project` | Get project details |
| Projects | `create_project` | Create a new project |

See [docs/tools.md](docs/tools.md) for the complete tool reference.

## Documentation

- [Overview](docs/overview.md)
- [Quickstart](docs/quickstart.md)
- [Authentication](docs/authentication.md)
- [Tools Reference](docs/tools.md)
- [Errors & Troubleshooting](docs/errors.md)
- [Security & Privacy](docs/security.md)
- [Changelog](docs/changelog.md)
- [Support](docs/support.md)
- [Marcora Website Documentation](https://marcora.ai/mcp)

## Security & Privacy

See [docs/security.md](docs/security.md) for details on data handling, permissions, and responsible disclosure.

## Support

- **Bug reports & feature requests:** [GitHub Issues](https://github.com/ccromp/marcora-mcp/issues)
- **Website:** [marcora.ai](https://marcora.ai)

## License

This repository contains documentation and metadata only. The Marcora MCP server implementation is proprietary and not included.

Documentation is licensed under [CC BY 4.0](LICENSE).
