# Headline Core/Prior/Checked Sweep Rerun

Date: 2026-05-01

Run id: `2026-05-01-headline-core-prior-checked-rerun`

Status: completed rerun of the same headline subset after the user reduced
visible background work. Raw logs are in ignored local cache:

```text
/Users/siyaoliu/rift/cache/perf-eval/2026-05-01-headline-core-prior-checked-rerun/
```

## Command

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-headline-core-prior-checked-rerun \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight core prior checked" \
bash scripts/run-performance-evaluation.sh
```

## Environment

| Field | Value |
|---|---|
| Parent repo | `main` at `ec83b856f4bc0e61f3850e5a92a12d1e5b7df548` |
| Child repo | `feature/rift` at `b74658903584f30474f6ce0c1fec21164b95dbab` |
| Machine | Apple M4 Pro, 24 GiB RAM |
| OS | Darwin 25.4.0 arm64 |
| Java | Temurin 17.0.18 |
| Scale | `headline` |
| Suites | `preflight core prior checked` |

## Rerun Versus Previous Headline Subset

| Benchmark | Previous | Rerun | Interpretation |
|---|---:|---:|---|
| GCBench heap | `221.514 ms` | `211.413 ms` | Slightly faster. |
| GCBench improved SafeZone | `211.699 ms` | `219.924 ms` | Slightly slower. |
| GCBench HPZone | `245.217 ms` | `244.039 ms` | Stable; HPZone loss reproduces. |
| ListOfLists heap | `15842.502 ms` with one `746679.110 ms` outlier | `15165.020 ms`, no huge outlier | Environment/outlier improved. |
| ListOfLists improved SafeZone | `10046.087 ms` | `9853.992 ms` | Stable and fastest. |
| ListOfLists HPZone | `12579.297 ms` | `12210.485 ms` | Stable second place, faster than heap. |
| Flat ListOfLists HPZone | `1571.557 ms` | `1567.144 ms` | Stable Rift layout win. |
| Chunked ListOfLists improved SafeZone | `2436.207 ms` | `2422.792 ms` | Stable SafeZone win. |
| Pipeline heap | `36.234 ms` | `34.353 ms` | Stable CPU-bound ceiling. |
| Pipeline HPZone | `49.520 ms` | `46.296 ms` | Still loses. |

## Core Runtime / Topology

| Benchmark | Heap ms | Current SafeZone ms | Improved SafeZone ms | Rift HPZone ms | Interpretation |
|---|---:|---:|---:|---:|---|
| GCBench runtime | `211.413` | `654.988` | `219.924` | `244.039` | Heap is fastest in this rerun; HPZone loss reproduces. |
| ListOfLists linked | `15165.020` | `136551.538` | `9853.992` | `12210.485` | Rift beats heap but loses to improved SafeZone. |
| ListOfLists flat | `1749.780` | `1776.599` | `1767.838` | `1567.144` | Rift still wins on flat layout. |
| ListOfLists chunked | `2593.937` | `4974.217` | `2422.792` | `2632.361` | Improved SafeZone is fastest; Rift does not win. |
| Pipeline surrogate | `34.353` | `34.599` | `34.639` | `46.296` | CPU-bound ceiling; Rift loses. |

Topology detail:

| Topology | Current SafeZone ms | Improved SafeZone ms | Rift ms |
|---|---:|---:|---:|
| one region | `134159.000` | `9832.075` | `12045.723` |
| nested | `10018.693` | `9968.961` | `12129.641` |
| mixed rooted heap-values | `57780.887` | `9972.048` | `14229.352` |

## Prior-Work Methodology

### Broom/Dataflow-style

| Operator | Heap ms | Current SafeZone ms | Improved SafeZone ms | Rift HP ms | Rift Streaming ms | Checked ms | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| SELECT | `28.251` | `26.249` | `22.980` | `27.662` | `27.253` | `25.269` | Checked beats heap, but improved SafeZone is fastest. |
| AGGREGATE | `50.131` | `49.132` | `41.135` | `51.009` | `50.094` | `44.826` | Checked beats heap, but improved SafeZone is fastest. |
| JOIN | `20.938` | `25.896` | `23.226` | `27.172` | `27.258` | `25.141` | Heap wins. |

### StreamFlex-style

| Row | Heap | Current SafeZone | Improved SafeZone | Rift HP | Rift Streaming | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| throughput ms | `43.223` | `41.522` | `41.248` | `48.219` | `47.671` | SafeZone wins elapsed; Rift loses elapsed. |
| latency ms | `10.040` | `11.006` | `11.131` | `12.835` | `11.803` | Heap fastest elapsed, but heap has `4` deadline misses while region modes have `0`. |

### Yak-style

| Workload | Heap ms | Improved SafeZone ms | Rift Streaming ms | Yak-runtime ms | Interpretation |
|---|---:|---:|---:|---:|---|
| wordcount | `48.180` | `38.053` | `51.066` | `57.892` | Improved SafeZone wins. |
| graphstep | `48.251` | `41.009` | `53.069` | `59.841` | Improved SafeZone wins. |
| sort | `75.035` | `74.656` | `76.838` | `78.732` | Near CPU/sort ceiling. |
| topword | `69.661` | `60.907` | `70.945` | `76.720` | Improved SafeZone wins; Rift no longer beats heap in this rerun. |
| graphchi | `43.383` | `36.183` | `49.171` | `53.854` | Improved SafeZone wins. |
| promotion proxy | `82.154` | n/a | n/a | `130.175` | Dynamic barrier/promotion proxy remains negative. |

### Stancu-style

| Heap ms | Current SafeZone ms | Improved SafeZone ms | Rift HP ms | Rift Streaming ms | Interpretation |
|---:|---:|---:|---:|---:|---|
| `44.088` | `33.433` | `33.902` | `51.612` | `51.379` | SafeZone wins; Rift loses elapsed despite removing GC. |

## Checked Operators

| Benchmark | Heap ms | Checked / best Rift ms | Interpretation |
|---|---:|---:|---|
| RegionBuffer | `32.825` | checked `34.197` | Removes GC but no elapsed win. |
| PriorityQueue | `29.780` | checked `31.323` | Slight checked overhead. |
| IndexedPriorityQueue | `103.852` | checked `121.920` | Checked overhead remains material. |
| StreamWindowRank | `192.081` | checked `335.617` | Rank/window container overhead dominates. |
| AppendWindow manual | `36.526` | checked `32.460` | Strong checked win. |
| AppendWindow cursor API | `36.526` | cursor `48.171` | Cursor API loss reproduces in this rerun. |
| AppendWindow prepend cursor | heap-prepend `36.778` | prepend cursor `34.652` | Prepend cursor still wins its fair control. |
| WindowFold | `95.542` | checked `111.481` | Fold remains gated out. |

## Main Findings

- The obvious environmental outlier from the previous linked ListOfLists heap
  row disappeared.
- The main ranking changes did not reverse. GCBench HPZone still loses to heap
  and improved SafeZone, and linked ListOfLists HPZone still loses to improved
  SafeZone while beating heap.
- The clean checked story is now narrower: manual AppendWindow and prepend
  cursor are the clear wins; RegionBuffer, append cursor, rank, and fold do not
  clear speed gates in this environment.
- Prior-work methodology rows are mostly improved-SafeZone wins in this clean
  rerun. Rift still removes GC in many rows, but elapsed time is the stricter
  thesis gate.
