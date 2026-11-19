# Errors and edge cases

Read this when a tool returns an error or an unexpected result.

---

## Error runbook

When things go wrong, surface the raw error to the user — don't silently retry.

- **A refusal you can act on (a wrong id, a malformed UUID, a permission or privacy refusal) comes back as a tool result with `isError: true` and a readable message**, not a protocol failure. Read the message and tell the user what it says; if it names a bad argument, correct it (re-list to get a fresh id, or pass the full UUID) and make one corrected call. Do not blindly retry. A malformed request envelope (for example a non-object `params`) returns JSON-RPC `-32602 Invalid params` naming the field.
- **`"Document not found"`** (from `update_project` with `project_brief_id`) → the UUID doesn't match any content document. Verify with the user; common mistake is pasting a project_id where a content UUID was expected.
- **`"Project not found in your current team."`** (from `update_project`) → the project belongs to a different team. Ask the user to switch active teams in the Marcora app.
- **`"Project not found"`** (from `get_relevant_context` with `project_id`) → the project doesn't exist, or belongs to a team other than the active team. Check `list_projects`; if it's in another team, `set_active_team` (tell the user first — it's global). No context or brief comes back.
- **`"You are not a member of project <id>"`** (from `get_relevant_context` with `project_id`) → the project is private and the user isn't one of its members. Tell the user; they can ask a project member to add them, or you can search without `project_id`. No context or brief comes back.
- **`"Marcora is already updating this document."`** (from `ask_content_assistant`, or per finding in `apply_grounding_fix`'s `errors[]`) → another run on that document is still in progress. Wait for it to finish (poll `get_generation_status` if you have its `generation_id`), then retry once (for `apply_grounding_fix`, retry just those findings). Don't retry in a tight loop.
- **`"Finding not found."`** (from `get_ci_finding`, or per finding in `apply_grounding_fix`'s `errors[]`) → the `finding_id` is unknown or you cannot read it. In `apply_grounding_fix`, that finding is skipped and the remaining findings in the call still run.
- **`"Nothing was applied. This document has private source history..."`** (from `apply_grounding_fix`, `isError: true`) → a fix on a document with private source history cannot update a context item in the Reference Library. Follow the next step named in the message: call again with the same `finding_ids` and without `context_item_overrides` when that fixes the document itself; otherwise revise the document with `update_content`, then re-check.
- **`"This check cannot use the document's private sources..."`** (from `check_content_grounding`, `isError: true`) → the document was built from Only me sources, which are never sent to an AI app. When they are the caller's own, the message includes a link to check the document privately in Marcora; relay that link to the user.
- **`"Integrations are only available with a creator license..."`** (403 on Connected Apps or Webhooks) → Connected Apps (`find_app`, `add_context` `import_from`) and Webhooks require a creator or admin seat. Relay the message so the user knows to ask their workspace admin to upgrade their role.
- **A plan-limit or Studio Credits refusal** (e.g. "This team has reached its plan's limit of N active projects", "Your team doesn't have enough Studio Credits") → relay Marcora's message to the user as written; it states the limit or shortfall and what they can do about it. Don't add upgrade or purchase advice of your own, and don't retry.
- **Auth / `unauthorized` errors** → tell the user to reconnect Marcora in their MCP client's integration settings. Don't try to recover.
- **Quota / rate-limit errors** → surface to the user with the message text. Don't retry in a tight loop.
- **Anything else** → tell the user what tool you called and what error came back. Suggest they file an issue at the GitHub repo if it persists.

---

## E17 — Copying Only me material into a team-visible document (or writing after private-source access changed)

**Symptom.** `update_content` or `create_content` returns a confirmation token instead of saving, or `create_content` saves a document as private when you expected a team document.

**Cause.** An item you read this session is marked `audience: "only_me"` (or comes from a private project or collection), so Marcora will not let it flow into a team-visible document unless the user agrees. In addition:
- If you read private material in this session to which the user has since lost access (or that changed after the read), `create_content` and `update_content` ask for confirmation (`confirm_private_sources`) even when writing to a document that stays private to the user (`scope` omitted/private: consent-only, nothing is shared, the document stays private).
- Calling `get_content` on a document derived from pending (unreleased) private sources records those sources as read in this session so a subsequent write cannot move that material into a wider document without confirmation.

**What to do.** Do not retry blindly and do not copy private material into a wider document on your own. Tell the user which material is involved and ask. Only if they agree, repeat the same `create_content` or `update_content` call with `confirm_private_sources` set to the token you were given. The token covers only the items it names, for that document and that one write, and expires in 5 minutes. For `create_content` when the user still has access to all read private sources and `scope` is omitted, the document is saved as private and restricted to its owner; make it team-visible only after the user agrees.

---

## E15 — Telling the user a workflow "is running" when it isn't

**Symptom.** You create a workflow, set it Active, and tell the user it's live — and nothing ever runs on its schedule. Or the user asks to "pause" a workflow and `update_workflow status:"paused"` is refused.

**Cause.** A workflow has two independent switches. The workflow is **Active** or **Inactive**; its schedule is **On** or **Paused**. Scheduled runs need both — Active **and** On. `create_workflow` saves the workflow Inactive and every schedule Paused, and no MCP tool can turn a schedule On: only the user can, in the app, with **Resume schedule**. There is no `paused` workflow status; `status` accepts only `active`, `inactive` and `archived`.

**What to do.** Read `next_step` (from `create_workflow` / `update_workflow`) or `run_state` (from `get_workflow`) and lead your reply with it — it is computed from what was actually saved. Whenever you say a workflow is Active, say in the same sentence whether its schedule is On, Paused, or absent. If the schedule is Paused, hand the user the workflow's `link_url` exactly as returned and ask them to click **Resume schedule**. To stop scheduled runs but keep manual runs, the user pauses the schedule in the app; to stop everything, set the workflow `inactive`.

---

## E5 — Content `category_id` doesn't change generation behavior

**Symptom.** User expects setting a category to affect output style. It doesn't.

**Cause.** `category_id` is purely organizational — helps the user find content later. Generation behavior is shaped by the blueprint (if any), `instructions`, context layers, and targeting dimensions.

**What to do.** Don't promise category-driven generation differences. If the user wants category-style output, recommend a blueprint instead.

---

## E10 — Surface human-readable identifiers, not UUIDs

Don't show the user a UUID like `7b2c4f...` as an identifier. Surface the human-readable name + the `link_url` instead. UUIDs are for tool calls, not user-facing references.

---

## E14 — A brand-new account's tool call is held, then answers "setup underway"

**Symptom.** Right after signup, a tool call takes up to about 30 seconds to return. Usually it then returns its normal result. If the account's website setup is still running after the hold, the call comes back with "Your Marcora account is still being set up. Your website is still being processed; some imports take several minutes. This call has not run yet. Retry this same tool call now without asking the user. ...", sometimes with a progress suffix like `(3 of 7 setup steps complete.)`. That result is marked as an error (`isError: true`), but the server lists all its tools normally.

**Cause.** The account was created recently and Marcora is actively importing its website to build the context. The server holds a tool call for up to 30 seconds and answers it normally if setup finishes in that window. If setup is still running after the hold, the call returns the message above instead of doing the work. Website imports can take several minutes. That is expected, not a fault, and the connection itself is healthy. An account with no setup running gets normal tool answers with no hold: that covers a team added from inside an existing account, a setup that failed, and one that stalled. An empty workspace is reported by the tools themselves, not by this message.

**What to do.** When the message tells you to retry the same tool call, do it yourself without asking the user. Each attempt waits up to 30 seconds on the server, so this is a paced continuation, not a tight loop; the call did not run, so repeating it cannot duplicate anything. Keep going only while this notice is returned, for up to 5 minutes in total, and stop as soon as a normal result arrives. If it is still pending after 5 minutes, tell the user setup is still processing and suggest trying again later. The error flag is how clients are made to see the message; it does not mean the tool or your arguments are broken. Do **not** treat it as a tool failure, do **not** retry in a tight sub-second loop, and do **not** suggest reconnecting the server or signing up again, because a second signup splits their context across two accounts. If it persists beyond about an hour, setup has stalled rather than being slow: tell them to contact support.

---

## E21 — Role-gated workspace actions (`Admin` / `Creator` vs. Collaborator)

**Symptom.** A Collaborator gets a 403 access-denied or `creator_license_required` error on document creation (`create_content`, `produce_plan`, `generate_cycle_content`, `create_blueprint_draft` — `"Only Admins and Creators can create documents."`), `add_context(connected_webpage_url=…)`, `update_context(refresh_webpage=true)`, `update_ci_finding_status`, `apply_grounding_fix`, `get_share_link_activity`, `list_share_link_activity`, or `find_app`.

**Cause.** Creating new documents, workspace-level context management, grounding/CI fixes, share-link analytics, and integrations require an active `Admin` or `Creator` role (`create_project` `team_visibility: "team"` makes a project visible to team Admins, Creators, and Viewers). Collaborators can read and update project-scoped content (`get_content`, `update_content`) in their projects.

**What to do.** Check `marcora:get_current_user_info` (`role`), explain that an Admin or Creator role is required, and suggest asking a workspace Admin to upgrade their role if needed.

---

## When you encounter something not in this list

1. Surface the raw error to the user — don't silently retry.
2. State what you tried and what came back.
3. Suggest plausible next steps (verify a parameter, retry, reconnect).
4. Don't assume a workaround that creates the wrong artifact in the wrong place — confirm with the user first.
