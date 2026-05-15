# Changelog

All notable changes to the MarketCore MCP server will be documented in this file.

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

- **New tool:** `update_context` — update an existing context item's name, content, collection, or project association. When the item has a linked editing canvas open in the MarketCore sidebar, its title, content, and word count stay in sync automatically, and a realtime event is broadcast to any open editors. `collection_id` and `project_id` use full-replace semantics — you must pass them on every call (pass `null` to clear).

## 2026-04-17

### `create_content` — Direct content support

- **New parameter:** `content` — supply your own text directly as a document, bypassing AI generation
- **Changed:** `instructions` is now optional (was required). You must provide either `content` or `instructions`, but not both
- **Fixed:** `content_id` now returns correctly in the synchronous response (was returning null)

## 2026-04-16

### Enhanced

- `add_context` — Added `link_url` field returning a direct URL to view the new context item in the MarketCore app. The URL resolves to the project, collection, or reference library view depending on which scope the item was added to.
- `create_context_collection` — Added `link_url` field returning a direct URL to open the new collection in the MarketCore app.
- `get_context_collections` — Added `link_url` field on each returned collection. Documentation expanded to include the full output field table.

## 2026-04-14

### Enhanced

- `get_projects` — Added `link_url` field returning a direct URL to view each project in the MarketCore app. Expanded output documentation with full field table.

## 2026-04-09

### Initial Release

First public documentation for the MarketCore MCP Server with 25 tools across 7 categories:

**Account**
- `get_current_user_info`

**Context & Resources**
- `get_core_context`
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
