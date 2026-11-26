# Share and export content

Read this before creating an external share link or exporting a document to Word.

---

## Recipe D — Share content externally

**Goal.** Generate a public share URL for a piece of content.

**Steps.**
1. `marcora:create_external_share(team_id, content_id, expires_at?, confirm_private_sources?)` — `expires_at` is an optional Unix timestamp in milliseconds.
2. Hand the returned `share_link` to the user.
3. Later, when the user asks whether it was opened (or who a link was created for): `marcora:get_share_link_activity(team_id, share_link)` with the link or its token, or omit `share_link` (`marcora:get_share_link_activity(team_id, filter?, query?)`) to list every link in that team. On paid plans with tracking enabled, each link includes `recipient_name` and `recipient_email` (or `null`) for who the link was created for; report `summary` (from `link_detail`), and if `opened` is true but the viewer list is short or empty, say some opens predate open details (`coverage_note`). Viewers are anonymous numbers, so never claim a named recipient opened it. Never open the link yourself to check.

**Rules & Preconditions.**
- Content must be `completed` — async generations need to finish first.
- Documents marked **Internal only** cannot be shared outside the workspace (refused directly).
- If the document used `only_me` material, the call returns a `confirm_private_sources` token instead of a link — ask the user, and only if they agree repeat the call with `confirm_private_sources` set to that token.

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
