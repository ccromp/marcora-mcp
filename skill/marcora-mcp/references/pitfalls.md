# Detailed pitfalls and edge cases

The high-frequency pitfalls are in `SKILL.md` (§ Pitfalls and conventions). This file covers detailed edge cases. Read it when something looks unusual or you're hitting an error pattern not covered in the main skill.

---

## E1 — `get_unified_deliverable`'s "Document not found" error

**Symptom.** `marcora:update_project(project_brief_id=<bad-uuid>)` returns `"Document not found"`.

**Cause.** The brief-resolution path delegates to a backend function (`get_unified_deliverable` — Xano-era name, now served by the Railway `marcora-backend`) that checks both the canvases and deliverables tables. If neither has a matching UUID, it throws this less-specific error.

**What to do.** Verify the UUID. Common mistakes:
- Pasting a `project_id` where a content UUID was expected.
- Pasting a `project_item.id` (integer) instead of a content UUID.

---

## E2 — `get_relevant_context` returns chunks, not full items

**Symptom.** You expected a complete document and got a few hundred words.

**Cause.** `marcora:get_relevant_context` returns RAG chunks (typically a few hundred words each) plus a `sources[]` array — one entry per parent item, each with its `context_item_id` and a `link_url`.

**What to do.** For the full body of a surfaced item, call `marcora:get_context_item(context_item_id)` (take the ID from `sources[]`), or hand the user the source's `link_url` to open it in the Marcora app. For most "what context exists about X?" questions, the chunks themselves are sufficient.

---

## E3 — Pagination for `get_relevant_context`

**Symptom.** Repeating a `get_relevant_context` call returns the same chunks.

**Cause.** Without pagination, every call returns the top-N most relevant chunks — same set.

**What to do.** Pass `context_rag_ids` (the IDs returned in the previous call) to exclude already-seen chunks. Effectively paginates.

---

## E4 — Project context items are included verbatim — no relevancy filtering

**Symptom.** A project with many large context items has slow generations or hits limits.

**Cause.** Project context items (Layer 3) are included in full during in-project generations — no relevancy scoring, unlike Reference Library (Layer 2).

**What to do.** Suggest the user prune project context to items still relevant to the initiative. Universally-useful items belong in the Reference Library (top-level) instead.

---

## E5 — Content `category_id` doesn't change generation behavior

**Symptom.** User expects setting a category to affect output style. It doesn't.

**Cause.** `category_id` is purely organizational — helps the user find content later. Generation behavior is shaped by the blueprint (if any), `instructions`, context layers, and targeting dimensions.

**What to do.** Don't promise category-driven generation differences. If the user wants category-style output, recommend a blueprint instead.

---

## E6 — `import_community_blueprint` requires the exchange ID, not a blueprint UUID

**Symptom.** Import fails with an invalid ID error.

**Cause.** `marcora:list_community_blueprints` returns items with their own `blueprint_exchange_id` — distinct from a regular blueprint UUID. Use that exchange ID for `get_community_blueprint_details` and `import_community_blueprint`. The imported blueprint then has a fresh team-level UUID.

---

## E7 — `private_override` and brief privacy

When `update_project` sets a private Content item as a project's brief, the underlying PATCH endpoint auto-sets `project_item.private_override = true` so other project members can see it. You don't need to manage this flag manually.

---

## E8 — Project document `purpose` field

`marcora:get_project` returns documents with a `purpose` field:
- `core_output` — the project's main work product
- `supporting` — background material (the brief defaults to this)

Most agents don't need to set or change `purpose` — it's surfaced for the UI. Treat it as informational. There's no MCP tool to change it.

---

## E10 — Surface human-readable identifiers, not UUIDs

Don't show the user a UUID like `7b2c4f...` as an identifier. Surface the human-readable name + the `link_url` instead. UUIDs are for tool calls, not user-facing references.

---

## E11 — `convert_markdown_to_word_doc` doesn't auto-fetch by ID

**Symptom.** Calling the conversion tool with a content ID instead of markdown content fails.

**Cause.** This tool takes `markdown_content` as a parameter — it does not pull content by ID.

**What to do.** Two-step: `marcora:get_content(content_id)` → `marcora:convert_markdown_to_word_doc(markdown_content=...)`. Optionally pass `document_url` (the original content's `link_url`) so the .docx footer links back.

---

## When you encounter something not in this list

1. Surface the raw error to the user — don't silently retry.
2. State what you tried and what came back.
3. Suggest plausible next steps (verify a parameter, retry, reconnect).
4. Don't assume a workaround that creates the wrong artifact in the wrong place — confirm with the user first.
