# O-3807 — Cora → Marcora prose sweep (MCP Server Engineer surfaces)

**Delegated by:** Director of Engineering (O-3756), on Chris's explicit order.
**Attestation:** Chris is aware of and requested this Cora→Marcora customer-facing
MCP metadata change. The agent was renamed **Marcora** in the ~May 2026 rebrand;
he wants the retired name gone from user-visible surfaces.

---

## Goal

Every **user-visible prose** reference to the retired agent name "Cora" is gone
from the three surfaces the MCP Server Engineer owns exclusively — the
`ccromp/marcora-mcp` skill/docs mirror **source**, the MCP tool metadata in
`marcora-backend/src/modules/mcp/`, and the Strapi MCP-tool doc pages — replaced
by "Marcora". Internal identifiers are untouched, so nothing breaks for a
connected client. Source and downstream skill copies agree afterwards, so the
next fan-out cannot silently re-introduce the retired name.

## Constraints / out of scope

- **PROSE ONLY.** Descriptions, "When to use" text, response/error strings, doc
  text, code comments. **Do NOT rename any shipped tool identifier or name** —
  that is a breaking change for every connected client.
  - ✅ **Verified: zero tool names contain "cora".** No breaking-rename decision
    is owed to Chris. (`grep '"name": "[^"]*[Cc]ora'` over
    `generated-metadata.ts` → only the three *server* display names, all already
    "Marcora …".)
- **Identifiers stay** — every one of these is load-bearing and untouched:
  - enum values `cora_requested`, `cora_proactive`
  - metadata keys `cora_session_id`, `cora_message_snippet`
  - module/dir `src/modules/cora-agent`, `src/modules/cora-channels`
  - TS symbols `CoraAgentServices`, `coraProgressQueue`, `sendCoraProgressForMcp`,
    `CoraServices`, …
  - realtime channel `cora_agent/<uuid>`, action key `cora_agent_progress`
  - endpoints `/cora-agent/recreate-agent`, `cora/agent/admin_upsert_skill_version`
  - env vars `CORA_AGENT_ID_LIVE`, `CORA_WORKER_ID_LIVE`, `CORA_MARKETCORE_SKILL_ID`
- **Not my lane** (report to DoE, do not edit): `src/modules/cora-agent/*`,
  `src/lib/billing.ts`, app UI strings (O-3794), Orchestra fleet configs (O-3782),
  Strapi *articles* (Content Publisher / DoM).
- **No `drizzle/` migrations.** None needed — prose only.
- `.planning/methodical/*/SPEC.md` archives in `marcora-mcp` keep their historical
  "Cora" references: they are dated internal records of work done under that name,
  not user-visible product surface.
- The canvas/deliverable distinction stays invisible, as always.
- The **etymology** paragraph in the rebrand article ("'Cora' from Cora, the agent
  inside the product…") **must stay** — it explains where the name Marcora comes
  from. Only the *stale agent-name* sentence in that article is a finding.

## Decisions already made

| # | Decision | Rationale |
|---|---|---|
| D1 | Replacement wording is **"Marcora agent sessions"** where the old text said "Cora sessions" | Matches verbatim what the ops sweep (O-3782) already wrote into the patched downstream copies, so source and copies converge instead of forking again |
| D2 | Backend work goes on a branch off `origin/staging`, draft PR → `staging`, `O-3807` in the title. DoE reviews; Chris gates merges | DoE brief + repo staging-first contract |
| D3 | `marcora-mcp` prose fix ships on its own merit, **not** gated on the backend promotion | It is a rename that has been true since ~May 2026, not a claim about tool behaviour. Nothing in it describes the staged metadata change |
| D4 | The **Skills-API upload** (`admin_upsert_skill_version`) is a LIVE production action touching the running Marcora agent → **gated**, not done unilaterally | Escalation rule 1: live-facing action |
| D5 | Pronoun "she" in `create_webhook_deep_link`'s example is left alone | Rename-only diff; changing product voice is a separate editorial call |
| D6 | `docs/changelog.md` historical entries **do** get the rename | They describe an ongoing mechanism ("picked up on X's next session") in a customer-facing changelog, and refer to the same live entity under its current name |

## Strapi timing — HELD, then released by DoE ruling (2026-07-26 02:52Z)

Initially held per the brief ("doc changes tied to tool-metadata text publish when
the metadata change is LIVE on prod"). **The DoE overruled the hold and approved
publishing immediately**, on the reasoning the spec had already flagged: the
publish-on-prod-live rule exists so docs never describe behaviour that isn't live,
and a *name correction describes nothing behavioural* — "Marcora" has been true
since May. Attestation: Chris requested these changes (O-3756).

**Executed:**

- Collection `mcp-tools`, `documentId` `w4g6o64qkdtnu8xquyhu6sbo` (`set_active_team`)
- `instructions`: `…running Cora sessions…` → `…running Marcora agent sessions…`
- `PUT ?status=draft` → 200, then `PUT` with no status → 200, `publishedAt`
  **2026-07-26T02:53:29.752Z**. Minimal single-field payload, so `parameters` /
  `inputSchema` were not touched (neither carried the string, so §2a's
  two-render-source agreement is preserved).

**Close status — origin correct, edge cache trailing (§2b diagnostic):**

| probe | `last-modified` | standalone `Cora` | new string |
|---|---|---|---|
| `?cb=` (origin) | 02:53:58Z | **0** | present |
| plain canonical (customer view) | 02:44:36Z, `age: 564` | 1 | absent |

Plain stale + `?cb=` clean is precisely the checklist's **"CDN only — content is
fine, wait it out"** signature. No Netlify credential in this lane, and the
checklist rates purge unreliable and a redeploy not worth it for <1h, so the close
gates on the page: re-probe the plain canonical until `last-modified` > 02:53:29Z
**and** standalone "Cora" ×0, with the semantic canary present.

---

## Task list

### A. `ccromp/marcora-mcp` — branch `fix/O-3807-cora-to-marcora`, PR → `main`

| # | Task | Verification |
|---|---|---|
| A1 | `skill/marcora-mcp/SKILL.md:384` — "Cora sessions" → "Marcora agent sessions". Leave L326 enum values | `LC_ALL=C grep -c 'Cora'` on the file = 0 for standalone; `diff` vs the ops-patched downstream copy shows only the version line |
| A2 | Bump `SKILL.md` `metadata.version` 0.7.1 → 0.7.2 | grep frontmatter |
| A3 | `docs/tools.md:112` — "running Cora sessions" → "running Marcora agent sessions". Leave the 4 enum-value rows | standalone-Cora grep = 0 |
| A4 | `docs/mcp-change-fanout-checklist.md` — 12 prose hits → "Marcora agent"; keep all endpoint/env/module identifiers | standalone-Cora grep = 0; identifier grep unchanged count |
| A5 | `docs/changelog.md` — 5 prose hits → "the Marcora agent" | standalone-Cora grep = 0 |
| A6 | Add a dated `docs/changelog.md` entry for this sweep | present in diff |
| A7 | Rebuild `marcora-mcp.skill` zip (`cd skill && zip -r -X -q ../marcora-mcp.skill marcora-mcp`) | `unzip -p` the zip, grep standalone Cora = 0; byte count recorded for the later dry-run check |
| A8 | Repo-wide assertion: zero standalone "Cora" outside `.planning/` | `LC_ALL=C git grep -nE '(^\|[^A-Za-z])Cora' -- . ':!.planning'` → empty |
| A9 | Open PR → `main` with `O-3807` in the title | `gh pr view` |

### B. `marcora-backend` — branch off `origin/staging`, draft PR → `staging`

| # | Task | Verification |
|---|---|---|
| B1 | `src/modules/mcp/generated-metadata.ts` L997 `create_plan` — "from interactive Cora sessions" → "from interactive Marcora agent sessions" | per-line grep |
| B2 | L1053 `create_plan.source` — "for Cora interactive callers" → "for Marcora interactive callers" | per-line grep |
| B3 | L1303 `create_workflow` — "inherit Cora's full tool set" → "inherit Marcora's full tool set" | per-line grep |
| B4 | L2075 `set_active_team` — "any running Cora sessions" → "any running Marcora agent sessions" | per-line grep |
| B5 | L4183 `create_webhook_deep_link` — "I want Cora to ping my n8n workflow" → "I want Marcora to ping…" (keep "she") | per-line grep |
| B6 | L6691 `update_plan` — "Accept a Cora-suggested plan" → "Accept a Marcora-suggested plan" | per-line grep |
| B7 | `src/modules/mcp/routes.ts:116` comment — "stale in-flight Cora session" → "Marcora agent session" | per-line grep |
| B8 | `src/modules/mcp/services.ts:291` comment — "protocol error\" in Cora" → "in Marcora" | per-line grep |
| B9 | Module-wide assertion: zero standalone "Cora" in `src/modules/mcp/`; identifier occurrences (`cora_*`, `Cora*` symbols) unchanged in count | `LC_ALL=C git grep` before/after counts |
| B10 | `npm run typecheck` + `npm test` | command output pasted |
| B11 | Draft PR → `staging`, `O-3807` in the title, CI green | `gh pr checks` |
| B12 | Live verification through the PR env: mint a per-PR token, JSON-RPC `tools/list` against `mcp.marcora.ai/staging/pr/<n>`, assert the six edited descriptions carry "Marcora" and standalone "Cora" is ×0 across the whole `tools/list` payload | raw response pasted |

### C. Strapi

| # | Task | Verification |
|---|---|---|
| C1 | `set_active_team` (`documentId w4g6o64qkdtnu8xquyhu6sbo`) `instructions` — "running Cora sessions" → "running Marcora agent sessions". Delegate the write to Content Publisher; timing per **F1** | after publish: plain canonical `https://marcora.ai/docs/tools/set-active-team` with a semantic canary present AND standalone "Cora" ×0; `last-modified` advanced past publish time |
| C2 | Re-assert the rest of Strapi is clean (58 mcp-tools + 8 doc-pages, published **and** draft) | already run — 1 hit, this one |

### D. Report (no edits — these are other lanes')

| # | Finding | Owner |
|---|---|---|
| D1 | `src/modules/cora-agent/routes.ts` **live user-facing realtime strings**: `Cora is thinking…`, `Cora finished` (×2 paths), `Cora hit the tool-call limit`, `Cora ran out of time`, `Cora hit an error`; title-gen system prompt "this Cora chat session"; OpenRouter attribution `'Marcora Cora Title'` | Backend / App Developer via DoE |
| D2 | `src/lib/billing.ts:91` — 402 body: "…purchase more to run Cora." Shown on credit exhaustion | Backend via DoE |
| D3 | `src/lib/observability/openrouter-metadata.ts:31` — internal comment only, low priority | Backend via DoE |
| D4 | Strapi article `marketcore-is-becoming-marcora-heres-why`: "Cora now lives where you already work." is stale. **The two etymology mentions must stay.** | Content Publisher / DoM |
| D5 | Fleet `marcora-mcp` SKILL.md drift: 12 workspaces on **v0.4.1**, 2 on **v0.7.0** (ops-patched, clean), 2 on **v0.7.1** (`director-of-marketing`, `qa-engineer` — still carry "Cora sessions"). After A1/A2 land, all 16 should be re-synced from source | ops (O-3782 lane) |
| D6 | No shipped tool identifier contains "cora" — no alias-and-migration plan is owed | — |

---

## Results (2026-07-25)

**A — `ccromp/marcora-mcp` → PR [#26](https://github.com/ccromp/marcora-mcp/pull/26)** (branch `fix/O-3807-cora-to-marcora`, commit `2073e01`).
A1–A9 all done. `SKILL.md` v0.7.1 → **0.7.2**; zip rebuilt 27410 → **27415 bytes**.
A8 assertion: zero standalone "Cora" across every tracked file outside `.planning/`,
and zero inside every member of the rebuilt zip — the sole survivor is the changelog
heading that names the rename itself.

**B — `marcora-backend` → draft PR [#326](https://github.com/ccromp/marcora-backend/pull/326)** (branch `fix/O-3807-mcp-metadata-cora-to-marcora`, commit `3bce249`).
B1–B12 all done. **Typecheck clean. 1458 tests pass, 0 fail** (111 files, 26 skipped).
**CI green** (4m43s), Railway api + worker both deployed.

B9 identifier parity (before → after, all unchanged): `cora_requested` 9→9,
`cora_proactive` 9→9, `cora_session_id` 2→2, `cora_message_snippet` 2→2,
`coraProgressQueue` 2→2, `sendCoraProgressForMcp` 4→4, `cora_agent` 2→2,
`CoraProgress*` 6→6.

B12 live `tools/list` through PR env 326 (`/health` → `{"version":"3bce249"}`),
**all three servers**:

| server | tools | `Marcora` (positive control) | standalone `Cora` |
|---|---|---|---|
| brand `EbZaDl-X` | 59 | 93 | **0** |
| utility `nqeZnt9_` | 12 | 3 | **0** |
| admin `p3YtBWFc` | 18 | 8 | **0** |

All six edited strings confirmed present in the served payloads; the four `cora_*`
enums/keys confirmed still served. The `Marcora` column is a deliberate positive
control — a zero-hit assertion against an empty payload passes vacuously, so the
zero only counts alongside proof the extractor saw real content.

**Correction to B5:** the tool carrying the webhook example is
`prepare_webhook_registration`, on the **utility** server — not
`create_webhook_deep_link` on brand, as first written. Caught because the brand
`tools/list` had no such tool; PR body corrected.

**C — Strapi.** C2 done (58 mcp-tools + 8 doc-pages, published *and* draft →
exactly one hit). C1 **held** per the rule above.

---

## Method note — the audit pattern that silently lies

**Do not use `grep -E '(^|[^A-Za-z])Cora'` on macOS.** BSD `grep` mishandles a
`^` anchor inside an ERE alternation group and returns **zero matches** on a file
that plainly contains the string — no error, no warning. An early pass in this
task reported "0 Cora" across the whole agent fleet on exactly this pattern, and
the finding was wrong. `LC_ALL=C` does not help; the locale was never the issue.

Reproduce:

```
$ echo "hello Cora there" > /tmp/t
$ grep -cE '(^|[^A-Za-z])Cora' /tmp/t   # → 0   ← WRONG, silently
$ grep -cE '[^A-Za-z]Cora'      /tmp/t   # → 1
$ perl -ne 'print if /(?<![A-Za-z])Cora(?![a-z])/' /tmp/t   # → matches
```

**Use `perl -ne 'print if /(?<![A-Za-z])Cora(?![a-z])/'`** (or Python `re`, or
`git grep`, whose own engine handles the alternation correctly) for every
word-boundary assertion in this task. Every count recorded in this spec was taken
with one of those three. A rename audit is exactly the shape of task where a
false "0 remaining" is indistinguishable from success — so the tool has to be
proven on a positive control before its zero is believed.
