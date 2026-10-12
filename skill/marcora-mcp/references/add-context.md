# Add reference context

Read this before calling `add_context`: saving pasted text, a one-off URL snapshot, or a refreshable web page to the Reference Library or a project.

---

### Workflow 3 — Add reference context to the user's library

**Goal.** Persist a reference document (brand guidelines, persona research, competitor analysis, product spec, customer interview) so future generations can draw on it.

**Preconditions.** None.

**Steps.**
1. **Disambiguate scope.** Ask if it's not obvious from context:
   - Top-level (Reference Library) → available across all projects.
   - Project-scoped → only for one initiative.
   - Project brief → strategic anchor for a project (use Workflow 2, not this one).
   - Document-specific (one-off context for a single generation) → don't store; pass `collection_ids` or `dimension_option_ids` on `create_content` instead.
2. If top-level + the user wants it organized: `marcora:list_context_collections`. Use existing collection if a fit; otherwise `marcora:create_context_collection`.
3. `marcora:add_context` with `name` and the body, plus optional `collection_id` (top-level) or `project_id` (project-scoped). Pick the body argument based on what you have — provide **exactly one** of these three (zero or more than one → 400):
   - **`content`** — paste markdown directly. Best for short or hand-authored material.
   - **`import_url`** — pass a public URL imported **once**: Marcora fetches it and converts the page to clean markdown, stored as a **static snapshot** (the URL is not retained, the item is not refreshable). Use for one-off sources — a blog post, a presigned-link export from Google Docs or a connected-app sandbox, etc. Don't `web_browse`/`web_fetch` it into your conversation first just to forward the bytes.
   - **`connected_webpage_url`** — pass a URL to track as a live, refreshable **web page** (`content_type: "webpage"`): the URL is stored so it can be re-pulled later via `update_context(refresh_webpage=true)` or the app's refresh button. Use this for the customer's own pages and anything you'll want to keep current. Dedupes by URL (re-adding updates in place). **Admin/editor only** — collaborators are rejected.

**Output to user.** "Added: [link]. Want to use this in a content generation now?"
