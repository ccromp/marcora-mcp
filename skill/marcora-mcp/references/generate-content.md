# Generate content

Read this before calling `create_content`, or when following up on a generation that is still running.

---

### Workflow 1 — Generate content (the everyday case)

**Goal.** Produce a piece of content for the user, optionally inside a project, optionally targeting an audience.

**Preconditions.** None hard-required. If you don't already know what blueprints exist, what projects exist, or what targeting options exist, fetch them first.

**Steps.**
1. If you don't already know it: `marcora:list_blueprints` (returns your published blueprints under a `blueprints` array). Propose a fitting one.
   - **If nothing in the user's library fits**, also check `marcora:list_community_blueprints` (the Blueprint Exchange). If something there fits, propose it: "I don't see a matching template in your library, but '\[name]' on the Blueprint Exchange looks like a fit — want me to import it?" If they say yes: `marcora:get_community_blueprint_details` to confirm fit → `marcora:import_community_blueprint` → use the returned UUID as the `blueprint_uuid` in step 5.
2. If you don't already know it: `marcora:list_projects`. If the user mentioned an initiative, propose scoping to it.
3. If the user named an audience attribute and you don't already know the option IDs: `marcora:list_targeting_dimensions`. Pick *option* IDs.
4. **State your plan** in one sentence — naming the blueprint (or "freeform"), the project (or "no project"), the targeting, and that generation takes 1–3 min sync (freeform) or 3–5 min async (blueprint).
5. `marcora:create_content` with `instructions` (always) + `blueprint_uuid` (if blueprint) + `project_id` + `dimension_option_ids` + optional `collection_ids` for one-off context. **Do not** pre-fetch context with `get_relevant_context` — the `instructions` path pulls all relevant context internally, including the project's brief when `project_id` is set. (This holds only when *Marcora* writes via `instructions`. If instead *you* draft the content yourself and save it through the `content` parameter, you DO fetch context first — see "Writing the content yourself?" in `references/find-context.md`.)
6. **If async** (returned a `generation_id`): poll `marcora:get_generation_status` every ~30s, surface progress to the user every minute. When `status == completed`, the response includes `content.link_url`.
7. **Hand the user `content.link_url`.** They open it in Marcora. **Do NOT call `get_content` to fetch the body** — they review it, not you.

**Validation.** Before step 5, sanity-check that `content` is not combined with `blueprint_uuid` or `instructions` (mutually exclusive — pick one mode).

**Output to user.** "Done — your case study is ready: [link]. Want me to share it externally, export to Word, or refine?"

**Narrow exception to "don't pre-fetch context".** If the user wants content about something narrow and specific that probably isn't in the standard Reference Library (a particular customer name, a specific incident, a niche internal initiative), one targeted `marcora:get_relevant_context` call up front is reasonable — purely so you can ask "I don't see source material on X yet — want to add some before I generate?" Skip the pre-check for broad topics (brand voice, common positioning, generic blog ideas). The model pulls what it needs at generation time.

---

## Recipe C — Async generation followup

**Goal.** Check on (or report) a blueprint-driven generation that's still running.

**Steps.**
1. Recall the `generation_id` from earlier in the conversation. If lost, ask the user — `list_content` won't show pending generations.
2. `marcora:get_generation_status(generation_id)`.
3. Status meanings:
   - `pending` / `gathering context` / `processing` → still working, surface progress.
   - `completed` → hand `response.content.link_url` to the user.
   - `failed` → tell the user; offer to retry.
