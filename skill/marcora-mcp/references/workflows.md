# Long-tail workflow recipes

The 5 most common workflows are in `SKILL.md`. This file covers less-frequent recipes. Read the relevant section only when the user's request matches.

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

## Recipe C — Async generation followup

**Goal.** Check on (or report) a blueprint-driven generation that's still running.

**Steps.**
1. Recall the `generation_id` from earlier in the conversation. If lost, ask the user — `list_content` won't show pending generations.
2. `marcora:get_generation_status(generation_id)`.
3. Status meanings:
   - `pending` / `gathering context` / `processing` → still working, surface progress.
   - `completed` → hand `response.content.link_url` to the user.
   - `failed` → tell the user; offer to retry.

---

## Recipe D — Share content externally

**Goal.** Generate a public share URL for a piece of content.

**Steps.**
1. `marcora:create_external_share(content_id, expires_at?)` — `expires_at` is an optional Unix timestamp.
2. Hand the returned `share_link` to the user.

**Precondition.** Content must be `completed` — async generations need to finish first.

---

## Recipe E — Export content to Word

**Goal.** Produce a `.docx` download for a content item.

**Steps.**
1. `marcora:get_content(content_id)` — fetch the markdown body. (This is one of the few legitimate uses of `get_content`.)
2. `marcora:convert_markdown_to_word_doc(markdown_content, filename?, document_url?)` — `document_url` embeds as a footer link to the original.
3. Hand the returned `download_url` to the user.

---

## Recipe F — Update a project's name / visibility / status

**Goal.** Rename, archive, or change the visibility of a project.

**Steps.**
1. If you don't already know the `project_id`: `marcora:list_projects`.
2. **State your plan** — name the field changing and the new value.
3. `marcora:update_project(project_id, …)` with ONLY the fields changing (PATCH semantics — omitted fields are untouched).
   - `name` (text)
   - `visibility` enum: `team` | `private`
   - `status` enum: `active` | `archived`

**Note.** Setting `status="active"` requires available active-project usage on the team's plan — call returns `"You have reached your active project limit."` if exhausted.

---

## Recipe G — Workflows and Content Plans / Playbooks

These two surfaces now have full chapters in `SKILL.md` — read them there, not here:

- **Workflows** (`create_workflow`, `update_workflow`, `run_workflow`, `get_workflow`, `list_workflows`, `get_workflow_runs`) — building, running, and scheduling reusable multi-step processes; output destinations; dedup via `since_last_run`; runner summary conventions. See the **Workflows** chapter.
- **Content Plans & Playbooks** (`create_plan`, `get_plan`, `list_plans`, `update_plan`, `produce_plan`; `list_playbooks`, `get_playbook`, `create_playbook`, `create_playbook_from_plans`, `update_playbook`, `instantiate_playbook`) — the plans board, the stage machine, async `produce_plan`, playbook `anchor_date` instantiation, and visibility defaults. See the **Content Plans & Playbooks** chapter.

---

## Recipe H — Read the team's Brand Foundation directly

Most of the time you don't need to call `marcora:get_brand_foundation` — every `create_content` call pulls Brand Foundation in automatically (Layer 1 of the four-layer model).

Call it explicitly when:
- The user asks "what brand voice does the AI use?"
- You're generating content *outside* Marcora (drafting a tweet in their voice elsewhere) and need the brand context.
- You're debugging "why does the content sound off?" — maybe Brand Foundation is stale.
- The user wants to update one of the four elements — fetch first with `marcora:get_brand_foundation({elements: ["<element>"]})` so the user can confirm what's being replaced, then call `marcora:update_brand_foundation`.

Returns structured JSON with per-element fields (`company_overview`, `brand_voice`, `writing_style`, `writing_examples`), plus a `link_url` that opens the Brand Foundation section in Marcora. Pass `elements` to scope the response; omit to return all four. Empty string is returned for any element the team has not filled out yet.

## Recipe H2 — Update a Brand Foundation element

When the user wants to change one of the four Brand Foundation elements:

1. Read the current value: `marcora:get_brand_foundation({elements: ["<element>"]})`.
2. Confirm with the user what's being replaced (Brand Foundation shapes every generation — unintended overwrites are costly).
3. Write: `marcora:update_brand_foundation({element: "<element>", content: "<new markdown>"})`. Always full-replace — no patch semantics.
4. Hand the user the `link_url` from the response — it opens the Brand Foundation section in Marcora. Use it **exactly as returned**; never build a Brand Foundation URL yourself. There is no `/brand-foundation` route (a hand-built link 404s and bounces them to `/home`, losing the chat).

Per-element character limits: `company_overview` 10,000; `brand_voice`, `writing_style`, `writing_examples` 20,000 each. Overflow returns a structured `ERROR_CODE_INPUT_ERROR` naming the limit; the write is rejected before any DB mutation.

---

## Recipe I — Ground a document against the context library

Grounding checks a document's factual claims against the team's own context library and sorts each into **supported**, **conflict**, or **gap**. Use it after drafting, or whenever the user asks whether something is accurate / on-message / consistent with what the company has already said.

**The loop: draft → ground → review → apply → re-ground.**

1. **Scan.** `marcora:check_content_grounding(...)` in one of three modes:
   - `content_id` alone — scan a document that already exists. **This is the safe default.**
   - `content` alone — hand over markdown; Marcora stores it as a new document and scans it.
   - `content_id` + `content` — **replaces that document's entire body**, then re-scans. See the warning below.
2. **Poll if needed.** It waits ~20 seconds. If you get `status: "running"`, poll `marcora:get_grounding_result({scan_id})` every 15–30 seconds — a fresh scan usually takes 120–150 seconds. **Poll with the `scan_id`, not the `content_id`.** Never call `check_content_grounding` again to check progress; that starts a second scan.
3. **Review with the user.** Walk them through `findings[]`. Each carries the **full** `suggested_fix` and the `context_item_id` applying would write to. Hand them the `link_url` so they can see it in Marcora.
4. **Apply what they approve.** `marcora:apply_grounding_fix({finding_ids: [...]})`. You never write the fix yourself — you reference the recommendation by id. Redirect a specific fix with `context_item_overrides`.
5. **Report honestly.** Applying is async: poll `marcora:get_generation_status({generation_id})` using the integer `generation_id` from each job. The `document_updated` field is the honest outcome — `true` means the document changed, `false` means the recommendation was already covered and nothing was written. Say which; don't imply every applied fix changed something.
6. **Re-ground** if they revised the document. Re-scanning an unchanged document is fast, because unchanged claims are reused.

`apply_grounding_fix` also applies **Context Intelligence health-audit** recommendations from `list_ci_findings` — same tool, same shape.

> **⚠️ Never pass a fragment with a `content_id`.** `content` + `content_id` replaces the document's **entire body**, exactly like `update_content`. If the user asks you to ground one paragraph of an existing document, pass `content_id` **alone** — passing just that paragraph would destroy the rest of the document.
