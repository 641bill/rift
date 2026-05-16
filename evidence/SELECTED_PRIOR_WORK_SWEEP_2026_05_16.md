# Selected Prior-Work-Style Sweep, 2026-05-16

Date: 2026-05-16
Last updated: 2026-05-16 13:10 CEST

Status: clean committed-tree normalized selected sweep for prior-work-style
presentation rows. This supersedes the older parent `prior` suite for
presentation because it runs the current framework/API matrices:
Broom retained dataflow, Dataflow direct epoch/page-token, StreamFlexDesign,
Yak local direct-epoch workloads, and the SPECjbb2005 workload port.

Run command:

```sh
RIFT_EVAL_SUITES=selected-prior \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_RUNS=3 \
RIFT_EVAL_RUN_ROOT=/private/tmp/rift-eval-selected-prior-headline-20260516 \
bash scripts/run-performance-evaluation.sh
```

Clean commits:

- parent: `14038d3`
- child: `15c4c39ac`

Run output:

- root: `/private/tmp/rift-eval-selected-prior-headline-20260516`
- summaries:
  - `/private/tmp/rift-eval-selected-prior-headline-20260516/summaries/broom-retained-dataflow/summary.tsv`
  - `/private/tmp/rift-eval-selected-prior-headline-20260516/summaries/streamflex-design/summary.tsv`
  - `/private/tmp/rift-eval-selected-prior-headline-20260516/summaries/yak-wordcount/summary.tsv`
  - `/private/tmp/rift-eval-selected-prior-headline-20260516/summaries/yak-graphstep/summary.tsv`
  - `/private/tmp/rift-eval-selected-prior-headline-20260516/summaries/yak-topword/summary.tsv`
  - `/private/tmp/rift-eval-selected-prior-headline-20260516/summaries/yak-graphchi/summary.tsv`
  - `/private/tmp/rift-eval-selected-prior-headline-20260516/summaries/yak-sort/summary.tsv`
  - `/private/tmp/rift-eval-selected-prior-headline-20260516/summaries/specjbb2005-port/summary.tsv`
- Dataflow writes result lines to `/private/tmp/rift-eval-selected-prior-headline-20260516/logs/selected-dataflow.log`.

No failures, exceptions, or checksum mismatches were found by log search.

## Broom Retained Dataflow

Input: generated Broom/Naiad-style timestamped retained dataflow, 1M records,
3 measured runs. Measurement level: L2 standard stats.

| Workload | Mode | Median ms | GC ms | GC runs | Max RSS | Checksum / output |
|---|---|---:|---:|---:|---:|---|
| aggregate | `heap-gc` | 97.000 | 24.564 | 3/3 | 75,825,152 | `2843352872537677199` / `708604` |
| aggregate | `checked-rift` | 65.106 | 0.000 | 0/3 | 13,631,488 | `2843352872537677199` / `708604` |
| aggregate | `checked-region-scoped` | 77.828 | 0.000 | 0/3 | 13,795,328 | `2843352872537677199` / `708604` |
| join | `heap-gc` | 87.291 | 12.337 | 3/3 | 75,071,488 | `-5733395378394929899` / `681426` |
| join | `checked-rift` | 76.914 | 0.000 | 0/3 | 12,894,208 | `-5733395378394929899` / `681426` |
| join | `checked-region-scoped` | 76.237 | 0.000 | 0/3 | 13,074,432 | `-5733395378394929899` / `681426` |

Interpretation:

- Aggregate: checked Rift is `32.9%` faster than heap in the L2 loop and cuts
  RSS by about `82%`; checked scoped is `19.8%` faster than heap.
- Join: checked Rift is `11.9%` faster than heap; checked scoped is `12.7%`
  faster than heap. Both checked rows remove timed heap GC and cut RSS by about
  `83%`.

## Dataflow Direct Epoch / Page Token

Input: Broom/Dataflow-style generated methodology, 10 epochs x 100k documents,
3 measured runs. Measurement level: L2 standard stats. Checksums match across
compared modes.

| Operator | Heap ms / GC ms | Rooted scoped ms | Checked epoch stream ms | Checked epoch scoped ms | Page-token row |
|---|---:|---:|---:|---:|---:|
| SELECT | 27.954 / 6.955 | 21.833 | 16.573 | 18.305 | checked page-token `19.092`; scoped page-token `16.916` |
| AGGREGATE | 49.965 / 11.489 | 38.944 | 33.436 | 32.648 | n/a |
| JOIN | 31.935 / 9.471 | 22.698 | 16.778 | 18.555 | n/a |

Interpretation: checked direct epoch is the reportable checked Rift topology
for Dataflow AGGREGATE/JOIN. SELECT is also page-token-shaped, and the scoped
page-token backend is the fastest SELECT row in this run.

## StreamFlexDesign

Input: Rift-native StreamFlex design reproduction, 1M throughput events, 50k
latency events, 100k pressure-latency events, 3 measured runs. Measurement
level: L2 standard stats.

| Workload | Mode | Median ms | GC ms | Max GC ms | p99 ns | p999 ns | Max ns | Misses | Max RSS |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| throughput | `gc-heap` | 503.013 | 95.462 | 97.976 |  |  |  |  | 21,479,424 |
| throughput | `region-scoped-rooted` | 467.967 | 0.000 | 0.229 |  |  |  |  | 21,725,184 |
| throughput | `checked-epoch-scoped` | 392.565 | 0.000 | 0.241 |  |  |  |  | 21,708,800 |
| throughput | `checked-epoch-stream` | 363.792 | 0.000 | 0.199 |  |  |  |  | 23,953,408 |
| latency | `gc-heap` | 63.667 | 6.233 | 7.753 | 1333 | 6583 | 538167 | 14 | 21,479,424 |
| latency | `region-scoped-rooted` | 67.460 | 0.748 | 1.158 | 1375 | 1667 | 439416 | 1 | 21,725,184 |
| latency | `checked-epoch-scoped` | 59.235 | 0.816 | 1.510 | 1208 | 1458 | 430959 | 1 | 21,708,800 |
| latency | `checked-epoch-stream` | 54.203 | 0.764 | 0.764 | 1083 | 1292 | 16833 | 0 | 23,953,408 |
| pressure-latency | `gc-heap` | 406.017 | 43.499 | 44.514 | 4375 | 15833 | 1444583 | 45 | 21,479,424 |
| pressure-latency | `checked-epoch-stream` | 331.318 | 1.952 | 2.289 | 3833 | 14250 | 916709 | 1 | 23,953,408 |

Interpretation: checked epoch stream is the best StreamFlexDesign throughput
and tail-latency row in this run. It is about `27.7%` faster than heap on
throughput and removes deadline misses in the latency row, with a modest RSS
increase versus heap.

## Yak Local Direct-Epoch Workloads

Input: generated Yak-style local workloads scaled to 1M logical records where
applicable. Measurement level: L2 standard stats. Checksums match across
compared modes.

| Workload | Heap ms / GC ms | Rooted scoped ms | Checked epoch stream ms | Checked epoch scoped ms | Best checked interpretation |
|---|---:|---:|---:|---:|---|
| wordcount | 23.904 / 4.028 | 17.619 | 16.450 | 14.944 | scoped checked, `37.5%` faster than heap |
| graphstep | 29.631 / 5.900 | 20.231 | 18.621 | 16.668 | scoped checked, `43.8%` faster than heap |
| topword | 35.956 / 4.831 | 28.788 | 27.010 | 25.634 | scoped checked, `28.7%` faster than heap |
| graphchi | 23.429 / 3.073 | 17.398 | 15.936 | 14.740 | scoped checked, `37.1%` faster than heap |
| sort | 38.812 / 1.622 | 37.485 | 37.530 | 37.252 | scoped checked modest win, `4.0%` faster than heap |

Interpretation: checked epoch scoped is the best local Yak topology for all
five generated workloads in this selected run. `sort` is close to a
ceiling/control row; the other four show material heap GC removal and
throughput wins.

## SPECjbb2005 Workload Port

Input: clean-room SPECjbb2005-shaped transaction workload, 4 warehouses x 250k
iterations, 1M transactions, 3 measured runs. Measurement level: L2 standard
stats. This is not official SPECjbb2005.

| Mode | Median ms | GC ms | Max GC ms | Max RSS | Region-freed object proxy | Region-freed byte proxy | Checksum |
|---|---:|---:|---:|---:|---:|---:|---|
| `gc-heap` | 162.939 | 18.756 | 19.862 | 8,011,776 | 5,197,176 | 239,887,040 | `3893577075282711027` |
| `region-scoped-rooted` | 146.624 | 0.254 | 0.264 | 8,093,696 | 5,197,176 | 239,887,040 | `3893577075282711027` |
| `checked-epoch-stream` | 119.916 | 0.000 | 0.436 | 8,044,544 | 5,197,176 | 239,887,040 | `3893577075282711027` |
| `checked-epoch-scoped` | 128.332 | 0.245 | 0.251 | 8,093,696 | 5,197,176 | 239,887,040 | `3893577075282711027` |

Interpretation: checked epoch stream is the fastest transaction topology in
this run, `26.4%` faster than heap and `18.2%` faster than rooted scoped,
with comparable RSS and matching checksum.

## Follow-Up

This selected-prior sweep is the correct normalized prior-work-style
presentation source for generated/local methodology rows. Next evidence work
should run the same selected discipline over the stream/real-input set:
generated Common Crawl-shaped q1/q2, LogHub top templates and q3/session,
GH Archive q1/q2, Theodolite power q2, DSPBench Fraud/Log q2, NEXMark
q3/q8/q9/q11, and real Yak LiveJournal / AskUbuntu where local data permits.

