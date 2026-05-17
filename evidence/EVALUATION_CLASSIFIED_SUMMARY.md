# Evaluation Classified Summary

Date: 2026-05-09
Last updated: 2026-05-18 00:44 CEST

Status: thesis-facing classified summary built from committed evidence.
Baseline commits for clean rows: parent `1cc3b2c`, child `13a3df1c7`.
Reusable top-k API rows include the increment hot-path follow-up after child
commit `bc9fd5979`, the Yak topword same-shape/L1 follow-up, and the larger
real HDFS 5M top-template scale-up from child `0773d4c17`. The AskUbuntu real
text row now also has a 20M-token scale-up from child `59c181746`. Child
`ca1978ef4` refreshes the focused page-token, StreamFlexDesign, and generated
Common Crawl-shaped page-token presentation rows after the open-allocation
cleanup. The latest working evidence adds LogHub HDFS q3 template/session
`streaming-file` rows as real-streaming-input RSS/control evidence. The latest
all-optimizations pass adds a focused dirty/warm-slab allocation probe and
refreshes handle-backed checked StreamFlex/page-token gates: StreamFlexDesign
20M default `checked-epoch-stream` is now `19.25 s` versus legacy `21.32 s`
and heap `30.90 s`; generated Common Crawl-shaped q2 default
`rift-checked-page-token` is `9.76 s` versus legacy `11.06 s` and heap
`16.23 s`; focused page-token default is `23.059 ms` versus legacy
`24.687 ms` and heap `38.352 ms`. The quick all-optimizations
SPECjbb/Stancu-style 4-warehouse gate reports checked epoch stream `0.18 s`
versus rooted scoped `0.21 s` and heap `0.51 s`. The follow-up SPECjbb
handle-backed promotion gate makes that explicit: `checked-epoch-stream` is
now the optimized default at `0.27 s` L1 / `51.168 ms` L2, versus legacy
`0.30 s` / `56.371 ms`. Child `3ee2fc173` also promotes GH Archive checked
page-token to backend-known allocation; the generated/preloaded 1M L2 transfer
gate improves q1 `316.947 -> 299.512 ms` and q2 `317.997 -> 298.186 ms` over
the legacy checked page-token path with matching checksums and object counts.
This row remains allocation-lowering transfer evidence rather than a
presentation headline. The LogHub top-template retained stream path now has
the same legacy/default control: generated/preloaded 1M improves
`291.519 -> 269.309 ms`, while a real HDFS streaming-file 100k sanity row is
neutral (`273.834 -> 275.054 ms`). Keep this as transfer evidence; the
presentation-facing LogHub API row is still scoped `EpochTopKByKey`. The
2026-05-16 selected all-optimizations sweep now records matching L1/L2
optimized-vs-legacy rows in `evidence/ALL_OPTIMIZATIONS_SELECTED_SWEEP.md`:
StreamFlexDesign 1M optimized checked stream is `0.88 s` versus legacy
`1.09 s`; Common Crawl-shaped q2 100k optimized page-token is `0.96 s`
versus legacy `1.07 s`; GH Archive-shaped q2 1M optimized page-token is
`0.80 s` versus legacy `0.85 s`; LogHub retained top-template 1M optimized
checked epoch is `0.69 s` versus legacy `0.75 s`.
The follow-up local Stancu transaction probe extends that default/legacy audit:
optimized `rift-checked-direct-epoch` is `28.554 ms` versus legacy
`29.687 ms`, with matching checksum and heap at `44.144 ms` / `4.837 ms` GC;
checked SafeZone direct epoch remains fastest at `26.405 ms`, so this is
allocation-lowering transfer evidence rather than a new headline row.
The current SPECjbb/Stancu-style scale row extends the clean-room workload
port to 8 warehouses and 1,000,000 transactions per warehouse. It is generated
methodology evidence, not real-input evidence and not official SPECjbb2005.
At 8M transactions, L1 heap is `4.89 s`, checked epoch stream is `4.35 s`,
and checked epoch scoped is `3.95 s`; L2 heap spends `164.932 ms` in GC
across `520` collections, while checked epoch stream is `996.765 ms` with
`4.075 ms` region-op time.
The latest retained-object prior-work row is
`evidence/BROOM_RETAINED_DATAFLOW_MATRIX.md`: a Broom/Naiad-style timestamped
aggregate/join matrix that headlines natural heap/GC versus checked Rift,
with ordinary event/value objects retained until timestamp notification.
The 2026-05-16 presentation normalization keeps this row as a first-class
prior-work-style headline row and keeps same-shape/drop-anchor rows in the
mechanism appendix unless they are explicitly being used for causality.
The latest Broom rerun adds `checked-region-scoped` as a best-safe-region
comparison row for the 1M, 5M, and 20M aggregate/join scale points.
The 20M active-16 follow-up is now the strongest Broom high-live-state row:
aggregate heap is `10.78 s`, RSS `236 MB`, with `953.153 ms` median timed GC,
versus checked Rift `8.48 s`, RSS `53 MB`, and zero timed GC; join heap is
`9.88 s`, RSS `438 MB`, with `486.649 ms` median timed GC, versus checked
Rift `8.09 s`, RSS `57 MB`, and zero timed GC. Heap completes at `512M` but
fails at `384M`/`256M`, while checked Rift completes with low RSS.
The 2026-05-17 q17 follow-up adds a TPC-H-Q17-style retained join/aggregate
shape to the same matrix. It is deterministic generated methodology evidence,
not exact TPC-H artifact reproduction. The strongest q17 row is 20M active-16:
heap is `14.45 s`, RSS `232 MB`, with `1370.380 ms` median timed GC inside
`4781.079 ms` L2, versus checked Rift `9.67 s`, RSS `50 MB`, and zero timed
GC. Heap caps down to `256M` complete, so q17 is a throughput/GC/RSS result
rather than a fixed-memory failure result.
An optional DBGEN/TPC-H file-backed q17 mode is now implemented and validated
at SF0.1 and SF1. The corrected file-backed implementation retains all
lineitems until timestamp close and only then applies the Q17 filters. At
SF0.1 (`600572` lineitems), checked Rift is `5.15 s`, RSS `50.9 MB`, with
`38.075 ms` L2 median timed GC and `0.468 ms` region-op time versus heap
`5.57 s`, RSS `257.5 MB`, and `59.210 ms` L2 median timed GC. Heap completes
at `128M` but fails at `64M`. At SF1 (`6001215` lineitems), checked Rift is
`51.47 s`, RSS `48.7 MB`, with `503.444 ms` L2 median timed GC and
`5.922 ms` region-op time versus heap `55.44 s`, RSS `433.3 MB`, and
`877.190 ms` L2 median timed GC. Heap completes at `256M`/`384M` but fails at
`128M`. SF1 is standardized generated TPC-H input evidence, not official
audited TPC-H or real-world input.
The Broom shopper JOIN-SELECT-JOIN follow-up is now complete as a separate
generated methodology row. At 20M records, natural heap is `10.41 s`, RSS
`94.3 MB`, with `601.284 ms` L2 median timed GC; checked Rift is `8.28 s`,
RSS `20.3 MB`, and zero timed GC; checked scoped is `8.56 s`, RSS `20.6 MB`,
and zero timed GC. Heap completes at `128M` but fails at `64M`/`32M`, while
checked Rift completes around `20 MB`.
The new `evidence/LOGHUB_RETAINED_SESSION_MATRIX.md` rows are the opposite
lesson: the HDFS retained session/join row is true real-streaming retained
state, but heap GC remains too small to headline; the Spark archive-wide
retained session follow-up is stronger fixed-memory evidence. At 1M active-16
session records, L1 heap is `27.62 s` and `391 MB` RSS, checked Rift is
`20.30 s` and `73 MB`, and checked scoped is `19.85 s` and `73 MB`. Heap
fails below a `128M` cap, while checked rows complete around `73 MB`. This is
real-streaming retained-object RSS/fixed-memory evidence, not a GC-time
flagship: heap median timed GC is about `2.1%` of the L2 loop.
The same retained line-session harness was also tried on the large compressed
Wikimedia enwiki clickstream file. At 1M streamed rows, L1 checked Rift is
`14.15 s`, RSS `136 MB`, versus heap `15.54 s`, RSS `864 MB`. Heap fails at
`256M` and `128M` caps, while checked rows complete under `128M` and `64M`.
This is another real-streaming retained-state RSS/fixed-memory row; heap L2
GC is `166.100 ms` inside `4826.234 ms`, about `3.4%`, so it remains below
the GC-time flagship threshold.
The latest Yak graph follow-up adds a true compressed-source
`YAK_GRAPH_INPUT_MODE=streaming-file` path for SNAP LiveJournal. At 20M
streamed edges, L1 checked epoch scoped is `17.15 s`, RSS `102 MB`, versus
heap `18.32 s`, RSS `577 MB`; L2 checked epoch stream is `5530.190 ms`, GC
`0 ms`, and region op `2.869 ms`, versus heap `6333.745 ms` with
`165.387 ms` timed GC. This is real-streaming graph RSS/fixed-memory and
throughput evidence, but not a GC-time flagship because heap GC is still only
about `2.6%` of L2 elapsed. A follow-up one-run cap probe shows heap
completes down to `128M` but fails at `64M`, while checked epoch rows complete
under `64M` and `32M` caps with matching checksums.
The backend classification has also been clarified: every measured row in this
file is Scala Native evidence unless it is explicitly marked paper-reported or
planned. JVM, Scala.js, Wasm, and analysis-only Rift are now tracked as future
backend experiments in `docs/SCALA_LEVEL_BACKEND_PLAN.md`; they inherit the
intended Scala-level safety/topology model but have no current performance
rows.
The latest normalized selected prior-work sweep is
`evidence/SELECTED_PRIOR_WORK_SWEEP_2026_05_16.md`, run from parent
`14038d3` and child `15c4c39ac`. It should be used as the current
presentation-facing generated/local methodology sweep for Broom, Dataflow,
StreamFlexDesign, Yak local direct-epoch workloads, and the SPECjbb2005
workload port. The older parent `prior` sweep remains L2 interpretation
evidence for legacy runners.
The latest normalized selected stream sweep is
`evidence/SELECTED_STREAMS_SWEEP_2026_05_16.md`, run from parent `46c4ea8`
and child `15c4c39ac`. It should be used as the current presentation-facing
stream/application sweep for Common Crawl page-token, NEXMark, GH Archive,
LogHub, LogHub top-template, and DSPBench real bundled rows. Theodolite q2 is
opt-in in the runner because it requires `THEODOLITE_POWER_INPUT`, but the
current evidence file now includes a selected-row addendum from the local real
UCI household-power trace: checked epoch stream `4.58 s` versus heap `5.13 s`,
with timed heap GC removed and slightly higher RSS.
The AskUbuntu true streaming-file text row now has a 5M compressed-source
scale-up from `askubuntu.com.7z`. It strengthens the RSS/fixed-memory story
but not the GC-time story: checked epoch scoped is L1 `6.23 s`, RSS `15 MB`,
versus heap `6.74 s`, RSS `41 MB`; heap L2 GC is only `27.237 ms` inside
`2109.524 ms`.

## How To Read This Table

Every row has an explicit comparison class. Do not read all rows as a single
"heap vs Rift" claim.

Measurement level is separate from comparison class. Some rows below now cite
L1 final-clean process timing from
`evidence/FINAL_CLEAN_HEADLINE_RESULTS.md`; older rows remain L2
standard-stats rows that report GC, RSS, and region counters for
interpretation. Use L1 rows for final elapsed/RSS when available, and use L2
rows to explain GC/region behavior.

| Comparison class | Meaning |
|---|---|
| natural heap baseline | End-to-end practical comparison against the current heap implementation. |
| same-shape heap control | Heap uses the same operator/topology as the region row. |
| summary-only topology | Records update summaries on append and are not retained until close. |
| retained-object drop-anchor | Heap and region both retain ordinary records until close, then close without user-level record traversal. |
| best checked topology | Fastest safe checked topology for the workload: usually epoch or page/window token. |
| unsafe/trusted lower bound | Internal optimization potential only; not a safe-system claim. |

Use `heap-retained-drop-anchor` in prose for
`heap-epoch-retained-no-traverse`. It closes in O(1) by dropping the bucket
reference, but the retained heap objects still remain for GC tracing/reclaim.
Representative API-boundary counts for epoch/page/window/`HeapRoot` usage are
tracked separately in `evidence/API_BURDEN_SUMMARY.md`; include those counts
when presenting Stancu/SPECjbb-style or final checked API rows.

## Presentation Completeness Audit

This audit covers the rows currently used in the report/slides as
representative evidence. `Complete` means the row has L1 headline elapsed/RSS,
L2 GC/region interpretation, input type, topology/API, comparison class, and
allowed claim. Rows outside this table remain detailed evidence or controls,
not presentation requirements.

| Presentation group | L1 elapsed/RSS | L2 GC/region interpretation | Metadata/classification | Current action |
|---|---|---|---|---|
| Focused retained epoch | complete | complete | retained-object memory-management | keep as cleanest memory-management row |
| Broom retained timestamped aggregate/join | complete, including 1M/5M/20M checked scoped backend comparison | complete, including 1M/5M/20M checked scoped backend interpretation | prior-work-style natural heap vs checked Rift retained dataflow | keep as the first Broom/Naiad-like GC-heavy dataflow row; same-shape controls are appendix-only and checked scoped is the safe backend comparison |
| Broom q17 retained join/aggregate | complete through 1M/5M/20M active-4, 5M/20M active-16, and DBGEN SF0.1/SF1 file-backed L1 | complete through the same generated scale points and DBGEN SF0.1/SF1 L2 plus heap-cap follow-ups | prior-work-style generated TPC-H-Q17-like retained dataflow; optional DBGEN/TPC-H file-backed input mode | keep as the next Broom/Naiad-like GC-heavy dataflow row; classify generated rows as deterministic methodology, and DBGEN rows as standardized generated TPC-H input rather than real-world input |
| Broom shopper JOIN-SELECT-JOIN | complete through 20k smoke and 1M/5M/20M L1 | complete through 1M/5M/20M L2 plus 20M heap-cap follow-up | prior-work-style generated Broom/Naiad shopper-like retained dataflow | keep as the second completed Broom/Naiad retained join shape after q17; generated methodology evidence, not real-input proof |
| GH Archive-shaped retained q2 | complete | complete | generated/preloaded retained-object row | keep; label generated/preloaded, not real-input proof |
| LogHub retained q2/q3 | complete | complete | generated/indexable retained rows | keep q2 as strong retained row; mark q3 checked-stream as modest/RSS row |
| DSPBench Fraud retained q2 | complete | complete | generated/indexable retained row | keep as modest retained win |
| Yak LiveJournal graphreal | complete, including 50M preloaded and 1M/5M/20M streaming-file compressed-source rows | complete | real-input and real-streaming-input best checked epoch topology | keep as strongest real graph/epoch row; preloaded 50M remains the strongest pure epoch row, while 20M streaming-file is the stream-processing RSS/fixed-memory row |
| Yak AskUbuntu topwordreal | complete at 10M and 20M preloaded plus 1M/5M streaming-file | complete | real-input and real-streaming-input best checked epoch topology | keep as first real text/top-word row; 20M preloaded strengthens direct epoch claim and 5M streaming-file confirms compressed-source RSS/fixed-memory behavior |
| Dataflow SELECT/AGGREGATE/JOIN | complete | complete | Broom-style generated methodology, direct epoch API | keep as prior-work-shaped checked epoch row |
| StreamFlex throughput/latency | complete | complete | StreamFlex-style generated methodology, latency/deadline axes | keep; report latency tail/deadline misses separately from throughput |
| StreamFlex design stable/transient/capsule | complete for first 1M throughput and latency candidates | complete | StreamFlex-design generated methodology, checked framework API, latency/deadline axes | keep as Rift-native StreamFlex design reproduction; not exact Ovm artifact evidence |
| StreamIt BeamFormer/FilterBank ports | 3-run L1 complete | 3-run L2 complete | StreamFlex/StreamIt-style primitive DSP controls | keep as methodology/control rows; not GC-heavy memory-management wins |
| Stancu and SPECjbb2005 workload port | complete, including current 8M transaction scale row | complete, including current 8M transaction scale row | generated transaction/epoch methodology; clean-room port, not real-input and not official SPEC | keep as Stancu/SPECjbb-style prior-work-axis evidence; do not call it real input |
| Common Crawl WET-shaped q1/q2 | complete, refreshed in selected stream sweep | complete | generated stream stressor, checked page-token | keep as generated high-object-pressure row only |
| NEXMark q3/q8/q9/q11 | complete, refreshed in selected stream sweep | L2 remains interpretation source | generated Beam-default-style methodology | keep; not exact Beam runner evidence |
| LogHub HDFS top templates | complete at 1M and 5M | complete | real retained top-k API row | keep as strongest real retained top-k row |
| LogHub HDFS streaming-file top templates | complete for first 1M candidate | complete | real-streaming-input retained top-k API row | keep as first true streaming-input row; not yet flagship GC-heavy evidence |
| LogHub q2/q3, LogHub top templates, LogHub retained session, DSPBench Fraud/Log q2, GH Archive q1/q2, Theodolite power q2 | selected-streams clean sweep complete for generated/default rows; Theodolite selected-row addendum complete over the local real trace; Spark q3 older L1 elapsed not promoted because `/usr/bin/time` real field was anomalous; Spark retained session archive-wide row complete | complete where used | generated, real-input, and real-streaming-input page/window/epoch/top-k/session modest/RSS/fixed-memory/control rows | use selected-streams for current generated/default presentation rows; keep real HDFS/GH/Theodolite/LogHub retained rows as separate real-input evidence |
| ReML/MLKit Tier 1 and first Tier 2 ports | complete for local ports | complete for local ports | local Scala Native port evidence | keep same-axes table; no raw ReML-vs-Rift wall-clock claim |
| Summary-only/direct-aggregate rows | complete for selected symmetric rows | complete where needed | topology lower bound | keep only with heap and checked counterparts; never claim reclaim win |

## Classified Rows

| Benchmark / row | Input type | Comparison class | Heap/control row | Best safe checked row | Elapsed delta | GC delta | RSS delta | Allowed claim |
|---|---|---|---|---|---:|---:|---:|---|
| Broom retained timestamped aggregate 20M | generated Broom/Naiad-style timestamped dataflow | natural heap baseline / prior-work-style retained dataflow | natural heap `5.27 s` L1, RSS `75.8 MB`; L2 `1728.037 ms`, GC `410.002 ms` | checked Rift `3.59 s` L1, RSS `13.6 MB`; L2 `1248.788 ms`, GC `0 ms`; checked scoped `4.55 s`, RSS `13.7 MB` | L1 `31.9%` faster; L2 `27.7%` faster | L2 `-410.002 ms` | L1 about `-82%` | Strong Broom-style retained-object GC/RSS/throughput win. Headline comparison is natural heap/GC versus checked Rift; same-shape/drop-anchor controls are appendix/mechanism evidence only. Checked scoped is now available as the safe backend comparison row. |
| Broom retained timestamped join 20M | generated Broom/Naiad-style timestamped dataflow | natural heap baseline / prior-work-style retained dataflow | natural heap `5.00 s` L1, RSS `74.7 MB`; L2 `1686.550 ms`, GC `267.636 ms` | checked Rift `4.26 s` L1, RSS `12.8 MB`; L2 `1465.638 ms`, GC `0 ms`; checked scoped `4.52 s`, RSS `13.0 MB` | L1 `14.8%` faster; L2 `13.1%` faster | L2 `-267.636 ms` | L1 about `-83%` | Broom-style retained join win with material heap GC and large RSS reduction. Checked scoped is also faster than heap and remains a backend comparison row. |
| Broom retained high-active aggregate/join 1M | generated Broom/Naiad-style high-live-state dataflow | natural heap baseline / prior-work-style retained dataflow / fixed-memory | aggregate heap `0.67 s`, RSS `232 MB`; join heap `0.63 s`, RSS `239 MB`; heap completes at `256M` but OOMs at `128M`/`64M` | aggregate checked Rift `0.51 s`, RSS `53 MB`; join checked Rift `0.42-0.45 s`, RSS `56 MB` | aggregate `23.9%` faster; join `29-33%` faster | L2 removes `53.115/28.080 ms` heap GC | about `-76%` to `-77%` | High-cardinality/multiple-active-timestamp variant confirms live-state RSS, GC pressure, and fixed-memory behavior. |
| Broom retained high-active aggregate/join 5M | generated Broom/Naiad-style high-live-state dataflow | natural heap baseline / prior-work-style retained dataflow | aggregate heap `2.84 s`, RSS `235.9 MB`; join heap `2.72 s`, RSS `362.3 MB`; L2 heap GC `176.734/147.124 ms` | aggregate checked Rift `2.06 s`, RSS `53.2 MB`; join checked Rift `2.04 s`, RSS `56.6 MB`; checked scoped aggregate/join `2.91/2.24 s`, RSS `53.6/56.8 MB` | aggregate `27.5%` faster; join `25.0%` faster | L2 removes `176.734/147.124 ms` heap GC | aggregate about `-77%`; join about `-84%` | Stronger high-live-state Broom row: heap GC is about `20%` of aggregate L2 and `19%` of join L2, while checked Rift keeps low RSS and small region-op time. |
| Broom retained high-active aggregate/join 20M | generated Broom/Naiad-style high-live-state dataflow | natural heap baseline / prior-work-style retained dataflow / fixed-memory | aggregate heap `10.78 s`, RSS `236 MB`, L2 `4235.563 ms`, GC `953.153 ms`; join heap `9.88 s`, RSS `438 MB`, L2 `3133.932 ms`, GC `486.649 ms`; heap fails at `384M`/`256M` | aggregate checked Rift `8.48 s`, RSS `53.3 MB`, L2 `2904.092 ms`, GC `0 ms`; join checked Rift `8.09 s`, RSS `56.6 MB`, L2 `2864.439 ms`, GC `0 ms`; checked scoped aggregate/join `11.51/9.15 s`, RSS `53.7/56.9 MB` | aggregate `21.3%` faster; join `18.1%` faster | L2 removes `953.153/486.649 ms` heap GC | aggregate about `-77%`; join about `-87%` | Strongest Broom high-live-state row. It gives throughput, GC, RSS, and fixed-memory evidence under the prior-work-style natural heap/GC versus checked Rift comparison. |
| Broom q17 retained join/aggregate active-4 20M | generated Broom/Naiad-style TPC-H-Q17-like dataflow | natural heap baseline / prior-work-style retained dataflow | q17 heap `5.89 s`, RSS `39.4 MB`, L2 `2840.837 ms`, GC `213.555 ms` | checked Rift `4.76 s`, RSS `13.2 MB`, L2 `1892.916 ms`, GC `0 ms`; checked scoped `5.91 s`, RSS `13.4 MB`, L2 `2200.976 ms` | L1 `19.2%` faster; L2 `33.4%` faster | L2 removes `213.555 ms` heap GC | L1 about `-66%` | Q17 active-4 reaches material heap GC at 20M while keeping the same logical TPC-H-Q17-like retained query across heap and checked Rift. |
| Broom q17 retained join/aggregate active-16 20M | generated Broom/Naiad-style TPC-H-Q17-like high-live-state dataflow | natural heap baseline / prior-work-style retained dataflow | q17 heap `14.45 s`, RSS `231.7 MB`, L2 `4781.079 ms`, GC `1370.380 ms`; heap caps `512M/384M/256M` all complete | checked Rift `9.67 s`, RSS `49.9 MB`, L2 `3349.128 ms`, GC `0 ms`; checked scoped `13.02 s`, RSS `50.3 MB`, L2 `4269.248 ms` | L1 `33.1%` faster; L2 `29.9%` faster | L2 removes `1370.380 ms` heap GC | L1 about `-78%` | Strongest q17 row. It is throughput/GC/RSS evidence for retained join/aggregate state; not fixed-memory failure evidence because heap still completes down to `256M`. |
| Broom shopper JOIN-SELECT-JOIN 20M | generated Broom/Naiad-style shopper retained dataflow | natural heap baseline / prior-work-style retained dataflow / fixed-memory | shopper heap `10.41 s`, RSS `94.3 MB`, L2 `3507.557 ms`, GC `601.284 ms`; heap completes at `128M` but fails at `64M`/`32M` | checked Rift `8.28 s`, RSS `20.3 MB`, L2 `2917.572 ms`, GC `0 ms`; checked scoped `8.56 s`, RSS `20.6 MB`, L2 `3069.260 ms`, GC `0 ms` | L1 `20.5%` faster; L2 `16.8%` faster | L2 removes `601.284 ms` heap GC | L1 about `-78%` | Second completed Broom/Naiad retained join shape. It gives throughput, GC, RSS, and fixed-memory evidence under the natural heap/GC versus checked Rift comparison. |
| Focused retained epoch 1M | synthetic focused matrix | retained-object drop-anchor | `heap-retained-drop-anchor` `36.233 ms`, GC `10.109 ms`, RSS `21.3 MB` | `checked-scoped-epoch-retained-no-traverse` `24.274 ms`, GC `0 ms`, RSS `4.9 MB` | `33.0%` faster | `-10.109 ms` | `-77%` | Clean retained-object memory-management win. |
| GH Archive-shaped retained q2 | generated/preloaded stressor | retained-object drop-anchor / L1 final-clean | L1 retained heap `4.62 s`, RSS `147 MB`; L2 retained heap `257.377 ms`, GC `77.208 ms` | L1 checked scoped retained `3.44 s`, RSS `16 MB`; L2 checked scoped retained `186.868 ms`, GC `0 ms` | L1 `25.5%` faster; L2 `27.4%` faster | L2 `-77.208 ms` | L1 about `-89%` | Strong retained memory-management and RSS win; generated/preloaded, not real-input proof. Summary-only L1 lower bound is `1.28 s`. |
| LogHub-shaped retained q2 | generated/indexable log stream | retained-object drop-anchor / L1 final-clean | L1 retained heap `10.79 s`, RSS `206 MB`; L2 retained heap `469.079 ms`, GC `64.060 ms` | L1 checked scoped retained `8.12 s`, RSS `22 MB`; L2 checked scoped retained `402.821 ms`, GC `0 ms` | L1 `24.7%` faster; L2 `14.1%` faster | L2 `-64.060 ms` | L1 about `-89%` | Strong retained throughput/GC/RSS win on generated/indexable log stream. |
| LogHub-shaped retained q3 | generated/indexable template/session stream | retained-object drop-anchor / L1 final-clean | L1 retained heap `47.55 s`, RSS `814 MB`; L2 retained heap `2244.266 ms`, GC `143.539 ms` | L1 checked stream retained `45.76 s`, RSS `29.5 MB`; checked scoped retained removes timed GC but is slower in L1 (`60.29 s`) | L1 best checked `3.8%` faster | L2 retained checked rows remove heap timed GC | L1 about `-96%` for best checked stream | Mixed retained win: checked stream is a modest elapsed/RSS win; checked scoped is an RSS/GC win but not an elapsed win at L1. |
| DSPBench Fraud retained q2 | generated/indexable DSPBench-shaped stream | retained-object drop-anchor / L1 final-clean | L1 retained heap `8.40 s`, RSS `206 MB`; L2 retained heap `392.743 ms`, GC `35.631 ms` | L1 checked scoped retained `7.90 s`, RSS `46.8 MB`; L2 checked scoped retained `370.746 ms`, GC `0 ms` | L1 `6.0%` faster; L2 `5.6%` faster | L2 `-35.631 ms` | L1 about `-77%` | Modest retained throughput/GC/RSS win. |
| DSPBench Fraud direct q2 | generated/indexable DSPBench-shaped stream | summary-only topology | natural heap `400.900 ms`; L1 heap direct summary `5.62 s` x20; L2 heap direct `272.251 ms` | L1 checked stream/scoped direct summary `5.67/5.68 s` x20; L2 checked scoped direct `267.739 ms` | direct topology gives most of the win; checked is within about `1%` of heap direct in L1 | heap direct has `0 ms` GC | L1 near-tie small RSS | Symmetric topology/operator lower bound; checked regions are close to same-shape heap. |
| DSPBench Log direct q2 | generated/indexable DSPBench-shaped stream | summary-only topology | natural heap `372.174 ms`; L1 heap direct summary `4.55 s` x20; L2 heap direct `227.036 ms` | L1 checked stream/scoped direct summary `4.56/4.59 s` x20; L2 checked scoped direct `230.374 ms` | checked is tied/near same-shape heap | heap direct still reports small non-region GC in L2 | L1 checked RSS lower than heap direct | Symmetric topology/operator lower bound; not memory-placement evidence. |
| GH Archive-shaped direct q2 | generated/preloaded stressor | summary-only topology | natural heap `287.380 ms`; L1 heap direct summary `1.36 s` x20; L2 heap direct `54.642 ms` | L1 checked stream/scoped direct summary `1.45/1.45 s` x20; L2 checked scoped direct `56.013 ms` | checked direct is within about `7%` of heap direct in L1 | heap direct has `0 ms` GC | near-tie small RSS | Symmetric topology/operator evidence for heap and regions, not memory-placement evidence. |
| LogHub-shaped direct q2 | generated/indexable log stream | summary-only topology | natural heap `526.803 ms`; L1 heap direct summary `4.23 s` x20; L2 heap direct `191.601 ms` | L1 checked stream/scoped direct summary `4.39/4.38 s` x20; L2 checked scoped direct `193.938 ms` | checked is within about `4%` of same-shape heap in L1 | heap direct has `0 ms` GC | near-tie small RSS | Symmetric direct-aggregate topology evidence. |
| LogHub-shaped direct q3 | generated/indexable template/session stream | summary-only topology | natural heap `2225.364 ms`; L1 heap direct summary `37.01 s` x20; L2 heap direct `1779.064 ms` | L1 checked stream/scoped direct summary `37.65/38.00 s` x20; L2 checked scoped direct `1792.397 ms` | checked is within about `2-3%` of same-shape heap in L1 | heap direct has `0 ms` median GC but q3 has occasional GC in L2 | near-tie small RSS | Symmetric topology evidence; richer query remains CPU-heavy. |
| Yak LiveJournal graphreal 50M | real SNAP LiveJournal edge list replay | best checked topology | heap `2958.659 ms`, GC `400.484 ms`, RSS `3.91 GB` | `checked-epoch-scoped` `2008.320 ms`, GC `0 ms`, RSS `2.11 GB` | `32.1%` faster | `-400.484 ms` | about `-46%` | Strongest real-input prior-work-shaped checked epoch win; local graph replay, not exact Yak/GraphChi artifact. |
| Yak LiveJournal graphreal 20M streaming-file | real-streaming-input SNAP LiveJournal gzip edge stream | best checked topology / L1 final-clean plus L2 standard stats / fixed-memory | L1 heap `18.32 s`, RSS `577 MB`; L2 heap `6333.745 ms`, GC `165.387 ms`; heap cap passes `128M` and fails `64M` | L1 `checked-epoch-scoped` `17.15 s`, RSS `102 MB`; L2 `checked-epoch-stream` `5530.190 ms`, GC `0 ms`, region op `2.869 ms`; checked epoch rows pass `64M` and `32M` caps | L1 checked scoped `6.4%` faster; L2 checked stream `12.7%` faster | L2 removes `165.387 ms`, but heap GC is only about `2.6%` of L2 | L1 about `-82%` | True compressed-source streaming graph row. Use as real-streaming graph RSS/fixed-memory and throughput evidence; not a GC-time-heavy flagship and not exact Yak/GraphChi artifact reproduction. Heap-cap rows are one-run probes. |
| Yak topword reusable top-k 10M x20 | Yak-style generated methodology | retained-object drop-anchor / reusable operator gate / L1 final-clean | L1 natural heap `6.25 s`, RSS `75 MB`; same-shape heap top-k retained `5.72 s`, RSS `147 MB`; L2 heap GC `44.654/71.767 ms` | L1 `checked-epoch-topk-scoped` `4.94 s`, RSS `16 MB`; L2 checked `249.311 ms`, GC `0 ms` | L1 `21.0%` faster than natural heap; `13.6%` faster than same-shape heap top-k | L2 removes timed heap GC | L1 about `-79%` vs natural heap and `-89%` vs same-shape heap top-k | Reusable top-k API passes on a second natural top-k workload, but older `checked-epoch-scoped` close-traversal topology is still faster in L1 (`4.61 s`) for this local topword shape. |
| Yak AskUbuntu `topwordreal` 10M x5 | real Stack Exchange AskUbuntu `Posts.xml` text replay | best checked topology / L1 final-clean | L1 natural heap `4.19 s`, RSS `428 MB`; same-shape heap top-k retained `4.40 s`, RSS `428 MB`; L2 heap `269.491 ms`, GC `23.715 ms` | L1 `checked-epoch-scoped` `3.86 s`, RSS `94 MB`; reusable top-k scoped `4.12 s`, RSS `94 MB`; L2 direct checked `207.490 ms`, GC `0 ms` | L1 direct checked `7.9%` faster than natural heap; reusable top-k `1.7%` faster than natural heap but slower than direct epoch | L2 direct checked removes `23.715 ms` heap GC | L1 about `-78%` vs natural heap | First real text/top-word Yak-style row. Direct checked epoch is the best safe topology; reusable top-k is an RSS/slight elapsed win but remains operator-cost gated. Not exact Yak/Hadoop evidence. |
| Yak AskUbuntu `topwordreal` 20M x5 | real Stack Exchange AskUbuntu `Posts.xml` text replay | best checked topology / L1 final-clean | L1 natural heap `7.77 s`, RSS `986 MB`; same-shape heap top-k retained `8.16 s`, RSS `986 MB`; L2 heap `511.485 ms`, GC `33.471 ms` | L1 `checked-epoch-scoped` `7.16 s`, RSS `174 MB`; reusable top-k scoped `7.86 s`, RSS `174 MB`; L2 direct checked `432.824 ms`, GC `0 ms` | L1 direct checked `7.9%` faster than natural heap; reusable top-k `1.2%` slower than natural heap | L2 direct checked removes `33.471 ms` heap GC | L1 about `-82%` vs natural heap | 20M scale-up strengthens real text checked epoch/RSS claim. Direct checked epoch remains the reportable safe framework win; reusable top-k stays gated for elapsed on this input. |
| Yak AskUbuntu `topwordreal` 5M streaming-file | real-streaming-input Stack Exchange AskUbuntu text from compressed `7z:` archive member | best checked topology / L1 final-clean plus L2 standard stats | L1 natural heap `6.74 s`, RSS `41.1 MB`; L2 heap `2109.524 ms`, GC `27.237 ms` | L1 `checked-epoch-scoped` `6.23 s`, RSS `15.0 MB`; L2 direct checked scoped `2061.736 ms`, GC `0 ms`; checked stream L1 `6.42 s`, RSS `15.0 MB` | L1 direct checked scoped `7.6%` faster than natural heap | L2 direct checked removes `27.237 ms`, but heap GC is only about `1.3%` of L2 | L1 about `-63%` vs natural heap | True compressed-source streaming-input text row. Useful RSS/fixed-memory and modest elapsed evidence; not a GC-heavy flagship because XML scan/tokenization dominates. |
| Dataflow SELECT/AGGREGATE/JOIN | Broom-style generated methodology | best checked topology | heap `27.775/50.837/30.387 ms`, GC `6.828/11.564/9.331 ms`, RSS `76 MB` | checked epoch scoped `19.691/34.676/19.762 ms`, GC `0 ms`, RSS `47 MB` | `29-35%` faster | removes timed heap GC | about `-38%` | Reusable direct epoch win across the full Dataflow operator family. |
| StreamFlex throughput 200k x20 | StreamFlex-style generated methodology | best checked topology / L1 final-clean | heap `0.79 s`, RSS `7.9 MB` | checked scoped direct epoch `0.58 s`, RSS `5.3 MB` | `26.6%` faster | L2 rows show timed GC removal; L1 intentionally omits GC reads | about `-33%` | L1 checked direct-epoch throughput win; direct epoch supersedes TransactionRegion for shared-batch pipeline throughput. |
| StreamFlex latency 10k x20 | StreamFlex-style generated methodology | best checked topology / L1 final-clean | heap `0.18 s`, p99 `792 ns`, max `327334 ns`, deadline misses `4` | checked scoped direct epoch `0.17 s`, p99 `833 ns`, max `25167 ns`, deadline misses `0` | `5.6%` faster | L2 rows show timed GC/tail context; L1 intentionally omits GC reads | near tie | L1 latency/deadline win: checked direct epoch removes deadline misses and reduces max tail in this local row. |
| StreamFlex design throughput | generated methodology / object-retained stream design | framework API win / L1 final-clean | 20M x3 L1 `gc-heap` `30.90 s`, RSS `12.4 MB` | optimized `checked-epoch-stream` `19.25 s`, RSS `12.6 MB`; legacy control `21.32 s`; `checked-epoch-scoped` `23.41 s` | checked stream `37.7%` faster than heap and `9.7%` faster than legacy checked stream | L2 1M: heap median GC `100.234 ms`; checked scoped median GC `0 ms` | near tie at 20M L1 | Rift-native StreamFlex stable/transient/capsule throughput evidence; handle-backed checked stream is now the default label, not a user-selected experiment. |
| StreamFlex design pressure latency | generated methodology / object-retained stream design | framework API win / tail-latency win | heap-same-shape `202.148 ms`, median GC `21.606 ms`, max `1356958 ns`, `22` deadline misses | `checked-epoch-scoped` `192.432 ms`, median GC `0.794 ms`, `1` miss; `checked-epoch-stream` max `20875 ns`, `0` misses | scoped checked fastest; streaming checked best tail/deadline row | `-20.812 ms` versus same-shape heap median GC | similar RSS in pressure row | StreamFlex-style allocation-pressure latency evidence: report throughput, GC, max latency, and misses separately. |
| Stancu-style transactions 200k x20 | transaction methodology probe | best checked topology / L1 final-clean | heap `0.85 s`, RSS `7.8 MB` | checked scoped direct epoch `0.57 s`, RSS `7.9 MB` | `32.9%` faster | L2 rows show timed GC removal; L1 intentionally omits GC reads | near tie | L1 checked transaction-boundary win; local methodology probe, not official SPEC. |
| SPECjbb2005 workload port, 8 warehouses x20 | clean-room transaction workload port | best checked topology / L1 final-clean | heap `2.64 s`, RSS `12.4 MB`; L2 heap GC `15.125 ms` per inner 8w run | checked epoch scoped `2.21 s`, RSS `8.0 MB`; L2 checked GC `0 ms` | `16.3%` faster | L2 removes heap timed GC on transaction-local objects | about `-35%` | L1 checked transaction/epoch win; clean-room Stancu/SPECjbb-shaped port, not official SPECjbb2005. |
| SPECjbb2005 workload port, 8M transactions | generated clean-room transaction workload port | prior-work-style generated methodology / Stancu axes / L1+L2 | L1 heap `4.89 s`, RSS `7.9 MB`; L2 heap `1379.590 ms`, GC `164.932 ms`, `520` collections | L1 checked epoch stream `4.35 s`, RSS `8.0 MB`; L2 checked epoch stream `996.765 ms`, GC `0.515 ms`, region op `4.075 ms`; L1 checked epoch scoped `3.95 s`, RSS `8.0 MB` | checked stream `11.0%` faster than heap at L1 and `27.7%` faster at L2; checked scoped `19.2%` faster at L1 | L2 removes almost all heap timed GC and reports region-freed proxy `41,585,448` objects / `1,919,417,920` bytes | roughly neutral RSS | Stronger current Stancu/SPECjbb-style methodology row. It is generated deterministic workload evidence, not real-input proof and not official SPECjbb2005. |
| SPECjbb2005 workload port, 4 warehouses | clean-room transaction workload port | handle-backed checked epoch promotion / L1+L2 gate | L1 heap `0.64 s`, RSS `7.9 MB`; L2 heap `67.378 ms`, GC `7.635 ms` | optimized checked epoch stream L1 `0.27 s`, RSS `6.8 MB`, L2 `51.168 ms`; legacy checked stream L1 `0.30 s`, L2 `56.371 ms`; checked scoped L1 `0.31 s`, L2 `54.146 ms`; rooted scoped L1 `0.34 s`, L2 `60.347 ms` | checked stream `57.8%` faster than heap and `10.0%` faster than legacy at L1 | L2 removes heap timed GC and reduces generic checked allocation path overhead | about `-14%` vs heap | First remaining-path audit win: backend-known checked allocation transfers from Dataflow/StreamFlex into the SPECjbb/Stancu transaction topology. Not official SPECjbb2005. |
| LogHub generated direct q2/q3 | generated/indexable log methodology | handle-backed checked epoch promotion / L2 gate | 1M q2/q3 heap `542.854/2161.937 ms`, GC `143.713/140.570 ms`, RSS `813 MB/2.29 GB` | optimized checked direct epoch `192.452/1794.369 ms`; legacy checked direct epoch `222.544/1837.885 ms`; checked scoped direct epoch `222.620/1869.150 ms` | optimized checked is `64.5%/17.0%` faster than heap and `13.5%/2.4%` faster than legacy checked | removes heap median timed GC in the direct-epoch rows | q2 about `-16%` RSS, q3 near-tie RSS | Generated allocation-lowering transfer evidence for LogHub q2/q3; not a real-input headline row. |
| LogHub generated page-token q2/q3 | generated/indexable log methodology | mechanism control / gated page-token lowering | 1M q2/q3 heap `518.300/2229.223 ms`, GC `126.070/160.218 ms` | explicit `rift-checked-page-token-open-handle` `548.894/2310.891 ms`; legacy `558.582/2357.261 ms`; checked scoped page-token `543.155/2448.068 ms` | open-handle is `1.7%/2.0%` faster than legacy but not a headline win | removes heap median timed GC, but q2/q3 page-token is not the best generated topology | near-tie/high RSS | Appendix/control evidence only; keep LogHub page-token default generic/legacy and use direct epoch for generated/indexable q2/q3. |
| Common Crawl WET-shaped q1 | generated stream stressor | best checked topology / L1 final-clean | 1M x3 L1 heap `16.67 s`, RSS `409 MB`; L2 heap q2 GC `1632.232 ms` shows the same pressure regime | optimized checked Rift page-token `9.30 s`, RSS `63 MB`; legacy checked page-token `10.29 s`; checked SafeZone-backed page-token `12.88 s` | optimized checked Rift page-token `44.2%` faster than heap and `9.6%` faster than legacy | L2 q2 rows show material heap GC removal | L1 about `-85%` | Strong generated stream-object pressure win; not real-input proof. |
| Common Crawl WET-shaped q2 | generated stream/window stressor | best checked topology / L1 final-clean | 1M x3 L1 heap `16.23 s`, RSS `409 MB`; L2 heap GC `1632.232 ms` | optimized checked Rift page-token `9.76 s`, RSS `63 MB`; legacy checked page-token `11.06 s`; checked SafeZone-backed page-token `14.39 s` | optimized checked Rift page-token `39.9%` faster than heap and `11.8%` faster than legacy | L2 optimized checked page-token GC `20.904 ms`; heap `1632.232 ms` | L1 about `-85%` | Strong generated window/object pressure win; handle-backed checked page-token is now the default label. |
| NEXMark q3/q8/q9/q11 | Beam-default generated methodology | best checked topology / L1 final-clean | heap L1 `6.18/9.54/16.27/4.47 s`, RSS `75/75/147/75 MB` | checked L1 `5.86/9.21/15.03/4.36 s`, RSS `9.6/10.2/13.2/14.2 MB` | `2.5-7.6%` faster | L2 rows remain the GC source; L1 intentionally omits GC reads | large RSS drop vs heap | L1 checked generated-methodology wins across selected NEXMark rows; not real-input proof or exact Beam runner evidence. |
| LogHub HDFS v1 q2 | real file-backed Hadoop log | best checked topology / L1 final-clean | L2 heap `8227.369 ms`, GC `92.659 ms`, RSS `409 MB`; L1 heap `25.60 s`, RSS `409 MB` for 3 q2 iterations | L2 checked scoped page-token `7871.856 ms`, GC `0 ms`, RSS `395 MB`; L1 checked scoped page-token `25.56 s`, RSS `79 MB` | L1 elapsed tie; L2 `4.3%` faster | L2 `-92.659 ms` | L1 about `-81%` | L1 real-input RSS win with elapsed tie; L2 standard stats remain a modest throughput/GC win. Heap GC is only about 1-2% elapsed, so this is not flagship GC-heavy proof. |
| LogHub HDFS q3 template/session streaming-file | real-streaming-input HDFS log replay | checked page/window token / L1 final-clean plus L2 standard stats | L1 heap `26.88 s`, RSS `862 MB`; L2 heap `8546.791 ms`, GC `97.322 ms`, max GC `131.533 ms` | L1 checked scoped page-token `30.29 s`, RSS `130 MB`; L2 checked `8763.838 ms`, GC `44.517 ms`, max GC `58.455 ms` | L1 `12.7%` slower | L2 median `-52.805 ms`, max `-73.078 ms` | L1 about `-85%` | Real-streaming-input RSS/fixed-memory and GC-tail control. The richer q3/session query streams the HDFS file without preloading, but parser/template/session CPU dominates and checked page-token is not a throughput win. |
| LogHub HDFS retained session/join streaming-file 1M active-16 | real-streaming-input HDFS log replay | retained session/join control | session heap `6595.172 ms`, GC `82.341 ms`; join heap `6837.810 ms`, GC `9.474 ms` | session checked Rift `6578.258 ms`, GC `5.572 ms`; join checked scoped `6681.557 ms` fastest but still reports nonzero GC from setup/runtime | session essentially tied; join checked scoped `2.3%` faster | session reduces timed GC by `76.769 ms`; join heap GC too small | 1M RSS not collected in sandboxed L2 run | Parked real-streaming retained-object control. It validates the retained session/join harness, but parser/hash/query CPU dominates and heap GC remains below the serious-case-study threshold. |
| LogHub Spark retained session archive-wide streaming 1M active-16 | real-streaming-input Spark logs from compressed `tar.gzcat` archive stream | retained session / fixed-memory evidence | L1 heap `27.62 s`, RSS `390.6 MB`; L2 heap `6642.276 ms`, GC `140.639 ms`, max GC `169.764 ms`; heap cap passes `256M` and fails `128M` | L1 checked Rift `20.30 s`, RSS `72.9 MB`; L2 checked Rift `6396.869 ms`, GC `14.407 ms`, region op `1.121 ms`; checked scoped L1 `19.85 s`, RSS `73.0 MB` | L1 checked scoped `28.1%` faster; L2 checked Rift `3.7%` faster | checked Rift L2 median `-126.232 ms`; heap GC is about `2.1%` of L2 | L1 about `-81%` | Strongest LogHub retained-session real-streaming fixed-memory/RSS row so far. Use as RSS/fixed-memory and modest checked-Rift throughput evidence; not a GC-time flagship because archive/parser/hash/query work dominates. |
| Wikimedia enwiki clickstream retained line-session 1M | real-streaming-input Wikimedia clickstream gzip stream | retained session / fixed-memory evidence | L1 heap `15.54 s`, RSS `864 MB`; L2 heap `4826.234 ms`, GC `166.100 ms`, max GC `217.036 ms`; heap cap passes `512M` and fails `256M`/`128M` | L1 checked Rift `14.15 s`, RSS `136 MB`; L2 checked Rift `5058.376 ms`, GC `11.537 ms`, region op `3.121 ms`; checked rows pass `128M` and `64M` caps | L1 checked Rift `8.9%` faster; L2 checked Rift `4.8%` slower | L2 median `-154.563 ms`; heap GC is about `3.4%` of L2 | L1 about `-84%` | Real compressed-stream retained-state RSS/fixed-memory row over Wikimedia enwiki clickstream. Use L1 for headline elapsed/RSS and L2 for GC interpretation; not a GC-time flagship and not a final named Wikimedia operator yet. |
| LogHub Spark q3 template/session | real file-backed Spark logs, 61-file application subset | ceiling/control / L2 standard stats plus L1 RSS | L2 heap `7602.328 ms`, GC `140.934 ms`; L1 RSS `408 MB` | L2 checked scoped page-token `7534.013 ms`, GC `31.147 ms`; L1 RSS `56 MB` | L2 `0.9%` faster | L2 median `-109.787 ms` | L1 about `-86%` | Real-input modest/control row. Richer Spark template/session materialization cuts RSS and timed GC, but heap timed GC is still only about `1.9%` of elapsed and the row is parser/query dominated. Do not use the anomalous L1 elapsed from this run. |
| DSPBench Fraud q2 | real DSPBench credit-card replay | best checked topology / L1 final-clean | L1 heap `4.39 s`, RSS `358 MB`; L2 heap `801.790 ms`, GC `69.686 ms` | L1 checked scoped page-token `4.44 s`, RSS `59.5 MB`; L2 checked scoped `822.846 ms`, GC `15.554 ms` | L1 `1.1%` slower | L2 median `-54.132 ms` | L1 about `-83%` | Real-input checked RSS win but not elapsed win; trusted Streaming lower bound is fastest (`4.18 s`). |
| DSPBench Log q2 | real DSPBench bundled common-log input | best checked topology / L1 final-clean | L1 heap `8.89 s`, RSS `308 MB`; L2 heap `1750.291 ms`, GC `44.992 ms`, max GC `88.210 ms` | L1 checked scoped page-token `8.79 s`, RSS `47.6 MB`; L2 checked scoped `1733.654 ms`, GC `18.402 ms`, max GC `18.584 ms` | L1 `1.1%` faster | L2 median `-26.590 ms`; max `-69.626 ms` | L1 about `-85%` | Modest real-input elapsed/RSS/GC-tail win; still not flagship GC-heavy evidence. |
| Theodolite power q2 streaming-file | real-streaming-input UCI household power-meter trace | best checked topology / L1 final-clean plus L2 standard stats | L1 heap `4.33 s`, RSS `75.3 MB`; L2 heap `1054.432 ms`, GC `19.906 ms` | L1 optimized `checked-epoch-stream` `3.80 s`, RSS `15.9 MB`; legacy checked stream `3.83 s`; checked scoped `3.83 s`; L2 optimized checked stream `993.191 ms`, GC `0 ms` | L1 `12.2%` faster than heap and `0.8%` faster than legacy; L2 `5.8%` faster than heap and `1.3%` faster than legacy | L2 median `-19.906 ms` vs heap | L1 about `-79%` | Real-streaming-input Theodolite row after replacing `String.split` with a byte-field cursor and promoting checked stream allocation to handle-backed lowering. It is a modest real-streaming throughput/RSS/fixed-memory win over heap and a small remaining-path allocation-lowering win over legacy checked stream. The older parser-heavy streaming row is superseded because it inflated GC (`143.088 ms` heap GC) with parser allocation. Older preloaded/full-local row remains a control (`5.45 s` checked vs `5.46 s` heap). |
| Theodolite retained UC4 q3 streaming-file | real-streaming-input UCI household power-meter trace | retained hierarchy/window objects / L1 final-clean plus L2 standard stats | Full local L1 heap `16.85 s`, RSS `207 MB`; L2 heap `4504.438 ms`, GC `335.309 ms`, max GC `482.380 ms`; heap `128M` cap `17.90 s`, heap `64M` cap fails | Full local L1 `checked-epoch-stream` `14.06 s`, RSS `26.6 MB`; L2 checked stream `3769.962 ms`, GC `31.570 ms`, region objects `26640640`; checked stream under `64M` cap `14.27 s`, RSS `26.6 MB` | L1 `16.6%` faster; L2 `16.3%` faster | L2 median `-303.739 ms`, max `-448.496 ms` | L1 about `-87%` | Strongest current real-streaming retained time-series row. It keeps the input compressed, streams the archive member, retains one measurement plus twelve hierarchy contribution objects per usable record, and shows throughput, RSS, GC, and fixed-memory wins. Not exact Theodolite artifact reproduction. |
| GH Archive q1/q2 byte-slice | real GH Archive file-backed JSON-lines | best checked topology / L1 final-clean | q1 heap `13.17 s`, RSS `265 MB`; q2 heap `13.18 s`, RSS `244 MB`; L2 heap GC about `58/62 ms` | q1 checked scoped page-token `12.89 s`, RSS `101 MB`; q2 checked scoped page-token `12.87 s`, RSS `102 MB`; L2 checked GC `0 ms` | q1 `2.1%` faster; q2 `2.4%` faster | L2 removes visible but small heap GC | q1 about `-62%`; q2 about `-58%` | L1 modest real-input elapsed/RSS win. Not GC-heavy flagship evidence because L2 heap GC is only about `1.5-1.6%` of elapsed; byte-slice parser scratch removes the old parser allocation cliff. |
| GH Archive q1/q2 byte-slice streaming-file 100k | real-streaming-input GH Archive gzip NDJSON replay | checked page/window token / L2 triage | q1 heap `10.39 s`, L2 `2325.844 ms`, max GC `71.641 ms`, RSS `169 MB`; q2 heap `9.38 s`, L2 `2151.431 ms`, max GC `72.159 ms`, RSS `169 MB` | q1 checked page-token `9.62 s`, L2 `1989.461 ms`, GC `0 ms`, RSS `162 MB`; q2 checked page-token `9.16 s`, L2 `2016.085 ms`, GC `0 ms`, RSS `162 MB` | q1 `7.4%` faster external / `14.5%` faster L2; q2 `2.3%` faster external / `6.3%` faster L2 | removes observed heap max-GC tail, but median heap GC is zero | about `-4%` RSS | Explicit `real-streaming-input` GH Archive row. Useful modest elapsed/RSS/tail evidence; not flagship GC-heavy because byte-slice parsing dominates and median heap GC is zero. |
| LogHub top templates HDFS 1M x20 | real HDFS file-backed/preloaded replay | retained-object drop-anchor / L1 final-clean | `heap-retained-drop-anchor` `5.46 s`, RSS `205 MB`; L2 heap GC `31.161 ms` per 1M run | checked scoped retained top templates `4.84 s`, RSS `28 MB`; L2 checked GC `0 ms` | `11.4%` faster | L2 removes heap timed GC | about `-86%` | L1 real-input retained top-k throughput/RSS win; process includes one input load plus 20 replays. |
| LogHub top templates 1M | generated LogHub-shaped stressor | retained-object drop-anchor | `heap-retained-drop-anchor` `424.443 ms`, GC `126.371 ms`, RSS `408 MB` | checked scoped retained top templates `290.610 ms`, GC `0 ms`, RSS `304 MB` | `31.5%` faster | `-126.371 ms` | about `-25%` | Generated retained top-k memory-management and RSS win; supports a reusable top-k API candidate. |
| LogHub reusable EpochTopKByKey HDFS 1M x20 | real HDFS file-backed/preloaded replay | retained-object drop-anchor / reusable operator gate / L1 final-clean | `heap-retained-drop-anchor` `5.52 s`, RSS `205 MB`; L2 heap `111.704 ms`, GC `30.542 ms` | L1 `checked-scoped-epoch-topk-retained-no-traverse` `4.88 s`, RSS `28 MB`; L2 checked `82.170 ms`, GC `0 ms` | L1 `11.6%` faster; L2 `26.4%` faster | L2 removes heap timed GC | about `-86%` in L1 | L1 reusable checked top-k API passes real-input retained gate with a strong RSS win; report-facing API overhead versus benchmark-local checked is now about `1.7%`. |
| LogHub reusable EpochTopKByKey HDFS 5M x5 | real HDFS file-backed/preloaded replay | retained-object drop-anchor / reusable operator gate / L1 final-clean | L1 `heap-retained-drop-anchor` `19.04 s`, RSS `504 MB`; L2 heap `463.633 ms`, GC `62.421 ms` | L1 `checked-scoped-epoch-topk-retained-no-traverse` `18.26 s`, RSS `92 MB`; L2 checked `402.916 ms`, GC `0 ms` | L1 `4.1%` faster; L2 `13.1%` faster | L2 removes heap timed GC | about `-82%` in L1 | Larger real-input retained top-k scale-up: modest L1 throughput win, strong RSS win, and clear L2 GC removal. |
| LogHub reusable EpochTopKByKey HDFS streaming-file 1M | real-streaming-input HDFS log replay | retained-object drop-anchor / reusable operator gate / L1 final-clean | L1 `heap-retained-drop-anchor` `8.10 s`, RSS `76 MB`; L2 heap `2765.068 ms`, GC `32.681 ms` | L1 `checked-scoped-epoch-topk-retained-no-traverse` `8.06 s`, RSS `12 MB`; L2 checked `2697.653 ms`, GC `0 ms` | L1 `0.5%` faster; L2 `2.4%` faster | L2 removes heap timed GC | about `-84%` in L1 | First true `real-streaming-input` row: input is consumed incrementally without parsed total-input arrays. Retained-object/RSS streaming evidence, not a huge-GC flagship because file/parser/query CPU dominates; benchmark-local checked retained is slightly faster than reusable top-k. |
| LogHub reusable EpochTopKByKey 1M | generated LogHub-shaped stressor | retained-object drop-anchor / reusable operator gate | `heap-retained-drop-anchor` `397.788 ms`, GC `126.601 ms`, RSS `408 MB` | `checked-scoped-epoch-topk-retained-no-traverse` `274.914 ms`, GC `0 ms`, RSS `305 MB` | `30.9%` faster | `-126.601 ms` | about `-25%` | Reusable checked top-k API passes generated retained gate; same-run overhead versus benchmark-local checked is about `5.7%`. |
| ReML-shaped Tier 2 logic/ray/tsp | local Scala Native ports | ceiling/control / L1 final-clean | `logic` heap `1.27 s`, RSS `7.9 MB`; `ray` heap `0.75 s`, RSS `4.1 MB`; `tsp` heap `3.40 s`, RSS `7.9 MB` | `logic` checked stream `1.27 s`, RSS `65.6 MB`; `ray` rooted/checked rows near `0.74-0.75 s`, RSS `4.1 MB`; `tsp` checked scoped `3.48 s`, RSS `5.9 MB` | logic tied; ray near-tie; tsp `2.4%` slower | L2 reduces/removes small timed GC, but GC is not material except logic's scaled heap row | logic RSS regression; ray near-tie; tsp about `-26%` RSS | Broader ReML-shaped local-port evidence, not a headline win. `logic` shows whole-region RSS risk, `ray` is compute/control, and `tsp` is an RSS/control row. |

## Current Claims

- **Memory-management claim:** retained heap versus retained checked epoch rows
  show that checked regions can reclaim ordinary retained Scala objects faster
  and with less GC work when lifetimes are epoch-structured.
- **Prior-work-style dataflow claim:** Broom retained timestamped aggregate and
  join now give the natural heap/GC versus checked Rift comparison reviewers
  expect from region papers, with material heap GC and large RSS reductions.
- **User-facing checked topology claim:** `RiftRegion.epoch { ... }` is now the
  default checked topology for batch/epoch workloads; page-token is the default
  checked topology for page/window append streams.
- **Generated stressor claim:** Common Crawl WET-shaped q1/q2 demonstrates the
  high-GC stream-object regime where checked page-token wins decisively.
- **Generated methodology claim:** NEXMark Beam-default-style q3/q8/q9/q11 now
  have L1 checked framework wins, but remain generated local-harness evidence.
- **Real-input claim:** Yak LiveJournal is the strongest real-input epoch row,
  and now also has a true compressed-source streaming-file variant with a
  20M-edge L1 checked-scoped RSS/fixed-memory and throughput win. AskUbuntu
  `topwordreal` adds the first real text/top-word checked epoch win,
  now with a 20M-token scale-up that keeps the same L1 speedup and increases
  the RSS reduction.
  LogHub top templates is now a real-preloaded retained top-k row at both
  1M x20 and 5M x5, and `EpochTopKByKey` is the first reusable top-k API to
  pass the retained gate. The same matrix now has the first
  `real-streaming-input` candidate row over HDFS `streaming-file`: checked
  scoped reusable top-k is a near-tie/slight throughput win and large RSS win while
  removing timed heap GC. Wikimedia enwiki clickstream adds a large compressed
  retained-session row with an L1 checked-Rift throughput/RSS win and heap-cap
  failure below `256M`, but still only `3.4%` heap L2 GC. Yak generated topword provides a second generated
  methodology top-k confirmation, while GH Archive byte-slice q1/q2, LogHub
  HDFS q2, and DSPBench Log q2 remain modest page/window rows.
- **Non-claim:** summary-only/direct-aggregate rows are topology/operator lower
  bounds. They must not be described as pure memory-management wins.

## Legacy / Rerun Required

These rows remain useful as history, diagnostics, or lower bounds, but they are
not presentation-headline evidence unless the action says they already have a
replacement.

| Evidence family | Why non-headline | Action | Presentation rule |
|---|---|---|---|
| Dirty page-token fast-path checkpoints | Collected before the committed clean fast-path state and may include transient local changes. | archive/control only | Cite only as motivation for the later clean page-token and Common Crawl-shaped L1 rows. |
| Dirty DSPBench Fraud q2 fast-path row | The dirty row made checked scoped page-token fastest, but the committed rerun was more conservative. | replace with L1 row | Use DSPBench Fraud q2 L1: checked scoped page-token is an RSS win and trusted Streaming is the lower-bound elapsed win. |
| Older L2 rows that now have L1 replacements | L2 reads GC/region counters in the timed section and is not final-clean headline timing. | keep as L2 interpretation only | Use L1 for elapsed/RSS and L2 only for GC/region explanations. |
| Old/current SafeZone root-mode-0 rows | They show provenance and old root-bookkeeping cliffs, not the fair SafeZone baseline. | archive/control only | Competitive tables use `region-scoped-rooted` / improved SafeZone-family rows; root-mode-0 appears only in historical/control tables. |
| Benchmark-local manual count arrays and direct-summary loops | They change the processing topology and often remove record retention entirely. | keep as lower-bound topology evidence | Always show heap and checked counterparts when available; never call these pure memory-management wins. |
| Exact-array Dataflow AGGREGATE rows used near `EpochFold` | The fast aggregate row is not the true generic `EpochFold` operator. | keep as lower-bound topology evidence | Present direct epoch/exact-array aggregate as the current win and keep generic `EpochFold` gated until it passes its own 1M API gate. |
| Older DEBS, TableRank, rank, median, and hash-heavy rows | Many predate the fair evaluation protocol or failed focused gates. | archive/control only | Do not use as final application claims; rerun only after natural heap, same-shape heap, retained controls, and focused 1M gates are defined. |
| Legacy GH Archive string-parser rows | Parser/string/decompression dominates and byte-slice L1 rows now replace them for current page-token evidence. | keep as L2 interpretation only | Use byte-slice GH Archive L1 rows for current elapsed/RSS; cite legacy parser rows only to explain parser allocation sensitivity. |

## Next Evidence Rules

- A future memory-management claim must include a retained-object drop-anchor
  control if ordinary records survive until close.
- A future rank/top-k/median/join claim must first add natural heap,
  same-shape heap, and retained controls before application integration.
  Current candidate status is tracked in `evidence/OPERATOR_GATE_STATUS.md`.
- Unsafe/rootless/trusted rows may be reported only as lower bounds or backend
  potential, never as final safe-system evidence.
