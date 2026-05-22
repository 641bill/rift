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
    ("region-inference", "Inference"),
    ("evaluation", "Evaluation"),
    ("results", "Results"),
    ("limitations", "Limitations"),
    ("takeaway", "Takeaway"),
    ("appendix", "Sources"),
]


THESIS = (
    "Rift asks whether Scala Native programs can use statically checked "
    "lifetime boundaries and capture-directed inference to move proven "
    "epoch/page/window objects out of Immix, reclaim them in bulk, and keep "
    "all unproven allocations on the GC heap."
)


SUMMARY_CARDS = [
    {
        "label": "Problem",
        "value": "Immix is strong, but lifetimes are visible",
        "detail": "Rift targets rows where stream/dataflow objects share an epoch, page, window, transaction, or retained-query lifetime.",
        "claim": "Systems + PL target",
        "tone": "method",
    },
    {
        "label": "Prototype",
        "value": "Checked regions + inference",
        "detail": "Scala Native runtime regions, checked APIs, NIR lowering, diagnostics, and conservative heap fallback are implemented.",
        "claim": "Working implementation",
        "tone": "method",
    },
    {
        "label": "Latest retained result",
        "value": "862ms vs 1071ms",
        "detail": "Broom aggregate 10M in the latest current-state matrix: checked Rift removes timed GC and cuts RSS from 148.7 MB to 16.4 MB.",
        "claim": "Retained dataflow win",
        "tone": "win",
    },
    {
        "label": "Latest real/local rows",
        "value": "274s vs 306s",
        "detail": "DSPBench Log q2 10M file-backed replay: checked Rift page-token beats Immix and SafeZone while reducing timed GC.",
        "claim": "Real/local stream win",
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


PRIOR_WORK_METRIC_ROWS = [
    [
        "Broom / Dataflow",
        "Real time, throughput, GC share/count, RSS, operator lifetime boundary.",
        "Retained timestamped aggregate/join and SELECT/AGGREGATE/JOIN rows.",
    ],
    [
        "StreamFlex",
        "Throughput, p50/p95/p99/p999/max latency, deadline misses, GC max/count, RSS.",
        "StreamFlexDesign stable/transient/capsule throughput and pressure-latency rows.",
    ],
    [
        "Yak",
        "App time, GC time/count, epoch boundary, peak RSS.",
        "LiveJournal graph replay and AskUbuntu/topword epoch rows.",
    ],
    [
        "Stancu / SPECjbb-style",
        "Real time, GC time/count, RSS, region-freed object/byte proxy, max live region payload, API/annotation burden.",
        "Stancu transactions and clean-room SPECjbb2005 workload port.",
    ],
    [
        "ReML / MLKit",
        "Program, LOC/source status, real time, RSS, GC count, region-vs-heap ratios.",
        "Same-axes PLDI-style table with local Scala Native ports where available.",
    ],
]


APPROACH_STEPS = [
    ("Expose lifetimes", "Programmers use checked APIs such as epoch and page/window regions to state where stream objects should die."),
    ("Check safety", "Compiler/runtime tests reject escaping region references, stale tokens, and unsafe mixed heap-region references."),
    ("Select safe backends", "The user-facing system is Rift; checked stream and checked scoped rows are backend choices selected by API shape and evidence."),
    ("Compare fairly", "Headline rows compare natural heap/GC against checked Rift with the same logical program. Mechanism controls stay in appendix tables."),
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
        "title": "Retained-object query",
        "api": "natural heap vs checked retained regions",
        "body": "The natural program materializes ordinary objects until a boundary; checked Rift places those data-path objects in regions and keeps durable control state on heap.",
    },
    {
        "title": "Backend selection",
        "api": "fastest safe backend for the shape",
        "body": "Checked scoped and checked stream are implementation choices under the Rift umbrella. If scoped wins, profile it and improve the Rift backend rather than presenting a separate system.",
    },
    {
        "title": "StreamFlex design",
        "api": "stable heap + transient epoch + capsule",
        "body": "For filter pipelines: durable state stays on heap, transient packet/feature/decision objects live in epochs, and bounded capsules export values across boundaries.",
    },
    {
        "title": "Throughput policy",
        "api": "RIFT_REGION_REUSE_POLICY",
        "body": "Opt-in slab reuse policies trade resident memory budget for lower allocator bookkeeping. The cache-large policy is currently a focused allocator win, not a default application claim.",
    },
]


INFERENCE_DONE_ROWS = [
    ["Expected-type local placement", "`val x: T^{r} = new T(...)` lowers into the checked region when `r` has a runtime owner term."],
    ["Branch/match placement", "All paths can allocate into a checked region when they prove the same owner."],
    ["Method/effect summaries", "Direct, returned-local, forwarding, branch/match, and selected local factory summaries are implemented."],
    ["Owner-token call sites", "Arguments to checked owner-token methods can be placed through the actual runtime owner argument."],
    ["Framework/operator owners", "Page-token, epoch-buffer, buffer, priority-queue, rank/table, and retained helpers recover the operator-owned region."],
    ["Synthetic allocations", "`Some`, `Option.apply`, `None`, `Tuple2`-`Tuple22`, arrays, generic cells, and wrapper records are covered in owner-proven shapes."],
    ["Closure placement", "Nonescaping closure objects and narrow captured-owner closure-body allocations are covered."],
    ["Diagnostics", "`-P:scalanative:riftInferReport` reports region, heap, unknown, and rejected placement decisions."],
]


INFERENCE_LEFT_ROWS = [
    ["Closure/effect summaries", "Finish escaping-safe closures, closure-body effects, hidden owner capture, and lambda environment rewriting."],
    ["Type-only owner recovery", "Recover a runtime owner when `T^{r}` has a unique owner term; otherwise keep heap fallback."],
    ["General callee summaries", "Support more callees, forwarding wrappers, helper libraries, and selected framework boundaries."],
    ["Polymorphic safety", "Stay conservative across virtual dispatch, mutation, callbacks, exceptions, erased generics, and generic containers."],
    ["Boxes and libraries", "Handle primitive boxes, boxed keys, iterators, collection nodes, strings, buffers, and parser helpers."],
    ["Evidence", "Keep expanding positive allocation-stat tests and negative safety tests before relaxing runtime checks."],
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
    [
        "Presentation audit",
        "Representative rows are checked for L1 elapsed/RSS, L2 GC/region interpretation, input type, API/workload shape, comparison class, and allowed claim.",
        "Prevents stale L2-only, legacy, or lower-bound rows from being mistaken for final evidence.",
    ],
    [
        "ReML same-axes table",
        "The PLDI Figure 9 program list keeps paper `loc`/`fcns`/`inst`/time/RSS/GC axes and adds local `gc-heap`, rooted-region, checked-stream, and checked-scoped time/RSS/GC columns where ports exist.",
        "Explains why Rift is better, worse, neutral, or unavailable without claiming raw cross-language wall-clock wins.",
    ],
    [
        "Throughput/RSS policies",
        "`RIFT_REGION_REUSE_POLICY` reports default, bulk-zero, cache-small, cache-large, and prezero-large rows as opt-in speed/RSS tradeoffs.",
        "Keeps throughput-biased allocation policies from being mistaken for lower-memory wins.",
    ],
]


ENFORCED_ROWS = [
    [
        "Actually enforced now",
        "Region values cannot escape their checked scope; heap/durable state cannot retain region values; nested region values cannot outlive parents; closure and polymorphic escapes are rejected by current compiler probes.",
        "Supports direct epoch, retained epoch, page/window token, and ReML-style safety claims.",
    ],
    [
        "Actually implemented/evaluated now",
        "Natural heap, checked `RiftRegion.epoch`, page/window token, checked scoped backend, checked stream backend, plus appendix-only same-shape/drop-anchor/summary/control modes.",
        "Headline rows use natural heap versus checked Rift. Backend and mechanism controls explain why a row wins or loses.",
    ],
    [
        "Defensive/runtime today",
        "Low-level public APIs still keep defensive checks; operator-owned paths remove hot-path checks only where the API controls bucket/epoch order.",
        "Avoids overstating static checking. Some runtime checks remain by design.",
    ],
    [
        "Design inspiration only",
        "Full active/closed typestate, transferable regions, concurrency ownership, and richer reference capabilities are not final user-facing Rift semantics yet.",
        "Use as proof/design vocabulary until measurements justify adding API complexity.",
    ],
]


REAL_RESULT_ROWS = [
    [
        "DSPBench Fraud q2",
        "Real bundled DSPBench credit-card file replayed to 10M events.",
        "Checked page-token: `187882.928 ms`; checked SafeZone page-token: `186988.431 ms`.",
        "Immix heap: `208405.569 ms`.",
        "Real/local stream win; SafeZone backend is slightly best for this row.",
    ],
    [
        "DSPBench Log q2",
        "Real bundled DSPBench HTTP log file replayed to 10M events.",
        "Checked page-token: `273860.718 ms`, GC `24816.086 ms`.",
        "Immix heap: `306392.943 ms`, GC `57338.467 ms`.",
        "Real/local stream win where checked Rift also beats the checked SafeZone row.",
    ],
    [
        "Theodolite q2 real time series",
        "UCI household-power streaming-file row, 2,049,280 records.",
        "Checked stream: `2160.896 ms`, RSS `80.4 MB`.",
        "Immix heap: `2256.219 ms`, RSS `147.9 MB`.",
        "Real time-series modest time win with clear RSS and GC reduction.",
    ],
]


RESULT_ROWS = [
    [
        "Broom retained aggregate/join",
        "Timestamped retained aggregate and join records, 10M events.",
        "Checked Rift: `862.143 / 896.583 ms`, RSS `16.4 / 15.1 MB`.",
        "Immix heap: `1071.498 / 1043.463 ms`, RSS `148.7 / 76.9 MB`.",
        "Retained dataflow win: checked Rift removes timed GC and cuts RSS substantially.",
    ],
    [
        "StreamFlexDesign",
        "Stable heap state plus transient period objects and capsule transfer, 10M events.",
        "Checked stream throughput: `3800.585 ms`; pressure-latency misses `4`.",
        "Immix heap throughput: `5138.231 ms`; pressure-latency misses `72`.",
        "Stream lifetime win: checked periods reduce GC and deadline/tail pressure.",
    ],
    [
        "Common Crawl-shaped q1/q2",
        "Generated WET-shaped tokenization and domain-window stressors, 10M pages.",
        "Checked page-token: `46491.537 / 46094.232 ms`.",
        "Immix heap: `70410.059 / 67398.152 ms`.",
        "Generated object-pressure win: page/window objects share clear lifetimes; not real-input proof.",
    ],
    [
        "Generated LogHub q2/q3",
        "Window-count and template/session log-shaped generated queries, 10M events.",
        "Checked epoch stream: `2600.244 / 26291.412 ms`.",
        "Immix heap: `6677.914 / 32867.576 ms`.",
        "Strong stream/operator win; q3 still has large query/session CPU.",
    ],
    [
        "SPECjbb2005-style port",
        "Clean-room transaction-lifetime workload, 10M transactions.",
        "Checked epoch stream: `1231.076 ms`, GC `0.593 ms`.",
        "Immix heap: `1674.726 ms`, GC `206.437 ms`.",
        "Prior-work-style transaction win, not official SPECjbb2005 certification.",
    ],
    [
        "NEXMark generated queries",
        "Generated Beam-default q3/q8/q9/q11 stream methodology rows.",
        "Checked q3/q8/q9/q11: `2591 / 4157 / 7929 / 2188 ms`.",
        "Immix heap: `2848 / 4432 / 8790 / 2217 ms`.",
        "Checked beats heap on these rows, but q9 favors the scoped/SafeZone backend.",
    ],
    [
        "GH Archive-shaped q1/q2",
        "Generated/preloaded GH Archive-shaped event rows, 10M events.",
        "Checked page-token: `3822.250 / 3842.741 ms`.",
        "Immix heap: `3975.523 / 3848.235 ms`.",
        "Honest control: q1 small win, q2 tie; parser/query floor dominates.",
    ],
    [
        "Object allocation and append",
        "Primitive-field object allocation and append-window microbenchmarks.",
        "Checked allocation `161.281 ms`; append-window `252.007 ms`.",
        "Immix allocation `263.639 ms`; append-window `338.362 ms`.",
        "Runtime/API overhead wins after GC removal; checked SafeZone is still the lower-overhead substrate for pure allocation.",
    ],
    [
        "Window fold",
        "Checked fold/traversal microbenchmark, 10M objects.",
        "Checked Rift: `930.973 ms`.",
        "Immix heap: `898.906 ms`.",
        "Negative control: traversal/API overhead can exceed removed GC and remains an optimization target.",
    ],
]


REAL_INPUT_ROWS = [
    ["DSPBench Fraud q2", "Bundled real credit-card file replayed to 10M events", "Checked page-token is about 10% faster than Immix", "Real/local stream win; SafeZone backend slightly best."],
    ["DSPBench Log q2", "Bundled real HTTP log file replayed to 10M events", "Checked page-token beats Immix and checked SafeZone", "Strongest latest real/local DSPBench row."],
    ["Theodolite q2", "UCI household-power streaming-file input", "Checked stream modestly faster, with lower RSS and GC", "Real time-series row in latest matrix."],
    ["Wikimedia clickstream-session", "Compressed public Wikimedia clickstream TSV", "Prior 10M x3 checked Rift throughput/RSS/GC/fixed-memory win", "Named retained streaming row; not official Wikimedia artifact."],
    ["Yak LiveJournal", "Real SNAP graph input", "Prior checked epoch time and RSS win", "Real graph replay evidence."],
    ["AskUbuntu topwordreal", "Real Stack Exchange text", "Prior checked epoch time/RSS win", "Real text/top-word evidence; not exact Yak/Hadoop."],
]


LIMITATIONS = [
    "The latest full matrix was a dirty working-tree engineering run; rerun from a clean committed tree before treating the exact numbers as publication evidence.",
    "Rift is not full ReML/MLKit inference yet: broad closure/effect summaries, hidden/type-only owner recovery, primitive boxes, and library summaries remain open.",
    "Some rows are dominated by parsing, hashing, traversal, or query CPU, so removing GC does not guarantee an elapsed-time win.",
    "Unsafe/rootless rows remain lower-bound controls, not user-facing safety claims.",
    "Runtime checks stay unless compiler/runtime probes prove active-handle, stale-token, owner, and close-order invariants.",
]


OPEN_WORK_ROWS = [
    ["Clean final matrix", "Rerun the latest selected matrix from a clean committed tree and promote only validated rows."],
    ["Closure/effect summaries", "Finish escaping-closure summaries, hidden owner capture, type-only owner recovery, and lambda environment rewriting."],
    ["Library inference", "Handle primitive boxes, boxed keys, iterators, collection nodes, strings, buffers, parser helpers, wrappers, and erased generic paths."],
    ["Runtime overhead", "Reduce fold/traversal/capsule work, token/handle plumbing, and object init/zeroing only under proof-gated invariants."],
    ["Mechanized proof", "Complete the core containment, heap-root, owner-token, and close/reset safety argument."],
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
        "Figure 5. User-facing checked APIs and controls.",
        "\n".join(parts),
        "Different workloads need different lifetimes. The API should expose epoch, page/window, and retained-object shapes instead of forcing one allocation style everywhere.",
    )


def render_topology_story() -> str:
    parts = ['<div class="paper-figure-grid">']
    parts.append(
        '''<article class="paper-figure">
  <h3>Natural heap topology</h3>
  <svg viewBox="0 0 360 260" role="img" aria-label="Natural heap topology with temporary and durable objects mixed in one heap">
    <defs>
      <marker id="heapScanArrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L7,3 z" fill="#475569"></path>
      </marker>
    </defs>
    <rect x="28" y="28" width="304" height="178" rx="20" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="2"></rect>
    <text x="143" y="55" class="svg-title">Immix heap</text>
    <circle cx="76" cy="96" r="13" fill="#7e57c2"></circle><text x="72" y="101" class="node-text">C</text>
    <circle cx="122" cy="142" r="13" fill="#1f78b4"></circle><text x="118" y="147" class="node-text">r</text>
    <circle cx="170" cy="94" r="13" fill="#1f78b4"></circle><text x="166" y="99" class="node-text">r</text>
    <circle cx="218" cy="146" r="13" fill="#1f78b4"></circle><text x="214" y="151" class="node-text">r</text>
    <circle cx="270" cy="100" r="13" fill="#7e57c2"></circle><text x="266" y="105" class="node-text">T</text>
    <path d="M65 184 C118 217, 236 217, 292 184" fill="none" stroke="#475569" stroke-width="3" stroke-dasharray="7 6" marker-end="url(#heapScanArrow)"></path>
    <text x="72" y="232" class="svg-legend">temporary and durable objects share one heap</text>
    <text x="72" y="248" class="svg-legend">GC later traces dead records</text>
  </svg>
  <p>This is the baseline: durable control objects and short-lived records are mixed. The collector finds dead temporary objects later.</p>
</article>'''
    )
    parts.append(
        '''<article class="paper-figure">
  <h3>Direct epoch topology</h3>
  <svg viewBox="0 0 360 260" role="img" aria-label="Direct epoch topology with durable heap state and repeated epoch regions">
    <defs>
      <marker id="epochArrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L7,3 z" fill="#238443"></path>
      </marker>
    </defs>
    <rect x="22" y="24" width="316" height="54" rx="16" fill="#f1f5f9" stroke="#cbd5e1"></rect>
    <text x="64" y="57" class="svg-title">heap: durable tables and counters</text>
    <rect x="30" y="116" width="84" height="68" rx="16" fill="#e8f5ec" stroke="#8fc49c" stroke-width="2"></rect>
    <rect x="138" y="116" width="84" height="68" rx="16" fill="#e8f5ec" stroke="#8fc49c" stroke-width="2"></rect>
    <rect x="246" y="116" width="84" height="68" rx="16" fill="#e8f5ec" stroke="#8fc49c" stroke-width="2"></rect>
    <text x="52" y="145" class="svg-title">epoch 1</text>
    <text x="160" y="145" class="svg-title">epoch 2</text>
    <text x="268" y="145" class="svg-title">epoch 3</text>
    <circle cx="57" cy="166" r="7" fill="#1f78b4"></circle><circle cx="75" cy="166" r="7" fill="#1f78b4"></circle><circle cx="93" cy="166" r="7" fill="#1f78b4"></circle>
    <circle cx="165" cy="166" r="7" fill="#1f78b4"></circle><circle cx="183" cy="166" r="7" fill="#1f78b4"></circle><circle cx="201" cy="166" r="7" fill="#1f78b4"></circle>
    <circle cx="273" cy="166" r="7" fill="#1f78b4"></circle><circle cx="291" cy="166" r="7" fill="#1f78b4"></circle><circle cx="309" cy="166" r="7" fill="#1f78b4"></circle>
    <path d="M114 150 L137 150" stroke="#238443" stroke-width="4" marker-end="url(#epochArrow)"></path>
    <path d="M222 150 L245 150" stroke="#238443" stroke-width="4" marker-end="url(#epochArrow)"></path>
    <text x="47" y="222" class="svg-legend">open → allocate → update durable state → close</text>
    <text x="47" y="240" class="svg-legend">graph, dataflow, stream, and transaction rows</text>
  </svg>
  <p>Each batch or transaction gets one checked region. Durable state remains on heap; temporary records die when the epoch closes.</p>
</article>'''
    )
    parts.append(
        '''<article class="paper-figure">
  <h3>StreamFlex stable / transient / capsule topology</h3>
  <svg viewBox="0 0 360 260" role="img" aria-label="StreamFlex design topology with stable heap state, transient period region, and bounded capsule export">
    <defs>
      <marker id="capsuleArrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L7,3 z" fill="#238443"></path>
      </marker>
    </defs>
    <rect x="24" y="24" width="312" height="50" rx="15" fill="#f1f5f9" stroke="#cbd5e1"></rect>
    <text x="68" y="55" class="svg-title">heap stable state</text>
    <rect x="32" y="111" width="154" height="76" rx="18" fill="#e8f5ec" stroke="#8fc49c" stroke-width="2"></rect>
    <text x="58" y="139" class="svg-title">transient region</text>
    <circle cx="62" cy="164" r="7" fill="#1f78b4"></circle><circle cx="84" cy="164" r="7" fill="#1f78b4"></circle><circle cx="106" cy="164" r="7" fill="#1f78b4"></circle><circle cx="128" cy="164" r="7" fill="#1f78b4"></circle><circle cx="150" cy="164" r="7" fill="#1f78b4"></circle>
    <rect x="228" y="117" width="94" height="64" rx="16" fill="#dbeafe" stroke="#93b4e8" stroke-width="2"></rect>
    <text x="246" y="143" class="svg-title">capsule</text>
    <text x="241" y="163" class="svg-legend">bounded export</text>
    <path d="M186 150 L227 150" stroke="#238443" stroke-width="4" marker-end="url(#capsuleArrow)"></path>
    <path d="M275 117 C275 88, 216 76, 180 75" fill="none" stroke="#238443" stroke-width="3" marker-end="url(#capsuleArrow)"></path>
    <text x="38" y="218" class="svg-legend">packet → feature → decision objects live in period</text>
    <text x="38" y="236" class="svg-legend">export capsule values, then close region</text>
  </svg>
  <p>This is the new StreamFlex-design row: stable state is durable, transient objects die by period, and capsules make transfer explicit.</p>
</article>'''
    )
    parts.append(
        '''<article class="paper-figure">
  <h3>Retained epoch drop-anchor</h3>
  <svg viewBox="0 0 360 260" role="img" aria-label="Retained epoch topology with heap and region both retaining records until close">
    <defs>
      <marker id="dropArrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L7,3 z" fill="#238443"></path>
      </marker>
    </defs>
    <rect x="28" y="36" width="304" height="50" rx="14" fill="#f1f5f9" stroke="#cbd5e1"></rect>
    <text x="90" y="67" class="svg-title">bucket anchor</text>
    <circle cx="72" cy="142" r="15" fill="#1f78b4"></circle><text x="68" y="148" class="node-text">r</text>
    <circle cx="126" cy="142" r="15" fill="#1f78b4"></circle><text x="122" y="148" class="node-text">r</text>
    <circle cx="180" cy="142" r="15" fill="#1f78b4"></circle><text x="176" y="148" class="node-text">r</text>
    <circle cx="234" cy="142" r="15" fill="#1f78b4"></circle><text x="230" y="148" class="node-text">r</text>
    <path d="M87 142 L110 142" stroke="#334155" stroke-width="3" marker-end="url(#dropArrow)"></path>
    <path d="M141 142 L164 142" stroke="#334155" stroke-width="3" marker-end="url(#dropArrow)"></path>
    <path d="M195 142 L218 142" stroke="#334155" stroke-width="3" marker-end="url(#dropArrow)"></path>
    <path d="M180 86 L180 122" stroke="#238443" stroke-width="4" marker-end="url(#dropArrow)"></path>
    <rect x="268" y="122" width="54" height="40" rx="10" fill="#e8f5ec" stroke="#8fc49c"></rect>
    <text x="282" y="147" class="svg-title">close</text>
    <text x="43" y="208" class="svg-legend">heap: drop anchor, GC reclaims later</text>
    <text x="43" y="228" class="svg-legend">region: clear anchor, close now; no scan</text>
  </svg>
  <p>This is the fair memory-management test: both sides retain ordinary objects until close; only reclaim differs.</p>
</article>'''
    )
    parts.append(
        '''<article class="paper-figure">
  <h3>Page / window token topology</h3>
  <svg viewBox="0 0 360 260" role="img" aria-label="Page and window token topology with parent metadata and child bucket regions">
    <defs>
      <marker id="tokenArrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L7,3 z" fill="#238443"></path>
      </marker>
    </defs>
    <rect x="24" y="26" width="312" height="58" rx="16" fill="#f1f5f9" stroke="#cbd5e1"></rect>
    <text x="66" y="61" class="svg-title">parent bucket table</text>
    <rect x="32" y="124" width="82" height="68" rx="16" fill="#e8f5ec" stroke="#8fc49c" stroke-width="2"></rect>
    <rect x="139" y="124" width="82" height="68" rx="16" fill="#e8f5ec" stroke="#8fc49c" stroke-width="2"></rect>
    <rect x="246" y="124" width="82" height="68" rx="16" fill="#e8f5ec" stroke="#8fc49c" stroke-width="2"></rect>
    <text x="51" y="148" class="svg-title">bucket</text>
    <text x="158" y="148" class="svg-title">current</text>
    <text x="268" y="148" class="svg-title">future</text>
    <circle cx="58" cy="171" r="6" fill="#1f78b4"></circle><circle cx="76" cy="171" r="6" fill="#1f78b4"></circle><circle cx="94" cy="171" r="6" fill="#1f78b4"></circle>
    <circle cx="165" cy="171" r="6" fill="#1f78b4"></circle><circle cx="183" cy="171" r="6" fill="#1f78b4"></circle><circle cx="201" cy="171" r="6" fill="#1f78b4"></circle>
    <circle cx="273" cy="171" r="6" fill="#1f78b4"></circle><circle cx="291" cy="171" r="6" fill="#1f78b4"></circle><circle cx="309" cy="171" r="6" fill="#1f78b4"></circle>
    <path d="M180 84 L180 123" stroke="#238443" stroke-width="4" marker-end="url(#tokenArrow)"></path>
    <path d="M73 124 C68 104, 92 91, 132 84" fill="none" stroke="#238443" stroke-width="3" stroke-dasharray="6 5" marker-end="url(#tokenArrow)"></path>
    <text x="44" y="220" class="svg-legend">token caches child region for hot append</text>
    <text x="44" y="238" class="svg-legend">close expired buckets independently</text>
  </svg>
  <p>This is the Common Crawl/log-style shape: parent metadata lives longer; each page/window bucket owns many records.</p>
</article>'''
    )
    parts.append(
        '''<article class="paper-figure">
  <h3>Summary-only topology</h3>
  <svg viewBox="0 0 360 260" role="img" aria-label="Summary-only topology where records are not retained until close">
    <defs>
      <marker id="sumArrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L7,3 z" fill="#238443"></path>
      </marker>
    </defs>
    <rect x="28" y="34" width="92" height="56" rx="15" fill="#e8f5ec" stroke="#8fc49c"></rect>
    <text x="47" y="67" class="svg-title">record</text>
    <rect x="142" y="34" width="92" height="56" rx="15" fill="#e8f5ec" stroke="#8fc49c"></rect>
    <text x="161" y="67" class="svg-title">record</text>
    <rect x="256" y="34" width="72" height="56" rx="15" fill="#e8f5ec" stroke="#8fc49c"></rect>
    <text x="273" y="67" class="svg-title">...</text>
    <rect x="82" y="144" width="196" height="62" rx="16" fill="#f9d778" stroke="#c28a18"></rect>
    <text x="112" y="171" class="svg-title">primitive summary</text>
    <text x="138" y="192" class="svg-legend">counts / sums / sketches</text>
    <path d="M74 91 L138 143" stroke="#238443" stroke-width="4" marker-end="url(#sumArrow)"></path>
    <path d="M188 91 L188 143" stroke="#238443" stroke-width="4" marker-end="url(#sumArrow)"></path>
    <path d="M288 91 L232 143" stroke="#238443" stroke-width="4" marker-end="url(#sumArrow)"></path>
    <text x="42" y="230" class="svg-legend">fast for heap and regions; not a reclaim claim</text>
  </svg>
  <p>Records do not survive to the close boundary. This can be the right processing topology, but it is not evidence that region reclaim beat GC.</p>
</article>'''
    )
    parts.append(
        '''<article class="paper-figure">
  <h3>Backend choice under the same API</h3>
  <svg viewBox="0 0 360 260" role="img" aria-label="Same checked API can lower to scoped or streaming region backends">
    <defs>
      <marker id="backendArrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L7,3 z" fill="#238443"></path>
      </marker>
    </defs>
    <rect x="78" y="26" width="204" height="48" rx="16" fill="#dbeafe" stroke="#93b4e8"></rect>
    <text x="114" y="56" class="svg-title">checked API shape</text>
    <rect x="30" y="122" width="132" height="70" rx="16" fill="#e8f5ec" stroke="#8fc49c"></rect>
    <text x="58" y="151" class="svg-title">scoped/rooted</text>
    <text x="59" y="171" class="svg-legend">SafeZone-backed</text>
    <rect x="198" y="122" width="132" height="70" rx="16" fill="#e8f5ec" stroke="#8fc49c"></rect>
    <text x="226" y="151" class="svg-title">stream/reset</text>
    <text x="230" y="171" class="svg-legend">Rift backend</text>
    <path d="M136 75 L96 121" stroke="#238443" stroke-width="4" marker-end="url(#backendArrow)"></path>
    <path d="M224 75 L264 121" stroke="#238443" stroke-width="4" marker-end="url(#backendArrow)"></path>
    <text x="42" y="226" class="svg-legend">same topology, different backend mechanics</text>
    <text x="42" y="244" class="svg-legend">rootless rows are lower-bound controls</text>
  </svg>
  <p>The topology is what the program expresses. The backend is how that topology is implemented and optimized.</p>
</article>'''
    )
    parts.append("</div>")

    parts.append('<div class="topology-board">')
    parts.append(
        '''<div class="topology-lane topology-heap">
  <div class="lane-heading">GC heap view</div>
  <div class="memory-stack">
    <div class="memory-cell durable">durable control state</div>
    <div class="memory-cell temp">temporary stream objects</div>
    <div class="memory-cell temp">window / epoch records</div>
    <div class="memory-cell durable">global metadata</div>
  </div>
  <p>GC must later rediscover which temporary objects died.</p>
</div>'''
    )
    parts.append('<div class="topology-arrow" aria-hidden="true">→</div>')
    parts.append(
        '''<div class="topology-lane topology-region">
  <div class="lane-heading">Rift lifetime view</div>
  <div class="memory-split">
    <div class="heap-box">heap: durable control metadata</div>
    <div class="region-box">region: epoch / page / window objects</div>
    <div class="close-box">bulk close/reset at boundary</div>
  </div>
  <p>Static checks make the boundary safe enough for bulk reclaim.</p>
</div>'''
    )
    parts.append("</div>")
    parts.append('<div class="topology-card-grid">')
    for card in TOPOLOGY_CARDS:
        parts.append(
            f'''<article class="topology-card topology-{attr(card["tone"])}">
  <div class="topology-label">{esc(card["label"])}</div>
  <h3>{esc(card["title"])}</h3>
  <p>{inline_markdown(card["shape"])}</p>
  <p><strong>Strategy:</strong> {inline_markdown(card["strategy"])}</p>
  <div>{tag(card["claim"], card["tone"])}</div>
</article>'''
        )
    parts.append("</div>")
    return figure_block(
        "Figure 4. Rift topology atlas.",
        "\n".join(parts),
        "These are the actual shapes used in the evaluation. A result should say which topology it uses before claiming a memory-management win.",
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
        "Table 2. Evaluation setup and baselines.",
        "The report separates user-facing checked rows from allocator lower bounds and separates clean headline timing from diagnostic counters.",
    )


def render_prior_work_metrics_table() -> str:
    rows = [[esc(a), esc(b), esc(c)] for a, b, c in PRIOR_WORK_METRIC_ROWS]
    return render_table_block(
        ["Prior system axis", "Metrics to report", "Rift row family"],
        rows,
        "Table 2a. Prior-work metric axes used for normalized reporting.",
        "Each benchmark family keeps the metrics its predecessor literature cared about, while Rift also records standardized L1/L2 evidence.",
    )


def render_enforced_table() -> str:
    rows = [[esc(a), inline_markdown(b), esc(c)] for a, b, c in ENFORCED_ROWS]
    return render_table_block(
        ["Status", "What it means", "Use in the report"],
        rows,
        "Table 1. What Rift actually enforces today versus design vocabulary.",
        "Prior-work ideas like active/closed capabilities are useful only when marked as future design vocabulary.",
    )


def render_region_inference() -> str:
    done_rows = [[esc(a), inline_markdown(b)] for a, b in INFERENCE_DONE_ROWS]
    left_rows = [[esc(a), inline_markdown(b)] for a, b in INFERENCE_LEFT_ROWS]
    return "\n".join(
        [
            render_table_block(
                ["Implemented inference slice", "Current status"],
                done_rows,
                "Table 2. Region inference implemented today.",
                "The compiler places allocations only when it can recover a concrete checked runtime owner; all ambiguous cases stay on the heap.",
            ),
            render_table_block(
                ["Remaining inference track", "Next work"],
                left_rows,
                "Table 3. Region inference still missing.",
                "The remaining work is broader effect summaries and library coverage, not relaxing safety for unknown owners.",
            ),
        ]
    )


def render_real_results_table() -> str:
    rows = [
        [esc(a), inline_markdown(b), inline_markdown(c), inline_markdown(d), esc(e)]
        for a, b, c, d, e in REAL_RESULT_ROWS
    ]
    return render_table_block(
        ["Result", "Workload", "Best checked row", "Immix heap", "Interpretation"],
        rows,
        "Table 4. Latest real/local input results.",
        "These rows use local/public input files or bundled real benchmark data; they are separated from generated and methodology stressors.",
    )


def render_results_table() -> str:
    rows = [
        [esc(a), inline_markdown(b), inline_markdown(c), inline_markdown(d), esc(e)]
        for a, b, c, d, e in RESULT_ROWS
    ]
    return render_table_block(
        ["Result", "Workload", "Best checked row", "Immix heap", "Interpretation"],
        rows,
        "Table 5. Latest generated, methodology, and microbenchmark results.",
        "These rows test memory-management shape, prior-work axes, or runtime/API overhead; they are useful evidence but not real-input proof.",
    )


def render_real_input_table() -> str:
    rows = [[esc(a), esc(b), esc(c), esc(d)] for a, b, c, d in REAL_INPUT_ROWS]
    return render_table_block(
        ["Benchmark", "Input", "Current result", "Report status"],
        rows,
        "Table 6. Additional real-input evidence status.",
        "Real datasets are not automatically GC-heavy. The current real/local positives are DSPBench Log/Fraud and Theodolite q2 in the latest matrix, plus earlier retained Wikimedia, LiveJournal, and AskUbuntu case studies; parser/query-heavy rows remain controls.",
    )


def render_open_work() -> str:
    rows = [[esc(a), esc(b)] for a, b in OPEN_WORK_ROWS]
    return render_table_block(
        ["Open track", "Next action"],
        rows,
        "Table 7. Work remaining before a final paper-style evaluation.",
        "The next work is about clean evidence, broader inference, proof-gated overhead removal, and library coverage, not benchmark-specific shortcuts.",
    )


def render_limitations() -> str:
    parts = ['<ul class="limitations-list">']
    for item in LIMITATIONS:
        parts.append(f"<li>{esc(item)}</li>")
    parts.append("</ul>")
    return figure_block(
        "Figure 6. What these results do not prove yet.",
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
        win"; it is that a checked lifetime/API path can remove GC reclaim
        work and reduce resident memory without resorting to unsafe manual
        memory management.
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
        algorithmic or API-shape wins. If a result depends on summarizing data
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
      {render_enforced_table()}
    </section>

    <section id="region-inference" class="section">
      <div class="section-kicker">Region inference</div>
      <h2>Proven allocations move to regions; unproven allocations stay on the heap</h2>
      <p>
        Rift's inference is ReML/MLKit-inspired, but it is currently a
        capture-directed placement system. The compiler uses expected captured
        types, owner-token arguments, framework boundaries, and local
        method/effect summaries to find a concrete checked runtime owner. When
        that proof is missing, the allocation remains on the Immix heap.
      </p>
      {render_region_inference()}
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
      {render_prior_work_metrics_table()}
      {render_evaluation_table()}
    </section>

    <section id="results" class="section">
      <div class="section-kicker">Main results</div>
      <h2>The important numbers are split by evidence class</h2>
      <p>
        The latest numbers are separated by evidence class. Real/local input
        rows show what happens on public or bundled files; generated,
        methodology, and microbenchmark rows isolate memory-management shapes
        and runtime/API overhead.
      </p>
      {render_real_results_table()}
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
  overflow-wrap: anywhere;
  word-break: break-word;
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
  min-width: 0;
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
  overflow-wrap: anywhere;
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
  min-width: 0;
}
.figure-block > figcaption {
  margin-bottom: 12px;
  color: #334155;
  font-size: 0.9rem;
  font-weight: 800;
  overflow-wrap: anywhere;
  word-break: normal;
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
  min-width: 0;
  overflow-wrap: anywhere;
  word-break: normal;
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
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: normal;
}
.tag-win { border-color: #b8dec6; background: var(--green-soft); color: var(--green); }
.tag-method { border-color: #c4d5f4; background: var(--blue-soft); color: var(--blue); }
.tag-warn { border-color: #ead099; background: var(--amber-soft); color: var(--amber); }
.tag-control { border-color: #d0d7de; background: #f1f5f9; color: #475569; }
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
  min-width: 0;
}
.context-box {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper-soft);
  min-width: 0;
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
  min-width: 0;
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
.lane-heading {
  color: #334155;
  font-size: 0.82rem;
  font-weight: 850;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.memory-stack,
.memory-split {
  display: grid;
  gap: 8px;
}
.memory-cell,
.heap-box,
.region-box,
.close-box {
  padding: 11px 12px;
  border: 1px solid rgba(51, 65, 85, 0.16);
  border-radius: 12px;
  font-weight: 750;
  min-width: 0;
  overflow-wrap: anywhere;
  word-break: normal;
}
.memory-cell.durable,
.heap-box {
  background: #edf2f7;
  color: #334155;
}
.memory-cell.temp,
.region-box {
  background: #dff3e7;
  color: #1d4430;
}
.close-box {
  background: #dbeafe;
  color: #1e3a8a;
}
.paper-figure code {
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: normal;
}
.paper-figure-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr));
  gap: 16px;
  margin-top: 22px;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
}
.paper-figure {
  display: grid;
  gap: 12px;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: #fff;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
}
.paper-figure h3 {
  margin-bottom: 2px;
}
.paper-figure svg {
  width: 100%;
  max-width: 100%;
  height: auto;
  aspect-ratio: 360 / 260;
  border: 1px solid #dbe2ea;
  border-radius: 14px;
  background: #fbfdff;
  overflow: hidden;
}
.paper-figure p {
  font-size: 0.95rem;
  min-width: 0;
  overflow-wrap: anywhere;
  word-break: normal;
}
.svg-title {
  fill: #243244;
  font: 700 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.svg-legend {
  fill: #475569;
  font: 11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.node-text {
  fill: #fff;
  font: 800 12px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
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
  overflow-wrap: anywhere;
  word-break: break-word;
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
  white-space: pre-wrap;
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
  .paper-figure-grid,
  .evidence-list {
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr));
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
  .paper-figure-grid,
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
