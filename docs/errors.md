# Errors & Troubleshooting

## Authentication Errors

### 401 Unauthorized

**Cause:** Missing or invalid authentication credentials.

**Solutions:**
- **OAuth:** Reconnect the MCP server in your client settings. Your token may have expired and failed to refresh.
- **API key:** Verify your API key is correct and hasn't been revoked. Check [Integration Settings](https://app.marcora.ai/integration-settings).
- Ensure you're using the correct URL: `https://mcp.marcora.ai` (the same for both OAuth and API key — the server negotiates the right transport automatically).

### 403 Forbidden

**Cause:** Your account doesn't have permission to perform the requested action.

**Solutions:**
- Check your team role — some actions require an Admin or Creator seat. Creating documents (`create_content`, `produce_plan`, `generate_cycle_content`, `create_blueprint_draft`) now requires an Admin or Creator role (*"Only Admins and Creators can create documents."*), connected-app call imports (`add_context` `import_from`) and Webhooks require a Creator or Admin seat (*"Integrations are only available with a creator license. Please contact your admin to upgrade your role."*; `find_app` works for any active team role), and `update_workflow` and `run_workflow` can only be called by the workflow's creator (`created_by_user_id`)
- Verify you passed the right `team_id` (check `get_current_user_info`)
- Private content/collections are only accessible by their creator

## Connection Errors

### Cannot connect to server

**Solutions:**
- Verify the server URL is correct (see above)
- Check your internet connection
- If using an API key, ensure the `Authorization` header format is `Bearer YOUR_API_KEY`
- Confirm your MCP client supports the transport type you're using (SSE or Streamable HTTP)

### Transport mismatch

**Cause:** Using an SSE URL with a client that expects Streamable HTTP, or vice versa.

**Solutions:**
- OAuth URL (`https://mcp.marcora.ai`) works with all compatible clients
- For API key connections, try switching between the SSE and Streaming URLs
- Check your client's documentation for which transport it supports

## Tool-Specific Errors

### Invalid UUID / ID not found

**Cause:** Passing an incorrect or stale ID to a tool (e.g., `blueprint_uuid`, `content_id`, `project_id`), or passing a community blueprint's `slug` instead of its UUID `id` to `get_community_blueprint_details` or `import_community_blueprint`.

**Solutions:**
- Use the corresponding list tool to get fresh IDs (e.g., `list_blueprints` before `get_blueprint`, or `list_user_webhooks` before `trigger_registered_webhook`)
- Calling `trigger_registered_webhook` with a missing or empty `webhook_id` returns `"Missing param: webhook_id. Call list_user_webhooks first, then pass its id as webhook_id."`
- For `get_community_blueprint_details` and `import_community_blueprint`, pass the UUID in the `id` field of the `list_community_blueprints` item — not its `slug` (passing `slug` returns a readable `isError: true` error telling you to pass `id`)
- IDs are UUIDs — ensure you're passing the full string, not a truncated version
- A malformed UUID is refused with a readable `isError: true` message that names the argument, so you can correct it and retry. The same applies to other refusals the caller can act on (not found, access denied, privacy): they come back as tool results with `isError: true` and a readable message rather than as protocol errors. A malformed request envelope (for example `params` that is not an object) returns JSON-RPC `-32602 Invalid params` naming the field.

### "Project not found" / "You are not a member of project …"

**Cause:** `get_relevant_context` was called with a `project_id` you can't search.
- **`Project not found`** — the project doesn't exist, or belongs to a team other than the `team_id` you passed.
- **`You are not a member of project <id>`** — the project is private and you are not one of its members.

Neither error returns any context or the project's brief.

**Solutions:**
- Check `get_current_user_info` and run `list_projects` with the right `team_id` to confirm the project id.
- For a private project, ask one of its members to add you — or search without `project_id`.

### "Marcora is already updating this document."

**Cause:** `ask_content_assistant` was called on a document that already has a Content Assistant run in progress, or `apply_finding_fix` tried to apply a fix to a document another run still holds (it comes back per finding in `errors[]`). Marcora runs one request per document at a time. A run that may edit the document also holds it until that run finishes or fails; a `chat_only_mode: true` Content Assistant run doesn't hold it, but a second call on the same document is still refused while it runs.

**Solutions:**
- Wait for the earlier run to finish (poll `get_generation_status` with its `generation_id` until it reaches a terminal status), then retry. For `apply_finding_fix`, retry just the findings that came back with this error.
- To make several changes to one document, send them one at a time, or combine them into one `prompt`.
- Do not retry in a tight loop.

### Grounding and Context Intelligence finding errors

**Cause:**
- **`"Finding not found."`** — returned as a tool error (`isError: true`) by `get_ci_finding` when the `finding_id` is unknown or belongs to another team, or per finding in `apply_finding_fix`'s `errors[]` when a `finding_id` is unknown or unreadable to the caller (that finding is skipped while the remaining findings in the call still run).
- **`"Nothing was applied. This document has private source history..."`** — returned as a tool error (`isError: true`) by `apply_finding_fix` when a fix on a document with private source history would update a context item in your Reference Library.
- **`"This check cannot use the document’s private sources..."`** — returned as a tool error (`isError: true`) by `check_content_grounding` when the document was built from Only me sources, which are never sent to an AI app.

**Solutions:**
- For `"Nothing was applied. This document has private source history..."`, follow the next step named in the message: call `apply_finding_fix` again with the same `finding_ids` and without `context_item_overrides` when that fixes the document itself; otherwise revise the document with `update_content`, then re-check.
- For `"This check cannot use the document’s private sources..."`, when the private sources are the caller's own, the message includes a link to check the document privately in Marcora; relay that link to the user.

### "Curated in Enablement · comment to suggest a change"

**Cause:** While Enablement is turned on for a team, only Enablement curators (team Admins or members granted curator permission) can edit curated Enablement material. Non-curators receive this `403` (`isError: true`) refusal from `ask_content_assistant` (when `chat_only_mode` is `false`), `apply_finding_fix`, `update_content`, `update_context`, and related edit/delete/restore paths when targeting a curated item or its linked document.

**Solutions:**
- Relay the refusal to the user — do not retry or duplicate the material. Tell them they can comment on the document in the Marcora Enablement Hub to suggest a change, or ask an Enablement curator to make the edit.
- For `ask_content_assistant`, passing `chat_only_mode: true` still works for read-only questions without editing the document.

### Content generation timeout

**Cause:** Content and blueprint generation can take a few minutes: Quick content up to about 3½ minutes, Multi-model and blueprint content 3–5 minutes, and blueprint creation/drafting 1–3 minutes.

**Solutions:**
- This is normal behavior, not an error. Wait for the response to complete.
- For blueprint-based and Multi-model generation (`generation_mode: "multi_model"`), `create_content` returns a `generation_id` (and on the `blueprint_uuid` path, also the draft's `content_id` and `link_url` at start) — use `get_generation_status` to poll for completion. `produce_plan`, `create_blueprint`, `create_blueprint_draft`, and `finalize_blueprint_draft` also return a `generation_id` immediately (`status: "processing"`) for polling via `get_generation_status`
- Do not retry the call while a generation is in progress

### Invalid category_id or dimension_option_ids

**Cause:** Using an ID that doesn't exist for that team.

**Solutions:**
- Use `list_content_categories(team_id)` to get valid category IDs
- Use `list_targeting_dimensions(team_id)` to get valid dimension option IDs

### "This action needs N Studio Credits and your team has M"

**Cause:** Your team doesn't have enough Studio Credits for a tool that spends them: `create_content`, `create_blueprint`, `create_blueprint_draft`, `finalize_blueprint_draft`, `produce_plan`, `create_project` (when it generates a brief), `create_workflow`, `update_workflow`, `run_workflow` and `ask_content_assistant`. The result is a tool error (`isError: true`) with readable text: what the action needs, what the team has, and a link to add credits or upgrade. It is not a server fault.

**Solutions:**
- Add credits or upgrade through the link in the message, then retry.
- Check what's left with `get_current_user_info` (`teams[].ai_credits_available`).

## Account Setup

### "Your Marcora account is still being set up"

**Cause:** The account is brand new and Marcora is importing its website to build the team's context. While that setup is running, the server holds each tool call for up to 30 seconds and answers it normally if setup finishes in that window. If setup is still running after the hold, the call returns "Your Marcora account is still being set up. Your website is still being processed; some imports take several minutes. This call has not run yet. Retry this same tool call now without asking the user. ..." The result is flagged as a tool error (`isError: true`) so that every client, including SDK-based ones, surfaces the message rather than rejecting the response.

This is expected, not a fault, even though the result is flagged as an error. The connection is fine: the server still lists all its tools and authentication has succeeded. Only the *calls* are held.

An account with no setup running is not held. A team added from inside an existing account, a setup that failed, and a setup that stalled all get normal tool answers. `get_current_user_info` is also exempt from the hold so you can list your teams and call another already-ready `team_id` while one team is setting up.

**Solutions:**
- Retry the same call. The call did not run, so repeating it cannot duplicate anything. Each attempt waits up to 30 seconds, so keep retrying only while the notice keeps coming, for up to 5 minutes in total, then tell the user setup is still processing and to try again later. Website imports can take several minutes.
- The message includes progress when it is available, e.g. `(3 of 7 setup steps complete.)`, so repeating the call is a reasonable way to watch it advance.
- Do not re-run signup or reconnect the server. Neither speeds this up, and creating a second account splits the team's context across two places.
- The hold releases automatically as soon as setup finishes, and in any case stops applying 72 hours after the account was created.

**Still seeing it after an hour?** Setup has likely stalled rather than being slow. Contact support with the account's email address; the import can be re-run from our side.

## Rate Limits

The Marcora MCP server applies reasonable rate limits to prevent abuse. Under normal usage, you are unlikely to hit these limits. If you receive a rate limit error (HTTP 429), wait a moment before retrying.

## Getting Help

If you encounter an issue not covered here:

- **GitHub Issues:** [github.com/ccromp/marcora-mcp/issues](https://github.com/ccromp/marcora-mcp/issues)
- **Website:** [marcora.ai](https://marcora.ai)
