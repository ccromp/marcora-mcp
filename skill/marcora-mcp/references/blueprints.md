# Blueprints and the Blueprint Exchange

Read this before creating a blueprint, or browsing / importing one from the Blueprint Exchange.

---

## Recipe A — Create a new blueprint from scratch

**Goal.** Author a reusable AI template for a content type the user produces repeatedly.

**Steps.**
1. **Check the Blueprint Exchange first.** `marcora:list_community_blueprints` — is there a community template that fits? If yes:
   - `marcora:get_community_blueprint_details` — confirm fit.
   - **State your plan**, then `marcora:import_community_blueprint`. Done.
2. **If no community match**, branch on what the user has:
   - **Strong sample document** (paste-able markdown that captures the structure): `marcora:create_blueprint` directly with `source_content`. Takes 1–3 min.
   - **Only a description**: `marcora:create_blueprint_draft` (returns a reviewable draft) → review with the user → `marcora:finalize_blueprint_draft` to publish. Both calls take 1–3 min.
3. Always pick a `category_id` from `marcora:list_content_categories` (required for `create_blueprint`).
4. Surface the new `blueprint_uuid` to the user; they'll use it in future content generations.

---

## Recipe B — Browse and import community blueprints

**Goal.** Pull a community-published blueprint into the user's library.

**Steps.**
1. `marcora:list_community_blueprints` — returns blueprints with names, summaries, contributor info, and `blueprint_exchange_id`.
2. For details on a specific one: `marcora:get_community_blueprint_details(blueprint_exchange_id)`.
3. **State your plan** (this clones the blueprint into the user's library).
4. `marcora:import_community_blueprint(blueprint_exchange_id)` — returns the new team-level `uuid` for use with `create_content`.

---

## E6 — `import_community_blueprint` requires the exchange ID, not a blueprint UUID

**Symptom.** Import fails with an invalid ID error.

**Cause.** `marcora:list_community_blueprints` returns items with their own `blueprint_exchange_id` — distinct from a regular blueprint UUID. Use that exchange ID for `get_community_blueprint_details` and `import_community_blueprint`. The imported blueprint then has a fresh team-level UUID.
