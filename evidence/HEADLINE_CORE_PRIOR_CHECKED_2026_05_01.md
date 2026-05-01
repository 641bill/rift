# Headline Core/Prior/Checked Sweep

Date: 2026-05-01

Run id: `2026-05-01-headline-core-prior-checked`

Status: completed clean headline subset. Raw logs are in ignored local cache:

```text
/Users/siyaoliu/rift/cache/perf-eval/2026-05-01-headline-core-prior-checked/
```

## Command

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-headline-core-prior-checked \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight core prior checked" \
bash scripts/run-performance-evaluation.sh
```

## Environment

| Field | Value |
|---|---|
| Parent repo | `main` at `e5748938c3788a1f827473c5a4cc312af7965eac` |
| Child repo | `feature/rift` at `b74658903584f30474f6ce0c1fec21164b95dbab` |
| Machine | Apple M4 Pro, 24 GiB RAM |
| OS | Darwin 25.4.0 arm64 |
| Java | Temurin 17.0.18 |
| Scale | `headline` |
| Suites | `preflight core prior checked` |

## Core Runtime / Topology

| Benchmark | Heap ms | Current SafeZone ms | Improved SafeZone ms | Rift HPZone ms | Interpretation |
|---|---:|---:|---:|---:|---|
| GCBench runtime | `221.514` | `654.894` | `211.699` | `245.217` | This clean row does not reproduce the older HPZone GCBench win; improved SafeZone is fastest. |
| ListOfLists linked | `15842.502` | `137223.310` | `10046.087` | `12579.297` | Rift beats heap but loses to improved SafeZone; current SafeZone remains pathological. |
| ListOfLists flat | `1770.286` | `1796.581` | `1818.396` | `1571.557` | Rift still wins on flat layout. |
| ListOfLists chunked | `2603.868` | `5097.474` | `2436.207` | `2685.155` | Improved SafeZone is fastest; Rift does not win. |
| Pipeline surrogate | `36.234` | `34.570` | `34.966` | `49.520` | CPU-bound/ceiling control; Rift loses. |

Topology detail:

| Topology | Current SafeZone ms | Improved SafeZone ms | Rift ms |
|---|---:|---:|---:|
| one region | `144394.417` | `10334.627` | `13338.288` |
| nested | `10551.999` | `10566.096` | `13066.825` |
| mixed rooted heap-values | `60782.826` | `10704.602` | `14895.419` |

## Prior-Work Methodology

### Broom/Dataflow-style

| Operator | Heap ms | Current SafeZone ms | Improved SafeZone ms | Rift HP ms | Rift Streaming ms | Checked ms | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| SELECT | `32.769` | `25.997` | `23.550` | `27.947` | `27.806` | `28.020` | Checked beats heap but loses to improved SafeZone. |
| AGGREGATE | `54.748` | `51.056` | `43.695` | `50.904` | `55.168` | `48.383` | Checked beats heap but loses to improved SafeZone. |
| JOIN | `22.067` | `26.161` | `24.013` | `27.358` | `27.552` | `26.089` | Heap wins in this run. |

### StreamFlex-style

| Row | Heap | Current SafeZone | Improved SafeZone | Rift HP | Rift Streaming | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| throughput ms | `43.724` | `41.380` | `41.160` | `48.252` | `47.574` | SafeZone wins elapsed; Rift loses elapsed. |
| latency ms | `10.022` | `10.858` | `11.460` | `12.966` | `12.090` | Heap fastest elapsed, but heap has `4` deadline misses while region modes have `0`. |

### Yak-style

| Workload | Heap ms | Improved SafeZone ms | Rift Streaming ms | Yak-runtime ms | Interpretation |
|---|---:|---:|---:|---:|---|
| wordcount | `49.704` | `39.233` | `50.874` | `56.883` | Improved SafeZone wins. |
| graphstep | `49.762` | `41.722` | `52.798` | `59.213` | Improved SafeZone wins. |
| sort | `76.915` | `76.143` | `77.795` | `78.267` | Near CPU/sort ceiling. |
| topword | `71.906` | `61.001` | `69.429` | `77.409` | Rift beats heap modestly, loses to improved SafeZone. |
| graphchi | `44.427` | `36.538` | `48.443` | `54.537` | Improved SafeZone wins. |
| promotion proxy | `84.404` | n/a | n/a | `129.926` | Dynamic barrier/promotion proxy remains negative. |

### Stancu-style

| Heap ms | Current SafeZone ms | Improved SafeZone ms | Rift HP ms | Rift Streaming ms | Interpretation |
|---:|---:|---:|---:|---:|---|
| `44.313` | `34.216` | `33.747` | `51.875` | `52.211` | SafeZone wins; Rift loses elapsed despite removing GC. |

## Checked Operators

| Benchmark | Heap ms | Checked / best Rift ms | Interpretation |
|---|---:|---:|---|
| RegionBuffer | `33.326` | checked `34.485` | Removes GC but no elapsed win in this clean run. |
| PriorityQueue | `29.641` | checked `30.612` | Slight checked overhead. |
| IndexedPriorityQueue | `102.433` | checked `119.609` | Checked overhead remains material. |
| StreamWindowRank | `205.320` | checked `356.931` | Rank/window container overhead dominates. |
| AppendWindow manual | `38.671` | checked `33.754` | Strongest checked win in this subset. |
| AppendWindow cursor API | `38.671` | cursor `48.480` | This clean row does not reproduce the earlier cursor API win. |
| AppendWindow prepend cursor | heap-prepend `37.642` | prepend cursor `35.523` | Prepend cursor still wins its fair heap-prepend control. |
| WindowFold | `98.279` | checked `116.049` | Fold remains gated out; trusted Rift is near heap but not a checked win. |

## Main Findings

- This run is a necessary correction to the evidence pack: several older
  positive rows do not reproduce under the clean headline subset.
- Improved SafeZone is the strongest competitor in more places than the older
  seeded summary implied.
- Rift still has useful rows: flat ListOfLists, checked/manual AppendWindow,
  prepend cursor, and heap-vs-Rift reductions in GC/RSS in focused operators.
- The best current research direction remains cheaper checked stream/window
  operators and broader GC-heavy stream candidates, not claiming that the
  runtime wins everywhere.
- Future headline runs should split pathological current-SafeZone ListOfLists
  rows into a separate job. They are valid but dominate wall-clock time.

## Caveats

- Raw logs are local and ignored by git; this file is the tracked summary.
- This run did not include `streams` or `debs`; those remain separate headline
  jobs.
- Several scripts are older sbt-driven runners rather than cached-native-binary
  runners, so wall-clock evaluation time is high.
