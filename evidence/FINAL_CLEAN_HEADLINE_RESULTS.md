# Final-Clean Headline Results

Date: 2026-05-09
Last updated: 2026-05-11 14:08 CEST

Status: L1 runner support exists for the first representative binaries. One
focused retained-epoch L1 row has been collected from clean child commit
`f1aa55484`, and Dataflow SELECT/AGGREGATE/JOIN representative L1 rows have
been collected from child `7573d7577`. The first Yak LiveJournal real-input
L1 row and generated Common Crawl-shaped q1/q2 L1 rows have also been
collected from child `7573d7577`. ReML-shaped Tier 1 L1 rows have been
collected from child `7573d7577`; the broader report-grade L1 headline sweep
is still pending.
Child `7573d7577` extends external timing/RSS summary support to Dataflow,
Yak, Common Crawl WET-shaped, and ReML runners. Child `c5bbc498f` adds the
same support to StreamFlex and Stancu. StreamFlex direct-epoch
throughput/latency and Stancu transaction representative L1 rows are now
recorded below. Child `678a6eb41` adds the same L1 support to the
SPECjbb2005-workload Scala Native port, and an 8-warehouse representative row
is recorded below. Child `3598efe29` adds L1 support to the LogHub
top-template matrix, and the real HDFS reusable top-k row is recorded below.
Child `fe8f0d853` adds L1 support to `LogHubRegionMatrix`, and the real HDFS
q2 page/window row is recorded below as an elapsed tie / RSS win.
Child `95f4f4d71` adds L1 support to `DSPBenchRegionMatrix`, and the Fraud/Log
q2 page/window rows are recorded below.
Child `dffe178a0` adds L1 support to `NexmarkRegionMatrix`, and the
Beam-default-style q3/q8/q9/q11 rows are recorded below.
Child `54bf38c45` adds L1 support to `GithubArchiveRegionMatrix`. The
two-hour real file-backed byte-slice q1/q2 rows and generated/preloaded
retained q2 rows are recorded below.
Child `bc9fd5979` records symmetric direct-summary L1 counterpart rows for
DSPBench and LogHub, so summary-only lower bounds are no longer heap-only.
Child `59acadda6` reduces `EpochTopKByKey` hot-path overhead; refreshed
LogHub HDFS top-k L1 rows are recorded below.
Child `bcbfe80f5` adds Yak topword same-shape heap top-k and reusable
`EpochTopKByKey` rows; the L1 10M x20 topword rows are recorded below.
Child `0773d4c17` is the clean implementation checkpoint for the retained-row
gap fill in this update: DSPBench Fraud retained q2 and LogHub q2/q3 retained
now have L1 final-clean rows with valid `/usr/bin/time -l` RSS. The same
checkpoint also adds a larger real-input LogHub HDFS top-k row at 5M lines x5.
Child `d1fd16a64` adds ReML/MLKit-shaped Tier 2 ports for `logic`, `ray`, and
`tsp`; their first report-grade L1/L2 rows are recorded below.
Child `cd08f23d4` adds Yak `topwordreal` over the real Stack Exchange
AskUbuntu `Posts.xml` dump; its first 10M-token x5 L1 rows are recorded below.

## Definition

An L1 final-clean row is the cleanest elapsed/RSS measurement:

- optimized non-profiled binary;
- no diagnostics, tracing, allocation attribution, or precise counters;
- no in-timed-section GC-stat or region-stat reads;
- external `/usr/bin/time -l` for total real/user/sys time and peak RSS;
- only checksum/output count and minimal mode/input metadata printed by the
  benchmark.

Current matrix result files are mostly L2 standard stats rows because they were
collected before final-clean mode existed. They remain the right source for
GC/RSS/region interpretation, but final paper headline timing should be filled
from this file after report-grade L1 reruns.

## Implemented L1 Entrypoints

Set `RIFT_FINAL_CLEAN=1` or `RIFT_EVAL_MEASUREMENT_LEVEL=L1` for:

- `RetainedEpochReclaimMatrix`
- `YakRegionMatrix`
- `DataflowRegionMatrix`
- `CommonCrawlWetMatrix`
- `ReMLRegionMatrix`
- `StreamFlexRegionMatrix`
- `StancuRegionMatrix`
- `SpecJbb2005PortMatrix`
- `LogHubTopTemplatesMatrix`
- `LogHubRegionMatrix`
- `DSPBenchRegionMatrix`
- `NexmarkRegionMatrix`
- `GithubArchiveRegionMatrix`

The binaries print `RESULT ... measurement_level=L1 final_clean=1 ...` and
avoid internal timed-section stats.

## Required First Sweep

| Group | Representative rows | Reason |
|---|---|---|
| retained-object reclaim | focused retained 1M; GH Archive-shaped q2; LogHub q2/q3; DSPBench Fraud q2 | isolates heap GC reclaim versus region bulk close/reset |
| direct epoch | Yak LiveJournal 10M/50M; Dataflow SELECT/AGGREGATE/JOIN; StreamFlex throughput; Stancu/SPECjbb-style | user-facing `RiftRegion.epoch` evidence |
| page/window token | generated Common Crawl-shaped q1/q2; DSPBench Fraud/Log q2; LogHub HDFS q2 | page/window stream operator evidence |
| generated stream methodology | NEXMark q3/q8/q9/q11 | recognized generated Beam-default-style stream controls |
| ReML/MLKit ports | `msort`, `msort-r`, `ratio`, Tier 2 `logic`/`ray`/`tsp`, plus compute/timing controls | non-stream typed-region comparison axis |
| StreamFlex | throughput and latency rows | prior-work latency/throughput axis |
| Stancu/SPECjbb-style | transaction rows | transaction-boundary region axis |
| retained top-k API | LogHub HDFS top templates; Yak topword | reusable `EpochTopKByKey` evidence |

## L1/L2 Completeness Audit

| Representative group | L1 headline status | L2 interpretation status | Action |
|---|---|---|---|
| retained-object reclaim | focused, GH Archive-shaped q2, DSPBench Fraud q2, and LogHub q2/q3 now have L1 rows | L2 rows exist in retained matrix docs | complete for current report |
| direct epoch | Yak LiveJournal, Dataflow, StreamFlex, Stancu, SPECjbb-style rows have L1 rows | L2 rows exist in per-matrix docs/report | complete for current report |
| page/window token | Common Crawl-shaped, LogHub HDFS q2, DSPBench Fraud/Log q2, GH Archive q1/q2 have L1 rows | L2 rows exist for GC/RSS interpretation | complete for current report |
| generated methodology | NEXMark q3/q8/q9/q11 have L1 rows | L2 rows remain the GC source | complete for selected rows |
| ReML/MLKit ports | Tier 1 and first Tier 2 local ports have L1 rows | L2 rows exist for Tier 1 and first Tier 2 interpretation | exact artifact rerun still blocked |
| real-input top-k/text | LogHub HDFS 1M x20 and 5M x5 have L1 rows; AskUbuntu `topwordreal` 10M x5 has L1 rows | HDFS 5M and AskUbuntu 10M L2 rows added for GC interpretation | continue larger real-input search after report update |

Presentation status: the current report/slides use only rows marked complete
in this audit or explicitly labeled lower-bound/control rows in
`evidence/EVALUATION_CLASSIFIED_SUMMARY.md`. L1 elapsed/RSS is the presentation
source; L2 rows are interpretation-only for GC/region behavior.

## L1 Headline Rows

Fill this table only from final-clean runs. Rows below use external
`/usr/bin/time -l` process timing. For the retained focused row, each external
process runs 20 identical 1M-record iterations inside the optimized native
binary to reduce process-startup noise; the table reports total process time
for those 20 iterations.

| Benchmark | Input type | API/topology | Comparison class | Mode | Runs | Median real time | Min real time | Max real time | Max RSS | Checksum/output | Claim |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| retained epoch focused 1M x20 | synthetic focused matrix | retained epoch/drop-anchor | retained-object memory-management | `heap-epoch-retained-no-traverse` | 3 processes x 20 iterations | `0.70 s` total (`35.0 ms/iter`) | `0.70 s` | `0.99 s` | `21233664 bytes` | checksum `-829278451938965381`, output `163644` | L1 clean heap retained/drop-anchor control |
| retained epoch focused 1M x20 | synthetic focused matrix | retained epoch/drop-anchor | retained-object memory-management | `checked-epoch-retained-no-traverse` | 3 processes x 20 iterations | `0.50 s` total (`25.0 ms/iter`) | `0.50 s` | `0.51 s` | `6144000 bytes` | checksum `-829278451938965381`, output `163644` | L1 clean checked stream retained win over heap retained |
| retained epoch focused 1M x20 | synthetic focused matrix | retained epoch/drop-anchor | retained-object memory-management | `checked-scoped-epoch-retained-no-traverse` | 3 processes x 20 iterations | `0.47 s` total (`23.5 ms/iter`) | `0.47 s` | `0.48 s` | `6193152 bytes` | checksum `-829278451938965381`, output `163644` | L1 clean checked scoped retained win over heap retained |
| GH Archive-shaped q2 retained 1M x20 | generated/preloaded stressor | summary-only direct aggregate | summary-only topology | `heap-direct-summary-only` | 3 processes x 20 iterations | `1.28 s` total (`64.0 ms/iter`) | `1.27 s` | `1.31 s` | `6832128 bytes` | checksum `7294087528134281006`, output `163487` | L1 clean topology lower bound, not memory-management evidence |
| GH Archive-shaped q2 direct-summary 1M x20 | generated/preloaded stressor | checked direct summary | summary-only topology / checked counterpart | `checked-epoch-stream` | 3 processes x 20 iterations | `1.45 s` total (`72.5 ms/iter`) | `1.43 s` | `1.46 s` | `6946816 bytes` | checksum `7294087528134281006`, output `163487` | L1 clean checked region counterpart to heap direct-summary; topology lower bound, not memory-management evidence |
| GH Archive-shaped q2 direct-summary 1M x20 | generated/preloaded stressor | checked scoped direct summary | summary-only topology / checked counterpart | `checked-epoch-scoped` | 3 processes x 20 iterations | `1.45 s` total (`72.5 ms/iter`) | `1.43 s` | `1.46 s` | `6995968 bytes` | checksum `7294087528134281006`, output `163487` | L1 clean checked scoped counterpart to heap direct-summary; topology lower bound, not memory-management evidence |
| DSPBench Fraud q2 direct-summary 1M x20 | generated/indexable DSPBench-shaped stream | direct summary | summary-only topology | `heap-direct-summary-only` | 3 processes x 20 iterations | `5.62 s` total (`281.0 ms/iter`) | `5.57 s` | `5.71 s` | `39747584 bytes` | checksum `-5765375221524988491`, output `613295` | L1 clean heap direct-summary topology lower bound |
| DSPBench Fraud q2 direct-summary 1M x20 | generated/indexable DSPBench-shaped stream | checked direct summary | summary-only topology / checked counterpart | `checked-epoch-stream` | 3 processes x 20 iterations | `5.67 s` total (`283.5 ms/iter`) | `5.61 s` | `5.87 s` | `39829504 bytes` | checksum `-5765375221524988491`, output `613295` | L1 clean checked stream counterpart, within about `1%` of heap direct-summary |
| DSPBench Fraud q2 direct-summary 1M x20 | generated/indexable DSPBench-shaped stream | checked scoped direct summary | summary-only topology / checked counterpart | `checked-epoch-scoped` | 3 processes x 20 iterations | `5.68 s` total (`284.0 ms/iter`) | `5.64 s` | `5.78 s` | `39829504 bytes` | checksum `-5765375221524988491`, output `613295` | L1 clean checked scoped counterpart, within about `1%` of heap direct-summary |
| DSPBench Log q2 direct-summary 1M x20 | generated/indexable DSPBench-shaped stream | direct summary | summary-only topology | `heap-direct-summary-only` | 3 processes x 20 iterations | `4.55 s` total (`227.5 ms/iter`) | `4.50 s` | `4.63 s` | `48693248 bytes` | checksum `-997356215995052759`, output `200` | L1 clean heap direct-summary topology lower bound |
| DSPBench Log q2 direct-summary 1M x20 | generated/indexable DSPBench-shaped stream | checked direct summary | summary-only topology / checked counterpart | `checked-epoch-stream` | 3 processes x 20 iterations | `4.56 s` total (`228.0 ms/iter`) | `4.55 s` | `4.64 s` | `39829504 bytes` | checksum `-997356215995052759`, output `200` | L1 clean checked stream counterpart, tied with heap direct-summary |
| DSPBench Log q2 direct-summary 1M x20 | generated/indexable DSPBench-shaped stream | checked scoped direct summary | summary-only topology / checked counterpart | `checked-epoch-scoped` | 3 processes x 20 iterations | `4.59 s` total (`229.5 ms/iter`) | `4.57 s` | `4.60 s` | `39829504 bytes` | checksum `-997356215995052759`, output `200` | L1 clean checked scoped counterpart, near same-shape heap |
| LogHub q2 direct-summary 1M x20 | generated/indexable log stream | direct summary | summary-only topology | `heap-direct-summary-only` | 3 processes x 20 iterations | `4.23 s` total (`211.5 ms/iter`) | `4.19 s` | `4.24 s` | `6504448 bytes` | checksum `-7709990302891202320`, output `163487` | L1 clean heap direct-summary topology lower bound |
| LogHub q2 direct-summary 1M x20 | generated/indexable log stream | checked direct summary | summary-only topology / checked counterpart | `checked-epoch-stream` | 3 processes x 20 iterations | `4.39 s` total (`219.5 ms/iter`) | `4.33 s` | `4.41 s` | `6668288 bytes` | checksum `-7709990302891202320`, output `163487` | L1 clean checked stream counterpart, within about `4%` of heap direct-summary |
| LogHub q2 direct-summary 1M x20 | generated/indexable log stream | checked scoped direct summary | summary-only topology / checked counterpart | `checked-epoch-scoped` | 3 processes x 20 iterations | `4.38 s` total (`219.0 ms/iter`) | `4.33 s` | `4.38 s` | `6701056 bytes` | checksum `-7709990302891202320`, output `163487` | L1 clean checked scoped counterpart, within about `4%` of heap direct-summary |
| LogHub q3 direct-summary 1M x20 | generated/indexable template/session stream | direct summary | summary-only topology | `heap-direct-summary-only` | 3 processes x 20 iterations | `37.01 s` total (`1850.5 ms/iter`) | `36.83 s` | `37.16 s` | `8372224 bytes` | checksum `-1899680319541187710`, output `312151` | L1 clean heap direct-summary topology lower bound |
| LogHub q3 direct-summary 1M x20 | generated/indexable template/session stream | checked direct summary | summary-only topology / checked counterpart | `checked-epoch-stream` | 3 processes x 20 iterations | `37.65 s` total (`1882.5 ms/iter`) | `37.15 s` | `37.71 s` | `8437760 bytes` | checksum `-1899680319541187710`, output `312151` | L1 clean checked stream counterpart; q3 remains query-CPU dominated |
| LogHub q3 direct-summary 1M x20 | generated/indexable template/session stream | checked scoped direct summary | summary-only topology / checked counterpart | `checked-epoch-scoped` | 3 processes x 20 iterations | `38.00 s` total (`1900.0 ms/iter`) | `37.36 s` | `38.33 s` | `8388608 bytes` | checksum `-1899680319541187710`, output `312151` | L1 clean checked scoped counterpart; q3 remains query-CPU dominated |
| GH Archive-shaped q2 retained 1M x20 | generated/preloaded stressor | retained epoch/drop-anchor | retained-object memory-management | `heap-epoch-retained-no-traverse` | 3 processes x 20 iterations | `4.62 s` total (`231.0 ms/iter`) | `4.58 s` | `4.73 s` | `147341312 bytes` | checksum `7294087528134281006`, output `163487` | L1 clean heap retained/drop-anchor control |
| GH Archive-shaped q2 retained 1M x20 | generated/preloaded stressor | retained epoch/drop-anchor | retained-object memory-management | `checked-epoch-retained-no-traverse` | 3 processes x 20 iterations | `3.65 s` total (`182.5 ms/iter`) | `3.58 s` | `3.73 s` | `15990784 bytes` | checksum `7294087528134281006`, output `163487` | L1 clean checked stream retained win over heap retained |
| GH Archive-shaped q2 retained 1M x20 | generated/preloaded stressor | retained epoch/drop-anchor | retained-object memory-management | `checked-scoped-epoch-retained-no-traverse` | 3 processes x 20 iterations | `3.44 s` total (`172.0 ms/iter`) | `3.43 s` | `3.47 s` | `16056320 bytes` | checksum `7294087528134281006`, output `163487` | L1 clean checked scoped retained win over heap retained: about 25.5% faster and 89% lower RSS |
| DSPBench Fraud q2 retained 1M x20 | generated/indexable DSPBench-shaped stream | retained epoch/drop-anchor | retained-object memory-management | `heap-epoch-retained-no-traverse` | 3 processes x 20 iterations | `8.40 s` total (`420.0 ms/iter`) | `8.38 s` | `8.46 s` | `206405632 bytes` | checksum `-5765375221524988491`, output `613295` | L1 clean heap retained/drop-anchor control |
| DSPBench Fraud q2 retained 1M x20 | generated/indexable DSPBench-shaped stream | retained epoch/drop-anchor | retained-object memory-management | `checked-epoch-retained-no-traverse` | 3 processes x 20 iterations | `7.92 s` total (`396.0 ms/iter`) | `7.91 s` | `7.98 s` | `46792704 bytes` | checksum `-5765375221524988491`, output `613295` | L1 clean checked stream retained win over heap retained |
| DSPBench Fraud q2 retained 1M x20 | generated/indexable DSPBench-shaped stream | retained epoch/drop-anchor | retained-object memory-management | `checked-scoped-epoch-retained-no-traverse` | 3 processes x 20 iterations | `7.90 s` total (`395.0 ms/iter`) | `7.74 s` | `7.97 s` | `46809088 bytes` | checksum `-5765375221524988491`, output `613295` | L1 clean checked scoped retained win over heap retained with much lower RSS |
| LogHub q2 retained 1M x20 | generated/indexable log stream | retained epoch/drop-anchor | retained-object memory-management | `heap-epoch-retained-no-traverse` | 3 processes x 20 iterations | `10.79 s` total (`539.5 ms/iter`) | `10.76 s` | `11.14 s` | `206340096 bytes` | checksum `-7709990302891202320`, output `163487` | L1 clean heap retained/drop-anchor control |
| LogHub q2 retained 1M x20 | generated/indexable log stream | retained epoch/drop-anchor | retained-object memory-management | `checked-epoch-retained-no-traverse` | 3 processes x 20 iterations | `8.57 s` total (`428.5 ms/iter`) | `8.36 s` | `8.67 s` | `21807104 bytes` | checksum `-7709990302891202320`, output `163487` | L1 clean checked stream retained win over heap retained |
| LogHub q2 retained 1M x20 | generated/indexable log stream | retained epoch/drop-anchor | retained-object memory-management | `checked-scoped-epoch-retained-no-traverse` | 3 processes x 20 iterations | `8.12 s` total (`406.0 ms/iter`) | `7.99 s` | `8.25 s` | `21905408 bytes` | checksum `-7709990302891202320`, output `163487` | L1 clean checked scoped retained win over heap retained |
| LogHub q3 retained 1M x20 | generated/indexable template/session stream | retained epoch/drop-anchor | retained-object memory-management | `heap-epoch-retained-no-traverse` | 3 processes x 20 iterations | `47.55 s` total (`2377.5 ms/iter`) | `47.24 s` | `47.74 s` | `813514752 bytes` | checksum `-1899680319541187710`, output `312151` | L1 clean heap retained/drop-anchor control |
| LogHub q3 retained 1M x20 | generated/indexable template/session stream | retained epoch/drop-anchor | retained-object memory-management | `checked-epoch-retained-no-traverse` | 3 processes x 20 iterations | `45.76 s` total (`2288.0 ms/iter`) | `45.57 s` | `46.09 s` | `29523968 bytes` | checksum `-1899680319541187710`, output `312151` | L1 clean checked stream retained modest elapsed win and large RSS win |
| LogHub q3 retained 1M x20 | generated/indexable template/session stream | retained epoch/drop-anchor | retained-object memory-management | `checked-scoped-epoch-retained-no-traverse` | 3 processes x 20 iterations | `60.29 s` total (`3014.5 ms/iter`) | `59.37 s` | `60.80 s` | `29671424 bytes` | checksum `-1899680319541187710`, output `312151` | L1 checked scoped retained is slower but still a large RSS win; use checked stream as the safe retained row for q3 |
| Dataflow SELECT 1M x20 | generated methodology | direct epoch / scoped region | framework API win | `gc-heap` | 3 processes x 20 iterations | `0.62 s` total (`31.0 ms/iter`) | `0.61 s` | `0.63 s` | `39288832 bytes` | checksum `131080080920` | L1 clean natural heap baseline |
| Dataflow SELECT 1M x20 | generated methodology | direct epoch / scoped region | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `0.46 s` total (`23.0 ms/iter`) | `0.46 s` | `0.48 s` | `7536640 bytes` | checksum `131080080920` | L1 clean rooted scoped-region baseline |
| Dataflow SELECT 1M x20 | generated methodology | `RiftRegion.epoch` checked scoped | framework API win | `checked-epoch-scoped` | 3 processes x 20 iterations | `0.38 s` total (`19.0 ms/iter`) | `0.38 s` | `0.39 s` | `7553024 bytes` | checksum `131080080920` | L1 clean checked epoch win over heap and rooted scoped baseline |
| Dataflow AGGREGATE 1M x20 | generated methodology | direct epoch / scoped region | framework API win | `gc-heap` | 3 processes x 20 iterations | `1.10 s` total (`55.0 ms/iter`) | `1.10 s` | `1.13 s` | `75890688 bytes` | checksum `163835709480` | L1 clean natural heap baseline |
| Dataflow AGGREGATE 1M x20 | generated methodology | direct epoch / scoped region | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `0.79 s` total (`39.5 ms/iter`) | `0.79 s` | `0.80 s` | `10829824 bytes` | checksum `163835709480` | L1 clean rooted scoped-region baseline |
| Dataflow AGGREGATE 1M x20 | generated methodology | `RiftRegion.epoch` checked scoped | framework API win | `checked-epoch-scoped` | 3 processes x 20 iterations | `0.69 s` total (`34.5 ms/iter`) | `0.69 s` | `0.70 s` | `10829824 bytes` | checksum `163835709480` | L1 clean checked epoch win over heap and rooted scoped baseline |
| Dataflow JOIN 1M x20 | generated methodology | direct epoch / scoped region | framework API win | `gc-heap` | 3 processes x 20 iterations | `0.55 s` total (`27.5 ms/iter`) | `0.55 s` | `0.55 s` | `75071488 bytes` | checksum `193232836790` | L1 clean natural heap baseline |
| Dataflow JOIN 1M x20 | generated methodology | direct epoch / scoped region | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `0.46 s` total (`23.0 ms/iter`) | `0.46 s` | `0.46 s` | `7389184 bytes` | checksum `193232836790` | L1 clean rooted scoped-region baseline |
| Dataflow JOIN 1M x20 | generated methodology | `RiftRegion.epoch` checked scoped | framework API win | `checked-epoch-scoped` | 3 processes x 20 iterations | `0.39 s` total (`19.5 ms/iter`) | `0.39 s` | `0.39 s` | `7405568 bytes` | checksum `193232836790` | L1 clean checked epoch win over heap and rooted scoped baseline |
| Yak topword 10M x20 | Yak-style generated methodology | retained epoch records + close traversal | natural heap baseline | `gc-heap` | 3 processes x 20 iterations | `6.25 s` total (`312.5 ms/iter`) | `6.08 s` | `6.26 s` | `75317248 bytes` | checksum `3387296563095546471` | L1 clean natural heap topword baseline |
| Yak topword 10M x20 | Yak-style generated methodology | rooted scoped retained records + close traversal | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `5.09 s` total (`254.5 ms/iter`) | `5.00 s` | `5.13 s` | `16007168 bytes` | checksum `3387296563095546471` | L1 clean rooted scoped win over heap |
| Yak topword 10M x20 | Yak-style generated methodology | retained records + append-time top-k | same-shape heap control | `heap-topk-retained-no-traverse` | 3 processes x 20 iterations | `5.72 s` total (`286.0 ms/iter`) | `5.64 s` | `5.73 s` | `146833408 bytes` | checksum `3387296563095546471` | L1 same-shape heap top-k retained control; faster than natural heap but higher RSS |
| Yak topword 10M x20 | Yak-style generated methodology | `RiftRegion.epoch` retained records + close traversal | framework API win | `checked-epoch-scoped` | 3 processes x 20 iterations | `4.61 s` total (`230.5 ms/iter`) | `4.55 s` | `4.61 s` | `16023552 bytes` | checksum `3387296563095546471` | L1 clean best checked Yak topword topology |
| Yak topword 10M x20 | Yak-style generated methodology | reusable checked `EpochTopKByKey` stream | framework API win / top-k API gate | `checked-epoch-topk-stream` | 3 processes x 20 iterations | `5.12 s` total (`256.0 ms/iter`) | `5.08 s` | `5.13 s` | `15958016 bytes` | checksum `3387296563095546471` | L1 reusable top-k stream row beats heap and same-shape heap top-k, but trails scoped top-k/direct epoch |
| Yak topword 10M x20 | Yak-style generated methodology | reusable checked `EpochTopKByKey` scoped | framework API win / top-k API gate | `checked-epoch-topk-scoped` | 3 processes x 20 iterations | `4.94 s` total (`247.0 ms/iter`) | `4.91 s` | `4.96 s` | `16023552 bytes` | checksum `3387296563095546471` | L1 reusable checked top-k win over natural heap and same-shape heap top-k; direct checked epoch remains the faster topology |
| Yak AskUbuntu `topwordreal` 10M x5 | real Stack Exchange AskUbuntu `Posts.xml` text replay | retained epoch records + close traversal | natural heap baseline | `gc-heap` | 3 processes x 5 iterations | `4.19 s` total (`838 ms/iter`) | `4.05 s` | `4.27 s` | `427720704 bytes` | checksum `-4151722340504273532` | L1 clean real text/top-word heap baseline |
| Yak AskUbuntu `topwordreal` 10M x5 | real Stack Exchange AskUbuntu `Posts.xml` text replay | rooted scoped retained records + close traversal | safe rooted baseline | `region-scoped-rooted` | 3 processes x 5 iterations | `3.97 s` total (`794 ms/iter`) | `3.86 s` | `3.97 s` | `94306304 bytes` | checksum `-4151722340504273532` | L1 clean rooted scoped win over heap and large RSS cut |
| Yak AskUbuntu `topwordreal` 10M x5 | real Stack Exchange AskUbuntu `Posts.xml` text replay | retained records + append-time top-k | same-shape heap control | `heap-topk-retained-no-traverse` | 3 processes x 5 iterations | `4.40 s` total (`880 ms/iter`) | `4.29 s` | `4.41 s` | `427737088 bytes` | checksum `-4151722340504273532` | L1 same-shape heap top-k retained control; slower than natural heap for this real text row |
| Yak AskUbuntu `topwordreal` 10M x5 | real Stack Exchange AskUbuntu `Posts.xml` text replay | `RiftRegion.epoch` retained records + close traversal | framework API win | `checked-epoch-scoped` | 3 processes x 5 iterations | `3.86 s` total (`772 ms/iter`) | `3.76 s` | `4.01 s` | `94306304 bytes` | checksum `-4151722340504273532` | L1 clean direct checked epoch win over heap; matching L2 removes `23.715 ms` timed heap GC |
| Yak AskUbuntu `topwordreal` 10M x5 | real Stack Exchange AskUbuntu `Posts.xml` text replay | reusable checked `EpochTopKByKey` scoped | framework API / top-k API gate | `checked-epoch-topk-scoped` | 3 processes x 5 iterations | `4.12 s` total (`824 ms/iter`) | `4.12 s` | `4.31 s` | `93536256 bytes` | checksum `-4151722340504273532` | L1 reusable top-k is a large RSS win and slight elapsed win over heap, but trails direct checked epoch |
| StreamFlex throughput 200k x20 | generated methodology | heap transaction batches | natural heap baseline | `heap` | 3 processes x 20 iterations | `0.79 s` total (`39.5 ms/iter`) | `0.78 s` | `0.80 s` | `7929856 bytes` | checksum `3320210680833752` | L1 clean natural heap baseline |
| StreamFlex throughput 200k x20 | generated methodology | scoped transaction batches | safe rooted baseline | `improved-safezone` | 3 processes x 20 iterations | `0.77 s` total (`38.5 ms/iter`) | `0.77 s` | `0.77 s` | `5324800 bytes` | checksum `3320210680833752` | L1 clean rooted scoped-region baseline |
| StreamFlex throughput 200k x20 | generated methodology | checked direct epoch batches | framework API win | `rift-checked-safezone-direct-epoch` | 3 processes x 20 iterations | `0.58 s` total (`29.0 ms/iter`) | `0.58 s` | `0.58 s` | `5308416 bytes` | checksum `3320210680833752` | L1 clean checked direct epoch win over heap and rooted scoped baseline |
| StreamFlex latency 10k x20 | generated methodology | heap per-event latency | natural heap baseline | `heap` | 3 processes x 20 iterations | `0.18 s` total | `0.18 s` | `0.18 s` | `7946240 bytes` | checksum `657450396996205`, p50 `625 ns`, p99 `792 ns`, max `327334 ns`, misses `4` | L1 clean natural heap baseline with deadline misses |
| StreamFlex latency 10k x20 | generated methodology | scoped per-event latency | safe rooted baseline / tail win | `improved-safezone` | 3 processes x 20 iterations | `0.21 s` total | `0.21 s` | `0.21 s` | `7979008 bytes` | checksum `657450396996205`, p50 `875 ns`, p99 `1083 ns`, max `2459 ns`, misses `0` | L1 clean slower elapsed but removes deadline misses |
| StreamFlex latency 10k x20 | generated methodology | checked direct epoch latency | framework API win / tail win | `rift-checked-safezone-direct-epoch` | 3 processes x 20 iterations | `0.17 s` total | `0.17 s` | `0.17 s` | `7962624 bytes` | checksum `657450396996205`, p50 `708 ns`, p99 `833 ns`, max `25167 ns`, misses `0` | L1 clean checked direct epoch elapsed and deadline win over heap |
| Stancu transactions 200k x20 | generated transaction methodology | heap transaction batches | natural heap baseline | `heap` | 3 processes x 20 iterations | `0.85 s` total (`42.5 ms/iter`) | `0.85 s` | `0.85 s` | `7847936 bytes` | checksum `-1953196317317355226` | L1 clean natural heap baseline |
| Stancu transactions 200k x20 | generated transaction methodology | scoped transaction batches | safe rooted baseline | `improved-safezone` | 3 processes x 20 iterations | `0.71 s` total (`35.5 ms/iter`) | `0.71 s` | `0.71 s` | `7897088 bytes` | checksum `-1953196317317355226` | L1 clean rooted scoped transaction win |
| Stancu transactions 200k x20 | generated transaction methodology | checked direct epoch transactions | framework API win | `rift-checked-safezone-direct-epoch` | 3 processes x 20 iterations | `0.57 s` total (`28.5 ms/iter`) | `0.57 s` | `0.57 s` | `7880704 bytes` | checksum `-1953196317317355226` | L1 clean checked transaction/epoch win over heap and rooted scoped baseline |
| SPECjbb2005-workload port 8 warehouses x20 | clean-room transaction workload port | heap transaction batches | natural heap baseline | `gc-heap` | 3 processes x 20 iterations | `2.64 s` total (`132.0 ms/iter`) | `2.63 s` | `2.66 s` | `12369920 bytes` | checksum `-9186304385429183494` | L1 clean natural heap baseline; not official SPECjbb2005 |
| SPECjbb2005-workload port 8 warehouses x20 | clean-room transaction workload port | scoped transaction batches | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `2.48 s` total (`124.0 ms/iter`) | `2.46 s` | `2.48 s` | `7962624 bytes` | checksum `-9186304385429183494` | L1 clean rooted scoped transaction win over heap |
| SPECjbb2005-workload port 8 warehouses x20 | clean-room transaction workload port | checked direct epoch transactions | framework API win | `checked-epoch-scoped` | 3 processes x 20 iterations | `2.21 s` total (`110.5 ms/iter`) | `2.21 s` | `2.22 s` | `7995392 bytes` | checksum `-9186304385429183494` | L1 clean checked transaction/epoch win over heap and rooted scoped baseline |
| LogHub top templates HDFS 1M x20 | real HDFS file-backed/preloaded replay | retained epoch/drop-anchor | retained-object memory-management | `heap-retained-drop-anchor` | 3 processes x 20 iterations | `5.52 s` total (`276.0 ms/iter`) | `5.50 s` | `5.52 s` | `205406208 bytes` | checksum `4142347521733569598`, output `1280` | L1 retained heap/drop-anchor control; process includes one HDFS input load plus 20 replays |
| LogHub top templates HDFS 1M x20 | real HDFS file-backed/preloaded replay | benchmark-local checked retained epoch | retained-object memory-management / lower bound | `checked-scoped-epoch-retained-no-traverse` | 3 processes x 20 iterations | `4.80 s` total (`240.0 ms/iter`) | `4.73 s` | `4.81 s` | `28262400 bytes` | checksum `4142347521733569598`, output `1280` | L1 checked retained lower-bound win over heap retained |
| LogHub top templates HDFS 1M x20 | real HDFS file-backed/preloaded replay | reusable checked `EpochTopKByKey` | framework API win | `checked-scoped-epoch-topk-retained-no-traverse` | 3 processes x 20 iterations | `4.88 s` total (`244.0 ms/iter`) | `4.87 s` | `4.94 s` | `28098560 bytes` | checksum `4142347521733569598`, output `1280` | L1 reusable checked top-k win over heap retained with much lower RSS; API overhead now about `1.7%` versus benchmark-local checked row |
| LogHub top templates HDFS 5M x5 | real HDFS file-backed/preloaded replay | retained epoch/drop-anchor | retained-object memory-management | `heap-retained-drop-anchor` | 3 processes x 5 iterations | `19.04 s` total (`3808 ms/iter`) | `18.59 s` | `19.06 s` | `503775232 bytes` | checksum `-4760084277314313220`, output `6400` | L1 larger real-input retained heap/drop-anchor control; process includes one HDFS input load plus five 5M-line replays |
| LogHub top templates HDFS 5M x5 | real HDFS file-backed/preloaded replay | reusable checked `EpochTopKByKey` | framework API win | `checked-scoped-epoch-topk-retained-no-traverse` | 3 processes x 5 iterations | `18.26 s` total (`3652 ms/iter`) | `18.23 s` | `18.27 s` | `92209152 bytes` | checksum `-4760084277314313220`, output `6400` | L1 larger real-input reusable checked top-k win: `4.1%` faster than retained heap and about `82%` lower RSS; matching L2 row is heap `463.633 ms`, GC `62.421 ms` versus checked `402.916 ms`, GC `0 ms` |
| LogHub HDFS q2 1M x3 | real HDFS file-backed stream | page/window token | natural heap baseline | `heap-immix` | 3 processes x 3 iterations | `25.60 s` total (`8533 ms/iter`) | `25.58 s` | `25.75 s` | `408649728 bytes` | checksum `-4515648042024502814`, output `41` | L1 natural heap baseline; process loads 1M HDFS lines and runs q2 three times |
| LogHub HDFS q2 1M x3 | real HDFS file-backed stream | scoped page/window token | safe rooted baseline | `safezone-improved-32k` | 3 processes x 3 iterations | `25.35 s` total (`8450 ms/iter`) | `25.33 s` | `25.39 s` | `79003648 bytes` | checksum `-4515648042024502814`, output `41` | L1 rooted scoped RSS win with near-tie elapsed |
| LogHub HDFS q2 1M x3 | real HDFS file-backed stream | checked scoped page-token | framework API / RSS win | `rift-checked-safezone-page-token` | 3 processes x 3 iterations | `25.56 s` total (`8520 ms/iter`) | `25.56 s` | `25.58 s` | `79036416 bytes` | checksum `-4515648042024502814`, output `41` | L1 checked page/window row essentially ties heap elapsed and cuts RSS by about 81%; L2 row remains the GC interpretation source |
| DSPBench Fraud q2 1M x5 | real DSPBench credit-card replay | page/window token | natural heap baseline | `heap-immix` | 3 processes x 5 iterations | `4.39 s` total (`878 ms/iter`) | `4.28 s` | `4.39 s` | `358318080 bytes` | checksum `2645894572926148009`, output `594182` | L1 natural heap baseline over public DSPBench sample replay |
| DSPBench Fraud q2 1M x5 | real DSPBench credit-card replay | scoped page/window token | safe rooted baseline | `safezone-improved-32k` | 3 processes x 5 iterations | `4.47 s` total (`894 ms/iter`) | `4.36 s` | `4.54 s` | `63455232 bytes` | checksum `2645894572926148009`, output `594182` | L1 rooted scoped RSS win but elapsed loss versus heap |
| DSPBench Fraud q2 1M x5 | real DSPBench credit-card replay | trusted streaming page/window token | unsafe/trusted lower bound | `rift-trusted-streaming` | 3 processes x 5 iterations | `4.18 s` total (`836 ms/iter`) | `4.07 s` | `4.18 s` | `63389696 bytes` | checksum `2645894572926148009`, output `594182` | L1 trusted lower-bound elapsed/RSS win |
| DSPBench Fraud q2 1M x5 | real DSPBench credit-card replay | checked scoped page-token | framework API / RSS win | `rift-checked-safezone-page-token` | 3 processes x 5 iterations | `4.44 s` total (`888 ms/iter`) | `4.34 s` | `4.46 s` | `59539456 bytes` | checksum `2645894572926148009`, output `594182` | L1 checked page/window row cuts RSS by about 83% but is slightly slower than heap; L2 remains the GC interpretation source |
| DSPBench Log q2 1M x5 | real DSPBench common-log replay | page/window token | natural heap baseline | `heap-immix` | 3 processes x 5 iterations | `8.89 s` total (`1778 ms/iter`) | `8.66 s` | `8.91 s` | `307593216 bytes` | checksum `-4720769113503374536`, output `179` | L1 natural heap baseline over public DSPBench sample replay |
| DSPBench Log q2 1M x5 | real DSPBench common-log replay | scoped page/window token | safe rooted baseline | `safezone-improved-32k` | 3 processes x 5 iterations | `8.91 s` total (`1782 ms/iter`) | `8.74 s` | `8.97 s` | `47939584 bytes` | checksum `-4720769113503374536`, output `179` | L1 rooted scoped RSS win with near-tie elapsed |
| DSPBench Log q2 1M x5 | real DSPBench common-log replay | trusted streaming page/window token | unsafe/trusted lower bound | `rift-trusted-streaming` | 3 processes x 5 iterations | `8.51 s` total (`1702 ms/iter`) | `8.39 s` | `8.73 s` | `47792128 bytes` | checksum `-4720769113503374536`, output `179` | L1 trusted lower-bound elapsed/RSS win |
| DSPBench Log q2 1M x5 | real DSPBench common-log replay | checked scoped page-token | framework API / RSS win | `rift-checked-safezone-page-token` | 3 processes x 5 iterations | `8.79 s` total (`1758 ms/iter`) | `8.66 s` | `8.97 s` | `47611904 bytes` | checksum `-4720769113503374536`, output `179` | L1 checked page/window row is about 1% faster than heap and cuts RSS by about 85%; L2 remains the GC-tail interpretation source |
| GH Archive q1 fields 200k x3 | real GH Archive file-backed byte-slice JSON-lines | heap page/window fields | natural heap baseline | `heap-immix` | 3 processes x 3 iterations | `13.17 s` total | `12.72 s` | `21.68 s` | `265142272 bytes` | checksum `818187435331427579`, output `2600000` | L1 natural heap baseline; file-backed row includes gzip/JSON byte-slice parsing and three q1 iterations |
| GH Archive q1 fields 200k x3 | real GH Archive file-backed byte-slice JSON-lines | rooted scoped page/window fields | safe rooted baseline | `safezone-improved-32k` | 3 processes x 3 iterations | `13.10 s` total | `12.91 s` | `41.22 s` | `101466112 bytes` | checksum `818187435331427579`, output `2600000` | L1 rooted scoped row is a near-tie elapsed/RSS win; large max real time shows external file-backed noise |
| GH Archive q1 fields 200k x3 | real GH Archive file-backed byte-slice JSON-lines | trusted streaming page/window fields | unsafe/trusted lower bound | `rift-trusted-streaming` | 3 processes x 3 iterations | `12.81 s` total | `12.69 s` | `17.28 s` | `101351424 bytes` | checksum `818187435331427579`, output `2600000` | L1 trusted lower-bound modest elapsed/RSS win |
| GH Archive q1 fields 200k x3 | real GH Archive file-backed byte-slice JSON-lines | checked scoped page-token | framework API / RSS win | `rift-checked-safezone-page-token` | 3 processes x 3 iterations | `12.89 s` total | `12.79 s` | `18.21 s` | `101416960 bytes` | checksum `818187435331427579`, output `2600000` | L1 checked page-token modest elapsed win over heap and about 62% lower RSS; L2 remains the GC interpretation source |
| GH Archive q2 repo window 200k x3 | real GH Archive file-backed byte-slice JSON-lines | heap page/window repo aggregation | natural heap baseline | `heap-immix` | 3 processes x 3 iterations | `13.18 s` total | `13.12 s` | `18.70 s` | `244039680 bytes` | checksum `3318970041429315053`, output `31794` | L1 natural heap baseline; file-backed row includes gzip/JSON byte-slice parsing and three q2 iterations |
| GH Archive q2 repo window 200k x3 | real GH Archive file-backed byte-slice JSON-lines | rooted scoped page/window repo aggregation | safe rooted baseline | `safezone-improved-32k` | 3 processes x 3 iterations | `12.90 s` total | `12.78 s` | `16.97 s` | `101892096 bytes` | checksum `3318970041429315053`, output `31794` | L1 rooted scoped modest elapsed/RSS win |
| GH Archive q2 repo window 200k x3 | real GH Archive file-backed byte-slice JSON-lines | trusted streaming page/window repo aggregation | unsafe/trusted lower bound | `rift-trusted-streaming` | 3 processes x 3 iterations | `12.79 s` total | `12.08 s` | `258.37 s` | `101826560 bytes` | checksum `3318970041429315053`, output `31794` | L1 trusted lower-bound modest elapsed/RSS win; max real time includes one external wall-clock outlier with normal CPU time |
| GH Archive q2 repo window 200k x3 | real GH Archive file-backed byte-slice JSON-lines | checked scoped page-token | framework API / RSS win | `rift-checked-safezone-page-token` | 3 processes x 3 iterations | `12.87 s` total | `12.53 s` | `14.72 s` | `101859328 bytes` | checksum `3318970041429315053`, output `31794` | L1 checked page-token modest elapsed win over heap and about 58% lower RSS; L2 remains the GC interpretation source |
| NEXMark q3 1M x20 | Beam-default generated methodology | heap stream/window records | natural heap baseline | `heap-immix` | 3 processes x 20 iterations | `6.18 s` total (`309 ms/iter`) | `6.15 s` | `6.24 s` | `75153408 bytes` | checksum `-1870509861264400004`, output `98266` | L1 generated-methodology heap baseline |
| NEXMark q3 1M x20 | Beam-default generated methodology | rooted scoped stream/window records | safe rooted baseline | `safezone-improved` | 3 processes x 20 iterations | `6.38 s` total (`319 ms/iter`) | `6.37 s` | `6.47 s` | `9814016 bytes` | checksum `-1870509861264400004`, output `98266` | L1 rooted scoped RSS win but elapsed loss |
| NEXMark q3 1M x20 | Beam-default generated methodology | checked stream/window records | framework API win | `rift-checked` | 3 processes x 20 iterations | `5.86 s` total (`293 ms/iter`) | `5.85 s` | `5.93 s` | `9551872 bytes` | checksum `-1870509861264400004`, output `98266` | L1 checked generated-methodology win over heap and rooted scoped baseline |
| NEXMark q8 1M x20 | Beam-default generated methodology | heap stream/window join | natural heap baseline | `heap-immix` | 3 processes x 20 iterations | `9.54 s` total (`477 ms/iter`) | `9.52 s` | `9.58 s` | `75153408 bytes` | checksum `-2856281405942686288`, output `199000` | L1 generated-methodology heap baseline |
| NEXMark q8 1M x20 | Beam-default generated methodology | rooted scoped stream/window join | safe rooted baseline | `safezone-improved` | 3 processes x 20 iterations | `10.13 s` total (`507 ms/iter`) | `9.98 s` | `10.19 s` | `10403840 bytes` | checksum `-2856281405942686288`, output `199000` | L1 rooted scoped RSS win but elapsed loss |
| NEXMark q8 1M x20 | Beam-default generated methodology | checked stream/window join | framework API win | `rift-checked` | 3 processes x 20 iterations | `9.21 s` total (`461 ms/iter`) | `9.07 s` | `9.22 s` | `10223616 bytes` | checksum `-2856281405942686288`, output `199000` | L1 checked modest elapsed/RSS win |
| NEXMark q9 1M x20 | Beam-default generated methodology | heap winning-bid stream | natural heap baseline | `heap-immix` | 3 processes x 20 iterations | `16.27 s` total (`814 ms/iter`) | `16.25 s` | `16.35 s` | `146718720 bytes` | checksum `-367213413844887517`, output `922` | L1 generated-methodology heap baseline |
| NEXMark q9 1M x20 | Beam-default generated methodology | rooted scoped winning-bid stream | safe rooted baseline | `safezone-improved` | 3 processes x 20 iterations | `18.10 s` total (`905 ms/iter`) | `18.08 s` | `18.16 s` | `13893632 bytes` | checksum `-367213413844887517`, output `922` | L1 rooted scoped RSS win but elapsed loss |
| NEXMark q9 1M x20 | Beam-default generated methodology | checked winning-bid stream | framework API win | `rift-checked` | 3 processes x 20 iterations | `15.03 s` total (`752 ms/iter`) | `14.94 s` | `15.28 s` | `13156352 bytes` | checksum `-367213413844887517`, output `922` | L1 strongest selected NEXMark checked win |
| NEXMark q11 1M x20 | Beam-default generated methodology | heap session stream | natural heap baseline | `heap-immix` | 3 processes x 20 iterations | `4.47 s` total (`224 ms/iter`) | `4.41 s` | `4.51 s` | `75153408 bytes` | checksum `-6797588007755916917`, output `250197` | L1 generated-methodology heap baseline |
| NEXMark q11 1M x20 | Beam-default generated methodology | rooted scoped session stream | safe rooted baseline | `safezone-improved` | 3 processes x 20 iterations | `5.11 s` total (`256 ms/iter`) | `4.94 s` | `5.13 s` | `15253504 bytes` | checksum `-6797588007755916917`, output `250197` | L1 rooted scoped RSS win but elapsed loss |
| NEXMark q11 1M x20 | Beam-default generated methodology | checked session stream | framework API win | `rift-checked` | 3 processes x 20 iterations | `4.36 s` total (`218 ms/iter`) | `4.27 s` | `4.36 s` | `14172160 bytes` | checksum `-6797588007755916917`, output `250197` | L1 checked modest elapsed/RSS win |
| Yak LiveJournal 50M x5 | real file-backed SNAP LiveJournal graph replay | heap linked epoch | natural heap baseline | `gc-heap` | 3 processes x 5 iterations | `18.79 s` total | `18.76 s` | `18.89 s` | `2772320256 bytes` | checksum `-6048644965681588176` | L1 clean file-backed total-process heap row; includes one gzipped input preload plus five 50M replays per process |
| Yak LiveJournal 50M x5 | real file-backed SNAP LiveJournal graph replay | scoped region epoch | safe rooted baseline | `region-scoped-rooted` | 3 processes x 5 iterations | `16.93 s` total | `16.91 s` | `16.94 s` | `611860480 bytes` | checksum `-6048644965681588176` | L1 clean rooted scoped-region row; same input/preload protocol |
| Yak LiveJournal 50M x5 | real file-backed SNAP LiveJournal graph replay | `RiftRegion.epoch` checked scoped | framework API win | `checked-epoch-scoped` | 3 processes x 5 iterations | `16.12 s` total | `16.03 s` | `16.16 s` | `611893248 bytes` | checksum `-6048644965681588176` | L1 clean real-input checked epoch win; total process row still includes input preload |
| Common Crawl-shaped q1 1M | generated WET-shaped stressor | heap page/token stream | natural heap baseline | `heap-immix` | 3 processes x 1 iteration | `5.68 s` | `5.67 s` | `5.70 s` | `408502272 bytes` | checksum `-3166891223384968696`, output `137000000` | L1 clean generated object-pressure baseline, not real-input proof |
| Common Crawl-shaped q1 1M | generated WET-shaped stressor | scoped page/token stream | safe rooted baseline | `safezone-improved-32k` | 3 processes x 1 iteration | `5.42 s` | `5.40 s` | `5.45 s` | `74334208 bytes` | checksum `-3166891223384968696`, output `137000000` | L1 clean rooted scoped-region baseline |
| Common Crawl-shaped q1 1M | generated WET-shaped stressor | checked page-token stream | framework API win | `rift-checked-page-token` | 3 processes x 1 iteration | `4.02 s` | `4.00 s` | `4.10 s` | `63176704 bytes` | checksum `-3166891223384968696`, output `137000000` | L1 clean checked page-token win over heap and rooted scoped baseline |
| Common Crawl-shaped q1 1M | generated WET-shaped stressor | checked scoped page-token | framework API win | `rift-checked-safezone-page-token` | 3 processes x 1 iteration | `4.51 s` | `4.49 s` | `4.56 s` | `63307776 bytes` | checksum `-3166891223384968696`, output `137000000` | L1 clean checked scoped page-token win over heap/rooted, but slower than checked stream page-token |
| Common Crawl-shaped q2 1M | generated WET-shaped stressor | heap page/window stream | natural heap baseline | `heap-immix` | 3 processes x 1 iteration | `5.53 s` | `5.52 s` | `5.54 s` | `408502272 bytes` | checksum `1076064953308107199`, output `929230` | L1 clean generated object-pressure baseline, not real-input proof |
| Common Crawl-shaped q2 1M | generated WET-shaped stressor | scoped page/window stream | safe rooted baseline | `safezone-improved-32k` | 3 processes x 1 iteration | `5.39 s` | `5.35 s` | `5.47 s` | `74334208 bytes` | checksum `1076064953308107199`, output `929230` | L1 clean rooted scoped-region baseline |
| Common Crawl-shaped q2 1M | generated WET-shaped stressor | checked page-token stream | framework API win | `rift-checked-page-token` | 3 processes x 1 iteration | `4.16 s` | `4.15 s` | `4.20 s` | `63176704 bytes` | checksum `1076064953308107199`, output `929230` | L1 clean checked page-token win over heap and rooted scoped baseline |
| Common Crawl-shaped q2 1M | generated WET-shaped stressor | checked scoped page-token | framework API win | `rift-checked-safezone-page-token` | 3 processes x 1 iteration | `4.75 s` | `4.75 s` | `4.76 s` | `63324160 bytes` | checksum `1076064953308107199`, output `929230` | L1 clean checked scoped page-token win over heap/rooted, but slower than checked stream page-token |
| ReML-shaped msort x20 | local Scala Native port | heap list/sort | natural heap baseline | `gc-heap` | 3 processes x 20 iterations | `2.46 s` total (`123.0 ms/iter`) | `2.46 s` | `2.47 s` | `21250048 bytes` | checksum `-6417646918322825706` | L1 clean local port baseline |
| ReML-shaped msort x20 | local Scala Native port | scoped region list/sort | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `2.31 s` total (`115.5 ms/iter`) | `2.31 s` | `2.32 s` | `10305536 bytes` | checksum `-6417646918322825706` | L1 clean rooted scoped-region baseline |
| ReML-shaped msort x20 | local Scala Native port | checked region list/sort | framework API win | `checked-region-stream` | 3 processes x 20 iterations | `2.06 s` total (`103.0 ms/iter`) | `2.05 s` | `2.06 s` | `10289152 bytes` | checksum `-6417646918322825706` | L1 clean checked stream win over heap and rooted scoped baseline |
| ReML-shaped msort-r x20 | local Scala Native port | heap reverse/sort | natural heap baseline | `gc-heap` | 3 processes x 20 iterations | `2.25 s` total (`112.5 ms/iter`) | `2.25 s` | `2.26 s` | `39141376 bytes` | checksum `5175249867721542949` | L1 clean local port baseline |
| ReML-shaped msort-r x20 | local Scala Native port | scoped region reverse/sort | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `2.20 s` total (`110.0 ms/iter`) | `2.20 s` | `2.21 s` | `14778368 bytes` | checksum `5175249867721542949` | L1 clean rooted scoped-region baseline |
| ReML-shaped msort-r x20 | local Scala Native port | checked region reverse/sort | framework API win | `checked-region-stream` | 3 processes x 20 iterations | `2.05 s` total (`102.5 ms/iter`) | `2.05 s` | `2.07 s` | `10289152 bytes` | checksum `5175249867721542949` | L1 clean checked stream win over heap and rooted scoped baseline |
| ReML-shaped ratio x20 | local Scala Native port | heap ratio objects | natural heap baseline | `gc-heap` | 3 processes x 20 iterations | `0.93 s` total (`46.5 ms/iter`) | `0.92 s` | `0.94 s` | `79888384 bytes` | checksum `499038617794598401` | L1 clean local port baseline |
| ReML-shaped ratio x20 | local Scala Native port | scoped ratio objects | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `0.93 s` total (`46.5 ms/iter`) | `0.92 s` | `0.95 s` | `15925248 bytes` | checksum `499038617794598401` | L1 clean RSS win, elapsed near-tie |
| ReML-shaped ratio x20 | local Scala Native port | checked scoped ratio objects | framework API/RSS win | `checked-region-scoped` | 3 processes x 20 iterations | `0.91 s` total (`45.5 ms/iter`) | `0.90 s` | `0.93 s` | `15892480 bytes` | checksum `499038617794598401` | L1 clean modest elapsed win and strong RSS win |
| ReML-shaped logic x20 | local Scala Native port | heap symbolic node chain | natural heap baseline | `gc-heap` | 3 processes x 20 iterations | `1.27 s` total (`63.5 ms/iter`) | `1.26 s` | `1.29 s` | `7880704 bytes` | checksum `-8976243430947238143` | L1 local Tier 2 heap baseline |
| ReML-shaped logic x20 | local Scala Native port | rooted scoped symbolic node chain | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `1.71 s` total (`85.5 ms/iter`) | `1.68 s` | `1.73 s` | `65732608 bytes` | checksum `-8976243430947238143` | L1 negative scoped row: slower and higher RSS for this whole-region chain |
| ReML-shaped logic x20 | local Scala Native port | checked stream symbolic node chain | checked local port control | `checked-region-stream` | 3 processes x 20 iterations | `1.27 s` total (`63.5 ms/iter`) | `1.25 s` | `1.28 s` | `65601536 bytes` | checksum `-8976243430947238143` | L1 elapsed tie but large RSS regression; not a headline win |
| ReML-shaped logic x20 | local Scala Native port | checked scoped symbolic node chain | checked local port control | `checked-region-scoped` | 3 processes x 20 iterations | `1.54 s` total (`77.0 ms/iter`) | `1.53 s` | `1.57 s` | `65732608 bytes` | checksum `-8976243430947238143` | L1 checked scoped negative/control row |
| ReML-shaped ray x20 | local Scala Native port | heap ray/sphere/hit objects | natural heap baseline | `gc-heap` | 3 processes x 20 iterations | `0.75 s` total (`37.5 ms/iter`) | `0.74 s` | `0.75 s` | `4145152 bytes` | checksum `8305719071369304666` | L1 local Tier 2 compute-heavy baseline |
| ReML-shaped ray x20 | local Scala Native port | rooted scoped ray/sphere/hit objects | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `0.74 s` total (`37.0 ms/iter`) | `0.74 s` | `0.78 s` | `4096000 bytes` | checksum `8305719071369304666` | L1 near-tie / tiny RSS row; ceiling/control |
| ReML-shaped ray x20 | local Scala Native port | checked stream ray/sphere/hit objects | checked local port control | `checked-region-stream` | 3 processes x 20 iterations | `0.75 s` total (`37.5 ms/iter`) | `0.74 s` | `0.76 s` | `4096000 bytes` | checksum `8305719071369304666` | L1 near-tie; no GC-heavy claim |
| ReML-shaped ray x20 | local Scala Native port | checked scoped ray/sphere/hit objects | checked local port control | `checked-region-scoped` | 3 processes x 20 iterations | `0.75 s` total (`37.5 ms/iter`) | `0.74 s` | `0.76 s` | `4079616 bytes` | checksum `8305719071369304666` | L1 near-tie / tiny RSS row; ceiling/control |
| ReML-shaped tsp x20 | local Scala Native port | heap nearest-neighbor tour nodes | natural heap baseline | `gc-heap` | 3 processes x 20 iterations | `3.40 s` total (`170.0 ms/iter`) | `3.39 s` | `3.71 s` | `7913472 bytes` | checksum `-8586201700104072648` | L1 local Tier 2 heap baseline |
| ReML-shaped tsp x20 | local Scala Native port | rooted scoped nearest-neighbor tour nodes | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `3.54 s` total (`177.0 ms/iter`) | `3.52 s` | `3.63 s` | `5947392 bytes` | checksum `-8586201700104072648` | L1 RSS win but elapsed loss |
| ReML-shaped tsp x20 | local Scala Native port | checked stream nearest-neighbor tour nodes | checked local port control | `checked-region-stream` | 3 processes x 20 iterations | `3.49 s` total (`174.5 ms/iter`) | `3.47 s` | `3.51 s` | `5881856 bytes` | checksum `-8586201700104072648` | L1 RSS win with small elapsed loss; not a throughput claim |
| ReML-shaped tsp x20 | local Scala Native port | checked scoped nearest-neighbor tour nodes | checked local port control | `checked-region-scoped` | 3 processes x 20 iterations | `3.48 s` total (`174.0 ms/iter`) | `3.44 s` | `3.54 s` | `5881856 bytes` | checksum `-8586201700104072648` | L1 RSS win with small elapsed loss; not a throughput claim |
| retained epoch smoke | synthetic focused matrix | retained epoch/drop-anchor | retained-object memory-management | `heap-epoch-retained-no-traverse` | 1 | external runner smoke only | external runner smoke only | external runner smoke only | `3801088 bytes` | checksum `-2003786531644562922`, output `1873` | L1 smoke only, not headline |
| retained epoch smoke | synthetic focused matrix | retained epoch/drop-anchor | retained-object memory-management | `checked-scoped-epoch-retained-no-traverse` | 1 | external runner smoke only | external runner smoke only | external runner smoke only | `3768320 bytes` | checksum `-2003786531644562922`, output `1873` | L1 smoke only, not headline |

1M x20 command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_FINAL_CLEAN=1 \
RETAINED_EPOCH_RECORDS=1000000 \
RETAINED_EPOCH_RECORDS_PER_EPOCH=25000 \
RETAINED_EPOCH_BENCHMARK_RUNS=20 \
RETAINED_EPOCH_WARMUPS=0 \
RETAINED_EPOCH_MODES="heap-epoch-retained-no-traverse checked-epoch-retained-no-traverse checked-scoped-epoch-retained-no-traverse" \
RETAINED_EPOCH_OUTPUT_DIR=/tmp/rift-l1-retained-epoch-1m-x20-clean-f1aa55484 \
zsh sandbox/run_retained_epoch_reclaim_matrix.sh
```

Dataflow SELECT/AGGREGATE/JOIN 1M x20 command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for op in select aggregate join; do
  for i in 1 2 3; do
    RIFT_FINAL_CLEAN=1 \
    DATAFLOW_BUILD=0 \
    DATAFLOW_EPOCHS=10 \
    DATAFLOW_DOCS_PER_EPOCH=100000 \
    DATAFLOW_BENCHMARK_RUNS=20 \
    DATAFLOW_WARMUPS=0 \
    DATAFLOW_OPERATOR=${op} \
    DATAFLOW_MODES="gc-heap region-scoped-rooted checked-epoch-scoped" \
    DATAFLOW_OUTPUT_DIR=/tmp/rift-l1-dataflow-${op}-1m-x20-7573d7577-r${i} \
    zsh sandbox/run_dataflow_region_instrumented_matrix.sh
  done
done
```

Yak LiveJournal 50M x5 command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  YAK_BUILD=0 \
  YAK_WORKLOAD=graphreal \
  YAK_GRAPH_INPUT=/Users/siyaoliu/rift/cache/benchmark-data/yak/snap/soc-LiveJournal1.txt.gz \
  YAK_GRAPH_INPUT_EDGES=50000000 \
  YAK_GRAPH_INPUT_VERTICES=1000000 \
  YAK_GRAPH_INPUT_EDGES_PER_EPOCH=5000000 \
  YAK_EPOCHS=10 \
  YAK_BENCHMARK_RUNS=5 \
  YAK_WARMUPS=0 \
  YAK_MODES="gc-heap region-scoped-rooted checked-epoch-scoped" \
  YAK_OUTPUT_DIR=/tmp/rift-l1-yak-livejournal-50m-x5-7573d7577-r${i} \
  zsh sandbox/run_yak_region_instrumented_matrix.sh
done
```

Common Crawl-shaped q1/q2 1M command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  COMMON_CRAWL_WET_BUILD=0 \
  COMMON_CRAWL_WET_PAGES=1000000 \
  COMMON_CRAWL_WET_BENCHMARK_RUNS=1 \
  COMMON_CRAWL_WET_WARMUPS=0 \
  COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window" \
  COMMON_CRAWL_WET_MODES="heap-immix safezone-improved-32k rift-checked-page-token rift-checked-safezone-page-token" \
  COMMON_CRAWL_WET_OUTPUT_DIR=/tmp/rift-l1-common-crawl-shaped-q1q2-1m-7573d7577-r${i} \
  zsh sandbox/run_common_crawl_wet_matrix.sh
done
```

ReML-shaped Tier 1 x20 command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  REML_BUILD=0 \
  REML_BENCHMARK_RUNS=20 \
  REML_WARMUPS=0 \
  REML_WORKLOADS="fib37 tak mandel msort msort-r life fft ratio" \
  REML_MODES="gc-heap region-scoped-rooted checked-region-stream checked-region-scoped" \
  REML_OUTPUT_DIR=/tmp/rift-l1-reml-tier1-x20-7573d7577-r${i} \
  zsh sandbox/run_reml_region_matrix.sh
done
```

ReML-shaped Tier 2 x20 command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  REML_BUILD=0 \
  REML_OUTPUT_DIR=/tmp/reml-tier2-l1-2026-05-11-r${i} \
  REML_WORKLOADS="logic ray tsp" \
  REML_MODES="gc-heap region-scoped-rooted checked-region-stream checked-region-scoped" \
  REML_LOGIC_ITERATIONS=200000 \
  REML_RAY_RAYS=50000 \
  REML_BENCHMARK_RUNS=20 \
  REML_WARMUPS=0 \
  zsh sandbox/run_reml_region_matrix.sh
done
```

ReML-shaped controls not listed as headline rows:

- `fib37` is a near-tie at this scale: heap `2.40 s`, checked stream `2.41 s`.
- `life` is a near-tie: heap `0.69 s`, best checked/rooted rows `0.68 s`.
- `tak`, `fft`, and `mandel` are too short under this configuration for
  useful external timing claims; keep them as correctness/configuration
  controls unless scaled up.

StreamFlex direct-epoch throughput command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  STREAMFLEX_BUILD=0 \
  STREAMFLEX_WORKLOAD=throughput \
  STREAMFLEX_EVENTS=200000 \
  STREAMFLEX_BENCHMARK_RUNS=20 \
  STREAMFLEX_WARMUPS=0 \
  STREAMFLEX_MODES="heap improved-safezone rift-checked-safezone-direct-epoch" \
  STREAMFLEX_OUTPUT_DIR=/tmp/rift-l1-streamflex-throughput-direct-epoch-200k-x20-c5bbc498f-r${i} \
  zsh sandbox/run_streamflex_region_instrumented_matrix.sh
done
```

StreamFlex direct-epoch latency command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  STREAMFLEX_BUILD=0 \
  STREAMFLEX_WORKLOAD=latency \
  STREAMFLEX_LATENCY_EVENTS=10000 \
  STREAMFLEX_BENCHMARK_RUNS=20 \
  STREAMFLEX_WARMUPS=0 \
  STREAMFLEX_MODES="heap improved-safezone rift-checked-safezone-direct-epoch" \
  STREAMFLEX_OUTPUT_DIR=/tmp/rift-l1-streamflex-latency-direct-epoch-10k-x20-c5bbc498f-r${i} \
  zsh sandbox/run_streamflex_region_instrumented_matrix.sh
done
```

Stancu transaction command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  STANCU_BUILD=0 \
  STANCU_TRANSACTIONS=200000 \
  STANCU_BENCHMARK_RUNS=20 \
  STANCU_WARMUPS=0 \
  STANCU_MODES="heap improved-safezone rift-checked-safezone-direct-epoch" \
  STANCU_OUTPUT_DIR=/tmp/rift-l1-stancu-200k-x20-c5bbc498f-r${i} \
  zsh sandbox/run_stancu_region_instrumented_matrix.sh
done
```

SPECjbb2005-workload port command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  SPECJBB_BUILD=0 \
  SPECJBB_WAREHOUSES=8 \
  SPECJBB_ITERATIONS_PER_WAREHOUSE=100000 \
  SPECJBB_BENCHMARK_RUNS=20 \
  SPECJBB_WARMUPS=0 \
  SPECJBB_MODES="gc-heap region-scoped-rooted checked-epoch-scoped" \
  SPECJBB_OUTPUT_DIR=/tmp/rift-l1-specjbb-8w-x20-678a6eb41-r${i} \
  zsh sandbox/run_specjbb2005_port_matrix.sh
done
```

LogHub real HDFS top-template command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  LOGHUB_TOP_BUILD=0 \
  LOGHUB_TOP_INPUT_MODE=file-backed \
  LOGHUB_TOP_INPUT=/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1/HDFS.log \
  LOGHUB_TOP_LINES=1000000 \
  LOGHUB_TOP_LINES_PER_EPOCH=25000 \
  LOGHUB_TOP_BENCHMARK_RUNS=20 \
  LOGHUB_TOP_WARMUPS=0 \
  LOGHUB_TOP_MODES="heap-retained-drop-anchor checked-scoped-epoch-retained-no-traverse checked-scoped-epoch-topk-retained-no-traverse" \
  LOGHUB_TOP_OUTPUT_DIR=/tmp/rift-l1-loghub-topk-hotpath-hdfs-1m-x20-bc9fd5979-r${i} \
  zsh sandbox/run_loghub_top_templates_matrix.sh
done
```

LogHub real HDFS top-template larger-scale command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  LOGHUB_TOP_BUILD=0 \
  LOGHUB_TOP_INPUT_MODE=file-backed \
  LOGHUB_TOP_INPUT=/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1/HDFS.log \
  LOGHUB_TOP_LINES=5000000 \
  LOGHUB_TOP_LINES_PER_EPOCH=25000 \
  LOGHUB_TOP_BENCHMARK_RUNS=5 \
  LOGHUB_TOP_WARMUPS=0 \
  LOGHUB_TOP_MODES="heap-retained-drop-anchor checked-scoped-epoch-topk-retained-no-traverse" \
  LOGHUB_TOP_OUTPUT_DIR=/tmp/rift-l1-loghub-topk-hdfs-5m-x5-0773d4c17-r${i} \
  zsh sandbox/run_loghub_top_templates_matrix.sh
done
```

Matching L2 interpretation command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
LOGHUB_TOP_BUILD=0 \
LOGHUB_TOP_INPUT_MODE=file-backed \
LOGHUB_TOP_INPUT=/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1/HDFS.log \
LOGHUB_TOP_LINES=5000000 \
LOGHUB_TOP_LINES_PER_EPOCH=25000 \
LOGHUB_TOP_BENCHMARK_RUNS=3 \
LOGHUB_TOP_WARMUPS=1 \
LOGHUB_TOP_MODES="heap-retained-drop-anchor checked-scoped-epoch-topk-retained-no-traverse" \
LOGHUB_TOP_OUTPUT_DIR=/tmp/rift-l2-loghub-topk-hdfs-5m-0773d4c17 \
zsh sandbox/run_loghub_top_templates_matrix.sh
```

GH Archive two-hour byte-slice command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  GITHUB_ARCHIVE_BUILD=0 \
  GITHUB_ARCHIVE_INPUTS="/Users/siyaoliu/rift/cache/benchmark-data/gharchive/2026-04-01-0.json.gz,/Users/siyaoliu/rift/cache/benchmark-data/gharchive/2026-04-01-1.json.gz" \
  GITHUB_ARCHIVE_INPUT_MODE=file-backed \
  GITHUB_ARCHIVE_FILE_PARSER=byte-slice \
  GITHUB_ARCHIVE_EVENTS=200000 \
  GITHUB_ARCHIVE_EVENTS_PER_BUCKET=25000 \
  GITHUB_ARCHIVE_BENCHMARK_RUNS=3 \
  GITHUB_ARCHIVE_WARMUPS=0 \
  GITHUB_ARCHIVE_QUERIES="q1-fields q2-repo-window" \
  GITHUB_ARCHIVE_MODES="heap-immix safezone-improved-32k rift-trusted-streaming rift-checked-safezone-page-token" \
  GITHUB_ARCHIVE_OUTPUT_DIR=/tmp/rift-l1-gharchive-byte-200k-x3-54bf38c45-r${i} \
  zsh sandbox/run_github_archive_region_matrix.sh
done
```

GH Archive generated/preloaded retained q2 command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  GITHUB_ARCHIVE_BUILD=0 \
  GITHUB_ARCHIVE_EVENTS=1000000 \
  GITHUB_ARCHIVE_EVENTS_PER_BUCKET=25000 \
  GITHUB_ARCHIVE_BENCHMARK_RUNS=20 \
  GITHUB_ARCHIVE_WARMUPS=0 \
  GITHUB_ARCHIVE_INPUT_MODE=preloaded \
  GITHUB_ARCHIVE_QUERIES="q2-repo-window" \
  GITHUB_ARCHIVE_MODES="heap-direct-summary-only heap-epoch-retained-no-traverse checked-epoch-retained-no-traverse checked-scoped-epoch-retained-no-traverse" \
  GITHUB_ARCHIVE_OUTPUT_DIR=/tmp/rift-l1-gharchive-retained-q2-1m-x20-36bbfa9cd-r${i} \
  zsh sandbox/run_github_archive_region_matrix.sh
done
```

GH Archive generated/preloaded direct-summary counterpart command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  GITHUB_ARCHIVE_BUILD=0 \
  GITHUB_ARCHIVE_EVENTS=1000000 \
  GITHUB_ARCHIVE_EVENTS_PER_BUCKET=25000 \
  GITHUB_ARCHIVE_BENCHMARK_RUNS=20 \
  GITHUB_ARCHIVE_WARMUPS=0 \
  GITHUB_ARCHIVE_INPUT_MODE=preloaded \
  GITHUB_ARCHIVE_QUERIES="q2-repo-window" \
  GITHUB_ARCHIVE_MODES="heap-direct-summary-only checked-epoch-stream checked-epoch-scoped" \
  GITHUB_ARCHIVE_OUTPUT_DIR=/tmp/rift-l1-gharchive-direct-summary-q2-1m-x20-b9ac4a647-r${i} \
  zsh sandbox/run_github_archive_region_matrix.sh
done
```

DSPBench generated/indexable retained q2 command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  DSPBENCH_BUILD=0 \
  DSPBENCH_EVENTS=1000000 \
  DSPBENCH_EVENTS_PER_BUCKET=25000 \
  DSPBENCH_BENCHMARK_RUNS=20 \
  DSPBENCH_WARMUPS=0 \
  DSPBENCH_INPUT_MODE=generated \
  DSPBENCH_QUERIES="fraud-q2-alert-window" \
  DSPBENCH_MODES="heap-epoch-retained-no-traverse checked-epoch-retained-no-traverse checked-scoped-epoch-retained-no-traverse" \
  DSPBENCH_OUTPUT_DIR=/tmp/rift-l1-dspbench-retained-fraud-q2-1m-x20-0773d4c17-r${i} \
  zsh sandbox/run_dspbench_region_matrix.sh
done
```

LogHub generated/indexable retained q2/q3 command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  LOGHUB_BUILD=0 \
  LOGHUB_LINES=1000000 \
  LOGHUB_LINES_PER_BUCKET=25000 \
  LOGHUB_BENCHMARK_RUNS=20 \
  LOGHUB_WARMUPS=0 \
  LOGHUB_INPUT_MODE=generated \
  LOGHUB_QUERIES="q2-window-counts q3-template-session" \
  LOGHUB_MODES="heap-epoch-retained-no-traverse checked-epoch-retained-no-traverse checked-scoped-epoch-retained-no-traverse" \
  LOGHUB_OUTPUT_DIR=/tmp/rift-l1-loghub-retained-q2q3-1m-x20-0773d4c17-r${i} \
  zsh sandbox/run_loghub_region_matrix.sh
done
```

DSPBench generated/indexable direct-summary counterpart command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  DSPBENCH_BUILD=0 \
  DSPBENCH_EVENTS=1000000 \
  DSPBENCH_EVENTS_PER_BUCKET=25000 \
  DSPBENCH_BENCHMARK_RUNS=20 \
  DSPBENCH_WARMUPS=0 \
  DSPBENCH_INPUT_MODE=generated \
  DSPBENCH_QUERIES="fraud-q2-alert-window log-q2-window" \
  DSPBENCH_MODES="heap-direct-summary-only checked-epoch-stream checked-epoch-scoped" \
  DSPBENCH_OUTPUT_DIR=/tmp/rift-l1-dspbench-direct-summary-q2-1m-x20-eea5894d5-r${i} \
  zsh sandbox/run_dspbench_region_matrix.sh
done
```

LogHub generated/indexable direct-summary counterpart command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
for i in 1 2 3; do
  RIFT_FINAL_CLEAN=1 \
  LOGHUB_BUILD=0 \
  LOGHUB_LINES=1000000 \
  LOGHUB_LINES_PER_BUCKET=25000 \
  LOGHUB_BENCHMARK_RUNS=20 \
  LOGHUB_WARMUPS=0 \
  LOGHUB_INPUT_MODE=generated \
  LOGHUB_QUERIES="q2-window-counts q3-template-session" \
  LOGHUB_MODES="heap-direct-summary-only checked-epoch-stream checked-epoch-scoped" \
  LOGHUB_OUTPUT_DIR=/tmp/rift-l1-loghub-direct-summary-q2q3-1m-x20-eea5894d5-r${i} \
  zsh sandbox/run_loghub_region_matrix.sh
done
```

Smoke command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_FINAL_CLEAN=1 \
RETAINED_EPOCH_RECORDS=2000 \
RETAINED_EPOCH_RECORDS_PER_EPOCH=500 \
RETAINED_EPOCH_BENCHMARK_RUNS=1 \
RETAINED_EPOCH_WARMUPS=0 \
RETAINED_EPOCH_MODES="heap-epoch-retained-no-traverse checked-scoped-epoch-retained-no-traverse" \
RETAINED_EPOCH_OUTPUT_DIR=/tmp/rift-final-clean-retained-smoke \
zsh sandbox/run_retained_epoch_reclaim_matrix.sh
```

## Cross-Check Requirement

Every L1 row must have a matching L2 row with the same input, mode, and
checksum/output count. If L1 and L2 elapsed differ materially, report the L1
elapsed as the headline value and use L2 only to explain GC/region behavior.
