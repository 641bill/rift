# Rift Benchmark Catalog

Date: 2026-05-05
Last updated: 2026-05-18 12:55 CEST

Status: working benchmark guide. Use this document to understand what each
benchmark is meant to test before reading the detailed result files in
`evidence/`.

## 1. How To Read The Benchmarks

Rift now has many benchmarks because they answer different questions. They
should not be collapsed into a single "Rift is faster/slower" statement.

| Evidence class | Question answered | Examples |
|---|---|---|
| Runtime-only | Is the allocator/reclaim path competitive before safety/operator overhead? | GCBench, ListOfLists, Dataflow trusted modes |
| Topology/layout | Does the object graph shape fit region reclaim? | ListOfLists linked/flat/chunked/topology, direct-epoch q2 summaries |
| Prior-work methodology | Does Rift behave well on Broom/Yak/StreamFlex/Stancu-shaped workloads? | Broom retained dataflow, Dataflow, StreamFlex, Yak, Stancu |
| MLKit/ReML lineage | Does Rift address classic safe region+GC workloads with higher-order and polymorphic code? | ReML paper table, `ReMLRegionMatrix` Tier 1 ports |
| Checked operator | Is a reusable safe API cheap enough for application use? | ObjectAllocationLowering, CheckedRegionBuffer, PageToken, AppendWindow, WindowFold, TableRank |
| Generated stream stressor | Does a realistic stream shape create enough heap pressure to show a memory-management win? | Common Crawl WET-shaped, NEXMark Beam-default |
| Real-input stream control | Does a public/real input preserve the same memory pressure? | Yak `graphreal`, AskUbuntu `topwordreal`, real WET/WAT, GH Archive, LogHub, Wikimedia, Linear Road |
| Real streaming-input replay | Does the result still hold when real records are consumed incrementally without preloading the full input? | Theodolite retained UC4; Wikimedia retained clickstream-session; LogHub HDFS `streaming-file` top templates, q3 template/session, and retained session/join; GH Archive `streaming-file` q1/q2; StackExchange, SNAP/Yak, and DSPBench archive-backed rows |
| Backend portability | Which parts of Rift are Scala-level versus Scala Native-specific? | `docs/SCALA_LEVEL_BACKEND_PLAN.md`; JVM/Scala.js/Wasm/analysis-only are planned experiments, not measured rows |
| Ceiling/negative | Does the workload prove heap/CPU/I/O dominates? | pipeline surrogate, real WET/WAT median-GC-zero rows |

Headline claims should use the canonical memory-mode names from
`docs/MEMORY_MODE_TAXONOMY.md`.

Headline claims should also follow `docs/FAIR_EVALUATION_PROTOCOL.md`.
Current result files are mostly L2 standard-stat rows; use
`evidence/MEASUREMENT_OVERHEAD_PROTOCOL.md` and
`evidence/FINAL_CLEAN_HEADLINE_RESULTS.md` when preparing final-clean headline
timing.

Default final-selection runs now exclude current SafeZone and rootless/unsafe
lower-bound rows. Use `RIFT_EVAL_INCLUDE_CONTROLS=1`,
`RIFT_BENCH_INCLUDE_CONTROLS=1`, or an explicit `*_MODES` variable when a
benchmark needs provenance or lower-bound controls.

The first clean default headline sweep is summarized in
`evidence/FINAL_SELECTION_HEADLINE_2026_05_06.md`.

The clean direct-epoch topology sweep is summarized in
`evidence/DIRECT_EPOCH_TOPOLOGY_MATRIX.md`.

Prior-system comparison tables should not force all systems into one metric
schema. Use the metric axes each paper reports, then add Rift's standardized
local metrics separately. The detailed contract is
`docs/LITERATURE_BENCHMARK_CONTRACT.md`. The higher-level interpretation of
why those systems win and what their limits are is
`docs/PRIOR_WORK_MEMORY_MANAGEMENT_INTERPRETATION.md`.

The latest GC-heavy benchmark-search note is
`evidence/GC_HEAVY_BENCHMARK_INVESTIGATION.md`. Use it when selecting new real
streaming or data-processing rows: larger input alone is not enough; the next
candidate should naturally retain ordinary objects in joins, sessions,
windows, graph epochs, transactions, or high-cardinality keyed state.

The current presentation-facing stream/application sweep is
`evidence/SELECTED_STREAMS_SWEEP_2026_05_16.md`, produced by
`RIFT_EVAL_SUITES=selected-streams`. It covers Common Crawl page-token,
NEXMark, GH Archive, LogHub q2/q3, LogHub top templates, and DSPBench
Fraud/Log q2. Theodolite q2 remains opt-in in the runner because it requires
`THEODOLITE_POWER_INPUT` to point to the real household-power trace, but the
current evidence file now includes a selected-row addendum for that local
trace.

## 1.1 Outcome Labels

Do not collapse all non-representative rows into "mixed" or "failed." Use a
more precise label:

| Label | Use when | Example |
|---|---|---|
| representative throughput win | elapsed win is large enough to support the final story | generated Common Crawl-shaped q1/q2 page-token |
| modest throughput win | elapsed improves but margin or provenance is not strong enough for a representative claim | NEXMark Q8, real WET/WAT page-token controls |
| RSS win | memory footprint improves materially even if elapsed is tied or slightly worse | ReML-shaped `ratio`, some checked fold/buffer controls |
| fixed-memory/tail win | heap wins uncapped by growing large, but region wins under cap or reduces max-GC/tail events | GH Archive q1 under `1G` heap cap |
| speed-gated | correct and useful API, but elapsed overhead is too high for final/public performance claims | `EpochFold`, `TableRank` |
| ceiling/negative | no material elapsed, RSS, GC, or latency benefit | pipeline, current Wikimedia/Linear Road rows |

Throughput means total completed work per unit time; in these batch matrices,
lower elapsed time means higher throughput. Latency means time observed by one
event/request, usually reported as p50/p95/max or deadline misses. A mode can
win throughput and lose latency, or lose median throughput but improve max-GC
tails.

## 1.2 Comparison Classes

Every headline table should identify the comparison class before interpreting
the numbers. Do not mix these rows into a single unqualified "heap vs Rift"
claim.

| Comparison class | What is compared | What it can prove |
|---|---|---|
| Natural heap baseline | Existing heap implementation against the best safe region topology. | Practical end-to-end result for the current program. |
| Same-shape heap control | Heap implementation using the same operator/topology as the region row. | Whether the win is from region memory placement or from a better algorithm/topology. |
| Summary-only topology | Records update summaries on append and are not retained until close. | Operator/data-processing lower bound; not a pure memory-management win. |
| Retained-object drop-anchor | Heap and region both allocate ordinary records, retain them until the epoch/window close, update summaries on append, and do not traverse records at close. | Fair memory-management comparison: heap GC reclaim versus region bulk close/reset. |
| Best checked topology | The fastest safe checked topology for the workload: usually `epoch`, `window`, or `page`. | User-facing Rift result. |
| Unsafe/trusted lower bound | Rootless/trusted region modes without the final checked user guarantee. | Optimization potential only, not a safe-system claim. |

Use the phrase `heap-retained-drop-anchor` in prose for
`heap-epoch-retained-no-traverse` when clarity matters. The heap row also
performs O(1) user-level close by dropping the bucket reference; the difference
is that heap objects remain for the GC to trace/reclaim later, while region
objects are reclaimed by closing/resetting the allocation area. This is why the
retained comparison isolates memory management better than comparing checked
regions against a summary-only heap row.

For prior-work-style headline rows, however, show the natural heap/GC program
against the region-enabled checked program first. Same-shape retained
heap/drop-anchor rows are appendix/mechanism controls for causality, not the
only paper-facing comparison. `BroomRetainedDataflowMatrix` is the first row
added under this rule.

Summary-only topology tables must be symmetric. If a result reports
`heap-direct-summary-only`, it should also report the checked/region
direct-summary counterpart when that framework topology exists. The point is to
show that the topology is fast, not to imply the lower bound is heap-only.

Prior region systems also choose a justified lifetime topology rather than
enumerating every possible heap rewrite. Broom uses dataflow/operator epochs,
Yak separates epoch-local data from durable control objects, StreamFlex uses
stream/period lifetimes and reports latency/throughput axes, Stancu et al. use
transaction-region annotations, and ReML/MLKit use compiler-selected region
modes. Rift should follow the same discipline: state the topology, state which
objects are region-local, include same-shape heap controls when computation
changes, and report unsafe/rootless modes only as lower bounds.

That prior-work principle is memory-management-first: reusable operators are
valuable only insofar as they expose an epoch/page/window/transaction lifetime
that the backend can reclaim in bulk. Do not present a benchmark-specific
operator as the main contribution unless it generalizes the lifetime boundary
and passes same-shape controls.

## 2. Core Runtime Baselines

| Benchmark | What it does | Input type | Main interpretation |
|---|---|---|---|
| GCBench | Allocates tree-shaped object graphs and stresses allocation/reclaim. | Synthetic runtime stressor | Useful for raw allocator/root-bookkeeping comparison; not a stream application. |
| ListOfLists | Builds many linked lists, plus flat/chunked/topology variants. | Synthetic topology stressor | Shows where linked object topology hurts/helps regions and where chunked layouts change the story. |
| Pipeline surrogate | CPU-heavy pipeline with little material GC pressure. | Synthetic ceiling control | Useful mainly to show that region memory cannot fix CPU-bound code. |

"Chunked" in ListOfLists means several logical list elements are grouped into a
larger region-friendly block/chunk. It changes topology and allocation count,
so it is layout evidence, not a pure allocator comparison.

## 3. Prior-Work Methodology Benchmarks

| Benchmark | Comparator anchor | What it does | Main interpretation |
|---|---|---|---|
| Dataflow SELECT/AGGREGATE/JOIN | Broom-style dataflow | Stream operators with short-lived tuples and operator-local lifetimes. | Good prior-work-shaped runtime evidence; SafeZone-family rows are often strong. |
| Broom retained dataflow | Broom/Naiad-style timestamped dataflow | Timestamped aggregate and join retain ordinary event/value objects in per-timestamp dictionaries until notify/close. The q17 workload adds deterministic generated `Part`/`LineItem` records, per-part retained aggregates, and a TPC-H-Q17-like below-average quantity/revenue filter at timestamp close. Q17 can read DBGEN/TPC-H `part.tbl` and `lineitem.tbl` with `BROOM_Q17_INPUT_MODE=tpch-file`, or generate temporary DBGEN tables per run with `BROOM_Q17_INPUT_MODE=tpch-dbgen` so persistent `cache/tpch-sf*` tables are optional. | Prior-work-style headline row: natural heap/GC versus checked Rift, with checked scoped as the best-safe-region comparison row. At 20M active-16, aggregate checked Rift is `8.48 s`, `53 MB` RSS vs heap `10.78 s`, `236 MB`, with heap L2 GC `953.153 ms`; join checked Rift is `8.09 s`, `57 MB` vs heap `9.88 s`, `438 MB`, with heap L2 GC `486.649 ms`. Q17 active-16 20M is checked Rift `9.67 s`, `50 MB` RSS vs heap `14.45 s`, `232 MB`, with heap L2 GC `1370.380 ms`. Aggregate/join have fixed-memory failure evidence; generated q17 is throughput/GC/RSS evidence because heap caps down to `256M` complete. DBGEN SF1 q17 is checked Rift `51.47 s`, `48.7 MB` RSS vs heap `55.44 s`, `433.3 MB`; heap fails at `128M` while checked Rift completes around `49-53 MB`. Evidence is in `evidence/BROOM_RETAINED_DATAFLOW_MATRIX.md`. |
| StreamFlex matrix | StreamFlex-style memory pressure/latency | Windowed stream pressure and latency-style measurements. | Methodology evidence, not exact artifact reproduction. |
| StreamFlex design matrix | StreamFlex stable/transient/capsule system design | Four-stage object pipeline with heap stable state, transient per-period objects, bounded primitive capsules, saturated throughput, paced latency, pressure latency, RSS, GC, and deadline metrics. | Rift-native StreamFlex design reproduction. First 1M L1 throughput row: checked epoch scoped `1.27 s` / `7.9 MB` RSS vs heap `1.52 s` / `12.4 MB`; pressure-latency L2: checked epoch scoped is fastest while checked epoch stream eliminates misses. Gap analysis is in `evidence/STREAMFLEX_GAP_ANALYSIS.md`: current speedup is close to the heap-GC-removal bound, so larger StreamFlex-style gains require reducing non-GC runtime costs and/or reproducing stronger scheduler/capsule pressure. |
| StreamIt kernel matrix | StreamFlex / StreamIt BeamFormer and FilterBank names | Local ports of FilterBank and BeamFormer from public StreamIt sources, with throughput, p50/p95/p99/p999/max latency, deadline misses, RSS, and GC metrics. | StreamFlex-axis control, not a GC-heavy Rift win. The 3-run L1 control matrix is complete; faithful primitive DSP shape is compute/array dominated. Evidence is in `evidence/STREAMIT_KERNEL_MATRIX.md`. |
| Yak matrix | Yak-style epochs and promotion pressure | Topword/filter, GraphChi-like intervals, grouped sort, escape/promotion proxies, `graphreal` over real SNAP edge lists, and `topwordreal` over real Stack Exchange AskUbuntu `Posts.xml` text. The LiveJournal topology follow-up separately measures whole-run checked regions, per-epoch checked regions, and page-token checked regions. The topword follow-up adds same-shape heap top-k retained controls and reusable `EpochTopKByKey` rows. | Useful to compare static checked regions against dynamic region/promotion ideas and to choose a region topology. `graphreal` is real-input Yak-shaped graph evidence, not exact Yak/GraphChi reproduction. AskUbuntu `topwordreal` is the first real text/top-word row: direct checked epoch is fastest among safe checked rows, while reusable top-k remains a lower-RSS but slower-than-direct API candidate. |
| Stancu matrix | RegionScope/static hybrid analysis | Transaction/region-boundary style workloads. | Safety/methodology anchor; not full SPECjbb reproduction. |
| SPECjbb2005 workload port | Stancu/SPECjbb2005 methodology | Deterministic single-process Scala Native port of the transaction workload shape, with durable warehouse/customer/stock state on heap arrays and transaction-local request/line/probe/receipt objects in epochs. | Clean-room workload port, not official SPECjbb2005. L2 rows cover warehouses 4..8; an L1 final-clean 8-warehouse representative row is reported in `evidence/SPECJBB2005_PORT_MATRIX.md`. |
| ReML / MLKit lineage | Elsman 2023 / MLKit typed-region lineage | Paper-reported benchmark table plus local Scala Native-shaped ports for classic SML benchmark programs. | New comparison axis for region polymorphism and GC-safety; not stream evidence and not exact ReML reproduction yet. |

These rows are intentionally labeled as methodology reproductions unless the
original benchmark artifact, input, and configuration are actually used.

The ReML PLDI-style table is now split out into
`evidence/REML_MLKIT_PLDI_TABLE.md`; `evidence/REML_COMPARISON_MATRIX.md`
keeps the broader source/provenance and local-port details. The ReML track has
four evidence classes:

| Class | Meaning |
|---|---|
| Paper-reported | Elsman 2023 Figure 9 data copied into tracked evidence, not rerun. |
| Exact artifact | Partial source provenance found in the public MLKit repo; still only valid after the paper-era revision/configuration and local `mlkit`/`mlton` runs are pinned. |
| Scala Native ports | Local `ReMLRegionMatrix` ports; valid for Rift-vs-Scala-Native ratios, not cross-language claims. |
| Safety probes | ReML-inspired compiler tests for polymorphic/higher-order GC-safety hazards; the current durable/static generic heap-retention probe is active and passing. |

## 4. Checked Operator Matrices

| Benchmark | What it isolates | Latest meaning |
|---|---|---|
| ObjectAllocationLoweringMatrix | Plain object allocation with no window/rank/query traversal. | Raw checked region allocation is not the main bottleneck: at 10M objects, checked SafeZone-backed allocation is `143.319 ms` versus heap `271.121 ms` with `105.807 ms` GC. |
| CheckedRegionBufferMatrix | Growable buffer, fixed `ObjectBuffer`, and exact-array retention. | Exact checked arrays are fast; generic bounded/growable buffers still pay layout/access/dispatch overhead. |
| CheckedAppendWindowMatrix | Reusable checked append/window bucket API. | Cursor/cached paths made the API viable, but generic paths are still slower than operator-owned fast paths. |
| CheckedPageTokenAppendMatrix | Operator-owned page/event/window append path. | First focused checked operator gate that clearly passes; it removes per-record stale-bucket checks and region lookups. |
| StreamChunkAppendWindow control | Operator-owned fixed object-array chunks per bucket. | Correct but slower than linked page-token at 1M; use as negative/control evidence for sequential append/drain workloads. |
| CheckedWindowFoldMatrix | Additive window fold/count API. | Correct but failed the 1M speed gate; do not use as application evidence yet. |
| CheckedStreamWindowRank/TableRank | Dense/keyed rank and fused table-rank structures. | Correct and useful framework progress, but current rank/table CPU overhead is too high for DEBS Q1 claims. |
| CheapOperatorFamilyMatrix | First reporting-mode/operator-family wiring for Dataflow SELECT, Dataflow AGGREGATE, ListOfLists linked topology, epoch buffers, and multi-list transaction regions. | Focused and staged-headline rows now include positive `PageTokenMapFilter`, `RegionList`, `EpochBuffer`, and partial-positive `TransactionRegion` evidence. Latest StreamFlex scoped checked `TransactionRegion` is `39.019 ms` versus heap `42.860 ms` and improved SafeZone `41.327 ms`; Rift-native checked transaction remains speed-gated. |

"Page/token" does not mean the benchmark is only about text tokens. It means
one page, event, or bucket owns many short-lived records. The operator owns the
bucket lookup, child-region access, append, and close, so checked code can skip
runtime work that static ownership makes redundant.

The cheap-operator family milestone generalizes that idea cautiously:

| Family | Intended shape | Current implementation status |
|---|---|---|
| `PageTokenMapFilter` | SELECT/filter/project rows where each page/event/window owns short-lived projected records. | First Dataflow SELECT page-token rows wired and smoke-tested. |
| `EpochFold` | Additive count/sum/fold rows with epochal record lifetimes. | General reusable API exists and is correct, but the latest true `EpochFold` row is `92.923 ms`; keep it gated until redesigned. |
| `RegionListOfListsBuilder` | Linked object topology where a whole structure/epoch dies together. | Checked builder row wired and smoke-tested; clean medians pending. |
| `EpochBuffer` | Append/drain epoch buffers for Yak/StreamFlex-style data/control splits. | Implemented and focused-positive: 1M checked epoch buffer `26.673 ms`, scoped checked epoch buffer `25.448 ms`, versus heap epoch `27.164 ms` with `5.707 ms` GC. |
| `TransactionRegion` | Multi-stage batch/transaction pipelines with several temporary lists and one shared child-region lifetime. | Implemented and partially validated. It fixes stacked `EpochBuffer` granularity in StreamFlex-shaped code; latest scoped checked transaction beats heap/improved SafeZone, while Rift-native checked remains slower than heap. |

Do not use these names to imply all applications can use the same operator.
Ranking, median maintenance, hash joins, and top-k still need separate focused
operators and gates.

## 5. Stream And Application Benchmarks

| Benchmark | Input type | Current status |
|---|---|---|
| DEBS 2015 | Real taxi CSV samples/full-month controls | Correctness and region-placement evidence exists, but elapsed wins are modest and much CPU is query/output work. Downstream validation, not the current tuning target. |
| NEXMark | Official Beam-default generated profile in local Scala Native harness | Useful recognized stream methodology. L1 final-clean rows now show checked Rift wins on selected q3/q8/q9/q11 rows: q3 `5.86 s` vs heap `6.18 s`, q8 `9.21 s` vs heap `9.54 s`, q9 `15.03 s` vs heap `16.27 s`, and q11 `4.36 s` vs heap `4.47 s` for 1M events x20 iterations. RSS also drops sharply versus heap. This remains generated methodology evidence, not real-input proof or exact Beam runner evidence. |
| Common Crawl WET-shaped | Generated WET-like pages/lines/tokens | Strongest GC-heavy stream stressor: heap spends about `1.55-1.59 s` in timed GC at 1M generated pages; trusted and page-token checked rows win. This is not real Common Crawl input proof. |
| Real Common Crawl WET/WAT | Public preloaded WET/WAT shards | Current shards have median timed GC of zero. Page-token rows work and win modestly on WAT, but these are ceiling/control rows. |
| GH Archive | Real hourly NDJSON GitHub event files | Strongest current real-input modest-win candidate, but not GC-heavy proof. Uncapped preloaded heap wins median by growing to about `1.7 GiB`; under a 1G heap cap, checked SafeZone-backed q1 wins. Legacy string-parser file-backed q1/q2 rows give RSS/fixed-memory wins but are parser/string dominated. The byte-slice file-backed parser reuses line buffers and extracts JSON fields from raw UTF-8 bytes; at two hourly files / 200k events, L1 final-clean checked scoped page-token is a modest elapsed/RSS win: q1 `12.89 s`, `101 MB` RSS vs heap `13.17 s`, `265 MB`; q2 `12.87 s`, `102 MB` RSS vs heap `13.18 s`, `244 MB`. `GITHUB_ARCHIVE_INPUT_MODE=streaming-file` now makes the same bounded replay an explicit `real-streaming-input` row. At 100k events, checked page-token wins q1 `9.62 s` vs heap `10.39 s` and q2 `9.16 s` vs heap `9.38 s`, while removing observed heap max-GC tails around `71-72 ms`; median heap GC is still zero. Generated/preloaded retained q2 is strong retained-object memory-management evidence in L1: checked scoped retained `3.44 s`, `16 MB` RSS vs retained heap `4.62 s`, `147 MB`, while summary-only `1.28 s` stays topology evidence only. |
| LogHub / LogPAI BGL and HDFS v1 | Real preloaded, file-backed, and streaming-input system logs | Real log matrix with q1 tokens, q2 window counts, q3 template/session mining, focused top-template retained rows, and retained session/join triage. HDFS v1 adds an 11.2M-line Hadoop log; its 1M q2 L2 row is a modest checked page-token row: checked scoped page-token `7871.856 ms` vs heap `8227.369 ms`, removing heap's `92.659 ms` median GC and lowering RSS. Its L1 final-clean row is more conservative: checked scoped page-token ties heap elapsed (`25.56 s` vs `25.60 s` for 1M lines x3 q2 iterations) while cutting RSS from about `409 MB` to about `79 MB`. The top-template row is stronger under the preloaded-input protocol: after the `EpochTopKByKey` hot-path pass, real HDFS retained heap is `111.704 ms`, checked scoped retained is `76.818 ms`, and reusable checked scoped top-k is `82.170 ms`; L1 1M x20 is retained heap `5.52 s` / `205 MB` versus reusable checked top-k `4.88 s` / `28 MB`. The 5M x5 scale-up keeps reusable checked top-k ahead at `18.26 s` / `92 MB` versus retained heap `19.04 s` / `504 MB`. New `streaming-file` top-template replay is the first true `real-streaming-input` row: at 1M HDFS lines, reusable checked scoped top-k L1 is `8.06 s`, RSS `12 MB`, versus retained heap `8.10 s`, RSS `76 MB`; L2 removes `32.681 ms` heap GC. HDFS q3 template/session now also has `LOGHUB_INPUT_MODE=streaming-file`: checked scoped page-token cuts RSS from about `862 MB` to `130 MB` and lowers max GC tails, but loses L1 elapsed (`30.29 s` vs heap `26.88 s`), so it is RSS/fixed-memory control evidence. The retained session/join streaming-file triage validates a natural retained-object shape but remains parser/hash dominated: session heap GC is only `82.341 ms` inside `6595.172 ms`, and join heap GC is only `9.474 ms` inside `6837.810 ms`. Generated q2/q3 direct epoch remains topology evidence, while generated top templates now provide retained top-k evidence. |
| DSPBench Spike/Fraud/Log Processing | Public DSPS benchmark source and bundled real sample files | `DSPBENCH_REGION_MATRIX.md` now includes local single-process Spike, Fraud, and Log rows. Spike is modest/control only. Fraud q2 and Log q2 are the useful real-input regression rows. L1 final-clean rows show Fraud q2 checked scoped page-token as an RSS win but not an elapsed win (`4.44 s`, `59.5 MB` RSS vs heap `4.39 s`, `358 MB`; trusted Streaming lower bound `4.18 s`). Log q2 checked scoped page-token is a modest elapsed/RSS win (`8.79 s`, `47.6 MB` RSS vs heap `8.89 s`, `308 MB`). L2 standard-stats rows remain the GC-tail source: Fraud q2 checked reduces median GC from `69.686 ms` to `15.554 ms`; Log q2 checked cuts max GC from `88.210 ms` to `18.584 ms`. Generated/indexable q2 direct-epoch rows are much stronger (`260.432 ms` checked scoped direct epoch vs heap `403.098 ms` on Fraud q2; `220.040 ms` vs heap `360.853 ms` on Log q2), but they are topology/operator evidence until heap same-shape controls are added. |
| Theodolite power | Real UCI household power-meter trace, preloaded and streaming-input | Local single-process Theodolite UC2/UC4-style downsampling/hierarchical aggregation over real energy data. The older preloaded/full-local q2 row ties elapsed and removes heap GC, but RSS is similar. `THEODOLITE_POWER_INPUT_MODE=streaming-file` now parses records inside each run through the shared byte-line reader and a reusable semicolon byte-field cursor. At 1M q2, checked scoped epoch is an L1 throughput/RSS/fixed-memory win: `3.77 s`, `24.9 MB` RSS versus heap `3.87 s`, `75.3 MB`; L2 checked scoped is `967.144 ms`, GC `0 ms` versus heap `1007.030 ms`, GC `19.932 ms`. The previous `String.split` streaming row is superseded because parser allocation inflated apparent GC pressure. |
| Wikimedia | Real/generated TSV/clickstream-style rows | Old preloaded counter/clickstream rows remain ceiling/regression controls. The named `wikimedia-clickstream-session` retained streaming workload is now positive evidence: at 1M, checked Rift is `5.81 s`, `138 MB` RSS versus heap `6.50 s`, `784 MB`; at 5M, checked Rift is `27.86 s`, `138 MB` versus heap `28.77 s`, `1.54 GB`, with heap max GC `1066.487 ms` and heap-cap failures at `1G`, `768M`, and `512M`. This is a local named workload over public compressed Wikimedia data, not an official Wikimedia benchmark artifact. |
| Linear Road | Official/generated position-report methodology | Useful latency/window methodology, but current rows are not GC-heavy enough for a Rift case study. |
| Yahoo-style ads | Local/generated ad-stream methodology | Some wins exist, but provenance is generated/local rather than official real input. |
| RIoTBench-style IoT / MHEALTH | Local/generated IoT ETL/statistics methodology plus UCI MHEALTH real sensor logs | The real/provenance gap is fixed for one FIT-style input, but MHEALTH 1M q1/q2 report zero timed heap GC. q1 is a near-tie with heap fastest; q2 gives a small SafeZone win. Park as ceiling/control evidence. |

## 6. Current Interpretation

The good numbers are meaningful, but they are narrower than a broad "regions
beat GC" claim:

- Region reclaim helps most when many ordinary objects share an epochal
  lifetime and the heap cannot just grow without collecting.
- Checked allocation can be fast when the compiler/runtime path is direct and
  the retention structure is simple.
- Generic checked containers still add CPU overhead through growth, dispatch,
  indexing, callback, or rank/table maintenance.
- Real input often does not trigger much timed GC at the measured scale because
  parsing, aggregation, checksum/output, or CPU traversal dominates.
- Heap-size controls matter: an uncapped heap can buy throughput with high RSS,
  while region modes are more interesting under fixed-memory or tail-latency
  constraints.

## 6.1 Real Dataset Expansion

The generated Common Crawl-shaped and NEXMark rows are useful but not enough.
The next real-data expansion should prioritize datasets that are naturally
record-oriented and can be processed as an event/page/window stream. The new
`real-streaming-input` ladder is stricter than file-backed replay: rows must
process records from a streaming source and avoid total-input parsed arrays.

| Candidate | Input form | First query shape |
|---|---|---|
| GH Archive | hourly real GitHub events, JSON/NDJSON | `streaming-file` byte-slice q1/q2 triage complete; scale only if heap caps or multi-hour replay expose material pressure |
| LogHub / LogPAI system logs | real HDFS/BGL/Spark/Thunderbird/etc. log lines | HDFS top templates and HDFS q3 template/session now have `streaming-file`; park q3 unless heap caps/latency expose stronger pressure |
| Larger/multiple Common Crawl WET/WAT shards | public WET/WAT archive records | page/token/link object materialization and domain/window counts |
| Theodolite plus real industrial energy data | Theodolite UC2/UC4 methodology plus a real public power-meter trace | downsampling or hierarchical aggregation over real active-power measurements |
| GDELT events | public event files | parse/project event fields and windowed country/topic counts |
| Public web/server/security logs | Apache/NASA-style logs or JSON security events | tokenize fields, filter/project, per-window counts |
| DSPBench local kernels | source benchmark workloads | choose kernels with clear epoch/window lifetimes and high object churn |
| MLKit/ReML source benchmarks | real prior-system benchmark programs | non-stream region+GC comparison by elapsed/RSS/GC count |
| SPECjbb2005 workload port | licensed SPECjbb2005 source/workload if obtained, or a documented Scala Native port of the transaction core | Stancu/SPECjbb2005 methodology comparison by elapsed, GC time/count, RSS, heap-cap behavior, region-freed fraction, and annotation/API-boundary count |

## 7. What Has Not Been Proven Yet

Rift still does not have a final checked result on a public, real-input,
GC-heavy stream workload that beats both `heap-immix` and
`safezone-improved-32k` by a clear case-study margin.

The nearest candidates are:

1. DSPBench local kernels: Spike/Fraud/Log q0/q1/q2 are implemented. Fraud q2
   and Log q2 are regression rows; continue only with richer DSPBench kernels
   or larger provenance-clean inputs.
2. Larger or richer Theodolite-style IoT input paired with real industrial-energy data, or larger machine/security traces. RIoTBench/MHEALTH is now wired but parked as zero-GC ceiling evidence; Theodolite source is cloned, and the local UCI power streaming-file byte-cursor row is a useful RSS/fixed-memory win but not a huge-GC flagship.
3. More LogHub / LogPAI variants only if they materialize richer per-line
   objects than the current HDFS retained top-template path.
4. Larger or multiple real Common Crawl WET/WAT shards.
5. GH Archive with heap-budgeted/file-backed/tail-latency runs as a modest-win
   control, not GC-heavy proof.
6. Another real NDJSON/log-event stream with heavier object churn.
7. Additional RIoTBench-style local kernels only if they use richer tasks or
   a different provenance-clean input that shows material heap pressure.

## 8. Source Files

Read these result files first for detailed numbers:

- `evidence/OBJECT_ALLOCATION_LOWERING_MATRIX.md`
- `evidence/CHECKED_REGION_BUFFER_MATRIX.md`
- `evidence/CHECKED_PAGE_TOKEN_APPEND_MATRIX.md`
- `evidence/CHEAP_OPERATOR_FAMILY_MATRIX.md`
- `evidence/REML_COMPARISON_MATRIX.md`
- `evidence/COMMON_CRAWL_LIKE_MATRIX.md`
- `evidence/REALISTIC_STREAM_GC_MATRIX.md`
- `evidence/GITHUB_ARCHIVE_REGION_MATRIX.md`
- `evidence/LOGHUB_REGION_MATRIX.md`
- `evidence/REAL_INPUT_BENCHMARK_SEARCH.md`
- `evidence/SN_WIN_ENVELOPE.md`
- `evidence/EVALUATION_SUMMARY_TABLES.md`
- `evidence/ALL_PHASE_RESULTS.md`
