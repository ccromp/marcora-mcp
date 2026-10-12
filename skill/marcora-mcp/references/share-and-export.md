# Share and export content

Read this before creating an external share link or exporting a document to Word.

---

## Recipe D — Share content externally

**Goal.** Generate a public share URL for a piece of content.

**Steps.**
1. `marcora:create_external_share(content_id, expires_at?)` — `expires_at` is an optional Unix timestamp.
2. Hand the returned `share_link` to the user.

**Precondition.** Content must be `completed` — async generations need to finish first.

---

## Recipe E — Export content to Word

**Goal.** Produce a `.docx` download for a content item.

**Steps.**
1. `marcora:get_content(content_id)` — fetch the markdown body. (This is one of the few legitimate uses of `get_content`.)
2. `marcora:convert_markdown_to_word_doc(markdown_content, filename?, document_url?)` — `document_url` embeds as a footer link to the original.
3. Hand the returned `download_url` to the user.

---

## E11 — `convert_markdown_to_word_doc` doesn't auto-fetch by ID

**Symptom.** Calling the conversion tool with a content ID instead of markdown content fails.

**Cause.** This tool takes `markdown_content` as a parameter — it does not pull content by ID.

**What to do.** Two-step: `marcora:get_content(content_id)` → `marcora:convert_markdown_to_word_doc(markdown_content=...)`. Optionally pass `document_url` (the original content's `link_url`) so the .docx footer links back.
