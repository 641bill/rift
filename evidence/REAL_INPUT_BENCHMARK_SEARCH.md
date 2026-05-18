# Real-Input GC-Heavy Stream Benchmark Search

Date: 2026-05-07
Last updated: 2026-05-18 16:01 CEST

Status: active Phase 6 search ledger. This file tracks public real-input
stream/dataflow candidates before implementation work. It is deliberately a
triage document: generated stressors such as Common Crawl WET-shaped q1/q2
remain useful memory-pressure detectors, but they are not real-data proof.

The latest GC-heavy benchmark investigation is recorded separately in
`evidence/GC_HEAVY_BENCHMARK_INVESTIGATION.md`. Its key conclusion is that
streaming input is not enough: a real row needs retained ordinary objects
behind joins, sessions, windows, graph epochs, transaction batches, or
high-cardinality keyed state before heap GC becomes a material bottleneck.
The newest graph follow-up adds a true compressed-streaming SNAP LiveJournal
row: `YAK_GRAPH_INPUT_MODE=streaming-file` consumes `soc-LiveJournal1.txt.gz`
inside the timed path instead of preloading edge arrays. At 20M streamed edges,
checked scoped is L1 `17.15 s`, RSS `102 MB`, versus heap `18.32 s`, RSS
`577 MB`; checked stream is L2 `5530.190 ms` versus heap `6333.745 ms`. Heap
timed GC is `165.387 ms`, still only about `2.6%`, so this is strong
real-streaming graph RSS/fixed-memory and throughput evidence, not the
GC-time flagship. A one-run cap probe adds fixed-memory evidence: heap passes
at `128M` but fails at `64M`, while checked epoch rows complete under `64M`
and `32M` caps with matching checksums.
The newest retained-state row promotes the Wikimedia clickstream triage into a
named `wikimedia-clickstream-session` workload. It streams the compressed
enwiki clickstream TSV, derives session keys from source article, target
article, and link kind, and retains ordinary clickstream session events plus
per-key aggregate entries until epoch close. At 1M streamed rows, L1 checked
Rift is `5.81 s`, RSS `138 MB`, versus heap `6.50 s`, RSS `784 MB`; L2
checked Rift is `1952.438 ms`, GC `9.237 ms`, versus heap `2038.262 ms`, GC
`150.157 ms`. Heap fails even at `512M`, while checked rows complete under
`128M` and `64M`. This is now real-streaming retained clickstream
throughput/RSS/GC/fixed-memory evidence. A 5M scale-up keeps checked Rift
slightly faster in L1 (`27.86 s` versus heap `28.77 s`) and cuts RSS from
`1.54 GB` to `138 MB`; L2 loop throughput is essentially tied, but heap max GC
reaches `1066.487 ms` and heap fails at `1G`, `768M`, and `512M`, while
checked rows complete under a `64M` GC heap cap. Treat the 5M row as
RSS/fixed-memory and GC-tail scale evidence.
The 10M 3-run follow-up promotes the row from feasibility to report-grade
scale-up evidence: checked Rift is L1 `59.37 s`, RSS `138 MB`, versus heap
`62.52 s`, RSS `1.80 GB`; L2 checked Rift is `19635.995 ms`, GC `96.069 ms`,
versus heap `20103.863 ms`, GC `851.023 ms`. Heap fails at `1G`, `768M`,
and `512M`; checked rows complete under a `64M` GC heap cap.

## Goal

Find a public, reproducible stream/dataflow workload where ordinary
intermediate Scala objects are naturally materialized, share a page, batch,
window, session, transaction, or epoch lifetime, and make `gc-heap` spend
material time or memory on garbage collection.

Current real-input rows are useful but not decisive. Yak LiveJournal is the
strongest real-input epoch row. The new Stack Exchange AskUbuntu `topwordreal`
row is the strongest real text/top-word follow-up so far: at 20M real tokens,
L1 `checked-epoch-scoped` is `7.16 s` versus heap `7.77 s` and cuts RSS from
about `986 MB` to `174 MB`; the matching L2 row removes `33.471 ms` median
timed heap GC. The same AskUbuntu row now has a true streaming-file variant:
`YAK_TEXT_INPUT_MODE=streaming-file` scans `Posts.xml` during the benchmark and
does not preload all token keys/weights. At 1M tokens, checked epoch scoped is
median L1 `0.91 s`, RSS `13.0 MB`, versus heap `0.96 s`, RSS `39.6 MB`; L2 removes
only `3.677 ms` heap GC. The 5M compressed-streaming scale-up keeps the same
classification: checked epoch scoped is L1 `6.23 s`, RSS `15.0 MB`, versus
heap `6.74 s`, RSS `41.1 MB`; L2 heap GC is `27.237 ms` inside
`2109.524 ms`, about `1.3%`. Classify it as modest real-streaming-input
RSS/fixed-memory evidence rather than a GC-heavy flagship. LogHub HDFS top
templates remains the strongest real-input
retained top-k row: the reusable checked `EpochTopKByKey` row at 5M HDFS lines
x5 is `18.26 s` versus retained heap `19.04 s`, while max RSS drops from about
`504 MB` to `92 MB`. The same matrix now has the first true streaming-input
row: `LOGHUB_TOP_INPUT_MODE=streaming-file` consumes 1M HDFS log lines inside
each run without parsed total-input arrays; reusable checked scoped top-k is
L1 `8.06 s`, RSS `12 MB`, versus retained heap `8.10 s`, RSS `76 MB`, and L2
removes `32.681 ms` heap GC. GH Archive byte-slice, LogHub BGL/HDFS line-token-window
rows, DSPBench Fraud/Log, and RIoTBench/MHEALTH are modest throughput/RSS/tail
wins or near-ties. Parser/query CPU often dominates and heap GC remains under a
few percent of elapsed at the measured scale, so the next benchmark must force
more natural object materialization, not just read more bytes.
The next LogHub streaming follow-up used the much larger local Windows log:
`Windows.log` has `114,608,388` lines and the 1M streaming top-template row
matches elapsed (`12.64 s` checked top-k versus `12.68 s` heap) while cutting
L1 RSS from about `147 MB` to `14.5 MB`. Heap still completes under a `64M`
heap cap and heap GC is below `1%` of L2 time, so classify it as
real-streaming-input RSS/fixed-memory evidence, not GC-heavy proof.
GH Archive now has an explicit `GITHUB_ARCHIVE_INPUT_MODE=streaming-file`
row over the byte-slice gzip NDJSON reader. At 100k events, checked page-token
wins q1 (`9.62 s` vs heap `10.39 s`) and q2 (`9.16 s` vs heap `9.38 s`),
removing the observed heap max-GC tails (`71-72 ms`) with modest RSS savings;
median heap GC is still zero, so keep it as real-streaming-input
RSS/tail/modest-throughput evidence.
`LogHubRegionMatrix` now also has `LOGHUB_INPUT_MODE=streaming-file` for the
richer HDFS `q3-template-session` row. At 1M streamed HDFS lines, checked
scoped page-token cuts L1 RSS from about `862 MB` to `130 MB` and reduces L2
max GC from `131.533 ms` to `58.455 ms`, but it is slower in L1
(`30.29 s` versus heap `26.88 s`). Keep it as real-streaming-input
RSS/fixed-memory/control evidence and park q3 unless heap caps or a more
naturally retained session query exposes stronger pressure.
The first active-window heap-cap follow-up found pressure but not a clean win:
with `LOGHUB_LIVE_BUCKETS=16`, 1M HDFS q3 streaming lines, and a `256M` heap
cap, heap slows to `21.34 s` external and `1989.577 ms` timed GC over
`17` collections; at `128M` it fails. The checked scoped page-token row
completes with matching checksum/output and zero timed GC at `17.87 s`, but
RSS rises to about `694 MB`, so classify this as heap-cap/GC-pressure triage
rather than an RSS win. The next LogHub step should be a more naturally
retained session/join shape, not simply more active q3 page-token buckets.
That retained-session follow-up has now been tried in
`evidence/LOGHUB_RETAINED_SESSION_MATRIX.md`. It is a true HDFS
streaming-file retained session/join row, but still not GC-heavy enough:
session heap GC is `82.341 ms` inside `6595.172 ms`, and join heap GC is only
`9.474 ms` inside `6837.810 ms`. Park it as real-streaming retained-object
control evidence and keep searching for higher-cardinality retained state or
transaction/graph/text epochs.
The same retained-session harness was then tried on the much larger Windows
archive member (`tar.gz:/.../Windows.tar.gz!Windows.log`). The 20k smoke
matched checksums, but the join emitted zero matches, so the 1M follow-up
scaled only `session`. It remains parser/archive/hash dominated: heap is
`17059.969 ms` with `125.783 ms` median GC and `318 MB` RSS; checked Rift is
`17808.808 ms` with `14.753 ms` GC and `63 MB` RSS; checked scoped is an
external near-tie (`51.58 s` vs heap `51.90 s`) with `64 MB` RSS. Park Windows
retained session as RSS/control evidence, not the missing GC-heavy row.
The archive-wide Spark retained-session follow-up is stronger. The new
`tar.gzcat:/Users/siyaoliu/rift/cache/benchmark-data/loghub/Spark.tar.gz`
source streams all regular-file contents from the compressed archive in one
pass, avoiding the repeated per-member tar scans of the first `tar.gzdir`
attempt. At 1M active-16 session records, L1 heap is `27.62 s` and `391 MB`
RSS, checked Rift is `20.30 s` and `73 MB`, and checked scoped is `19.85 s`
and `73 MB`. The L2 row has heap `6642.276 ms` with `140.639 ms` median GC,
checked Rift `6396.869 ms` with `14.407 ms` GC and `1.121 ms` region op time,
and checked scoped `6615.206 ms`. Heap completes at `256M` but fails at
`128M`, while checked rows complete around `73 MB` RSS. Keep this as the
strongest LogHub retained-session real-streaming RSS/fixed-memory row so far;
it is still not a GC-time flagship because heap GC is only about `2.1%` of
the L2 loop.

The new Broom q17 retained join/aggregate row is useful for the search, but it
does not change the real-input ledger: it is deterministic generated
methodology evidence, not real-input proof. It shows that a TPC-H-Q17-like
retained dataflow shape can make Scala Native heap GC material (`1370.380 ms`
median timed GC inside `4781.079 ms` L2 at 20M active-16), and checked Rift
cuts L1 elapsed from `14.45 s` to `9.67 s` while reducing RSS from about
`232 MB` to `50 MB`. The real-input search should now look for public data
that naturally behaves like this: retained joins, high-cardinality sessions,
graph/text epochs, or transaction-local object batches. Do not treat q17 as a
real-data substitute. The DBGEN/TPC-H file-backed q17 mode is now implemented
and validated at SF0.1 and SF1. At SF1, checked Rift cuts RSS from about
`433 MB` to `49 MB`, improves L1 elapsed from `55.44 s` to `51.47 s`, lowers
L2 GC from `877.190 ms` to `503.444 ms`, and heap fails at a `128M` cap while
checked Rift completes around `49-53 MB`. It is still standardized generated
input rather than real-world input.

2026-05-16 18:39 second search pass: the next real-input search should be more
selective. Official/prior-work sources point to retained heap objects in
stateful joins, keyed/session dictionaries, graph/text epochs, transaction
batches, and heap-state windows as the GC-sensitive shape. Larger real log
files alone have repeatedly produced parser/hash-dominated rows. The current
ranked real-input actions are:

| Rank | Action | Why this is next |
|---:|---|---|
| 1 | Larger StackExchange/StackOverflow text epochs | AskUbuntu already gives an RSS/fixed-memory win; larger text should increase retained token/top-k state without inventing a new workload. |
| 2 | Larger SNAP/Twitter-style graph replay | LiveJournal is the strongest real graph row; SNAP Twitter-2010 is public and has the right shape, but its `1.468B` edges make it a disk/time-gated step. |
| 3 | Higher-cardinality LogHub session/template dictionaries | Existing LogHub rows are parser-heavy; a useful next row must retain per-session/per-key objects long enough to stress heap. |
| 4 | Alibaba-style machine/cluster trace for DSPBench Machine Outlier | DSPBench Machine Outlier is promising only if a larger real usage trace is pinned; Alibaba 2018 `machine_usage` is the plausible first slice, while the full trace is much larger. |
| 5 | Theodolite/UCI retained window contributions | Use only if the query retains ordinary measurement/window contribution objects; primitive-only downsampling remains control evidence. |

Do not spend another pass on simple parse/filter/count rows unless the row adds
retained objects, heap caps, or latency/tail evidence.

2026-05-11 local-data preflight: the cache currently has AskUbuntu for
StackExchange text, HDFS/BGL/Spark/Windows for LogHub, Twitter ego and
LiveJournal for SNAP/Yak graph replay, and no larger StackOverflow dump yet.
The existing AskUbuntu `topwordreal` row has now been scaled to 20M tokens.
Theodolite-style UC2/UC4 local rows have also been wired to the real UCI
Household Electric Power trace. The q2 hierarchical row removes timed heap GC
and ties end-to-end process time, but does not become a GC-heavy flagship. The
next text slot should fetch a larger provenance-clean StackOverflow or
StackExchange dump if network/disk allow; otherwise continue richer LogHub
session/template mining. Do not substitute generated text for this slot.

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
| 1 | Yak-style real graph replay | SNAP Twitter ego graph at `cache/benchmark-data/yak/snap/twitter_combined.txt.gz`; SNAP LiveJournal graph at `cache/benchmark-data/yak/snap/soc-LiveJournal1.txt.gz`; future larger candidate is SNAP Twitter-2010. | `graphreal`: preload real edge pairs into primitive control arrays or stream compressed edge lines with `YAK_GRAPH_INPUT_MODE=streaming-file`, replay source/destination pairs as epoch-local `EdgeUpdate` objects, and update durable vertex state. | `EdgeUpdate` objects from real graph edges. | Epoch boundary; durable vertex array remains heap/primitive. | Implemented in `YakRegionMatrix`; Twitter ego smoke/1M/2M and LiveJournal 5M/10M/50M preloaded medians completed, including checked page-token, checked epoch topology, and reusable `EpochBuffer` rows. `RiftRegion.epoch { ... }` now exposes direct checked epoch topology. The new streaming-file path has LiveJournal 20k, 1M, 5M, and 20M compressed-source rows. | Current top real-input Yak-shaped row. LiveJournal 50M preloaded topology follow-up has `gc-heap` `1618.105 ms`, median GC `273.410 ms`, RSS `2.76 GB`; low-RSS epoch rows are `checked-epoch-scoped` `1069.241 ms`, `checked-epoch-stream` `1113.261 ms`, `region-scoped-rooted` `1256.538 ms`, and `region-stream-rootless` `1345.479 ms`, with region RSS about `1.53 GB`. Whole-run checked scoped is faster (`1048.751 ms`) but high-RSS (`2.98 GB`). The true streaming-file 20M row consumes `soc-LiveJournal1.txt.gz` inside the timed path: L1 checked scoped is `17.15 s`, RSS `102 MB`, versus heap `18.32 s`, RSS `577 MB`; L2 checked stream is `5530.190 ms` versus heap `6333.745 ms`, but heap GC is only `165.387 ms` (`2.6%`). This is strong real-streaming graph RSS/fixed-memory and throughput evidence, not exact Yak/GraphChi artifact evidence. |
| 1a | Stack Exchange AskUbuntu top-word replay | Public Stack Exchange data dump from Internet Archive. Local archive `cache/benchmark-data/yak/stackexchange/askubuntu.com.7z`; extracted `Posts.xml` is `1400891844` bytes and `945113` lines. | `topwordreal`: tokenize real AskUbuntu post titles/bodies, replay tokens as epoch-local `WordRecord` objects, and compute per-epoch top word/count. Preloaded mode stores key/weight arrays first; `YAK_TEXT_INPUT_MODE=streaming-file` scans XML during the benchmark. | `WordRecord` objects from real text tokens. | Epoch boundary; durable counters remain heap/primitive control metadata. Streaming-file mode does not retain a full token replay array. | Implemented in `YakRegionMatrix`; preloaded 20k smoke, 1M L2, 10M L2/L1, and 20M L2/L1 rows completed. Streaming-file 20k smoke, 1M L1/L2, and 5M compressed-streaming L1/L2 rows completed. | Keep as real text/top-word evidence. Preloaded 20M remains stronger for scale: L1 `checked-epoch-scoped` `7.16 s`, RSS `174 MB`, versus heap `7.77 s`, RSS `986 MB`. Streaming-file 5M confirms true compressed replay from `askubuntu.com.7z`: checked epoch scoped L1 `6.23 s`, RSS `15.0 MB`, versus heap `6.74 s`, RSS `41.1 MB`, but heap GC is only `27.237 ms` inside `2109.524 ms`, so classify as modest RSS/fixed-memory stream evidence, not a GC-heavy flagship. Not exact Yak/Hadoop evidence. |
| 2 | DSPBench Spike Detection | DSPBench paper/source; pinned source ZIP at `cache/benchmark-data/dspbench/DSPBench-00c20da828faf2b960fdb697c61d34cb25461875.zip`; bundled `dspbench-threads/data/sensors.dat` has `79999` usable lines after filtering. | `q0-parse` sensor readings; `q1-moving-average` emits moving-average records; `q2-spike-window` groups spike alerts by time/device. | `SensorReading`, `MovingAverageRecord`, `SpikeCandidate`, optional per-device window contribution objects. The original threads implementation uses parser `Values`, tuples, and per-device `LinkedList[Double]` state. | Sensor-event bucket and moving-average window; durable per-device sums/windows stay heap/primitive. | Implemented as `DSPBenchRegionMatrix`; 20k smoke, 100k medians, and 1M medians completed. The runner now reads this file through a `zip:/archive!member` spec. | Park as real-input modest/control evidence. At 1M, heap GC is real but only `10.880-32.793 ms`; best throughput wins are modest and checked q2 loses slightly. Move to Fraud Detection next. |
| 3 | DSPBench Fraud Detection | Same DSPBench source ZIP; bundled `dspbench-threads/data/credit-card.dat` has `185000` lines plus Markov model resources. | `fraud-q0-parse` transaction records; `fraud-q1-predict` creates prediction/state records; `fraud-q2-alert-window` windows outlier alerts. | `Transaction`, `Prediction`, state-token list/string pieces, alert records. | Transaction/alert bucket; Markov model remains durable heap metadata. | Implemented as `DSPBenchRegionMatrix`; 20k smoke, 100k medians, 1M medians, q2 heap-cap follow-up, dirty fast-path row, and committed-code safe-fast-path rerun completed. The runner now reads this file through a `zip:/archive!member` spec. | Keep as the best DSPBench real-input regression row. The dirty fast-path row made checked scoped page-token fastest (`818.574 ms` vs heap `862.834 ms`), but the committed-code rerun is more conservative: trusted Streaming `788.040 ms`, checked scoped page-token `810.770 ms`, heap `820.945 ms`, with checked RSS about `279 MB` vs heap `358 MB`. Heap caps did not create a fixed-memory checked win at 1M. |
| 4 | DSPBench Log Processing | Same DSPBench source ZIP; bundled Spark `logprocessing/http-server.log` has `55000` common-log lines. | `log-q0-parse`, `log-q1-status`, and `log-q2-window`. | HTTP log records, status/update records, and window contribution records. | Event/window bucket; durable status counters on heap/primitive arrays. | Implemented as `DSPBenchRegionMatrix`; 20k smoke, 100k medians, and 1M medians completed. The runner now reads this file through a `zip:/archive!member` spec. | Keep q2 as a modest real-input throughput/GC-tail control. At 1M, checked scoped page-token is fastest (`1733.654 ms` vs heap `1750.291 ms`) and cuts heap max GC from `88.210 ms` to `18.584 ms`, but heap GC is only about `2.6%` of elapsed and region RSS is higher. |
| 5 | DSPBench Machine Outlier | Same DSPBench source ZIP; bundled `machine-usage.csv` is only `1012` lines. | Machine usage anomaly scoring and alert windows. | Observation/profile/score/alert records. | Observation/window bucket; anomaly model on heap. | Source inspected; sample input is tiny. | Defer unless a larger public Alibaba machine-usage trace is pinned. |
| 6 | DSPBench Bargain Index | Same DSPBench source ZIP; bundled `stocks.csv` has `411` lines. | Parse quotes/trades, compute VWAP, join quotes with trade summaries, emit bargain records. | `Quote`, `Trade`, `VwapRecord`, `TradeSummary`, `BargainCandidate`. | Quote/trade window or day/interval boundary; summary table durable. | Source inspected; sample input is too small for headline real-input rows. | Do not implement first unless a larger public quote/trade stream is found. |
| 7 | Real RIoTBench-style input | RIoTBench source clone at `cache/benchmark-data/riot-bench/source`, commit `c86414f7f926ed5ae0fab756bb3d82fbfb6e5bf7`; bundled SenML samples are tiny, so UCI MHEALTH (`1215745` rows) is used as the FIT-style real sensor source. | Parse sensor/health records, clean/filter, annotate, sliding-window statistics, anomaly output. | Sensor reading, cleaned reading, annotation, statistic contribution, anomaly records. | Sensor/window/session bucket; device metadata durable. | `RiotBenchRegionMatrix` now accepts `RIOTBENCH_INPUT_KIND=mhealth` and directory input; 20k smoke and 1M q1/q2 medians completed. | Park as provenance-clean real-input ceiling/control. MHEALTH q1/q2 have zero timed heap GC at 1M; q1 is near-tie with heap fastest, q2 gives a small SafeZone win. |
| 8 | Richer LogHub template/session mining | LogHub BGL and HDFS v1 are local and measured. BGL has `4747963` lines; HDFS v1 has `11175629` lines from Zenodo v7. LogHub Spark is now local from Zenodo record `8196385`, with `3852` `.log` files and `33236604` total lines. LogHub Windows is also local from the same Zenodo record, with one `Windows.log` file, `114608388` lines, and `28012696901` bytes. | Parse log events, tokenize templates, infer block/session candidates, window template counts, and retained top-template summaries. | `LogEvent`, `TemplateToken`, `TemplateCandidate`, `SessionEvent`, `WindowSummary`, retained top-k/template candidates. | Log-line/template/session/window/epoch bucket; template dictionary and block index durable. | Implemented as `LogHubRegionMatrix` q1/q2/q3, `LogHubTopTemplatesMatrix`, and `LogHubRetainedSessionMatrix`; 20k smoke, 1M medians, HDFS q2 L1, HDFS top templates 1M x20 L1, HDFS top templates 5M x5 L1/L2, Spark top-template 20k/1M/5M rows, Windows top-template 20k/1M/5M rows, HDFS top-template `streaming-file` 1M rows, HDFS q3 `streaming-file` 1M rows, HDFS retained session/join `streaming-file` 1M active-16 rows, and Spark archive-wide retained session `tar.gzcat` 1M active-16 rows completed. | Keep as real-input modest throughput/RSS/tail evidence and the strongest current real retained top-k/session family. HDFS q2 remains a checked page/window RSS win with elapsed tie. HDFS top templates is better: reusable checked `EpochTopKByKey` at 5M lines x5 is `18.26 s`, RSS `92 MB`, versus retained heap `19.04 s`, RSS `504 MB`; L2 also removes heap's `62.421 ms` timed GC. The streaming-file top-template row upgrades the same shape to real-streaming-input evidence with checked top-k L1 `8.06 s`, RSS `12 MB`, versus retained heap `8.10 s`, RSS `76 MB`. The HDFS q3 streaming-file row cuts RSS sharply (`130 MB` checked versus `862 MB` heap) and lowers GC tails, but loses L1 elapsed (`30.29 s` versus `26.88 s`). HDFS retained session/join is true streaming input but heap GC remains too small (`1.2%` session, about `0.1%` join). Spark archive-wide retained session is stronger fixed-memory evidence: L1 heap `27.62 s`/`391 MB` versus checked scoped `19.85 s`/`73 MB`, and heap fails below `128M`; L2 heap GC is still only about `2.1%`, so it is not the missing GC-time flagship. Spark and Windows top templates confirm the same retained top-k shape can remove more timed GC (`128.140 ms` Spark and `122.440 ms` Windows median at 5M), but L1 is only a modest elapsed win and RSS is tied/slightly worse at 5M. |
| 8a | Wikimedia clickstream retained session | Public Wikimedia clickstream enwiki dump at `cache/benchmark-data/wikimedia/clickstream-enwiki-2026-03.tsv.gz`. | Stream clickstream TSV rows, derive session keys from source article, target article, and link kind, retain per-row clickstream events plus per-key aggregate entries. | `ClickstreamSessionEvent`-shaped retained event objects plus session aggregate entries. | Epoch/session close; source archive stays compressed. | Implemented via `LogHubRetainedSessionMatrix` workload `wikimedia-clickstream-session`; 20k smoke, 1M L1/L2, 5M L1/L2, 10M 3-run L1/L2, and heap/checked cap probes completed. | Promote as real-streaming retained clickstream evidence. At 1M, checked Rift is L1 `5.81 s`, RSS `138 MB`, versus heap `6.50 s`, RSS `784 MB`; L2 checked Rift is `1952.438 ms`, GC `9.237 ms`, versus heap `2038.262 ms`, GC `150.157 ms`. At 5M, checked Rift is L1 `27.86 s`, RSS `138 MB`, versus heap `28.77 s`, RSS `1.54 GB`; L2 is essentially tied but checked cuts median/max GC to `46.492/46.991 ms` from heap `334.176/1066.487 ms`. At 10M x3, checked Rift is `59.37 s`, RSS `138 MB`, versus heap `62.52 s`, RSS `1.80 GB`; L2 checked Rift is `19635.995 ms`, GC `96.069 ms`, versus heap `20103.863 ms`, GC `851.023 ms`. Heap fails at `1G`, `768M`, and `512M`; checked rows complete under `64M`. |
| 9 | Theodolite UC2 / UC4 local kernel | Theodolite source clone at `cache/benchmark-data/theodolite/source`, commit `dfa768a25eec3c3f5a57b7d4839a0c255fd6fa7d`. Real source paired for local rows: UCI Household Electric Power Consumption archive at `cache/benchmark-data/theodolite/real-power/household_power_consumption.zip`, SHA-256 `9f84b46ade8a2d8e1286ec4b2b6c2987a45a755c59f263be3b3b3d10dfbda3ff`; extracted text has `2075260` lines including header and `2049280` usable measurements in the current parser. | `q1-downsample` real measurements by group/window; `q2-hierarchical` measurement plus three hierarchy contribution records per line; `q3-retained-uc4` measurement plus twelve UC4-style retained hierarchy contribution records per line, without Kafka/Kubernetes. | Measurement records, hierarchy contribution records, aggregate outputs. | Epoch/window/group bucket; hierarchy/group arrays durable. | Implemented as `TheodolitePowerRegionMatrix`; 20k smoke, 1M q1/q2 rows, full local q2 L1/L2 rows, and retained UC4 q3 20k/1M/full L1/L2 rows completed over compressed archive-member input. | Keep q2 as real-input modest/control evidence, but promote q3 as the current strongest real-streaming retained time-series row. Full local q3 processes `2049280` usable records and allocates `26640640` checked region objects in L2. L1 checked Rift is `14.06 s`, RSS `26.6 MB`, versus heap `16.85 s`, RSS `207 MB`; L2 checked Rift is `3769.962 ms`, GC `31.570 ms`, versus heap `4504.438 ms`, GC `335.309 ms`, max GC `482.380 ms`. Heap completes at `128M` cap but slows to `17.90 s`, fails at `64M`, while checked Rift completes at `64M` in `14.27 s`. This is still a local Theodolite-style kernel paired with real input, not an exact Theodolite artifact reproduction. |
| 10 | GDELT / security NDJSON logs | Public event/log streams; exact dataset not selected. | Byte-slice parse/project, enrichment, session/window counts, alert candidates. | Event records, field slices, enrichment records, alert/session/window contributions. | Line/session/window bucket; enrichment dictionary durable. | Not selected or downloaded. | Lower-priority public-log fallback after DSPBench/RIoTBench/LogHub. |

## DSPBench Triage Notes

The DSPBench project is the best immediate candidate family because it is a
published DSPS benchmark suite with 15 applications spanning finance,
telecommunications, sensor networks, social networks, and other domains, and
the paper reports workload characterization including memory occupation. The
public source is available at `https://github.com/GMAP/DSPBench`; the local
pinned archive is:

`/Users/siyaoliu/rift/cache/benchmark-data/dspbench/DSPBench-00c20da828faf2b960fdb697c61d34cb25461875.zip`

Pinned source commit:

`00c20da828faf2b960fdb697c61d34cb25461875`

The expanded checkout at
`/Users/siyaoliu/rift/cache/benchmark-data/dspbench/source` is optional now
that `DSPBenchRegionMatrix` reads the sample inputs through `zip:/archive!member`
specs.

Relevant inspected paths:

- `dspbench-threads/src/main/java/org/dspbench/applications/spikedetection/*`
- `dspbench-threads/src/main/java/org/dspbench/applications/frauddetection/*`
- `dspbench-threads/src/main/java/org/dspbench/applications/bargainindex/*`
- `dspbench-threads/data/sensors.dat`
- `dspbench-threads/data/credit-card.dat`
- `dspbench-threads/data/stocks.csv`

Bundled local data counts from the source archive:

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

HDFS q3 active-window heap-cap follow-up:

| Row | Heap/control | Checked row | Interpretation |
|---|---:|---:|---|
| HDFS q3 streaming 1M, active 16, `512M` heap | heap `17.87 s`, GC `136.507 ms`, RSS `540786688` | checked page-token `17.87 s`, GC `0`, RSS `693813248` | near tie; checked removes GC but uses higher RSS under this live-window shape. |
| HDFS q3 streaming 1M, active 16, `256M` heap | heap `21.34 s`, GC `1989.577 ms`, `17` collections, RSS `272449536` | checked page-token same row above | heap-cap pressure appears; checked avoids GC slowdown but is not lower-RSS. |
| HDFS q3 streaming 1M, active 16, `128M` heap | heap fails with out-of-heap | checked page-token completes | fixed-memory pressure exists, but the checked page-token live payload is too high for a clean memory win. |

Decision: useful triage. It confirms that retained real log session/template
objects can stress Scala Native heap under caps, but the current page-token q3
topology pays high live region payload. The next attempt should use a
Broom-like retained join/session topology or StreamFlex-style event-correlation
shape where retained objects die at tighter logical boundaries.

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
| HDFS streaming-file 1M x3 L1 | retained heap `8.10 s`, RSS `76 MB` | checked scoped `EpochTopKByKey` `8.06 s`, RSS `12 MB` | first true streaming-input row: no parsed total-input arrays; reusable checked top-k is a near-tie/slight throughput win and about `84%` lower RSS. |
| HDFS streaming-file 1M L2 | retained heap `2765.068 ms`, GC `32.681 ms` | checked scoped `EpochTopKByKey` `2697.653 ms`, GC `0 ms` | removes timed heap GC but parser/file/query CPU dominates the full streaming loop. |

Decision: keep HDFS top templates as the real-input retained top-k regression
row. It is still not a huge-GC flagship, but it demonstrates the kind of
real-input retained-object/RSS win that should guide future top-k/session
operator work. The new `streaming-file` row upgrades this evidence from
preloaded replay to a true streaming-input candidate.

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

The richer `LogHubRegionMatrix` `q3-template-session` path was also run on
Windows to test whether materializing more per-line template/session objects
would create a stronger real-input case. It did not:

| Row | Heap/control | Best region/checked row | Interpretation |
|---|---:|---:|---|
| Windows q3 20k smoke | heap `217.586 ms`, GC `0 ms`, L1 RSS `21938176` | checked scoped page-token `218.801 ms`, GC `0 ms`, RSS `27426816` | Smoke only; checksums/output matched. |
| Windows q3 1M x3 | heap L2 `17405.613 ms`, GC `147.336 ms`, max GC `151.350 ms`; L1 `88.57 s`, RSS `408715264` | checked scoped page-token L2 `17783.560 ms`, GC `33.945 ms`; L1 `90.26 s`, RSS `445661184`; trusted Streaming L2 `17854.141 ms`, GC `23.482 ms` | Negative/control row. q3 is much more CPU/file dominated than top-template; region rows cut timed GC but lose elapsed and RSS. |

Decision: do not tune Windows q3. It is useful evidence that richer real log
materialization alone is not enough; the query must retain enough ordinary
objects with reclaim-sensitive lifetimes for region bulk close to matter more
than parser/query CPU.

## LogHub Spark q3 Template/Session Follow-Up

Spark q3 was run after the Spark and Windows top-template rows to check
whether richer session/template object materialization over Spark logs changes
the conclusion. The row uses one large Spark application subset:

`/Users/siyaoliu/rift/cache/benchmark-data/loghub/Spark/application_1485248649253_0132/*.log`

The subset has `61` log files and `4242303` lines, enough for a bounded 1M
row without passing all `3852` Spark files through `LOGHUB_INPUTS`.

| Row | Heap/control | Best region/checked row | Interpretation |
|---|---:|---:|---|
| Spark q3 20k smoke | heap `133.410 ms`, GC `0 ms` | checked scoped page-token `136.338 ms`, GC `0 ms` | Smoke only; checksums/output matched. |
| Spark q3 1M x3 | heap L2 `7602.328 ms`, GC `140.934 ms`, max GC `168.854 ms`; L1 RSS `408354816` | checked scoped page-token L2 `7534.013 ms`, GC `31.147 ms`; L1 RSS `56098816`; safezone/trusted rows are slower in L2 but also low-RSS | Real-input modest/control row. Checked scoped page-token is only `0.9%` faster than heap in the L2 loop and cuts RSS sharply, but heap timed GC is still only about `1.9%` of elapsed. |

L1 final-clean was run to collect RSS/checksum status. Do not promote the L1
elapsed from that Spark q3 run: two Darwin `/usr/bin/time -l` real-time fields
were inconsistent with user/sys time and observed process duration. Use L2
elapsed for this control row and L1 only for RSS/checksum.

Decision: park Spark q3 alongside Windows q3. Richer real log
session/template parsing is still parser/query dominated; the stronger LogHub
story remains retained top-k/template rows, especially HDFS 5M.

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

1. Continue the retained top-k/session family only if the next query is more
   naturally stateful than the current parser/hash rows. Spark archive-wide
   retained session is now the strongest LogHub fixed-memory row, but it is
   still not GC-heavy by time share. The next LogHub variant should be a
   genuinely high-cardinality session/template/join API row, or else park the
   family and move to larger StackExchange/SNAP or other retained-state inputs.
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
