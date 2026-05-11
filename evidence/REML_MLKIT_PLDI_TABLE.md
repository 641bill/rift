# ReML / MLKit PLDI-Style Table

Date: 2026-05-09
Last updated: 2026-05-11 14:32 CEST

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
| exact artifact rerun | gated/low-priority; source provenance partial, local `mlkit`/`mlton` not installed, and Docker daemon unavailable in the latest check | resume only if raw same-machine wall-clock comparison becomes necessary |
| Scala Native ports | Tier 1 L1 final-clean rows for `fib37`, `tak`, `mandel`, `msort`, `msort-r`, `life`, `fft`, `ratio`; Tier 2 L1 final-clean rows for `logic`, `ray`, and `tsp` | valid local Rift-vs-Scala-Native ratios, not exact ReML reproduction |
| safety probes | ReML-style polymorphic/generic heap-retention probes active | design/safety evidence |

## Tier 2 Scala Native Port Rows

Child implementation now includes the first Tier 2 shaped ports in
`ReMLRegionMatrix`: `logic`, `ray`, and `tsp`. These are **Scala Native shaped
ports**, not exact MLKit/ReML source reproductions.

Rows below use three external L1 final-clean repeats. Each process ran 20
iterations. `logic` was scaled with `REML_LOGIC_ITERATIONS=200000`; `ray` was
scaled with `REML_RAY_RAYS=50000`; `tsp` used the current default size.

| Program | Local port shape | Heap total s | Best checked/rooted mode | Best total s | Approx speedup | Heap RSS bytes | Best RSS bytes | L1 interpretation |
|---|---|---:|---|---:|---:|---:|---:|---|
| `logic` | symbolic expression chain with ordinary node objects | `1.27` | `checked-region-stream` | `1.27` | `1.00x` | `7880704` | `65601536` | elapsed tie but large RSS regression; not a win |
| `ray` | ray/sphere/hit object allocation and intersection loop | `0.75` | `region-scoped-rooted` | `0.74` | `1.01x` | `4145152` | `4096000` | near-tie compute/control row |
| `tsp` | nearest-neighbor tour construction with point and tour-node objects | `3.40` | `checked-region-scoped` | `3.48` | `0.98x` | `7913472` | `5881856` | RSS win with small elapsed loss; heap GC is tiny |

L1 command:

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

L2 standard-stats interpretation command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
REML_BUILD=0 \
REML_OUTPUT_DIR=/tmp/reml-tier2-l2-scaled-2026-05-11 \
REML_WORKLOADS="logic ray tsp" \
REML_MODES="gc-heap region-scoped-rooted checked-region-stream checked-region-scoped" \
REML_LOGIC_ITERATIONS=200000 \
REML_RAY_RAYS=50000 \
REML_BENCHMARK_RUNS=3 \
REML_WARMUPS=1 \
zsh sandbox/run_reml_region_matrix.sh
```

Validation:

```sh
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"
```

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

This table intentionally keeps the exact paper metric columns:
`loc`, `fcns`, `inst`, `delta`, `rg s`, `rg- s`, `r s`, `MLton s`,
`rg RSS MB`, `rg- RSS MB`, `r RSS MB`, `MLton RSS MB`, `rg GC #`, and
`rg- GC #`. Later interpretation tables compress these paper columns for
readability, but this section is the same-axis source table.

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

## Same-Metric Paper Plus Scala Native Port Table

This is the side-by-side table to use for thesis comparison. The left columns
are the exact ReML/MLKit Figure 9 axes. The right columns use the closest local
Scala Native/Rift analogue: `gc-heap`, `region-scoped-rooted`,
`checked-region-stream`, and `checked-region-scoped`. Local wall-clock and RSS
columns use L1 final-clean rows where available. Local GC columns use L2
standard-stats rows and are interpretation evidence, not headline timing.

ReML-specific static columns `fcns`, `inst`, and `delta` do not have a local
Scala Native analogue yet; they remain paper columns. A future local analogue
would be an audited Rift safety/API-burden table, not a renamed ReML metric.
RSS is reported as MiB for local rows, converted from L1 max RSS bytes.

| Program | loc | fcns | inst | delta | rg s | rg- s | r s | MLton s | rg RSS MB | rg- RSS MB | r RSS MB | MLton RSS MB | rg GC # | rg- GC # | SN gc-heap s | SN region-scoped-rooted s | SN checked-stream s | SN checked-scoped s | SN gc-heap RSS MiB | SN region-scoped-rooted RSS MiB | SN checked-stream RSS MiB | SN checked-scoped RSS MiB | SN gc-heap GC ms/runs | SN best GC ms/runs | Local status |
|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| DLX | 2841 | 2/149 | 0/690 | yes | 0.14 | 0.15 | 0.12 | 0.40 | 8 | 8 | 7 | 31 | 3 | 3 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | source/provenance-blocked |
| b-hut | 1245 | 2/140 | 0/459 | no | 0.67 | 0.70 | 0.63 | 0.14 | 5 | 5 | 169 | 3 | 471 | 471 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | port-planned |
| fft | 71 | 0/9 | 0/34 | no | 0.64 | 0.66 | 0.51 | 0.26 | 69 | 69 | 56 | 125 | 10 | 10 | 0.02 | -- | -- | -- | 7.55 | -- | -- | -- | 0.000 / 0 | 0.000 / 0 | timing-control |
| fib37 | 7 | 0/1 | 0/0 | no | 0.98 | 0.98 | 0.21 | 0.85 | 3 | 3 | 3 | 1 | 1 | 1 | 2.40 | -- | 2.41 | -- | 3.61 | -- | 3.61 | -- | 0.000 / 0 | 0.000 / 0 | compute/control |
| kbc | 679 | 1/90 | 0/249 | yes | 0.21 | 0.21 | 0.19 | 0.07 | 10 | 10 | 10 | 2 | 10 | 10 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | source/provenance-blocked |
| lexgen | 1322 | 0/108 | 0/531 | no | 0.74 | 0.81 | 0.62 | 0.43 | 15 | 15 | 67 | 18 | 109 | 109 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | tool-benchmark-deferred |
| life | 202 | 0/35 | 0/146 | no | 0.44 | 0.46 | 0.43 | 0.43 | 3 | 3 | 14 | 2 | 58 | 58 | 0.69 | 0.68 | 0.68 | 0.68 | 4.94 | 4.94 | 4.94 | 4.94 | 0.000 / 0 | 0.000 / 0 | compute/control |
| logic | 351 | 0/22 | 0/806 | no | 0.63 | 0.64 | 0.43 | 0.13 | 4 | 4 | 251 | 2 | 1843 | 1843 | 1.27 | 1.71 | 1.27 | 1.54 | 7.52 | 62.69 | 62.56 | 62.69 | 6.705 / -- | 1.288 / -- | elapsed tie, RSS regression |
| mandel | 62 | 0/5 | 0/0 | no | 0.53 | 0.53 | 0.38 | 0.31 | 3 | 3 | 3 | 1 | 1 | 1 | 0.06 | -- | -- | -- | 3.61 | -- | -- | -- | 0.000 / 0 | 0.000 / 0 | timing-control |
| mlyacc | 7385 | 10/966 | 5/3256 | yes | 0.36 | 0.34 | 0.30 | 0.33 | 18 | 15 | 115 | 10 | 29 | 28 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | tool-benchmark-deferred |
| mpuz | 124 | 0/13 | 0/44 | no | 0.68 | 0.66 | 0.46 | 0.27 | 3 | 3 | 3 | 1 | 2 | 2 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | port-planned |
| msort-r | 119 | 0/14 | 0/27 | no | 0.69 | 0.67 | 0.47 | 0.93 | 116 | 116 | 97 | 577 | 16 | 16 | 2.25 | 2.20 | 2.05 | -- | 37.33 | 14.09 | 9.81 | -- | 27.280 / 3 | 6.005 / 3 | local checked speed/RSS win |
| msort | 113 | 0/13 | 0/22 | no | 0.89 | 0.89 | 0.54 | 0.93 | 131 | 131 | 375 | 421 | 26 | 26 | 2.46 | 2.31 | 2.06 | -- | 20.27 | 9.83 | 9.81 | -- | 27.180 / 3 | 6.063 / 3 | local checked speed/RSS win |
| nucleic | 3215 | 1/40 | 475/1273 | no | 0.34 | 0.34 | 0.33 | 0.17 | 5 | 5 | 231 | 3 | 645 | 645 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | port-planned |
| prof | 282 | 0/57 | 0/99 | no | 0.49 | 0.48 | 0.38 | 0.42 | 4 | 4 | 11 | 1 | 263 | 263 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | paper-only |
| ratio | 620 | 0/54 | 0/848 | no | 1.71 | 1.67 | 1.33 | 0.48 | 16 | 16 | 36 | 46 | 14 | 14 | 0.93 | 0.93 | -- | 0.91 | 76.19 | 15.19 | -- | 15.16 | 3.191 / 2 | 0.000 / 0 | modest elapsed, strong RSS win |
| ray | 529 | 1/48 | 0/120 | no | 0.69 | 0.67 | 0.64 | 0.25 | 14 | 14 | 14 | 15 | 12 | 12 | 0.75 | 0.74 | 0.75 | 0.75 | 3.95 | 3.91 | 3.91 | 3.89 | 0.000 / 0 | 0.000 / 0 | ceiling/control |
| simple | 1053 | 15/327 | 0/448 | yes | 0.19 | 0.16 | 0.13 | 0.28 | 5 | 5 | 4 | 8 | 4 | 4 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | paper-only |
| tak | 12 | 0/2 | 0/0 | no | 2.09 | 2.04 | 0.55 | 2.12 | 3 | 3 | 3 | 1 | 1 | 1 | 0.00 | -- | -- | -- | 3.61 | -- | -- | -- | 0.000 / 0 | 0.000 / 0 | timing-control |
| tsp | 493 | 0/26 | 0/19 | no | 0.14 | 0.14 | 0.11 | 0.14 | 11 | 11 | 6 | 11 | 7 | 7 | 3.40 | 3.54 | 3.49 | 3.48 | 7.55 | 5.67 | 5.61 | 5.61 | 0.339 / -- | 0.000 / -- | RSS/control |
| vliw | 3681 | 5/563 | 4/2133 | yes | 0.78 | 0.73 | 0.56 | 0.30 | 14 | 14 | 44 | 9 | 15 | 15 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | tool-benchmark-deferred |
| zebra | 313 | 2/50 | 0/288 | yes | 1.58 | 1.58 | 1.15 | 0.45 | 3 | 3 | 122 | 1 | 1066 | 1504 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | source/provenance-blocked |
| zern | 605 | 3/103 | 0/34 | yes | 0.80 | 0.80 | 0.52 | 0.30 | 6 | 5 | 5 | 11 | 4503 | 4503 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | paper-only |

## Paper-Style Combined Snapshot

This is the thesis table shape: paper-reported columns on the left, local
Scala Native port ratios on the right when a port exists. The local time and
RSS columns below use L1 final-clean rows. L2 GC numbers remain interpretation
evidence in `evidence/REML_COMPARISON_MATRIX.md`; they are not headline
timing.

| Program | Source/local status | Paper rg s | Paper r s | Paper MLton s | Paper rg RSS MB | Paper rg GC # | Local gc-heap L1 s | Best local checked/rooted mode | Best local L1 s | Local speedup | Local RSS ratio | Local GC interpretation | Evidence class |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---|---|
| DLX | source candidate found; no SN port | 0.14 | 0.12 | 0.40 | 8 | 3 | -- | -- | -- | -- | -- | -- | paper-reported |
| b-hut | source candidate found; Tier 2 planned | 0.67 | 0.63 | 0.14 | 5 | 471 | -- | -- | -- | -- | -- | -- | paper-reported |
| fft | Tier 1 SN port; too short locally | 0.64 | 0.51 | 0.26 | 69 | 10 | 0.02 | -- | -- | -- | -- | L2 reports no timed GC | SN port timing-control |
| fib37 | Tier 1 SN port; MLKit candidates are fib35 | 0.98 | 0.21 | 0.85 | 3 | 1 | 2.40 | `checked-region-stream` | 2.41 | 1.00x | 1.00x | L2 reports no timed GC | SN port compute/control |
| kbc | source/config still open | 0.21 | 0.19 | 0.07 | 10 | 10 | -- | -- | -- | -- | -- | -- | paper-reported |
| lexgen | source/config still open | 0.74 | 0.62 | 0.43 | 15 | 109 | -- | -- | -- | -- | -- | -- | paper-reported |
| life | Tier 1 SN port | 0.44 | 0.43 | 0.43 | 3 | 58 | 0.69 | `checked-region-stream` / `region-scoped-rooted` | 0.68 | 1.01x | 1.00x | L2 reports no timed GC | SN port compute/control |
| logic | Tier 2 SN port | 0.63 | 0.43 | 0.13 | 4 | 1843 | 1.27 | `checked-region-stream` | 1.27 | 1.00x | 8.32x | L2 heap GC `6.705 ms`; checked stream GC `1.288 ms`; scoped rows are slower/higher RSS | SN port L1 control |
| mandel | Tier 1 SN port; config differs and is too short locally | 0.53 | 0.38 | 0.31 | 3 | 1 | 0.06 | -- | -- | -- | -- | L2 reports no timed GC | SN port timing-control |
| mlyacc | source/config still open | 0.36 | 0.30 | 0.33 | 18 | 29 | -- | -- | -- | -- | -- | -- | paper-reported |
| mpuz | source candidate found; Tier 2 planned | 0.68 | 0.46 | 0.27 | 3 | 2 | -- | -- | -- | -- | -- | -- | paper-reported |
| msort-r | Tier 1 SN port | 0.69 | 0.47 | 0.93 | 116 | 16 | 2.25 | `checked-region-stream` | 2.05 | 1.10x | 0.26x | L2 heap GC `27.280 ms` to checked `6.005 ms` | SN port L1 |
| msort | Tier 1 SN port | 0.89 | 0.54 | 0.93 | 131 | 26 | 2.46 | `checked-region-stream` | 2.06 | 1.19x | 0.48x | L2 heap GC `27.180 ms` to checked `6.063 ms` | SN port L1 |
| nucleic | source candidate found; Tier 2 planned | 0.34 | 0.33 | 0.17 | 5 | 645 | -- | -- | -- | -- | -- | -- | paper-reported |
| prof | source candidate found; no SN port | 0.49 | 0.38 | 0.42 | 4 | 263 | -- | -- | -- | -- | -- | -- | paper-reported |
| ratio | Tier 1 SN port | 1.71 | 1.33 | 0.48 | 16 | 14 | 0.93 | `checked-region-scoped` | 0.91 | 1.02x | 0.20x | L2 heap GC `3.191 ms` to checked `0 ms` | SN port L1 |
| ray | Tier 2 SN port | 0.69 | 0.64 | 0.25 | 14 | 12 | 0.75 | `region-scoped-rooted` | 0.74 | 1.01x | 0.99x | L2 reports no timed GC | SN port L1 ceiling/control |
| simple | source candidate found; no SN port | 0.19 | 0.13 | 0.28 | 5 | 4 | -- | -- | -- | -- | -- | -- | paper-reported |
| tak | Tier 1 SN port; config differs and is too short locally | 2.09 | 0.55 | 2.12 | 3 | 1 | 0.00 | -- | -- | -- | -- | L2 reports no timed GC | SN port timing-control |
| tsp | Tier 2 SN port | 0.14 | 0.11 | 0.14 | 11 | 7 | 3.40 | `checked-region-scoped` | 3.48 | 0.98x | 0.74x | L2 heap GC `0.339 ms`; checked rows remove it but query CPU dominates | SN port L1 RSS/control |
| vliw | source/config still open | 0.78 | 0.56 | 0.30 | 14 | 15 | -- | -- | -- | -- | -- | -- | paper-reported |
| zebra | source/config still open | 1.58 | 1.15 | 0.45 | 3 | 1066 | -- | -- | -- | -- | -- | -- | paper-reported |
| zern | source candidate found; no SN port | 0.80 | 0.52 | 0.30 | 6 | 4503 | -- | -- | -- | -- | -- | -- | paper-reported |

## Interpretation

- The L1 final-clean rows confirm `msort` and `msort-r` as the meaningful local
  ReML-shaped allocation/list wins.
- `ratio` is a modest elapsed win but a strong RSS row in L1.
- `fib37` and `life` are near-tie compute/control rows; `tak`, `fft`, and
  `mandel` are too short at the current configuration for headline timing.
- The combined snapshot now uses L1 final-clean local timing/RSS for the local
  Scala Native ports. Use L2 only to explain GC behavior.
- `logic`, `ray`, and `tsp` now have Scala Native Tier 2 shaped-port L1/L2
  rows. They broaden the ReML comparison axis, but they do not add a new
  headline Rift win: `logic` is an elapsed tie with a large region RSS
  regression, `ray` is a near-tie control, and `tsp` is an RSS win with a small
  elapsed loss.
- Exact MLKit/ReML artifact reruns are gated/low-priority. The latest local
  check found no `mlkit` or `mlton` executable, and Docker was installed but
  the daemon was not available. Use `docs/REML_ARTIFACT_RUNBOOK.md` only if a
  raw same-machine cross-language timing claim becomes necessary.

## Same-Axes Thesis Interpretation Table

This table keeps the PLDI Figure 9 program list and paper axes visible while
adding local Scala Native evidence only where a port exists. It is the table to
use in the thesis discussion when explaining why Rift is better, worse, or not
yet comparable.

Status labels:

- `local-port`: local Scala Native shaped port with L1 and L2 rows.
- `timing-control`: local port exists but current scale is too short for a
  headline timing claim.
- `port-planned`: reasonable next local port candidate.
- `tool-benchmark-deferred`: large compiler/tool benchmark; defer until source
  and configuration provenance are clean.
- `source/provenance-blocked`: paper row retained, local source/config mapping
  not yet clean enough.
- `paper-only`: literature row only.

| Program | Paper axes | Paper time/RSS/GC anchor | Local Scala Native row | Local ratio | Local status | Why local Rift is better/worse or unavailable |
|---|---|---|---|---|---|---|
| DLX | loc `2841`; fcns `2/149`; inst `0/690`; delta yes | rg `0.14s`, r `0.12s`, MLton `0.40s`; rg RSS `8 MB`; rg GC `3` | -- | -- | source/provenance-blocked | Source candidate/provenance still not clean enough; no local claim. |
| b-hut | loc `1245`; fcns `2/140`; inst `0/459`; delta no | rg `0.67s`, r `0.63s`, MLton `0.14s`; rg RSS `5 MB`; rg GC `471` | -- | -- | port-planned | Interesting object/graph workload; local port deferred until source shape is mapped. |
| fft | loc `71`; fcns `0/9`; inst `0/34`; delta no | rg `0.64s`, r `0.51s`, MLton `0.26s`; rg RSS `69 MB`; rg GC `10` | local heap L1 `0.02s`, no useful best row | -- | timing-control | Current Scala Native scale is too short and not allocation-heavy enough; rescale before interpreting. |
| fib37 | loc `7`; fcns `0/1`; inst `0/0`; delta no | rg `0.98s`, r `0.21s`, MLton `0.85s`; rg RSS `3 MB`; rg GC `1` | heap `2.40s`; checked stream `2.41s`; RSS tied | `1.00x` | local-port | Compute/control workload; regions do not help because there is no meaningful allocation/GC pressure. |
| kbc | loc `679`; fcns `1/90`; inst `0/249`; delta yes | rg `0.21s`, r `0.19s`, MLton `0.07s`; rg RSS `10 MB`; rg GC `10` | -- | -- | source/provenance-blocked | Keep paper row only until source/config mapping is clean. |
| lexgen | loc `1322`; fcns `0/108`; inst `0/531`; delta no | rg `0.74s`, r `0.62s`, MLton `0.43s`; rg RSS `15 MB`; rg GC `109` | -- | -- | tool-benchmark-deferred | Tool/compiler-style benchmark; defer until exact input/configuration provenance is clear. |
| life | loc `202`; fcns `0/35`; inst `0/146`; delta no | rg `0.44s`, r `0.43s`, MLton `0.43s`; rg RSS `3 MB`; rg GC `58` | heap `0.69s`; checked/rooted `0.68s`; RSS tied | `1.01x` | local-port | Near-tie compute/control row; useful as ceiling evidence, not a memory win. |
| logic | loc `351`; fcns `0/22`; inst `0/806`; delta no | rg `0.63s`, r `0.43s`, MLton `0.13s`; rg RSS `4 MB`; rg GC `1843` | heap `1.27s`; checked stream `1.27s`; RSS `65.6 MB` vs heap `7.9 MB` | `1.00x`; RSS `8.32x` | local-port | Worse RSS because the current local port retains too much in one region; heap GC is small and query/control work dominates. |
| mandel | loc `62`; fcns `0/5`; inst `0/0`; delta no | rg `0.53s`, r `0.38s`, MLton `0.31s`; rg RSS `3 MB`; rg GC `1` | local heap L1 `0.06s`, no useful best row | -- | timing-control | Current configuration is too short and compute-heavy; no local memory-management claim. |
| mlyacc | loc `7385`; fcns `10/966`; inst `5/3256`; delta yes | rg `0.36s`, r `0.30s`, MLton `0.33s`; rg RSS `18 MB`; rg GC `29` | -- | -- | tool-benchmark-deferred | Large parser/compiler-style benchmark; defer until source/config provenance is clean. |
| mpuz | loc `124`; fcns `0/13`; inst `0/44`; delta no | rg `0.68s`, r `0.46s`, MLton `0.27s`; rg RSS `3 MB`; rg GC `2` | -- | -- | port-planned | Small search/allocation candidate; local port not implemented yet. |
| msort-r | loc `119`; fcns `0/14`; inst `0/27`; delta no | rg `0.69s`, r `0.47s`, MLton `0.93s`; rg RSS `116 MB`; rg GC `16` | heap `2.25s`; checked stream `2.05s`; RSS ratio `0.26x` | `1.10x` | local-port | Rift is better locally because linked allocation/list nodes have epochal lifetime; checked stream cuts RSS and reduces timed GC. |
| msort | loc `113`; fcns `0/13`; inst `0/22`; delta no | rg `0.89s`, r `0.54s`, MLton `0.93s`; rg RSS `131 MB`; rg GC `26` | heap `2.46s`; checked stream `2.06s`; RSS ratio `0.48x` | `1.19x` | local-port | Best local ReML-shaped win: allocation/list shape fits checked region lifetime and heap pays visible GC/RSS. |
| nucleic | loc `3215`; fcns `1/40`; inst `475/1273`; delta no | rg `0.34s`, r `0.33s`, MLton `0.17s`; rg RSS `5 MB`; rg GC `645` | -- | -- | port-planned | Potentially interesting object workload, but local source/config mapping is not implemented. |
| prof | loc `282`; fcns `0/57`; inst `0/99`; delta no | rg `0.49s`, r `0.38s`, MLton `0.42s`; rg RSS `4 MB`; rg GC `263` | -- | -- | paper-only | Keep as paper-reported literature row unless a clean source mapping is found. |
| ratio | loc `620`; fcns `0/54`; inst `0/848`; delta no | rg `1.71s`, r `1.33s`, MLton `0.48s`; rg RSS `16 MB`; rg GC `14` | heap `0.93s`; checked scoped `0.91s`; RSS ratio `0.20x` | `1.02x` | local-port | Rift is modestly faster and much lower RSS; elapsed win is small because heap GC is small. |
| ray | loc `529`; fcns `1/48`; inst `0/120`; delta no | rg `0.69s`, r `0.64s`, MLton `0.25s`; rg RSS `14 MB`; rg GC `12` | heap `0.75s`; rooted `0.74s`; RSS tied | `1.01x` | local-port | Near-tie compute/control row; region placement does not change much at current scale. |
| simple | loc `1053`; fcns `15/327`; inst `0/448`; delta yes | rg `0.19s`, r `0.13s`, MLton `0.28s`; rg RSS `5 MB`; rg GC `4` | -- | -- | paper-only | Keep as paper row; no local port currently planned. |
| tak | loc `12`; fcns `0/2`; inst `0/0`; delta no | rg `2.09s`, r `0.55s`, MLton `2.12s`; rg RSS `3 MB`; rg GC `1` | local heap L1 `0.00s`, no useful best row | -- | timing-control | Local configuration is too short/mismatched for comparison; rescale before interpreting. |
| tsp | loc `493`; fcns `0/26`; inst `0/19`; delta no | rg `0.14s`, r `0.11s`, MLton `0.14s`; rg RSS `11 MB`; rg GC `7` | heap `3.40s`; checked scoped `3.48s`; RSS ratio `0.74x` | `0.98x` | local-port | Rift is worse on elapsed but better on RSS; query CPU dominates and GC is tiny. |
| vliw | loc `3681`; fcns `5/563`; inst `4/2133`; delta yes | rg `0.78s`, r `0.56s`, MLton `0.30s`; rg RSS `14 MB`; rg GC `15` | -- | -- | tool-benchmark-deferred | Large tool/compiler-style workload; defer until source/config provenance is clean. |
| zebra | loc `313`; fcns `2/50`; inst `0/288`; delta yes | rg `1.58s`, r `1.15s`, MLton `0.45s`; rg RSS `3 MB`; rg GC `1066` | -- | -- | source/provenance-blocked | Paper row has many GC collections; local source/config mapping is not clean yet. |
| zern | loc `605`; fcns `3/103`; inst `0/34`; delta yes | rg `0.80s`, r `0.52s`, MLton `0.30s`; rg RSS `6 MB`; rg GC `4503` | -- | -- | paper-only | Keep as paper-reported row unless source/config is mapped later. |
