# Optimization Literature Notes For Rift

Last updated: 2026-05-13 00:52 CEST

Status: literature-guided optimization checklist. This document translates
well-known GC, allocator, and memory-safety performance results into concrete
Rift engineering guidance. It does not introduce new benchmark evidence by
itself.

## Why This Exists

Recent Rift profiles point to allocation lowering, object construction,
mandatory zeroing, linked-object traversal, and capsule/operator CPU as the
remaining costs after GC/reclaim work has been reduced. Before further runtime
tweaks, this note records what prior performance literature suggests and how
that should constrain the next experiments.

The main rule is: do not remove a cost merely because it is visible in a
profile. Remove it only when Scala Native semantics, Rift's static safety
rules, and same-shape benchmark controls justify the change.

## Literature Takeaways

| Source family | Relevant lesson | Rift implication |
|---|---|---|
| Blackburn et al., zeroing work | Zero initialization is not incidental allocator noise; it can be a large direct and indirect cost, but it also enforces language safety and affects cache behavior. | Do not globally skip object zeroing. Treat `_platform_memset` as a legitimate target only through proven initialization, pre-zeroed slabs, or measured refill-time policies. |
| Blackburn / managed-runtime methodology | GC cost is more than visible pause time. Allocation rate, locality, heap growth, mutator barriers, root scanning, and measurement overhead all affect the total result. | Keep L1 clean timing separate from L2/L3/L4 interpretation. When discussing "memory cost", include allocation, zeroing, bookkeeping, GC, and reclaim, not only collection pauses. |
| Hertz and Berger-style GC versus explicit memory work | Apparent GC overhead depends strongly on heap size. With large enough heap, GC may collect rarely; with tighter heaps, pauses and memory pressure become visible. | Use heap caps and RSS/fixed-memory rows for serious claims. A region win with zero GC on heap is still possible, but it must be explained as allocation/locality/RSS/tail behavior, not "collection avoided". |
| HotSpot TLAB and fast allocation | High-performance heap allocation is a compiler/runtime fast path: bump pointer, inline checks, and rare slow-path refill. | Checked Rift allocation should move closer to intrinsic bump allocation when backend is statically known. Generic method lookup and wrapper calls should be treated as avoidable lowering overhead only if tests preserve semantics. |
| HotSpot escape analysis / scalar replacement | The best allocation is often no allocation, but only when nonescape and initialization are proven. | Summary-only/direct-count rows are valid topology evidence, not memory-management evidence. A Rift zero-elision or allocation-elision pass needs compiler proof: no `this` escape, all fields assigned, no hidden heap retention. |
| Barrier-cost papers | Barriers are not universally dominant; their cost depends on placement, frequency, compiler treatment, and workload. | Do not assume `HeapRoot`, bridge handles, or root checks are expensive until profiles show them. Prefer measured removal inside operator-owned checked paths. |
| StreamFlex / scoped-memory real-time systems | Region/scoped memory is valuable for predictability and tail latency, not only mean throughput. Stable state, transient state, and transfer/capsule boundaries are the important concepts. | StreamFlex-style rows should report throughput plus p95/p99/max/deadline misses and GC max/count. Rift's checked `epoch` and page/window paths should be explained as stable/transient boundary APIs. |
| Broom and Yak | The durable-control versus high-churn-data split is central. Regions win when many data-path objects share an epoch/operator lifetime. | Every benchmark claim should state what remains on the heap and what moves into regions. Direct `RiftRegion.epoch` is the main checked topology for Yak-like workloads. |
| Stancu et al. | Region benefits depend on chosen scope, annotation/API burden, and phase-local allocation volume. | Keep Stancu/SPECjbb-style rows tied to transaction boundaries and report API burden plus region-freed object/byte proxies. |
| ReML / MLKit | Regions plus GC require careful treatment of polymorphism and higher-order values; local speedups are not enough if GC safety is unsound. | Keep ReML-style probes for generic hiding, closure escape, heap-retains-region, and polymorphic containers. Same-axes ReML tables should compare ratios and evidence classes, not raw cross-language wall-clock. |
| Reference-capability and active/closed-region work | Capability distinctions can clarify which references may mutate, escape, transfer, or survive close. | Use active/closed typestate, immutable/static metadata, and bridge/root handles as proof/runtime-overhead tools first. Do not expose a broad capability API until it removes measured runtime work or closes a concrete safety gap. |

## Concrete Rift Optimization Targets

### 1. Zeroing And Object Initialization

Current profiles still sample `_platform_memset` in checked allocation paths.
The literature makes this a valid target, but only under strict safety gates.

Safe next experiments:

- profile fresh-slab versus dirty-slab allocation separately;
- measure refill-time slab zeroing versus per-object dirty-slab zeroing, with
  focused allocation rows and application sanity gates;
- prototype compiler-proven no-zero only for a narrow record-like class family:
  final class, all instance fields definitely assigned before escape, no
  virtual calls during construction, superclass fields handled, arrays excluded.

Unsafe or misleading experiments:

- globally skipping zeroing;
- claiming speedup from manually rewriting objects into primitive arrays unless
  same-shape heap controls are present;
- using no-zero rows as safety-preserving evidence before compiler probes exist.

### 2. Allocation Lowering Toward A TLAB-Like Fast Path

The target shape is a compiler-visible bump-pointer fast path plus rare refill,
not repeated generic method lookup. Rift has already removed several wrapper and
bookkeeping costs, but checked allocation is still not as intrinsic as heap
allocation.

Safe next experiments:

- inspect current NIR lowering for `OpenStreamingRegion` allocation and count
  remaining call boundaries;
- add a backend-known internal intrinsic only when the static backend is known;
- keep public allocation APIs defensive while generated/operator-owned paths use
  the direct lowering;
- gate with `ObjectAllocationLoweringMatrix`, page-token, StreamFlexDesign, and
  Yak graphstep.

### 3. Barriers, Roots, And Metadata

The literature cautions against assuming barriers dominate. Rift should remove
root/barrier-like work only when the static model proves it unnecessary.

Safe next experiments:

- keep `HeapRoot` as the explicit bridge for mutable/dynamic heap metadata;
- allow static/immutable metadata references only when they cannot capture
  regions;
- treat root-free checked rows as disabled until rejection tests cover
  `HeapRoot`, unrooted dynamic heap references, heap-retains-region,
  outer-retains-inner, closure escape, and ReML-style generic hiding.

### 4. Traversal And Summary APIs

Traversal avoidance is often an algorithm/topology win, not a pure
memory-management win. This still matters for Rift because framework APIs can
make append-time summaries and bulk close natural, but claims must be labeled
correctly.

Safe next experiments:

- maintain same-shape heap controls for any summary-on-append operator;
- report summary-only rows as topology/operator lower bounds;
- use retained heap/drop-anchor versus retained checked region for reclaim
  claims;
- continue to avoid close-time scans in operator-owned paths only when output
  does not require per-record close traversal.

### 5. Latency And Fixed-Memory Evidence

StreamFlex-style work suggests that throughput alone is incomplete. A checked
region system can be valuable by reducing tail latency, max GC pauses, deadline
misses, or RSS even when median throughput is close.

Safe next experiments:

- run paced StreamFlex-design and streaming-input rows with p50, p95, p99,
  p999, max, deadline misses, GC max, and runs-with-GC;
- keep L1 final-clean elapsed/RSS as the headline source;
- keep L2/L3/L4 as interpretation only;
- add heap-cap rows when uncapped heap grows instead of collecting.

## Near-Term Decision Tree

1. Re-profile the latest `126e2950b` allocator state on the representative
   profile rows.
2. If allocation/zeroing remains dominant, prototype a narrow zeroing or
   allocation-lowering experiment.
3. If parser/hash/query CPU dominates, do not tune the allocator for that row;
   classify it as parser/control evidence or improve the shared parser under
   heap and region modes.
4. If traversal dominates but output can be computed on append, add a
   reusable same-shape summary API and a heap counterpart.
5. If latency tails show GC pauses, report latency/RSS/fixed-memory wins even
   when throughput is near-tied.

## Sources

- Blackburn et al.,
  ["Why Nothing Matters: The Impact of Zeroing"](https://www.microsoft.com/en-us/research/publication/why-nothing-matters-the-impact-of-zeroing/).
- Blackburn and Hosking,
  ["Barriers: Friend or Foe?"](https://openresearch-repository.anu.edu.au/entities/publication/15aeca80-8003-4ee3-bab5-58fc3b47de71).
- Blackburn et al.,
  ["The DaCapo Benchmarks: Java Benchmarking Development and Analysis"](https://research.ibm.com/publications/the-dacapo-benchmarks-java-benchmarking-development-and-analysis).
- Blackburn, Cheng, and McKinley,
  ["Myths and Realities: The Performance Impact of Garbage Collection"](https://research.ibm.com/publications/myths-and-realities-the-performance-impact-of-garbage-collection).
- Cai, Blackburn, Bond, and Maas,
  ["Distilling the Real Cost of Production Garbage Collectors"](https://www.steveblackburn.org/pubs/papers/lbo-ispass-2022.pdf).
- Hertz and Berger, "Quantifying the Performance of Garbage Collection vs.
  Explicit Memory Management".
- Oracle/OpenJDK documentation on
  [HotSpot performance enhancements and escape analysis](https://docs.oracle.com/en/java/javase/17/vm/java-hotspot-virtual-machine-performance-enhancements.html)
  plus the [OpenJDK escape-analysis note](https://wiki.openjdk.org/display/hotspot/escapeanalysis).
- StreamFlex and scoped-memory real-time stream processing work.
- Broom, Yak, Stancu et al., and ReML/MLKit papers already tracked in
  `docs/PRIOR_WORK_MEMORY_MANAGEMENT_INTERPRETATION.md`.
- Arvidsson et al.,
  ["Reference Capabilities for Flexible Memory Management"](https://www.microsoft.com/en-us/research/publication/reference-capabilities-for-flexible-memory-management/?locale=ja),
  and Stoldt et al.,
  ["Dynamic Region Ownership for Concurrency Safety"](https://www.microsoft.com/en-us/research/publication/dynamic-region-ownership-for-concurrency-safety/).
