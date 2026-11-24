# Share and export content

Read this before creating an external share link or exporting a document to Word.

---

## Recipe D — Share content externally

**Goal.** Generate a public share URL for a piece of content.

**Steps.**
1. `marcora:create_external_share(team_id, content_id, expires_at?)` — `expires_at` is an optional Unix timestamp.
2. Hand the returned `share_link` to the user.
3. Later, when the user asks whether it was opened: `marcora:get_share_link_activity(team_id, share_link)` with the link or its token, or omit `share_link` (`marcora:get_share_link_activity(team_id, filter?, query?)`) to list every link in that team. Report `summary` (from `link_detail`); if `opened` is true but the viewer list is short or empty, say some opens predate open details (`coverage_note`). Viewers are anonymous numbers, so never name who opened it. Never open the link yourself to check.

**Precondition.** Content must be `completed` — async generations need to finish first.

---

## Recipe E — Export content to Word

**Goal.** Produce a `.docx` download for a content item.

**Steps.**
1. `marcora:get_content(team_id, content_id)` — fetch the markdown body. (This is one of the few legitimate uses of `get_content`.)
2. `marcora:convert_markdown_to_word_doc(team_id, markdown_content, filename?, document_url?)` — `document_url` embeds as a footer link to the original.
3. Hand the returned `download_url` to the user.

---

## E11 — `convert_markdown_to_word_doc` doesn't auto-fetch by ID

**Symptom.** Calling the conversion tool with a content ID instead of markdown content fails.

**Cause.** This tool takes `markdown_content` as a parameter — it does not pull content by ID.

**What to do.** Two-step: `marcora:get_content(team_id, content_id)` → `marcora:convert_markdown_to_word_doc(team_id, markdown_content=...)`. Optionally pass `document_url` (the original content's `link_url`) so the .docx footer links back.

---

## Recipe F — Publish a document to a connected app destination

**Goal.** Publish a Marcora document to a configured destination (e.g. Google Docs, Notion), update all linked copies, or link an existing external copy.

**Steps.**
1. Call `marcora:publish_content(team_id, content_id, mode="status")` first to inspect `destinations[]` (`workflow_id`, `app`, `first_run`), `published_to[]`, `is_private`, and `is_owner`.
   - If `destinations[]` is empty, tell the user that publish destinations can only be set up in the Marcora app (`setup_url`), not over MCP.
2. Call `marcora:publish_content(team_id, content_id, mode="publish", workflow_id=...)` (or `mode="update_everywhere"` to refresh all current copies).
   - **Started:** a publish returns `status: "started"` straight away. Poll `publish_content(mode="status")` and read the destination's `last_run.status`, `last_run.error_summary` and `link.external_url`; never publish again just because the run is still running.
   - **Private documents:** if `private_document_needs_confirmation` is returned (or `status` shows `is_private: true, is_owner: true`), ask the owner to confirm before repeating with `confirm_private_document: true`. Never retry `private_document_owner_required`.
   - **First-run approval:** if the run returns `awaiting_approval`, tell the user to approve it in Marcora (`link_url`) — do **not** retry.
   - **Outside edits / already sent / unrecorded:** surface `needs_decision` (`outside_edit` → ask `skip` vs `replace`) or `blocked` (`already_sent` → offer `new_copy: true`; `created_unlinked` / `publish_unrecorded` → do not publish again; use `mode="link"` with `reference` or link in Marcora).

