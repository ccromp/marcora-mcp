#!/usr/bin/env python3
"""Build a side-by-side review HTML comparing with-skill vs baseline subagent outputs."""

import sys
from pathlib import Path
import html
import json

ITER = Path(__file__).parent
EVALS = [
    {
        "id": "eval-01-blueprint-content",
        "title": "Eval 01 — Blueprint-driven content (the everyday case)",
        "prompt": "I want to write a case study about our recent deployment with Acme Corp. Targeting healthcare CIOs. Can you do that for me?",
        "what_to_look_for": [
            "Does the agent check for an existing case-study blueprint before generating from scratch?",
            "Does it propose targeting via dimension_option_ids for 'Healthcare CIO'?",
            "Does it look up project context (is this for an Acme project that exists)?",
            "Does it state its plan to the user BEFORE acting?",
            "Does it correctly handle the async polling for blueprint-driven generation?",
        ],
    },
    {
        "id": "eval-02-brief-on-existing-project",
        "title": "Eval 02 — Brief on existing project (the founding bug)",
        "prompt": "Set the brief on the 'Q4 Product Launch' project to that messaging document I just made.",
        "what_to_look_for": [
            "Does it use update_project(project_brief_id=...) — NOT add_context?",
            "Does it FIRST verify the messaging document is already in the project's documents (precondition for update_project)?",
            "Does it have a sensible plan if the doc isn't in the project yet?",
            "Does it ask which document the user means (disambiguation)?",
            "Does it state its plan before acting?",
        ],
    },
    {
        "id": "eval-03-multi-project-content-discovery",
        "title": "Eval 03 — Multi-project content discovery",
        "prompt": "What content do I have related to the launch? I want to see what's already been written across all my projects.",
        "what_to_look_for": [
            "Does it call list_projects to scope the search to projects?",
            "Does it organize results BY project (not a flat list)?",
            "Does it ask what 'launch' refers to (could be ambiguous)?",
            "Does it offer follow-up actions (drill into specific content, share, etc.)?",
            "Does it translate 'deliverable_id' / 'canvas' field names to user-friendly 'content'?",
        ],
    },
]


def load(eval_id, condition):
    p = ITER / eval_id / condition / "outputs" / "plan.md"
    if not p.exists():
        return f"<em>(no plan.md found at {p})</em>"
    return p.read_text()


def md_to_html(md):
    """Very simple markdown rendering — code blocks, headings, lists, paragraphs."""
    lines = md.split("\n")
    out = []
    in_code = False
    in_list = False
    for line in lines:
        if line.startswith("```"):
            if in_code:
                out.append("</pre>")
                in_code = False
            else:
                out.append('<pre class="code">')
                in_code = True
            continue
        if in_code:
            out.append(html.escape(line))
            continue
        # Headings
        if line.startswith("### "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h4>{html.escape(line[4:])}</h4>")
            continue
        if line.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h3>{html.escape(line[3:])}</h3>")
            continue
        if line.startswith("# "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h2>{html.escape(line[2:])}</h2>")
            continue
        # Lists
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            content = stripped[2:]
            content = render_inline(content)
            out.append(f"<li>{content}</li>")
            continue
        # Numbered list — treat similarly
        if stripped and stripped[0].isdigit() and ". " in stripped[:5]:
            if not in_list:
                out.append("<ol>")
                in_list = "ol"
            num, _, rest = stripped.partition(". ")
            out.append(f"<li>{render_inline(rest)}</li>")
            continue
        # Close list if open
        if in_list:
            out.append("</ul>" if in_list != "ol" else "</ol>")
            in_list = False
        # Paragraph or blank
        if stripped:
            out.append(f"<p>{render_inline(stripped)}</p>")
        else:
            out.append("")
    if in_list:
        out.append("</ul>" if in_list != "ol" else "</ol>")
    if in_code:
        out.append("</pre>")
    return "\n".join(out)


def render_inline(text):
    """Render basic inline markdown: bold, code, links."""
    s = html.escape(text)
    # Code spans `x`
    import re
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    # Bold **x**
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    # Italic *x*
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s


sections = []
for ev in EVALS:
    with_html = md_to_html(load(ev["id"], "with_skill"))
    without_html = md_to_html(load(ev["id"], "without_skill"))
    look_for_items = "".join(f"<li>{html.escape(x)}</li>" for x in ev["what_to_look_for"])
    sections.append(f'''
<section class="eval">
  <h2>{html.escape(ev["title"])}</h2>
  <div class="prompt"><strong>User prompt:</strong> "{html.escape(ev["prompt"])}"</div>
  <details class="rubric">
    <summary>What to look for</summary>
    <ul>{look_for_items}</ul>
  </details>
  <div class="grid">
    <div class="col with-skill">
      <h3>WITH skill</h3>
      <div class="content">{with_html}</div>
    </div>
    <div class="col baseline">
      <h3>WITHOUT skill (baseline)</h3>
      <div class="content">{without_html}</div>
    </div>
  </div>
</section>
''')

html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>marcora-mcp skill — eval review (iteration 1)</title>
<style>
  :root {{
    --fg: #1a1a1a;
    --muted: #666;
    --bg: #fafafa;
    --card: #fff;
    --accent: #2563eb;
    --skill-tint: #ecfdf5;
    --baseline-tint: #fef3c7;
    --code-bg: #f4f4f5;
    --border: #e5e7eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif;
    color: var(--fg);
    background: var(--bg);
    margin: 0;
    padding: 1.5rem;
    line-height: 1.5;
  }}
  header {{
    max-width: 1400px;
    margin: 0 auto 2rem;
  }}
  h1 {{ margin: 0 0 0.5rem; font-size: 1.5rem; }}
  h2 {{ font-size: 1.2rem; margin: 0 0 0.5rem; }}
  h3 {{ font-size: 1rem; margin: 0 0 0.5rem; color: var(--muted); }}
  h4 {{ font-size: 0.95rem; margin: 1rem 0 0.3rem; }}
  .meta {{ color: var(--muted); font-size: 0.9rem; }}
  section.eval {{
    max-width: 1400px;
    margin: 0 auto 2rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
  }}
  .prompt {{
    background: var(--code-bg);
    padding: 0.75rem 1rem;
    border-radius: 4px;
    margin: 0.5rem 0 1rem;
    font-size: 0.95rem;
  }}
  .rubric {{ margin: 0 0 1rem; }}
  .rubric summary {{ cursor: pointer; color: var(--accent); font-size: 0.9rem; }}
  .rubric ul {{ margin: 0.5rem 0 0 1rem; font-size: 0.9rem; }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }}
  .col {{
    border-radius: 6px;
    padding: 1rem;
    overflow-x: auto;
  }}
  .with-skill {{ background: var(--skill-tint); border: 1px solid #a7f3d0; }}
  .baseline {{ background: var(--baseline-tint); border: 1px solid #fde68a; }}
  .col h3 {{ margin: 0 0 0.75rem; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--fg); }}
  .content p {{ margin: 0.5rem 0; }}
  .content ul, .content ol {{ margin: 0.5rem 0; padding-left: 1.25rem; }}
  .content li {{ margin: 0.2rem 0; }}
  code {{
    background: var(--code-bg);
    padding: 0.1em 0.3em;
    border-radius: 3px;
    font-size: 0.9em;
    font-family: ui-monospace, "SF Mono", monospace;
  }}
  pre.code {{
    background: var(--code-bg);
    padding: 0.75rem;
    border-radius: 4px;
    overflow-x: auto;
    font-family: ui-monospace, "SF Mono", monospace;
    font-size: 0.85em;
    line-height: 1.4;
  }}
  @media (max-width: 1000px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<header>
<h1>marcora-mcp skill — eval review (iteration 1)</h1>
<p class="meta">3 prompts × 2 conditions (with-skill subagent | baseline subagent without skill). Both subagents had the same MCP tool inventory available; the only difference was whether they read the skill files. Both planned (didn't execute). Output is each agent's planning document — read side-by-side and judge whether the skill changes the agent's behavior in ways that matter to your customers.</p>
</header>
{"".join(sections)}
</body>
</html>'''

out = ITER / "review.html"
out.write_text(html_doc)
print(f"Wrote: {out}")
print(f"Size: {out.stat().st_size} bytes")
