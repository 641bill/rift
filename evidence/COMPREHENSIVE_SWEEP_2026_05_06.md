# Comprehensive Staged Headline Sweep - 2026-05-06

Last updated: 2026-05-06 00:55 CEST

Status: completed staged headline sweep. This file supersedes the
2026-05-05 reusable-operator checkpoint for prior-work, checked-operator, and
stream/application rows. Core runtime/topology headline rows remain from the
earlier clean core runs unless explicitly listed here.

## Run Provenance

Primary run:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-05-comprehensive-headline \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_RUNS=3 \
RIFT_EVAL_SUITES="preflight prior checked safezone-cost streams" \
bash scripts/run-performance-evaluation.sh
```

This run completed `preflight`, `prior`, and `checked`. It was stopped after
entering the first unwanted `current-safezone` row inside the SafeZone-cost
suite. The completed prior/checked logs are valid; the partial SafeZone-cost
log from this run is not headline evidence.

Continuation run:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-05-comprehensive-headline-cont \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_RUNS=3 \
RIFT_EVAL_SUITES="safezone-cost streams" \
SAFEZONE_COST_CONFIGS="improved-default:1: chunk-default:2: unsafe-hp-32k:3:32768 improved-32k:1:32768" \
bash scripts/run-performance-evaluation.sh
```

Both runs used:

| Field | Value |
|---|---|
| Parent repo | `/Users/siyaoliu/rift` |
| Parent commit | `10da348b22ea165f41656bbb34222ab9bcf56ff8` |
| Child repo | `/Users/siyaoliu/rift/scala-native-rift` |
| Child commit | `34f4fb57c55a63883140ffae0771178d440b32f2` |
| Branches | parent `main`, child `feature/rift` |
| Machine | Apple M4 Pro, 24 GiB RAM |
| OS | Darwin 25.4.0 arm64 |
| Java | Temurin 17.0.18 |

Competitive stream/prior rows skip `current-safezone` by default. The
continuation SafeZone-cost rows also exclude `current-default`; root-mode 0
remains available only as historical/provenance evidence.

## Main Findings

| Finding | Evidence |
|---|---|
| Checked page-token is now the strongest checked application-shaped path. | Generated Common Crawl-shaped q1: checked SafeZone-backed page-token `3696.284 ms`, checked Rift page-token `3905.285 ms`, heap `5350.531 ms`. |
| Generated Common Crawl-shaped q1/q2 is the clearest GC-heavy stream detector. | Heap q1 GC `1517.640 ms`; heap q2 GC `1526.751 ms`; region rows cut that to roughly `19-32 ms`. |
| NEXMark Beam-default is broadly favorable but modest. | `rift-checked` is fastest on q0/q1/q2/q3/q4/q5/q8/q9/q11, but most wins are small. |
| TransactionRegion is the best checked StreamFlex shape so far. | Scoped checked TransactionRegion throughput `39.019 ms`, faster than heap `42.860 ms` and improved SafeZone `41.327 ms`; trusted Rift remains fastest at `36.436 ms`. |
| Object allocation lowering is no longer the obvious bottleneck in the clean focused shape. | Checked SafeZone-backed allocation `14.903 ms`, checked Rift `16.039 ms`, heap `21.885 ms` at 1M retained objects. |
| Table/rank remains a negative checked-container control. | Checked stream-window rank `344.918 ms` versus heap `227.736 ms`. |
| Some realistic stream probes are still ceiling controls. | Linear Road heap is fastest or tied; Yahoo/RioT/Wikimedia rows are mostly small-GC/near-tie rows. |

## Prior-Work Methodology

### Dataflow

Source: `cache/perf-eval/2026-05-05-comprehensive-headline/logs/dataflow.log`.

| Query / mode | Median ms | GC ms | Rift op ms | Interpretation |
|---|---:|---:|---:|---|
| SELECT heap | `29.347` | `7.304` | `0.000` | heap baseline |
| SELECT improved SafeZone | `23.896` | `0.000` | `0.000` | rooted scoped baseline |
| SELECT rootless SafeZone | `23.587` | `0.000` | `0.000` | unsafe lower bound |
| SELECT Rift HP | `23.318` | `0.000` | `0.065` | trusted Rift backend |
| SELECT checked Rift | `20.832` | `0.000` | `0.192` | checked beats trusted rows here |
| SELECT checked page-token | `20.479` | `0.000` | `0.063` | reusable checked fast path |
| SELECT checked scoped page-token | `18.458` | `0.000` | `0.000` | best SELECT row |
| AGGREGATE heap | `53.677` | `11.080` | `0.000` | heap baseline |
| AGGREGATE improved SafeZone | `42.650` | `0.000` | `0.000` | rooted scoped baseline |
| AGGREGATE rootless SafeZone | `42.227` | `0.000` | `0.000` | unsafe lower bound |
| AGGREGATE checked Rift | `40.098` | `0.000` | `0.289` | current checked exact-array aggregate remains good |
| AGGREGATE checked EpochFold | `92.923` | `1.968` | `0.131` | true reusable fold is still speed-gated |
| JOIN heap | `33.438` | `11.410` | `0.000` | heap baseline |
| JOIN improved SafeZone | `23.846` | `0.000` | `0.000` | best safe baseline |
| JOIN checked Rift | `21.607` | `0.000` | `0.151` | checked beats heap and SafeZone in this rerun |

### StreamFlex

Source: `cache/perf-eval/2026-05-05-comprehensive-headline/summaries/streamflex/summary.tsv`.

| Workload | Mode | Median ms | Region objects | Deadline misses |
|---|---|---:|---:|---:|
| throughput | Rift HP | `36.436` | `2499843` | |
| throughput | Rift Streaming | `36.516` | `2499843` | |
| throughput | checked scoped TransactionRegion | `39.019` | `0` | |
| throughput | improved SafeZone | `41.327` | `0` | |
| throughput | heap | `42.860` | `0` | |
| throughput | checked TransactionRegion | `45.620` | `2499843` | |
| throughput | checked EpochBuffer | `47.934` | `2499843` | |
| latency | Rift Streaming | `9.818` | `499789` | `0` |
| latency | heap | `9.838` | `0` | `4` |
| latency | checked scoped TransactionRegion | `13.162` | `0` | `1` |
| latency | checked scoped EpochBuffer | `22.720` | `0` | `4` |

Interpretation: TransactionRegion is the right checked shape for multi-stage
batch pipelines; stacked EpochBuffer is the wrong granularity.

### Yak And Stancu-Shaped Rows

Source: `cache/perf-eval/2026-05-05-comprehensive-headline/summaries/yak/summary.tsv`
and `.../stancu/summary.tsv`.

| Workload | Fastest row | Heap row | Interpretation |
|---|---:|---:|---|
| Yak wordcount | rootless SafeZone `38.292 ms` | `48.438 ms` | SafeZone-family substrate win |
| Yak topword | rootless SafeZone `61.388 ms` | `72.894 ms` | SafeZone-family substrate win |
| Yak graphchi | rootless SafeZone `36.189 ms` | `41.742 ms` | SafeZone-family substrate win |
| Yak sort | heap `75.984 ms` | `75.984 ms` | CPU/container ceiling |
| Yak promotion proxy | heap `87.467 ms` | `87.467 ms` | runtime-promotion proxy remains negative |
| Stancu transactions | rootless SafeZone `36.018 ms` | `45.029 ms` | scoped-region boundary win |

## Checked Operator Costs

### Object Allocation Lowering

Source: `cache/perf-eval/2026-05-05-comprehensive-headline/summaries/object-allocation-lowering/summary.tsv`.

| Mode | Median ms | GC ms | Rift op ms |
|---|---:|---:|---:|
| checked SafeZone-backed | `14.903` | `0.000` | `0.000` |
| checked Rift | `16.039` | `0.000` | `0.042` |
| trusted Rift HP | `19.571` | `0.000` | `0.039` |
| trusted Rift Streaming | `19.790` | `0.000` | `0.041` |
| heap | `21.885` | `0.000` | `0.000` |

Interpretation: in the focused retained-object shape, checked allocation is
not the remaining bottleneck. Generic containers and application traversal are
more important.

### Append / Page-Token

Source: `cache/perf-eval/2026-05-05-comprehensive-headline/summaries/checked-append-window/summary.tsv`.

| Mode | Median ms | GC ms | Rift op ms |
|---|---:|---:|---:|
| checked scoped EpochBuffer | `26.461` | `0.000` | `0.000` |
| checked scoped page-token | `26.883` | `0.000` | `0.000` |
| checked EpochBuffer | `27.519` | `0.000` | `0.066` |
| checked page-token | `27.886` | `0.000` | `0.070` |
| current checked append | `28.365` | `0.000` | `0.070` |
| heap epoch | `30.183` | `6.070` | `0.000` |
| heap Immix | `36.944` | `10.900` | `0.000` |
| trusted Rift Streaming | `39.725` | `0.000` | `0.077` |

Interpretation: cheap operator-owned checked paths beat heap; exact shape
matters more than generic "region allocation".

### Negative Checked Controls

| Matrix | Heap | Checked | Interpretation |
|---|---:|---:|---|
| StreamWindowRank | `227.736 ms` | `344.918 ms` | rank/index maintenance still dominates |
| WindowFold | `97.230 ms` | `97.081 ms` | near tie, but not a strong win |

## Stream / Application Rows

### NEXMark Beam-Default

Source: `cache/perf-eval/2026-05-05-comprehensive-headline-cont/summaries/nexmark-beam-default/summary.tsv`.

| Query | Heap ms / GC | Fastest row | Interpretation |
|---|---:|---:|---|
| q0 | `509.871` / `76.936` | checked Rift `457.274` | checked win |
| q1 | `936.755` / `89.865` | checked Rift `880.309` | checked win |
| q2 | `584.562` / `65.214` | checked Rift `534.910` | checked win |
| q3 | `287.568` / `16.303` | checked Rift `282.629` | modest checked win |
| q4 | `558.816` / `37.766` | checked Rift `555.929` | near-tie win |
| q5 | `392.515` / `26.645` | checked Rift `374.551` | checked win |
| q8 | `452.128` / `30.766` | checked Rift `432.391` | checked win |
| q9 | `779.032` / `78.555` | checked Rift `708.391` | checked win |
| q11 | `214.492` / `17.244` | checked Rift `210.212` | near-tie win |

Interpretation: NEXMark Beam-default is broad generated methodology evidence.
It is favorable to checked Rift in this sweep, but most rows are modest.

### Generated Common Crawl WET-Shaped

Source: `cache/perf-eval/2026-05-05-comprehensive-headline-cont/summaries/common-crawl-page-token/summary.tsv`.

| Query / mode | Median ms | GC ms | Rift op ms | Output count |
|---|---:|---:|---:|---:|
| q1 heap | `5350.531` | `1517.640` | `0.000` | `137000000` |
| q1 checked SafeZone page-token | `3696.284` | `29.341` | `0.000` | `137000000` |
| q1 checked Rift page-token | `3905.285` | `19.901` | `7.840` | `137000000` |
| q1 trusted Rift HP | `4265.969` | `19.659` | `10.038` | `137000000` |
| q1 current checked Rift | `4786.499` | `19.628` | `9.916` | `137000000` |
| q2 heap | `5183.656` | `1526.751` | `0.000` | `929230` |
| q2 checked SafeZone page-token | `3732.171` | `30.514` | `0.000` | `929230` |
| q2 checked Rift page-token | `3972.493` | `19.508` | `7.807` | `929230` |
| q2 trusted Rift Streaming | `4109.290` | `19.080` | `10.439` | `929230` |
| q2 current checked Rift | `4713.524` | `20.080` | `10.077` | `929230` |

Interpretation: this is the strongest current checked stream result. It is a
generated WET-shaped stressor, not real Common Crawl proof.

The broad generated Common Crawl q3 parser-scratch row is a negative control:
heap is `10188.412 ms` with `961.503 ms` GC; SafeZone-family rows can be much
slower, so q3 should not be tuned into a claim without a better parser/scratch
ownership design.

### Other Stream Probes

| Benchmark | Fastest row | Heap row | Interpretation |
|---|---:|---:|---|
| Yahoo q2 campaign window | heap `101.722 ms` | `101.722 ms` | low-GC/near-tie ceiling; region reduces RSS but not elapsed |
| RIoTBench q1 clean/annotate | heap `135.876 ms` | `135.876 ms` | heap fastest despite lower region GC |
| RIoTBench q2 window stats | Rift HP/rootless SafeZone `166.837 ms` | `169.846 ms` | modest region win |
| Wikimedia q1 counts | Rift Streaming `148.157 ms` | `154.105 ms` | modest generated TSV-shaped win |
| Wikimedia q2 clickstream | Rift HP `151.177 ms` | `159.476 ms` | modest generated TSV-shaped win |
| Linear Road q1 tolls | heap `179.487 ms` | `179.487 ms` | region rows remove GC but lose elapsed/RSS |
| Linear Road q2 accidents | heap `194.557 ms` | `194.557 ms` | near tie; ceiling/control |
| GH Archive q1 | Rift Streaming `246.174 ms` | heap uncapped `286.721 ms`; heap 1G `286.025 ms` | generated GH-shaped row favors trusted Rift/page-token |
| GH Archive q2 | Rift HP `233.427 ms` | heap uncapped `268.717 ms`; heap 1G `257.148 ms` | generated GH-shaped row favors trusted Rift/page-token |

## SafeZone Cost Decomposition

Source: `cache/perf-eval/2026-05-05-comprehensive-headline-cont/summaries/safezone-cost/summary.tsv`.

These rows run with `SAFEZONE_TRACE=1`, so elapsed times are diagnostic, not
headline throughput results.

| Benchmark / config | Median ms | Claim ms | Reclaim ms | Root add+remove ms | Interpretation |
|---|---:|---:|---:|---:|---|
| GCBench unsafe 32K | `697.984` | `0.977` | `1.321` | `0.000` | rootless lower bound |
| GCBench improved 32K | `703.092` | `2.556` | `1.326` | `1.596` | close to rootless |
| GCBench improved default | `706.871` | `9.286` | `5.966` | `5.484` | page-size/config cost visible |
| ListOfLists linked improved 32K | `32837.097` | `93.615` | `60.867` | `58.205` | faster than rootless here |
| ListOfLists linked rootless 32K | `33588.729` | `31.243` | `52.382` | `0.000` | root work gone, total still dominated elsewhere |
| Common Crawl q1 improved 32K | `8443.875` | `54.623` | `42.836` | `45.283` | trace-mode diagnostic |
| Common Crawl q1 rootless 32K | `8459.317` | `16.318` | `31.718` | `0.000` | rootless does not improve total in trace mode |

Interpretation: root removal was the old cliff, but after improved roots and
32K pages the remaining cost is not just root registration. Avoiding root work
helps, but object/query/topology behavior still dominates many rows.

## Caveats

- This is a staged sweep, not a single monolithic completed `all` run.
- The first run was intentionally stopped after entering unwanted
  `current-safezone` inside SafeZone-cost; only completed compile/prior/checked
  logs from that run are used.
- Core runtime/topology long rows were not rerun in this pass because current
  SafeZone core scripts are still expensive and already documented.
- NEXMark/Yahoo/RioT/Wikimedia/GH Archive rows here are generated or
  methodology-shaped unless explicitly labeled otherwise.
- Generated Common Crawl WET-shaped q1/q2 is the current memory-pressure
  detector, not a real-data proof.
