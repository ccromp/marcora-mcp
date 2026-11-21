# Blueprints and the Blueprint Exchange

Read this before creating a blueprint, or browsing / importing one from the Blueprint Exchange.

---

## Recipe A — Create a new blueprint from scratch

**Goal.** Author a reusable AI template for a content type the user produces repeatedly.

**Steps.**
1. **Check the Blueprint Exchange first.** `marcora:list_community_blueprints` — is there a community template that fits? If yes:
   - `marcora:get_community_blueprint_details(blueprint_exchange_id=<id>)` (pass the UUID in the item's `id` field, never its `slug`) — confirm fit.
   - **State your plan**, then `marcora:import_community_blueprint(team_id, blueprint_exchange_id=<id>)`. Done.
2. **If no community match**, branch on what the user has:
   - **Strong sample document** (paste-able markdown that captures the structure): `marcora:create_blueprint` directly with `source_content`. Async: returns a `generation_id`, `blueprint_uuid`, and `link_url` immediately; poll `marcora:get_generation_status` until `completed` (1–3 min).
   - **Only a description**: `marcora:create_blueprint_draft` (async: returns a `generation_id`, draft `uuid`, and `link_url` immediately; poll `marcora:get_generation_status` until `completed`, 1–2 min) → review with the user at `link_url` → `marcora:finalize_blueprint_draft` to publish (async: returns a `generation_id`, `blueprint_uuid`, and `link_url`; poll `marcora:get_generation_status` until `completed`, 1–3 min).
3. Always pick a `category_id` from `marcora:list_content_categories` (required for `create_blueprint`).
4. Surface the new `blueprint_uuid` to the user; they'll use it in future content generations.

---

## Recipe B — Browse and import community blueprints

**Goal.** Pull a community-published blueprint into the user's library.

**Steps.**
1. `marcora:list_community_blueprints` (optional `category`, `limit` default 150 max 300, `offset`) — returns a compact index of `community_blueprints` (`id`, `slug`, `name`, `category`, `is_featured`), plus `total` and `next_offset` (when `next_offset` is not `null`, call again with `offset=next_offset`).
2. For summary, contributor info, input instructions, and full sample content on a specific one: `marcora:get_community_blueprint_details(blueprint_exchange_id=<id>)` using the UUID in the returned `id` field (not `slug`, which is refused with a readable tool error).
3. **State your plan** (this clones the blueprint into the user's library).
4. `marcora:import_community_blueprint(team_id, blueprint_exchange_id=<id>)` (pass the same `id` UUID, not `slug`) — returns the new team-level `uuid` for use with `create_content`.

---

## E6 — `import_community_blueprint` and `get_community_blueprint_details` require the exchange UUID `id`, not `slug` or a team blueprint UUID

**Symptom.** Calling `get_community_blueprint_details` or `import_community_blueprint` fails with `"blueprint_exchange_id must be the UUID in the \`id\` field of a list_community_blueprints item, not its \`slug\`..."` (`isError: true`).

**Cause.** `marcora:list_community_blueprints` returns items with both a UUID `id` and a human-readable `slug`. Both `get_community_blueprint_details` and `import_community_blueprint` require that UUID `id` as `blueprint_exchange_id` — passing `slug` (or a regular team blueprint UUID) is refused. Once imported, `import_community_blueprint` returns a fresh team-level `uuid` to pass as `blueprint_uuid` to `create_content`.

---

## E18 — Treating `create_blueprint`, `create_blueprint_draft`, or `finalize_blueprint_draft` as synchronous

**Symptom.** Calling `create_blueprint`, `create_blueprint_draft`, or `finalize_blueprint_draft` returns `status: "processing"`, or calling `create_content(team_id, blueprint_uuid=…)` / `finalize_blueprint_draft(team_id, draft_uuid=…)` immediately fails because processing is still running.

**Cause.** All three blueprint tools run asynchronously, returning `status: "processing"`, `generation_id`, and start-time identifiers (`blueprint_uuid`, `name`, `link_url` on `create_blueprint` and `finalize_blueprint_draft`; `uuid`, `title`, `link_url` on `create_blueprint_draft`).

**What to do.** Poll `marcora:get_generation_status(team_id, generation_id)` (or `marcora:get_blueprint(team_id, blueprint_uuid)`) until `status` is `"completed"` (`flow_type: "blueprint_item"` or `"blueprint_draft"`), or report `error_message` on `"failed"`.
