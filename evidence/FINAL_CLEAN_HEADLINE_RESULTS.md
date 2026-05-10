# Final-Clean Headline Results

Date: 2026-05-09
Last updated: 2026-05-10 16:05 CEST

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

The binaries print `RESULT ... measurement_level=L1 final_clean=1 ...` and
avoid internal timed-section stats.

## Required First Sweep

| Group | Representative rows | Reason |
|---|---|---|
| retained-object reclaim | focused retained 1M; GH Archive-shaped q2; LogHub q2/q3; DSPBench Fraud q2 | isolates heap GC reclaim versus region bulk close/reset |
| direct epoch | Yak LiveJournal 10M/50M; Dataflow SELECT/AGGREGATE/JOIN; StreamFlex throughput; Stancu/SPECjbb-style | user-facing `RiftRegion.epoch` evidence |
| page/window token | generated Common Crawl-shaped q1/q2; DSPBench Fraud/Log q2; LogHub HDFS q2 | page/window stream operator evidence |
| generated stream methodology | NEXMark q3/q8/q9/q11 | recognized generated Beam-default-style stream controls |
| ReML/MLKit ports | `msort`, `msort-r`, `ratio`, plus `fib37`/`tak`/`mandel` controls | non-stream typed-region comparison axis |
| StreamFlex | throughput and latency rows | prior-work latency/throughput axis |
| Stancu/SPECjbb-style | transaction rows | transaction-boundary region axis |
| retained top-k API | LogHub HDFS top templates | reusable `EpochTopKByKey` evidence |

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
| Dataflow SELECT 1M x20 | generated methodology | direct epoch / scoped region | framework API win | `gc-heap` | 3 processes x 20 iterations | `0.62 s` total (`31.0 ms/iter`) | `0.61 s` | `0.63 s` | `39288832 bytes` | checksum `131080080920` | L1 clean natural heap baseline |
| Dataflow SELECT 1M x20 | generated methodology | direct epoch / scoped region | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `0.46 s` total (`23.0 ms/iter`) | `0.46 s` | `0.48 s` | `7536640 bytes` | checksum `131080080920` | L1 clean rooted scoped-region baseline |
| Dataflow SELECT 1M x20 | generated methodology | `RiftRegion.epoch` checked scoped | framework API win | `checked-epoch-scoped` | 3 processes x 20 iterations | `0.38 s` total (`19.0 ms/iter`) | `0.38 s` | `0.39 s` | `7553024 bytes` | checksum `131080080920` | L1 clean checked epoch win over heap and rooted scoped baseline |
| Dataflow AGGREGATE 1M x20 | generated methodology | direct epoch / scoped region | framework API win | `gc-heap` | 3 processes x 20 iterations | `1.10 s` total (`55.0 ms/iter`) | `1.10 s` | `1.13 s` | `75890688 bytes` | checksum `163835709480` | L1 clean natural heap baseline |
| Dataflow AGGREGATE 1M x20 | generated methodology | direct epoch / scoped region | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `0.79 s` total (`39.5 ms/iter`) | `0.79 s` | `0.80 s` | `10829824 bytes` | checksum `163835709480` | L1 clean rooted scoped-region baseline |
| Dataflow AGGREGATE 1M x20 | generated methodology | `RiftRegion.epoch` checked scoped | framework API win | `checked-epoch-scoped` | 3 processes x 20 iterations | `0.69 s` total (`34.5 ms/iter`) | `0.69 s` | `0.70 s` | `10829824 bytes` | checksum `163835709480` | L1 clean checked epoch win over heap and rooted scoped baseline |
| Dataflow JOIN 1M x20 | generated methodology | direct epoch / scoped region | framework API win | `gc-heap` | 3 processes x 20 iterations | `0.55 s` total (`27.5 ms/iter`) | `0.55 s` | `0.55 s` | `75071488 bytes` | checksum `193232836790` | L1 clean natural heap baseline |
| Dataflow JOIN 1M x20 | generated methodology | direct epoch / scoped region | safe rooted baseline | `region-scoped-rooted` | 3 processes x 20 iterations | `0.46 s` total (`23.0 ms/iter`) | `0.46 s` | `0.46 s` | `7389184 bytes` | checksum `193232836790` | L1 clean rooted scoped-region baseline |
| Dataflow JOIN 1M x20 | generated methodology | `RiftRegion.epoch` checked scoped | framework API win | `checked-epoch-scoped` | 3 processes x 20 iterations | `0.39 s` total (`19.5 ms/iter`) | `0.39 s` | `0.39 s` | `7405568 bytes` | checksum `193232836790` | L1 clean checked epoch win over heap and rooted scoped baseline |
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
| LogHub top templates HDFS 1M x20 | real HDFS file-backed/preloaded replay | retained epoch/drop-anchor | retained-object memory-management | `heap-retained-drop-anchor` | 3 processes x 20 iterations | `5.46 s` total (`273.0 ms/iter`) | `5.43 s` | `5.47 s` | `205406208 bytes` | checksum `4142347521733569598`, output `1280` | L1 retained heap/drop-anchor control; process includes one HDFS input load plus 20 replays |
| LogHub top templates HDFS 1M x20 | real HDFS file-backed/preloaded replay | benchmark-local checked retained epoch | retained-object memory-management / lower bound | `checked-scoped-epoch-retained-no-traverse` | 3 processes x 20 iterations | `4.84 s` total (`242.0 ms/iter`) | `4.82 s` | `4.88 s` | `28262400 bytes` | checksum `4142347521733569598`, output `1280` | L1 checked retained lower-bound win over heap retained |
| LogHub top templates HDFS 1M x20 | real HDFS file-backed/preloaded replay | reusable checked `EpochTopKByKey` | framework API win | `checked-scoped-epoch-topk-retained-no-traverse` | 3 processes x 20 iterations | `5.05 s` total (`252.5 ms/iter`) | `5.05 s` | `5.08 s` | `28114944 bytes` | checksum `4142347521733569598`, output `1280` | L1 reusable checked top-k win over heap retained with much lower RSS; API overhead remains versus benchmark-local checked row |
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
  LOGHUB_TOP_OUTPUT_DIR=/tmp/rift-l1-loghub-top-hdfs-1m-x20-3598efe29-r${i} \
  zsh sandbox/run_loghub_top_templates_matrix.sh
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
