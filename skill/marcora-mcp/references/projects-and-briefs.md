# Projects and project briefs

Read this before creating a project, setting or editing a project brief, renaming / archiving a project, or doing substantive work inside a project.

---

### Workflow 4 — Create a project

**Goal.** Set up a workstream container for an initiative.

**Preconditions.** None hard-required. If you don't already know the user's projects: `marcora:list_projects` to avoid duplicates.

**Steps.**
1. Ask the user whether to seed the brief now (written by Marcora from a prompt via `project_brief_instructions`, or their own finished text via `project_brief_content`) or set up empty (and add a brief later via Workflow 2). Both paths are fine.
2. **State your plan.**
3. `marcora:create_project` with `name`, optional `visibility` (`team` default | `private`), optional `project_brief_instructions` or `project_brief_content` (if both are sent, `project_brief_content` wins; `project_brief_instructions` uses Studio Credits). When a brief is created, the response includes `project_brief: {name, content_id}` — save the `content_id` so the user can edit the brief later via `update_content`.
4. Offer to add project context items next ("Want to add research / competitor materials to this project's context?").

**Output to user.** "Project created: [link]."

---

### Workflow 2 — Set or change a project brief

**Goal.** Make a specific Content item the strategic anchor of a project.

**Preconditions.** A project (you have the `project_id`) and a Content item (you have its UUID). Both must exist; the user must have editor or owner access to the team.

**Steps.**
1. If you don't already know the project's UUID: `marcora:list_projects` to resolve it from the name.
2. If the user said "the doc I just made" and you don't already know the Content UUID: `marcora:list_content` and disambiguate with the user.
3. **State your plan** ("I'll set the brief on \[project] to '\[doc title]'.").
4. `marcora:update_project(project_id, project_brief_id=<content_uuid>)`. **The tool handles BOTH cases automatically:** if the content is already in the project's documents → pins it as the brief; if not → attaches it AND sets it as the brief in one call.

**Validation.** None required after the call — the tool returns `success: true` with the updated project record.

**Output to user.** "Brief set: [project link]."

**To edit the brief (not change which doc IS the brief):** use `update_content` on the brief's `content_id`. Discover it via `get_project(project_id).project_brief.content_id` (`project_brief` is `null` when the project has no brief) or, when the user just created the project, take it directly from the `create_project` response. **Read the current brief before you rewrite it** — `get_content(content_id)` for the full body — because `update_content` replaces the body in full.

**Pitfalls — this is the founding misfire that motivated this skill:**
- **Don't** fetch the content with `get_content` and re-create it via `create_content(project_id=...)` to "put it in the project." That creates a duplicate with a fresh UUID, orphaned from the original. Attachment is a relationship, not a copy. `update_project` handles it.
- **Don't** call `get_project` first to check if the doc is in the project. `update_project` handles both states. (If the project *already has* a brief and the user is replacing it, it is worth reading the old one first — `get_project` then `get_content` — so nothing it settled is lost without the user knowing. That is a read for the user's benefit, not an attachment check.)
- **Don't** use `add_context` to set a brief — `add_context` creates a *Context item*, which is a different object than a Content item used as a brief.

---

### Working inside a project — read the brief first

**Goal.** Before you draft, revise, assess, critique or answer questions about work *in* a project, know what the project has already decided.

The brief is the project's authoritative statement of premise, scope and the structural decisions already taken. The project's other documents and context items may be older than it or contradict it — **the brief wins**. Work produced without reading it is likely to contradict decisions the user has already made.

**Two tools hand you the brief — you only need it once per project per conversation:**
1. **`marcora:get_project(project_id)`** → a `project_brief` block (`null` when there is no brief). Its entry in `documents` is flagged `is_project_brief: true` and sorted first.
2. **`marcora:get_relevant_context(prompt, project_id=…)`** → the same `project_brief` block, as the **first** key of the response, when the project has a brief. `include_project_brief` defaults to `true`.

**Steps.**
1. On your **first** touch of a project in the conversation, take the brief from whichever of the two calls you make first.
2. Read `content_intro`. If `truncated` is `true`, it is only the opening excerpt — call `marcora:get_content(content_id)` for the full body **before** doing the work. (This is always a legitimate use of `get_content`.)
3. On **every later** `get_relevant_context` call for the same project in the same conversation, pass `include_project_brief: false` — you already have it. If you got the brief from `get_project` first, the first `get_relevant_context` call for that project already counts as a later call. The same goes for a brief your environment has already put in your instructions for that project.
4. A **different** project is a fresh start: leave `include_project_brief` at its default for your first call on it.

**When you don't need to read it yourself.** Handing off to `create_content` with `instructions` + `project_id` — Marcora layers the brief in internally (Layer 3 of the context model). Read it when *you* are the one reasoning about the project.

**Output to user.** When the brief shapes your answer, say so in a phrase ("per the project brief, the launch leads with …") so the user can see which decisions you worked from.

---

## Recipe F — Update a project's name / visibility / status

**Goal.** Rename, archive, or change the visibility of a project.

**Steps.**
1. If you don't already know the `project_id`: `marcora:list_projects`.
2. **State your plan** — name the field changing and the new value.
3. `marcora:update_project(project_id, …)` with ONLY the fields changing (a partial update — omitted fields are untouched).
   - `name` (text)
   - `visibility` enum: `team` | `private`
   - `status` enum: `active` | `archived`

**Note.** Setting `status="active"` requires available active-project usage on the team's plan — call returns `"You have reached your active project limit."` if exhausted.

---

## E1 — "Document not found" when resolving a project brief

**Symptom.** `marcora:update_project(project_brief_id=<bad-uuid>)` returns `"Document not found"`.

**Cause.** The UUID doesn't match any content document in the team, and this is the error that comes back.

**What to do.** Verify the UUID. Common mistakes:
- Pasting a `project_id` where a content UUID was expected.
- Pasting a project document's numeric id instead of a content UUID.

---

## E2b — The project brief isn't among the chunks

**Symptom.** You searched a project with `get_relevant_context(project_id=…)` and none of the chunks come from the project's brief.

**Cause.** The brief is a Content document, not a context item, so relevancy search never indexes it. It reaches you as a separate `project_brief` block instead — on the first call for that project (`include_project_brief` defaults to `true`), or from `get_project`.

**What to do.** Read the `project_brief` block (and `get_content` when `truncated` is `true`). If you passed `include_project_brief: false` and don't have the brief yet, call again without it, or call `get_project`.

---

## E7 — A private document as a project brief

When `update_project` sets a private Content item as a project's brief, Marcora automatically makes it visible to the project's members. You don't need to change its privacy yourself.

---

## E8 — Project document `purpose` field

`marcora:get_project` returns documents with a `purpose` field:
- `core_output` — the project's main work product
- `supporting` — background material (the brief defaults to this)

Most agents don't need to set or change `purpose` — it's surfaced for the UI. Treat it as informational. There's no MCP tool to change it.

**Don't use `purpose` to find the brief.** The brief's entry carries `is_project_brief: true` and is sorted first in `documents`; `get_project` also returns it separately as the top-level `project_brief` block. Use those.
