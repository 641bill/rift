# Rift Evaluation Summary Slides

Date: 2026-05-03
Last updated: 2026-05-06 23:24 CEST

Status: markdown slide deck outline. Use
`docs/PERFORMANCE_EVALUATION_REPORT.md` as the source report and this file as
the talk skeleton. Use `docs/BENCHMARK_CATALOG.md` for benchmark definitions
and evidence-class labels.

## Slide 1: One-Sentence Thesis

Rift is a checked region system for Scala Native that tries to move
epochal stream/data objects out of Immix and reclaim them in bulk, while using
static capture/lifetime/rooting rules to avoid Yak-style barriers, escape
tables, and blanket GC root registration.

## Slide 2: The Design Target

| Keep on heap | Put in regions |
|---|---|
| durable control metadata | page/batch/window records |
| unpredictable lifetime state | token/event/output scratch objects |
| global/static metadata | child-bucket object graphs |
| explicitly rooted heap values | epoch-local query intermediates |

The goal is the same logical program for heap and Rift; only allocation
placement and lifetime policy should differ.

## Slide 3: Canonical Memory Modes

| Name | Meaning |
|---|---|
| `gc-heap` | Scala Native Immix baseline. |
| `region-scoped-rooted` | SafeZone-family scoped regions with improved roots. |
| `region-scoped-rootless` | Unsafe lower-bound SafeZone no-root mode. |
| `region-hp-rootless` / `region-stream-rootless` | Trusted region backend potential. |
| `checked-region-stream` | Checked Rift API over Rift backend. |
| `checked-region-scoped` | Checked Rift API over SafeZone-family scoped backend. |
| `checked-page-token` | Operator-owned checked page/event/window append fast path. |

Raw labels remain aliases in scripts and source result packs.

Default final-selection runs now show safe/rooted and checked candidates.
Rootless/current SafeZone controls require an explicit control flag.

## Slide 4: Runtime Lesson

Old SafeZone was not just "regions are slow." Its root bookkeeping was the
cliff. Improved roots and page-size configuration make SafeZone a strong
baseline, and rootless SafeZone shows a lower bound for what allocator/pool
mechanics can do when roots are unnecessary.

## Slide 5: Static Safety Should Remove Runtime Work

| Static property | Runtime work we want absent |
|---|---|
| no region escape | no escape table, no promotion barrier |
| no heap-retains-region | no dynamic retention tracker |
| safe region-to-heap only through static/rooted metadata | no blanket page roots for eligible checked code |
| no outer-retains-inner | no close-time graph scan |
| no closure escape | no runtime closure tracker |
| diagnostics opt-in | no per-allocation global atomics |

## Slide 6: What We Actually Removed So Far

| Removed/avoided overhead | Status |
|---|---|
| Rift per-allocation byte-counter atomics | implemented; Common Crawl-like q1/q2 improved. |
| SafeZone per-page root removal cliff | implemented as improved roots mode. |
| AppendWindow per-entry close callback | implemented cursor close. |
| Page/token append per-record open checks/lookups | implemented in `StreamPageTokenAppendWindow`; generated Common Crawl-shaped q1/q2 gate passed. |
| Rootless SafeZone root registration | benchmark-only lower bound, not safety claim. |

Remaining generic fold/join/rank hot-path checks and rootless checked backend
require more static probes before removal.

## Slide 7: Strongest GC-Heavy Stream Detector

Generated Common Crawl WET-shaped q1/q2 is not real-input proof, but it is the
clearest memory-regime detector.

| Query | heap elapsed / GC | improved SafeZone 32K | checked page-token | checked scoped page-token |
|---|---:|---:|---:|---:|
| q1 tokenization | `5619.896 ms` / `1625.936 ms` | `4710.779 ms` | `4159.837 ms` | `3860.248 ms` |
| q2 domain window | `5429.530 ms` / `1643.346 ms` | `4577.498 ms` | `4175.633 ms` | `3895.711 ms` |

Interpretation: region placement removes GC, and an operator-owned checked
path can also remove enough redundant runtime overhead to win on this generated
stressor. This is not yet real-input proof.

## Slide 8: Why Allocation Still Matters

Region close is cheap, but ordinary object construction is not free.

| Cost | Still paid in region rows? |
|---|---|
| object header / RTTI setup | yes |
| zero/init and field stores | yes |
| constructor body | yes |
| checked allocation through `allocImpl` | yes, but clean retained-array rows no longer make it the primary bottleneck |
| bucket append / cursor traversal / aggregation | yes, application/query CPU |
| GC tracing of closed region objects | no |

The retained-region-array `ObjectAllocationLoweringMatrix` now isolates object
allocation from generic checked-container overhead. At 100k objects, checked
Rift is `1.576 ms` and checked SafeZone-backed is `1.395 ms` versus heap
`1.691 ms`. At 10M objects, heap reaches about `971 MB` RSS and spends
`105.807 ms` median timed GC; trusted Rift HP is `199.627 ms`, checked Rift is
`165.774 ms`, and checked SafeZone-backed allocation is `143.319 ms` with
about `404 MB` RSS. This says allocation/reclaim is already a win in the clean
shape; generic checked buffers/operators are the next overhead target.

The first generic-buffer decomposition confirms that target: at 10 x 100k
records, `rift-checked-array` is `18.574 ms`, fixed `ObjectBuffer` is
`25.788 ms`, growable `RegionBuffer` is `29.968 ms`, and pre-sized
`RegionBuffer` is `25.980 ms`. Static safety is already enough to make exact
region arrays fast; the remaining checked work is turning common operators
into array/chunk-owned fast paths without losing the safe boundary.

The first fixed-chunk append path is a useful negative control, not the next
fast path. At 1M records, `rift-checked-chunk-token` is `34.273 ms` versus
linked page-token `28.452 ms`; SafeZone-backed chunk-token is `33.108 ms`
versus page-token `27.214 ms`. Chunk allocation/control overhead outweighs the
saved per-record link write in this sequential append/drain workload.

GH Archive q1 shows the same evaluation issue at application scale: uncapped
heap wins median by growing to GB-scale RSS, while checked regions win the 1G
memory-budget diagnostic by removing GC pressure.

## Slide 9: Best Checked Stream Rows

| Query | heap | improved SafeZone | best checked | Interpretation |
|---|---:|---:|---:|---|
| NEXMark Q3 | `317.003 ms` | `304.246 ms` | `287.541 ms` | best checked methodology row, modest win. |
| NEXMark Q8 | `471.966 ms` | `465.297 ms` | `445.214 ms` | checked wins modestly. |
| NEXMark Q9 | `806.418 ms` | `756.289 ms` | `731.810 ms` | strong Beam-default checked row. |

NEXMark uses generated Beam-default methodology, not the Beam runner.

## Slide 10: Cheap Checked Operators

Focused 1M append/window rows:

| Mode | Median |
|---|---:|
| `heap-immix` | `37.046 ms` |
| `rift-checked-page-token` | `28.160 ms` |
| `rift-checked-safezone-page-token` | `26.866 ms` |

The generic SafeZone-backed cursor was a useful backend step. The page/token
operator is stronger: generated Common Crawl-shaped q1/q2 improves current
checked by about `16-23%` in the 2026-05-06 staged sweep.

`Page/token` means an operator-owned child-bucket append path: one
page/event/window owns many short-lived records, the operator caches the child
bucket/region, and static lifetime ownership justifies removing per-record
defensive checks.

First cheap-family focused rows now pass their initial gates with RSS:
Dataflow SELECT scoped page-token is `19.063 ms` versus heap `29.272 ms`.
ListOfLists checked builder is `6053.235 ms` versus heap `15820.172 ms` and
improved SafeZone `10133.449 ms`. Dataflow AGGREGATE checked is a near-tie
with improved SafeZone (`41.827 ms` vs `41.810 ms`) and should not be
presented as a generic `EpochFold` win.

The first multi-list `TransactionRegion` row is a partial checked win:
StreamFlex 1M-shape throughput scoped checked transaction is `40.512 ms`,
faster than heap `42.431 ms` and improved SafeZone `42.236 ms`, but latency
median is worse. The lesson is reusable and concrete:
multi-stage stream operators should share one child-region lifetime, but hot
list state must be operator-owned fields rather than generic indexed metadata.

## Slide 11: What Counts As A Win

| Outcome | Meaning |
|---|---|
| representative throughput win | large elapsed win with a reusable shape and correct outputs. |
| modest throughput win | faster, but margin/provenance is not enough for the final headline. |
| RSS win | materially lower resident memory, even with tied/slightly worse elapsed. |
| fixed-memory/tail win | heap wins uncapped by growing large, but regions win under a cap or reduce max-GC tails. |
| speed-gated | correct API, but CPU overhead too high for public performance claims. |
| ceiling/negative | no material throughput, RSS, GC, or latency benefit. |

Throughput is total completed work per unit time; lower batch elapsed means
higher throughput. Latency is per-event/request time, usually p50/p95/max or
deadline misses. They can move in different directions.

## Slide 12: What Is Gated Or Negative

| Negative result | Meaning |
|---|---|
| current Rift HP loses to improved SafeZone on linked/prior rows | learn from SafeZone internals. |
| TableRank/rank/fold fail 1M gates | do not use them in app claims yet. |
| real WET/WAT/Wikimedia/Linear Road mostly heap-fastest or median-GC-zero | current real inputs are not GC-heavy enough for representative claims, though WET/WAT page-token rows are modest real-input wins. |
| pipeline surrogate heap wins | CPU-bound workloads are not Rift targets. |

## Slide 13: Benchmark Ladder

Next realistic GC-heavy search:

1. larger/multiple real Common Crawl WET/WAT shards;
2. GH Archive file-backed and memory-budget NDJSON rows;
3. other real NDJSON/log-event streams such as GDELT or public web/server/security logs;
4. DSPBench local-kernel subset;
5. NEXMark Q3/Q8/Q9/Q11 as generated controls;
6. provenance-clean RIoTBench real input;
7. exact MLKit/ReML source benchmark reproduction as a non-stream typed-region axis.

The first real WAT shard now validates link-object placement and modestly
favors SafeZone-backed page-token, but heap still reports zero timed GC.
GH Archive is now a real memory-budget/tail-latency candidate: the 8-hour 1M
oracle row has heap winning uncapped median by growing to about `1.7 GB`, but
the same q1 shape under a `1G` heap cap makes checked SafeZone-backed
page-token faster than heap.
The file-backed q1/q2 rows include gzip/JSON parsing in timing and show
RSS/fixed-memory wins; both heap rows fail under a `1G` cap. Parser/string
allocation still causes GC in region rows too, so parser scratch is the next
technical question.

Every stream headline should now say whether the win is uncapped throughput,
fixed-memory, RSS, or tail-latency evidence.

## Slide 14: ReML / MLKit Lineage

The ReML paper is a separate comparison axis: higher-order/polymorphic
region+GC safety, not stream processing. We now have:

- paper-reported Figure 9 data transcribed;
- local Scala Native Tier 1 ports;
- fixed ReML-style erased-generic heap-retention probes;
- public MLKit source provenance in ignored cache.

Exact speed comparison is still open. The public MLKit repo contains many
Figure 9-style sources, and tags `v4.7.4`/`v4.7.5`/`v4.7.6` bracket the
paper-era ReML release. We still need local `mlkit`/`mlton` executables and
verified command mappings for `rg`, `rg-`, and `r`.

## Slide 15: Current Claim

Rift has credible trusted-runtime wins on epochal object-heavy streams and
early checked safety/operator evidence. It now has a checked generated-stressor
win, but it does not yet have a final checked real-input application win.

## Slide 16: Next Work

1. Keep allocation and generic checked-container overhead separated; optimize buffers/operators next.
2. Keep `StreamPageTokenAppendWindow` as the first cheap checked operator.
3. Add heap-size-controlled rows for GH Archive, Common Crawl-shaped, and NEXMark.
4. Test larger/multiple real WET/WAT, GH Archive file-backed, GDELT/logs, and DSPBench-style local kernels.
5. Promote only repeated winning shapes; keep TableRank/rank gated out.
6. Run exact MLKit/ReML artifact reproduction if toolchain/provenance is pinned.
7. Apply `docs/FINAL_COMPONENT_SELECTION.md`: public candidates only in the
   default story; rootless/loss rows only as explicit controls.

## Slide 15: ReML / MLKit Lineage Track

This is not a stream benchmark. It asks whether Rift's checked region model
also addresses the classic typed-region problem: higher-order and polymorphic
programs where region values can be hidden by type abstraction.

| Evidence | Status |
|---|---|
| ReML paper Figure 9 | transcribed as paper-reported, not rerun. |
| Exact MLKit/ReML artifact | open; needed for raw timing comparisons. |
| Scala Native Tier 1 ports | scaffolded for `fib37`, `tak`, `mandel`, `msort`, `msort-r`, `life`, `fft`, `ratio`. |
| Safety probes | erased-generic heap retention is now rejected in durable/static state; local polymorphic use remains legal. |

Claim boundary: compare relative region-vs-heap/RSS/GC effects and safety
burden until exact artifacts are rerun. The generic-retention fix is compiler
probe evidence, not a full mechanized proof.

## Slide 16: Prior-System Metric Rule

Compare each prior system on the axes it actually reported:

| System | Axes to preserve |
|---|---|
| Broom | runtime speedup, GC share, dataflow synchronization delays |
| Yak | normalized runtime, GC time, app time, epoch/promotion behavior |
| StreamFlex | throughput, latency tails, deadline misses |
| Stancu et al. | young-gen sensitivity, collections, annotation burden, region-freed memory |
| ReML/MLKit | real time, RSS, GC count |

Then show Rift's local standardized metrics separately: elapsed, GC time/count,
RSS, region op time, correctness, and annotation/API burden.
