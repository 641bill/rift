#!/usr/bin/env python3
"""Generate the self-contained presentation HTML report for Rift.

The Markdown report remains the archival source of truth. This script builds a
curated, presentation-oriented HTML page with summary cards, styled tables, and
a collapsed detailed appendix rendered from the Markdown source.
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


def esc(value: object) -> str:
    return html.escape(str(value), quote=False)


def attr(value: object) -> str:
    return html.escape(str(value), quote=True)


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


def render_markdown_table(lines: list[str]) -> str:
    header = split_table_row(lines[0])
    body = [split_table_row(line) for line in lines[2:]]
    out = ['<div class="table-scroll appendix-table"><table>']
    out.append("<thead><tr>")
    for cell in header:
        out.append(f"<th>{inline_markdown(cell)}</th>")
    out.append("</tr></thead><tbody>")
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
            out.append(render_markdown_table(table_lines))
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph(out, paragraph)
            level = len(heading.group(1))
            title = heading.group(2).strip()
            slug = slugify(re.sub(r"`([^`]+)`", r"\1", title), used_slugs)
            toc.append((level, title, slug))
            out.append(f'<h{level} id="appendix-{slug}">{inline_markdown(title)}</h{level}>')
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


NAV = [
    ("summary", "Summary"),
    ("design", "Design"),
    ("protocol", "Protocol"),
    ("evidence", "Evidence"),
    ("real-input", "Real Input"),
    ("operators", "Operators"),
    ("open-work", "Open Work"),
    ("appendix", "Appendix"),
]


SUMMARY_CARDS = [
    {
        "label": "Real-input epoch workload",
        "value": "16.12s vs 18.79s",
        "detail": "Yak LiveJournal 50M L1: checked epoch scoped vs gc-heap, with RSS about 612 MB vs 2.77 GB.",
        "claim": "Real-input throughput and RSS win",
        "tone": "win",
    },
    {
        "label": "Retained-object reclaim",
        "value": "0.47s vs 0.70s",
        "detail": "Focused retained epoch 1M x20 L1: checked scoped retained/drop-anchor vs heap retained/drop-anchor.",
        "claim": "Memory-management evidence",
        "tone": "win",
    },
    {
        "label": "Generated stream pressure",
        "value": "4.02s vs 5.68s",
        "detail": "Common Crawl WET-shaped q1 page-token L1: checked stream page-token vs heap.",
        "claim": "Generated stressor, not real-input proof",
        "tone": "method",
    },
    {
        "label": "Reusable top-k API",
        "value": "4.88s vs 5.52s",
        "detail": "LogHub HDFS top templates 1M x20 L1: checked top-k scoped API vs retained heap.",
        "claim": "Real-input modest throughput and RSS win",
        "tone": "win",
    },
]


DESIGN_CARDS = [
    {
        "title": "Epoch regions",
        "api": "RiftRegion.epoch { ... }",
        "body": "Batch, transaction, graph-step, and Yak-style workloads allocate ordinary objects inside an epoch and bulk-close them at the boundary.",
    },
    {
        "title": "Page/window token regions",
        "api": "page/window token operators",
        "body": "Page, event-bucket, and window-owned records are appended through operator-owned paths that cache the active child region and close buckets in bulk.",
    },
    {
        "title": "Retained-object controls",
        "api": "retained/drop-anchor",
        "body": "Heap and regions both retain ordinary records until close. Heap drops the anchor and later relies on GC; regions close the allocation area.",
    },
    {
        "title": "Checked scoped backend",
        "api": "checked-region-scoped",
        "body": "Checked Rift APIs over the rooted SafeZone-family scoped backend. This is the main safe backend candidate when scoped allocation wins.",
    },
]


CLASS_CARDS = [
    ("Natural heap baseline", "Original gc-heap program. This is the user-visible GC baseline."),
    ("Same-shape heap control", "Heap uses the same retained, epoch, page, or window topology as the region row."),
    ("Retained-object memory-management", "Both sides retain ordinary objects until close; region wins by bulk reclaim rather than tracing."),
    ("Framework API win", "Uses reusable APIs such as RiftRegion.epoch, page-token, or EpochTopKByKey."),
    ("Summary-only topology", "Updates summaries on append and does not retain records. Useful lower bound, not a GC/reclaim claim."),
    ("Unsafe/trusted lower bound", "Rootless or trusted modes show backend potential only, never final safety claims."),
]


MODE_ROWS = [
    ("gc-heap", "Scala Native Immix heap", "Natural baseline"),
    ("region-scoped-rooted", "SafeZone-family rooted scoped allocation", "Safe rooted baseline"),
    ("region-scoped-rootless", "SafeZone allocator with root tracking disabled", "Unsafe lower bound"),
    ("region-stream-rootless", "Rift streaming/reset backend without checked guarantee", "Trusted lower bound"),
    ("checked-region-stream", "Checked Rift API over Rift streaming backend", "Safe checked candidate"),
    ("checked-region-scoped", "Checked Rift API over rooted scoped backend", "Safe checked candidate"),
    ("checked-page-token", "Operator-owned checked page/window fast path", "Safe checked API"),
    ("checked-epoch-scoped", "Direct checked epoch topology over scoped backend", "Safe checked API"),
    ("checked-epoch-topk-scoped", "Reusable top-k API over checked epoch/scoped topology", "Safe checked API candidate"),
]


EVIDENCE_ROWS = [
    {
        "claim": "Real-input checked epoch win",
        "benchmark": "Yak LiveJournal graph replay, real SNAP input, 50M replayed edges",
        "checked": "checked-epoch-scoped: 16.12s L1, RSS about 612 MB",
        "control": "gc-heap: 18.79s L1, RSS about 2.77 GB",
        "interpretation": "Reusable epoch API beats heap on throughput and memory footprint; this is the strongest real-input epoch row.",
        "class": "Framework API win",
    },
    {
        "claim": "Retained-object reclaim win",
        "benchmark": "Focused RetainedEpochReclaimMatrix, 1M records x20",
        "checked": "checked scoped retained/drop-anchor: 0.47s L1",
        "control": "heap retained/drop-anchor: 0.70s L1",
        "interpretation": "Both retain ordinary objects until close; region bulk close avoids heap GC reclaim work.",
        "class": "Retained-object memory-management",
    },
    {
        "claim": "Dataflow family checked win",
        "benchmark": "Dataflow SELECT / AGGREGATE / JOIN, 1M x20",
        "checked": "checked epoch scoped: 0.38 / 0.69 / 0.39s",
        "control": "gc-heap: 0.62 / 1.10 / 0.55s",
        "interpretation": "Reusable epoch topology wins across prior-work-shaped dataflow rows.",
        "class": "Framework API win",
    },
    {
        "claim": "StreamFlex throughput and latency",
        "benchmark": "StreamFlex-style throughput and latency rows",
        "checked": "checked scoped direct epoch: 0.58s throughput; 0.17s latency row with zero misses",
        "control": "heap: 0.79s throughput; 0.18s latency row with four misses",
        "interpretation": "Epoch API improves throughput and reduces deadline/tail events on this methodology row.",
        "class": "Framework API win",
    },
    {
        "claim": "Transaction-style checked win",
        "benchmark": "Stancu-style transactions and SPECjbb2005-workload port",
        "checked": "Stancu: 0.57s checked scoped epoch; SPECjbb port: 2.21s",
        "control": "Heap: 0.85s Stancu; 2.64s SPECjbb port",
        "interpretation": "Transaction/epoch boundaries are a good reusable checked topology. SPECjbb row is a clean-room port, not official SPECjbb.",
        "class": "Framework API win",
    },
    {
        "claim": "Generated stream object-pressure win",
        "benchmark": "Generated Common Crawl WET-shaped q1/q2, 1M pages",
        "checked": "checked stream page-token: 4.02s q1, 4.16s q2 L1",
        "control": "gc-heap: 5.68s q1, 5.53s q2 L1",
        "interpretation": "Shows page/window API strength under generated object pressure; not a real-input proof.",
        "class": "Framework API win",
    },
    {
        "claim": "Real-input top-k modest win",
        "benchmark": "LogHub HDFS top templates, real HDFS input, 1M x20",
        "checked": "checked epoch top-k scoped: 4.88s, RSS about 28 MB",
        "control": "retained heap: 5.52s, RSS about 205 MB",
        "interpretation": "Reusable top-k API is close to manual retained lower bound and improves memory footprint sharply.",
        "class": "Framework API win",
    },
    {
        "claim": "Real-input RSS win",
        "benchmark": "LogHub HDFS q2 page/window, real HDFS input",
        "checked": "checked scoped page-token: 25.56s, RSS about 79 MB",
        "control": "gc-heap: 25.60s, RSS about 409 MB",
        "interpretation": "Elapsed is effectively tied, but the checked row materially lowers RSS.",
        "class": "RSS win / real-input control",
    },
    {
        "claim": "Generated retained controls",
        "benchmark": "GH Archive-shaped, DSPBench, and LogHub generated retained rows",
        "checked": "checked retained/drop-anchor rows",
        "control": "heap retained/drop-anchor and summary-only controls",
        "interpretation": "Useful for separating topology wins from memory-management wins. Summary-only rows are not headline memory claims.",
        "class": "Retained-object or topology control",
    },
]


REAL_INPUT_ROWS = [
    ("Yak LiveJournal", "Real SNAP graph input", "Strong checked epoch throughput and RSS win", "Use as flagship real-input epoch row."),
    ("LogHub HDFS top templates", "Real LogHub HDFS log lines", "Modest throughput win and large RSS reduction", "Reusable EpochTopKByKey row."),
    ("LogHub HDFS q2", "Real LogHub HDFS log lines", "Elapsed tie, strong RSS reduction", "Real-input page/window control."),
    ("GH Archive", "Real NDJSON event data", "Mostly modest RSS/tail evidence", "Parser/string CPU often dominates."),
    ("Real WET/WAT", "Real Common Crawl shards", "Not materially GC-heavy in current queries", "Ceiling/control, not flagship proof."),
    ("Wikimedia / Linear Road", "Real TSV / official methodology input", "Heap is often fast and GC-light", "Regression or ceiling controls."),
]


OPEN_WORK_ROWS = [
    ("Measurement-clean sweep", "Finish L1 final-clean rows for all representative API wins and keep L2 stats for interpretation."),
    ("ReML/MLKit table", "Fill paper-reported rows, exact-rerun provenance, and Scala Native port rows in the PLDI-style table."),
    ("Real-input search", "Continue with larger LiveJournal/SNAP, richer LogHub template/session mining, Theodolite traces, and DSPBench kernels."),
    ("Operator gates", "Do not headline rank/hash/median/join until each has natural heap, same-shape heap, retained controls, and a focused API gate."),
    ("Backend selection", "Keep only safe user-facing components that win; unsafe/rootless rows remain internal lower bounds."),
]


def tag(text: str, tone: str = "neutral") -> str:
    return f'<span class="tag tag-{attr(tone)}">{esc(text)}</span>'


def render_summary_cards() -> str:
    parts = ['<div class="summary-grid">']
    for item in SUMMARY_CARDS:
        parts.append(
            f'''<article class="metric-card metric-{attr(item["tone"])}">
  <div class="metric-label">{esc(item["label"])}</div>
  <div class="metric-value">{esc(item["value"])}</div>
  <p>{esc(item["detail"])}</p>
  <div>{tag(item["claim"], item["tone"])}</div>
</article>'''
        )
    parts.append("</div>")
    return "\n".join(parts)


def render_design_cards() -> str:
    parts = ['<div class="feature-grid">']
    for item in DESIGN_CARDS:
        parts.append(
            f'''<article class="feature-card">
  <h3>{esc(item["title"])}</h3>
  <div class="api-chip"><code>{esc(item["api"])}</code></div>
  <p>{esc(item["body"])}</p>
</article>'''
        )
    parts.append("</div>")
    return "\n".join(parts)


def render_class_cards() -> str:
    parts = ['<div class="class-grid">']
    for title, body in CLASS_CARDS:
        parts.append(
            f'''<article class="class-card">
  <h3>{esc(title)}</h3>
  <p>{esc(body)}</p>
</article>'''
        )
    parts.append("</div>")
    return "\n".join(parts)


def render_table(headers: list[str], rows: list[list[str]], caption: str | None = None) -> str:
    parts = ['<div class="table-scroll"><table class="data-table">']
    if caption:
        parts.append(f"<caption>{esc(caption)}</caption>")
    parts.append("<thead><tr>")
    for header in headers:
        parts.append(f"<th>{esc(header)}</th>")
    parts.append("</tr></thead><tbody>")
    for row in rows:
        parts.append("<tr>")
        for cell in row:
            parts.append(f"<td>{cell}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    return "\n".join(parts)


def render_mode_table() -> str:
    rows = [[f"<code>{esc(name)}</code>", esc(meaning), esc(status)] for name, meaning, status in MODE_ROWS]
    return render_table(["Reporting name", "Meaning", "Role"], rows)


def render_evidence_cards() -> str:
    parts = ['<div class="evidence-list">']
    for item in EVIDENCE_ROWS:
        parts.append(
            f'''<article class="evidence-card">
  <header>
    <div>{tag(item["class"], "method")}</div>
    <h3>{esc(item["claim"])}</h3>
  </header>
  <dl>
    <div><dt>Benchmark</dt><dd>{esc(item["benchmark"])}</dd></div>
    <div><dt>Best checked row</dt><dd>{esc(item["checked"])}</dd></div>
    <div><dt>Control</dt><dd>{esc(item["control"])}</dd></div>
    <div><dt>Interpretation</dt><dd>{esc(item["interpretation"])}</dd></div>
  </dl>
</article>'''
        )
    parts.append("</div>")
    return "\n".join(parts)


def render_real_input_table() -> str:
    rows = [[esc(a), esc(b), esc(c), esc(d)] for a, b, c, d in REAL_INPUT_ROWS]
    return render_table(["Benchmark", "Input", "Current result", "Report status"], rows)


def render_open_work() -> str:
    rows = [[esc(a), esc(b)] for a, b in OPEN_WORK_ROWS]
    return render_table(["Track", "Next action"], rows)


def render_nav() -> str:
    return "\n".join(
        f'<a href="#{attr(anchor)}">{esc(label)}</a>' for anchor, label in NAV
    )


def build_html(source: Path, markdown: str, title: str) -> str:
    appendix_body, _appendix_toc = render_markdown(markdown)
    generated = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>
  <header class="site-header">
    <a class="brand" href="#top">Rift Evaluation</a>
    <nav aria-label="Main report sections">
      {render_nav()}
    </nav>
  </header>

  <main id="top">
    <section class="hero">
      <div class="hero-copy">
        <div class="eyebrow">Scala Native checked stream regions</div>
        <h1>Rift performance evaluation report</h1>
        <p class="hero-lede">
          A presentation-ready summary of where checked region APIs beat
          Scala Native Immix, where SafeZone-family backends help, and where
          results are topology controls rather than memory-management claims.
        </p>
        <div class="hero-actions">
          <a class="button" href="#evidence">View representative data</a>
          <a class="button button-secondary" href="PERFORMANCE_EVALUATION_REPORT.md">Open source Markdown</a>
        </div>
      </div>
      <aside class="hero-panel" aria-label="Report metadata">
        <div class="panel-row"><span>Generated</span><strong>{esc(generated)}</strong></div>
        <div class="panel-row"><span>Source</span><strong>{esc(source)}</strong></div>
        <div class="panel-row"><span>Headline rule</span><strong>L1 clean timing for elapsed/RSS</strong></div>
        <div class="panel-row"><span>Interpretation rule</span><strong>L2-L4 for GC, region stats, profiles</strong></div>
      </aside>
    </section>

    <section id="summary" class="section">
      <div class="section-kicker">Executive summary</div>
      <h2>What the current evidence says</h2>
      <p>
        Rift should be reported as a checked stream-region programming model,
        not as a collection of benchmark-local rewrites. The strongest rows use
        reusable epoch, page/window, retained-object, and top-k APIs with clear
        comparison classes.
      </p>
      {render_summary_cards()}
    </section>

    <section id="design" class="section">
      <div class="section-kicker">System shape</div>
      <h2>Reusable checked APIs, not one-off benchmark tricks</h2>
      <p>
        The public story is now organized around safe framework APIs. Static
        capture and separation checking is what permits the backend to remove
        runtime escape tables, promotion barriers, close-time scans, and
        per-record defensive checks inside operator-owned fast paths.
      </p>
      {render_design_cards()}
      <div class="callout">
        <strong>Important boundary:</strong> summary-only count-array rows are
        useful lower bounds, but they are not memory-management wins. A memory
        management claim compares retained heap/drop-anchor against retained
        checked regions.
      </div>
    </section>

    <section id="protocol" class="section">
      <div class="section-kicker">Evaluation contract</div>
      <h2>Every row needs a comparison class and measurement level</h2>
      <p>
        This report separates final clean timing from diagnostic evidence. L1
        rows use external process timing and RSS only. L2 rows explain GC and
        region behavior. L3/L4 diagnostics and profiles are never headline
        elapsed numbers.
      </p>
      {render_class_cards()}
      <h3>Canonical reporting names</h3>
      {render_mode_table()}
    </section>

    <section id="evidence" class="section">
      <div class="section-kicker">Representative evidence</div>
      <h2>Wins, controls, and what each one proves</h2>
      <p>
        The table cards below intentionally mix throughput, RSS, retained-object
        memory-management, and generated-stressor evidence, but each row states
        the allowed claim. This avoids presenting topology lower bounds as GC
        wins.
      </p>
      {render_evidence_cards()}
    </section>

    <section id="real-input" class="section">
      <div class="section-kicker">Real inputs</div>
      <h2>Real datasets are useful, but not all are GC-heavy</h2>
      <p>
        The best real-input case so far is Yak LiveJournal with a direct checked
        epoch topology. Other real inputs often spend more time in parsing,
        string handling, or query CPU than GC; those rows remain important RSS,
        tail, or ceiling controls.
      </p>
      {render_real_input_table()}
    </section>

    <section id="operators" class="section split-section">
      <div>
        <div class="section-kicker">Component selection</div>
        <h2>Keep winning safe components public</h2>
        <p>
          Final user-facing components should be selected by evidence: checked
          epoch for epochal workloads, page/window token for page-owned streams,
          and checked top-k only after focused and application rows pass.
          Unsafe/rootless rows remain internal lower bounds.
        </p>
      </div>
      <div class="status-stack">
        <div class="status-card status-good"><strong>Keep</strong><span>checked epoch, checked page/window token, checked scoped backend candidates</span></div>
        <div class="status-card status-watch"><strong>Gate</strong><span>EpochTopKByKey, rank/hash/median/join, richer real-input workloads</span></div>
        <div class="status-card status-bad"><strong>Demote</strong><span>benchmark-local manual arrays, summary-only rows, unsafe/rootless rows for public claims</span></div>
      </div>
    </section>

    <section id="open-work" class="section">
      <div class="section-kicker">Next steps</div>
      <h2>What remains before a thesis-grade final package</h2>
      {render_open_work()}
    </section>

    <section id="appendix" class="section appendix">
      <div class="section-kicker">Detailed appendix</div>
      <h2>Full Markdown report snapshot</h2>
      <p>
        The presentation sections above are curated. The detailed Markdown
        report is included below for a self-contained shareable artifact.
      </p>
      <details>
        <summary>Open full rendered Markdown appendix</summary>
        <div class="appendix-body">
          {appendix_body}
        </div>
      </details>
      <div class="source-links">
        <a href="PERFORMANCE_EVALUATION_REPORT.md">Markdown report</a>
        <a href="../evidence/EVALUATION_CLASSIFIED_SUMMARY.md">Classified summary</a>
        <a href="../evidence/FINAL_CLEAN_HEADLINE_RESULTS.md">Final-clean results</a>
        <a href="../evidence/MEASUREMENT_OVERHEAD_PROTOCOL.md">Measurement protocol</a>
      </div>
    </section>
  </main>
</body>
</html>
"""


CSS = """
:root {
  color-scheme: light;
  --bg: #f4f6f8;
  --paper: #ffffff;
  --paper-soft: #f8fafc;
  --ink: #16202f;
  --muted: #5f6d7e;
  --line: #dbe2ea;
  --accent: #1f6f78;
  --accent-dark: #154c58;
  --accent-soft: #e7f5f6;
  --blue: #2858a4;
  --blue-soft: #e9f0ff;
  --green: #28784f;
  --green-soft: #eaf7ef;
  --amber: #926313;
  --amber-soft: #fff4db;
  --red: #9b3b3b;
  --red-soft: #ffecec;
  --shadow: 0 24px 70px rgba(22, 32, 47, 0.10);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background:
    radial-gradient(circle at top left, rgba(31, 111, 120, 0.11), transparent 34rem),
    linear-gradient(180deg, #fbfcfd 0, var(--bg) 28rem);
  color: var(--ink);
  font: 16px/1.58 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: var(--accent-dark); }
code {
  padding: 0.12em 0.36em;
  border-radius: 5px;
  background: #edf2f7;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.92em;
}
.site-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 12px 28px;
  border-bottom: 1px solid rgba(219, 226, 234, 0.84);
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(14px);
}
.brand {
  color: var(--ink);
  font-weight: 800;
  text-decoration: none;
  letter-spacing: 0;
  white-space: nowrap;
}
nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 4px;
}
nav a {
  padding: 7px 10px;
  border-radius: 999px;
  color: var(--muted);
  font-size: 0.88rem;
  text-decoration: none;
}
nav a:hover {
  background: var(--accent-soft);
  color: var(--accent-dark);
}
main {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
}
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.65fr);
  gap: 28px;
  align-items: stretch;
  padding: 56px 0 34px;
}
.hero-copy, .hero-panel, .section {
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: var(--shadow);
}
.hero-copy {
  min-height: 420px;
  padding: clamp(28px, 5vw, 56px);
  border-radius: 24px;
}
.eyebrow, .section-kicker {
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
h1, h2, h3 {
  margin: 0;
  line-height: 1.12;
  letter-spacing: 0;
}
h1 {
  max-width: 920px;
  margin-top: 12px;
  font-size: clamp(2.55rem, 7vw, 5.1rem);
}
h2 {
  margin-top: 8px;
  font-size: clamp(1.85rem, 4vw, 3rem);
}
h3 { font-size: 1.08rem; }
p {
  margin: 0;
  color: var(--muted);
}
.hero-lede {
  max-width: 780px;
  margin-top: 20px;
  font-size: clamp(1.04rem, 2vw, 1.28rem);
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 30px;
}
.button {
  display: inline-flex;
  align-items: center;
  min-height: 42px;
  padding: 10px 16px;
  border-radius: 999px;
  background: var(--accent-dark);
  color: white;
  font-weight: 700;
  text-decoration: none;
}
.button-secondary {
  border: 1px solid var(--line);
  background: white;
  color: var(--ink);
}
.hero-panel {
  display: grid;
  align-content: center;
  gap: 14px;
  padding: 26px;
  border-radius: 24px;
}
.panel-row {
  display: grid;
  gap: 4px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--line);
}
.panel-row:last-child { border-bottom: 0; padding-bottom: 0; }
.panel-row span {
  color: var(--muted);
  font-size: 0.82rem;
}
.panel-row strong {
  overflow-wrap: anywhere;
  font-size: 0.98rem;
}
.section {
  margin: 24px 0;
  padding: clamp(24px, 4vw, 42px);
  border-radius: 22px;
}
.section > p {
  max-width: 900px;
  margin-top: 14px;
  font-size: 1.03rem;
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-top: 26px;
}
.metric-card {
  display: grid;
  gap: 10px;
  min-height: 236px;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper-soft);
}
.metric-win { background: linear-gradient(180deg, var(--green-soft), white); }
.metric-method { background: linear-gradient(180deg, var(--blue-soft), white); }
.metric-label {
  color: var(--muted);
  font-size: 0.82rem;
  font-weight: 800;
  text-transform: uppercase;
}
.metric-value {
  font-size: clamp(1.75rem, 4vw, 2.55rem);
  font-weight: 850;
  line-height: 1;
}
.tag {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  padding: 5px 9px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: white;
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 800;
}
.tag-win { border-color: #b8dec6; background: var(--green-soft); color: var(--green); }
.tag-method { border-color: #c4d5f4; background: var(--blue-soft); color: var(--blue); }
.feature-grid, .class-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-top: 24px;
}
.class-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.feature-card, .class-card {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper-soft);
}
.feature-card h3, .class-card h3 { margin-bottom: 10px; }
.api-chip {
  margin: 10px 0 12px;
  overflow-wrap: anywhere;
}
.callout {
  margin-top: 22px;
  padding: 16px 18px;
  border: 1px solid #ead099;
  border-radius: 16px;
  background: var(--amber-soft);
  color: #5c400e;
}
.table-scroll {
  width: 100%;
  margin-top: 18px;
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: white;
}
.data-table, .appendix table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
}
caption {
  padding: 12px 14px;
  color: var(--muted);
  text-align: left;
}
th, td {
  padding: 11px 13px;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
}
th {
  background: #eef3f8;
  color: #334155;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
tr:last-child td { border-bottom: 0; }
tbody tr:nth-child(even) td { background: #fafbfd; }
.evidence-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 24px;
}
.evidence-card {
  padding: 20px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper-soft);
}
.evidence-card header {
  display: grid;
  gap: 10px;
  margin-bottom: 14px;
}
dl {
  display: grid;
  gap: 11px;
  margin: 0;
}
dt {
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
}
dd {
  margin: 2px 0 0;
}
.split-section {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(300px, 0.75fr);
  gap: 26px;
}
.status-stack {
  display: grid;
  gap: 12px;
}
.status-card {
  display: grid;
  grid-template-columns: 90px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 16px;
}
.status-card strong { font-size: 1rem; }
.status-card span { color: var(--muted); }
.status-good { background: var(--green-soft); }
.status-watch { background: var(--amber-soft); }
.status-bad { background: var(--red-soft); }
.appendix details {
  margin-top: 18px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: white;
}
.appendix summary {
  cursor: pointer;
  padding: 16px 18px;
  font-weight: 800;
}
.appendix-body {
  padding: 0 22px 24px;
  border-top: 1px solid var(--line);
}
.appendix-body h1, .appendix-body h2, .appendix-body h3 {
  margin-top: 1.4em;
}
.appendix-body h1 { font-size: 2rem; }
.appendix-body h2 { font-size: 1.5rem; }
.appendix-body h3 { font-size: 1.2rem; }
pre {
  overflow: auto;
  padding: 16px;
  border-radius: 12px;
  background: #111827;
  color: #f8fafc;
}
pre code {
  padding: 0;
  background: transparent;
  color: inherit;
}
.source-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}
.source-links a {
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: white;
  text-decoration: none;
}
@media (max-width: 980px) {
  .site-header {
    position: static;
    align-items: flex-start;
    flex-direction: column;
  }
  nav { justify-content: flex-start; }
  .hero,
  .split-section {
    grid-template-columns: 1fr;
  }
  .summary-grid,
  .feature-grid,
  .class-grid,
  .evidence-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 640px) {
  body { font-size: 15px; }
  main { width: min(100% - 20px, 1180px); }
  .hero { padding-top: 20px; }
  .hero-copy, .hero-panel, .section { border-radius: 18px; }
  .summary-grid,
  .feature-grid,
  .class-grid,
  .evidence-list {
    grid-template-columns: 1fr;
  }
  .status-card { grid-template-columns: 1fr; }
  .data-table, .appendix table { min-width: 620px; }
}
@media print {
  body { background: white; }
  .site-header { position: static; }
  .hero-copy, .hero-panel, .section { box-shadow: none; }
  details:not([open]) .appendix-body { display: block; }
}
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
    title = "Rift Performance Evaluation Report"
    output.write_text(build_html(source, markdown, title), encoding="utf-8")
    print(f"Generated {output} from {source}")


if __name__ == "__main__":
    main()
