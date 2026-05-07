# Real-Input GC-Heavy Stream Benchmark Search

Date: 2026-05-07
Last updated: 2026-05-07 16:20 CEST

Status: active Phase 6 search ledger. This file tracks public real-input
stream/dataflow candidates before implementation work. It is deliberately a
triage document: generated stressors such as Common Crawl WET-shaped q1/q2
remain useful memory-pressure detectors, but they are not real-data proof.

## Goal

Find a public, reproducible stream/dataflow workload where ordinary
intermediate Scala objects are naturally materialized, share a page, batch,
window, session, transaction, or epoch lifetime, and make `gc-heap` spend
material time or memory on garbage collection.

Current real-input rows are useful but not decisive. GH Archive byte-slice and
LogHub BGL produce modest throughput/RSS/tail wins, but parser/query CPU
dominates and heap GC remains under a few percent of elapsed at the measured
scale. The next benchmark must force more natural object materialization, not
just read more bytes.

## Search Gates

| Gate | Required signal |
|---|---|
| Public provenance | Dataset or source is public, versioned or cited, and recorded in `evidence/BENCHMARK_DATA_SOURCES.md`. |
| Natural object pressure | The query naturally creates many records, tokens, features, alerts, partial matches, template pieces, sessions, or window contributions. |
| Structured lifetime | Most intermediate objects die at a page, window, session, epoch, operator, or transaction boundary. |
| Material heap pressure | Heap median GC is at least 5% of elapsed, max-GC tails affect latency, heap caps materially slow/fail, or heap RSS is much higher with no elapsed advantage. |
| Fair program shape | Heap and region rows share the logical query; only allocation placement/lifetime policy changes. |
| Region case-study gate | A safe/checked row beats `gc-heap` and `region-scoped-rooted` by about 10%, or materially cuts GC/RSS with no more than 5% elapsed overhead. |

If heap GC stays below 2-3% of elapsed after scaling, park the workload as a
modest/control row and move to the next candidate.

## Candidate Table

| Rank | Candidate | Source / provenance | Query shape to test | Expected object materialization | Lifetime boundary | Local status | Decision |
|---:|---|---|---|---|---|---|---|
| 1 | DSPBench Spike Detection | DSPBench paper/source; local clone at `cache/benchmark-data/dspbench/source`, commit `00c20da828faf2b960fdb697c61d34cb25461875`; bundled `dspbench-threads/data/sensors.dat` has `79999` usable lines after filtering. | `q0-parse` sensor readings; `q1-moving-average` emits moving-average records; `q2-spike-window` groups spike alerts by time/device. | `SensorReading`, `MovingAverageRecord`, `SpikeCandidate`, optional per-device window contribution objects. The original threads implementation uses parser `Values`, tuples, and per-device `LinkedList[Double]` state. | Sensor-event bucket and moving-average window; durable per-device sums/windows stay heap/primitive. | Implemented as `DSPBenchRegionMatrix`; 20k smoke, 100k medians, and 1M medians completed. | Park as real-input modest/control evidence. At 1M, heap GC is real but only `10.880-32.793 ms`; best throughput wins are modest and checked q2 loses slightly. Move to Fraud Detection next. |
| 2 | DSPBench Fraud Detection | Same DSPBench clone; bundled `dspbench-threads/data/credit-card.dat` has `185000` lines plus Markov model resources. | `fraud-q0-parse` transaction records; `fraud-q1-predict` creates prediction/state records; `fraud-q2-alert-window` windows outlier alerts. | `Transaction`, `Prediction`, state-token list/string pieces, alert records. | Transaction/alert bucket; Markov model remains durable heap metadata. | Implemented as `DSPBenchRegionMatrix`; 20k smoke, 100k medians, 1M medians, q2 heap-cap follow-up, dirty fast-path row, and committed-code safe-fast-path rerun completed. | Keep as the best DSPBench real-input regression row. The dirty fast-path row made checked scoped page-token fastest (`818.574 ms` vs heap `862.834 ms`), but the committed-code rerun is more conservative: trusted Streaming `788.040 ms`, checked scoped page-token `810.770 ms`, heap `820.945 ms`, with checked RSS about `279 MB` vs heap `358 MB`. Heap caps did not create a fixed-memory checked win at 1M. |
| 3 | DSPBench Machine Outlier / Log Processing | Same DSPBench clone; bundled `machine-usage.csv` is only `35 KB`, `http-server.log` has `55000` lines. | Machine usage anomaly or common-log status/volume windows. | Observation/profile/score/alert or HTTP log/token/status records. | Observation or minute/window bucket; durable anomaly model/status counters on heap. | Source located but not deeply triaged. | Backup DSPBench target if Spike/Fraud are not GC-heavy. |
| 4 | DSPBench Bargain Index | Same DSPBench clone; bundled `stocks.csv` has `411` lines. | Parse quotes/trades, compute VWAP, join quotes with trade summaries, emit bargain records. | `Quote`, `Trade`, `VwapRecord`, `TradeSummary`, `BargainCandidate`. | Quote/trade window or day/interval boundary; summary table durable. | Source inspected; sample input is too small for headline real-input rows. | Do not implement first unless a larger public quote/trade stream is found. |
| 5 | Real RIoTBench-style input | RIoTBench paper describes 27 IoT tasks and four real smart-city/health observation workloads with high-rate streams. | Parse sensor/health records, clean/filter, annotate, sliding-window statistics, anomaly output. | Sensor reading, cleaned reading, annotation, statistic contribution, anomaly records. | Sensor/window/session bucket; device metadata durable. | Source/provenance not yet pinned locally. | Second family after DSPBench; only proceed with provenance-clean input. |
| 6 | Richer LogHub template/session mining | LogHub BGL already local and measured; other LogHub datasets can be fetched. | Parse log events, tokenize templates, infer block/session candidates, window template counts. | `LogEvent`, `TemplateToken`, `TemplateCandidate`, `SessionEvent`, `WindowSummary`. | Log-line/template/session/window bucket; template dictionary and block index durable. | Current BGL line/token/window path implemented but not GC-heavy. | Worth a richer query only if it materializes more objects than the current token-count path. |
| 7 | Theodolite UC2 / UC4 local kernel | Theodolite has industrial IoT stream benchmarks and implementations for Kafka Streams, Flink, Hazelcast Jet, and Beam. UC2 is downsampling; UC4 is hierarchical aggregation. | Local single-process downsampling or hierarchical aggregation without Kafka/Kubernetes. | Measurement records, hierarchy updates, duplicated group contributions, aggregate outputs. | Window/group bucket; hierarchy table durable. | Source not cloned locally in this pass. | Later target if DSPBench/RIoTBench do not produce stronger pressure. Remove external systems from headline rows. |
| 8 | GDELT / security NDJSON logs | Public event/log streams; exact dataset not selected. | Byte-slice parse/project, enrichment, session/window counts, alert candidates. | Event records, field slices, enrichment records, alert/session/window contributions. | Line/session/window bucket; enrichment dictionary durable. | Not selected or downloaded. | Lower-priority public-log fallback after DSPBench/RIoTBench/LogHub. |

## DSPBench Triage Notes

The DSPBench project is the best immediate candidate family because it is a
published DSPS benchmark suite with 15 applications spanning finance,
telecommunications, sensor networks, social networks, and other domains, and
the paper reports workload characterization including memory occupation. The
public source is available at `https://github.com/GMAP/DSPBench`; the local
ignored clone is:

`/Users/siyaoliu/rift/cache/benchmark-data/dspbench/source`

Current local clone commit:

`00c20da828faf2b960fdb697c61d34cb25461875`

Relevant inspected paths:

- `dspbench-threads/src/main/java/org/dspbench/applications/spikedetection/*`
- `dspbench-threads/src/main/java/org/dspbench/applications/frauddetection/*`
- `dspbench-threads/src/main/java/org/dspbench/applications/bargainindex/*`
- `dspbench-threads/data/sensors.dat`
- `dspbench-threads/data/credit-card.dat`
- `dspbench-threads/data/stocks.csv`

Bundled local data counts from the cloned source:

| File | Lines | First-use interpretation |
|---|---:|---|
| `dspbench-threads/data/credit-card.dat` | `185000` | Best first Fraud Detection source; can be replayed with provenance labels. |
| `dspbench-threads/data/sensors.dat` | `80000` | Best first Spike Detection source; can be replayed with provenance labels. |
| `dspbench-threads/data/http-server.log` | `55000` | Possible log-processing backup. |
| `dspbench-threads/data/click-stream.json` | `37500` | Possible click/log backup, but current GH/LogHub already cover similar shapes. |
| `dspbench-threads/data/stocks.csv` | `411` | Too small for Bargain Index headline rows without a larger quote source. |

The first Scala Native DSPBench port should avoid the DSPBench thread engine
itself and implement local single-process kernels with the same logical
operator shapes. External Storm/Spark/Flink/Kafka runtime overhead would hide
the memory-management effect we are trying to measure.

## First Implementation Slice

`DSPBenchRegionMatrix` has now been implemented for the first Spike Detection
slice. Source: `evidence/DSPBENCH_REGION_MATRIX.md`.

Implemented first slice:

| Query | Heap shape | Region shape |
|---|---|---|
| `q0-spike-parse` | Allocate one `SensorReading` per real input line. | Allocate `SensorReading` in page/event buckets. |
| `q1-spike-moving-average` | Allocate `SensorReading` plus `MovingAverageRecord`; keep per-device window state as heap/primitive metadata. | Allocate stream records in page/window regions; durable per-device state remains heap. |
| `q2-spike-alert-window` | Allocate `SpikeCandidate`/alert records and summarize per window. | Allocate candidates/alerts in window buckets and close in bulk. |
| `q0-fraud-parse` | Allocate one `Transaction` per real line. | Allocate transactions in page/event buckets. |
| `q1-fraud-predict` | Allocate `Prediction` and state-token objects from the Markov predictor. | Allocate predictions/state-token records in region buckets; Markov model remains heap. |
| `q2-fraud-alert-window` | Allocate outlier alert/window records. | Allocate alerts in window buckets and close in bulk. |

Required first modes:

- `gc-heap`
- `region-scoped-rooted`
- `region-stream-rootless`
- `checked-region-scoped` with page-token only when the q1/q2 shape fits

Do not add a new checked operator unless the heap rows show material GC and the
existing page-token shape is insufficient.

## Spike Detection Result

The 20k smoke matched checksums/output counts. The 1M run replays the `79999`
usable real sensor rows `13` times.

| Query | Best region row | Heap row | Interpretation |
|---|---:|---:|---|
| `q0-parse` | checked scoped page-token `1058.429 ms`, GC `4.269 ms`, RSS `80461824` | heap `1068.850 ms`, GC `10.880 ms`, RSS `147030016` | tiny throughput win plus large RSS reduction; heap GC is about 1% of elapsed. |
| `q1-moving-average` | checked scoped page-token `1163.045 ms`, GC `8.174 ms`, RSS `156827648` | heap `1187.525 ms`, GC `21.421 ms`, RSS `147111936` | modest checked throughput win; RSS is slightly higher. |
| `q2-spike-window` | trusted Streaming `1258.164 ms`, GC `8.900 ms`, RSS `223117312`; checked scoped page-token `1277.947 ms` | heap `1271.677 ms`, GC `32.793 ms`, RSS `206438400` | trusted region row modestly wins; checked scoped page-token is slightly slower despite lower GC. |

Decision: do not tune Spike into a flagship case. It confirms the local
DSPBench harness and page/window lifetime placement, but parser/query/object
CPU dominates over collection time.

## Fraud Detection Result

The 20k smoke matched checksums/output counts. The 1M run replays the
`185000` real transaction rows `6` times.

| Query | Best region row | Heap row | Interpretation |
|---|---:|---:|---|
| `fraud-q0-parse` | improved SafeZone `431.301 ms`, GC `0.000 ms`, RSS `134709248` | heap `433.606 ms`, GC `9.997 ms`, RSS `129204224` | near tie; parse-only row is not GC-heavy. |
| `fraud-q1-predict` | trusted Streaming `658.144 ms`, GC `0.000 ms`, RSS `276725760` | heap `673.635 ms`, GC `43.801 ms`, RSS `254427136` | modest trusted throughput win; checked scoped page-token loses elapsed. |
| `fraud-q2-alert-window` | trusted Streaming `763.819 ms`, GC `12.492 ms`, RSS `282460160` | heap `801.790 ms`, GC `69.686 ms`, RSS `358252544` | first q2 matrix: modest trusted throughput/RSS/GC win. Checked scoped page-token cuts GC/RSS but loses elapsed at `822.846 ms`. |

Post-fast-path follow-up:

| Run | Best row | Heap row | Interpretation |
|---|---:|---:|---|
| Dirty page-token fast-path q2 | checked scoped page-token `818.574 ms`, GC `14.151 ms`, RSS about `279 MB` | heap `862.834 ms`, GC `74.513 ms`, RSS about `358 MB` | useful direction check, but the worktree was dirty and should not be used as a final headline row. |
| Committed-code safe-fast-path q2 | trusted Streaming `788.040 ms`, GC `11.547 ms`, RSS `282443776`; checked scoped page-token `810.770 ms`, GC `15.105 ms`, RSS `278593536` | heap `820.945 ms`, GC `75.928 ms`, RSS `358154240` | conservative checkpoint: checked scoped page-token is a modest throughput/RSS/GC win over heap but not fastest; trusted Streaming is fastest. |

Decision: keep Fraud q2 as a trusted-runtime modest win and checked-overhead
regression row. Heap-cap follow-up is complete: `512M`/`384M` caps are near
uncapped behavior, and `256M` raises the max GC tail to `101.267 ms` without
making checked scoped page-token a fixed-memory throughput win. The next action
is to profile checked scoped page-token q2 before trying another DSPBench
kernel.

## Sources

- DSPBench Zenodo/paper record: `https://zenodo.org/records/4671407`
- DSPBench source: `https://github.com/GMAP/DSPBench`
- Older Storm applications provenance and dataset mapping:
  `https://github.com/mayconbordin/storm-applications`
- RIoTBench resource:
  `https://www.canr.msu.edu/resources/Riotbench-an-iot-benchmark-for-distributed-stream-processing-systems`
- Theodolite benchmark overview:
  `https://www.theodolite.rocks/theodolite-benchmarks/`
- Theodolite UC2:
  `https://www.theodolite.rocks/theodolite-benchmarks/benchmark-uc2.html`

## Next Action

Profile `fraud-q2-alert-window` checked scoped page-token against heap,
SafeZone improved, and trusted Streaming. The profile should distinguish
allocation lowering, page-token append bookkeeping, alert/window traversal, and
summary/checksum work before adding another DSPBench kernel.
