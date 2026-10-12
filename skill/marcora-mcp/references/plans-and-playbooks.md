# Content plans and playbooks

Read this before calling any plan or playbook tool (`create_plan`, `update_plan`, `produce_plan`, `list_plans`, `get_plan`, `create_playbook`, `create_playbook_from_plans`, `instantiate_playbook`, …): a content plan, the plans board, a launch calendar, or a reusable sequence of content to write.

---

## Content Plans & Playbooks

The **plans board** is Marcora's content pipeline: a queue of ideas/intents (**plans**) that move through stages and get *produced* into real Content. **Playbooks** are reusable, ordered templates of plan items you can stamp out as a batch.

> **Mindset:** a plan is *intent*, Content is *output*. Creating a plan doesn't write anything — `produce_plan` does. Keep the two straight: `create_content` generates a document now; `create_plan` records "we should write X" for later.

### The plan stage machine

`Suggested → Accepted → In_Process → Complete`, plus `Dismissed` (terminal). Transitions go through `update_plan target_stage:` (use the UNDERSCORE form `In_Process`). Only these are allowed: Suggested→Accepted/Dismissed · Accepted→In_Process/Dismissed · In_Process→Complete/Accepted/Dismissed · Complete→Accepted (re-open, clears produced content)/Dismissed. **There is no `delete_plan`** — dismiss with `target_stage:"Dismissed"`.

The **starting stage is set automatically from `source`**, you don't control it directly: `user_added` / `cora_requested` / `playbook` → **Accepted** (actionable now); `cora_proactive` → **Suggested** (awaits user accept). Set `source:"cora_requested"` when the user explicitly asked; `source:"cora_proactive"` when you're surfacing an unprompted suggestion. **Never** pass `source:"workflow"` or `"playbook"` from an interactive session.

### Visibility

**Plans are `private` by default** — the creator's ideas queue, invisible to teammates (a teammate's private plans return NotFound and never appear in their `list_plans`). Assigning a plan to another member (`assigned_to`) **auto-promotes it to `team`** — assignment is a communication act, even over an explicit `private`. Only the plan's **creator** can change `visibility`; mention the change to the user before sending it. **Playbooks default to `team`;** `instantiate_playbook` **inherits** the playbook's visibility onto the plans it creates.

### The 5 plan tools

- **`create_plan`** — Create a plan. Only `title` is required. Optional executable params (`prompt`, `blueprint_id`, `project_id`, `category_id`, `due_date`, `reference_document_ids`, `context_collection_ids`, `targeting_dimension_ids`, `assigned_to`, `visibility`). **Dedupe first:** call `list_plans` with a `project_id` filter before creating; if a matching Accepted/Suggested plan exists, offer to `update_plan` it instead. When creating several in one turn, correlate them with `source_metadata.batch_id` and deep-link the filtered view.
- **`get_plan`** — Fetch one plan by `plan_uuid` with all linked params. **Always call before `update_plan`** to avoid overwriting with stale values. `_produced_content` null = no content yet.
- **`list_plans`** — Discovery + dedup. Results cover only the plans the user can see (an empty result ≠ the team has no plans). Useful filters: `stage` (single-value array, UNDERSCORE form), `project_id`, `assignee_scope` (`me` default | `created_by_me` | `all_visible`). Current limitations: `due_before`, `due_after` and `search_text` are accepted but not yet applied, and for `stage` and `source` only the first value is used — pass single-value arrays.
- **`update_plan`** — Partial update; only keys you send mutate. Construct a minimal diff after `get_plan`. `reference_document_ids` / `context_collection_ids` / `targeting_dimension_ids` are **full-replace** (pass `[]` to clear). Server-managed fields (`source`, `produced_content_id`, timestamps, etc.) are rejected as immutable.
- **`produce_plan`** — The MCP equivalent of the plans-board **Generate** button. Requires the plan in **Accepted** stage (Suggested → `update_plan target_stage:"Accepted"` first). **⚠️ Consumes Studio Credits and takes 1–2 min — confirm before producing a plan the user didn't explicitly ask to produce.** The plan's `prompt`, targeting, context collections, and project are used as generation inputs — set them via `update_plan` BEFORE producing.
  - **Both paths are ASYNC now** — the tool returns immediately with a `generation_id`; **poll `get_generation_status`**. A plan **with** a blueprint → `path:"blueprint"`; **without** a blueprint → `path:"freeform"`. On completion Marcora links the produced content and flips the plan to `In_Process` (then `Complete` when the content reaches ready).

### The 6 playbook tools

- **`list_playbooks`** — All playbooks visible to the caller (team + own private). Summaries only — call `get_playbook` for items. Use before `instantiate_playbook`/`update_playbook` to find the right id.
- **`get_playbook`** — One playbook with its full ordered item list. Inspect before instantiating/editing.
- **`create_playbook`** — Author a reusable template from scratch: `name` + optional ordered `items` (each item becomes one plan on instantiation). Defaults `visibility:"team"`. Optionally set **`anchor_date`** (`YYYY-MM-DD`) when the template is built around a real date — it persists on the playbook and becomes the default anchor at instantiation.
- **`create_playbook_from_plans`** — Capture existing plans as a template ("save what worked"): pass `plan_ids`; their title/description/prompt/blueprint/category copy into ordered items. Use this (vs `create_playbook`) when the user liked a batch they already ran.
- **`update_playbook`** — Rename/re-describe (patch in place) or restructure. If `items` is provided it **FULLY REPLACES** the items and their order; omit `items` to leave them. `visibility` change is creator-only. Pass **`anchor_date`** to set the reference date, or `null` to clear it.
- **`instantiate_playbook`** — **Run** a playbook: create one Accepted plan per item, in order, as a batch (source `"playbook"`, inheriting the playbook's visibility). This is a distinct bulk action — it does NOT create/edit the playbook. Optional `project_id`, `assigned_to`, `category_id`, and **`anchor_date`**: each item's `offset_days` is applied to the anchor to compute that plan's due date (e.g. "instantiate my launch playbook anchored to next Monday"). If `anchor_date` is omitted, the playbook's persisted anchor is used.

> **Playbook responses carry links — hand them to the user, not raw ids.** Every playbook read/write tool returns `anchor_date` (persisted `YYYY-MM-DD`, or `null`) and a **`link_url`** that opens the playbook in Marcora. `instantiate_playbook` returns the created **cycle** (`run`, with its own `link_url` → `app.marcora.ai/runs/{run_id}`) plus a `plans[]` array where **each plan has its own `link_url`** → `app.marcora.ai/plans/{plan_uuid}`. Share the cycle link to hand off the whole batch.

### Typical flows

- **Turn a suggestion into content:** `list_plans` (find it) → `update_plan target_stage:"Accepted"` → `produce_plan` → poll `get_generation_status` → hand the user the produced content's link.
- **Capture then reuse:** user runs a good batch of plans → `create_playbook_from_plans(plan_ids)` → later `instantiate_playbook(anchor_date=…)` to redeploy the sequence.
- **Author a template:** `create_playbook(name, items)` → `instantiate_playbook` when ready to deploy.
