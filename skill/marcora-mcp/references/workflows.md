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
1. `marcora:list_community_blueprints` (optional `category`, `limit` default 150 max 300, `offset`) — returns a compact index of `community_blueprints` (`id`, `slug`, `name`, `category`, `is_featured`), plus `total` and `next_offset` (when `next_offset` is not `null`, call again with `offset=next_offset`).
2. For summary, contributor info, input instructions, and full sample content on a specific one: `marcora:get_community_blueprint_details(blueprint_exchange_id=<id>)` using the returned `id`.
3. **State your plan** (this clones the blueprint into the user's library).
4. `marcora:import_community_blueprint(blueprint_exchange_id=<id>)` — returns the new team-level `uuid` for use with `create_content`.

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
3. Later, when the user asks whether it was opened: `marcora:get_share_link_activity(share_link)` with the link or its token, or `marcora:list_share_link_activity(filter?, query?)` to see every link in the active workspace. Report `summary`; if `opened` is true but the viewer list is short or empty, say some opens predate open details (`coverage_note`). Viewers are anonymous numbers, so never name who opened it. Never open the link yourself to check.

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
3. `marcora:update_project(project_id, …)` with ONLY the fields changing (a partial update — omitted fields are untouched).
   - `name` (text)
   - `visibility` enum: `team` | `private`
   - `status` enum: `active` | `archived`

**Note.** Setting `status="active"` requires available active-project usage on the team's plan — call returns a refusal stating the plan's active-project limit if exhausted; relay it as written.

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

Per-element character limits: `company_overview` 10,000; `brand_voice`, `writing_style`, `writing_examples` 20,000 each. Overflow returns an input error naming the limit, and nothing is saved.

---

## Recipe I — Ground a document against the context library

Grounding runs a two-pass check on a document's factual claims and sorts each into **supported**, **conflict**, **gap**, or **note**. Use it after drafting, or whenever the user asks whether something is accurate / on-message / consistent with what the company has already said.

**How two-pass grounding works:**
- **Pass 1 (built-from sources):** checks the sources the document was built from (`context_item`, `project_brief`, `brand_foundation`, plus recorded `web_research` and `connected_app` material used during generation). **Conflicts come only from what the document was built from.**
- **Pass 2 (other collections):** checks other accessible collections for support on remaining claims. **Other collections can support a claim or add a note** (`notes[]` with `kind: "other_collection_disagrees"` when another collection says something different), never a conflict.
- **Claim subject and battle-card rule:** each claim and finding reports `claim_subject` (`{ kind: "team" | "company" | "general" | "unknown", company_name, confidence }`). A claim about the user's own company (`team`) is checked only against material about their company; a claim about another named company (`company`) is checked against material about that company, which can support or contradict it. On conflict claims and conflict findings, `conflict_scope` is `"team_facts"` (disagrees with your own facts) or `"company_material"` (disagrees with your material about that company, not your own facts). A company conflict's fix revises the document (`context_item_id: null`), never your facts, and a company gap offers no add-to-library (`add_to_library_eligible: false`; the backend refuses it).
- **Recorded research appears as a source; grounding itself never browses.**

**The loop: draft → ground → review → apply → re-ground.**

1. **Scan.** `marcora:check_content_grounding(...)` in one of three modes:
   - `content_id` alone — scan a document that already exists. **This is the safe default.**
   - `content` alone — hand over markdown; Marcora stores it as a new document and scans it.
   - `content_id` + `content` — **replaces that document's entire body**, then re-scans. See the warning below.
2. **Poll if needed.** It waits ~20 seconds. If you get `status: "running"`, poll `marcora:get_grounding_result({scan_id})` every 15–30 seconds — a fresh scan usually takes 120–150 seconds. **Poll with the `scan_id`, not the `content_id`.** Never call `check_content_grounding` again to check progress; that starts a second scan.
3. **Check coverage first.** Before you tell the user a claim is unsupported, read `coverage_complete`. `false` means some context items were not part of this check, so a gap may still have support in one of them. `coverage_reason` says why: `library_catch_up` (some context items have not been prepared yet; re-run the check to include more of them), `library_extraction_failed` (some could not be prepared), `library_token_budget` (the reference library is larger than one check can read; the unread items appear in `excluded_items`), `source_access_changed` (a built-from source is no longer accessible), `source_content_changed` (the document or a source this check read was edited after it completed; re-check to refresh), or `support_lookup_incomplete` (pass-2 support lookup across other collections did not finish). `excluded_items`, when present, lists context items skipped because they were being edited during the check (`reason: "sync_lock"`); it can appear even when `coverage_complete` is `true`. If either signal is there, describe gaps as "not yet confirmed", not "unsupported".
   - Check `summary.notes` (note-only claims, disjoint from `supported`, `conflicts`, and `gaps`) and each claim's `claim_subject` (`team | company | general | unknown`), `conflict_scope` (`team_facts | company_material`, on conflicts only), `notes[]` (`kind: "other_collection_disagrees"`, `message`, `refs`), and `add_to_library_eligible` (true only when the claim is a completely searched, nowhere-supported true gap eligible to be added to the library; false for company gaps, notes, supported claims with notes, or incomplete checks).
   - Each ref on `claims[].refs`, `claims[].notes[].refs`, and `corpus_items[]` includes `source` (`context_item`, `project_brief`, `brand_foundation`, `web_research`, `connected_app`), `pass` (`1` or `2`), and source identity details (`collection`, `core_context_item_id`, `research_id`, `research_turn_id`, `owner_id`, `urls`, `app_sources`).
   - A supported claim may carry `support_only_calls`: it appears only when every supporting source is a call. Tell the user such a claim rests only on calls, which are one conversation's word rather than a written source.
4. **Review with the user.** Walk them through `findings[]`. Each carries `claim_subject`, (on conflicts) `conflict_scope`, the **full** `suggested_fix`, and the `context_item_id` applying would write to. Hand them the `link_url` so they can see it in Marcora.
5. **Apply what they approve.** `marcora:apply_grounding_fix({finding_ids: [...]})`. You never write the fix yourself — you reference the recommendation by id. A `company_material` conflict's fix revises the document (`context_item_id: null`), never your facts, and a company gap offers no add-to-library. Redirect a specific fix with `context_item_overrides`.
6. **Report honestly.** Applying is async: poll `marcora:get_generation_status({generation_id})` using the UUID `generation_id` from `jobs[]`. Findings whose fixes land in the same document (the same context item, or the same content document when `context_item_id` is null) are applied together in one run and share one `generation_id`, so poll each distinct `generation_id` once; its `document_updated` covers every finding in that run. Brand Foundation findings are not grouped. A finding that comes back in `errors[]` with "Marcora is already updating this document." hit a document another run still holds: wait for that run, then retry just those findings. The `document_updated` field is the honest outcome — `true` means the document changed, `false` means the recommendation was already covered and nothing was written. Say which; don't imply every applied fix changed something.
7. **Re-ground** if they revised the document. Re-scanning an unchanged document is fast, because unchanged claims are reused.

`apply_grounding_fix` also applies **Context Intelligence health-audit** recommendations from `list_ci_findings` — same tool, same shape.

> **⚠️ Never pass a fragment with a `content_id`.** `content` + `content_id` replaces the document's **entire body**, exactly like `update_content`. If the user asks you to ground one paragraph of an existing document, pass `content_id` **alone** — passing just that paragraph would destroy the rest of the document.

