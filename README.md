# Marcora MCP Server

> Marcora is the context layer for go-to-market teams: your positioning, brand voice, and product facts in one source of truth that your AI tools read from.

**Learn more:** [marcora.ai](https://marcora.ai) · **Docs:** [marcora.ai/docs/mcp-overview](https://marcora.ai/docs/mcp-overview)

[![Add to Kiro](https://kiro.dev/images/add-to-kiro.svg)](https://kiro.dev/launch/mcp/add?name=marcora&config=%7B%22url%22%3A%22https%3A%2F%2Fmcp.marcora.ai%2F%22%7D)

## About

This is the **public documentation and plugin repository** for Marcora's hosted MCP server. The server itself is a commercial, closed-source remote service. This repo provides Portable Agent Plugin v1 metadata (`plugin.json` + `mcp.json`), the companion `marcora-mcp` workflow skill, connection instructions, tool documentation, and support resources.

| | |
|---|---|
| **Type** | Hosted remote MCP server |
| **Implementation** | Closed-source (commercial) |
| **Transport** | Streamable HTTP |
| **Authentication** | OAuth 2.1 (PKCE) or API token |
| **Status** | Production |

## What It Does

Marcora is the context layer for go-to-market teams. Build your source of truth once: a Brand Foundation (positioning, brand voice, and writing style) plus a Reference Library of product docs, buyer personas, competitive analysis, and messaging. Claude, ChatGPT, and any AI tool that supports MCP connections read from it, so what you write stays on-brand and accurate.

Marcora was formerly called MarketCore.

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

**Server URL (OAuth):** `https://mcp.marcora.ai/`

**Authentication options:**
- **OAuth 2.1 with PKCE** (recommended for interactive clients) — connect using `https://mcp.marcora.ai/`
- **API Token** (for non-interactive environments) — generate a key at [Integration Settings](https://app.marcora.ai/integration-settings) and connect to the same URL (`https://mcp.marcora.ai/`), passing the key in an `Authorization: Bearer <your-api-key>` header. The server negotiates the right transport automatically.

## Quickstart

Add to your MCP client config (`mcp.json` / `.kiro/settings/mcp.json` / `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "marcora": {
      "url": "https://mcp.marcora.ai/"
    }
  }
}
```

- **Kiro:** Click **Add to Kiro** above, or add the snippet to `~/.kiro/settings/mcp.json` (user) or `.kiro/settings/mcp.json` (workspace). Kiro signs in via browser OAuth on first connection.
- **Hermes Agent:** Run `hermes plugins install marcora` (or `hermes plugins install https://github.com/ccromp/marcora-mcp`) to install both the remote MCP server connection and the bundled `marcora-mcp` workflow skill.

See [docs/quickstart.md](docs/quickstart.md) for setup instructions for Claude, ChatGPT, Claude Desktop, Cursor, Kiro, Hermes Agent, and VS Code.

## The Marcora AI Workflows Skill (recommended)

The **Marcora AI Workflows** Anthropic Skill ships alongside this server. It teaches your AI client Marcora's mental model, the right tool sequencing, the questions to ask the user before acting, and the pitfalls to avoid — so the agent stops misfiring on tasks that look ambiguous from tool descriptions alone.

| Skill | What it covers | Source |
|---|---|---|
| **Marcora AI Workflows** (`marcora-mcp`) | A short core (object model, the 4-layer context model, which workflow fits which job, the rules every call needs) plus one reference file per workflow: generating content, projects and briefs, adding and finding context, Brand Foundation, grounding, content plans and playbooks, reusable multi-step workflows, blueprints, sharing and export, and choosing between similar tools | [`skill/marcora-mcp/`](skill/marcora-mcp/) |

Your AI client picks the skill up on demand based on the task.

### Install with the skills CLI

```bash
npx skills add ccromp/marcora-mcp
```

This installs the `marcora-mcp` skill for Claude Code and other agents that read `SKILL.md` skills. To preview first, run `npx skills add ccromp/marcora-mcp --list`.

### Download

Get the `.skill` file from the [latest release](https://github.com/ccromp/marcora-mcp/releases/latest):

- `marcora-mcp.skill` — the Marcora skill (a zip archive containing a short `SKILL.md` core plus one reference file per workflow under `references/`, which your AI client opens only when a task needs it).

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

These clients don't directly support Anthropic Skills (yet). Workaround: unzip the `.skill` file and paste the contents of `SKILL.md` into your client's custom instructions or system-prompt slot. `SKILL.md` names the reference file for each workflow: paste the ones you use most (for example `references/workflows.md` if you build Marcora workflows), or all of them if your client supports longer context.

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
| Account | `get_current_user_info` | Get profile, enabled `teams[]`, roles, subscription plans, credits, and member rosters |
| Account | `invite_user` | Invite a teammate or project collaborator to a team by email |
| Context & Resources | `get_brand_foundation` | Get team's Brand Foundation (company overview, voice, style, examples) |
| Context & Resources | `update_brand_foundation` | Overwrite one Brand Foundation element |
| Context & Resources | `list_context_collections` | List context collections |
| Context & Resources | `create_context_collection` | Create a new context collection |
| Context & Resources | `list_marcora_collections` | Browse published Marcora Collections (curated reference collections) |
| Context & Resources | `add_marcora_collection` | Add a Marcora Collection to your library |
| Context & Resources | `add_context` | Add a context item to your library |
| Context & Resources | `update_context` | Update an existing context item |
| Context & Resources | `list_context_items` | List context items in your library (optional semantic `search`) |
| Context & Resources | `get_context_item` | Get a context item's full markdown content |
| Context & Resources | `get_relevant_context` | Search context library by prompt (with optional `only_these_collections` filter; with a `project_id`, also returns the project's brief) |
| Context & Resources | `list_call_instructions` | List your standing call instructions (guidance and word fixes) and automatic call imports |
| Context & Resources | `add_call_instruction` | Save a standing call instruction (`guidance` or `word_fix`) for future calls |
| Context & Resources | `update_call_instruction` | Edit or switch on/off a standing call instruction |
| Context & Resources | `remove_call_instruction` | Permanently remove a standing call instruction |
| Context & Resources | `find_app` | Look up available third-party apps connected to Marcora |
| Enablement | `find_enablement_documents` | Find and browse curated Enablement Hub documents (visible when Enablement is on for a team) |
| Context Intelligence | `list_ci_findings` | List findings from automated context-library scans |
| Context Intelligence | `get_ci_finding` | Get one finding in full detail by UUID |
| Context Intelligence | `update_ci_finding_status` | Acknowledge, dismiss, or resolve a finding |
| Context Intelligence | `trigger_health_audit_scan` | Start a library-wide context health audit |
| Content Grounding | `check_content_grounding` | Check a document's claims against your context library |
| Content Grounding | `get_grounding_result` | Read a grounding scan's result (poll with `scan_id`) |
| Content Grounding | `apply_finding_fix` | Apply recommended fixes for grounding or health-audit findings by id |
| Reference | `list_content_categories` | List content categories |
| Reference | `list_targeting_dimensions` | List targeting dimensions and options |
| Reference | `learn_marcora_tools` | Search/read Marcora Documentation pages (`{}`, `page`, `query`) or compact `topic` sections |
| Blueprints | `list_blueprints` | List all blueprints |
| Blueprints | `get_blueprint` | Get blueprint details by UUID |
| Blueprints | `create_blueprint` | Create a reusable content template |
| Blueprints | `create_blueprint_draft` | Create an AI-assisted blueprint draft |
| Blueprints | `finalize_blueprint_draft` | Publish a blueprint draft |
| Community Blueprints | `list_community_blueprints` | Browse community templates |
| Community Blueprints | `get_community_blueprint_details` | Get community blueprint details |
| Community Blueprints | `import_community_blueprint` | Import a community blueprint |
| Content | `create_content` | Save a new document in the workspace: your own text by default, or written by Marcora (with or without blueprint) |
| Content | `get_generation_status` | Check async generation status |
| Content | `list_content` | List all content (optional semantic `search`) |
| Content | `get_content` | Get full content by ID |
| Content | `update_content` | Update a content document |
| Content | `ask_content_assistant` | Run the in-document Content Assistant on a document |
| Sharing & Export | `create_external_share` | Create a public share link (refused for Internal only documents; supports `confirm_private_sources`) |
| Sharing & Export | `get_share_link_activity` | List workspace share links (`share_link` omitted) or inspect one link's viewers and opens |
| Sharing & Export | `convert_markdown_to_word_doc` | Export markdown as Word doc |
| Projects | `list_projects` | List all projects |
| Projects | `get_project` | Get project details, including its brief |
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
| Plans & Playbooks | `instantiate_playbook` | Run a playbook into a cycle of plans (optionally anchored to a date, with a topic) |
| Plans & Playbooks | `list_playbook_suggestions` | List call-detected playbook suggestions (`suggested`, `started`, `dismissed`) |
| Plans & Playbooks | `dismiss_playbook_suggestion` | Dismiss a call-detected playbook suggestion (optionally saving a call rule) |
| Plans & Playbooks | `list_playbook_cycles` | List running playbook cycles with progress |
| Plans & Playbooks | `get_playbook_cycle` | Read one cycle with its ordered steps |
| Plans & Playbooks | `list_my_playbook_steps` | List open playbook steps assigned to you (or to a typed `owner_name`), soonest due first |
| Plans & Playbooks | `list_playbook_owner_names` | List the typed owner names in use on the team's playbook steps |
| Plans & Playbooks | `add_playbook_step` | Add a step to a running playbook cycle without changing its template |
| Plans & Playbooks | `update_playbook_step_status` | Mark a cycle step Complete (`action: "complete"`) or reopen a completed checklist step (`action: "reopen"`) |
| Plans & Playbooks | `update_playbook_cycle` | Rename a cycle and change its topic |
| Plans & Playbooks | `generate_cycle_content` | Generate the content for every step of a cycle that has none (uses Studio Credits) |
| Plans & Playbooks | `get_cycle_generation` | Check the progress of a cycle's "Generate all" batch |
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

## Security, Privacy & Runtime Disclosures

- **External service & authentication:** This package connects over HTTPS to Marcora's hosted MCP server at `https://mcp.marcora.ai/`. Connecting requires a Marcora account (a permanent Free tier is available at [marcora.ai/pricing](https://marcora.ai/pricing)) authenticated via OAuth 2.1 with PKCE (`/oauth/authorize`, `/oauth/token`, `/oauth/register`, `/oauth/revoke`) or a user-generated Bearer API token from [Integration Settings](https://app.marcora.ai/integration-settings).
- **Runtime tool surface (`77` tools) & Studio Credit costs:** At runtime, `https://mcp.marcora.ai/` serves **77 MCP tools**: **38 read-only tools** (`readOnlyHint: true`, `destructiveHint: false`, always free to call) and **39 non-read-only tools** (`readOnlyHint: false`, of which **19** have `destructiveHint: false` and **20** have `destructiveHint: true` because they overwrite existing records in place, trigger scans/workflows, or send team invites). Those 39 tools create or update team records or consume team Marcora Studio Credits when AI generation, scans, or Word exports run (`create_content` on the `instructions` generation path, `produce_plan`, `generate_cycle_content` (one generation per step), `create_blueprint_draft`, `create_project` with `project_brief_instructions`, `ask_content_assistant`, `check_content_grounding`, `trigger_health_audit_scan`, `convert_markdown_to_word_doc` at 2 Studio Credits per conversion, and `run_workflow`). Every team-scoped tool requires an explicit numeric `team_id` (and team-scoped writes echo `team: { id, name }`).
- **Server-side background agents, scheduled workflows & connected apps:** Calling `run_workflow` starts an automated agent session on Marcora's backend that executes the workflow's steps using Marcora tools and any third-party apps the user has connected in Marcora (`allowed_tools` on a workflow is a prompt instruction to the workflow runner, not a separate hard permission check). Workflows created (`create_workflow`) or activated (`update_workflow` with `status: "active"`) that have an `On` schedule are dispatched automatically by Marcora's server-side scheduler independently of the local MCP client. Calling `ask_content_assistant` starts an asynchronous background AI assistant run on an existing document that may edit the document body in place.
- **Advisory nature of MCP annotations & Hermes `trust: "untrusted"` scope:** MCP `ToolAnnotations` (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) are advisory hints; each MCP host decides whether and how to prompt for confirmation. In Hermes Agent, `plugin.json` declares `"trust": "untrusted"` and `"timeout": 180` on the `marcora` server so Hermes's host policy prompts before client-initiated calls to non-read-only tools, but client-side `trust: "untrusted"` and MCP annotations only govern calls initiated by the local client and do not prevent server-side scheduled workflow runs or background agent execution once a workflow is started or activated on Marcora.
- **Privacy Policy:** [marcora.ai/privacy-policy](https://marcora.ai/privacy-policy)
- **Terms of Service:** [marcora.ai/terms](https://marcora.ai/terms)
- **Security & Trust Center:** [marcora.ai/security](https://marcora.ai/security) and [docs/security.md](docs/security.md)

## Support

- **Email support:** [support@marcora.ai](mailto:support@marcora.ai)
- **Security disclosures:** [security@marcora.ai](mailto:security@marcora.ai)
- **Bug reports & feature requests:** [GitHub Issues](https://github.com/ccromp/marcora-mcp/issues)
- **Website:** [marcora.ai](https://marcora.ai)

## License

The documentation, skill, and metadata in this repository are licensed under the [MIT License](LICENSE). The Marcora MCP server implementation is proprietary and is not covered by that license or included in this repository.
