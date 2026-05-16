# Selected Streams Sweep, 2026-05-16

Last updated: 2026-05-16 14:42 CEST

Status: clean selected stream/application sweep for presentation-facing rows.

## Provenance

- Parent commit: `46c4ea8356b26361f258963b66f6fa1d5e4fe01a`
- Child commit: `15c4c39acdb98d499c18c68e43c3f2130a69d5f1`
- Command:

```bash
RIFT_EVAL_SUITES=selected-streams \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_RUNS=3 \
RIFT_EVAL_RUN_ROOT=/private/tmp/rift-eval-selected-streams-headline-20260516 \
bash scripts/run-performance-evaluation.sh
```

- Output root: `/private/tmp/rift-eval-selected-streams-headline-20260516`
- Summary files:
  - `summaries/common-crawl-page-token/summary.tsv`
  - `summaries/nexmark/summary.tsv`
  - `summaries/github-archive/summary.tsv`
  - `summaries/loghub-region/summary.tsv`
  - `summaries/loghub-top-templates/summary.tsv`
  - `summaries/dspbench/summary.tsv`
- Theodolite power q2 was skipped in the full selected-streams run because
  `THEODOLITE_POWER_INPUT` was not set. It was filled by the addendum run
  below after locating the local UCI household-power trace.

No failed rows, exceptions, checksum mismatches, or output-count mismatches
were found in the selected rows.

## Theodolite Addendum

The missing Theodolite row was filled with the local real UCI household-power
trace:

- Parent commit at addendum run: `0a6776e`
- Child commit at addendum run: `15c4c39ac`

```bash
THEODOLITE_POWER_INPUT_MODE=streaming-file \
THEODOLITE_POWER_INPUT=/Users/siyaoliu/rift/cache/benchmark-data/theodolite/real-power/household_power_consumption.txt \
THEODOLITE_POWER_RECORDS=1000000 \
THEODOLITE_POWER_BENCHMARK_RUNS=3 \
THEODOLITE_POWER_WARMUPS=0 \
THEODOLITE_POWER_QUERIES=q2-hierarchical \
THEODOLITE_POWER_MODES="heap-immix region-scoped-rooted checked-epoch-stream checked-epoch-scoped" \
THEODOLITE_POWER_OUTPUT_DIR=/private/tmp/rift-eval-theodolite-selected-headline-20260516 \
zsh sandbox/run_theodolite_power_region_matrix.sh
```

Output: `/private/tmp/rift-eval-theodolite-selected-headline-20260516/summary.tsv`.
No failures or checksum mismatches were found.

## Headline Rows

L1 elapsed/RSS comes from external `/usr/bin/time -l`; L2 columns are standard
matrix medians used for GC/region interpretation.

### Common Crawl WET-Shaped Page-Token

Input type: generated stream stressor. Claim class: generated page/window
stream-object pressure.

| Query | Mode | L1 real s | L2 median ms | L2 GC ms | Runs with GC | Output | RSS bytes |
|---|---|---:|---:|---:|---:|---:|---:|
| q1-tokenize | heap-immix | 22.55 | 5506.860 | 1595.727 | 3 | 137000000 | 408698880 |
| q1-tokenize | safezone-improved-32k | 19.26 | 4510.358 | 31.581 | 2 | 137000000 | 474824704 |
| q1-tokenize | rift-checked-page-token | 16.04 | 3460.683 | 19.665 | 2 | 137000000 | 463749120 |
| q1-tokenize | rift-checked-safezone-page-token | 16.63 | 3646.587 | 30.048 | 2 | 137000000 | 463863808 |
| q2-domain-window | heap-immix | 21.41 | 5314.737 | 1593.068 | 3 | 929230 | 408698880 |
| q2-domain-window | safezone-improved-32k | 18.58 | 4333.816 | 33.356 | 2 | 929230 | 474841088 |
| q2-domain-window | rift-checked-page-token | 16.36 | 3637.571 | 21.673 | 3 | 929230 | 463749120 |
| q2-domain-window | rift-checked-safezone-page-token | 16.70 | 3722.129 | 30.518 | 2 | 929230 | 463781888 |

Interpretation: checked page-token is the best safe checked row in this sweep:
`28.9%` faster than heap on q1 and `23.6%` faster than heap on q2, while
removing about `1.57 s` of median timed heap GC per L2 matrix row. This remains
generated stressor evidence, not real-input proof.

### NEXMark

Input type: generated local NEXMark-style events. Claim class: generated
methodology/control evidence.

| Query | Mode | L1 real s | L2 median ms | L2 GC ms | Runs with GC | Output |
|---|---|---:|---:|---:|---:|---:|
| q3 | heap | 1.49 | 296.751 | 28.216 | 3 | 22497 |
| q3 | safezone-improved | 1.15 | 282.787 | 10.273 | 3 | 22497 |
| q3 | rift-checked | 1.14 | 262.133 | 10.264 | 3 | 22497 |
| q8 | heap | 1.78 | 436.534 | 27.509 | 3 | 100000 |
| q8 | safezone-improved | 1.73 | 424.226 | 19.110 | 3 | 100000 |
| q8 | rift-checked | 1.67 | 404.077 | 15.954 | 3 | 100000 |
| q9 | heap | 3.69 | 898.549 | 99.436 | 3 | 216101 |
| q9 | safezone-improved | 3.51 | 843.190 | 37.680 | 3 | 216101 |
| q9 | rift-checked | 3.45 | 818.771 | 35.142 | 3 | 216101 |
| q11 | heap | 0.91 | 219.972 | 17.199 | 3 | 250869 |
| q11 | safezone-improved | 0.93 | 228.766 | 9.930 | 2 | 250869 |
| q11 | rift-checked | 0.91 | 215.739 | 8.288 | 2 | 250869 |

Interpretation: checked Rift is best or tied-best across selected NEXMark
queries. The elapsed gains are modest except q3/q9, but RSS and GC movement
remain favorable. This is generated local-harness evidence, not exact Beam.

### GH Archive Shaped

Input type: generated/preloaded GH Archive-shaped NDJSON records. Claim class:
generated page/window stream control.

| Query | Mode | L1 real s | L2 median ms | L2 max GC ms | Output | RSS bytes |
|---|---|---:|---:|---:|---:|---:|
| q1-fields | heap-immix | 1.43 | 334.971 | 161.386 | 7502145 | 206618624 |
| q1-fields | safezone-improved-32k | 0.98 | 287.975 | 42.169 | 7502145 | 45006848 |
| q1-fields | rift-checked-page-token | 1.00 | 289.489 | 2.693 | 7502145 | 44941312 |
| q1-fields | rift-checked-safezone-page-token | 1.12 | 333.757 | 41.691 | 7502145 | 45039616 |
| q2-repo-window | heap-immix | 1.03 | 313.433 | 156.871 | 163487 | 206585856 |
| q2-repo-window | safezone-improved-32k | 0.86 | 278.624 | 51.641 | 163487 | 45006848 |
| q2-repo-window | rift-checked-page-token | 0.91 | 292.492 | 2.732 | 163487 | 44957696 |
| q2-repo-window | rift-checked-safezone-page-token | 1.06 | 344.086 | 54.047 | 163487 | 45023232 |

Interpretation: safezone-improved is fastest on the generated/preloaded GH
Archive-shaped rows; checked page-token is close and has the lowest L2 GC max.
This is a safe-backend comparison/control, not a flagship Rift throughput win.

### LogHub Region

Input type: generated LogHub-shaped records. Claim classes: direct epoch
topology for q2/q3, page/window control for checked scoped page-token.

| Query | Mode | L1 real s | L2 median ms | L2 GC ms | Output | RSS bytes |
|---|---|---:|---:|---:|---:|---:|
| q2-window-counts | heap-immix | 3.63 | 542.036 | 130.172 | 163487 | 813137920 |
| q2-window-counts | safezone-improved-32k | 3.12 | 433.904 | 0.000 | 163487 | 801980416 |
| q2-window-counts | rift-checked-safezone-page-token | 3.19 | 454.806 | 0.000 | 163487 | 801996800 |
| q2-window-counts | checked-epoch-stream | 2.49 | 222.147 | 0.000 | 163487 | 678821888 |
| q2-window-counts | checked-epoch-scoped | 2.46 | 220.824 | 0.000 | 163487 | 678821888 |
| q3-template-session | heap-immix | 11.22 | 2215.913 | 181.359 | 312151 | 2291269632 |
| q3-template-session | safezone-improved-32k | 11.33 | 2208.320 | 0.000 | 312151 | 2290294784 |
| q3-template-session | rift-checked-safezone-page-token | 11.46 | 2234.723 | 0.000 | 312151 | 2290294784 |
| q3-template-session | checked-epoch-stream | 10.35 | 2014.570 | 0.000 | 312151 | 2167828480 |
| q3-template-session | checked-epoch-scoped | 10.32 | 2002.367 | 0.000 | 312151 | 2167959552 |

Interpretation: direct checked epoch is the best topology on generated LogHub
q2/q3. q2 is a strong generated topology win; q3 is a more modest CPU-heavy
template/session win with a large RSS footprint in all modes.

### LogHub Top Templates

Input type: generated LogHub-shaped top-template records. Claim class:
reusable checked top-k API evidence.

| Mode | L1 real s | L2 median ms | L2 GC ms | Output | RSS bytes |
|---|---:|---:|---:|---:|---:|
| heap-natural | 2.03 | 423.408 | 134.143 | 1280 | 289226752 |
| checked-epoch-topk-retained-no-traverse | 1.42 | 301.111 | 0.000 | 1280 | 304545792 |
| checked-scoped-epoch-topk-retained-no-traverse | 1.39 | 294.813 | 0.000 | 1280 | 304594944 |

Interpretation: checked scoped top-k is `31.5%` faster than natural heap and
removes `134.143 ms` median timed GC, but uses slightly higher RSS than heap in
this generated run. This is a throughput/GC win, not an RSS win.

### DSPBench Real Bundled Inputs

Input type: real DSPBench bundled credit-card and HTTP log files, file-backed
with replay to 1M records. Claim class: real-input page/window modest/control.

| Query | Mode | L1 real s | L2 median ms | L2 GC ms | Output | RSS bytes |
|---|---|---:|---:|---:|---:|---:|
| fraud-q2-alert-window | heap-immix | 3.74 | 844.319 | 96.671 | 594182 | 254623744 |
| fraud-q2-alert-window | safezone-improved-32k | 3.41 | 812.990 | 15.232 | 594182 | 282558464 |
| fraud-q2-alert-window | rift-checked-page-token | 3.46 | 827.185 | 12.272 | 594182 | 278544384 |
| fraud-q2-alert-window | rift-checked-safezone-page-token | 3.46 | 833.962 | 14.216 | 594182 | 278691840 |
| log-q2-window | heap-immix | 6.91 | 1688.522 | 45.034 | 179 | 307757056 |
| log-q2-window | safezone-improved-32k | 6.90 | 1679.166 | 18.893 | 179 | 324583424 |
| log-q2-window | rift-checked-page-token | 6.90 | 1678.577 | 14.199 | 179 | 320552960 |
| log-q2-window | rift-checked-safezone-page-token | 6.95 | 1696.654 | 16.842 | 179 | 320716800 |

Interpretation: DSPBench real file-backed rows are modest/control evidence.
SafeZone is fastest for Fraud q2 and checked page-token is essentially tied on
Log q2. Checked page-token reduces L2 timed GC but does not produce a strong
RSS win in this selected run.

### Theodolite Power q2

Input type: real UCI household-power trace, streaming-file replay. Claim class:
real-streaming-input direct epoch throughput/GC win, not an RSS win in this
selected rerun.

| Query | Mode | L1 real s | L2 median ms | L2 GC ms | Runs with GC | Output | RSS bytes |
|---|---|---:|---:|---:|---:|---:|---:|
| q2-hierarchical | heap-immix | 5.13 | 989.733 | 19.465 | 3 | 40960 | 75268096 |
| q2-hierarchical | region-scoped-rooted | 4.73 | 963.378 | 0.000 | 0 | 40960 | 78528512 |
| q2-hierarchical | checked-epoch-stream | 4.58 | 929.243 | 0.000 | 0 | 40960 | 78479360 |
| q2-hierarchical | checked-epoch-scoped | 4.63 | 941.877 | 0.000 | 0 | 40960 | 78512128 |

Interpretation: checked epoch stream is `10.7%` faster than heap and removes
`19.465 ms` median timed heap GC. RSS is slightly higher than heap in this
selected rerun, so the row is a real-streaming throughput/GC win rather than
an RSS win.

## Overall Interpretation

- The clean selected stream sweep strengthens the generated stream-object
  pressure story: Common Crawl page-token and LogHub direct epoch/top-k rows
  are clear checked wins.
- Real bundled/file-like rows remain more modest: DSPBench, GH Archive, and
  Theodolite are useful controls, but not flagship GC-heavy evidence.
- NEXMark remains generated methodology evidence with modest checked wins.
- Theodolite's selected row is now filled from the real power trace; continue
  treating it as modest real-streaming evidence unless a retained-window
  variant creates stronger heap GC/RSS pressure.
