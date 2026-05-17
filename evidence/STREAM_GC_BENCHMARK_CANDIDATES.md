# Stream GC Benchmark Candidates

Date: 2026-05-01
Last updated: 2026-05-16 18:39 CEST

Status: benchmark-selection note for Phase 6. This is not a result pack.

Related investigation:
`evidence/GC_HEAVY_BENCHMARK_INVESTIGATION.md` records the 2026-05-15
literature/online follow-up on why many real streaming rows are not GC-heavy,
where prior systems and practitioners see GC pressure, and which retained
object workloads should be tried next.

2026-05-16 second-pass update: after the Broom active-16 scaling and LogHub
retained-session triage, the search direction is sharper. Keep simple
parse/filter/count streams as controls. The next GC-heavy stream candidates
must retain ordinary objects in keyed/window/session state or expose
latency/tail pressure. HiBench, BigDataBench, and Renaissance are useful
catalogues for standard workload names, but they should not replace local
single-process Rift kernels unless their framework overhead is itself the
research question.

## Decision

Rift should not use DaCapo, Renaissance, or SPECjbb2015 as primary
performance evidence. They can be useful background for "managed runtimes can
be GC-heavy," but their lifetimes are not naturally stream/dataflow shaped:
framework caches, global indexes, thread pools, long-lived graphs, and
cross-request state make region topology annotations intrusive and likely weak.

The primary search space is GC-heavy stream processing:

- many ordinary event/data objects;
- clear page, batch, window, epoch, transaction, or operator close boundary;
- durable control state separated into heap or primitive metadata;
- heap and Rift versions share the same logical program;
- region modes change only allocation placement and lifetime policy.

SPECjbb remains visible only as the Stancu/SPECjbb2005 literature anchor.
Do not start a Scala Native port of SPECjbb2015 unless a separate question
requires it and licensing/provenance are explicit.

## Sources Checked In This Pass

| Source | What it contributes | Rift relevance |
|---|---|---|
| Apache Beam NEXMark | Deterministic synthetic auction streams and many query shapes over `Person`/`Auction`/`Bid`. | Already active as generated-profile evidence; Q3/Q8 remain the best checked profile rows. |
| Yahoo Streaming Benchmark | Synthetic ad-event pipeline: JSON parse, filter/project, ad-to-campaign join, 10-second campaign windows, Redis sink in the original system. | Current local version is a useful GC-pressure control; not a 1M case-study win. |
| RIoTBench | IoT tasks/applications coupled to real smart-city/fitness style observation streams. | Current local generated probe is useful, but the next provenance step should use real RIoTBench-style input. |
| DSPBench | 15 DSPS applications from Finance, Telecommunications, Sensor Networks, Social Networks, and other domains, with workload characterization including memory occupation. | Best new candidate family because it offers varied stream topologies without being only one relational query. |
| Theodolite | Four Industrial IoT stream-processing benchmarks with load generators and implementations for Kafka Streams, Flink, Hazelcast Jet, and Beam. | Good methodology source, but distributed/Kubernetes services can hide allocator effects; port local kernels first. |
| HiBench Streaming | Spark/Flink/Storm/Gearpump streaming workloads: identity, repartition, stateful wordcount, fixed window. | Easy controls, but too small/simple for a primary Rift case study. |
| BigDataBench | Broad big-data/AI suite with streaming among several workload types and real-world datasets. | Useful workload catalogue; likely too broad/heavy for the immediate next implementation. |
| ShuffleBench / SH-Bench | Large-scale stream shuffling/routing to state-local aggregations, inspired by observability workloads. | Interesting if we want routing/shuffle object pressure; less directly region-lifetime-friendly than append/window ETL. |
| RiverBench RDF streaming | Real-life RDF stream datasets and streaming tasks including serialization/deserialization throughput. | Potentially object-heavy parser/record workload, but RDF/network serialization may dominate memory-management effects. |
| LogHub / LogPAI logs | Real HDFS/BGL/Spark/Thunderbird-style system logs with multi-million-line datasets. | Implemented first as `LogHubRegionMatrix` over real BGL; useful modest real-input row, but not yet the missing GC-heavy flagship. |
| DaCapo / Renaissance / SPECjbb2015 | General JVM/managed-runtime benchmark context. | Deprioritized for primary Rift evidence because lifetimes are not stream-structured. |

Sources:

- Apache Beam NEXMark: https://beam.apache.org/documentation/sdks/java/testing/nexmark/
- Yahoo Streaming Benchmark writeup: https://www.tumblr.com/yahooeng/135321837876/benchmarking-streaming-computation-engines-at
- RIoTBench paper/resource: https://www.canr.msu.edu/resources/Riotbench-an-iot-benchmark-for-distributed-stream-processing-systems
- DSPBench paper/resource: https://arpi.unipi.it/handle/11568/1066388
- DSPBench Zenodo record: https://zenodo.org/record/4671407
- Theodolite benchmarks: https://www.theodolite.rocks/theodolite-benchmarks/
- HiBench repository: https://github.com/Intel-bigdata/HiBench
- BigDataBench: https://www.benchcouncil.org/BigDataBench/index.html
- ShuffleBench replication package: https://zenodo.org/records/10667717/latest
- RiverBench: https://riverbench.github.io/v/latest/
- LogHub: https://github.com/logpai/loghub
- LogHub dataset table: https://github.com/logpai/loghub/blob/master/docs/datasets.md
- Spark tuning guide: https://spark.apache.org/docs/latest/tuning.html
- Flink state backend documentation:
  https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/state_backends/
- Broom HotOS paper:
  https://www.usenix.org/system/files/conference/hotos15/hotos15-paper-gog.pdf
- Yak OSDI page: https://www.usenix.org/conference/osdi16/technical-sessions/presentation/nguyen
- SPECjbb2005: https://www.spec.org/jbb2005/
- SNAP Twitter-2010: https://snap.stanford.edu/data/twitter-2010.html
- Alibaba Cluster Trace: https://github.com/alibaba/clusterdata
- TPC-H current specification:
  https://www.tpc.org/tpc_documents_current_versions/current_specifications5.asp

## Candidate Ranking

| Rank | Candidate | Why it fits Rift | First action |
|---:|---|---|---|
| 1 | StreamFlex retained event-correlation / transaction-tracking / IDS | Closest stream-processing predecessor: stable state plus transient scoped objects, and the important axes are throughput, p95/p99/max latency, deadline misses, RSS, and GC pauses. | Extend `StreamFlexDesignMatrix` with retained event/session/capsule objects; keep BeamFormer/FilterBank as primitive controls. |
| 2 | Broom/Naiad-style retained stream/dataflow join | The strongest GC-heavy signal so far comes from retained timestamp dictionaries; a TPC-H-Q17/shopper-like stream/dataflow shape is the most prior-work-aligned extension. | Add Q17-like retained join/aggregate and shopper JOIN-SELECT-JOIN rows; report natural heap/GC versus checked Rift first. |
| 3 | Real StackExchange/StackOverflow text stream | AskUbuntu already gives true streaming RSS/fixed-memory evidence; larger text can increase retained token/top-k state. | Fetch or stage a larger provenance-clean Posts dump if disk/network allow; run direct epoch and reusable top-k rows. |
| 4 | SNAP/Twitter graph edge stream | LiveJournal is the current real-input flagship and exactly matches epochal graph updates. | Preflight disk/time for larger SNAP/Twitter; stream edges through `RiftRegion.epoch`. |
| 5 | Higher-cardinality LogHub retained sessions/templates | HDFS/Spark/Windows top-k rows show RSS wins, but parser/hash CPU dominates; a useful next row must retain more objects. | Build session/template dictionaries or windowed joins that retain per-key objects, not just line counters. |
| 6 | DSPBench next retained kernels | Fraud/Log q2 are modest; Machine Outlier could work only with larger real traces. | Pin a larger Alibaba-style machine-usage trace before implementing Machine Outlier; otherwise pause DSPBench. |
| 7 | Theodolite retained power windows | Industrial monitoring is a good stream-latency story, but current q2 is not GC-heavy. | Add retained measurement/window contribution objects only if the semantics require them; report latency/tails. |
| 8 | HiBench / BigDataBench streaming catalogues | Standard workload names and generated/real data catalogues; useful for evaluation breadth. | Port retained SQL join/aggregate, stateful wordcount/top-k, or PageRank kernels locally; avoid opaque Spark/Flink runtime overhead. |
| 9 | NEXMark Beam-default expansion | Generated auction streams have explicit event/window lifetimes and are useful stress/regression controls. | Keep Q3/Q8/Q9/Q11 as generated methodology evidence; do not claim real-input proof. |
| 10 | DaCapo / Renaissance / SPECjbb2015 | Useful managed-runtime/GC background, but not stream-topology-first. | Keep Renaissance as optional general comparison and SPECjbb only through the Stancu/SPECjbb2005-style port. |

## Gates

A candidate becomes a serious Rift case study only if:

- heap shows material memory pressure by median/max GC time or allocation
  attribution;
- Rift beats heap and improved SafeZone by about `>=10%`, or materially reduces
  GC/RSS with `<=5%` elapsed overhead;
- the heap and Rift programs remain logically aligned;
- checked mode is added only after the relevant checked operator passes a
  focused gate.

## Immediate Use

Treat Wikimedia real pageviews/clickstream, Common Crawl real WET/WAT, official
Linear Road input, GH Archive byte-slice rows, and LogHub BGL as
ceiling/modest-win controls unless a future operator changes their allocation
shape. Keep NEXMark Q3/Q8, Yahoo Q2, and RIoTBench q1 as stream-GC
profile/regression controls, but make checked operator overhead reduction and
DSPBench / real RIoTBench triage the next engineering focus. The next
benchmark-search action should be checked Fraud q2 profiling or real
RIoTBench/Theodolite, not another generic JVM suite.

## LogHub BGL Update

`LogHubRegionMatrix` now runs against the real BGL log:
`/Users/siyaoliu/rift/cache/benchmark-data/loghub/BGL/BGL.log`
(`4747963` lines, `743185031` bytes).

The first 100k/1M medians and a full-file q2 scale probe show that LogHub BGL
is a real-input modest-win/control benchmark, not the missing GC-heavy flagship:

- at 1M q1/q2, heap GC is `99.271 ms` / `157.198 ms` inside roughly `5.6 s`;
- region rows remove timed GC and modestly improve selected rows;
- at full-file q2, heap spends `595.599 ms` in GC inside `32161.391 ms`;
- checked scoped page-token full-file q2 is faster and lower-RSS than heap,
  but the GC share is still under 2% of elapsed.

This is enough to keep real log streams in the benchmark ladder, but not enough
to stop searching for a stronger real GC-heavy data-stream workload.
