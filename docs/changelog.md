# Changelog

All notable changes to the Marcora MCP server will be documented in this file.

## 2026-06-19

### Changed

- **`create_workflow` — `allowed_tools` is now required.** A workflow cannot be created without an explicit, non-empty tool allowlist (an empty list would let the runner inherit the full tool set). Omitting it now returns a clean input-validation error. Previously `allowed_tools` was optional, and omitting it produced a fatal error. No change to the success output shape.

### Fixed

- **`create_workflow` no longer returns a fatal error.** Calls now surface backend rejections as clean input errors instead of an internal `ERROR_FATAL`.
- **`create_blueprint_draft` now returns a valid `uuid`.** The draft's identifier (and its `link_url`) were previously `null`, which also broke `finalize_blueprint_draft`. The full `create_blueprint_draft → finalize_blueprint_draft` chain now works end to end.

## 2026-06-11

### Changed

- **Brand Foundation tool-selection guidance (instructions only — no behavior or I/O change).** Tightened the descriptions on two tools so agents reliably reach for Brand Foundation when a user asks about it:
  - `get_brand_foundation` now has an explicit **"When to use it"** trigger (brand voice / company overview / writing style / writing examples questions) and the old note that framed it as an outside-the-flow / external-agent tool was reworded so it no longer discourages direct use.
  - `get_relevant_context` now (a) cross-references `get_brand_foundation` — relevancy search does not surface Brand Foundation elements, so a *"what is our brand voice?"* question can't be answered from relevancy chunks — and (b) recommends defaulting `include_brand_foundation: true` on the **first** call of a conversation (then `false`/omit on subsequent calls), so the agent has company overview + brand voice on hand for the whole session.

  No parameters, output shapes, or annotations changed.

## 2026-06-10

### Changed

- **Output shape — eight list tools now return a JSON object wrapping their array** instead of a bare top-level array, so each can carry a spec-compliant `outputSchema` (the MCP spec requires `outputSchema` to be a top-level `object`). Each wraps its array under one semantic key, and the item fields are otherwise unchanged:
  - `list_blueprints` → `{ "blueprints": [...] }`
  - `list_projects` → `{ "projects": [...] }`
  - `list_content` → `{ "content": [...] }`
  - `list_context_collections` → `{ "collections": [...] }`
  - `list_context_items` → `{ "context_items": [...] }`
  - `list_community_blueprints` → `{ "community_blueprints": [...] }`
  - `list_content_categories` → `{ "categories": [...] }`
  - `list_targeting_dimensions` → `{ "dimensions": [...] }`

  Clients that previously read the bare array must now read `response.<key>` (e.g. `response.projects`).
- **`get_workflow_runs` output schema** is now a single top-level `object` (previously a `oneOf` of two object shapes, which has no top-level `type` and so could not be promoted to `outputSchema`). The returned data is unchanged — list mode still returns `items` + `itemsTotal`; single-run mode still returns the run fields plus `_step_logs` / `_tool_call_logs`.
- **Per-tool `annotations`** (`title`, `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) are now published on every customer tool, and a valid `outputSchema` is now promoted on all of them.
- **`get_current_user_info` reshaped** — the nested `usage` object is removed. The response now exposes two top-level integer fields: `ai_credits_max` (the plan's AI-credit limit) and `ai_credits_available` (credits remaining = limit minus used). The other fields (`name`, `email`, `active_team_name`, `active_team_role`, `subscription_status`, `plan_name`, `plan_slug`) are unchanged. Annotations and `outputSchema` were also added to this tool (it had been temporarily detached during the annotations pass).

### Added

- **Workflows documentation** — `docs/tools.md` now documents the six workflow tools (`list_workflows`, `get_workflow`, `create_workflow`, `update_workflow`, `run_workflow`, `get_workflow_runs`) under a new **Workflows** section. They were previously undocumented.

### Fixed

- **Documentation tool-name corrections** — several tools had been documented under stale `get_*` names that did not match the live `list_*` tools. Renamed throughout `docs/tools.md`, `docs/errors.md`, and the README tool table: `get_content_categories` → `list_content_categories`, `get_targeting_dimensions` → `list_targeting_dimensions`, `get_community_blueprints` → `list_community_blueprints`, `get_projects` → `list_projects`, and `get_blueprints` → `list_blueprints`. The README "Available Tools" table was also refreshed to list every current tool (adding the missing/renamed Context, Content, Projects, Plans, and Workflows entries).

## 2026-06-09

### Changed

- **`get_relevant_context` response reshaped** to give clients everything they need to cite and link sources in a single call:
  - **New `sources` array** — one entry per parent context item that contributed chunks. Each carries `context_item_id`, `context_item_name`, `content_type`, a `link_url` deep-link into the Marcora app, `collection_id` / `project_id` / `last_updated`, and the `context_rag_ids` from that item (the per-source chunk lists partition the top-level `context_rag_ids`). `webpage` items additionally carry `source_url` (the original external page URL); other content types omit it.
  - **New `retrieval` object** echoing the scope the search ran under: `team_scope`, `project_id`, `collection_ids`, `dimension_option_ids`, `excluded_context_rag_ids`, `returned_count`.
  - **`brand_foundation` reshaped** from a flat object to `{ included, elements, link_url }` — `elements` (the four Brand Foundation fields) is `null` unless `include_brand_foundation: true`, and `link_url` deep-links the Brand Foundation tab when included.
  - **Removed the top-level `context_item_ids`** field — each `sources[]` entry now carries its own `context_item_id`. `relevant_context` and `context_rag_ids` are unchanged.
  - Implementation note: the new per-source metadata is assembled from data already loaded by the existing retrieval queries (no added per-chunk lookups); only a single `webpage`-table lookup is added to resolve `source_url`. Retrieval itself is unchanged — the same chunks/items are returned as before.
- **`get_relevant_context` input docs clarified:** `collection_ids` and `project_id` are **additive** — they broaden the search to also include those collections / that project's context alongside the general reference library; they are not exclusive filters. (Behavior is unchanged; only the wording was misleading.)

## 2026-06-03

### Added

- **`get_relevant_context`** — new optional `include_brand_foundation` parameter (boolean, default `false`). When `true`, the response gains a `brand_foundation` object carrying the team's four Brand Foundation elements (`company_overview`, `brand_voice`, `writing_style`, `writing_examples`), making the tool a one-stop context fetch for clients that write content themselves with their own model. Relevancy scoring would never surface Brand Foundation on its own, so previously a caller had to make a second `get_brand_foundation` call and stitch the two together. The Brand Foundation fetch is gated behind the flag — callers who don't opt in don't pay the extra query. When omitted or `false`, `brand_foundation` is `null`. The bundled Brand Foundation is sourced identically to `get_brand_foundation`, so the two always agree.
- **New tool:** `ask_content_assistant` — drives Marcora's in-document Content Assistant on an existing canvas or deliverable. Send a natural-language `prompt` (plus optional `selected_text`, `collection_ids`, `project_id`, `thinking_mode`, `chat_only_mode`, `ai_provider`) and the assistant edits the document, extends it, or just replies — its choice, unless `chat_only_mode: true` forces a reply-only response. Asynchronous: returns a `generation_id` (UUID) immediately; the reply and any edits stream live into the document's AI Assistant sidebar for users with the doc open, and headless callers poll `get_generation_status` for the result.

### Changed

- **`get_relevant_context` output** now includes a `brand_foundation` field (`object | null`) on every response — `null` unless `include_brand_foundation` is `true`. Existing fields (`relevant_context`, `context_rag_ids`, `context_item_ids`) are unchanged. Docs also now list the `dimension_option_ids` parameter, which the tool already accepted but the table had omitted.
- **`get_generation_status`** now also handles `ask_content_assistant` generations. Every response gains a top-level `flow_type` (`ai_assistant` vs. blueprint). For the Content Assistant flow, once `status` is `complete` the `content` object carries `document_type`, `assistant_summary` (the latest sidebar reply), `document_updated` (whether this changed the body), and `current_content` (the document's current markdown), alongside `content_id`, `name`, and `link_url`. `status` tracks the specific run; `content` reflects the document's current state and the most recent interaction, not a frozen snapshot. Blueprint-flow output is unchanged.

## 2026-06-01

### Fixed

- **`list_blueprints`** no longer errors with `Exception: Please use a numerically indexed array`. The underlying `blueprint_items` endpoint had been refactored to return a structured object (`{ blueprints: [...content categories with nested blueprint_items[]...], blueprint_drafts: [...] }`) instead of a flat list, but the tool still iterated it as a flat array. The tool now flattens the category-grouped structure correctly and sources `content_count` from each blueprint's `deliverable_count`.

### Changed

- **`list_blueprints` output is now a flat top-level array of blueprints** (previously an object wrapper `{ blueprints, blueprint_drafts }`). Each item carries `blueprint_uuid`, `name`, `input_instructions`, `team_visibility`, `exchange_visibility`, `content_count`, `created_at`, `category {id, name}`, and `web_url`. The `blueprint_drafts` array has been removed entirely — the tool no longer returns in-progress drafts.

## 2026-05-25

### Added

- **New tool:** `update_content` — partial-update writer for canvas and deliverable documents. Mutate any combination of body (`content`), display name (`name_override`), stage (`in_progress` / `ready`), visibility (`private` / `team`), category (`category_id`), and project association (`project_id`) in one call. Omit a field to leave it unchanged; at least one mutable field is required. `name_override` locks the title so it won't auto-resync from the body's first header on future edits. Setting `project_id` replaces any existing project association; there is no way to remove a doc from all projects via this tool (use the Marcora app). Documents with `canvas_type` other than `deliverable` (e.g. the canvases that back the context-item editor) are rejected — those are managed by separate sync flows.

### Changed

- **`list_content` output:** canvas-type items now surface their category in the `category` field (previously hard-coded to `null` despite the column existing on the canvas table) and emit `stage` consistently with deliverable items (previously emitted `is_ready` for canvas items, breaking the declared schema).
- **`create_project` response:** the response shape now matches its declared schema — top-level keys are exactly `project_id`, `name`, `link_url`, `project_brief`. The deprecated `system_prompt` and the unhelpful internal-id `project_brief_id` are no longer leaked. When `project_brief_details` is supplied, the response includes a `project_brief: {name, content_id}` object — `content_id` is the brief canvas's UUID, suitable for passing directly to `update_content` later. When no brief was created, `project_brief: null`.
- **`get_project` response:** added top-level `project_brief: {name, content_id} | null` to match `create_project`'s shape. Previously the brief was buried inside `documents[]` with no unambiguous discriminator (the `purpose` field isn't brief-specific). Same field is in addition to — not a replacement for — the existing `documents` array.

## 2026-05-21

### Changed

- **Renamed `get_core_context` → `get_brand_foundation`.** Output shape changed from a single concatenated markdown blob (`core_context` field) to per-element JSON fields (`company_overview`, `brand_voice`, `writing_style`, `writing_examples`), with a new optional `elements` array parameter to scope the response. This matches the app's "Brand Foundation" terminology and gives the calling agent finer control over which elements to fetch. The disabled `Custom Instructions` category is excluded entirely.

### Added

- **New tool:** `update_brand_foundation` — overwrites a single Brand Foundation element with new content. Required `element` enum + `content` text. Always full-replace, no patch semantics. Per-element character limits enforced (10,000 for `company_overview`, 20,000 for the others) with a clear `ERROR_CODE_INPUT_ERROR` response naming the limit and the actual length if exceeded — write is rejected before any DB mutation.

## 2026-05-15

### Enhanced

- `add_context` and `update_context` — new optional `content_url` parameter. Pass a public URL and the backend fetches it and converts the page to clean markdown server-side using a headless browser + Mozilla Readability, then stores the result as the context item body. Use this when the body is large, comes from a presigned-link export (Google Doc, connected-app sandbox), or you'd otherwise have to pull the page into the conversation just to forward it. Mutually exclusive with `content` — exactly one of `content` / `content_url` is required on `add_context`; on `update_context` you may also omit both to leave the body unchanged.

## 2026-05-02

### Added

- **New tool:** `list_context_items` — list context items in your team's library, with `id`, `name`, `content_intro`, `content_type`, `word_count`, `added_by`, `collection_id`, `project_id`, and other metadata. By default returns all items the user can see; set `reference_library_only=true` to return only items not in any project or collection. Honors collection and project privacy: items in private collections you don't own and items in private projects you're not a member of are filtered out.
- **New tool:** `get_context_item` — fetch the full markdown content of a single context item by ID. Same privacy rules as `list_context_items`. IDs can come from `list_context_items`, `get_project`, `list_context_collections`, or `get_relevant_context`.

## 2026-04-29

### Added

- **New category: Plans** — 4 new tools for managing content plans:
  - `list_plans` — paginated list of plans with filters by stage, source, project, and category
  - `get_plan` — fetch a single plan by UUID with full linked data (references, collections, dimensions, produced content)
  - `create_plan` — create a new plan with optional pre-attachments and blueprint prompt
  - `update_plan` — partial update: mutable fields and stage transitions

### Enhanced

- `create_content` — new optional `plan_id` parameter: associates the new content with a plan and triggers an automatic stage transition to `In_Process`. Auto-linking applies when used with `blueprint_uuid`. Do not pass if the plan is in `Complete` stage.

---

## 2026-04-23

### Added

- **New tool:** `update_context` — update an existing context item's name, content, collection, or project association. When the item has a linked editing canvas open in the Marcora sidebar, its title, content, and word count stay in sync automatically, and a realtime event is broadcast to any open editors. `collection_id` and `project_id` use full-replace semantics — you must pass them on every call (pass `null` to clear).

## 2026-04-17

### `create_content` — Direct content support

- **New parameter:** `content` — supply your own text directly as a document, bypassing AI generation
- **Changed:** `instructions` is now optional (was required). You must provide either `content` or `instructions`, but not both
- **Fixed:** `content_id` now returns correctly in the synchronous response (was returning null)

## 2026-04-16

### Enhanced

- `add_context` — Added `link_url` field returning a direct URL to view the new context item in the Marcora app. The URL resolves to the project, collection, or reference library view depending on which scope the item was added to.
- `create_context_collection` — Added `link_url` field returning a direct URL to open the new collection in the Marcora app.
- `get_context_collections` — Added `link_url` field on each returned collection. Documentation expanded to include the full output field table.

## 2026-04-14

### Enhanced

- `get_projects` — Added `link_url` field returning a direct URL to view each project in the Marcora app. Expanded output documentation with full field table.

## 2026-04-09

### Initial Release

First public documentation for the Marcora MCP Server with 25 tools across 7 categories:

**Account**
- `get_current_user_info`

**Context & Resources**
- `get_core_context` *(renamed to `get_brand_foundation` on 2026-05-21)*
- `get_context_collections`
- `create_context_collection`
- `add_context`
- `get_relevant_context`

**Reference**
- `get_content_categories`
- `get_targeting_dimensions`

**Blueprints**
- `get_blueprints`
- `get_blueprint`
- `create_blueprint`
- `create_blueprint_draft`
- `finalize_blueprint_draft`

**Community Blueprints**
- `get_community_blueprints`
- `get_community_blueprint_details`
- `import_community_blueprint`

**Content**
- `create_content`
- `get_generation_status`
- `get_content_list`
- `get_content`

**Sharing & Export**
- `create_external_share`
- `convert_markdown_to_word_doc`

**Projects**
- `get_projects`
- `get_project`
- `create_project`
