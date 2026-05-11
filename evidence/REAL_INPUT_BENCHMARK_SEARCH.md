# Real-Input GC-Heavy Stream Benchmark Search

Date: 2026-05-07
Last updated: 2026-05-11 11:59 CEST

Status: active Phase 6 search ledger. This file tracks public real-input
stream/dataflow candidates before implementation work. It is deliberately a
triage document: generated stressors such as Common Crawl WET-shaped q1/q2
remain useful memory-pressure detectors, but they are not real-data proof.

## Goal

Find a public, reproducible stream/dataflow workload where ordinary
intermediate Scala objects are naturally materialized, share a page, batch,
window, session, transaction, or epoch lifetime, and make `gc-heap` spend
material time or memory on garbage collection.

Current real-input rows are useful but not decisive. Yak LiveJournal is the
strongest real-input epoch row. LogHub HDFS top templates is now the strongest
real-input retained top-k row: the reusable checked `EpochTopKByKey` row at
5M HDFS lines x5 is `18.26 s` versus retained heap `19.04 s`, while max RSS
drops from about `504 MB` to `92 MB`. GH Archive byte-slice, LogHub BGL/HDFS
line-token-window rows, DSPBench Fraud/Log, and RIoTBench/MHEALTH are modest
throughput/RSS/tail wins or near-ties. Parser/query CPU often dominates and
heap GC remains under a few percent of elapsed at the measured scale, so the
next benchmark must force more natural object materialization, not just read
more bytes.

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
| 1 | Yak-style real graph replay | SNAP Twitter ego graph at `cache/benchmark-data/yak/snap/twitter_combined.txt.gz`; SNAP LiveJournal graph at `cache/benchmark-data/yak/snap/soc-LiveJournal1.txt.gz`; future larger candidate is SNAP Twitter-2010. | `graphreal`: preload real edge pairs into primitive control arrays, replay source/destination pairs as epoch-local `EdgeUpdate` objects, and update durable vertex state. | `EdgeUpdate` objects from real graph edges. | Epoch boundary; durable vertex array remains heap/primitive. | Implemented in `YakRegionMatrix`; Twitter ego smoke/1M/2M and LiveJournal 5M/10M/50M medians completed, including checked page-token, checked epoch topology, and reusable `EpochBuffer` rows. `RiftRegion.epoch { ... }` now exposes direct checked epoch topology; it has a 2-epoch smoke, a 10M API-backed rerun, and an apples-to-apples 50M API-backed rerun with the same 10 x 5M topology as the earlier topology table. | Current top real-input Yak-shaped row. LiveJournal 50M topology follow-up has `gc-heap` `1618.105 ms`, median GC `273.410 ms`, RSS `2.76 GB`; low-RSS epoch rows are `checked-epoch-scoped` `1069.241 ms`, `checked-epoch-stream` `1113.261 ms`, `region-scoped-rooted` `1256.538 ms`, and `region-stream-rootless` `1345.479 ms`, with region RSS about `1.53 GB`. Whole-run checked scoped is faster (`1048.751 ms`) but high-RSS (`2.98 GB`). Reusable `EpochBuffer` scoped also beats heap (`1343.071 ms` vs same-rerun heap `1514.313 ms`) but is not yet the fastest checked epoch lowering. The API-backed 10M row confirms direct checked epoch (`212.691/229.532 ms` scoped/stream) stays ahead of heap (`317.779 ms`) and `EpochBuffer` (`285.605/287.201 ms`); the apples-to-apples 50M API-backed row has `checked-epoch-scoped` `1055.958 ms`, `checked-epoch-stream` `1101.001 ms`, and heap `1604.811 ms` with `288.801 ms` GC. This is still not exact Yak/GraphChi artifact evidence, but it is a strong real graph ladder row and shows that checked epoch topology is the right safe shape. |
| 2 | DSPBench Spike Detection | DSPBench paper/source; local clone at `cache/benchmark-data/dspbench/source`, commit `00c20da828faf2b960fdb697c61d34cb25461875`; bundled `dspbench-threads/data/sensors.dat` has `79999` usable lines after filtering. | `q0-parse` sensor readings; `q1-moving-average` emits moving-average records; `q2-spike-window` groups spike alerts by time/device. | `SensorReading`, `MovingAverageRecord`, `SpikeCandidate`, optional per-device window contribution objects. The original threads implementation uses parser `Values`, tuples, and per-device `LinkedList[Double]` state. | Sensor-event bucket and moving-average window; durable per-device sums/windows stay heap/primitive. | Implemented as `DSPBenchRegionMatrix`; 20k smoke, 100k medians, and 1M medians completed. | Park as real-input modest/control evidence. At 1M, heap GC is real but only `10.880-32.793 ms`; best throughput wins are modest and checked q2 loses slightly. Move to Fraud Detection next. |
| 3 | DSPBench Fraud Detection | Same DSPBench clone; bundled `dspbench-threads/data/credit-card.dat` has `185000` lines plus Markov model resources. | `fraud-q0-parse` transaction records; `fraud-q1-predict` creates prediction/state records; `fraud-q2-alert-window` windows outlier alerts. | `Transaction`, `Prediction`, state-token list/string pieces, alert records. | Transaction/alert bucket; Markov model remains durable heap metadata. | Implemented as `DSPBenchRegionMatrix`; 20k smoke, 100k medians, 1M medians, q2 heap-cap follow-up, dirty fast-path row, and committed-code safe-fast-path rerun completed. | Keep as the best DSPBench real-input regression row. The dirty fast-path row made checked scoped page-token fastest (`818.574 ms` vs heap `862.834 ms`), but the committed-code rerun is more conservative: trusted Streaming `788.040 ms`, checked scoped page-token `810.770 ms`, heap `820.945 ms`, with checked RSS about `279 MB` vs heap `358 MB`. Heap caps did not create a fixed-memory checked win at 1M. |
| 4 | DSPBench Log Processing | Same DSPBench clone; bundled Spark `logprocessing/http-server.log` has `55000` common-log lines. | `log-q0-parse`, `log-q1-status`, and `log-q2-window`. | HTTP log records, status/update records, and window contribution records. | Event/window bucket; durable status counters on heap/primitive arrays. | Implemented as `DSPBenchRegionMatrix`; 20k smoke, 100k medians, and 1M medians completed. | Keep q2 as a modest real-input throughput/GC-tail control. At 1M, checked scoped page-token is fastest (`1733.654 ms` vs heap `1750.291 ms`) and cuts heap max GC from `88.210 ms` to `18.584 ms`, but heap GC is only about `2.6%` of elapsed and region RSS is higher. |
| 5 | DSPBench Machine Outlier | Same DSPBench clone; bundled `machine-usage.csv` is only `1012` lines. | Machine usage anomaly scoring and alert windows. | Observation/profile/score/alert records. | Observation/window bucket; anomaly model on heap. | Source inspected; sample input is tiny. | Defer unless a larger public Alibaba machine-usage trace is pinned. |
| 6 | DSPBench Bargain Index | Same DSPBench clone; bundled `stocks.csv` has `411` lines. | Parse quotes/trades, compute VWAP, join quotes with trade summaries, emit bargain records. | `Quote`, `Trade`, `VwapRecord`, `TradeSummary`, `BargainCandidate`. | Quote/trade window or day/interval boundary; summary table durable. | Source inspected; sample input is too small for headline real-input rows. | Do not implement first unless a larger public quote/trade stream is found. |
| 7 | Real RIoTBench-style input | RIoTBench source clone at `cache/benchmark-data/riot-bench/source`, commit `c86414f7f926ed5ae0fab756bb3d82fbfb6e5bf7`; bundled SenML samples are tiny, so UCI MHEALTH (`1215745` rows) is used as the FIT-style real sensor source. | Parse sensor/health records, clean/filter, annotate, sliding-window statistics, anomaly output. | Sensor reading, cleaned reading, annotation, statistic contribution, anomaly records. | Sensor/window/session bucket; device metadata durable. | `RiotBenchRegionMatrix` now accepts `RIOTBENCH_INPUT_KIND=mhealth` and directory input; 20k smoke and 1M q1/q2 medians completed. | Park as provenance-clean real-input ceiling/control. MHEALTH q1/q2 have zero timed heap GC at 1M; q1 is near-tie with heap fastest, q2 gives a small SafeZone win. |
| 8 | Richer LogHub template/session mining | LogHub BGL and HDFS v1 are local and measured. BGL has `4747963` lines; HDFS v1 has `11175629` lines from Zenodo v7. LogHub Spark is now local from Zenodo record `8196385`, with `3852` `.log` files and `33236604` total lines. LogHub Windows is also local from the same Zenodo record, with one `Windows.log` file, `114608388` lines, and `28012696901` bytes. | Parse log events, tokenize templates, infer block/session candidates, window template counts, and retained top-template summaries. | `LogEvent`, `TemplateToken`, `TemplateCandidate`, `SessionEvent`, `WindowSummary`, retained top-k/template candidates. | Log-line/template/session/window/epoch bucket; template dictionary and block index durable. | Implemented as `LogHubRegionMatrix` q1/q2/q3 and `LogHubTopTemplatesMatrix`; 20k smoke, 1M medians, HDFS q2 L1, HDFS top templates 1M x20 L1, HDFS top templates 5M x5 L1/L2, Spark top-template 20k/1M/5M rows, and Windows top-template 20k/1M/5M rows completed. | Keep as real-input modest throughput/RSS/tail evidence and the strongest current real retained top-k row. HDFS q2 remains a checked page/window RSS win with elapsed tie. HDFS top templates is better: reusable checked `EpochTopKByKey` at 5M lines x5 is `18.26 s`, RSS `92 MB`, versus retained heap `19.04 s`, RSS `504 MB`; L2 also removes heap's `62.421 ms` timed GC. Spark and Windows top templates confirm the same retained top-k shape can remove more timed GC (`128.140 ms` Spark and `122.440 ms` Windows median at 5M), but L1 is only a modest elapsed win and RSS is tied/slightly worse at 5M. Still not flagship GC-heavy because file loading/query CPU remains a large share of process time. |
| 9 | Theodolite UC2 / UC4 local kernel | Theodolite source clone at `cache/benchmark-data/theodolite/source`, commit `dfa768a25eec3c3f5a57b7d4839a0c255fd6fa7d`. The docs describe official generated active-power load generators, not a static real input file. | Local single-process downsampling or hierarchical aggregation without Kafka/Kubernetes. | Measurement records, hierarchy updates, duplicated group contributions, aggregate outputs. | Window/group bucket; hierarchy table durable. | Source cloned and inspected. UC2/UC4 are good methodology shapes, but the bundled input path is generated smart-meter active-power records. | Do not spend the next real-input slot on Theodolite alone unless paired with a separate public real industrial-energy trace. Candidate real sources include SPARK/SPARK-Raw or another open industrial power-meter dataset. |
| 10 | GDELT / security NDJSON logs | Public event/log streams; exact dataset not selected. | Byte-slice parse/project, enrichment, session/window counts, alert candidates. | Event records, field slices, enrichment records, alert/session/window contributions. | Line/session/window bucket; enrichment dictionary durable. | Not selected or downloaded. | Lower-priority public-log fallback after DSPBench/RIoTBench/LogHub. |

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
| `dspbench-spark/data/logprocessing/http-server.log` | `55000` | Implemented Log Processing source; common-log records with parse/status/window query tiers. |
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
| `log-q0-parse` | Allocate one common-log record per real line. | Allocate log records in page/event buckets. |
| `log-q1-status` | Allocate log and status/update records; update durable status counters. | Allocate stream records in buckets; durable status counters remain heap/primitive. |
| `log-q2-window` | Allocate log, status/update, and window contribution records, then summarize per status/window. | Allocate contributions in window buckets and close in bulk. |

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

## Log Processing Result

The 20k smoke matched checksums/output counts across heap, improved SafeZone,
trusted Streaming, and checked scoped page-token. The 1M run replays the
`55000` real common-log rows `19` times.

| Query | Best region row | Heap row | Interpretation |
|---|---:|---:|---|
| `log-q0-parse` | trusted Streaming `1443.724 ms`, GC `6.251 ms`, RSS `152928256` | heap `1462.188 ms`, GC `23.052 ms`, RSS `147193856` | modest trusted throughput/GC win; checked scoped is tied with heap and q0 is parser/replay dominated. |
| `log-q1-status` | improved SafeZone `1645.205 ms`, GC `12.930 ms`, RSS `217694208`; trusted Streaming `1647.471 ms` | heap `1669.816 ms`, GC `40.058 ms`, RSS `206503936` | modest safe/trusted throughput/GC win; checked scoped is faster than heap but slower than safe/trusted. |
| `log-q2-window` | checked scoped page-token `1733.654 ms`, GC `18.402 ms`, RSS `322027520` | heap `1750.291 ms`, GC `44.992 ms`, RSS `307773440` | best log row: checked scoped page-token is fastest and cuts max GC from `88.210 ms` to `18.584 ms`, but region RSS is higher and heap GC remains only about `2.6%` of elapsed. |

Decision: keep DSPBench Log q2 as a modest real-input throughput/GC-tail row
and a page-token regression target. It does not become the flagship GC-heavy
case because parser/query CPU dominates and the RSS tradeoff is unfavorable.
The next real-input search should target richer object materialization:
RIoTBench/Theodolite-style IoT records, richer LogHub template/session mining,
or a larger provenance-clean machine/outlier trace.

## LogHub Template/Session Result

`LogHubRegionMatrix` now includes `q3-template-session`, a richer real BGL query
that parses message suffixes into template buckets, derives session buckets
from node/template fields, allocates template-token and session-candidate
records, and counts sessions by window. The 20k smoke matched checksums/output
counts. At 1M real BGL lines:

| Mode | Elapsed ms | GC median ms | GC max ms | RSS bytes | Output |
|---|---:|---:|---:|---:|---:|
| heap-immix | `8683.558` | `84.166` | `117.946` | `290242560` | `243309` |
| safezone-improved-32k | `8635.167` | `34.787` | `38.138` | `236945408` | `243309` |
| rift-trusted-streaming | `8615.627` | `21.841` | `22.533` | `236814336` | `243309` |
| rift-checked-safezone-page-token | `8722.008` | `34.865` | `35.456` | `236961792` | `243309` |

Decision: park q3 as richer real-input modest/control evidence. It does
materialize more ordinary objects than q1/q2 and cuts RSS by roughly `53 MB`,
but heap GC is still less than 1% of elapsed. The row is useful for proving the
template/session shape works with checked page-token, not for the flagship
GC-heavy claim.

## LogHub HDFS v1 Result

HDFS v1 was added after BGL q3 and MHEALTH to test a larger real machine-log
input without writing another matrix. The data came from LogHub / LogPAI's
Zenodo v7 record:

`/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1/HDFS.log`

The extracted log has `11175629` lines and `1576383671` bytes. The 20k smoke
matched checksums/output counts for q1/q2/q3 across heap, improved SafeZone,
trusted Streaming, and checked scoped page-token. The 1M medians were:

| Query | Best region row | Heap row | Interpretation |
|---|---:|---:|---|
| `q1-tokens` | safezone-improved-32k `7919.352 ms`; checked scoped page-token `7923.079 ms` | heap `8059.155 ms`, GC `139.906 ms`, RSS `408551424` | modest real-input throughput/RSS/GC win; checked scoped is close to best region row. |
| `q2-window-counts` | trusted Streaming `7871.713 ms`; checked scoped page-token `7871.856 ms` | heap `8227.369 ms`, GC `92.659 ms`, RSS `408666112` | best HDFS row: checked scoped page-token beats heap by about 4.3%, removes timed GC, and lowers RSS. |
| `q3-template-session` | safezone-improved-32k `8360.487 ms`; trusted Streaming `8439.205 ms` | heap `8460.928 ms`, GC `81.910 ms`, RSS `408666112` | RSS/GC-tail evidence, but checked scoped page-token loses elapsed at `8506.708 ms`. |

Decision: keep HDFS q2 as a real-input checked/modest-win regression row. It
is stronger than the MHEALTH ceiling result and comparable to the best LogHub
BGL rows, but it still does not satisfy the flagship GC-heavy gate because heap
GC is only about 1-2% of elapsed.

## LogHub HDFS Top Templates Result

The retained top-template path uses reusable checked `EpochTopKByKey` instead
of a benchmark-local manual count array. It is the current strongest real-input
LogHub row because heap and checked modes both retain ordinary per-line/template
objects to the epoch boundary, then close by dropping anchors.

| Row | Heap/control | Best checked row | Interpretation |
|---|---:|---:|---|
| HDFS 1M x20 L1 | retained heap `5.52 s`, RSS `205 MB` | checked scoped `EpochTopKByKey` `4.88 s`, RSS `28 MB` | reusable top-k API is `11.6%` faster than retained heap and cuts RSS by about `86%`; API overhead versus benchmark-local checked is about `1.7%`. |
| HDFS 5M x5 L1 | retained heap `19.04 s`, RSS `504 MB` | checked scoped `EpochTopKByKey` `18.26 s`, RSS `92 MB` | larger real-input scale-up is a modest `4.1%` throughput win and strong RSS win. |
| HDFS 5M L2 | retained heap `463.633 ms`, GC `62.421 ms` | checked scoped `EpochTopKByKey` `402.916 ms`, GC `0 ms` | standard-stats interpretation row shows timed GC removal and a `13.1%` same-run elapsed win. |

Decision: keep HDFS top templates as the real-input retained top-k regression
row. It is still not a huge-GC flagship, but it demonstrates the kind of
real-input retained-object/RSS win that should guide future top-k/session
operator work.

## LogHub Spark Top Templates Follow-Up

Spark was added as the next larger LogHub search candidate because the archive
contains many real Spark/YARN container logs rather than one monolithic HDFS
file:

`/Users/siyaoliu/rift/cache/benchmark-data/loghub/Spark`

Local provenance:

| Item | Value |
|---|---:|
| Archive bytes | `183474743` |
| Extracted size | about `2.7G` |
| `.log` files | `3852` |
| Total extracted log lines | `33236604` |
| Source | LogHub Spark archive from Zenodo record `8196385` |

First smoke and scale-up used the largest container logs through
`LogHubTopTemplatesMatrix`, not a benchmark-local parser. Checksums and output
counts matched across retained heap and checked scoped top-k rows.

| Row | Heap/control | Best checked row | Interpretation |
|---|---:|---:|---|
| Spark 20k smoke | retained heap `2.738 ms`, GC `0 ms` | checked scoped `EpochTopKByKey` `2.832 ms`, GC `0 ms` | Validates file-backed Spark parsing/checksum only; too small for evidence. |
| Spark 1M x3 L2/L1 | retained heap L2 `144.298 ms`, GC `25.418 ms`, max GC `43.002 ms`; L1 `3.43 s`, RSS `205242368` | checked scoped `EpochTopKByKey` L2 `113.791 ms`, GC `0 ms`; L1 `3.24 s`, RSS `151633920` | Promising retained top-k real-input row: L2 removes timed GC and L1 is about `5.5%` faster with lower RSS. |
| Spark 5M x3 L2/L1 | retained heap L2 `703.804 ms`, GC `128.140 ms`, max GC `144.367 ms`; L1 `16.93 s`, RSS `503988224` | checked scoped `EpochTopKByKey` L2 `579.440 ms`, GC `0 ms`; L1 `16.63 s`, RSS `509476864` | L2 work-loop win and timed-GC removal scale, but L1 process time is only `1.8%` faster and RSS is tied/slightly worse because input loading/preload dominates. |

Decision: keep Spark top templates as a useful real-input retained top-k
confirmation, not a new headline flagship. It strengthens the claim that the
reusable checked top-k API removes heap GC on retained log-template objects,
but the 5M L1 row shows the end-to-end process is still dominated by file
loading and query CPU. The next LogHub search should try a richer
session/template query over Spark, Windows, or Thunderbird only if it
materializes more objects than the current top-template path.

## LogHub Windows Top Templates Follow-Up

Windows was added after Spark because it is much larger and has a single
large real log file:

`/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows/Windows.log`

Local provenance:

| Item | Value |
|---|---:|
| Archive bytes | `1670098945` |
| Extracted log bytes | `28012696901` |
| Extracted log lines | `114608388` |
| Source | LogHub Windows archive from Zenodo record `8196385` |

The same `LogHubTopTemplatesMatrix` path was used. Checksums and output counts
matched across retained heap and checked scoped top-k rows.

| Row | Heap/control | Best checked row | Interpretation |
|---|---:|---:|---|
| Windows 20k smoke | retained heap `1.809 ms`, GC `0 ms`, L1 RSS `8536064` | checked scoped `EpochTopKByKey` `2.042 ms`, GC `0 ms`, L1 RSS `9306112` | Validates file-backed Windows parsing/checksum only; too small for evidence. |
| Windows 1M x3 L2/L1 | retained heap L2 `147.667 ms`, GC `39.420 ms`, max GC `45.591 ms`; L1 `6.33 s`, RSS `205176832` | checked scoped `EpochTopKByKey` L2 `108.569 ms`, GC `0 ms`; L1 `6.21 s`, RSS `152403968` | Retained top-k row with timed-GC removal and lower RSS, but L1 process elapsed improves only about `1.9%`. |
| Windows 5M x3 L2/L1 | retained heap L2 `679.123 ms`, GC `122.440 ms`, max GC `133.835 ms`; L1 `32.37 s`, RSS `503889920` | checked scoped `EpochTopKByKey` L2 `548.806 ms`, GC `0 ms`; L1 `31.28 s`, RSS `513048576` | L2 retained-object loop win and timed-GC removal scale, but file reading dominates L1 and RSS is tied/slightly worse. |

Decision: Windows confirms that the reusable checked top-k API removes heap GC
on retained real log-template objects at larger input scale, but it still does
not create the missing huge end-to-end real-input win. Use it as evidence that
the current LogHub top-template shape is memory-management-positive inside the
work loop while remaining file/parser dominated at process level.

## Theodolite Source Triage

The public Theodolite source has been cloned locally:

`/Users/siyaoliu/rift/cache/benchmark-data/theodolite/source`

Clone commit:

`dfa768a25eec3c3f5a57b7d4839a0c255fd6fa7d`

The repo contains UC2 downsampling and UC4 hierarchical aggregation
implementations plus load generators. The load generator simulates active-power
records with fields `identifier`, `timestamp`, and `valueInW`. This is a good
recognized stream methodology shape, but it is generated input, not the
missing real-data proof. The next useful Theodolite step is to pair UC2/UC4
logic with a real industrial-energy trace such as SPARK/SPARK-Raw or another
open power-meter dataset, rather than porting Theodolite's generated load
alone.

## RIoTBench / MHEALTH Result

RIoTBench is a good benchmark-family match because it defines IoT parse,
filter, aggregate/statistical, prediction, and I/O tasks. The source repo was
cloned into ignored cache at:

`/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/source`

Clone commit:

`c86414f7f926ed5ae0fab756bb3d82fbfb6e5bf7`

The bundled RIoTBench resource inputs are too small for headline evidence:
`SYS_sample_data_senml.csv` has `1000` lines, `TAXI_sample_data_senml.csv`
has `999`, and `FIT_sample_data_senml.csv` has `45`. The RIoTBench FIT
configuration references MHEALTH-style data, so the UCI MHEALTH dataset was
downloaded and wired as the real sensor input:

`/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/mhealth/MHEALTHDATASET`

It has `1215745` rows across ten subject logs. `RiotBenchRegionMatrix` now
loads that directory with `RIOTBENCH_INPUT_KIND=mhealth`.

First 1M medians:

| Query | Mode | Median ms | Median GC ms | Max GC ms | Runs with GC | RSS bytes | Outputs |
|---|---|---:|---:|---:|---:|---:|---:|
| q1-clean-annotate | heap | 117.977 | 0.000 | 0.000 | 0 | 7585677312 | 1273497 |
| q1-clean-annotate | safezone-improved | 121.024 | 0.000 | 0.000 | 0 | 11959386112 | 1273497 |
| q1-clean-annotate | rift-streaming | 119.077 | 0.000 | 0.000 | 0 | 10965843968 | 1273497 |
| q2-window-stats | heap | 109.589 | 0.000 | 0.000 | 0 | 10995482624 | 273497 |
| q2-window-stats | safezone-improved | 107.194 | 0.000 | 0.000 | 0 | 10964779008 | 273497 |
| q2-window-stats | rift-streaming | 110.760 | 0.000 | 0.000 | 0 | 11643322368 | 273497 |

Decision: MHEALTH is a good provenance correction for RIoTBench-style input,
but it is not GC-heavy under this local preloaded matrix. Keep it as a
ceiling/control row. A file-backed MHEALTH parser may reduce preloaded RSS,
but zero timed GC means it should not displace the search for a richer
object-materializing real stream.

## Sources

- DSPBench Zenodo/paper record: `https://zenodo.org/records/4671407`
- DSPBench source: `https://github.com/GMAP/DSPBench`
- Older Storm applications provenance and dataset mapping:
  `https://github.com/mayconbordin/storm-applications`
- RIoTBench resource:
  `https://www.canr.msu.edu/resources/Riotbench-an-iot-benchmark-for-distributed-stream-processing-systems`
- RIoTBench source:
  `https://github.com/dream-lab/riot-bench`
- UCI MHEALTH dataset:
  `https://archive.ics.uci.edu/dataset/319/mhealth+dataset`
- Theodolite benchmark overview:
  `https://www.theodolite.rocks/theodolite-benchmarks/`
- Theodolite UC2:
  `https://www.theodolite.rocks/theodolite-benchmarks/benchmark-uc2.html`
- Theodolite source:
  `https://github.com/cau-se/theodolite`
- LogHub Zenodo v7:
  `https://zenodo.org/records/3227177`
- LogHub Spark/Windows/Thunderbird Zenodo record:
  `https://zenodo.org/records/8196385`

## Next Action

Continue beyond the HDFS q2 modest win and HDFS top-template retained win. The
next best search path is:

1. Continue the retained top-k/session family on larger LogHub streams. Spark
   and Windows now have 20k/1M/5M top-template follow-ups; the next variants
   are Thunderbird or a richer Spark/Windows session-template query that
   materializes more objects than the current top-template path.
2. Add StackOverflow/text top-word only after fetching provenance-clean posts
   data. No StackOverflow/Posts data is currently present under
   `cache/benchmark-data`; `scripts/fetch-benchmark-data.sh` has a gated
   `RIFT_FETCH_STACKOVERFLOW_POSTS` path, but it has not been run locally.
3. Pair Theodolite UC2/UC4 logic with a real industrial-energy trace for
   downsampling or hierarchical aggregation, not Theodolite's generated load
   alone.
4. Keep DSPBench Fraud q2, DSPBench Log q2, LogHub BGL q3, LogHub HDFS q2,
   LogHub HDFS top templates, and RIoTBench/MHEALTH q1/q2 as regression rows
   for page-token, top-k, and real-input modest/RSS/tail or ceiling behavior.
