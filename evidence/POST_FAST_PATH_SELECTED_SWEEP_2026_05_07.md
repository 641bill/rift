# Post Fast-Path Selected Sweep, 2026-05-07

Last updated: 2026-05-07 13:51 CEST

Status: post-fast-path evidence pass from the current dirty page-token
checkpoint. This is not a clean commit-bound headline sweep. It is the first
selected 1M rerun after adding `StreamAppendCursor.nextOrNull()`,
page-token-owned batch close, and the monotonic current-bucket fast path.

Run directory:
`cache/perf-eval/2026-05-07-post-fast-path-selected/`

Relevant validation before/around this pass:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- `RiftRegionCheckedCompilerTest` passed `118/118`.
- `RiftRegionCheckedTest` passed `50/50`.

## Commands

Dataflow selected rows:

```sh
DATAFLOW_BENCHMARK_RUNS=3 \
DATAFLOW_OPERATOR=all \
DATAFLOW_MODES="heap improved-safezone rift-checked checked-page-token checked-page-token-scoped" \
DATAFLOW_OUTPUT_DIR="cache/perf-eval/2026-05-07-post-fast-path-selected/summaries/dataflow" \
zsh sandbox/run_dataflow_region_matrix.sh
```

NEXMark Beam-default selected rows:

```sh
NEXMARK_BEAM_DEFAULTS=1 \
NEXMARK_EVENTS=1000000 \
NEXMARK_BENCHMARK_RUNS=3 \
NEXMARK_WARMUPS=1 \
NEXMARK_QUERIES="q3 q8 q9 q11" \
NEXMARK_MODES="heap safezone-improved rift-checked" \
NEXMARK_OUTPUT_DIR="cache/perf-eval/2026-05-07-post-fast-path-selected/summaries/nexmark-beam-default" \
zsh sandbox/run_nexmark_region_matrix.sh
```

Generated Common Crawl-shaped page-token rows:

```sh
COMMON_CRAWL_WET_PAGES=1000000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=3 \
COMMON_CRAWL_WET_WARMUPS=1 \
COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window" \
COMMON_CRAWL_WET_MODES="heap-immix safezone-improved-32k rift-trusted-streaming rift-checked-page-token rift-checked-safezone-page-token" \
COMMON_CRAWL_WET_OUTPUT_DIR="cache/perf-eval/2026-05-07-post-fast-path-selected/summaries/common-crawl-page-token" \
zsh sandbox/run_common_crawl_wet_matrix.sh
```

DSPBench Fraud q2 source row:
`/tmp/dspbench-fraud-q2-page-token-fast-1m/summary.tsv` from the same
page-token fast-path checkpoint.

## Dataflow

Input: generated Broom/Dataflow-shaped workload, 10 epochs x 100k documents.
All checksums matched.

| Operator | Mode | Median ms | GC ms | Rift op ms | Interpretation |
|---|---|---:|---:|---:|---|
| SELECT | `heap` | `28.942` | `7.810` | `0.000` | heap baseline |
| SELECT | `improved-safezone` | `22.463` | `0.000` | `0.000` | rooted scoped baseline |
| SELECT | `rift-checked` | `20.661` | `0.000` | `0.186` | generic checked row |
| SELECT | `checked-page-token` | `19.503` | `0.000` | `0.054` | reusable page-token row |
| SELECT | `checked-page-token-scoped` | `18.572` | `0.000` | `0.000` | fastest SELECT row |
| AGGREGATE | `heap` | `52.071` | `10.300` | `0.000` | heap baseline |
| AGGREGATE | `improved-safezone` | `40.596` | `0.000` | `0.000` | rooted scoped baseline |
| AGGREGATE | `rift-checked` | `38.198` | `0.000` | `0.209` | exact-array checked aggregate, not `EpochFold` |
| JOIN | `heap` | `31.760` | `10.793` | `0.000` | variable heap row |
| JOIN | `improved-safezone` | `23.459` | `0.000` | `0.000` | fastest JOIN row in this selected pass |
| JOIN | `rift-checked` | `24.183` | `0.000` | `1.458` | checked still beats heap, but loses to improved SafeZone |

Interpretation: the page-token fast path remains a real reusable SELECT
operator win. AGGREGATE remains a checked exact-array win, not a reusable
`EpochFold` win. JOIN is a modest checked-vs-heap result in this run, but
improved SafeZone wins the same-run comparison.

## NEXMark Beam-Default

Input: Beam-default generated NEXMark profile, 1M events, 3 timed runs. These
are generated methodology rows, not exact Beam-runner evidence.

| Query | Heap ms / GC ms | Improved SafeZone ms / GC ms | Checked Rift ms / GC ms | RSS checked | Interpretation |
|---|---:|---:|---:|---:|---|
| q3 | `305.799` / `26.411` | `300.271` / `11.704` | `285.356` / `9.958` | `40.9 MB` | checked generated-methodology win |
| q8 | `466.964` / `33.120` | `452.158` / `16.571` | `443.020` / `15.250` | `77.3 MB` | checked modest win |
| q9 | `798.672` / `84.697` | `744.343` / `33.977` | `724.479` / `29.070` | `151.8 MB` | strongest selected NEXMark row |
| q11 | `215.910` / `17.208` | `227.575` / `5.485` | `209.918` / `3.706` | `81.3 MB` | checked wins elapsed and cuts GC |

Interpretation: the selected Beam-default generated stream controls remain
positive. The margins over improved SafeZone are modest, but checked Rift wins
all four selected queries in this same-run pass.

## Generated Common Crawl-Shaped Page-Token

Input: generated WET-shaped page/token stream, 1M generated pages, 3 timed
runs. This is a generated object-pressure detector, not real Common Crawl
input. All checksums/output counts matched.

| Query | Mode | Median ms | GC ms | Rift op ms | RSS bytes | Output count |
|---|---|---:|---:|---:|---:|---:|
| q1 tokenize | `heap-immix` | `5618.631` | `1655.357` | `0.000` | `408600576` | `137000000` |
| q1 tokenize | `safezone-improved-32k` | `4777.409` | `33.822` | `0.000` | `474693632` | `137000000` |
| q1 tokenize | `rift-trusted-streaming` | `4492.936` | `20.357` | `11.077` | `474497024` | `137000000` |
| q1 tokenize | `rift-checked-page-token` | `4069.265` | `20.486` | `8.402` | `463634432` | `137000000` |
| q1 tokenize | `rift-checked-safezone-page-token` | `3840.668` | `30.767` | `0.000` | `463650816` | `137000000` |
| q2 domain window | `heap-immix` | `5303.179` | `1599.698` | `0.000` | `408600576` | `929230` |
| q2 domain window | `safezone-improved-32k` | `4436.680` | `32.029` | `0.000` | `474759168` | `929230` |
| q2 domain window | `rift-trusted-streaming` | `4205.312` | `18.431` | `10.372` | `474071040` | `929230` |
| q2 domain window | `rift-checked-page-token` | `4041.548` | `17.698` | `8.173` | `463650816` | `929230` |
| q2 domain window | `rift-checked-safezone-page-token` | `3839.158` | `36.024` | `0.000` | `463765504` | `929230` |

Interpretation: this is the strongest current checked generated stream result.
The fast page-token path makes both checked rows faster than trusted Streaming,
and the SafeZone-backed checked page-token row is fastest overall on both q1
and q2. Heap still has lower RSS, so this is primarily an elapsed/GC win, not
an RSS win.

## DSPBench Fraud q2

Input: DSPBench Fraud Detection `credit-card.dat`, file-backed, 1M loaded
events from 185k unique lines with six replays. This is real-input evidence.

| Mode | Median ms | GC ms | RSS bytes | Output count | Interpretation |
|---|---:|---:|---:|---:|---|
| `heap-immix` | `862.834` | `79.393` | `358268928` | `594182` | heap baseline |
| `safezone-improved-32k` | `873.859` | `17.176` | `282509312` | `594182` | RSS/GC win, elapsed loss |
| `rift-trusted-streaming` | `834.447` | `11.632` | `282476544` | `594182` | trusted runtime win |
| `rift-checked-page-token` | `851.488` | `11.244` | `278413312` | `594182` | checked RSS/GC win, modest elapsed win vs heap |
| `rift-checked-safezone-page-token` | `818.574` | `17.265` | `278544384` | `594182` | fastest same-run real-input row |

Interpretation: Fraud q2 is now a modest real-input checked win after the
page-token fast path. It is not a huge GC-heavy flagship: heap GC is material
but only about 9% of elapsed. It is still the most promising real-input
checked stream row so far.

## Selection Consequences

- `checked-page-token` is stronger after the batch-close/current-bucket fast
  path. It now has focused, Dataflow SELECT, generated Common Crawl-shaped,
  and DSPBench Fraud q2 support.
- `checked-region-scoped` / SafeZone-backed page-token is the fastest checked
  backend for the generated Common Crawl-shaped q1/q2 and DSPBench Fraud q2
  rows in this selected pass.
- NEXMark remains a useful generated methodology control with modest checked
  wins, especially q9.
- This pass does not change the status of `EpochFold`, `TableRank`, chunk
  append, or rank-heavy operators. They remain gated or negative.
- Because this run was from a dirty checkpoint, a clean commit-bound selected
  headline rerun is still needed before final paper/presentation tables.
