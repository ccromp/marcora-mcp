# Changelog

All notable changes to the Marcora MCP server will be documented in this file.

## 2026-07-26 (doc accuracy)

### Fixed

- **Release tag convention corrected in the README.** It said releases are tagged `skill-vX.Y.Z`; the actual convention has been `marcora-vX.Y.Z` since v0.2.3, so anyone following it was looking for a tag format that no longer exists. The README now also notes that the skill's own `metadata.version` moves independently of the release tag.

## 2026-07-25 (agent name: Cora → Marcora)

### Changed

- **The agent is called Marcora.** The retired pre-rebrand name has been removed from every user-visible string in this repo's docs and companion skill — most visibly the `set_active_team` warning, which now reads "app tabs, Marcora agent sessions, other clients". No behavior change and **no tool, field, or enum was renamed**: `cora_requested` / `cora_proactive` sources and the `cora_session_id` / `cora_message_snippet` metadata keys are unchanged stable identifiers and will stay as they are.

### Skill → v0.7.2

- Agent-name wording only, in the `set_active_team` decision-table row. Content-only release — `version: "latest"` picks it up on the Marcora agent's next session; no agent change needed.

## 2026-07-25 (new-account setup hold documented)

### Documented

- **A brand-new account holds tool calls until its setup finishes.** For up to 72 hours after an account is created, and only until Marcora has finished building its context, every `tools/call` returns "Your Marcora account setup is still underway…" as a *successful result* rather than running the tool. `initialize` and `tools/list` are unaffected, so the connection looks healthy throughout. This shipped with MCP-first signup; it was previously undocumented. See [Errors & Troubleshooting → Account Setup](./errors.md#account-setup).

## 2026-07-22 (content/document language normalization)

### Changed

- **Tool descriptions and schemas normalized to content/document terminology.** Wording across `ask_content_assistant`, `get_generation_status`, `update_content`, `update_context`, and `produce_plan` now refers uniformly to a "content document". This is a wording change on the served surface, not a behavior change.
- **`produce_plan` output `path` values are now `blueprint` and `freeform`.** The two async paths are unchanged — generated from a blueprint vs. no blueprint; the legacy value names were retired in favor of these. Poll `get_generation_status` exactly as before.

### Fixed

- **`get_generation_status` no longer returns a storage-specific `document_type` field** on the Content Assistant flow. It has been removed from both the response and the output schema. Read `document_updated` to tell whether the run changed the document.
- **`create_content` output `generation_id` is a `string` (UUID), not an `integer`.** The value has always been a UUID at runtime — only the advertised type label was wrong; what you poll `get_generation_status` with is unchanged. (Mirrors the earlier `apply_grounding_fix` fix.)

### Skill → v0.7.0

- `produce_plan` guidance updated to the new `path` values, and content/document terminology applied across the `update_content` / `ask_content_assistant` / `produce_plan` guidance. Workflow guidance changed, so this is a skill CONTENT release — `version: "latest"` picks it up on the Marcora agent's next session; no agent change needed.

## 2026-07-21 (content grounding)

### Added

- **Content grounding — three new tools (`check_content_grounding`, `get_grounding_result`, `apply_grounding_fix`).** Grounding checks a document's factual claims against the team's own context library and sorts each into supported, conflict, or gap. Together the three close the agent-writing loop — draft, ground, review, apply, re-ground — without leaving the conversation. Requires the Command plan.
  - `check_content_grounding` scans new or existing content. Three entry modes: an existing document by id, fresh markdown (stored then scanned), or both (revise then re-scan). It waits ~20 seconds inline and hands off to polling if the scan is still running.
  - `get_grounding_result` reads a result and never starts a scan. **Poll it with `scan_id`** — that reads the exact run you started. Passing `content_id` alone returns the latest *completed* grounding and deliberately skips an in-flight scan, so it is the wrong call for polling.
  - `apply_grounding_fix` applies a finding's stored recommendation by id — the agent never composes the fix itself. It serves **both** content-grounding findings and Context Intelligence health-audit recommendations, and returns one job per finding. Poll `get_generation_status` with a job's `generation_id` (a UUID); the `document_updated` field there tells you whether the document actually changed or the recommendation was already covered.

### Changed

- **Findings now carry their full `suggested_fix`, not a presence flag,** plus the `context_item_id` that applying would write to — so a fix can be reviewed with the user before it is applied.
- **Context Intelligence docs corrected:** applying a finding's suggested fix no longer "happens in the Marcora web app only". `apply_grounding_fix` does it from the MCP, for health-audit findings as well as grounding ones.
- **`list_ci_findings` / `get_ci_finding` return a `link_url`,** so every finding-bearing tool links consistently.

## 2026-07-14 (brand-foundation link train)

### Fixed

- **`update_brand_foundation` now returns a `link_url`.** `get_brand_foundation` returned a `link_url` deep-linking the Brand Foundation section; `update_brand_foundation` returned only `{ element, content }`, and its output schema promised nothing more. With a successful write but no link to hand back, agents filled the gap by inventing one — `https://app.marcora.ai/brand-foundation`, which does not exist as a route. It 404s, redirects to `/home`, and the user loses the chat they were in. The update response now carries the same `link_url` as the getter (`/context-hub?tab=brand-foundation`), declared in the output schema; both tools read it from one shared constant so they can't drift apart again. The tool description now also tells the model to use the returned link verbatim rather than construct one.

### Changed

- **Docs:** `docs/tools.md` documents `link_url` on both `update_brand_foundation` and `get_brand_foundation` — the getter has always returned it, but its Output table never listed it.
- **Skill → v0.5.4:** Recipe H2 (update a Brand Foundation element) gained the "hand the user the returned `link_url`" step that every other link-returning recipe already had, plus a matching pitfall entry and decision-table note. Workflow guidance changed, so this is a skill CONTENT release — `version: "latest"` picks it up on the Marcora agent's next session; no agent change needed.

## 2026-07-14 (later train)

### Fixed

- **`update_context` — `collection_id` / `project_id` now accept a JSON `null`.** The tool always documented these as "REQUIRED (but nullable)" with full-replace semantics — pass `null` to move an item back to the top level of the Reference Library or detach it from a project — but the input schema typed them as a bare `integer` / `string`. Strict MCP clients validate arguments against that schema *before sending*, so `null` was rejected client-side ("Value is not a valid integer") and omitting the field returned `Missing param` — meaning the documented detach was impossible to express. The schema now types them `["integer","null"]` / `["string","null"]` (uuid `format` preserved), so `null` reaches the backend, which already handled it. No behavior change on the server — the advertised contract just matches what the tool always did.
- **`add_context` — items created without a `collection_id` are no longer invisible.** Omitting `collection_id` (the normal "add to the Reference Library" case) wrote the item with `collection_id = 0` — a dangling reference the read layer filtered out, so the item was returned by no read path (`list_context_items` omitted it, `get_context_item` 404'd, semantic search never matched it) even though the create call succeeded and echoed the item back. Omitted, `null`, and `0` now all mean the top level of the **Reference Library**, and the item is visible everywhere. `update_context` matches: `collection_id: 0` is coerced to `null` (it previously errored "Collection not found").

  Note the client-visible difference between the two tools: `add_context.collection_id` is still typed as a bare `integer` in the input schema, so a strict MCP client can only **omit** it or pass `0` — it can't send a literal `null`. That costs nothing, because the field is optional there and omitting it is the idiomatic "file at the top level" path. `update_context.collection_id` is the one that needed the nullable type, because it's required-but-nullable with full-replace semantics: without a sendable `null` there was no way to express "detach".

### Changed

- **Docs:** `docs/tools.md` now spells out the Reference-Library filing rule on `add_context`, and on `update_context` documents the `null` (and `0`) detach plus the omit asymmetry — omitting `collection_id` errors, omitting `project_id` silently detaches. No companion-skill change (no workflow changed), so the skill stays at v0.5.3 and the Marcora agent needs no update.

## 2026-07-14

### Changed

- **Playbook tools now return `anchor_date` + `link_url`.** Every playbook read/write tool — `list_playbooks`, `get_playbook`, `create_playbook`, `create_playbook_from_plans`, `update_playbook` — now returns the playbook's persisted `anchor_date` (`YYYY-MM-DD`, or `null`) and a `link_url` that opens it in the Marcora web app. `create_playbook` and `update_playbook` also accept `anchor_date` as an input (the reference date each item's `offset_days` counts from, and the default when instantiating). `instantiate_playbook` now returns the created **cycle** (`run` / `run_id`, with the cycle's `link_url` → `app.marcora.ai/runs/{run_id}`), a `created_count`, and a `plans[]` array in which **each plan carries its own `link_url`** → `app.marcora.ai/plans/{plan_uuid}`. Documented in `docs/tools.md`; the companion skill's **Content Plans & Playbooks** chapter now tells agents to hand these links to the user. No behavior change to what the tools do — only richer, link-carrying responses.
- **`get_team_info` description sharpened.** The tool description now leads with the trigger — always call it when the user asks what teams they have / belong to or wants to switch teams, rather than answering from memory or session context (which knows only the single active team and undercounts). Doc copy reconciled in `docs/tools.md`. Output shape unchanged.
- **Companion skill `marcora-mcp` v0.5.3 + rebuilt `.skill`.** Playbook-chapter guidance for the new `anchor_date` / `link_url` response fields. Content-only — picked up automatically by the Marcora agent at `version: "latest"`, no agent change.

## 2026-07-13

### Added

- **Context Intelligence tools documented.** The four Context Intelligence tools — `list_ci_findings`, `get_ci_finding`, `update_ci_finding_status`, and `trigger_health_audit_scan` — are now documented under a new **Context Intelligence** category in `docs/tools.md` and the README tool table. These tools were already live on the customer server (`mcp.marcora.ai`); this fills a documentation gap. Context Intelligence is Marcora's automated review layer: health-audit and web-freshness scans produce **findings** (stale content, contradictions, outdated web sources, gaps) with a `pending → acknowledged / dismissed / resolved` lifecycle. `trigger_health_audit_scan` is plan-gated (Business/Command, ≥50 credits) and runs in the background; applying a finding's suggested fix is done in the Marcora web app, not through the MCP. No tool behavior changed.
- **`get_team_info` + `set_active_team` — new Account tools.** `get_team_info` (read-only) returns every team you belong to with its full member roster — including each active member's numeric `user_id` (what `assigned_to` expects) plus pending invites — so an agent can resolve "assign this to Sarah" to a real id. `set_active_team` switches your active team and returns `previous_team_id` for a switch → work → restore loop; its description carries a global-effect warning (the change applies everywhere for your account). Excludes credits/subscription (that stays with `get_current_user_info`). Brand server tool count 54 → 56.
- **`list_content` — optional semantic `search`.** Pass a natural-language `search` query and results are ranked by semantic relevance instead of recency; each row then carries a `relevance_score` (cosine `0`–`1`, higher = more relevant). Omitting `search` is unchanged (recency-ordered, no score) — fully backward-compatible.
- **`list_context_items` — optional semantic `search`.** Same addition: pass a natural-language `search` query to rank items by semantic relevance (by each item's best-matching chunk) instead of recency; each item then carries a `relevance_score` (cosine `0`–`1`). Omitting `search` is unchanged.
- **Cross-tool ranking.** The `relevance_score` values from `list_content` and `list_context_items` are **cross-comparable**: call both with the same `search` query, merge the two result arrays, and take the top matches by `relevance_score` — then confirm with the user before pulling full text with `get_content` / `get_context_item`. Documented in `docs/tools.md`.
- **Companion skill `marcora-mcp` v0.5.2 + `.skill` release.** The skill now teaches the semantic-search discovery path (a new bullet + "Steps (semantic-search path)" in Workflow 5 and a decision-table row: rank `list_content` / `list_context_items` by `relevance_score`, merge cross-tool, confirm before opening full text). Content-only — picked up automatically by the Marcora agent at `version: "latest"`, no agent change.

## 2026-07-12

### Changed

- **One server, one skill.** The separate **Content Plans** MCP server has been retired and its 11 tools folded into the main **Brand Context & Writing** server (`mcp.marcora.ai`) — so users connect **one** server. In lockstep, the two companion skills are unified into **one** (`marcora-mcp`, v0.5.0): the former `marcora-workflow-builder` skill is now the skill's **Workflows** chapter, and a new **Content Plans & Playbooks** chapter covers the plans board. The Claude Code plugin + marketplace bundle rebuilt to ship one server + one skill (plugin v1.1.0).

### Added

- **Content Plans & Playbooks tools now on the main server** — `produce_plan` (produce a plan's content — async on both the blueprint→deliverable and no-blueprint→canvas paths; poll `get_generation_status`), plus the six playbook tools `list_playbooks`, `get_playbook`, `create_playbook`, `create_playbook_from_plans`, `update_playbook`, and `instantiate_playbook` (run a playbook into a batch of plans, optionally anchored to a date via `anchor_date` + each item's `offset_days`). Documented in `docs/tools.md` under **Plans & Playbooks**. Plans are `private` by default; playbooks default to `team` and instantiation inherits the playbook's visibility.

## 2026-07-02

### Added

- **`invite_user` — new Account tool.** Invite someone to the team by email as a `creator` or `admin`, or into a specific project as a `collaborator`, without leaving the agent. It wraps the same invitation flow the web app uses (dedupe guards, invitation email, sign-up/login links) and returns the exact `invite_link` in the response, so the agent can share it directly (e.g. paste it into Slack) instead of relying on the email — `emailed: true` confirms the invitation was sent. Authorization matches the app: admins can invite any role, a creator can invite collaborators only, viewers cannot invite. `project_id` is required for a collaborator (the project they'll work in) and optional for a creator/admin (also adds them to that project and deep-links their invite there — it does not limit their access). *Currently on the `dev` server; not yet promoted to the live customer MCP.*

## 2026-06-30

### Changed

- **`update_content` — `change_summary` now asks for skimmable markdown.** The guidance previously said only that markdown was "supported"; agents kept writing flat plain-text run-ons. It now gives a concrete shape — one line for a small edit, or a short bulleted list (each bullet a bold 2–5 word lead, a colon, then the detail) for multi-part edits — so the AI-assistant history sidebar stays scannable. Wording only; no schema change.
- **`create_content` / `update_content` — default to in-place editing for revisions.** Both tool instructions now make clear that revising an existing document should use `update_content` (edit in place), not `create_content` (which forks a new doc). They state edits are non-destructive — Marcora keeps a full version history and the user can revert from the app — so agents stop defensively duplicating a document to "preserve the original." Mirrored in `docs/tools.md` and the `marcora-mcp` skill. No input/output schema changes.
- **`marcora-mcp` skill — tool-anchored trigger + URL→id guidance (v0.4.0).** The skill `description` now leads with "use BEFORE calling any Marcora MCP tool" and names a pasted Marcora URL as a trigger, so agents reach for the workflow guidance instead of driving the raw tools blind. Added a "Starting from a Marcora URL or ID" section: the UUID in an `app.marcora.ai/library/<id>` or `/canvas/<id>` link IS the `content_id` — use `get_content` / `update_content` directly instead of web-browsing the page.
- **`add_context` — `import_url` is now asynchronous.** Importing a URL used to fetch and convert the page inline, which could take 15–60s and **time out** on slow pages — and bulk-importing several URLs back-to-back made it worse. Now the call returns **immediately** with the new item's `id` and `import_status: "processing"`; the content finishes loading in the background a moment later. Poll `get_context_item` to confirm (the content appears and `import_status` flips to `"ready"`). You can fire many imports in a row without timeouts. If an item is still missing a minute or two later, the fetch failed — check the URL and retry. The `content` (paste) and `connected_webpage_url` paths are unchanged.

### Added

- **`update_content` — `change_summary` input.** Pass a summary of what you changed and why (e.g. "Tightened the closing CTA"); it's shown in the document's AI-assistant history sidebar in place of the generic "Content updated via MCP." that every MCP edit otherwise logs — so after several edits the history stays scannable instead of a wall of identical rows. Size it to the change (a sentence to a few paragraphs) and use markdown where it helps. Optional and backward-compatible: omitted or whitespace-only falls back to the generic label. Only recorded when the call also changes the body (`content`).
- **`add_context` — `import_status` output field.** For `import_url` items: `"processing"` immediately after the call, `"ready"` once content has loaded. `null` for pasted content and web pages. (Relatedly, `content` is `null` and `word_count` is `0` in the immediate response for imports — fetch the body with `get_context_item`.)

## 2026-06-28

### Changed

- **`create_content`, `get_relevant_context`, `update_content` — context-fetch guidance is now conditional on who writes.** The instructions previously told agents never to call `get_relevant_context` before `create_content`. That holds only when Marcora does the writing (the `instructions` path, which pulls Brand Foundation + Reference Library + Project Context internally). When the agent composes the content itself and saves it via the `content` parameter — of either `create_content` or `update_content` — those paths store the text verbatim and consult no context, so the agent must call `get_relevant_context` with `include_brand_foundation: true` first or the result is off-brand. Tool instructions, `docs/tools.md`, and the `marcora-mcp` skill were updated to make the rule conditional. No input/output schema changes.
- **MCP server display name** changed to **"Marcora: Brand Context & Writing"** (was "Marcora MCP Server").

## 2026-06-27

### Changed

- **`add_context` / `update_context` — `content_url` renamed to `import_url`** (breaking, on those two tools). The behavior is unchanged — fetch a public URL once, convert to clean markdown server-side, store it as a static snapshot — but the name now makes clear it is a **one-off import** that does NOT retain the URL or create a refreshable item. Callers using `content_url` must switch to `import_url`. (Use the new `connected_webpage_url` / `refresh_webpage` instead when you want a tracked, refreshable web page.)

### Added

- **`add_context` — `connected_webpage_url`.** Pass a URL to create a true, tracked **web-page** context item (`content_type: "webpage"`): the page is fetched, stored, and its URL is **remembered** so it can be re-pulled later. Dedupes by URL — adding a URL that's already tracked updates the existing item in place instead of creating a duplicate. Requires admin or editor role (matches the in-app *Add web page* rule). This brings MCP to parity with the app's *Add web page* feature, which `import_url` (a static snapshot) does not.
- **`update_context` — `refresh_webpage: true`.** Re-pulls a tracked web-page item's content from its stored URL — the same action as the app's refresh button. No content needed; `name` / `content` / `import_url` are ignored when set. Only valid on items created via `connected_webpage_url`; returns a clear input error on any other item. Requires admin or editor role.
- **`list_context_items` / `get_context_item` — `source_url` field.** For `webpage` items this is the tracked page URL (`null` for all other types), so an agent can discover which items are refreshable and re-pull them without the user hand-feeding URLs.

### Fixed

- **`add_context` web-page items created without a collection are no longer hidden.** A web page added via `connected_webpage_url` with no `collection_id` was created successfully but then excluded from `list_context_items` / `get_context_item` (it was stored with `collection_id = 0`, a dangling reference the team-scoped read queries filter out). Now stored as `null`, so new web-page items appear immediately. (Only affected the new web-page path; `content` / `import_url` items were never impacted.)

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

- `add_context` and `update_context` — new optional `content_url` parameter. Pass a public URL and the backend fetches it and converts the page to clean markdown server-side using a headless browser + Mozilla Readability, then stores the result as the context item body. Use this when the body is large, comes from a presigned-link export (Google Doc, Composio sandbox), or you'd otherwise have to pull the page into the conversation just to forward it. Mutually exclusive with `content` — exactly one of `content` / `content_url` is required on `add_context`; on `update_context` you may also omit both to leave the body unchanged.

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
