# O-3408 — #294 MCP docs / skill / Cora fan-out (PREPARE + HOLD)

Brief: wp/606 (`O-3188-O-3396-production-docs-fanout-brief.md`, DoE).
Canonical process: `docs/mcp-change-fanout-checklist.md`.

## Goal

Prepare the complete documentation + skill-bundle + Cora-skill fan-out for
backend **#294 / O-3396** (canvas·deliverable → content·document language sweep
+ two structural contract changes), grounded exactly on the staged tool
definitions. **Publish/merge/upload NOTHING** until the Director posts the live
production SHA and says `promotion live — go`. This lane produces held
artifacts + a ready-to-fire promotion checklist only.

## Grounding (verified this session)

- Backend staging tip = `110b474` ✓. #294 squash commit = `41306fb` ✓
  ("O-3396: MCP def drift…"). Production train = draft backend PR #298
  (staging→main). Truth source = `src/modules/mcp/generated-metadata.ts` +
  `registry.ts` at `41306fb`.
- Cora pins ONE unified companion skill = `marcora-mcp.skill`
  (`CORA_MARKETCORE_SKILL_ID` / `skill_01UtGxCJJmSZNTDDwPFzZcXX`) + anthropic
  doc-format skills (pptx/docx/xlsx/pdf). The old `marcora-workflow-builder`
  skill was folded into `marcora-mcp.skill` on 2026-07-12 (repo #2). → The Cora
  audit is fully covered by this bundle + a grep of Cora's system-prompt prose.
- Prior art: O-3064 grounding tools ran the same held pattern (held repo PR #22,
  branch `docs/O-3064-grounding-tools`). Keep #294 INDEPENDENT of it (branch off
  `origin/main`; touch only #294 surfaces).

## The #294 contract truth (before → after)

1. **`list_external_shares.document_name`** desc: "Canvas title or deliverable
   name, or null." → "The document's name, or null."
2. **`ask_content_assistant`** — description + `content_id` param + `notfound`
   error: canvas/deliverable → content document.
3. **`create_blueprint_draft`** — `id` output field desc: "Canvas record ID for
   the blueprint draft." → "Record ID for the blueprint draft."
4. **`create_content.outputSchema.generation_id`**: `integer` →
   `string`/`format:uuid` (8th surface — brief's contract list; its doc page
   `tools.md:1175` still says integer).
5. **`get_generation_status`** — description + `content.content_id` desc, and
   **REMOVE the `content.document_type` field** from the outputSchema (registry
   also drops it from the response body).
6. **`update_content`** — description sweep canvas/deliverable → content
   document (incl. "non-editable canvas type" → "non-editable document type").
7. **`update_context`** — description: "linked canvas" → "linked editor
   document".
8. **`produce_plan`** — description + **`path` enum: `deliverable`/`canvas` →
   `blueprint`/`freeform`** (+ neutralized path message).

Scope discipline: mirror #294 EXACTLY. Do NOT rewrite pre-existing
canvas/deliverable mentions in OTHER tools' docs (e.g. `list_content`,
`content_type` enum values `canvas`/`deliverable` which are legitimate public
API enums, `get_project` brief, `update_project`). Those were not in #294 and
are "unrelated doc drift" (hard gate). Residuals get flagged in the handback,
not silently swept.

## Deliverables (ALL held / unpublished)

### A. Strapi doc-page change-set (Content Publisher publishes at go-time)
Held work-product: precise per-page edits for each affected customer-facing
tool page — BOTH render sources (`parameters` component AND `inputSchema` field,
checklist §2a) — plus a ready-to-fire Content Publisher delegation brief.
Verify which of the 8 have live Strapi pages first. NOT published here.

### B. GitHub bundle (`ccromp/marcora-mcp`) — held branch, draft PR, NOT released
- `docs/tools.md`: fix the 8 tool sections only (canvas/deliverable → content/
  document; remove `document_type` row; `path` enum; create_content
  generation_id integer→uuid).
- `README.md`: `update_content` row wording.
- `docs/changelog.md`: ADD one dated #294 entry (do NOT edit history).
- `skill/marcora-mcp/SKILL.md`: fix `path:"deliverable"/"canvas"` →
  `blueprint/freeform` (line ~339 — THE Cora logic leak), sweep the in-scope
  tools' wording, bump `metadata.version` 0.6.0 → 0.7.0.
- `references/workflows.md` + `references/pitfalls.md`: audit + fix in-scope
  leaks (leave internal-architecture notes).
- Rebuild `marcora-mcp.skill` zip (`cd skill && zip -r -X -q ../marcora-mcp.skill marcora-mcp`).
- Version bumps: server.json / plugin.json / marketplace.json as needed.
  ⚠️ Sequencing: if O-3064/#22 releases first, rebase version bumps — flag to DoE.

### C. Cora skills compatibility audit
- Audit `marcora-mcp.skill` (SKILL.md + references) for `path === 'deliverable'`,
  `document_type`, canvas/deliverable wording → fixed in B.
- Grep Cora's system-prompt prose (`src/modules/cora-agent`) + `get_system_context`
  for the same patterns → FLAG hits for App Developer (not my artifact to edit),
  or report explicit zero-result evidence.

### D. Promotion-live checklist + handback
Ordered go-list keyed to fanout checklist §2–4, executable the moment the DoE
supplies the prod SHA + "promotion live — go". Before/after evidence for
get_generation_status, produce_plan.path, create_content.generation_id. Cora
audit result. All artifacts left held; thread → ready_for_review for DoE.

## Hard gates (from brief)
PREPARE only. No Strapi publish, no repo merge/release, no Skills-API upload, no
customer-visible change until DoE posts the exact live prod SHA + "promotion
live — go". Do not touch backend MCP defs/runtime. No unrelated doc drift. Keep
the canvas/deliverable implementation distinction off customer/agent surfaces.

## Task list (all complete — held)
- [x] T1 — `docs/tools.md`: get_generation_status (document_type row removed), ask_content_assistant, update_content, update_context, produce_plan (path enum), create_content generation_id→uuid. Verified: stale strings ×0 in scope; list_content residual intact.
- [x] T2 — `README.md` update_content row. Verified: grep.
- [x] T3 — `docs/changelog.md` 2026-07-22 entry (history untouched). Verified: git diff.
- [x] T4 — `SKILL.md` path leak → blueprint/freeform + in-scope wording + version 0.7.0. Verified: `path:"deliverable"` ×0.
- [x] T5 — `references/`: workflows.md zero leaks; pitfalls.md E1 internal note flagged as residual.
- [x] T6 — rebuilt `.skill` zip (26960 bytes); SKILL.md v0.7.0 confirmed inside. plugin/marketplace/server left (repo convention; release tag line independent).
- [x] T7 — Cora audit: zero code branches on path/document_type; SKILL prose leak fixed; system-prompt (DB-stored, App-Dev-owned) flagged for go-time grep.
- [x] T8 — Strapi change-set + Content Publisher brief (wp/607), all 7 pages confirmed live, both render sources specified.
- [x] T9 — committed + pushed branch, **draft** PR #23; handback + promotion-live checklist (wp/608). Nothing merged/published/uploaded.
