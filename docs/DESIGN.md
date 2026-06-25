# Rift Design

Status: active research design for the Scala Native fork.

Last updated: 2026-06-01 14:54 CEST

Active worktree: `/Users/siyaoliu/rift/scala-native-rift`

Branch: `feature/rift`

Current merge state is tracked in `docs/HANDOFF.md`; the substantive design
revision began at implementation commit `ddbba577aecd4c0adc741cbf7085ee93548c46b4`.

This document supersedes the older standalone-library framing. The older design
pack in `/Users/siyaoliu/rift/Claude_output` is useful provenance, but the
active artifact is the Scala Native fork.

## 1. Objective

Rift is a hybrid region-GC memory system for Scala Native. The intended
contribution is not merely "a faster SafeZone." The target is a system that
combines:

- Fast region allocation and bulk close/reset inside the Scala Native runtime.
- A GC heap for ordinary control objects and objects whose lifetimes are not
  statically predictable.
- Region-managed memory for data-path objects with structured lifetimes.
- Scala-facing region APIs that can eventually be checked by Scala 3 capture
  checking, especially for closures and higher-order code.
- Region-shaped stream and collection libraries that make logical lifetimes
  visible to the allocator.
- A mechanized core safety argument for containment and safe close/reset.

Longer term, Rift should be understood as a Scala-level checked lifetime
topology system with Scala Native as the first backend. The source concepts
(`epoch`, `window`, `page`, `transaction`, `HeapRoot`, active/closed handles,
and capture/separation checks) should be reusable by other Scala backends. What
changes is the lowering:

| Backend | Intended lowering |
|---|---|
| Scala Native | Real region slabs, backend-known checked allocation, bulk close/reset, and proof-gated initialization optimizations. |
| JVM | Experimental object pools, scoped arenas for selected record-like classes, reusable buffers, off-heap/foreign-memory handles where practical, and normal heap fallback. |
| Scala.js | Object pooling/reuse and analysis-guided allocation reduction. |
| Wasm | Linear-memory arenas and bump/reset allocation. |
| Analysis-only | Capture/separation checking with ordinary heap allocation. |

This is now tracked in `docs/SCALA_LEVEL_BACKEND_PLAN.md`. The current
validated implementation and benchmark evidence remain Scala Native only.
Other backend tracks are planned experiments, not completed claims. The
algorithmic reason Scala Native's heap baseline is strong is tracked in
`docs/IMMIX_REGION_COMPARISON.md`: Immix is itself a mark-region collector with
bump-style allocation and line/block reclamation, so Rift's clearest wins are
expected when static lifetime topology avoids tracing retained transient object
graphs or improves RSS/fixed-memory/tail behavior.

### Automatic Region Placement Inference

Rift can grow a ReML-style automatic placement track for Scala Native, but it
should be staged rather than presented as already solved. ReML/MLKit infer
regions for a functional language with an ML-style type/effect discipline.
Scala adds mutable objects, subtyping, arrays, virtual dispatch, closures,
generics erased to runtime classes, and mixed heap/region references, so the
safe path is incremental:

The detailed lineage/evaluation note is
[`docs/REGION_INFERENCE_LINEAGE.md`](REGION_INFERENCE_LINEAGE.md). The short
version is: Rift is ReML/MLKit-inspired, but capture-checking-native and
stream/dataflow-oriented. It should not be described as a full Tofte/Talpin,
MLKit, or ReML whole-program inference implementation yet.

Current 2026-06-01 validation boundary: a later prototype re-enabled broad
automatic local-escape wrapping and GenNIR source-span local-escape placement,
then was gated off by default after it reached ordinary javalib/concurrency
heap allocations too broadly. The child worktree now passes the compiler
checked suite (`718/718`), native runtime checked suite (`322/322`), and
`sandbox3_next` compile with automatic scopes default-off. Automatic
compiler-inserted region scopes are therefore design/prototype work, not a
promoted feature. The validated system remains explicit lifetime boundaries
plus capture-directed placement with heap fallback.

1. **Explicit lifetime, inferred allocation placement.** Inside a checked
   `epoch`, `window`, `page`, or `transaction`, the compiler may lower ordinary
   `new T(...)` to region allocation when capture/separation checks prove the
   object does not escape the lifetime. Non-proven allocations stay on the GC
   heap.
2. **Framework boundary inference.** For checked Rift operators, the compiler
   can use operator signatures to infer that data-path records are epoch/window
   local while durable control state remains heap allocated.
3. **Effect summaries for methods and closures.** Methods, lambdas, and generic
   helpers can carry summaries such as "returns heap value", "returns value
   captured by current region", or "does not retain argument"; this is the
   Scala analogue of ReML-style region effects.
4. **Whole-program or whole-module inference.** Only after the local and
   framework-guided cases are reliable should Rift attempt broader inference of
   lifetime boundaries or automatic migration of allocation sites.

This keeps the user-facing story compatible with prior work: the headline
program remains the natural heap object shape, and the checked Rift version has
the same semantics, but the compiler can remove explicit `alloc(...)` calls
where it can prove that a normal `new` allocation is region-local. The first
implemented slices are intentionally narrow. Direct `new T(...)` sites are
lowered into Rift regions when the expected type is captured by an explicit
checked `ScopedRegion` or `OpenStreamingRegion`. Immutable local direct `new`
values can also be inferred when a captured val/assignment or checked
`RegionList` prepend call supplies a unique region owner. A first method
summary slice also handles direct `new` returned from a method with an explicit
runtime checked-region parameter, such as
`def make(using r: RiftRegion.ScopedRegion^): T^{r} = new T(...)`, and the
returned-local form
`def make(using r: RiftRegion.ScopedRegion^): T^{r} = { val x = new T(...); x }`.
The returned-local method case is validated for both scoped regions and direct
epoch/open-streaming regions. Simple branch-returned direct allocation, such
as `if p then new T(...) else new T(...)`, is also covered when all returned
allocations share the explicit checked region result owner. Branch-returned
local allocations, such as
`if p then { val x = new T(...); x } else { val y = new T(...); y }`, are also
covered under the same explicit checked-region-parameter rule. Simple
match-returned direct and local allocations are now covered under that rule as
well. Captured return
owners that only mention an outer region stay on the heap for now, because the
method body has no runtime region handle. Explicit
owner-token buffer append calls can now infer immutable local direct or
block-final `new` values for checked `ObjectBuffer` and `RegionBuffer`,
including `region.append(...)` extension syntax. The owner-token slice also
covers direct and block-final inline construction at scoped checked
list/buffer boundaries, such as
`prependRegionList(region, list, new T(...))`,
`RiftRegion.append(region, buffer, new T(...))`, and
`region.append(buffer, { ...; new T(...) })`; this covers both fixed
`ObjectBuffer` and growable `RegionBuffer` append paths. Scoped checked priority-queue owner-token
calls can now infer immutable local direct `new` values plus direct and
block-final inline `new` value arguments for `RegionPriorityQueue`,
`RegionIndexedPriorityQueue`, and `RegionLongIndexedPriorityQueue` push/put
boundaries, with runtime allocation stats proving placement. The first
page/window child-owner slice is validated for locals returned by selected
checked child-region helpers such as `pageTokenAppendRegionFor`,
`pageTokenMapFilterRegionFor`, and `pageTokenCountByKeyRegionFor`, so a
bucket-local record can use ordinary `new` when its expected type is captured
by that local child owner. Parent `StreamingRegion` remains excluded from
generic
allocation-owner inference. Captured
`Some(...)` factory allocation is validated through exact `Some` and widened
`Option` expected types; tuple factory allocation is validated for
reference-only `TupleN(...)` arities 2 through 22, with `Tuple2(...)`/tuple
literal syntax as the base proof point and Tuple3 as the first higher-arity
proof point. These shapes are covered as local region-owned values and as
direct or returned-local method-returned values from explicit checked
region-parameter methods, including returned-local `Option = Some(...)` and
returned-local tuple factories. The narrow `None` follow-up validates static
empty `Option` values and `if flag then Some(new T(...)) else None` optional
flows for local expected types and explicit checked region-parameter method
results without allocating for the `None` branch. The null-preserving
`Option.apply(...)` follow-up validates local, method-returned, owner-token
method-argument, and region-owned array-store forms: null stays `None`, while
non-null direct payloads allocate the `Some` branch in the checked region.
The region-owned array-store path now also covers closure objects for direct
inline closures and selected immutable local closure aliases when the array
element type carries the checked owner. Unrooted heap captures remain rejected;
this is closure-object placement at a proven owner boundary, not full
closure/effect inference. Checked owner-token containers now have the same
bounded closure-object proof for `ObjectBuffer`, `RegionBuffer`, and ordinary
`RegionPriorityQueue` value stores; inline and selected immutable local
closure values can be placed when the value type carries the owner, while
unrooted heap captures remain rejected. Checked stream-window rank/table-rank
APIs now have the same bounded closure-object proof for inline and selected
immutable local closure values typed as `Function1[...]^{stream}`; this remains
explicit framework-owner placement, not broad stream topology or closure/effect
inference.
A narrow local generic object
slice is also
validated: `Cell[T^{region}]^{region} = new Cell[T^{region}](value)` is
placed in the checked region when the expected type and value argument prove
the same owner, while widened `AnyRef` escape and unrooted dynamic heap
metadata are rejected. The same generic cell shape is validated through direct
and returned-local explicit checked region-parameter method factories. Broader
container
flow, stream-window rank/table-rank operators, and automatic page/window child
placement beyond explicit child-region locals remain explicit. Generic parent
`StreamingRegion` captures are not inferred yet because page/window operators
need child-bucket placement rather than parent-stream placement. Dynamic heap
metadata still requires `HeapRoot`. `-P:scalanative:riftInferReport` emits
opt-in placement diagnostics for `Region`, `Unknown`, and `Rejected`
decisions. Diagnostics should explain why an allocation stayed on the heap,
especially for heap retention, closure escape, outer-retains-inner,
ReML-style generic hiding, and mutable heap metadata hazards.

The current implementation has only part of that system. The runtime path,
compiler lowering, baseline corrections, benchmark harnesses, and DEBS scaffold
exist. The capture-checked safe API, region-heavy DEBS path, region-backed
parallel collections, and Lean proof are still open.

The latest UnsafeZone-HP and SafeZone cost evidence adds a backend direction,
not a new user-facing mode. Rootless SafeZone with 32 KiB pages is useful as an
unsafe lower-bound substrate probe, but it is not automatically the best next
backend: the first traced cost matrix shows improved SafeZone with 32 KiB pages
matching or beating rootless UnsafeZone-HP on several key rows, and generated
Common Crawl q1 exposes a severe trace-mode `unsafe-hp-32k` pathology that does
not reproduce in non-trace q1/q2. The intended next prototype is therefore a
checked SafeZone-family backend, not necessarily a rootless one: reuse or learn
from SafeZone allocator/pool mechanics only when capture/provenance checks prove
that GC root registration or region scanning is unnecessary, and otherwise
prefer improved-root or chunk-root configurations. Unsupported mixed-reference
cases should be rejected in v1 rather than silently falling back to a different
backend.

The latest Yak `graphreal` topology evidence clarifies the user-facing API
target. Checked regions should not force every workload into the page-token
operator. Programmers should express logical lifetime topology, and Rift should
check and lower that topology:

```scala
Rift.stream {
  epoch {
    // batch/epoch-local data
  }

  window(...) {
    // sliding or tumbling window-local data
  }

  page {
    // page or record-group-local data
  }
}
```

Backend and topology are distinct. A scoped SafeZone-backed checked backend may
be fastest for one row, a streaming reset backend may be better for another,
and page-token is only the right checked operator when the data lifetime is
actually page/window/bucket shaped. The 50M SNAP LiveJournal `graphreal`
follow-up shows this concretely: checked epoch topology gives the low-RSS safe
win, whole-run checked topology is faster but high-RSS, and page-token checked
topology remains safe but slower for Yak because the workload is epochal.
The reusable `EpochBuffer` follow-up turns that into an implementation task:
it is safe and beats heap on LiveJournal, but it trails the benchmark-local
linked epoch path. `RiftRegion.epoch { ... }` is now the direct checked
linked-epoch API: it gives the block an `OpenStreamingRegion`, resets Rift
streaming epochs in bulk, and opens/closes scoped SafeZone-backed child regions
for the scoped backend. Epoch workloads should use this direct topology when
they can consume their object graph inside the epoch; `EpochBuffer` remains for
append/drain API compatibility rather than as the fastest possible epoch
lowering.

## 2. Evidence Levels

Use these labels in all claims:

| Label | Meaning |
|---|---|
| Validated | Backed by checked-in commands, recorded run counts, and matching outputs or tests. |
| Partially validated | Implemented and exercised, but missing full test coverage, medians, or comparison modes. |
| Provisional | Single-run, surrogate, reconstructed, or generated from uncommitted code. |
| Planned | Design target only; no implementation evidence yet. |

Current reliable evidence:

- Phase 0 GCBench and ListOfLists runtime medians are validated enough to use as
  local baseline evidence.
- Phase 4 topology and layout studies are validated enough to move on, with the
  explicit caveat that several results use uncommitted runtime changes.
- DEBS correctness on bounded sorted samples is partially validated.
- DEBS performance is now bounded-sample application evidence, but not a final
  full-DEBS claim. Current phase timers show Q2 processing and output/ranking
  work still matter. With the reusable ranking/result-array backend, Q2
  bounded cell tables, Q1 primitive route table, Q1 indexed ranking, Q2
  latest-empty taxi table, Q2 array-backed ranking index, Q2 taxi-id table,
  RunBoth output snapshots, Q2 incremental median heap arrays, region-backed
  latency buffers, and the shared Q2 top-10 cache, Rift region-operation time
  is a small share of total elapsed time. The latest trusted 1M byte-output
  medians are heap `4640.593 ms`, HPZone `4524.706 ms`, and Streaming
  `4522.308 ms`; GC collection time drops from heap `21.025 ms` to below
  `1 ms` in both trusted Rift modes. Checked RunBoth now has its own 100k/1M
  median matrix: at 1M, heap is `5363.257 ms`, trusted HPZone is
  `5224.005 ms`, trusted Streaming is `5209.104 ms`, and checked is
  `5043.240 ms`. Opt-in `SCALANATIVE_GC_ALLOC_STATS=1` attribution runs show
  the 1M trusted byte-output path dropping from `6,025,143` heap allocation
  calls and `235,159,552` rounded bytes to about `0.56M` calls and `10.5 MB`
  in trusted Rift modes; checked RunBoth drops the same heap baseline to
  `752,568` calls and `28,785,632` bytes. This supports the claim that
  structured-lifetime Scala objects are moving into regions. It does not close
  the SafeZone/full-scale and safe API gaps. A 3-run Commix DEBS control now
  also exists: checked Rift wins elapsed time and RSS at 100k and 1M, while
  reducing measured GC collection time. The first full-month checked RunBoth
  control matched heap output but had invalid checked wall-clock timing. A
  runtime pool-cap control then made full-month checked runs practical. The
  first same-run full-month pool-cap control is heap `71.919 s`, `0.323 s` GC,
  `579.1 MiB` RSS versus checked `77.947 s`, `0.190 s` GC, `695.2 MiB` RSS,
  with matching output. After the `ChildBucket` single-control-object change,
  the same-order full-month 3-run median is heap `73.029 s` versus checked
  `67.670 s`, with GC `0.315 s` versus `0.086 s`; checked RSS regresses
  (`866.6 MiB` median versus heap `586.4 MiB`), and one checked repeat is
  slower. The first active-memory diagnostic narrows the RSS issue: a
  full-month checked-only run reports peak active requested bytes `823153856`,
  peak active mapped bytes `904790016`, final active bytes `0`, and final
  mapped bytes `134479872` against the `128 MiB` pool cap. That means the
  remaining RSS regression is mostly live checked-region payload under current
  lifetimes, not free-slab retention. Per-family attribution then found the
  largest source: Q1 checked rank object graphs were parent-lived. Moving those
  ordinary Scala rank objects into Q1 child bucket regions cuts full-month
  checked active requested peak from `823153856` to `180948200` bytes and RSS
  from `1086668800` to `613318656` bytes in a checked-only diagnostic. A
  follow-up full-month 3-run heap/checked control after this fix matched
  outputs and gives a near-tie elapsed median: heap `67.122 s` versus checked
  `66.804 s`. Checked median RSS is now `613.3 MiB`, close to heap
  `595.9 MiB`; GC collection time drops from `0.285 s` to `0.117 s`, but
  checked pays `0.779 s` median Rift region-operation time and has slower Q1/Q2
  process CPU phases. A closeable SafeZone DEBS mode now exists and matches
  heap output on 100k controls and 1M 3-run medians for both current and
  improved roots modes. At 1M, SafeZone is lower-RSS than heap but slower than
  heap and checked Rift; checked Rift remains fastest and lowest-RSS in both
  SafeZone roots-mode median matrices. Opt-in
  `DEBS2015_PROCESS_DIAGNOSTICS=1` rows now attribute the remaining checked CPU
  shape: Q2 operation counts are identical between heap and checked, while Q1
  checked rank creations rise from `6195167` heap to `14487771` checked at
  full-month scale because checked rank objects are refreshed into child-bucket
  lifetimes. This is still not a final full-DEBS claim because full-month
  SafeZone controls, CPU-overhead reduction, and stronger safe API boundaries
  remain open. A
  route-lifetime child-bucket probe was rejected: it reduced Q1
  rank-object churn but opened one child region per active route, raising 100k
  checked RSS to `113721344` bytes.
- Phase 7 checked API evidence has started. The targeted Scala-next compiler
  suite passed 80/80 for the current `Scoped`/`Streaming` API slice, including
  for-loop allocation, nested scoped regions, local higher-order consumers, and
  direct escape/reset rejection. Returned function values are now rejected
  conservatively because returned closures can hide region-local captures.
  `RiftRegion.root` now provides an explicit `HeapRoot` path for region objects
  that need to refer to heap metadata. Checked allocation lowering now rejects
  direct unrooted heap-object constructor arguments while still allowing
  ordinary region-to-region object graphs, simple region-local aliases, static
  module singletons and immutable module vals, and stable constructor fields
  whose source types are explicitly tied to `{region}`. Mutable static vars are
  rejected. Region-owned arrays are supported as checked containers when the
  array object and reference element type are both explicitly region-captured.
  `RiftRegion.ObjectBuffer` adds a first checked higher-level container, using
  owner-token APIs to keep region data in a region-owned backing array while
  rejecting direct heap and cross-region stores. `RiftRegion.RegionBuffer`
  extends the same rule to a growable checked buffer whose growth arrays are
  allocated in the owner region. `RiftRegion.RegionPriorityQueue` extends the
  owner-token container family to ranking/top-k style state: values live in a
  region-owned object array, priorities live in a parallel region-owned
  primitive array, and heap values are rejected unless explicitly rooted.
  `RiftRegion.RegionIndexedPriorityQueue` adds durable dense-key ranking state:
  one ordinary Scala object can be created per key, fetched, mutated, and
  re-ranked without allocating a new rank object on every refresh.
  `RiftRegion.RegionLongIndexedPriorityQueue` is the hash-keyed counterpart:
  it keeps arbitrary `Long` keys, values, heap priorities, and open-addressed
  index state in region-owned arrays, so route-style packed keys do not need a
  benchmark-specific dense remapping layer before entering checked rank state.
  `RiftRegion.StreamWindowLongIndexedRank` composes that long-key queue with
  `StreamBucketArena`: bucket-owned long-key rank entries are tracked in a
  region-owned owner table and removed before the child bucket closes.
  Raw
  `RiftRegion.childStreaming` plus the
  preferred `RiftRegion.childWindow` wrapper are now first checked
  multi-region building blocks: a child streaming-region handle cannot escape
  its parent stream, and `RiftRegion.childRegion(parent, window)` makes
  deliberate child-to-parent widening explicit. `closeChildWindow(parent,
  window) { cleanup }` adds the first structured close boundary: direct user
  `window.close()` is rejected and child-region reuse after close throws at
  runtime. `RiftRegion.ChildBucket` is now the reusable wrapper for that
  pattern; Q1/Q2 checked processors use `childBucketRegion` and
  `closeChildBucket` instead of carrying raw `ChildWindow` fields. This is not
  a full affine close proof yet. `RiftRegion.StreamBucketArena` now generalizes
  the accepted "fine event buckets plus coarser rank/output arenas" lifetime
  primitive; checked Q1 uses it for rank buckets, and sample plus 100k
  heap/checked RunBoth controls match outputs after migration.
  `RiftRegion.StreamWindowIndexedRank` now composes that bucket-lifetime
  primitive with `RegionIndexedPriorityQueue`, giving stream operators a
  dense-key checked rank/window collection whose values can live in child
  bucket regions. The `putWindowRankInBucket` path records which child bucket
  owns each dense key, and bucket close removes those tracked keys from
  parent-owned rank state before closing the child region. The compiler guard
  rejects direct unrooted heap stores through both `putWindowRank` and
  `putWindowRankInBucket`; standalone dense-key and long-key checked rank
  queues use the same owner-token value-store guard. The focused compiler
  suite is now `80/80`, and the native checked runtime suite is `28/28`. The Q1
  checked-processing probe uses path-dependent bucket event nodes to keep
  child-owned values local before closing the child region at bucket eviction.
  The focused `CheckedRegionBufferMatrix`
  harness now validates this as a benchmark-shaped safe API path: default local
  medians were heap `33.825 ms` with `7.611 ms` GC versus checked Rift
  `28.654 ms` with `0.301 ms` Rift op time and no measured GC. The focused
  `CheckedRegionPriorityQueueMatrix` validates the new checked ranking
  primitive: default local medians were heap `27.369 ms` with `2.160 ms` GC
  versus checked Rift `28.621 ms` with `0.279 ms` Rift op time, no measured GC,
  and lower RSS. `CheckedRegionIndexedPriorityQueueMatrix` validates the next
  keyed-state step: default local medians were heap `100.254 ms` with
  `2.201 ms` GC versus checked Rift `103.052 ms` with no measured GC and
  `0.406 ms` Rift op time. `CheckedStreamWindowRankMatrix` validates the next
  stream-window shape: ordinary Scala records allocated in child bucket
  regions are ranked through checked parent state and automatically unlinked
  before close, with matching heap/Rift checksums. Its entry-cleanup API now
  reports removed rank entries during bucket close so operators can clean their
  side tables without maintaining a duplicate checked-side key list. The current
  remove-with-value close probe keeps this API shape and validates the
  already-popped-key case, but is still a negative speed signal: the latest
  default local median was heap `205.849 ms` versus checked `329.761 ms`,
  although checked uses less RSS and only `0.352 ms` measured Rift operation
  time. The lexicographic priority API now supports Q1-style
  count/time/sequence/key tie-breakers without changing the bucket-close
  discipline, and the long-key stream-window rank API removes the dense-key
  remapping blocker for route-keyed stream-window ranking. The earlier entry-cleanup step improved the previous auto-cleanup median
  (`313.572 ms` checked) but remained slower than the earlier manual-cleanup
  median (`254.050 ms`). Treat these as API/safety evidence and
  overhead diagnostics rather than speed claims.
  Dataflow
  SELECT, AGGREGATE, and JOIN now have checked `rift-checked` modes using the
  same safe API; local checked medians are SELECT `18.865 ms`, AGGREGATE
  `36.003 ms`, and JOIN `18.736 ms`, faster than heap, improved SafeZone, and
  trusted Rift in the same run. Checked DEBS RunBoth now also has bounded
  100k/1M medians; at 1M it is fastest in the local matrix while preserving
  heap-equivalent output, but it still uses trusted helpers for byte-reader and
  output/latency scratch buffers. Both
  `RiftRegion.append(region, buffer, value)` and `region.append(buffer, value)`
  are covered. The latest probes
  cover reset-epoch record arrays, top-word-style rooted metadata buffers,
  GraphChi-style rooted heap metadata, and rejection of reset-epoch values
  stored into outer streaming buffers. Mutable linked-list builders are now
  supported when a local head's observed assignments are `null`, direct Rift
  allocations, or already-known region values; heap-object assignment drops
  that provenance and is rejected when later stored into region memory.
- The raw-array pipeline is a surrogate and must not be presented as a
  replacement for Broom-style or `ZoneParVector` collection evidence.

## 3. What Changed

The original project story over-indexed on replacing SafeZone with a standalone
arena. The fork evidence and literature review require a narrower, stronger
framing:

- SafeZone must remain in the comparison set. `SAFEZONE_ROOTS_MODE=1` changes
  the baseline materially and closes much of the old root-bookkeeping gap.
- Runtime speed still matters. It is not acceptable to explain every win as
  "the data structure changed." Rift must keep same-layout runtime wins.
- Layout and topology are first-order effects. They must be reported separately
  from allocator effects.
- Application evidence must allocate the application's dominant data operations
  in regions. Current DEBS region-allocates Q1/Q2 window entries, Q2 active
  profit values, Q2 median scratch, the RunBoth input buffer, ranking/result
  objects, Q2 bounded cell tables, Q1 primitive route-table arrays, and Q2
  latest-empty taxi arrays, Q2 ranking-index arrays, and Q2 taxi-id table
  entries/bytes, output snapshots, and latency buffers in Rift modes. The
  latest bounded-sample medians show Rift elapsed wins and much lower RSS, and
  allocation attribution shows fewer heap allocation calls/bytes. Full-month
  checked RunBoth now has a post-lifetime-fix heap/checked 3-run median that is
  a near-tie on elapsed time with much better checked RSS than the earlier
  checked run. Closeable SafeZone DEBS controls also exist at 100k and 1M. This
  still does not prove a final application-level win because full-month
  SafeZone controls, richer rank/window collections, checked Q2 same-operation
  overhead explanation, and safe API boundaries are still incomplete.
- The literature-review target is broader than local baselines: Rift must be
  compared against Broom, StreamFlex, Yak, Stancu-style hybrid static analysis,
  the MLKit typed-region lineage, and Reggio/Verona-style capabilities.

## 4. Comparison Contract

Rift should be judged against prior systems on performance, safety,
annotations, support for Scala-like higher-order OO code, closure capture,
native compatibility, and proof obligations.

| Prior system | Main strength | Main limitation | Current Rift addresses | Still needed to surpass or differentiate |
|---|---|---|---|---|
| Broom | Maps dataflow lifetimes to transferable, actor, and temporary regions; reports large synthetic allocation wins. | Prototype has no enforced safety, no formal model, no closure story, and CLR/Bartok dependency. | Rift adopts the dataflow-lifetime insight and has in-fork region allocation plus DEBS scaffolding. | Build a real region-backed operator/collection API, show end-to-end stream wins, and enforce containment statically. |
| StreamFlex | Statically safe zero-GC stream processing with implicit ownership and very low latency. | Domain-specific filter/channel model, primitive-only capsules, no lambdas/closures, no mechanized proof. | Rift targets stream workloads in Scala Native and keeps GC for control objects rather than requiring full heap isolation. | Implement a safe streaming API, prove closure/capture constraints, and show latency/GC-pause evidence on streaming workloads. |
| Yak | Hybrid control-space GC plus data-space regions; dynamic promotion makes epochs safe with very low annotation burden. | Purely dynamic, write-barrier overhead, STW during epoch end, JVM-specific, no formal type story. | Rift adopts the two-space control/data split, and the current Yak-style harness now includes wordcount, graph-step, external-sort-shaped grouped sort, Hadoop-like top-word/filter, GraphChi-like subinterval updates, a Scala Native runtime-safety proxy, and a `RiftRegion.RuntimeEpoch` promotion/escape API with barrier checks, remembered refs, and promoted-copy accounting. | Replace Yak's dynamic safety with static capture checking, then show comparable GC-time reductions without barriers/STW promotion. Current memory-API-level promotion is slower than heap, which strengthens the case for static rejection/checked boundaries. Do not claim exact Yak coverage until there is real field-write barrier or static rejection evidence plus Hyracks/Hadoop/GraphChi-shaped workloads. |
| Stancu et al. `@RegionScope` | Static points-to analysis infers region allocation from few annotations and falls back to GC. | Closed-world whole-program analysis, coarse phases, no higher-order Scala story, no formal proof. | Rift is already compiler-integrated and aims for lightweight region boundaries plus inference. | Implement capture-guided allocation/fallback, count annotations per KLOC, and avoid closed-world assumptions where possible. |
| Tofte-Talpin / MLKit | Deep formal basis, automatic region inference, region polymorphism, zero annotations in ML. | ML-specific, region size problem, unpredictable lifetimes with closures, no Scala subtyping/object model. | Rift borrows region polymorphism and containment as proof targets. | Keep annotation burden low without pretending full Scala inference is tractable; mechanize the higher-order case. |
| ReML / GC-safe MLKit lineage | Shows how region-polymorphic programs can be made safe with tracing GC and reports time, RSS, and GC-count data on classic SML benchmarks. | ML benchmark suite and type system differ from Scala Native; exact comparison requires artifact reproduction. The lineage highlights subtle higher-order/polymorphic soundness hazards. | Rift now has a ReML comparison track, local Scala Native ReML-shaped ports, and active ReML-inspired compiler probes, including generic heap-retention rejection. | Reproduce exact MLKit/ReML artifacts if available, run local Tier 1 medians, and compare relative region-vs-heap effects rather than raw cross-language time. |
| Hallenberg-Elsman-Tofte, PLDI 2002 | Regions plus intra-region GC handle region leaks and preserve region safety. | Copying GC and tags conflict with Scala Native's native/non-moving assumptions; conservative closure restrictions. | Rift keeps a non-moving GC heap and region slabs compatible with native code. | Decide whether safe mixed region/GC references require handles, GC-scanned metadata, or stricter static rejection. |
| Elsman-Hallenberg typed regions | Typed regions enable tag-free layouts and write-barrier-free generational GC. | ML-only, stack discipline, rare mutation, STW, no mechanized proof, later soundness concerns in the lineage. | Rift's native backend could eventually exploit typed-region/BIBOP-style layout information. | This is not implemented. A future phase must define region type metadata and prove layout/GC safety. |
| Reggio / Verona | Static reference capabilities isolate regions and permit per-region memory strategies. | Forest topology, single mutable window, pervasive annotations, limited higher-order support, no mechanized proof. | Rift plans to use capture/separation checking as a lower-annotation capability analogue. | Show multiple active regions and Scala closures can be checked safely without Reggio's annotation burden. |
| Pony / Orca | Actor-local heaps, ownership transfer, no STW pauses or barriers in the actor model. | Actor model is a major programming-model constraint. | Rift can borrow the principle that type-system isolation enables cheaper runtime memory management. | Demonstrate low pause times without requiring users to rewrite code into actors. |
| Scala Native SafeZone | Existing in-tree region-like mechanism with GC root integration. | Current mode has root-bookkeeping pathologies; safety is dynamic/root-based, not capture-proven. | Rift work improved the SafeZone baseline and exposed the relevant runtime costs. | Rift must beat improved SafeZone, not only old SafeZone, and must offer a checked safe path rather than only HPZone. |

The contribution bar is therefore a combination claim:

- Performance: same-layout runtime wins plus application wins where region
  memory covers dominant data operations.
- Safety: statically checked non-escape and safe close/reset for the safe API.
- Ergonomics: far fewer annotations than capability-heavy systems, closer to
  phase-boundary annotations plus capture inference.
- Scala fit: higher-order functions and closures are central, not optional.
- Native fit: non-moving GC assumptions and C interop must remain valid.
- Proof: a mechanized core containment theorem, not only prose.

## 5. Memory Model

Rift uses two memory spaces:

| Space | Purpose | Current status |
|---|---|---|
| `H_GC` | Scala Native heap managed by Immix/Commix for ordinary Scala objects and unpredictable lifetimes. | Existing Scala Native runtime. |
| `H_R` | Rift-managed slab regions for structured-lifetime data objects. | Implemented for HPZone-style allocation in the fork. |

Region modes:

| Mode | Intended meaning | Current status |
|---|---|---|
| `HPZone` | Trusted fast region path for benchmarks and hot loops. No static escape guarantee. | Implemented as a runtime kind and exercised by benchmarks. |
| `Scoped` | Lexically scoped, capture-checked region. | Runtime kind and checked API slice exist; direct function results are conservatively rejected; `HeapRoot` handles provide explicit region-to-GC metadata roots; direct unrooted heap-object constructor arguments are rejected in checked allocation lowering; simple region-local aliases are propagated; static module singletons and immutable module vals are allowed; owner-token `ObjectBuffer` and growable `RegionBuffer` give first checked container primitives. |
| `Streaming` | Resettable streaming region with capture/use-after-reset constraints. | Runtime kind and checked reset wrapper exist; `HeapRoot` handles are cleared on reset/close; the same checked allocation guard applies inside reset epochs; `OpenStreamingRegion` is the internal allocation-capable handle for `allocOpen`, and checked user code can no longer call `close()` or `reset()` through that handle; open allocation probes cover direct epoch, page-token append/map-filter/count-by-key, and epoch-buffer paths; raw `childStreaming` can open a child streaming region whose handle cannot escape the parent stream; `childWindow` is the preferred stream-window wrapper; `childRegion(parent, window)` is an explicit owner-token accessor for deliberate parent-visible child records; child close ordering remains explicit. |

The important corrected invariant is about GC visibility:

- GC-to-region references are forbidden for safe regions unless the type system
  proves the region is live wherever the heap object can be reached.
- Region-to-GC references are not automatically safe in the implementation.
  Scala Native's GC does not scan Rift region memory. A heap object reachable
  only from a Rift region may be collected.
- Safe mixed region/GC designs must use one of three strategies: reject owning
  region-to-GC references statically, register/scavenge region metadata with
  the GC, or require another GC-visible root/handle for every heap object
  referenced from a region.
- The current v1 API implements the explicit-root option through
  `RiftRegion.HeapRoot[T]` and `RiftRegion.root(value)`. The live region object
  keeps these handles in a heap list, so the referent remains visible to the
  GC. Direct unrooted heap-object constructor arguments in checked Rift
  allocation are rejected by the compiler lowering guard; safe code can use
  static module singletons and immutable module vals for independently rooted
  metadata, but should use `HeapRoot` for ordinary heap metadata until plain
  `T^` selected fields and higher-level container aliases have a more precise
  policy. Operator-owned page-token and epoch-buffer probes currently require
  the event type to express the metadata capability inside the stream lifetime;
  externally inferred metadata root capabilities remain a compiler/API
  precision gap.
- `HPZone` remains a trusted path. It may be used to measure runtime potential,
  but it is not the safety story.

Active/closed typestate is now partly enforced internally. The open checked
handle is allocation-capable, but lifecycle operations are owned by `epoch`,
page/window-token, and child-close helpers. Low-level public handles still keep
runtime defensive checks; the compiler rule is only a basis for removing checks
inside operator-owned paths where close ordering is statically fixed. The
current audit is `evidence/OPEN_REGION_TYPESTATE_AUDIT.md`: it records that
page-token/epoch-buffer open handles are fast allocation tokens, but they are
not yet statically linear after bucket close, so no further public stale/open
checks are removed in this slice.

Region-managed values are allowed to be ordinary Scala objects. Rift is not a
primitive-record-only system. Packed primitive keys in the current DEBS code are
an interim boundary technique used where the runtime cannot yet prove or expose
mixed-reference safety. The intended v1 safe mixed-reference policy is:

- `GC -> region`: allowed only when the heap object's type/capture set proves
  the heap object cannot outlive the region it points into.
- `region -> GC`: allowed only for immutable/static referents or explicit
  GC-visible root handles. The current checked implementation covers static
  module singletons and immutable module vals, and rejects mutable static vars.
  A region object must not be the sole owner of a collectible heap object
  because Scala Native's GC does not scan Rift slabs.
- No GC scanning of arbitrary region slabs in v1; that would complicate
  non-moving native-runtime assumptions and should be evaluated only after the
  explicit-root/static-capture design is tested.

Stable heap references used by region objects must therefore be independently
rooted metadata, static/immutable objects, or future checked root handles. The
current benchmark HPZone paths are trusted experiments and must be labeled as
such when they store heap metadata or heap collection entries that point at
region objects.

This correction comes from two repo-grounded findings:

- `sandbox/PHASE4_TOPOLOGY.md` records an unrooted mixed Rift topology checksum
  mismatch when region nodes pointed at heap value objects.
- `bench/debs2015/RESULTS.md` records an earlier Q1 issue where region entries
  stored heap `Route` objects; the fixed Q1 path stores packed `Long` keys.

## 6. Runtime Design

The active in-tree runtime is under:

- `nativelib/src/main/resources/scala-native/rift/RiftRuntime.c`
- `nativelib/src/main/resources/scala-native/rift/RiftRuntime.h`

Current runtime properties:

- 32 KB regular slabs.
- `mmap`-backed slab acquisition.
- Thread-local cache up to 8 slabs.
- Global Treiber stack for free slabs.
- Region open, close, reset, raw allocation, and managed object allocation.
- Slab resident counters and instrumentation counters.
- Fresh mmapped slabs are treated as zero-filled.
- Reused slabs are not eagerly zeroed on acquire. Managed object and array
  allocation zeroes the exact allocated object when the current slab is marked
  non-zeroed.
- The reset path keeps the retained first slab, resets the bump pointer, and
  marks the slab non-zeroed instead of clearing the whole 32 KB slab.
- Huge slabs avoid the synchronous `MAP_POPULATE`/`MADV_HUGEPAGE` path that
  caused a flat-layout regression.

SafeZone changes are part of the design, not noise:

- `SAFEZONE_ROOTS_MODE=0` is the current baseline.
- `SAFEZONE_ROOTS_MODE=1` coalesces root removal and is the improved baseline.
- `SAFEZONE_TRACE` and `SAFEZONE_PAGE_SIZE` support diagnosis.
- `GC_Roots_RemoveByRange` was fixed for fully covered root ranges.

Open runtime issues:

- The stats functions exposed to Scala externs are not declared in
  `RiftRuntime.h`.
- Full Scala Native tests have not been run.
- Commix coverage is missing from most benchmark matrices.
- Instrumentation timing on macOS is useful for diagnosis but not a final
  low-overhead design.

## 7. Compiler And Scala API

Current compiler/API implementation:

- `RiftRegion` extends the allocation-zone shape used by SafeZone.
- `region.alloc(new T(...))` lowers through compiler-plugin support.
- The plugin added `RIFT_ALLOC`, `RuntimeRiftAllocator_allocate`, and a
  generalized allocation-zone attachment.
- Scala 3 companion support exists for the allocation syntax.
- Scala 2 compatibility surface exists where needed.

Key files:

- `nativelib/src/main/scala/scala/scalanative/memory/RiftRegion.scala`
- `nativelib/src/main/scala/scala/scalanative/runtime/RiftAllocator.scala`
- `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirDefinitions.scala`
- `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirGenExpr.scala`
- `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirPrimitives.scala`

This is compiler integration for allocation. It is not yet capture checking.

## 8. Static Safety Strategy

The safe API target is a capture-checked region discipline:

- Region handles are capabilities.
- Values allocated in a region capture that region capability.
- A value cannot outlive any region capability in its capture set.
- Closing or resetting a region is legal only when no accessible value can use
  that region afterward.
- Closures must carry the regions captured by their environment.
- Region-polymorphic functions should allow reusable higher-order code without
  forcing everything into one global region.

The design intentionally avoids:

- Yak-style write barriers for every heap write in the intended safe Rift
  design. The Yak benchmark harness may still model barrier counts as a
  comparison/control path.
- Reggio-style pervasive capability annotations on every type.
- Fully automatic Tofte-Talpin inference for all Scala code.
- Cheney copying collection inside regions, because Scala Native relies on
  native/non-moving assumptions.

The open hard problem is closure-region interaction. Prior systems either
avoid closures, restrict them heavily, or handle escapes dynamically. Rift must
make this problem explicit in tests and proof obligations. The first
Scala-next checked API slice now passes compiler probes for scoped object
graphs, for-loop allocation, nested scoped regions returning pure values, local
higher-order consumers, non-escaping closures, direct return escape rejection,
heap retention rejection, nested-region leak rejection, streaming reset escape
rejection, returned-closure rejection, and explicit heap-root handles. This is
useful evidence, but it is not a complete closure or mixed-reference story: the
v1 API rejects direct function results from checked region boundaries because a
returned closure can hide region-local captures. Direct unrooted heap-object
constructor arguments are now rejected in checked allocation lowering, but this
is not yet a full mixed-reference alias analysis. Simple local aliases of known
region values are propagated; heap aliases and heap field selections are
rejected. Stable constructor fields whose source types are explicitly tied to
`{region}` are accepted; plain `T^` field reuse remains rejected by Scala
capture checking because the selected field gets its own capability.
Region-owned arrays require explicit element capture such as
`Array[Leaf^{region}]^{region}`; stores into known region arrays reject
unrooted heap objects and accept region-local values or `HeapRoot` handles.
The ReML-style polymorphic escape gap is now fixed for the current checked
compiler probe boundary. Heap generic objects such as
`Cell[Box^{region}]`, generic cells widened to `AnyRef`, heap arrays that
store region-captured values, and escaping closures that hide generic region
values are rejected when they flow into durable/static heap state. Local
nonescaping polymorphic consumers and local heap generic cells remain legal
inside the region scope. This fix is intentionally narrower than a full heap
alias analysis: it tracks known Rift-derived values and durable/static
retention sites, while broader heap-object field provenance remains open.
Rootless checked backends still require a separate root-free eligibility proof
before they can be claimed safe.
`RiftRegion.ObjectBuffer` is the first checked higher-level container: it uses
heap control metadata plus a region-owned backing object array. Its v1 API is
owner-token based, for example `RiftRegion.append(region, buffer, value)` or
the lighter `region.append(buffer, value)` extension method. `RegionBuffer`
uses the same owner-token rule but permits growth by allocating larger backing
arrays in the owner region and leaving old arrays for batch reclamation. The
same owner-token pattern now covers `RegionPriorityQueue` for append/pop
top-k state and `RegionIndexedPriorityQueue` for dense-key mutable ranking
state. The indexed queue is important because it lets a stream operator keep an
ordinary region object for a key, mutate that object's fields, and update the
ranking priority without per-refresh object churn. The
current checker still needs the owner token; a plain `buffer.append(value)`
method does not prove the same-region relation. Raw `childStreaming` and the
preferred `childWindow` wrapper prove that a child region handle cannot escape
its parent stream. The `childRegion(parent, window)` accessor is intentionally
explicit for the case where parent-lived control metadata retains child-window
records until eviction. `closeChildWindow(parent, window) { cleanup }` is the
primitive close boundary: caller cleanup runs while the parent owner token and
window are both in scope, then the child region closes; direct user
`window.close()` is not public. `ChildBucket` packages that pattern for stream
operators so code uses `childBucketRegion(parent, bucket)` and
`closeChildBucket(parent, bucket) { cleanup }` instead of exposing the raw
window. This is still not a full affine lifetime system, because the checker
does not prove all parent-visible child references were cleared before close.
The next step is a stronger typed cleanup obligation or static close proof.
Direct heap stores are rejected by Rift lowering, and cross-region stores are
rejected by the owner-token type.
Checked streaming can express subinterval or epoch data with region-owned
arrays, fixed/growable checked buffers, and local linked-list heads whose
assignments preserve region-owned provenance. This rule is still a local
provenance check, not a full dataflow analysis for arbitrary mutable
containers.

Minimum Phase 6 evidence:

- Positive cases for for-loops, nested regions, and higher-order functions.
  Initial compiler probes now exist for this slice.
- Negative cases for return escape, closure capture escape, cross-region
  leakage, use-after-reset, and unrooted region-to-GC ownership. Initial probes
  cover the escape/reset cases, the explicit `HeapRoot` path, and direct
  unrooted heap-object constructor-argument rejection, including simple
  heap-alias and heap-field-selection variants. Explicitly region-captured
  constructor field reuse is covered positively; plain `T^` field reuse is
  covered as a current negative. Static module singletons and immutable module
  vals are covered positively; mutable static vars are covered negatively.
  Region-owned array containers are covered with
  positive region-value/`HeapRoot` stores and a negative unrooted heap store.
  ReML-style probes now include local polymorphic consumer acceptance,
  polymorphic identity escape rejection, durable/static generic heap-cell
  retention rejection, widened `AnyRef` rejection, heap-array retention
  rejection, escaping-closure hiding rejection, and unrooted heap-metadata
  rejection.
  `ObjectBuffer` and growable `RegionBuffer` are covered as the first checked
  higher-level containers, with
  positive region-value/`HeapRoot` stores, owner-token extension method syntax,
  and negative direct-heap,
  cross-region, and escape probes. Literature-shaped probes now cover
  top-word-style rooted metadata records, GraphChi-style rooted/unrooted heap
  metadata, and reset-epoch values stored into outer streaming buffers.
- A report stating exactly what current Scala capture checking can express and
  what requires compiler or API changes. The first slice is recorded in
  `docs/REPORT_CAPTURE_CHECK.md`.

## 9. Application And Library Design

The application/library story must follow the literature-review lesson:
regions win when the program exposes structured lifetimes.

For Broom-like dataflow:

- Messages or window buckets should be self-contained or explicitly rooted.
- Operator state should live in actor/operator regions or the GC heap depending
  on lifetime.
- Temporary scratch should live in scoped or streaming regions.
- The API must make ownership transfer and region close/reset explicit enough
  for static checking.

For DEBS 2015:

- Benchmark fairness rule: heap and Rift variants should share the same query
  algorithm and data-shape as much as possible. The variable under test should
  be allocation placement and lifetime management: heap uses ordinary `new`;
  Rift uses minimal region annotations, `region.alloc`, and close/reset at the
  same logical lifetime boundary.
- Current Q1 uses a shared bucketed-window implementation. Heap mode allocates
  the same `BucketWindowEntry` class on the GC heap; Rift modes allocate that
  class in per-timestamp regions and close the bucket region at eviction.
- Current Q2 uses a shared bucketed-window implementation for profit and
  empty-taxi window entries. Heap mode allocates the same entry classes on the
  GC heap; Rift modes allocate those entries in per-timestamp regions and close
  each region at window eviction.
- RunBoth parsing now uses a shared byte parser. Heap mode allocates the input
  byte buffer on the GC heap; Rift modes allocate the same run-lifetime input
  buffer in a region. The hot RunBoth path avoids `String.split`, per-row
  `Option`, per-row `Trip`, per-row line strings, and per-row taxi/timestamp
  substrings.
- Q1 ranking replaced boxed route-count and route-rank `HashMap`s with a
  shared primitive open-addressed route table. Heap allocates the backing arrays
  with `new`; Rift modes allocate those arrays in the run-lifetime
  ranking/control region.
- Q1 replaced the heap `TreeSet` ranking index with a shared indexed binary
  heap over ordinary `RankedRoute` objects. Heap allocates the index arrays
  with `new`; Rift modes allocate those arrays, plus `RankedRoute`, `Route`,
  and `Cell` objects, in the run-lifetime ranking/control region. Returned
  top-k arrays are cached by exact size and reused, rather than allocated in a
  resettable per-event snapshot region.
- The checked Q1 processing probe validates a source-level safe-API shape for
  ordinary Scala Q1 objects: route events live in per-bucket `childWindow`
  regions and close at bucket eviction, while route/rank arrays and rank
  objects remain in the parent streaming region. This is not yet the production
  RunBoth backend and not a full affine close guarantee.
- The checked Q2 processing probe validates the same direction for a richer
  stream-processing object graph: profit/empty window entries live in
  `childWindow` regions, median heap arrays and ranking objects live in the
  parent streaming region, taxi-id entries/bytes are region-backed, and only
  `ProfitStats` remains heap control metadata captured by the stream. Q2 uses
  `childRegion(parent, window)` where parent-lived metadata intentionally
  retains child-window entries until eviction. This is standalone Q2 evidence,
  not RunBoth integration.
- RunBoth now has a checked integration mode, `q1_mode=rift-checked`. It runs
  checked Q1 and checked Q2 processors together in the shared byte-parser loop
  and matched heap Q1/Q2 output on sample, 100k, and 1M sorted inputs. The
  follow-up 100k/1M median matrix includes `heap`, `rift-hp`,
  `rift-streaming`, and `rift-checked`; at 1M, checked is fastest in that local
  matrix. The checked processors use the safe API; the byte-reader buffer and
  output/latency scratch buffers still use existing trusted runtime helpers,
  and previous output snapshots remain primitive heap control metadata.
- Q2 window queues now hold primitive-key entries in heap or Rift memory, and
  active profit values are stored in those entries rather than duplicated in a
  heap `ArrayBuffer`.
- Q2 median sorting arrays are heap-allocated in heap mode and allocated in a
  run-lifetime scratch region in Rift modes. The scratch array grows by
  capacity and is reused rather than reset for each recomputation.
- Q2 replaced the boxed per-cell `HashMap` tables for active `ProfitStats`,
  empty-taxi counts, latest sequence, and current ranked area with fixed arrays
  over the benchmark's bounded cell key space. Heap allocates those arrays and
  `ProfitStats` with `new`; Rift modes allocate them in the run-lifetime
  ranking/control region.
- Q2 replaced `latestEmptyByTaxi` with a growable dense array indexed by the
  existing `TaxiIds` integer key. Heap allocates the array with `new`; Rift
  modes allocate it in the run-lifetime ranking/control region.
- Q2 replaced the heap `TreeSet` ranking index with a shared indexed binary
  heap over `ProfitableArea` objects. Heap allocates the index arrays with
  `new`; Rift modes allocate them in the run-lifetime ranking/control region.
  In Rift modes, `ProfitableArea` ranking objects are region-allocated,
  returned top-k arrays are cached and reused, and output rows are written
  directly through shared writer-based formatting rather than per-row
  `StringBuilder.toString`.
- Q2 replaced durable taxi-id `String` interning and a heap `HashMap` with a
  shared byte-backed taxi-id table. Heap allocates table arrays, entries, and
  taxi-id byte copies with `new`; Rift modes allocate them in the run-lifetime
  ranking/control region. Region entries store only primitive/region data, not
  heap `String` references.
- RunBoth previous-output snapshots now have a heap/Rift allocation-placement
  split. Heap mode allocates Q1/Q2 snapshot arrays with `new`; Rift modes
  allocate the same arrays and Q2 `Snapshot` objects in a run-lifetime snapshot
  region. This is a placement checkpoint, not a dominant bottleneck fix.
- RunBoth latency collectors now use shared primitive buffers. Heap uses heap
  arrays; Rift modes allocate backing arrays in the snapshot region and copy
  final metrics arrays out before region close.
- Q2 top-10 extraction now uses a shared conservative cache. Heap and Rift use
  the same invalidation logic and still return top-k on every event; the cache
  avoids recomputing the heap frontier when a rank update cannot affect the
  cached top 10.
- Opt-in GC allocation attribution now distinguishes collection time from heap
  allocation-call cost. It records heap allocation calls, rounded heap bytes,
  and measured time spent in GC allocation entry points when
  `SCALANATIVE_GC_ALLOC_STATS=1`.

Therefore current DEBS exercises more of the region-heavy application design
and now has bounded-sample elapsed wins, but it is still not final Phase 5
success. The latest trusted 1M byte-output medians are heap `4640.593 ms`,
HPZone `4524.706 ms`, and Streaming `4522.308 ms`; trusted Rift GC collection
time is below `1 ms`, and RSS drops from about `160 MB` to about `117 MB`.
The latest checked 1M RunBoth medians are heap `5363.257 ms`, HPZone
`5224.005 ms`, Streaming `5209.104 ms`, and checked `5043.240 ms`. Rift
operation time remains small enough to avoid replacing GC as the bottleneck:
checked is `16.128 ms` at 1M. GC collection time is lower but not the whole
story: heap-to-checked elapsed drops by about `320 ms`, while measured GC
collection time drops by about `18.8 ms`. After byte output, the 1M
allocation-attribution run shows that trusted Rift removes about `5.46M` GC
heap allocation calls and about `224 MB` of rounded heap allocation requests,
while measured heap allocation-call time drops from `171.868 ms` in heap to
about `12.8-12.9 ms` in trusted Rift modes. The checked attribution run shows
the same direction: at 1M, total heap allocation calls drop from `6025149` to
`752568`, rounded heap bytes drop from `235159840` to `28785632`, and measured
heap allocation-call time drops from `173.578 ms` to `20.514 ms`. That is the
correct interpretation of the speedup: not only shorter collection pauses, but
less ordinary heap allocation work because structured-lifetime Scala objects
are placed in regions.

The strongest performance evidence is still bounded-sample. The remaining
pressure is in Q2 rank/output work, residual heap allocation/control metadata,
SafeZone, controlled full-scale comparisons, and the need for safe
region-backed collections/control structures that preserve the heap logical
program.

For parallel collections:

- The current raw-array pipeline surrogate is not comparable to amordo
  `ZoneParVector`.
- A fair comparison requires a `RiftParVector` or equivalent region-backed API
  with the same workload shape as the parallel-collections benchmark.

## 10. Current Benchmark Summary

Validated local runtime medians:

| Benchmark | Immix heap | Current SafeZone | Improved SafeZone | Rift HPZone |
|---|---:|---:|---:|---:|
| GCBench, 5 runs | 203.514 ms | 684.517 ms | 223.770 ms | 161.641 ms |
| ListOfLists linked, 5 runs | 15085.511 ms | 138171.998 ms | 10132.854 ms | 6951.331 ms |

Layout study:

| Mode | Linked ms | Chunked ms | Flat ms |
|---|---:|---:|---:|
| Immix heap | 15260.875 | 2636.480 | 1766.295 |
| current SafeZone | 136016.922 | 4835.904 | 1735.453 |
| improved SafeZone | 9824.936 | 2369.108 | 1743.161 |
| Rift HPZone | 7278.150 | 2463.674 | 1515.091 |

Report-scale topology:

| Mode | Topology | Median ms |
|---|---|---:|
| Immix heap | full heap graph | 14755.580 |
| current SafeZone | one-region | 136016.922 |
| current SafeZone | nested | 10289.097 |
| improved SafeZone | one-region | 9767.048 |
| improved SafeZone | nested | 9929.699 |
| Rift HPZone | one-region | 7256.426 |
| Rift HPZone | nested | 7314.201 |
| Rift HPZone | mixed rooted heap-values | 11695.748 |

Pipeline status:

| Benchmark | Result |
|---|---|
| Cleaned raw-array surrogate, 2M records | Heap, SafeZone, and Rift are near parity; Rift is not a clear win. |
| amordo `ZoneParVector`, 100k records | Region-per-stage median 30.36 ms, on-heap `ParVector` median 30.75 ms. |
| Rift raw-array surrogate, 100k records | Heap raw arrays 1.845 ms, Rift HPZone 2.502 ms; not apples-to-apples with `ZoneParVector`. |

DEBS status:

| Run | Heap | Rift HPZone | Rift Streaming | Evidence level |
|---|---:|---:|---:|---|
| 1M RunBoth, elapsed | 21658.215 ms | 22314.989 ms | 22184.467 ms | Single-run, provisional |
| 1M instrumented, elapsed | 22827.882 ms | 22366.285 ms | 22810.687 ms | Single-run, provisional |
| 1M instrumented, GC time | 1051.752 ms | 1003.171 ms | 1012.489 ms | Single-run, provisional |
| 1M after reusable ranking arrays, elapsed | 14633.019 ms | 14234.470 ms | 14392.097 ms | 3-run median, bounded sample |
| 1M after reusable ranking arrays, GC time | 513.199 ms | 457.726 ms | 478.912 ms | 3-run median, bounded sample |
| 1M after Q2 cell tables, elapsed | 11471.085 ms | 11442.637 ms | 11477.431 ms | 3-run median, bounded sample |
| 1M after Q2 cell tables, GC time | 478.636 ms | 419.658 ms | 428.339 ms | 3-run median, bounded sample |
| 1M after Q2 cell tables, peak RSS bytes | 609730560 | 490766336 | 490799104 | 3-run median, bounded sample |
| 1M after Q1 primitive route table, elapsed | 11957.721 ms | 11659.223 ms | 11739.195 ms | 3-run median, bounded sample |
| 1M after Q1 primitive route table, GC time | 463.555 ms | 397.162 ms | 398.268 ms | 3-run median, bounded sample |
| 1M after Q1 primitive route table, peak RSS bytes | 433209344 | 381222912 | 381190144 | 3-run median, bounded sample |
| 1M after Q2 latest-empty taxi table, elapsed | 11649.547 ms | 11263.680 ms | 11188.144 ms | 3-run median, bounded sample |
| 1M after Q2 latest-empty taxi table, GC time | 487.774 ms | 381.099 ms | 382.734 ms | 3-run median, bounded sample |
| 1M after Q2 latest-empty taxi table, peak RSS bytes | 609304576 | 381501440 | 381501440 | 3-run median, bounded sample |
| 1M after Q2 array-backed ranking, elapsed | 11202.975 ms | 10808.901 ms | 10804.756 ms | 3-run median, bounded sample |
| 1M after Q2 array-backed ranking, GC time | 423.932 ms | 348.901 ms | 344.376 ms | 3-run median, bounded sample |
| 1M after Q2 array-backed ranking, peak RSS bytes | 431718400 | 383631360 | 383631360 | 3-run median, bounded sample |
| 1M after Q2 taxi-id table, elapsed | 9876.359 ms | 9676.525 ms | 9667.365 ms | 3-run median, bounded sample |
| 1M after Q2 taxi-id table, GC time | 376.602 ms | 358.127 ms | 270.482 ms | 3-run median, bounded sample |
| 1M after Q2 taxi-id table, peak RSS bytes | 431751168 | 169312256 | 169295872 | 3-run median, bounded sample |
| 1M after Q1 indexed ranking, elapsed | 9746.536 ms | 9441.064 ms | 9442.026 ms | 3-run median, bounded sample |
| 1M after Q1 indexed ranking, GC time | 312.151 ms | 320.025 ms | 306.311 ms | 3-run median, bounded sample |
| 1M after Q1 indexed ranking, peak RSS bytes | 431669248 | 108445696 | 108969984 | 3-run median, bounded sample |
| 1M after output snapshots, elapsed | 8983.464 ms | 8815.087 ms | 8836.488 ms | 3-run median, bounded sample |
| 1M after output snapshots, GC time | 290.712 ms | 292.155 ms | 296.305 ms | 3-run median, bounded sample |
| 1M after output snapshots, peak RSS bytes | 431652864 | 119865344 | 119898112 | 3-run median, bounded sample |
| 1M after Q2 incremental medians, elapsed | 5976.447 ms | 5794.879 ms | 5948.755 ms | 3-run median, bounded sample |
| 1M after Q2 incremental medians, GC time | 67.086 ms | 59.658 ms | 55.056 ms | 3-run median, bounded sample |
| 1M after Q2 incremental medians, peak RSS bytes | 305758208 | 113950720 | 113934336 | 3-run median, bounded sample |
| 1M after Q2 top-10 cache, elapsed | 6192.692 ms | 5697.948 ms | 5657.424 ms | 3-run median, bounded sample |
| 1M after Q2 top-10 cache, GC time | 70.762 ms | 36.231 ms | 36.288 ms | 3-run median, bounded sample |
| 1M after Q2 top-10 cache, peak RSS bytes | 304463872 | 116588544 | 96239616 | 3-run median, bounded sample |
| 1M allocation attribution, GC alloc calls | 19924383 | 14462042 | 14462060 | Single-run diagnostic, instrumentation perturbs elapsed |
| 1M allocation attribution, GC alloc bytes | 679841024 | 455349920 | 455350304 | Single-run diagnostic, instrumentation perturbs elapsed |
| 1M allocation attribution, GC alloc time | 582.629 ms | 385.807 ms | 384.031 ms | Single-run diagnostic, instrumentation perturbs elapsed |

Checked RunBoth median addendum:

| Run | Heap | Rift HPZone | Rift Streaming | Rift checked | Evidence level |
|---|---:|---:|---:|---:|---|
| 100k checked RunBoth median, elapsed | 553.059 ms | 529.613 ms | 512.808 ms | 508.056 ms | 3-run median, bounded sample |
| 100k checked RunBoth median, GC time | 9.541 ms | 0.000 ms | 0.000 ms | 0.077 ms | 3-run median, bounded sample |
| 100k checked RunBoth median, peak RSS bytes | 55459840 | 38895616 | 38912000 | 39878656 | 3-run median, bounded sample |
| 1M checked RunBoth median, elapsed | 5363.257 ms | 5224.005 ms | 5209.104 ms | 5043.240 ms | 3-run median, bounded sample |
| 1M checked RunBoth median, GC time | 21.226 ms | 0.834 ms | 0.862 ms | 2.473 ms | 3-run median, bounded sample |
| 1M checked RunBoth median, peak RSS bytes | 159989760 | 116867072 | 116850688 | 123977728 | 3-run median, bounded sample |
| 1M checked allocation attribution, GC alloc calls | 6025149 | n/a | n/a | 752568 | Single-run diagnostic, instrumentation perturbs elapsed |
| 1M checked allocation attribution, GC alloc bytes | 235159840 | n/a | n/a | 28785632 | Single-run diagnostic, instrumentation perturbs elapsed |
| 1M checked allocation attribution, GC alloc time | 173.578 ms | n/a | n/a | 20.514 ms | Single-run diagnostic, instrumentation perturbs elapsed |

Commix control addendum:

| Run | Commix heap | Commix Rift checked | Evidence level |
|---|---:|---:|---|
| 100k elapsed | 492.372 ms | 472.477 ms | 3-run median, bounded sample |
| 100k GC time | 4.942 ms | 0.092 ms | 3-run median, bounded sample |
| 100k peak RSS bytes | 56885248 | 39534592 | 3-run median, bounded sample |
| 1M elapsed | 4968.773 ms | 4745.291 ms | 3-run median, bounded sample |
| 1M GC time | 8.206 ms | 1.137 ms | 3-run median, bounded sample |
| 1M peak RSS bytes | 158924800 | 125698048 | 3-run median, bounded sample |

Full-month control addendum:

| Run | Heap | Rift checked | Evidence level |
|---|---:|---:|---|
| month 1 full parsed rows | 14776529 | 14776529 | single run, output matched |
| month 1 full invalid rows | 86 | 86 | single run, output matched |
| month 1 full elapsed | 69.754 s | 1258.714 s | checked wall-clock invalid |
| month 1 full external user+sys time | 69.64 s | 63.97 s | external `/usr/bin/time -l` |
| month 1 full GC time | 0.288 s | 0.143 s | single run |
| month 1 full peak RSS bytes | 624902144 | 1029373952 | single run |
| month 1 full region objects | 0 | 68834523 | single run |

Streaming first-slab and pool-cap follow-up:

| Run | Before cap | After cap | Evidence level |
|---|---:|---:|---|
| checked full-month external real time | 1258.76 s | 70.87 s | single run |
| checked full-month user+sys time | 63.97 s | 68.86 s | single run |
| checked full-month GC time | 0.143 s | 0.166 s | single run |
| checked full-month peak RSS bytes | 1029373952 | 887078912 | single run |
| checked full-month closed-slab pool | 780.4 MiB | 128.0 MiB | single run |
| checked full-month cumulative Rift mmap | 932.5 MiB | 864.4 MiB | single run |
| checked full-month Rift op time | 0.679 s | 0.998 s | single run |

Same-run full-month pool-cap control:

| Run | Heap | Rift checked | Evidence level |
|---|---:|---:|---|
| month 1 full elapsed | 71.919 s | 77.947 s | single run, output matched |
| month 1 full external real time | 71.96 s | 77.98 s | single run |
| month 1 full user+sys time | 69.58 s | 74.24 s | single run |
| month 1 full GC time | 0.323 s | 0.190 s | single run |
| month 1 full peak RSS bytes | 607240192 | 728940544 | single run |
| month 1 full Rift op time | 0.000 s | 1.137 s | single run |

Checked `ChildBucket` single-control-object follow-up:

| Run | Heap | Rift checked / streaming | Evidence level |
|---|---:|---:|---|
| full-month trusted Streaming elapsed | 73.888 s | 68.990 s | single run, output matched |
| full-month trusted Streaming GC time | 0.360 s | 0.088 s | single run |
| full-month trusted Streaming peak RSS bytes | 624623616 | 840646656 | single run |
| 1M checked after `ChildBucket` change, elapsed | 4.810 s | 4.678 s | single run, output matched |
| full-month checked after `ChildBucket` change, elapsed | 70.872 s | 65.928 s | single run, output matched |
| full-month checked after `ChildBucket` change, GC time | 0.315 s | 0.086 s | single run |
| full-month checked after `ChildBucket` change, peak RSS bytes | 614891520 | 908656640 | single run |

Same-order full-month 3-run median after the `ChildBucket` API change:

| Metric | Heap | Rift checked | Evidence level |
|---|---:|---:|---|
| elapsed | 73.029 s | 67.670 s | 3-run median, output matched |
| external real time | 73.06 s | 67.69 s | 3-run median |
| user+sys time | 71.05 s | 67.18 s | 3-run median |
| GC time | 0.315 s | 0.086 s | 3-run median |
| peak RSS | 586.4 MiB | 866.6 MiB | 3-run median |
| Rift op time | 0.000 s | 0.885 s | 3-run median |
| Q1 process time | 20.507 s | 19.233 s | 3-run median |
| Q2 process time | 22.154 s | 20.142 s | 3-run median |

Interpretation:

- Rift has credible same-layout runtime wins on GCBench and linked ListOfLists.
- Improved SafeZone is a serious baseline.
- Layout changes can dominate allocator changes and must be separated.
- Current DEBS now moves more application data operations into regions and has
  bounded-sample elapsed/RSS wins under Immix and Commix. The first full-month
  checked run matched heap output but did not provide usable wall-clock
  performance evidence. The pool-cap follow-up fixes the closed-slab retention
  problem enough to produce a credible same-run full-month control. In that
  single run, checked is slower than heap by about `6.0 s`, while GC collection
  time is lower and RSS is much closer to heap than before the cap. The
  `ChildBucket` follow-up then shows the checked API shape itself matters:
  removing one heap control object per checked bucket makes checked full-month
  elapsed faster on the same-order 3-run median. The improvement is noisy and
  RSS gets worse, so this is an elapsed/checker-overhead result, not a memory
  footprint win. The active-memory diagnostic shows that RSS is mostly live
  checked-region payload under current lifetimes, not capped free-slab
  retention. The first per-family fix moves Q1 checked rank object graphs from
  parent lifetime to child-bucket lifetime and brings the checked full-month
  RSS diagnostic back to heap scale. The post-fix full-month median is a
  near-tie on elapsed time and much better on RSS than the pre-fix checked
  median, but not a large speedup. The closeable SafeZone DEBS controls now
  have 1M medians: SafeZone is lower-RSS than heap but slower than heap and
  checked Rift. Opt-in process diagnostics show Q2 has identical operation
  counts between heap and checked. The next Q1 fix introduces coarser
  window-rank arenas: checked Q1 keeps per-second event buckets for eviction,
  but stores ordinary Scala rank object graphs in arenas whose lifetime matches
  the Q1 window. This reduces checked rank churn and gives a full-month
  single-run RSS win. `StreamBucketArena` now extracts the reusable bucket
  lifetime primitive, and `StreamWindowIndexedRank` adds the first dense-key
  rank/window collection. Its auto-cleanup path moves bucket-owned rank-key
  removal into the framework close path, validating a stronger close boundary.
  The entry-cleanup path removes the duplicate checked-side bucket key list and
  improved the focused default median, but the matrix remained slower than heap
  and slower than the earlier manual-cleanup path. The follow-up
  remove-with-value close primitive simplifies framework unlinking and validates
  already-popped-key cleanup, but did not produce a measured speedup. The
  lexicographic priority API removes one Q1 integration blocker. Standalone
  long-key stream-window rank state now removes the dense-key remapping blocker,
  but lower-overhead checked rank containers and application integration remain
  open before direct DEBS Q1 use.
  Hash-key collections, checked Q1/Q2 CPU overhead work, and
  stronger safe API boundaries are still needed before it can support a final
  application claim.
- Checked RunBoth is now median-backed on bounded 100k/1M samples. It is
  encouraging Phase 5/7 evidence, but not an apples-to-apples proof that the
  checked API is always faster than the trusted API because the trusted and
  checked paths still differ in implementation shape.
- DEBS changes that merely hand-optimize the heap query implementation are not
  evidence. A change is Phase-5 relevant only if it preserves the same logical
  benchmark for heap and Rift while moving structured-lifetime data into region
  memory or making that lifetime boundary explicit.
- The current Q1/Q2 direction follows that boundary: timestamp-bucket window
  entries, median scratch buffers, bounded Q2 per-cell tables, Q1 route-table
  arrays, Q2 latest-empty taxi state, Q2 ranking index arrays, and Q2 taxi-id
  table entries/bytes are region-backed in Rift modes. Q1 ranking now uses a
  shared indexed heap whose arrays and ordinary Scala ranking objects are
  region-backed in Rift modes. RunBoth output snapshots are also region-backed
  in Rift modes. Latency backing arrays are region-backed in Rift modes and
  final metrics arrays are copied out before region close. Primitive packed
  keys are used in the shared logic to avoid accidental heap objects in the hot
  path. Allocation attribution confirms this is reducing heap allocation
  calls/bytes/time, not merely collection pause time.

## 11. Formal Model

The proof target should be a small calculus, not the whole Scala compiler:

- Terms for allocation, region open, region close, reset, function values,
  capture sets, and GC fallback.
- A two-space store with `H_GC` and `H_R`.
- Liveness of region capabilities.
- A typing judgment that records capture sets.
- An operational semantics that permits closing/resetting only when no live
  value can still access the region.

Required theorems:

- Progress.
- Preservation.
- Containment: every reachable value is in `H_GC` or in a live region allowed
  by its capture set.
- Safe close/reset: closing or resetting a region cannot leave a reachable
  dangling pointer.

The MLKit/ReML lineage shows why this cannot stay pen-and-paper only: later
work found soundness problems in higher-order polymorphic cases. Rift's proof
must pay special attention to higher-order functions, closures, generic heap
containers, and capture preservation through type erasure/widening.

## 12. Claim Boundaries

Claims that are currently supported:

- In-fork Rift HPZone can beat heap and improved SafeZone on specific
  allocation-heavy same-layout workloads.
- Improved SafeZone changes the baseline materially.
- Topology and layout effects are large enough to require separate reporting.
- Region memory is not GC-scanned, so unrooted region-to-GC references are
  unsafe in the current runtime.

Claims that are not yet supported:

- Rift has a final full-DEBS application-level speedup. It has bounded-sample
  Q2 top-cache and checked RunBoth medians plus allocation-attribution evidence,
  including a 3-run Commix control, one full-month output-equivalence run, one
  post-pool-cap same-run full-month timing row, one post-Q1-lifetime-fix
  heap/checked full-month 3-run median, a Q1 window-rank arena checkpoint, and
  bounded closeable SafeZone DEBS medians, but not SafeZone full-month
  controls, Q1/Q2 CPU-overhead reduction, richer checked rank/window
  collections, or complete safe-API controls.
- Rift has a capture-checked safe API.
- Rift beats Broom, StreamFlex, Yak, Stancu et al., or Reggio on their strongest
  axes.
- Rift has lower p99/p99.9 latency than low-pause JVM collectors.
- Rift has a mechanized proof.

The project should narrow claims honestly until those gaps are closed.
