# Rift Project And Performance Evaluation Report

Date: 2026-05-03
Last updated: 2026-05-15 22:16 CEST

Status: presentation-ready working report. This document is the single
high-level artifact to read before presenting or planning the next engineering
step. It summarizes the design, implementation status, benchmark evidence,
runtime-overhead story, wins, losses, and open work. Individual evidence files
remain the source of detailed command provenance.

Latest clean final-selection headline sweep:
`evidence/FINAL_SELECTION_HEADLINE_2026_05_06.md`.

Latest classified evidence summary:
`evidence/EVALUATION_CLASSIFIED_SUMMARY.md`. This is the first table to use
when deciding whether a row is topology evidence, retained-object
memory-management evidence, a best checked topology result, a real-input modest
win, or a ceiling/control row. It now also contains the explicit
“Legacy / Rerun Required” audit for dirty, old-SafeZone, L2-only,
benchmark-local, and gated-operator rows.

Latest fair-evaluation contract:
`docs/FAIR_EVALUATION_PROTOCOL.md`. This is now the reviewer-facing rulebook:
headline rows must use reusable checked framework APIs or be clearly labeled as
controls; memory-management claims require retained-object heap controls; and
manual summary/count-array rows remain topology/operator lower bounds.

Latest prior-work interpretation:
`docs/PRIOR_WORK_MEMORY_MANAGEMENT_INTERPRETATION.md`. This is the zoomed-out
principle layer for Broom, Yak, StreamFlex, Stancu et al., and ReML/MLKit:
their core performance argument is exposing a lifetime boundary so temporary
objects are not repeatedly traced by GC. Operators are evidence mechanisms for
those boundaries, not the root contribution by themselves.

Latest GC-heavy benchmark investigation:
`evidence/GC_HEAVY_BENCHMARK_INVESTIGATION.md`. The key update is that true
streaming input does not by itself imply GC pressure. Many real stream rows are
parser/hash/query dominated because production-style stream code reads bytes,
updates compact state, and discards records quickly. GC-heavy cases in prior
work and practitioner reports cluster around retained ordinary objects:
Broom-like joins/aggregates and per-timestamp dictionaries, Yak graph/text
epochs, StreamFlex event-correlation/transaction/IDS latency workloads,
Spark/Flink high-cardinality groupBy/join/top-k/session state, and
Stancu-style transaction batches. The next benchmark-search work should
therefore target retained-object workloads first, not just larger line counts.

Latest visual report update:
`docs/report.html` now includes a Rift topology atlas rather than copies of
prior-work figures. It shows the actual topologies used in the evaluation:
natural heap, direct epoch, retained epoch/drop-anchor, page/window token,
summary-only lower bound, and same-API backend choices. It also adds a table
separating what Rift enforces today from design vocabulary borrowed from prior
work.

Latest profile-guided backend cleanup:
child `450465743` caches Rift allocation-stats mode per opened region. The
post-change profiles no longer sample `scalanative_rift_alloc_stats_enabled`;
diagnostic counters still work with `RIFT_ALLOC_STATS=1`. The focused
allocation row is mixed (`71.702 ms` versus the earlier object-fast
`69.912 ms`), so this is reported as a cleanup/modest app improvement rather
than a new allocation headline. Representative gates move slightly:
page-token checked Rift `25.007 -> 24.618 ms`, StreamFlexDesign checked stream
`22.81 -> 22.55 s`, and generated Common Crawl-shaped q2 checked Rift
`11.49 -> 11.39 s`.

Latest allocation-body cleanup:
child `126e2950b` caches current-slab zeroed state on the Rift region so object
allocation no longer reloads the current slab's flags before the memset
decision. This keeps the same zeroing semantics and is now the latest accepted
allocation-body win: focused 5M checked Rift allocation is `68.998 ms`, focused
page-token checked Rift is `23.930 ms`, StreamFlexDesign checked stream is
`22.31 s`, and generated Common Crawl-shaped q2 checked Rift is `11.17 s`.

Latest remaining generic allocation-path audit:
child `3ee2fc173` promotes GH Archive `rift-checked-page-token` to the
backend-known Rift open-handle allocation path and keeps
`rift-checked-page-token-legacy` as the old generic allocation control. The
generated/preloaded 1M transfer gate improves q1 `316.947 -> 299.512 ms` and
q2 `317.997 -> 298.186 ms`, with matching checksums, region object counts, and
open/close counts. This is page/window allocation-lowering transfer evidence,
not a new real-input headline row; the real GH Archive streaming/file-backed
rows remain parser/source/query dominated.
The same audit now covers LogHub top-template retained stream:
`checked-epoch-retained-no-traverse` uses the handle-backed epoch path and the
old generic path is `checked-epoch-retained-no-traverse-legacy`.
Generated/preloaded 1M improves `291.519 -> 269.309 ms`; a real HDFS
streaming-file 100k sanity row is neutral (`273.834 -> 275.054 ms`). This
confirms the low-level optimization transfers to another retained-object shape,
but also reinforces that small real streaming rows are dominated by source and
query CPU. The report-facing LogHub result remains the scoped/reusable
`EpochTopKByKey` evidence.

Latest zeroing attribution probe:
`evidence/OBJECT_ALLOCATION_LOWERING_MATRIX.md` now records diagnostic counters
for managed object allocations that actually call `memset` versus allocations
that skip zeroing on fresh zeroed slabs. These counters are L2-only and remain
off in `RIFT_FINAL_CLEAN=1`. At 5M handle-backed checked Rift allocations, the
row is `70.197 ms`; `4,198,392` objects (`134,348,544` bytes) are zeroed and
`801,608` objects (`25,651,456` bytes) skip zeroing. This confirms
initialization/zeroing is a real remaining allocation-body cost, but it is not
a no-zero optimization or safety claim.

Latest unsafe no-zero lower-bound:
`ObjectAllocationLoweringMatrix` now includes
`rift-checked-rift-open-handle-nozero-unsafe`, which writes the object
RTTI/header word and skips object-body zeroing. This row is explicitly unsafe
lower-bound evidence, not a checked/default optimization. It measures the
ceiling for a future compiler-proven no-zero lowering: at 5M objects, normal
handle-backed checked Rift is `71.320 ms` while unsafe no-zero is `65.196 ms`;
at 10M, normal is `155.947 ms` while unsafe no-zero is `142.769 ms`. Checksums
match and RSS is unchanged in this fully initialized benchmark shape. The
result makes definite-initialization proof the next serious zeroing target:
final record-like class, all fields assigned before escape, no virtual
call/`this` escape during construction, superclass fields handled, and arrays
excluded.

Latest proof-gated no-zero lowering:
normal `RiftOpenStreamingHandle` allocation now calls the no-zero allocator
only when the lowerer proves the local allocation is a definitely initialized
primitive-field record: concrete/non-module/no-subclass class, primitive
instance fields, and every field stored before the object is otherwise used,
before control-flow exit, and before any non-pure operation. If this proof
fails, the existing zeroing allocation path remains in place. The focused 5M
`ObjectAllocationLoweringMatrix` row is now `65.528 ms` with `0` zeroed
objects and `5,000,000` zero-skipped objects, essentially matching the unsafe
lower-bound row `65.277 ms`; the 10M row is `139.832 ms` with all
`10,000,000` objects zero-skipped. This is the first safe no-zero result for a
narrow record-like shape. A focused page-token sanity gate remains positive:
promoted `rift-checked-page-token` is `24.975 ms`, legacy checked page-token is
`26.495 ms`, and heap is `35.918 ms` at 1M, with matching checksum and lower
RSS than heap. Two application transfer gates are now recorded. Dataflow L2 at
10 epochs x 100k documents keeps the optimized checked stream row ahead of
legacy on SELECT/AGGREGATE/JOIN (`18.141/33.574/17.669 ms` versus
`22.523/36.711/20.202 ms`) while removing heap's `6.630-11.195 ms` median
timed GC. StreamFlexDesign L1 at 20M events x3 reports heap `29.04 s`, legacy
checked stream `22.19 s`, optimized checked stream `19.91 s`, and checked
scoped `23.57 s`, all with matching checksum and no material RSS regression;
the matching pressure-latency L2 row cuts heap's `49` deadline misses to
`0-1` for checked region rows. The follow-up proof slice now includes
definitely initialized reference-field records. Focused 5M linked reference
records put normal checked open-handle allocation at the unsafe no-zero
ceiling (`66.249 ms` versus `66.177 ms`), with all `5,000,001` checked objects
zero-skipped and matching checksum; the primitive-shape regression row remains
positive at `63.303 ms`. StreamFlexDesign linked-object transfer stays
positive versus heap and legacy but does not show a fresh application win,
which means remaining StreamFlex-style work is now mostly query/traversal/
capsule/allocation-body cost rather than reference-field zeroing alone. The
selected page/window and real-streaming transfer gates keep the optimized
defaults stable: generated Common Crawl-shaped q1/q2 `rift-checked-page-token`
is `3590.874/3589.017 ms` versus legacy `3938.596/3961.363 ms` and heap
`5501.961/5286.428 ms`, cutting about `1.58-1.59 s` of timed heap GC but not
RSS; Theodolite real streaming q2 `checked-epoch-stream` is `952.664 ms`
versus heap `988.976 ms` and legacy `963.018 ms`, removing heap's `19.292 ms`
median timed GC. These are L2 interpretation/transfer rows, not new L1
headline rows.

Latest reusable-slab zeroing experiment:
`RIFT_ZERO_REUSED_SLABS=1` is a gated runtime policy that bulk-zeros dead
non-huge slabs at region close/reset before caching them for reuse. It keeps
Scala object zero-initialization semantics, but moves zeroing out of the
allocation hot path. Focused handle-backed allocation gates improve from
`68.692 ms` to `65.228 ms` at 5M objects and from `144.067 ms` to `138.078 ms`
at 10M objects, with matching checksums and essentially unchanged RSS. Region
op time rises because close/reset now performs the bulk zero. This is
promising but remains experimental. First application gates are positive:
StreamFlexDesign throughput 20M x3 improves `19.51 s -> 18.91 s`, and
generated Common Crawl-shaped q2 1M x3 improves `10.00 s -> 9.22 s`, both with
matching checksum/output and unchanged RSS. L2 confirms this is a transfer of
work, not free: StreamFlexDesign region op time rises `23.563 -> 254.858 ms`,
and Common Crawl q2 region op time rises `9.640 -> 68.771 ms`. The first real
streaming-input gate, Theodolite real power q2, is throughput-positive
(`3.94 s -> 3.60 s`) but RSS-negative (`15,908,864 -> 24,870,912` bytes).
Therefore this remains a workload-selective experimental policy, not a default
runtime setting.
A high-water prefix-zeroing follow-up was rejected: it reduced neither the
focused allocation elapsed nor region-op cost enough to justify the metadata
bookkeeping. The transition-only version still ran `69.619 ms` enabled at 5M,
worse than the accepted full-slab policy's `65.228 ms`.
A TLS/local-only zeroing follow-up was also rejected: it avoided global-pool
zeroing but kept almost the same object-zeroing shape as default and ran
`72.339 ms` at 5M, versus `71.834 ms` default and `68.614 ms` full bulk-zero.
The useful skip-zero benefit in the focused allocator row comes mostly from
global-pool reuse, so local-only zeroing is too narrow.
A static global-pool-cap follow-up was rejected too: shrinking the cap made the
focused allocator row slower (`68.124 ms` at the default cap versus
`78.603 ms` at cap zero) and did not materially reduce Theodolite q2 RSS
(`78.5 MB` versus `78.4 MB`). The next serious zeroing target is therefore
compiler-proven no-zero or a much more precise page-release design, not another
cache-size knob.

Latest throughput/RSS reuse-policy update:
the runtime now has a canonical `RIFT_REGION_REUSE_POLICY` knob. Supported
values are `default`, `bulk-zero-retained` (also the legacy
`RIFT_ZERO_REUSED_SLABS=1` alias), `cache-small`, `cache-large`, and
`prezero-large`. Default behavior remains memory-conservative. `cache-small`
and `cache-large` retain bounded reusable regular-slab pools without eager
bulk zeroing; `prezero-large` retains the larger pool and prezeros reusable
slabs at close/reset. Huge slabs, explicit close semantics, and safety checks
are unchanged. Focused `ObjectAllocationLoweringMatrix` gates show
`cache-large` as the best allocation-pressure policy so far: at 10M primitive
handle-backed checked allocations, elapsed improves `149.609 -> 130.250 ms`
and region-op time drops `17.445 -> 0.894 ms`, with matching checksum and
similar RSS (`404.0 -> 404.2 MB`). At 5M, `cache-large` improves
`67.822 -> 63.566 ms`. The first StreamFlexDesign 1M L1 application smoke is
neutral after a warm rerun (`0.93 s` default and `0.93 s` cache-large), and
L2 also ties (`373.053 -> 372.851 ms`). Treat `cache-large` as a promising
throughput-biased focused allocator policy, not a broad application default
until at least two representative L1 rows improve. These rows are
throughput/RSS tradeoff evidence, not lower-memory claims.
The selected follow-up policy gates are now recorded in
`evidence/REGION_REUSE_POLICY_MATRIX.md`: Dataflow AGGREGATE is too short and
neutral (`0.08-0.20 s` across policies), and generated Common Crawl-shaped q2
is also neutral in a one-pass L1 gate (`3.09 s` default and `3.09 s`
`cache-large`, same checksum/output). Therefore `cache-large` remains a
focused allocator policy candidate, not a broad optimized application mode.

Latest handle-backed allocation promotion:
the default checked epoch/page-token rows now use handle-backed Rift allocation
where the operator owns the lifetime. For StreamFlexDesign, default
`checked-epoch-stream` now reports `19.25 s` at 20M events versus legacy
`21.32 s` and heap `30.90 s`, with matching checksum/output and unchanged RSS.
For page-token rows, generated Common Crawl-shaped q2 now reports optimized
`rift-checked-page-token` at `9.76 s` versus legacy `11.06 s` and heap
`16.23 s`; the focused 1M page-token row is `23.059 ms` versus legacy
`24.687 ms` and heap `38.352 ms`. A focused warm/dirty-slab allocation probe
does not justify no-zero allocation yet: it likely measures pool warmup as
well as dirty-slab reuse, so zero-elision remains blocked on a lower-level
fresh/dirty probe plus definite-initialization proof.

Dataflow follow-up: `DataflowRegionMatrix` now promotes handle-backed
allocation for the full `checked-epoch-stream` direct-epoch family. The
handle-array crash is fixed by making the internal `RiftOpenStreamingHandle`
satisfy the allocation-only `SafeZone` contract used by Scala Native's array
helpers. The 10 epochs x 100k L2 gate reports legacy versus promoted default:
SELECT `18.956 -> 17.178 ms`, AGGREGATE `36.888 -> 33.551 ms`, and JOIN
`20.270 -> 19.133 ms`, all with matching checksums and zero GC. The matching
L1 final-clean rerun now reports promoted `checked-epoch-stream` at
SELECT/AGGREGATE/JOIN `15.5/30.5/15.5 ms` per iteration, versus
`gc-heap` `30.5/59.0/28.0 ms`, `region-scoped-rooted` `22.0/39.0/22.0 ms`,
and `checked-epoch-scoped` `17.5/32.5/18.5 ms`. This closes the current
Dataflow array blocker and turns the handle-backed stream row into L1 headline
timing plus L2 interpretation evidence.
Validation for this checkpoint passed: `sandbox3_next/compile`,
`RiftRegionCheckedCompilerTest` (`141/141`), `RiftRegionCheckedTest`
(`65/65`), and parent/child `git diff --check`.

Yak remaining-path follow-up: the real-input LiveJournal `graphreal`
`checked-epoch-stream` linked epoch now uses backend-known open-handle
allocation, with `checked-epoch-stream-legacy` retained as the old generic
allocation control. The 10M same-binary gate improves checked stream
`290.539 -> 279.469 ms` with matching checksum and RSS; checked scoped is
`280.801 ms` in the same run. This is a modest real-input allocation-lowering
gate, not a replacement for the larger 50M Yak topology headline.

Latest measurement-overhead protocol:
`evidence/MEASUREMENT_OVERHEAD_PROTOCOL.md` and
`evidence/FINAL_CLEAN_HEADLINE_RESULTS.md`. Initial L1 final-clean support now
exists for retained epoch, Yak, Dataflow, Common Crawl WET-shaped, ReML
Tier 1/Tier 2, StreamFlex, Stancu, SPECjbb2005-workload, LogHub, DSPBench, and
NEXMark binaries. The L1 table
now includes retained, Dataflow, Yak LiveJournal, generated Common
Crawl-shaped q1/q2, ReML Tier 1/Tier 2, StreamFlex direct epoch, Stancu transaction,
SPECjbb2005-workload port, LogHub top-template, and LogHub HDFS q2 page/window
rows, plus DSPBench Fraud/Log q2, NEXMark q3/q8/q9/q11, GH Archive
file-backed byte-slice q1/q2 rows, retained DSPBench/LogHub gap-fill rows, and
a larger LogHub HDFS top-template 5M x5 L1 row. It also now includes symmetric
direct-summary counterpart rows for GH Archive-shaped, DSPBench, and LogHub
generated/indexable lower bounds, plus the first AskUbuntu real text/top-word
L1 rows in `YakRegionMatrix`, plus the first `StreamFlexDesignMatrix` L1
throughput rows for the stable/transient/capsule design reproduction.
Remaining benchmark result files are still mostly L2 standard-stats evidence.
`evidence/EVALUATION_CLASSIFIED_SUMMARY.md` now also has a presentation
completeness audit: every representative row used by the report/slides is
complete for L1 elapsed/RSS, L2 interpretation, input type, topology/API,
comparison class, and allowed claim, or is explicitly lower-bound/control
evidence.
Latest L4 profiling update:
`sandbox/run_l4_profile_sweep.sh` is now the reusable external-profile harness
for representative benchmark sweeps, with usage recorded in
`evidence/PROFILE_SWEEP_MATRIX.md`. The first representative L4 sweep is now
complete for StreamFlex-design, generated Common Crawl-shaped q2, DSPBench
Fraud q2, LogHub HDFS streaming top-k, StreamIt FilterBank, and StreamIt
BeamFormer, with a follow-up sweep for Yak LiveJournal, Dataflow AGGREGATE,
SPECjbb2005-workload, ReML-shaped `msort`/`ratio`, a Yak graphstep epoch-body
profile, and a completion pass covering AskUbuntu real text, LogHub
Spark/Windows top-k, Theodolite power q2, NEXMark Q8/Q9, larger SPECjbb, and
ReML `logic`/`ray`/`tsp`. The main finding is stable across families: real
streaming/text/log/time-series rows are mostly parser/hash/query dominated;
generated object-pressure rows expose allocator/zeroing/traversal costs;
StreamIt primitive kernels and ReML `ray`/`tsp`/`ratio` are compute controls
rather than GC-heavy evidence; generic
`EpochFold` is slow because of table/probe, cursor, allocator/stat, and
`checkOpen` work rather than because close/reclaim alone is expensive. The
first Yak LiveJournal profile mostly samples gzip/file input parsing; the
generated graphstep profile now isolates the epoch body and shows the checked
cost is allocation/object construction/zeroing in a tight linked-object epoch,
while heap pays the same graph loop plus Immix allocation/metadata/mark/sweep.
The ReML `logic` profile adds one important caveat: even checked scoped region
nodes can still trigger heap GC if the port allocates heap scratch arrays inside
the hot loop.
L4 remains interpretation-only; L1/L2 keep their existing roles.

Post-rerun profiles now cover the actual clean winners as well:
StreamFlexDesign `checked-epoch-stream` and generated Common Crawl-shaped q2
`rift-checked-page-token`. They confirm the same optimization direction after
the clean medians: remaining checked cost is allocation/object construction,
mandatory zeroing, stable-state or token-query CPU, capsule/cursor traversal,
and a still-visible final-clean allocation-stats enable check. They do not
point to more bucket open/close lifecycle tuning as the next high-value target.

Latest profile-guided allocator work:
child `9ee340950` implements and validates the first narrow zone allocator
cleanup suggested by the Yak graphstep profile: cache the page size in each
`Zone` and lower the allocator's pad-to-8 calculation to a macro. This removes
the sampled `MemoryPool_page_size`, `Util_pad`, and `scalanative_zone_pad8`
frames from the post-change Yak graphstep checked scoped L4 profile without
changing object layout or zero-initialization semantics. Validation now passes:
`sandbox3_next/compile`, `RiftRegionCheckedCompilerTest` (`141/141`), and
`RiftRegionCheckedTest` (`64/64`). This is not a new headline throughput row;
it is profiling-guided overhead cleanup. The remaining sampled checked cost is
allocator body, mandatory zeroing, and SafeZone-backed `allocUncheckedImpl`
wrappers.

Latest post-cleanup timing check:
`evidence/YAK_REGION_MATRIX.md` now records focused Yak graphstep L1/L2 rows
after the allocator cleanup. At 10M logical messages, checked scoped graphstep
improves from the previous clean `181.341 ms` row to `167.164 ms`, with
external L1 `0.93 s`; heap is `263.051 ms` / `1.31 s`. At the 50M graphstep
profile scale, checked scoped remains the fastest safe row at `1710.128 ms`
L2 and `9.57 s` L1, versus heap `2276.697 ms` / `12.25 s`, rooted scoped
`1746.292 ms` / `9.76 s`, and checked stream `2005.310 ms` / `11.11 s`.
This upgrades the allocator cleanup from profile-only evidence to a measured
focused timing improvement, while still leaving allocation body and zeroing as
the next real bottlenecks.

Latest final-clean allocator-stat cleanup:
Rift raw/object/byte allocation counters are now disabled automatically in
`RIFT_FINAL_CLEAN=1` runs, with `RIFT_ALLOC_STATS=1` as an explicit diagnostic
override. The focused 5M `ObjectAllocationLoweringMatrix`
`rift-checked-rift` row improves from `87.999 ms` with counters forced on to
`76.345 ms` with final-clean counters disabled, with matching checksum and zero
GC. This improves L1-style headline binaries without changing L2/default stats
runs. The first application impact gate is workload-sensitive rather than
universal: StreamFlex-design `checked-epoch-stream` improves from `9.18 s` to
`8.57 s`, and generated Common Crawl-shaped q2 `rift-checked-page-token`
improves from `4.33 s` to `4.23 s`; Dataflow AGGREGATE and Yak graphstep
single-process gates are noisy and should remain interpretation-only.

Latest allocation-lowering cleanup:
Rift managed-object allocation now has a dedicated pointer-aligned fast path
instead of routing every checked object allocation through the generic
raw-allocation alignment helper. This keeps object zero/init and header setup
unchanged. The focused 5M `ObjectAllocationLoweringMatrix` `rift-checked-rift`
row improves from the previous final-clean `76.345 ms` to `69.912 ms`, with
matching checksum and zero GC. The forced-stats row is `89.081 ms`, so L2
allocation counters remain interpretation overhead. Single-run application
gates also move in the expected direction: StreamFlex-design checked stream
`8.57 s -> 8.07 s`, and generated Common Crawl-shaped checked page-token q2
`4.23 s -> 3.98 s`. This is allocation-lowering evidence for the Rift-native
checked backend, not a SafeZone-backed result and not yet a new final headline
median.

Latest open-allocation cleanup:
The final `OpenStreamingRegion` classes now call the Rift/SafeZone backend
allocators directly in `allocUncheckedImpl`, removing an extra superclass hop
from operator-owned `allocOpen`. Public defensive `allocImpl` is unchanged.
Focused final-clean 1M page-token rows are `24.665 ms` for checked Rift and
`24.816 ms` for checked SafeZone-backed, with matching checksum and zero GC.
Single-run application gates are workload-sensitive: StreamFlex-design checked
stream moves from `8.07 s` to `7.72 s`, while generated Common Crawl-shaped q2
is flat at `3.98 s -> 4.00 s`. A dirty-slab bulk-zeroing attempt was rejected:
it preserved zero-init semantics but regressed focused 5M allocation slightly
(`70.044 ms` versus the committed `69.912 ms`) by moving work into slab attach.

Latest clean final-clean reruns:
The latest all-optimizations rows refresh the post-cleanup L1 evidence.
Focused 1M page-token, five measured runs: heap `38.352 ms`, legacy checked
Rift page-token `24.687 ms`, promoted checked Rift page-token `23.059 ms`,
and checked SafeZone-backed page-token `25.805 ms`, all with matching
checksum. StreamFlexDesign throughput at 20M events x3 is heap `30.90 s`,
legacy checked stream `21.32 s`, promoted checked stream `19.25 s`, and
checked scoped `23.41 s`. Generated Common Crawl-shaped q1/q2 at 1M pages x3
is heap `16.67/16.23 s`, promoted checked Rift page-token `9.30/9.76 s`,
legacy checked page-token `10.29/11.06 s`, and checked SafeZone-backed
page-token `12.88/14.39 s`. A quick SPECjbb/Stancu-style 4-warehouse
transaction gate keeps the same direction: heap `0.51 s`, rooted scoped
`0.21 s`, checked epoch stream `0.18 s`, and checked scoped epoch `0.19 s`.
These are presentation-grade generated/StreamFlex-design/transaction-topology
rows; Common Crawl remains generated stressor evidence.

Latest remaining-path allocation-lowering gate:
`evidence/SPECJBB2005_PORT_MATRIX.md` now records the SPECjbb/Stancu-style
checked stream epoch promotion from generic `RiftRegion.allocOpen` to
backend-known `RiftAllocator.allocateOpenHandle`. The public benchmark label
`checked-epoch-stream` is the optimized default; `checked-epoch-stream-legacy`
keeps the old path. At 4 warehouses x 100k transactions, L1 is optimized
checked stream `0.27 s`, explicit open-handle alias `0.27 s`, legacy checked
stream `0.30 s`, checked scoped epoch `0.31 s`, rooted scoped `0.34 s`, and
heap `0.64 s`. L2 medians are optimized checked stream `51.168 ms`, legacy
`56.371 ms`, checked scoped `54.146 ms`, rooted scoped `60.347 ms`, and heap
`67.378 ms` with `7.635 ms` GC. The follow-up Theodolite real-streaming q2
gate transfers the same optimization to a parser/query-dominated time-series
row: optimized `checked-epoch-stream` is L1 `3.80 s` versus legacy `3.83 s`,
checked scoped `3.83 s`, rooted scoped `3.90 s`, and heap `4.33 s`; L2 is
optimized `993.191 ms`, legacy `1006.176 ms`, checked scoped `995.167 ms`,
rooted scoped `1009.541 ms`, and heap `1054.432 ms` with `19.906 ms` GC. These
are positive handle-backed allocation results, not zeroing/root-free claims.

Latest operator-gate status:
`evidence/OPERATOR_GATE_STATUS.md`. This keeps rank/top-k/median/hash/join work
out of application claims until each candidate has natural heap, same-shape
heap, retained controls where needed, and a focused 1M gate.

Latest top-k candidate:
`evidence/LOGHUB_TOP_TEMPLATES_MATRIX.md`. This adds a retained-object
top-template workload over generated LogHub-shaped data and real-preloaded HDFS
logs. At 1M real HDFS lines, checked scoped retained top templates are
`81.174 ms` versus retained heap `116.138 ms`, removing `31.161 ms` median
timed GC. That earlier benchmark-local row was primarily a throughput/GC win.
The reusable `EpochTopKByKey` API also passes the retained gate. After the
increment hot-path follow-up, generated 1M checked scoped top-k
is `274.914 ms` versus retained heap `397.788 ms`, and real HDFS preloaded
checked scoped top-k is `82.170 ms` versus retained heap `111.704 ms`. The
same-run API overhead versus the benchmark-local checked path is now about
`5.7%` generated and `7.0%` real HDFS in L2. L1 final-clean real HDFS x20 rows
confirm the direction with external timing: reusable checked top-k scoped is
`4.88 s` and about `28 MB` RSS versus retained heap `5.52 s` and about
`205 MB` RSS; the benchmark-local checked retained path is `4.80 s`, so the
report-facing API overhead is about `1.7%`. The larger real HDFS 5M x5 row
keeps the reusable API ahead of retained heap (`18.26 s`, `92 MB` versus
`19.04 s`, `504 MB`), while the matching L2 row removes heap's `62.421 ms`
timed GC. Yak topword now provides a second
natural top-k workload for the same reusable API: at 10M generated records,
`checked-epoch-topk-scoped` is `249.311 ms` versus natural heap `313.724 ms`
and the same-shape heap top-k retained control `297.740 ms`, with zero timed
GC and region-like RSS. The caveat is important: the older checked direct
epoch close-traversal topology is still faster for this local Yak topword row
at `234.031 ms`, so `EpochTopKByKey` is a passed reusable top-k API, not the
universal best topology.
The L1 final-clean Yak topword x20 row confirms the same direction with
external timing/RSS: reusable checked top-k scoped is `4.94 s` and about
`16 MB` RSS versus natural heap `6.25 s` / `75 MB` and same-shape heap top-k
`5.72 s` / `147 MB`. Direct checked epoch remains faster at `4.61 s`.
AskUbuntu `topwordreal` now adds a real Stack Exchange text row to the same
Yak/Hadoop top-word family. At 20M real tokens x5, direct checked epoch scoped
is `7.16 s` and `174 MB` RSS versus heap `7.77 s` and `986 MB`; the matching L2
row is `432.824 ms` with no timed GC versus heap `511.485 ms` with
`33.471 ms` median timed GC. The reusable top-k scoped row is still a large RSS
win but loses elapsed to natural heap at 20M (`7.86 s` vs `7.77 s`), so it
remains an API cost target rather than the fastest text-top-word
implementation.
Spark now provides a third real LogHub input check. At 5M real Spark log lines
x3, reusable checked scoped top-k removes the retained heap row's `128.140 ms`
median timed GC and wins the L2 work loop (`579.440 ms` versus `703.804 ms`),
but the L1 process row is only modestly faster (`16.63 s` versus `16.93 s`)
and RSS is tied/slightly worse (`509 MB` versus `504 MB`). Treat it as
retained top-k confirmation, not a new flagship real-input claim.
Windows provides a fourth real LogHub input check at much larger source scale
(`114608388` log lines). At 5M lines x3, checked scoped top-k removes
`122.440 ms` median timed GC and wins the L2 work loop (`548.806 ms` versus
retained heap `679.123 ms`), while L1 process time is `31.28 s` versus
`32.37 s` and RSS is tied/slightly worse. This reinforces the same conclusion:
the retained top-k API helps the memory-management part, but file loading and
query CPU dominate end-to-end real-log time.

Latest streaming-input checkpoint:
`evidence/STREAMING_INPUT_PROTOCOL.md` defines the new `real-streaming-input`
class. `evidence/REAL_STREAMING_INPUT_MATRIX.md` records the first converted
row: LogHub HDFS top templates with `LOGHUB_TOP_INPUT_MODE=streaming-file`.
Unlike the older `file-backed` top-template rows, this mode reopens the real
HDFS log inside every benchmark run, streams line records through a bounded
source cursor, and does not preload parsed arrays. At 1M HDFS lines, reusable
checked scoped `EpochTopKByKey` is L1 `8.06 s`, RSS `12 MB`, versus retained
heap/drop-anchor L1 `8.10 s`, RSS `76 MB`; the matching L2 row removes
`32.681 ms` median timed heap GC. This is real streaming-input retained-object
and RSS evidence, not yet the missing flagship GC-heavy stream result because
file parsing/query CPU still dominates.
The 5M streaming-file scale-up confirms that ceiling: retained heap is external
`66.63 s`, L2 `13244.113 ms`, median GC `109.535 ms`; checked scoped top-k is
external `66.95 s`, L2 `13368.555 ms`, GC `0 ms`, with matching
checksum/output. Heap GC is only about `0.8%` of the streaming loop, so this is
streaming ceiling/control evidence. The sandboxed 5M run missed RSS because
`/usr/bin/time -l` hit a `sysctl` permission failure; rerun L1 outside the
sandbox before using it as a presentation table.
GH Archive now has the same explicit streaming-input classification:
`GITHUB_ARCHIVE_INPUT_MODE=streaming-file` replays gzip NDJSON lines through
the byte-slice reader inside each run. The 100k q1/q2 triage shows modest
checked page-token wins and removes heap's observed max-GC tails
(`71-72 ms` in one heap run per query), but median heap GC remains zero and
byte-slice parsing dominates. Treat this as real-streaming-input RSS/tail
evidence rather than the missing GC-heavy stream flagship.
Theodolite now has the same explicit streaming-input treatment for a real
power-meter trace: `THEODOLITE_POWER_INPUT_MODE=streaming-file` parses records
inside each run instead of preloading parsed primitive arrays. The current row
uses the shared byte-line reader plus a reusable semicolon byte-field cursor,
superseding the first `String.split` streaming row. At 1M q2 hierarchical
records, checked scoped epoch is an L1 throughput/RSS/fixed-memory win
(`3.83 s`, `16.0 MB` RSS) versus heap (`4.33 s`, `75.3 MB` RSS), and the
optimized checked stream row is slightly faster (`3.80 s`, `15.9 MB` RSS).
The L2 row is `993.191 ms` with `0 ms` median GC for optimized checked stream
versus heap `1054.432 ms` with `19.906 ms` median GC. This is useful
real-streaming evidence and also a methodology lesson: parser allocation can
inflate apparent GC pressure if not controlled.
LogHub richer q3 template/session now also has explicit streaming-input
evidence in `LogHubRegionMatrix`: `LOGHUB_INPUT_MODE=streaming-file` streams
1M HDFS log lines into the existing page/window template/session query. This
row is an RSS/fixed-memory control, not a throughput win: checked scoped
page-token is L1 `30.29 s`, RSS `130 MB`, versus heap `26.88 s`, RSS
`862 MB`; L2 reduces heap's max GC tail from `131.533 ms` to `58.455 ms`, but
parser/template/session CPU dominates.
The richer Windows q3 template/session row is negative/control evidence:
checked page-token cuts median timed GC (`33.945 ms` versus heap `147.336 ms`)
but loses elapsed (`17783.560 ms` versus heap `17405.613 ms`) and RSS. This
confirms that richer real-log parsing alone is still parser/query CPU bound.
The richer Spark q3 template/session row reaches the same conclusion on a
61-file real Spark application subset. At 1M lines, checked scoped page-token
is only slightly faster in L2 (`7534.013 ms` versus heap `7602.328 ms`) and
cuts RSS sharply (`56 MB` versus heap `408 MB` in the L1 RSS run), but heap
timed GC is still only `140.934 ms`, about `1.9%` of elapsed. Treat Spark q3
as real-input modest/control evidence, not as the missing GC-heavy flagship.

Latest ReML/MLKit PLDI-style table:
`evidence/REML_MLKIT_PLDI_TABLE.md`. It recreates the paper table shape as
paper-reported evidence, then places local Scala Native Tier 1 port ratios next
to it using L1 local timing/RSS where available. It also now includes first
Tier 2 shaped-port rows for `logic`, `ray`, and `tsp`. These broaden the
comparison axis but are not new headline wins: `logic` ties elapsed while
regressing RSS, `ray` is a near-tie control, and `tsp` is an RSS/control row
with a small elapsed loss. Exact MLKit/ReML artifact reruns are now
**gated/low-priority**, not an active blocker: they are useful only if we need a
same-machine raw wall-clock comparison. The report should otherwise compare
paper axes, local Scala Native ratios, RSS, GC, and safety/API burden.
The same file now includes a same-axes thesis interpretation table over the
full PLDI Figure 9 program list. It also includes a wide same-metric table:
the paper columns (`loc`, `fcns`, `inst`, `delta`, ReML/MLKit time, RSS, and
GC count) stay intact, while local Scala Native columns add `gc-heap`,
`region-scoped-rooted`, `checked-region-stream`, and `checked-region-scoped`
time/RSS plus L2 GC interpretation where available. Each row then explains why
Rift is better, worse, neutral, or unavailable on that shape.

Latest SPECjbb2005-workload port checkpoint:
`evidence/SPECJBB2005_PORT_MATRIX.md`. This is a clean-room Scala Native
workload port, not an official SPEC result. It now has an L1 final-clean
8-warehouse representative row from child `678a6eb41`: checked epoch scoped is
`2.21 s` total for 20 inner iterations versus heap `2.64 s` and rooted scoped
regions `2.48 s`, with RSS about `8.0 MB` versus heap `12.4 MB`. The L2 scale
rows still provide GC interpretation: at 8 warehouses, checked epoch scoped is
`108.649 ms` versus heap `129.674 ms` with `15.125 ms` timed GC. The
transaction-local object proxy is `4,163,936` region-freed objects at 8
warehouses.

Latest direct-epoch extension checkpoint:
`evidence/DIRECT_EPOCH_TOPOLOGY_MATRIX.md` now includes generated/indexable q2
extensions for DSPBench, GH Archive-shaped, and LogHub-shaped rows. Checked
direct epoch allocates ordinary records inside a bucket epoch and retains only
primitive bucket summaries until the original close point. The 2026-05-09
`heap-direct-epoch` same-shape control shows the large q2/q3 deltas are mostly
direct-aggregate topology wins: GH Archive-shaped q2 is heap `287.380 ms`,
heap-direct `54.642 ms`, checked scoped `56.013 ms`; LogHub-shaped q2 is heap
`526.803 ms`, heap-direct `191.601 ms`, checked scoped `193.938 ms`;
DSPBench Fraud q2 is heap `400.900 ms`, heap-direct `272.251 ms`, checked
scoped `267.739 ms`. Interpretation: checked regions are close to same-shape
heap, and Fraud q2 still has a small checked-region edge, but these rows should
be reported as topology/operator evidence rather than pure placement wins.
NEXMark Q3/Q8/Q9/Q11 remain page-token/join/window topology rows because their
state affects later events.

Latest clean representative direct-epoch rerun:
After child commit `918c7d4c1` and parent commit `ab570b1`, the representative
direct-epoch rows were rerun from clean commits. The strongest current real
input row is SNAP LiveJournal `graphreal` at 50M replayed edges:
`checked-epoch-scoped` is `2008.320 ms`, `0 ms` timed GC, and `2.11 GB` RSS
versus `gc-heap` `2958.659 ms`, `400.484 ms` timed GC, and `3.91 GB` RSS.
Dataflow SELECT/AGGREGATE/JOIN are `19.691/34.676/19.762 ms` for checked
epoch scoped versus heap `27.775/50.837/30.387 ms`; StreamFlex throughput is
`157.334 ms` for checked scoped direct epoch versus heap `216.853 ms`; and
Stancu-style transactions are `155.863 ms` for checked scoped direct epoch
versus heap `220.951 ms`.

The current handle-backed dirty checkpoint supersedes the Dataflow stream-side
numbers but not the other clean direct-epoch rows: Dataflow
SELECT/AGGREGATE/JOIN now report L1 `checked-epoch-stream`
`15.5/30.5/15.5 ms` per iteration, with same-run heap
`30.5/59.0/28.0 ms` and checked scoped `17.5/32.5/18.5 ms`.

Latest L1 final-clean direct-epoch follow-up:
`evidence/FINAL_CLEAN_HEADLINE_RESULTS.md` now records external `/usr/bin/time`
rows for the same StreamFlex/Stancu story. StreamFlex throughput at 20 x 200k
events is checked scoped direct epoch `0.58 s` versus heap `0.79 s` and
improved SafeZone `0.77 s`. StreamFlex latency at 20 x 10k events is checked
scoped direct epoch `0.17 s` versus heap `0.18 s`, and deadline misses drop
from heap `4` to checked `0`. Stancu transactions at 20 x 200k transactions
are checked scoped direct epoch `0.57 s` versus heap `0.85 s` and improved
SafeZone `0.71 s`. These rows are the clean headline timing/RSS versions of
the earlier L2 standard-stats interpretation.

Latest retained-epoch reclaim checkpoint:
`evidence/RETAINED_EPOCH_RECLAIM_MATRIX.md` adds retained no-traverse controls
to separate topology from memory management. In the focused 1M matrix,
`checked-scoped-epoch-retained-no-traverse` is `24.274 ms` versus retained heap
`36.233 ms`, while heap spends `10.109 ms` in timed GC and uses about `21.3 MB`
RSS versus about `4.9 MB` for checked scoped. DSPBench Fraud q2 retained
controls show checked scoped retained epoch `370.746 ms` versus retained heap
`392.743 ms`, removing `35.631 ms` median timed GC. GH Archive-shaped q2 is the
strongest retained generated/preloaded row so far: checked scoped retained
epoch `186.868 ms` versus retained heap `257.377 ms`, removing `77.208 ms`
median timed GC and cutting RSS from about `147 MB` to `15 MB`. LogHub q2
retained also wins (`402.821 ms` versus retained heap `469.079 ms`); LogHub q3
is a mixed row where checked scoped retained improves elapsed (`2106.541 ms`
versus `2244.266 ms`) but not RSS. This is the fair memory-management
comparison: ordinary objects survive until the epoch boundary in both heap and
region modes, and close does not traverse records. The summary-only direct rows
remain topology/operator lower bounds, not pure Rift placement wins.

The GH Archive-shaped q2 retained row now also has L1 final-clean external
timing/RSS: over 20 x 1M generated/preloaded q2 iterations, retained heap is
`4.62 s` and `147 MB` RSS, checked stream retained is `3.65 s` and `16 MB`,
and checked scoped retained is `3.44 s` and `16 MB`. The summary-only lower
bound is `1.28 s` and remains topology evidence only.

That lower bound is now symmetric: the L1 checked direct-summary counterparts
are `1.45 s` for checked stream and `1.45 s` for checked scoped, both around
`7 MB` RSS, versus heap direct-summary `1.36 s`. Direct-summary is therefore a
fast operator topology for both heap and regions, not a heap-only special case
and not a reclaim claim.

The same symmetry audit now covers DSPBench and LogHub generated/indexable
direct-summary rows. DSPBench Fraud q2 direct-summary is heap `5.62 s` versus
checked stream/scoped `5.67/5.68 s` over 20 x 1M iterations; DSPBench Log q2
is heap `4.55 s` versus checked `4.56/4.59 s`. LogHub q2 is heap `4.23 s`
versus checked `4.39/4.38 s`, and LogHub q3 is heap `37.01 s` versus checked
`37.65/38.00 s`. These rows are classified as symmetric topology lower bounds,
not memory-management wins, because they legally compute summaries on append
and avoid retaining ordinary records until close.

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

Latest reusable epoch checkpoint:
The direct `RiftRegion.epoch { ... }` API that won on Yak/LiveJournal now also
covers the Broom/Dataflow methodology harness. At 10 epochs x 100k documents,
the current handle-backed `checked-epoch-stream` row is the fastest checked
direct-epoch row in the L1 presentation gate:
SELECT/AGGREGATE/JOIN `15.5/30.5/15.5 ms` per iteration versus `gc-heap`
`30.5/59.0/28.0 ms`, region-scoped rooted `22.0/39.0/22.0 ms`, and
checked scoped epoch `17.5/32.5/18.5 ms`. The matching L2 gate reports zero
timed GC for checked rows and confirms the promoted stream row improves all
three operators versus legacy checked stream allocation. Page-token remains a
useful SELECT-only control, but the direct epoch API is the reusable topology
for the whole Dataflow family. The same work closed the Yak grouped-sort gap
with a region-captured array:
`checked-epoch-stream` `230.000 ms`, `checked-epoch-scoped` `230.799 ms`,
heap `235.554 ms`, improved SafeZone `233.068 ms`; this is coverage/modest
CPU-bound evidence because heap timed GC is only `3.333 ms`.

Latest real-input search checkpoint:
`evidence/DSPBENCH_REGION_MATRIX.md` includes DSPBench Log Processing over the
bundled real `http-server.log` common-log file, and
`evidence/LOGHUB_REGION_MATRIX.md` now includes richer real BGL
`q3-template-session` plus a larger HDFS v1 follow-up. DSPBench Log 1M
`log-q2-window` is a modest checked scoped page-token win:
`1733.654 ms` versus heap `1750.291 ms`, with heap median/max GC
`44.992/88.210 ms` reduced to `18.402/18.584 ms` in L2. Its L1 final-clean
row is checked scoped page-token `8.79 s`, `47.6 MB` RSS versus heap `8.89 s`,
`308 MB` RSS for 1M events x5 iterations. Fraud q2's L1 row is an RSS win but
not an elapsed win for checked scoped page-token: `4.44 s`, `59.5 MB` RSS
versus heap `4.39 s`, `358 MB`, while trusted Streaming is the elapsed
lower-bound at `4.18 s`. LogHub HDFS v1 q2 is the
best new real-log row: checked scoped page-token `7871.856 ms` versus heap
`8227.369 ms`, removing heap's `92.659 ms` median timed GC and lowering RSS in
L2 standard stats. Its L1 final-clean row is more conservative: checked scoped
page-token essentially ties heap on total process elapsed (`25.56 s` versus
`25.60 s` for 1M lines x3 q2 iterations) while cutting max RSS from about
`409 MB` to about `79 MB`.
RIoTBench/MHEALTH is now wired as a provenance-clean IoT source: the UCI
MHEALTH dataset has `1215745` rows, but 1M q1/q2 report zero timed heap GC and
only near-tie/small-SafeZone-win elapsed results. Theodolite UC2/UC4-style
local rows are now paired with the real UCI Household Electric Power trace.
The q2 hierarchical row creates visible heap GC but remains a tie/control: at
full local input, heap is `287.296 ms` with `20.354 ms` median timed GC, while
`checked-epoch-scoped` is `288.495 ms` with zero timed GC and tied process
elapsed in strict L1 (`5.45 s` versus heap `5.46 s`) with slightly lower RSS.
These are useful real-input/control rows, not the missing GC-heavy flagship.

Latest Yak real-input checkpoint:
`YakRegionMatrix` now has `graphreal`, a real edge-list replay over SNAP
Twitter ego and LiveJournal graphs. The benchmark preloads real edge pairs into
primitive control arrays, maps vertex IDs into the configured vertex range,
then replays them as epoch-local `EdgeUpdate` objects. Twitter ego proved the
path; the larger SNAP LiveJournal follow-up is now the representative row. The
new 10M/50M topology follow-up separates checked backend from checked
topology: whole-run region, per-epoch region, and page-token region are all
measured. In the latest clean 50M rerun, `gc-heap` is `2958.659 ms`, median
timed GC is `400.484 ms`, and RSS is `3913564160` bytes. Per-epoch region rows
remove timed GC and keep RSS near `2.11 GB`: `region-scoped-rooted` is
`2351.582 ms`, `region-stream-rootless` is `2499.975 ms`,
`checked-epoch-scoped` is `2008.320 ms`, and `checked-epoch-stream` is
`2064.867 ms`.
Page-token checked rows remain wins over heap but are slower for Yak:
`checked-page-token-scoped` is `2586.919 ms`, and
`checked-page-token-stream` is `2746.897 ms`. Interpretation: checked Rift
needs user-visible lifetime topology (`epoch`, `window`, `page`) rather than a
single universal checked operator. This is the first strong real-input
prior-work-shaped row where checked regions win over heap; it is still not
exact Yak/GraphChi artifact evidence. The reusable `EpochBuffer` follow-up
was correct and beat heap in an earlier rerun, but the clean direct epoch path
is the row to headline. `RiftRegion.epoch { ... }` now exposes the direct
checked linked epoch block as a reusable API, and `graphreal` routes through
it. The clean 10M rerun confirms the direction: direct checked epoch is
`417.426/425.983 ms` scoped/stream, versus heap `599.428 ms`. The same
reusable epoch topology now covers local Yak-shaped `wordcount`, `graphstep`,
`topword`, and `graphchi`; in the 10M rerun, `checked-epoch-scoped` is fastest
among measured heap/rooted/streaming/checked rows for all four and removes the
heap timed-GC component. `sort` is now covered by a checked region-captured
array row, but remains CPU-bound/modest rather than a representative GC win.
The topword follow-up also adds the reusable `EpochTopKByKey` operator with a
same-shape heap top-k retained control. This confirms reusable top-k beats heap
and same-shape heap, while preserving the separate conclusion that direct
checked epoch remains the best Yak topword topology in the current harness.
The L1 final-clean row records `4.94 s` for reusable checked scoped top-k
versus `6.25 s` heap and `5.72 s` same-shape heap top-k over 20 x 10M
generated records, with matching checksum.

Benchmark guide: `docs/BENCHMARK_CATALOG.md` describes what each benchmark is
meant to measure and which rows are generated, real-input, focused, or
ceiling/control evidence.

Memory-cost reporting rule:
Timed GC is collection time only. It does not include all heap
memory-management costs, and it does not explain every elapsed win by itself.
For example, LogHub HDFS q2 has heap `8227.369 ms` with only `92.659 ms`
median timed GC, while checked scoped page-token is `7871.856 ms`. The
roughly `355 ms` elapsed gap is larger than timed GC because the row also
changes mutator-side memory behavior: allocation-path work, heap growth, RSS
and cache locality, object lifetime placement, region bucket close policy, and
operator append/traversal shape. Future representative tables should therefore
report both direct GC columns and broader memory-cost signals:

- timed GC median/max and runs with GC;
- RSS and heap-cap sensitivity;
- allocation-call counts/bytes/time where attribution is enabled;
- region operation time, object count, opens/closes/resets;
- diagnostic-only append, bucket open/close, cursor traversal, and query CPU
  buckets when investigating overhead.

Diagnostic allocation/timing counters are useful for attribution, but they are
not headline timing rows because they can perturb performance.

## How To Read The Tables

Rift results must be structured by comparison class before interpretation. A
natural heap baseline answers the practical end-to-end question; a same-shape
heap control answers whether a region result is really memory placement rather
than a better topology; a summary-only row is an operator/data-processing lower
bound; and a retained-object drop-anchor row is the fair memory-management
comparison. In the retained case, both heap and region allocate ordinary
records, retain them until the epoch/window boundary, update summaries on
append, and avoid user-level close traversal. The heap version can also close
in O(1) by dropping a bucket reference, but those objects remain for the GC to
trace/reclaim later. The region version closes/resets the allocation area in
bulk. That retained comparison is the clearest answer to whether Rift improves
memory management.

This also matches the prior-work discipline. Broom, Yak, StreamFlex, Stancu et
al., and ReML/MLKit do not enumerate every possible heap rewrite. They choose a
memory/lifetime model justified by the system: dataflow epochs, data/control
splits, stream periods, transaction annotations, or compiler-inferred regions.
Rift should therefore report the best safe checked topology for each workload,
but include same-shape heap controls whenever the topology changes computation.
Unsafe/rootless modes remain lower bounds, not user-facing claims.

The project-level interpretation is now recorded in
`docs/PRIOR_WORK_MEMORY_MANAGEMENT_INTERPRETATION.md`. The short version is:
prior work gets wins when it can keep durable control state under the normal GC
while moving high-churn data objects into a lifetime domain that is closed in
bulk. That is why `RiftRegion.epoch`, retained epoch controls, and page/window
tokens are the central abstractions. More specialized top-k/join/rank/median
operators are useful only when they expose the same lifetime principle without
turning the benchmark into a manual algorithm rewrite.

| Prior system | General reason it can win | Rift reporting lesson |
|---|---|---|
| Broom | Dataflow operators create fate-sharing objects whose lifetime is bounded by the dataflow step/operator. | Dataflow rows should report operator lifetime boundaries and GC share, not just elapsed. |
| Yak | Data-space objects are epochal while control objects are durable. | Checked epochs should replace dynamic escape/promotion where static capture checks are strong enough. |
| StreamFlex | Scoped stream memory reduces GC interference and deadline/tail events. | Latency/tail rows matter even when throughput deltas are modest. |
| Stancu et al. | Transaction/phase-local allocation can be region-freed, especially under young-gen pressure. | SPECjbb/Stancu-shaped rows need transaction-boundary, region-freed proxy, GC count/time, and API burden. |
| ReML/MLKit | Region inference and GC safety reduce tracing while preserving polymorphic correctness. | ReML comparisons should report ratios/RSS/GC/safety burden, not raw cross-language wall-clock unless exact artifacts rerun locally. |

Design implications for Rift:

- Keep the primary public story at the lifetime level: epoch, page/window,
  transaction, retained-object reclaim.
- Treat reference capabilities, active/closed region type-state, immutable or
  static metadata, and bridge/root objects as proof/design vocabulary first.
- Add those capabilities to the user-facing API only when they remove measured
  runtime work such as blanket root registration, close-time scans, dynamic
  escape tables, or stale-token checks.
- Do not turn the system into a large operator catalog unless the operator
  exposes a reusable lifetime boundary and passes same-shape controls.

Design-lesson backlog:

| Candidate | Why it matters | Runtime work it could remove | Current status |
|---|---|---|---|
| Active/closed region typestate | Names which handles may allocate, close, or only observe. | Hot-path `isOpen` checks and stale-token defenses in operator-owned paths. | Internal probes now cover direct epoch, page-token append/map-filter/count-by-key, epoch buffer, and stale public page-token regions. No further checks were removed because open page-token handles are not yet statically linear after close. |
| Immutable/static metadata references | Lets region objects point at durable read-only metadata safely. | Blanket page/root registration for root-free eligible checked rows. | Positive compiler probes now cover static metadata through `allocOpen` in direct epoch and operator-owned page/epoch-buffer paths; root-free backend lowering is still not a safety claim. |
| Bridge/root handles | Makes mixed heap-region edges explicit. | Ad hoc heap-region tracking and conservative roots. | Existing `HeapRoot` is the v1 bridge handle; probes now cover it in direct epoch and operator-owned page/epoch-buffer paths. Needs measured backend payoff before broader API. |
| StreamFlex-style latency reporting | Captures wins from removing GC tails even when median throughput is close. | Not runtime removal; it changes what evidence we collect. | Keep p95/max/deadline metrics in latency workloads. |
| Stancu-style annotation/API burden | Measures how much code users must mark with epoch/page/window/root scopes. | Not runtime removal directly; constrains API complexity. | Representative burden counts now live in `evidence/API_BURDEN_SUMMARY.md`; keep extending them with final rows. |

Rule: none of these becomes a user-facing capability until it either removes a
measured runtime cost or fixes a concrete safety gap.

Current claim table:

| Claim type | Current evidence | Claim boundary |
|---|---|---|
| Retained-object memory management | Focused retained 1M, GH Archive-shaped retained q2, LogHub retained q2/q3, DSPBench Fraud retained q2. | Compare retained heap/drop-anchor against retained checked regions only. |
| Reusable checked epoch topology | Yak LiveJournal 50M, Dataflow SELECT/AGGREGATE/JOIN, StreamFlex throughput/latency, Stancu/SPECjbb-style transactions. | Applies when ordinary objects share a batch/epoch lifetime. |
| Page/window checked stream topology | Generated Common Crawl WET-shaped q1/q2, focused page-token rows, modest real LogHub/DSPBench rows. | Strongest rows are generated stressors; real-input rows are modest. |
| Topology/operator lower bound | Summary-only/direct-aggregate rows for GH Archive-shaped, LogHub-shaped, and DSPBench q2/q3. | Not a pure memory-management win. |
| Gated operators | Rank/table/fold/hash-heavy operators. | Require natural heap, same-shape heap, retained control if applicable, and a focused 1M gate before application claims. |

Legacy and rerun-required evidence is not removed from the project history, but
it is demoted in presentation tables. Dirty fast-path rows, root-mode-0
SafeZone rows, old L2 rows with L1 replacements, benchmark-local count arrays,
legacy GH Archive string-parser rows, and pre-protocol DEBS/TableRank/rank rows
must be treated according to the audit in
`evidence/EVALUATION_CLASSIFIED_SUMMARY.md`: either replace with a current L1
row, keep as L2 interpretation, keep as lower-bound topology evidence, or
archive/control only.

Measurement levels are separate from comparison classes. Current evidence rows
are mostly **L2 standard stats**: they are valid for interpreting GC, RSS, and
region behavior, but they still read counters around the timed section. Final
paper headline elapsed/RSS should come from **L1 final-clean** runs: optimized
non-profiled binaries, no diagnostics or in-timed-section GC/region counter
reads, and external `/usr/bin/time -l` only. **L3 diagnostics** and **L4
external profiles** (`samply`, macOS `sample`, Linux `perf`) explain CPU
composition and visible GC pauses, but their elapsed time is not headline
timing.

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
| Checked Rift | Checked APIs are fast for simple append/window shapes and direct epoch shapes. Page-token, direct Dataflow epoch, Yak direct epoch, RegionList, GH Archive-shaped q1/q2, and generated Common Crawl-shaped q1/q2 clear useful gates; rank/table containers and the older generic `EpochFold` still add too much CPU overhead. |
| Safe checked backend | `checked-region-scoped` is the best page-token backend in the clean final-selection sweep. It is fastest on focused page-token append and generated Common Crawl-shaped q1/q2. |
| Real-input stream evidence | Yak `graphreal` over SNAP LiveJournal is now the strongest real-input prior-work-shaped region win. In the latest clean committed 50M rerun, `gc-heap` is `2958.659 ms` with `400.484 ms` timed GC and `3.91 GB` RSS. Per-epoch region rows remove timed GC and use about `2.11 GB` RSS: `region-scoped-rooted` is `2351.582 ms`, `region-stream-rootless` is `2499.975 ms`, `checked-epoch-scoped` is `2008.320 ms`, and `checked-epoch-stream` is `2064.867 ms`. Page-token checked rows still beat heap (`2586.919/2746.897 ms`) but are the wrong topology for Yak. AskUbuntu `topwordreal` adds a real text/top-word row: checked direct epoch scoped is `7.16 s`, `174 MB` RSS at 20M tokens x5 versus heap `7.77 s`, `986 MB`; L2 removes `33.471 ms` median timed heap GC. The same AskUbuntu row now has a true `streaming-file` variant that scans `Posts.xml` during the benchmark instead of preloading token arrays: at 1M tokens, checked epoch scoped is median L1 `0.91 s`, RSS `13.0 MB`, versus heap `0.96 s`, RSS `39.6 MB`; L2 removes only `3.677 ms` heap GC, so this is modest real-streaming-input RSS/fixed-memory evidence. GH Archive byte-slice file-backed q1/q2, LogHub BGL/HDFS/Spark/Windows q1/q2/q3/top-template rows, DSPBench Fraud q2, DSPBench Log q2, and Theodolite power q2 remain real-input modest/control candidates. GH Archive now has L1 final-clean confirmation on two hourly files / 200k events: checked scoped page-token q1 is `12.89 s`, `101 MB` RSS vs heap `13.17 s`, `265 MB`; q2 is `12.87 s`, `102 MB` RSS vs heap `13.18 s`, `244 MB`. HDFS v1 q2 now has both L2 and L1 evidence: L2 checked scoped page-token is `7871.856 ms` vs `gc-heap` `8227.369 ms`, removing `gc-heap`'s `92.659 ms` median GC; L1 checked scoped page-token is an elapsed tie (`25.56 s` vs heap `25.60 s`) but cuts max RSS to about `79 MB` from heap's `409 MB`. HDFS top templates is the strongest real LogHub retained-object row: reusable checked `EpochTopKByKey` is `18.26 s`, `92 MB` RSS at 5M x5 versus retained heap `19.04 s`, `504 MB`, and L2 removes `62.421 ms` timed heap GC. Spark and Windows top templates confirm the same reusable top-k shape over larger real LogHub datasets: at 5M lines x3 they remove `128.140 ms` and `122.440 ms` median timed GC respectively and win the L2 loop, but L1 is only modestly faster and RSS is not consistently better. Richer Windows q3 and Spark q3 template/session rows are negative/modest controls: checked page-token cuts timed GC and Spark q3 cuts RSS, but the rows are parser/query dominated and do not become flagship GC-heavy evidence. DSPBench Fraud q2 now also has L1: checked scoped page-token is a large RSS win (`59.5 MB` vs heap `358 MB`) but a slight elapsed loss (`4.44 s` vs heap `4.39 s`), while `region-stream-rootless` is fastest (`4.18 s`). DSPBench Log q2 has an L1 checked page-token modest elapsed/RSS win (`8.79 s`, `47.6 MB` vs heap `8.89 s`, `308 MB`) and the L2 row cuts max GC from `88.210 ms` to `18.584 ms`. Theodolite's byte-parser streaming q2 row is now cleaner than the earlier `String.split` row and has a handle-backed checked-stream follow-up: optimized `checked-epoch-stream` is L1 `3.80 s`, RSS `15.9 MB`, versus heap `4.33 s`, RSS `75.3 MB`; L2 optimized checked stream is `993.191 ms`, GC `0 ms`, versus heap `1054.432 ms`, GC `19.906 ms`. RIoTBench/MHEALTH is zero-GC/ceiling evidence. These are useful real-input rows; Yak LiveJournal is the first strong real-input prior-work-shaped row, but it remains local graph replay rather than exact Yak/GraphChi artifact evidence. |
| Real streaming-input replay | This class is now started. LogHub HDFS top templates has `LOGHUB_TOP_INPUT_MODE=streaming-file`, which streams real HDFS log lines inside each run without parsed total-input arrays. At 1M lines, reusable checked scoped `EpochTopKByKey` is L1 `8.06 s`, RSS `12 MB`, versus retained heap/drop-anchor `8.10 s`, RSS `76 MB`; L2 removes `32.681 ms` heap GC. GH Archive q1/q2 also has explicit `streaming-file` rows with modest checked page-token wins and max-GC-tail removal. Theodolite q2 now adds a byte-cursor time-series streaming row: optimized checked epoch stream is L1 `3.80 s`, RSS `15.9 MB`, versus heap `4.33 s`, RSS `75.3 MB`; L2 removes heap timed GC (`19.906 ms`) and improves modestly over the legacy checked stream path. LogHub HDFS q3 template/session has now been rerun as true streaming-file replay: checked page-token cuts RSS from about `862 MB` to `130 MB` and reduces max GC tail, but loses throughput (`30.29 s` vs heap `26.88 s`). Treat these as retained/RSS/fixed-memory streaming evidence; after parser allocation is controlled, the real stream rows are not huge-GC flagships. |
| Strongest memory-pressure row | Generated Common Crawl WET-shaped q1/q2 creates heavy stream object churn. After open allocation, heap spends `1.7/1.6 s` timed GC on q1/q2. Checked scoped page-token is fastest in the rerun (`3707.214 ms` q1, `3902.795 ms` q2), followed by checked Rift page-token (`3933.900 ms` q1, `4040.310 ms` q2). |
| Real-input search direction | The search is tracked in `evidence/REAL_INPUT_BENCHMARK_SEARCH.md`. Yak `graphreal` over SNAP LiveJournal is now the top prior-work-shaped real-input ladder row, and AskUbuntu `topwordreal` is the first real text/top-word follow-up. The new AskUbuntu `streaming-file` row confirms bounded file replay but also confirms that XML/text scanning can dominate when heap GC is small. LogHub HDFS top-template streaming remains the best true streaming retained/top-k row; richer HDFS q3 streaming confirms an RSS win but not an elapsed win. Next adjacent targets are larger Stack Exchange/StackOverflow text if disk/time allow, SNAP Twitter-2010 only if disk/time allow, Theodolite/energy variants with retained windows, and public text/security NDJSON streams that naturally materialize retained objects. DSPBench Spike, Fraud, and Log Processing q0/q1/q2 are implemented; LogHub BGL, HDFS, Spark, and Windows q1/q2/q3/top-template variants have been tried; RIoTBench/MHEALTH q1/q2 has been tried; Theodolite UC2/UC4-style q1/q2 has been tried over the real UCI power trace and parked as modest/control evidence. |
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
- NEXMark Beam-default selected rows now have L1 final-clean confirmation:
  q3/q8/q9/q11 checked `5.86/9.21/15.03/4.36 s` for 20 x 1M events versus
  heap `6.18/9.54/16.27/4.47 s` and improved SafeZone
  `6.38/10.13/18.10/5.11 s`.
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
- Direct checked epoch is the best StreamFlex shape so far. In L1 final-clean
  timing, checked scoped direct epoch throughput is `0.58 s` for 20 x 200k
  events versus heap `0.79 s` and improved SafeZone `0.77 s`; latency is
  `0.17 s` versus heap `0.18 s`, with heap deadline misses `4` and checked
  misses `0`. `TransactionRegion` remains a useful multi-list API, but it is
  no longer the best StreamFlex headline row.
- The StreamIt BeamFormer/FilterBank track is now started as a StreamFlex-axis
  control. The initial local ports are based on public StreamIt sources and
  report throughput, p95/p99/p999/max latency, deadline misses, RSS, and GC.
  The 3-run L1 control matrix is now complete: heap `15.00 s`, checked scoped
  `15.23 s`, checked stream `15.56 s`. The 3-run L2 rows show FilterBank
  throughput tied around `406 ms` with zero GC, while BeamFormer latency is
  about `3.28 s` with only `22 ms` heap GC.
  They are not memory-management wins yet because faithful BeamFormer/FilterBank
  are primitive DSP kernels rather than retained object-stream workloads.
- `StreamFlexDesignMatrix` is now the Rift-native StreamFlex system-design
  reproduction: stable state on heap, transient packet/feature/decision/alert
  objects in per-period epochs, and a bounded primitive capsule that exports
  values without retaining transient object references. First L1 throughput
  rows at 1M events x3 show checked scoped `1.27 s`, `7.9 MB` RSS versus heap
  `1.52 s`, `12.4 MB`; L2 pressure-latency shows checked scoped fastest
  (`192.432 ms` vs heap-same-shape `202.148 ms`) while checked stream gives
  the best tail/deadline row (`0` misses, max `20875 ns`).
- `evidence/STREAMFLEX_GAP_ANALYSIS.md` explains why this is not yet a
  StreamFlex-scale speedup. On the 1M L2 throughput row, heap spends
  `69-100 ms` of `477-509 ms` in timed GC, so the best possible speedup from
  removing only median GC is about `1.17-1.25x`; checked scoped reaches about
  `1.13-1.20x`. The remaining gap is therefore mostly non-GC work:
  allocation lowering, object construction, linked-object traversal, primitive
  capsule export, and the fact that this is not the original Ovm/StreamFlex
  scheduler/capsule runtime.
- The 2026-05-12 `/usr/bin/sample` profiles confirm this interpretation:
  checked scoped samples are split across `processCheckedPeriod`, stable-state
  query work, SafeZone-backed allocation/zeroing, and capsule add/drain, while
  heap samples show the same query floor plus Immix allocation/object-metadata
  paths. The next StreamFlex-specific optimization should target transient
  object layout/count, allocation zeroing/alignment, and linked traversal or a
  closer capsule runtime, with same-shape heap controls.
- NEXMark Beam-default is broadly favorable but modest. The L1 selected rows
  now show checked q3/q8/q9/q11 at `5.86/9.21/15.03/4.36 s` versus heap
  `6.18/9.54/16.27/4.47 s`; q9 is the strongest selected row at about `7.6%`
  faster than heap and lower RSS.
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
| Modest throughput win | Correct row is faster, but margin is below the representative gate or the workload is not broad enough. | NEXMark Q8, real WET/WAT page-token controls. |
| RSS win | Region row materially lowers resident memory even if elapsed is tied or slightly worse. | ReML-shaped `msort`/`ratio`, `CheckedWindowFold` style rows. |
| Fixed-memory / tail win | Uncapped heap is competitive by growing large, but under a heap cap or in max-GC/tail runs regions improve completion or tails. | GH Archive q1 under `1G` heap cap. |
| Speed-gated operator | Correct API has some GC/RSS benefit, but CPU overhead is too high for public performance claims. | `EpochFold`, `StreamWindowFold`, `TableRank`. |
| Negative/ceiling | Heap is fastest and there is no material GC/RSS/tail benefit at the measured scale. | Pipeline surrogate, current Wikimedia/Linear Road rows. |

Throughput and latency are different axes. Throughput asks how much total work
finishes per unit time; in batch-style matrices we approximate it with elapsed
time, where lower elapsed means higher throughput. Latency asks how long an
individual event/request waits; p50/p95/max latency and deadline misses can
improve even when average throughput changes only modestly, or worsen even when
throughput improves. StreamFlex is the current example: the L1 direct-epoch row
improves throughput and removes heap deadline misses, while earlier
TransactionRegion rows showed why the chosen framework topology matters.

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
| Active/open checked allocation handles | Internal slice implemented | `OpenStreamingRegion` is allocation-capable and lowered to the unchecked allocation path; direct user close/reset is now rejected so lifecycle stays owned by epoch/page/window helpers. |
| Mixed-reference rules | Partial | Static/immutable heap metadata and explicit `HeapRoot` supported, including through the open allocation path; full root-free SafeZone policy is not proven. |
| Checked stream operators | Partial | AppendWindow/cursor works; Join/Fold/Rank/TableRank exist but many fail performance gates. |
| Checked SafeZone-backed backend | Implemented as benchmark prototype | `RiftRegion.streamingSafeZone(...)`; object allocation/close supported, raw allocation/reset unsupported. |
| Canonical benchmark labels | Implemented for key matrices | Checked AppendWindow and Common Crawl WET-shaped runners accept new names and old aliases. |
| Cheap checked operator families | Started | `PageTokenMapFilter`, `RegionList`, `EpochBuffer`, and `TransactionRegion` are now real reusable APIs with passing safety probes. In the latest staged sweep, scoped checked append operators remain fast (`26.461 ms` scoped EpochBuffer, `26.883 ms` scoped page-token vs heap `36.944 ms`). Direct `RiftRegion.epoch` supersedes `TransactionRegion` for the current StreamFlex headline because all stage objects share one batch lifetime; `TransactionRegion` stays as a multi-list API for shapes direct epoch cannot express cleanly. `EpochFold` is implemented and correct but failed the Dataflow AGGREGATE speed gate (`92.923 ms`). |
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
| Dataflow SELECT | L1 direct `checked-epoch-stream` `15.5 ms/iter`; checked scoped `17.5 ms/iter` | L1 heap `30.5 ms/iter`; L2 heap GC previously material | handle-backed direct epoch is reusable across all Dataflow operators |
| Dataflow AGGREGATE | L1 direct `checked-epoch-stream` `30.5 ms/iter`; checked scoped `32.5 ms/iter`; generic `EpochFold` remains gated | L1 heap `59.0 ms/iter`; L2 heap GC previously material | direct epoch is the reusable win; `EpochFold` is still a negative control |
| Dataflow JOIN | L1 direct `checked-epoch-stream` `15.5 ms/iter`; checked scoped `18.5 ms/iter` | L1 heap `28.0 ms/iter`; L2 heap GC previously material | handle-backed direct epoch beats heap and rooted scoped in the current L1 sweep |
| StreamFlex throughput | scoped direct checked epoch `157.334 ms`; trusted Streaming `186.029 ms` | `216.853 ms` / `46.036 ms` GC | direct epoch is now the right checked shape for the StreamFlex batch pipeline; `TransactionRegion` is superseded on this row |
| Stancu transaction boundary | scoped direct checked epoch `155.863 ms`; direct checked epoch `165.116 ms` | `220.951 ms` / `22.819 ms` GC | direct epoch is now the checked Stancu-shaped win; durable accounting arrays stay heap control metadata |
| SPECjbb2005-workload port | L1 8 warehouses x20: checked epoch scoped `2.21 s`; L2 checked epoch scoped `108.649 ms` | L1 heap `2.64 s`; L2 heap `129.674 ms` / `15.125 ms` GC | clean-room Scala Native port, not official SPEC; reproduces Stancu-style transaction-local lifetime axes |
| Object allocation lowering | checked SafeZone-backed `14.903 ms`, checked Rift `16.039 ms` | `21.885 ms` | focused allocation path is not the main bottleneck now |
| Checked append/window | checked scoped EpochBuffer `26.461 ms`, checked scoped page-token `26.883 ms` | heap Immix `36.944 ms` / `10.900 ms` GC | cheap checked append operators beat heap |
| Page-token fast path | checked scoped page-token `27.549 ms`; checked Rift page-token `29.319 ms` | heap `36.920 ms` / `10.995 ms` GC | batch-close/current-bucket fast path keeps linked page-token ahead of chunk-token |
| StreamWindowRank | checked `344.918 ms` | `227.736 ms` | rank/index maintenance remains negative |
| NEXMark Beam-default | L1 checked q3/q8/q9/q11 `5.86/9.21/15.03/4.36 s` | L1 heap `6.18/9.54/16.27/4.47 s`; improved SafeZone `6.38/10.13/18.10/5.11 s` | broad generated methodology win, mostly modest; not exact Beam runner evidence |
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
| Stancu transaction boundary | `225.798 ms` | improved `186.122 ms` | scoped direct checked epoch `160.198 ms`; direct checked epoch `174.137 ms` | Direct checked epoch turns the local Stancu-shaped row into a checked win. |
| SPECjbb2005-workload port, 8 warehouses | L1 `2.64 s`; L2 `129.674 ms` | L1 rooted scoped `2.48 s`; L2 rooted scoped `122.022 ms` | L1 scoped direct checked epoch `2.21 s`; L2 scoped direct checked epoch `108.649 ms`; stream direct checked epoch `114.651 ms` | New clean-room port extends the Stancu transaction-lifetime story; not official SPEC output. |

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

Source: `evidence/REML_MLKIT_PLDI_TABLE.md`,
`evidence/REML_COMPARISON_MATRIX.md`, and `docs/REML_COMPARISON_PLAN.md`.

This is a new comparison track, not a stream benchmark. It matters because the
MLKit/ReML lineage stresses region polymorphism, higher-order programs, and
tracing-GC safety when region values can be hidden by polymorphic types.

| Evidence class | Current status | Claim boundary |
|---|---|---|
| Paper-reported ReML table | Elsman 2023 Figure 9 is transcribed into tracked evidence. | Literature anchor only; not local measurement. |
| Exact artifact rerun | Gated/low-priority. Current MLKit HEAD was inspected and contains many benchmark sources, but paper-era source/configuration and local `mlkit`/`mlton` toolchain runs are not pinned. Host `mlkit`/`mlton` are missing, and Docker is installed but the daemon is not running. | Resume only if we need raw same-machine "Rift beats ReML" timing; otherwise compare paper axes plus local Scala Native ratios/RSS/GC/safety burden. |
| Scala Native ports | `ReMLRegionMatrix` has Tier 1 medians for `fib37`, `tak`, `mandel`, `msort`, `msort-r`, `life`, `fft`, and `ratio`, plus first Tier 2 rows for `logic`, `ray`, and `tsp`. | Valid for local Rift-vs-Scala-Native ratios, not exact ReML reproduction. |
| Safety probes | ReML-inspired compiler probes now include local polymorphic use, generic identity escape, generic heap-cell durable retention, widened `AnyRef`, heap arrays, closure hiding, and unrooted heap metadata. | The previous erased-generic gap is fixed at the current durable/static-retention probe level. Broader heap alias analysis remains open. |

Tier 1 interpretation:

| Workload | Best local checked row | Heap row | Current meaning |
|---|---:|---:|---|
| `msort` | checked stream `104.358 ms`, RSS `10.4 MB` | `124.983 ms`, RSS `21.4 MB`, GC `27.180 ms` | allocation/RSS win on a linked-node sort shape. |
| `msort-r` | checked stream `104.929 ms`, RSS `10.4 MB` | `126.163 ms`, RSS `39.2 MB`, GC `27.280 ms` | allocation/RSS win on reverse-input linked sort. |
| `ratio` | checked scoped `48.929 ms`, RSS `16.0 MB`, GC `0` | `51.302 ms`, RSS `44.0 MB`, GC `3.191 ms` | modest elapsed win and strong RSS/GC reduction. |
| `fib37`/`tak`/`mandel`/`life` | small or noisy differences | heap has no material GC | compute/control rows, not memory-management evidence. |

Tier 2 interpretation:

| Workload | Best local checked/rooted row | Heap row | Current meaning |
|---|---:|---:|---|
| `logic` | checked stream L1 `1.27 s`, RSS `65.6 MB`; L2 GC `1.288 ms` | L1 `1.27 s`, RSS `7.9 MB`; L2 GC `6.705 ms` | elapsed tie but large region RSS regression; whole-region chain is a control/negative row. |
| `ray` | rooted scoped L1 `0.74 s`, RSS `4.1 MB` | L1 `0.75 s`, RSS `4.1 MB` | near-tie compute/control row; no material GC. |
| `tsp` | checked scoped L1 `3.48 s`, RSS `5.9 MB`; L2 GC `0 ms` | L1 `3.40 s`, RSS `7.9 MB`; L2 GC `0.339 ms` | RSS win with small elapsed loss; heap GC is too small for a throughput claim. |

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
| `EpochBuffer` | focused epoch append/drain and Yak LiveJournal `graphreal` | focused heap epoch `27.164 ms`, GC `5.707 ms`; Yak 50M heap rerun `1514.313 ms`, GC `279.226 ms` | focused checked Rift `26.673 ms`; focused scoped checked `25.448 ms`; Yak 50M scoped reusable `EpochBuffer` `1343.071 ms` | Focused gate passes and Yak integration beats heap/RSS, but reusable `EpochBuffer` trails benchmark-local linked epoch (`1022.643 ms`). Next target: lower reusable `epoch` to a linked epoch fast path. |
| `EpochBuffer` in StreamFlex | StreamFlex 200k throughput | heap `42.504 ms`; improved SafeZone `40.224 ms`; Rift Streaming `36.357 ms` | checked Rift `47.462 ms`; scoped checked `44.504 ms` | Correct but negative. Stacking four independent epoch buffers per batch pays too much lifecycle/operator overhead; it motivated shared-lifetime operators. |
| `TransactionRegion` in StreamFlex | StreamFlex throughput | older heap `42.860 ms`; improved SafeZone `41.327 ms`; Rift HP `36.436 ms` | checked Rift `45.620 ms`; scoped checked `39.019 ms`; later 1M scoped transaction `205.929 ms` | Partial win and useful multi-list control, but superseded for this benchmark by direct checked epoch. |
| Direct checked epoch in StreamFlex | StreamFlex 1M throughput | heap `218.582 ms`, improved SafeZone `208.653 ms`, trusted Streaming `182.246 ms` | checked stream epoch `185.550 ms`; scoped checked epoch `163.339 ms` | Representative checked StreamFlex-shaped win. A single checked epoch block with ordinary linked objects is better than both `EpochBuffer` and `TransactionRegion` when all stage objects share one batch lifetime. |
| Direct checked epoch in Stancu | Stancu 1M transactions, 64 tx/epoch | heap `225.798 ms`, improved SafeZone `186.122 ms`, trusted Streaming `219.668 ms` | checked stream epoch `174.137 ms`; scoped checked epoch `160.198 ms` | Representative checked transaction-boundary win. Transaction line/order objects live in the epoch; stock/revenue/customer arrays remain heap metadata. |

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
| StreamFlex TransactionRegion | checked Rift `45.620 ms`; SafeZone-backed checked `39.019 ms`; later 1M scoped transaction `205.929 ms` | heap `42.860 ms`; improved SafeZone `41.327 ms`; Rift HP `36.436 ms` | Useful multi-list control, but no longer the best checked StreamFlex-shaped row after direct epoch. |
| StreamFlex direct epoch | checked stream `185.550 ms`; checked scoped `163.339 ms` at 1M | heap `218.582 ms`; improved SafeZone `208.653 ms`; trusted Streaming `182.246 ms` | Gate passes for this shape. Direct epoch should be preferred when all temporary stream-stage objects share the same epoch lifetime. |
| Fixed-chunk append | checked chunk-token `34.273 ms`; SafeZone-backed chunk-token `33.108 ms` | page-token `28.452 ms`; SafeZone-backed page-token `27.214 ms`; heap chunk `45.363 ms` | Correct but failed; chunk allocation/control overhead outweighs saved link writes in this sequential append/drain shape. |
| Object allocation lowering | checked Rift `165.774 ms`; checked SafeZone-backed `143.319 ms`; trusted HP `199.627 ms` at 10M | heap `271.121 ms`, GC median `105.807 ms`, RSS `971 MB` | Allocation/reclaim win at scale; prior checked gap was mostly generic `RegionBuffer` retention overhead. |
| WindowFold additive | checked `118.726 ms` | heap `103.244 ms` | Failed; checked aggregate overhead. |
| StreamWindowRank long-key | checked-long `503.906 ms` | heap-long `358.988 ms` | Failed; rank/container overhead. |
| StreamWindowTableRank | table-long `568.572 ms` | heap-long `437.702 ms` | Failed; gated out of DEBS. |

### Stream And Application Rows

| Workload | Input | Heap | Best SafeZone-family | Best Rift / checked | Interpretation |
|---|---|---:|---:|---:|---|
| NEXMark Q3 | Beam-default generated | L1 `6.18 s`, RSS `75 MB` | improved `6.38 s`, RSS `9.8 MB` | checked `5.86 s`, RSS `9.6 MB` | L1 checked generated methodology win; below 10% gate. |
| NEXMark Q8 | Beam-default generated | L1 `9.54 s`, RSS `75 MB` | improved `10.13 s`, RSS `10 MB` | checked `9.21 s`, RSS `10 MB` | L1 checked modest elapsed/RSS win. |
| NEXMark Q9 | Beam-default generated | L1 `16.27 s`, RSS `147 MB` | improved `18.10 s`, RSS `14 MB` | checked `15.03 s`, RSS `13 MB` | Strongest selected NEXMark L1 row. |
| NEXMark Q11 | Beam-default generated | L1 `4.47 s`, RSS `75 MB` | improved `5.11 s`, RSS `15 MB` | checked `4.36 s`, RSS `14 MB` | L1 checked modest elapsed/RSS win. |
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
| GH Archive q1 fields | real file-backed NDJSON, 2 hourly files, byte-slice parser | L2 200k heap `3806.120 ms`, median GC `57.685 ms`, RSS `290 MB`; L1 heap `13.17 s`, RSS `265 MB` for 3 q1 iterations | L1 improved-32k `13.10 s`, RSS `101 MB` | L2 Streaming `3626.219 ms`, RSS `211 MB`; L2 SafeZone-backed page-token `3629.193 ms`, RSS `211 MB`; L1 checked scoped page-token `12.89 s`, RSS `101 MB` | Byte-slice parser-scratch makes q1 a modest real-input throughput/RSS/tail win. L1 confirms the direction with clean external timing/RSS; L2 shows heap collects in 2/3 runs and region rows report zero timed GC. Not GC-heavy: heap GC is about `1.5%` of elapsed. |
| GH Archive q2 repo window | real preloaded NDJSON | 8-hour oracle 1M heap `271.880 ms`, max GC `136.353 ms` | improved-32k `363.049 ms` | Streaming `325.665 ms`; SafeZone-backed page-token `347.033 ms` | Heap median wins; repo-window aggregation CPU dominates despite a GC outlier. |
| GH Archive q2 repo window | real file-backed NDJSON | 100k heap `3995.632 ms`, median GC `158.277 ms`, RSS `1.22 GB`; `1G` cap fails with signal 11 | improved-32k `3934.094 ms`, RSS `672.1 MB` | Streaming `3906.291 ms`, RSS `673.6 MB`; SafeZone-backed page-token `3921.127 ms`, RSS `673.8 MB` | With parsing timed, q2 becomes a modest region/RSS/fixed-memory win; parser/string allocation still causes GC in region rows. |
| GH Archive q2 repo window | real file-backed NDJSON, 2 hourly files, legacy string parser | 200k heap `7641.540 ms`, median GC `199.876 ms`, RSS `2.43 GB` | not rerun in this subset | Streaming `7442.005 ms`, RSS `724.8 MB`; SafeZone-backed page-token `7498.263 ms`, RSS `925.6 MB` | Legacy parser row: Streaming modestly wins elapsed and strongly wins RSS; checked scoped page-token is near-tied. |
| GH Archive q2 repo window | real file-backed NDJSON, 2 hourly files, byte-slice parser | L2 200k heap `3756.950 ms`, median GC `61.625 ms`, RSS `290 MB`; L1 heap `13.18 s`, RSS `244 MB` for 3 q2 iterations | L1 improved-32k `12.90 s`, RSS `102 MB` | L2 Streaming `3645.458 ms`, RSS `211 MB`; L2 SafeZone-backed page-token `3626.107 ms`, RSS `211 MB`; L1 checked scoped page-token `12.87 s`, RSS `102 MB` | Byte-slice parser-scratch turns q2 into a modest checked scoped page-token win with zero timed GC in region rows. L1 confirms a modest elapsed/RSS win; not GC-heavy because heap GC is about `1.6%` of elapsed. |
| LogHub BGL q1 tokens | real file-backed BGL system log | 1M heap `5568.252 ms`, median GC `99.271 ms`, RSS `408 MB`; 256M heap cap `5807.256 ms`, median GC `194.609 ms` | improved-32k `5589.860 ms`, RSS `358 MB` | Streaming `5491.033 ms`, RSS `358 MB`; checked scoped page-token `5552.988 ms`, RSS `476 MB` | Real log stream modest win/control: heap GC appears in every 1M run but remains only about 1.8% of elapsed. Trusted Streaming wins modestly and reduces RSS; checked scoped page-token is near-tied but high-RSS in this row. |
| LogHub BGL q2 window counts | real file-backed BGL system log | 1M heap `5646.824 ms`, median GC `157.198 ms`, RSS `409 MB`; full-file q2 heap `32161.391 ms`, GC `595.599 ms`, RSS `576 MB` | 1M improved-32k `5509.481 ms`; full-file improved-32k `31459.104 ms`, RSS `490 MB` | 1M Streaming `5605.787 ms`; full-file Streaming `30899.595 ms`; full-file checked scoped page-token `31165.087 ms`, RSS `491 MB` | Full-file q2 is a real-input modest throughput/RSS/tail win for region rows, but heap GC is still under 2% of elapsed, so it is not the missing huge-GC case. |
| LogHub BGL q3 template/session | real file-backed BGL system log | 1M heap `8683.558 ms`, median GC `84.166 ms`, max GC `117.946 ms`, RSS `290 MB` | improved-32k `8635.167 ms`, RSS `237 MB` | Streaming `8615.627 ms`, RSS `237 MB`; checked scoped page-token `8722.008 ms`, RSS `237 MB` | Richer real log query with template/session objects. Regions cut RSS/tails, but checked scoped loses elapsed and heap GC is under 1% of elapsed. |
| LogHub HDFS v1 q2 window counts | real file-backed HDFS log | L2 1M heap `8227.369 ms`, median GC `92.659 ms`, RSS `409 MB`; L1 heap `25.60 s`, RSS `409 MB` for 3 q2 iterations | L2 improved-32k `7924.213 ms`, RSS `395 MB`; L1 improved-32k `25.35 s`, RSS `79 MB` | L2 Streaming `7871.713 ms`, RSS `356 MB`; L2 checked scoped page-token `7871.856 ms`, RSS `395 MB`; L1 checked scoped page-token `25.56 s`, RSS `79 MB` | Strongest HDFS page/window row: L1 elapsed tie plus large RSS win; L2 gives modest checked throughput/GC interpretation. Heap GC is still only about 1-2% of elapsed. |
| LogHub HDFS top templates | real file-backed/preloaded HDFS log | 5M x5 L1 retained heap `19.04 s`, RSS `504 MB`; L2 heap `463.633 ms`, GC `62.421 ms` | not a SafeZone-only row | checked scoped `EpochTopKByKey` 5M x5 L1 `18.26 s`, RSS `92 MB`; L2 checked `402.916 ms`, GC `0 ms` | Strongest real retained top-k row: modest L1 throughput win, large RSS win, and L2 timed-GC removal using a reusable checked API. Heap GC is still modest relative to elapsed, so this is retained-object/RSS evidence, not a huge-GC flagship. |
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
| DSPBench Fraud q2 | `rift-checked-safezone-page-token`; `rift-trusted-streaming` as lower bound | Transaction, prediction, state-token, and alert records are allocated in page/window buckets. | Real DSPBench `credit-card.dat`, `185000` rows replayed to 1M events. | Heap spends `69.686 ms` median GC in L2, but L1 checked elapsed is slightly slower than heap. | Transaction/prediction/alert records in regions; predictor state on heap/primitive arrays. | Real-input checked RSS win and trusted lower-bound elapsed win; not checked throughput headline. |
| DSPBench Log q2 | `rift-checked-safezone-page-token` | Common-log records, status/update records, and window contributions are allocated in checked page-token buckets. | Real DSPBench `http-server.log`, `55000` common-log lines replayed to 1M events. | Heap spends `44.992 ms` median GC and has an `88.210 ms` max-GC tail in L2, about `2.6%` of elapsed. L1 checked is `8.79 s` vs heap `8.89 s`. | Log/status/window contribution records in regions; status counters and input replay state on heap/primitive arrays. | Real-input modest throughput/RSS/GC-tail control; not a flagship case. |
| NEXMark Q3/Q8/Q9/Q11 | `rift-checked-rift` | Checked region APIs on generated Beam-default methodology streams. | Generated NEXMark profile. | Moderate object/window pressure; L1 margins are `2.5-7.6%` faster than heap, with much lower RSS. | Event/window records in regions where checked operator exists; durable tables/counters on heap. | Generated methodology win; not real-input proof or exact Beam runner evidence. |
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
| 4 | More real text/log/NDJSON streams | AskUbuntu text is a real checked-epoch win; LogHub BGL/HDFS/Spark/Windows and GH Archive are modest wins but not GC-heavy. | Scale to larger Stack Exchange/StackOverflow text if feasible; try Thunderbird logs, GDELT, or security logs only if they materialize more per-record objects than the current line/template paths. |
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
   Tier 1 and the first Tier 2 local shaped-port rows now exist. Next, pin the
   exact MLKit/ReML artifact or build environment and verify the paper's
   `rg`/`rg-`/`r` command mapping. Additional Tier 2 ports should be added only
   when they map clearly to the paper sources. Keep exact ReML artifact search
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
