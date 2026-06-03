# Tools Reference

The Marcora MCP Server exposes a set of tools that your AI assistant can call directly to interact with your workspace. Each tool maps to a specific action — from generating content to retrieving context — and can be invoked naturally through conversation.

The tools below are available to any connected AI assistant once the Marcora MCP Server is configured.

---

## Account

### `get_current_user_info`

Returns profile and subscription information for the currently authenticated user, including active team, role, subscription plan, and usage statistics.

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
| `usage` | object | Usage statistics for the current billing period |

**Example prompts:**
- "What plan am I on?"
- "Show me my account info"
- "How much usage do I have left?"

---

## Context & Resources

### `get_brand_foundation`

Returns the team's Brand Foundation — the foundational brand and company information that guides all AI-generated content. The four elements are:

- **`company_overview`** — general information about the company
- **`brand_voice`** — tone, core values, mission, and personality
- **`writing_style`** — language complexity, sentence structure, formatting preferences, CTA style
- **`writing_examples`** — sample content demonstrating the team's distinctive voice (free-form structure; users organize this however they like)

By default returns all four elements. Pass `elements` to scope the response to a subset. The response is structured JSON — paste it directly into a downstream AI prompt (modern LLMs read JSON fine) or template-string the fields into markdown if you prefer.

> **Note:** `create_content`, `create_plan`, and Marcora's in-app content generation system automatically pull Brand Foundation in — you only need this tool when you're operating *outside* those flows (e.g. providing Brand Foundation context to an external AI agent).

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

> **Errors:** If `content` exceeds the element's max character limit, the call returns a structured `ERROR_CODE_INPUT_ERROR` response naming both the limit and the actual length (e.g. *"company_overview content exceeds the 10000-character limit (got 12483 chars)"*). The write is rejected before any DB mutation — no partial updates.

**Example prompts:**
- "Update my brand voice to be less formal and more conversational"
- "Replace my company overview with the latest one-pager I just shared"
- "Save this as my writing examples"

---

### `list_context_collections`

Returns all context collections accessible to the current user. Collections organize reference materials (context items) that inform AI-generated content.

**Parameters:** None

**Output:** Array of context collections, each with the following fields:

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

You can supply the body two ways:

- **`content`** — paste the markdown body directly. Best for short or hand-authored material.
- **`content_url`** — pass a public URL and the backend fetches it and converts it to clean markdown server-side using a headless browser + Mozilla Readability (the same engine used for the user-website context-import flow). Use this whenever the body is large, comes from a presigned-link export (e.g. Google Doc, Composio sandbox), or you'd otherwise have to pull the page into your own conversation just to forward it.

Exactly one of `content` or `content_url` is required — providing both returns a 400.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Descriptive name for the context item |
| `content` | string | Conditional | Markdown body. Mutually exclusive with `content_url` — provide exactly one |
| `content_url` | string | Conditional | Public URL — backend fetches it and extracts clean markdown server-side. Mutually exclusive with `content` |
| `collection_id` | integer | No | Collection ID to organize the item (from `list_context_collections` or `create_context_collection`) |
| `project_id` | string | No | Project ID to associate with (from `get_projects`) |

**Output:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Context item ID |
| `name` | string | Context item name |
| `content` | string | The stored reference content |
| `word_count` | integer | Word count of content |
| `collection_id` | integer | Collection this item belongs to (if assigned) |
| `project_id` | string | Project association (if assigned) |
| `created_at` | integer | Unix timestamp of creation |
| `link_url` | string | Direct URL to view this context item in the Marcora app. Resolves to the project, collection, or reference library view depending on the item's scope |

**Example prompts:**
- "Add our brand guidelines to Marcora"
- "Store this competitive analysis as context"
- "Save https://example.com/competitor-pricing as a context item called 'Acme pricing'"
- "Add this product brief to the 'Product Launch' collection"

---

### `update_context`

Update an existing context item — change its name, content, or move it between collections / projects. If the item has a linked editing canvas open in the Marcora sidebar, its title and content stay in sync automatically.

Like `add_context`, you can supply a new body either as inline `content` or as a `content_url` the backend fetches and converts to markdown server-side. Pass at most one — providing both returns a 400. Omit both to leave the body untouched (e.g. when you're only renaming the item or moving it between collections).

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `context_item_id` | string (uuid) | Yes | The context item to update |
| `name` | string | No | If provided, updates the name. Omit to leave unchanged |
| `content` | string | No | New markdown body. Omit to leave unchanged. Triggers RAG re-embedding. Mutually exclusive with `content_url` |
| `content_url` | string | No | Public URL — backend fetches and converts to clean markdown server-side, then stores it as the new body. Mutually exclusive with `content` |
| `collection_id` | integer \| null | **Yes (nullable)** | Full replace. Pass the current ID to keep the item in its collection, pass a different ID to move it, or pass `null` to remove it from any collection |
| `project_id` | string (uuid) \| null | **Yes (nullable)** | Full replace. Pass the current ID to keep the project association, pass a different ID to move it, or pass `null` to disassociate it |

> **Important:** `collection_id` and `project_id` use full-replace semantics — you must pass them on every call. Omitting them is NOT the same as leaving them unchanged. If you don't know the current values, call `get_context_item` first or check the context item in the web app before updating.

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
- "Refresh the Acme pricing context item from https://example.com/competitor-pricing"

---

### `list_context_items`

Lists context items from the team's context library. By default returns all items the user can see (across projects, collections, and the reference library). Set `reference_library_only=true` to return only items that are not in any project or collection — these are the items shown in the "Reference Library" section of the Marcora web app.

Each returned item carries its own `collection_id` and `project_id` (both nullable), so you always know where it lives. To get the full markdown content of any item, pass its id to `get_context_item`.

**Privacy:** items in private collections (where you are not the creator) and items in private projects (where you are not a member) are filtered out — they will not appear in the response.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `reference_library_only` | boolean | No | When `true`, returns only items not in any project or collection. Default `false` returns everything |

**Output:** An array of context items. Each item has:

| Field | Type | Description |
|---|---|---|
| `id` | string (uuid) | Context item ID. Pass to `get_context_item` to fetch full markdown |
| `name` | string | Context item name |
| `content_intro` | string | Short truncation of the content for previews |
| `content_type` | string | One of `manual`, `webpage`, `canvas`, `deliverable`, `integration_data`, `call_transcript`, `file` |
| `word_count` | integer | Word count of the full content |
| `created_at` | integer | Unix timestamp of creation |
| `updated_at` | integer \| null | Unix timestamp of last update |
| `added_by` | object | `{id, name}` of the user who added the item |
| `relevancy_processed_status` | string | RAG indexing status (`unprocessed`, `provisional`, `complete`) |
| `collection_id` | integer \| null | Collection this item lives in, or `null` |
| `project_id` | string (uuid) \| null | Project this item is associated with, or `null` |

**Other ways to discover context-item IDs:**
- `get_project(project_id).context_items` — items attached to a specific project
- `get_relevant_context` — returns `context_item_ids` of parent items for matched chunks

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

Searches the team's context library and returns the most relevant chunks for a given prompt. Use this to gather supporting context before generating or refining content.

Set `include_brand_foundation: true` to also receive the team's Brand Foundation (company overview, brand voice, writing style, writing examples) in the same response — a one-stop fetch of everything you need to write on-brand yourself with your own model. (You don't need it when handing off to `create_content`, which pulls Brand Foundation in automatically.)

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | Yes | Search string describing what context you need |
| `project_id` | string | No | Project ID to scope context search |
| `collection_ids` | array | No | Collection IDs to scope context search |
| `dimension_option_ids` | array | No | Targeting dimension option IDs to scope the search by audience / persona / industry |
| `context_rag_ids` | array | No | Previously returned chunk IDs to exclude (for pagination) |
| `include_brand_foundation` | boolean | No | When `true`, also returns the team's Brand Foundation in the response. Default `false`. When paginating, set it `true` on the first call and `false`/omit on follow-ups so it isn't re-sent each page |

**Output:**

| Field | Type | Description |
|---|---|---|
| `relevant_context` | string | Concatenated relevant context text from matched chunks |
| `context_rag_ids` | array | Chunk IDs returned. Pass back to exclude from future searches |
| `context_item_ids` | array | Parent context item IDs that the chunks belong to |
| `brand_foundation` | object \| null | The team's four Brand Foundation elements (`company_overview`, `brand_voice`, `writing_style`, `writing_examples`); empty string for any not yet set. Non-null only when `include_brand_foundation` is `true`, otherwise `null` |

**Example prompts:**
- "Find context about our enterprise pricing"
- "What do we know about competitor X?"
- "Get context relevant to writing a product launch blog post"
- "Pull together everything I need to write a healthcare launch email, including our brand foundation"

---

## Reference

### `get_content_categories`

Returns all content categories available to your team. Categories organize blueprints and content by type (e.g. GTM Strategy, Product Launch, etc).

**Parameters:** None

**Output:** Array of categories with `id`, `name`, and metadata. Use the `id` as `category_id` when creating blueprints or content.

**Example prompts:**
- "What content categories do I have?"
- "Show me the available content types"

---

### `get_targeting_dimensions`

Returns targeting dimensions and their options for the current team. Dimensions are categories (e.g. Buying Stage, Persona) with selectable options used to target content generation.

**Parameters:** None

**Output:** Array of dimensions, each containing selectable options with IDs. Pass `dimension_option_ids` to `create_content` to target generation.

**Example prompts:**
- "What targeting dimensions are available?"
- "Show me the persona options"

---

## Blueprints

### `list_blueprints`

Get all blueprints in your team's library as a flat list. Each blueprint includes its content category and a web URL.

**Parameters:** None

**Output:** A flat array of blueprints. Each item:

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
| `category_id` | integer | Yes | Category ID from `get_content_categories` |
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
- Invalid `category_id` — use `get_content_categories` first to get valid IDs
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
| `category_id` | integer | No | Category ID from `get_content_categories` |

**Output:**

| Field | Type | Description |
|---|---|---|
| `id` | integer | Record ID for the blueprint draft |
| `uuid` | string | Unique identifier for this draft |
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

### `get_community_blueprints`

Browse community blueprints available for import. Returns blueprints shared by Marcora users, including name, summary, contributor info, and category.

**Parameters:** None

**Output:** Array of community blueprints with IDs, names, summaries, contributor details, and categories.

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
| `blueprint_exchange_id` | string | No | Blueprint exchange ID from `get_community_blueprints` |

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
| `blueprint_exchange_id` | string | No | Blueprint exchange ID from `get_community_blueprints` |

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

You must provide either `content` or `instructions` (not both).

- **With `content`** (synchronous): Saves your supplied text directly as a document — no AI generation. Returns immediately.
- **With `instructions`** (synchronous): Creates a freeform document from an AI prompt. Takes 1–3 minutes.
- **With `instructions` + `blueprint_uuid`** (asynchronous): Generates content from a blueprint template. Returns a `generation_id` to poll via `get_generation_status`. Takes 3–5 minutes.

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
| `generation_id` | integer | ID to track async generation — pass to `get_generation_status` |

**Example prompts:**
- "Save this document to Marcora" (with `content`)
- "Write a blog post about our new product launch" (with `instructions`)
- "Generate a case study using my case study blueprint" (with `instructions` + `blueprint_uuid`)
- "Create content from my newsletter blueprint for the enterprise persona"

**Common errors:**
- Providing both `content` and `instructions` — use one or the other
- Using `content` with `blueprint_uuid` — blueprints require `instructions`
- Invalid `blueprint_uuid` — use `get_blueprints` to find valid UUIDs
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
| `content_id` | string (uuid) | The generated deliverable's ID. Pass to `get_content` if you need the body |
| `name` | string | Document name |
| `blueprint_id` | integer | Blueprint used to generate |
| `link_url` | string | Direct URL to view/open in Marcora |

**`content` — Content Assistant flow** (`flow_type` = `ai_assistant`):

> `status` is per-run, but `content` is the **current** state: the live document (which may include edits the user made themselves afterward) plus the **most recent** Content Assistant interaction on that document. It is intentionally not a frozen snapshot of this specific generation — a stale snapshot isn't useful, the current version is.

| Field | Type | Description |
|---|---|---|
| `content_id` | string (uuid) | The canvas/deliverable the assistant acted on |
| `name` | string \| null | Document name |
| `document_type` | string | `canvas` or `deliverable` |
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

Returns all content visible to the current user as a single unified array. Content created from scratch (canvas) and from blueprints (deliverable) are merged with consistent field names. The same `content_id` can be passed to `get_content`, `update_content`, and `create_external_share`.

**Parameters:** None

**Output:** Array of items.

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

Update a content document (canvas or deliverable) by `content_id`. Partial-update semantics — every field besides `content_id` is optional and only the fields you supply are changed; everything else is left untouched. At least one mutable field must be supplied.

> **Reading before writing:** for `content` edits that splice into existing text, call `get_content` first, edit the markdown in your context, then send the FULL new body back. This tool replaces the entire body — there is no patch / diff mode.

> **Name behavior:** by default a document's name auto-syncs from the first markdown header in its body. Set `name_override` to lock a custom name; once locked, the title stays even when the body is edited. There is no un-lock path in this tool.

> **Stage:** writing `stage` also keeps the internal `is_ready` bool in sync. For deliverables linked to a content plan, transitioning to `ready` moves the plan to `Complete` as a side-effect (non-blocking on failure).

> **Project association:** pass `project_id` to set the document's project. If the document is already in a different project the old association is replaced; if already in the supplied project this is a no-op. Omit `project_id` to leave projects untouched. There's no way to remove a doc from all projects via this tool — use the Marcora app for that.

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
- `inputerror` — no mutable field supplied; invalid `category_id`; invalid `project_id`; or the document is a non-editable canvas type (e.g. a context-item editor canvas, which is managed by a separate sync flow)
- `accessdenied` — you don't have write access to the document

**Example prompts:**
- "Mark my latest case study as ready"
- "Add this doc to the Q4 GTM project"
- "Rename this document to 'Acme Pricing One-Pager'"
- "Replace the body of my pricing one-pager with the markdown above"

---

### `ask_content_assistant`

Send a natural-language request to Marcora's in-document **Content Assistant** for an existing document (a canvas or deliverable). The request can ask for an edit ("add an intro paragraph", "tighten paragraph two"), an extension, or pure ideation / a question ("give me three headline ideas") — the assistant decides whether to change the document or just reply.

> This is the in-editor Content Assistant that operates on one specific document — not the general Marcora Agent.

**Asynchronous.** Returns a `generation_id` (UUID) immediately and does the model work in the background. When the user has the document open in Marcora, the assistant's reply and any edits stream live into the document's AI Assistant sidebar via a realtime channel — they don't need to poll. Headless callers (or anyone wanting the result text) poll `get_generation_status` with the returned `generation_id`.

**Behavior:**
- The assistant only rewrites the document body when it decides the request warrants a change; otherwise it just replies in the sidebar thread.
- `chat_only_mode: true` forces a reply-only response with no document changes.
- The current document body and the prior sidebar conversation are loaded automatically; pass `collection_ids` and/or `project_id` to fold in extra context.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `content_id` | string (uuid) | Yes | The canvas or deliverable to act on (from `list_content`, `get_content`, or `get_project`). Canvas vs. deliverable is detected automatically |
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
- `notfound` — `content_id` matches no canvas or deliverable

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

### `get_projects`

Returns all projects visible to the current user. Projects organize content into workstreams.

**Parameters:** None

**Output:**

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
| `project_brief` | object \| null | Present (non-null) only when `project_brief_details` was supplied. `{name, content_id}`. `content_id` is the canvas UUID — pass it to `update_content` / `get_content` to edit or read the brief. `name` may be empty immediately after creation while AI generation is in flight |

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

## Plans

Plans are units of content intent — a titled, assignable record that captures what content needs to be created, when, and with what context. Use plans to queue content work, track progress through stages, and link produced content back to the originating plan.

**Stage lifecycle:** `Suggested` → `Accepted` → `In_Process` → `Complete` (or `Dismissed` from any stage except `Dismissed`).

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
