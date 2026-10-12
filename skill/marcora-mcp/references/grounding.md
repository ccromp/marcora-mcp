# Ground a document against the library

Read this before calling `check_content_grounding` or `apply_grounding_fix`: checking whether a document is accurate or consistent with what the team has already said, or applying health-audit fixes.

---

### Workflow 6 — Ground a document against the library

**Goal.** Check whether a document's factual claims hold up against the team's own context library, and fix the ones that don't.

**Preconditions.** Command plan with credits. A document to check — either already in Marcora, or markdown you're holding.

**When to reach for it.** After drafting anything factual, or when the user asks "is this accurate", "does this contradict anything we've said", "check this against our context". It is the natural second beat after Workflow 1.

**Steps.**
1. `marcora:check_content_grounding` — `content_id` alone to scan an existing document, `content` alone to store-and-scan new markdown.
2. If it returns `status: "running"`, poll `marcora:get_grounding_result({scan_id})` every 15–30s. **Poll with `scan_id`.** Polling with `content_id` returns the last *completed* scan, which during your run is the previous one — you'd report stale findings as fresh. Never re-call `check_content_grounding` to check progress.
3. **Check coverage before calling anything unsupported.** If `coverage_complete` is `false`, or `excluded_items` is present, the check did not read every context item, so a gap may still have support. Say so: describe those gaps as "not yet confirmed", not "unsupported". `coverage_reason: "library_catch_up"` means some context items have not been prepared yet; re-run the check to include more of them. `library_extraction_failed` means some could not be prepared. Then review `findings[]` with the user. Each carries the full `suggested_fix` and the `context_item_id` it would write to. Hand over `link_url`.
4. `marcora:apply_grounding_fix({finding_ids: [...]})` for what they approve. Use `context_item_overrides` to redirect a fix.
5. Poll `marcora:get_generation_status({generation_id})` with the UUID `generation_id` from `jobs[]`. Findings whose fixes land in the same document (the same context item, or the same content document when `context_item_id` is null) are applied together in one run and share one `generation_id`: poll each distinct `generation_id` once, and its `document_updated` covers every finding in that run. Brand Foundation findings are not grouped. **`document_updated`** is the honest outcome: `false` means the recommendation was already covered and nothing was written. Report that distinction.

**⚠️ The one way to lose data here.** `content` + `content_id` replaces the document's **entire body**, exactly like `update_content`. To ground part of an existing document, pass `content_id` **alone**. Never pass a paragraph alongside a `content_id` — the rest of the document is gone.

`apply_grounding_fix` also applies Context Intelligence health-audit recommendations from `list_ci_findings`. Full recipe: Recipe I below.

---

## Recipe I — Ground a document against the context library

Grounding checks a document's factual claims against the team's own context library and sorts each into **supported**, **conflict**, or **gap**. Use it after drafting, or whenever the user asks whether something is accurate / on-message / consistent with what the company has already said.

**The loop: draft → ground → review → apply → re-ground.**

1. **Scan.** `marcora:check_content_grounding(...)` in one of three modes:
   - `content_id` alone — scan a document that already exists. **This is the safe default.**
   - `content` alone — hand over markdown; Marcora stores it as a new document and scans it.
   - `content_id` + `content` — **replaces that document's entire body**, then re-scans. See the warning below.
2. **Poll if needed.** It waits ~20 seconds. If you get `status: "running"`, poll `marcora:get_grounding_result({scan_id})` every 15–30 seconds — a fresh scan usually takes 120–150 seconds. **Poll with the `scan_id`, not the `content_id`.** Never call `check_content_grounding` again to check progress; that starts a second scan.
3. **Check coverage first.** Before you tell the user a claim is unsupported, read `coverage_complete`. `false` means some context items were not part of this check, so a gap may still have support in one of them. `coverage_reason` says why: `library_catch_up` (some context items have not been prepared yet; re-run the check to include more of them) or `library_extraction_failed` (some could not be prepared). `excluded_items`, when present, lists context items skipped because they were being edited during the check (`reason: "sync_lock"`); it can appear even when `coverage_complete` is `true`. If either signal is there, describe gaps as "not yet confirmed", not "unsupported".
4. **Review with the user.** Walk them through `findings[]`. Each carries the **full** `suggested_fix` and the `context_item_id` applying would write to. Hand them the `link_url` so they can see it in Marcora.
5. **Apply what they approve.** `marcora:apply_grounding_fix({finding_ids: [...]})`. You never write the fix yourself — you reference the recommendation by id. Redirect a specific fix with `context_item_overrides`.
6. **Report honestly.** Applying is async: poll `marcora:get_generation_status({generation_id})` using the UUID `generation_id` from `jobs[]`. Findings whose fixes land in the same document (the same context item, or the same content document when `context_item_id` is null) are applied together in one run and share one `generation_id`, so poll each distinct `generation_id` once; its `document_updated` covers every finding in that run. Brand Foundation findings are not grouped. A finding that comes back in `errors[]` with "Marcora is already updating this document." hit a document another run still holds: wait for that run, then retry just those findings. The `document_updated` field is the honest outcome — `true` means the document changed, `false` means the recommendation was already covered and nothing was written. Say which; don't imply every applied fix changed something.
7. **Re-ground** if they revised the document. Re-scanning an unchanged document is fast, because unchanged claims are reused.

`apply_grounding_fix` also applies **Context Intelligence health-audit** recommendations from `list_ci_findings` — same tool, same shape.

> **⚠️ Never pass a fragment with a `content_id`.** `content` + `content_id` replaces the document's **entire body**, exactly like `update_content`. If the user asks you to ground one paragraph of an existing document, pass `content_id` **alone** — passing just that paragraph would destroy the rest of the document.

---

## E12 — `check_content_grounding` with `content` + `content_id` overwrites the whole document

**Symptom.** You ground "just this paragraph" of an existing document, and the rest of the document is gone.

**Cause.** `content` combined with `content_id` is a **full-body replacement**, identical to `update_content`. It is not a partial or fragment check. Whatever you pass in `content` becomes the entire document.

**What to do.** To check part of an existing document, pass **`content_id` alone** — the scan reads the document as it currently stands. Only pass `content` alongside `content_id` when you genuinely intend to replace the document, and then pass the **full revised document**, never an excerpt.

---

## E13 — Polling grounding with `content_id` returns the previous scan

**Symptom.** `check_content_grounding` returned `running`; you poll with the `content_id` and immediately get `status: "complete"` — but the findings are from an earlier scan.

**Cause.** `get_grounding_result` with a `content_id` and no `scan_id` returns the latest **completed** grounding, deliberately skipping a scan that is still in flight. During your scan, the latest completed one is the *previous* result.

**What to do.** Poll with the **`scan_id`** that `check_content_grounding` returned. That reads the exact run you started, whatever its status. Reserve the `content_id` form for "what is this document's grounding state right now", when nothing is running.

---

## E16 — Calling a grounding gap "unsupported" when the check was incomplete

**Symptom.** You tell the user a claim has no support in their reference library, and it turns out a context item covers it.

**Cause.** The check did not read every context item. `coverage_complete` was `false` (some context items had not been prepared yet, `coverage_reason: "library_catch_up"`, or could not be prepared, `library_extraction_failed`), or `excluded_items` listed items skipped because they were being edited during the check. A gap only means "nothing in what was checked backs this".

**What to do.** Read `coverage_complete` and `excluded_items` before reporting gaps. If coverage is incomplete, say the gaps are not yet confirmed. For `library_catch_up`, re-run the check to include more context items. Treat gaps as unsupported only when `coverage_complete` is `true` and there are no `excluded_items`.
