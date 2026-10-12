# Brand Foundation

Read this before reading or changing the team's Brand Foundation (company overview, brand voice, writing style, writing examples), or linking the user to it.

---

## Recipe H — Read the team's Brand Foundation directly

Most of the time you don't need to call `marcora:get_brand_foundation` — every `create_content` call pulls Brand Foundation in automatically (Layer 1 of the four-layer model).

Call it explicitly when:
- The user asks "what brand voice does the AI use?"
- You're generating content *outside* Marcora (drafting a tweet in their voice elsewhere) and need the brand context.
- You're debugging "why does the content sound off?" — maybe Brand Foundation is stale.
- The user wants to update one of the four elements — fetch first with `marcora:get_brand_foundation({elements: ["<element>"]})` so the user can confirm what's being replaced, then call `marcora:update_brand_foundation`.

Returns structured JSON with per-element fields (`company_overview`, `brand_voice`, `writing_style`, `writing_examples`), plus a `link_url` that opens the Brand Foundation section in Marcora. Pass `elements` to scope the response; omit to return all four. Empty string is returned for any element the team has not filled out yet.

---

## Recipe H2 — Update a Brand Foundation element

When the user wants to change one of the four Brand Foundation elements:

1. Read the current value: `marcora:get_brand_foundation({elements: ["<element>"]})`.
2. Confirm with the user what's being replaced (Brand Foundation shapes every generation — unintended overwrites are costly).
3. Write: `marcora:update_brand_foundation({element: "<element>", content: "<new markdown>"})`. Always full-replace — no patch semantics.
4. Hand the user the `link_url` from the response — it opens the Brand Foundation section in Marcora. Use it **exactly as returned**; never build a Brand Foundation URL yourself. There is no `/brand-foundation` route (a hand-built link 404s and bounces them to `/home`, losing the chat).

Per-element character limits: `company_overview` 10,000; `brand_voice`, `writing_style`, `writing_examples` 20,000 each. Overflow returns an input error naming the limit, and nothing is saved.

---

## Linking the user to their Brand Foundation

**Symptom.** You update the user's Brand Foundation, link them to it, and the link 404s — they land on `/home` and the conversation they were in is gone.

**Cause.** Guessing the URL. `https://app.marcora.ai/brand-foundation` reads like the obvious route but does not exist. Brand Foundation is a tab of the Context Hub, not a page of its own.

**What to do.** Use the `link_url` that `update_brand_foundation` and `get_brand_foundation` return, exactly as returned — it points at `/context-hub?tab=brand-foundation`. This holds generally: every Marcora tool that returns a `link_url` returns the correct one. Never assemble a Marcora URL from a pattern you inferred.
