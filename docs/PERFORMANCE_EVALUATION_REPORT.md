# Rift Performance Evaluation Report

Date: 2026-05-01

Status: working report scaffold plus current evidence summary. This document
is ready to be filled from a clean sweep run using
`evidence/PERF_EVAL_RUNBOOK.md`.

## Executive Summary

Current evidence supports a narrower and stronger claim than "regions always
beat GC":

- Rift has credible runtime wins on allocation-heavy linked structures
  (`GCBench`, linked `ListOfLists`).
- Rift has strong local methodology wins on Broom/Dataflow and StreamFlex-like
  dataflow/latency shapes.
- Checked Rift can be fast when the operator shape is simple
  (`RegionBuffer`, `AppendWindow` cursor).
- Checked Rift still loses on heavier rank/table/fold containers
  (`TableRank`, long-key stream-window rank, additive fold).
- NEXMark Beam-default Q3/Q8 are the best current checked stream rows, but
  they are generated-profile methodology evidence, not Beam runner evidence.
- Real/preloaded Wikimedia, Common Crawl WET, and official Linear Road rows are
  ceiling controls so far: heap is usually fastest and timed GC is often zero
  in the measured section.

The next report revision should replace this scaffold with clean-sweep rows
from `cache/perf-eval/<run-id>/` and update the claim language accordingly.

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

GCBench and linked ListOfLists remain the strongest runtime/topology baseline
rows. Current medians are HPZone `161.641 ms` vs heap `203.514 ms` for
GCBench, and HPZone `6951.331 ms` vs heap `15085.511 ms` for linked
ListOfLists. These should be rerun in the clean sweep with improved SafeZone
and current SafeZone retained.

### Prior-Work Methodology

The current Broom-style Dataflow checked rows are strong: SELECT `18.865 ms`
vs heap `36.868 ms`, AGGREGATE `36.003 ms` vs heap `51.474 ms`, and JOIN
`18.736 ms` vs heap `32.170 ms`. StreamFlex-style pressure and Yak
top-word/filter also show useful Rift wins. These are local methodology
reproductions, not exact artifact reproductions.

### Checked Operators

Checked `RegionBuffer` and `AppendWindow` cursor are positive API evidence.
`TableRank`, long-key stream-window rank, and additive `StreamWindowFold` are
negative or gated results. This distinction matters: application benchmarks
should only use checked operators that passed focused gates.

### Stream/Application Benchmarks

DEBS full-month checked is currently a near-tie with memory-pressure
improvement, not a large speedup. NEXMark Beam-default Q3/Q8 are the best
checked stream rows. Yahoo Q2 and RIoTBench q1 are useful profile controls but
do not beat improved SafeZone strongly enough. Real Wikimedia/Common
Crawl/Linear Road rows are parked as ceiling controls unless future operators
change their allocation shape.

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

## Pending Clean-Sweep Sections

Fill these after running the runbook:

1. Environment table.
2. Core runtime baseline tables.
3. Prior-work methodology tables.
4. Checked-operator gate table.
5. Existing stream/application table.
6. New candidate benchmark table.
7. Final win-envelope and next API plan.

Use `evidence/EVALUATION_SUMMARY_TABLES.md` for compact tables and the
individual result packs for detailed command provenance.
