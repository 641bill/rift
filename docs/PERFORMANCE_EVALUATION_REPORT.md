# Rift Project And Performance Evaluation Report

Date: 2026-05-03
Last updated: 2026-05-08 10:04 CEST

Status: presentation-ready working report. This document is the single
high-level artifact to read before presenting or planning the next engineering
step. It summarizes the design, implementation status, benchmark evidence,
runtime-overhead story, wins, losses, and open work. Individual evidence files
remain the source of detailed command provenance.

Latest clean final-selection headline sweep:
`evidence/FINAL_SELECTION_HEADLINE_2026_05_06.md`.

Latest post-fast-path selected sweep:
`evidence/POST_FAST_PATH_SELECTED_SWEEP_2026_05_07.md`. This is from the
current dirty page-token checkpoint, not a clean commit-bound headline sweep.

Latest clean post-fast-path checkpoint:
`evidence/CHECKED_PAGE_TOKEN_COST_MATRIX.md` plus raw summaries under
`cache/perf-eval/2026-05-07-clean-post-fast-path-selected/`. The clean
focused page-token row is checked scoped page-token `27.240 ms` versus heap
`36.722 ms`; the new no-drain cost split shows no-drain close is safe but not
the main remaining bottleneck.

Latest attribution checkpoint:
`docs/CPU_PROFILE_REPORT.md`, `evidence/CHECKED_OVERHEAD_REMOVAL_MATRIX.md`,
and diagnostic logs under
`cache/common-crawl-page-token-diag2-2026-05-07` and
`cache/dspbench-fraud-q2-diag2-2026-05-07`. These are non-headline one-run
diagnostics. They show that raw bucket-switch timing mostly included
expired-bucket close work; estimated true bucket open/switch is only about
`3-10 ms` on generated Common Crawl-shaped q1/q2 and below `1 ms` on
DSPBench Fraud q2. Remaining cost is allocation+append plus cursor/node
traversal and query/replay CPU. In Fraud q2, region allocation+append is
already faster than heap in the diagnostic row.

Latest page-token bookkeeping checkpoint:
`evidence/CHECKED_PAGE_TOKEN_COST_MATRIX.md` now records both page-token
live-length removal and owned-cursor link-clearing removal. These are valid
static-safety cleanups: page-token-owned APIs do not expose a generic live
length, and close callbacks do not need to clear every record link when parent
refs are already gone and the child region is about to die. Focused 1M checked
scoped page-token is now `73.590/83.997/81.296 ms` for
append-only/drain/aggregate, improving the previous no-length rows by roughly
`3.5-4.8 ms`. DSPBench Fraud q2 now has checked scoped page-token
`800.369 ms` versus heap `807.974 ms`, while cutting RSS from `358 MB` to
`279 MB` and median timed GC from `71.317 ms` to `15.726 ms`. Trusted
Streaming remains faster at `785.682 ms`, so this is a modest safe checked/RSS
win, not the final lower bound.

Latest open-allocation checkpoint:
`RiftRegion.OpenStreamingRegion` and `RiftRegion.allocOpen(...)` now remove the
generic checked `allocImpl/checkOpen` branch from operator-owned page-token
child-bucket allocation. This is a static-safety cleanup, not a public
low-level API relaxation. Focused 1M checked scoped page-token is
`73.632/83.177/82.198 ms` on append-only/drain/aggregate versus heap
`76.295/85.873/84.354 ms`; checked scoped count-by-key is `95.946 ms` versus
heap `103.946 ms`. DSPBench Fraud q2 improves slightly to checked scoped
`797.782 ms` versus heap `806.697 ms`, but trusted Streaming remains fastest
at `778.975 ms`. Generated Common Crawl-shaped q1/q2 remains the strongest
object-pressure row: checked scoped page-token `3707.214/3902.795 ms` versus
heap `5577.965/5183.074 ms`; heap timed GC is `1741.640/1565.074 ms` versus
checked scoped `30.693/27.027 ms`. Interpretation: `checkOpen` was worth
removing, but object construction, append/linking, cursor traversal, and query
CPU are now the larger limits.

Latest profiling checkpoint:
`docs/CPU_PROFILE_REPORT.md` now includes post-open-allocation target profiles.
Generated Common Crawl-shaped q2 checked scoped samples
`allocUncheckedImpl`, `scalanative_zone_alloc`/`memset`, append/linking,
`nextOwnedOrNull`, close traversal, and token-hash/query work; generic
`allocImpl/checkOpen` is no longer visible. Real DSPBench Fraud q2 checked
scoped samples are led by byte-line parsing/replay, stable hashing, predictor
state update, CSV/state parsing, append, and close traversal. This confirms
that the next useful work is not another open-check removal. The choice is now
between lower-level append/cursor/zeroing work with fair controls and moving
back to the real-input benchmark search.

Latest real-input search checkpoint:
`evidence/DSPBENCH_REGION_MATRIX.md` includes DSPBench Log Processing over the
bundled real `http-server.log` common-log file, and
`evidence/LOGHUB_REGION_MATRIX.md` now includes richer real BGL
`q3-template-session`. DSPBench Log 1M `log-q2-window` is a modest checked
scoped page-token win: `1733.654 ms` versus heap `1750.291 ms`, with heap
median/max GC `44.992/88.210 ms` reduced to `18.402/18.584 ms`. LogHub q3
materializes template-token/session-candidate records and cuts RSS from
`290 MB` to about `237 MB`, but heap GC is `84.166 ms` inside `8683.558 ms`
elapsed. RIoTBench/MHEALTH is now wired as a provenance-clean IoT source:
the UCI MHEALTH dataset has `1215745` rows, but 1M q1/q2 report zero timed
heap GC and only near-tie/small-SafeZone-win elapsed results. These are useful
real-input/control rows, not the missing GC-heavy flagship.

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

The current evidence is mixed but useful. "Mixed" should not be read as
"not a win." Several rows are modest throughput wins, RSS wins, or
tail/heap-budget wins even when they are not strong enough to become final
representative components.

| Result class | Current conclusion |
|---|---|
| Runtime substrate | Improved SafeZone/rooted scoped regions remain the safe baseline; rootless/trusted rows are now explicit controls, not default public evidence. |
| Checked Rift | Checked APIs are fast for simple append/window shapes. Page-token, Dataflow SELECT, RegionList, GH Archive-shaped q1/q2, and generated Common Crawl-shaped q1/q2 clear useful gates; rank/fold/table containers still add too much CPU overhead. |
| Safe checked backend | `checked-region-scoped` is the best page-token backend in the clean final-selection sweep. It is fastest on focused page-token append and generated Common Crawl-shaped q1/q2. |
| Real-input stream evidence | GH Archive byte-slice file-backed q1/q2, LogHub BGL q1/q2/q3, DSPBench Fraud q2, and DSPBench Log q2 are the strongest real-input modest-win candidates. After open allocation, Fraud q2 checked scoped page-token is a modest elapsed/RSS win (`797.782 ms` vs heap `806.697 ms`, RSS about `279 MB` vs heap `358 MB`), while trusted Streaming remains fastest (`778.975 ms`). DSPBench Log q2 has checked scoped fastest (`1733.654 ms` vs heap `1750.291 ms`) and cuts max GC from `88.210 ms` to `18.584 ms`, but with higher RSS. LogHub q3 reduces RSS/tails but not elapsed for checked scoped. RIoTBench/MHEALTH fixes an IoT real-input provenance gap but is zero-GC/ceiling evidence. These are useful real-input rows, not flagship GC-heavy cases. |
| Strongest memory-pressure row | Generated Common Crawl WET-shaped q1/q2 creates heavy stream object churn. After open allocation, heap spends `1.7/1.6 s` timed GC on q1/q2. Checked scoped page-token is fastest in the rerun (`3707.214 ms` q1, `3902.795 ms` q2), followed by checked Rift page-token (`3933.900 ms` q1, `4040.310 ms` q2). |
| Real-input search direction | The search is tracked in `evidence/REAL_INPUT_BENCHMARK_SEARCH.md`. DSPBench Spike, Fraud, and Log Processing q0/q1/q2 are implemented; LogHub BGL q3 template/session mining and RIoTBench/MHEALTH q1/q2 have been tried. Fraud q2, Log q2, LogHub q3, and MHEALTH q1/q2 are regression/control rows. Continue Theodolite-style inputs or a larger provenance-clean machine/security trace; current DSPBench/LogHub/RIoTBench rows are modest/control or ceiling evidence. |
| ReML/MLKit lineage | Tier 1 Scala Native ReML-shaped medians now exist. `msort`, `msort-r`, and `ratio` show useful checked-region allocation/RSS/GC behavior; exact ReML artifact rerun remains blocked by missing local `mlkit`/`mlton` and no running Docker daemon. |

The strongest current claim is:

> Rift can remove most GC time for epochal, object-heavy stream workloads, and
> trusted Rift backends can beat heap on those workloads. The first cheap
> checked page/token operator now shows that static lifetime ownership can also
> remove enough runtime overhead to win on the generated Common Crawl-shaped
> q1/q2 stressor. The remaining research problem is making that result hold for
> real-input GC-heavy streams and broader checked operators.

Latest post-fast-path selected interpretation:

- Dataflow SELECT is the clearest prior-work-shaped page-token rerun:
  heap `28.942 ms`, improved SafeZone `22.463 ms`, checked page-token
  `19.503 ms`, and scoped checked page-token `18.572 ms`.
- Dataflow AGGREGATE is still an exact-array checked win, not an `EpochFold`
  win: checked `38.198 ms`, improved SafeZone `40.596 ms`, heap `52.071 ms`.
- Dataflow JOIN is positive only against heap in this selected pass:
  checked `24.183 ms`, improved SafeZone `23.459 ms`, heap `31.760 ms`.
- NEXMark Beam-default selected rows remain broadly positive:
  q3 checked `285.356 ms`, q8 `443.020 ms`, q9 `724.479 ms`, and q11
  `209.918 ms`, all faster than heap and improved SafeZone in the same run.
- Generated Common Crawl-shaped q1/q2 now show the strongest checked
  stream-object result: q1 checked scoped page-token `3643.680 ms` versus heap
  `5392.344 ms`; q2 checked scoped page-token `3790.138 ms` versus heap
  `5201.862 ms`. Heap spends about `1.58 s` in timed GC on each query.
- DSPBench Fraud q2 is the best real-input checked regression row so far.
  After owned-cursor cleanup, checked scoped page-token is `800.369 ms` versus
  heap `807.974 ms`, with checked RSS about `279 MB` versus heap `358 MB`.
  Trusted Streaming remains fastest at `785.682 ms`, so this is a modest
  checked/RSS win rather than a decisive checked-system flagship.

Latest clean final-selection headline interpretation:

- Focused page-token append is strong: heap `37.046 ms`, checked page-token
  `28.160 ms`, and scoped checked page-token `26.866 ms`, with lower RSS than
  heap.
- `PageTokenMapFilter` remains the reusable SELECT/filter/project API:
  Dataflow SELECT is heap `29.272 ms`, improved SafeZone `23.253 ms`, checked
  page-token `20.528 ms`, and scoped checked page-token `19.063 ms`.
- `RegionList` is a reusable topology API: linked ListOfLists is heap
  `15820.172 ms`, improved SafeZone `10133.449 ms`, and checked builder
  `6053.235 ms`.
- `EpochFold` is implemented and correct, but its latest true Dataflow
  reusable fold row remains gated; Dataflow AGGREGATE is a checked/safezone
  near-tie (`41.827 ms` checked, `41.810 ms` improved SafeZone) rather than a
  generic fold win.
- `TransactionRegion` is the best checked StreamFlex shape so far: scoped
  checked transaction throughput is `40.512 ms`, faster than heap `42.431 ms`
  and improved SafeZone `42.236 ms`, but latency median is worse.
- NEXMark Beam-default is broadly favorable but modest: checked wins q0/q1/q2/
  q3/q4/q5/q8/q9/q11, with q3 `287.541 ms` versus heap `317.003 ms` and
  improved SafeZone `304.246 ms`.
- GH Archive-shaped q1/q2 now favor checked page-token on uncapped generated
  rows: q1 `262.139 ms` versus heap `293.716 ms`; q2 `261.762 ms` versus heap
  `279.743 ms`, with much lower RSS.
- Real file-backed GH Archive now has a byte-slice parser-scratch path. At two
  hourly files / 200k real events, q1 heap is `3806.120 ms`, median GC
  `57.685 ms`, RSS `290177024`; trusted Streaming is `3626.219 ms` and
  checked scoped page-token is `3629.193 ms`, both with zero timed GC and
  about `211 MB` RSS. q2 is similar: heap `3756.950 ms`, checked scoped
  page-token `3626.107 ms`.
- Real file-backed LogHub BGL now has a line/token/window matrix. At 1M real
  lines, q1 heap is `5568.252 ms` with `99.271 ms` GC and trusted Streaming
  is `5491.033 ms`; q2 heap is `5646.824 ms` with `157.198 ms` GC and
  improved SafeZone-32k is `5509.481 ms`. A full-file q2 single-run probe
  loads `4747963` lines: heap `32161.391 ms`, `595.599 ms` GC, RSS
  `576012288`; checked scoped page-token `31165.087 ms`, zero timed GC, RSS
  `490946560`. A richer q3 template/session query over 1M real BGL lines
  validates template-token/session-candidate object placement: heap
  `8683.558 ms`, GC `84.166 ms`, RSS `290242560`; trusted Streaming
  `8615.627 ms`, RSS `236814336`; checked scoped page-token `8722.008 ms`,
  RSS `236961792`. This is an RSS/tail/modest control, not a GC-heavy
  flagship.
- DSPBench Spike Detection is measured as a local single-process methodology
  port over `79999` usable real sensor lines from `sensors.dat`. Treat Spike
  as real-input modest/control evidence. DSPBench Fraud Detection is measured
  over `credit-card.dat`. The first q2 rows made trusted Streaming the best
  row (`763.819 ms` vs heap `801.790 ms`) and exposed checked page-token
  overhead. The dirty 2026-05-07 fast-path direction check made checked scoped
  page-token fastest (`818.574 ms` vs heap `862.834 ms`), but the clean
  committed-code rerun has trusted Streaming fastest (`788.040 ms`) and
  checked scoped page-token as a modest checked/RSS win (`810.770 ms` vs heap
  `820.945 ms`, RSS about `279 MB` vs heap `358 MB`).
- ReML-shaped Tier 1 ports add a non-stream axis. In the latest direct Tier 1
  run, checked stream wins `msort` (`104.358 ms` versus heap `124.983 ms`) and
  `msort-r` (`104.929 ms` versus heap `126.163 ms`) while cutting RSS
  substantially; `ratio` is a smaller elapsed win (`48.929-49.681 ms` checked
  versus heap `51.302 ms`) but a strong RSS/GC reduction.
- Generated Common Crawl WET-shaped q1/q2 is the current best GC-heavy stream
  stressor; q3 parser-scratch is a negative/mixed control and real-input
  GC-heavy proof is still open.

### Evidence Outcome Classes

Use these labels when reading "mixed" rows:

| Outcome | Meaning | Example |
|---|---|---|
| Representative win | Clear elapsed win, usually around `>=10%`, with correctness and a reusable workload shape. | Generated Common Crawl-shaped q1/q2 with checked scoped page-token. |
| Modest throughput win | Correct row is faster, but margin is below the representative gate or the workload is not broad enough. | NEXMark Q8, real WET/WAT page-token controls, StreamFlex throughput. |
| RSS win | Region row materially lowers resident memory even if elapsed is tied or slightly worse. | ReML-shaped `msort`/`ratio`, `CheckedWindowFold` style rows. |
| Fixed-memory / tail win | Uncapped heap is competitive by growing large, but under a heap cap or in max-GC/tail runs regions improve completion or tails. | GH Archive q1 under `1G` heap cap. |
| Speed-gated operator | Correct API has some GC/RSS benefit, but CPU overhead is too high for public performance claims. | `EpochFold`, `StreamWindowFold`, `TableRank`. |
| Negative/ceiling | Heap is fastest and there is no material GC/RSS/tail benefit at the measured scale. | Pipeline surrogate, current Wikimedia/Linear Road rows. |

Throughput and latency are different axes. Throughput asks how much total work
finishes per unit time; in batch-style matrices we approximate it with elapsed
time, where lower elapsed means higher throughput. Latency asks how long an
individual event/request waits; p50/p95/max latency and deadline misses can
improve even when average throughput changes only modestly, or worsen even when
throughput improves. StreamFlex is the current example: scoped
`TransactionRegion` improves throughput modestly, but latency remains mixed.

The project still does not have a final checked application result on a
real-input GC-heavy stream benchmark.

The closest real-input stream candidate is GH Archive. The legacy file-backed
path included gzip read/decompression and JSON field extraction during timing,
but it allocated parser strings/builders heavily. A sampled profile confirmed
that the string parser, not region allocation, dominated. The new byte-slice
file-backed parser reuses input buffers and extracts JSON fields from raw
UTF-8 bytes. At two hourly files / 200k real events, both trusted Streaming
and checked scoped page-token modestly beat heap while cutting RSS from about
`290 MB` to about `211 MB` and removing timed GC. This is a real-input
throughput/RSS/tail win, but it is not a GC-heavy case study: the heap row
spends only about `1.5-1.6%` of elapsed time in timed GC. LogHub BGL is the
newest real log control and is slightly more GC-visible than GH Archive
byte-slice, but it reaches the same conclusion: regions remove timed GC and
can modestly improve elapsed/RSS/tails, while parser/token/query CPU still
dominates.

The new search ledger makes this explicit: generated Common Crawl-shaped q1/q2
is a memory-pressure detector, not real-data proof. The first DSPBench Spike
and Fraud matrices have now been run. Spike should be parked as modest/control
evidence because parser/query/object CPU dominates over GC. Fraud q2 should
stay in the suite as the regression row for checked close/open and page-token
overhead: the clean checkpoint is a modest checked/RSS win over heap, while
trusted Streaming is still fastest. Kafka, Storm, Spark, Flink, and
thread-engine overhead should stay out of headline rows so memory-management
effects remain visible.

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
| ReML/MLKit comparison track | Started with local medians | `ReMLRegionMatrix` implements Tier 1 Scala Native-shaped ports and `REML_COMPARISON_MATRIX.md` records paper-reported ReML data. The 2026-05-06 Tier 1 run gives local medians for `fib37`, `tak`, `mandel`, `msort`, `msort-r`, `life`, `fft`, and `ratio`; `msort`/`msort-r`/`ratio` are the meaningful allocation/RSS rows. The public MLKit repo has been cloned into ignored cache and contains many Figure 9-style benchmark sources; exact paper-era configuration and local MLKit/MLton toolchain reproduction remain open. |
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
| Page/token append has operator-owned bucket lifetime. | `StreamPageTokenAppendWindow` avoids per-record child-bucket `checkOpen`, per-record child-region lookup, stale-current `isOpen` checks, generic leftover drain in page-token close, and repeated close/open work for monotonic same-bucket streams when the current bucket is the only live bucket. | Focused 1M fast-path page-token rows pass (`27.549 ms` SafeZone-backed checked vs heap `36.920 ms`); generated Common Crawl-shaped q1/q2 100k regression has SafeZone-backed checked page-token fastest on both q1 and q2. |
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
| Page-token fast path | checked scoped page-token `27.549 ms`; checked Rift page-token `29.319 ms` | heap `36.920 ms` / `10.995 ms` GC | batch-close/current-bucket fast path keeps linked page-token ahead of chunk-token |
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
| Exact artifact rerun | Open. Current MLKit HEAD was inspected and contains many benchmark sources; paper-era source/configuration and local `mlkit`/`mlton` toolchain runs remain to be pinned. Host `mlkit`/`mlton` are missing, and Docker is installed but the daemon is not running. | Required before any raw wall-clock "Rift beats ReML" claim. |
| Scala Native ports | `ReMLRegionMatrix` has Tier 1 medians for `fib37`, `tak`, `mandel`, `msort`, `msort-r`, `life`, `fft`, and `ratio`. | Valid for local Rift-vs-Scala-Native ratios, not exact ReML reproduction. |
| Safety probes | ReML-inspired compiler probes now include local polymorphic use, generic identity escape, generic heap-cell durable retention, widened `AnyRef`, heap arrays, closure hiding, and unrooted heap metadata. | The previous erased-generic gap is fixed at the current durable/static-retention probe level. Broader heap alias analysis remains open. |

Tier 1 interpretation:

| Workload | Best local checked row | Heap row | Current meaning |
|---|---:|---:|---|
| `msort` | checked stream `104.358 ms`, RSS `10.4 MB` | `124.983 ms`, RSS `21.4 MB`, GC `27.180 ms` | allocation/RSS win on a linked-node sort shape. |
| `msort-r` | checked stream `104.929 ms`, RSS `10.4 MB` | `126.163 ms`, RSS `39.2 MB`, GC `27.280 ms` | allocation/RSS win on reverse-input linked sort. |
| `ratio` | checked scoped `48.929 ms`, RSS `16.0 MB`, GC `0` | `51.302 ms`, RSS `44.0 MB`, GC `3.191 ms` | modest elapsed win and strong RSS/GC reduction. |
| `fib37`/`tak`/`mandel`/`life` | small or noisy differences | heap has no material GC | compute/control rows, not memory-management evidence. |

These should be interpreted separately from stream workloads and compared to
ReML by relative ratios until exact MLKit/ReML artifacts are run locally.

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
| GH Archive q1 fields | real file-backed NDJSON | 100k heap uncapped `4014.909 ms`, median GC `157.495 ms`, RSS `1.22 GB`; `1G` cap fails with signal 11 | improved-32k `4000.812 ms`, RSS `673.8 MB` | Streaming `3995.238 ms`, RSS `673.6 MB`; SafeZone-backed page-token `4023.883 ms`, RSS `674.7 MB` | Mostly RSS/fixed-memory evidence: trusted Streaming modestly wins elapsed, checked scoped page-token is a near tie/slight elapsed loss, and parser/string allocation still triggers GC in every mode. |
| GH Archive q1 fields | real file-backed NDJSON, 2 hourly files, legacy string parser | 200k heap `7549.355 ms`, median GC `198.535 ms`, RSS `2.43 GB` | not rerun in this subset | Streaming `7448.838 ms`, RSS `925.5 MB`; SafeZone-backed page-token `7489.923 ms`, RSS `925.6 MB` | Legacy parser row: RSS/fixed-memory story, but parser/string/decompression dominates. |
| GH Archive q1 fields | real file-backed NDJSON, 2 hourly files, byte-slice parser | 200k heap `3806.120 ms`, median GC `57.685 ms`, RSS `290 MB` | not rerun in this subset | Streaming `3626.219 ms`, RSS `211 MB`; SafeZone-backed page-token `3629.193 ms`, RSS `211 MB` | Byte-slice parser-scratch makes q1 a modest real-input throughput/RSS/tail win; heap collects in 2/3 runs, region rows report zero timed GC. Not GC-heavy: heap GC is about `1.5%` of elapsed. |
| GH Archive q2 repo window | real preloaded NDJSON | 8-hour oracle 1M heap `271.880 ms`, max GC `136.353 ms` | improved-32k `363.049 ms` | Streaming `325.665 ms`; SafeZone-backed page-token `347.033 ms` | Heap median wins; repo-window aggregation CPU dominates despite a GC outlier. |
| GH Archive q2 repo window | real file-backed NDJSON | 100k heap `3995.632 ms`, median GC `158.277 ms`, RSS `1.22 GB`; `1G` cap fails with signal 11 | improved-32k `3934.094 ms`, RSS `672.1 MB` | Streaming `3906.291 ms`, RSS `673.6 MB`; SafeZone-backed page-token `3921.127 ms`, RSS `673.8 MB` | With parsing timed, q2 becomes a modest region/RSS/fixed-memory win; parser/string allocation still causes GC in region rows. |
| GH Archive q2 repo window | real file-backed NDJSON, 2 hourly files, legacy string parser | 200k heap `7641.540 ms`, median GC `199.876 ms`, RSS `2.43 GB` | not rerun in this subset | Streaming `7442.005 ms`, RSS `724.8 MB`; SafeZone-backed page-token `7498.263 ms`, RSS `925.6 MB` | Legacy parser row: Streaming modestly wins elapsed and strongly wins RSS; checked scoped page-token is near-tied. |
| GH Archive q2 repo window | real file-backed NDJSON, 2 hourly files, byte-slice parser | 200k heap `3756.950 ms`, median GC `61.625 ms`, RSS `290 MB` | not rerun in this subset | Streaming `3645.458 ms`, RSS `211 MB`; SafeZone-backed page-token `3626.107 ms`, RSS `211 MB` | Byte-slice parser-scratch turns q2 into a modest checked scoped page-token win with zero timed GC in region rows. Not GC-heavy: heap GC is about `1.6%` of elapsed. |
| LogHub BGL q1 tokens | real file-backed BGL system log | 1M heap `5568.252 ms`, median GC `99.271 ms`, RSS `408 MB`; 256M heap cap `5807.256 ms`, median GC `194.609 ms` | improved-32k `5589.860 ms`, RSS `358 MB` | Streaming `5491.033 ms`, RSS `358 MB`; checked scoped page-token `5552.988 ms`, RSS `476 MB` | Real log stream modest win/control: heap GC appears in every 1M run but remains only about 1.8% of elapsed. Trusted Streaming wins modestly and reduces RSS; checked scoped page-token is near-tied but high-RSS in this row. |
| LogHub BGL q2 window counts | real file-backed BGL system log | 1M heap `5646.824 ms`, median GC `157.198 ms`, RSS `409 MB`; full-file q2 heap `32161.391 ms`, GC `595.599 ms`, RSS `576 MB` | 1M improved-32k `5509.481 ms`; full-file improved-32k `31459.104 ms`, RSS `490 MB` | 1M Streaming `5605.787 ms`; full-file Streaming `30899.595 ms`; full-file checked scoped page-token `31165.087 ms`, RSS `491 MB` | Full-file q2 is a real-input modest throughput/RSS/tail win for region rows, but heap GC is still under 2% of elapsed, so it is not the missing huge-GC case. |
| LogHub BGL q3 template/session | real file-backed BGL system log | 1M heap `8683.558 ms`, median GC `84.166 ms`, max GC `117.946 ms`, RSS `290 MB` | improved-32k `8635.167 ms`, RSS `237 MB` | Streaming `8615.627 ms`, RSS `237 MB`; checked scoped page-token `8722.008 ms`, RSS `237 MB` | Richer real log query with template/session objects. Regions cut RSS/tails, but checked scoped loses elapsed and heap GC is under 1% of elapsed. |
| Wikimedia real clickstream | real preloaded TSV | heap `126.800 ms` | improved `149.062 ms` | Streaming `157.449 ms` | Heap wins; ceiling control. |
| Linear Road official q1 | official input | heap `162.668 ms` | source pack | HPZone `180.277 ms` | Heap wins; ceiling control. |

## 7. What Is A Win, What Is A Loss

### Wins

| Win | Why it matters |
|---|---|
| Generated Common Crawl WET-shaped q1/q2 | Shows the memory-management regime Rift is built for: many ordinary stream objects, epochal lifetimes, heap spends ~1.5s in GC at 1M. |
| NEXMark Q3/Q8 checked rows | Shows checked operator surface can beat heap and improved SafeZone on recognized stream-methodology shapes, though margins are still modest. |
| Modest real-input page-token WET/WAT rows | Shows the operator works on real Common Crawl records and sometimes improves elapsed/RSS, even though these shards are not GC-heavy enough for a representative case study. |
| RSS/fixed-memory wins | Shows regions can be valuable even when uncapped throughput is only tied or modestly worse; GH Archive q1 under heap cap and several ReML-shaped ports belong here. |
| LogHub BGL q1/q2 modest wins | Shows the page/token/log-line shape generalizes beyond GH Archive and Common Crawl-shaped stressors to a public multi-million-line real system log. The result is useful but still parser/query dominated. |
| SafeZone-backed checked AppendWindow | Shows SafeZone-family backend mechanics can reduce checked overhead without changing the user-level checked API. |
| Checked page/token append operator | Shows static lifetime ownership can remove redundant runtime checks and turn the generated Common Crawl-like q1/q2 path from checked-overhead evidence into a checked generated-stressor win. |
| SafeZone cost decomposition | Shows old SafeZone slowness was largely root bookkeeping and page-size configuration, not inherent region cost. |
| Rootless SafeZone lower bound | Shows what allocator mechanics might achieve when root registration is unnecessary, but only as unsafe evidence. |

### Gated / Negative / Ceiling Results

| Loss / ceiling | Interpretation |
|---|---|
| Current Rift HPZone loses to improved SafeZone on linked/prior-work rows. | Standalone Rift allocator should learn from SafeZone internals instead of being tuned in isolation. |
| Generic checked Common Crawl q1/q2 trail trusted Rift. | The generic `StreamAppendWindow` allocator placement is correct but too costly. The specialized page/token operator fixes this generated q1/q2 shape, but not yet real inputs or other operators. |
| TableRank / rank / fold containers fail focused gates. | Do not use them for application claims yet. |
| Real WET/WAT/Wikimedia/Linear Road rows mostly heap-fastest or median-GC-zero; LogHub/GH Archive are only modest wins. | These inputs, as currently wired, do not stress GC enough for the flagship claim. GH Archive q1 and LogHub BGL q2 are memory-budget/tail/modest-throughput candidates rather than decisive uncapped throughput wins. |
| CPU-bound rows like pipeline surrogate. | Regions add overhead when memory management is not the limiting factor. |
| Fixed-chunk append path. | Array/chunk structures are not automatically faster; the fair heap-chunk and checked chunk-token controls are slower than linked page-token for sequential append/drain. |

### When Rift Wins

| Situation | Mode | What the mode does | Benchmark/input | Why it is GC-heavy or not | Region data / heap data | Evidence class |
|---|---|---|---|---|---|---|
| Generated Common Crawl WET-shaped q1/q2 | `rift-checked-page-token` and `rift-checked-safezone-improved-32k` page-token | Checked operator-owned child buckets; SafeZone-backed row delegates object allocation to improved SafeZone + 32 KiB pages. | Generated WET-shaped stressor, 1M pages / 137M token records. | Heap spends about `1.57 s` in timed GC; many page/token records share page/window lifetimes. | Page/token records in regions; durable counters/config on heap or primitive arrays. | Uncapped generated-stressor throughput win; not real-input proof. |
| Focused page/token append | `rift-checked-page-token`, `rift-checked-safezone-improved-32k` page-token | Same checked API idea without application parsing or aggregation. | Synthetic focused append matrix, 1M records. | Isolates append/object lifetime overhead rather than full GC pressure. | Short-lived records in child bucket regions; operator metadata on parent/heap. | Static-safety overhead-removal win; 2026-05-07 fast path is `27.549 ms` scoped checked vs heap `36.920 ms`. |
| GH Archive q1 under heap budget | `rift-checked-safezone-page-token` compared with capped `heap-immix` | Checked page-token path over SafeZone-backed region allocation. | Real preloaded GH Archive NDJSON, 1M events / 13M event-field records. | Uncapped heap wins by growing to about `1.7 GiB`; under `1G` cap heap collects materially and slows. | Event/field records in regions; preloaded primitive input arrays and control metadata on heap. | Fixed-memory / GC-tail candidate, not uncapped throughput win. |
| LogHub BGL full-file q2 | `rift-trusted-streaming`, `rift-checked-safezone-page-token`, and `safezone-improved-32k` | Line/token records are allocated with window/bucket lifetimes; checked scoped page-token uses the safe operator-owned path. | Real BGL system log, full `4747963` lines / `66868883` line+token records. | Heap spends `595.599 ms` in GC, but that is still under 2% of total elapsed. | Line/token records in regions; file input, severity/component classification, and aggregate counters remain heap/primitive. | Real-input modest throughput/RSS/tail control, not flagship GC-heavy proof. |
| DSPBench Log q2 | `rift-checked-safezone-page-token` | Common-log records, status/update records, and window contributions are allocated in checked page-token buckets. | Real DSPBench `http-server.log`, `55000` common-log lines replayed to 1M events. | Heap spends `44.992 ms` median GC and has an `88.210 ms` max-GC tail, about `2.6%` of elapsed. | Log/status/window contribution records in regions; status counters and input replay state on heap/primitive arrays. | Real-input modest throughput/GC-tail control; RSS is higher than heap, so not a flagship case. |
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
| 1 | DSPBench local-kernel subset | Stream benchmark family with varied applications; choose high object churn kernels only. | Triage 2-3 kernels with clear windows/epochs and local no-cluster execution. |
| 2 | Real RIoTBench-style input | Current local RIoTBench is generated; real sensor traces may have richer parse/window pressure. | Find provenance-clean traces and require material heap GC before tuning. |
| 3 | Larger/multiple Common Crawl WET/WAT shards | Same domain as current GC-heavy stressor; one WAT shard was not enough to trigger GC. | Actual loaded pages/tokens/links large enough; heap median/max GC material. |
| 4 | More real log/NDJSON streams | LogHub BGL q1/q2/q3 and GH Archive are modest wins but not GC-heavy. | Try HDFS/Thunderbird/Spark logs, GDELT, or security logs only if they materialize more per-record objects. |
| 5 | GH Archive file-backed and memory-budget JSON-lines | Preloaded q1 shows heap can avoid GC by growing to GB-scale RSS; under a 1G heap cap checked regions win q1. File-backed q1/q2 rows show RSS/fixed-memory wins, but byte-slice parser rows are not GC-heavy. | Keep as modest-win parser-scratch control. |
| 6 | NEXMark Q3/Q8/Q9/Q11 | Recognized generated stream methodology; already has promising rows. | Keep as methodology/regression, not real-input proof. |
| 7 | Real MLKit/ReML benchmark sources | Non-stream but real prior-system source programs; useful for region+GC safety/performance comparison. | Build/run paper-era MLKit modes and local Scala Native ports; compare ratios, RSS, and GC counts. |
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
   `samply`/flamegraph-style sampled profiles where available. Use `samply` on
   the linked Scala Native binary, not `sbt run`, to inspect CPU composition and
   visible GC pause/collection frames. Use profiling as diagnostic evidence, not
   headline timing. The first GH Archive file-backed
   q1 profile is now recorded in `docs/CPU_PROFILE_REPORT.md`; it points to
   `BufferedReader`/UTF-8/StringBuilder/field-count/hashing/gzip work, not
   region close, as the next bottleneck. Continue profiling the smallest
   representative set: Common Crawl-shaped q1/q2 (`heap-immix`,
   `rift-checked-page-token`, `rift-checked-safezone-page-token`), Dataflow
   AGGREGATE exact-array versus true `EpochFold`, StreamFlex trusted Rift
   versus checked `TransactionRegion`, and Common Crawl q3 parser-scratch. The
   goal is to
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

7. **Continue the ReML/MLKit comparison as a separate axis.**
   Tier 1 local medians now exist. Next, pin the exact MLKit/ReML artifact or
   build environment, verify the paper's `rg`/`rg-`/`r` command mapping, and
   decide whether Tier 2 ports are worth adding. Keep exact ReML artifact search
   open, and treat the fixed erased-generic probe as current compiler evidence
   rather than a full proof of arbitrary heap alias safety.

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
- `docs/REML_ARTIFACT_RUNBOOK.md`
- `docs/CPU_PROFILE_REPORT.md`
- `docs/LITERATURE_BENCHMARK_CONTRACT.md`
- `evidence/SN_WIN_ENVELOPE.md`
- `evidence/SAFEZONE_COST_MATRIX.md`
- `docs/HANDOFF.md`
