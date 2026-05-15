# GC-Heavy Data Processing Benchmark Investigation

Date: 2026-05-15
Last updated: 2026-05-15 17:36 CEST

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
| 1 | Broom-like join/aggregate/session pressure | Prior work explicitly reports high GC share in dataflow joins/aggregates and operator-local state. | Add a retained-object Broom-style Q17/shopper-inspired matrix or extend `DataflowRegionMatrix` with retained tuple dictionaries and same-shape heap controls. |
| 2 | StreamFlex event-correlation / transaction-tracking / IDS design rows | StreamFlex's strongest story is latency/tail GC interference, not just primitive DSP throughput. | Extend `StreamFlexDesignMatrix` with retained event-correlation and transaction-tracking variants, paced latency, and deadline misses. |
| 3 | Yak-scale graph/text epochs | LiveJournal already works; Yak's original graph/text rows were much larger and more epochal. | Scale LiveJournal/SNAP if feasible; only fetch Twitter-2010 or larger StackExchange after disk/time preflight. |
| 4 | Spark/Flink-like high-cardinality groupBy/join/top-k/session | Practitioner GC complaints concentrate here; objects are retained in keyed state/windows. | Use real LogHub/StackExchange/GH Archive fields to build same-shape heap retained keyed-state rows plus checked epoch/page/window counterparts. |
| 5 | Heap-state versus region-state time-series windows | Flink/RocksDB evidence suggests heap state can cause GC while off-heap trades RSS/serialization. | Use Theodolite/UCI power rows only if the query retains ordinary measurement/window objects, not just primitive aggregates. |
| 6 | SPECjbb/Stancu transaction batches | General data-processing phase locality, not streaming, but close to prior region/GC evidence. | Continue SPECjbb2005-workload port scaling and heap caps as Stancu-style evidence. |
| 7 | ReML allocation/list programs | Useful same-axes region+GC safety comparison; less stream-specific. | Add optional Tier 2 ports only after real-input pass or when very cheap. |

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
- Apache Flink low-latency and state-backend guidance:
  <https://flink.apache.org/2022/05/18/getting-into-low-latency-gears-with-apache-flink-part-one/>,
  <https://flink.apache.org/2021/01/18/using-rocksdb-state-backend-in-apache-flink-when-and-how/>
- Apache Flink object-reuse documentation:
  <https://nightlies.apache.org/flink/flink-docs-release-1.15/docs/dev/dataset/overview/>
- Kafka Streams memory management:
  <https://kafka.apache.org/28/streams/developer-guide/memory-mgmt/>
- Example practitioner GC-overhead reports:
  <https://stackoverflow.com/questions/27462061/why-does-spark-fail-with-java-lang-outofmemoryerror-gc-overhead-limit-exceeded>,
  <https://stackoverflow.com/questions/52069879/pyspark-java-lang-outofmemoryerror-gc-overhead-limit-exceeded>,
  <https://stackoverflow.com/questions/77677416/high-latency-in-flinks-keyby-operation>
