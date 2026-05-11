# Prior Work Memory-Management Interpretation

Date: 2026-05-11
Last updated: 2026-05-11 13:30 CEST

Status: interpretation guide for the Rift report and benchmark design. This
file complements `docs/LITERATURE_BENCHMARK_CONTRACT.md`: that file records
benchmark targets and axes; this file records the higher-level lesson from the
prior systems.

## Core Lesson

The common thread across Broom, Yak, StreamFlex, Stancu et al., and ReML/MLKit
is not a catalog of reusable stream operators. The common thread is that each
system exposes a lifetime boundary that the ordinary collector cannot see
cheaply enough:

- Broom exposes dataflow/operator/fate-sharing lifetimes.
- Yak exposes the data path/control path split and epochal data-object
  lifetimes.
- StreamFlex exposes stream period/filter lifetimes to avoid pause-time
  interference.
- Stancu et al. expose coarse transaction or phase regions, then statically
  prove which allocation sites are safe.
- ReML/MLKit exposes compiler-inferred lexical regions and then studies how
  those regions interact with tracing GC and polymorphism.

The performance claim is therefore principled and general: objects with a
shared epoch/page/window/transaction lifetime should not be repeatedly traced,
promoted, evacuated, or discovered by a general-purpose collector. The system
should allocate them in a region-like lifetime domain and reclaim that domain
in bulk, while leaving durable or unpredictable objects on the normal GC heap.

## Prior-Work Reading

| System | Lifetime boundary | Why the paper says it can be faster | Main limitations / caveats | Rift lesson |
|---|---|---|---|---|
| Broom | Dataflow operators, actors, logical batches, and fate-sharing objects. | Big-data operators create high object churn in large heaps; many operator objects live no longer than the operator or logical batch, so region allocation avoids scanning a large heap. Broom reports GC can add up to about 40% runtime and emulated Naiad vertex runtime reductions around one third. | The HotOS work is a system proposal/proof of concept. Exact Naiad artifacts are not in this workspace, and the strongest claim depends on dataflow workloads with clearly bounded operator lifetimes. | Keep Dataflow SELECT/AGGREGATE/JOIN as methodology evidence; compare region lifetime placement, not benchmark-local array tricks. |
| Yak | Control space versus data space; data objects allocated in epochs. | Big-data systems create "sea of data objects" whose lifetimes align with epochs. Yak keeps control objects under regular tracing GC and frees data-space regions as whole epochs, reducing tracing of the data path and GC pauses. | Requires epoch boundaries and a runtime mechanism for objects escaping the data space. Original results are distributed JVM systems, not Scala Native; exact GraphChi/Hadoop/Hyracks reproduction is separate from local methodology rows. | Direct `RiftRegion.epoch` is central. Rift should use static capture/separation checks to reject escapes instead of relying on dynamic Yak-style promotion/barrier machinery. |
| StreamFlex | Stream filters, periods, and scoped memory for real-time stream processing. | The target is predictability: avoid abrupt GC interference and deadline misses in stream processing. StreamFlex frames the win in throughput and latency/tail behavior, not only mean elapsed time. | The model is a specialized Java stream language/runtime. Its strongest evidence is latency predictability; exact Ovm/StreamFlex artifact reproduction is not available here. | Report p95/max latency and deadline misses for StreamFlex-shaped rows. Region wins can be tail wins even when median throughput is modest. |
| Stancu et al. | Programmer-marked transaction/phase scopes plus static analysis of region-safe allocation sites. | Phase-local allocation can be region-allocated and freed on region exit; the paper reports up to about 78% region-allocatable memory and reduced GC/collection pressure, especially under young-generation pressure. | Needs annotations and static analysis; benefits depend on phase choice and heap/young-gen pressure. Official SPECjbb2005 cannot be run directly on Scala Native, so local rows are ports/methodology unless exact artifacts are used. | Use checked epochs for transaction-local objects, report region-freed object/byte proxies and heap-cap sensitivity, and be explicit about API/annotation burden. |
| ReML / MLKit | Compiler-inferred regions plus GC-safe handling of polymorphic/higher-order values. | Region inference can reduce or remove reference-tracing GC for many values; MLKit also combines regions with tracing GC where dynamic behavior remains. The key PLDI 2023 point is that GC safety with type polymorphism requires careful region/effect tracking. | Not a stream-processing system and not directly comparable by raw wall-clock across languages. Exact artifact reruns are still open; local Scala Native ports are only shaped comparisons. | Keep ReML-style polymorphic safety probes in Rift. Compare ratios, RSS, GC counts/time, and safety burden rather than claiming raw cross-language wins. |

## What This Means For Rift

Rift should be described primarily as a checked region/lifetime system, not as a
bag of benchmark-specific operators. Operators matter because they are how a
framework exposes lifetimes to the runtime:

- `RiftRegion.epoch { ... }` exposes a batch/transaction/graph-step lifetime.
- Page/window token APIs expose event-page or bucket lifetimes.
- Top-k, join, rank, and median APIs should exist only when they expose a real
  shared lifetime and can beat same-shape heap controls.

The current report should therefore separate:

- **memory-management evidence:** heap and region both retain ordinary objects
  until the boundary, then heap drops anchors and GC reclaims later while the
  region closes/resets in bulk;
- **topology/operator evidence:** both heap and region update summaries on
  append and avoid retaining objects, proving a good data-processing topology
  rather than a reclaim win;
- **latency/RSS evidence:** GC time may be a small median fraction, but region
  placement can still cut RSS, heap-cap failures, or max/tail pauses;
- **lower-bound evidence:** rootless/trusted modes and manual arrays show what
  the backend might do, not what the safe user-facing system can claim.

## Design Choices Worth Borrowing

The following ideas are useful for Rift, but they should be adopted only when
they simplify the checked story or remove measured runtime work.

| Prior idea | Why it is useful | Rift interpretation |
|---|---|---|
| Broom control/data path split | It explains why regions help dataflow systems: control state is durable, data-path records are short-lived. | Every benchmark/API should state what remains on the heap/control path and what moves into the region/data path. |
| Yak data space versus control space | Yak avoids tracing the data path and keeps unpredictable control objects under GC. | `RiftRegion.epoch` is the checked static version of this split. Instead of Yak-style promotion/barriers, reject escaping data-space references statically where possible. |
| Yak epoch pages and remembered sets | The memory layout physically separates data-space epochs from the ordinary heap. | SafeZone-backed checked regions and Rift streaming backends should be judged by page/slab allocation, epoch close cost, and whether blanket roots are avoided. |
| StreamFlex stable/transient/capsule regions | This gives a vocabulary for stable stream state, transient scratch data, and data transferred between pipeline stages. | Rift can use `epoch`, `page/window`, and explicit output/export handles as the equivalent vocabulary. It should report latency and deadline/tail effects, not only throughput. |
| Stancu transaction regions | Coarse transaction scopes are understandable and statically checkable. | Keep the SPECjbb/Stancu port as transaction-lifetime evidence; count API/annotation burden and region-freed object proxies. |
| ReML GC-safety for polymorphism | Region values hidden in generic or higher-order code can become GC-unsafe if effects are erased. | Keep ReML-style probes: generic containers widened to `AnyRef`, heap arrays, escaping closures, and polymorphic consumers. |
| Dynamic region ownership active/closed states | Active regions can be mutated; closed/frozen regions can be isolated or transferred if references obey the capability discipline. | Use active/closed type-state as proof vocabulary for no use-after-close, nested child-region close ordering, and possible future transfer safety. |
| Reference capabilities | Capabilities distinguish mutable, read-only/immutable, transferable, and region-scoped references. | Capture/separation checking can express much of this. A future user-facing design could expose mutable active region refs, immutable/static metadata refs, `HeapRoot` bridge handles, and closed/transferable region handles. |
| Bridge/root objects | A bridge can connect lifetimes without rooting or scanning the whole region. | `HeapRoot`, rooted metadata, and possible future bridge handles can reduce blanket GC root registration while keeping mixed heap-region references explicit. |

The caution is that every new capability increases user-facing complexity. The
right sequence is:

1. Use capture/separation checking for the common single-threaded stream case.
2. Add active/closed/nested-region vocabulary to the design and proof story.
3. Add immutable/static metadata and bridge handles only where they remove
   measurable root-registration or close-time scanning overhead.
4. Defer transferable/concurrent ownership until a benchmark or concurrency
   use case needs it.

## Evaluation Principle

Prior systems do not compare every possible heap rewrite against every possible
region topology. They choose a lifetime topology justified by the system and
then measure the axes that expose the memory-management effect.

For Rift, that means:

1. State the natural lifetime boundary first: epoch, page, window, transaction,
   or whole run.
2. State which objects live in regions and which remain on heap.
3. Use the same logical query and checksum/output semantics.
4. Add same-shape heap controls when the topology changes computation.
5. Treat summary-only/direct-aggregate rows as topology lower bounds, not
   memory-management wins.
6. Treat retained heap/drop-anchor versus retained checked region as the
   clearest memory-management comparison.
7. Report prior systems on their native axes, then add Rift's standardized
   local metrics separately.

## Sources

- Broom: [USENIX HotOS 2015](https://www.usenix.org/conference/hotos15/workshop-program/presentation/gog), [paper PDF](https://www.usenix.org/system/files/conference/hotos15/hotos15-paper-gog.pdf).
- Yak: [USENIX OSDI 2016](https://www.usenix.org/conference/osdi16/technical-sessions/presentation/nguyen), [paper PDF](https://www.usenix.org/system/files/conference/osdi16/osdi16-nguyen.pdf).
- StreamFlex: [paper PDF](https://infoscience.epfl.ch/bitstreams/c5fd2b30-5712-4f80-9a98-6120b99b9987/download).
- Stancu et al.: [ISMM 2015 page](https://conf.researchr.org/details/ismm-2015/ismm-2015-papers/4/Safe-and-Efficient-Hybrid-Memory-Management-for-Java), [paper PDF](https://codrutstancu.com/papers/p81-stancu.pdf).
- ReML/MLKit: [Elsman PLDI 2023 PDF](https://elsman.com/pdf/gcsafe-pldi23.pdf), [MLKit papers page](https://elsman.com/mlkit/papers).
