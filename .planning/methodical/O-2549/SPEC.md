# O-2549 — docs fan-out: `update_context` null-detach (#212) + omitted-collection fix (#213)

## Goal
Both changes are LIVE on prod (`api.marcora.ai` → `9dd31ce`, verified; prod brand
`tools/list` serves `update_context.collection_id: ["integer","null"]` /
`project_id: ["string","null"]`). Per the fan-out checklist's timing rule (docs land
on prod-live, not staging merge), publish the customer-facing documentation for the
corrected behavior. Done = `marcora-mcp` docs updated + Strapi pages updated, and the
DoE told it's published.

## Verified behavior on prod (read from merged `origin/main`, not from a summary)
**`add_context` (create)** — `validateCollectionInput` maps omitted / `null` / `0` → SQL
NULL and validates real IDs. So all three mean **root Reference Library**, and the item
is VISIBLE. (#213 deleted the `manualCreateCollectionId` wrapper that re-broke the
omitted case back to `0` — a dangling FK the read layer filtered out, i.e. the
invisible-item bug.)

**`update_context` (full-replace)** — `requireParam(body,'collection_id')` is STILL
enforced, then `nullableInt` → `rawCollectionId === 0 ? null : rawCollectionId`:
- `collection_id`: **omitting → hard error "Missing param."** `null` **or** `0` → root
  Reference Library (the `0 → null` coercion is new in #213; `0` previously 500'd
  "Collection not found"). A real id → moved + validated.
- `project_id`: NOT `requireParam`'d — `nullableUuid` maps omitted/`null`/`''` → null,
  so **omitting it silently DETACHES** the item from its project. This asymmetry is why
  the docs say "you must pass both on every call".
- #212 makes the documented `null` actually expressible: previously a spec-compliant
  client rejected `null` against the bare `integer`/`string` schema before sending.

## Constraints / out of scope
- **Docs only.** No backend/tool-definition change (the tool description on prod is
  already accurate — it always said "REQUIRED (but nullable) … pass null").
- **No skill release, no version bumps, no Cora action.** Per the checklist: "Pure
  tool-metadata changes (description/schema/annotations, no skill-content change) need
  only steps 1–3." Neither #212 nor #213 changes a workflow the skill teaches — the
  skill's guidance ("Reference Library = add_context with no project_id") was always
  correct; the backend was buggy. So `skill/marcora-mcp/**`, `server.json`,
  `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` stay untouched.
- Do NOT re-run the #203/#193 fan-out (already complete + vetted under O-2527).

## Tasks
1. `docs/tools.md` — `add_context`: `collection_id` row + prose note that omitted/null/0
   all mean the root Reference Library (and the item is visible).
   _Verify:_ diff reads correctly; claims match the merged `origin/main` code above.
2. `docs/tools.md` — `update_context`: record that `null` is now expressible (schema
   advertises it), that `0` is accepted as an alias for null, and the
   omit-collection_id-errors vs omit-project_id-detaches asymmetry.
   _Verify:_ same.
3. `docs/changelog.md` — dated 2026-07-14 entry covering #212 + #213.
   _Verify:_ entry present, accurate, no skill-release claim.
4. PR → `main` (repo convention: squash-merged PRs).
   _Verify:_ PR URL.
5. Delegate Strapi leg to **Content Publisher** (`update_context` + `add_context` pages;
   `doc_page` parent `mcp-tools`, keep category/slug/order).
   _Verify:_ their published documentIds + HTTP 200s.
6. Confirm published to the DoE — closes the lane.

## Outcome (2026-07-14)
- Prod verified live BEFORE publishing: `api.marcora.ai/health` → `9dd31ce`; prod brand
  `tools/list` (minted prod token via `agent-token-exchange`, direct handshake at
  `/x2/mcp/EbZaDl-X/mcp/stream`) → 56 tools, `update_context.collection_id`
  `["integer","null"]`, `project_id` `["string","null"]`. Timing rule satisfied.
- T1–T3 ✅ `docs/tools.md` (add_context + update_context) + dated `docs/changelog.md`
  entry. Diff verified docs-only — no skill/version files touched.
- T4 ✅ marcora-mcp **PR #13** → `main`.
- T5 ✅ Strapi leg delegated to Content Publisher — thread **O-2590**, brief `wp/437`
  (scope: `update_context` + `add_context` pages only).
- T6 — confirm to DoE once Content Publisher reports published documentIds.
- Cora: no action (no skill-content change; skill stays v0.5.3, `version:"latest"`).
