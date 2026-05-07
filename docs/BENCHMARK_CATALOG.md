# Rift Benchmark Catalog

Date: 2026-05-05
Last updated: 2026-05-07 12:24 CEST

Status: working benchmark guide. Use this document to understand what each
benchmark is meant to test before reading the detailed result files in
`evidence/`.

## 1. How To Read The Benchmarks

Rift now has many benchmarks because they answer different questions. They
should not be collapsed into a single "Rift is faster/slower" statement.

| Evidence class | Question answered | Examples |
|---|---|---|
| Runtime-only | Is the allocator/reclaim path competitive before safety/operator overhead? | GCBench, ListOfLists, Dataflow trusted modes |
| Topology/layout | Does the object graph shape fit region reclaim? | ListOfLists linked/flat/chunked/topology |
| Prior-work methodology | Does Rift behave well on Broom/Yak/StreamFlex/Stancu-shaped workloads? | Dataflow, StreamFlex, Yak, Stancu |
| MLKit/ReML lineage | Does Rift address classic safe region+GC workloads with higher-order and polymorphic code? | ReML paper table, `ReMLRegionMatrix` Tier 1 ports |
| Checked operator | Is a reusable safe API cheap enough for application use? | ObjectAllocationLowering, CheckedRegionBuffer, PageToken, AppendWindow, WindowFold, TableRank |
| Generated stream stressor | Does a realistic stream shape create enough heap pressure to show a memory-management win? | Common Crawl WET-shaped, NEXMark Beam-default |
| Real-input stream control | Does a public/real input preserve the same memory pressure? | real WET/WAT, GH Archive, LogHub, Wikimedia, Linear Road |
| Ceiling/negative | Does the workload prove heap/CPU/I/O dominates? | pipeline surrogate, real WET/WAT median-GC-zero rows |

Headline claims should use the canonical memory-mode names from
`docs/MEMORY_MODE_TAXONOMY.md`.

Default final-selection runs now exclude current SafeZone and rootless/unsafe
lower-bound rows. Use `RIFT_EVAL_INCLUDE_CONTROLS=1`,
`RIFT_BENCH_INCLUDE_CONTROLS=1`, or an explicit `*_MODES` variable when a
benchmark needs provenance or lower-bound controls.

The first clean default headline sweep is summarized in
`evidence/FINAL_SELECTION_HEADLINE_2026_05_06.md`.

Prior-system comparison tables should not force all systems into one metric
schema. Use the metric axes each paper reports, then add Rift's standardized
local metrics separately. The detailed contract is
`docs/LITERATURE_BENCHMARK_CONTRACT.md`.

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
| StreamFlex matrix | StreamFlex-style memory pressure/latency | Windowed stream pressure and latency-style measurements. | Methodology evidence, not exact artifact reproduction. |
| Yak matrix | Yak-style epochs and promotion pressure | Topword/filter, GraphChi-like intervals, grouped sort, escape/promotion proxies. | Useful to compare static checked regions against dynamic region/promotion ideas. |
| Stancu matrix | RegionScope/static hybrid analysis | Transaction/region-boundary style workloads. | Safety/methodology anchor; not full SPECjbb reproduction. |
| ReML / MLKit lineage | Elsman 2023 / MLKit typed-region lineage | Paper-reported benchmark table plus local Scala Native-shaped ports for classic SML benchmark programs. | New comparison axis for region polymorphism and GC-safety; not stream evidence and not exact ReML reproduction yet. |

These rows are intentionally labeled as methodology reproductions unless the
original benchmark artifact, input, and configuration are actually used.

The ReML track has four evidence classes:

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
| NEXMark | Official Beam-default generated profile in local Scala Native harness | Useful recognized stream methodology. Some wins on Q3/Q8-style rows, but not a decisive real-data case study. |
| Common Crawl WET-shaped | Generated WET-like pages/lines/tokens | Strongest GC-heavy stream stressor: heap spends about `1.55-1.59 s` in timed GC at 1M generated pages; trusted and page-token checked rows win. This is not real Common Crawl input proof. |
| Real Common Crawl WET/WAT | Public preloaded WET/WAT shards | Current shards have median timed GC of zero. Page-token rows work and win modestly on WAT, but these are ceiling/control rows. |
| GH Archive | Real hourly NDJSON GitHub event files | Strongest current real-input modest-win candidate, but not GC-heavy proof. Uncapped preloaded heap wins median by growing to about `1.7 GiB`; under a 1G heap cap, checked SafeZone-backed q1 wins. Legacy string-parser file-backed q1/q2 rows give RSS/fixed-memory wins but are parser/string dominated. The new byte-slice file-backed parser reuses line buffers and extracts JSON fields from raw UTF-8 bytes; at two hourly files / 200k events it makes q1/q2 modest region throughput/RSS/tail wins and removes timed GC from region rows, but heap GC is only about `1.5-1.6%` of elapsed. |
| LogHub / LogPAI BGL | Real file-backed BGL system log | New real log matrix. At 1M real lines, heap q1/q2 spends `99-157 ms` in GC inside roughly `5.6 s`; region rows remove timed GC and several rows modestly improve throughput/RSS. Full-file q2 loads `4747963` lines and heap spends `595.599 ms` in GC inside `32.161 s`, while checked scoped page-token is faster and lower-RSS. Useful real-input modest-win/fixed-memory control, not the missing huge-GC flagship. |
| DSPBench Spike/Fraud Detection | Public DSPS benchmark source and bundled real sample files | `DSPBENCH_REGION_MATRIX.md` now includes local single-process Spike and Fraud rows. Spike is modest/control only. Fraud q2 is more interesting: at 1M, trusted Streaming is `763.819 ms` vs heap `801.790 ms`, with heap GC `69.686 ms`. Heap caps do not create a fixed-memory checked win at 1M; checked scoped page-token q2 cuts GC/RSS but loses elapsed, so Fraud is a trusted-runtime modest win and checked-overhead diagnostic, not final checked application evidence. |
| Wikimedia | Real/generated TSV/clickstream-style rows | Mostly heap or improved SafeZone wins with low median GC; parked as ceiling/regression control. |
| Linear Road | Official/generated position-report methodology | Useful latency/window methodology, but current rows are not GC-heavy enough for a Rift case study. |
| Yahoo-style ads | Local/generated ad-stream methodology | Some wins exist, but provenance is generated/local rather than official real input. |
| RIoTBench-style IoT | Local/generated IoT ETL/statistics methodology | Some q1 wins exist, but real/provenance-clean input remains open. |

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
record-oriented and can be processed as an event/page/window stream:

| Candidate | Input form | First query shape |
|---|---|---|
| GH Archive | hourly real GitHub events, JSON/NDJSON | file-backed byte-slice parse/project fields, repo/window counts, heap-capped tails, parser/string-scratch controls |
| LogHub / LogPAI system logs | real HDFS/BGL/Spark/Thunderbird/etc. log lines | BGL is wired and measured; parse log records, tokenize fields/templates, window/session/block counts |
| Larger/multiple Common Crawl WET/WAT shards | public WET/WAT archive records | page/token/link object materialization and domain/window counts |
| GDELT events | public event files | parse/project event fields and windowed country/topic counts |
| Public web/server/security logs | Apache/NASA-style logs or JSON security events | tokenize fields, filter/project, per-window counts |
| DSPBench local kernels | source benchmark workloads | choose kernels with clear epoch/window lifetimes and high object churn |
| MLKit/ReML source benchmarks | real prior-system benchmark programs | non-stream region+GC comparison by elapsed/RSS/GC count |

## 7. What Has Not Been Proven Yet

Rift still does not have a final checked result on a public, real-input,
GC-heavy stream workload that beats both `heap-immix` and
`safezone-improved-32k` by a clear case-study margin.

The nearest candidates are:

1. DSPBench local kernels: Spike/Fraud q0/q1/q2 are implemented; profile
   checked Fraud q2 before adding another kernel.
2. Real RIoTBench-style input, if provenance-clean traces are available.
3. More LogHub / LogPAI variants only if they materialize richer per-line
   objects than the current BGL line/token/window path.
4. Larger or multiple real Common Crawl WET/WAT shards.
5. GH Archive with heap-budgeted/file-backed/tail-latency runs as a modest-win
   control, not GC-heavy proof.
6. Another real NDJSON/log-event stream with heavier object churn.
7. Theodolite/RIoTBench-style local kernels only if input provenance
   and lifetime structure are clean.

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
