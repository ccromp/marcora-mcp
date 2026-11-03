import * as sdk from "@superhuman/plugins-sdk";

export const pack = sdk.newPack();

// Marcora's hosted MCP server (Streamable HTTP).
pack.addMCPServer({
  name: "Marcora",
  endpointUrl: "https://mcp.marcora.ai/",
  // Read-only search tool Go's knowledge search can use.
  searchToolNames: ["get_relevant_context"],
});

// OAuth 2.1 with Dynamic Client Registration and PKCE (S256). The platform
// registers itself and discovers the endpoints from
// https://mcp.marcora.ai/.well-known/oauth-authorization-server.
pack.setUserAuthentication({
  type: sdk.AuthenticationType.OAuth2,
  useDynamicClientRegistration: true,
  useProofKeyForCodeExchange: true,
});

// Outbound traffic must be declared; the MCP and OAuth endpoints share this host.
pack.addNetworkDomain("marcora.ai");
