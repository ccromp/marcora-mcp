# O-3672 — Fan-out checklist: a completion marker that actually clears

## Goal

Close the process hole that made a finished fan-out read as outstanding for ten days.

O-2589's `update_brand_foundation` link_url fan-out ran **in full** on 2026-07-14 —
docs PR #14 merged 20:01Z, release `marcora-v1.5.3` cut 20:02Z, Skills-API upload
20:03Z. Yet the promotion ledger still listed it as HELD on 2026-07-24, and a
verify-and-release task was raised against it.

Root cause: **the only "held" marker was the text `[HELD until prod]` in a PR
title, and nothing in the checklist clears it.** Nobody retitles a PR after
merging it, so the marker outlived the hold by ten days. The ledger was reading a
stale string while every real artifact said shipped.

Fix: amend step 5 of `docs/mcp-change-fanout-checklist.md` so that (a) completion
is asserted against artifacts that actually move — the Skills-API upload
timestamp and the release tag — and (b) clearing the hold marker is an explicit
closing step, not something left to memory.

Authorized by the Director of Engineering (O-3485 → O-3672, 2026-07-25):
"standardize it… fold into the fan-out checklist's step 5 that the completion
marker is the Skills-API upload timestamp / release tag (the artifacts that
actually move), and that the closing step CLEARS the hold marker."

## Constraints / out of scope

- **Only** `docs/mcp-change-fanout-checklist.md` in `ccromp/marcora-mcp`. No tool
  metadata, no `docs/tools.md`, no skill content, no `marcora-backend` change.
- No skill version bump and no `.skill` rebuild — this is an internal process doc,
  not skill content, so nothing propagates to Cora and no Skills-API upload is owed.
- Not a "held until prod" change itself: it documents process, describes no tool
  behavior, and has no prod dependency. It can land immediately.
- **Do not** start the input-description sweep (Finding 2 of the O-3672 audit:
  22 of 59 served tools have inputs with no description). That is a separate,
  larger piece of work still awaiting the DoE's sequencing call. Out of scope here.
- Keep the existing checklist voice: imperative checkboxes, a named incident as
  the justification for each hard rule, no restructuring of steps 0–4.

## Decisions already made

- **Completion is asserted, not assumed.** The two artifacts that move are the
  Skills-API version `created_at` and the GitHub release tag. A merged PR is not
  evidence of a completed fan-out; a PR title is not evidence of anything.
- **Clearing the marker is a checkbox**, so it can be audited like every other
  step. An uncleared marker is itself the defect.
- **Hold markers do not belong in PR titles alone.** A title is immutable in
  practice. The ledger line is the durable record.
- Scope the guidance to the general case (any held package), not just the
  `link_url` incident, so it applies to the next one.

## Tasks

| # | Task | Verification |
|---|---|---|
| 1 | Branch `docs/o3672-fanout-completion-marker` off `origin/main` | `git log --oneline -1` = `1851dce` ✅ |
| 2 | Commit this spec | file present on branch |
| 3 | Amend step 5 with the completion-marker + marker-clearing rules, citing O-2589/O-3672 | render the new step 5; assert it names the Skills-API timestamp, the release tag, and the clearing step |
| 4 | Add the closing step to the Quick-reference pipeline diagram so the two views agree | diff shows the diagram terminating in the clear-the-marker step |
| 5 | Markdown sanity — no broken checkboxes, consistent 6-space continuation indent | re-read the rendered section end-to-end |
| 6 | Push, open PR → `main` | PR URL returned; `gh pr view` shows base=main |

## Verification

The change is documentation, so verification is by inspection rather than
execution — but the *claim it encodes* was verified first-hand during the O-3672
audit and is cited in the spec above:

- Skills-API `dry_run` against prod showed the upload at `2026-07-14T20:03:40Z`,
  56 seconds after the `marcora-v1.5.3` release at `20:02:44Z` — i.e. the
  artifacts that "actually move" did move, on time, and were the only reliable
  evidence available.
- The v1.7.0 release asset is 26,895 bytes, byte-identical to the repo zip, and
  the live Skills-API `latest` description is a byte-exact match to
  `origin/main`'s `SKILL.md` — so the artifact-based assertion the new step 5
  prescribes is actually checkable in practice, which is the point.

Final gate: the rendered step 5 must let a reader with no context answer "is this
fan-out done?" from artifacts alone, without reading a PR title.
