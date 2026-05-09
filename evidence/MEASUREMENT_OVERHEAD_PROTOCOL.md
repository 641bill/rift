# Measurement Overhead Protocol

Date: 2026-05-09
Last updated: 2026-05-10 00:46 CEST

Status: active protocol. Initial L1 final-clean support is implemented for the
first representative benchmark binaries. The first clean focused retained L1
row, Dataflow SELECT/AGGREGATE/JOIN representative L1 rows, and the first Yak
LiveJournal real-input L1 row are recorded in
`evidence/FINAL_CLEAN_HEADLINE_RESULTS.md`; the broader L1 headline sweep
remains to be collected. Generated Common Crawl-shaped q1/q2 now also have L1
page-token rows in the same file. Dataflow, Yak, Common Crawl WET-shaped, and
ReML runners write external real/user/sys/RSS columns into their summaries when
run under `/usr/bin/time`.

## Why This Exists

The benchmark harness itself can affect performance. Internal GC-stat reads,
region-stat reads, allocation attribution, trace counters, diagnostic timers,
and sampled profilers all add some cost or change code shape. The final report
therefore separates clean timing from interpretive measurement.

## Measurement Levels

| Level | Name | Use for | What is allowed |
|---|---|---|---|
| L1 | final-clean headline | final elapsed/RSS claims | optimized non-profiled binary; no in-timed-section GC/region counter reads; external `/usr/bin/time -l` only |
| L2 | standard stats | GC/RSS/region interpretation | existing per-run elapsed, GC median/max/runs-with-GC, RSS, region op time, opens/closes/resets, object/allocation counts |
| L3 | diagnostic | bottleneck attribution | `*_DIAG`, allocation attribution, trace mode, internal allocation/open/close/traversal/query timers |
| L4 | external profile | CPU composition and GC pause visibility | `samply`, macOS `sample`, or Linux `perf`; profiler elapsed is not a timing claim |

Headline elapsed and RSS must come from L1 when final-clean rows exist. L2-L4
explain why L1 behaved that way.

## Current Runner Status

Most sandbox runner scripts already wrap native binaries with
`/usr/bin/time -l`, which is the right external timing/RSS source for macOS.
Before 2026-05-09, the benchmark binaries also read Scala Native GC stats and
Rift/SafeZone stats around the timed region. That made those result files
**L2 standard stats**, not fully clean L1 headline rows.

Initial final-clean binary support now exists for:

- `RetainedEpochReclaimMatrix`
- `YakRegionMatrix`
- `DataflowRegionMatrix`
- `CommonCrawlWetMatrix`
- `ReMLRegionMatrix`

Set `RIFT_FINAL_CLEAN=1` or `RIFT_EVAL_MEASUREMENT_LEVEL=L1`. In that mode the
binary skips warmups, heap expected-baseline runs, internal elapsed timing,
`GC.getStats*`, `RiftAllocator` stat reads/resets, and diagnostic counters. It
prints one minimal `RESULT ... measurement_level=L1 final_clean=1` line with
checksum/output metadata. The runner's `/usr/bin/time -l` output supplies the
elapsed/RSS row. As of child `7573d7577`, the retained, Dataflow, Yak, Common
Crawl WET-shaped, and ReML runners write that external timing/RSS data into
their summary TSVs.

Current medians remain valid standard evidence, but should not be described as
"measurement overhead removed completely" unless they were collected in L1
mode.

## External Profiling Policy

Use the official Scala Native profiling guidance as diagnostic support:

- `samply` on macOS when available;
- macOS `sample` as a low-friction fallback;
- Linux `perf` plus FlameGraph/hotspot on Linux machines;
- `/usr/bin/time -l` for external elapsed/RSS measurement on macOS.

Sampling profilers still perturb runtime because they interrupt execution,
record samples, and may require debug symbols or symbolization. They are much
less invasive than per-allocation instrumentation, but profiler elapsed is
diagnostic only.

Profile rows should use the same input and logical mode as the headline row,
but may use profiler-friendly symbols. If debug/symbol settings differ from
the optimized headline binary, say so in the profile report.

## Reporting Rules

- L1 final-clean tables report process real/user/sys time, max RSS,
  checksum/output count, input label, mode, and API/topology.
- L2 tables report GC and region statistics.
- L3 tables report internal timing buckets and attribution.
- L4 reports summarize sampled hot frames and visible GC pause/collection
  frames.
- If L1 and L2 disagree materially, mark the difference as measurement
  overhead and trust L1 for elapsed.
- Never mix L3 or L4 elapsed into a headline median table.

## First Rows To Convert To L1

The first final-clean sweep should cover representative rows only:

| Area | Rows |
|---|---|
| retained epoch | focused retained 1M, GH Archive-shaped q2, LogHub q2/q3, DSPBench Fraud q2 |
| direct epoch | Yak LiveJournal 10M/50M if feasible, Dataflow SELECT/AGGREGATE/JOIN, StreamFlex throughput, Stancu/SPECjbb-style |
| page/window token | generated Common Crawl-shaped q1/q2, DSPBench Fraud/Log q2, LogHub HDFS q2 |
| ReML/MLKit ports | Tier 1 `msort`, `msort-r`, `ratio`, plus compute controls |
