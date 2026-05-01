# Rift Performance Evaluation Report

Date: 2026-05-01

Status: working report scaffold plus current evidence summary. This document
is ready to be filled from a clean sweep run using
`evidence/PERF_EVAL_RUNBOOK.md`.

## Executive Summary

Current evidence supports a narrower and stronger claim than "regions always
beat GC":

- Older baseline rows showed runtime wins on `GCBench` and linked
  `ListOfLists`, but the clean 2026-05-01 rerun weakened that claim: improved
  SafeZone now wins those rows while Rift still wins flat ListOfLists.
- Older Broom/Dataflow and StreamFlex-like rows were strong, but the clean
  rerun also narrows those claims: checked Dataflow SELECT/AGGREGATE beat heap
  but lose to improved SafeZone, JOIN is heap-fastest, and StreamFlex is mainly
  latency-control evidence.
- Checked Rift can be fast when the operator shape is simple
  (`RegionBuffer`, `AppendWindow` cursor).
- Checked Rift still loses on heavier rank/table/fold containers
  (`TableRank`, long-key stream-window rank, additive fold).
- NEXMark Beam-default Q3/Q8 are the best current checked stream rows, but
  they are generated-profile methodology evidence, not Beam runner evidence,
  and the clean Q3 margin is below the `>=10%` case-study gate.
- Generated Common Crawl WET-shaped tokenization is now the clearest GC-heavy
  stream detector: heap spends about `1.56 s` in timed GC at 1M generated
  pages. Rift beats heap and cuts GC, but improved SafeZone is still faster.
- Real/preloaded Wikimedia, real Common Crawl WET, official Linear Road, Yahoo,
  RIoTBench, and most generated stream probes are ceiling or near-tie controls:
  heap or improved SafeZone often wins elapsed time even when Rift lowers GC.

The next report revision should replace this scaffold with clean-sweep rows
from `cache/perf-eval/<run-id>/` and update the claim language accordingly.

Latest harness validation:

| Run id | Scale | Suites | Result | Evidence status |
|---|---|---|---|---|
| `2026-05-01-smoke-streams` | smoke | `preflight streams` | Passed; 7 stream summary TSVs produced | Harness validation only |
| `2026-05-01-headline-core-prior-checked` | headline | `preflight core prior checked` | Passed; tracked summary in `evidence/HEADLINE_CORE_PRIOR_CHECKED_2026_05_01.md` | Current clean headline subset |
| `2026-05-01-headline-core-prior-checked-rerun` | headline | `preflight core prior checked` | Passed; tracked summary in `evidence/HEADLINE_CORE_PRIOR_CHECKED_RERUN_2026_05_01.md` | Current rerun evidence |
| `2026-05-01-headline-streams` | headline | `preflight streams` | Passed; tracked summary in `evidence/HEADLINE_STREAMS_2026_05_01.md` | Current stream headline leg |
| `2026-05-01-headline-debs-1m` | headline | `preflight debs` | Passed on `/tmp/debs2015-month1-1000000.csv`; tracked summary in `evidence/HEADLINE_DEBS_1M_2026_05_01.md` | Bounded DEBS 1M single-run leg |

The smoke run validates harness wiring only. The headline rows above are the
current evidence for their respective suites.

## Experimental Method

Baseline modes:

| Mode | Meaning |
|---|---|
| `heap` | Scala Native Immix. |
| `safezone-current` | SafeZone with `SAFEZONE_ROOTS_MODE=0`. |
| `safezone-improved` | SafeZone with `SAFEZONE_ROOTS_MODE=1`. |
| `rift-hp` | Trusted Rift HPZone. |
| `rift-streaming` | Trusted Rift StreamingZone. |
| `rift-checked` | Checked Rift API path where a checked operator exists. |
| `commix` | Included where supported and meaningful. |

Headline measurements should use:

- clean parent and child repositories;
- recorded SHAs, OS, CPU, memory, Java version, and Scala Native branch;
- smoke runs before medians;
- 100k 3-run medians;
- 1M 5-run medians for headline candidates;
- full-input runs only after 1M gates pass;
- allocation attribution only after non-attribution medians are stable.

## Current Evidence By Category

### Runtime And Topology

GCBench and linked ListOfLists were historically the strongest runtime/topology
rows, but the 2026-05-01 headline subset and rerun weaken the Rift runtime
claim. In the rerun, GCBench is heap `211.413 ms`, improved SafeZone
`219.924 ms`, and HPZone `244.039 ms`. Linked ListOfLists is heap
`15165.020 ms`, improved SafeZone `9853.992 ms`, and HPZone `12210.485 ms`.
Rift still wins flat ListOfLists (`1567.144 ms` versus heap `1749.780 ms`),
but it does not currently beat improved SafeZone on the linked headline row.

### Prior-Work Methodology

The current Broom-style Dataflow checked rows are strong: SELECT `18.865 ms`
vs heap `36.868 ms`, AGGREGATE `36.003 ms` vs heap `51.474 ms`, and JOIN
`18.736 ms` vs heap `32.170 ms` in older evidence. The clean 2026-05-01
headline subset and rerun are weaker: checked SELECT/AGGREGATE beat heap but
lose to improved SafeZone, and JOIN is won by heap. StreamFlex keeps a latency
story because region modes remove deadline misses, but they do not win elapsed
time in the clean subset. Yak/Stancu rows are mostly improved-SafeZone wins.
These are local methodology reproductions, not exact artifact reproductions.

### Checked Operators

Checked `RegionBuffer` and `AppendWindow` cursor are positive API evidence.
`TableRank`, long-key stream-window rank, and additive `StreamWindowFold` are
negative or gated results. The clean 2026-05-01 subset narrows the positive
checked story further: manual AppendWindow still wins, prepend cursor wins its
fair heap-prepend control, but RegionBuffer and append cursor do not win
elapsed time. The rerun confirms this narrower checked story. Application
benchmarks should only use checked operators that pass focused gates in the
current clean environment.

### Stream/Application Benchmarks

DEBS full-month checked is currently a near-tie with memory-pressure
improvement, not a large speedup. The clean bounded 1M DEBS single-run leg has
trusted Streaming at `4681.292 ms` versus heap `4987.579 ms`; checked is
`4882.562 ms`. The best checked stream row in the clean stream leg is NEXMark
Beam-default Q3: checked `295.166 ms`, heap `315.715 ms`, improved SafeZone
`302.668 ms`. Q8 is a checked near-tie with improved SafeZone (`457.518 ms`
versus `457.725 ms`). Generated Common Crawl WET-shaped Q1 tokenization is
the clearest GC-heavy detector: heap `4770.503 ms` with `1559.601 ms` GC,
HPZone `4301.536 ms` with `20.543 ms` GC, but improved SafeZone wins elapsed
at `4066.435 ms`. Yahoo, RIoTBench, generated Wikimedia, generated Linear
Road, real Wikimedia/Common Crawl/Linear Road, and NEXMark Q11 are controls
where heap or improved SafeZone wins or the gap is too small for a case-study
claim.

## Acceptance Criteria For Claims

A benchmark can be a serious Rift case study only if:

- outputs/checksums match across modes;
- Rift beats heap and improved SafeZone by about `>=10%`; or
- Rift cuts GC/RSS materially with `<=5%` elapsed overhead and better latency;
- checked rows use a focused-gated checked API;
- result provenance is explicit: generated, real/preloaded, methodology, or
  exact artifact reproduction.

Rows that fail these criteria still belong in the report as negative evidence
or ceiling results.

## Threats To Validity

- Many literature-shaped rows are methodology reproductions, not exact
  artifacts.
- NEXMark rows use local Scala Native execution, not the Apache Beam runner.
- Real-input rows often preload data; parser/decompression/I/O are separated
  from memory-management claims.
- Scala Native performance differs from JVM performance, so JVM benchmark
  suites are not direct targets.
- Allocation-attribution counters perturb timing and should not provide
  headline elapsed numbers.
- Improved SafeZone is a moving and strong baseline; beating old SafeZone is
  not sufficient.

## Remaining Report Work

The core/prior/checked, stream, and bounded DEBS 1M legs have now run. The
remaining report work is:

1. Convert the current tracked summaries into final thesis tables.
2. Decide whether to run a full-month DEBS rerun under the same quiet-machine
   discipline.
3. Add only targeted follow-up benchmarks for repeated winning shapes.
4. Finalize the win-envelope and next API plan around cheaper checked
   operators, not benchmark-specific rewrites.

Use `evidence/EVALUATION_SUMMARY_TABLES.md` for compact tables and the
individual result packs for detailed command provenance.
