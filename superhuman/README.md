# Marcora connector for Superhuman Go (Pack source)

Wraps the hosted Marcora MCP server (`https://mcp.marcora.ai/`) as a Superhuman Go connector, using OAuth 2.1 with Dynamic Client Registration and PKCE.

Local checks (these never contact Superhuman or Marcora):

    npm install
    npx packs validate pack.ts
    npx packs build pack.ts

Uploading (`npx packs upload`) needs a Superhuman account with Doc Maker access and is a separate step.
