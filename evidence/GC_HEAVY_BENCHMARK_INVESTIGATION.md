# GC-Heavy Data Processing Benchmark Investigation

Date: 2026-05-15
Last updated: 2026-05-16 19:31 CEST

Status: literature and online-investigation note. This is not a benchmark
result pack. It records where GC pressure is expected in stream/data-processing
systems, why many real-file streaming rows are not GC-heavy, and which
benchmark families should be tried next.

## Main Finding

Streaming input does not automatically create a GC-heavy workload. A row becomes
GC-heavy only when it combines high allocation rate, ordinary GC-visible object
materialization, retention until a window/epoch/session/join boundary, and a
heap that cannot simply absorb the allocation without collecting. Many current
real-input rows read bytes or lines, update compact counters or primitive
arrays, and discard each parsed record quickly. Those rows are valid streaming
systems, but they are parser/hash/query dominated rather than GC dominated.

This explains the current evidence shape:

- generated Common Crawl-shaped rows are GC-heavy because they intentionally
  materialize many ordinary page/token/window records and retain them until a
  page/window boundary;
- Yak LiveJournal is strong real-input evidence because edge-update records
  naturally share epoch lifetimes and heap pays visible collection/RSS cost at
  scale;
- LogHub/GH Archive/Theodolite/DSPBench real-streaming rows are useful
  throughput/RSS/tail controls, but their parser, hashing, or compact-state
  work often dominates elapsed time.

2026-05-16 follow-up: increasing active windows can expose heap-cap pressure,
but it is still not sufficient by itself. HDFS `q3-template-session`
`streaming-file` with 16 live buckets slows heap materially under a `256M` cap
(`1989.577 ms` timed GC over `17` collections) and fails at `128M`; the checked
page-token row completes with matching checksum/output and zero timed GC. The
checked row's RSS is high under this topology, however, so the lesson is not
"more active buckets wins"; it is that retained real session/template objects
can stress heap only when the logical topology also keeps region live payload
bounded.

The same day, the Broom/Naiad-style retained dataflow benchmark was scaled to
5M records with 16 active timestamps. This is the stronger next-benchmark
direction: aggregate heap spends `176.734 ms` of `869.384 ms` in timed GC, and
join spends `147.124 ms` of `791.787 ms` in timed GC. Checked Rift removes
timed GC and cuts L1 RSS from `235-362 MB` to `53-57 MB` while improving L1
elapsed by about `25-28%`. This supports the investigation's priority order:
retained dataflow/session/join shapes are more promising than simply reading
larger real log files.

2026-05-16 18:20 follow-up: the same Broom/Naiad-style active-16 row was
scaled to 20M records. It is now the strongest GC-heavy methodology case:
aggregate heap spends `953.153 ms` median timed GC inside `4235.563 ms`, with a
`2241.709 ms` max GC tail; checked Rift is `2904.092 ms` with zero timed GC.
Join heap spends `486.649 ms` median timed GC inside `3133.932 ms`; checked
Rift is `2864.439 ms` with zero timed GC. L1 final-clean rows are
`10.78 -> 8.48 s` for aggregate and `9.88 -> 8.09 s` for join; RSS drops from
`236/438 MB` heap to `53/57 MB` checked Rift. Heap completes at `512M` but fails at `384M` and
`256M`, while the checked rows complete at about `53-57 MB` RSS. A new real
LogHub retained session/join streaming-file triage row, however, remains
parser/hash dominated: session heap GC is only `82.341 ms` inside
`6595.172 ms`, and join heap GC is only `9.474 ms` inside `6837.810 ms`.
Therefore, larger retained real log rows are not automatically sufficient; the
best next real candidates need Broom-like high-cardinality retained state or
transaction/graph epochs where object management is a larger share of work.

2026-05-16 18:39 second search pass: a fresh prior-work/official-source pass
confirms the same direction. Spark's tuning guide says GC cost becomes a
problem with high object churn and many Java objects, and specifically calls out
object headers, strings, boxed primitives, `HashMap`, and `LinkedList` wrapper
objects. Flink's heap state backend keeps state as heap objects, while its TTL
cleanup documentation explicitly notes that incremental cleanup can increase
record-processing latency. SPECjbb2005 is explicitly designed to exercise Java
object manipulation and garbage collection. HiBench, BigDataBench, and
Renaissance are useful workload catalogues, but they are not automatically
Rift-shaped; use them to select retained joins, graph/text epochs, stateful
wordcount/top-k, PageRank, and transaction-like object workloads, not as opaque
distributed-framework runs. The immediate benchmark-search decision is:

1. **Implement one more Broom/Naiad-style retained dataflow shape** before
   another real-log row: TPC-H-Q17-like retained join/aggregate or a shopper
   JOIN-SELECT-JOIN shape. This is the strongest literature match for
   `20-40%` GC time and maps directly to Rift timestamp/epoch regions.
2. **Add a StreamFlex-style retained event-correlation/transaction-tracking
   latency row**. This targets p95/p99/max/deadline misses and GC max, not only
   median throughput.
3. **For real input, prefer larger graph/text/state workloads**: larger
   StackExchange/StackOverflow text epochs, larger SNAP/Twitter graph epochs,
   high-cardinality LogHub session/template dictionaries, and Alibaba-style
   machine-usage traces if provenance is clean.
4. **Treat HiBench/BigDataBench/Renaissance as catalogues**, not headline
   systems. A local single-process retained kernel is preferable to importing
   Spark/Flink/Hadoop runtime overhead when the question is memory management.

Concrete provenance notes from this pass:

- SNAP Twitter-2010 is public and has the right graph-epoch shape, but it is a
  large disk/time commitment: `41,652,230` nodes and `1,468,364,884` edges.
- Alibaba Cluster Trace 2018 is public and relevant for Machine Outlier /
  cluster-usage stream shapes. The full archive is about `49G`; the
  `machine_usage` slice is about `1.7G`, making it the first plausible subset
  to pin if DSPBench Machine Outlier is revived.
- TPC-H should use official DBGEN/QGEN when we build a Q17-like retained
  join/aggregate methodology row. This will be generated benchmark data, not
  real-input proof, but it is the closest Broom/Naiad paper-axis match.

2026-05-16 19:31 backend implication: it is plausible that many public
real-input rows will not become strongly GC-heavy under Scala Native Immix.
Immix is already a fast mark-region collector with cheap allocation and good
reclamation behavior when objects die young or when the heap has enough headroom.
That does not invalidate Rift; it narrows the expected win conditions. The
current evidence should be presented as:

- Scala Native Immix is a strong baseline, not a weak strawman;
- Rift wins most clearly when logical lifetime topology lets it avoid tracing
  retained transient object graphs or reduce RSS/fixed-memory/tail behavior;
- if public real-input streams remain parser/hash dominated, the stronger
  benchmark story should combine real-input modest/RSS/tail rows with
  prior-work-methodology GC-heavy rows such as Broom/Naiad and StreamFlex-style
  retained workloads;
- the longer-term project should separate the Scala-level checked topology
  model from backend lowering, so JVM, Scala.js, Wasm, and analysis-only
  backends can inherit the safety story even if their allocation strategies
  differ from Scala Native.

## Why Real Streaming Rows Often Are Not GC-Heavy

Production stream processors are usually engineered to avoid avoidable
allocation:

- parsers reuse byte/string buffers or deserialize into compact state;
- counters, summaries, and keyed state are stored in arrays, maps, or external
  state backends rather than as retained per-record objects;
- watermarks/windows close frequently enough that young objects die young;
- RocksDB/off-heap state, serialization, object reuse, and batch/vectorized
  execution shift pressure away from tracing GC and toward CPU/RSS/IO;
- simple parse/filter/count queries do not retain enough ordinary objects to
  force a large heap collection.

For Rift, this means a real stream workload must naturally retain intermediate
objects, not merely read a large real file. Good candidates are sessions,
joins, event correlations, alert/feature pipelines, graph epochs, transaction
batches, top-k/template candidates, and windowed state that cannot legally be
summarized away before the lifetime boundary.

## Prior-Work Signals

| Source | What it says about GC pressure | Rift implication |
|---|---|---|
| Broom / Naiad | Dataflow workloads such as TPC-H Q17, shopper, and SCC can spend about `20-40%` of runtime in GC when operator objects and per-timestamp state churn in a large heap. | Build Broom-like join/aggregate/session workloads with retained ordinary tuples and dictionaries, not only count-array summaries. |
| Yak | Big-data systems create a "sea of data objects" with epochal lifetimes. Yak's strongest rows are Hyracks/Hadoop/GraphChi-style tasks over large inputs such as YahooWebmap, StackOverflow text, and large graph partitions. | Keep `RiftRegion.epoch` as the main safe topology for graph/text/dataflow epochs; scale LiveJournal/SNAP and StackExchange only when disk/time allow. |
| StreamFlex | The key axis is latency predictability: stable state stays durable, transient stream objects live in scoped periods, and GC interference shows up as deadline misses/tails. | Treat throughput, p95/p99/p999/max latency, deadline misses, RSS, and GC max/count as first-class axes. Event correlation, transaction tracking, IDS, and retained capsule workloads are better targets than primitive BeamFormer/FilterBank alone. |
| Stancu et al. | Phase/transaction-local Java allocation can be region-freed; the paper reports large region-freed fractions and fewer young collections under small young-gen pressure. | Keep SPECjbb2005-style transaction ports and heap-cap rows; report API/annotation burden and region-freed object proxies. |
| ReML/MLKit | Region+GC systems must handle polymorphic and higher-order safety, and benchmark claims include real time, RSS, and GC count. | Keep ReML-shaped ports as same-axes safety/comparison evidence, not the main stream proof. |

## Industrial / Practitioner Signals

| Source family | Observed signal | Rift implication |
|---|---|---|
| Apache Spark tuning docs and GC-overhead reports | Many Java objects, boxed values, `String`, `HashMap`, `LinkedList`, shuffle/groupBy/join/cache state, and combinatorial keys can make GC dominant. Spark guidance pushes serialized or primitive layouts to reduce object overhead. | Good Rift candidates look like groupBy/join/top-k/session/shuffle object churn with same-shape heap controls. Pure primitive/vectorized Spark-style rewrites are topology/layout controls, not memory-management wins. |
| Apache Flink heap state, RocksDB state, and object reuse guidance | Heap state can cause GC pauses; RocksDB/off-heap backends reduce GC unpredictability but trade toward serialization/RSS. Object reuse reduces allocation but complicates correctness. | Compare Rift against heap-state shapes when objects are retained, and classify RocksDB/off-heap-like designs as RSS/latency tradeoff baselines, not ordinary heap controls. |
| Kafka Streams state stores | Large state is often RocksDB/off-heap; memory pressure may appear as RSS/block cache rather than tracing-GC time. | Stream workloads using external/off-heap state are not ideal pure GC baselines unless a heap-state variant is also measured. |
| Developer reports of GC overhead in Spark/Flink jobs | Problems cluster around high-cardinality grouping, joins, cached intermediate objects, large key spaces, and retained state, not simple line parsing. | Search for real datasets that force retained key/session/window objects rather than merely increasing bytes read. |

## Next Candidate Ladder

| Priority | Candidate shape | Why it is promising | First local action |
|---:|---|---|---|
| 1 | Broom-like TPC-H Q17 / shopper retained dataflow | Prior work explicitly reports high GC share in join-heavy dataflow workflows and our Broom active-16 row already reproduces material Scala Native GC pressure. | Add one Q17-like retained join/aggregate and one shopper-style JOIN-SELECT-JOIN shape with natural heap/GC versus checked Rift headline rows. |
| 2 | StreamFlex event-correlation / transaction-tracking / IDS design rows | StreamFlex's strongest story is latency/tail GC interference, stable/transient state, and scoped periods, not just primitive DSP throughput. | Extend `StreamFlexDesignMatrix` with retained event-correlation and transaction-tracking variants, paced latency, p99/p999/max, and deadline misses. |
| 3 | Yak-scale graph/text epochs | LiveJournal already works; Yak's original graph/text rows were much larger and more epochal. | Scale LiveJournal/SNAP if feasible; only fetch Twitter-2010 or larger StackExchange after disk/time preflight. |
| 4 | Spark/Flink-like high-cardinality groupBy/join/top-k/session | Official Spark/Flink guidance points to many retained heap objects and heap state as the GC-sensitive shape. | Use real LogHub/StackExchange/GH Archive fields to build retained keyed-state rows plus checked epoch/page/window counterparts. |
| 5 | SPECjbb/Stancu transaction batches | SPECjbb2005 is explicitly object-oriented and GC-exercising, and Stancu uses it as the phase/transaction-local region anchor. | Continue SPECjbb2005-workload port scaling, heap caps, region-freed proxies, and API-burden reporting. |
| 6 | Heap-state versus region-state time-series windows | Flink heap-state/TTL evidence suggests retained window state can affect latency, while off-heap backends trade toward serialization/RSS. | Use Theodolite/UCI power rows only if the query retains ordinary measurement/window objects, not just primitive aggregates. |
| 7 | HiBench / BigDataBench / Renaissance catalogue rows | They provide standard names and workload families, but opaque Spark/Flink/JVM harnesses can hide Rift's memory-management effect. | Port only the retained kernels that match Rift lifetimes: SQL join/aggregate, PageRank/graph epochs, stateful wordcount/top-k, k-means/list-heavy variants. |
| 8 | ReML allocation/list programs | Useful same-axes region+GC safety comparison; less stream-specific. | Add optional Tier 2 ports only after real-input pass or when very cheap. |

## Search Gates

A candidate advances to a serious case study only if:

- it uses public/provenance-clean real input or a clearly labeled prior-work
  methodology generator;
- heap naturally allocates and retains ordinary intermediate objects until a
  boundary;
- checksum/output matches across modes;
- heap shows material median GC, max/tail GC, heap-cap sensitivity, or much
  higher RSS with no elapsed advantage;
- the checked Rift row either beats heap/best safe baseline by about `10%`, or
  materially reduces RSS/GC/tail latency with no more than `5%` elapsed
  overhead.

If a row is parser/IO/hash dominated and heap GC stays below `2-3%` elapsed,
park it as ceiling/control evidence and move to a more retained-object-heavy
candidate.

## Sources

- Broom HotOS 2015 paper:
  <https://www.usenix.org/system/files/conference/hotos15/hotos15-paper-gog.pdf>
- Yak OSDI 2016 page and paper:
  <https://www.usenix.org/conference/osdi16/technical-sessions/presentation/nguyen>
- StreamFlex paper:
  <https://infoscience.epfl.ch/bitstreams/c5fd2b30-5712-4f80-9a98-6120b99b9987/download>
- Stancu et al. ISMM 2015 paper:
  <https://codrutstancu.com/papers/p81-stancu.pdf>
- Apache Spark tuning guide:
  <https://spark.apache.org/docs/latest/tuning.html>
- Apache Flink state backend and TTL cleanup guidance:
  <https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/state_backends/>,
  <https://flink.apache.org/2019/05/17/state-ttl-in-flink-1.8.0-how-to-automatically-cleanup-application-state-in-apache-flink/>
- Apache Flink low-latency and state-backend guidance:
  <https://flink.apache.org/2022/05/18/getting-into-low-latency-gears-with-apache-flink-part-one/>,
  <https://flink.apache.org/2021/01/18/using-rocksdb-state-backend-in-apache-flink-when-and-how/>
- Apache Flink object-reuse documentation:
  <https://nightlies.apache.org/flink/flink-docs-release-1.15/docs/dev/dataset/overview/>
- Kafka Streams memory management:
  <https://kafka.apache.org/28/streams/developer-guide/memory-mgmt/>
- HiBench:
  <https://github.com/Intel-bigdata/HiBench>
- BigDataBench:
  <https://www.benchcouncil.org/BigDataBench/>
- Renaissance:
  <https://github.com/renaissance-benchmarks/renaissance>
- SPECjbb2005:
  <https://www.spec.org/jbb2005/>
- Example practitioner GC-overhead reports:
  <https://stackoverflow.com/questions/27462061/why-does-spark-fail-with-java-lang-outofmemoryerror-gc-overhead-limit-exceeded>,
  <https://stackoverflow.com/questions/52069879/pyspark-java-lang-outofmemoryerror-gc-overhead-limit-exceeded>,
  <https://stackoverflow.com/questions/77677416/high-latency-in-flinks-keyby-operation>
