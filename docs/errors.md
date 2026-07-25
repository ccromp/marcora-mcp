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
- Check your team role — some actions may require owner or admin permissions
- Verify you're on the correct active team
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

**Cause:** Passing an incorrect or stale ID to a tool (e.g., `blueprint_uuid`, `content_id`, `project_id`).

**Solutions:**
- Use the corresponding list tool to get fresh IDs (e.g., `list_blueprints` before `get_blueprint`)
- IDs are UUIDs — ensure you're passing the full string, not a truncated version

### Content generation timeout

**Cause:** Content generation (especially from blueprints) can take 1–3 minutes.

**Solutions:**
- This is normal behavior, not an error. Wait for the response to complete.
- For blueprint-based generation, `create_content` returns a `generation_id` — use `get_generation_status` to poll for completion
- Do not retry the call while a generation is in progress

### Invalid category_id or dimension_option_ids

**Cause:** Using an ID that doesn't exist for your team.

**Solutions:**
- Use `list_content_categories` to get valid category IDs
- Use `list_targeting_dimensions` to get valid dimension option IDs

## Account Setup

### "Your Marcora account setup is still underway"

**Cause:** The account is brand new and Marcora is still building its context — importing the team's top web pages, writing the brand foundation, and preparing a first document. While that is running, every tool call returns this message instead of its normal result.

This is expected, not a fault. The connection is fine: the server still lists all its tools and authentication has succeeded. Only the *calls* are held.

**Solutions:**
- Wait a few minutes and try the call again. Setup usually finishes well inside that.
- The message includes progress when it is available — e.g. `(3 of 7 setup steps complete.)` — so repeating the call is a reasonable way to watch it advance.
- Do not re-run signup or reconnect the server. Neither speeds this up, and creating a second account splits the team's context across two places.
- The hold releases automatically as soon as setup finishes, and in any case stops applying 72 hours after the account was created.

**Still seeing it after an hour?** Setup has likely stalled rather than being slow. Contact support with the account's email address — the import can be re-run from our side.

## Rate Limits

The Marcora MCP server applies reasonable rate limits to prevent abuse. Under normal usage, you are unlikely to hit these limits. If you receive a rate limit error (HTTP 429), wait a moment before retrying.

## Getting Help

If you encounter an issue not covered here:

- **GitHub Issues:** [github.com/ccromp/marcora-mcp/issues](https://github.com/ccromp/marcora-mcp/issues)
- **Website:** [marcora.ai](https://marcora.ai)
