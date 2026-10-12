# Find existing context and answer questions

Read this before answering "what do we have on X?", browsing or searching the library, or drafting content yourself (saving it through `content`) that must be on-brand.

---

### Workflow 5 — Find existing context / Q&A / ideation

**Goal.** Answer the user's question about what's in their library, or help them ideate using their existing context.

**Preconditions.** None.

**Pick the right discovery tool based on intent:**
- **RAG search ("what do we have on topic X?")** → `marcora:get_relevant_context`. Returns relevance-ranked chunks. Best when the user has a question that needs *content*, not a list.
- **Browse the catalog ("what context items do I have?", "show me my reference library")** → `marcora:list_context_items`. Returns names + intros + IDs. No RAG, just inventory. Set `reference_library_only=true` to scope to top-level Reference Library items only (i.e. items not in any project or collection).
- **Fetch the full content of a known item ("pull the brand voice guide", "open the manager-feedback transcript")** → `marcora:get_context_item(context_item_id)`. Returns full markdown + metadata + link.
- **Semantic ranked search ("find my most relevant docs/items on X", "which of my content is closest to this brief?")** → `marcora:list_content(search=…)` and/or `marcora:list_context_items(search=…)`. Pass a natural-language `search` query to rank by semantic relevance (each row/item gains a `relevance_score`, cosine `0`–`1`, higher = closer) instead of recency. The two tools' scores are **cross-comparable** — run both with the same query, merge, take the top by `relevance_score`, then confirm with the user before opening full text. Use this when the user wants the *right existing document/item* ranked by meaning — vs `get_relevant_context`, which returns RAG *chunks* of context for answering, not a ranked doc+item list.

**Steps (RAG path).**
1. `marcora:get_relevant_context` with a descriptive `prompt`. Optionally **broaden** with `project_id` or `collection_ids` — these are *additive* (they add that project's / those collections' items on top of the general library, they don't restrict to only them). This is the *only* legitimate use of this tool besides the narrow Workflow 1 sourcing-check.
2. Returns RAG chunks (a few hundred words each, not full items) plus a `sources[]` array — one entry per parent context item, each with its `context_item_id`, name, `content_type`, a `link_url` deep-link (and `source_url` for webpage items), and the chunk IDs from that item. Use `sources` to cite/link what you surface. Each source also carries `content_category` (`company_authoritative` outranks `reference_material` when they disagree) and `is_stale` (treat a stale item's claims with caution).
   - **With `project_id`, the first call also returns the project's brief** as a `project_brief` block ahead of the chunks. Read it first, and weigh the chunks against it — see "Working inside a project" in `references/projects-and-briefs.md`. Pass `include_project_brief: false` on later calls for the same project.
3. If results are sparse: paginate with `context_rag_ids` (excludes already-returned chunks), or offer to add new context.
4. If the user wants the *full* content of one of the surfaced items, follow up with `marcora:get_context_item(context_item_id)` — `get_relevant_context` only returns chunks, not the whole item.
5. Summarize for the user — don't dump raw chunks unless asked.

**Writing the content yourself?** If you'll draft with your *own* model and then save it via the `content` parameter of `create_content` (or `update_content`) — rather than letting Marcora generate from `instructions` — call `marcora:get_relevant_context(prompt, include_brand_foundation=true)` **first** and write from what it returns. You get Reference Library RAG chunks **and** the team's Brand Foundation (company overview, brand voice, writing style, writing examples) in one response — so you write on-brand without a separate `get_brand_foundation` call. Those `content`-save paths store your text verbatim and consult no context on their own, so this fetch is the only thing that grounds your draft. Don't set the flag when handing off via `instructions` (that path pulls Brand Foundation in automatically). When paginating, set it `true` on the first page only. If you are writing for a project, pass its `project_id` too: the first call returns the project's brief, and your draft must not contradict it.

**Steps (browse path).**
1. `marcora:list_context_items` (default returns everything the user can see; pass `reference_library_only=true` for just orphan items in the top-level Reference Library). Items in private collections / private projects the user is not in are filtered out automatically.
2. Optionally `marcora:list_context_collections` if the user is asking about collection-level organization, or `marcora:get_project(project_id).context_items` for one project's items.
3. If the user wants to read the actual content of an item, `marcora:get_context_item(context_item_id)`.

**Steps (semantic-search path).**
1. `marcora:list_content(search="<natural-language query>")` and `marcora:list_context_items(search="<same query>")`. When `search` is provided, results are ordered by semantic relevance to the query instead of recency.
2. Each returns its rows/items with a `relevance_score` (cosine `0`–`1`, higher = closer). The scores are **cross-comparable across the two tools**, so merge both arrays and sort by `relevance_score` to get the single best set. (Omit `search` for the normal recency-ordered list; `relevance_score` is present only when `search` is supplied.)
3. Present the top matches to the user for confirmation, then fetch full text with `marcora:get_content(content_id)` / `marcora:get_context_item(context_item_id)`.

**Output to user.** A summary, not a JSON dump. Offer next steps: drill into a specific item (`get_context_item`), add new context, generate something based on what was found.

---

## E2 — `get_relevant_context` returns chunks, not full items

**Symptom.** You expected a complete document and got a few hundred words.

**Cause.** `marcora:get_relevant_context` returns RAG chunks (typically a few hundred words each) plus a `sources[]` array — one entry per parent item, each with its `context_item_id` and a `link_url`.

**What to do.** For the full body of a surfaced item, call `marcora:get_context_item(context_item_id)` (take the ID from `sources[]`), or hand the user the source's `link_url` to open it in the Marcora app. For most "what context exists about X?" questions, the chunks themselves are sufficient.

---

## E3 — Pagination for `get_relevant_context`

**Symptom.** Repeating a `get_relevant_context` call returns the same chunks.

**Cause.** Without pagination, every call returns the top-N most relevant chunks — same set.

**What to do.** Pass `context_rag_ids` (the IDs returned in the previous call) to exclude already-seen chunks. Effectively paginates.

---

## E4 — Project context items are included verbatim — no relevancy filtering

**Symptom.** A project with many large context items has slow generations or hits limits.

**Cause.** Project context items (Layer 3) are included in full during in-project generations — no relevancy scoring, unlike Reference Library (Layer 2).

**What to do.** Suggest the user prune project context to items still relevant to the initiative. Universally-useful items belong in the Reference Library (top-level) instead.
