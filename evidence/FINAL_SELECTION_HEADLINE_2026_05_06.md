# Final Selection Headline Sweep, 2026-05-06

Last updated: 2026-05-06 15:57 CEST

Status: clean-run final-selection evidence. This run uses the new default
public/candidate mode lists, with current SafeZone and rootless/trusted
lower-bound controls excluded.

Run directory:
`cache/perf-eval/2026-05-06-final-selection-headline/`

Command:

```bash
RIFT_EVAL_RUN_ID=2026-05-06-final-selection-headline \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight core prior checked streams reml" \
bash scripts/run-performance-evaluation.sh
```

Environment:

| Field | Value |
|---|---|
| Parent repo | `main` at `72dc1dfb974cc1620dc950a8ff2fb104233ec8b0` |
| Child repo | `feature/rift` at `458c556d20698887d753fc29969847dc29ac8cb4` |
| Controls | `include_controls=0` |
| Machine | Apple M4 Pro, 24 GiB RAM |
| Java | Temurin 17.0.18 |

## Executive Summary

The sweep supports a narrower final component story:

- Keep `checked-page-token` and `checked-region-scoped` as public candidates.
- Keep `RegionList` as the linked-topology public candidate.
- Keep `TransactionRegion` as a partial candidate: throughput improves, but
  latency shape is mixed.
- Keep `StreamWindowFold`, `TableRank`, and ranking/table-heavy containers
  gated.
- Keep rootless/trusted modes as explicit controls only.

## Representative Wins

| Workload | Heap ms | Safe/rooted baseline ms | Best checked candidate ms | RSS note | Interpretation |
|---|---:|---:|---:|---|---|
| Checked page-token append | 37.046 | n/a | `checked-region-scoped page-token` 26.866 | 47.5 MB vs heap 75.1 MB | Focused page-token gate passes on elapsed and RSS. |
| Common Crawl-shaped q1 tokenize | 5619.896 | 4710.779 | `checked-region-scoped page-token` 3860.248 | 463.2 MB vs heap 408.6 MB | Strong generated stream/object-pressure win; RSS higher than heap but lower than SafeZone. |
| Common Crawl-shaped q2 domain window | 5429.530 | 4577.498 | `checked-region-scoped page-token` 3895.711 | 463.7 MB vs heap 408.6 MB | Strong generated stream/window win; RSS still a caveat. |
| GH Archive-shaped q1 fields | 293.716 | 319.870 | `checked-page-token` 262.139 | 44.8 MB vs heap 206.5 MB | Strong generated NDJSON/object-shape win; checked SafeZone-backed row is slower here. |
| GH Archive-shaped q2 repo window | 279.743 | 311.288 | `checked-page-token` 261.762 | 44.8 MB vs heap 206.5 MB | Strong generated NDJSON/window win. |
| Dataflow SELECT | 29.272 | 23.253 | `checked-region-scoped page-token` 19.063 | RSS not captured in this log | Strong SELECT/filter/project win. |
| ListOfLists linked | 15820.172 | 10133.449 | `RegionList` 6053.235 | RSS not captured in this log | Strong linked-topology region-builder win. |
| ReML-shaped `msort-r` | 127.936 | 117.237 | `checked-region-stream` 103.878 | 10.35 MB vs heap 21.36 MB | Good MLKit/ReML-shaped local port win. |
| ReML-shaped `msort` | 118.185 | 118.761 | `checked-region-stream` 106.813 | 10.35 MB vs heap 39.24 MB | Good local port win and large RSS reduction. |

## Mixed Or Gated Rows

| Workload | Result | Interpretation |
|---|---|---|
| Dataflow AGGREGATE | heap 58.484, SafeZone 41.810, checked 41.827 | Checked matches safe baseline and beats heap, but does not prove a faster generic `EpochFold`. |
| Dataflow JOIN | heap 21.434, SafeZone 23.866, checked 22.375 | Heap wins; join remains gated. |
| CheckedWindowFold | heap 96.106, checked 102.008, RSS 75.1 MB vs 40.4 MB | RSS win but elapsed speed gate fails. |
| StreamFlex throughput | heap 42.431, SafeZone 42.236, checked scoped transaction 40.512 | Throughput improves modestly. |
| StreamFlex latency | heap 9.843, SafeZone 11.266, checked scoped transaction 13.355 | Latency median worsens; deadline misses improve versus heap but not SafeZone. |
| NEXMark Beam-default Q3 | heap 317.003, SafeZone 304.246, checked 287.541 | Good generated methodology row, but not a huge margin over SafeZone. |
| NEXMark Beam-default Q9 | heap 806.418, SafeZone 756.289, checked 731.810 | Good generated methodology row, still moderate. |
| Linear Road q0/q1/q2 | heap fastest despite GC in all rows | Ceiling/control for current implementation. |
| Yahoo/Wikimedia/RIoTBench | mostly near-ties or SafeZone-only rows | Useful stream controls, not final Rift case studies yet. |
| Common Crawl q3 parser scratch | heap 10388.393, checked scoped 23001.108 | Negative control: parser-scratch shape is not the right region topology. |

## ReML-Shaped Tier 1 Local Ports

These are Scala Native ports, not exact ReML/MLKit artifact reproductions.

| Workload | Best row | Heap ms | Best ms | RSS note |
|---|---|---:|---:|---|
| `fib37` | checked scoped | 152.979 | 132.636 | same small RSS |
| `tak` | checked stream | 0.189 | 0.181 | same small RSS |
| `mandel` | checked stream | 3.455 | 3.385 | same small RSS |
| `msort` | checked stream | 118.185 | 106.813 | 10.35 MB vs heap 39.24 MB |
| `msort-r` | checked stream | 127.936 | 103.878 | 10.35 MB vs heap 21.36 MB |
| `life` | checked stream | 36.696 | 36.113 | near tie |
| `fft` | checked scoped | 0.839 | 0.744 | 5.34 MB vs heap 8.06 MB |
| `ratio` | checked scoped | 49.733 | 49.591 | 15.99 MB vs heap 46.97 MB |

## Selection Consequences

- `checked-page-token` passes focused, generated Common Crawl-shaped, GH
  Archive-shaped, and Dataflow SELECT evidence.
- `checked-region-scoped` is the best backend for page-token Common
  Crawl-shaped rows and focused page-token append.
- `checked-region-stream` remains important: it wins GH Archive-shaped q1/q2
  and ReML-shaped `msort`/`msort-r` in this sweep.
- `RegionList` remains a strong public candidate.
- `TransactionRegion` remains a candidate, not final: throughput wins are real,
  but latency evidence is mixed.
- Generic fold/join/rank operators remain gated until focused speed gates pass.

## Caveats

- Common Crawl-shaped and GH Archive-shaped rows are generated stressors, not
  real-input proof.
- Some core logs do not include RSS because their older harnesses still print
  only `RESULT` lines.
- The run excludes rootless/trusted lower-bound controls by design. Use
  `RIFT_EVAL_INCLUDE_CONTROLS=1` for backend-potential comparison sweeps.
