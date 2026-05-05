# Comprehensive Sweep Checkpoint: 2026-05-05

Date: 2026-05-05
Last updated: 2026-05-05 20:52:18 CEST

Status: clean staged sweep checkpoint after introducing reusable checked
operator APIs. This is not a single monolithic all-suite run; it is a staged
clean sweep because core ListOfLists topology contains known pathological
current-SafeZone rows.

Source commits at run start:

| Repo | Commit |
|---|---|
| parent `rift` | `aab9a72` |
| child `scala-native-rift` | `acc748e80` |

## Run IDs

| Run id | Scale | Suites | Status |
|---|---|---|---|
| `2026-05-05-reusable-operators-preflight` | smoke | `preflight` | completed |
| `2026-05-05-reusable-operators-prior-checked-streams-smoke` | smoke | `prior checked streams` | completed |
| `2026-05-05-reusable-operators-core-smoke-small` | smoke | `core` | completed after fixing smoke ListOfLists dimensions |
| `2026-05-05-reusable-operators-prior-checked-headline` | headline, 3 runs | `prior checked` | completed |
| `2026-05-05-reusable-operators-streams-headline` | headline, 3 runs | `streams` | completed |

Interrupted/non-evidence runs:

| Run id | Reason not headline evidence |
|---|---|
| `2026-05-05-reusable-operators-smoke` | dirty-repo exploratory run, stopped early |
| `2026-05-05-reusable-operators-core-smoke` | launched large ListOfLists topology despite smoke scale; stopped in pathological current SafeZone row |

## Reusable Operator Validation

The reusable API implementation checkpoint is in child commit `acc748e80`.

Validation before the sweep:

```sh
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"
```

Result: compile passed, compiler probes `106/106`, runtime checked tests
`47/47`.

## Key Headline Rows

### Dataflow SELECT And AGGREGATE

Source:
`cache/perf-eval/2026-05-05-reusable-operators-prior-checked-headline/logs/dataflow.log`.

| Operator | Mode | Median ms | Median GC ms | Interpretation |
|---|---|---:|---:|---|
| SELECT | heap | `27.9-28 ms` class | about `6-7 ms` | baseline |
| SELECT | `checked-page-token` (`PageTokenMapFilter`) | `20.129` | `0.000` | reusable page-token SELECT remains fast |
| SELECT | scoped `checked-page-token` | `18.685` | `0.000` | fastest SELECT row |
| AGGREGATE | current checked exact-array path | `39.759` | `0.000` | still the good checked aggregate control |
| AGGREGATE | true reusable `EpochFold` | `94.378` | `2.114` | correct but failed speed gate |

Interpretation: `PageTokenMapFilter` is a successful reusable API. `EpochFold`
is a negative/gated reusable API; do not use it for application claims yet.

### Checked Append/Page-Token Operator

Source:
`cache/perf-eval/2026-05-05-reusable-operators-prior-checked-headline/summaries/checked-append-window/summary.tsv`.

| Mode | Median ms | Median GC ms | RSS bytes | Interpretation |
|---|---:|---:|---:|---|
| `heap-immix` | `37.490` | `11.053` | `75071488` | heap pays GC |
| `rift-checked-rift` | `32.137` | `0.000` | `47579136` | checked generic cursor path |
| `rift-checked-page-token` | `28.341` | `0.000` | `47579136` | operator-owned fast path |
| `rift-checked-safezone-page-token` | `27.004` | `0.000` | `47448064` | fastest focused checked append row |

### Object Allocation Lowering

Source:
`cache/perf-eval/2026-05-05-reusable-operators-prior-checked-headline/summaries/object-allocation-lowering/summary.tsv`.

| Mode | Median ms | Median GC ms | RSS bytes | Interpretation |
|---|---:|---:|---:|---|
| `heap-immix` | `20.797` | `6.108` | `63815680` | heap already collects at 1M |
| `rift-trusted-hp` | `20.262` | `0.069` | `43827200` | trusted region allocation roughly ties heap elapsed with lower RSS |
| `rift-checked-rift` | `16.734` | `0.000` | `43532288` | checked retained-array shape beats heap |
| `rift-checked-safezone-improved-32k` | `15.166` | `0.000` | `43810816` | fastest allocation-lowering row |

Interpretation: raw checked allocation is not the main bottleneck for this
shape; generic containers/operators are.

### Common Crawl WET-Shaped Page/Token

Source:
`cache/perf-eval/2026-05-05-reusable-operators-streams-headline/summaries/common-crawl-page-token/summary.tsv`.

| Query | Mode | Median ms | Median GC ms | Output count | Interpretation |
|---|---|---:|---:|---:|---|
| q1 tokenization | `heap-immix` | `5313.928` | `1517.397` | `137000000` | GC-heavy generated stream stressor |
| q1 tokenization | `safezone-improved-32k` | `4506.594` | `30.383` | `137000000` | rooted scoped region win over heap |
| q1 tokenization | `rift-trusted-hp` | `4301.937` | `24.181` | `137000000` | trusted Rift win over SafeZone |
| q1 tokenization | `rift-checked-page-token` | `3856.625` | `19.479` | `137000000` | checked fast path clears gate |
| q1 tokenization | scoped `checked-page-token` | `3654.143` | `29.394` | `137000000` | fastest q1 row |
| q2 domain window | `heap-immix` | `5250.408` | `1628.382` | `929230` | GC-heavy generated stream stressor |
| q2 domain window | `safezone-improved-32k` | `4342.934` | `29.533` | `929230` | rooted scoped region win over heap |
| q2 domain window | `rift-trusted-hp` | `4125.546` | `21.255` | `929230` | trusted Rift win over SafeZone |
| q2 domain window | `rift-checked-page-token` | `3927.449` | `18.313` | `929230` | checked fast path clears gate |
| q2 domain window | scoped `checked-page-token` | `3713.483` | `28.845` | `929230` | fastest q2 row |

Interpretation: this is now the strongest generated stream evidence. It shows
large heap GC time and a real checked operator win. Caveat: the input is
generated WET-shaped, not real Common Crawl data.

### NEXMark Beam-Default Methodology

Source:
`cache/perf-eval/2026-05-05-reusable-operators-streams-headline/summaries/nexmark-beam-default/summary.tsv`.

| Query | Heap ms | Improved SafeZone ms | Checked Rift ms | Best interpretation |
|---|---:|---:|---:|---|
| q3 | `288.108` | `293.091` | `278.455` | checked Rift wins modestly |
| q8 | `452.716` | `441.159` | `429.087` | checked Rift wins modestly |
| q9 | `768.000` | `738.177` | `711.256` | checked Rift wins modestly |
| q11 | `215.050` | `224.467` | `211.000` | near tie / small checked win |

Interpretation: NEXMark remains generated methodology evidence. It supports
the stream-region direction, but not a dramatic GC-heavy real-data claim.

### GH Archive Shaped Stream

Source:
`cache/perf-eval/2026-05-05-reusable-operators-streams-headline/summaries/github-archive/summary.tsv`.

| Query | Mode | Heap cap | Median ms | Median GC ms | RSS bytes | Interpretation |
|---|---|---|---:|---:|---:|---|
| q1 fields | `heap-immix` | uncapped | `284.689` | `78.496` | `206487552` | heap is fastest but pays GC/RSS |
| q1 fields | `rift-trusted-hp` | uncapped | `246.205` | `2.252` | `44761088` | trusted region win in this generated-shaped row |
| q1 fields | `rift-checked-page-token` | uncapped | `250.705` | `2.347` | `44793856` | checked page-token also wins |
| q1 fields | scoped `checked-page-token` | uncapped | `287.511` | `54.049` | `44875776` | SafeZone-backed checked is not best here |

Interpretation: current headline runner used generated GH Archive-shaped input
unless real files are supplied. The earlier real 8-hour input remains a
memory-budget/tail-latency candidate, not yet a clean uncapped throughput win.

### Other Stream Candidates

| Benchmark | Representative row | Interpretation |
|---|---|---|
| Yahoo q2 campaign window | heap `107.871 ms`, Rift HP `104.877 ms`, improved SafeZone `105.895 ms` | small generated win, not a large GC-heavy case |
| RIoTBench q1 clean/annotate | heap `132.252 ms`, Rift HP `138.693 ms`, improved SafeZone `145.869 ms` | heap elapsed still best; region rows reduce GC/RSS but do not win |
| Linear Road q1 tolls | heap `179.883 ms`, improved SafeZone `184.512 ms`, Rift HP `182.112 ms` | ceiling/control row |
| Wikimedia q1 counts | heap `155.223 ms`, Rift HP `147.442 ms`, improved SafeZone `152.381 ms` | small generated TSV-shaped win |

## Core Smoke Fix

The parent runner now passes explicit ListOfLists smoke dimensions:

- smoke: `LISTBENCH_N=200`, `LISTBENCH_STRUCTURES=1`;
- headline/full: defaults remain `LISTBENCH_N=3000`,
  `LISTBENCH_STRUCTURES=40`.

The fixed core smoke run completed. Core headline rows are still best taken
from the 2026-05-01 clean core rerun unless a separate long core job is
intentionally launched.

## Current Conclusions

- The reusable API milestone is real: `PageTokenMapFilter` and `RegionList`
  are not benchmark-local one-offs.
- Post-sweep follow-up added `EpochBuffer` as the next reusable checked
  operator. Its focused 1M epoch append/drain row is positive:
  `rift-checked-safezone-epoch-buffer` `25.448 ms` and
  `rift-checked-epoch-buffer` `26.673 ms` versus `heap-epoch` `27.164 ms` with
  `5.707 ms` GC. This is focused operator evidence, not an application row.
- `EpochFold` is correct but currently too slow, so fold-style reusable APIs
  need a lower-overhead representation before application use.
- The strongest current win remains generated Common Crawl WET-shaped q1/q2
  with checked page-token, especially the scoped backend variant.
- Real-input GC-heavy stream proof remains open. GH Archive and real WET/WAT
  controls are useful, but current clean headline rows do not yet settle that
  case.
- Full core headline should remain a separate long-running job because current
  SafeZone root-mode-0 topology rows are intentionally pathological.
