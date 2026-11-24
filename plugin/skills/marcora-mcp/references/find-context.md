# Find existing context and answer questions

Read this before answering "what do we have on X?", browsing or searching the library, or drafting content yourself (saving it through `content`) that must be on-brand.

---

### Workflow 5 — Find existing context / Q&A / ideation

**Goal.** Answer the user's question about what's in their library, or help them ideate using their existing context.

**Preconditions.** None.

**Pick the right discovery tool based on intent:**
- **Find what the library says about a topic ("what do we have on topic X?")** → `marcora:get_relevant_context`. Returns the passages most relevant to the question, with `sources`. Best when the user has a question that needs *content*, not a list.
- **Browse the catalog ("what context items do I have?", "show me my reference library")** → `marcora:list_context_items`. Returns names + intros + IDs, newest first. Set `reference_library_only=true` to scope to top-level Reference Library items only (i.e. items not in any project or collection). An optional `search` re-orders all visible items with no cutoff—title matches first (`title_exact`, `title_prefix`, `title_words`, `title_fuzzy`), then `meaning` (`relevance_score >= 0.4`), then unmatched items (`none`) in default order—adding `match` and `relevance_score` to each item.
- **Fetch the full content of a known item ("pull the brand voice guide", "open the manager-feedback transcript")** → `marcora:get_context_item(team_id, context_item_id)`. Returns full markdown + metadata + link.
- **Browse the team's content ("what documents have we made?")** → `marcora:list_content`. Returns every piece the user can see (including `blueprint: { blueprint_uuid, name } | null`), newest first; an optional `search` re-orders all visible content with no cutoff—title matches first (`title_exact`, `title_prefix`, `title_words`, `title_fuzzy`), then `meaning` (`relevance_score >= 0.4`), then unmatched content (`none`) in default order—adding `match` and `relevance_score` to each row. Use `get_relevant_context` when you want the reference material that is relevant to a question.

**Steps (RAG path).**
1. `marcora:get_relevant_context` with a descriptive `prompt`. Optionally **broaden** with `project_id` or `collection_ids` — these are *additive* (they add that project's / those collections' items on top of the general library) unless you also pass `only_these_collections: true`, which strictly scopes search to ONLY the specified `collection_ids` (rejects empty `collection_ids` and cannot combine with `project_id` or `calls`). Full docs: `learn_marcora_tools({ page: "find-and-search-context" })`.
2. Returns RAG chunks (a few hundred words each, not full items) plus a `sources[]` array — one entry per parent context item, each with its `context_item_id`, name, `content_type`, a `link_url` deep-link (and `source_url` for webpage items), and the chunk IDs from that item. Use `sources` to cite/link what you surface. Each source also carries `content_category` (`company_authoritative` outranks `reference_material` when they disagree) and `is_stale` (treat a stale item's claims with caution).
   - **Passage source labels and block headers:** inside `relevant_context`, every passage carries `<!-- source: company|third_party|unclassified -->` right after its `<!-- ## BEGIN [...] -->` marker (`third_party` covers external reference material, another team's shared Marcora Collection item, and calls; `unclassified` is never `third_party`). Treat `third_party` passages as claims about others or external material, never as the team's own facts or voice. Passages are grouped under `--- From the "<name>" collection: <desc> ---`, `--- From the "<title>" Marcora Collection: <desc> ---` (Marcora Collection passages sit in their own blocks after the Reference Library), `--- Calls ---`, or `--- Collection Context ---` fallback (`: <desc>` is omitted when empty).
   - **With `project_id`, the first call also returns the project's brief** as a `project_brief` block ahead of the chunks. Read it first, and weigh the chunks against it — see "Working inside a project" in `references/projects-and-briefs.md`. Pass `include_project_brief: false` on later calls for the same project.
3. If results are sparse: paginate with `context_rag_ids` (excludes already-returned chunks), or offer to add new context.
   - **To search the team's calls too, pass `calls`:** `{ date_from, date_to, kinds, companies }`, every field optional (dates as YYYY-MM-DD or ISO 8601; `kinds` from `customer`, `external`, `team_meeting`, `one_on_one`, `recorded`; `{}` is every call you may use). Each call's heading carries its date, kind and company. Only Team calls come back, never a teammate's Only me call; `include_only_me: true` adds the user's own Only me calls. Leave `calls` out and nothing changes.
   - **A Team call filed in a private project or private collection reads as Only me.** Its source carries `audience: "only_me"`, so treat it like any other Only me source: do not put its text in anything the team can see without asking the user.
4. If the user wants the *full* content of one of the surfaced items, follow up with `marcora:get_context_item(team_id, context_item_id)` — `get_relevant_context` only returns chunks, not the whole item.
5. Summarize for the user — don't dump raw chunks unless asked.

**Writing the content yourself? (This is the default for new content.)** When you draft with your *own* model and then save it via the `content` parameter of `create_content` (or `update_content`) — rather than letting Marcora generate from `instructions` — call `marcora:get_relevant_context(team_id, prompt, include_brand_foundation=true)` **first** and write from what it returns. You get Reference Library RAG chunks **and** the team's Brand Foundation (company overview, brand voice, writing style, writing examples) in one response — so you write on-brand without a separate `get_brand_foundation` call. Those `content`-save paths store your text verbatim and consult no context on their own, so this fetch is the only thing that grounds your draft. Don't set the flag when handing off via `instructions` (that path pulls Brand Foundation in automatically). When paginating, set it `true` on the first page only. If you are writing for a project, pass its `project_id` too: the first call returns the project's brief, and your draft must not contradict it.

**Steps (browse path).**
1. `marcora:list_context_items` (default returns everything the user can see; pass `reference_library_only=true` for just orphan items in the top-level Reference Library). Items in private collections / private projects the user is not in are filtered out automatically. Calls come back too: filter with `content_type: "call_transcript"`, `date_from` / `date_to`, `kinds` and `company`, and read each call's `call` block (date, kind, company, people, audience).
2. Optionally `marcora:list_context_collections` if the user is asking about collection-level organization (it also lists the Marcora Collections in their library, marked `source: "marcora_collection"`), or `marcora:get_project(team_id, project_id).context_items` for one project's items.
3. If the user wants to read the actual content of an item, `marcora:get_context_item(team_id, context_item_id)`.

**Output to user.** A summary, not a JSON dump. Offer next steps: drill into a specific item (`get_context_item`), add new context, generate something based on what was found.

---

## E2 — `get_relevant_context` returns chunks, not full items

**Symptom.** You expected a complete document and got a few hundred words.

**Cause.** `marcora:get_relevant_context` returns RAG chunks (typically a few hundred words each) plus a `sources[]` array — one entry per parent item, each with its `context_item_id` and a `link_url`.

**What to do.** For the full body of a surfaced item, call `marcora:get_context_item(team_id, context_item_id)` (take the ID from `sources[]`), or hand the user the source's `link_url` to open it in the Marcora app. For most "what context exists about X?" questions, the chunks themselves are sufficient.

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

**Named collection ("Use the 'X' context collection in Marcora…").** Check `list_context_collections` first. If the title is there (`source: "team"` or `"marcora_collection"`), pass its `id` in `collection_ids` on `get_relevant_context` (with `include_brand_foundation: true`, and `only_these_collections: true` when they want ONLY that collection without the Reference Library), or as `collection_id` on `list_context_items`, and answer. If it is **not** there, do not say it does not exist: it is likely a published Marcora Collection not yet in the user's library. Find it with `list_marcora_collections` (`search` set to the title) and, if `in_library` is `false`, call `add_marcora_collection` **without asking** (naming the collection to use is the instruction to add it). Then use the returned `collection_id` the same way. `already_in_library: true` means it was already there (for example attached at signup): do not tell the user you just added it. Present each `link_url` exactly as returned.
