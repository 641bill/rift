#!/usr/bin/env python3
"""Generate a standalone HTML view of the Rift performance report.

This intentionally implements the Markdown subset used by the project report
instead of depending on pandoc/cmark being installed on the local machine.
The Markdown file remains the source of truth; this script only creates a
readable companion artifact for browsing and sharing.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
from pathlib import Path


INLINE_CODE = re.compile(r"`([^`]+)`")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def slugify(text: str, used: set[str]) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    slug = slug or "section"
    base = slug
    index = 2
    while slug in used:
      slug = f"{base}-{index}"
      index += 1
    used.add(slug)
    return slug


def inline_markdown(text: str) -> str:
    placeholders: list[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"\u0000{len(placeholders) - 1}\u0000"

    escaped = html.escape(text, quote=False)

    escaped = INLINE_CODE.sub(
        lambda m: stash(f"<code>{html.escape(m.group(1))}</code>"), escaped
    )
    escaped = LINK.sub(
        lambda m: stash(
            f'<a href="{html.escape(m.group(2), quote=True)}">'
            f"{inline_markdown(m.group(1))}</a>"
        ),
        escaped,
    )
    escaped = BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", escaped)
    escaped = ITALIC.sub(lambda m: f"<em>{m.group(1)}</em>", escaped)

    for i, value in enumerate(placeholders):
        escaped = escaped.replace(f"\u0000{i}\u0000", value)
    return escaped


def is_table_separator(line: str) -> bool:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return False
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_table(lines: list[str]) -> str:
    header = split_table_row(lines[0])
    body = [split_table_row(line) for line in lines[2:]]
    out = ["<div class=\"table-wrap\"><table>"]
    out.append("<thead><tr>")
    for cell in header:
        out.append(f"<th>{inline_markdown(cell)}</th>")
    out.append("</tr></thead>")
    out.append("<tbody>")
    for row in body:
        out.append("<tr>")
        for cell in row:
            out.append(f"<td>{inline_markdown(cell)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def flush_paragraph(out: list[str], paragraph: list[str]) -> None:
    if paragraph:
        out.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
        paragraph.clear()


def render_markdown(markdown: str) -> tuple[str, list[tuple[int, str, str]]]:
    lines = markdown.splitlines()
    out: list[str] = []
    toc: list[tuple[int, str, str]] = []
    paragraph: list[str] = []
    used_slugs: set[str] = set()
    i = 0
    in_code = False
    code_lang = ""
    code_lines: list[str] = []

    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            if in_code:
                out.append(
                    f'<pre><code class="language-{html.escape(code_lang)}">'
                    f"{html.escape(chr(10).join(code_lines))}</code></pre>"
                )
                in_code = False
                code_lang = ""
                code_lines = []
            else:
                flush_paragraph(out, paragraph)
                in_code = True
                code_lang = line[3:].strip()
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if not line.strip():
            flush_paragraph(out, paragraph)
            i += 1
            continue

        if line.startswith("|") and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            flush_paragraph(out, paragraph)
            table_lines = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.append(render_table(table_lines))
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph(out, paragraph)
            level = len(heading.group(1))
            title = heading.group(2).strip()
            slug = slugify(re.sub(r"`([^`]+)`", r"\1", title), used_slugs)
            toc.append((level, title, slug))
            out.append(f'<h{level} id="{slug}">{inline_markdown(title)}</h{level}>')
            i += 1
            continue

        if line.startswith("- "):
            flush_paragraph(out, paragraph)
            out.append("<ul>")
            while i < len(lines) and lines[i].startswith("- "):
                out.append(f"<li>{inline_markdown(lines[i][2:].strip())}</li>")
                i += 1
            out.append("</ul>")
            continue

        ordered = re.match(r"^\d+\.\s+(.+)$", line)
        if ordered:
            flush_paragraph(out, paragraph)
            out.append("<ol>")
            while i < len(lines):
                item = re.match(r"^\d+\.\s+(.+)$", lines[i])
                if not item:
                    break
                out.append(f"<li>{inline_markdown(item.group(1).strip())}</li>")
                i += 1
            out.append("</ol>")
            continue

        paragraph.append(line.strip())
        i += 1

    flush_paragraph(out, paragraph)
    if in_code:
        out.append(
            f'<pre><code class="language-{html.escape(code_lang)}">'
            f"{html.escape(chr(10).join(code_lines))}</code></pre>"
        )
    return "\n".join(out), toc


CSS = """
:root {
  color-scheme: light;
  --bg: #f6f7f9;
  --paper: #ffffff;
  --ink: #18212f;
  --muted: #5c6675;
  --line: #d8dee8;
  --accent: #2457a6;
  --accent-soft: #e8f0ff;
  --code: #f1f4f8;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 16px/1.58 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.shell {
  display: grid;
  grid-template-columns: minmax(220px, 300px) minmax(0, 1fr);
  gap: 28px;
  max-width: 1560px;
  margin: 0 auto;
  padding: 28px;
}
aside {
  position: sticky;
  top: 20px;
  align-self: start;
  max-height: calc(100vh - 40px);
  overflow: auto;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
}
aside h2 { margin: 0 0 12px; font-size: 0.95rem; }
aside a {
  display: block;
  color: var(--muted);
  text-decoration: none;
  padding: 3px 0;
  font-size: 0.9rem;
}
aside a:hover { color: var(--accent); }
aside .toc-level-1 { font-weight: 700; color: var(--ink); margin-top: 6px; }
aside .toc-level-2 { padding-left: 10px; }
aside .toc-level-3 { padding-left: 20px; font-size: 0.84rem; }
aside .toc-level-4, aside .toc-level-5, aside .toc-level-6 {
  padding-left: 30px;
  font-size: 0.8rem;
}
main {
  min-width: 0;
  padding: 36px 48px 60px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--paper);
  box-shadow: 0 8px 30px rgba(24, 33, 47, 0.06);
}
.meta {
  margin-bottom: 26px;
  padding: 14px 16px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--accent-soft);
  color: var(--muted);
  font-size: 0.92rem;
}
h1, h2, h3, h4 {
  line-height: 1.2;
  margin: 1.7em 0 0.55em;
}
h1 { margin-top: 0; font-size: 2.1rem; }
h2 {
  padding-top: 0.65em;
  border-top: 1px solid var(--line);
  font-size: 1.55rem;
}
h3 { font-size: 1.2rem; }
a { color: var(--accent); }
code {
  padding: 0.12em 0.32em;
  border-radius: 4px;
  background: var(--code);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.92em;
}
pre {
  overflow: auto;
  padding: 16px;
  border-radius: 8px;
  background: #101827;
  color: #f4f7fb;
}
pre code {
  padding: 0;
  background: transparent;
  color: inherit;
}
.table-wrap {
  width: 100%;
  overflow-x: auto;
  margin: 18px 0 24px;
  border: 1px solid var(--line);
  border-radius: 8px;
}
table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
  font-size: 0.9rem;
}
th, td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--line);
  vertical-align: top;
  text-align: left;
}
th {
  position: sticky;
  top: 0;
  background: #edf2f8;
  z-index: 1;
}
tr:nth-child(even) td { background: #fafbfd; }
ul, ol { padding-left: 1.4rem; }
@media (max-width: 900px) {
  .shell { display: block; padding: 14px; }
  aside { position: static; max-height: none; margin-bottom: 14px; }
  main { padding: 24px 18px 40px; }
}
"""


def build_html(source: Path, markdown: str, title: str) -> str:
    body, toc = render_markdown(markdown)
    generated = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    toc_html = "\n".join(
        f'<a class="toc-level-{level}" href="#{slug}">{html.escape(text)}</a>'
        for level, text, slug in toc
        if level <= 4
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="shell">
    <aside>
      <h2>Contents</h2>
      {toc_html}
    </aside>
    <main>
      <div class="meta">
        Generated {html.escape(generated)} from
        <code>{html.escape(str(source))}</code>. Markdown remains the source of truth.
      </div>
      {body}
    </main>
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        nargs="?",
        default="docs/PERFORMANCE_EVALUATION_REPORT.md",
        help="Markdown source report",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="docs/report.html",
        help="HTML output path",
    )
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    markdown = source.read_text(encoding="utf-8")
    title = "Rift Project And Performance Evaluation Report"
    output.write_text(build_html(source, markdown, title), encoding="utf-8")
    print(f"Generated {output} from {source}")


if __name__ == "__main__":
    main()
