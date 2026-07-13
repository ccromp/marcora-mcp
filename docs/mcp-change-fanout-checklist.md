# MCP tool-change fan-out checklist (CANONICAL)

**Any change to an MCP tool definition must run this checklist — no matter which lane made the
change** (MCP Engineer, App Developer, or a backend lane). This is the single citable source of
truth for the process. Briefs that touch `marcora-backend/src/modules/mcp/` must name this doc and
notify the **MCP Server Engineer**.

A "tool definition change" = any edit to a tool's **name, description, input schema, output schema,
or annotations**, or adding/removing a tool. (Pure handler-logic refactors that don't change the
served surface are exempt.)

Owner of this process: **MCP Server Engineer**. If another lane made the change, that lane must
notify the MCP Server Engineer, who runs (or delegates) the fan-out.

---

## 0. Timing rule — docs land on PROD, not on staging merge
Documentation updates go live **when the tool change is LIVE ON `api.marcora.ai`**, not at staging
merge. For a staged-but-unpromoted change: **prepare** the doc updates on a held branch, open them
as draft/hold, and **report the held set to the Director of Engineering** (promotion-ledger
obligation). Release on the DoE's "promotion live — go" signal. Fingerprint prod with
`GET api.marcora.ai/health` (commit) + a `tools/list` through the prod lane.

## 1. Backend metadata (source of truth)
- [ ] Edit `marcora-backend/src/modules/mcp/generated-metadata.ts` by hand. **Do not** re-run
      `scripts/extract-mcp-metadata.mjs` — metadata is hand-authored.
- [ ] Author **native** fields, never marker text:
      - `annotations`: `{ title, readOnlyHint, destructiveHint, idempotentHint, openWorldHint }`
      - `outputSchema`: a plain JSON Schema object for the return shape.
      - **Never** write `---OUTPUT_SCHEMA---` / `---ANNOTATIONS---` marker blocks in a description.
        (The proxy still tolerates them as a legacy safety net, but native fields are authoritative;
        markers are deprecated and being removed.)
- [ ] Staging-first: branch off `origin/staging`, PR → `staging`, draft + wait for CI. No migrations
      in this lane (escalate schema needs to the DoE).
- [ ] Verify the tool end-to-end (curl through a PR env or `mcp.marcora.ai/staging`) before "ready".

## 1a. Annotation + outputSchema completeness gate (HARD — every served tool)
**No served tool ships without all five annotation hints AND a native `outputSchema`.** This applies
to EVERY server the metadata defines — **brand, admin, AND utility** — not just the customer-facing
brand server. (2026-07-13 / O-2451 audit found 28 admin+utility tools shipped with NO `annotations`
object and 3 with no `outputSchema`; `update_playbook` shipped with two wrong hints. The Anthropic
directory reviewer can pull `tools/list` on any exposed server, so all of them must be spec-perfect.)

- [ ] **All 5 hints present and SEMANTICALLY chosen** (never defaulted, never omitted): `title`,
      `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`. Pick each from what the
      **handler actually does** — read the handler in `registry.ts` → feature route; do NOT trust
      sibling copy-paste (that is exactly how `update_playbook` drifted).

      | Handler shape | readOnly | destructive | idempotent | openWorld |
      |---|---|---|---|---|
      | `get_*` / `list_*` — pure read | `true` | `false` | `true` | `false` |
      | `create_*` / add / import / instantiate — writes a new row | `false` | `false` | `false` | `false` |
      | `update_*` / edit-in-place — may overwrite or remove | `false` | **`true`** | **`true`** | `false` |
      | delete / destroy | `false` | `true` | `true` | `false` |
      | web search / browse / fetch-a-URL | `true` | `false` | `true` | **`true`** |
      | send / trigger an external webhook | `false` | `false` | `false` | **`true`** |
      | pure transform that stores a new artifact (e.g. md→docx) | `false` | `false` | `false` | `false` |

      Rules of thumb: `destructiveHint` is only meaningful when `readOnlyHint=false`.
      `idempotentHint=true` **iff** repeating the call with identical args leaves the same end state
      (partial-patch / full-replace updates ARE idempotent; anything that mints a new row/artifact
      each call is NOT). `openWorldHint=true` **iff** the tool reaches an unbounded external world
      (open web, arbitrary email/webhook target) — NOT for internal LLM generation over team context.
- [ ] **Native `outputSchema` present and accurate to the REAL return shape.** If the handler returns
      a **bare array**, `toolResult()` wraps it under `result`, so the schema's top level is
      `{ "type": "object", "properties": { "result": { "type": "array", ... } } }` — never a
      top-level array. JSON Schema allows extra properties by default, so a subset of known fields is
      fine, but the required/known fields must match reality.
- [ ] **Completeness scan before "ready"** — parse `generated-metadata.ts` and assert ZERO *served*
      tools lack `annotations`, `annotations.title`, or `outputSchema`. (A *served* tool = one listed
      in a `servers[].tools` array; hidden/internal tool defs like `signal_response_ready` that are in
      no server list are exempt.) One-liner:
      ```
      node -e 'const m=require("./generated-metadata.cjs");const s={};for(const x of m.servers)for(const t of x.tools)s[t]=1;const bad=m.tools.filter(t=>s[t.name]&&(!t.annotations||!t.annotations.title||!t.outputSchema)).map(t=>t.name);console.log(bad.length?"FAIL: "+bad.join(","):"OK: all served tools complete")'
      ```
      (or inline-parse the `MCP_METADATA` export — the point is a mechanical zero-gap assertion, not eyeballing.)

## 2. Strapi marketing-site docs (customer-facing tools only) — POST-PROMOTION
- [ ] Delegate to **Content Publisher**. Conventions: a "When to use" trigger sentence; set the
      `doc_page` parent relation to `mcp-tools`; put **workflow** tools under the **Workflows**
      category; pick the right tool category otherwise.
- [ ] Internal/admin/utility tools do not need Strapi docs.

## 3. GitHub repo docs + skills bundle (`ccromp/marcora-mcp`) — POST-PROMOTION
- [ ] Update `docs/tools.md` (the authoritative tool catalog) **and** the `README.md` "Available
      Tools" table.
- [ ] Add a `docs/changelog.md` entry (dated).
- [ ] Update the companion skill if workflows/usage changed: `skill/marcora-mcp/SKILL.md`
      (+ `references/workflows.md`, `references/pitfalls.md`), bump `SKILL.md` `metadata.version`.
- [ ] Rebuild the `marcora-mcp.skill` zip and publish a **GitHub release** (tag `skill-vX.Y.Z`) —
      this is what Cora consumes (see step 4).
- [ ] Bump versions as needed: `server.json`, `plugin/.claude-plugin/plugin.json`,
      `.claude-plugin/marketplace.json`.

## 4. Cora (Marcora Agent) skills — CONTENT vs SET change
Cora's skills are pinned at `version: "latest"`, so a **content-only** skill release is picked up
automatically on the agent's next session — no agent change needed. Only a **skill-SET** change
(adding, removing, or swapping a skill id on the agent) requires touching the managed agent.
- [ ] **Content-only release** (a new `.skill` for an already-pinned skill id — e.g. edited workflow
      text, a new tool row in the decision table, a usage-guidance addition): publish the
      `marcora-mcp.skill` GitHub release (step 3) and you're done. `version: "latest"` picks it up on
      the next session — **no** App-Developer action required.
- [ ] **Skill-SET change** (add/remove/swap a skill id on the agent): after the GitHub release,
      **notify the App Developer** to land the SET change on Cora via the in-place update
      (`POST /cora-agent/recreate-agent` / `/recreate-worker-agent`, default path — same agent id,
      versioned, no env swap; O-2387). A CONTENT-only release needs **no** agent change (see above).
      Do the **dev** agent first, then **live with approval**. Live agent IDs are env-resolved
      (`CORA_AGENT_ID_LIVE` / `CORA_WORKER_ID_LIVE`) — never hardcode an agent id in docs.
- [ ] Pure tool-metadata changes (description/schema/annotations, no skill-content change) need only
      steps 1–3 — no skill release and no Cora action.

## 5. Notify + record
- [ ] If the change was made by a lane **other than** the MCP Server Engineer, that lane notifies
      the MCP Server Engineer, who owns the fan-out.
- [ ] Record held (staged-but-unpromoted) doc obligations with the DoE for the promotion ledger.

---

### Quick reference — the pipeline
```
edit generated-metadata.ts (native fields, no markers)
   → staging PR (draft, CI) → prod promotion (DoE)
      → [on prod-live signal] Strapi (Content Publisher) + GitHub docs/skill release
         → [if skill CONTENT changed] publish .skill GitHub release (version:"latest" auto-picks up)
            → [if skill SET changed] notify App Developer → in-place Cora agent update (dev → live w/ approval)
```
