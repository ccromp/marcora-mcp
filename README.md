# Marcora MCP Server

> The context layer for GTM teams — one source of truth for brand and company context, so your whole team produces consistent, on-brand content in any AI tool. Connect your AI tools to [Marcora](https://marcora.ai) through the Model Context Protocol.

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

Marcora is the context layer for go-to-market teams — one source of truth for your brand and company context, so your whole team produces consistent, on-brand content in any AI tool. It stores your brand context, manages reusable content templates (blueprints), and generates marketing documents informed by your full company context. The MCP server brings all of this into your AI assistant — create content, manage context, browse community templates, and organize projects without leaving your chat.

Marcora's MCP server enables AI clients to:

- Manage brand and company context and reference materials
- Create and manage blueprints for content generation
- Generate marketing content from context and blueprints
- Organize work with projects and collections
- Browse and import community blueprints and templates
- Plan content on the plans board and produce it, individually or from reusable playbooks
- Automate recurring work with reusable, multi-step workflows
- Share content externally and export to Word

## Connection

**Server URL (OAuth):** `https://mcp.marcora.ai`

**Authentication options:**
- **OAuth 2.0** (recommended for interactive clients) — connect using `https://mcp.marcora.ai`
- **API Token** (for non-interactive environments) — generate a key at [Integration Settings](https://app.marcora.ai/integration-settings) and connect to the same URL (`https://mcp.marcora.ai`), passing the key in an `Authorization: Bearer <your-api-key>` header. The server negotiates the right transport automatically.

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

## Companion Anthropic Skill (recommended)

One companion **Anthropic Skill** ships alongside this server. It teaches your AI client Marcora's mental model, the right tool sequencing, the questions to ask the user before acting, and the pitfalls to avoid — so the agent stops misfiring on tasks that look ambiguous from tool descriptions alone.

| Skill | What it covers | Source |
|---|---|---|
| **Marcora AI Workflows** (`marcora-mcp`) | Object model (content, blueprints, projects, context items); content-generation patterns; the 4-layer context model; project-brief mechanics; the content plans board and playbooks; building reusable multi-step workflows; and choosing between similar tools | [`skill/marcora-mcp/`](skill/marcora-mcp/) |

Your AI client picks the skill up on demand based on the task.

### Download

Get the `.skill` file from the [latest release](https://github.com/ccromp/marcora-mcp/releases/latest):

- `marcora-mcp.skill` — the Marcora skill (a zip archive containing `SKILL.md` and its bundled reference files).

### Install

**Claude Code:**

```bash
# Download and unzip into your skills directory
mkdir -p ~/.claude/skills
unzip ~/Downloads/marcora-mcp.skill -d ~/.claude/skills/
```

Restart Claude Code. The skill loads automatically on any matching task.

**Claude Desktop:**

Import the `.skill` file via Claude Desktop's Skills folder. See [Anthropic's Skills documentation](https://support.anthropic.com/en/articles/agent-skills) for the current path on your platform.

**ChatGPT, Cursor, and other non-Anthropic clients:**

These clients don't directly support Anthropic Skills (yet). Workaround: unzip the `.skill` file and paste the contents of `SKILL.md` into your client's custom instructions or system-prompt slot. Bundled reference files can be pasted in too if your client supports longer context.

### Power-user install (clone and symlink)

If you'd rather track `main` directly:

```bash
git clone https://github.com/ccromp/marcora-mcp.git
ln -s "$(pwd)/marcora-mcp/skill/marcora-mcp" ~/.claude/skills/marcora-mcp
```

The unbundled skill source lives under [`skill/`](skill/).

### Releases

Releases are tagged `marcora-vX.Y.Z` — see [Releases](https://github.com/ccromp/marcora-mcp/releases). Each release attaches the bundled skill as `marcora-mcp.skill`. The skill's own version is the `metadata.version` field in its `SKILL.md`, and it moves independently of the release tag.

## Available Tools

| Category | Tool | Description |
|---|---|---|
| Account | `get_current_user_info` | Get profile, subscription, and usage info |
| Account | `get_team_info` | List every team you belong to + each team's members (numeric user_ids for assignment) |
| Account | `set_active_team` | Switch your active team (returns `previous_team_id` to restore) |
| Context & Resources | `get_brand_foundation` | Get team's Brand Foundation (company overview, voice, style, examples) |
| Context & Resources | `update_brand_foundation` | Overwrite one Brand Foundation element |
| Context & Resources | `list_context_collections` | List context collections |
| Context & Resources | `create_context_collection` | Create a new context collection |
| Context & Resources | `add_context` | Add a context item to your library |
| Context & Resources | `update_context` | Update an existing context item |
| Context & Resources | `list_context_items` | List context items in your library (optional semantic `search`) |
| Context & Resources | `get_context_item` | Get a context item's full markdown content |
| Context & Resources | `get_relevant_context` | Search context library by prompt |
| Context Intelligence | `list_ci_findings` | List findings from automated context-library scans |
| Context Intelligence | `get_ci_finding` | Get one finding in full detail by UUID |
| Context Intelligence | `update_ci_finding_status` | Acknowledge, dismiss, or resolve a finding |
| Context Intelligence | `trigger_health_audit_scan` | Start a library-wide context health audit |
| Content Grounding | `check_content_grounding` | Check a document's claims against your context library |
| Content Grounding | `get_grounding_result` | Read a grounding scan's result (poll with `scan_id`) |
| Content Grounding | `apply_grounding_fix` | Apply a finding's recommended fix by id |
| Reference | `list_content_categories` | List content categories |
| Reference | `list_targeting_dimensions` | List targeting dimensions and options |
| Blueprints | `list_blueprints` | List all blueprints |
| Blueprints | `get_blueprint` | Get blueprint details by UUID |
| Blueprints | `create_blueprint` | Create a reusable content template |
| Blueprints | `create_blueprint_draft` | Create an AI-assisted blueprint draft |
| Blueprints | `finalize_blueprint_draft` | Publish a blueprint draft |
| Community Blueprints | `list_community_blueprints` | Browse community templates |
| Community Blueprints | `get_community_blueprint_details` | Get community blueprint details |
| Community Blueprints | `import_community_blueprint` | Import a community blueprint |
| Content | `create_content` | Generate content (with or without blueprint) |
| Content | `get_generation_status` | Check async generation status |
| Content | `list_content` | List all content (optional semantic `search`) |
| Content | `get_content` | Get full content by ID |
| Content | `update_content` | Update a content document |
| Content | `ask_content_assistant` | Run the in-document Content Assistant on a document |
| Sharing & Export | `create_external_share` | Create a public share link |
| Sharing & Export | `convert_markdown_to_word_doc` | Export markdown as Word doc |
| Projects | `list_projects` | List all projects |
| Projects | `get_project` | Get project details |
| Projects | `create_project` | Create a new project |
| Projects | `update_project` | Update mutable fields on a project |
| Plans & Playbooks | `list_plans` | List content plans (with filters) |
| Plans & Playbooks | `get_plan` | Get plan details by UUID |
| Plans & Playbooks | `create_plan` | Create a new content plan |
| Plans & Playbooks | `update_plan` | Update a plan or transition its stage |
| Plans & Playbooks | `produce_plan` | Produce (generate) the content a plan describes |
| Plans & Playbooks | `list_playbooks` | List content playbooks |
| Plans & Playbooks | `get_playbook` | Get a playbook and its ordered items |
| Plans & Playbooks | `create_playbook` | Author a reusable playbook of plan items |
| Plans & Playbooks | `create_playbook_from_plans` | Capture existing plans as a playbook |
| Plans & Playbooks | `update_playbook` | Rename, re-describe, or restructure a playbook |
| Plans & Playbooks | `instantiate_playbook` | Run a playbook into a batch of plans (optionally anchored to a date) |
| Workflows | `list_workflows` | List workflows |
| Workflows | `get_workflow` | Get a workflow's full definition |
| Workflows | `create_workflow` | Create a new workflow template |
| Workflows | `update_workflow` | Update, activate, or archive a workflow |
| Workflows | `run_workflow` | Run a workflow now |
| Workflows | `get_workflow_runs` | Inspect workflow run history |

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
