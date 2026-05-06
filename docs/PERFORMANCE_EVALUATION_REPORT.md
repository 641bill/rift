# Rift Project And Performance Evaluation Report

Date: 2026-05-03
Last updated: 2026-05-06 15:05 CEST

Status: presentation-ready working report. This document is the single
high-level artifact to read before presenting or planning the next engineering
step. It summarizes the design, implementation status, benchmark evidence,
runtime-overhead story, wins, losses, and open work. Individual evidence files
remain the source of detailed command provenance.

Latest staged headline sweep checkpoint:
`evidence/COMPREHENSIVE_SWEEP_2026_05_06.md`.

Benchmark guide: `docs/BENCHMARK_CATALOG.md` describes what each benchmark is
meant to measure and which rows are generated, real-input, focused, or
ceiling/control evidence.

## 1. Executive Summary

Rift targets a specific regime: ordinary Scala Native objects whose lifetimes
are page-, batch-, window-, transaction-, or epoch-structured. The intended
programming model is not "rewrite benchmarks into primitive arrays"; it is:

- keep durable or unpredictable control state on the Scala Native Immix heap;
- allocate structured-lifetime stream/data objects in regions;
- reclaim those objects in bulk;
- use static capture/lifetime/rooting checks to remove runtime memory-safety
  bookkeeping that would otherwise erase the win.

The current evidence is mixed but useful:

| Result class | Current conclusion |
|---|---|
| Runtime substrate | SafeZone-family allocator/pool mechanics are strong. Improved SafeZone and rootless SafeZone often beat current standalone Rift HPZone on linked/prior-work rows. |
| Trusted Rift | `rift-trusted-hp` / `rift-trusted-streaming` win on the best generated GC-heavy stream detector: Common Crawl WET-shaped q1/q2. |
| Checked Rift | Checked APIs can be fast for simple append/window shapes. The new page/token append operator now clears the generated Common Crawl-shaped q1/q2 gate, while rank/fold/table containers still add too much CPU overhead. |
| Safe checked backend | `rift-checked-safezone-improved-32k` improves focused checked append/window. The page/token SafeZone-backed variant is fastest on generated Common Crawl-shaped q1/q2, but it is still generated stressor evidence rather than real-input proof. |
| Real-input stream evidence | Current real/preloaded WET, Wikimedia, Linear Road, Yahoo, and RIoTBench rows mostly have low/zero median GC or heap wins. They are ceiling controls, not final Rift case studies. |
| Strongest memory-pressure row | Generated Common Crawl WET-shaped q1/q2 creates heavy stream object churn: in the 2026-05-06 staged headline sweep, heap spends `1517.640 ms` timed GC on q1 and `1526.751 ms` on q2. Checked SafeZone-backed page-token is fastest (`3696.284 ms` q1, `3732.171 ms` q2), followed by checked Rift page-token (`3905.285 ms` q1, `3972.493 ms` q2). |
| ReML/MLKit lineage | New comparison track started. The paper table is transcribed as paper-reported/not-rerun evidence, and Tier 1 Scala Native ReML-shaped ports are scaffolded. The erased-generic heap-retention probe is now active and passing; exact ReML artifact rerun and headline medians remain open. |

The strongest current claim is:

> Rift can remove most GC time for epochal, object-heavy stream workloads, and
> trusted Rift backends can beat heap on those workloads. The first cheap
> checked page/token operator now shows that static lifetime ownership can also
> remove enough runtime overhead to win on the generated Common Crawl-shaped
> q1/q2 stressor. The remaining research problem is making that result hold for
> real-input GC-heavy streams and broader checked operators.

Latest staged headline sweep interpretation:

- `PageTokenMapFilter` is now a reusable API, not a benchmark-local primitive;
  scoped Dataflow SELECT is `18.458 ms` and Rift page-token SELECT is
  `20.479 ms`.
- `RegionList` is a reusable topology API and remains the preferred direction
  for linked ListOfLists-style region-friendly structures.
- `EpochFold` is implemented and correct, but its latest true Dataflow
  AGGREGATE row is `92.923 ms`; it is gated out until redesigned.
- `TransactionRegion` is the best checked StreamFlex shape so far: scoped
  checked transaction throughput is `39.019 ms`, faster than heap
  `42.860 ms` and improved SafeZone `41.327 ms`, while trusted Rift remains
  fastest around `36.4 ms`.
- NEXMark Beam-default is broadly favorable but modest: `rift-checked` is the
  fastest row for q0/q1/q2/q3/q4/q5/q8/q9/q11 in the latest sweep, but most
  wins are not large enough to be the central case study.
- Generated Common Crawl WET-shaped q1/q2 is the current best GC-heavy stream
  stressor; q3 parser-scratch is a negative/mixed control and real-input
  GC-heavy proof is still open.

The project still does not have a final checked application result on a
real-input GC-heavy stream benchmark.

## 2. Design Target

Rift is a hybrid region-GC memory system for Scala Native. It is motivated by
systems such as Broom, StreamFlex, Yak, Tofte-Talpin/MLKit-style regions,
typed region+GC systems, and Stancu-style RegionScope work, but the target
combination is Scala-specific:

| Axis | Rift target |
|---|---|
| Runtime performance | Bulk reclaim epochal data without tracing each object. |
| Static safety | Reject escaping region values, illegal heap retention, closure escape, outer-to-inner lifetime bugs, and use-after-close/reset. |
| Ergonomics | Keep heap and Rift benchmark programs logically identical; use minimal lifetime/allocation annotations. |
| Higher-order Scala | Support closures and ordinary Scala object graphs, not only primitive records. |
| Native compatibility | Avoid moving objects and avoid requiring GC scans of region memory in v1. |
| Mixed references | Allow safe cases through static rules or explicit `HeapRoot`; reject unsupported cases instead of dynamic promotion/barriers. |
| Proof path | Preserve a small capture/lifetime discipline that can be mechanized later. |

The current implementation has three layers:

| Layer | Role |
|---|---|
| Trusted region backends | `rift-trusted-hp`, `rift-trusted-streaming`; useful for measuring backend potential without user-level checked proof. |
| Checked Rift API | `rift-checked-rift`; ordinary objects allocated through checked region APIs and owner-token operators. |
| Checked SafeZone-backed prototype | `rift-checked-safezone-improved-32k`; same checked surface, SafeZone-family object allocation backend. |

## 3. Canonical Memory Modes

Use these reporting names in presentation tables. Older raw labels remain
accepted by scripts and appear in detailed source packs.

| Reporting name | Raw/common aliases | Meaning |
|---|---|---|
| `gc-heap` | `heap`, `heap-immix` | Normal Scala Native Immix heap. |
| `region-scoped-rooted` | `safezone-improved`, `safezone-improved-32k` | SafeZone-family scoped regions with coalesced GC-root bookkeeping. |
| `region-scoped-rootless` | `safezone-rootless-32k`, `unsafezone-hp` | SafeZone-family scoped regions with root tracking disabled; unsafe lower-bound only. |
| `region-hp-rootless` | `rift-trusted-hp`, `rift-hp`, HPZone | Trusted Rift HP backend without checked user-level proof. |
| `region-stream-rootless` | `rift-trusted-streaming`, `rift-streaming` | Trusted Rift streaming/reset backend without checked user-level proof. |
| `checked-region-stream` | `rift-checked-rift`, `rift-checked` | Checked Rift API over the Rift backend. |
| `checked-region-scoped` | `rift-checked-safezone-improved-32k`, `rift-checked-safezone-32k` | Checked Rift API over rooted SafeZone-family scoped allocation. |
| `checked-page-token` | `rift-checked-page-token`, `rift-checked-safezone-page-token` | Operator-owned checked page/event/bucket append fast path. |

Detailed taxonomy: `docs/MEMORY_MODE_TAXONOMY.md`.

## 4. What Has Been Implemented

| Area | Status | Notes |
|---|---|---|
| Rift runtime backends | Implemented | HP and Streaming trusted modes exist and are benchmarked. |
| SafeZone root modes | Implemented | Current, improved, chunk-root, and rootless benchmark mode are available. |
| Checked object allocation | Implemented | Scala 3 checked API allocates ordinary Scala objects in regions. |
| Mixed-reference rules | Partial | Static/immutable heap metadata and explicit `HeapRoot` supported; full root-free SafeZone policy is not proven. |
| Checked stream operators | Partial | AppendWindow/cursor works; Join/Fold/Rank/TableRank exist but many fail performance gates. |
| Checked SafeZone-backed backend | Implemented as benchmark prototype | `RiftRegion.streamingSafeZone(...)`; object allocation/close supported, raw allocation/reset unsupported. |
| Canonical benchmark labels | Implemented for key matrices | Checked AppendWindow and Common Crawl WET-shaped runners accept new names and old aliases. |
| Cheap checked operator families | Started | `PageTokenMapFilter`, `RegionList`, `EpochBuffer`, and `TransactionRegion` are now real reusable APIs with passing safety probes. In the latest staged sweep, scoped checked append operators remain fast (`26.461 ms` scoped EpochBuffer, `26.883 ms` scoped page-token vs heap `36.944 ms`). `TransactionRegion` fixes the stacked-EpochBuffer StreamFlex granularity issue enough that scoped checked transaction is the best checked StreamFlex row (`39.019 ms`), but trusted Rift remains faster. `EpochFold` is implemented and correct but failed the Dataflow AGGREGATE speed gate (`92.923 ms`). |
| ReML/MLKit comparison track | Scaffolded | `ReMLRegionMatrix` implements Tier 1 Scala Native-shaped ports and `REML_COMPARISON_MATRIX.md` records paper-reported ReML data. Exact artifact reproduction and headline Tier 1 medians remain open. |
| Final component selection | Started | `docs/FINAL_COMPONENT_SELECTION.md` classifies public candidates, internal lower-bound controls, and gated/rejected operators without deleting runtime code. The parent evaluation runner and main sandbox matrices now exclude current/rootless controls by default; set `RIFT_EVAL_INCLUDE_CONTROLS=1` or `RIFT_BENCH_INCLUDE_CONTROLS=1` to reproduce lower-bound/control rows. Dirty-worktree smoke run `2026-05-06-final-selection-smoke` completed broad suites with `include_controls=0`; it validates runner behavior, not headline performance. |
| Performance report package | In progress | This report now consolidates the main evidence; individual packs remain backing data. |

## 5. Runtime Overhead Removal

The key design principle is: when static safety proves a memory-management fact,
the runtime should not pay a second dynamic cost for that same fact.

### Why Region Allocation Is Not Automatically Free

Bulk close/reset avoids tracing and per-object reclamation, but every mode still
pays to construct each ordinary Scala object. Object construction includes
object header and RTTI setup, zero/init work, constructor execution, and field
stores. Current checked region allocation also reaches the backend through an
`allocImpl` method path rather than the same intrinsic fast path as normal heap
allocation. That means an uncapped Immix heap can win median elapsed time when
it grows to a large RSS and rarely collects, even though region rows remove GC
tails.

Operator/query CPU is separate from GC tracing. In the stream matrices it
means bucket lookup/open, append/link writes, cursor close, linked-record
traversal, aggregation, output/checksum work, and any ranking/table
maintenance. Regions do not trace those records at close, but the benchmark
must still traverse them when computing q1/q2 answers. The new
`ObjectAllocationLoweringMatrix` isolates allocation/object-construction cost
from those operator/query costs.

The first retained-buffer allocation-lowering rows showed a checked gap, but
that gap was partly self-inflicted: the checked rows retained records through
the generic `RegionBuffer` API. The refined retained-region-array matrix uses
`Array[T^{region}]^{region}` in checked rows. With that fairer retention shape,
checked rows are fastest even at 100k (`1.576 ms` checked Rift and `1.395 ms`
checked SafeZone-backed versus heap `1.691 ms`). At 1M, checked Rift is
`16.100 ms`, checked SafeZone-backed is `14.347 ms`, and heap is `20.429 ms`
with `5.745 ms` median timed GC. At 10M, heap becomes GC/RSS-bound: heap is
`271.121 ms` with `105.807 ms` median timed GC and about `971 MB` RSS, while
trusted Rift HP is `199.627 ms` with about `404 MB` RSS. Checked Rift is
`165.774 ms`; checked SafeZone-backed allocation is `143.319 ms`.
Interpretation: allocation/reclaim is not the dominant checked cost in this
focused shape; generic checked containers and application traversal are now
more likely to explain checked overhead in larger workloads.

### Already Removed Or Avoided

| Static fact / design decision | Runtime overhead removed or avoided | Evidence / impact |
|---|---|---|
| Region values cannot escape checked lifetime APIs. | No runtime escape table and no Yak-style promotion barrier. | Compiler probes reject direct escape/closure escape/use-after-reset cases. |
| Heap cannot retain region values through checked APIs. | No dynamic heap-to-region tracking table in current checked paths. | Negative compiler probes cover direct retention patterns. |
| Diagnostics are opt-in. | Rift allocation byte counters were moved off the per-allocation global-atomic hot path. | Common Crawl-like q1/q2 ordering moved in favor of trusted Rift after fast-path cleanup. |
| SafeZone root bookkeeping was the old cliff. | Improved roots mode coalesces root add/remove. | Current SafeZone pathology disappears in improved mode on GCBench/ListOfLists/Common Crawl-like rows. |
| Append-window close has structured bucket ownership. | Cursor close avoids per-entry close callback dispatch. | Focused AppendWindow cursor rows pass the 1M gate; SafeZone-backed cursor row is fastest focused checked row. |
| Page/token append has operator-owned bucket lifetime. | `StreamPageTokenAppendWindow` avoids per-record child-bucket `checkOpen`, per-record child-region lookup, and stale-current `isOpen` checks in that owned path. | Focused 1M page-token rows pass; generated Common Crawl-shaped q1/q2 checked rows improve by `16.2-18.5%` versus current checked. |
| Fixed-chunk append was tested as an array/chunk variant. | `StreamChunkAppendWindow` stores records in region-owned object-array chunks. | Correct, but the focused 1M gate failed: `rift-checked-chunk-token` is `34.273 ms` versus page-token `28.452 ms`; use as negative/control evidence. |
| Rootless SafeZone lower-bound is explicit. | `safezone-rootless-32k` skips SafeZone page/chunk root registration. | Useful substrate lower bound only; not a safe user-facing mode. |

### Not Yet Removed

| Remaining runtime cost | Why it remains | Next condition for removal |
|---|---|---|
| Defensive `isOpen` / `checkOpen` in generic checked hot paths | They also protect direct low-level misuse and current runtime tests. | Removed only in the new page/token owned path; fold/join/rank need equivalent stale-token probes before similar removal. |
| SafeZone roots in `rift-checked-safezone-improved-32k` | This is the safe prototype backend; rootless checked policy is not proven. | Prove/reject unrooted region-to-heap cases and add root-free lowering only for eligible checked code. |
| Checked owner-token/operator dispatch | It is part of the current API implementation, not required by region memory itself. | Specialize cheap page/token/window append operators and measure focused gates. |
| Rank/table/fold container maintenance | These are algorithmic container costs, not allocator costs. | Redesign only if the same shape recurs in winning workloads. |

Detailed matrix: `evidence/CHECKED_OVERHEAD_REMOVAL_MATRIX.md`.

### What "Page/Token Append" Means

`StreamPageTokenAppendWindow` is not about lexical tokens specifically. It is a
checked operator-owned append path for workloads shaped like "one page, event,
bucket, or window owns many short-lived records." The caller asks the operator
for the current child region when entering a page/bucket, allocates ordinary
Scala record objects in that child region, and appends those records through
the operator. Because user code does not receive reusable raw bucket tokens for
the hot append path, the operator can maintain the invariant that the current
bucket is open and clear it during close. That static/structured ownership is
what justifies removing per-record defensive checks while keeping the lower
level APIs defensive.

## 6. Representative Results

All numbers below are medians unless labeled otherwise. They are compiled from
the tracked evidence packs; use the source files for full commands and raw
caveats.

### Latest Staged Headline Sweep (2026-05-06)

Source: `evidence/COMPREHENSIVE_SWEEP_2026_05_06.md`.

This was a staged sweep, not a single monolithic `all` run. It used run IDs
`2026-05-05-comprehensive-headline` for compile/prior/checked rows and
`2026-05-05-comprehensive-headline-cont` for corrected SafeZone-cost and
stream rows. Competitive rows skip `current-safezone`; the SafeZone-cost
continuation also excludes `current-default`.

| Area | Best / key row | Heap row | Interpretation |
|---|---:|---:|---|
| Dataflow SELECT | checked scoped page-token `18.458 ms` | `29.347 ms` / `7.304 ms` GC | reusable page-token fast path wins |
| Dataflow AGGREGATE | checked exact-array aggregate `40.098 ms`; true `EpochFold` `92.923 ms` | `53.677 ms` / `11.080 ms` GC | current checked aggregate wins; reusable `EpochFold` remains gated |
| Dataflow JOIN | checked Rift `21.607 ms` | `33.438 ms` / `11.410 ms` GC | checked row beats heap and SafeZone in this rerun |
| StreamFlex throughput | trusted Rift HP `36.436 ms`; checked scoped TransactionRegion `39.019 ms` | `42.860 ms` | TransactionRegion is the right checked shape; trusted Rift remains fastest |
| Object allocation lowering | checked SafeZone-backed `14.903 ms`, checked Rift `16.039 ms` | `21.885 ms` | focused allocation path is not the main bottleneck now |
| Checked append/window | checked scoped EpochBuffer `26.461 ms`, checked scoped page-token `26.883 ms` | heap Immix `36.944 ms` / `10.900 ms` GC | cheap checked append operators beat heap |
| StreamWindowRank | checked `344.918 ms` | `227.736 ms` | rank/index maintenance remains negative |
| NEXMark Beam-default | checked Rift fastest on q0/q1/q2/q3/q4/q5/q8/q9/q11 | varies by query | broad generated methodology win, mostly modest |
| Common Crawl-shaped q1 | checked SafeZone page-token `3696.284 ms`; checked Rift page-token `3905.285 ms` | `5350.531 ms` / `1517.640 ms` GC | strongest checked generated stream win |
| Common Crawl-shaped q2 | checked SafeZone page-token `3732.171 ms`; checked Rift page-token `3972.493 ms` | `5183.656 ms` / `1526.751 ms` GC | strongest checked generated window win |
| GH Archive-shaped q1/q2 | trusted Rift/page-token rows around `233-251 ms` | heap uncapped `268-287 ms`, heap caps still complete | generated GH-shaped rows favor regions; not real-input proof |
| Linear Road q1/q2 | heap `179.487` / `194.557 ms` | same | region rows remove GC but do not win elapsed/RSS |

The main update versus the previous report is that page-token and transaction
operators now have cleaner comprehensive coverage. The project has real
checked wins on generated stream stressors and prior-work-shaped rows, but it
still lacks a public real-input GC-heavy stream case study.

### Runtime And Topology

| Benchmark | `heap-immix` | Best safe baseline | Best Rift/trusted | Interpretation |
|---|---:|---:|---:|---|
| GCBench runtime | `213.817 ms` | `safezone-improved` `213.239 ms`; `safezone-rootless-32k` `206.636 ms` | HPZone `236.393 ms` | SafeZone-family substrate wins; old HPZone win weakened. |
| ListOfLists linked | `15191.230 ms` | `safezone-improved` `9914.397 ms`; rootless `9818.653 ms` | HPZone `12400.062 ms` | Region-friendly topology, but SafeZone-family beats current Rift backend. |
| ListOfLists flat | `1748.743 ms` | `safezone-improved` `1769.278 ms` | HPZone `1540.958 ms` | Rift HPZone wins when layout is flat/contiguous. |
| Pipeline surrogate | `35.077 ms` | `safezone-improved` `34.660 ms` | Streaming `45.648 ms` | CPU-bound ceiling; not a Rift target. |

### Prior-Work Methodology Rows

| Benchmark | `heap-immix` | `safezone-improved` / rootless | Best Rift/checked | Interpretation |
|---|---:|---:|---:|---|
| Broom Dataflow SELECT | `28.258 ms` | improved `22.501 ms`; rootless `21.957 ms` | checked `24.413 ms` | Checked beats heap; SafeZone-family wins. |
| Broom Dataflow AGGREGATE | `48.849 ms` | improved `40.124 ms`; rootless `39.434 ms` | checked `44.146 ms` | Checked beats heap; SafeZone-family wins. |
| Broom Dataflow JOIN | `29.122 ms` | improved `22.784 ms`; rootless `22.359 ms` | checked `24.935 ms` | Checked beats heap; SafeZone-family wins. |
| Yak topword | `70.370 ms` | improved `59.286 ms`; rootless `58.686 ms` | Streaming `68.959 ms` | SafeZone-family substrate is strongest. |
| Stancu transaction boundary | `44.141 ms` | improved `33.720 ms`; rootless `33.335 ms` | HPZone `51.380 ms` | Current Rift backend loses; SafeZone mechanics matter. |

These are local methodology reproductions unless original artifacts are used.
They compare shapes, not exact published systems.

Prior-system comparisons must use each system's own reported axes, then show
Rift's standardized metrics separately. Broom is strongest on runtime and GC
share in dataflow systems; Yak reports normalized runtime, GC time, app time,
and epoch/promotion behavior; StreamFlex emphasizes throughput, latency tails,
and deadline misses; Stancu et al. report young-generation sensitivity,
collections, annotation burden, and region-freed memory; ReML/MLKit reports
real time, RSS, and GC counts. Rift tables should always add local elapsed,
GC time/count, RSS, region op time, checksum/output, and annotation/API burden
where available.

### ReML / MLKit Lineage

Source: `evidence/REML_COMPARISON_MATRIX.md` and
`docs/REML_COMPARISON_PLAN.md`.

This is a new comparison track, not a stream benchmark. It matters because the
MLKit/ReML lineage stresses region polymorphism, higher-order programs, and
tracing-GC safety when region values can be hidden by polymorphic types.

| Evidence class | Current status | Claim boundary |
|---|---|---|
| Paper-reported ReML table | Elsman 2023 Figure 9 is transcribed into tracked evidence. | Literature anchor only; not local measurement. |
| Exact artifact rerun | Open. Original source/configuration provenance still needs to be found. | Required before any raw wall-clock "Rift beats ReML" claim. |
| Scala Native ports | `ReMLRegionMatrix` has Tier 1 ports for `fib37`, `tak`, `mandel`, `msort`, `msort-r`, `life`, `fft`, and `ratio`. | Valid for local Rift-vs-Scala-Native ratios, not exact ReML reproduction. |
| Safety probes | ReML-inspired compiler probes now include local polymorphic use, generic identity escape, generic heap-cell durable retention, widened `AnyRef`, heap arrays, closure hiding, and unrooted heap metadata. | The previous erased-generic gap is fixed at the current durable/static-retention probe level. Broader heap alias analysis remains open. |

The next useful result here is a Tier 1 3-run local matrix reporting
region-vs-heap ratios, RSS, GC time/count, and checked overhead. It should be
interpreted separately from stream workloads.

### Cheap Operator Family Checkpoint

These focused 1M-shape 3-run rows from
`evidence/CHEAP_OPERATOR_FAMILY_MATRIX.md` show which cheap-operator directions
are worth taking into the clean comprehensive sweep. RSS rows are now recorded;
they still need a committed/clean rerun before being treated as final headline
evidence.

| Operator family | Row | Heap / baseline | New checked row | Interpretation |
|---|---|---:|---:|---|
| `PageTokenMapFilter` | Dataflow SELECT | heap `27.872 ms`; improved SafeZone `23.025 ms`; current checked `20.844 ms` | scoped-backend page-token `18.214 ms`; Rift page-token `19.881 ms` | Gate passes: real reusable SELECT/filter/project API, with scoped backend fastest and lower RSS than heap in the RSS rerun. |
| `EpochFold` | Dataflow AGGREGATE | latest exact-array checked aggregate `40.098 ms`; heap `53.677 ms` | true reusable `EpochFold` `92.923 ms` | Correct but failed speed gate. Keep as negative/gated operator evidence; do not headline until optimized. |
| `RegionList` | ListOfLists linked | earlier heap `14822.115 ms` / RSS `575930368`; scoped rooted `9812.764 ms`; HP `9547.748 ms` | reusable checked builder `5927.385 ms` | Gate passes strongly for linked topology with shared lifetime; this is now a real reusable API row, not benchmark-local code. |
| `EpochBuffer` | focused epoch append/drain | heap epoch `27.164 ms`, GC `5.707 ms` | checked Rift `26.673 ms`; scoped checked `25.448 ms` | Focused gate passes at 1M. Use for Yak/StreamFlex-style batch/epoch data paths before any rank/hash-heavy integration. |
| `EpochBuffer` in StreamFlex | StreamFlex 200k throughput | heap `42.504 ms`; improved SafeZone `40.224 ms`; Rift Streaming `36.357 ms` | checked Rift `47.462 ms`; scoped checked `44.504 ms` | Correct but negative. Stacking four independent epoch buffers per batch pays too much lifecycle/operator overhead; next shape should be `TransactionRegion`/multi-list epoch. |
| `TransactionRegion` in StreamFlex | StreamFlex throughput | heap `42.860 ms`; improved SafeZone `41.327 ms`; Rift HP `36.436 ms` | checked Rift `45.620 ms`; scoped checked `39.019 ms` | Partial win. One child region plus several typed lists fixes the granularity problem, and the SafeZone-backed checked row beats heap/improved SafeZone. Trusted Rift remains fastest. |

This checkpoint supports the updated design framing: Rift is the checked
stream-region programming model and operator library, while SafeZone-derived
and Rift-native runtimes are backend choices. It does not imply that DEBS
ranking/median paths should be moved now; those remain stateful/indexed
operator problems with separate gates.

### Checked Operator Costs

| Operator | Best checked result | Heap/control | Gate status |
|---|---:|---:|---|
| RegionBuffer decomposition | checked array `18.574 ms`; fixed `ObjectBuffer` `25.788 ms`; growable `RegionBuffer` `29.968 ms`; pre-sized `RegionBuffer` `25.980 ms` | heap array `21.089 ms`; heap buffer `34.097 ms` | Checked arrays are fast; bounded/growable buffer overhead remains. |
| AppendWindow cursor | cursor `34.708 ms` | heap `35.705 ms` | Positive, cheap shape. |
| SafeZone-backed AppendWindow | `rift-checked-safezone-improved-32k` `29.444 ms` | current checked cursor `30.922 ms`; heap `35.511 ms` | Focused gate passed. |
| Page/token append | checked page-token `27.141 ms`; SafeZone-backed page-token `26.191 ms` | current checked `30.819 ms`; heap `35.652 ms` | Focused gate passed and feeds generated Common Crawl-shaped q1/q2. |
| EpochBuffer append/drain | checked Rift `26.673 ms`; SafeZone-backed checked `25.448 ms` | heap epoch `27.164 ms`, GC `5.707 ms` | Focused gate passed for whole-epoch append/drain. |
| StreamFlex stacked EpochBuffer | checked Rift `47.462 ms`; SafeZone-backed checked `44.504 ms` | heap `42.504 ms`; improved SafeZone `40.224 ms`; Rift Streaming `36.357 ms` | Failed; the issue is not GC but too many child-region lifecycles and cursor drains per batch. |
| StreamFlex TransactionRegion | checked Rift `45.620 ms`; SafeZone-backed checked `39.019 ms` | heap `42.860 ms`; improved SafeZone `41.327 ms`; Rift HP `36.436 ms` | Scoped checked transaction is the best checked StreamFlex-shaped row so far. Rift-native checked still pays too much operator/list CPU. |
| Fixed-chunk append | checked chunk-token `34.273 ms`; SafeZone-backed chunk-token `33.108 ms` | page-token `28.452 ms`; SafeZone-backed page-token `27.214 ms`; heap chunk `45.363 ms` | Correct but failed; chunk allocation/control overhead outweighs saved link writes in this sequential append/drain shape. |
| Object allocation lowering | checked Rift `165.774 ms`; checked SafeZone-backed `143.319 ms`; trusted HP `199.627 ms` at 10M | heap `271.121 ms`, GC median `105.807 ms`, RSS `971 MB` | Allocation/reclaim win at scale; prior checked gap was mostly generic `RegionBuffer` retention overhead. |
| WindowFold additive | checked `118.726 ms` | heap `103.244 ms` | Failed; checked aggregate overhead. |
| StreamWindowRank long-key | checked-long `503.906 ms` | heap-long `358.988 ms` | Failed; rank/container overhead. |
| StreamWindowTableRank | table-long `568.572 ms` | heap-long `437.702 ms` | Failed; gated out of DEBS. |

### Stream And Application Rows

| Workload | Input | Heap | Best SafeZone-family | Best Rift / checked | Interpretation |
|---|---|---:|---:|---:|---|
| NEXMark Q3 | Beam-default generated | `316.626 ms` | rootless `296.480 ms`, improved `297.962 ms` | checked `292.371 ms` | Best checked generated methodology row; below 10% gate over improved SafeZone. |
| NEXMark Q8 | Beam-default generated | `467.213 ms` | rootless `460.822 ms`, improved `462.599 ms` | checked `450.904 ms` | Checked wins modestly; promising but not decisive. |
| Common Crawl WET-shaped q1 | generated stressor | `5412.618 ms`, GC `1570.724 ms` | improved-32k `4637.981 ms`, rootless `4620.056 ms` | checked page-token `3956.366 ms`; SafeZone-backed page-token `3728.286 ms`; HPZone `4367.265 ms` | First checked generated application-gate pass; generated stressor, not real input. |
| Common Crawl WET-shaped q2 | generated stressor | `5252.803 ms`, GC `1572.021 ms` | improved-32k `4580.687 ms`, rootless `4423.332 ms` | checked page-token `4039.855 ms`; SafeZone-backed page-token `3816.247 ms`; Streaming `4212.494 ms` | First checked generated application-gate pass; generated stressor, not real input. |
| Checked SafeZone-backed q1 | generated stressor | current checked `4744.872 ms` | improved-32k `4570.772 ms` | checked SafeZone-backed `4512.743 ms` | Backend improves checked by ~4.9%, misses application gate. |
| Checked SafeZone-backed q2 | generated stressor | current checked `4698.903 ms` | improved-32k `4362.405 ms` | checked SafeZone-backed `4431.865 ms` | Backend improves checked by ~5.7%, still trails trusted modes. |
| DEBS bounded 1M | real DEBS slice | heap `4861.406 ms` | improved SafeZone `5341.010 ms`; rootless `4639.791 ms` | Streaming `4663.529 ms`; checked `4844.738 ms` | Modest application-shaped substrate signal; checked near heap. |
| Real Common Crawl WET q1/q2 | real preloaded WET shard | q1 heap `32.215 ms`; q2 heap `31.227 ms`; GC `0.000 ms` | q1 improved-32k `35.264 ms`; q2 `35.888 ms` | SafeZone-backed page-token q1 `30.474 ms`; q2 `30.783 ms` | Page-token matches output and wins modestly, but current shard is still median/max-GC-zero; ceiling/control evidence. |
| Real Common Crawl WAT q4/q5 | real preloaded WAT shard | q4 heap `33.646 ms`; q5 heap `35.066 ms`; GC `0.000 ms` | q4 improved-32k `39.551 ms`; q5 `39.579 ms` | SafeZone-backed page-token q4 `31.792 ms`; q5 `33.937 ms` | Real link-object path works and wins modestly, but heap still has zero timed GC; ceiling/control evidence. |
| GH Archive q1 fields | real preloaded NDJSON | 8-hour oracle 1M heap `293.204 ms`, max GC `135.368 ms`, RSS `1.74 GB`; 1G heap-cap diagnostic `395.295 ms`, median GC `92.347 ms` | 8-hour improved-32k `374.923 ms` | 8-hour Streaming rerun `340.820 ms`; SafeZone-backed page-token `348.817 ms` | Heap wins uncapped median by growing to a large heap; checked region wins the 1G memory-budget diagnostic and removes GC tails. |
| GH Archive q2 repo window | real preloaded NDJSON | 8-hour oracle 1M heap `271.880 ms`, max GC `136.353 ms` | improved-32k `363.049 ms` | Streaming `325.665 ms`; SafeZone-backed page-token `347.033 ms` | Heap median wins; repo-window aggregation CPU dominates despite a GC outlier. |
| Wikimedia real clickstream | real preloaded TSV | heap `126.800 ms` | improved `149.062 ms` | Streaming `157.449 ms` | Heap wins; ceiling control. |
| Linear Road official q1 | official input | heap `162.668 ms` | source pack | HPZone `180.277 ms` | Heap wins; ceiling control. |

## 7. What Is A Win, What Is A Loss

### Wins

| Win | Why it matters |
|---|---|
| Generated Common Crawl WET-shaped q1/q2 | Shows the memory-management regime Rift is built for: many ordinary stream objects, epochal lifetimes, heap spends ~1.5s in GC at 1M. |
| NEXMark Q3/Q8 checked rows | Shows checked operator surface can beat heap and improved SafeZone on recognized stream-methodology shapes, though margins are still modest. |
| SafeZone-backed checked AppendWindow | Shows SafeZone-family backend mechanics can reduce checked overhead without changing the user-level checked API. |
| Checked page/token append operator | Shows static lifetime ownership can remove redundant runtime checks and turn the generated Common Crawl-like q1/q2 path from checked-overhead evidence into a checked generated-stressor win. |
| SafeZone cost decomposition | Shows old SafeZone slowness was largely root bookkeeping and page-size configuration, not inherent region cost. |
| Rootless SafeZone lower bound | Shows what allocator mechanics might achieve when root registration is unnecessary, but only as unsafe evidence. |

### Losses / Ceiling Results

| Loss / ceiling | Interpretation |
|---|---|
| Current Rift HPZone loses to improved SafeZone on linked/prior-work rows. | Standalone Rift allocator should learn from SafeZone internals instead of being tuned in isolation. |
| Generic checked Common Crawl q1/q2 trail trusted Rift. | The generic `StreamAppendWindow` allocator placement is correct but too costly. The specialized page/token operator fixes this generated q1/q2 shape, but not yet real inputs or other operators. |
| TableRank / rank / fold containers fail focused gates. | Do not use them for application claims yet. |
| Real WET/WAT/Wikimedia/Linear Road rows mostly heap-fastest or median-GC-zero. | These inputs, as currently wired, do not stress GC enough; they are controls, not failures to tune. GH Archive q1 is now a memory-budget/tail-latency candidate rather than an uncapped throughput win. |
| CPU-bound rows like pipeline surrogate. | Regions add overhead when memory management is not the limiting factor. |
| Fixed-chunk append path. | Array/chunk structures are not automatically faster; the fair heap-chunk and checked chunk-token controls are slower than linked page-token for sequential append/drain. |

### When Rift Wins

| Situation | Mode | What the mode does | Benchmark/input | Why it is GC-heavy or not | Region data / heap data | Evidence class |
|---|---|---|---|---|---|---|
| Generated Common Crawl WET-shaped q1/q2 | `rift-checked-page-token` and `rift-checked-safezone-improved-32k` page-token | Checked operator-owned child buckets; SafeZone-backed row delegates object allocation to improved SafeZone + 32 KiB pages. | Generated WET-shaped stressor, 1M pages / 137M token records. | Heap spends about `1.57 s` in timed GC; many page/token records share page/window lifetimes. | Page/token records in regions; durable counters/config on heap or primitive arrays. | Uncapped generated-stressor throughput win; not real-input proof. |
| Focused page/token append | `rift-checked-page-token` | Same checked API idea without application parsing or aggregation. | Synthetic focused append matrix, 1M records. | Isolates append/object lifetime overhead rather than full GC pressure. | Short-lived records in child bucket regions; operator metadata on parent/heap. | Static-safety overhead-removal win. |
| GH Archive q1 under heap budget | `rift-checked-safezone-page-token` compared with capped `heap-immix` | Checked page-token path over SafeZone-backed region allocation. | Real preloaded GH Archive NDJSON, 1M events / 13M event-field records. | Uncapped heap wins by growing to about `1.7 GiB`; under `1G` cap heap collects materially and slows. | Event/field records in regions; preloaded primitive input arrays and control metadata on heap. | Fixed-memory / GC-tail candidate, not uncapped throughput win. |
| NEXMark Q3/Q8 | `rift-checked-rift` | Checked region APIs on generated Beam-default methodology streams. | Generated NEXMark profile. | Moderate object/window pressure; margins are modest. | Event/window records in regions where checked operator exists; durable tables/counters on heap. | Generated methodology win/near-win. |
| Broom-style Dataflow | `rift-checked-rift`, with SafeZone-family often fastest | Checked local epoch objects; SafeZone-family rows measure allocator substrate. | Local SELECT/AGGREGATE/JOIN methodology reproduction. | Documents/outputs are epoch-local. | Per-epoch document/output objects in regions; control state on heap. | Prior-work-shaped method evidence, not exact artifact reproduction. |
| Real WET/WAT current shards | `rift-checked-safezone-improved-32k` page-token | Checked page/link-object path works over real preloaded data. | Real Common Crawl WET/WAT shards. | Current shards report zero timed heap GC, so this is not yet GC-heavy. | Page/link/token records in regions; input/control on heap. | Real-input ceiling/control with modest region wins only. |
| Object-allocation scale-up | `rift-checked-rift`, `rift-checked-safezone-improved-32k` | Region-backed retained object array without stream/query operators. | Focused 10M-object matrix. | Heap spends `105.807 ms` median timed GC and reaches about `971 MB` RSS. | Ordinary small Scala objects in regions; one retained array/traversal in every mode. | Allocation/reclaim win; generic checked container overhead isolated as a separate problem. |

## 8. What "Common Crawl WET-Shaped" Means

`Common Crawl WET-shaped` is a generated stressor, not real Common Crawl data.
It imitates the object shape of WET processing:

- page records;
- header/body-like fields;
- many lines per page;
- many token objects per line;
- page/window lifetime boundaries.

It is useful because it isolates the memory-management question and reliably
creates heavy short/epochal object churn. It is not real-input proof. The real
WET shard currently wired is much smaller and does not create comparable GC
pressure. Real WAT link extraction now materializes about `1.0M` page/link
records at 50k requested pages and the checked SafeZone-backed row wins
modestly, but heap still reports zero timed GC. Both current real shards are
therefore ceiling controls until larger/multiple shards or a different
real-data stream creates material heap pressure.

## 9. Realistic GC-Heavy Stream Benchmark Ladder

The next benchmark search should focus on real or realistic stream workloads
where object churn and epochal lifetimes are both present.

| Priority | Candidate | Why | First gate |
|---:|---|---|---|
| 1 | Larger/multiple Common Crawl WET/WAT shards | Same domain as current GC-heavy stressor; one WAT shard was not enough to trigger GC. | Actual loaded pages/tokens/links large enough; heap median/max GC material. |
| 2 | GH Archive file-backed and memory-budget JSON-lines | Preloaded q1 shows heap can avoid GC by growing to GB-scale RSS; under a 1G heap cap checked regions win q1. | Include parse/string allocation in timing; report heap caps, RSS, per-run elapsed/GC tails. |
| 3 | Other public NDJSON/log-event streams | Real records often allocate JSON fields, tokens, maps, projected events, and output rows. | Preloaded and file-backed parse/project/window-count controls. |
| 4 | DSPBench local-kernel subset | Stream benchmark family with varied applications; choose high object churn kernels only. | Triage 2-3 kernels with clear windows/epochs and local no-cluster execution. |
| 5 | NEXMark Q3/Q8/Q9/Q11 | Recognized generated stream methodology; already has promising rows. | Keep as methodology/regression, not real-input proof. |
| 6 | RIoTBench with provenance-clean input | IoT streams may have parse/filter/window lifetimes. | Only rerun with real/provenance-clean input or clearly labeled generator. |
| Control | Wikimedia, Linear Road, Yahoo, DEBS | Useful regression/ceiling rows. | Revisit only after a checked operator/backend change alters allocation behavior. |

Detailed ladder: `evidence/REALISTIC_STREAM_GC_MATRIX.md`.

## 10. Reportable Claim Boundaries

Use these claim boundaries in talks and writing:

| Claim | Current status |
|---|---|
| "Rift regions always beat GC." | False. CPU-bound and low-GC rows often favor heap. |
| "Old SafeZone is slow." | Too vague. Current roots mode 0 can be pathological; improved SafeZone is a strong baseline. |
| "Trusted Rift can beat heap on GC-heavy epochal streams." | Supported by Common Crawl WET-shaped q1/q2 and some NEXMark rows. |
| "Checked Rift already has a final application win." | Not yet. Checked rows are promising but still gated by operator overhead. |
| "SafeZone internals are worth using for Rift." | Supported by SafeZone cost and checked SafeZone-backed AppendWindow. |
| "Rootless SafeZone is safe." | False. It is an unsafe lower-bound unless root-free checked policy is proven. |
| "Real stream data is always GC-heavy." | False. Current real WET/Wikimedia/Linear Road rows are mostly ceiling controls. |

## 11. Next Engineering Plan

The next implementation work should be ordered like this:

1. **Keep allocation and generic checked-container costs separated.**
   The region-array allocation matrix is positive; the earlier negative row was
   mostly `RegionBuffer` overhead. The decomposition now shows
   `rift-checked-array` at `18.574 ms` versus fixed `ObjectBuffer` at
   `25.788 ms`, growable `RegionBuffer` at `29.968 ms`, and pre-sized
   `RegionBuffer` at `25.980 ms`, so optimize generic checked
   buffers/operators separately instead of treating that gap as raw allocation
   cost.

2. **Add CPU profiling before the next tuning pass.**
   Scala Native's official profiling guidance treats Scala Native output as a
   native binary: use external time/RSS tools, platform native profilers, and
   `samply`/flamegraph-style sampled profiles where available. Use profiling as
   diagnostic evidence, not headline timing. Record the run plan and results in
   `docs/CPU_PROFILE_REPORT.md` after profiling the smallest representative set:
   Common Crawl-shaped q1/q2 (`heap-immix`, `rift-checked-page-token`,
   `rift-checked-safezone-page-token`), Dataflow AGGREGATE exact-array versus
   true `EpochFold`, StreamFlex trusted Rift versus checked
   `TransactionRegion`, and Common Crawl q3 parser-scratch. The goal is to
   attribute remaining time to object construction, checked allocation
   lowering, operator/link/cursor traversal, SafeZone claim/reclaim/root work,
   parser/token scratch, rank/table maintenance, or output/checksum CPU.

3. **Use `StreamPageTokenAppendWindow` as the first cheap checked operator.**
   Keep the generic `StreamAppendWindow` path as the defensive control, and
   apply the owned-path/no-check idea to fold/join/rank only after equivalent
   stale-token probes exist.

4. **Run the realistic stream ladder against the new operator.**
   Start with larger/multiple WET shards and WAT metadata/link extraction, then
   NDJSON/logs, then DSPBench triage. Park rows where heap median/max GC is
   immaterial.

5. **Advance checked SafeZone-backed backend carefully.**
   Keep `rift-checked-safezone-improved-32k` as the safe candidate. Do not
   make rootless checked claims until mixed-reference/root-free policy tests
   prove eligibility.

6. **Promote only repeated winning shapes into public APIs.**
   Do not add more TableRank/rank-style application integration until focused
   gates pass.

7. **Run the ReML/MLKit Tier 1 comparison as a separate axis.**
   Run `ReMLRegionMatrix` for `fib37`, `tak`, `mandel`, `msort`, `msort-r`,
   `life`, `fft`, and `ratio` with 3-run medians, then decide whether Tier 2
   ports are worth adding. Keep exact ReML artifact search open, and treat the
   fixed erased-generic probe as current compiler evidence rather than a full
   proof of arbitrary heap alias safety.

8. **Run final component selection benchmarks.**
   Use `docs/FINAL_COMPONENT_SELECTION.md` as the public/internal filter:
   include `gc-heap`, the best safe/rooted baseline, the best checked backend,
   and the best operator-specific candidate by default; keep rootless and
   losing operators in explicit control sections only. The runner now encodes
   this split in default mode lists; control sweeps must opt in with
   `RIFT_EVAL_INCLUDE_CONTROLS=1` or explicit per-matrix mode variables.

## 12. Presentation Outline

Use `docs/RIFT_EVALUATION_SUMMARY_SLIDES.md` as a slide skeleton. The talk
should follow this order:

1. Problem: GC overhead in epochal stream/dataflow object graphs.
2. Design: checked regions plus GC heap fallback.
3. Mode taxonomy: heap, SafeZone, rootless lower bound, trusted Rift, checked
   Rift, checked SafeZone-backed Rift.
4. Runtime lesson: SafeZone root coalescing and page size matter.
5. Safety lesson: static checks should remove runtime escape/root/barrier work.
6. Benchmark lesson: only some stream workloads are GC-heavy.
7. Representative tables: Common Crawl-shaped q1/q2, NEXMark Q3/Q8, Dataflow,
   ListOfLists, checked AppendWindow, negative rows.
8. Current win envelope and losses.
9. Next engineering plan.

## 13. Source Evidence

Read these files for detail:

- `docs/MEMORY_MODE_TAXONOMY.md`
- `evidence/EVALUATION_SUMMARY_TABLES.md`
- `evidence/CHECKED_OVERHEAD_REMOVAL_MATRIX.md`
- `evidence/CHECKED_PAGE_TOKEN_APPEND_MATRIX.md`
- `evidence/CHECKED_SAFEZONE_BACKEND_MATRIX.md`
- `evidence/REALISTIC_STREAM_GC_MATRIX.md`
- `evidence/COMMON_CRAWL_LIKE_MATRIX.md`
- `evidence/REML_COMPARISON_MATRIX.md`
- `docs/REML_COMPARISON_PLAN.md`
- `docs/CPU_PROFILE_REPORT.md`
- `docs/LITERATURE_BENCHMARK_CONTRACT.md`
- `evidence/SN_WIN_ENVELOPE.md`
- `evidence/SAFEZONE_COST_MATRIX.md`
- `docs/HANDOFF.md`
