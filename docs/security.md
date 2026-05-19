# Security & Privacy

## Data Handling

The Marcora MCP server acts as a bridge between your AI client and your Marcora account. Here's how data flows:

- **Requests:** Your AI client sends tool calls to the Marcora MCP server over HTTPS. Each request includes your authentication credentials and the tool parameters.
- **Processing:** The server processes your request within the scope of your authenticated account and active team. No data is shared across teams or accounts.
- **Responses:** Tool results are returned to your AI client over the same HTTPS connection. The MCP server does not cache or store request/response data beyond what is persisted to your Marcora account (e.g., content you create, context you add).

**What the MCP server can access:**
- Your team's context library (brand voice, reference materials, collections)
- Your team's blueprints and content
- Your team's projects and their associated documents
- Your account profile and subscription information

**What the MCP server cannot do:**
- Access other teams' data
- Access billing or payment information
- Modify your account settings or team membership
- Access data outside your Marcora workspace

## Permissions Model

Access is scoped to your Marcora account and active team:

- **Team role** — Your role (owner, admin, member) determines what actions you can perform
- **Visibility** — Content and collections can be `private` (creator-only) or `team` (all team members)
- **Read/write** — All authenticated users can read team-visible data. Write operations (creating content, adding context) respect your team role and visibility settings

The MCP server enforces the same permission rules as the Marcora web application. There are no additional scopes or permissions specific to the MCP connection.

## Credential Management

- **OAuth tokens** are managed by your MCP client. Tokens are short-lived and automatically refreshed. Revoking OAuth access immediately invalidates the token.
- **API keys** are long-lived and should be treated like passwords. Store them securely and never commit them to version control. You can revoke API keys at any time from [Integration Settings](https://app.marcora.ai/integration-settings).

## Responsible Disclosure

If you discover a security vulnerability in the Marcora MCP server, please report it responsibly:

**Email:** [chris@marketcore.ai](mailto:chris@marketcore.ai)

Please include:
- A description of the vulnerability
- Steps to reproduce
- Any relevant screenshots or logs

Do **not** file public GitHub issues for security vulnerabilities. We will acknowledge your report within 48 hours and work to address verified issues promptly.
