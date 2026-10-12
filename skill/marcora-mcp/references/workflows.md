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

- **`create_workflow`** — Create a template. Inputs: `name`, `steps`, `description`, `inputs`, `allowed_tools`, `tags`, optional `schedule_config`. Saves the workflow **Inactive** and any schedule **Paused**; the response carries a `next_step` saying what will and won't run.
- **`get_workflow`** — Fetch one workflow with triggers + latest run, plus `run_state` (one sentence covering both switches) and `schedule` (its read-back, when it has one). Call before `update_workflow` to avoid clobbering unknown fields, and before saying whether a workflow runs.
- **`list_workflows`** — List the user's workflows (`status`, `search`, pagination). Call with `search:` before creating to spot duplicate names. The list does not show schedules — `status: "active"` in it does not mean a workflow is running.
- **`update_workflow`** — Partial update; send only keys you want to change. `status` accepts `"active"`, `"inactive"` or `"archived"` (soft-delete); anything else is refused and nothing is saved. It cannot edit a schedule or switch one On. When the call changes the status to Active or Inactive, the response carries a `next_step`.
- **`run_workflow`** — Manually dispatch a run. Only an **Active** workflow runs; the schedule plays no part in a manual run. Inspect `.status`: `"running"` = success, `"failed"` = check `.error_reason`.
- **`get_workflow_runs`** — Run history. Pass `run_id` for single-run detail (step logs + tool-call logs); omit for a paginated list.

### Building well

1. **Confirm intent before creating.** Restate the workflow in one or two sentences; call `create_workflow` only after the user agrees.
2. **Confirm where the result lands — BEFORE creating.** Workflows run in a background runner with no live chat surface. Every run writes a markdown summary to its run-detail page, but most workflows also send output somewhere. Ask which of:
   - **(a) An external destination** — depending on the user's connected integrations: `create_content`, `add_context`, `create_project`, `update_context`, `create_external_share`, or connected apps: send an email (Gmail), post a message (Slack, Teams, Discord), create a task (Google Tasks, Asana, Linear), or write to Google Docs, Sheets or Notion.
   - **(b) Run summary only** — the user just reads the result on the run-detail page. Legitimate for "look something up / summarize / find me" workflows. Restate it back so they know where to look.
3. **Translate steps into plain-language `{name, description}` entries** specific enough that a fresh agent can act without follow-up. Add `agent_hint` for non-obvious guidance. Tool names in step descriptions render as chips — write them in canonical `SCREAMING_SNAKE_CASE`.
4. **Set `allowed_tools` narrowly** (3–6 tools). The call is rejected if `allowed_tools` is missing or empty — even summary-only workflows need read tools spelled out (e.g. `web_search`, `web_browse`).
5. **Two switches, two vocabularies — never mix them.** The workflow is **Active** or **Inactive** (or Archived). Its schedule, if it has one, is **On** or **Paused**. Never call a schedule "active" or "inactive", and never call a workflow "paused" or "on". Whenever you say a workflow is Active, say in the same sentence whether its schedule is On, Paused, or absent — "Active" alone only means the workflow is *allowed* to run.
   - **What runs needs both switches:** a scheduled run needs the workflow Active **and** the schedule On. A manual run (`run_workflow`) needs only Active.
   - Inactive → nothing runs, by any route (manual runs are refused too). Active with no schedule → runs only when started manually. Active with the schedule Paused → manual runs work, but it won't run on its schedule until the user clicks **Resume schedule** in the app. Active with the schedule On → runs on its schedule. Inactive with the schedule On → nothing runs until the workflow is set Active.
   - **`create_workflow` saves the workflow Inactive** and any schedule Paused. Setting it Active is fine once the user has asked for that — call `update_workflow status:"active"` and describe the state after *that* call (its `next_step`), not the state `create_workflow` reported.
   - **Lead your reply with the tool's `next_step` / `run_state`.** They are computed from what was actually saved, so they are the authority on what will and won't run. If the schedule is already On, activating the workflow starts its scheduled runs — say so before you do it, and after.
6. **Scheduling is optional — and a schedule is always saved Paused.** Skip `schedule_config` entirely for manual/on-demand workflows.
   - **Preferred (calendar) shape:** `{"frequency": "daily"|"weekly", "hour": <0-23 UTC>, "days_of_week": [<0=Sun…6=Sat, UTC>], "timezone": "<the user's IANA zone>"}`. `days_of_week` takes 1–7 distinct days, so "3 times a week" is ONE schedule (`[1,3,5]`) — use it rather than approximating with an interval. (The older single `day_of_week` is still read when the array is absent.) Convert the user's local time and weekdays to UTC yourself; `timezone` is display-only. This is the shape the app's schedule editor shows and edits.
   - **Interval shape:** omit `hour` and pass `interval_hours` (or rely on the 1h / 24h / 168h default for hourly / daily / weekly). It runs every N hours with no fixed time of day, the first run landing one interval after the user switches the schedule On. The app's editor cannot display or edit it — use it only when the calendar shape can't express the need.
   - **No MCP tool can switch a schedule On.** `update_workflow` silently ignores `schedule_config` and still returns success. Tell the user the schedule is Paused, hand them the workflow's `link_url` exactly as returned, and ask them to review it and click **Resume schedule**. Quote `schedule.summary` when you describe what was saved.
   - **The app's editor offers:** Daily at a set time, or Weekly on one or more days at a set time (it has a weekday picker). It cannot hold a second time of day or an every-N-hours interval, and cron expressions are not supported. If the user asks for something it genuinely can't express ("twice a day"), say exactly what you saved and that it is an approximation.
7. **For workflows that process entities over time** ("summarize new content each week"), be explicit about dedup BEFORE creating: use a `since_last_run` input binding (Marcora computes the window from the last successful run — don't compute it yourself), match schedule cadence to lookback, and write source entity IDs into downstream artifacts so a future run can tell what it already processed. Raise this proactively if the user doesn't.

### What the runner writes to its run summary

The runner agent's FINAL message becomes the run's summary (rendered as markdown on the run-detail page). Instruct it to: format in markdown, lead with a one-line conclusion, and **link back to anything created** (most Marcora tools return a `url`/`link` — include it). For summary-only workflows, the summary IS the deliverable — make it complete.

**Setting the run's status:** tell the runner to start its final message with one of these prefixes — `Workflow complete: <md>` → succeeded · `Partial completion: <md>` → succeeded (partial) · `SKIP: <reason>` → skipped · `FAIL: <reason>` → failed. With no prefix, the final message is used as the run summary as-is.

### Risk warnings

- **Set a workflow Active when the user has asked for it, and tell them what that does.** Activating is not the risk; an inaccurate reply is. With the schedule On, activating starts scheduled runs — say so. With it Paused, the workflow can be run manually but still won't run on its schedule. Never tell the user a workflow will run on its own unless it is Active and its schedule is On.
- **Setting a workflow Inactive keeps its schedule exactly as it was.** A schedule that was On is still On and fires again as soon as the workflow is Active. To stop scheduled runs but keep manual runs, the user pauses the schedule in the app — there is no `"paused"` workflow status.
- **Hard-delete isn't exposed** — use `update_workflow status:"archived"`. Restore with `status:"inactive"` or `status:"active"`.
- **Duplicate names aren't prevented** — `list_workflows search:"<name>"` first if re-creating is possible.
- **Schedule edits via MCP are NOT supported** — changing a schedule, and switching it On or Paused, happen in the app. Direct the user there with the workflow's `link_url`.
- **Runner sessions don't author workflows** — these 6 tools are for interactive sessions; a runner executing a scheduled run uses a different tool set and must not call `create_workflow`/`update_workflow`.

---

## E15 — Telling the user a workflow "is running" when it isn't

**Symptom.** You create a workflow, set it Active, and tell the user it's live — and nothing ever runs on its schedule. Or the user asks to "pause" a workflow and `update_workflow status:"paused"` is refused.

**Cause.** A workflow has two independent switches. The workflow is **Active** or **Inactive**; its schedule is **On** or **Paused**. Scheduled runs need both — Active **and** On. `create_workflow` saves the workflow Inactive and every schedule Paused, and no MCP tool can turn a schedule On: only the user can, in the app, with **Resume schedule**. There is no `paused` workflow status; `status` accepts only `active`, `inactive` and `archived`.

**What to do.** Read `next_step` (from `create_workflow` / `update_workflow`) or `run_state` (from `get_workflow`) and lead your reply with it — it is computed from what was actually saved. Whenever you say a workflow is Active, say in the same sentence whether its schedule is On, Paused, or absent. If the schedule is Paused, hand the user the workflow's `link_url` exactly as returned and ask them to click **Resume schedule**. To stop scheduled runs but keep manual runs, the user pauses the schedule in the app; to stop everything, set the workflow `inactive`.
