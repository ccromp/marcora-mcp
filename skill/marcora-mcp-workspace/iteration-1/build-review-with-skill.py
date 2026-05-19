#!/usr/bin/env python3
"""Build a with-skill-only review HTML showing the updated plans for each eval."""

import sys
from pathlib import Path
import html
import re

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
            "Does it AVOID calling get_relevant_context broadly before create_content (allowing the narrow Workflow-1 sourcing-check for 'Acme Corp')?",
            "Does it AVOID calling get_content after generation completes (just hand the link)?",
            "Does it use the marcora:tool_name fully-qualified naming convention?",
        ],
    },
    {
        "id": "eval-02-brief-on-existing-project",
        "title": "Eval 02 — Brief on existing project (the founding bug)",
        "prompt": "Set the brief on the 'Q4 Product Launch' project to that messaging document I just made.",
        "what_to_look_for": [
            "Does it use update_project(project_brief_id=...) — NOT add_context?",
            "Does it AVOID checking get_project first to see if doc is already attached?",
            "Does it AVOID duplicating the content via create_content(project_id=...) (the founding Cora misfire)?",
            "Does it understand update_project auto-attaches if the doc isn't in the project yet?",
            "Does it ask which document the user means (disambiguation)?",
            "Does it state its plan before acting?",
            "Does it use the marcora:tool_name fully-qualified naming convention?",
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
            "Does it translate 'deliverable_id' field names to user-friendly 'content'?",
            "Does it use the marcora:tool_name fully-qualified naming convention?",
        ],
    },
]


def load(eval_id):
    p = ITER / eval_id / "with_skill" / "outputs" / "plan.md"
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
        if line.startswith("### "):
            if in_list:
                out.append("</ul>" if in_list != "ol" else "</ol>")
                in_list = False
            out.append(f"<h4>{html.escape(line[4:])}</h4>")
            continue
        if line.startswith("## "):
            if in_list:
                out.append("</ul>" if in_list != "ol" else "</ol>")
                in_list = False
            out.append(f"<h3>{html.escape(line[3:])}</h3>")
            continue
        if line.startswith("# "):
            if in_list:
                out.append("</ul>" if in_list != "ol" else "</ol>")
                in_list = False
            out.append(f"<h2>{html.escape(line[2:])}</h2>")
            continue
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            if in_list != "ul":
                if in_list == "ol":
                    out.append("</ol>")
                out.append("<ul>")
                in_list = "ul"
            content = stripped[2:]
            content = render_inline(content)
            out.append(f"<li>{content}</li>")
            continue
        if stripped and stripped[0].isdigit() and ". " in stripped[:5]:
            if in_list != "ol":
                if in_list == "ul":
                    out.append("</ul>")
                out.append("<ol>")
                in_list = "ol"
            num, _, rest = stripped.partition(". ")
            out.append(f"<li>{render_inline(rest)}</li>")
            continue
        if in_list:
            out.append("</ul>" if in_list == "ul" else "</ol>")
            in_list = False
        if stripped:
            out.append(f"<p>{render_inline(stripped)}</p>")
        else:
            out.append("")
    if in_list:
        out.append("</ul>" if in_list == "ul" else "</ol>")
    if in_code:
        out.append("</pre>")
    return "\n".join(out)


def render_inline(text):
    s = html.escape(text)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s


sections = []
for ev in EVALS:
    plan_html = md_to_html(load(ev["id"]))
    look_for_items = "".join(f"<li>{html.escape(x)}</li>" for x in ev["what_to_look_for"])
    sections.append(f'''
<section class="eval">
  <h2>{html.escape(ev["title"])}</h2>
  <div class="prompt"><strong>User prompt:</strong> "{html.escape(ev["prompt"])}"</div>
  <details class="rubric" open>
    <summary>What to look for</summary>
    <ul>{look_for_items}</ul>
  </details>
  <div class="plan-card">
    <h3>Agent plan (with updated skill)</h3>
    <div class="content">{plan_html}</div>
  </div>
</section>
''')

html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>marcora-mcp skill — eval review (with skill, updated)</title>
<style>
  :root {{
    --fg: #1a1a1a;
    --muted: #666;
    --bg: #fafafa;
    --card: #fff;
    --accent: #2563eb;
    --skill-tint: #ecfdf5;
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
    max-width: 900px;
    margin: 0 auto 2rem;
  }}
  h1 {{ margin: 0 0 0.5rem; font-size: 1.5rem; }}
  h2 {{ font-size: 1.2rem; margin: 0 0 0.5rem; }}
  h3 {{ font-size: 1rem; margin: 0 0 0.5rem; color: var(--muted); }}
  h4 {{ font-size: 0.95rem; margin: 1rem 0 0.3rem; }}
  .meta {{ color: var(--muted); font-size: 0.9rem; }}
  section.eval {{
    max-width: 900px;
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
  .plan-card {{
    background: var(--skill-tint);
    border: 1px solid #a7f3d0;
    border-radius: 6px;
    padding: 1rem;
    overflow-x: auto;
  }}
  .plan-card h3 {{
    margin: 0 0 0.75rem;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--fg);
  }}
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
</style>
</head>
<body>
<header>
<h1>marcora-mcp skill — eval review (with skill, updated)</h1>
<p class="meta">3 prompts, with-skill subagents only. Each subagent loaded the full updated skill (SKILL.md + 5 references) and produced a planning document for how it would handle the user prompt — without actually executing tools. Read each plan against the rubric to judge whether the skill leads the agent to the right behavior.</p>
</header>
{"".join(sections)}
</body>
</html>'''

out = ITER / "review-with-skill.html"
out.write_text(html_doc)
print(f"Wrote: {out}")
print(f"Size: {out.stat().st_size} bytes")
