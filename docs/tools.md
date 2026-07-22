# Tools Reference

The Marcora MCP Server exposes a set of tools that your AI assistant can call directly to interact with your workspace. Each tool maps to a specific action — from generating content to retrieving context — and can be invoked naturally through conversation.

The tools below are available to any connected AI assistant once the Marcora MCP Server is configured.

---

## Account

### `get_current_user_info`

Returns profile and subscription information for the currently authenticated user, including active team, role, subscription plan, and AI-credit usage.

**Parameters:** None

**Output:**

| Field | Type | Description |
|---|---|---|
| `name` | string | User's display name |
| `email` | string | User's email address |
| `active_team_name` | string | Name of the user's active team |
| `active_team_role` | string | User's role on the active team |
| `plan_name` | string | Subscription plan display name |
| `plan_slug` | string | Subscription plan identifier |
| `subscription_status` | string | Current subscription status |
| `ai_credits_available` | integer | AI credits remaining this billing period (limit minus used) |
| `ai_credits_max` | integer | AI credit limit for this billing period |

**Example prompts:**
- "What plan am I on?"
- "Show me my account info"
- "How much usage do I have left?"

---

### `invite_user`

Invite someone to your Marcora account by email. An invitation email is sent automatically, and the response also returns the exact invite link so you can share it directly (e.g. paste it to the person in Slack).

Roles: **creator** (a full team member who can create and edit content), **admin** (a team administrator), and **collaborator** (a project-scoped member who only works inside one project). Brand-new invitees get a sign-up link; people who already have a Marcora account get a login link and see the invitation in-app after they log in.

> **Who can invite whom.** You must be an **admin** to invite an admin or a creator (admins can invite any role). A **creator** can invite collaborators only. Viewers cannot invite anyone.

> **`project_id` behavior.** Required for a **collaborator** — it's the project they'll collaborate on. Optional for a **creator/admin**, where it does **not** limit their access (they keep full team access); it just also adds them to that project and deep-links their invite so they land in it on first sign-in.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `email` | string | Yes | Email address of the person to invite |
| `role` | string | Yes | `admin`, `creator`, or `collaborator` |
| `project_id` | string | Conditional | Project UUID (from `list_projects`). Required for `collaborator`; optional for `creator`/`admin` to also add them to that project |

**Output:**

| Field | Type | Description |
|---|---|---|
| `outcome` | string | `invited` (an invitation email was sent) or `added_to_project` (the email was already a team member and was added straight to the project) |
| `emailed` | boolean | True when an invitation email was sent |
| `invite_link` | string \| null | The exact link to share directly — the sign-up link (with the project deep-link when a project was given) for new users, or the login URL for existing users. `null` when no invitation was sent |
| `message` | string | Human-readable summary of what happened |
| `email` | string | The invited email address |
| `role` | string | `admin`, `creator`, or `collaborator` |
| `project_id` | string \| null | Project the invitee was added to / pointed at, if any |
| `existing_user` | boolean \| null | True if the email already had a Marcora account (login link) vs a new sign-up link |
| `invitation_id` | integer \| null | ID of the created/reused invitation, when one was sent |
| `invite_token` | string \| null | Invitation token, when one was sent |

> **Errors.** A collaborator with no `project_id` returns a 400. Inviting a creator/admin when you are not an admin returns a 403. An email that is already an active team member (with no project to add them to), or already has a pending invitation, returns a clear error.

**Example prompts:**
- "Invite jordan@acme.com to the team as a creator"
- "Add sam@acme.com as a collaborator on the Website Update project"
- "Invite priya@acme.com as an admin and give me the sign-up link to send her"

---

### `get_team_info`

**Always** use this when the user asks what team accounts they have, which teams they belong to / are on, or wants to switch teams — do **not** answer from memory or session context, which knows only the single currently-active team and will undercount (a user can belong to many teams). This tool is the only way to enumerate the full list. Returns every team you belong to, each with its full member roster. Read-only, no inputs. Also use it **before** assigning a plan or content to a teammate (to look up their numeric `user_id` — the value `assigned_to` expects), or to answer questions about the team's members and your role. Deliberately excludes credits/subscription — call `get_current_user_info` for those.

**Parameters:** none.

**Output:**

| Field | Type | Description |
|---|---|---|
| `teams` | array | Every team the caller is an active member of |
| `teams[].team_id` | integer | Numeric team id. Pass to `set_active_team` |
| `teams[].team_name` | string | Team name |
| `teams[].is_active` | boolean | True for the caller's currently active team (exactly one) |
| `teams[].your_role` | string | The caller's role in this team (e.g. `admin`, `editor`, `viewer`) |
| `teams[].members` | array | The team's members |
| `teams[].members[].user_id` | integer \| null | Numeric user id (what `assigned_to` expects). `null` for a pending invite |
| `teams[].members[].name` | string | Member name (or the invited email for pending invites) |
| `teams[].members[].email` | string \| null | Member email |
| `teams[].members[].role` | string | Member's role |
| `teams[].members[].status` | string | `active` or `invited` |

**Example prompts:**
- "Who's on my team?"
- "Assign this plan to Sarah" (look up Sarah's `user_id`, then `update_plan`)

---

### `set_active_team`

Sets your active team — the team all subsequent Marcora tool calls operate against. Input: `team_id` (from `get_team_info`).

> **⚠️ Global effect.** Switching your active team changes it **everywhere** for your account — open Marcora app tabs, running Cora sessions, and every other connected MCP client — because it writes the same active-team setting the in-app switcher uses. Tell the user before switching, and don't switch while other work is mid-flight for them. The response returns `previous_team_id` so you can restore their original team when done: switch → do the work → `set_active_team` back to `previous_team_id`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `team_id` | integer | Yes | The numeric `team_id` (from `get_team_info`) to switch to. Must be a team you belong to |

**Output:**

| Field | Type | Description |
|---|---|---|
| `previous_team_id` | integer \| null | The team that was active before this call. Pass it back to `set_active_team` to restore |
| `active_team.team_id` | integer | The now-active team's id |
| `active_team.team_name` | string | The now-active team's name |

> **Errors.** A `team_id` you don't belong to (or that doesn't exist) returns a readable "you are not a member of that team" error. A missing / non-positive `team_id` returns a readable input error.

**Example prompts:**
- "Switch me to my Acme team"
- "Work in my other team for this, then switch me back"

---

## Context & Resources

### `get_brand_foundation`

Returns the team's Brand Foundation — the foundational brand and company information that guides all AI-generated content. The four elements are:

- **`company_overview`** — general information about the company
- **`brand_voice`** — tone, core values, mission, and personality
- **`writing_style`** — language complexity, sentence structure, formatting preferences, CTA style
- **`writing_examples`** — sample content demonstrating the team's distinctive voice (free-form structure; users organize this however they like)

**When to use it:** call it whenever the user asks about — or wants the agent to use — their brand voice, company overview, writing style, or writing examples (e.g. *"What is our brand voice?"*, *"What is the brand voice of `<company>`?"*, *"Summarize our company overview"*). These four elements live ONLY here — `get_relevant_context`'s relevancy search does **not** surface Brand Foundation, so this is the correct tool for any brand-voice / company-overview / writing-style / writing-examples question, not relevancy search.

By default returns all four elements. Pass `elements` to scope the response to a subset. The response is structured JSON — paste it directly into a downstream AI prompt (modern LLMs read JSON fine) or template-string the fields into markdown if you prefer.

> **Note:** You don't need to call this before `create_content` with `instructions` (or `create_plan`) — those pull Brand Foundation in automatically. But if **you** are composing content yourself to save via the `content` parameter of `create_content`/`update_content`, fetch it first (or use `get_relevant_context` with `include_brand_foundation: true`), since those verbatim-save paths consult no context. Call it directly whenever the user wants to see, discuss, or hand off their Brand Foundation.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `elements` | array of enum | No | Optional subset of elements to return. Values: `company_overview`, `brand_voice`, `writing_style`, `writing_examples`. Omit or pass empty to return all four |

**Output:**

| Field | Type | Description |
|---|---|---|
| `company_overview` | string | Markdown content for Company Overview. Empty string if not set. Only present if requested via `elements` |
| `brand_voice` | string | Markdown content for Brand Voice. Empty string if not set. Only present if requested via `elements` |
| `writing_style` | string | Markdown content for Writing Style. Empty string if not set. Only present if requested via `elements` |
| `writing_examples` | string | Markdown content for Writing Examples. Free-form structure — whatever the user has saved. Empty string if not set. Only present if requested via `elements` |
| `link_url` | string | Deep-link that opens the Brand Foundation section in the Marcora web app (where the user can toggle between the four elements). Always present |

**Example prompts:**
- "What's my brand foundation?"
- "Show me my company's brand voice"
- "Just show me my writing style and writing examples"

---

### `update_brand_foundation`

Overwrites one of the team's four Brand Foundation elements with new content. **Always full-replace — no patch semantics.** Other elements are untouched. If the team has no row for the element yet, one is created.

> **Important:** Before calling this tool, you should typically call `get_brand_foundation({elements: ["<element>"]})` first to read the current value so the user can confirm what's being replaced. Brand Foundation content shapes every AI-generated piece of content the team produces, so unintended overwrites are costly.

**Elements and limits:**

| Element | Description | Max chars |
|---|---|---|
| `company_overview` | General information about the company | 10,000 |
| `brand_voice` | Tone, core values, mission, personality | 20,000 |
| `writing_style` | Language complexity, sentence structure, formatting preferences, CTA style | 20,000 |
| `writing_examples` | Sample content demonstrating the team's distinctive voice (free-form structure) | 20,000 |

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `element` | enum | Yes | Which element to overwrite. One of `company_overview`, `brand_voice`, `writing_style`, `writing_examples` |
| `content` | string | Yes | New markdown content. Replaces existing content in full. Free-form — no enforced structure |

**Output:**

| Field | Type | Description |
|---|---|---|
| `element` | string | Which element was updated (echoes the input) |
| `content` | string | Updated markdown content (echoes what was stored) |
| `link_url` | string | Deep-link that opens the Brand Foundation section in the Marcora web app. Always present |

> **Hand the user the returned `link_url`** when you point them at their updated Brand Foundation — don't construct a URL yourself. There is no `/brand-foundation` route; the real one is `/context-hub?tab=brand-foundation`, and a hand-built link 404s and bounces the user to `/home`.

> **Errors:** If `content` exceeds the element's max character limit, the call returns a structured `ERROR_CODE_INPUT_ERROR` response naming both the limit and the actual length (e.g. *"company_overview content exceeds the 10000-character limit (got 12483 chars)"*). The write is rejected before any DB mutation — no partial updates.

**Example prompts:**
- "Update my brand voice to be less formal and more conversational"
- "Replace my company overview with the latest one-pager I just shared"
- "Save this as my writing examples"

---

### `list_context_collections`

Returns all context collections accessible to the current user. Collections organize reference materials (context items) that inform AI-generated content.

**Parameters:** None

**Output:** An object with a single `collections` key holding an array of context collections. Each item:

| Field | Type | Description |
|---|---|---|
| `id` | integer | Collection ID. Pass to `add_context` or `get_relevant_context` |
| `name` | string | Collection name |
| `description` | string | Collection description |
| `is_private` | boolean | Whether this collection is private to the creator |
| `item_count` | integer | Number of context items in this collection |
| `link_url` | string | Direct URL to view this collection in the Marcora app |

**Example prompts:**
- "Show me my context collections"
- "What reference materials do I have?"

---

### `create_context_collection`

Create a new context collection to organize your reference materials. Collections group related context items together for easier management and targeted retrieval.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | A descriptive name for the collection |
| `description` | string | Yes | A short description of what this collection contains |
| `is_private` | boolean | Yes | If true, only you can see this collection. If false, all team members can access it |

**Output:**

| Field | Type | Description |
|---|---|---|
| `id` | integer | Collection ID. Pass as `collection_id` to `add_context` |
| `name` | string | Collection name |
| `description` | string | Collection description |
| `is_private` | boolean | Whether this collection is private to the creator |
| `created_at` | integer | Unix timestamp of creation |
| `link_url` | string | Direct URL to view this collection in the Marcora app |

**Example prompts:**
- "Create a new collection called 'Q2 Product Research'"
- "Make a private collection for competitive analysis"

---

### `add_context`

Add a new context item to your reference library. Context items are reference materials that power AI generation — they help the AI produce more accurate, on-brand, and relevant content.

You can supply the body in exactly one of three ways:

- **`content`** — paste the markdown body directly. Best for short or hand-authored material. Creates a plain-text (`manual`) item.
- **`import_url`** — pass a public URL to import **once**. The backend fetches it and converts it to clean markdown server-side using a headless browser + Mozilla Readability (the same engine used for the user-website context-import flow), then stores that markdown as a **static snapshot**. The URL is **not** retained and the item is **not** refreshable. Use for one-off imports — a presigned-link export (e.g. Google Doc, connected-app sandbox), a competitor's blog post, or anything you'd otherwise have to pull into your own conversation just to forward. Importing is **asynchronous**: the call returns immediately with the new item's `id` and `import_status: "processing"`, and the content finishes loading a moment later — poll `get_context_item` to confirm (the content appears and `import_status` flips to `"ready"`). Because it returns right away, you can import many URLs back-to-back without anything timing out. If an item is still missing a minute or two later, the fetch didn't succeed — check the URL and try again.
- **`connected_webpage_url`** — pass a URL to track as a live **web page**. The backend fetches the page, stores it as a `webpage` context item, and **remembers the URL** so it can be re-pulled later (via `update_context` `refresh_webpage`, or the refresh button in the Marcora web app). Use this for the customer's own pages and any page you want to keep current. If the same URL is already tracked, the existing item is **updated in place** (no duplicate).

Providing zero, or more than one, of `content` / `import_url` / `connected_webpage_url` returns a 400.

> **Web pages require admin or editor role.** `connected_webpage_url` is rejected for collaborators, matching the in-app *Add web page* rule. `content` and `import_url` remain available to collaborators.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Descriptive name for the context item |
| `content` | string | Conditional | Markdown body (creates a `manual` item). Provide exactly one of `content` / `import_url` / `connected_webpage_url` |
| `import_url` | string | Conditional | Public URL imported **once** as a static markdown snapshot (URL not retained, not refreshable). Provide exactly one of the three body inputs |
| `connected_webpage_url` | string | Conditional | Public URL tracked as a live, refreshable `webpage` item (URL stored; dedupes by URL; admin/editor only). Provide exactly one of the three body inputs |
| `collection_id` | integer | No | Collection ID to organize the item (from `list_context_collections` or `create_context_collection`). **Omit it — or pass `0` — to file the item at the top level of the Reference Library** |
| `project_id` | string | No | Project ID to associate with (from `list_projects`). Omit it to leave the item unassociated |

> **Filing an item in the Reference Library:** omitting `collection_id` — or passing `0` — files the item at the top level of the **Reference Library**, where it's returned by `list_context_items`, fetchable via `get_context_item`, and eligible for semantic search. This is the normal path for team-wide reference material.
>
> Unlike `update_context`, this tool's `collection_id` is typed as a bare `integer` in the input schema, so a strict MCP client **cannot** send a literal `null` here. You don't need one: `collection_id` is optional on `add_context`, so simply **omitting** it is the idiomatic way to file at the top level. (The server treats an explicit `null` the same as omitted/`0`, but only clients that don't validate against the schema can send it.)

**Output:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Context item ID |
| `name` | string | Context item name |
| `content_type` | string | `manual` (from `content` / `import_url`) or `webpage` (from `connected_webpage_url`) |
| `content` | string \| null | The stored reference content. `null` for `import_url` items in the immediate response (still loading) — fetch the full body with `get_context_item` |
| `word_count` | integer | Word count of content (`0` while an import is still processing) |
| `import_status` | string \| null | For `import_url` items: `"processing"` right after the call, `"ready"` once the content has loaded. `null` for pasted content and web pages |
| `collection_id` | integer \| null | Collection this item belongs to (null if none) |
| `project_id` | string \| null | Project association (null if none) |
| `created_at` | integer | Unix timestamp of creation |
| `link_url` | string | Direct URL to view this context item in the Marcora app. Resolves to the project, collection, or reference library view depending on the item's scope |

**Example prompts:**
- "Add our brand guidelines to Marcora"
- "Store this competitive analysis as context"
- "Import https://example.com/competitor-pricing as a one-off snapshot called 'Acme pricing'"
- "Import these 20 article URLs into my 'Research' collection"
- "Track our pricing page (https://example.com/pricing) as a web page so I can refresh it later"
- "Add this product brief to the 'Product Launch' collection"

---

### `update_context`

Update an existing context item — change its name, content, or move it between collections / projects. If the item has a linked editing document open in the Marcora sidebar, its title and content stay in sync automatically.

Like `add_context`, you can supply a new body either as inline `content` or as an `import_url` the backend fetches and converts to markdown server-side. Pass at most one — providing both returns a 400. Omit both to leave the body untouched (e.g. when you're only renaming the item or moving it between collections).

To **re-pull a tracked web-page item** from its stored URL — the same action as the refresh button in the Marcora web app — pass **`refresh_webpage: true`**. No content is needed; the content comes from re-fetching the page, and `name` / `content` / `import_url` are ignored when it's set. `refresh_webpage` only works on items added via `add_context` `connected_webpage_url` (content type `webpage`); on any other item it returns a clear error. Requires admin or editor role.

> **`import_url` vs `refresh_webpage`:** `import_url` replaces the body with a fresh **one-off snapshot** and does not establish a tracked URL. To keep a web-page item in sync with its source over time, use `refresh_webpage` on an item that was created with `connected_webpage_url`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `context_item_id` | string (uuid) | Yes | The context item to update |
| `refresh_webpage` | boolean | No | Set `true` to re-pull a `webpage` item's content from its stored URL. Ignores `name` / `content` / `import_url`. Errors on non-webpage items. Admin/editor only |
| `name` | string | No | If provided, updates the name. Omit to leave unchanged. Ignored when `refresh_webpage` is true |
| `content` | string | No | New markdown body. Omit to leave unchanged. Triggers RAG re-embedding. Mutually exclusive with `import_url`. Ignored when `refresh_webpage` is true |
| `import_url` | string | No | Public URL — backend fetches and converts to clean markdown server-side, then stores it as a fresh one-off snapshot body. Mutually exclusive with `content`. Ignored when `refresh_webpage` is true |
| `collection_id` | integer \| null | **Yes (nullable)** | Full replace. Pass the current ID to keep the item in its collection, pass a different ID to move it, or pass `null` (`0` works too) to move it back to the top level of the Reference Library |
| `project_id` | string (uuid) \| null | **Yes (nullable)** | Full replace. Pass the current ID to keep the project association, pass a different ID to move it, or pass `null` to disassociate it |

> **Important:** `collection_id` and `project_id` use full-replace semantics — you must pass them on every call (even with `refresh_webpage`, pass the item's current values; the refresh does not change them). Omitting them is NOT the same as leaving them unchanged. If you don't know the current values, call `get_context_item` first or check the context item in the web app before updating.
>
> The two behave differently when omitted, so pass both explicitly: omitting **`collection_id`** returns a `Missing param` error, while omitting **`project_id`** silently **detaches** the item from its project.

Both fields accept a JSON `null` — the tool's input schema types them as `["integer","null"]` / `["string","null"]`, so strict MCP clients can send `null` directly. Use it to move an item **out of a collection and back to the top level of the Reference Library**, or to **detach it from a project**. For `collection_id`, `0` is accepted as an alias for `null`.

**Output:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Context item ID |
| `name` | string | Updated context item name |
| `content` | string | Updated reference content |
| `content_intro` | string | Truncated content intro used in listings |
| `collection_id` | integer \| null | Collection this item belongs to (null if none) |
| `project_id` | string \| null | Project this item is associated with (null if none) |
| `word_count` | integer | Word count of updated content |
| `updated_at` | integer | Unix timestamp of last update |
| `relevancy_processed_status` | string | RAG re-processing status (`unprocessed`, `provisional`, `complete`). Flips to `unprocessed` whenever name or content changes |
| `link_url` | string | Direct URL to view this context item in the Marcora app |

**Example prompts:**
- "Rename that brand voice context item to 'Brand Voice v2'"
- "Move the competitive analysis out of the 'Archive' collection"
- "Update our pricing context with the new Enterprise tier info"
- "I updated our pricing page — refresh that web-page context item"
- "Re-import the Acme snapshot from https://example.com/competitor-pricing"

---

### `list_context_items`

Lists context items from the team's context library. By default returns all items the user can see (across projects, collections, and the reference library). Set `reference_library_only=true` to return only items that are not in any project or collection — these are the items shown in the "Reference Library" section of the Marcora web app.

Each returned item carries its own `collection_id` and `project_id` (both nullable), so you always know where it lives. To get the full markdown content of any item, pass its id to `get_context_item`.

**Privacy:** items in private collections (where you are not the creator) and items in private projects (where you are not a member) are filtered out — they will not appear in the response.

**Semantic search:** pass a natural-language `search` query to rank items by semantic relevance (by their best-matching chunk) instead of recency; each item then carries a `relevance_score` (cosine `0`–`1`, higher = more relevant). Omit or leave `search` empty for the normal recency-ordered list. The scores are **cross-comparable with `list_content`** — call both tools with the same `search` query, merge the two arrays, and take the top matches by `relevance_score`, then present them to the user for confirmation before fetching full text with `get_context_item` / `get_content`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `search` | string | No | Optional natural-language query. When provided, items are ranked by semantic relevance to it (by their best-matching chunk) instead of recency, and each item gains a `relevance_score`. Omit or leave empty for the normal recency-ordered list. Scores are cross-comparable with `list_content` |
| `reference_library_only` | boolean | No | When `true`, returns only items not in any project or collection. Default `false` returns everything |

**Output:** An object with a single `context_items` key holding an array of context items. Each item has:

| Field | Type | Description |
|---|---|---|
| `id` | string (uuid) | Context item ID. Pass to `get_context_item` to fetch full markdown |
| `name` | string | Context item name |
| `content_intro` | string | Short truncation of the content for previews |
| `content_type` | string | One of `manual`, `webpage`, `canvas`, `deliverable`, `integration_data`, `call_transcript`, `file` |
| `source_url` | string \| null | For `webpage` items, the tracked page URL (re-pull it with `update_context` `refresh_webpage`); `null` for all other item types |
| `word_count` | integer | Word count of the full content |
| `created_at` | integer | Unix timestamp of creation |
| `updated_at` | integer \| null | Unix timestamp of last update |
| `added_by` | object | `{id, name}` of the user who added the item |
| `relevancy_processed_status` | string | RAG indexing status (`unprocessed`, `provisional`, `complete`) |
| `collection_id` | integer \| null | Collection this item lives in, or `null` |
| `project_id` | string (uuid) \| null | Project this item is associated with, or `null` |
| `relevance_score` | number | Present only when a `search` query is supplied. Cosine similarity (`0`–`1`, higher = more relevant) of the item's best-matching chunk to the query. Cross-comparable with the `relevance_score` returned by `list_content` |

**Other ways to discover context-item IDs:**
- `get_project(project_id).context_items` — items attached to a specific project
- `get_relevant_context` — its `sources[]` array carries the `context_item_id` of each parent item for the matched chunks

**Example prompts:**
- "What context items do I have in Marcora?"
- "Show me everything in my reference library"
- "List the context items I haven't filed into a collection or project"

---

### `get_context_item`

Fetch the full markdown content of a single context item by ID. Use this when you need the actual content of an item — `list_context_items` only returns `content_intro` (a short truncation).

The IDs you pass here can come from `list_context_items`, `get_project(project_id).context_items`, `list_context_collections`, or `get_relevant_context`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `context_item_id` | string (uuid) | Yes | UUID of the context item to fetch |

**Output:**

| Field | Type | Description |
|---|---|---|
| `id` | string (uuid) | Context item ID |
| `name` | string | Context item name |
| `content` | string | Full markdown content |
| `content_intro` | string | Short truncation used in listings |
| `content_type` | string | One of `manual`, `webpage`, `canvas`, `deliverable`, `integration_data`, `call_transcript`, `file` |
| `source_url` | string \| null | For `webpage` items, the tracked page URL (re-pull it with `update_context` `refresh_webpage`, or pass it back to `add_context` `connected_webpage_url`); `null` for all other item types |
| `word_count` | integer | Word count of the content |
| `created_at` | integer | Unix timestamp of creation |
| `updated_at` | integer \| null | Unix timestamp of last update |
| `added_by` | object | `{id, name}` of the user who added the item |
| `relevancy_processed_status` | string | RAG indexing status |
| `collection_id` | integer \| null | Collection this item lives in, or `null` |
| `project_id` | string (uuid) \| null | Project this item is associated with, or `null` |
| `link_url` | string | Direct URL to view this context item in the Marcora app |

**Authorization:** the item must belong to your team. Items in private collections (where you are not the creator) and items in private projects (where you are not a member) return a 404 — same as items that do not exist.

**Example prompts:**
- "Pull the full content of my brand voice guide"
- "Show me what's actually in that competitor analysis context item"

---

### `get_relevant_context`

Searches the team's context library and returns the most relevant chunks for a given prompt, assembled into a ready-to-use markdown packet. Alongside the packet it returns a structured `sources` array — one entry per parent context item — so you can cite and deep-link each source without follow-up lookups, plus a `retrieval` object echoing the scope the search ran under. Use this to gather supporting context before generating or refining content.

`collection_ids` and `project_id` are **additive**: they broaden the search to ALSO include those collections / that project's context alongside your general reference library — they do not restrict results to only that collection or project.

Set `include_brand_foundation: true` to also receive the team's Brand Foundation (company overview, brand voice, writing style, writing examples) in the same response — a one-stop fetch of everything you need to write on-brand yourself with your own model. Use this whenever **you** are composing content to save via the `content` parameter of `create_content` or `update_content` (those paths store text verbatim and consult no context). You **don't** need it when handing off to `create_content` with `instructions` — that path pulls Brand Foundation in automatically.

> **Tip — bundle Brand Foundation on the first call:** Default the **first** `get_relevant_context` call of a conversation to `include_brand_foundation: true`. Brand Foundation is always-on foundational context that relevancy scoring never surfaces on its own; pulling it in once, up front, means the agent has the team's company overview and brand voice on hand for the rest of the session — useful even when just answering a question. On **subsequent** calls in the same conversation, set it `false`/omit so it isn't re-sent each time.

> For **Brand Foundation specifically** (brand voice, company overview, writing style, writing examples), relevancy search will **not** return those elements — use `get_brand_foundation`, or `include_brand_foundation: true` above. A *"what is our brand voice?"* question can't be answered from relevancy chunks alone.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | Yes | Search string describing what context you need |
| `project_id` | string (uuid) | No | **Additive** — ALSO searches that project's context alongside the general library. Not an exclusive filter |
| `collection_ids` | array | No | **Additive** — ALSO searches those collections alongside the general library. Not an exclusive filter |
| `dimension_option_ids` | array | No | Targeting dimension option IDs that bias relevancy toward an audience / persona / industry |
| `context_rag_ids` | array | No | Previously returned chunk IDs to exclude (for pagination) |
| `include_brand_foundation` | boolean | No | When `true`, also returns the team's Brand Foundation in the response. Default `false`. Recommended `true` on the **first** call of a conversation (and when paginating, the first page), then `false`/omit on follow-ups so it isn't re-sent each time |

**Output:**

| Field | Type | Description |
|---|---|---|
| `relevant_context` | string | Ready-to-use markdown context packet assembled from the matched chunks |
| `context_rag_ids` | array (uuid) | All chunk IDs returned. Pass back in `context_rag_ids` to exclude from future searches (pagination) |
| `brand_foundation` | object | Always present — see below. `elements` is `null` unless `include_brand_foundation` is `true` |
| `retrieval` | object | Echo of the search scope this response ran under — see below |
| `sources` | array | One entry per parent context item the returned chunks came from — see below |

> The previous top-level `context_item_ids` field has been **removed** — each entry in `sources` carries its own `context_item_id`, and the union of every source's `context_rag_ids` equals the top-level `context_rag_ids`.

**`brand_foundation` object:**

| Field | Type | Description |
|---|---|---|
| `included` | boolean | `true` only when `include_brand_foundation: true` was passed |
| `elements` | object \| null | `null` unless included. When present: `company_overview`, `brand_voice`, `writing_style`, `writing_examples` (strings; empty string for any not yet set) |
| `link_url` | string | Deep-link to the Brand Foundation tab in the Marcora app. Present only when included |

**`retrieval` object:**

| Field | Type | Description |
|---|---|---|
| `team_scope` | string | Always `authenticated_user_active_team` |
| `project_id` | string (uuid) \| null | Echo of the `project_id` input |
| `collection_ids` | array | Echo of the `collection_ids` input |
| `dimension_option_ids` | array | Echo of the `dimension_option_ids` input |
| `excluded_context_rag_ids` | array (uuid) | Echo of the `context_rag_ids` input (the exclusions) |
| `returned_count` | integer | Number of context chunks returned |

**`sources[]` — each entry:**

| Field | Type | Description |
|---|---|---|
| `context_item_id` | string (uuid) | The parent context item's ID |
| `context_item_name` | string \| null | The item's name |
| `content_type` | string \| null | One of `file`, `manual`, `webpage`, `canvas`, `deliverable`, `integration_data`, `call_transcript` |
| `link_url` | string \| null | Deep-link that opens this item in the Marcora app (present for every source) |
| `source_url` | string | Original external page URL — **present only for `webpage` items**, omitted otherwise |
| `collection_id` | integer \| null | Collection the item belongs to, if any |
| `project_id` | string (uuid) \| null | Project the item belongs to, if any |
| `last_updated` | integer \| null | Unix-ms timestamp of the item's last update (`null` if never updated) |
| `context_rag_ids` | array (uuid) | The chunk IDs in this response that came from this item |

**Example prompts:**
- "Find context about our enterprise pricing" (then cite each source via its `link_url`)
- "What do we know about competitor X?"
- "Get context relevant to writing a product launch blog post"
- "Pull together everything I need to write a healthcare launch email, including our brand foundation"

---

## Context Intelligence

Context Intelligence is Marcora's automated review layer for your reference/context library. Health-audit and web-freshness scans produce **findings** — stale content, contradictions, outdated web sources, classification gaps — each with a status lifecycle (`pending` → `acknowledged` / `dismissed` / `resolved`). These tools list and inspect findings, record your decision on them, and kick off a new health-audit sweep. To **apply** a finding's suggested fix, use [`apply_grounding_fix`](#apply_grounding_fix) — it works on health-audit findings and content-grounding findings alike.

### `list_ci_findings`

List Context Intelligence findings for your team — issues Marcora's automated scans detected in your reference/context library (stale content, contradictions, outdated web sources, classification gaps). This is also the right **first call** before updating any finding's status, to get its UUID.

Findings are returned **newest-first**. Each has a status lifecycle: `pending` (new, needs review) → `acknowledged` / `dismissed` / `resolved`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `status` | string | No | Filter by status: `pending` (the actionable queue), `acknowledged`, `dismissed`, `resolved`. Omit for all |
| `severity` | string | No | Filter by severity as recorded by the scan (e.g. `high`, `medium`, `low`). Omit for all |
| `process_type` | string | No | Filter by originating scan: `health_audit` (library-wide sweep) or `web_freshness` (tracked webpage changes). Omit for all |
| `page` | integer | No | Page number (default 1) |
| `per_page` | integer | No | Items per page (default 20, max 100) |

**Output:**

| Field | Type | Description |
|---|---|---|
| `items` | array | Finding objects, each with `id` (uuid), `summary`, `recommendation`, `severity`, `status`, `process_type`, `finding_type`, `suggested_fix`, `context_item_ids`, `created_at`, `resolved_at`, `resolved_by` |
| `itemsTotal` | integer | Total findings matching the filter |
| `curPage` | integer | Current page number |
| `nextPage` | integer \| null | Next page number, or `null` |
| `prevPage` | integer \| null | Previous page number, or `null` |

**Example prompts:**
- "What did Context Intelligence find in our reference library?"
- "Show me the open (pending) context findings"
- "Any high-severity issues from the last health audit?"

---

### `get_ci_finding`

Fetch one Context Intelligence finding in full detail by its UUID (from `list_ci_findings`). Use it when you want the specifics of a finding — the full recommendation, the suggested fix content, or which context items it involves — before deciding to act on it.

The `suggested_fix` object (when present) contains the proposed replacement content. Review it with the user, then **apply** it with [`apply_grounding_fix`](#apply_grounding_fix) — or record a decision without applying anything using `update_ci_finding_status`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `finding_id` | string (uuid) | Yes | UUID of the finding (from `list_ci_findings`) |

**Output:**

| Field | Type | Description |
|---|---|---|
| `id` | string (uuid) | Finding ID |
| `summary` | string | Short description of the finding |
| `recommendation` | string \| null | Full recommended action |
| `severity` | string | Severity as recorded by the scan |
| `status` | string | `pending`, `acknowledged`, `dismissed`, or `resolved` |
| `process_type` | string | Originating scan (`health_audit` or `web_freshness`) |
| `finding_type` | string | The kind of issue detected |
| `suggested_fix` | object \| null | Proposed fix: `field`, `new_value`, `context_item_id`. Apply it with `apply_grounding_fix` |
| `context_item_ids` | array \| null | Context items this finding involves |
| `created_at` | integer | Unix timestamp of creation |
| `resolved_at` | integer \| null | Unix timestamp when resolved, or `null` |
| `resolved_by` | integer \| null | User ID who resolved it, or `null` |

**Errors:**
- **Finding not found** / **You do not have access to this finding** — the UUID is unknown or belongs to another team.

**Example prompts:**
- "Show me the full details of that finding"
- "What's the suggested fix for that context issue?"

---

### `update_ci_finding_status`

Update the status of a Context Intelligence finding — **acknowledge** it, **dismiss** it, or mark it **resolved**. Use it after the user has reviewed a finding (via `list_ci_findings` / `get_ci_finding`) and told you their decision.

Status meanings:
- `acknowledged` — seen, kept on the radar (still open).
- `dismissed` — not relevant / won't fix — removes it from the actionable queue.
- `resolved` — the underlying issue was fixed (records who resolved it and when). This records the resolution **only** — it does **not** apply the suggested fix. To actually apply it, use `apply_grounding_fix` (which resolves the finding for you on success).

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `finding_id` | string (uuid) | Yes | UUID of the finding (from `list_ci_findings`) |
| `status` | string | Yes | New status: `acknowledged`, `dismissed`, or `resolved` |

**Output:**

The updated finding row, including the new `status` (and `resolved_at` / `resolved_by` when resolved).

**Authorization:** requires **admin or editor** role. Confirm with the user before dismissing or resolving a finding they haven't explicitly decided on.

**Errors:**
- **Invalid status** — must be one of `acknowledged`, `dismissed`, `resolved`.
- **Finding not found** / **You do not have access to this finding.**

**Example prompts:**
- "Dismiss that finding — it's not relevant"
- "Mark that one as resolved"
- "Acknowledge those for now"

---

### `trigger_health_audit_scan`

Start a Context Intelligence **health audit** — a library-wide AI sweep of your team's context/reference items that produces findings (stale content, contradictions, gaps) reviewable via `list_ci_findings`. Use it only when the user **explicitly** asks to check/audit their context health; do **not** trigger one unprompted.

The scan runs in the **background**: the response returns immediately with a `scan_run_id`, and findings land as the scan progresses — check `list_ci_findings` afterwards.

**⚠️ Cost + gating:** the scan consumes team AI credits and is gated. It requires the **Business or Command plan** (active subscription) with at least **50 credits** remaining. Only one health audit can run at a time, and a cooldown applies after each completed run. **Starting a new audit clears the previous health-audit findings.**

**Parameters:** None

**Output:**

| Field | Type | Description |
|---|---|---|
| `scan_run_id` | string (uuid) \| null | ID of the started scan run |
| `status` | string | `running` |
| `message` | string | Human-readable status message |

**Errors:**
- **`ci_not_eligible` (403)** — plan / subscription / credits gate failed (JSON error body with reason + credit numbers).
- **A health check is already running** — wait for it to finish.
- **Health check ran recently** — you can run it again after the cooldown (the message says when).

**Example prompts:**
- "Run a health check on our context library"
- "Audit our reference docs for anything stale or contradictory"

---

## Content Grounding

Content grounding checks a **document** against the team's context library: it extracts the document's factual claims and sorts each one into **supported** (the library backs it), **conflict** (the library says something different), or **gap** (the library has nothing on it).

This closes the loop for agent-driven writing — **draft → ground → review → apply → re-ground** — without leaving the conversation.

Three tools:

| Tool | What it does |
|---|---|
| `check_content_grounding` | Runs a scan on new or existing content |
| `get_grounding_result` | Reads a scan's result |
| `apply_grounding_fix` | Applies a finding's recommended fix |

**Two things to get right:**

1. **Grounding is asynchronous.** `check_content_grounding` waits about 20 seconds inline; a fresh scan usually needs 120–150. If it comes back `running`, **poll `get_grounding_result` with the `scan_id`** — calling `check_content_grounding` again starts a *second*, redundant scan.
2. **Review before applying.** Each finding carries its full `suggested_fix`. Show it to the user and get a decision. `apply_grounding_fix` writes to their library.

Grounding requires the **Command plan** with an active subscription and available AI credits.

---

### `check_content_grounding`

Run a grounding scan on a piece of content and get back its claims, findings, and the context items it was checked against.

**When to use:** the user wants to know whether a document is accurate and consistent with what the company has already said — "check this against our context", "is this on-message", "fact-check this draft". Also the natural second step after you draft something for them.

**Three entry modes:**

- **`content_id` alone** — scan a document that already exists in Marcora.
- **`content` alone** — hand over markdown; Marcora stores it as a new document and scans it. The new `content_id` comes back in the response.
- **`content_id` + `content`** — **⚠️ replaces that document's entire body** with the markdown you pass, then re-scans. This is the revise-and-re-ground path.

Passing neither is an error.

> **⚠️ `content` + `content_id` is a whole-document overwrite, identical to `update_content`.**
>
> It is **never** a "check this part" operation. If a user asks you to ground one paragraph or section of a document that already exists, do **not** pass that fragment with its `content_id` — you would replace the entire document with the fragment and destroy the rest of it.
>
> To check part of an existing document: pass **`content_id` alone** and scan the document as it stands. To revise and re-check: pass the **full revised document**, not a fragment.

**Timing (read before calling):** this waits up to ~20 seconds. If the scan finishes in that window you get the full result inline. Otherwise you get `status: "running"` with a `scan_id` — poll `get_grounding_result` with that `scan_id` every 15–30 seconds. Re-scanning an **unchanged** document is fast (a few seconds), because unchanged claims are reused.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `content_id` | string (uuid) | No\* | Existing document to scan. **Pass it alone** to scan the document as it stands — the safe default |
| `content` | string | No\* | Markdown to ground. Alone, stored as a new document. **With `content_id`, replaces that document's entire body** — pass the full document, never a fragment |
| `title` | string | No | Only meaningful with `content`. Omit and the title is taken from the first line |

\* One of `content_id` or `content` is required.

**Output:** the grounding envelope — see [Result envelope](#result-envelope) below.

**Errors:**
- **Provide either 'content_id' or 'content'** (400) — neither was supplied.
- **Not a valid UUID** (400) — malformed `content_id`.
- **Content not found** (404) — no such document in your team.
- **ci_not_eligible** (403) — the team is not on the Command plan, has no active subscription, or is out of AI credits.

**Example prompts:**
- "Ground this draft against our context library"
- "Does this blog post contradict anything we've published?"
- "Rewrite the pricing section and re-check it"

---

### `get_grounding_result`

Read the result of a grounding scan. The poll companion to `check_content_grounding`. It never starts a scan and never charges credits.

**When to use:** `check_content_grounding` returned `running`, or you want to re-read a document's last grounding result without paying for a new scan.

**Which id to pass — this matters:**

- **`scan_id`** — reads that exact scan, whatever its status. **This is what you want when polling**: it always reports the run you started.
- **`content_id`** (no `scan_id`) — reads the latest **completed** grounding for that document. Good for "what's this document's grounding state right now". It deliberately **skips a scan that is still running**, so it is the wrong call for polling: you would get the *previous* result back marked `complete`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `scan_id` | string (uuid) | No\* | The scan to read. Use this when polling |
| `content_id` | string (uuid) | No\* | Read the latest completed grounding for this document |

\* One of `scan_id` or `content_id` is required.

**Output:** identical to `check_content_grounding` — the same handling works for both.

**Errors:**
- **Provide 'scan_id' or 'content_id'** (400) — neither was supplied.
- **Scan not found** (404) — no such grounding scan in your team.
- **scan_id and content_id refer to different content** (400) — pass `scan_id` alone.

**Example prompts:**
- "Is that check done yet?"
- "What did the last grounding pass find on this doc?"

---

### `apply_grounding_fix`

Apply Marcora's recommended fix for one or more findings — "yes, do recommendation `<id>`".

**When to use:** the user has reviewed findings (from `check_content_grounding`, `get_grounding_result`, or `list_ci_findings`) and wants them acted on. **Read the finding's `suggested_fix` and confirm with the user first** — this writes to their library.

You never compose the fix yourself. Every finding already stores its recommended update, so applying is purely a reference by `finding_id`. This is the same action as the Apply button in the Marcora app: same permissions, same billing, same result.

**Works on both finding families** — content-grounding findings and Context Intelligence health-audit recommendations.

**Where each fix lands:** by default the context item named in that finding's `context_item_id`. A `null` `context_item_id` means the fix targets the document itself. Pass `context_item_overrides` to send a specific fix somewhere else.

**Asynchronous.** Returns immediately with one job per finding. To follow one to completion, poll `get_generation_status` with its `generation_id` — a **UUID** (the response hands you the UUID poll key `get_generation_status` expects). The honest outcome is the **`document_updated`** field on that response's `content` object: `true` means the document was actually changed, `false` means the recommendation was already covered and nothing was written. Report that distinction rather than assuming every applied fix changed something.

**Partial success is normal:** findings that could not be started come back in `errors[]` with a reason while the rest still run. Check **both** `jobs[]` and `errors[]`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `finding_ids` | array of uuid | Yes | The findings to apply. One or many |
| `context_item_overrides` | object | No | Map of `finding_id` → `context_item_id` to redirect specific fixes. Every key must also appear in `finding_ids` |

**Output:**

| Field | Type | Description |
|---|---|---|
| `requested` | integer | How many findings were submitted |
| `queued` | integer | How many runs actually started |
| `skipped` | integer | How many could not start — see `errors[]` |
| `jobs` | array | Per finding: `finding_id`, `status`, `generation_id` (uuid — poll `get_generation_status` with it), `document_uuid`, `context_item_id` |
| `errors` | array | Per finding: `finding_id`, `error` |

**Errors:**
- **Missing param: finding_ids** (400) — pass `finding_id` values from a prior findings response.
- **finding_ids must be finding_id UUIDs** (400).
- **context_item_overrides names a finding not in finding_ids** (400) — the override would be ignored, so it is rejected rather than silently dropped.
- **You are not authorized to perform this action** (403) — applying requires an admin or editor role.
- Per-finding failures (already resolved, not a grounding finding) arrive in `errors[]`, not as a thrown error.

**Example prompts:**
- "Fix the pricing conflict it found"
- "Apply all three of those recommendations"
- "Add that gap to our positioning doc instead"

---

### Result envelope

`check_content_grounding` and `get_grounding_result` return the same shape:

| Field | Type | Description |
|---|---|---|
| `content_id` | string (uuid) | The document that was scanned |
| `scan_id` | string (uuid) \| null | The scan run. Poll with this |
| `status` | string | `running`, `complete`, `failed`, or `none` |
| `link_url` | string | Opens the document with its grounding panel open — hand this to the user |
| `summary` | object | `supported`, `conflicts`, `gaps`, `total_claims`, plus `corpus_freshness` |
| `findings` | array | See below |
| `claims` | array | Each extracted claim: `claim_text`, `subject`, `value`, `bucket` (`supported`/`conflict`/`gap`), `refs[]`, `confidence` (a **string**) |
| `corpus_items` | array | The context items the scan was checked against: `context_item_id`, `name`, `source`, `content_category`, `link_url` |
| `details_visible` | boolean | `false` when you are not the document's creator — you get counts only |

Each entry in `findings[]`:

| Field | Type | Description |
|---|---|---|
| `finding_id` | string (uuid) | Pass to `apply_grounding_fix` |
| `type` | string | `conflict` or `gap` |
| `subject` | string \| null | What the finding is about |
| `statement` | string \| null | What the document says versus what the library says |
| `recommendation` | string \| null | What Marcora suggests doing |
| `severity` | string \| null | How serious |
| `status` | string \| null | `pending`, `acknowledged`, `dismissed`, `resolved` |
| `suggested_fix` | object \| null | The **full** recommended update — review this before applying |
| `context_item_id` | string (uuid) \| null | Where applying would write. `null` = the document itself |
| `link_url` | string \| null | Opens the finding |

---

## Reference

### `list_content_categories`

Returns all content categories available to your team. Categories organize blueprints and content by type (e.g. GTM Strategy, Product Launch, etc).

**Parameters:** None

**Output:** An object with a single `categories` key holding an array of categories, each with `id` and `name`. Use the `id` as `category_id` when creating blueprints or content.

**Example prompts:**
- "What content categories do I have?"
- "Show me the available content types"

---

### `list_targeting_dimensions`

Returns targeting dimensions and their options for the current team. Dimensions are categories (e.g. Buying Stage, Persona) with selectable options used to target content generation.

**Parameters:** None

**Output:** An object with a single `dimensions` key holding an array of dimensions. Each dimension has `id`, `name`, and an `options` array (each option `{ id, name }`). Pass option `id`s as `dimension_option_ids` to `create_content` to target generation.

**Example prompts:**
- "What targeting dimensions are available?"
- "Show me the persona options"

---

## Blueprints

### `list_blueprints`

Get all blueprints in your team's library as a flat list. Each blueprint includes its content category and a web URL.

**Parameters:** None

**Output:** An object with a single `blueprints` key holding a flat array of blueprints. Each item:

| Field | Type | Description |
|---|---|---|
| `blueprint_uuid` | string (uuid) | Unique identifier — pass as `blueprint_uuid` to `create_content` |
| `name` | string | Blueprint name |
| `input_instructions` | string | Guidance on what context to provide when generating from this blueprint |
| `team_visibility` | string | Visibility within your team (e.g. `team`, `private`) |
| `exchange_visibility` | string | Community exchange visibility (e.g. `public`, `none`) |
| `content_count` | integer | Number of content items generated from this blueprint |
| `created_at` | integer | Unix timestamp of creation |
| `category` | object | Content category — `{ id, name }`, matches `list_content_categories` |
| `web_url` | string | Direct URL to view this blueprint in Marcora |

**Example prompts:**
- "Show me my blueprints"
- "What templates do I have?"
- "List all my content blueprints"

---

### `get_blueprint`

Retrieve the full details of a specific blueprint by its UUID, including content, AI-generated analysis, and metadata.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `blueprint_uuid` | string | Yes | UUID of the blueprint to retrieve |

**Output:**

| Field | Type | Description |
|---|---|---|
| `name` | string | Blueprint name |
| `summary` | string | AI-generated summary |
| `blueprint_uuid` | string | Unique identifier |
| `source_content` | string | Original template content |
| `reference_content` | string | AI-polished reference version |
| `blueprint_dna` | string | AI-generated analysis of structure, tone, and sections |
| `input_instructions` | string | AI-generated guidance for what context to provide |
| `category` | object/null | Content category |
| `team_visibility` | string | Visibility within your team |
| `exchange_visibility` | string | Community exchange visibility |
| `web_url` | string | Direct URL to view in Marcora |
| `created_at` | integer | Unix timestamp of creation |

**Example prompts:**
- "Show me the details of my blog post blueprint"
- "What does the product launch blueprint look like?"

---

### `create_blueprint`

Create a reusable blueprint template for generating content at scale. Blueprints define the structure and AI instructions for a document type. Takes 1–3 minutes to return.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Blueprint name |
| `category_id` | integer | Yes | Category ID from `list_content_categories` |
| `source_content` | string | Yes | Well-structured markdown template content |

**Output:**

| Field | Type | Description |
|---|---|---|
| `name` | string | Blueprint name |
| `summary` | string | AI-generated summary of what this blueprint produces |
| `blueprint_uuid` | string | Unique identifier for use with `create_content` |
| `blueprint_dna` | string | AI-generated analysis of the template structure |
| `source_content` | string | The original template content |
| `reference_content` | string | AI-polished reference version |
| `input_instructions` | string | Guidance for what context to provide when generating |
| `category` | object | Content category |
| `link_url` | string | Direct link to view in Marcora |
| `team_visibility` | string | Team visibility setting |
| `created_at` | integer | Unix timestamp of creation |

**Example prompts:**
- "Create a blueprint for case studies"
- "Build me a template for product launch announcements"

**Common errors:**
- Invalid `category_id` — use `list_content_categories` first to get valid IDs
- Empty `source_content` — provide a well-structured markdown template

---

### `create_blueprint_draft`

Create an AI-assisted blueprint draft from a prompt. This creates a draft you can review before saving as a full blueprint — it does not create content directly.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Name for the draft |
| `instructions` | string | Yes | Description of the blueprint to create |
| `content` | string | Yes | Initial content as markdown |
| `category_id` | integer | No | Category ID from `list_content_categories` |

**Output:**

| Field | Type | Description |
|---|---|---|
| `id` | integer | Record ID for the blueprint draft |
| `uuid` | string | Unique identifier for this draft — pass as `draft_uuid` to `finalize_blueprint_draft` |
| `title` | string | Blueprint draft name |
| `content` | string | AI-generated blueprint template content in markdown |
| `link_url` | string | Direct URL to view/edit in Marcora |

**Example prompts:**
- "Draft a blueprint for weekly newsletters"
- "Help me create a template for competitor battle cards"

---

### `finalize_blueprint_draft`

Finalize (publish) a previously created blueprint draft into a full, usable blueprint. This is the final step in the draft workflow: `create_blueprint_draft` → review → `finalize_blueprint_draft`. Takes 1–3 minutes.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `draft_uuid` | string | Yes | The UUID of the blueprint draft to finalize (from `create_blueprint_draft`) |
| `name` | string | No | Optional name override |
| `category_id` | integer | No | Optional category ID override |

**Output:**

| Field | Type | Description |
|---|---|---|
| `name` | string | Blueprint name |
| `summary` | string | AI-generated summary |
| `blueprint_uuid` | string | Unique identifier for use with `create_content` |
| `blueprint_dna` | string | AI-generated analysis |
| `source_content` | string | Template content from the finalized draft |
| `reference_content` | string | AI-polished reference version |
| `input_instructions` | string | Guidance for users on what context to provide |
| `category` | object | Content category |
| `link_url` | string | Direct link in Marcora |
| `team_visibility` | string | Team visibility setting |
| `created_at` | integer | Unix timestamp of creation |

**Example prompts:**
- "Finalize my newsletter blueprint draft"
- "Publish the draft blueprint I just created"

---

## Community Blueprints

### `list_community_blueprints`

Browse community blueprints available for import. Returns blueprints shared by Marcora users, including name, summary, contributor info, and category.

**Parameters:** None

**Output:** An object with a single `community_blueprints` key holding an array of community blueprints. Each item carries `id`, `slug`, `name`, `summary`, `is_featured`, `input_instructions`, `visibility`, `contributor_name`, `contributor_company`, `category`, and `category_short`.

**Example prompts:**
- "Show me community blueprints"
- "What templates has the community shared?"
- "Browse blueprints from other users"

---

### `get_community_blueprint_details`

Get the full details for a specific community blueprint, including complete content, style guide, and contributor information.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `blueprint_exchange_id` | string | No | Blueprint exchange ID from `list_community_blueprints` |

**Output:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Blueprint exchange ID |
| `name` | string | Blueprint name |
| `slug` | string | URL slug |
| `content` | string | Full example document content in markdown |
| `summary` | string | Blueprint summary |
| `content_description` | string | Template structure and style guidelines |
| `input_instructions` | string | What context to provide when generating |
| `contributor_name` | string | Author name |
| `contributor_company` | string | Author company |
| `contributor_job_title` | string | Author job title |
| `suggested_content_type` | string | Recommended content category |
| `is_featured` | boolean | Whether the blueprint is featured |
| `visibility` | string | Visibility setting |

**Example prompts:**
- "Show me the details of that case study blueprint"
- "What does the community blog post template look like?"

---

### `import_community_blueprint`

Import a blueprint from the Marcora community exchange into your team's library. Once imported, use it like any of your own blueprints to generate content.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `blueprint_exchange_id` | string | No | Blueprint exchange ID from `list_community_blueprints` |

**Output:**

| Field | Type | Description |
|---|---|---|
| `id` | integer | Blueprint record ID |
| `name` | string | Blueprint name |
| `uuid` | string | Unique identifier for use with `create_content` |
| `content` | string | Blueprint content |
| `team_visibility` | string | Team visibility setting |
| `imported_exchange_id` | string | Original exchange ID |
| `created_at` | integer | Unix timestamp of creation |

**Example prompts:**
- "Import that community case study blueprint"
- "Add the blog post template to my library"

---

## Content

### `create_content`

Create content by supplying your own text directly, generating from an AI prompt, or generating from a blueprint.

> **Revising an existing document? Use `update_content` instead** — edit it in place rather than forking a new doc. Edits are non-destructive: Marcora keeps a version history and the user can revert from the app.

You must provide either `content` or `instructions` (not both).

- **With `content`** (synchronous): Saves your supplied text directly as a document — no AI generation. Returns immediately.
- **With `instructions`** (synchronous): Creates a freeform document from an AI prompt. Takes 1–3 minutes.
- **With `instructions` + `blueprint_uuid`** (asynchronous): Generates content from a blueprint template. Returns a `generation_id` to poll via `get_generation_status`. Takes 3–5 minutes.

> **Context handling depends on which input you use.** With **`instructions`** (Marcora writes it), the tool pulls all relevant context internally — Brand Foundation + Reference Library (relevancy-scored) + Project Context (if `project_id`) + any `collection_ids` — so do **not** pre-fetch with `get_relevant_context`; that's wasted work. With **`content`** (you supply finished text), the tool stores your markdown **verbatim** and consults **no** context. So if you're composing the content yourself, call `get_relevant_context` with `include_brand_foundation: true` **first** and write from what it returns — otherwise your draft ignores the team's brand and reference material. Rule of thumb: to have Marcora write against full team context automatically, use `instructions`; use `content` to save text the user already wrote/approved, or when the user wants *you* to do the writing (fetch context first).

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `content` | string | No* | Your own text to save directly as a document. Cannot be used with `blueprint_uuid` |
| `instructions` | string | No* | Detailed instructions describing what to create (AI will generate it) |
| `blueprint_uuid` | string | No | Blueprint UUID to generate from. Makes the call async. Only works with `instructions` |
| `plan_id` | string (uuid) | No | Plan UUID from `create_plan`, `list_plans`, or `get_plan` (use `plan_uuid`, not the integer id). Associates the new content with the plan and triggers an automatic stage transition to `In_Process`. Auto-linking only applies when used with `blueprint_uuid`. Do not pass if the plan is in `Complete` stage — call `update_plan` with `target_stage=Accepted` first |
| `project_id` | string | No | Project to associate this content with |
| `category_id` | integer | No | Content category ID |
| `collection_ids` | array | No | Context collection IDs to include |
| `dimension_option_ids` | array | No | Targeting dimension option IDs |
| `use_extended_thinking` | boolean | No | Enable extended thinking for complex content (sync mode only, with `instructions`) |

\* You must provide either `content` or `instructions`, but not both.

**Output (without blueprint — synchronous):**

| Field | Type | Description |
|---|---|---|
| `id` | integer | Content record ID |
| `title` | string | Document title |
| `content` | string | Document content in markdown |
| `content_id` | string | Unique identifier for use with `get_content` and share tools |
| `link_url` | string | Direct URL to view in Marcora |
| `created_at` | integer | Unix timestamp of creation |

**Output (with blueprint — asynchronous):**

| Field | Type | Description |
|---|---|---|
| `generation_id` | string (uuid) | ID to track async generation — pass to `get_generation_status` |

**Example prompts:**
- "Save this document to Marcora" (with `content`)
- "Write a blog post about our new product launch" (with `instructions`)
- "Generate a case study using my case study blueprint" (with `instructions` + `blueprint_uuid`)
- "Create content from my newsletter blueprint for the enterprise persona"

**Common errors:**
- Providing both `content` and `instructions` — use one or the other
- Using `content` with `blueprint_uuid` — blueprints require `instructions`
- Invalid `blueprint_uuid` — use `list_blueprints` to find valid UUIDs
- Timeout on synchronous calls — AI-generated content can take 1–3 minutes, which is normal

---

### `get_generation_status`

Poll the status of an async generation by `generation_id`. Two tools produce a `generation_id` you can check here:
- `create_content` with a `blueprint_uuid` (blueprint document generation)
- `ask_content_assistant` (the in-document Content Assistant)

The response always includes `status`, `generation_id`, and `flow_type`. `content` is `null` until the run finishes.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `generation_id` | string (uuid) | Yes | The generation ID returned by `create_content` (with `blueprint_uuid`) or `ask_content_assistant` |

**Output:**

| Field | Type | Description |
|---|---|---|
| `generation_id` | string (uuid) | The generation ID being checked |
| `status` | string | Status of this run. Blueprint flow terminates at `completed`; Content Assistant flow terminates at `complete`; `failed` on error. Intermediate values: `pending`, `processing`, `streaming` |
| `flow_type` | string | `ai_assistant` for `ask_content_assistant` runs, otherwise a blueprint/content generation |
| `content` | object \| null | `null` until the run completes. Shape depends on `flow_type` (below) |

**`content` — blueprint flow** (`flow_type` ≠ `ai_assistant`):

| Field | Type | Description |
|---|---|---|
| `content_id` | string (uuid) | The generated document's ID. Pass to `get_content` if you need the body |
| `name` | string | Document name |
| `blueprint_id` | integer | Blueprint used to generate |
| `link_url` | string | Direct URL to view/open in Marcora |

**`content` — Content Assistant flow** (`flow_type` = `ai_assistant`):

> `status` is per-run, but `content` is the **current** state: the live document (which may include edits the user made themselves afterward) plus the **most recent** Content Assistant interaction on that document. It is intentionally not a frozen snapshot of this specific generation — a stale snapshot isn't useful, the current version is.

| Field | Type | Description |
|---|---|---|
| `content_id` | string (uuid) | The content document the assistant acted on |
| `name` | string \| null | Document name |
| `assistant_summary` | string \| null | The most recent assistant reply shown in the document's sidebar thread |
| `document_updated` | boolean | Whether the most recent interaction changed the document body (false for a reply-only / chat-only response) |
| `current_content` | string \| null | The document's current markdown |
| `link_url` | string | Direct URL to view/open in Marcora |

**Example prompts:**
- "Check on my content generation"
- "Is my blog post done yet?"
- "Did the assistant finish editing my document?"

---

### `list_content`

Returns all content visible to the current user as a single unified array. Content created from scratch and from blueprints are merged with consistent field names. The same `content_id` can be passed to `get_content`, `update_content`, and `create_external_share`.

**Semantic search:** pass a natural-language `search` query to rank results by semantic relevance instead of recency; each row then carries a `relevance_score` (cosine `0`–`1`, higher = more relevant). Omit or leave `search` empty for the normal recency-ordered list. The scores are **cross-comparable with `list_context_items`** — call both tools with the same `search` query, merge the two arrays, and take the top matches by `relevance_score`, then present them to the user for confirmation before fetching full text with `get_content` / `get_context_item`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `search` | string | No | Optional natural-language query. When provided, results are ranked by semantic relevance to it (instead of recency) and each row gains a `relevance_score`. Omit or leave empty for the normal recency-ordered list. Scores are cross-comparable with `list_context_items` |

**Output:** An object with a single `content` key holding an array of items.

| Field | Type | Description |
|---|---|---|
| `name` | string | Content name |
| `content_id` | string (uuid) | Content identifier |
| `visibility` | string | `private` or `team` |
| `stage` | string | `in_progress` or `ready` |
| `category` | object \| null | `{id, name}` or null if uncategorized |
| `created_by` | string | Name of the creator |
| `projects` | string[] | Project names this content belongs to |
| `web_url` | string | Direct URL to view this content in Marcora |
| `relevance_score` | number | Present only when a `search` query is supplied. Cosine similarity (`0`–`1`, higher = more relevant) of the row to the query. Cross-comparable with the `relevance_score` returned by `list_context_items` |

**Example prompts:**
- "Show me all my content"
- "List my documents"
- "What content have I created?"

---

### `get_content`

Retrieves the full content of a specific document by its `content_id` (UUID).

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `content_id` | string | Yes | The UUID of the content to retrieve |

**Output:**

| Field | Type | Description |
|---|---|---|
| `name` | string | Content name |
| `content` | string | Full document content in markdown format |
| `content_id` | string | Content identifier |
| `stage` | string | `in_progress` or `ready` |
| `category` | object/null | Content category, or null if not categorized |
| `visibility` | string | Visibility setting (e.g. `private`, `team`) |
| `link_url` | string | Direct URL to view in Marcora |

**Example prompts:**
- "Show me the full content of that blog post"
- "Read my latest case study"

---

### `update_content`

Update a content document by `content_id`. Partial-update semantics — every field besides `content_id` is optional and only the fields you supply are changed; everything else is left untouched. At least one mutable field must be supplied.

> **Use this to revise an existing document — edit it in place; don't create a new one.** Edits are safe: Marcora keeps a full version history and the user can revert any change from the app.

> **Ground the body before you write it:** the `content` you send REPLACES the entire body verbatim (there is no patch / diff mode), and this tool consults **no** Brand Foundation or Reference Library of its own. So whenever you author or rewrite the body yourself, fetch context first: call `get_content` to read the current body, AND call `get_relevant_context` with `include_brand_foundation: true` to pull the team's brand voice and reference material; then compose the FULL new body from both and send it back. Body content written without fetching context first will be off-brand. (No fetch needed when you're only changing non-body fields — `stage`, `visibility`, `category_id`, `project_id`, or `name_override`.)

> **Name behavior:** by default a document's name auto-syncs from the first markdown header in its body. Set `name_override` to lock a custom name; once locked, the title stays even when the body is edited. There is no un-lock path in this tool.

> **Stage:** writing `stage` also keeps the internal `is_ready` bool in sync. For documents linked to a content plan, transitioning to `ready` moves the plan to `Complete` as a side-effect (non-blocking on failure).

> **Project association:** pass `project_id` to set the document's project. If the document is already in a different project the old association is replaced; if already in the supplied project this is a no-op. Omit `project_id` to leave projects untouched. There's no way to remove a doc from all projects via this tool — use the Marcora app for that.

> **Change summary:** pass `change_summary` — what you changed and why — shown in the document's AI-assistant history sidebar for a human to skim, so **write it as skimmable markdown**: a single line for one small edit (e.g. "Tightened the closing CTA"); for several distinct edits, a short **bulleted list** where each bullet is a bold 2–5 word lead, a colon, then the detail. Match length to substance — don't pad. Recommended on every call; blank/omitted falls back to a generic "Content updated via MCP." label. Only recorded when the call also changes the body (`content`).

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `content_id` | string (uuid) | Yes | UUID of the content to update. From `list_content`, `get_content`, `get_generation_status`, or `get_project` |
| `content` | string | No | New full markdown body. Omit to leave body unchanged |
| `name_override` | string | No | Custom document name. Setting this locks the name (won't auto-resync from content header on future edits) |
| `stage` | string | No | `in_progress` or `ready` |
| `visibility` | string | No | `private` or `team` |
| `category_id` | integer | No | Category ID from `list_content_categories` |
| `project_id` | string (uuid) | No | Project UUID to associate with this content. Replaces any existing project association |
| `change_summary` | string | No | What changed and why, shown in the document's AI-assistant history. Format as skimmable markdown — a bulleted list (bold lead + detail) for multi-part edits. Recommended on every call; blank/omitted falls back to a generic label. Only recorded when `content` also changes |

**Output:**

| Field | Type | Description |
|---|---|---|
| `content_id` | string (uuid) | Content identifier |
| `name` | string | Document name (post-update) |
| `content` | string | Full document content in markdown |
| `visibility` | string | `private` or `team` |
| `stage` | string | `in_progress` or `ready` |
| `category` | object \| null | `{id, name}` or null if uncategorized |
| `link_url` | string | Direct URL to view this content in Marcora |

**Errors:**
- `notfound` — `content_id` doesn't match any content document
- `inputerror` — no mutable field supplied; invalid `category_id`; invalid `project_id`; or the document is a non-editable document type (e.g. a context-item editor document, which is managed by a separate sync flow)
- `accessdenied` — you don't have write access to the document

**Example prompts:**
- "Mark my latest case study as ready"
- "Add this doc to the Q4 GTM project"
- "Rename this document to 'Acme Pricing One-Pager'"
- "Replace the body of my pricing one-pager with the markdown above"

---

### `ask_content_assistant`

Send a natural-language request to Marcora's in-document **Content Assistant** for an existing content document. The request can ask for an edit ("add an intro paragraph", "tighten paragraph two"), an extension, or pure ideation / a question ("give me three headline ideas") — the assistant decides whether to change the document or just reply.

> This is the in-editor Content Assistant that operates on one specific document — not the general Marcora Agent.

**Asynchronous.** Returns a `generation_id` (UUID) immediately and does the model work in the background. When the user has the document open in Marcora, the assistant's reply and any edits stream live into the document's AI Assistant sidebar via a realtime channel — they don't need to poll. Headless callers (or anyone wanting the result text) poll `get_generation_status` with the returned `generation_id`.

**Behavior:**
- The assistant only rewrites the document body when it decides the request warrants a change; otherwise it just replies in the sidebar thread.
- `chat_only_mode: true` forces a reply-only response with no document changes.
- The current document body and the prior sidebar conversation are loaded automatically; pass `collection_ids` and/or `project_id` to fold in extra context.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `content_id` | string (uuid) | Yes | The content document to act on (from `list_content`, `get_content`, or `get_project`) |
| `prompt` | string | Yes | The request, in natural language |
| `selected_text` | string | No | Text the user has highlighted in the document, to focus the request on |
| `thinking_mode` | boolean | No | Enable extended reasoning for harder requests |
| `chat_only_mode` | boolean | No | Force a reply-only response with no document edit |
| `ai_provider` | string | No | Model family: `anthropic` (default) or `openai` |
| `collection_ids` | array | No | Context Collection IDs (from `list_context_collections`) to include |
| `project_id` | string (uuid) | No | Project UUID (from `list_projects`) whose context to include |

**Output:**

| Field | Type | Description |
|---|---|---|
| `generation_id` | string (uuid) | Identifies this run. Poll `get_generation_status` with it for the result |
| `status` | string | Always `pending` on dispatch |

**Example prompts:**
- "Add a short intro paragraph to this document"
- "Give me three alternative headlines for this draft" (reply-only)
- "Tighten the second paragraph and fix the tone"

**Errors:**
- `notfound` — `content_id` matches no content document

---

## Sharing & Export

### `create_external_share`

Creates a public share link for content, with optional expiration. Accessible publicly without a Marcora account.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `content_id` | string | Yes | The ID of the content to share |
| `expires_at` | integer | No | Unix timestamp for link expiration |

**Output:**

| Field | Type | Description |
|---|---|---|
| `share_link` | string | Public URL anyone can use to view the content |

**Example prompts:**
- "Create a share link for my latest blog post"
- "Share this document with an expiration in 7 days"

---

### `convert_markdown_to_word_doc`

Export a markdown document as a downloadable Word (.docx) file. Returns a download URL.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `markdown_content` | string | Yes | Markdown content to convert |
| `filename` | string | No | Filename without extension |
| `document_url` | string | No | URL to embed as footer link to original document |

**Output:**

| Field | Type | Description |
|---|---|---|
| `filename` | string | Filename of the generated Word document |
| `download_url` | string | URL to download the generated .docx file |

**Example prompts:**
- "Export my blog post as a Word doc"
- "Convert this to a .docx file"
- "Download my case study as Word"

---

## Projects

### `list_projects`

Returns all projects visible to the current user. Projects organize content into workstreams.

**Parameters:** None

**Output:** An object with a single `projects` key holding an array of projects. Each item:

| Field | Type | Description |
|---|---|---|
| `id` | string (uuid) | Project ID. Pass to `get_project` or use when creating content |
| `name` | string | Project name |
| `link_url` | string (uri) | Direct URL to view this project in the Marcora app |
| `visibility` | string | Visibility setting (e.g. team, private) |
| `status` | string | Project status (e.g. active, archived) |
| `content_count` | integer | Number of content items in this project |
| `created_by` | string | Name of the project creator |
| `member_count` | integer | Number of project members |

**Example prompts:**
- "Show me my projects"
- "What projects do I have?"

---

### `get_project`

Returns details for a specific project including its members, documents, context items, and (when set) a top-level `project_brief` shortcut so the brief is directly addressable for follow-up edits via `update_content`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `project_id` | string | Yes | Project UUID from `list_projects` |

**Output:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Project ID |
| `name` | string | Project name |
| `status` | string | Project status |
| `visibility` | string | Visibility setting |
| `members` | array | Project members |
| `documents` | array | Documents in this project |
| `project_brief` | object \| null | The project's pinned brief document, if set. `{name, content_id}` — same shape as `create_project`'s `project_brief` field. Pass `content_id` to `update_content` / `get_content` to edit or read the brief. `null` if the project has no brief set |
| `context_items` | array | Context items associated with this project |
| `created_at` | integer | Unix timestamp of creation |

**Example prompts:**
- "Show me the details of my product launch project"
- "What documents are in this project?"
- "Open the brief for the Acme project so I can edit it"

---

### `create_project`

Create a new project for organizing content and context into a workstream. Optionally generates a project brief document in the same call.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Project name |
| `visibility` | string | No | `team` or `private`. Defaults to `team` |
| `project_brief_details` | string | No | If supplied, an AI-generated project brief is created and attached to the project. The brief's `content_id` is returned in the response so it can be passed to `update_content` later for edits |

**Output:**

| Field | Type | Description |
|---|---|---|
| `project_id` | string (uuid) | Project identifier |
| `name` | string | Project name |
| `link_url` | string | Direct URL to view this project in Marcora |
| `project_brief` | object \| null | Present (non-null) only when `project_brief_details` was supplied. `{name, content_id}`. `content_id` is the brief document's UUID — pass it to `update_content` / `get_content` to edit or read the brief. `name` may be empty immediately after creation while AI generation is in flight |

**Example prompts:**
- "Create a project for our Q3 product launch"
- "Start a new project called 'Brand Refresh 2025'"
- "Create a project for our Acme deal with a brief covering the customer's stack and pain points"

---

### `update_project`

Update mutable fields on an existing project (name, visibility, status, project brief). Uses PATCH semantics — only fields you pass are changed; omit a field to leave it unchanged.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `project_id` | string (uuid) | Yes | UUID of the project to update. Get from `list_projects` or `get_project`. |
| `name` | string | No | New project name. Must be non-empty when provided. |
| `visibility` | string | No | New visibility setting. `team` makes it visible to all team members; `private` restricts to the creator and explicit project members. |
| `status` | string | No | New project status. `active` for ongoing work; `archived` to hide from the active list while preserving content. Setting to `active` requires available active-project usage. |
| `project_brief_id` | string (uuid) | No | UUID of an existing content item to set as this project's brief. If the content isn't already attached to the project, this tool will attach it AND set it as the brief in one call. |

**Output:**

| Field | Type | Description |
|---|---|---|
| `success` | boolean | True if the update applied successfully |
| `message` | string | Human-readable status message |
| `project` | object \| null | The updated project record |

**Example prompts:**
- "Set the brief on the Acme Launch project to this content"
- "Rename this project to 'Q4 GTM'"
- "Make this project private"
- "Archive the Brand Refresh project"

---

## Plans & Playbooks

Plans are units of content intent — a titled, assignable record that captures what content needs to be created, when, and with what context. Use plans to queue content work, track progress through stages, produce the content a plan describes (`produce_plan`), and link produced content back to the originating plan. **Playbooks** are reusable, ordered templates of plan items you can stamp out as a batch (`instantiate_playbook`).

**Stage lifecycle:** `Suggested` → `Accepted` → `In_Process` → `Complete` (or `Dismissed` from any stage except `Dismissed`). There is no delete tool — dismiss a plan with `update_plan` `target_stage: "Dismissed"`.

**Visibility:** plans are `private` (creator-only) by default; assigning to another team member auto-promotes to `team`. Playbooks default to `team`, and `instantiate_playbook` inherits the playbook's visibility onto the plans it creates.

---

### `list_plans`

Returns a paginated list of plans visible to the authenticated user. Use filters to narrow by stage, source, project, or category.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `stage` | string[] | No | Filter by stage. Use UNDERSCORE form (e.g. `In_Process`). Allowed: `Suggested`, `Accepted`, `In_Process`, `Complete`, `Dismissed`. Only the first element is honored currently |
| `source` | string[] | No | Filter by source. Allowed: `user_added`, `cora_proactive`, `cora_requested`, `workflow`, `playbook`. Only the first element is honored currently |
| `project_id` | string | No | Filter to plans associated with this project UUID |
| `category_id` | integer | No | Filter to plans in this content category |
| `assignee_scope` | string | No | Whose plans to return: `me` (default), `created_by_me`, or `all_visible` |
| `due_before` | string | No | ISO date YYYY-MM-DD. Note: does not apply yet |
| `due_after` | string | No | ISO date YYYY-MM-DD. Note: does not apply yet |
| `search_text` | string | No | Substring match on plan title. Note: does not apply yet |
| `sort` | string | No | `due_asc_nulls_last` (default) or `created_desc` |
| `page` | integer | No | Page number (default 1) |
| `per_page` | integer | No | Items per page (default 20, max 100) |

**Output:**

| Field | Type | Description |
|---|---|---|
| `items` | array | Array of plan objects |
| `items[].plan_uuid` | string (uuid) | Plan UUID — use this (not integer id) with `get_plan`, `update_plan`, and `create_content` |
| `items[].title` | string | Plan title |
| `items[].stage` | string | Current stage |
| `items[].source` | string | How the plan was created |
| `items[].assigned_to` | integer | User ID of assignee |
| `items[].created_by` | integer | User ID of creator |
| `items[].due_date` | string | Due date (YYYY-MM-DD), or null |
| `items[].produced_content_id` | string | UUID of linked content item, or null |
| `items[].created_at` | string | ISO timestamp |
| `items[].updated_at` | string | ISO timestamp |
| `itemsTotal` | integer | Total number of matching plans |
| `curPage` | integer | Current page |
| `nextPage` | integer/null | Next page number, or null if last page |
| `prevPage` | integer/null | Previous page number, or null if first page |

**Example prompts:**
- "Show me my pending plans"
- "List all Accepted plans assigned to me"
- "What plans are in progress?"

---

### `get_plan`

Fetch a single plan by UUID with full details including linked references, context collections, targeting dimensions, and produced content.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `plan_uuid` | string (uuid) | Yes | UUID of the plan to fetch. Use `plan_uuid`, not the integer id |

**Output:**

| Field | Type | Description |
|---|---|---|
| `plan.plan_uuid` | string (uuid) | Plan UUID |
| `plan.id` | integer | Integer record ID (use `plan_uuid` for API calls) |
| `plan.title` | string | Plan title |
| `plan.description` | string | Free-text description |
| `plan.stage` | string | Current stage |
| `plan.source` | string | How the plan was created (immutable) |
| `plan.prompt` | string | Content prompt pre-set for this plan |
| `plan.blueprint_id` | string | Blueprint UUID, or null |
| `plan.project_id` | string | Project UUID, or null |
| `plan.category_id` | integer | Content category ID, or null |
| `plan.due_date` | string | Due date, or null |
| `plan.assigned_to` | integer | Assignee user ID |
| `plan.created_by` | integer | Creator user ID |
| `plan.team_id` | integer | Team ID |
| `plan.produced_content_id` | string | UUID of produced content, or null |
| `plan.reference_documents` | array | Content items attached as reference material |
| `plan.context_collections` | array | Context collections pre-attached to the plan |
| `plan.targeting_dimensions` | array | Targeting dimension options pre-attached |
| `plan._produced_content` | object/null | Full produced content object, or null |
| `plan._source_metadata_resolved` | object/null | Resolved source metadata, or null |

**Example prompts:**
- "Show me the details of that plan"
- "What references are attached to this plan?"

---

### `create_plan`

Create a new content plan in the authenticated user's active team.

**Starting stage by source:**
- `user_added`, `cora_requested`, `playbook` → starts at **Accepted**
- `cora_proactive` → starts at **Suggested**
- `workflow` → starts at **Suggested** (by default)

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `title` | string | Yes | One-line summary of the content intent (1-200 characters) |
| `description` | string | No | Free-text description |
| `due_date` | string | No | ISO date YYYY-MM-DD |
| `prompt` | string | No | Content prompt that pre-populates the creation form when the plan is acted on |
| `blueprint_id` | string (uuid) | No | UUID of the content blueprint/template |
| `project_id` | string (uuid) | No | Project UUID to associate with |
| `category_id` | integer | No | Content category ID (from `list_content_categories`) |
| `reference_document_ids` | uuid[] | No | Content UUIDs to associate as reference material |
| `context_collection_ids` | integer[] | No | Integer collection IDs to pre-attach (from `list_context_collections`) |
| `targeting_dimension_ids` | integer[] | No | Integer dimension option IDs to pre-attach (from `list_targeting_dimensions`) |
| `source` | string | No | `user_added`, `cora_proactive`, `cora_requested`, `workflow`, or `playbook`. Default: `cora_requested`. Immutable after creation |
| `source_metadata` | object | No | Contextual metadata (JSON). Immutable after creation |
| `assigned_to` | integer | No | Integer user ID. Defaults to creator. Must be a current team member |
| `plan_uuid` | string (uuid) | No | Client-supplied UUIDv4 for optimistic creates. Server generates if omitted |

**Output:** Full plan object (same fields as `get_plan`).

**Example prompts:**
- "Create a plan to write a case study about our Acme deal"
- "Add a content plan for a Q3 product launch blog post"

---

### `update_plan`

Partial update of a plan: mutable fields and stage transitions. All fields are optional — supply only what you want to change.

> **Array fields replace entirely:** `reference_document_ids`, `context_collection_ids`, and `targeting_dimension_ids` REPLACE the full set when provided. Pass `[]` to clear all.

> **Nullable fields:** Pass `null` to clear `blueprint_id`, `project_id`, `category_id`, and `due_date`.

**Stage transition rules:**
- `Suggested` → `Accepted` or `Dismissed`
- `Accepted` → `In_Process` or `Dismissed`
- `In_Process` → `Complete`, `Accepted`, or `Dismissed`
- `Complete` → `Accepted` or `Dismissed`
- `Dismissed` → terminal, no further transitions

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `plan_uuid` | string (uuid) | Yes | UUID of the plan to update |
| `title` | string | No | New title |
| `description` | string | No | New description |
| `prompt` | string | No | Updated content prompt |
| `blueprint_id` | string/null | No | Blueprint UUID. Pass `null` to clear |
| `project_id` | string/null | No | Project UUID. Pass `null` to clear |
| `category_id` | integer/null | No | Content category ID. Pass `null` to clear |
| `due_date` | string/null | No | ISO YYYY-MM-DD. Pass `null` to clear |
| `assigned_to` | integer | No | Integer user ID. Must be a current team member |
| `reference_document_ids` | string[] | No | REPLACES the full set of reference documents. Pass `[]` to clear all |
| `context_collection_ids` | integer[] | No | REPLACES the full set of context collections. Pass `[]` to clear all |
| `targeting_dimension_ids` | integer[] | No | REPLACES the full set of targeting dimensions. Pass `[]` to clear all |
| `target_stage` | string | No | Trigger a stage transition. Use UNDERSCORE form (e.g. `In_Process`). Allowed: `Suggested`, `Accepted`, `In_Process`, `Complete`, `Dismissed` |

**Output:** Updated plan object with all fields.

**Example prompts:**
- "Mark this plan as In Progress"
- "Assign this plan to the content team"
- "Set a due date of next Friday on this plan"
- "Dismiss the outdated Q2 plan"

---

### `produce_plan`

Produce (generate) the actual content a plan describes — the MCP equivalent of the **Generate** button on the plans board. The plan must be in the `Accepted` stage (transition a `Suggested` plan first with `update_plan` `target_stage: "Accepted"`). Consumes team AI credits and typically takes 1–2 minutes; confirm with the user before producing a plan they didn't explicitly ask to produce. The plan's `prompt`, targeting dimensions, context collections, and project association are used as generation inputs — set them via `update_plan` before producing.

**Both paths are asynchronous** — the call returns immediately with a `generation_id`; poll `get_generation_status`. On completion the backend links the produced content and moves the plan to `In_Process` (then `Complete` when the content reaches ready).

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `plan_uuid` | string (uuid) | Yes | UUID of the plan to produce. Must be in `Accepted` stage |

**Output:**

| Field | Type | Description |
|---|---|---|
| `path` | string | `blueprint` (plan has a blueprint) or `freeform` (no blueprint) |
| `generation_id` | string | Poll `get_generation_status` with this until complete |
| `plan_uuid` | string (uuid) | The plan being produced |

**Example prompts:**
- "Go ahead and produce that launch email plan"
- "Generate the content for this plan"

---

### `list_playbooks`

List all content playbooks visible to the caller in the current team (team-visible playbooks plus the caller's own private ones). Returns summaries only — call `get_playbook` for a playbook's items. Use before `instantiate_playbook` / `update_playbook` to find the right id.

**Parameters:** none.

**Output:** an array of playbook summary objects (`id`, `name`, `description`, `visibility`, `anchor_date`, `link_url`, item count, timestamps). Each object's `anchor_date` is the persisted `YYYY-MM-DD` reference date (or `null`), and `link_url` opens that playbook in the Marcora web app — surface it instead of the raw id.

**Example prompts:**
- "What playbooks do I have?"
- "Show my content templates"

---

### `get_playbook`

Fetch one content playbook by id, including its full ordered list of items.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `playbook_id` | integer | Yes | ID of the playbook to fetch |

**Output:** the playbook object — including its `anchor_date` (persisted `YYYY-MM-DD` reference date, or `null`) and `link_url` (opens the playbook in the Marcora web app) — with an ordered `items` array. Each item carries the plan fields it will stamp out (title, description, prompt, blueprint, category) plus an `offset_days` counted from the anchor date to compute each due date on instantiation.

**Example prompts:**
- "What's in my launch-week playbook?"

---

### `create_playbook`

Create a reusable content playbook — an ordered template of content-plan items ("save a repeatable content sequence"). Provide a name and, optionally, the ordered items; each item becomes one content plan when the playbook is instantiated. To build a playbook from plans you already ran, use `create_playbook_from_plans` instead.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Playbook name |
| `description` | string | No | Free-text description |
| `visibility` | string | No | `team` (default) or `private` |
| `anchor_date` | string | No | Optional `YYYY-MM-DD` reference date the playbook is built around (a launch, event, campaign kickoff). Persisted on the playbook; each item's `offset_days` counts from it, and it becomes the default anchor when instantiating. Leave off for an evergreen/undated template |
| `items` | array | No | Ordered playbook items (each becomes one plan on instantiation) |

**Output:** the created playbook object, including its persisted `anchor_date` (or `null`) and a `link_url` that opens the new playbook in the Marcora web app — share it with the user.

**Example prompts:**
- "Make me a launch-week playbook"
- "Save this sequence as a template"

---

### `create_playbook_from_plans`

Create a playbook by capturing existing content plans as reusable template items ("save what worked as a template"). Pass the plan UUIDs; their title / description / prompt / blueprint / category are copied into ordered playbook items.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `plan_ids` | uuid[] | Yes | Plan UUIDs to capture as ordered template items |
| `name` | string | No | Playbook name (derived if omitted) |
| `description` | string | No | Free-text description |
| `visibility` | string | No | `team` (default) or `private` |

**Output:** the created playbook object, including its `anchor_date` (`null` unless later set) and a `link_url` that opens the new playbook in the Marcora web app — share it with the user.

**Example prompts:**
- "Turn these plans into a playbook"
- "Save this campaign as a template"

---

### `update_playbook`

Edit a content playbook. Any playbook is fully editable. Pass only the fields to change: `name` and/or `description` patch in place. If `items` is provided it **fully replaces** the playbook's items and their order; omit `items` to leave them untouched. Changing `visibility` is creator-only.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `playbook_id` | integer | Yes | ID of the playbook to update |
| `name` | string | No | New name |
| `description` | string | No | New description (pass `null` to clear) |
| `visibility` | string | No | `team` or `private` (creator-only) |
| `anchor_date` | string | No | Set the playbook's `YYYY-MM-DD` reference date. Omit to keep the current value; pass `null` to clear it |
| `items` | array | No | If provided, REPLACES the full ordered item list |

**Output:** the updated playbook object, including its `anchor_date` (or `null`) and `link_url`.

**Example prompts:**
- "Add a follow-up email to my launch playbook"
- "Reorder these steps"

---

### `instantiate_playbook`

Run a playbook: create one content plan per playbook item, in order, as a batch. Plans land in the `Accepted` stage with source `playbook` and inherit the playbook's visibility. Optionally anchor due dates to a date (each item's `offset_days` is applied to `anchor_date`) and/or scope the batch to a project. This is a distinct bulk action — it does not create or edit the playbook itself.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `playbook_id` | integer | Yes | ID of the playbook to instantiate |
| `anchor_date` | string | No | ISO date YYYY-MM-DD. Each item's `offset_days` is added to it to compute that plan's due date |
| `project_id` | string (uuid) | No | Scope the created plans to this project |
| `assigned_to` | integer | No | Assign the created plans to this team member |
| `category_id` | integer | No | Apply this content category to the created plans |

If `anchor_date` is omitted, the playbook's persisted `anchor_date` (if any) is used.

**Output:** an object describing the run:

| Field | Type | Description |
|---|---|---|
| `playbook_id` | integer | The instantiated playbook |
| `run_id` | integer | ID of the cycle (run) this created — the group the plans belong to |
| `run` | object | The created cycle: `id`, `name` (auto-named `"<playbook> — <Mon YYYY>"` unless you passed a name), `anchor_date`, and `link_url` (`https://app.marcora.ai/runs/{run_id}`) — share it to hand the user their new cycle |
| `created_count` | integer | Number of plans created (one per playbook item) |
| `plans` | array | The created content plans (same shape as `create_plan` / `get_plan`), each with its own `link_url` (`https://app.marcora.ai/plans/{plan_uuid}`). Stage `Accepted`, source `playbook` |

**Example prompts:**
- "Run my launch playbook"
- "Instantiate this template anchored to next Monday"

---

## Workflows

Workflows are reusable, multi-step automations that a Managed Agents session executes on demand or on a schedule. Build them with `create_workflow`, activate and edit them with `update_workflow`, trigger them with `run_workflow`, and inspect run history with `get_workflow_runs`. The companion **`marcora-mcp`** skill documents authoring patterns (step design, scheduling, deduplication, runner-summary conventions) in its Workflows chapter.

### `list_workflows`

List workflows for your active team. Supports an optional status filter and a name substring search. Call this before `create_workflow` to check for duplicate names.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `status` | string | No | Filter by status: `draft`, `active`, or `archived`. Omit to return all |
| `search` | string | No | Substring match against workflow name |
| `page` | integer | No | Page number (default 1) |
| `per_page` | integer | No | Items per page (default 20, max 100) |

**Output:** A paginated object.

| Field | Type | Description |
|---|---|---|
| `items` | array | Array of workflow summaries |
| `items[].id` | string (uuid) | Workflow ID. Use as `workflow_id` in `get_workflow`, `update_workflow`, `run_workflow`, and `get_workflow_runs` |
| `items[].name` | string | Workflow name |
| `items[].status` | string | `draft`, `active`, or `archived` |
| `items[].link_url` | string (uri) | Direct URL to view the workflow in Marcora |
| `itemsTotal` | integer | Total number of matching workflows |
| `curPage` | integer | Current page |
| `nextPage` | integer/null | Next page number, or null if last page |
| `prevPage` | integer/null | Previous page number, or null if first page |

**Example prompts:**
- "What workflows do I have?"
- "List my active automations"
- "Do I already have a workflow named 'Weekly digest'?"

---

### `get_workflow`

Fetch one workflow's full definition plus its triggers and latest run. Always call this before `update_workflow` — partial updates clobber unspecified keys, so you need the current values first.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | string (uuid) | Yes | UUID of the workflow to fetch |

**Output:** An object with a single `workflow` key.

| Field | Type | Description |
|---|---|---|
| `workflow.id` | string (uuid) | Workflow ID |
| `workflow.name` | string | Workflow name |
| `workflow.status` | string | `draft`, `active`, or `archived` |
| `workflow.steps` | array | Ordered step definitions |
| `workflow.inputs` | object | Declared input schema |
| `workflow.allowed_tools` | array | Tool allowlist for the runner |
| `workflow._triggers` | array | Schedule/trigger configs (inspect `_triggers[0].schedule_config` and `.is_enabled`) |
| `workflow._latest_run` | object/null | Most recent run (carries its own `link_url`), or null if never run |
| `workflow.link_url` | string (uri) | Direct URL to view the workflow in Marcora |

**Example prompts:**
- "Show me the details of that workflow"
- "What's this workflow's schedule?"
- "When did this workflow last run?"

---

### `create_workflow`

Create a new workflow template for your active team. Workflows start as `draft` — activate them with `update_workflow` once the user confirms. Check `list_workflows` with a `search` filter for duplicate names first.

> **Scheduling:** include `schedule_config` ONLY if the user explicitly wants the workflow scheduled. Otherwise omit it and the workflow runs on demand via `run_workflow`.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Human-readable workflow name. Confirm with the user before creating |
| `description` | string | No | One or two sentences; becomes part of the runner's system prompt |
| `steps` | array | Yes | Ordered list of steps. Each should be specific enough that a fresh agent can execute it without follow-up questions |
| `inputs` | object | No | Declares what the workflow needs (e.g. `topic`, `date_range`); resolved from trigger bindings on scheduled runs |
| `allowed_tools` | array | **Yes** | **Required, non-empty.** The exact set of tools the workflow runner is permitted to use. A workflow cannot be created without an explicit allowlist — an empty list would let the runner inherit the full tool set. Prefer tight allowlists, especially for scheduled runs |
| `tags` | string[] | No | Optional tags |
| `schedule_config` | object | No | Scheduling config. Shape: `{ "frequency": "daily"\|"weekly"\|"hourly", "interval_hours": N, "timezone": "UTC" }`. Omit unless scheduling is requested |

**Output:** The created workflow object — `id`, `team_id`, `created_by_user_id`, `name`, `description`, `status` (`draft`), `inputs`, `steps`, `allowed_tools`, `tags`, `created_at`, `updated_at`, `link_url`. Use `id` as `workflow_id` in the other workflow tools.

**Example prompts:**
- "Create a workflow that drafts a weekly LinkedIn post from our latest content"
- "Set up an automation to import new call transcripts every Monday"

---

### `update_workflow`

Partial update of a workflow template — only the keys you send mutate; unspecified keys are preserved. Call `get_workflow` first to read the current values, then send the minimal diff.

> **Activate / soft-delete:** `{ workflow_id, status: "active" }` activates; `{ workflow_id, status: "archived" }` soft-deletes.

> **Do NOT send `schedule_config`** — it is rejected with an InputError on update. Schedule edits happen in the Marcora UI.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | string (uuid) | Yes | UUID of the workflow to update |
| `name` | string | No | New name |
| `description` | string | No | New description |
| `status` | string | No | `draft`, `active`, or `archived` (use `archived` as soft-delete) |
| `steps` | array | No | Replacement step definitions |
| `inputs` | object | No | Replacement input schema |
| `allowed_tools` | array | No | Replacement tool allowlist |
| `tags` | string[] | No | Replacement tags |

**Output:** The updated workflow object — `id`, `name`, `status`, `steps`, `inputs`, `allowed_tools`, `tags`, `updated_at`, `link_url`.

**Example prompts:**
- "Activate that workflow"
- "Archive the old digest workflow"
- "Rename this workflow to 'Q3 launch prep'"

---

### `run_workflow`

Manually run a workflow now. Creates a workflow run and dispatches a Managed Agents session. Inspect the returned `status` to know what happened.

> **Check `status`:** `running` → dispatch succeeded, a session is live; `failed` → dispatch failed, read `error_reason` for the cause; `skipped` → the runner decided no work was needed (rare for manual runs).

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | string (uuid) | Yes | UUID of the workflow to run |
| `input_values` | object | No | Object matching the workflow's declared `inputs` schema. Pass `{}` or omit for workflows with no inputs. Call `get_workflow` first if unsure |

**Output:** The workflow run object.

| Field | Type | Description |
|---|---|---|
| `id` | string (uuid) | Workflow run UUID. Use as `run_id` in `get_workflow_runs` (single mode) to inspect the run |
| `workflow_template_id` | string (uuid) | Parent workflow UUID |
| `status` | string | `running`, `failed`, or `skipped` |
| `trigger_type` | string | How the run was triggered (`manual` here) |
| `runner_session_id` | string | Managed Agents session ID for the run |
| `error_reason` | string/null | Failure cause when `status` is `failed`, else null |
| `error_summary` | string | Human-readable error summary |
| `link_url` | string (uri) | Direct URL to view this run in Marcora |

**Example prompts:**
- "Run the weekly digest workflow now"
- "Trigger that automation manually"

---

### `get_workflow_runs`

Inspect workflow run history. Two modes, controlled by whether `run_id` is supplied: omit it for a paginated list of runs; supply it for a single run's detail including step logs and tool-call logs.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | string (uuid) | Yes | UUID of the workflow |
| `run_id` | string (uuid) | No | If supplied → single-run detail; if omitted → paginated list of runs |
| `status` | string | No | List-mode filter (e.g. `failed`). Ignored in single mode |
| `page` | integer | No | List-mode page number (default 1) |
| `per_page` | integer | No | List-mode page size (default 20) |

**Output:** An object whose shape depends on the mode:

- **List mode** (`run_id` omitted): `items` — an array of runs, each `{ id, workflow_template_id, status, link_url }` — plus `itemsTotal` (integer).
- **Single-run mode** (`run_id` supplied): `id`, `workflow_template_id`, `status`, `_step_logs` (array), `_tool_call_logs` (array), and `link_url`.

**Example prompts:**
- "Did my workflow run?"
- "Show me the latest runs of this workflow"
- "What did that run do?"
- "Show me the failed runs"
