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

### 2c. On a SKILL release, update the `mcp-overview` page's version reference
The `mcp-overview` doc-page (documentId `iwzhpqpsxrf6tlzir71k5txp`) names the companion skill's
version inline — *"**Marcora AI Workflows** (`marcora-mcp`, vX.Y.Z)"*. **Nothing updates it
automatically**, and no other step in this checklist touches it, so it silently rots one release at
a time. Found stale at **v0.5.0 while v0.7.2 was live** — four releases behind (O-3807, 2026-07-26).

- [ ] Whenever step 3 bumps `SKILL.md` `metadata.version`, update that string in the same pass.
- [ ] Verify: `GET /api/doc-pages?filters[slug][$eq]=mcp-overview` and assert the version in
      `content` equals the `metadata.version` you just shipped. Assert on the number, not on
      "I edited the page".

### 2a. A tool doc page has TWO render sources — update BOTH, in ONE pass
`marcora.ai/docs/tools/<slug>` renders two independent sections from two different fields:
- **"Parameters"** table ← the `parameters` repeatable component (markdown renders literally).
- **"Input Schema"** raw-JSON block ← the `inputSchema` field, dumped verbatim.

- [ ] Update the field in **both** places, or the page self-contradicts (this has failed vetting).
- [ ] **`inputSchema` must mirror the LIVE PROD schema exactly** (DoE ruling, O-2549) — it is a
      mirror, never aspirational or hand-tuned. The Parameters prose must AGREE with it. When
      they'd conflict, the schema block is the one it's wrong to edit: fix the real schema, or
      fix the prose — never fork them. Runtime-only contracts (e.g. an `omitted → Missing param`
      error that the schema doesn't encode) belong in the PROSE.
- [ ] Publish **all** fields of a page in ONE pass. Two publishes minutes apart can pin a render
      with new `parameters` + old `inputSchema` into cache for an hour.

### 2b. Verifying a published page — use the PLAIN canonical URL
`marcora.ai` serves these pages with `cache-control: s-maxage=3600, stale-while-revalidate`
and **`netlify-vary: query`**. Because the cache key varies by query string, a `?cb=<rand>`
probe is a guaranteed MISS → reads the **origin**, NOT what a customer sees.

- [ ] Assert on the **plain canonical URL** (no query). That is the customer's view, and the
      only one that closes a fan-out.
- [ ] Use both deliberately as a **diagnostic**: plain stale + `?cb=` clean = **CDN only**
      (content is fine — wait it out); both stale = **real content gap** (fix the content).
- [ ] Assert the new strings are **present** AND the old strings appear **zero** times. Presence
      checks alone miss a stale string coexisting on the same page.
- [ ] **Run a positive control before believing any absence.** "0 occurrences of the stale
      string" is *vacuously true against an empty string* — and an empty body fails silently, so
      the check reports a confident green having matched nothing. Near-miss O-2590, 2026-07-14:
      a `subprocess.run(..., text=True)` normalized `\r\n`→`\n`, so a `partition("\r\n\r\n")`
      header/body split returned an **empty body** and every stale-absent assertion passed
      against `""`. Same class as the `?cb=` trap, one layer down: **an assertion that cannot
      fail is not evidence.**
- [ ] Make the control **semantic, not size-based**: assert a canary that MUST be present —
      `Input Schema`, `Parameters`, the tool name. That proves the extractor saw *this* page.
      ⚠️ Do NOT gate on a body-length threshold. O-2549 tried "abort if <10k chars" and it
      false-negatived on its **first real run**: `update-context`'s visible text is ~9.7k, so a
      perfectly clean page failed the guard. A magic number is a proxy for "did I fetch
      anything", and it is easy to miscalibrate in the direction that blocks good work; the
      canary answers the question directly.
- [ ] Strip `<script>`/`<style>` before matching — the page embeds a payload for ALL ~56 tools,
      so a naive grep hits another tool's wording.
- [ ] **`last-modified` is the only trustworthy freshness signal** — not `age`, not
      `cache-status`. Compare it to your publish time; if it predates the publish, the page is
      stale whatever else the headers say.
- [ ] A Strapi edit does NOT purge the edge cache. `POST api.netlify.com/api/v1/purge` (site
      `marcora-main` = `a97ddd13-f656-41be-b0ec-8965fdb4510c`) returns 202 and resets `age`, but
      its effect is **eventually-consistent, not immediate** — do not treat 202 as done.
      Observed O-2549/O-2590 (2026-07-14): four purges produced **no immediate eviction**
      (`last-modified` stayed pinned, stale bytes kept serving), yet both pages then re-rendered
      **~34 min before** their nominal `s-maxage=3600` expiry — and one page's re-render
      *predates* the purge credited with fixing it. The mechanism is **unexplained**; don't
      invent one. What's ruled out: "purge never works", "purge works", and "it can only
      self-heal at 3600s" are all unsafe beliefs.
- [ ] **Never gate on the purge call — gate on the page.** The only trustworthy close is:
      `last-modified` has advanced past your publish time AND stale strings are ×0 on the PLAIN
      canonical URL. `age: 0` + `202` is the classic false green (a purge resets `age` while
      still serving the old render).
- [ ] Purging is safe and worth trying **once the origin is correct** — just re-verify by the
      rule above rather than believing it. Purging BEFORE the content is right only re-caches
      the wrong copy. A site redeploy (app-developer/DoE lane) is the only hard lever; rarely
      worth it for <1h.

## 3. GitHub repo docs + skills bundle (`ccromp/marcora-mcp`) — POST-PROMOTION
- [ ] Update `docs/tools.md` (the authoritative tool catalog) **and** the `README.md` "Available
      Tools" table.
- [ ] Add a `docs/changelog.md` entry (dated).
- [ ] Update the companion skill if workflows/usage changed: `skill/marcora-mcp/SKILL.md`
      (+ `references/workflows.md`, `references/pitfalls.md`), bump `SKILL.md` `metadata.version`.
- [ ] Rebuild the `marcora-mcp.skill` zip (`cd skill && zip -r -X -q ../marcora-mcp.skill marcora-mcp`)
      and publish a **GitHub release**, tagged **`marcora-vX.Y.Z`** (the repo's actual convention —
      NOT `skill-vX.Y.Z`), with the zip attached as an asset named exactly `marcora-mcp.skill`.
      **The GitHub release alone does NOT reach the Marcora agent — you must also do the Skills-API upload in
      step 4.**
- [ ] Bump versions as needed: `server.json`, `plugin/.claude-plugin/plugin.json`,
      `.claude-plugin/marketplace.json`.
- [ ] **Immediately after cutting the release, assert §2c actually happened** — fetch the
      `mcp-overview` page and check the advertised skill version equals the version you just
      released. §2c says "in the same pass", but a release and a docs edit often land in
      separate sittings and the step then silently doesn't fire — that is exactly how the page
      reached **v0.5.0 while v0.7.2 was live**, and it recurred once more within the hour of
      §2c being written (O-3807, 2026-07-26: released v0.7.3, page still said v0.7.2). Check it
      here, at the release, where the drift is observable — not from memory.

## 4. Marcora agent skills — CONTENT vs SET change
The Marcora agent's skills are pinned at `version: "latest"`, so a **content-only** skill release is picked up
automatically on the agent's next session — no agent change needed. Only a **skill-SET** change
(adding, removing, or swapping a skill id on the agent) requires touching the managed agent.
- [ ] **Content-only release** (a new `.skill` for an already-pinned skill id — e.g. edited workflow
      text, a new tool row in the decision table, a usage-guidance addition):
      **1)** publish the `marcora-mcp.skill` GitHub release (step 3), **then 2) upload it to the
      Anthropic Skills API** (below). `version: "latest"` then resolves it on the Marcora agent's next session —
      **no** App-Developer action and no agent change required.

  🚨 **A GitHub release does NOT update the live skill. The Skills-API upload is a REQUIRED,
  SEPARATE step every single time.** `version: "latest"` resolves the newest version *uploaded to
  the Skills API* — it does not watch GitHub. Skipping this leaves the Marcora agent serving the stale skill
  while every artifact looks shipped. This has already bitten us once: **O-2531 (2026-07-14)** found
  the live Marcora agent still on a stale version a full train after the releases existed.

  **Upload:** `POST https://api.marcora.ai/api:V2eJloU_/cora/agent/admin_upsert_skill_version`
  (auth: any prod user token — mint via `POST /api:rFjIObWc/agent-token-exchange` with the prod
  `XANO_AGENT_SECRET` from Railway `production`; the backend holds the `ANTHROPIC_API_KEY`).
  Body: `{"action":"dry_run"|"upload", "release_url":"<explicit versioned URL>", "verify_agent_id":"<live coordinator>"}`.
  Defaults: `skill_id` = `CORA_MARKETCORE_SKILL_ID`. Resolve `verify_agent_id` from Railway
  `production` `CORA_AGENT_ID_LIVE` — never hardcode an agent id.

  - [ ] **Pass an EXPLICIT versioned `release_url`** — `.../releases/download/<tag>/marcora-mcp.skill`.
        **Never `/releases/latest/download/...`**: GitHub's CDN serves a stale asset to the backend's
        region for a while after a release/clobber, so the upload can silently ship the OLD zip.
  - [ ] `dry_run` first and confirm **`fetch_bytes` == your local zip's byte count** (`wc -c`). A
        mismatch means you fetched a stale asset — stop, don't upload.
  - [ ] Then `action: "upload"`; verify **`versions_after` == before + 1** and that the newest
        version's `created_at` is *now*. Confirm `agent_check.skills[]` pins the custom skill at
        `version: "latest"` (that's what makes it auto-propagate).
  - [ ] **Anthropic frontmatter limits (hard — 400 at upload, not caught in git):** SKILL.md
        `description` ≤ **1024 chars** and **no angle-bracket/XML tags** in it.
- [ ] **Skill-SET change** (add/remove/swap a skill id on the agent): after the GitHub release,
      **notify the App Developer** to land the SET change on the Marcora agent via the in-place update
      (`POST /cora-agent/recreate-agent` / `/recreate-worker-agent`, default path — same agent id,
      versioned, no env swap; O-2387). A CONTENT-only release needs **no** agent change (see above).
      Do the **dev** agent first, then **live with approval**. Live agent IDs are env-resolved
      (`CORA_AGENT_ID_LIVE` / `CORA_WORKER_ID_LIVE`) — never hardcode an agent id in docs.
- [ ] Pure tool-metadata changes (description/schema/annotations, no skill-content change) need only
      steps 1–3 — no skill release and no Marcora-agent action.

## 5. Notify + record
- [ ] If the change was made by a lane **other than** the MCP Server Engineer, that lane notifies
      the MCP Server Engineer, who owns the fan-out.
- [ ] Record held (staged-but-unpromoted) doc obligations with the DoE for the promotion ledger.

### 5a. Completion is asserted from artifacts that MOVE — never from a PR title
A held item's status must be answerable from things that change when the work ships. Two do:
the **Skills-API version `created_at`** and the **GitHub release tag**. A merged PR does not prove
a fan-out completed, and a PR *title* proves nothing at all — titles are immutable in practice,
because nobody retitles a PR after merging it.

- [ ] **Close a held item against the artifacts, in this order:** the release tag exists →
      the Skills-API `created_at` for the newest version post-dates that release (step 4's upload
      actually happened) → the Strapi page's `last-modified` has advanced past your publish
      (§2b) → prod `tools/list` serves the new schema. Each is independently checkable by anyone
      later, with no access to your memory of the evening.
- [ ] **Never record a hold marker ONLY in a PR title.** Put it on the **ledger line** — that is
      the durable record and the thing a later audit reads. A `[HELD until prod]` title is a
      convenience label, not state.

      > **O-2589 / O-3672 (2026-07-14 → 07-24).** The `update_brand_foundation` link_url fan-out
      > ran in full and on time: docs PR merged `20:01Z`, release `marcora-v1.5.3` cut `20:02Z`,
      > Skills-API upload `20:03Z` — 56 seconds after the release. But the only "held" marker was
      > `[HELD until prod]` in the PR title, and nothing cleared it. Ten days later the promotion
      > ledger still read HELD and a verify-and-release task was raised against work that had been
      > live for over a week. Every real artifact said shipped; one stale string outvoted them all.

### 5b. Clearing the marker is the closing step — do it, don't remember it
A fan-out is not finished when the artifacts land. It is finished when nothing left behind still
claims it is pending. An uncleared marker **is** a defect: it costs a future audit cycle.

- [ ] **Retitle the PR** — drop `[HELD until prod]` (or strike it) once released.
- [ ] **Update the ledger line** to released, and stamp it with the Skills-API upload timestamp /
      release tag from 5a, so the next reader sees the evidence and not just a claim.
- [ ] **Tell the DoE the hold is cleared** in the same message that reports the release. The
      promotion ledger is theirs to close; releasing without saying so recreates the O-2589 gap.

---

## 6. Audit discipline — when a grep proves nothing
Several steps above close on an absence ("zero occurrences of the stale string"). An absence is
only evidence if the instrument could have found the thing. **Three separate audits in one day
(2026-07-26) returned a confident all-clear that was false**, each for a different reason:

1. **The tool lied.** `grep -E '(^|[^A-Za-z])Cora'` returns a silent **0** on BSD/macOS grep — it
   mishandles a `^` anchor inside an ERE alternation. No error, no warning. It reported an entire
   16-workspace agent fleet clean of a string that four copies plainly contained.
   ```
   $ echo "hello Cora there" > /tmp/t
   $ grep -cE '(^|[^A-Za-z])Cora' /tmp/t   # → 0   ← WRONG, silently
   $ grep -cE '[^A-Za-z]Cora'      /tmp/t   # → 1
   ```
   `LC_ALL=C` does not help; the locale is not the issue. Use `perl -ne 'print if
   /(?<![A-Za-z])X(?![a-z])/'`, Python `re`, or `git grep` — git's own engine handles it.
2. **The output was truncated.** An audit grep piped through `head -20` looked clean because the
   hits were on line 21+. **Never `head` an audit grep.** Count first, then page.
3. **The claim was paraphrasable.** A false marketing claim was swept for with two independent
   keyword nets, both of which missed the nearest real instance — it was found only by *reading the
   file*. A claim that can be reworded cannot be bounded by a word list.

- [ ] **Pair every zero with a positive control.** Assert that something which MUST be present IS
      present, in the same pass — e.g. "`Marcora` ×93" alongside "standalone `Cora` ×0". A zero next
      to a zero is indistinguishable from having matched nothing at all (empty body, wrong path,
      broken regex). This is the same trap as §2b's `?cb=` and empty-body cases, one layer down.
- [ ] **Prove the pattern on a known-positive input before trusting its zero.** One `echo` into a
      temp file costs nothing and catches failure mode 1 outright.
- [ ] **For semantic claims — positioning, security posture, capability assertions — READ the
      files.** Greps are for tokens. Meaning is not a token, and the surfaces that carry positioning
      claims (`README.md`, `docs/overview.md`, `docs/security.md`, the Strapi `mcp-overview` page)
      are short enough to read in full. Do that instead of widening the regex.

---

### Quick reference — the pipeline
```
edit generated-metadata.ts (native fields, no markers)
   → staging PR (draft, CI) → prod promotion (DoE)
      → [on prod-live signal] Strapi (Content Publisher) + GitHub docs/skill release
         → [if skill CONTENT changed] GitHub release (tag marcora-vX.Y.Z)
              → ⚠️ admin_upsert_skill_version UPLOAD  ← REQUIRED; the release alone does NOT
                                                        reach the agent. version:"latest" tracks
                                                        Skills API, not GitHub. (O-2531)
            → [if skill SET changed] notify App Developer → in-place Marcora agent update (dev → live w/ approval)
   → CLOSE: assert from artifacts (release tag + Skills-API created_at + Strapi last-modified
            + prod tools/list) → CLEAR the hold marker (retitle PR, stamp the ledger line)
            → tell the DoE it's cleared            ← §5a/§5b; skipping this is how a shipped
                                                     fan-out reads as HELD ten days later (O-2589)
```
