# Rift Roadmap

Last updated: 2026-05-16 16:45 CEST

Status: revised from the active fork state, benchmark notes, handoff, and the
literature-review comparison contract.

Latest report/HTML normalization:
`docs/PERFORMANCE_EVALUATION_REPORT.md` is the normalized narrative source for
presentation and `docs/report.html` is generated from it. The current report
now foregrounds natural heap/GC versus checked Rift, separates best safe
backend rows from mechanism controls, includes a prior-work metric-axis table
in the Markdown source and generated HTML, and fixes topology-atlas
wrapping/responsiveness. Future report edits should
update the Markdown source, regenerate HTML, and keep same-shape retained,
legacy checked, unsafe/rootless, and summary-only rows in appendix/control
sections unless they are the explicit object of a mechanism claim.
The parent evaluation runner now includes Broom retained dataflow in the
`prior` suite and as a standalone `broom` suite.
`evidence/PRIOR_WORK_HEADLINE_SWEEP_2026_05_16.md` records the first clean
headline-scale parent `prior` run after that integration. Treat it as L2
runner/interpretation evidence. The next final sweep should move to normalized
selected matrices instead of relying only on the older `prior` suite.
That selected path is now implemented as `RIFT_EVAL_SUITES=selected-prior`.
The dirty-patch smoke at `/private/tmp/rift-eval-selected-prior-smoke-20260516`
passed across Broom, Dataflow, StreamFlexDesign, Yak local direct-epoch rows,
and SPECjbb2005 port. The next step is a clean headline-scale
`selected-prior` run.
The clean headline run is now recorded in
`evidence/SELECTED_PRIOR_WORK_SWEEP_2026_05_16.md`; it should supersede the
older parent `prior` suite for presentation-facing generated/local methodology
rows. Next sweep target: apply the same normalized selected-runner discipline
to streams and real-input rows.
That selected stream path is now implemented as
`RIFT_EVAL_SUITES=selected-streams`, covering Common Crawl page-token q1/q2,
NEXMark q3/q8/q9/q11, GH Archive q1/q2, LogHub q2/q3 and top-template rows,
and DSPBench Fraud/Log q2. Theodolite power q2 is opt-in because the matrix
requires the real `household_power_consumption.txt` trace through
`THEODOLITE_POWER_INPUT`. The suite uses natural heap, best safe backend, and
checked Rift topology rows by default; controls remain behind
`RIFT_EVAL_INCLUDE_CONTROLS=1`. Dirty-runner smoke passed at
`/private/tmp/rift-eval-selected-streams-smoke2-20260516` with no failed rows
across Common Crawl, NEXMark, GH Archive, LogHub, and DSPBench; Theodolite was
skipped as intended because the real trace path was unset. Next: commit the
runner and run a clean headline selected-streams sweep for presentation
evidence. That clean selected-streams sweep is now recorded in
`evidence/SELECTED_STREAMS_SWEEP_2026_05_16.md` from parent `46c4ea8` and child
`15c4c39ac`, with no failed rows. It should be the current generated/default
stream/application presentation source. The opt-in Theodolite q2 row has now
been filled as a selected-row addendum over the local real UCI household-power
trace: `checked-epoch-stream` is `4.58 s` versus heap `5.13 s`, removes
`19.465 ms` median timed heap GC, and has slightly higher RSS, so it is a
real-streaming throughput/GC control rather than an RSS win.

Latest all-optimizations selected sweep:
`evidence/ALL_OPTIMIZATIONS_SELECTED_SWEEP.md` records the 2026-05-16 compact
L1/L2 check for the optimized checked defaults. The current result supports
continuing backend-known checked allocation as the best near-term optimization:
optimized checked direct epoch, page-token, and retained epoch all beat their
legacy generic checked controls on L1 elapsed while keeping checksums/output
matched. Next optimization work should audit any remaining generic allocation
paths and then move to constructor/field-store and traversal/capsule
simplification; do not spend more time on region reuse policies unless a row
specifically exposes slab reuse as the bottleneck.

Latest Broom retained-dataflow update:
Child implementation commit: `15c4c39ac`
(`Add Broom scoped backend comparison`), building on `9ec2fa95d`
(`Add Broom retained dataflow benchmark`).
`evidence/BROOM_RETAINED_DATAFLOW_MATRIX.md` adds a local Broom/Naiad-style
timestamped dataflow benchmark that follows the prior-work headline style:
natural heap/GC versus checked Rift. Aggregate and join retain ordinary
records in per-timestamp dictionaries until notification/close, so this is not
a summary-only loop. The latest 20M rerun adds `checked-region-scoped` as the
best-safe-region/backend comparison row. The 20M aggregate row is heap
`5.27 s`, RSS `75.8 MB`, L2 GC `410.002 ms`, versus checked Rift `3.59 s`,
RSS `13.6 MB`, GC `0 ms`, and checked scoped `4.55 s`, RSS `13.7 MB`; 20M
join is heap `5.00 s`, RSS `74.7 MB`, L2 GC `267.636 ms`, versus checked
Rift `4.26 s`, RSS `12.8 MB`, GC `0 ms`, and checked scoped `4.52 s`,
RSS `13.0 MB`. The 1M active-16 variant confirms
the high-live-state direction: heap RSS `232-239 MB`, checked RSS `53-56 MB`,
and checked Rift is `24-33%` faster. The high-active heap-cap follow-up
completes at `256M` but fails at `128M` and `64M`, while checked Rift
completes with matching checksum/output at about `53-56 MB` total RSS. This
should become the first Broom-style GC-heavy dataflow case study. Next:
add 1M/5M checked scoped rows only if the presentation needs the full safe
backend scale curve; keep retained heap/drop-anchor controls in appendix for
causality, not as the headline comparison.

Latest GC-heavy benchmark investigation:
`evidence/GC_HEAVY_BENCHMARK_INVESTIGATION.md` records the 2026-05-15
literature and online follow-up. The conclusion changes the real-input search
priority: streaming-file replay is necessary for stream claims, but it is not
sufficient for GC pressure. The next promising candidates are retained-object
workloads: Broom-like joins/aggregates/session dictionaries, StreamFlex-style
event-correlation/transaction/IDS latency rows, Yak-scale graph/text epochs,
Spark/Flink-like high-cardinality keyed state, heap-state time-series windows,
and Stancu/SPECjbb-style transaction batches. Rows that only read more bytes
and update compact counters should remain ceiling/control evidence unless they
show RSS, tail, fixed-memory, or material GC pressure.

Latest throughput/RSS reuse-policy update:
Child implementation commit: `70672972c`
(`Add Rift region reuse policies`). Parent evidence/report commit: the commit
containing this roadmap update.

The child runtime now implements `RIFT_REGION_REUSE_POLICY` with `default`,
`bulk-zero-retained`, `cache-small`, `cache-large`, and `prezero-large`.
`RIFT_ZERO_REUSED_SLABS=1` remains an alias for
`bulk-zero-retained`. Default behavior stays memory-conservative; the cache
policies are opt-in throughput/RSS tradeoff modes. Focused 10M
`ObjectAllocationLoweringMatrix` shows `cache-large` as the best current
policy (`149.609 -> 130.250 ms`, region-op time `17.445 -> 0.894 ms`, similar
RSS and matching checksum). The first StreamFlexDesign 1M L1/L2 smoke is
neutral after rerun, so this is not yet a broad application win. Next policy
work should run selected application gates and only promote a throughput policy
if at least two representative L1 rows improve without correctness changes.
The first selected application follow-up is now recorded in
`evidence/REGION_REUSE_POLICY_MATRIX.md`: Dataflow AGGREGATE and generated
Common Crawl-shaped q2 are neutral under the canonical policies, so the policy
track should pause unless a future workload specifically exposes slab reuse as
the bottleneck. Keep `cache-large` as a focused allocator control.

Latest remaining-path audit update:
Yak `graphreal` `checked-epoch-stream` now uses backend-known open-handle
allocation for epoch-local `EdgeUpdate` objects; `checked-epoch-stream-legacy`
keeps the old generic allocation path as a control. The 10M LiveJournal
same-binary gate improves checked stream `290.539 -> 279.469 ms` with matching
checksum/RSS and puts the stream row roughly even with checked scoped
(`280.801 ms`). Child `3ee2fc173` extends the audit to GH Archive checked
page-token: the default `rift-checked-page-token` now uses the backend-known
Rift open-handle path, with `rift-checked-page-token-legacy` as the old generic
allocation control. The generated/preloaded 1M L2 transfer gate improves q1
`316.947 -> 299.512 ms` and q2 `317.997 -> 298.186 ms` with matching checksums
and identical object/open/close counts. Continue the allocation-path audit only
for rows where profiles still show allocation lowering is material. The latest
follow-up promotes LogHub top-template `checked-epoch-retained-no-traverse` to
the open-handle epoch path with
`checked-epoch-retained-no-traverse-legacy` as the old generic allocation
control. Generated/preloaded 1M improves `291.519 -> 269.309 ms`; a real HDFS
streaming-file 100k sanity row is neutral (`273.834 -> 275.054 ms`), so this is
transfer evidence rather than a new real-input headline. Leave reusable
`EpochTopKByKey` scoped rows as the report-facing LogHub API result.
Child `3aa045af4` extends the same audit to the local Stancu transaction
matrix. The default `rift-checked-direct-epoch` now uses backend-known
open-handle allocation, while `rift-checked-direct-epoch-legacy` keeps the old
generic checked path. The 200k transaction gate improves checked direct epoch
`29.687 -> 28.554 ms` with matching checksum and removes heap's `4.837 ms`
median timed GC; checked SafeZone direct epoch remains fastest at `26.405 ms`.
Keep this as allocation-lowering transfer evidence and continue using the
SPECjbb2005-workload port for the report-facing Stancu/SPECjbb row.
Child `308867063` adds the same open-handle control to LogHub page-token rows,
but does not promote it to the default. At 1M generated q2/q3,
`rift-checked-page-token-open-handle` is only modestly faster than legacy
(`548.894/2310.891 ms` versus `558.582/2357.261 ms`), and the better
generated/indexable topology is still direct epoch. Keep this as an
appendix/control row unless a future page-token workload shows a larger win.

Latest handle-backed allocation checkpoint:
- child implementation commit: `1a1c45c75` (`Promote handle-backed checked allocation`)
- parent evidence/report commit: `17148ea` (`Record handle-backed allocation evidence`)

Latest proof-gated no-zero update:
Child implementation commit: `1ee5bf491`
(`Add proof-gated no-zero lowering`). Parent evidence/report commit: the
commit containing this roadmap update.

Normal `RiftOpenStreamingHandle` allocation now uses no-zero allocation only
when the lowerer proves a local definitely-initialized record shape: concrete
non-module class, no reachable subclasses, primitive instance fields, and all
fields stored before first object use/control-flow exit/non-pure operation.
Focused `ObjectAllocationLoweringMatrix` results show the proved normal path
reaches the unsafe lower-bound ceiling: 5M improves from the pre-proof
`71.320 ms` to `65.528 ms`, and 10M improves from `155.947 ms` to
`139.832 ms`, with matching checksums and all allocations zero-skipped. The
first focused page-token sanity gate remains positive: promoted checked
page-token is `24.975 ms`, legacy checked page-token is `26.495 ms`, and heap
is `35.918 ms` at 1M. The first application transfer gates are also positive:
Dataflow optimized checked stream beats legacy checked stream on
SELECT/AGGREGATE/JOIN (`18.141/33.574/17.669 ms` versus
`22.523/36.711/20.202 ms`) and removes heap's `6.630-11.195 ms` median timed
GC; StreamFlexDesign final-clean throughput at 20M events x3 is heap
`29.04 s`, optimized checked stream `19.91 s`, legacy checked stream
`22.19 s`, and checked scoped `23.57 s`. Next work should broaden the proof
carefully to reference fields only when GC visibility is proven safe, then
rerun selected page/window and real-streaming gates.

Latest reference-field no-zero proof update:
the proof has now been broadened to definitely initialized reference-field
records allocated through `RiftOpenStreamingHandle`. The safety boundary is
still narrow: concrete/non-module/no-subclass classes only, every field stored
before first object use/control-flow exit/non-pure operation, and Rift-backed
open handles only. The GC argument relies on Rift slabs not being scanned as
roots while checked region safety separately rejects unsafe heap-region
references. Focused 5M linked reference records now put normal checked
open-handle allocation at the unsafe no-zero ceiling (`66.249 ms` versus
`66.177 ms`), with all `5,000,001` region objects zero-skipped and matching
checksum. Primitive-shape regression stays positive (`63.303 ms` at 5M).
StreamFlexDesign linked-object transfer remains positive versus heap/legacy
but does not show a fresh application win. The selected follow-up gates are now
recorded: generated Common Crawl-shaped q1/q2 keeps promoted
`rift-checked-page-token` ahead of legacy (`3590.874/3589.017 ms` versus
`3938.596/3961.363 ms`) and ahead of heap (`5501.961/5286.428 ms`) by removing
about `1.58-1.59 s` of timed heap GC, while Theodolite real streaming q2 keeps
optimized `checked-epoch-stream` modestly ahead of heap (`952.664 ms` versus
`988.976 ms`) and legacy (`963.018 ms`). These are transfer/stability gates:
Common Crawl remains generated and not an RSS win, and Theodolite remains
parser/query dominated. Next optimization should target remaining non-zeroing
costs: constructor/field-store lowering, query/traversal/capsule CPU, and
root-free scoped checks only after mixed-reference probes pass.

Five-optimization closure status, 2026-05-16:
the current evidence-driven optimization pass is closed as follows. Safe
backend-known allocation and proof-gated no-zero are implemented for
Rift-backed open-handle paths where the lowerer proves definite
initialization; a fresh reference-record gate reports normal checked
open-handle `67.109 ms`, unsafe no-zero `69.435 ms`, checked SafeZone-backed
`72.053 ms`, and heap `311.085 ms`, with all checked open-handle objects
zero-skipped and matching checksum. Constructor and field semantics remain
intact; arrays, `this` escape, subclassable/module classes, impure operations,
and unproven control flow keep the normal zeroing path. Cursor/capsule
simplification and same-shape summaries are done only inside reusable
operator/topology APIs. Root-free checked scoped remains future work until
mixed-reference rejection and a real benchmark row both exist.

Latest unsafe no-zero lower-bound update:
Child implementation commit: `c5fb808a7`
(`Add unsafe no-zero allocation lower-bound`). Parent evidence/report commit:
the commit containing this roadmap update.

`ObjectAllocationLoweringMatrix` now has
`rift-checked-rift-open-handle-nozero-unsafe`, an explicit unsafe lower-bound
mode that skips object-body zeroing after writing the object RTTI/header word.
This is not a checked/default optimization. It measures the ceiling for future
compiler-proven no-zero lowering. Focused 5M gates improve normal
handle-backed checked Rift `71.320 ms -> 65.196 ms`; 10M gates improve
`155.947 ms -> 142.769 ms`, with matching checksums and unchanged RSS. This
puts compiler proof of definite initialization back at the top of the low-level
optimization list. Required proof obligations before any safe/default use:
final record-like class, all fields definitely assigned before escape, no
virtual call or `this` escape during construction, superclass fields handled,
and arrays excluded.

Latest reusable-slab bulk-zero update:
`RIFT_ZERO_REUSED_SLABS=1` is now an experimental Rift runtime policy that
bulk-zeros dead non-huge slabs at region close/reset before caching them for
reuse. It is safe because it preserves zero-filled allocation semantics; it
does not skip initialization based on compiler proof. Focused
`ObjectAllocationLoweringMatrix` gates show a promising tradeoff:
handle-backed checked Rift improves from `68.692 ms` to `65.228 ms` at 5M
objects and from `144.067 ms` to `138.078 ms` at 10M objects, while RSS and
checksums are unchanged. The cost moves into region op time (`2.153 -> 4.121`
ms at 5M, `10.813 -> 13.817` ms at 10M), so this remains experimental until
more application gates show it is broadly favorable. The first two gates are
positive: StreamFlexDesign throughput 20M x3 improves `19.51 s -> 18.91 s`,
and generated Common Crawl-shaped q2 1M x3 improves `10.00 s -> 9.22 s`,
with matching checksum/output and unchanged RSS. L2 makes the cost transfer
explicit: StreamFlexDesign region op time rises `23.563 -> 254.858 ms`, and
Common Crawl q2 rises `9.640 -> 68.771 ms`. The real Theodolite streaming q2
gate is throughput-positive (`3.94 s -> 3.60 s`) but RSS-negative
(`15,908,864 -> 24,870,912` bytes). Keep this as a workload-selective
experimental knob until more real streaming rows confirm the tradeoff.
Rejected follow-up: child `f2116677e` records a high-water prefix-zeroing
prototype that was reverted. The transition-only version still failed the
focused 5M gate (`69.619 ms` enabled, worse than the accepted full-slab
bulk-zero `65.228 ms`). Next zeroing policy work should test coarser knobs
such as TLS-cache-only zeroing or RSS-aware cache release, or move to
compiler-proven no-zero.
Rejected follow-up: child `7750778f1` records a TLS/local-only zeroing
prototype that was also reverted. It avoided global-pool page touches, but the
focused 5M gate was worse than both default and full bulk-zeroing (`72.339 ms`
local-only versus `71.834 ms` default and `68.614 ms` full bulk-zero). This
shows the current allocation row gets most of the skip-zero benefit from
global-pool reuse, so TLS-only is too narrow. Prefer RSS-aware cold-slab
release or compiler-proven no-zero next.
Rejected follow-up: child `41d9c95cc` records a runtime global-pool-cap
prototype that was also reverted. Lowering the reusable pool cap while using
full bulk-zeroing introduced mmap/unmap churn in the focused allocator row and
did not materially reduce Theodolite q2 RSS. Static pool-cap release is
therefore too blunt. Next work should move to compiler-proven no-zero, or only
revisit RSS release with a more precise untouched-page/madvise design and a row
where RSS is demonstrably the blocker.

Latest all-optimizations evaluation update:
the current child working tree adds a focused warm/dirty-slab measurement mode
for handle-backed checked allocation and refreshes the main all-optimizations
gates. At 5M focused allocations, handle-backed checked Rift is `69.422 ms`
versus current checked Rift `78.557 ms`; the warm/dirty-slab probe is
`67.128 ms` but is not a no-zero claim because pool warmup is mixed into the
setup. Application gates now show promoted defaults clearly beating legacy:
StreamFlexDesign 20M throughput default `checked-epoch-stream` is `19.25 s`
versus legacy `21.32 s` and heap `30.90 s`; generated Common Crawl q2 default
`rift-checked-page-token` is `9.76 s` versus legacy `11.06 s` and heap
`16.23 s`; focused append-window default is `23.059 ms` versus legacy
`24.687 ms` and heap `38.352 ms`. A quick SPECjbb/Stancu-style
4-warehouse gate preserves the transaction topology direction with checked
epoch stream `0.18 s`, checked scoped epoch `0.19 s`, rooted scoped `0.21 s`,
and heap `0.51 s`. Next optimization work should either fold handle-backed
allocation into remaining epoch-shaped matrices where profiles show allocation
lowering is material, or build a lower-level fresh/dirty zeroing probe before
considering any compiler-proven no-zero prototype.

Latest remaining-path allocation-lowering update:
the SPECjbb/Stancu-style `checked-epoch-stream` path now follows the same
backend-known handle-backed lowering used by Dataflow and StreamFlex. The old
generic checked path is retained as `checked-epoch-stream-legacy`; the explicit
`checked-epoch-stream-open-handle` row remains as provenance. At 4 warehouses x
100k transactions, 5-run L1 reports optimized checked stream `0.27 s` versus
legacy `0.30 s`, checked scoped `0.31 s`, rooted scoped `0.34 s`, and heap
`0.64 s`. L2 medians are optimized `51.168 ms`, legacy `56.371 ms`, checked
scoped `54.146 ms`, rooted scoped `60.347 ms`, and heap `67.378 ms` with
`7.635 ms` GC.

Latest real-streaming allocation-lowering update:
Theodolite real power q2 `streaming-file` now has the same handle-backed
checked stream lowering. At 1M records x3, L1 reports optimized
`checked-epoch-stream` `3.80 s` versus legacy `3.83 s`, checked scoped
`3.83 s`, rooted scoped `3.90 s`, and heap `4.33 s`. L2 reports optimized
`993.191 ms` versus legacy `1006.176 ms`, checked scoped `995.167 ms`, rooted
scoped `1009.541 ms`, and heap `1054.432 ms` with `19.906 ms` GC. Treat this
as a modest positive remaining-path audit result and continue the audit on
Yak/NEXMark only where profiles show generic checked allocation is still
material.

Latest generated LogHub allocation-lowering update:
`LogHubRegionMatrix` direct-epoch q2/q3 now has the same handle-backed checked
Rift lowering, with `rift-checked-direct-epoch-legacy` retained as the generic
allocator control. At 1M generated/indexable log lines, optimized checked
direct epoch is `192.452 ms` on q2 and `1794.369 ms` on q3. Legacy checked
direct epoch is `222.544/1837.885 ms`, checked scoped direct epoch is
`222.620/1869.150 ms`, and heap is `542.854/2161.937 ms` with
`143.713/140.570 ms` timed GC. This is positive transfer evidence for the
general allocation-lowering audit, but it remains generated/indexable evidence
rather than real streaming-input proof.

Latest zeroing attribution update:
The object-initialization/zeroing target now has a diagnostic counter instead
of a guess. Rift allocation stats record managed object allocations that call
`memset` and those that skip zeroing on fresh zeroed slabs; final-clean runs
still keep these counters disabled. At 5M objects x5 in
`ObjectAllocationLoweringMatrix`, handle-backed checked Rift reports
`4,198,392` zeroed objects (`134,348,544` bytes) and `801,608` zero-skipped
objects (`25,651,456` bytes), with median `70.197 ms`. This confirms zeroing
is a material remaining allocation-body cost, but it is not a no-zero claim.
Next work should either add compiler proof for definite initialization of
final record-like classes, or find a runtime policy that improves the
zeroed/skipped ratio without increasing slab attach/reset cost.

Latest streaming-input follow-up:
Checkpoint commits before the latest working-tree row: child `79b1a6ec2`,
parent `289f8ee`.
Child `7660e54e4` adds `LOGHUB_INPUT_MODE=streaming-file` to
`LogHubRegionMatrix` and records the first richer HDFS q3 template/session
streaming-input row. The row is useful as RSS/fixed-memory and GC-tail control
evidence: checked scoped page-token cuts L1 RSS from heap's `862 MB` to
`130 MB` and reduces L2 max GC from `131.533 ms` to `58.455 ms`, but loses
L1 elapsed (`30.29 s` versus heap `26.88 s`). Keep it parked unless heap caps
or a more naturally retained session workload expose stronger pressure.
Child `5f8ab6145` adds `YAK_TEXT_INPUT_MODE=streaming-file` for
`YakRegionMatrix topwordreal`. The 1M AskUbuntu streaming-file row consumes
`Posts.xml` during the benchmark with no full token replay array: checked
epoch scoped is median L1 `0.91 s`, RSS `13.0 MB`, versus heap `0.96 s`, RSS
`39.6 MB`; L2 removes only `3.677 ms` heap GC. Keep this as modest
real-streaming-input RSS/fixed-memory evidence and continue the search for a
stream workload with material retained-object GC pressure.
`GithubArchiveRegionMatrix` now has an explicit `streaming-file` input mode
for real GH Archive gzip NDJSON replay. The 100k q1/q2 triage gives checked
page-token modest elapsed/RSS wins and removes the observed heap max-GC tails,
but median heap GC remains zero, so this is a real-streaming-input
RSS/tail/control row rather than a flagship GC-heavy stream result.
Child `22a0f9f4c` adds `THEODOLITE_POWER_INPUT_MODE=streaming-file` to
`TheodolitePowerRegionMatrix`; child `ad9f84a07` extends that with a shared
byte-line/semicolon byte-field parser. At 1M real UCI power q2 records,
checked scoped epoch is L1 `3.77 s`, RSS `24.9 MB`, versus heap `3.87 s`,
RSS `75.3 MB`; L2 is `967.144 ms`, GC `0`, versus heap `1007.030 ms`,
GC `19.932 ms`. This supersedes the earlier `String.split` streaming row,
which inflated parser allocation and heap GC. The current row is cleaner
real-streaming throughput/RSS/fixed-memory evidence, but not a huge-GC
flagship.

Latest prior-work interpretation update:
`docs/PRIOR_WORK_MEMORY_MANAGEMENT_INTERPRETATION.md` now captures the
principled lesson from Broom, Yak, StreamFlex, Stancu et al., and ReML/MLKit.
The main Rift goal should stay framed as regions versus GC: expose safe
epoch/page/window/transaction lifetimes so the runtime avoids tracing,
promotion, close-time scans, and unnecessary bookkeeping for temporary data.
Reusable operators remain important when they expose those lifetimes, but they
are not the root contribution by themselves.
The same doc now records design vocabulary to borrow cautiously: active/closed
regions, nested-region state, immutable/static metadata, bridge/root handles,
and reference-capability-style ownership. These should be added to the public
API only when they remove measured runtime work or simplify the proof story.

Latest evidence-normalization update:
`evidence/EVALUATION_CLASSIFIED_SUMMARY.md` now audits every representative
presentation row for L1, L2, input type, topology/API, comparison class, and
allowed claim. `evidence/REML_MLKIT_PLDI_TABLE.md` now has both the raw PLDI
Figure 9 metric columns and a same-metric local table that appends Scala
Native/Rift time, RSS, and L2 GC interpretation columns for available ports.
Exact MLKit/ReML reruns stay deferred; the immediate ReML deliverable is
explaining local Scala Native ratios and why Rift wins, loses, or is
unavailable on each paper row.

Latest profiling update:
child `e1f140c0a` completes the representative L4 profile harness cases. The
coverage now includes StreamFlex-design, generated Common Crawl-shaped q2,
DSPBench Fraud q2, LogHub HDFS/Spark/Windows top-k, Theodolite power q2,
StreamIt controls, Yak LiveJournal graph replay, AskUbuntu top-word, Dataflow
AGGREGATE, NEXMark Q8/Q9, SPECjbb2005-workload including a larger transaction
row, ReML Tier 1/Tier 2 shaped ports, and a generated Yak `graphstep` profile
case to isolate epoch-body CPU. The sweep is recorded in
`evidence/PROFILE_SWEEP_MATRIX.md` and `docs/CPU_PROFILE_REPORT.md`. It confirms
that real text/log/time-series rows are parser/hash/string dominated, generic
`EpochFold` is slow because of table/probe/cursor/allocator/stat/`checkOpen`
costs, NEXMark Q8/Q9 are operator/indexing-heavy, StreamIt and ReML
`ray`/`tsp`/`ratio` are compute controls, and Yak graphstep remains the most
actionable allocation-body profile. ReML `logic` adds a port-shape caveat:
checked region nodes do not remove heap GC if the hot loop still allocates heap
scratch arrays.

Latest allocator optimization update:
child `9ee340950` completes the first profile-guided zone allocator cleanup:
cache `MemoryPool_page_size()` in each opened `Zone` and make the allocator's
pad-to-8 calculation a macro instead of a sampled helper call. This is a narrow
response to the Yak graphstep samples in `MemoryPool_page_size`, `Util_pad`,
`scalanative_zone_pad8`, and `scalanative_zone_alloc`; it does not skip zeroing
or change object layout. The normal validation gate now passes:
`sandbox3_next/compile`, `RiftRegionCheckedCompilerTest` (`141/141`), and
`RiftRegionCheckedTest` (`64/64`, rerun after the macro change). The
post-change Yak graphstep L4 profile confirms the intended cleanup:
`MemoryPool_page_size`, `Util_pad`, and `scalanative_zone_pad8` are no longer
sampled; remaining checked scoped cost is allocator body, mandatory zeroing,
and SafeZone-backed `allocUncheckedImpl` wrappers.

Latest allocator timing update:
child `be79f93f2` adds the post-cleanup focused graphstep timing rows to
`evidence/YAK_REGION_MATRIX.md`. The 10M checked scoped graphstep row improves
from the previous `181.341 ms` to `167.164 ms`, and the 50M profile-scale row
keeps checked scoped fastest among safe modes (`1710.128 ms` L2,
`9.57 s` L1 external) versus heap (`2276.697 ms`, `12.25 s`) and rooted scoped
(`1746.292 ms`, `9.76 s`). Next low-level backend work should target
allocation lowering/object construction/zeroing rather than page-size or
padding helpers.

Latest allocation-stat cleanup:
child `593346af2` disables Rift raw/object/byte allocation counters
automatically under `RIFT_FINAL_CLEAN=1`, with `RIFT_ALLOC_STATS=1` as an
explicit diagnostic override. The focused 5M `ObjectAllocationLoweringMatrix`
gate for `rift-checked-rift` improved from `87.999 ms` with counters forced on
to `76.345 ms` with final-clean counters disabled, same checksum and zero GC.
This is a measurement-clean/headline-mode optimization, not a replacement for
L2 stats rows.
The first application impact gate confirms the effect on some Rift-native
stream rows: StreamFlex-design `checked-epoch-stream` improves from `9.18 s`
to `8.57 s`, and generated Common Crawl-shaped q2 `rift-checked-page-token`
improves from `4.33 s` to `4.23 s`. Dataflow AGGREGATE and Yak graphstep are
too noisy at the single-process gate scale, so do not present this as a
universal application-speedup claim.

Latest region-cached stats cleanup:
child `450465743` caches allocation-stats mode per Rift region, removing
`scalanative_rift_alloc_stats_enabled` from the sampled final-clean winner
profiles while preserving `RIFT_ALLOC_STATS=1` diagnostics. This is a modest
application cleanup, not a focused allocation win: the 5M object-allocation row
is `71.702 ms` versus the earlier object-fast `69.912 ms`, while page-token
checked Rift improves `25.007 -> 24.618 ms`, StreamFlexDesign checked stream
`22.81 -> 22.55 s`, and generated Common Crawl-shaped q2 checked Rift
`11.49 -> 11.39 s`. Next low-level work should target object construction,
mandatory zeroing, allocation-body code shape, and same-shape operator summaries
rather than more stats/check-open cleanup.

Latest allocation-body cleanup:
child `126e2950b` caches the current slab's zeroed/dirty state on each Rift
region. This preserves the existing zeroing policy but removes a per-object
current-slab flag load before the `_platform_memset` decision. It is a measured
allocation-body win: focused 5M checked Rift allocation improves to
`68.998 ms` from the earlier object-fast `69.912 ms` and cached-stats
`71.702 ms`; page-token checked Rift improves `24.618 -> 23.930 ms`;
StreamFlexDesign checked stream improves `22.55 -> 22.31 s`; generated
Common Crawl-shaped q2 checked Rift improves `11.39 -> 11.17 s`. This confirms
that small allocator-body cleanup can still matter, but the remaining hard
targets are object construction/field initialization, mandatory zeroing on
dirty slabs, and reducing required traversal through reusable same-shape APIs.

Latest optimization-literature pass:
`docs/OPTIMIZATION_LITERATURE_NOTES.md` now records the next tuning work against
Blackburn-style zeroing and managed-runtime methodology, HotSpot TLAB/escape
analysis practice, GC lower-bound-overhead evaluation, StreamFlex latency
lessons, and reference-capability/active-region design ideas. The next runtime
experiments should follow that checklist: do not skip zeroing globally; only
consider no-zero or allocation-elision when compiler proof covers definite
initialization and nonescape; move checked allocation toward a backend-known
TLAB-like bump fast path; classify summary-only traversal avoidance as
topology/operator evidence; and report latency/RSS/fixed-memory wins separately
from throughput.

Latest rejected allocation-body experiment:
the post-current-slab-zeroed L4 sweep in
`/Users/siyaoliu/rift/cache/profile-post-slab-zeroed-20260513-escalated`
confirms that allocation/zeroing is still visible, but the first obvious
C-level branch split was rejected. Splitting stats-disabled and stats-enabled
object allocation helpers improved the focused 5M checked Rift row to
`68.561 ms`, but page-token and StreamFlexDesign application gates regressed
against the accepted current-slab zeroed-cache rows. This narrows the next
target: do not keep reshuffling C branches; instead investigate a
backend-known compiler lowering path or a narrow compiler-proven initialization
optimization.

Latest backend-known allocation prototype result:
the first marker-trait approach was rejected and reverted. It showed that
backend-specific open-region marker types are not enough to make allocation
lowering safe and fast: overloads made generic checked code ambiguous, and the
narrow direct-open mode crashed. The next viable design should be lower-level:
either add an explicit NIR/compiler intrinsic that carries the backend/handle
to the allocation lowering, or refactor open-region handles so generated code
can call a handle-level fast path directly without dynamic `allocUncheckedImpl`
method lookup.

Focused handle-level allocation result:
the explicit handle-level direction now has a positive focused gate. A
Rift-only experimental open handle lowers directly to
`scalanative_rift_region_alloc` in NIR. The 5M allocation matrix reports
`59.777 ms` for `rift-checked-rift-open-handle`, compared with `70.247 ms` for
the current checked path in the same binary and `68.998 ms` for the accepted
current-slab zeroed-cache baseline. `RiftRegionCheckedCompilerTest` (`141/141`)
and `RiftRegionCheckedTest` (`64/64`) pass. Next milestone: make this a
compiler-owned internal lowering for checked epoch/page-token APIs, keep
generic/public APIs defensive, and rerun StreamFlex-design, Common
Crawl-shaped q2, and focused page-token gates before promoting it.

The first StreamFlex-design application gate is also positive. Experimental
`checked-epoch-stream-open-handle` preserves the StreamFlex period/reset
topology but lowers transient allocations through the handle path. Same-binary
L1 gates: 2M events `1.09 s -> 0.67 s`; 20M events `7.27 s -> 6.60 s`, with
matching checksum/output and lower RSS. This moves the handle-level path from
focused-only evidence to candidate application evidence. Remaining promotion
work: make the lowering compiler-owned behind the normal checked API, run L2
interpretation rows, and test page/window-token rows.

Clean 3-run L1 follow-up: 20M StreamFlexDesign throughput now reports
`checked-epoch-stream-open-handle` at `19.69 s` and `12550144` RSS, versus
`checked-epoch-stream` at `22.57 s` and `12615680` RSS, with the same checksum
and output count. This is a `12.8%` improvement over the current checked stream
row and keeps the handle-level path as the next compiler-owned lowering target.

Promotion follow-up: the handle-backed path is now the default
`checked-epoch-stream` implementation in `StreamFlexDesignMatrix`; the old
open-region lowering is `checked-epoch-stream-legacy`, and the explicit
`checked-epoch-stream-open-handle` label remains only as a provenance alias.
The 20M L1 gate reports legacy `22.68 s`, promoted default `21.01 s`, and
open-handle alias `20.79 s`, all with matching checksum/output. L2 reports
legacy `8776.217 ms` versus promoted default `8096.514 ms`, with the same
`499999119` region objects and `78125` resets. This completes the first
normal-label promotion for checked epoch stream lowering; next promotions
should target other checked epoch/page operators only where profiles show
allocation lowering is material.

Generated Common Crawl-shaped q2 now provides the corresponding page/window
gate. `rift-checked-page-token-open-handle` keeps the normal page-token
topology but lowers active-bucket record allocation through the handle path.
At 1M generated pages, L1 improves from current checked page-token `10.62 s`
to `9.66 s` with matching checksum/output and near-identical RSS; L2 median
time improves from `3883.742 ms` to `3695.704 ms` with identical region-object
and open/close counts. This means the backend-known allocation target is no
longer StreamFlex-specific. Next work should make the handle owner an internal
compiler lowering detail for checked epoch/page-token APIs, not a benchmark
mode users choose explicitly.

Promotion follow-up: the default `rift-checked-page-token` row now uses the
handle-backed Rift page-token path, while the old open-region lowering is
preserved as `rift-checked-page-token-legacy`. On generated Common
Crawl-shaped q2 at 1M pages, the promoted default row is `10.59 s` L1 versus
legacy `11.18 s`, with matching checksum/output and identical L1 RSS. L2
median time is `3562.617 ms` versus legacy `3909.015 ms`, with identical
region-object and open/close counts. The next optimization target remains
making this lowering a general compiler-owned internal path for other
operator-owned checked APIs.

Focused page-token follow-up: `CheckedAppendWindowMatrix` now uses the
handle-backed path for the default `rift-checked-page-token` row and keeps
`rift-checked-page-token-legacy` as the old open-region control. Focused 1M
results are legacy `23.913 ms`, promoted default `22.785 ms`, and checked
SafeZone page-token `25.520 ms`, all with matching checksum and zero GC. This
confirms the promotion in the focused operator gate; next rows to migrate are
application matrices that still call `pageTokenAppendOpenRegionFor` directly
and have a Rift-backed checked mode.

DSPBench Fraud q2 now has the same promoted default row. The real-file 1M L1
gate reports `rift-checked-page-token-legacy` at `2.63 s`, promoted
`rift-checked-page-token` at `2.60 s`, and SafeZone-backed checked page-token
at `2.78 s`, with matching checksum/output and about `59 MB` RSS for all three
rows. The L2 medians are noise-tied (`863.329/867.751/857.657 ms`), with the
promoted row only reducing measured Rift op time slightly (`0.613 -> 0.559 ms`)
and leaving object/open/close counts unchanged. Use this as an application
sanity gate for handle-backed page-token lowering, not as a new real-input
GC-heavy win. The next optimizer target is still lowering/object construction
where profiles show it matters, while real-input StreamFlex/streaming evidence
continues separately.

Dataflow handle-backed allocation gate:
`DataflowRegionMatrix` now promotes handle-backed checked allocation for the
full direct-epoch `checked-epoch-stream` family. The previous AGGREGATE crash
was a region-owned array allocation issue: Scala Native arrays lower through
`Array.alloc(length, zone: SafeZone)`, so the internal `RiftOpenStreamingHandle`
now satisfies the allocation-only `SafeZone` contract and routes `allocImpl`
directly to the Rift allocator. A 2k smoke matched SELECT/AGGREGATE/JOIN
checksums for legacy/default/open-handle rows. The 10 epochs x 100k L2 gate
reports legacy versus promoted default: SELECT `18.956 -> 17.178 ms`,
AGGREGATE `36.888 -> 33.551 ms`, and JOIN `20.270 -> 19.133 ms`, all with
matching checksums and zero GC. The matching 3-process L1 final-clean control
rerun reports promoted `checked-epoch-stream` at SELECT/AGGREGATE/JOIN
`15.5/30.5/15.5 ms` per iteration, versus heap `30.5/59.0/28.0 ms`, rooted
scoped `22.0/39.0/22.0 ms`, and checked scoped epoch `17.5/32.5/18.5 ms`.
This closes the current handle-array blocker with L1 headline timing plus L2
interpretation.
Validation for the current dirty checkpoint: `sandbox3_next/compile` passed,
compiler checked-region probes passed `141/141`, runtime checked-region tests
passed `65/65`, and parent/child `git diff --check` passed.

Latest allocation-lowering update:
child `b0e1bc232` specializes Rift managed-object allocation with a
pointer-aligned fast path that bypasses the generic raw-allocation alignment
normalizer for ordinary managed objects. It keeps slab refill, zero/init, and
object header semantics unchanged. The focused 5M `ObjectAllocationLoweringMatrix`
`rift-checked-rift` row improves from the previous final-clean `76.345 ms` to
`69.912 ms`, with matching checksum and zero GC. The forced-stats row is
`89.081 ms`, so allocation statistics remain L2 interpretation overhead rather
than headline timing. Single-run application gates also move:
StreamFlex-design checked stream `8.57 s -> 8.07 s`; generated Common
Crawl-shaped checked page-token q2 `4.23 s -> 3.98 s`. This is the clearest
next optimization target completed after profiling: reduce allocation lowering
overhead before touching benchmark-specific algorithms.

Latest open-allocation update:
child `c22c78d57` removes the final-class superclass wrapper from
`OpenStreamingRegion.allocUncheckedImpl`. Operator-owned `allocOpen` now calls
the Rift or SafeZone allocator directly in the final concrete open-region
classes; public defensive allocation remains unchanged. Validation passes:
`sandbox3_next/compile`, `RiftRegionCheckedCompilerTest` (`141/141`), and
`RiftRegionCheckedTest` (`64/64`). Focused final-clean 1M page-token rows are
`24.665 ms` checked Rift and `24.816 ms` checked SafeZone-backed. Application
impact is mixed but non-negative: StreamFlex-design checked stream improves in
the single-run gate (`8.07 s -> 7.72 s`), while generated Common Crawl-shaped
q2 is flat (`3.98 s -> 4.00 s`). The attempted dirty-slab bulk-zero policy was
rejected because it slightly regressed the 5M allocation row (`70.044 ms`
versus `69.912 ms`) and moved time into slab attach.

Latest clean-rerun update:
child `ca1978ef4` upgrades the open-allocation sanity gates into clean
final-clean evidence rows. Focused page-token 1M x5: heap `38.378 ms`,
checked Rift page-token `25.007 ms`, checked SafeZone-backed page-token
`25.591 ms`, all checksums matching. StreamFlexDesign 20M x3 L1:
heap `31.26 s`, checked scoped `24.39 s`, checked stream `22.81 s`.
Generated Common Crawl-shaped q1/q2 1M x3 L1: heap `17.49/16.73 s`, checked
Rift page-token `10.88/11.49 s`, checked SafeZone-backed page-token
`13.29/14.84 s`. Next optimization work should be guided by post-rerun L4
profiles rather than more speculative allocator policy changes.

Latest post-rerun profile update:
child `61944b487` updates the L4 harness with explicit clean-winner cases for
`streamflex-design-checked-stream` and `commoncrawl-q2-checked-rift`. The
profiles in
`/Users/siyaoliu/rift/cache/profile-post-rerun-20260512-clean-winners`
confirm that StreamFlexDesign checked stream is led by epoch-body work,
Rift allocation/object zeroing, stable-state classify/event updates, and
capsule add/drain; generated Common Crawl q2 checked page-token is led by
close cursor traversal, page-token append/linking, allocation/zeroing, and
token hashing. Both profiles still show `scalanative_rift_alloc_stats_enabled`
in final-clean allocation paths. Treat that as the next small runtime cleanup
candidate before larger object-construction/zeroing work; do not spend the next
pass on more bucket close/open bookkeeping unless a new profile contradicts
this.

Latest ReML priority decision:
Exact MLKit/ReML artifact reruns are now gated/low-priority. Keep the
paper-reported Figure 9 table and local Scala Native shaped-port columns as the
main deliverable. Only resume exact artifact reproduction if a same-machine raw
wall-clock comparison becomes necessary; otherwise compare relative
region-vs-heap ratios, RSS, GC, and safety/API burden.

Design-lesson backlog:

| Candidate | Runtime work it might remove | Gate before public API |
|---|---|---|
| Active/closed region typestate | hot-path `isOpen` and stale-token checks | internal probes now cover direct epoch, page-token append/map-filter/count-by-key, epoch buffer, and stale public page-token child regions; next gate is measured operator-owned payoff or a statically linear open-token API |
| Immutable/static metadata references | blanket root registration for durable read-only metadata | open-allocation compiler probes now cover direct epoch and operator-owned page/epoch-buffer paths; backend root-removal evidence still required |
| Bridge/root handles | conservative heap-region tracking and roots | `HeapRoot` is v1 bridge and is now covered on direct epoch and operator-owned page/epoch-buffer allocation paths; measure before broadening |
| StreamFlex-style latency reporting | none directly; exposes GC-tail wins | L2 latency rows must include throughput, p50, p95, max, misses, GC max, runs-with-GC |
| Stancu-style annotation/API burden | none directly; limits API complexity | representative burden counts tracked in `evidence/API_BURDEN_SUMMARY.md` |

Latest final-clean table update: retained L1 gaps are now filled for DSPBench
Fraud q2 and LogHub q2/q3, and the reusable LogHub HDFS `EpochTopKByKey` row
has a 5M x5 scale-up (`18.26 s`, `92 MB` RSS) against retained heap
(`19.04 s`, `504 MB` RSS). ReML/MLKit PLDI-style local Tier 1 combined rows now
use L1 timing/RSS rather than stale L2 elapsed; exact MLKit timing remains
toolchain/provenance-blocked.

Latest ReML/MLKit implementation update: child `d1fd16a64` adds the first
Tier 2 Scala Native shaped ports, `logic`, `ray`, and `tsp`, to
`ReMLRegionMatrix`. L1/L2 rows have now been collected and classified:
`logic` is an elapsed tie with a large region RSS regression, `ray` is a
near-tie control, and `tsp` is an RSS/control row with a small elapsed loss.
The next ReML step is exact MLKit artifact/toolchain reproduction or carefully
selected additional Tier 2 ports with clear paper-source mappings.

Latest real-input search update: LogHub Spark is now local from Zenodo record
`8196385` and recorded in `evidence/BENCHMARK_DATA_SOURCES.md`. The extracted
dataset has `3852` `.log` files and `33236604` total lines. First
`LogHubTopTemplatesMatrix` rows show the reusable checked `EpochTopKByKey`
path still removes heap GC on retained template objects: at 5M Spark lines x3,
retained heap has L2 `703.804 ms` with `128.140 ms` median GC, while checked
scoped top-k has L2 `579.440 ms` and GC `0 ms`. The L1 process row is only a
modest win (`16.63 s` versus `16.93 s`) and RSS is tied/slightly worse, so this
is retained top-k confirmation rather than a new flagship real-input claim.
LogHub Windows is now local from the same record as well: one `Windows.log`
file, `114608388` lines, `28012696901` bytes. Its 5M top-template row confirms
the same pattern: checked scoped top-k removes heap's `122.440 ms` median timed
GC and wins the L2 loop (`548.806 ms` versus `679.123 ms`), while L1 process
time improves modestly (`31.28 s` versus `32.37 s`) and RSS is tied/slightly
worse.
The richer Windows q3 template/session row is negative/control evidence: heap
L2 `17405.613 ms`, median GC `147.336 ms`, L1 `88.57 s`, RSS `408715264`;
checked scoped page-token L2 `17783.560 ms`, median GC `33.945 ms`, L1
`90.26 s`, RSS `445661184`. Do not tune this q3 shape unless a new reusable
operator changes the CPU profile.
The richer Spark q3 template/session row was also run over the
`application_1485248649253_0132` subset (`61` files, `1M` loaded lines). It
confirms the same control conclusion: checked scoped page-token is only
slightly faster in L2 (`7534.013 ms` versus heap `7602.328 ms`) and cuts L1 RSS
(`56 MB` versus heap `408 MB`), but heap timed GC is still only `140.934 ms`
or about `1.9%` of elapsed. Park Spark q3 as real-input modest/control
evidence, not a GC-heavy flagship.
Theodolite UC2/UC4-style local rows are now wired to the real UCI Household
Electric Power trace in `TheodolitePowerRegionMatrix`. This closes the
"Theodolite only has generated input" gap for a local methodology row, but the
result is still modest/control evidence. q1 downsampling has zero timed heap
GC. Full local q2 hierarchical aggregation loads `2049280` usable real
measurements and allocates one measurement plus three hierarchy contribution
records per input; heap is `287.296 ms` with `20.354 ms` median timed GC, while
`checked-epoch-scoped` is `288.495 ms` with zero timed GC and tied process
elapsed in strict L1 (`5.45 s` versus heap `5.46 s`) with slightly lower RSS.
Do not tune this as a flagship unless a larger/richer real power trace creates
material RSS/tail/fixed-memory pressure.

Latest streaming-input update: the evaluation protocol now has a stricter
`real-streaming-input` class for bounded replay that consumes records
incrementally and forbids parsed arrays/lists proportional to total input.
Child working tree after `0a042b920` adds
`LOGHUB_TOP_INPUT_MODE=streaming-file` to `LogHubTopTemplatesMatrix` through
`BenchmarkInputSupport.StreamingByteLineSource`. The first HDFS 1M row streams
the real log file inside each run: retained heap is L1 `8.10 s`, RSS `76 MB`,
while reusable checked scoped `EpochTopKByKey` is L1 `8.06 s`, RSS `12 MB`;
the L2 row removes `32.681 ms` median heap GC. Treat this as the first
streaming-input retained/RSS candidate, not as the missing GC-heavy flagship.
The 5M scale-up keeps the same classification: retained heap external
`66.63 s`, L2 `13244.113 ms`, median GC `109.535 ms`; checked scoped top-k
external `66.95 s`, L2 `13368.555 ms`, GC `0 ms`. Since heap GC is only about
`0.8%` of the streaming loop, larger HDFS line streaming remains
parser/query-bound ceiling evidence. RSS is missing from that sandboxed run and
needs an external rerun before presentation.
Next conversions should be StackExchange/StackOverflow text, SNAP/Yak edge
streams, richer LogHub session/template rows, and DSPBench Fraud/Log only if
retained pressure remains material.

Latest StreamIt/StreamFlex-axis update: child working tree now has
`StreamItKernelMatrix` and `sandbox/run_streamit_kernel_matrix.sh`, with local
ports of the public StreamIt FilterBank and BeamFormer kernels. The first smoke
validates heap versus checked scoped epoch checksums for throughput and
latency, including p95/p99/p999/max and deadline-miss metrics. Treat this as a
StreamFlex-axis methodology control: faithful primitive DSP kernels are not
expected to be GC-heavy Rift wins. The first 3-run L2 candidate confirms that
FilterBank is essentially zero-GC and BeamFormer remains compute/array
dominated. The clean 3-run L1 control matrix is now complete too: heap
`15.00 s`, checked scoped `15.23 s`, checked stream `15.56 s`. Only add
object-retained variants if we need a separate GC-pressure stressor.

Latest StreamFlex design-reproduction update: child `90c899644` now has
`StreamFlexDesignMatrix` and `sandbox/run_streamflex_design_matrix.sh`. This is
the Rift-native reproduction of StreamFlex's system design, separate from the
primitive BeamFormer/FilterBank controls: stable filter state stays on heap,
transient packet/feature/decision/alert objects live in per-period regions,
and a bounded capsule exports primitive alert values across the transient
boundary. First evidence is in `evidence/STREAMFLEX_DESIGN_MATRIX.md`: L1 1M
throughput has checked scoped `1.27 s` / `7.9 MB` RSS versus heap/same-shape
heap `1.52 s` / `12.4 MB`; L2 throughput removes heap's `100.234 ms` median
GC; L2 pressure-latency has checked scoped fastest and checked stream with
zero deadline misses. `evidence/STREAMFLEX_GAP_ANALYSIS.md` now records the
current gap to the original StreamFlex-style magnitude: checked scoped is close
to the GC-removal bound for this workload, so further gains require profiling
and reducing non-GC work such as allocation lowering, object construction,
linked traversal, capsule transfer overhead, and the missing VM/scheduler
integration. Next step is to profile this row and then decide whether a
retained-object BeamFormer/FilterBank variant or closer capsule runtime is
worthwhile.
The first `/usr/bin/sample` profiles are now recorded in
`docs/CPU_PROFILE_REPORT.md` and `evidence/STREAMFLEX_GAP_ANALYSIS.md`.
Conclusion: the checked scoped row is not dominated by close-time cleanup or
`checkOpen`; it is split across shared pipeline/query work, SafeZone-backed
allocation/zeroing, and capsule transfer. Optimize transient object layout,
allocation zeroing/alignment, linked traversal, or a closer capsule runtime
before adding another close/open fast path.
Latest profiling-sweep update: child `5300e3217` completes the reusable
`sandbox/run_l4_profile_sweep.sh` harness. The default profiles StreamFlex
checked and heap; `RIFT_PROFILE_CASES=all` now expands to representative
StreamFlex, generated Common Crawl-shaped q2, DSPBench Fraud q2 with the
bundled real credit-card input, LogHub HDFS streaming top-k, StreamIt
FilterBank, and profile-sized StreamIt BeamFormer rows. The first
representative `/usr/bin/sample` sweep is recorded in
`evidence/PROFILE_SWEEP_MATRIX.md` and summarized in
`docs/CPU_PROFILE_REPORT.md`. Use this harness whenever a benchmark row wins,
loses despite GC removal, or changes after an operator/backend optimization.

Latest Yak real-text update: child `cd08f23d4` adds Stack Exchange AskUbuntu
support, and child `59c181746` adds the current 20M scale-up rows. The dataset
is now local under `cache/benchmark-data/yak/stackexchange`. `YakRegionMatrix topwordreal`
tokenizes real `Posts.xml` title/body text into replayed epoch-local
`WordRecord` objects. At 20M real tokens x5, L1 `checked-epoch-scoped` is
`7.16 s` and `174 MB` RSS versus heap `7.77 s` and `986 MB`; the matching L2 row
is `432.824 ms`, GC `0 ms`, versus heap `511.485 ms`, median GC `33.471 ms`.
This is the first real text/top-word row in the Yak ladder. It strengthens the
checked epoch real-input story, while the reusable `EpochTopKByKey` row remains
a tuning target because it is slower than direct checked epoch and heap elapsed
on this input.

Latest open-region safety audit: child `55ce32ec6` extends the internal
typestate and mixed-reference probes to operator-owned checked paths. The new
audit in `evidence/OPEN_REGION_TYPESTATE_AUDIT.md` classifies
`RiftRegion.epoch`, page-token open helpers, epoch-buffer open helpers, public
child regions, and transaction regions by active-handle versus defensive API
status. It also records the remaining limitation: page-token open handles are
not statically linear after close, so this slice adds probes and documentation
but does not remove more public stale/open checks.

Latest presentation-normalization update: parent checkpoints `5185a3e`
(`Normalize final-clean evidence tables`) and `5cf9ac3` (`Audit legacy evidence
for presentation`) are the committed evidence baseline, child checkpoint
`0773d4c17` remains the implementation baseline, and
`evidence/EVALUATION_CLASSIFIED_SUMMARY.md` now explicitly marks dirty,
old-SafeZone, L2-only, benchmark-local, legacy parser, and gated
DEBS/TableRank/rank rows as replace-with-L1, L2-interpretation-only,
lower-bound topology, or archive/control-only evidence.

Active worktree: `/Users/siyaoliu/rift/scala-native-rift`

Branch: `feature/rift`

Naming checkpoint: new reports should use the canonical taxonomy in
`docs/MEMORY_MODE_TAXONOMY.md`. In particular, use `heap-immix`,
`safezone-improved-32k`, `safezone-rootless-32k`, `rift-trusted-hp`,
`rift-trusted-streaming`, `rift-checked-rift`, and
`rift-checked-safezone-improved-32k` instead of older ambiguous labels such as
`heap`, `unsafezone-hp`, or `rift-checked-safezone-32k`, except when quoting raw
legacy output.

Reporting-name checkpoint: the presentation layer is now moving to more
descriptive names: `gc-heap`, `region-scoped-rooted`,
`region-scoped-rootless`, `region-stream-rootless`,
`checked-region-stream`, `checked-region-scoped`, and `checked-page-token`.
Raw code symbols and script modes are not being renamed in this milestone.
Final public/internal classification is tracked in
`docs/FINAL_COMPONENT_SELECTION.md`; this phase prunes the public/default
story before physically deleting any runtime code. The staged performance
runner and main sandbox matrix defaults now follow this split: rootless/current
controls require `RIFT_EVAL_INCLUDE_CONTROLS=1`,
`RIFT_BENCH_INCLUDE_CONTROLS=1`, or explicit per-matrix mode variables.
Smoke run `2026-05-06-final-selection-smoke` completed the broad default path
with controls off; treat it as validation only because it ran from the current
dirty checkpoint.
Clean run `2026-05-06-final-selection-headline` then completed from parent
`72dc1df` and child `458c556d`; source summary is
`evidence/FINAL_SELECTION_HEADLINE_2026_05_06.md`.

Current merge state is tracked in `docs/HANDOFF.md`; the substantive roadmap
revision began at implementation commit `ddbba577aecd4c0adc741cbf7085ee93548c46b4`.
Benchmark descriptions and evidence classes are tracked separately in
`docs/BENCHMARK_CATALOG.md`.

Classified evaluation checkpoint: `evidence/EVALUATION_CLASSIFIED_SUMMARY.md`
is now the top-level reporting index for representative results. It separates
natural heap baselines, same-shape heap controls, summary-only topology rows,
retained-object drop-anchor comparisons, best checked topology rows, and
unsafe/trusted lower bounds. Future benchmark/operator work should add rows to
that structure before turning a result into a thesis claim.

Fair-evaluation and measurement checkpoint:
`docs/FAIR_EVALUATION_PROTOCOL.md` now defines the reviewer-facing comparison
contract. Headline rows must use framework APIs or be labeled controls, and
memory-management causality claims should compare retained heap/drop-anchor
against retained checked regions, while prior-work-style headline tables should
show natural heap/GC versus checked Rift first.
`evidence/MEASUREMENT_OVERHEAD_PROTOCOL.md` defines
L1 final-clean, L2 standard stats, L3 diagnostics, and L4 external profiles.
Initial L1 final-clean support now exists for retained epoch, Yak, Dataflow,
Common Crawl WET-shaped, ReML Tier 1, StreamFlex, Stancu,
SPECjbb2005-workload, LogHub top-template, LogHub region, and DSPBench region
binaries, NEXMark, and GH Archive. Current report-grade benchmark rows are still mostly L2; the final elapsed/RSS
headline table should be collected into
`evidence/FINAL_CLEAN_HEADLINE_RESULTS.md`. The first clean
focused retained L1 row is now recorded from child `f1aa55484`: 1M retained
records, 20 iterations per external process, 3 external repeats, with checked
scoped retained at `0.47 s` median total process time versus heap
retained/drop-anchor at `0.70 s`.
Child `7573d7577` then extended external real/user/sys/RSS summary columns to
the Dataflow, Yak, Common Crawl WET-shaped, and ReML runners. The next
measurement step is no longer runner plumbing; it is selecting and running the
representative L1 rows for the final-clean headline table. Dataflow
SELECT/AGGREGATE/JOIN now have representative L1 rows: checked epoch scoped is
`0.38/0.69/0.39 s` median total process time for 20 1M-document iterations
versus heap `0.62/1.10/0.55 s`.
Yak LiveJournal now has the first L1 real-input epoch row: checked epoch
scoped is `16.12 s` median total process time versus heap `18.79 s`, including
one gzipped input preload plus five 50M-edge replays per process; RSS drops
from about `2.77 GB` to about `612 MB`.
Generated Common Crawl-shaped q1/q2 now have L1 page-token rows. At 1M pages,
checked page-token stream is fastest (`4.02/4.16 s`) versus heap
`5.68/5.53 s` and safezone-improved-32k `5.42/5.39 s`; checked scoped
page-token also wins over heap/rooted (`4.51/4.75 s`) but trails the checked
streaming page-token backend.
Child `c5bbc498f` adds L1 final-clean support and external timing/RSS summary
columns for StreamFlex and Stancu. Tiny smokes matched checksums; clean
representative L1 throughput/latency and transaction rows are now recorded.
The direct-epoch StreamFlex rerun is the relevant headline: throughput is
checked scoped direct epoch `0.58 s` versus heap `0.79 s`, and latency is
checked `0.17 s` with zero misses versus heap `0.18 s` with four misses.
Stancu transactions are checked scoped direct epoch `0.57 s` versus heap
`0.85 s` and improved SafeZone `0.71 s`.
Child `678a6eb41` adds L1 final-clean support for the SPECjbb2005-workload
port. The 8-warehouse representative row is checked epoch scoped `2.21 s`
versus heap `2.64 s` and rooted scoped region `2.48 s`, with RSS about
`8.0 MB` versus heap `12.4 MB`.
Child `3598efe29` adds L1 final-clean support for LogHub top templates. The
hot-path follow-up at child `59acadda6` reduces reusable top-k overhead:
real HDFS 1M x20 is reusable checked top-k scoped `4.88 s` and about `28 MB`
RSS versus retained heap `5.52 s` and about `205 MB` RSS. The benchmark-local
checked retained path is `4.80 s`, so report-facing API overhead is now about
`1.7%`.
Child `fe8f0d853` adds L1 final-clean support for `LogHubRegionMatrix`. The
real HDFS q2 page/window row is an L1 elapsed tie plus RSS win: checked scoped
page-token `25.56 s`, about `79 MB` RSS versus heap `25.60 s`, about `409 MB`
RSS for 1M lines x3 q2 iterations per process. The L2 standard-stats row still
provides the GC interpretation: checked scoped page-token `7871.856 ms` versus
heap `8227.369 ms`, removing heap's `92.659 ms` median timed GC.
Child `95f4f4d71` adds L1 final-clean support for `DSPBenchRegionMatrix`.
Fraud q2 is a checked RSS win but not a checked throughput headline: checked
scoped page-token is `4.44 s`, about `59.5 MB` RSS versus heap `4.39 s`, about
`358 MB` RSS, while trusted Streaming is the unsafe/trusted lower-bound at
`4.18 s`. Log q2 is a modest checked elapsed/RSS win: checked scoped page-token
is `8.79 s`, about `47.6 MB` RSS versus heap `8.89 s`, about `308 MB` RSS,
while trusted Streaming is again the lower-bound at `8.51 s`.
Child `dffe178a0` adds L1 final-clean support for `NexmarkRegionMatrix`.
Beam-default-style q3/q8/q9/q11 are checked generated-methodology wins in L1:
checked `5.86/9.21/15.03/4.36 s` versus heap `6.18/9.54/16.27/4.47 s` and
improved SafeZone `6.38/10.13/18.10/5.11 s`, with much lower RSS than heap.
Child `54bf38c45` adds L1 final-clean support for `GithubArchiveRegionMatrix`.
The two-hour real file-backed byte-slice q1/q2 rows are modest checked
page-token elapsed/RSS wins: q1 checked scoped page-token `12.89 s`, about
`101 MB` RSS versus heap `13.17 s`, about `265 MB`; q2 checked scoped
page-token `12.87 s`, about `102 MB` RSS versus heap `13.18 s`, about
`244 MB`. L2 rows show heap GC is only about `1.5-1.6%` of elapsed, so this is
a useful real-input modest/RSS row rather than a flagship GC-heavy case.
The same L1 support now also covers generated/preloaded retained q2:
`heap-epoch-retained-no-traverse` is `4.62 s` and about `147 MB` RSS for 20 x
1M q2 iterations, while `checked-scoped-epoch-retained-no-traverse` is
`3.44 s` and about `16 MB`. This is retained-object memory-management
evidence; the `heap-direct-summary-only` lower bound is `1.28 s` and remains
topology evidence only.
The direct-summary topology lower bound is now symmetric: checked stream and
checked scoped direct-summary counterparts are both `1.45 s` and about `7 MB`
RSS versus heap direct-summary `1.36 s`. Future summary-only tables should not
list heap-only lower bounds when region counterparts exist.
Child `bc9fd5979` applies the same symmetry rule to DSPBench and LogHub
generated/indexable direct-summary rows. DSPBench Fraud/Log q2 checked
direct-summary rows are within about `1%` of heap direct-summary in L1; LogHub
q2 is within about `4%`, and q3 is within about `2-3%` while remaining
query-CPU dominated. These rows stay classified as topology/operator lower
bounds, not memory-management claims.
The Yak topword follow-up now applies the same fair-control rule to top-k:
same-shape heap top-k retained/no-traverse is measured alongside reusable
checked `EpochTopKByKey` rows. At 10M, checked scoped top-k is `249.311 ms`
versus natural heap `313.724 ms` and same-shape heap top-k `297.740 ms`, with
zero timed GC and RSS near other region rows. Direct checked epoch remains the
best Yak topword topology at `234.031 ms`, so the top-k API is a passed
reusable operator row but not the default topology for every topword-shaped
program.
The L1 final-clean follow-up confirms this with external process timing:
checked scoped top-k is `4.94 s` over 20 x 10M generated records versus
natural heap `6.25 s` and same-shape heap top-k `5.72 s`; direct checked epoch
is still best at `4.61 s`.

ReML/MLKit PLDI-style table checkpoint:
`evidence/REML_MLKIT_PLDI_TABLE.md` now separates paper-reported Figure 9
data, exact-artifact rerun status, local Scala Native port rows, and
ReML-inspired safety probes. L1 final-clean Tier 1 rows have been added for
the local Scala Native ports. The useful L1 rows are `msort` and `msort-r`
speed/RSS wins and `ratio` as a modest elapsed but strong RSS row; `fib37`,
`life`, `tak`, `fft`, and `mandel` are controls at the current scale. Exact
MLKit/ReML timing remains open; compare ratios and safety burden until local
`mlkit`/`mlton` runs are available.

Operator-gate checkpoint: `evidence/OPERATOR_GATE_STATUS.md` now records the
next-rank/hash/median/join decision tree. Q8 join is framework/RSS evidence but
not a speed claim against `heap-join-api`; priority queues and TableRank remain
API/gated evidence; LogHub top templates are now the first retained top-k shape
with a reusable checked API gate.

LogHub top-template checkpoint: child commit `2393a69c4` adds the focused
retained top-k matrix. It passes the retained-object gate on generated and
real-preloaded HDFS input. Child commit `9abac4833` adds the follow-up
`EpochTopKByKey` API, which also passes. After the increment hot-path pass,
generated 1M checked scoped top-k is `274.914 ms` versus retained heap
`397.788 ms`, and real HDFS preloaded checked scoped top-k is `82.170 ms`
versus retained heap `111.704 ms`. The L1 real HDFS x20 row confirms the same
direction with external timing/RSS: reusable checked top-k scoped `4.88 s` and
about `28 MB` RSS versus retained heap `5.52 s` and about `205 MB` RSS. The
remaining top-k API overhead is small enough that the next step is integration
only for natural retained top-k workloads, not DEBS ranking or generic
TableRank.
Yak topword is now that second natural top-k integration check. It passes
against natural and same-shape heap controls, while preserving the topology
caveat above.

Latest staged headline sweep: `evidence/COMPREHENSIVE_SWEEP_2026_05_06.md`.
It completed prior-work, checked-operator, SafeZone-cost, and stream rows with
current SafeZone skipped in competitive rows. Core runtime/topology headline
rows remain from the earlier clean core runs until a separate current-skipped
core sweep is added.

Latest direct-epoch sweep: `evidence/DIRECT_EPOCH_TOPOLOGY_MATRIX.md`. The
latest representative rerun was run after child commit `918c7d4c1` and parent
commit `ab570b1`; earlier local-Yak rows remain clean prior checkpoint
evidence. It confirms direct checked epoch as a reusable positive topology
across Yak real LiveJournal graph replay, Broom-style Dataflow
SELECT/AGGREGATE/JOIN, StreamFlex throughput/latency, and Stancu-style
transaction batches. The strongest current row is 50M LiveJournal:
checked epoch scoped is `2008.320 ms` and about `2.11 GB` RSS versus heap
`2958.659 ms`, `400.484 ms` timed GC, and about `3.91 GB` RSS.

Direct-epoch extension checkpoint: generated/indexable DSPBench q2, GH
Archive-shaped q2, and LogHub-shaped q2/q3 now have checked direct-epoch modes
and a `heap-direct-epoch` same-shape aggregate control. These rows allocate
ordinary records in bucket epochs and retain only primitive bucket summaries
until the original close point. The same-shape control shows this is primarily
operator/topology evidence: GH Archive-shaped q2 is heap `287.380 ms`,
heap-direct `54.642 ms`, checked scoped `56.013 ms`; LogHub-shaped q2 is heap
`526.803 ms`, heap-direct `191.601 ms`, checked scoped `193.938 ms`; LogHub
q3 is heap `2225.364 ms`, heap-direct `1779.064 ms`, checked scoped
`1792.397 ms`; DSPBench Fraud q2 is heap `400.900 ms`, heap-direct
`272.251 ms`, checked scoped `267.739 ms`. NEXMark Q3/Q8/Q9/Q11 remain
page-token/join/window candidates, not direct-epoch candidates.

Retained-epoch reclaim checkpoint:
`evidence/RETAINED_EPOCH_RECLAIM_MATRIX.md` now separates summary-only topology
from retained-object memory-management evidence. The focused 1M retained
matrix shows checked scoped retained epoch `24.274 ms` versus retained heap
`36.233 ms`, with heap spending `10.109 ms` in timed GC and using about
`21.3 MB` RSS versus about `4.9 MB` for checked scoped. DSPBench Fraud q2 1M
retained controls show checked scoped retained epoch `370.746 ms` versus
retained heap `392.743 ms`, removing `35.631 ms` median timed GC. GH
Archive-shaped q2 retained controls show a larger memory-management win:
checked scoped `186.868 ms` versus retained heap `257.377 ms`, with RSS about
`15 MB` versus `147 MB`. LogHub q2 retained shows checked scoped `402.821 ms`
versus retained heap `469.079 ms`; LogHub q3 retained is mixed but checked
scoped still improves elapsed over retained heap (`2106.541 ms` versus
`2244.266 ms`). Treat retained rows as the fair memory-management comparison;
`heap-direct-summary-only` remains the operator/topology lower bound and must
not be used as a pure placement claim. When it is listed, include the checked
direct-summary counterpart as well.

Latest SPECjbb2005-workload port: `evidence/SPECJBB2005_PORT_MATRIX.md`.
`SpecJbb2005PortMatrix` is a clean-room Scala Native workload port, not an
official SPECjbb2005 result. It covers warehouses 4 through 8 with 100,000
transactions per warehouse. L1 final-clean 8-warehouse rows show checked epoch
scoped `2.21 s` versus heap `2.64 s` and rooted scoped region `2.48 s` for 20
inner iterations. L2 scale rows still give the GC interpretation: at 8
warehouses, checked epoch scoped is `108.649 ms` versus heap `129.674 ms` with
`15.125 ms` timed GC. This strengthens the Stancu/SPECjbb methodology track
while keeping exact-artifact claims out of scope.

Latest page-token cost checkpoint: `evidence/CHECKED_PAGE_TOKEN_COST_MATRIX.md`.
The focused cost split shows checked scoped page-token is competitive on
append-only/drain/aggregate same-shape rows, but no-drain close is not the main
remaining bottleneck. Next operator work should target allocation/query CPU
and application paths that still do bucket/region lookup too often, not more
generic close-drain removal.

Latest page-token live-length checkpoint: page-token-owned appends now skip the
generic append-window live-length counter while keeping per-bucket length for
close/cursor correctness. This is a valid overhead cleanup but not a large
application speedup. Focused count-by-key remains positive (`102.504 ms`
checked scoped versus `114.143 ms` heap), but DSPBench Fraud q2 is only a
checked RSS/GC near-tie (`843.380 ms` checked scoped versus `842.739 ms` heap).
This weakens the value of further page-token bookkeeping tweaks and makes
generated allocation lowering under static operator ownership the next
meaningful checked-runtime target.

Latest owned-cursor checkpoint: `StreamAppendCursor.nextOwnedOrNull()` removes
per-record link clearing only for operator-owned page-token close callbacks;
generic cursors stay defensive. This is a validated static-safety overhead
removal, not a new benchmark algorithm. Validation passed compile,
`RiftRegionCheckedCompilerTest` `120/120`, and `RiftRegionCheckedTest` `52/52`.
The focused 1M checked scoped page-token rows improved to
`73.590/83.997/81.296 ms` for append-only/drain/aggregate. Real DSPBench Fraud
q2 moved from checked/RSS near-tie to a modest checked elapsed win:
checked scoped page-token `800.369 ms` versus heap `807.974 ms`, with RSS
about `278 MB` versus heap `358 MB`; trusted Streaming is still faster at
`785.682 ms`. Generated Common Crawl-shaped 1M q1/q2 strengthens the checked
page-token story: checked scoped page-token `3643.680/3790.138 ms` versus heap
`5392.344/5201.862 ms`, with heap timed GC about `1.58 s`.

Latest open-allocation checkpoint: checked page-token operators now have an
internal `OpenStreamingRegion`/`allocOpen` path. Lowering
`Classalloc(OpenStreamingRegion)` calls `RiftRegion.allocUncheckedImpl`, so
operator-owned child-bucket allocation avoids the generic checked
`allocImpl/checkOpen` branch while public checked APIs remain defensive.
Validation passed the checked compiler/runtime suites and sandbox compile.
Focused 1M checked scoped page-token is now `73.632/83.177/82.198 ms` on
append-only/drain/aggregate versus heap `76.295/85.873/84.354 ms`; checked
scoped count-by-key is `95.946 ms` versus heap `103.946 ms`. DSPBench Fraud q2
improves only slightly (`797.782 ms` checked scoped versus `806.697 ms` heap
and `778.975 ms` trusted Streaming), while generated Common Crawl-shaped 1M
q1/q2 remains strong (`3707.214/3902.795 ms` checked scoped versus
`5577.965/5183.074 ms` heap). Conclusion: static safety can remove this
runtime check, but it is not the dominant remaining cost. Next performance work
should profile object construction, append/linking, cursor traversal, and query
CPU before adding another page-token micro-optimization.

Latest post-open-allocation profile checkpoint: `docs/CPU_PROFILE_REPORT.md`.
The Common Crawl-shaped q2 checked scoped profile confirms the hot allocation
path now goes through `allocUncheckedImpl`; `allocImpl/checkOpen` is gone from
the target sample. Remaining sampled costs are zone allocation/zeroing/alignment,
append/linking, close cursor traversal, and token hashing/query work. The real
DSPBench Fraud q2 profile is led by byte-line parsing/replay, stable hashing,
fraud predictor state, CSV/state parsing, append, and close traversal. This
keeps Fraud q2 as a real-input regression row, but it argues against more
checked allocation micro-tuning as the next default step.

Latest real-input search checkpoint: LogHub HDFS v1 and Theodolite source were
added to the search ledger. HDFS v1 has `11175629` real Hadoop log lines; the
1M q2 row is the strongest checked real-log result so far, with checked scoped
page-token `7871.856 ms` versus heap `8227.369 ms`, removing heap's
`92.659 ms` median timed GC and lowering RSS. This is a useful modest
throughput/RSS/GC row, but still not the flagship GC-heavy case because heap GC
is only about 1-2% of elapsed. Theodolite UC2/UC4 source is cloned and has good
industrial-IoT methodology shapes, but its bundled load generator simulates
active-power records; pair it with a real industrial-energy trace before
claiming real-input evidence.

Latest Yak real-input checkpoint: `YakRegionMatrix` now includes `graphreal`
over SNAP Twitter ego and SNAP LiveJournal edge lists. LiveJournal is the
stronger row and now has checked topology coverage. At 50M replayed real
edges in the latest clean rerun, `gc-heap` is `2958.659 ms`, median timed GC
is `400.484 ms`, and RSS is `3913564160`. The best low-RSS checked shape is
epochal: `checked-epoch-scoped` is `2008.320 ms` and `checked-epoch-stream` is
`2064.867 ms`, both around `2.11 GB` RSS. Page-token checked still beats heap
but is slower (`2586.919/2746.897 ms`) because Yak is an epoch workload, not a
page/window-token workload. A reusable `EpochBuffer` follow-up confirms the
API direction but trailed the direct linked epoch path, so direct epoch is the
row to headline. This is now the strongest current real-input
prior-work-shaped row and the clearest evidence that the user-facing API should
expose `Rift.stream { epoch { ... }; window(...) { ... }; page { ... } }`
while the implementation chooses the backend/operator. It remains local
methodology evidence: not exact Yak, not exact GraphChi, and not Yak-scale
Twitter-2010/SampleTwitter evidence. `RiftRegion.epoch { ... }` now provides
that reusable checked linked-epoch block: streaming backends reset at the epoch
boundary, SafeZone-backed checked regions open/close a scoped child region, and
callers get an `OpenStreamingRegion` for `allocOpen`. A small `graphreal`
smoke matched checksums across heap, direct checked epoch, and `EpochBuffer`.
The latest clean 10M/50M reruns confirm the direction: direct checked epoch is
`417.426/425.983 ms` scoped/stream versus heap `599.428 ms` at 10M; at 50M,
`checked-epoch-scoped` is `2008.320 ms` with `2.11 GB` RSS versus heap
`2958.659 ms`, `400.484 ms` timed GC, and `3.91 GB` RSS. The same reusable
epoch topology now covers local Yak-shaped `wordcount`, `graphstep`, `sort`,
`topword`, and `graphchi`; at 10M logical objects, `checked-epoch-scoped` is
fastest among measured rows for wordcount/graphstep/topword/graphchi, and the
new 1M sort row is a modest checked array win. The same direct epoch topology
now covers Broom/Dataflow SELECT, AGGREGATE, and JOIN: at 10 epochs x 100k
documents, `checked-epoch-scoped` is `19.691/34.676/19.762 ms` versus heap
`27.775/50.837/30.387 ms` and region-scoped rooted
`22.971/39.665/22.619 ms`.
Yak grouped sort now uses a checked region-captured array topology:
`checked-epoch-stream` `230.000 ms` and `checked-epoch-scoped` `230.799 ms`
versus heap `235.554 ms` and improved SafeZone `233.068 ms`. Treat sort as
coverage/modest CPU-bound evidence, not a flagship GC win.
The same direct epoch topology now covers StreamFlex-shaped throughput and
latency: at 1M throughput, scoped direct checked epoch is `163.339 ms` versus
heap `218.582 ms`, improved SafeZone `208.653 ms`, trusted Streaming
`182.246 ms`, and scoped checked `TransactionRegion` `205.929 ms`. This
changes the StreamFlex checked direction from "TransactionRegion is best" to
"direct epoch is best when the pipeline stages share one batch lifetime."
Stancu-style transaction batches now follow the same direct epoch direction:
in the clean direct-epoch sweep at 1M transactions, scoped direct checked epoch
is `155.992 ms`, direct stream epoch is `168.617 ms`, improved SafeZone is
`180.912 ms`, trusted Streaming is `214.052 ms`, and heap is `222.415 ms`.

Stancu/SPECjbb2005 reproduction boundary: the current Stancu matrix remains a
local transaction-shaped probe. The stronger target now has an initial
documented SPECjbb2005-workload Scala Native port, not an official SPECjbb2005
run on Scala Native. The plan is tracked in
`docs/STANCU_SPECJBB2005_PORT_PLAN.md`; it distinguishes optional JVM artifact
controls, Scala Native workload-port rows, and Stancu paper-axis reproduction
metrics.

Latest CPU profile checkpoint: `docs/CPU_PROFILE_REPORT.md`. macOS
`/usr/bin/sample` profiles for generated Common Crawl-shaped q2 at 2M pages
show the checked page-token hot paths are close cursor traversal,
`appendWindowOwnedOpen`/`appendPageToken`, backend allocation/zeroing
(`scalanative_zone_alloc` for scoped and `scalanative_rift_region_alloc/raw`
for Rift), `allocImpl/checkOpen`, and token-hash/query work. Bucket opening is
not dominant. This shifts the next optimization search toward generated
allocation lowering/stat-check removal and operator-owned `checkOpen`/append
specialization, with traversal/query CPU treated as a shared floor.

Latest profiling-plan checkpoint: add `samply` to the diagnostic workflow when
available on macOS. Use it on the linked Scala Native binary, not `sbt run`, to
inspect both CPU composition and visible GC pause/collection frames. First
targets are generated Common Crawl-shaped q2, DSPBench Fraud q2, LogHub BGL q3,
and the focused page-token cost matrix. `samply` profiles are diagnostic only:
they can explain where time goes, but headline timings still come from clean
non-profiled benchmark medians.

## 1. Roadmap Principles

The roadmap separates four questions:

- Can the runtime path itself beat current SafeZone, improved SafeZone, and
  heap on same-layout workloads?
- Which effects come from runtime, topology, and layout?
- Can real stream/dataflow workloads move dominant data operations into regions?
- Can the safe API be justified by static capture checking and a mechanized
  containment proof?

The roadmap also keeps prior-work comparison anchors visible. Rift is not done
when it beats old SafeZone on one benchmark. It must eventually explain its
position relative to Broom, StreamFlex, Yak, Stancu-style static hybrid
analysis, Tofte-Talpin/MLKit, Hallenberg-Elsman typed regions, and
Reggio/Verona capabilities.

## 2. Status Summary

| Phase | Status | Evidence | Main remaining work |
|---|---|---|---|
| Phase 0: baseline and comparison contract | Mostly complete, not sealed | `sandbox/PHASE0_BASELINES.md`; literature review now read as design constraint. | Commit/provenance boundary, Commix gaps, pipeline remains surrogate. |
| Phase 1: standalone allocator bootstrap | Done as provenance | `/Users/siyaoliu/rift/rift-bootstrap/bench/microbench/results.md`. | Do not continue active design there unless validating bootstrap artifacts. |
| Phase 2: in-tree runtime/compiler path | Partially done | `RiftRuntime.c/h`, `RiftRegion`, plugin lowering, `RiftRegionTest`. | Header/API cleanup, broader tests, commit boundary, stats ABI decision. |
| Phase 3: runtime-only evaluation | Done enough for current claim | GCBench and ListOfLists medians show Rift wins over heap and improved SafeZone. | Add Commix where relevant; avoid overclaiming pipeline. |
| Phase 4: topology/layout decomposition | Done enough to move on | `PHASE4_LAYOUT.md`, `PHASE4_TOPOLOGY.md`, `PHASE4_EXIT.md`. | Carry safety finding into Phase 6; chunked layout still not clear Rift win vs improved SafeZone. |
| Phase 5: application evidence | In progress, not complete | DEBS Q1/Q2 scaffold runs and outputs match on bounded real-data samples; RunBoth uses a shared byte parser and region-backed input buffer; Rift modes now region-allocate Q1/Q2 window entries, Q2 median scratch, ranking objects, reusable top-k result arrays, Q2 bounded cell tables, Q1 primitive route-table arrays, Q1 ranking-index arrays, Q2 latest-empty taxi arrays, Q2 ranking-index arrays, Q2 taxi-id table entries/bytes, RunBoth output snapshots, Q2 incremental median heap arrays, and RunBoth latency buffers. The current trusted 1M byte-output 3-run medians are heap `4640.593 ms`, HPZone `4524.706 ms`, and Streaming `4522.308 ms`; GC collection medians are heap `21.025 ms`, HPZone `0.685 ms`, and Streaming `0.635 ms`; heap RSS is `159907840` bytes vs `116785152` bytes for HPZone/Streaming. A 1M allocation-attribution run shows heap at `6,025,143` GC allocation calls, `235,159,552` rounded bytes, and `171.868 ms` allocation-call time, versus about `0.56M` calls, `10.5 MB`, and `12.8-12.9 ms` in Rift modes. Q1 checked-output, Q1 checked-processing, and Q2 checked-processing probes now match heap output on bounded sorted samples; checked Q1 closes live event-node `childWindow` regions at bucket eviction, and checked Q2 region-manages profit/empty entries, median heaps, rank objects, taxi-id entries/bytes, and top-k storage using `childWindow` plus explicit `childRegion(parent, window)` owner-token widening where parent metadata retains child entries. RunBoth `rift-checked` now has 100k/1M 3-run medians. At 1M, heap is `5363.257 ms`, trusted HPZone is `5224.005 ms`, trusted Streaming is `5209.104 ms`, and checked is `5043.240 ms`; GC medians are heap `21.226 ms`, HPZone `0.834 ms`, Streaming `0.862 ms`, and checked `2.473 ms`. Checked allocation attribution at 1M drops heap allocation calls from `6025149` to `752568`, rounded bytes from `235159840` to `28785632`, and measured allocation-call time from `173.578 ms` to `20.514 ms`. A 3-run Commix DEBS control now also has checked Rift faster and lower-RSS: at 1M, Commix heap is `4968.773 ms` and `158924800` bytes RSS, versus checked Rift `4745.291 ms` and `125698048` bytes RSS. The first full-month checked RunBoth control matched heap output but had invalid checked wall-clock timing. A runtime pool cap then made full-month checked runs practical: the first same-run pool-cap control was heap `71.919 s`, `0.323 s` GC, `579.1 MiB` RSS versus checked `77.947 s`, `0.190 s` GC, `695.2 MiB` RSS. After the single-control-object `ChildBucket` change, the same-order full-month 3-run median is heap `73.029 s` versus checked `67.670 s`, with GC `0.315 s` versus `0.086 s`; checked RSS regresses (`866.6 MiB` median versus heap `586.4 MiB`) and one checked repeat is slower. Active-memory diagnostics then showed this RSS regression was mostly live checked-region payload at current lifetimes, especially Q1 rank objects in the parent checked stream. Moving Q1 checked rank object graphs into current child-bucket regions reduces full-month checked active requested peak from `823153856` to `180948200` bytes and RSS from `1086668800` to `613318656` bytes in checked-only diagnostics. The post-fix full-month 3-run heap/checked control matched outputs and gives a near-tie elapsed median: heap `67.122 s` versus checked `66.804 s`; checked RSS median is now `613.3 MiB` versus heap `595.9 MiB`, with GC `0.117 s` versus heap `0.285 s` and checked Rift op `0.779 s`. A closeable SafeZone DEBS mode now exists; 100k controls and 1M 3-run medians match heap output for current and improved SafeZone roots modes. In 1M medians, SafeZone is lower-RSS than heap but slower; checked Rift remains lower-RSS and faster than heap/SafeZone. Opt-in process diagnostics attribute checked CPU shape: Q2 operation counts are identical between heap and checked, while the pre-arena full-month Q1 checked rank creations rose from `6195167` to `14487771`. The accepted Q1 window-rank arena reduces that checked count to `8842434` in a full-month single-run scale check and records lower checked RSS than heap in that row. `StreamBucketArena` generalizes the checked bucket lifetime primitive and checked Q1 uses it; sample and 100k heap/checked controls matched outputs after migration. `StreamWindowIndexedRank` now adds the first dense-key checked rank/window collection above that primitive, and `CheckedStreamWindowRankMatrix` validates that pattern with matching checksums while showing current CPU overhead. The auto-cleanup update adds `putWindowRankInBucket`, so tracked keys are removed from parent rank state before child bucket close; it strengthens the safety boundary but increases focused benchmark CPU overhead. The entry-cleanup update adds close-with-entry callbacks so checked operators can clean side tables during framework unlinking without a duplicate bucket-local key list; it improves the focused checked default from `313.572 ms` to `302.001 ms` and RSS from `94732288` to `87441408` bytes, but remains slower than heap and the earlier manual-cleanup path. The follow-up remove-with-value close primitive validates already-popped-key cleanup but did not produce a measured speedup. The lexicographic priority rank API now supports Q1-style count/time/sequence/key tie-breakers while preserving the dense-key close discipline; hash-keyed state and lower container CPU overhead remain open. The Q2 CPU substep diagnostic adds opt-in `diag_q2_cpu_*` timers and shows bounded 100k/1M checked Q2 process time lower than heap in those perturbing rows, with matching Q2 operation counts. | Continue reducing `StreamWindowIndexedRank` container CPU overhead or add hash-key rank variants before broad Q1 integration, and only revisit Q2 CPU if a clean or full-month diagnostic identifies a specific substep. |
| Phase 6: literature-aligned methodology evidence | Started | `DATAFLOW_REGION_MATRIX.md`, `STREAMFLEX_REGION_MATRIX.md`, `YAK_REGION_MATRIX.md`, `STANCU_REGION_MATRIX.md`, `NEXMARK_REGION_MATRIX.md`, `COMMON_CRAWL_WET_MATRIX.md`, `COMMON_CRAWL_LIKE_MATRIX.md`, `WIKIMEDIA_REGION_MATRIX.md`, `LINEAR_ROAD_REGION_MATRIX.md`, `YAHOO_AD_REGION_MATRIX.md`, `RIOTBENCH_REGION_MATRIX.md`, `GITHUB_ARCHIVE_REGION_MATRIX.md`, `LOGHUB_REGION_MATRIX.md`, `DSPBENCH_REGION_MATRIX.md`, `REML_COMPARISON_MATRIX.md`, `STREAM_GC_BENCHMARK_CANDIDATES.md`, `REAL_INPUT_BENCHMARK_SEARCH.md`, and `STREAM_BENCHMARK_LADDER.md` now cover Broom-style dataflow, StreamFlex-style latency/throughput, Yak-style control/data epochs including grouped sort, top-word/filter, and GraphChi-like subinterval updates plus runtime and memory-API-level promotion/escape proxies, Stancu-style transaction accounting, ReML/MLKit-lineage paper-reported benchmarks plus local Scala Native-shaped Tier 1 ports, NEXMark-lite and Beam-default generated-profile streaming including Q3/Q4/Q9/Q11, generated and real/preloaded Common Crawl WET/WAT, Wikimedia clickstream, generated and official Linear Road position/toll probes, Yahoo-style ad-stream probes, RIoTBench-style IoT ETL/statistics probes with UCI MHEALTH real-input follow-up, real GH Archive NDJSON probes, real LogHub BGL system-log probes including richer q3 template/session mining, DSPBench Spike/Fraud Detection q0/q1/q2 over bundled real rows, and a ranked stream-GC benchmark ladder. Dataflow now includes checked SELECT/AGGREGATE/JOIN modes. ReML exact-artifact source provenance has started: the public MLKit repo is cloned in ignored cache, many Figure 9-style benchmark sources were found, and tags `v4.7.4`/`v4.7.5`/`v4.7.6` bracket the public ReML release; local `mlkit`/`mlton` runs and verified `rg`/`rg-`/`r` command mappings remain open. The clean stream headline sweep makes NEXMark Beam-default Q3 the best checked application-style row (`295.166 ms` checked vs `315.715 ms` heap and `302.668 ms` improved SafeZone), while Q8 is a checked near-tie with improved SafeZone and Q11 is heap-fastest. Generated Common Crawl WET-shaped q1/q2 are now the clearest trusted-Rift GC-heavy stream wins after removing default per-allocation global allocated-byte atomics: q1 `rift-hp` is `4386.590 ms` vs heap `5466.535 ms` and improved-32k `4608.641 ms`; q2 `rift-streaming` is `4164.288 ms` vs heap `5267.784 ms` and improved-32k `4425.273 ms`. q3 parser scratch remains a negative control where heap wins despite GC. GH Archive q1 and LogHub BGL q1/q2/q3 are memory-budget/tail/modest-throughput candidates, not flagship GC-heavy proof; q3 cuts RSS by about `53 MB` but heap GC is under 1% of elapsed. DSPBench Spike is modest/control evidence. DSPBench Fraud q2 is the strongest DSPBench row so far: trusted Streaming `763.819 ms` vs heap `801.790 ms`, heap GC `69.686 ms`, and RSS `282460160` vs heap `358252544`; checked scoped q2 lowers GC/RSS but loses elapsed. A heap-cap follow-up does not create a checked fixed-memory win at 1M. RIoTBench/MHEALTH fixes the IoT real-input provenance gap but is zero-GC ceiling evidence at 1M: q1 heap `117.977 ms` vs Streaming `119.077 ms`; q2 SafeZone `107.194 ms` vs heap `109.589 ms`. Yahoo, Wikimedia, Linear Road, GH Archive q2, current real WET/WAT rows, and MHEALTH are mostly near-ties, modest wins, or heap/improved-SafeZone wins. | Keep these labeled as methodology reproductions, local ports, paper-reported literature numbers, generated stressors, or real-input probes as appropriate. Count modest throughput, RSS, and fixed-memory/tail wins separately instead of collapsing them into "mixed"; only representative wins become final public components. Do not claim exact ReML/MLKit reproduction until original artifacts/configurations are run locally. The clean core/prior/checked rerun weakens several older positives, including Broom-style checked rows against improved SafeZone. The Q8 reusable join API is framework progress; packed counts narrowed the fair 1M gap but it still failed the speed gate against `heap-join-api` (`20.987 ms` vs `17.393 ms`). The additive `StreamWindowFold` gate also failed (`118.726 ms` checked vs `103.244 ms` heap at 1M). Common Crawl-like q1/q2 are legitimate trusted runtime/backend evidence, but 1M RSS is not a win. Next work should preserve the page/token fast path and move to Theodolite-style inputs or another provenance-clean machine/security stream. |
| Phase 7: capture-checked safe API | Started | `RiftRegion.scoped`/`streaming` APIs exist; compiler probes now pass for scoped object graphs, for-loop allocation, nested scoped regions, local higher-order consumers, non-escaping closures, return escape rejection, heap retention rejection, nested-region leak rejection, streaming reset escape rejection, conservative returned-function rejection, ReML-style polymorphic local-consumer acceptance, ReML-style polymorphic return rejection, durable/static generic heap-retention rejection, widened `AnyRef` rejection, heap-array retention rejection, escaping-closure hiding rejection, explicit `HeapRoot` region-to-GC metadata handles, static module singleton and immutable module-val metadata, direct unrooted heap-object constructor-argument rejection, ReML-style polymorphic unrooted-heap constructor rejection, region-local alias acceptance, heap-alias rejection, heap-field-selection rejection, explicitly region-captured constructor-field reuse, plain `T^` field-reuse rejection, region-owned array checks, the owner-token `ObjectBuffer` checked container including `region.append/get/length`, growable owner-token `RegionBuffer`, owner-token `RegionPriorityQueue` for checked ranking/top-k state, owner-token `RegionIndexedPriorityQueue` for dense-key mutable ranking state, lexicographic checked indexed-rank priorities for Q1-style tie-breakers, reset epoch arrays, raw `childStreaming` handles that cannot escape their parent stream, the preferred `childWindow` stream-window wrapper, explicit `childRegion(parent, window)` owner-token child-entry widening, reusable `ChildBucket` wrapper plus `childBucketRegion`/`closeChildBucket`, reusable `StreamBucketArena` plus `streamBucketFor`/`streamBucketRegion`/structured close helpers, `StreamWindowIndexedRank` for dense-key stream-window ranking, `putWindowRankInBucket` auto-cleanup of bucket-owned rank keys before child bucket close, `closeWindowRankBucketsBeforeWithEntries`/`closeAllWindowRankBucketsWithEntries` callbacks for side-table cleanup during framework unlinking, reusable `StreamAppendWindow` append/fold bucket ownership plus `StreamAppendCursor` close, reusable `StreamJoinWindow` with packed-count put/remove fast paths, additive `StreamWindowFold` with checked put/remove and cursor close, benchmark-only `RiftRegion.streamingSafeZone(...)` checked SafeZone-backed allocation, top-word-style rooted metadata buffers, GraphChi-style rooted heap metadata, rejection of reset-epoch values stored into an outer streaming buffer, mutable local linked-list heads with provenance-preserving assignments, pinned diagnostic substrings for every current negative compiler probe, a focused `CheckedRegionBufferMatrix` where checked Rift beats the heap growable-buffer path on the default 1M-record local median, a focused `CheckedRegionPriorityQueueMatrix` that validates checked ranking/top-k state with no measured GC but slightly slower elapsed time than heap, a focused `CheckedRegionIndexedPriorityQueueMatrix` that validates fetch/mutate/update keyed rank state with no measured GC but slightly slower elapsed time than heap, a focused `CheckedStreamWindowRankMatrix` that validates checked child-bucket objects plus parent rank state with matching checksums but slower elapsed time than heap, a focused `CheckedAppendWindowMatrix` where the manual checked child-bucket shape wins at 1M, the cached/cursor reusable `StreamAppendWindow` API clears the focused 1M gate, and the checked SafeZone-backed backend improves the focused 1M row to `29.444 ms`; a focused `CheckedWindowFoldMatrix` where the additive fold API matches checksums and lowers RSS but fails the 1M speed gate, checked Dataflow SELECT/AGGREGATE/JOIN modes where checked Rift is fastest among heap, SafeZone, trusted Rift, and checked Rift in the local median, Q1 checked-output on real DEBS rows, Q1 checked-processing using checked event/rank objects plus per-bucket `ChildBucket` event regions and `StreamBucketArena` rank arenas, Q2 checked-processing using checked window entries, median heaps, rank objects, taxi-id entries/bytes, and result storage, first checked RunBoth integration through `q1_mode=rift-checked`, checked Q1 event-window `StreamAppendWindow` cursor integration with 1M bounded medians, and stronger structured close boundaries that reject direct user `window.close()`/runtime reuse after close and remove tracked rank references before bucket close. `docs/REPORT_CAPTURE_CHECK.md` records the checker slice. | Broader collection/operator APIs, hash-keyed state, lower CPU overhead in checked window/rank/fold containers, broader non-static heap-field provenance, full affine/linear close guarantees beyond the current close helper, rootless checked backend eligibility, and a better ergonomics story for field/container provenance beyond local linked-list heads. |
| Phase 8: native GC/region integration hardening | Started | Safety bug found for unrooted region-to-GC references; v1 explicit `HeapRoot` handles now retain heap metadata through a GC-visible list on the live region object, and checked lowering rejects direct unrooted heap-object constructor arguments, unsafe region-array stores, unsafe owner-token `ObjectBuffer`/`RegionBuffer` heap stores, mutable static vars, and mutable-head retagging from heap values while allowing region-to-region object graphs, simple region-local aliases, static module singletons, immutable module vals, stable constructor fields explicitly captured by `{region}`, region arrays with explicitly captured element types, owner-token object buffers, growable region buffers, and provenance-preserving mutable linked-list heads. | Extend or deliberately limit the mixed-reference rule for richer containers; decide whether plain `T^` field reuse and plain receiver-style container operations need a compiler extension or owner-token APIs. |
| Phase 9: Lean mechanization | Open | Design target only; older proof pack is not active in fork. | Core calculus and proofs without `sorry`. |
| Phase 10: writing | Not started beyond notes | Handoff and result packs exist. | Paper/thesis narrative after evidence stabilizes. |

Current Phase 7 checkpoint note: the summary table above should be read with
the latest checked-rank and cheap checked-operator slices included.
`RegionLongIndexedPriorityQueue` and `StreamWindowLongIndexedRank` cover
hash-keyed checked rank state for arbitrary `Long` keys. Fused
`StreamWindowTableRank` is implemented, tested, and profiled, but it remains
gated out of DEBS Q1: the latest 1M profile row is `568.572 ms` versus
same-run heap-long `437.702 ms`, with the gap explained by combined
lookup/probe/replacement/heap-maintenance pressure rather than Rift
open/close/allocation bookkeeping. The focused checked compiler suite is now
`96/96`, and the native checked runtime suite is `40/40`.

The current roadmap direction is therefore not "tune TableRank harder before
anything else." `SN_WIN_ENVELOPE.md` is now the selection guide: favor
allocation-heavy stream operators whose data objects share a structured
lifetime and whose control work is append/fold/filter/window-shaped rather
than rank/table-maintenance-heavy. `CheckedAppendWindowMatrix` is the new
positive focused result for that envelope. At 1M events, checked Rift is
`32.261 ms` versus heap `35.513 ms`, with `0.000 ms` GC versus heap
`11.149 ms`, `47.5 MB` RSS versus `75.0 MB`, and `0.074 ms` Rift op time. At
100k events, heap remains faster (`2.782 ms` versus checked `3.370 ms`), so
the result is a threshold result, not a universal checked-region win. The first
reusable per-entry `StreamAppendWindow` close API was correctness-valid but
not performance-ready. Cached bucket/region use narrowed the gap, and cursor
close now clears the focused 1M API gate: `rift-checked-api-cursor` is
`34.708 ms` versus same-run heap `35.705 ms` and same-run manual checked
`32.367 ms`. The order-insensitive `prependWindow` sibling also clears its
matching focused 1M gate but is effectively tied with append cursor, so it is
framework/control evidence rather than a DEBS migration trigger. Checked Q1
event-window entries now use this cursor-close shape
and match heap output on sample/100k Q1 and RunBoth controls plus a 1M 3-run
RunBoth control. The 1M median is heap `4559.928 ms` versus checked
`4514.165 ms`, with RSS `153.8 MiB` versus `91.7 MiB`. Treat that as bounded
application-path evidence, not final full-DEBS proof. DEBS Q1 ranking remains
out of scope until rank/table-maintenance primitives clear their own gates.
Checked Q2 profit/empty-window entries now also use the same cursor-close API
and match heap output through a 1M 3-run control, but this is API
generalization rather than a new speed win: the 1M median is heap
`4993.892 ms` versus checked `4995.946 ms`, and checked RSS rises to
`142.4 MiB`. The next safe direction is to understand the append-window
footprint/regression or reduce checked Q1 process overhead before migrating
more DEBS paths. The first NEXMark-lite matrix now broadens Phase 6 beyond
DEBS: Q1 conversion and checked Q2 selection are modest 1M wins, generic Q8
window join is a stronger checked win, Q0 passthrough is a near tie, and Q5
hot-items loses. The follow-up `StreamJoinWindow` API factors Q8 into a
reusable checked operator; packed counts narrowed its 1M checked row to
`20.987 ms`, but it is still slower than the fair specialized heap control
at `17.393 ms`, while reducing GC and RSS. Q5 diagnostics show top scanning is a shared
cost rather than the checked-specific loss. The additive `StreamWindowFold`
follow-up then removed measured GC and lowered RSS, but failed the focused 1M
speed gate (`118.726 ms` checked versus `103.244 ms` heap). This supports
building reusable region-backed stream/join/window operators, but every
specialized API needs a fair heap counterpart and a focused passing gate before
it becomes performance evidence or feeds Common Crawl WET. The Common
Crawl-like checked q1/q2 follow-up now confirms this rule at application
scale: `rift-checked` places `137000000` ordinary records in checked
child-bucket regions and beats heap, but q1 `5088.712 ms` and q2
`5061.479 ms` are still slower than improved SafeZone and trusted Rift. Treat
that as checked-overhead evidence, not a checked application win.

Current checked SafeZone-backed backend checkpoint:
`RiftRegion.streamingSafeZone(...)` now exists as a benchmark-only checked
backend entrypoint. It preserves the checked Rift programming model while
delegating object allocation to SafeZone allocator internals; child buckets
opened from a SafeZone-backed parent use the same backend. V1 supports object
allocation and close, while raw byte allocation and reset are explicitly
unsupported. The focused `CheckedAppendWindowMatrix` backend gate passes:
1M `rift-checked-safezone-32k` is `29.444 ms` versus current
`rift-checked-api-cursor` at `30.922 ms`, with matching checksum and no RSS
regression. The Common Crawl-like application follow-up improves current
checked q1/q2 by `4.9-5.7%` at 1M, but misses the application gate against
trusted Rift/improved SafeZone. Treat this as backend feasibility evidence,
not a final checked application-speed claim.

Current checked page/token append checkpoint:
`RiftRegion.StreamPageTokenAppendWindow[T]` is now the first checked operator
that removes a targeted set of runtime costs justified by static lifetime
ownership. The operator owns bucket lookup, child-region caching, append, and
close, so the hot path avoids per-record `bucket.child.checkOpen()`, per-record
`streamBucketRegion(...)`, stale-current `isOpen` checks, page-token-owned
generic leftover-drain close work, and repeated close/open work for monotonic
same-bucket streams when the current bucket is the only live bucket while
keeping public low-level APIs defensive. New
stale-bucket probes and compiler guards validate the boundary. After the
2026-05-07 batch-close fast path, validation is `sandbox3_next/compile`
passed, compiler tests `118/118`, and runtime tests `50/50`; after the
no-drain close API, runtime tests pass `51/51`. Focused 1M rows are heap
`36.920 ms`, `rift-checked-page-token` `29.319 ms`, and SafeZone-backed
checked page-token `27.549 ms`; chunk-token remains slower. Generated Common
Crawl-shaped q1/q2 still pass the checked application-shaped gate, and the
fast-path 100k regression makes SafeZone-backed checked page-token fastest on
both q1 (`370.758 ms`) and q2 (`377.482 ms`). DSPBench Fraud q2 had a dirty
direction-check row where checked scoped page-token was fastest (`818.574 ms`
versus heap `862.834 ms`), but the committed-code rerun is more conservative:
trusted Streaming `788.040 ms`, checked scoped page-token `810.770 ms`, and
heap `820.945 ms`. Treat generated WET-shaped rows as
memory-pressure evidence, Fraud q2 as modest real-input regression evidence,
and keep the remaining checked page-token CPU path as a profiling target.

The first native samples of the checked page-token path confirm that target:
Common Crawl-shaped q2 at 2M pages shows `closeRecords` /
`StreamAppendCursor.nextOrNull`, `appendWindowOwnedOpen`, backend allocation
and zeroing, `allocImpl/checkOpen`, and token-hash/query work as the visible
costs. Do not spend more time on bucket-open tuning unless a new diagnostic
contradicts this.

Post-fast-path selected 1M sweep:
`evidence/POST_FAST_PATH_SELECTED_SWEEP_2026_05_07.md` reruns selected rows
from the current dirty checkpoint. Dataflow SELECT remains a strong page-token
win (`18.572 ms` scoped checked page-token vs heap `28.942 ms` and improved
SafeZone `22.463 ms`). NEXMark Beam-default q3/q8/q9/q11 all have checked
Rift fastest in the same-run selected pass. Generated Common Crawl-shaped
q1/q2 strengthen the checked page-token story at 1M: checked scoped page-token
is `3840.668 ms` on q1 and `3839.158 ms` on q2, versus heap `5618.631 ms` and
`5303.179 ms`, with heap spending about `1.6 s` timed GC in both queries. This
does not change the status of rank/fold/chunk operators; it strengthens the
final-candidate status of `checked-page-token` and the scoped checked backend.

Current cheap operator-family checkpoint:
The first reusable-family slice is wired and has focused 1M-shape 3-run rows,
and has now been followed by staged headline batches recorded in
`evidence/COMPREHENSIVE_SWEEP_2026_05_06.md`. `PageTokenMapFilter[T]` is now
a real reusable SELECT/filter/project API; focused medians are `19.881 ms` for
the Rift checked backend and `18.214 ms` for the scoped backend, versus current
checked `20.844 ms`, improved SafeZone/scoped rooted `23.025 ms`, and heap
`27.872 ms`; the latest staged headline rerun records scoped page-token SELECT at
`18.458 ms` and Rift page-token SELECT at `20.479 ms`. `RegionList[T]` is now
a real reusable linked-topology API; the
ListOfLists checked builder rerun is `5927.385 ms`, faster than the earlier
benchmark-local checked builder around `9.2-9.4 s` and earlier heap rows around
`14.8-15.4 s`. `EpochFold[T]` is implemented and correct, but the first true
reusable Dataflow AGGREGATE row is `92.923 ms` in the latest staged headline run, so it remains gated; the older
`38.399-38.991 ms` aggregate row should be treated as exact-array checked
aggregate evidence, not `EpochFold` evidence. The next roadmap gate is
lower-overhead fold/epoch operators after `EpochBuffer` and
`TransactionRegion`. `EpochBuffer` passed a focused 1M gate, and
`TransactionRegion` is validated as a useful multi-list control, but direct
`RiftRegion.epoch` now supersedes it for the current StreamFlex-shaped
multi-stage pipeline and for local Stancu-style transaction batches. StreamFlex
scoped direct epoch is `163.339 ms` at 1M versus heap `218.582 ms`; Stancu
scoped direct epoch is `160.198 ms` at 1M versus heap `225.798 ms` and
improved SafeZone `186.122 ms`. Real hash/join/rank/median operators
remain open.

Current fixed-chunk append checkpoint:
`StreamChunkAppendWindow[T]` is implemented as an operator-owned fixed
object-array chunk variant, and it has compiler/runtime probes. It is correct
but failed the speed gate. At 1M, `rift-checked-chunk-token` is `34.273 ms`
versus linked page-token `28.452 ms`, and SafeZone-backed chunk-token is
`33.108 ms` versus SafeZone-backed page-token `27.214 ms`. The fair heap
chunk control is also slower than normal heap (`45.363 ms` versus
`37.748 ms`). Keep chunk-token as negative/control evidence; do not integrate
it into Common Crawl, GH Archive, or DEBS until a workload needs random access
or much larger page-local payloads.

Current generic buffer checkpoint:
`CheckedRegionBufferMatrix` now decomposes growable-buffer overhead from raw
checked allocation. At 10 x 100k records, `rift-checked-array` is
`18.574 ms`, fixed `ObjectBuffer` is `25.788 ms`, and growable
`RegionBuffer` is `29.968 ms`; pre-sizing `RegionBuffer` to the epoch size
improves it to `25.980 ms`, roughly tied with `ObjectBuffer`, but both still
trail the exact-array path. This keeps the next Phase 7 direction concrete:
known-size stream operators should use checked operator-owned array/chunk fast
paths, `ObjectBuffer` should be the bounded ergonomic fallback, and
`RegionBuffer` should stay the growable fallback until its access/layout cost
is addressed by a focused patch.

Current post-UnsafeZone direction:
SafeZone-family internals are now a serious runtime-substrate candidate, but
the first cost run says the next target should be safer than blindly rootless
UnsafeZone-HP. `SAFEZONE_COST_MATRIX.md` and
`sandbox/run_safezone_cost_matrix.sh` decompose root bookkeeping, page-size,
reclaim/sort, and page/chunk allocation costs for SafeZone-family modes. The
headline diagnostic run shows current SafeZone root removal is the old cliff,
but improved roots plus 32 KiB pages match or beat `unsafe-hp-32k` on traced
GCBench, linked ListOfLists, flat ListOfLists, and trace-mode Common Crawl q1.
The `unsafe-hp-32k` Common Crawl q1 pathology does not reproduce in non-trace
q1/q2, so it is an instrumentation-sensitive warning rather than a normal-run
result. The leading prototype direction remains improved SafeZone with explicit
32 KiB/page-size or chunk-root configuration, with rootless UnsafeZone-HP
retained as an unsafe lower-bound control. `SAFEZONE_HP_BACKEND_PROTOTYPE.md`
and `CHECKED_SAFEZONE_BACKEND_MATRIX.md` now record the first checked
SafeZone-backed backend result: useful focused speedup, insufficient
application-scale speedup. Common Crawl WET-shaped q2/q3 probes now have
100k/1M generated medians: q2 is a GC-heavy SafeZone-family win, while q3 is a
negative scratch-shape control.

Phase 0 is not "final." It is complete enough for GCBench and ListOfLists, but
not for a final pipeline or application story.

## 3. Phase 0: Baseline And Comparison Contract

Goal: establish trustworthy local baselines and explicit prior-work comparison
targets before making claims.

Completed:

- GCBench 5-run matrix: Immix, current SafeZone, improved SafeZone, Rift HPZone.
- ListOfLists 5-run matrix: Immix, current SafeZone, improved SafeZone, Rift
  HPZone.
- GCBench topology rerun.
- Cleaned raw-array pipeline surrogate.
- Literature-review comparison contract covering Broom, StreamFlex, Yak,
  Stancu et al., Tofte-Talpin/MLKit, Hallenberg-Elsman-Tofte,
  Reggio/Verona, and Pony/Orca.

Key local baseline medians:

| Benchmark | Immix | Current SafeZone | Improved SafeZone | Rift HPZone |
|---|---:|---:|---:|---:|
| GCBench | 203.514 ms | 684.517 ms | 223.770 ms | 161.641 ms |
| ListOfLists linked | 15085.511 ms | 138171.998 ms | 10132.854 ms | 6951.331 ms |

Exit criteria:

- Baseline commands are checked in.
- Results state run counts and environment variables.
- Surrogates are labeled as surrogates.
- The comparison section in `DESIGN.md` stays visible in future docs.

Remaining:

- Add Commix where it is a meaningful comparison.
- Stabilize current uncommitted work into a commit or patch boundary.
- Do not treat the pipeline surrogate as a tracked-source reproduction.

## 4. Phase 1: Standalone Allocator Bootstrap

Goal: prove the slab allocator core before in-tree integration.

Status: done as historical provenance, not active architecture.

Evidence:

- Old bootstrap tree: `/Users/siyaoliu/rift/rift-bootstrap`.
- Recorded microbench results show Rift HPZone allocation around `2.1 ns`
  p50 and close/free around `3000 ns` p50 for 100000 allocations.

Do not redo:

- Do not restart implementation from the standalone scaffold.
- Use it only for provenance or focused allocator sanity checks.

## 5. Phase 2: In-Tree Runtime And Compiler Path

Goal: make Rift a real Scala Native runtime/compiler path.

Completed or partially completed:

- `nativelib/src/main/resources/scala-native/rift/RiftRuntime.c`
- `nativelib/src/main/resources/scala-native/rift/RiftRuntime.h`
- `nativelib/src/main/scala/scala/scalanative/memory/RiftRegion.scala`
- `nativelib/src/main/scala/scala/scalanative/runtime/RiftAllocator.scala`
- Scala 2/3 companion surface.
- Compiler primitive and lowering for `region.alloc(new T(...))`.
- `RiftRegionTest` recorded as passing `5/5`.
- SafeZone baseline correction in `MemoryPool.c`, `Zone.c`, and
  `GCRoots.c`.

Exit criteria:

- Full API/header consistency, including stats functions or an explicit choice
  to keep them private.
- Dedicated compiler-plugin regression tests.
- Broader Scala Native test subset beyond `RiftRegionTest`.
- No untracked implementation files for the core runtime/API.

Risks:

- `RiftRuntime.h` does not currently declare all stats functions used by Scala
  externs.

## 6. Phase 3: Runtime-Only Evaluation

Goal: establish whether the runtime claim stands before relying on layout or
library redesign.

Completed enough:

- GCBench: Rift HPZone `161.641 ms` vs heap `203.514 ms` and improved SafeZone
  `223.770 ms`.
- ListOfLists linked: Rift HPZone `6951.331 ms` vs heap `15085.511 ms` and
  improved SafeZone `10132.854 ms`.

Interpretation:

- Same-layout runtime wins exist.
- Old SafeZone pathologies reproduce in the current fork for linked one-region
  shapes.
- Improved SafeZone is much stronger and must remain a baseline.
- The cleaned pipeline does not currently show Rift separation.

Remaining:

- Add Commix where supported.
- Keep the runtime claim scoped to workloads where measurements support it.
- Do not use layout-specialized results to prove same-layout runtime speed.

## 7. Phase 4: Topology And Layout Decomposition

Goal: separate allocator wins from topology wins and data-layout wins.

Completed enough:

- Linked, chunked, and flat ListOfLists layout study.
- One-region, nested, and mixed rooted topology study.
- Exit summary tying runtime, layout, topology, and safety findings together.

Key results:

| Mode | Linked ms | Chunked ms | Flat ms |
|---|---:|---:|---:|
| Immix heap | 15260.875 | 2636.480 | 1766.295 |
| current SafeZone | 136016.922 | 4835.904 | 1735.453 |
| improved SafeZone | 9824.936 | 2369.108 | 1743.161 |
| Rift HPZone | 7278.150 | 2463.674 | 1515.091 |

Key findings:

- Layout is first-order for every runtime.
- Rift still has a runtime win on linked allocation-heavy structures.
- The flat Rift cliff was a runtime bug and was fixed.
- The first chunked layout does not clearly beat improved SafeZone.
- Mixed rooted heap-values is not a Rift win.
- Unrooted region-to-GC references are unsafe because the GC does not scan Rift
  regions.

Exit criteria:

- Phase 4 is complete enough to move to Phase 5.
- The safety finding must be tested and designed around in Phase 7/8.

## 8. Phase 5: Application Evidence And DEBS 2015

Goal: produce real application-level evidence that region memory reduces the
dominant allocation and GC costs in a streaming workload.

Current status:

- `bench/debs2015` scaffold exists.
- Q1 and Q2 run simultaneously on sorted bounded real NYC taxi samples.
- Heap, Rift HPZone, and Rift Streaming outputs match after stripping only the
  measured latency column.
- Instrumented runs report GC collection counters, RSS, and Rift counters.
  With `SCALANATIVE_GC_ALLOC_STATS=1`, they also report heap allocation-call
  counts, rounded heap bytes, and measured heap allocation-call time.
- The RunBoth hot path now uses a shared byte parser. Heap mode uses a heap
  input byte buffer; Rift modes allocate the same run-lifetime input buffer in
  a region. The parser avoids `String.split`, per-row `Option`, per-row `Trip`,
  per-row line strings, and per-row taxi/timestamp substrings in the RunBoth
  path.
- Q1 now uses a shared bucketed-window implementation for heap and Rift. Heap
  allocates the same bucket-entry class with `new`; Rift allocates it with
  `region.alloc` and closes the per-timestamp region at bucket eviction.
- Q2 now uses the same shared-backend shape for profit-window and empty-taxi
  window entries. Heap allocates the same entry classes with `new`; Rift
  allocates them with `region.alloc` and closes each per-timestamp region at
  window eviction.

Current limitation:

- Current Rift DEBS region-allocates Q1 and Q2 window entries using the same
  bucketed algorithms as heap.
- Q1 replaced boxed route-count and route-rank `HashMap`s with a shared
  primitive open-addressed route table. Heap allocates the backing arrays with
  `new`; Rift modes allocate them in the run-lifetime ranking/control region.
- Q1 replaced the heap `TreeSet` ranking index with a shared indexed binary
  heap over ordinary `RankedRoute` Scala objects. Heap allocates the index
  arrays with `new`; Rift modes allocate those arrays, plus `RankedRoute`,
  `Route`, and `Cell` objects, in the run-lifetime ranking/control region.
- Q2 replaced boxed per-cell `HashMap` tables for active profits, empty counts,
  latest sequence, and current ranked area with fixed arrays over the bounded
  grid key space. Heap allocates those arrays and `ProfitStats` with `new`;
  Rift modes allocate them in the run-lifetime ranking/control region.
- Q2 replaced `latestEmptyByTaxi` with a growable dense array indexed by the
  existing `TaxiIds` integer key. Heap allocates the array with `new`; Rift
  modes allocate it in the run-lifetime ranking/control region.
- Q2 replaced the heap `TreeSet` ranking index with a shared indexed binary
  heap over `ProfitableArea` objects. Heap allocates the index arrays with
  `new`; Rift modes allocate them in the run-lifetime ranking/control region.
- Q2 replaced durable taxi-id `String` interning and a heap `HashMap` with a
  shared byte-backed taxi-id table. Heap allocates the table, entries, and
  taxi-id byte arrays with `new`; Rift modes allocate them in the run-lifetime
  ranking/control region. This avoids unscanned region-to-GC `String`
  references in Rift entries.
- RunBoth latency collectors now use shared primitive buffers. Heap uses heap
  arrays; Rift modes allocate backing arrays in the snapshot region and copy
  final metrics arrays out before region close.
- Returned top-k arrays are cached by exact size and reused. In Rift modes the
  cached arrays are region-allocated; RunBoth previous-output snapshots also
  have a heap/Rift allocation-placement split, with Rift snapshots allocated in
  a run-lifetime snapshot region.
- Output formatting now writes directly to `Writer` through shared code and
  avoids hot per-row `StringBuilder.toString` and Q2 `f""` formatting.
- Q2 median scratch arrays are region-backed in Rift modes and reused with
  capacity growth. Q2 ranking uses packed primitive cell keys internally.
- Q2 top-10 extraction now uses a shared conservative cache. Heap and Rift use
  the same invalidation logic; Rift's difference remains allocation placement
  for the region-managed ranking/control state.
- Therefore current DEBS has bounded-sample Rift wins and lower RSS, plus
  allocation-attribution evidence that heap allocation work drops when
  structured-lifetime objects move into regions. It does not yet establish the
  final application claim because the controls below remain open.

Current provisional evidence:

| Run | Heap | Rift HPZone | Rift Streaming |
|---|---:|---:|---:|
| 1M RunBoth elapsed | 21658.215 ms | 22314.989 ms | 22184.467 ms |
| 1M instrumented elapsed | 22827.882 ms | 22366.285 ms | 22810.687 ms |
| 1M instrumented GC time | 1051.752 ms | 1003.171 ms | 1012.489 ms |
| 100k after Q2 windows, elapsed | 1837.501 ms | 1794.929 ms | 1843.627 ms |
| 100k after Q2 windows, region objects | 0 | 294284 | 294284 |
| 100k after Q2 profit values, elapsed | 1816.773 ms | 1791.195 ms | 1802.942 ms |
| 100k after Q2 median scratch, elapsed | 1881.304 ms | 1920.875 ms | 1937.911 ms |
| 100k after Q2 median scratch, region resets | 0 | 171197 | 171197 |
| 100k after per-trip scratch reset, elapsed | 1748.744 ms | 1775.350 ms | 1768.716 ms |
| 100k after per-trip scratch reset, region resets | 0 | 87438 | 87438 |
| 100k after primitive Q2 ranking keys, elapsed | 1813.074 ms | 1863.806 ms | 1832.249 ms |
| 100k phase share after primitive Q2 ranking keys, Q2 process | 48.6% | 48.8% | 48.9% |
| 100k after region-backed input buffer, elapsed | 1557.171 ms | 1703.600 ms | 1591.372 ms |
| 100k after region-backed input buffer, read+parse share | 9.6% | 8.8% | 9.4% |
| 1M after region-backed input buffer, elapsed | 18692.484 ms | 17789.410 ms | 17280.431 ms |
| 1M after region-backed input buffer, GC time | 731.171 ms | 644.394 ms | 643.015 ms |
| 1M median after region-backed input buffer, elapsed | 17047.611 ms | 17119.396 ms | 17210.458 ms |
| 1M median after region-backed input buffer, GC time | 684.338 ms | 640.062 ms | 628.808 ms |
| 1M single after region ranking/result snapshots, elapsed | 16363.012 ms | 17243.387 ms | 17301.238 ms |
| 1M single after region ranking/result snapshots, GC time | 601.615 ms | 503.198 ms | 529.115 ms |
| 1M single after region ranking/result snapshots, Rift op time | 0.000 ms | 933.640 ms | 936.641 ms |
| 1M single after region ranking/result snapshots, peak RSS | 1148436480 | 1088684032 | 1088618496 |
| 100k 3-run median after reusable ranking arrays, elapsed | 1286.990 ms | 1262.091 ms | 1265.775 ms |
| 100k 3-run median after reusable ranking arrays, GC time | 61.087 ms | 35.098 ms | 35.855 ms |
| 100k 3-run median after reusable ranking arrays, Rift op time | 0.000 ms | 1.430 ms | 1.420 ms |
| 1M 3-run median after reusable ranking arrays, elapsed | 14633.019 ms | 14234.470 ms | 14392.097 ms |
| 1M 3-run median after reusable ranking arrays, GC time | 513.199 ms | 457.726 ms | 478.912 ms |
| 1M 3-run median after reusable ranking arrays, Rift op time | 0.000 ms | 13.003 ms | 14.166 ms |
| 1M 3-run median after reusable ranking arrays, peak RSS | 813105152 | 876101632 | 876101632 |
| 100k 3-run median after Q2 cell tables, elapsed | 1037.748 ms | 997.997 ms | 983.928 ms |
| 100k 3-run median after Q2 cell tables, GC time | 45.193 ms | 33.453 ms | 32.947 ms |
| 100k 3-run median after Q2 cell tables, Rift op time | 0.000 ms | 1.745 ms | 1.349 ms |
| 100k 3-run median after Q2 cell tables, peak RSS | 217137152 | 172113920 | 172097536 |
| 1M 3-run median after Q2 cell tables, elapsed | 11471.085 ms | 11442.637 ms | 11477.431 ms |
| 1M 3-run median after Q2 cell tables, GC time | 478.636 ms | 419.658 ms | 428.339 ms |
| 1M 3-run median after Q2 cell tables, Rift op time | 0.000 ms | 11.759 ms | 11.421 ms |
| 1M 3-run median after Q2 cell tables, peak RSS | 609730560 | 490766336 | 490799104 |
| 100k 3-run median after Q1 primitive route table, elapsed | 1067.019 ms | 1031.787 ms | 1026.118 ms |
| 100k 3-run median after Q1 primitive route table, GC time | 46.067 ms | 31.820 ms | 32.090 ms |
| 100k 3-run median after Q1 primitive route table, Rift op time | 0.000 ms | 1.911 ms | 1.877 ms |
| 100k 3-run median after Q1 primitive route table, peak RSS | 217038848 | 174833664 | 174833664 |
| 1M 3-run median after Q1 primitive route table, elapsed | 11957.721 ms | 11659.223 ms | 11739.195 ms |
| 1M 3-run median after Q1 primitive route table, GC time | 463.555 ms | 397.162 ms | 398.268 ms |
| 1M 3-run median after Q1 primitive route table, Rift op time | 0.000 ms | 15.102 ms | 15.164 ms |
| 1M 3-run median after Q1 primitive route table, peak RSS | 433209344 | 381222912 | 381190144 |
| 100k 3-run median after Q2 latest-empty taxi table, elapsed | 1072.361 ms | 1005.303 ms | 996.131 ms |
| 100k 3-run median after Q2 latest-empty taxi table, GC time | 47.078 ms | 31.095 ms | 31.187 ms |
| 100k 3-run median after Q2 latest-empty taxi table, Rift op time | 0.000 ms | 2.161 ms | 2.136 ms |
| 100k 3-run median after Q2 latest-empty taxi table, peak RSS | 217071616 | 174964736 | 174964736 |
| 1M 3-run median after Q2 latest-empty taxi table, elapsed | 11649.547 ms | 11263.680 ms | 11188.144 ms |
| 1M 3-run median after Q2 latest-empty taxi table, GC time | 487.774 ms | 381.099 ms | 382.734 ms |
| 1M 3-run median after Q2 latest-empty taxi table, Rift op time | 0.000 ms | 14.536 ms | 14.991 ms |
| 1M 3-run median after Q2 latest-empty taxi table, peak RSS | 609304576 | 381501440 | 381501440 |
| 100k 3-run median after Q2 array-backed ranking, elapsed | 1005.710 ms | 965.099 ms | 947.514 ms |
| 100k 3-run median after Q2 array-backed ranking, GC time | 45.375 ms | 30.805 ms | 30.700 ms |
| 100k 3-run median after Q2 array-backed ranking, Rift op time | 0.000 ms | 1.981 ms | 1.932 ms |
| 100k 3-run median after Q2 array-backed ranking, peak RSS | 216858624 | 176029696 | 176013312 |
| 1M 3-run median after Q2 array-backed ranking, elapsed | 11202.975 ms | 10808.901 ms | 10804.756 ms |
| 1M 3-run median after Q2 array-backed ranking, GC time | 423.932 ms | 348.901 ms | 344.376 ms |
| 1M 3-run median after Q2 array-backed ranking, Rift op time | 0.000 ms | 14.861 ms | 14.684 ms |
| 1M 3-run median after Q2 array-backed ranking, peak RSS | 431718400 | 383631360 | 383631360 |
| 100k 3-run median after Q2 taxi-id table, elapsed | 793.461 ms | 787.594 ms | 785.273 ms |
| 100k 3-run median after Q2 taxi-id table, GC time | 18.122 ms | 23.902 ms | 19.621 ms |
| 100k 3-run median after Q2 taxi-id table, Rift op time | 0.000 ms | 1.443 ms | 1.421 ms |
| 100k 3-run median after Q2 taxi-id table, peak RSS | 199983104 | 69402624 | 69402624 |
| 1M 3-run median after Q2 taxi-id table, elapsed | 9876.359 ms | 9676.525 ms | 9667.365 ms |
| 1M 3-run median after Q2 taxi-id table, GC time | 376.602 ms | 358.127 ms | 270.482 ms |
| 1M 3-run median after Q2 taxi-id table, Rift op time | 0.000 ms | 13.216 ms | 13.915 ms |
| 1M 3-run median after Q2 taxi-id table, peak RSS | 431751168 | 169312256 | 169295872 |
| 100k 3-run median after Q1 indexed ranking, elapsed | 903.449 ms | 874.280 ms | 863.219 ms |
| 100k 3-run median after Q1 indexed ranking, GC time | 19.414 ms | 18.821 ms | 18.578 ms |
| 100k 3-run median after Q1 indexed ranking, Rift op time | 0.000 ms | 1.820 ms | 1.778 ms |
| 100k 3-run median after Q1 indexed ranking, peak RSS | 184090624 | 43024384 | 43024384 |
| 1M 3-run median after Q1 indexed ranking, elapsed | 9746.536 ms | 9441.064 ms | 9442.026 ms |
| 1M 3-run median after Q1 indexed ranking, GC time | 312.151 ms | 320.025 ms | 306.311 ms |
| 1M 3-run median after Q1 indexed ranking, Rift op time | 0.000 ms | 10.528 ms | 10.094 ms |
| 1M 3-run median after Q1 indexed ranking, peak RSS | 431669248 | 108445696 | 108969984 |
| 100k 3-run median after output snapshots, elapsed | 829.612 ms | 811.389 ms | 815.476 ms |
| 100k 3-run median after output snapshots, GC time | 18.383 ms | 18.242 ms | 20.286 ms |
| 100k 3-run median after output snapshots, Rift op time | 0.000 ms | 1.615 ms | 1.604 ms |
| 100k 3-run median after output snapshots, peak RSS | 184107008 | 44613632 | 44597248 |
| 1M 3-run median after output snapshots, elapsed | 8983.464 ms | 8815.087 ms | 8836.488 ms |
| 1M 3-run median after output snapshots, GC time | 290.712 ms | 292.155 ms | 296.305 ms |
| 1M 3-run median after output snapshots, Rift op time | 0.000 ms | 10.053 ms | 10.061 ms |
| 1M 3-run median after output snapshots, peak RSS | 431652864 | 119865344 | 119898112 |
| 100k 3-run median after Q2 incremental medians, elapsed | 619.735 ms | 626.609 ms | 610.258 ms |
| 100k 3-run median after Q2 incremental medians, GC time | 8.091 ms | 5.839 ms | 5.781 ms |
| 100k 3-run median after Q2 incremental medians, Rift op time | 0.000 ms | 1.518 ms | 1.573 ms |
| 100k 3-run median after Q2 incremental medians, peak RSS | 97370112 | 40173568 | 40173568 |
| 1M 3-run median after Q2 incremental medians, elapsed | 5976.447 ms | 5794.879 ms | 5948.755 ms |
| 1M 3-run median after Q2 incremental medians, GC time | 67.086 ms | 59.658 ms | 55.056 ms |
| 1M 3-run median after Q2 incremental medians, Rift op time | 0.000 ms | 10.737 ms | 11.172 ms |
| 1M 3-run median after Q2 incremental medians, peak RSS | 305758208 | 113950720 | 113934336 |
| 100k single after Q2 top-10 cache, elapsed | 628.690 ms | 550.082 ms | 553.841 ms |
| 100k single after Q2 top-10 cache, top-10 recomputes | 4189 | 4189 | 4189 |
| 100k single after Q2 top-10 cache, top-candidate comparisons | 144949 | 144949 | 144949 |
| 1M single after Q2 top-10 cache, elapsed | 5367.670 ms | 5149.720 ms | 5191.038 ms |
| 1M single after Q2 top-10 cache, GC time | 68.932 ms | 35.475 ms | 35.887 ms |
| 1M single after Q2 top-10 cache, Rift op time | 0.000 ms | 11.813 ms | 12.376 ms |
| 1M single after Q2 top-10 cache, peak RSS | 305627136 | 116604928 | 116588544 |
| 1M single after Q2 top-10 cache, top-10 recomputes | 29983 | 29983 | 29983 |
| 100k 3-run median after Q2 top-10 cache, elapsed | 607.176 ms | 571.465 ms | 590.900 ms |
| 100k 3-run median after Q2 top-10 cache, GC time | 9.254 ms | 5.348 ms | 5.093 ms |
| 100k 3-run median after Q2 top-10 cache, Rift op time | 0.000 ms | 2.677 ms | 2.620 ms |
| 100k 3-run median after Q2 top-10 cache, peak RSS | 102350848 | 41500672 | 41500672 |
| 1M 3-run median after Q2 top-10 cache, elapsed | 6192.692 ms | 5697.948 ms | 5657.424 ms |
| 1M 3-run median after Q2 top-10 cache, GC time | 70.762 ms | 36.231 ms | 36.288 ms |
| 1M 3-run median after Q2 top-10 cache, Rift op time | 0.000 ms | 18.824 ms | 21.925 ms |
| 1M 3-run median after Q2 top-10 cache, peak RSS | 304463872 | 116588544 | 96239616 |
| 1M single allocation attribution, GC alloc calls | 19924383 | 14462042 | 14462060 |
| 1M single allocation attribution, GC alloc bytes | 679841024 | 455349920 | 455350304 |
| 1M single allocation attribution, GC alloc time | 582.629 ms | 385.807 ms | 384.031 ms |

Checked RunBoth median addendum:

| Run | Heap | Rift HPZone | Rift Streaming | Rift checked |
|---|---:|---:|---:|---:|
| 100k checked RunBoth median, elapsed | 553.059 ms | 529.613 ms | 512.808 ms | 508.056 ms |
| 100k checked RunBoth median, GC time | 9.541 ms | 0.000 ms | 0.000 ms | 0.077 ms |
| 100k checked RunBoth median, peak RSS bytes | 55459840 | 38895616 | 38912000 | 39878656 |
| 1M checked RunBoth median, elapsed | 5363.257 ms | 5224.005 ms | 5209.104 ms | 5043.240 ms |
| 1M checked RunBoth median, GC time | 21.226 ms | 0.834 ms | 0.862 ms | 2.473 ms |
| 1M checked RunBoth median, peak RSS bytes | 159989760 | 116867072 | 116850688 | 123977728 |
| 1M checked allocation attribution, GC alloc calls | 6025149 | n/a | n/a | 752568 |
| 1M checked allocation attribution, GC alloc bytes | 235159840 | n/a | n/a | 28785632 |
| 1M checked allocation attribution, GC alloc time | 173.578 ms | n/a | n/a | 20.514 ms |

Commix control addendum:

| Run | Commix heap | Commix Rift checked |
|---|---:|---:|
| 100k median elapsed | 492.372 ms | 472.477 ms |
| 100k median GC time | 4.942 ms | 0.092 ms |
| 100k median peak RSS bytes | 56885248 | 39534592 |
| 1M median elapsed | 4968.773 ms | 4745.291 ms |
| 1M median GC time | 8.206 ms | 1.137 ms |
| 1M median peak RSS bytes | 158924800 | 125698048 |

This is a 3-run bounded-sample control. Commix makes the heap GC collection
baseline smaller than Immix, but checked Rift still wins elapsed time and RSS
in the local 100k/1M medians. The elapsed delta remains much larger than the
GC collection-time delta, so the interpretation is allocation-placement and
object-churn reduction, not only shorter GC pauses.

Full-month control addendum:

| Run | Heap | Rift checked |
|---|---:|---:|
| month 1 full parsed rows | 14776529 | 14776529 |
| month 1 full invalid rows | 86 | 86 |
| month 1 full elapsed | 69.754 s | 1258.714 s |
| month 1 full external real time | 69.78 s | 1258.76 s |
| month 1 full external user+sys time | 69.64 s | 63.97 s |
| month 1 full GC time | 0.288 s | 0.143 s |
| month 1 full peak RSS | 624902144 bytes | 1029373952 bytes |
| month 1 full region objects | 0 | 68834523 |
| month 1 full opens/closes | 0 / 0 | 6890164 / 6890164 |

This is a single-run full-month correctness and scale diagnostic, not a
performance result. Heap and checked Rift outputs matched after stripping
latency, but the checked process reported only about `64 s` user+sys CPU time
for about `1259 s` real time. Future full-month controls must use the new
external `time_real_s`, `time_user_s`, and `time_sys_s` summary columns and run
under controlled load before making speed claims.

Streaming first-slab and pool-cap follow-up:

| Run | Before cap | After cap |
|---|---:|---:|
| checked full-month external real time | 1258.76 s | 70.87 s |
| checked full-month user+sys time | 63.97 s | 68.86 s |
| checked full-month GC time | 0.143 s | 0.166 s |
| checked full-month peak RSS | 1029373952 bytes | 887078912 bytes |
| checked full-month closed-slab pool | 780.4 MiB | 128.0 MiB |
| checked full-month cumulative Rift mmap | 932.5 MiB | 864.4 MiB |
| checked full-month Rift op time | 0.679 s | 0.998 s |

The follow-up runtime change is backend-wide: streaming regions now start with
a page-sized first slab and the global closed-slab pool is capped at `128 MiB`.
It does not specialize DEBS or change the Q1/Q2 logical program. The post-cap
full-month checked run has credible wall/user/sys alignment and heap-equivalent
output, but it is still one checked-only full-month run. Treat it as the first
usable full-scale checked data point, not a final full-DEBS speed claim.

Same-run full-month pool-cap control:

| Run | Heap | Rift checked |
|---|---:|---:|
| month 1 full elapsed | 71.919 s | 77.947 s |
| month 1 full external real time | 71.96 s | 77.98 s |
| month 1 full user+sys time | 69.58 s | 74.24 s |
| month 1 full GC time | 0.323 s | 0.190 s |
| month 1 full peak RSS | 607240192 bytes | 728940544 bytes |
| month 1 full Rift op time | 0.000 s | 1.137 s |
| month 1 full closed-slab pool | 0.0 MiB | 128.0 MiB |

This same-binary run matched heap and checked Q1/Q2 outputs after stripping
latency. It was the first same-binary full-month heap/checked pool-cap control:
checked was about `6.0 s` slower than heap, while reducing measured GC
collection time by about `0.13 s` and keeping RSS much closer to heap than the
pre-cap checked run. It is historical context for the later `ChildBucket`
follow-up, and remains a single run, not a median.

Checked `ChildBucket` single-control-object follow-up:

| Run | Heap | Rift checked / streaming |
|---|---:|---:|
| full-month trusted Streaming elapsed | 73.888 s | 68.990 s |
| full-month trusted Streaming GC time | 0.360 s | 0.088 s |
| full-month trusted Streaming peak RSS | 624623616 bytes | 840646656 bytes |
| 1M checked after `ChildBucket` change, elapsed | 4.810 s | 4.678 s |
| full-month checked after `ChildBucket` change, elapsed | 70.872 s | 65.928 s |
| full-month checked after `ChildBucket` change, GC time | 0.315 s | 0.086 s |
| full-month checked after `ChildBucket` change, peak RSS | 614891520 bytes | 908656640 bytes |

Same-order 3-run median after the `ChildBucket` change:

| Metric | Heap | Rift checked |
|---|---:|---:|
| full-month elapsed | 73.029 s | 67.670 s |
| full-month external real time | 73.06 s | 67.69 s |
| full-month user+sys time | 71.05 s | 67.18 s |
| full-month GC time | 0.315 s | 0.086 s |
| full-month peak RSS | 586.4 MiB | 866.6 MiB |
| full-month Rift op time | 0.000 s | 0.885 s |
| full-month Q1 process time | 20.507 s | 19.233 s |
| full-month Q2 process time | 22.154 s | 20.142 s |

This follow-up changes the checked API shape rather than the DEBS algorithm:
`ChildBucket` now owns its child region directly, avoiding one extra
`ChildWindow` heap control object per bucket. The full-month evidence is now a
same-order 3-run median, and checked is faster by `5.359 s` (`~7.3%`) on
elapsed time. The result is still noisy: one checked repeat was slower
(`75.100 s` checked versus `73.166 s` heap), and the reverse-order heap row was
invalid due descheduling. RSS did not improve; checked median RSS is
`866.6 MiB` versus heap `586.4 MiB`, with one checked repeat reaching
`983.9 MiB`. Treat this as elapsed/checker-overhead evidence, not a memory
footprint win.

Immediate next step:

- Preserve benchmark fairness before adding more region code. Heap and Rift
  variants should be the same logical program with allocation/lifetime policy
  as the variable, not separate hand-specialized algorithms.
- The input-buffer median rerun is complete. The single-run Rift win after the
  byte-reader change did not hold as a median: Rift reduced GC time, but region
  operation time offset it.
- The first ranking/result-region experiment showed that resettable top-k
  snapshot regions are the wrong lifetime shape.
- The follow-up reusable ranking-array backend removed that reset churn and made
  Rift region-operation time small again. The current 1M 3-run median has Rift
  HPZone faster than heap, but this remains bounded-sample evidence with an RSS
  tradeoff; later checkpoints add SafeZone 1M controls, but broader full-month
  and safe-API controls still matter.
- The Q2 cell-table step replaced boxed per-cell maps with a shared bounded
  array layout. It improves both heap and Rift, and Rift modes place those
  arrays and `ProfitStats` in a region. The 1M HPZone median is only slightly
  faster than heap, but it reduces median GC by about `59 ms` and peak RSS by
  about `119 MB` with low Rift operation time.
- The Q1 route-table step replaced boxed route maps and immutable `RouteState`
  churn with a shared primitive table. It lowers Q1 processing and GC/RSS, but
  total elapsed remains Q2-dominated and is not a clean cross-checkpoint speedup
  over the Q2-cell-table median.
- The Q2 latest-empty taxi-table step replaced a heap map with a shared dense
  array over existing taxi IDs. It improves Q2 processing and gives the
  strongest bounded-sample DEBS result so far, while keeping Rift operation time
  around `15 ms` at 1M.
- The Q2 array-backed ranking step replaced Java `TreeSet` ranking nodes with a
  shared indexed heap over ordinary `ProfitableArea` objects. Heap and Rift use
  the same ranking algorithm; Rift modes allocate the ranking index arrays in
  the run-lifetime ranking/control region. The 1M HPZone median is
  `394.074 ms` faster than heap and Rift operation time stays around `15 ms`.
- The Q2 taxi-id table step replaced heap `HashMap`/`String` taxi-id metadata
  with a shared byte-backed table. Heap and Rift use the same table; Rift modes
  allocate table arrays, entries, and taxi-id byte copies in the run-lifetime
  ranking/control region. The 1M medians are now heap `9876.359 ms`, HPZone
  `9676.525 ms`, and Streaming `9667.365 ms`, with Streaming GC at
  `270.482 ms` vs heap `376.602 ms` and peak RSS around `169 MB` for Rift.
  Because the byte-backed representation also improves heap, cross-checkpoint
  elapsed improvements are not pure Rift effects.
- The Q1 indexed-ranking step replaced the remaining Q1 heap `TreeSet` ranking
  nodes with a shared indexed heap over ordinary `RankedRoute` objects. Heap
  and Rift use the same ranking algorithm; Rift modes allocate ranking arrays
  and the ranking object graph in the run-lifetime ranking/control region. The
  1M medians are heap `9746.536 ms`, HPZone `9441.064 ms`, and Streaming
  `9442.026 ms`; peak RSS drops from `431669248` bytes to about `108-109 MB`
  in Rift modes. GC time is mixed: Streaming is slightly below heap, HPZone is
  slightly above heap.
- The output-snapshot placement step moved Q1/Q2 previous-output snapshots into
  a run-lifetime region in Rift modes while keeping the changed-output logic
  shared. It is valid placement evidence but not a clean GC-time win: 1M
  medians are heap `8983.464 ms`, HPZone `8815.087 ms`, and Streaming
  `8836.488 ms`, with GC roughly flat/slightly higher in Rift and RSS around
  `120 MB`.
- The Q2 incremental-median step replaced dirty-cell copy/sort recomputation
  with shared per-cell two-heap median maintenance. Heap and Rift use the same
  Q2 algorithm; Rift modes allocate the `ProfitStats` and median heap arrays in
  the run-lifetime ranking/control region. The 1M medians are heap
  `5976.447 ms`, HPZone `5794.879 ms`, and Streaming `5948.755 ms`; HPZone is
  `181.568 ms` faster than heap, Streaming is `27.692 ms` faster, GC drops to
  `59.658 ms`/`55.056 ms`, and RSS is about `114 MB` for Rift.
- The Q2 rank/output attribution step adds change-check timers, snapshot
  timers, rank comparison/swap counters, top-candidate comparison counters,
  and changed-output comparison counters. On the 100k validation run, snapshots
  are about `0.7 ms`, Q2 changed checks are about `18-19 ms`, and
  top-candidate extraction accounts for about `4.45M` of `5.08M` Q2 rank
  comparisons. A small binary top-candidate heap was tried and rejected before
  commit because it increased comparisons.
- The Q2 top-10 cache step is the first fix based on those attribution
  counters. It keeps heap and Rift on the same logical query algorithm and
  avoids recomputing the top-10 frontier when the rank update cannot affect the
  cached result. The 100k single-run validation reduced top-candidate
  comparisons from `4.45M` to `144949`; the 1M single-run validation recomputed
  top 10 `29983` times out of `1000000` calls. The 3-run medians confirm the
  direction at bounded scale: at 1M, heap is `6192.692 ms`, HPZone is
  `5697.948 ms`, and Streaming is `5657.424 ms`; GC drops from `70.762 ms` to
  about `36 ms`, and Rift RSS is much lower. One 1M HPZone run was slower than
  heap, so this is still bounded-sample evidence, not final DEBS proof.
- The GC heap allocation-attribution step adds a separate diagnostic axis for
  memory-management overhead. `gc_time_ns` is only collection time; attribution
  mode shows the cost of ordinary heap allocator calls as well. At 1M, Rift
  removes about `5.46M` heap allocation calls and `224 MB` of rounded heap
  allocation requests, and measured heap allocation-call time falls by about
  `197-199 ms`. Because this mode times every heap allocation, its elapsed
  timings are diagnostic rather than headline throughput numbers.
- The checked RunBoth median step moves the earlier checked Q1/Q2 standalone
  probes into the shared RunBoth loop and records 100k/1M medians. At 1M,
  checked is fastest in the local matrix (`5043.240 ms`) versus heap
  `5363.257 ms`, trusted HPZone `5224.005 ms`, and trusted Streaming
  `5209.104 ms`. The result-array counters are zero for checked Q1/Q2, but
  checked and trusted backends still differ in implementation shape.
- The checked allocation-attribution step confirms the memory-management
  direction for checked RunBoth. At 1M, checked reduces heap allocation calls
  from `6025149` to `752568`, rounded heap bytes from `235159840` to
  `28785632`, and measured heap allocation-call time from `173.578 ms` to
  `20.514 ms`; the remaining visible heap allocations are mostly output and
  primitive snapshot/control paths.
- The active-memory diagnostic shows the remaining full-month RSS problem is
  not primarily closed-slab retention. In the checked-only full-month
  diagnostic, peak active requested bytes are `823153856`, peak active mapped
  bytes are `904790016`, final active bytes are zero, and final mapped bytes
  are near the `128 MiB` pool cap. Per-family attribution then found a concrete
  wrong lifetime: Q1 checked rank object graphs were allocated in the parent
  checked stream. Moving those ordinary Scala rank objects into Q1 child bucket
  regions cuts the full-month checked active requested peak to `180948200`
  bytes and RSS to `613318656` bytes in a checked-only diagnostic, without
  changing the logical Q1 query.
- The post-fix full-month 3-run control confirms the memory fix at production
  scale but not a large speedup: checked median elapsed is `66.804 s` versus
  heap `67.122 s`, checked median RSS is `613.3 MiB` versus heap `595.9 MiB`,
  and checked median GC collection time is `0.117 s` versus heap `0.285 s`.
  Checked still pays `0.779 s` median Rift region-op time and slower Q1/Q2
  process CPU phases.
- A closeable SafeZone mode now exists for Q1/Q2 data-structure placement. The
  100k controls and 1M 3-run medians match heap output for
  `SAFEZONE_ROOTS_MODE=0` and `SAFEZONE_ROOTS_MODE=1`. SafeZone lowers RSS
  versus heap in the 1M medians but remains slower than heap and checked Rift.
  Full-month SafeZone controls are optional follow-up.
- Opt-in process diagnostics now cover the checked Q1/Q2 CPU question without
  replacing clean medians. With `DEBS2015_PROCESS_DIAGNOSTICS=1`, the
  full-month row shows identical Q2 operation counts between heap and checked;
  the checked overhead is not a different median/rank algorithm. Q1's main
  checked-shape difference is rank-object refresh: checked creates `14487771`
  region rank objects at full-month scale versus heap's `6195167` durable rank
  objects, matching the `14487771` rank refreshes.
- A narrower opt-in Q2 CPU substep diagnostic now times the same Q2 operations
  in heap and checked modes behind `DEBS2015_Q2_CPU_DIAGNOSTICS=1`. On the
  bounded 1M diagnostic row, checked Q2 process time is `1327.500 ms` versus
  heap `1438.062 ms`, with recorded Q2 CPU substeps `1142.533 ms` versus heap
  `1246.509 ms` and matching Q2 operation counts. This is attribution-only
  because `System.nanoTime()` probes perturb hot Q2 code, but it means bounded
  same-operation Q2 overhead is not currently reproduced.

Implementation substeps:

- Treat input/parser cleanup as shared noise reduction unless the only
  allocation-placement difference is explicit, as with the current heap input
  buffer vs Rift region input buffer.
- Keep Q1 heap and Rift algorithms aligned. Any future Q1 optimization must be
  shared by both modes unless the only difference is allocation placement.
- Q2 profit and empty-taxi windows now have heap and Rift backends over the
  same algorithm.
- Q2 active profit values now live in window entries instead of a heap
  `ArrayBuffer`; Q2 median scratch arrays are region-backed in Rift modes and
  reused rather than reset per processed trip.
- Q1 route-table arrays now have a heap/Rift allocation-placement split over
  the same primitive open-addressed layout. Q1 still uses a heap `TreeSet` for
  ranking order. This is trusted HPZone benchmark code, not the final safe
  mixed-reference story.
- Q1/Q2 ranking objects now have a heap/Rift allocation-placement split.
- Q2 bounded cell tables now have a heap/Rift allocation-placement split over
  the same fixed-array layout. This is acceptable Phase 5 evidence because Q2's
  grid key space is bounded by the benchmark and both modes use the same
  logical structure.
- Q2 latest-empty taxi state now has a heap/Rift allocation-placement split over
  the same growable dense-array layout.
- Q2 ranking now has a heap/Rift allocation-placement split over the same
  indexed-heap layout. The ranked values are ordinary `ProfitableArea` Scala
  objects; the ranking index arrays are region-backed in Rift modes.
- Q2 taxi-id metadata now has a heap/Rift allocation-placement split over a
  shared byte-backed hash table. This deliberately avoids storing heap `String`
  references in region entries.
- Q1 ranking now has a heap/Rift allocation-placement split over a shared
  indexed-heap layout. The ranked values are ordinary `RankedRoute`, `Route`,
  and `Cell` Scala objects; the ranking index arrays and objects are
  region-backed in Rift modes.
- Primitive keys and packed cell/route IDs remain acceptable only as shared
  noise cleanup or as temporary boundaries where mixed-reference safety is not
  implemented.
- RunBoth input bytes now have a heap/Rift allocation-placement split over the
  same byte parser. Single-query Q1/Q2 runners still use the older file input
  path and are not the source of Phase 5 input-buffer evidence.
- Do not add more reset-per-event region scratch paths; the superseded
  snapshot-result experiment showed they can replace GC as the bottleneck.
- Do not add a separate hand-specialized heap-only Q1/Q2 implementation. The
  useful Q1 indexed-ranking checkpoint kept heap and Rift on the same logical
  algorithm, then changed allocation placement by mode.
- Use primitive keys and packed cell/route IDs only when the change is shared
  across modes or needed to avoid unsafe region-to-GC references.
- Keep heap roots explicit for any heap object referenced from region memory.
- Rerun 100k and 1M instrumented matrices with medians after each change that
  looks promising in a single run. The superseded resettable snapshot-result
  numbers are diagnostic only; the current reusable-array backend has 100k and
  1M medians.
- Q1 checked rank-refresh churn now has a bounded window-rank arena fix:
  ordinary `CheckedRankedRoute`/`CheckedRoute`/`CheckedCell` objects live in
  coarser rank arenas, not per-second event buckets or a parent stream. The
  `StreamBucketArena` primitive now generalizes the bucket lifetime layer. The
  `StreamWindowIndexedRank` primitive now generalizes the dense-key ranking
  layer. The `putWindowRankInBucket` auto-cleanup path now moves key-unlinking
  into the framework close path, but the focused matrix shows this stronger
  boundary is slower than heap and slower than the earlier manual-cleanup path.
  The entry-cleanup path removes the duplicate checked-side bucket key list and
  improves the focused default checked median from `313.572 ms` to `302.001 ms`,
  but it is still not a speed win. The follow-up remove-with-value close
  primitive simplifies unlinking and validates already-popped-key cleanup, but
  it did not produce a measured speedup. The long-key stream-window rank shape
  now exists and has focused 100k/1M matrix measurements. It removes the
  packed-route-key/dense-remap blocker, but the 1M checked-long mode is slower
  and higher-RSS than heap-long, so the next step is container CPU/memory
  reduction before broad Q1 route-key integration. Bounded Q2
  same-operation overhead should not be optimized further until a clean or
  full-month diagnostic identifies a specific substep.
- Scale to full-month joined/sorted data only after the bounded samples have a
  stable region-heavy implementation.

Exit criteria:

- Both queries run simultaneously and correctly.
- Results include medians for throughput, p50/p99/p99.9 latency, GC time, RSS,
  and Rift operation time.
- At least one Rift mode reduces GC time or tail latency for a reason traceable
  to region-backed application data structures.
- The writeup separates runtime-only, topology/layout, and application effects.

Do not claim Phase 5 success until these criteria are met.

## 9. Phase 6: Literature-Aligned Methodology And API Evidence

Goal: compare Rift against literature-shaped workloads while preserving the
separation between runtime-only effects, topology/layout effects, and
static-safety ambitions. These are local methodology reproductions unless an
original artifact is available.

Current status:

- `evidence/DATAFLOW_REGION_MATRIX.md` records Broom-style
  SELECT/AGGREGATE/JOIN methodology workloads over ordinary Scala objects.
- `evidence/STREAMFLEX_REGION_MATRIX.md` records StreamFlex-style throughput
  and per-event latency/deadline-miss workloads.
- `evidence/YAK_REGION_MATRIX.md` records Yak-style word-count, graph-step,
  external-sort-shaped grouped sort, top-word/filter, GraphChi-like subinterval
  updates, and promotion/escape epoch/control-data
  split workloads. It now includes a `yak-runtime` proxy for a pure
  runtime-managed epoch discipline on Scala Native and a
  `RiftRegion.RuntimeEpoch` memory API for rare escaping data objects.
  Top-word/filter gives a strong local raw Rift-vs-heap win and a modest
  Rift-vs-improved-SafeZone win; GraphChi-like subintervals give a strong
  Rift-vs-heap win but still trail improved SafeZone; grouped sort gives a
  modest raw Rift-vs-heap win while sorting dominates elapsed time; the
  promotion proxy removes measured heap GC but is slower than heap on elapsed
  time at the current pressure size.
- `evidence/STANCU_REGION_MATRIX.md` records Stancu-style
  transaction/accounting workloads. A 2026-04-26 boundary sweep confirms that
  one transaction per region is too fine-grained, while 64 transactions per
  region gives a Rift-vs-heap win; SafeZone remains faster.
- `docs/STANCU_SPECJBB2005_PORT_PLAN.md` defines the stronger
  SPECjbb2005-workload port target, and
  `evidence/SPECJBB2005_PORT_MATRIX.md` now records the first clean-room
  Scala Native port rows. Official JVM controls, Scala Native workload-port
  rows, and Stancu paper-axis reproduction metrics remain separate evidence
  classes.
- `sandbox/PIPELINE_PARCOLL_COMPARISON.md` records the amordo
  `ZoneParVector` benchmark and the Rift raw-array surrogate.
- `evidence/REML_COMPARISON_MATRIX.md` starts Phase 6c for the MLKit/ReML
  lineage. It currently contains the Elsman 2023 paper table as
  paper-reported/not-rerun evidence, a Scala Native `ReMLRegionMatrix` scaffold
  for Tier 1 ReML-shaped ports (`fib37`, `tak`, `mandel`, `msort`, `msort-r`,
  `life`, `fft`, `ratio`), and the claim boundary that exact ReML comparison
  requires original artifacts/configurations.
- The comparison is explicitly not apples-to-apples.

Required work:

- Keep the Broom/Yak/StreamFlex/Stancu harnesses clearly labeled as
  methodology reproductions and avoid comparing absolute speedups to paper
  systems with unavailable artifacts.
- Build a `RiftParVector`, region-backed stage buffer, or equivalent
  collection/operator API.
- Reproduce the amordo pipeline shape using the Rift API, not raw arrays.
- Compare heap `ParVector`, amordo `ZoneParVector`, SafeZone, and Rift under the
  same logical API.
- Track annotation burden, release/reset ergonomics, and any capture-checking
  rejection/fallback cases.

Exit criteria:

- Literature-shaped benchmark notes include commands, run counts, data sizes,
  medians, GC/Rift operation metrics, RSS where collected, and caveats.
- Rift has a fair Broom/parallel-collections API comparison, not only a raw
  array surrogate.
- Results state whether wins come from allocator runtime, topology/lifetime
  boundaries, data layout, or lower-level array loops.

### Phase 6c: ReML / MLKit Lineage Comparison

Goal: add a second comparison axis beyond stream/dataflow. ReML/MLKit matters
because it stresses region polymorphism, higher-order code, and tracing-GC
safety for non-stream programs. This should not replace the stream-processing
story; it should clarify whether Rift's checked object/lifetime model also
handles the classic typed-region benchmark regime.

Current status:

- Paper-reported ReML Figure 9 numbers are transcribed in
  `evidence/REML_COMPARISON_MATRIX.md`. They are literature anchors only, not
  local measurements.
- `sandbox/src/main/scala-next/ReMLRegionMatrix.scala` and
  `sandbox/run_reml_region_matrix.sh` implement the first Scala Native
  ReML-shaped Tier 1 matrix.
- Local smoke rows for Tier 1 matched checksums. The `ratio` smoke now retains
  region objects so checked allocation is not optimized away.
- A 2026-05-06 Tier 1 3-run median matrix has been recorded. `msort`,
  `msort-r`, and `ratio` are the meaningful allocation/RSS rows:
  `checked-region-stream` is `104.358 ms` on `msort` versus heap
  `124.983 ms`, `104.929 ms` on `msort-r` versus heap `126.163 ms`, and
  `checked-region-scoped` is `48.929 ms` on `ratio` versus heap `51.302 ms`.
  `fib37`, `tak`, `mandel`, and `life` are mostly compute/control rows.
- ReML-inspired compiler probes now reject the previously ignored generic
  heap-retention case: heap generic `Cell[Box^{region}]`, widened `AnyRef`,
  heap-array retention, and escaping closure hiding are rejected when they flow
  into durable/static heap state. Local nonescaping polymorphic use remains
  legal.

Required work:

- Keep Tier 1 interpreted as Scala Native ReML-shaped port evidence. Report
  relative region-vs-heap ratios, RSS, GC, and checked overhead; do not compare
  raw wall-clock to ReML paper numbers.
- Compare overlapping Scala Native benchmark families where useful. In
  particular, `scala-native-benchmarks` has a Mandelbrot-style benchmark that
  can serve as an additional Scala Native control for the ReML `mandel` family
  once configuration differences are documented.
- Search for exact MLKit/ReML benchmark provenance. The public MLKit repo is
  cloned in ignored cache and has likely paper-era tags, but host `mlkit`/
  `mlton` are missing and Docker is not running. If exact artifacts are not
  available, mark exact reproduction unavailable and keep Scala Native ports
  labeled as methodology-shaped evidence.
- If exact artifacts are found, rerun the paper configurations for `rg`,
  `rg-`, `r`, and MLton, recording source provenance, tool versions, commands,
  run counts, real time, RSS, and GC counts.
- Add Tier 2 ports only after Tier 1 is interpreted.
- Extend the current durable/static generic-retention check into a broader heap
  alias story, or explicitly document the API boundary, before making rootless
  checked safety claims.

## 10. Phase 7: Capture-Checked Safe API

Goal: make `Scoped` and `Streaming` regions safe by construction rather than by
convention.

Required work:

- Define user-facing safe APIs for scoped and streaming regions. First slice is
  implemented as `RiftRegion.scoped`, `RiftRegion.streaming`, and
  `RiftRegion.reset`.
- Add positive compile/run tests for for-loops, nested regions, and
  higher-order code. Compiler probes now cover for-loop allocation, nested
  scoped regions, and a local higher-order consumer.
- Add negative compile tests for return escape, closure capture escape,
  cross-region leakage, use-after-reset, GC-to-region fields, and unrooted
  region-to-GC ownership. Current probes cover return escape, a heap singleton
  retaining a scoped value, a closure that captures the region handle, nested
  inner-region leakage, streaming reset escape, returned function values, and
  the positive explicit-root path for region-to-GC metadata. Direct unrooted
  heap-object constructor arguments are now rejected in checked Rift allocation
  lowering; simple region-local aliases are allowed, while heap aliases and
  heap field selections are rejected. Static module singletons and immutable
  module vals are allowed as independently rooted metadata, while mutable
  static vars are rejected. Stable constructor fields with source type
  `T^{region}` are allowed; plain `T^` fields selected from a region owner are
  rejected by Scala capture checking when `T^{region}` is required.
  Region-owned arrays are allowed when reference elements are explicitly
  captured, for example `Array[T^{region}]^{region}`; stores into known region
  arrays reject unrooted heap objects. Mutable local linked-list heads are
  allowed when their observed assignments are `null`, direct Rift allocations,
  or already-known region values; assigning a heap object drops the provenance
  and is rejected if the head is later stored into region memory. Checked
  owner-token containers now include fixed-capacity `ObjectBuffer` and
  growable `RegionBuffer`; both accept region objects and `HeapRoot` handles,
  reject direct heap stores, and reject values from an inner region stored into
  an outer buffer. `CheckedRegionBufferMatrix` is the first benchmark-shaped
  safe-API harness using `RegionBuffer` rather than trusted `RiftRegion.open`.
  `RegionPriorityQueue` covers append/pop ranking and
  `RegionIndexedPriorityQueue` covers dense-key fetch/mutate/update ranking.
  `RegionLongIndexedPriorityQueue` covers the same checked ranking shape for
  arbitrary `Long` keys, using region-owned heap arrays plus a region-owned
  open-addressed index table. `StreamWindowLongIndexedRank` composes it with
  `StreamBucketArena` close cleanup for bucket-owned long-key entries.
  The first focused long-key matrix validates matching heap/checked checksums
  but shows overhead rather than a speed win, so it is a measurement gate before
  DEBS integration rather than an application result.
  `CheckedRegionIndexedPriorityQueueMatrix` is the first focused harness for
  durable keyed region state with ordinary mutable Scala objects.
  `CheckedStreamWindowRankMatrix` is the first focused stream-window rank
  harness above `StreamBucketArena`; it validates child-bucket region records
  plus parent rank state but currently loses elapsed time to heap.
  `DataflowRegionMatrix` now also has checked safe-API modes for SELECT,
  AGGREGATE, and JOIN, including a region-owned aggregate table and
  RegionBuffer-backed SELECT/JOIN outputs.
- Create or update `REPORT_CAPTURE_CHECK.md` with exact checker behavior. The
  first report slice is filled in from the 2026-04-26 targeted compiler run.
- Decide whether current Scala 3 capture checking is enough or whether the fork
  needs a small compiler extension.

Exit criteria:

- Positive cases compile and run.
- Negative cases fail for capture/safety reasons, not incidental type errors.
- Any checker limitation is documented and reflected in the design. Current
  documented limitations are conservative rejection of direct function results,
  incomplete higher-level-container mixed-reference modeling beyond the current
  owner-token buffers,
  limited ergonomics for plain selected fields and array element captures,
  local-only mutable-head provenance, the need for owner-token container
  methods, and the need for broader negative probes as new checked shapes are
  added.

Comparison obligation:

- Show why the API is less restrictive than StreamFlex and Reggio but safer
  than Broom and HPZone.
- Count annotations and compare qualitatively to Stancu-style `@RegionScope`
  and Reggio capability annotations.

## 11. Phase 8: Native GC/Region Integration Hardening

Goal: resolve mixed GC-region safety and native-runtime compatibility.

Required decisions:

- Should safe regions forbid owning region-to-GC references?
- Should Rift expose explicit GC-root handles for heap values stored in regions?
  First v1 answer: yes, through `RiftRegion.HeapRoot[T]` and
  `RiftRegion.root(value)`.
- Should region metadata be scanned by the GC?
- Should typed-region metadata eventually support BIBOP-style layout or
  tag-free scanning?

Required tests:

- Region-to-GC reference retained only by region memory must fail statically or
  be kept alive by explicit root/scan machinery. The explicit-root path now has
  compiler and runtime smoke coverage; direct unrooted heap-object constructor
  arguments and simple heap aliases/field selections now fail in checked
  allocation lowering. Static module singletons and immutable module vals are
  allowed; mutable static vars are rejected. Stable constructor fields
  explicitly captured by `{region}` are allowed. Stores into known region-owned
  arrays are checked. Owner-token `ObjectBuffer` and `RegionBuffer` appends are
  checked with the same heap/root and cross-region rules.
  Mutable local region heads preserve provenance across `null`, direct Rift
  allocations, and known region values, but heap assignment invalidates that
  provenance.
- GC-to-region references through heap fields must fail for safe regions.
- HPZone versions of these cases must be labeled unsafe/trusted.

Exit criteria:

- The mixed reference story is explicit in design, tests, and benchmarks.
- Native/non-moving assumptions remain valid.
- No copying collector is introduced into Scala Native's C interop path.

## 12. Phase 9: Lean Mechanization

Goal: mechanize the core safety story.

Required model:

- Syntax for functions, closures, allocation, region open, close, reset, and
  capture sets.
- Two-space store: GC heap plus region heaps.
- Typing judgment with capture sets.
- Operational semantics for allocation and close/reset.
- A model of GC fallback sufficient to state containment.

Required theorems:

- Progress.
- Preservation.
- Containment.
- Safe close/reset.

Exit criteria:

- Core theorems are proved without `sorry`.
- The model covers at least one higher-order closure case, because that is where
  the literature review identifies prior proof fragility.

## 13. Phase 10: Writing

Goal: turn the artifact into a defensible research narrative.

Expected structure:

- Literature gap and comparison contract.
- Baseline correction and why old SafeZone numbers were incomplete.
- In-tree runtime/compiler implementation.
- Runtime-only evidence.
- Topology/layout decomposition.
- Application evidence from region-heavy DEBS and collection operators.
- Capture-checking safety.
- Lean proof.
- Limitations and failure cases.

Do not write the conclusion before Phase 5, Phase 7, and Phase 9 have real
evidence.

## 14. Immediate Safe Next Action

After the clean headline stream and bounded DEBS legs, the safest technical
next action is:

1. Treat real enwiki clickstream, real Common Crawl WET, and official Linear
   Road preloaded rows as ceiling/regression evidence. Heap is fastest and
   median measured GC is `0.000 ms`, although Wikimedia and Linear Road heap
   1M logs have sporadic collection outliers, so they should not drive
   application-specific tuning.
2. Keep NEXMark Beam-default Q3 as the current best checked
   application-profile check, with Q8 as a checked near-tie and Q0/Q1/Q2/Q5/Q9
   as trusted or lower-GC profile rows. Generated Common Crawl WET-shaped Q1 is
   the current GC-heavy detector, but improved SafeZone wins elapsed time.
   Yahoo and RIoTBench should be regression controls rather than active case
   studies until their 1M rows improve.
3. Return to focused checked-operator overhead work. The highest-value target
   is a cheap checked map/filter/output or join-window primitive with a fair
   specialized heap control, not more DEBS/TableRank integration.
4. Preserve the fair-backend rule: same logical query algorithm, heap backend
   with `new`, Rift backend with `region.alloc`, and region close/reset at the
   same lifetime boundary.
5. Use the real-input ladders as regression controls after operator changes.
   Do not claim a case study unless Rift beats heap and improved SafeZone by
   about `10%`, or materially lowers GC/RSS with at most `5%` elapsed overhead.
6. Use `SCALANATIVE_GC_ALLOC_STATS=1` selectively for attribution, not as a
   default headline benchmark.
7. Continue official Scala Native native profiling before more broad operator
   tuning. The first representative L4 sweep now covers StreamFlex-design,
   Common Crawl-shaped q2, DSPBench Fraud q2, LogHub HDFS top-k, StreamIt
   controls, Dataflow AGGREGATE, SPECjbb2005-workload, ReML-shaped ports, Yak
   input parsing, and generated Yak graphstep epoch-body processing. The
   remaining profiling gap is a delayed/preloaded real LiveJournal processing
   profile if real-input provenance matters for attribution, and larger/delayed
   transaction profiles if transaction tuning resumes.
   Treat profiles as diagnostic-only rows.

Do not move to new runtime micro-optimizations unless a focused benchmark or
application diagnostic points there. The next runtime change needs concrete
evidence comparable to the earlier full-month closed-slab pool signal.

## 15. Unsafe Assumptions To Avoid

- Rift already has final DEBS application proof. The bounded-sample top-cache
  and checked RunBoth medians are encouraging application evidence, and the
  pool-cap/`ChildBucket` follow-up now gives a same-order full-month 3-run
  median. The Q1 rank lifetime fix removes the large checked RSS regression,
  and the Q1 window-rank arena reduces the per-refresh checked-rank churn
  without one child region per route. The reusable `StreamBucketArena`
  primitive and dense-key `StreamWindowIndexedRank` are now implemented, and
  the auto-cleanup path moves bucket-owned rank-key removal into the framework
  close path. The focused stream-window rank matrix is still slower than heap,
  and auto cleanup currently adds CPU overhead versus manual cleanup. The
  entry-cleanup callback reduces that overhead but does not remove it. The
  remove-with-value close primitive simplifies framework unlinking but has no
  measured speed win yet. Hash-key rank collections, optional
  full-month SafeZone controls, and stronger safe API controls are still
  missing. Bounded Q2 same-operation overhead is not currently reproduced by
  the opt-in substep diagnostic.
- `gc_time_ns` captures all memory-management cost. It captures collection
  time only; heap allocation-call cost now has its own opt-in diagnostic
  counters.
- Allocation-attribution elapsed timings are headline results. They are
  intentionally perturbing and should be used for diagnosis.
- SafeZone is solved or irrelevant.
- Layout wins prove allocator wins.
- The raw-array pipeline surrogate is a Broom or `ZoneParVector` replacement.
- Region-to-GC references are safe just because region memory is live.
- Full automatic region inference is realistic for all Scala code.
- Reggio-style capabilities can be copied without paying annotation or topology
  costs.
- The active `origin` remote is the intended `641bill` fork.
