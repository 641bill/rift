# Stream GC Evidence And Prior-Work Comparison Plan

Date: 2026-04-25

Status: research/roadmap memo. This is not a benchmark result pack.

## 1. Current Rift DEBS Object Placement

Current implementation evidence is in:

- `/Users/siyaoliu/rift/scala-native-rift/bench/debs2015/RESULTS.md`
- `/Users/siyaoliu/rift/scala-native-rift/docs/HANDOFF.md`
- `/Users/siyaoliu/rift/scala-native-rift/DESIGN.md`

As of commit `8e3b78f0f` in `scala-native-rift`, Rift modes region-allocate:

| Data or control object | Current Rift placement | Lifetime boundary |
|---|---|---|
| RunBoth input byte buffer | Region | Whole run |
| Q1 bucket window entries | Region | Per dropoff-second bucket |
| Q2 profit window entries | Region | Per dropoff-second bucket |
| Q2 empty-taxi window entries | Region | Per dropoff-second bucket |
| Q2 active profit values | Inside region window entries | Per profit-window bucket |
| Q2 median scratch array | Region | Whole query, capacity-grown |
| Q1 `RankedRoute` / `Route` / `Cell` ranking objects | Region | Whole query/ranking region |
| Q2 `ProfitableArea` ranking objects | Region | Whole query/ranking region |
| Reusable top-k result arrays | Region | Whole query/ranking region |
| Q2 per-cell tables | Region arrays | Whole query/ranking region |
| Q1 primitive route table arrays | Region arrays | Whole query/ranking region |
| Q2 latest-empty taxi table | Region array | Whole query/ranking region |
| Q2 ranking index | Region arrays | Whole query/ranking region |

Still GC-managed or likely heap-allocating:

| Remaining path | Why it matters |
|---|---|
| Q1 ranking `TreeSet` | Java tree nodes remain heap metadata; a first indexed-heap replacement was correct but slower and was backed out. |
| Q1/Q2 `Grid.cell(...)` | Hot path returns `Option[Cell]`, so valid cells likely allocate `Some` and `Cell` objects before being packed into keys. |
| `TaxiIds` map and interned taxi ID strings | Durable metadata with unpredictable lifetime; heap placement is currently intentional. |
| Previous-output snapshots | Heap primitive arrays retained between outputs so region-backed results do not escape. |
| Latency buffers | Heap `ArrayBuffer[Long]`; instrumentation-only but included in measured runs. |
| Bucket queue control objects | Heap `mutable.Queue` nodes and bucket wrapper objects; the payload entries are region-backed. |
| File writers and output plumbing | Durable I/O/control metadata; heap placement is expected. |

## 2. Why Current Real-Data Speedup Is Modest

The latest 1M bounded DEBS median after Q2 array-backed ranking is:

| Mode | Elapsed ms | GC ms | Q2 process ms | Rift op ms | RSS bytes |
|---|---:|---:|---:|---:|---:|
| heap | 11202.975 | 423.932 | 6761.082 | 0.000 | 431718400 |
| Rift HPZone | 10808.901 | 348.901 | 6430.000 | 14.861 | 383631360 |
| Rift Streaming | 10804.756 | 344.376 | 6462.097 | 14.684 | 383631360 |

Two implications:

- Heap GC time is about `3.8%` of heap elapsed at this checkpoint. Even deleting all GC time would not produce a Yak-scale speedup on this exact workload.
- Q2 processing is about `60%` of elapsed. The current bottleneck is mostly CPU/data-structure work in the query, not region allocation overhead.

This does not mean regions are unimportant. It means the current bounded DEBS
path has already removed enough heap churn that the remaining single-node
runtime is dominated by query work. Region evidence must therefore be judged by:

- GC time and RSS reduction;
- tail-latency reduction when GC pauses are visible;
- scale-up behavior on larger inputs/heaps;
- cases where data-path object churn is still large;
- annotation/safety advantages over dynamic systems.

## 3. External Evidence: GC Is Real, But Workload-Dependent

The literature and production-system docs support a nuanced answer.

| Source | What it says | Implication for Rift |
|---|---|---|
| Broom, HotOS 2015 | Big-data systems create many fate-sharing objects; the paper reports GC increasing typical data processing task runtime by up to `40%` and region-based management reducing emulated Naiad vertex runtime by up to about `34%`. | There are dataflow workloads where region lifetimes matter a lot. Reproduce Broom-style vertices, not just DEBS. |
| Yak, OSDI 2016 | USENIX abstract says big-data managed runtimes suffer from massive object creation and GC strain; Yak splits control space from data space, allocating epochal data-path objects in regions. | Our control/data split is directly aligned with Yak, but Rift must show static safety instead of Yak's dynamic barriers/STW promotion. |
| Spark tuning guide | Spark says programs can be bottlenecked by CPU, network, or memory; GC is a problem with high object churn, and GC cost is proportional to the number of Java objects. | It is expected that GC is not always the bottleneck. Our benchmark plan must measure phase shares before claiming region wins. |
| Flink memory management docs/blog | Flink stores records serialized in pooled memory segments rather than gathering long-lived records as objects; off-heap memory is motivated by avoiding large-heap GC stalls and reducing copies. | Modern stream systems already avoid naive object heaps. Rift's target should be safe region-backed object/data structures, not merely "objects vs raw bytes." |
| Ousterhout et al., NSDI 2015 | Their Spark study found CPU often dominates and network improvements had limited median effect. | This validates our own finding that after memory cleanup, real workloads may become CPU-bound. We still need allocation-heavy and latency-sensitive workloads. |
| StreamFlex, OOPSLA 2007 | StreamFlex targets high-throughput/low-latency stream processing with type-safe region allocation and a stricter filter discipline. | We should compare on latency-sensitive StreamIt-style kernels, not only throughput. |
| Stancu et al., ISMM 2015 | Static analysis plus coarse annotations found up to `78%` memory region-allocatable, with GC fallback for the rest. | Rift should report "region-allocatable fraction" and annotation count, not just elapsed time. |

Primary links to keep in the bibliography:

- Broom PDF: `https://cs.brown.edu/people/malte/pub/papers/2015-hotos-broom.pdf`
- Yak USENIX page: `https://www.usenix.org/conference/osdi16/technical-sessions/presentation/nguyen`
- StreamFlex IBM page: `https://research.ibm.com/publications/streamflex-high-throughput-stream-programming-in-java--1`
- Stancu et al. ISMM page: `https://conf.researchr.org/details/ismm-2015/ismm-2015-papers/4/Safe-and-Efficient-Hybrid-Memory-Management-for-Java`
- Spark tuning guide: `https://spark.apache.org/docs/latest/tuning.html`
- Flink off-heap memory blog: `https://flink.apache.org/2015/09/16/off-heap-memory-in-apache-flink-and-the-curious-jit-compiler/`
- Flink memory management page: `https://cwiki.apache.org/confluence/pages/viewpage.action?pageId=53741525`
- Ousterhout et al. NSDI page: `https://www.usenix.org/conference/nsdi15/technical-sessions/presentation/ousterhout`

## 4. What We Should Compare Against

### Broom-Style Dataflow Vertices

Goal: reproduce the methodology, not the closed prototype.

Benchmarks to add in Scala Native:

| Broom anchor | Rift benchmark shape | Required evidence |
|---|---|---|
| SELECT | Stateless map/filter over region-allocated message batches | Throughput, GC time, region op time, allocations/event |
| AGGREGATE | Group-by/window aggregate with per-key state and per-batch temp regions | Throughput, GC time, RSS, region-allocatable fraction |
| JOIN | Windowed join with transferable message batches and actor/operator state | Throughput, latency, GC/RSS, escape fraction |

Design rule: heap and Rift must share logical operators. Rift differs only by
allocation placement and lifetime boundary annotations.

### Yak-Style Epochal Data Path

Goal: show the control/data split on workloads where data objects die by epoch.

Benchmarks to add:

| Yak anchor | Rift approximation |
|---|---|
| Hadoop/Hyracks group-by and join | Single-node batch/stream group-by and join over epoch regions |
| GraphChi/Giraph supersteps | Iterative graph superstep benchmark with per-superstep data regions and heap control state |
| Escaping object rarity | Instrument region objects that must be retained beyond an epoch and report escape fraction |

Metrics must include:

- GC time reduction;
- elapsed time;
- p99/p99.9 pauses or per-event latency;
- object allocation count/fraction in regions;
- annotation count;
- no write barrier / no STW promotion overhead, if the safe API supports the claim.

### StreamFlex / StreamIt Latency

Goal: test latency-sensitive streaming, not only total throughput.

Benchmarks to add:

- StreamIt-like `FilterBank`;
- StreamIt-like `BeamFormer`;
- packet/IDS-style filter chain if data is available or can be generated.

Rift target:

- ordinary Scala objects allowed in regions;
- transient per-tick region;
- stable per-filter/operator region;
- heap control fallback for unpredictable metadata;
- p50/p99/p99.9 latency and deadline misses.

### Stancu-Style Static Hybrid Evaluation

Goal: evaluate safety/ergonomics as well as speed.

Add a report table per benchmark:

| Metric | Meaning |
|---|---|
| Region-allocatable allocation sites | Allocation sites safe under the region/capture rules |
| Region-allocated bytes/objects | Dynamic fraction of data moved out of GC |
| Escapes/fallbacks | Objects that must stay on heap |
| Annotation count | Region annotations per KLOC |
| Compile/check time | Capture-checking overhead |

This is the direct comparison to Stancu et al.'s "region-allocatable memory"
claim, and it avoids over-indexing on elapsed time.

## 5. Immediate Technical Plan

Do not jump directly to another data-structure replacement. First measure the
remaining heap churn.

1. Add low-overhead DEBS counters for:
   - `Grid.cell` calls and successful cells;
   - Q1 `TreeSet` add/remove/update count;
   - Q1/Q2 output snapshot allocations;
   - latency buffer appends;
   - taxi-id intern count and map hit/miss count.
2. Rerun 100k and 1M instrumented matrices with counters.
3. Decide next implementation from those counters:
   - If `Grid.cell`/`Option[Cell]` churn is high, add a shared no-allocation
     `Grid.cellKeyOrZero` hot path. This is noise removal, not a Rift-specific
     win, but it clarifies the remaining memory story.
   - If Q1 `TreeSet` churn is high, do not repeat the failed indexed-heap
     replacement. Try a Q1 rank-cache design that computes top-10 only when the
     rank version changes, or a specialized ordered structure validated against
     the current `TreeSet`.
   - If latency arrays matter, gate latency recording or replace it with fixed
     histograms so instrumentation does not become part of the memory story.
   - If durable taxi metadata dominates, leave it on heap unless a safe root
     handle design exists; this is exactly the GC fallback use case.
4. In parallel, add a Broom-style `select/aggregate/join` benchmark pack under
   `sandbox` or `bench/dataflow`, because DEBS alone may now be too CPU-bound
   to demonstrate the full memory-management contribution.

## 6. Do We Need More PDFs?

Not immediately for the high-level direction: the local literature review plus
public primary pages are enough to set the plan.

PDFs are useful for the next step if we want exact reproduction details:

- Broom: exact SELECT/AGGREGATE/JOIN setup and reported tables.
- Yak: exact Hadoop/Hyracks/GraphChi benchmark configurations and pause/GC
  metrics.
- StreamFlex: exact StreamIt benchmark parameters and latency/deadline setup.
- Stancu et al.: exact `@RegionScope` annotation method, region-allocatable
  fraction tables, and SPECjbb2005 setup.

If these PDFs are available locally, put them under `docs/literature/` or
record their paths in this memo. Do not rely on memory for exact benchmark
parameters.

## 7. Bottom Line

Current DEBS does show that Rift can move ordinary Scala objects and ranking
arrays into regions safely enough for trusted HPZone benchmarking, and it now
has modest bounded-sample elapsed/GC/RSS wins. It does not yet show the big
GC-collapse story from Yak or Broom because the current single-node DEBS path is
mostly Q2 CPU/data-structure work after object-churn cleanup.

The next evidence target should be two-pronged:

1. finish diagnosing remaining DEBS heap churn without hand-specializing the
   benchmark; and
2. add Broom/Yak/StreamFlex-shaped workloads where structured data lifetimes are
   the dominant cost and where prior systems reported their wins.
