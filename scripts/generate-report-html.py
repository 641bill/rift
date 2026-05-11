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
    ("executive-summary", "Summary"),
    ("motivation", "Motivation"),
    ("background", "Background"),
    ("question", "Question"),
    ("approach", "Approach"),
    ("design", "Design"),
    ("evaluation", "Evaluation"),
    ("results", "Results"),
    ("limitations", "Limitations"),
    ("takeaway", "Takeaway"),
    ("appendix", "Sources"),
]


THESIS = (
    "This project asks whether a Scala Native system can use statically checked "
    "regions to reclaim stream-processing objects in bulk, avoiding garbage "
    "collection work without giving up memory safety."
)


SUMMARY_CARDS = [
    {
        "label": "Problem",
        "value": "GC overhead in structured streams",
        "detail": "Many dataflow programs allocate short-lived or epoch-local records whose lifetimes are visible at the operator boundary.",
        "claim": "Systems + PL motivation",
        "tone": "method",
    },
    {
        "label": "Prototype",
        "value": "Checked stream regions",
        "detail": "Rift adds checked epoch and page/window APIs on top of Scala Native runtime allocation backends.",
        "claim": "Static safety plus region allocation",
        "tone": "method",
    },
    {
        "label": "Best real-input result",
        "value": "16.12s vs 18.79s",
        "detail": "Yak LiveJournal graph replay: checked epoch scoped beats the garbage-collected heap and cuts resident memory.",
        "claim": "Real-input throughput + RSS win",
        "tone": "win",
    },
    {
        "label": "Most controlled reclaim test",
        "value": "0.47s vs 0.70s",
        "detail": "Both heap and regions retain ordinary objects until close; checked regions bulk-close them faster.",
        "claim": "Memory-management evidence",
        "tone": "win",
    },
]


CONTEXT_BOXES = [
    (
        "Garbage collection (GC)",
        "A runtime service that finds unreachable heap objects and reclaims them. GC is convenient, but tracing and pauses can cost time and memory on allocation-heavy workloads.",
    ),
    (
        "Region",
        "A memory area whose objects are reclaimed together. If all objects in a stream epoch or window die together, the runtime can close the region in bulk.",
    ),
    (
        "Static checking",
        "Compile-time capture and separation rules reject references that would outlive their region, such as storing an epoch object into a long-lived heap object.",
    ),
    (
        "RSS",
        "Resident set size: the operating-system memory footprint of the process. Lower RSS can matter even when elapsed time is tied.",
    ),
]


APPROACH_STEPS = [
    ("Expose lifetimes", "Programmers use checked APIs such as epoch and page/window regions to state where stream objects should die."),
    ("Check safety", "Compiler/runtime tests reject escaping region references, stale tokens, and unsafe mixed heap-region references."),
    ("Lower to fast backends", "The prototype lowers checked APIs to Rift streaming regions or SafeZone-family scoped allocation backends."),
    ("Compare fairly", "Benchmarks include natural heap baselines, same-shape heap controls, and retained-object controls before making memory-management claims."),
]


DESIGN_CARDS = [
    {
        "title": "Epoch API",
        "api": "RiftRegion.epoch { ... }",
        "body": "For graph steps, dataflow batches, and transactions. Objects allocated inside the epoch are consumed before the epoch closes.",
    },
    {
        "title": "Page/window API",
        "api": "checked page/window token",
        "body": "For streams where a page, record group, or time bucket owns many short-lived records that can be closed together.",
    },
    {
        "title": "Retained-object control",
        "api": "heap retained/drop-anchor vs checked retained",
        "body": "Both sides materialize and retain ordinary objects until the boundary. This isolates GC reclaim from algorithmic shortcut wins.",
    },
    {
        "title": "Backend selection",
        "api": "checked-region-scoped or checked-region-stream",
        "body": "The user-facing API is checked; the runtime backend can be selected by evidence. Unsafe rootless modes are lower-bound controls only.",
    },
]


EVALUATION_ROWS = [
    [
        "Main baseline",
        "Scala Native Immix garbage-collected heap (`gc-heap`).",
        "Shows whether regions beat the normal memory manager a Scala Native user would get.",
    ],
    [
        "Safe region baseline",
        "Rooted SafeZone-family scoped allocation (`region-scoped-rooted`).",
        "Separates the checked API contribution from the underlying region allocator.",
    ],
    [
        "Checked candidates",
        "Checked epoch, checked page/window token, checked scoped backend, checked top-k API.",
        "These are the rows that can support user-facing system claims.",
    ],
    [
        "Measurement levels",
        "L1 final-clean timing/RSS; L2 standard GC/region stats; L3 diagnostics; L4 sampled profiles.",
        "Prevents instrumentation overhead from becoming the headline result.",
    ],
]


RESULT_ROWS = [
    [
        "Real graph replay",
        "Yak LiveJournal, real SNAP graph input, 50M replayed edges.",
        "Checked epoch scoped: `16.12s`, RSS about `612 MB`.",
        "GC heap: `18.79s`, RSS about `2.77 GB`.",
        "The strongest real-input result: epoch regions improve both time and memory footprint.",
    ],
    [
        "Real text top-word",
        "Stack Exchange AskUbuntu `Posts.xml`, 10M real tokens x5.",
        "Checked epoch scoped: `3.86s`, RSS about `94 MB`.",
        "GC heap: `4.19s`, RSS about `428 MB`.",
        "First real text/top-word row: direct checked epoch wins; reusable top-k is lower-RSS but still slower than direct epoch.",
    ],
    [
        "Controlled retained-object reclaim",
        "Focused retained-epoch matrix, 1M ordinary records x20.",
        "Checked scoped retained/drop-anchor: `0.47s`.",
        "Heap retained/drop-anchor: `0.70s`.",
        "This is the cleanest memory-management comparison because both sides retain objects until close.",
    ],
    [
        "Prior-work-shaped dataflow",
        "SELECT / AGGREGATE / JOIN, 1M documents x20.",
        "Checked epoch scoped: `0.38 / 0.69 / 0.39s`.",
        "GC heap: `0.62 / 1.10 / 0.55s`.",
        "The epoch API generalizes beyond one benchmark to dataflow-style operators.",
    ],
    [
        "Generated object-pressure stream",
        "Common Crawl WET-shaped generated q1/q2, 1M pages.",
        "Checked page-token stream: `4.02 / 4.16s`.",
        "GC heap: `5.68 / 5.53s`.",
        "Shows the intended high-allocation stream regime, but it is generated, not a real-data proof.",
    ],
    [
        "Real log top-k",
        "LogHub HDFS top templates, real HDFS logs, 1M x20.",
        "Checked top-k scoped API: `4.88s`, RSS about `28 MB`.",
        "Retained heap: `5.52s`, RSS about `205 MB`.",
        "A reusable top-k API can keep most of the retained-region benefit on real logs.",
    ],
]


REAL_INPUT_ROWS = [
    ["Yak LiveJournal", "Real SNAP graph input", "Strong checked epoch time and RSS win", "Flagship real-input row."],
    ["AskUbuntu topwordreal", "Real Stack Exchange text", "Checked epoch time/RSS win", "First real text/top-word row; not exact Yak/Hadoop."],
    ["LogHub HDFS top templates", "Real LogHub HDFS logs", "Modest time win and large RSS reduction", "Promising reusable top-k API row."],
    ["LogHub HDFS q2", "Real LogHub HDFS logs", "Elapsed tie, strong RSS reduction", "Useful page/window control."],
    ["GH Archive", "Real NDJSON events", "Small time/RSS wins; parser CPU dominates", "Useful but not GC-heavy enough yet."],
    ["Common Crawl WET/WAT", "Real archive shards", "Current real rows are GC-light", "Ceiling/control, not a flagship result."],
]


LIMITATIONS = [
    "The best GC-heavy page/window stream result is still generated, so it demonstrates a workload regime rather than a real-data case study.",
    "Some real inputs are dominated by parsing, hashing, or query CPU, so removing GC does not automatically produce large elapsed-time wins.",
    "Unsafe/rootless region modes are useful lower bounds but are not user-facing safety claims.",
    "Rank, median, hash-join, and table-heavy operators still need focused API gates before they can support application claims.",
    "The ReML/MLKit comparison table is still being assembled; cross-language raw wall-clock comparisons will be treated as contextual, not definitive.",
]


OPEN_WORK_ROWS = [
    ["Finalize L1 rows", "Finish final-clean headline runs for the selected representative API wins."],
    ["Find a stronger real stream input", "Continue with larger LiveJournal/SNAP, richer LogHub sessions/templates, Theodolite traces, and DSPBench kernels."],
    ["Complete ReML/MLKit table", "Separate paper-reported, exact artifact rerun, and Scala Native port evidence."],
    ["Gate complex operators", "Only headline rank/hash/median/join after natural heap, same-shape heap, retained controls, and focused 1M API gates."],
]


def tag(text: str, tone: str = "neutral") -> str:
    return f'<span class="tag tag-{attr(tone)}">{esc(text)}</span>'


def figure_block(caption: str, body: str, so_what: str) -> str:
    return f'''<figure class="figure-block">
  <figcaption>{esc(caption)}</figcaption>
  {body}
  <p class="so-what"><strong>So what?</strong> {esc(so_what)}</p>
</figure>'''


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
    return figure_block(
        "Figure 1. Executive summary cards. Read these as the whole talk in four claims.",
        "\n".join(parts),
        "The project has a clear systems question, a checked-region prototype, and two kinds of current wins: real-input epoch wins and controlled memory-management wins.",
    )


def render_context_boxes() -> str:
    parts = ['<div class="context-grid">']
    for title, body in CONTEXT_BOXES:
        parts.append(
            f'''<article class="context-box">
  <h3>{esc(title)}</h3>
  <p>{esc(body)}</p>
</article>'''
        )
    parts.append("</div>")
    return figure_block(
        "Figure 2. Minimal background vocabulary.",
        "\n".join(parts),
        "The rest of the report only needs these concepts: GC, regions, static safety checks, and RSS.",
    )


def render_approach_steps() -> str:
    parts = ['<div class="flow-grid">']
    for index, (title, body) in enumerate(APPROACH_STEPS, start=1):
        parts.append(
            f'''<article class="flow-card">
  <div class="flow-number">{index}</div>
  <h3>{esc(title)}</h3>
  <p>{esc(body)}</p>
</article>'''
        )
    parts.append("</div>")
    return figure_block(
        "Figure 3. What was built and tested.",
        "\n".join(parts),
        "The contribution is not a benchmark rewrite; it is a checked API plus backend lowering and a fair comparison protocol.",
    )


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
    return figure_block(
        "Figure 4. User-facing region topologies and controls.",
        "\n".join(parts),
        "Different workloads need different lifetimes. The API should expose epoch, page/window, and retained-object shapes instead of forcing one region topology everywhere.",
    )


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


def render_table_block(
    headers: list[str],
    rows: list[list[str]],
    caption: str,
    so_what: str,
) -> str:
    body = render_table(headers, rows)
    return figure_block(caption, body, so_what)


def render_evaluation_table() -> str:
    rows = [[esc(a), inline_markdown(b), esc(c)] for a, b, c in EVALUATION_ROWS]
    return render_table_block(
        ["Evaluation component", "What was measured", "Why it matters"],
        rows,
        "Table 1. Evaluation setup and baselines.",
        "The report separates user-facing checked rows from allocator lower bounds and separates clean headline timing from diagnostic counters.",
    )


def render_results_table() -> str:
    rows = [
        [esc(a), esc(b), inline_markdown(c), inline_markdown(d), esc(e)]
        for a, b, c, d, e in RESULT_ROWS
    ]
    return render_table_block(
        ["Result", "Workload", "Best checked row", "Baseline/control", "Interpretation"],
        rows,
        "Table 2. Five results to remember.",
        "The current story is strongest for epochal graph/dataflow/transaction shapes and controlled retained-object reclaim; generated stream pressure is promising but not yet real-input proof.",
    )


def render_real_input_table() -> str:
    rows = [[esc(a), esc(b), esc(c), esc(d)] for a, b, c, d in REAL_INPUT_ROWS]
    return render_table_block(
        ["Benchmark", "Input", "Current result", "Report status"],
        rows,
        "Table 3. Real-input evidence status.",
        "Real datasets are not automatically GC-heavy. The strongest real row is LiveJournal; several others are useful RSS or ceiling controls.",
    )


def render_open_work() -> str:
    rows = [[esc(a), esc(b)] for a, b in OPEN_WORK_ROWS]
    return render_table_block(
        ["Open track", "Next action"],
        rows,
        "Table 4. Work remaining before a final paper-style evaluation.",
        "The next work is about finalizing evidence quality and extending real inputs, not adding benchmark-specific shortcuts.",
    )


def render_limitations() -> str:
    parts = ['<ul class="limitations-list">']
    for item in LIMITATIONS:
        parts.append(f"<li>{esc(item)}</li>")
    parts.append("</ul>")
    return figure_block(
        "Figure 5. What these results do not prove yet.",
        "\n".join(parts),
        "The prototype has encouraging evidence, but the final claim should stay narrower than 'regions always beat GC'.",
    )


def render_nav() -> str:
    return "\n".join(
        f'<a href="#{attr(anchor)}">{esc(label)}</a>' for anchor, label in NAV
    )


def build_html(source: Path, markdown: str, title: str) -> str:
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
        <h1>Can checked regions make stream processing cheaper than garbage collection?</h1>
        <div class="thesis-strip">
          <span>One-sentence thesis</span>
          <p>{esc(THESIS)}</p>
        </div>
        <p class="hero-lede">
          A self-contained 10-minute research presentation for systems and
          programming-languages readers with no prior project context.
        </p>
        <div class="hero-actions">
          <a class="button" href="#results">View main results</a>
          <a class="button button-secondary" href="PERFORMANCE_EVALUATION_REPORT.md">Open source Markdown</a>
        </div>
      </div>
      <aside class="hero-panel" aria-label="Report metadata">
        <div class="panel-row"><span>Generated</span><strong>{esc(generated)}</strong></div>
        <div class="panel-row"><span>Source</span><strong>{esc(source)}</strong></div>
        <div class="panel-row"><span>Audience</span><strong>External systems / PL reader</strong></div>
        <div class="panel-row"><span>Headline rule</span><strong>Clean total time and RSS first</strong></div>
      </aside>
    </section>

    <section id="executive-summary" class="section">
      <div class="section-kicker">Executive summary</div>
      <h2>The result in one slide</h2>
      <p>
        The prototype shows that checked region APIs can beat the garbage-
        collected heap when a workload has explicit epoch, transaction, page,
        or window lifetimes. The strongest evidence is not "regions always
        win"; it is that the right checked topology can remove GC reclaim work
        and reduce resident memory without resorting to unsafe manual memory
        management.
      </p>
      {render_summary_cards()}
    </section>

    <section id="motivation" class="section split-section">
      <div>
        <div class="section-kicker">Motivation</div>
        <h2>Many streaming systems allocate data whose lifetime is already structured</h2>
        <p>
          Garbage collection is a strong default for general-purpose programs,
          but data processing often has explicit lifetime boundaries: an epoch
          ends, a window closes, or a transaction commits. In those cases, a
          runtime may be able to reclaim many ordinary objects together rather
          than tracing them one by one.
        </p>
      </div>
      <div class="context-box emphasis-box">
        <h3>Why this matters</h3>
        <p>
          This is a systems and programming-languages question: can we expose
          lifetimes in the programming model, check them statically, and lower
          them to faster memory management without making users write unsafe
          manual allocation code?
        </p>
      </div>
    </section>

    <section id="background" class="section">
      <div class="section-kicker">Background</div>
      <h2>Only four concepts are needed</h2>
      {render_context_boxes()}
    </section>

    <section id="question" class="section">
      <div class="section-kicker">Research question</div>
      <h2>Can checked regions win on the workloads they are designed for?</h2>
      <div class="research-question">
        <p>
          <strong>Question.</strong> When stream/dataflow objects have visible
          epoch, page, transaction, or window lifetimes, can a checked region
          API outperform Scala Native's Immix garbage-collected heap, while
          preserving safety and using fair same-shape controls?
        </p>
      </div>
      <p>
        The report therefore distinguishes memory-management wins from
        algorithmic or topology wins. If a result depends on summarizing data
        early or avoiding object retention entirely, it is useful but it is not
        reported as a GC-reclaim win.
      </p>
    </section>

    <section id="approach" class="section">
      <div class="section-kicker">Approach</div>
      <h2>Build a checked API, then compare it against fair heap baselines</h2>
      <p>
        Rift is a Scala Native prototype. It adds checked region-shaped APIs
        and benchmark modes that lower those APIs to runtime allocation
        backends. The important methodological choice is that headline rows use
        reusable framework APIs, not benchmark-local manual arrays or one-off
        count loops.
      </p>
      {render_approach_steps()}
    </section>

    <section id="design" class="section">
      <div class="section-kicker">Key design idea</div>
      <h2>Use static safety to remove runtime memory bookkeeping</h2>
      <p>
        The novel part is not just "allocate in a region." The useful part is a
        checked API that proves which references cannot escape. Under those
        invariants, the runtime can avoid escape tables, promotion barriers,
        heap-to-region tracking tables, close-time object scans, and hot-path
        stale-token checks inside operator-owned paths.
      </p>
      {render_design_cards()}
    </section>

    <section id="evaluation" class="section">
      <div class="section-kicker">Evaluation setup</div>
      <h2>Measure clean process time first, then explain it with diagnostics</h2>
      <p>
        Headline elapsed time and resident set size (RSS) come from final-clean
        runs with no profiling, tracing, attribution, or internal diagnostic
        timers in the timed section. Garbage collection and region counters are
        reported separately as interpretation evidence.
      </p>
      {render_evaluation_table()}
    </section>

    <section id="results" class="section">
      <div class="section-kicker">Main results</div>
      <h2>The important numbers fit on one table</h2>
      <p>
        The strongest current story has five representative rows: one real
        graph workload, one controlled retained-object reclaim test, two
        prior-work-shaped methodology groups, one generated high-allocation
        stream stressor, and one real log top-k workload.
      </p>
      {render_results_table()}
    </section>

    <section id="real-input" class="section">
      <div class="section-kicker">Real-data status</div>
      <h2>Real inputs help, but many are not GC-heavy enough</h2>
      <p>
        A recurring finding is that public real inputs often spend most time in
        parsing, hashing, or query logic. Those rows are still useful: they can
        show memory-footprint wins, tail behavior, or ceiling cases where GC is
        not the dominant cost.
      </p>
      {render_real_input_table()}
    </section>

    <section id="limitations" class="section">
      <div class="section-kicker">Limitations</div>
      <h2>What this does not prove yet</h2>
      {render_limitations()}
    </section>

    <section id="takeaway" class="section">
      <div class="section-kicker">Takeaway</div>
      <h2>Checked regions are promising when lifetimes are part of the program structure</h2>
      <div class="takeaway-panel">
        <p>
          The current evidence supports a precise claim: for stream/dataflow
          workloads with explicit epoch, page/window, or transaction lifetimes,
          a checked region API can remove GC reclaim work and reduce memory
          footprint while preserving safety. The remaining research work is to
          finish the clean evaluation, find more real GC-heavy inputs, and gate
          more complex operators without relying on benchmark-specific tricks.
        </p>
      </div>
      {render_open_work()}
    </section>

    <section id="appendix" class="section appendix">
      <div class="section-kicker">Sources and provenance</div>
      <h2>Where the detailed evidence lives</h2>
      <p>
        This HTML file is intentionally a 10-minute presentation report, not a
        dump of every benchmark table. The source Markdown and evidence files
        remain the archival record for full commands, row classifications, and
        run provenance.
      </p>
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
figure {
  margin: 0;
}
.hero-lede {
  max-width: 780px;
  margin-top: 20px;
  font-size: clamp(1.04rem, 2vw, 1.28rem);
}
.thesis-strip {
  max-width: 840px;
  margin-top: 20px;
  padding: 16px 18px;
  border: 1px solid #c4d5f4;
  border-radius: 18px;
  background: var(--blue-soft);
}
.thesis-strip span {
  display: block;
  margin-bottom: 6px;
  color: var(--blue);
  font-size: 0.76rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.thesis-strip p {
  color: #26364f;
  font-size: 1.04rem;
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
.figure-block {
  margin-top: 24px;
}
.figure-block > figcaption {
  margin-bottom: 12px;
  color: #334155;
  font-size: 0.9rem;
  font-weight: 800;
}
.so-what {
  margin-top: 12px;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: #f8fafc;
  color: #334155;
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
.context-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}
.feature-card, .class-card {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper-soft);
}
.context-box {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper-soft);
}
.emphasis-box {
  background: linear-gradient(180deg, var(--blue-soft), white);
}
.feature-card h3, .class-card h3, .context-box h3 { margin-bottom: 10px; }
.api-chip {
  margin: 10px 0 12px;
  overflow-wrap: anywhere;
}
.research-question {
  margin-top: 22px;
  padding: 20px;
  border: 1px solid #c4d5f4;
  border-radius: 18px;
  background: var(--blue-soft);
}
.research-question p {
  color: #24334d;
  font-size: 1.08rem;
}
.flow-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}
.flow-card {
  position: relative;
  padding: 46px 18px 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper-soft);
}
.flow-number {
  position: absolute;
  top: 14px;
  left: 18px;
  display: grid;
  width: 26px;
  height: 26px;
  place-items: center;
  border-radius: 999px;
  background: var(--accent-dark);
  color: white;
  font-size: 0.82rem;
  font-weight: 800;
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
.limitations-list {
  display: grid;
  gap: 10px;
  margin: 0;
  padding-left: 1.2rem;
  color: var(--muted);
}
.limitations-list li {
  padding-left: 4px;
}
.takeaway-panel {
  margin-top: 20px;
  padding: clamp(20px, 3vw, 30px);
  border: 1px solid #b8dec6;
  border-radius: 20px;
  background: linear-gradient(180deg, var(--green-soft), white);
}
.takeaway-panel p {
  max-width: 980px;
  color: #1d4430;
  font-size: 1.12rem;
}
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
  .context-grid,
  .flow-grid,
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
  .context-grid,
  .flow-grid,
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
