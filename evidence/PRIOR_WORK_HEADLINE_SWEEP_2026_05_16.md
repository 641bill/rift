# Prior-Work Headline-Scale Sweep, 2026-05-16

Date: 2026-05-16
Last updated: 2026-05-16 12:38 CEST

Status: clean committed-tree prior-work sweep, useful as L2 standard-stats
interpretation evidence. This is not the final normalized presentation sweep:
the parent `prior` suite still mixes older prior-work runners with newer
framework-API matrices. Use this file to confirm runner health and prior-work
metric axes; use L1 final-clean tables for headline elapsed/RSS when available.

Run command:

```sh
RIFT_EVAL_SUITES=prior \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_RUNS=3 \
RIFT_EVAL_RUN_ROOT=/private/tmp/rift-eval-prior-headline-20260516 \
bash scripts/run-performance-evaluation.sh
```

Clean commits:

- parent: `98b0114`
- child: `15c4c39ac`

Run output:

- root: `/private/tmp/rift-eval-prior-headline-20260516`
- summaries:
  - `/private/tmp/rift-eval-prior-headline-20260516/summaries/broom-retained-dataflow/summary.tsv`
  - `/private/tmp/rift-eval-prior-headline-20260516/summaries/streamflex/summary.tsv`
  - `/private/tmp/rift-eval-prior-headline-20260516/summaries/yak/summary.tsv`
  - `/private/tmp/rift-eval-prior-headline-20260516/summaries/stancu/summary.tsv`
- Dataflow writes result lines to `/private/tmp/rift-eval-prior-headline-20260516/logs/dataflow.log`.

## Result Summary

### Broom Retained Dataflow

This is the normalized prior-work-style row: natural heap/GC versus checked
Rift, with `checked-region-scoped` as the best-safe-region/backend comparison.
All checksums and output counts match.

| Workload | Mode | Median ms | GC ms | GC runs | Max RSS | Checksum / output |
|---|---|---:|---:|---:|---:|---|
| aggregate | `heap-gc` | 99.115 | 23.134 | 3/3 | 75,825,152 | `2843352872537677199` / `708604` |
| aggregate | `checked-rift` | 67.364 | 0.000 | 0/3 | 13,631,488 | `2843352872537677199` / `708604` |
| aggregate | `checked-region-scoped` | 79.022 | 0.000 | 0/3 | 13,811,712 | `2843352872537677199` / `708604` |
| join | `heap-gc` | 86.547 | 10.914 | 3/3 | 75,071,488 | `-5733395378394929899` / `681426` |
| join | `checked-rift` | 78.615 | 0.000 | 0/3 | 12,894,208 | `-5733395378394929899` / `681426` |
| join | `checked-region-scoped` | 77.058 | 0.000 | 0/3 | 13,107,200 | `-5733395378394929899` / `681426` |

Interpretation:

- Aggregate: checked Rift is `32.0%` faster than heap in the L2 loop and cuts
  RSS by about `82%`; checked scoped is `20.3%` faster than heap with similar
  low RSS.
- Join: checked Rift is `9.2%` faster than heap; checked scoped is `11.0%`
  faster than heap. Both remove timed heap GC and cut RSS by about `83%`.

### Dataflow

Dataflow is logged in `logs/dataflow.log` rather than a summary TSV. Checksums
match across heap, improved SafeZone, checked Rift, and page-token SELECT rows.

| Operator | Heap ms / GC ms | Improved SafeZone ms | Checked Rift ms | Other checked row |
|---|---:|---:|---:|---:|
| SELECT | 28.369 / 7.175 | 21.796 | 21.009 | checked page-token `18.200`; scoped page-token `16.964` |
| AGGREGATE | 54.841 / 12.756 | 39.434 | 37.677 | n/a |
| JOIN | 30.475 / 9.389 | 22.648 | 21.010 | n/a |

Interpretation: this run confirms the prior Dataflow direction under the
parent runner: checked Rift/direct region rows remove timed heap GC and beat
heap across SELECT/AGGREGATE/JOIN. SELECT remains the page-token-friendly
operator.

### StreamFlex Instrumented Runner

This is the older StreamFlex instrumented matrix, not the newer
`StreamFlexDesignMatrix`. Treat it as prior-work-axis interpretation evidence.

| Row | Mode | Median ms | GC ms | p50 ns | p99 ns | p999 ns | Max ns | Misses | Max RSS |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| throughput | `heap` | 43.048 | 9.357 |  |  |  |  |  | 8,011,776 |
| throughput | `improved-safezone` | 38.436 | 0.000 |  |  |  |  |  | 8,159,232 |
| throughput | `rift-checked-safezone-transaction-region` | 39.712 | 0.000 |  |  |  |  |  | 8,159,232 |
| latency | `heap` | 9.941 | 1.331 | 667 | 875 | 6583 | 370583 | 4 | 8,011,776 |
| latency | `improved-safezone` | 10.558 | 0.000 | 875 | 1125 | 1417 | 24584 | 0 | 8,159,232 |
| latency | `rift-checked-safezone-transaction-region` | 13.258 | 0.354 | 1083 | 1458 | 13709 | 355583 | 1 | 8,159,232 |

Interpretation: improved SafeZone removes heap GC and deadline misses in this
small latency row. The checked transaction-region row is not the current best
StreamFlex-style evidence; use `StreamFlexDesignMatrix` for the normalized
Rift-native StreamFlex design reproduction.

### Yak Instrumented Runner

This is the older Yak instrumented matrix over generated local workloads, not
the LiveJournal real-input graph replay. It remains useful for Yak-style axes.

| Workload | Heap ms / GC ms | Improved SafeZone ms | Yak runtime ms |
|---|---:|---:|---:|
| wordcount | 51.272 / 11.492 | 36.009 | 47.795 |
| graphstep | 51.123 / 7.549 | 39.204 | 49.926 |
| sort | 75.616 / 0.000 | 77.278 | 76.765 |
| topword | 69.757 / 10.157 | 58.321 | 67.963 |
| graphchi | 43.474 / 4.200 | 34.194 | 45.112 |

Interpretation: improved SafeZone is the strongest row in this old local Yak
runner; direct checked epoch and real LiveJournal rows are tracked elsewhere
and should be used for the presentation-facing checked Rift story.

### Stancu Instrumented Runner

| Mode | Median ms | GC ms | Max RSS | Region/object proxy | Checksum |
|---|---:|---:|---:|---:|---|
| `heap` | 45.037 | 5.632 | 7,929,856 | 1,800,000 logical objects | `-1953196317317355226` |
| `improved-safezone` | 32.402 | 0.000 | 8,028,160 | 1,800,000 logical objects | `-1953196317317355226` |

Interpretation: this legacy Stancu runner shows the scoped-region direction,
but it does not include the newer checked direct-epoch/SPECjbb-style rows. Use
`SPECJBB2005_PORT_MATRIX.md` for the normalized Stancu/SPECjbb-style checked
Rift comparison.

## Follow-Up

The runner is healthy, and Broom is now integrated into the parent `prior`
suite. The next presentation-grade sweep should use the normalized selected
matrix set rather than only `RIFT_EVAL_SUITES=prior`:

- Broom retained dataflow: natural heap/GC, checked Rift, checked scoped.
- Dataflow direct epoch: heap, checked Rift, checked scoped.
- StreamFlexDesign: heap, checked epoch stream/scoped, legacy checked only as
  appendix control.
- Yak LiveJournal / AskUbuntu: real-input direct epoch rows.
- SPECjbb2005 port: heap, checked epoch stream/scoped, rooted scoped.
- Streams/real input: Common Crawl-shaped, LogHub, GH Archive, Theodolite,
  DSPBench, NEXMark with L1/L2 separation.

