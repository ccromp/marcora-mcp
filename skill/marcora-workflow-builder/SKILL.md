---
name: marcora-workflow-builder
description: Use this skill whenever the user wants to build, modify, run, or troubleshoot a Marcora workflow — a reusable, multi-step process the user can run on demand or on a schedule. Triggers on phrases like "every day", "every week", "on a schedule", "recurring", "automate this", and ALSO on "playbook", "make this reusable", "I want an agent that does X", "set this up so I can run it again later", or any request to encapsulate a sequence of work so it can be re-run consistently. Covers the 6 workflow MCP tools, choosing where the output should land, scheduling, deduplication patterns, and what the runner should write to its run summary.
license: CC-BY-4.0
metadata:
  mcp-server: marcora
  version: 0.1.0
---

# Marcora Workflow Builder

*The companion skill to the Marcora MCP server, focused on workflows.*

You can help the user build, modify, and run Marcora **workflows**. A workflow lets the user describe a multi-step process once and run it reliably afterwards — manually on demand, on a schedule, or both — without re-explaining the steps each time.

> **Mindset:** A workflow is a *reusable, named process*. Some workflows are scheduled (a daily digest, a weekly competitor sweep). Many are not (a launch playbook, a customer-onboarding routine the user wants to run on demand). Both are first-class. Don't assume "workflow = recurring scheduled task" — the user's intent might be either, and the skill applies to both.

---

## Signals that the user wants a workflow

Listen for these patterns:

- **Process encapsulation / reusability.** "Make this a reusable thing", "I do this every time we launch", "Can you set this up so I can run it again next quarter?", "Build me a playbook for…", "I want an agent that does X."
- **Re-running with different inputs.** "Take what we just made and run it for our next competitor", "Do this for each of these 5 customers."
- **Scheduling cues.** "Every day", "every Monday morning", "weekly", "on a schedule", "recurring", "automate this."
- **Watching for new things.** "Whenever a new X appears, do Y with it" — a scheduled workflow with a `since_last_run` input binding.
- **Explicit mentions** of cron, webhooks, runners, or triggers.

If the intent is ambiguous, ask: *"Do you want to run this once, or set it up as a reusable process you can run again later — manually, on a schedule, or both?"*

---

## Your 6 MCP tools (marcora server)

- **`create_workflow`** — Create a new workflow template. Inputs: `name`, `steps`, `description`, `inputs`, `allowed_tools`, `tags`, optional `schedule_config`. Always creates as `status="draft"`.
- **`get_workflow`** — Fetch one workflow with triggers + latest run. Call before `update_workflow` to avoid clobbering unknown fields.
- **`list_workflows`** — List the user's workflows. Supports `status`, `search`, pagination. Call with `search:` before creating to spot duplicate names.
- **`update_workflow`** — Partial update. Send only the keys you want to change. Use `status: "active"` to activate, `status: "archived"` to soft-delete.
- **`run_workflow`** — Manually dispatch a workflow run. Inspect `.status` on the returned row: `"running"` = success, `"failed"` = check `.error_reason`.
- **`get_workflow_runs`** — Inspect run history. Pass `run_id` for single-run detail with step logs and tool call logs; omit `run_id` for a paginated list.

The MCP tool definitions document each parameter — don't restate them. This skill covers the workflow patterns, the user-facing decisions, and the gotchas the schemas can't.

---

## Building well

1. **Confirm intent before creating.** Restate the workflow back to the user in one or two sentences. Only call `create_workflow` after they agree.

2. **Confirm where the result should land.** Workflows execute in a background runner session — there is no chat surface for the user to watch results in real time. Every run produces a markdown summary on the workflow's run-detail page, but most workflows also send the result somewhere else. ASK the user where they want the output to land BEFORE calling `create_workflow`. Two valid answers:
   - **(a) An external destination** — depending on which integrations the user has connected, examples may include `create_content` (a new content piece in Marcora), `add_context` (add to a Context Collection), `create_project`, `update_context`, `create_external_share`, GMAIL_SEND_EMAIL / Slack / Teams / Discord, GOOGLETASKS_INSERT_TASK / Asana / Linear, Google Docs / Sheets / Notion. The actual options depend on the user's connected toolkits.
   - **(b) Run summary only** — the user just wants to read the result in the workflow's run-detail page (the markdown summary the runner produces). This is a legitimate choice for "look something up", "summarize X", "find me Y" workflows. If the user picks this path, restate it back: *"Got it — this will write its result to the run summary on the workflow detail page, and you'll read it there. Sound good?"*

   Don't call `create_workflow` until you have a clear answer (a or b). The backend rejects empty `allowed_tools` with `allowed_tools_required` regardless — even a summary-only workflow needs read tools spelled out (e.g. `web_search`, `web_browse`).

3. **Translate steps into plain-language `{name, description}` entries.** Each step's `description` must be specific enough that a fresh agent can act on it without follow-up questions. Include `agent_hint` for non-obvious execution guidance. Tool names that appear in step descriptions render as inline code chips in the UI; write them in their canonical SCREAMING_SNAKE_CASE form (e.g. `GMAIL_SEND_EMAIL`).

4. **Set `allowed_tools` narrowly.** Prefer explicit short allowlists (3–6 tools). The runner inherits Marcora's tool set otherwise; an empty list is rejected by the backend.

5. **Always create as `status="draft"` first.** Then walk the user through the definition; only call `update_workflow` with `status: "active"` once they confirm.

6. **Scheduling is optional.** For workflows the user wants on a clock, set `schedule_config: {"frequency": "daily"|"weekly"|"hourly", "interval_hours": N, "timezone": "UTC"}`. The trigger is created with `is_enabled=false`; the user activates it from the UI. Cron expressions are not supported in v1. **Skip `schedule_config` entirely for manual-only / on-demand workflows** — those are perfectly valid and the user runs them via the UI's "Run now" button or via `run_workflow`.

7. **For workflows that process entities over time** (e.g., "summarize new content each week", "pull recent Gong calls about competitor X"), be EXPLICIT with the user about how duplicates will be avoided BEFORE creating:
   - **Time-window via `since_last_run`** — describe the input binding to the user as "since last successful run". The scheduler and resolver compute the window automatically from the trigger's `last_successful_run_at`. Don't compute it yourself.
   - **Schedule cadence should match the lookback** — weekly schedule looks at the last week of data; daily at the last day.
   - **Write source IDs into downstream artifacts** — when a step creates content, a context item, etc. from a source entity, include the source entity's external ID inside the new artifact so a future run could detect "I already processed this".
   - **Raise it proactively.** If the user describes a workflow where this matters but doesn't ask, surface it: *"If this runs every day but pulls 'recent' data, we could process the same items more than once. I'll set this up so it only sees things new since the last successful run, and tags each new item with the source ID so we can tell what we've already covered. Sound right?"*

---

## What the runner should write to its run summary

Workflow steps are executed by a runner agent in a background session. The runner's FINAL agent message becomes the workflow run's `result_summary`, which the user reads on the workflow's run-detail page. When you write step descriptions or `agent_hint`s, instruct the runner to:

- **Format the final summary in markdown** (headings, bullet lists, **bold**, *italic*, links). The detail page renders the markdown as HTML.
- **Lead with a short concluding sentence** — what was done, what was found, what was created. Then optional supporting detail.
- **Always link back to anything created or touched in Marcora.** Most Marcora MCP tools return a `url` or `link` field in their response — include it in the summary as a markdown link so the user can jump straight to the artifact (e.g. `[New blog post: How AI rewrites GTM](https://app.marcora.ai/library/abc123)`). The same applies to anything created in connected integrations that returns a URL (Google Docs, Notion pages, Linear issues, etc.).
- **For "summary only" workflows** (option 2b above), the summary IS the deliverable. Make it complete enough to act on without opening anything else — include the actual findings, not just "I searched for X and found 5 results."

### Marker prefixes the runner can use

The relay parses these prefixes from the runner's final message and sets the `workflow_run` status:

- `Workflow complete: <markdown>` → status = succeeded, `result_summary` = markdown
- `Partial completion: <markdown>` → status = succeeded with partial flag
- `SKIP: <reason>` → status = skipped (e.g., the input resolver returned no entities to process)
- `FAIL: <reason>` → status = failed

If no prefix is found, the runner's final message becomes `result_summary` as-is.

---

## Risk warnings

- **Don't create active workflows without explicit user confirmation.** A workflow that fires on a schedule is long-lived state — always get a "yes" before activating. (On-demand workflows can stay in draft until the user explicitly says "make it active".)
- **Hard-delete is not exposed.** Use `update_workflow status: "archived"` instead. If the user asks to "delete" a workflow, archive it and note that it can be restored via `update_workflow status: "draft"` or `"active"`.
- **Duplicate-name workflows are not prevented at the DB level.** If the user might be re-creating something, call `list_workflows search: "<name>"` first.
- **Schedule changes via MCP tools are NOT supported in v1.** If the user asks to change a workflow's schedule, direct them to the workflow's settings UI.
- **Runner sessions do NOT author workflows.** These 6 tools are for you (Marcora) in interactive sessions. A runner working through a scheduled execution uses a different tool set and should not call `create_workflow` or `update_workflow`.

---

## See also

For broader Marcora object-model and content-creation patterns (blueprints, projects, briefs, context items, generation), the `marcora-mcp` skill is the authority. This skill assumes you already have that context and focuses solely on the workflow surface.
