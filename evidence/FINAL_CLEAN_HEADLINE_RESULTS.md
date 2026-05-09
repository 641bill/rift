# Final-Clean Headline Results

Date: 2026-05-09
Last updated: 2026-05-10 00:31 CEST

Status: L1 runner support exists for the first representative binaries. One
focused retained-epoch L1 row has been collected from clean child commit
`f1aa55484`, and Dataflow SELECT/AGGREGATE/JOIN representative L1 rows have
been collected from child `7573d7577`; the broader report-grade L1 headline
sweep is still pending.
Child `7573d7577` extends external timing/RSS summary support to Dataflow,
Yak, Common Crawl WET-shaped, and ReML runners; those rows are ready to collect
next.

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

The binaries print `RESULT ... measurement_level=L1 final_clean=1 ...` and
avoid internal timed-section stats.

## Required First Sweep

| Group | Representative rows | Reason |
|---|---|---|
| retained-object reclaim | focused retained 1M; GH Archive-shaped q2; LogHub q2/q3; DSPBench Fraud q2 | isolates heap GC reclaim versus region bulk close/reset |
| direct epoch | Yak LiveJournal 10M/50M; Dataflow SELECT/AGGREGATE/JOIN; StreamFlex throughput; Stancu/SPECjbb-style | user-facing `RiftRegion.epoch` evidence |
| page/window token | generated Common Crawl-shaped q1/q2; DSPBench Fraud/Log q2; LogHub HDFS q2 | page/window stream operator evidence |
| ReML/MLKit ports | `msort`, `msort-r`, `ratio`, plus `fib37`/`tak`/`mandel` controls | non-stream typed-region comparison axis |

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
