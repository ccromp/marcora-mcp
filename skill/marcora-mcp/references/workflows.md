# Workflows (reusable multi-step processes)

Read this before calling any workflow tool (`create_workflow`, `update_workflow`, `run_workflow`, `get_workflow`, `list_workflows`, `get_workflow_runs`), or whenever the user wants something reusable, recurring or scheduled ("every Monday", "automate this", "make this a reusable process").

---

## Workflows — reusable, multi-step processes

A **workflow** lets the user describe a multi-step process once and run it reliably afterwards — manually on demand, on a schedule, or both — without re-explaining the steps each time.

> **Mindset:** a workflow is a *reusable, named process*. Some are scheduled (a daily digest, a weekly competitor sweep); many are not (a launch playbook, a customer-onboarding routine run on demand). **Both are first-class** — don't assume "workflow = recurring scheduled task."

### Signals the user wants a workflow

- **Process encapsulation / reusability** — "make this a reusable thing", "I do this every time we launch", "build me a playbook for…", "I want an agent that does X."
- **Re-running with different inputs** — "run this for our next competitor", "do this for each of these 5 customers."
- **Scheduling cues** — "every day", "every Monday morning", "weekly", "recurring", "automate this."
- **Watching for new things** — "whenever a new X appears, do Y with it" → a scheduled workflow with a `since_last_run` input binding.
- **Explicit mentions** of cron, webhooks, runners, or triggers.

If intent is ambiguous, ask: *"Do you want to run this once, or set it up as a reusable process you can run again later — manually, on a schedule, or both?"*

> **Workflow vs. Playbook — pick the right surface.** A **Playbook** (see `references/plans-and-playbooks.md`) produces a *batch of content plans* — an ordered set of things to write, landing on the plans board for a human to produce. A **Workflow** runs an *agent through arbitrary steps* (search, summarize, create content, send an email) in a background session. "Save this content sequence as a template" → playbook. "Every Monday, sweep competitor blogs and email me a digest" → workflow.

### The 6 workflow tools

(Not available in ChatGPT, where these six tools aren't offered; ask the Marcora agent in the Marcora app or in Slack, Microsoft Teams, Google Chat, or Discord. Every other client sees them.)

- **`create_workflow`** — Create a template. Inputs: `name`, `steps`, `description`, `inputs`, `allowed_tools`, `tags`, optional `schedule_config`. Saves the workflow **Inactive** by default (or keeps an allowed passed `status`) and any schedule **Paused**; the response carries a `next_step` saying what will and won't run.
- **`get_workflow`** — Read-only. Returns one workflow's name, description, status (Active / Inactive), steps, inputs, `allowed_tools` and tags, plus its triggers (including the schedule, if any) and latest run, and `run_state` (one sentence covering both switches) and `schedule` (its read-back, when it has one). Call before `update_workflow` to avoid clobbering unknown fields, and before saying whether a workflow runs.
- **`list_workflows`** — List the user's workflows (`status`, `search`, pagination). Call with `search:` before creating to spot duplicate names. The list does not show schedules — `status: "active"` in it does not mean a workflow is running.
- **`update_workflow`** — Partial update; send only keys you want to change. Who can update it: for a workflow set up from a template, the owner or a team admin if it is shared with the team, only the owner if it is private, and it changes through its setup (a direct edit returns `setup_required`); for any other workflow, only its creator (`created_by_user_id`). Anyone else gets an access-denied error. `status` accepts `"active"`, `"inactive"` or `"archived"` (soft-delete); anything else is refused and nothing is saved. It cannot edit a schedule or switch one On. When the call changes the status to Active or Inactive, the response carries a `next_step`.
- **`run_workflow`** — Manually run a workflow: creates a run record and starts an automated agent session that carries out the steps, using Marcora tools and the user's connected apps, instructed to use only the tools in `allowed_tools`. Who can run it: for a workflow set up from a template and shared with the team, any team member; if it is private, only its owner; for any other workflow, only its creator (`created_by_user_id`). Anyone else gets an access-denied error. Only an **Active** workflow runs; the schedule plays no part in a manual run. Inspect `.status`: `"running"` = success, `"failed"` = check `.error_reason`.
- **`get_workflow_runs`** — Run history. Pass `run_id` for single-run detail (step logs + tool-call logs); omit for a paginated list.

### Building well

1. **Confirm intent before creating.** Restate the workflow in one or two sentences; call `create_workflow` only after the user agrees.
2. **Confirm where the result lands — BEFORE creating.** Workflows run in a background runner with no live chat surface. Every run writes a markdown summary to its run-detail page, but most workflows also send output somewhere. Ask which of:
   - **(a) An external destination** — depending on the user's connected integrations: `create_content`, `add_context`, `create_project`, `update_context`, `create_external_share`, or connected apps: send an email (Gmail), post a message (Slack, Teams, Discord), create a task (Google Tasks, Asana, Linear), or write to Google Docs, Sheets or Notion.
   - **(b) Run summary only** — the user just reads the result on the run-detail page. Legitimate for "look something up / summarize / find me" workflows. Restate it back so they know where to look.
3. **Translate steps into plain-language `{name, description}` entries** specific enough that a fresh agent can act without follow-up. Add `agent_hint` for non-obvious guidance. Tool names in step descriptions render as chips — write them in canonical `SCREAMING_SNAKE_CASE`.
4. **Set `allowed_tools` narrowly** (3–6 tools). It is the list of tools the runner agent is instructed to use. The call is rejected if `allowed_tools` is missing or empty — even summary-only workflows need read tools spelled out (e.g. `web_search`, `web_browse`).
5. **Two switches, two vocabularies — never mix them.** The workflow is **Active** or **Inactive** (or Archived). Its schedule, if it has one, is **On** or **Paused**. Never call a schedule "active" or "inactive", and never call a workflow "paused" or "on". Whenever you say a workflow is Active, say in the same sentence whether its schedule is On, Paused, or absent — "Active" alone only means the workflow is *allowed* to run.
   - **What runs needs both switches:** a scheduled run needs the workflow Active **and** the schedule On. A manual run (`run_workflow`) needs only Active.
   - Inactive → nothing runs, by any route (manual runs are refused too). Active with no schedule → runs only when started manually. Active with the schedule Paused → manual runs work, but it won't run on its schedule until the user clicks **Resume schedule** in the app. Active with the schedule On → runs on its schedule. Inactive with the schedule On → nothing runs until the workflow is set Active.
   - **`create_workflow` saves the workflow Inactive by default** (unless an allowed `status` is passed) and any schedule Paused. Setting it Active is fine once the user has asked for that — call `update_workflow status:"active"` and describe the state after *that* call (its `next_step`), not the state `create_workflow` reported.
   - **Lead your reply with the tool's `next_step` / `run_state`.** They are computed from what was actually saved, so they are the authority on what will and won't run. If the schedule is already On, activating the workflow starts its scheduled runs — say so before you do it, and after.
6. **Scheduling is optional — and a schedule is always saved Paused.** Skip `schedule_config` entirely for manual/on-demand workflows.
   - **Preferred (v2 local-time calendar) shape:** `{"version": 2, "frequency": "daily"|"weekly", "time": "HH:MM", "timezone": "<the user's IANA zone>", "days": [<0=Sun…6=Sat, local>]}` (`days` is required for `weekly` with 1–7 distinct local weekdays, e.g. `[1,3,5]` for Mon/Wed/Fri; omit for `daily`). Pass the user's local 24-hour `HH:MM` time, local weekdays, and IANA timezone directly — do **not** convert to UTC (v2 preserves exact minutes and local time across daylight saving changes).
   - **Legacy v1 calendar / interval shapes:** older clients may still send v1 (`hour` 0–23 UTC + `days_of_week`/`day_of_week` UTC, with display-only `timezone`) or interval mode (omit `version: 2` and `hour`, pass `interval_hours`, or rely on 1h / 24h / 168h default for hourly / daily / weekly). Interval mode runs every N hours with no fixed time of day (first run one interval after switching On) and cannot be shown or edited in the app's editor — use it only when calendar mode can't express the need.
   - **No MCP tool can switch a schedule On.** `update_workflow` silently ignores `schedule_config` and still returns success. Tell the user the schedule is Paused, hand them the workflow's `link_url` exactly as returned, and ask them to review it and click **Resume schedule**. Quote `schedule.summary` when you describe what was saved.
   - **The app's editor offers:** Daily at a set time, or Weekly on one or more days at a set time (it has a weekday picker). It cannot hold a second time of day or an every-N-hours interval, and cron expressions are not supported. If the user asks for something it genuinely can't express ("twice a day"), say exactly what you saved and that it is an approximation.
7. **For workflows that process entities over time** ("summarize new content each week"), be explicit about dedup BEFORE creating: use a `since_last_run` input binding (Marcora computes the window from the last successful run — don't compute it yourself), match schedule cadence to lookback, and write source entity IDs into downstream artifacts so a future run can tell what it already processed. Raise this proactively if the user doesn't.

### What the runner writes to its run summary

The runner agent's FINAL message becomes the run's summary (rendered as markdown on the run-detail page). Instruct it to: format in markdown, lead with a one-line conclusion, and **link back to anything created** (most Marcora tools return a `url`/`link` — include it). For summary-only workflows, the summary IS the output — make it complete.

**Setting the run's status:** tell the runner to start its final message with one of these prefixes — `Workflow complete: <md>` → succeeded · `Partial completion: <md>` → succeeded (partial) · `SKIP: <reason>` → skipped · `FAIL: <reason>` → failed. With no prefix, the final message is used as the run summary as-is.

### Risk warnings

- **Set a workflow Active when the user has asked for it, and tell them what that does.** Activating is not the risk; an inaccurate reply is. With the schedule On, activating starts scheduled runs — say so. With it Paused, the workflow can be run manually but still won't run on its schedule. Never tell the user a workflow will run on its own unless it is Active and its schedule is On.
- **Setting a workflow Inactive keeps its schedule exactly as it was.** A schedule that was On is still On and fires again as soon as the workflow is Active. To stop scheduled runs but keep manual runs, the user pauses the schedule in the app — there is no `"paused"` workflow status.
- **Hard-delete isn't exposed** — use `update_workflow status:"archived"`. Restore with `status:"inactive"` or `status:"active"`.
- **Duplicate names aren't prevented** — `list_workflows search:"<name>"` first if re-creating is possible.
- **Schedule edits via MCP are NOT supported** — changing a schedule, and switching it On or Paused, happen in the app. Direct the user there with the workflow's `link_url`.
- **Document update proposals from workflows** — inspect with `list_document_updates` / `get_document_update` and approve or discard interactively with `approve_document_update` / `discard_document_update` (not available in ChatGPT; background runner sessions cannot approve or discard).
- **Runner sessions don't author workflows** — these 6 tools are for interactive sessions; a runner executing a scheduled run uses a different tool set and must not call `create_workflow`/`update_workflow`.

---

## E20 — Updating or manually running a teammate's workflow (`update_workflow` / `run_workflow`)

**Symptom.** `marcora:update_workflow` or `marcora:run_workflow` returns an access-denied error even though the caller is an Admin or Creator, or `marcora:update_workflow` returns `setup_required`.

**Cause.**
- **Workflow set up from a template:** for `run_workflow`, any team member can run it when shared with the team, while only its owner can run a private one; for `update_workflow`, the owner or a team admin can update a team-shared one and only the owner can update a private one, and it changes through its setup (a direct edit returns `setup_required`).
- **Any other workflow:** only its creator (`created_by_user_id`) can update it or run it manually; anyone else gets an access-denied error.

**What to do.** If `update_workflow` returns `setup_required`, direct the user to update or activate it through the workflow's setup in the Marcora app (`link_url`). Otherwise check `created_by_user_id` on `get_workflow` / `list_workflows` against `get_current_user_info`, explain who can run or update the workflow, or offer to create a new workflow (`create_workflow`).
