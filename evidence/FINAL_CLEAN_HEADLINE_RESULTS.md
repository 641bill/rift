# Final-Clean Headline Results

Date: 2026-05-09
Last updated: 2026-05-10 01:10 CEST

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
same support to StreamFlex and Stancu; those rows are ready to collect next.

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

The binaries print `RESULT ... measurement_level=L1 final_clean=1 ...` and
avoid internal timed-section stats.

## Required First Sweep

| Group | Representative rows | Reason |
|---|---|---|
| retained-object reclaim | focused retained 1M; GH Archive-shaped q2; LogHub q2/q3; DSPBench Fraud q2 | isolates heap GC reclaim versus region bulk close/reset |
| direct epoch | Yak LiveJournal 10M/50M; Dataflow SELECT/AGGREGATE/JOIN; StreamFlex throughput; Stancu/SPECjbb-style | user-facing `RiftRegion.epoch` evidence |
| page/window token | generated Common Crawl-shaped q1/q2; DSPBench Fraud/Log q2; LogHub HDFS q2 | page/window stream operator evidence |
| ReML/MLKit ports | `msort`, `msort-r`, `ratio`, plus `fib37`/`tak`/`mandel` controls | non-stream typed-region comparison axis |
| StreamFlex | throughput and latency rows | prior-work latency/throughput axis |
| Stancu/SPECjbb-style | transaction rows | transaction-boundary region axis |

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
