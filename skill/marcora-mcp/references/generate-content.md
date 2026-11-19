# Generate content

Read this before calling `create_content`, or when following up on a generation that is still running.

---

### Workflow 1 — Generate content (the everyday case)

**Goal.** Produce a piece of content for the user, optionally inside a project, optionally targeting an audience.

**The default: you write it.** When the user asks you to write, draft or create something (and, optionally, to save it to Marcora), write it yourself from the team's context, then save it with `content`. Marcora's own writer (`instructions`) is for three cases only: **(a)** the user asks Marcora to write or generate it, **(b)** a Blueprint is used (the user names one or asks for a template), or **(c)** a plan is being fulfilled. Do not go looking for a blueprint on every request, and do not hand a plain "write X" to the generator.

**Preconditions.** Creating documents requires an **Admin** or **Creator** role on the team (Collaborators and Viewers are refused with `"Only Admins and Creators can create documents."`). If the user mentioned an initiative and you don't already know the project, fetch it first.

**Steps — you write it (the default).**
1. If the user mentioned an initiative and you don't already know it: `marcora:list_projects`. If they want the piece scoped to it, keep the `project_id`.
2. `marcora:get_relevant_context` with a `prompt` describing the piece and `include_brand_foundation: true` on the first call of the conversation. Pass `project_id` when the piece belongs to a project (the first call returns the project's brief — read it; your draft must not contradict it). One response gives you Reference Library chunks and the team's Brand Foundation (company overview, brand voice, writing style, writing examples).
3. Write the piece yourself from what it returned. To build on existing documents, read them with `marcora:get_content` (find them with `list_content`) and write from them.
4. If the user only wants a draft, give it in the chat and stop. If they want it saved in Marcora (including "write X and save it in Marcora"): `marcora:create_content` with `content` only. Start `content` with `# <Title>` on the first line; add `project_id` and `category_id` where relevant. `content` cannot be combined with `instructions` or `blueprint_uuid`, and `reference_content_ids` is rejected with it. Saving your own `content` returns `content_id`, `title`, `link_url`, and a confirmation message without echoing the body back.
5. **Hand the user `link_url`** exactly as returned. They open it in Marcora. **Do NOT call `get_content` to fetch the body back** — they review it, not you.

**Steps — Marcora writes it (the user asks Marcora to write it, a Blueprint is used, or a plan is being fulfilled).**
1. If a Blueprint is wanted and you don't already know its UUID: `marcora:list_blueprints` (returns your published blueprints under a `blueprints` array) and propose a fitting one.
   - **If nothing in the user's library fits**, also check `marcora:list_community_blueprints` (the Blueprint Exchange — returns a compact index of `id`, `slug`, `name`, `category`, and `is_featured`, filterable by `category` and paged with `next_offset`). If something there looks relevant, call `marcora:get_community_blueprint_details` with its `id` (the UUID in the item's `id` field, never its `slug`) to read the summary, contributor info, input instructions, and content, then propose it: "I don't see a matching template in your library, but '\[name]' on the Blueprint Exchange looks like a fit — want me to import it?" If they say yes: `marcora:import_community_blueprint` with that same `id` (not `slug`) → use the returned UUID as the `blueprint_uuid` in step 5.
2. If you don't already know it: `marcora:list_projects`. If the user mentioned an initiative, propose scoping to it.
3. If the user named an audience attribute and you don't already know the option IDs: `marcora:list_targeting_dimensions`. Pick *option* IDs.
4. **State your plan** in one sentence — naming the blueprint (or "freeform"), the project (or "no project"), the targeting, and the mode and wait: Quick (freeform default) is sync and takes about 45 s to 3½ min; Multi-model (blueprint default, or `generation_mode: "multi_model"`) is async and takes 3–5 min. Quick costs 1–2 Studio Credits, Multi-model 6–7.
5. `marcora:create_content` with `instructions` + `blueprint_uuid` (if blueprint) + `project_id` + `dimension_option_ids` + optional `collection_ids` for one-off context. **Do not** pre-fetch context with `get_relevant_context` — the `instructions` path pulls all relevant context internally, including the project's brief when `project_id` is set. (This holds only when *Marcora* writes via `instructions`; when you draft the content yourself you DO fetch context first — see "Writing the content yourself?" in `references/find-context.md`.)
6. **If async** (returned a `generation_id`): on the `blueprint_uuid` path, `create_content` also returns the draft's `content_id` and `link_url` at start (the draft saves itself when generation completes, and `link_url` opens it from then on; `multi_model` without a blueprint returns `generation_id` only). Poll `marcora:get_generation_status` every ~30s, surface progress to the user every minute. When `status == completed`, the response includes `content.link_url`.
7. **Hand the user `content.link_url` (or the start-time `link_url`).** They open it in Marcora. **Do NOT call `get_content` to fetch the body** — they review it, not you.

**Validation.** Before saving, sanity-check that `content` is not combined with `blueprint_uuid` or `instructions` (mutually exclusive — pick one mode).

**Output to user.** "Done — your case study is ready: [link]. Want me to share it externally, export to Word, or refine?"

**Narrow exception to "don't pre-fetch context" (Marcora-writes path only).** If the user asks Marcora to write about something narrow and specific that probably isn't in the standard Reference Library (a particular customer name, a specific incident, a niche internal initiative), one targeted `marcora:get_relevant_context` call up front is reasonable — purely so you can ask "I don't see source material on X yet — want to add some before I generate?" Skip the pre-check for broad topics (brand voice, common positioning, generic blog ideas). The model pulls what it needs at generation time.

---

## Recipe C — Async generation followup

**Goal.** Check on (or report) an async document or blueprint generation that's still running.

**Steps.**
1. Recall the `generation_id` from earlier in the conversation. (On the `blueprint_uuid` path, `create_content` also returned the draft's `content_id` and `link_url` at start; `create_blueprint`, `create_blueprint_draft`, and `finalize_blueprint_draft` also return their `blueprint_uuid` / draft `uuid` and `link_url` at start.) If lost, ask the user — `list_content` won't show pending generations.
2. `marcora:get_generation_status(generation_id)`.
3. Status meanings:
   - `pending` / `gathering context` / `processing` → still working, surface progress.
   - `completed` → hand `response.content.link_url` (or the start-time `link_url`) to the user.
   - `failed` → tell the user why (`response.error_message` when present); offer to retry.
