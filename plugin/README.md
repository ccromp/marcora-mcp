# Marcora

Marcora is your living company context, in Claude and in any AI tool or agent that supports MCP. Set up your positioning, voice, and product facts once. Add each campaign's material without muddying the rest. Update it in one place, and every connected AI tool gets the change.

Marcora keeps it organized:

- **Brand Foundation**: your company overview, brand voice, and writing style, drafted from your website when you sign up
- **Reference Library**: context items like product docs, positioning, persona research, competitive analysis, and messaging
- **Projects**: each campaign's brief, call notes, and research, so they apply while you work on that campaign and stay out of everything else

Use it in Claude, Cowork, and Claude Code. Connect Marcora to ChatGPT, Cursor, or any other AI tool or agent that supports MCP, and those tools read the same context. Your AI draws on that context when it answers questions and creates content for you, so the work stays on-brand, accurate, and grounded in how your company actually talks.

Marcora is built for product marketers and go-to-market teams at B2B SaaS companies, and it extends to sales, customer success, and product.

## What You Can Do in Claude

- **Ask about your own business.** Get answers on positioning, personas, and competitors from your Reference Library, with cited sources.
- **Create on-brand content.** Draft blog posts, emails, and launch messaging freeform or from proven Blueprints (reusable content templates), tailored to a persona, industry, or buying stage.
- **Launch coordinated campaigns.** Generate a matching blog post, email, and in-app message from a single multi-format Blueprint.
- **Organize launches and campaigns.** Group the work into Projects with auto-generated briefs, and turn content sequences that worked into reusable Playbooks.
- **Check the facts.** Content Grounding tests a document's claims against your Reference Library and suggests fixes you can apply.
- **Share and export.** Publish content as a trackable, branded share link or export it to Word.
- **Automate repeat work.** Turn a multi-step process into a reusable Workflow that runs on demand or on a schedule.

On the Command plan, **Context Intelligence** keeps it all current: Marcora checks web-sourced context for freshness, scans for drift as your messaging evolves, and suggests one-click fixes. Through 200+ integrations, the tools where your work already lives become context for your content.

## What's in the Plugin

- **The Marcora connector** links Claude to your Marcora account through Marcora's hosted server at `https://mcp.marcora.ai`. It works within your active team, with the same permissions you have in the Marcora web app. When Claude uses a Marcora tool, the request and the information it needs, such as your prompt or a document's text, go to Marcora. Marcora handles that data under its [privacy policy](https://marcora.ai/privacy-policy).
- **Marcora's companion skill** teaches Claude to use Marcora well: which tool fits each job, how your context fits together, and the steps for everyday work like creating content, setting up Projects, and building Workflows. The skill is instructions only. It runs no code and sends nothing on its own.

## Get Started

1. Add the Marcora plugin from the directory in Claude.
2. Open the plugin's **Connectors** tab, connect Marcora, and sign in with your Marcora account. New to Marcora? [Create a free account](https://app.marcora.ai/signup).
3. Ask Claude something that needs your context, like "What's our positioning against our top competitor?" or "Draft a launch email for our newest feature."
4. The first time Claude uses each Marcora tool, it asks for your permission. Choose **Always allow** to skip the prompt next time.

Marcora's free plan is permanent, not a trial. One person gets context access, their own Brand Foundation, and a one-time set of credits to try content generation, and reading your context is always free. Paid plans add team sharing, monthly credits for content generation, and 200+ integrations. The Command plan adds Context Intelligence, Content Grounding, and branded share links. [See pricing](https://marcora.ai/pricing).

## Support and Links

- Documentation: [marcora.ai/docs/mcp-overview](https://marcora.ai/docs/mcp-overview)
- Support: [support@marcora.ai](mailto:support@marcora.ai)
- Privacy policy: [marcora.ai/privacy-policy](https://marcora.ai/privacy-policy)
- Terms and conditions: [marcora.ai/terms](https://marcora.ai/terms)

## Using It in Claude Code

To install the plugin from Claude Code:

```
/plugin marketplace add ccromp/marcora-mcp
/plugin install marcora@marcora
```

Then restart Claude Code or run `/reload-plugins`. The skill runs automatically when a task calls for it, or on demand as `/marcora:marcora-mcp`. Marcora's tools appear as `mcp__marcora__*`.

**Sign in.** The plugin signs in with OAuth, so there's nothing to set up beyond a one-time browser login. On first connect, Claude Code flags marcora for authentication. Run `/mcp`, select **marcora**, and complete the browser login. Claude Code stores the token in your OS keychain (or in `~/.claude/.credentials.json` where no keychain is available) and refreshes it automatically. To sign out, use **Clear authentication** in the `/mcp` menu or run `claude mcp logout marcora`.

**API token for non-interactive or CI use.** Generate a token at [Integration Settings](https://app.marcora.ai/integration-settings) and add your own server entry with an `Authorization` header. Don't add the header to the bundled plugin config, because a present `Authorization` header disables the automatic OAuth sign-in.

```bash
claude mcp add --transport http marcora https://mcp.marcora.ai \
  --header "Authorization: Bearer YOUR_API_TOKEN"
```

To report a problem with the plugin, [open an issue on GitHub](https://github.com/ccromp/marcora-mcp/issues).
