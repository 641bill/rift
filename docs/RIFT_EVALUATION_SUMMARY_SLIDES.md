# Rift Evaluation Summary Slides

Date: 2026-05-03
Last updated: 2026-05-06 00:55 CEST

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

| Query | heap elapsed / GC | best trusted Rift | improved SafeZone 32K | best checked page-token |
|---|---:|---:|---:|---:|
| q1 tokenization | `5350.531 ms` / `1517.640 ms` | HPZone `4265.969 ms` | `4578.914 ms` | SafeZone-backed `3696.284 ms` |
| q2 domain window | `5183.656 ms` / `1526.751 ms` | Streaming `4109.290 ms` | `4364.704 ms` | SafeZone-backed `3732.171 ms` |

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
| NEXMark Q3 | `287.568 ms` | `291.839 ms` | `282.629 ms` | best checked methodology row, modest win. |
| NEXMark Q8 | `452.128 ms` | `442.092 ms` | `432.391 ms` | checked wins modestly. |
| NEXMark Q9 | `779.032 ms` | `742.398 ms` | `708.391 ms` | strongest Beam-default checked row in this sweep. |

NEXMark uses generated Beam-default methodology, not the Beam runner.

## Slide 10: Cheap Checked Operators

Focused 1M append/window rows:

| Mode | Median |
|---|---:|
| `heap-immix` | `36.944 ms` |
| `rift-checked-rift` current | `32.226 ms` |
| `rift-checked-page-token` | `27.886 ms` |
| `rift-checked-safezone-page-token` | `26.883 ms` |

The generic SafeZone-backed cursor was a useful backend step. The page/token
operator is stronger: generated Common Crawl-shaped q1/q2 improves current
checked by about `16-23%` in the 2026-05-06 staged sweep.

`Page/token` means an operator-owned child-bucket append path: one
page/event/window owns many short-lived records, the operator caches the child
bucket/region, and static lifetime ownership justifies removing per-record
defensive checks.

First cheap-family focused rows now pass their initial gates with RSS:
Dataflow SELECT scoped page-token is `17.980 ms` / `30.4 MB` RSS versus heap
`27.932 ms` / `39.3 MB`; ListOfLists checked builder is `9228.561 ms` /
`364.2 MB` versus heap `14822.115 ms` / `575.9 MB`. Dataflow AGGREGATE
epoch-fold is `38.399 ms` versus heap `61.585 ms`, but it raises RSS and still
uses the exact-array checked aggregate path.

The first multi-list `TransactionRegion` row is a partial checked win:
StreamFlex 1M-shape throughput scoped checked transaction is `39.019 ms`,
faster than heap `42.860 ms` and improved SafeZone `41.327 ms`, while trusted
Rift HP/Streaming remain best at about `36.4 ms`. The lesson is reusable and concrete:
multi-stage stream operators should share one child-region lifetime, but hot
list state must be operator-owned fields rather than generic indexed metadata.

## Slide 11: What Is A Loss

| Negative result | Meaning |
|---|---|
| current Rift HP loses to improved SafeZone on linked/prior rows | learn from SafeZone internals. |
| TableRank/rank/fold fail 1M gates | do not use them in app claims yet. |
| real WET/WAT/Wikimedia/Linear Road mostly heap-fastest or median-GC-zero | current real inputs are not GC-heavy enough. |
| pipeline surrogate heap wins | CPU-bound workloads are not Rift targets. |

## Slide 12: Benchmark Ladder

Next realistic GC-heavy search:

1. larger/multiple real Common Crawl WET/WAT shards;
2. GH Archive file-backed and memory-budget NDJSON rows;
3. DSPBench local-kernel subset;
4. NEXMark Q3/Q8/Q9/Q11 as generated controls;
5. provenance-clean RIoTBench real input.

The first real WAT shard now validates link-object placement and modestly
favors SafeZone-backed page-token, but heap still reports zero timed GC.
GH Archive is now a real memory-budget/tail-latency candidate: the 8-hour 1M
oracle row has heap winning uncapped median by growing to about `1.7 GB`, but
the same q1 shape under a `1G` heap cap makes checked SafeZone-backed
page-token faster than heap.

Every stream headline should now say whether the win is uncapped throughput,
fixed-memory, RSS, or tail-latency evidence.

## Slide 13: Current Claim

Rift has credible trusted-runtime wins on epochal object-heavy streams and
early checked safety/operator evidence. It now has a checked generated-stressor
win, but it does not yet have a final checked real-input application win.

## Slide 14: Next Work

1. Keep allocation and generic checked-container overhead separated; optimize buffers/operators next.
2. Keep `StreamPageTokenAppendWindow` as the first cheap checked operator.
3. Add heap-size-controlled rows for GH Archive, Common Crawl-shaped, and NEXMark.
4. Test larger/multiple real WET/WAT, NDJSON/logs, and DSPBench-style local kernels.
5. Promote only repeated winning shapes; keep TableRank/rank gated out.
