# Ground a document against the library

Read this before calling `check_content_grounding` or `apply_finding_fix`: checking whether a document is accurate or consistent with what the team has already said, or applying health-audit fixes (`learn_marcora_tools({ page: "check-a-documents-grounding" })` / `learn_marcora_tools({ page: "apply-grounding-fixes" })`).

---

### Workflow 6 — Ground a document against the library

**Goal.** Check whether a document's factual claims hold up against the team's own context library in two passes, and fix the ones that don't.

**Preconditions.** Available Studio Credits (Marcora estimates the cost first and won't start a scan the team's balance can't cover; teams still on a legacy plan keep that plan's existing requirements). A Creator or Admin role on the team to run a scan (a collaborator gets a 403 from both `check_content_grounding` and `get_grounding_result`). A document to check — either already in Marcora, or markdown you're holding.

**When to reach for it.** After drafting anything factual, or when the user asks "is this accurate", "does this contradict anything we've said", "check this against our context". It is the natural second beat after Workflow 1.

**How two-pass grounding works.**
- **Pass 1 (built-from sources):** checks the root Reference Library, Brand Foundation, the project brief and project items, and any collections/items used in drafting, plus recorded drafting research (`web_research`, `connected_app`). **Conflicts come ONLY from authoritative built-from sources**; recorded research can support a claim, never conflict.
- **Pass 2 (other collections):** checks other visible collections not used to build the document. They can **support** a claim or add a **`note`** (`bucket: "note"`, or `notes[]` on a supported claim), never a conflict. Notes have no finding or fix action; only completely searched, nowhere-supported true gaps have `add_to_library_eligible: true`. Grounding itself never browses the web.
- **Claim subject and battle-card rule:** each claim and finding reports `claim_subject` (`{ kind: "team" | "company" | "general" | "unknown", company_name, confidence }`). A claim about the user's own company (`team`) is checked only against material about their company; a claim about another named company (`company`) is checked against material about that company, which can support or contradict it. On conflict claims and conflict findings, `conflict_scope` is `"team_facts"` (disagrees with your own facts) or `"company_material"` (disagrees with your material about that company, not your own facts). A company conflict's fix revises the document (`context_item_id: null`), never your facts, and a company gap offers no add-to-library (`add_to_library_eligible: false`; the backend refuses it).

**Steps.**
1. `marcora:check_content_grounding` — `content_id` alone to scan an existing document, `content` alone to store-and-scan new markdown.
2. If it returns `status: "running"`, poll `marcora:get_grounding_result({ team_id, scan_id })` every 15–30s. **Poll with `scan_id`.** Polling with `content_id` returns the last *completed* scan, which during your run is the previous one — you'd report stale findings as fresh. Never re-call `check_content_grounding` to check progress.
3. **Check coverage before calling anything unsupported.** If `coverage_complete` is `false`, or `excluded_items` is present, the check did not read every source, so a gap may still have support. Say so: describe those gaps as "not yet confirmed", not "unsupported". `coverage_reason: "library_catch_up"` means some context items have not been prepared yet; re-run the check to include more of them. `library_extraction_failed` means some could not be prepared; `library_token_budget` means the library exceeds one scan's budget; `source_access_changed` means access to a cited source changed after the scan; `source_content_changed` means the document or a source this check read was edited after it completed (re-check to refresh); `reader_scope_narrower` means you can read fewer sources than the person who ran the check, so results may be incomplete for you (re-check to refresh); `support_lookup_incomplete` means the pass-2 lookup across other collections did not finish. **Also check `conflict_check`:** if present (`no_company_overview`, `no_confirmed_sources`, or `items_unconfirmed`), tell the user that `summary.conflicts` of `0` does **not** mean the content agrees with their sources and relay `conflict_check.message`. Then review `findings[]` and any `note` claims (`bucket: "note"` or `notes[]`) with the user, noting each claim/finding's `claim_subject` and (on conflicts) `conflict_scope` (`team_facts` vs. `company_material`). Each finding carries the full `suggested_fix` and the `context_item_id` it would write to. Hand over `link_url`.
4. `marcora:apply_finding_fix({ team_id, finding_ids: [...] })` for what they approve (only built-from pass-1 conflicts and `add_to_library_eligible: true` gaps have fixes; a `company_material` conflict's fix revises the document, never your facts, and a company gap offers no add-to-library; pass-2 `note` outcomes have none). Use `context_item_overrides` to redirect a fix.
5. Poll `marcora:get_generation_status({ team_id, generation_id })` with the UUID `generation_id` from `jobs[]`. Findings whose fixes land in the same document (the same context item, or the same content document when `context_item_id` is null) are applied together in one run and share one `generation_id`: poll each distinct `generation_id` once, and its `document_updated` covers every finding in that run. Brand Foundation findings are not grouped. **`document_updated`** is the honest outcome: `false` means the recommendation was already covered and nothing was written. Report that distinction.

**⚠️ The one way to lose data here.** `content` + `content_id` replaces the document's **entire body**, exactly like `update_content`. To ground part of an existing document, pass `content_id` **alone**. Never pass a paragraph alongside a `content_id` — the rest of the document is gone.

**Claims that rest only on calls.** A supported claim may carry `support_only_calls` (one entry per call, with its date, kind and company). It appears only when every supporting source is a call. Tell the user such a claim rests only on calls, which are one conversation's word rather than a written source.

**Private sources stay in Marcora.** Documents built from `Only me` sources cannot be grounded over MCP (`check_content_grounding` refuses with a link for the owner to run an isolated private check in Marcora; `get_grounding_result` reads shared scans only). On shared re-checks, dismissed findings stay dismissed as long as the claim and its warning evidence are unchanged. Calling `get_grounding_result({ team_id, content_id })` reads the latest completed scan with live finding statuses and counts (so dismissed or resolved findings appear as `dismissed` / `resolved` immediately), whereas `get_grounding_result({ team_id, scan_id })` reads that scan's frozen snapshot (captured per-scan claims and completion-time finding statuses; returns `"Grounding result not found."` if a cited source was later erased).

**Context Intelligence findings (`list_ci_findings`, `answer_finding_question`, `apply_finding_fix`, `undo_finding_fix`):**
- Call `list_ci_findings({ team_id })` (omit `bucket`/`status` for the actionable queue, or pass `bucket: "questions" | "queued" | "applied" | "cleared"`).
- Answer open questions (`decision: "ask"`) with `answer_finding_question({ team_id, finding_id, choice })` (`apply`, `edit` + `text`, `leave_out`, `library_right`, `this_right`, `both_right`).
- Queued library `auto_fix` findings apply synchronously in `apply_finding_fix` (returned in `applied[]` with `can_undo`), or can be declined/re-queued with `update_ci_finding_status({ status: "decline" | "undecline" })`.
- Revert applied fixes when `can_undo` is true with `undo_finding_fix({ team_id, finding_id })` (refuses with `changed_since_apply` if edited afterward or `never_applied` if resolved outside Marcora).
- Unsupported `web_freshness` / `impact_scan` findings without a queued fix return in `errors[]` pointing to `update_ci_finding_status`. Full recipe: `references/grounding-recipe.md`.

---

## E12 — `check_content_grounding` with `content` + `content_id` overwrites the whole document

**Symptom.** You ground "just this paragraph" of an existing document, and the rest of the document is gone.

**Cause.** `content` combined with `content_id` is a **full-body replacement**, identical to `update_content`. It is not a partial or fragment check. Whatever you pass in `content` becomes the entire document.

**What to do.** To check part of an existing document, pass **`content_id` alone** — the scan reads the document as it currently stands. Only pass `content` alongside `content_id` when you genuinely intend to replace the document, and then pass the **full revised document**, never an excerpt.

---

## E13 — Polling grounding with `content_id` returns the previous scan

**Symptom.** `check_content_grounding` returned `running`; you poll with the `content_id` and immediately get `status: "complete"` — but the findings are from an earlier scan.

**Cause.** `get_grounding_result` with a `content_id` and no `scan_id` returns the latest **completed** grounding, deliberately skipping a scan that is still in flight. During your scan, the latest completed one is the *previous* result.

**What to do.** Poll with the **`scan_id`** that `check_content_grounding` returned. That reads the exact run you started, whatever its status (and for completed scans, preserves that scan's captured claims and completion-time finding statuses). Reserve the `content_id` form for "what is this document's grounding state right now", when nothing is running — it reads the latest completed scan alongside live finding statuses and counts, so dismissed or resolved findings read as `dismissed` / `resolved` immediately.

---

## E16 — Calling a grounding gap "unsupported" when the check was incomplete

**Symptom.** You tell the user a claim has no support in their reference library, and it turns out a context item covers it.

**Cause.** The check did not read every context item. `coverage_complete` was `false` (some context items had not been prepared yet, `coverage_reason: "library_catch_up"`, or could not be prepared, `library_extraction_failed`; the reference library was larger than one check can read, `library_token_budget`; access to a source changed after the scan, `source_access_changed`; the document or a read source changed after the scan, `source_content_changed`; you can read fewer sources than the person who ran the check, `reader_scope_narrower`; or pass-2 support lookup across other collections did not complete, `support_lookup_incomplete`), or `excluded_items` listed items skipped because they were being edited (`sync_lock`) or over the read budget (`library_token_budget`) during the check. A gap only means "nothing in what was checked backs this".

**What to do.** Read `coverage_complete` and `excluded_items` before reporting gaps. If coverage is incomplete, say the gaps are not yet confirmed. For `library_catch_up`, re-run the check to include more context items; for `source_content_changed` or `reader_scope_narrower`, re-check to refresh. Treat gaps as unsupported only when `coverage_complete` is `true` and there are no `excluded_items`.
