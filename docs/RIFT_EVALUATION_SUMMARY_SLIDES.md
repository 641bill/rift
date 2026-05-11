# Rift Evaluation Summary Slides

Date: 2026-05-03
Last updated: 2026-05-11 15:44 CEST

Status: markdown slide deck outline. Use
`docs/PERFORMANCE_EVALUATION_REPORT.md` as the source report,
`docs/BENCHMARK_CATALOG.md` for benchmark definitions, and
`evidence/EVALUATION_CLASSIFIED_SUMMARY.md` for the classified result table.
Use `docs/FAIR_EVALUATION_PROTOCOL.md` for the evaluation contract,
`evidence/MEASUREMENT_OVERHEAD_PROTOCOL.md` for measurement levels, and
`evidence/OPERATOR_GATE_STATUS.md` when discussing why rank/top-k/median and
join operators remain gated.

Recommended talk order:

1. Problem and design target.
2. Comparison classes: natural heap, same-shape heap, summary-only topology,
   retained-object drop-anchor, best checked topology, unsafe/trusted lower
   bound.
3. Measurement levels: L1 final-clean headline versus L2 stats, L3
   diagnostics, and L4 external profiles.
4. Direct `RiftRegion.epoch { ... }` as the reusable checked topology for
   batch/epoch workloads.
5. Retained-object evidence as the fair memory-management comparison.
6. Real-input Yak LiveJournal and AskUbuntu as checked epoch rows.
7. Page-token stream evidence for page/window append workloads.
8. ReML/MLKit PLDI-style comparison as a non-stream typed-region axis.
9. Open work: remaining L1 final-clean gaps, real-input GC-heavy search, and gated
   rank/hash/median/join
   operators.

Representative numbers to keep on slides:

| Evidence class | Best current row | Interpretation |
|---|---|---|
| Retained-object memory management | Focused 1M retained: checked scoped `24.274 ms`, `0 ms` GC, `4.9 MB` RSS vs retained heap `36.233 ms`, `10.109 ms` GC, `21.3 MB` RSS. | Fair region-reclaim win: both sides retain ordinary objects until epoch close. |
| Retained generated/preloaded stressor | GH Archive-shaped retained q2 L1: checked scoped `3.44 s`, `16 MB` RSS vs retained heap `4.62 s`, `147 MB` RSS for 20 x 1M iterations; L2 checked scoped `186.868 ms` vs retained heap `257.377 ms`, `77.208 ms` GC. | Strong retained memory/RSS win, but not real-input proof. |
| Direct-summary lower bound | GH Archive-shaped q2 L1: heap direct-summary `1.36 s`; checked stream/scoped direct-summary `1.45/1.45 s`. DSPBench Fraud/Log q2 and LogHub q2/q3 now also have checked direct-summary counterparts within about `1-4%` of heap direct-summary, except LogHub q3's CPU-heavy row at about `2-3%`. | Symmetric topology lower bound: direct-summary is fast for heap and checked regions, but it is not a reclaim claim. |
| Real-input checked epoch | SNAP LiveJournal 50M: checked epoch scoped `2008.320 ms`, `0 ms` GC, `2.11 GB` RSS vs heap `2958.659 ms`, `400.484 ms` GC, `3.91 GB` RSS. | Strongest real-input prior-work-shaped row; local graph replay, not exact Yak/GraphChi. |
| Real-input text checked epoch | AskUbuntu `topwordreal` 20M x5: checked epoch scoped `7.16 s`, `174 MB` RSS vs heap `7.77 s`, `986 MB`; L2 checked `432.824 ms`, `0 ms` GC vs heap `511.485 ms`, `33.471 ms` GC. | First real text/top-word row; local Yak/Hadoop-shaped replay, not exact Yak/Hadoop. Reusable top-k is an RSS win but trails direct epoch and heap elapsed at 20M. |
| Reusable Dataflow epoch | SELECT/AGGREGATE/JOIN: checked epoch scoped `19.691/34.676/19.762 ms` vs heap `27.775/50.837/30.387 ms`. | Direct epoch covers the full Broom-style operator family. |
| StreamFlex/Stancu epoch | L1 StreamFlex throughput `0.58 s` vs heap `0.79 s`; L1 Stancu `0.57 s` vs heap `0.85 s`. | Direct epoch supersedes older TransactionRegion/EpochBuffer rows for shared batch lifetimes. |
| SPECjbb2005-workload port | L1 8 warehouses x20: checked epoch scoped `2.21 s` vs heap `2.64 s` and rooted scoped `2.48 s`; RSS about `8.0 MB` vs heap `12.4 MB`. | Clean-room Scala Native port strengthens the Stancu/SPECjbb transaction-lifetime story; not official SPECjbb2005. |
| Generated page/window stressor | Common Crawl-shaped q1/q2: checked scoped page-token `3707.214/3902.795 ms` vs heap `5577.965/5183.074 ms`. | Strong generated stream-object pressure win; RSS caveat; not real-input proof. |
| Modest real-input page/window | GH Archive byte-slice q1/q2 L1 checked scoped page-token `12.89/12.87 s`, `101/102 MB` RSS vs heap `13.17/13.18 s`, `265/244 MB`; LogHub HDFS q2 L1 checked scoped page-token `25.56 s`, `79 MB` RSS vs heap `25.60 s`, `409 MB` RSS; DSPBench Log q2 L1 checked `8.79 s`, `47.6 MB` vs heap `8.89 s`, `308 MB`. | Real-input page/window wins are mostly RSS/tail/modest-throughput because parser/query CPU dominates and heap GC is small. |
| Real-preloaded retained top-k | L1 LogHub HDFS 1M x20 after hot-path pass: reusable `EpochTopKByKey` checked scoped `4.88 s`, `28 MB` RSS vs retained heap `5.52 s`, `205 MB` RSS; 5M x5 scale-up is `18.26 s`, `92 MB` RSS vs retained heap `19.04 s`, `504 MB`. | First retained top-k API gate has L1 real-input confirmation and strong RSS win; report-facing API overhead is about `1.7%` at 1M x20 and the 5M row keeps a modest throughput/RSS win. |

Slide-level rule: summary-only/direct-aggregate rows are topology/operator
lower bounds. Retained heap versus retained checked epoch is the fair
memory-management story. Dirty checkpoints, old SafeZone root-mode-0 rows,
legacy parser rows, and gated DEBS/TableRank/rank rows are not slide headline
evidence unless rerun under the current fair-evaluation protocol.

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

## Slide 3: Evaluation And Measurement Contract

| Topic | Rule |
|---|---|
| headline system evidence | must use reusable checked framework APIs, not benchmark-local manual arrays |
| memory-management claim | must compare retained heap/drop-anchor against retained checked regions |
| topology lower bound | summary-only/direct-aggregate rows are useful, but not pure GC/reclaim wins |
| final timing | L1 final-clean uses external `/usr/bin/time -l` only |
| interpretation | L2 stats provide GC/RSS/region counters; L3/L4 diagnostics and profiles explain bottlenecks |

Profiler elapsed from `samply`, `sample`, or `perf` is diagnostic, not a
headline median.

## Slide 4: Canonical Memory Modes

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

## Slide 5: Runtime Lesson

Old SafeZone was not just "regions are slow." Its root bookkeeping was the
cliff. Improved roots and page-size configuration make SafeZone a strong
baseline, and rootless SafeZone shows a lower bound for what allocator/pool
mechanics can do when roots are unnecessary.

## Slide 6: Static Safety Should Remove Runtime Work

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
| Page/token append per-record open checks/lookups plus generic leftover-drain close work | implemented in `StreamPageTokenAppendWindow`; 2026-05-07 batch-close/current-bucket fast path strengthened focused and generated Common Crawl-shaped rows. |
| Page/token no-drain close | implemented as an operator-owned option; cost matrix says it is safe but not the main bottleneck. |
| Rootless SafeZone root registration | benchmark-only lower bound, not safety claim. |

Remaining generic fold/join/rank hot-path checks and rootless checked backend
require more static probes before removal.

## Slide 7: Strongest GC-Heavy Stream Detector

Generated Common Crawl WET-shaped q1/q2 is not real-input proof, but it is the
clearest memory-regime detector.

| Query | heap elapsed / GC | improved SafeZone 32K | checked page-token | checked scoped page-token |
|---|---:|---:|---:|---:|
| q1 tokenization | `5577.965 ms` / `1741.640 ms` | `4595.446 ms` | `3933.900 ms` | `3707.214 ms` |
| q2 domain window | `5183.074 ms` / `1565.074 ms` | `4410.391 ms` | `4040.310 ms` | `3902.795 ms` |

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

GH Archive shows both the evaluation issue and the next reusable optimization:
the legacy file-backed parser spent most time in `BufferedReader`/UTF-8/
`StringBuilder` work, while the new byte-slice parser-scratch path removes
that allocation cliff. With two real hourly files / 200k events, byte-slice q1
is heap `3806.120 ms` versus checked scoped page-token `3629.193 ms`; byte-
slice q2 is heap `3756.950 ms` versus checked scoped page-token `3626.107 ms`.
Both checked rows cut RSS from about `290 MB` to `211 MB` and report zero timed
GC. This is a modest real-input throughput/RSS/tail win, not a GC-heavy case
study: heap GC is only about `58-62 ms` inside roughly `3.8 s` elapsed.

LogHub BGL is now the next real log control. At 1M real lines, q1 heap is
`5568.252 ms` with `99.271 ms` GC and trusted Streaming is `5491.033 ms`; q2
heap is `5646.824 ms` with `157.198 ms` GC and improved SafeZone-32k is
`5509.481 ms`. Full-file q2 loads all `4747963` BGL lines: heap
`32161.391 ms`, `595.599 ms` GC, RSS `576 MB`; checked scoped page-token
`31165.087 ms`, zero timed GC, RSS `491 MB`. This strengthens the real-input
modest-win story, but still not the missing huge-GC case.

The richer BGL q3 template/session query materializes line, template-token, and
session-candidate records. At 1M real lines, heap is `8683.558 ms` with
`84.166 ms` median GC and RSS `290 MB`; trusted Streaming is `8615.627 ms` with
RSS `237 MB`; checked scoped page-token is `8722.008 ms` with RSS `237 MB`.
This is an RSS/tail control and a correctness validation for the richer log
shape, not a throughput flagship.

DSPBench Spike Detection is now measured as the first DSPS local-kernel row.
At 1M real sensor events replayed from `79999` usable lines, checked scoped
page-token q1 is `1163.045 ms` vs heap `1187.525 ms`; trusted Streaming q2 is
`1258.164 ms` vs heap `1271.677 ms`. Heap GC is real but small
(`10.880-32.793 ms`), so Spike is a real-input modest/control row. Fraud
Detection is now measured too. The first 1M q2 matrix made trusted Streaming
the best row (`763.819 ms` vs heap `801.790 ms`). The dirty 2026-05-07
page-token batch-close fast-path direction check made checked scoped
page-token fastest: `818.574 ms` versus heap `862.834 ms`, improved SafeZone
`873.859 ms`, and trusted Streaming `834.447 ms`, with RSS cut from about
`358 MB` to `279 MB`. This was useful direction evidence, not final headline
data.

The first committed-code q2 rerun was conservative: trusted Streaming was
fastest at `788.040 ms`; checked scoped page-token was `810.770 ms`; heap was
`820.945 ms`. After owned-cursor link-clearing and open-allocation removal, q2
is now: trusted Streaming `778.975 ms`, checked scoped page-token `797.782 ms`,
and heap `806.697 ms`. Checked scoped has a modest elapsed/RSS win over heap,
but trusted Streaming remains the lower-bound row.

DSPBench Log Processing adds a second DSPBench real-input control using the
bundled `http-server.log` common-log file. At 1M events, q2 is the useful row:
checked scoped page-token is `1733.654 ms`, trusted Streaming is `1737.469 ms`,
and heap is `1750.291 ms`; checked scoped cuts max GC from `88.210 ms` to
`18.584 ms`. This is modest real-input throughput/GC-tail evidence, not the
flagship: heap GC is only about `2.6%` of elapsed and region RSS is higher.

Latest non-headline attribution changes the next tuning target. In DSPBench
Fraud q2, estimated bucket open/switch is below `1 ms`; trusted Streaming
append is `131.493 ms`, checked scoped append is `144.353 ms`, and heap append
is `186.048 ms`. Generated Common Crawl-shaped q1/q2 shows the same pattern at
larger scale: bucket open is only about `3-10 ms`, while allocation+append is
about `3.18-3.52 s` and close traversal is about `0.76-0.81 s` for `137M`
records. The remaining checked work is cursor/node traversal and query CPU,
not bucket opening.

## Slide 9: Best Checked Stream Rows

| Query | heap | improved SafeZone | best checked | Interpretation |
|---|---:|---:|---:|---|
| NEXMark Q3 L1 x20 | `6.18 s` | `6.38 s` | `5.86 s` | checked generated-methodology win. |
| NEXMark Q8 L1 x20 | `9.54 s` | `10.13 s` | `9.21 s` | checked modest elapsed/RSS win. |
| NEXMark Q9 L1 x20 | `16.27 s` | `18.10 s` | `15.03 s` | strongest selected NEXMark L1 row. |
| NEXMark Q11 L1 x20 | `4.47 s` | `5.11 s` | `4.36 s` | checked modest elapsed/RSS win. |

NEXMark uses generated Beam-default methodology, not the Beam runner. These
are L1 final-clean total-process rows; L2 rows remain the source for GC
interpretation.

## Slide 10: Cheap Checked Operators

Focused 1M append/window rows:

| Mode | Median |
|---|---:|
| `heap-immix` | `36.920 ms` |
| `rift-checked-page-token` | `29.319 ms` |
| `rift-checked-safezone-page-token` | `27.549 ms` |

The generic SafeZone-backed cursor was a useful backend step. The page/token
operator is stronger: generated Common Crawl-shaped q1/q2 improves current
checked by about `16-23%` in the 2026-05-06 staged sweep.
The 2026-05-07 fast-path regression keeps linked page-token ahead of
chunk-token. The post-fast-path selected 1M sweep makes checked scoped
page-token fastest on generated Common Crawl-shaped q1 (`3840.668 ms`) and q2
(`3839.158 ms`), and it keeps Dataflow SELECT scoped page-token fastest at
`18.572 ms`.

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

The StreamFlex follow-up strengthens that lesson. `TransactionRegion` was a
partial checked win, but direct checked epoch is better when all temporary
stage objects share one batch lifetime. In L1 final-clean timing, 20 x 200k
throughput is checked scoped direct epoch `0.58 s` versus heap `0.79 s` and
improved SafeZone `0.77 s`. The latency row is also favorable: checked scoped
direct epoch is `0.17 s` versus heap `0.18 s`, and deadline misses drop from
heap `4` to checked `0`. The user-facing topology should be `epoch { ... }`
first; specialized operators are for shapes direct epoch cannot express
cleanly.

Stancu-style transaction batches now show the same pattern. In L1 final-clean
timing, 20 x 200k transactions are checked scoped direct epoch `0.57 s` versus
heap `0.85 s` and improved SafeZone `0.71 s`. This is the clearest local
transaction-boundary checked win so far.

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
| real WET/WAT/Wikimedia/Linear Road/RIoTBench-MHEALTH mostly heap-fastest or median-GC-zero; GH Archive/LogHub/DSPBench are modest wins | current real inputs are not GC-heavy enough for representative claims, though HDFS q2 and other page-token/log rows are useful controls. |
| pipeline surrogate heap wins | CPU-bound workloads are not Rift targets. |

## Slide 13: Benchmark Ladder

Next realistic GC-heavy search:

1. Theodolite UC2/UC4-style industrial energy over a real power-meter trace;
2. larger provenance-clean machine/security traces such as LogHub Spark/Windows, GDELT, or public SOC/NDJSON logs;
3. larger/multiple real Common Crawl WET/WAT shards;
4. GH Archive, LogHub, DSPBench, and RIoTBench/MHEALTH as modest-win or ceiling controls;
5. NEXMark Q3/Q8/Q9/Q11 as generated controls;
6. exact MLKit/ReML source benchmark reproduction as a non-stream typed-region axis.

The first real WAT shard now validates link-object placement and modestly
favors SafeZone-backed page-token, but heap still reports zero timed GC.
RIoTBench/MHEALTH fixes one IoT provenance gap but is also zero-GC at 1M.
Theodolite source is cloned, but its official load generator is simulated
smart-meter input; use it as methodology unless paired with real energy data.
GH Archive is now the strongest real-input modest-win candidate, but not the
missing GC-heavy proof. The 8-hour preloaded
oracle row has heap winning uncapped median by growing to about `1.7 GB`, but
the same q1 shape under a `1G` heap cap makes checked SafeZone-backed
page-token faster than heap. The legacy file-backed q1/q2 rows showed RSS/
fixed-memory wins but were dominated by string parser allocation. The new
byte-slice file-backed rows keep gzip/JSON parsing in timing while reusing
parser scratch, and now show modest checked throughput wins plus zero timed GC
in region rows. LogHub BGL adds a real multi-million-line system-log control,
including q3 template/session mining, but full-file q2 heap GC is still under
2% of elapsed and q3 heap GC is under 1%. Heap GC remains a small share of
elapsed in current real inputs, so next benchmark work still needs a real-input
workload with materially higher GC pressure.

The 2-hour file-backed GH Archive rows strengthen that interpretation:
heap uses about `2.43 GB` RSS, while region rows use about `0.72-0.93 GB`.
Trusted Streaming is modestly faster on q1/q2, checked scoped page-token is
near-tied, and a sampled q1 profile shows the remaining bottleneck is
`BufferedReader`/UTF-8/StringBuilder/field parsing/hashing/gzip rather than
region close.

## Slide 14: ReML / MLKit Axis

This is not stream evidence; it tests the MLKit/ReML lineage: higher-order,
polymorphic, region+GC safety.

| Workload | Heap | Best checked | Meaning |
|---|---:|---:|---|
| `msort` | `124.983 ms`, RSS `21.4 MB`, GC `27.180 ms` | checked stream `104.358 ms`, RSS `10.4 MB`, GC `6.063 ms` | local linked-allocation win. |
| `msort-r` | `126.163 ms`, RSS `39.2 MB`, GC `27.280 ms` | checked stream `104.929 ms`, RSS `10.4 MB`, GC `6.005 ms` | local reverse-list allocation win. |
| `ratio` | `51.302 ms`, RSS `44.0 MB`, GC `3.191 ms` | checked scoped `48.929 ms`, RSS `16.0 MB`, GC `0` | modest elapsed, strong RSS/GC win. |

Exact ReML/MLKit reproduction is still open: public MLKit sources and likely
paper-era tags are found, but host `mlkit`/`mlton` are missing and Docker is
not running. Until exact artifacts run locally, compare ratios and safety
properties, not raw cross-language wall-clock.

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
| Exact MLKit/ReML artifact | gated/low-priority; resume only if raw same-machine timing becomes necessary. |
| Scala Native Tier 1 ports | scaffolded for `fib37`, `tak`, `mandel`, `msort`, `msort-r`, `life`, `fft`, `ratio`. |
| Safety probes | erased-generic heap retention is now rejected in durable/static state; local polymorphic use remains legal. |

Claim boundary: compare relative region-vs-heap/RSS/GC effects and safety
burden. Do not spend thesis time on exact artifact reruns unless raw
same-machine ReML timing becomes necessary. The generic-retention fix is
compiler probe evidence, not a full mechanized proof.

## Slide 16: Prior-Work Memory-Management Lesson

The prior systems are not primarily operator-library stories. They are lifetime
visibility stories.

| System | What becomes visible | Why it helps |
|---|---|---|
| Broom | dataflow/operator lifetime | short-lived fate-sharing data does not need repeated heap tracing |
| Yak | data-space epochs separate from durable control space | data objects are reclaimed by epoch; control objects remain under GC |
| StreamFlex | stream/filter/period scopes | fewer GC-induced tail pauses and deadline misses |
| Stancu et al. | transaction/phase scopes | transaction-local allocation can be region-freed |
| ReML/MLKit | inferred lexical regions with GC safety | tracing GC work is reduced while preserving polymorphic safety |

Rift's central claim should be framed the same way: checked capture/separation
rules make epoch/page/window/transaction lifetimes visible enough that the
runtime can avoid escape tables, promotion barriers, close-time scans, and
unnecessary tracing of temporary data.

## Slide 17: Design Ideas To Borrow Carefully

| Idea | Use in Rift |
|---|---|
| active / closed regions | internal probes now cover direct epoch, page-token, count-by-key, map/filter, epoch buffer, and stale public page-token regions; future public typestate depends on measured payoff |
| immutable/static metadata | open-allocation compiler probes accept stable static metadata in direct epoch and operator-owned page/epoch-buffer paths; root-free backend claims still need proof/evidence |
| bridge/root handles | existing `HeapRoot` is the v1 bridge handle and is now covered on direct epoch and operator-owned page/epoch-buffer paths |
| control path / data path split | report what stays on heap and what moves to regions |
| reference capabilities | future way to name mutable, read-only, transferable, and region-scoped refs |

Rule: add a capability to the user-facing API only if it removes measured
runtime work or makes the safety proof simpler. Do not add type vocabulary just
because another paper has it.

## Slide 18: Prior-System Metric Rule

Compare each prior system on the axes it actually reported:

| System | Axes to preserve |
|---|---|
| Broom | runtime speedup, GC share, dataflow synchronization delays |
| Yak | normalized runtime, GC time, app time, epoch/promotion behavior |
| StreamFlex | throughput, latency tails, deadline misses |
| Stancu et al. | young-gen sensitivity, collections, annotation burden, region-freed memory |
| ReML/MLKit | real time, RSS, GC count |

Then show Rift's local standardized metrics separately: elapsed, GC time/count,
RSS, region op time, correctness, and annotation/API burden. For latency rows,
also show throughput, p50, p95, max, deadline misses, GC max, and runs-with-GC.
