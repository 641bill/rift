# ReML / MLKit PLDI-Style Table

Date: 2026-05-09
Last updated: 2026-05-10 01:04 CEST

Status: dedicated PLDI-style table artifact. Paper rows are transcribed from
Elsman 2023 Figure 9 and are **paper-reported, not rerun locally**. Local L1
rows come from the Scala Native `ReMLRegionMatrix` Tier 1 ports and are
**local Scala Native port evidence**, not exact MLKit/ReML reproduction.

References:

- Martin Elsman, "Garbage-Collection Safety for Region-Based
  Type-Polymorphic Programs", PLDI 2023, DOI `10.1145/3591229`.
- MLKit home: <https://elsman.com/mlkit/>.
- Public MLKit repository inspected locally: <https://github.com/melsman/mlkit>.

## Claim Boundary

Do not claim raw "Rift beats ReML" from this table. Exact cross-system timing
requires original MLKit/ReML artifacts, paper-era compiler flags, MLton, and
the same machine. Until then, compare ratios and axes:

- paper ReML/MLKit `rg`, `rg-`, `r`, and MLton behavior;
- local Scala Native heap-versus-checked-region ratios;
- RSS reduction;
- GC time/count reduction;
- safety and annotation/API burden.

## Evidence Layers

| Layer | Status | Claim boundary |
|---|---|---|
| paper-reported | Figure 9 data transcribed below | literature anchor only |
| exact artifact rerun | source provenance partial; local `mlkit`/`mlton` timing not run | required for raw wall-clock comparison |
| Scala Native ports | Tier 1 L1 final-clean rows for `fib37`, `tak`, `mandel`, `msort`, `msort-r`, `life`, `fft`, `ratio` | valid local Rift-vs-Scala-Native ratios |
| safety probes | ReML-style polymorphic/generic heap-retention probes active | design/safety evidence |

## Local L1 Final-Clean Tier 1 Rows

These rows were collected from child `7573d7577` with
`RIFT_FINAL_CLEAN=1`, three external `/usr/bin/time -l` processes, and
20 benchmark iterations per process. Times below are total process time for
the 20 iterations; the per-iteration value is derived only for readability.

| Program | Local status | Heap total s | Best checked/rooted mode | Best total s | Approx speedup | Heap RSS bytes | Best RSS bytes | L1 interpretation |
|---|---|---:|---|---:|---:|---:|---:|---|
| `fib37` | compute/control | `2.40` | `checked-region-stream` | `2.41` | `1.00x` | `3784704` | `3784704` | near-tie; no memory-management claim |
| `tak` | timing-granularity control | `0.00` | -- | -- | -- | `3784704` | `3784704` | too short under this configuration |
| `mandel` | timing-granularity control | `0.06` | -- | -- | -- | `3784704` | `3784704` | too short for useful external timing |
| `msort` | allocation/list workload | `2.46` (`123.0 ms/iter`) | `checked-region-stream` | `2.06` (`103.0 ms/iter`) | `1.19x` | `21250048` | `10289152` | clear local checked speed/RSS win |
| `msort-r` | allocation/list workload | `2.25` (`112.5 ms/iter`) | `checked-region-stream` | `2.05` (`102.5 ms/iter`) | `1.10x` | `39141376` | `10289152` | local checked speed/RSS win |
| `life` | compute/control | `0.69` | `checked-region-stream` / `region-scoped-rooted` | `0.68` | `1.01x` | `5177344` | `5177344` | near-tie; no strong memory claim |
| `fft` | timing-granularity control | `0.02` | -- | -- | -- | `7913472` | `5079040` | too short for useful external timing |
| `ratio` | allocation/object workload | `0.93` (`46.5 ms/iter`) | `checked-region-scoped` | `0.91` (`45.5 ms/iter`) | `1.02x` | `79888384` | `15892480` | modest elapsed win, strong RSS win |

Command:

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

## Paper-Reported Figure 9 Recreation

`rg` is ReML/MLKit regions plus tracing GC with the GC-safety refinement.
`rg-` is the paper variant without the spurious-type-variable refinement. `r`
is pure region inference/no tracing GC. `MLton` is the optimizing SML baseline.

| Program | loc | fcns | inst | delta | rg s | rg- s | r s | MLton s | rg RSS MB | rg- RSS MB | r RSS MB | MLton RSS MB | rg GC # | rg- GC # |
|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DLX | 2841 | 2/149 | 0/690 | yes | 0.14 | 0.15 | 0.12 | 0.40 | 8 | 8 | 7 | 31 | 3 | 3 |
| b-hut | 1245 | 2/140 | 0/459 | no | 0.67 | 0.70 | 0.63 | 0.14 | 5 | 5 | 169 | 3 | 471 | 471 |
| fft | 71 | 0/9 | 0/34 | no | 0.64 | 0.66 | 0.51 | 0.26 | 69 | 69 | 56 | 125 | 10 | 10 |
| fib37 | 7 | 0/1 | 0/0 | no | 0.98 | 0.98 | 0.21 | 0.85 | 3 | 3 | 3 | 1 | 1 | 1 |
| kbc | 679 | 1/90 | 0/249 | yes | 0.21 | 0.21 | 0.19 | 0.07 | 10 | 10 | 10 | 2 | 10 | 10 |
| lexgen | 1322 | 0/108 | 0/531 | no | 0.74 | 0.81 | 0.62 | 0.43 | 15 | 15 | 67 | 18 | 109 | 109 |
| life | 202 | 0/35 | 0/146 | no | 0.44 | 0.46 | 0.43 | 0.43 | 3 | 3 | 14 | 2 | 58 | 58 |
| logic | 351 | 0/22 | 0/806 | no | 0.63 | 0.64 | 0.43 | 0.13 | 4 | 4 | 251 | 2 | 1843 | 1843 |
| mandel | 62 | 0/5 | 0/0 | no | 0.53 | 0.53 | 0.38 | 0.31 | 3 | 3 | 3 | 1 | 1 | 1 |
| mlyacc | 7385 | 10/966 | 5/3256 | yes | 0.36 | 0.34 | 0.30 | 0.33 | 18 | 15 | 115 | 10 | 29 | 28 |
| mpuz | 124 | 0/13 | 0/44 | no | 0.68 | 0.66 | 0.46 | 0.27 | 3 | 3 | 3 | 1 | 2 | 2 |
| msort-r | 119 | 0/14 | 0/27 | no | 0.69 | 0.67 | 0.47 | 0.93 | 116 | 116 | 97 | 577 | 16 | 16 |
| msort | 113 | 0/13 | 0/22 | no | 0.89 | 0.89 | 0.54 | 0.93 | 131 | 131 | 375 | 421 | 26 | 26 |
| nucleic | 3215 | 1/40 | 475/1273 | no | 0.34 | 0.34 | 0.33 | 0.17 | 5 | 5 | 231 | 3 | 645 | 645 |
| prof | 282 | 0/57 | 0/99 | no | 0.49 | 0.48 | 0.38 | 0.42 | 4 | 4 | 11 | 1 | 263 | 263 |
| ratio | 620 | 0/54 | 0/848 | no | 1.71 | 1.67 | 1.33 | 0.48 | 16 | 16 | 36 | 46 | 14 | 14 |
| ray | 529 | 1/48 | 0/120 | no | 0.69 | 0.67 | 0.64 | 0.25 | 14 | 14 | 14 | 15 | 12 | 12 |
| simple | 1053 | 15/327 | 0/448 | yes | 0.19 | 0.16 | 0.13 | 0.28 | 5 | 5 | 4 | 8 | 4 | 4 |
| tak | 12 | 0/2 | 0/0 | no | 2.09 | 2.04 | 0.55 | 2.12 | 3 | 3 | 3 | 1 | 1 | 1 |
| tsp | 493 | 0/26 | 0/19 | no | 0.14 | 0.14 | 0.11 | 0.14 | 11 | 11 | 6 | 11 | 7 | 7 |
| vliw | 3681 | 5/563 | 4/2133 | yes | 0.78 | 0.73 | 0.56 | 0.30 | 14 | 14 | 44 | 9 | 15 | 15 |
| zebra | 313 | 2/50 | 0/288 | yes | 1.58 | 1.58 | 1.15 | 0.45 | 3 | 3 | 122 | 1 | 1066 | 1504 |
| zern | 605 | 3/103 | 0/34 | yes | 0.80 | 0.80 | 0.52 | 0.30 | 6 | 5 | 5 | 11 | 4503 | 4503 |

## Paper-Style Combined Snapshot

This is the thesis table shape: paper-reported columns on the left, local
Scala Native port ratios on the right when a port exists. The local columns
below remain the earlier L2 standard-stats snapshot until they are fully
rewritten from the L1 rows above; use the L1 table above for headline timing.

| Program | Source/local status | Paper rg s | Paper r s | Paper MLton s | Paper rg RSS MB | Paper rg GC # | Local gc-heap ms | Best local checked mode | Best local checked ms | Local speedup | Local RSS ratio | Local GC change | Evidence class |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---|---|
| DLX | source candidate found; no SN port | 0.14 | 0.12 | 0.40 | 8 | 3 | -- | -- | -- | -- | -- | -- | paper-reported |
| b-hut | source candidate found; Tier 2 planned | 0.67 | 0.63 | 0.14 | 5 | 471 | -- | -- | -- | -- | -- | -- | paper-reported |
| fft | Tier 1 SN port | 0.64 | 0.51 | 0.26 | 69 | 10 | 0.823 | `checked-region-scoped` | 0.764 | 1.08x | 0.67x | `0.000 -> 0.000 ms` | SN port |
| fib37 | Tier 1 SN port; MLKit candidates are fib35 | 0.98 | 0.21 | 0.85 | 3 | 1 | 132.735 | `checked-region-stream` | 126.017 | 1.05x | 1.00x | `0.000 -> 0.000 ms` | SN port |
| kbc | source/config still open | 0.21 | 0.19 | 0.07 | 10 | 10 | -- | -- | -- | -- | -- | -- | paper-reported |
| lexgen | source/config still open | 0.74 | 0.62 | 0.43 | 15 | 109 | -- | -- | -- | -- | -- | -- | paper-reported |
| life | Tier 1 SN port | 0.44 | 0.43 | 0.43 | 3 | 58 | 36.684 | `checked-region-scoped` | 35.563 | 1.03x | 1.00x | `0.000 -> 0.000 ms` | SN port |
| logic | source candidate found; Tier 2 planned | 0.63 | 0.43 | 0.13 | 4 | 1843 | -- | -- | -- | -- | -- | -- | paper-reported |
| mandel | Tier 1 SN port; config differs | 0.53 | 0.38 | 0.31 | 3 | 1 | 3.462 | `checked-region-stream` | 3.297 | 1.05x | 1.00x | `0.000 -> 0.000 ms` | SN port |
| mlyacc | source/config still open | 0.36 | 0.30 | 0.33 | 18 | 29 | -- | -- | -- | -- | -- | -- | paper-reported |
| mpuz | source candidate found; Tier 2 planned | 0.68 | 0.46 | 0.27 | 3 | 2 | -- | -- | -- | -- | -- | -- | paper-reported |
| msort-r | Tier 1 SN port | 0.69 | 0.47 | 0.93 | 116 | 16 | 126.163 | `checked-region-stream` | 104.929 | 1.20x | 0.26x | `27.280 -> 6.005 ms` | SN port |
| msort | Tier 1 SN port | 0.89 | 0.54 | 0.93 | 131 | 26 | 124.983 | `checked-region-stream` | 104.358 | 1.20x | 0.49x | `27.180 -> 6.063 ms` | SN port |
| nucleic | source candidate found; Tier 2 planned | 0.34 | 0.33 | 0.17 | 5 | 645 | -- | -- | -- | -- | -- | -- | paper-reported |
| prof | source candidate found; no SN port | 0.49 | 0.38 | 0.42 | 4 | 263 | -- | -- | -- | -- | -- | -- | paper-reported |
| ratio | Tier 1 SN port | 1.71 | 1.33 | 0.48 | 16 | 14 | 51.302 | `checked-region-scoped` | 48.929 | 1.05x | 0.36x | `3.191 -> 0.000 ms` | SN port |
| ray | source candidate found; Tier 2 planned | 0.69 | 0.64 | 0.25 | 14 | 12 | -- | -- | -- | -- | -- | -- | paper-reported |
| simple | source candidate found; no SN port | 0.19 | 0.13 | 0.28 | 5 | 4 | -- | -- | -- | -- | -- | -- | paper-reported |
| tak | Tier 1 SN port; config differs | 2.09 | 0.55 | 2.12 | 3 | 1 | 0.188 | `checked-region-stream` | 0.180 | 1.04x | 1.00x | `0.000 -> 0.000 ms` | SN port |
| tsp | source candidate found; Tier 2 planned | 0.14 | 0.11 | 0.14 | 11 | 7 | -- | -- | -- | -- | -- | -- | paper-reported |
| vliw | source/config still open | 0.78 | 0.56 | 0.30 | 14 | 15 | -- | -- | -- | -- | -- | -- | paper-reported |
| zebra | source/config still open | 1.58 | 1.15 | 0.45 | 3 | 1066 | -- | -- | -- | -- | -- | -- | paper-reported |
| zern | source candidate found; no SN port | 0.80 | 0.52 | 0.30 | 6 | 4503 | -- | -- | -- | -- | -- | -- | paper-reported |

## Interpretation

- The L1 final-clean rows confirm `msort` and `msort-r` as the meaningful local
  ReML-shaped allocation/list wins.
- `ratio` is a modest elapsed win but a strong RSS row in L1.
- `fib37` and `life` are near-tie compute/control rows; `tak`, `fft`, and
  `mandel` are too short at the current configuration for headline timing.
- The combined snapshot above still includes older L2 GC/RSS interpretation
  columns. Use the L1 section for final elapsed/RSS claims, and use L2 only to
  explain GC behavior.
- Exact MLKit/ReML artifact reruns remain open; use the public-source
  provenance and runbook in `docs/REML_ARTIFACT_RUNBOOK.md` before making any
  raw cross-language timing claim.
