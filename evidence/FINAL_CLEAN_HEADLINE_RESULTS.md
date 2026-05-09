# Final-Clean Headline Results

Date: 2026-05-09
Last updated: 2026-05-09 23:55 CEST

Status: L1 runner support exists for the first representative binaries. One
tiny retained-epoch smoke has been collected; no report-grade L1 headline sweep
has been collected yet.

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

## L1 Table Template

Fill this table only from final-clean runs.

| Benchmark | Input type | API/topology | Comparison class | Mode | Runs | Median real time | Min real time | Max real time | Max RSS | Checksum/output | Claim |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| retained epoch smoke | synthetic focused matrix | retained epoch/drop-anchor | retained-object memory-management | `heap-epoch-retained-no-traverse` | 1 | external runner smoke only | external runner smoke only | external runner smoke only | `3801088 bytes` | checksum `-2003786531644562922`, output `1873` | L1 smoke only, not headline |
| retained epoch smoke | synthetic focused matrix | retained epoch/drop-anchor | retained-object memory-management | `checked-scoped-epoch-retained-no-traverse` | 1 | external runner smoke only | external runner smoke only | external runner smoke only | `3768320 bytes` | checksum `-2003786531644562922`, output `1873` | L1 smoke only, not headline |

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
