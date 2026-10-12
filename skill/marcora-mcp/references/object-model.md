# The Marcora object model (long form)

Read this when you need the precise definition of a Marcora object, how objects relate, their lifecycle states, or how generation layers context. SKILL.md carries the short version.

---

## The Marcora object model

These are Marcora's core nouns. Internalize them before calling any tool.

- **Content** — A document. The unit of output. Created by `marcora:create_content`. Two creation modes that share one tool: pass `instructions` only for freeform AI generation (sync, 1–3 min), pass `instructions + blueprint_uuid` for blueprint-driven generation (async, 3–5 min, returns a `generation_id` to poll), or pass `content` only to save the user's own pre-written text directly.
  **A document's title comes from its first heading — there is no title parameter.** On the `content` path, start the markdown with `# <Title>` on the first line. On the `instructions` path, state the wanted title inside the instructions text. Never send `content` and `instructions` together (that is rejected), not even to carry a title. The title keeps following the first heading unless someone locks it with `update_content name_override`.

- **Blueprint** — A reusable AI template that defines structure, tone, and instructions for a content type (case study, launch one-pager, weekly newsletter, etc.). Has Blueprint DNA — a structural/tonal analysis Marcora uses to guide generation. Multi-format blueprints can produce a coordinated *campaign* (blog + email + in-app) in a single generation.

- **Project** — A workstream container. Groups related content + project-scoped context items + (optionally) a project brief. One project per initiative (a launch, a campaign, a positioning exercise). Projects have **members** (`owner` / `editor` / `viewer`) and a separate **Collaborator** role for project-only stakeholders.

- **Project brief** — A piece of Content pinned inside a project as its strategic anchor, and the project's **authoritative** statement of premise, scope and the decisions already taken. Surfaced prominently in the project UI. **Read it before doing substantive work in the project** (see "Working inside a project" in `references/projects-and-briefs.md`). Set at project creation via `create_project` — `project_brief_instructions` (Marcora writes the brief from your prompt) or `project_brief_content` (your finished text, saved as-is) — or on an existing project via `update_project(project_brief_id=<content uuid>)`. The latter handles attachment automatically: if the content isn't yet in the project, the tool attaches it AND sets it as the brief in one call.

- **Context item** — A reference document (brand guidelines, persona research, competitor analysis, product spec, customer interview) that informs AI generation. Lives in one of three places:
  - **Reference Library** — top-level, team-wide. Created by `add_context` with no `project_id`. Filtered by relevancy at generation time.
  - **Project context** — scoped to a single project. Created by `add_context` with `project_id`. Always pulled in for that project's generations.
  - **Document-specific** — one-off chips passed at generation time as `collection_ids` or `dimension_option_ids` on `create_content`. Not persisted as reusable context.

- **Brand Foundation** — The team's company overview, brand voice, writing style, and writing examples. Read with `marcora:get_brand_foundation`. Always pulled into every content generation. You don't need to read it manually before generating.

- **Context Collection** — A folder for organizing reference items. Optional. Can be private to the creator or shared with the team. A project can have **default collections** automatically attached to its generations.

- **Targeting dimension** — A categorical attribute (Buying Stage, Persona, Industry, Product Line). Each has selectable **options** (e.g. Persona: VP Marketing, Director of Sales). Pass *option* IDs (not dimension IDs) as `dimension_option_ids` to shape generation for an audience.

- **Content category** — A taxonomy slot for blueprints and content (GTM Strategy, Product Launch, Sales Enablement). Required when creating a blueprint, optional when creating content. Organizational only — doesn't change generation behavior.

- **Workflow** — A reusable, multi-step process the user can run on demand or on a schedule. Owns the 6 workflow tools (`create_workflow`, `update_workflow`, `run_workflow`, `get_workflow`, `list_workflows`, `get_workflow_runs`). See `references/workflows.md` for the output-destination, scheduling, and dedup patterns.

- **Content Plan** — A tracked content idea/intent on the plans board, moving through stages Suggested → Accepted → In_Process → Complete (or Dismissed). Created by `create_plan`, produced into a real Content document by `produce_plan`. **Private to its creator by default.** See `references/plans-and-playbooks.md`.

- **Playbook** — A reusable, ordered template of content-plan items ("save a repeatable content sequence"). Instantiated into a batch of plans by `instantiate_playbook`, optionally anchored to a date. **Team-visible by default.** See `references/plans-and-playbooks.md`.

### Relationship map

- A **Project** contains many **Content** items and many **Context items**, plus optionally one **Project brief** (which is itself a Content item, pinned).
- A **Content** item may belong to a Project (`project_id`) and may be generated from a **Blueprint** (`blueprint_uuid`).
- A **Context item** lives at the team level (Reference Library) OR at the project level — never both at once.
- The **Project brief** is a Content item, attached to the project and pinned as its brief. It is NOT a context item — different model, different tool. That is also why relevancy search never surfaces it as a chunk: it reaches you as a dedicated `project_brief` block instead.

### Lifecycle states worth knowing

- **Content `stage`**: `in_progress` (being generated or edited) → `ready` (final).
- **Async generation `status`**: `pending` → `gathering context` → `processing` → `completed` (or `failed`). Poll `marcora:get_generation_status` until `completed`.
- **Project `status`**: `active` or `archived`. `Project visibility`: `team` or `private`.

---

## The four-layer context model

When `marcora:create_content` runs **inside a project**, Marcora automatically layers (these are the in-app labels — quote them when explaining context):

1. **Brand Foundation** — *"Includes your company's core context such as company overview, brand voice, and writing style."* Always on. (Pulled internally — you don't fetch it.)
2. **Reference Library** — *"Includes your website content, plus any other context and messaging documents you've added."* Always on. Relevancy-scored against the prompt.
3. **Project Context** — *"Includes project brief and any project-specific context items."* Always on **inside a project**. Both the brief and project context items count.
4. **Context Collections** — User-toggleable per generation via `collection_ids`. A project can have default collections.

Outside a project, only layers 1, 2, and 4 apply.

**Implication:** don't repeat brand voice in your prompt (Layer 1 has it). Don't re-explain a project's strategic angle (Layer 3 has the brief). Your prompt's job is the one-off signal for *this* document — through `dimension_option_ids` (audience) or one-time `collection_ids`.

---

## Glossary

- **Blueprint** — Reusable AI content template.
- **Brand Foundation** — Team-wide voice/style/examples context. Auto-injected into every generation.
- **Content** — A document. The unit of output.
- **Context item** — A reference document used to inform AI generation.
- **Context Collection** — Optional folder for organizing context items.
- **Content category** — Taxonomy slot (organizational only).
- **Project** — A workstream container.
- **Project brief** — A Content item pinned as a project's strategic anchor.
- **Reference Library** — The team-wide top-level set of context items.
- **Targeting dimension** — Categorical attribute (Persona, Industry, Buying Stage…) with selectable options.
- **Workflow** — Reusable multi-step process run by a background agent. See `references/workflows.md`.
- **Content Plan** — A tracked content intent on the plans board (Suggested → Accepted → In_Process → Complete). See `references/plans-and-playbooks.md`.
- **Playbook** — A reusable, ordered template of content-plan items, instantiated as a batch. See `references/plans-and-playbooks.md`.
