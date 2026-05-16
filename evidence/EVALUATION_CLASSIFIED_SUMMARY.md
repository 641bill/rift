# Evaluation Classified Summary

Date: 2026-05-09
Last updated: 2026-05-16 03:56 CEST

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
The latest retained-object prior-work row is
`evidence/BROOM_RETAINED_DATAFLOW_MATRIX.md`: a Broom/Naiad-style timestamped
aggregate/join matrix that headlines natural heap/GC versus checked Rift,
with ordinary event/value objects retained until timestamp notification.
The 2026-05-16 presentation normalization keeps this row as a first-class
prior-work-style headline row and keeps same-shape/drop-anchor rows in the
mechanism appendix unless they are explicitly being used for causality.
The latest Broom rerun adds `checked-region-scoped` as a best-safe-region
comparison row for the 20M aggregate/join scale point.

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
| Broom retained timestamped aggregate/join | complete, including 20M checked scoped backend comparison | complete, including 20M checked scoped backend interpretation | prior-work-style natural heap vs checked Rift retained dataflow | keep as the first Broom/Naiad-like GC-heavy dataflow row; same-shape controls are appendix-only and checked scoped is the safe backend comparison |
| GH Archive-shaped retained q2 | complete | complete | generated/preloaded retained-object row | keep; label generated/preloaded, not real-input proof |
| LogHub retained q2/q3 | complete | complete | generated/indexable retained rows | keep q2 as strong retained row; mark q3 checked-stream as modest/RSS row |
| DSPBench Fraud retained q2 | complete | complete | generated/indexable retained row | keep as modest retained win |
| Yak LiveJournal graphreal | complete | complete | real-input best checked epoch topology | keep as strongest real-input epoch row |
| Yak AskUbuntu topwordreal | complete at 10M and 20M | complete | real-input best checked epoch topology | keep as first real text/top-word row; 20M strengthens direct epoch claim |
| Dataflow SELECT/AGGREGATE/JOIN | complete | complete | Broom-style generated methodology, direct epoch API | keep as prior-work-shaped checked epoch row |
| StreamFlex throughput/latency | complete | complete | StreamFlex-style generated methodology, latency/deadline axes | keep; report latency tail/deadline misses separately from throughput |
| StreamFlex design stable/transient/capsule | complete for first 1M throughput and latency candidates | complete | StreamFlex-design generated methodology, checked framework API, latency/deadline axes | keep as Rift-native StreamFlex design reproduction; not exact Ovm artifact evidence |
| StreamIt BeamFormer/FilterBank ports | 3-run L1 complete | 3-run L2 complete | StreamFlex/StreamIt-style primitive DSP controls | keep as methodology/control rows; not GC-heavy memory-management wins |
| Stancu and SPECjbb2005 workload port | complete | complete | transaction/epoch topology | keep; label SPECjbb row as clean-room port, not official SPEC |
| Common Crawl WET-shaped q1/q2 | complete | complete | generated stream stressor, checked page-token | keep as generated high-object-pressure row only |
| NEXMark q3/q8/q9/q11 | complete | L2 remains interpretation source | generated Beam-default-style methodology | keep; not exact Beam runner evidence |
| LogHub HDFS top templates | complete at 1M and 5M | complete | real retained top-k API row | keep as strongest real retained top-k row |
| LogHub HDFS streaming-file top templates | complete for first 1M candidate | complete | real-streaming-input retained top-k API row | keep as first true streaming-input row; not yet flagship GC-heavy evidence |
| LogHub HDFS q2/q3 streaming, Spark/Windows q3, DSPBench Log q2, GH Archive q1/q2, Theodolite power q2 | complete where used; Spark q3 L1 elapsed not promoted because `/usr/bin/time` real field was anomalous | complete | real-input and real-streaming-input page/window/epoch modest/RSS/control rows | keep as real-input modest/control evidence; HDFS q3 streaming is an RSS/fixed-memory control, not a throughput win |
| ReML/MLKit Tier 1 and first Tier 2 ports | complete for local ports | complete for local ports | local Scala Native port evidence | keep same-axes table; no raw ReML-vs-Rift wall-clock claim |
| Summary-only/direct-aggregate rows | complete for selected symmetric rows | complete where needed | topology lower bound | keep only with heap and checked counterparts; never claim reclaim win |

## Classified Rows

| Benchmark / row | Input type | Comparison class | Heap/control row | Best safe checked row | Elapsed delta | GC delta | RSS delta | Allowed claim |
|---|---|---|---|---|---:|---:|---:|---|
| Broom retained timestamped aggregate 20M | generated Broom/Naiad-style timestamped dataflow | natural heap baseline / prior-work-style retained dataflow | natural heap `5.27 s` L1, RSS `75.8 MB`; L2 `1728.037 ms`, GC `410.002 ms` | checked Rift `3.59 s` L1, RSS `13.6 MB`; L2 `1248.788 ms`, GC `0 ms`; checked scoped `4.55 s`, RSS `13.7 MB` | L1 `31.9%` faster; L2 `27.7%` faster | L2 `-410.002 ms` | L1 about `-82%` | Strong Broom-style retained-object GC/RSS/throughput win. Headline comparison is natural heap/GC versus checked Rift; same-shape/drop-anchor controls are appendix/mechanism evidence only. Checked scoped is now available as the safe backend comparison row. |
| Broom retained timestamped join 20M | generated Broom/Naiad-style timestamped dataflow | natural heap baseline / prior-work-style retained dataflow | natural heap `5.00 s` L1, RSS `74.7 MB`; L2 `1686.550 ms`, GC `267.636 ms` | checked Rift `4.26 s` L1, RSS `12.8 MB`; L2 `1465.638 ms`, GC `0 ms`; checked scoped `4.52 s`, RSS `13.0 MB` | L1 `14.8%` faster; L2 `13.1%` faster | L2 `-267.636 ms` | L1 about `-83%` | Broom-style retained join win with material heap GC and large RSS reduction. Checked scoped is also faster than heap and remains a backend comparison row. |
| Broom retained high-active aggregate/join 1M | generated Broom/Naiad-style high-live-state dataflow | natural heap baseline / prior-work-style retained dataflow / fixed-memory | aggregate heap `0.67 s`, RSS `232 MB`; join heap `0.63 s`, RSS `239 MB`; heap completes at `256M` but OOMs at `128M`/`64M` | aggregate checked Rift `0.51 s`, RSS `53 MB`; join checked Rift `0.42-0.45 s`, RSS `56 MB` | aggregate `23.9%` faster; join `29-33%` faster | L2 removes `53.115/28.080 ms` heap GC | about `-76%` to `-77%` | High-cardinality/multiple-active-timestamp variant confirms live-state RSS, GC pressure, and fixed-memory behavior. |
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
| Yak topword reusable top-k 10M x20 | Yak-style generated methodology | retained-object drop-anchor / reusable operator gate / L1 final-clean | L1 natural heap `6.25 s`, RSS `75 MB`; same-shape heap top-k retained `5.72 s`, RSS `147 MB`; L2 heap GC `44.654/71.767 ms` | L1 `checked-epoch-topk-scoped` `4.94 s`, RSS `16 MB`; L2 checked `249.311 ms`, GC `0 ms` | L1 `21.0%` faster than natural heap; `13.6%` faster than same-shape heap top-k | L2 removes timed heap GC | L1 about `-79%` vs natural heap and `-89%` vs same-shape heap top-k | Reusable top-k API passes on a second natural top-k workload, but older `checked-epoch-scoped` close-traversal topology is still faster in L1 (`4.61 s`) for this local topword shape. |
| Yak AskUbuntu `topwordreal` 10M x5 | real Stack Exchange AskUbuntu `Posts.xml` text replay | best checked topology / L1 final-clean | L1 natural heap `4.19 s`, RSS `428 MB`; same-shape heap top-k retained `4.40 s`, RSS `428 MB`; L2 heap `269.491 ms`, GC `23.715 ms` | L1 `checked-epoch-scoped` `3.86 s`, RSS `94 MB`; reusable top-k scoped `4.12 s`, RSS `94 MB`; L2 direct checked `207.490 ms`, GC `0 ms` | L1 direct checked `7.9%` faster than natural heap; reusable top-k `1.7%` faster than natural heap but slower than direct epoch | L2 direct checked removes `23.715 ms` heap GC | L1 about `-78%` vs natural heap | First real text/top-word Yak-style row. Direct checked epoch is the best safe topology; reusable top-k is an RSS/slight elapsed win but remains operator-cost gated. Not exact Yak/Hadoop evidence. |
| Yak AskUbuntu `topwordreal` 20M x5 | real Stack Exchange AskUbuntu `Posts.xml` text replay | best checked topology / L1 final-clean | L1 natural heap `7.77 s`, RSS `986 MB`; same-shape heap top-k retained `8.16 s`, RSS `986 MB`; L2 heap `511.485 ms`, GC `33.471 ms` | L1 `checked-epoch-scoped` `7.16 s`, RSS `174 MB`; reusable top-k scoped `7.86 s`, RSS `174 MB`; L2 direct checked `432.824 ms`, GC `0 ms` | L1 direct checked `7.9%` faster than natural heap; reusable top-k `1.2%` slower than natural heap | L2 direct checked removes `33.471 ms` heap GC | L1 about `-82%` vs natural heap | 20M scale-up strengthens real text checked epoch/RSS claim. Direct checked epoch remains the reportable safe framework win; reusable top-k stays gated for elapsed on this input. |
| Dataflow SELECT/AGGREGATE/JOIN | Broom-style generated methodology | best checked topology | heap `27.775/50.837/30.387 ms`, GC `6.828/11.564/9.331 ms`, RSS `76 MB` | checked epoch scoped `19.691/34.676/19.762 ms`, GC `0 ms`, RSS `47 MB` | `29-35%` faster | removes timed heap GC | about `-38%` | Reusable direct epoch win across the full Dataflow operator family. |
| StreamFlex throughput 200k x20 | StreamFlex-style generated methodology | best checked topology / L1 final-clean | heap `0.79 s`, RSS `7.9 MB` | checked scoped direct epoch `0.58 s`, RSS `5.3 MB` | `26.6%` faster | L2 rows show timed GC removal; L1 intentionally omits GC reads | about `-33%` | L1 checked direct-epoch throughput win; direct epoch supersedes TransactionRegion for shared-batch pipeline throughput. |
| StreamFlex latency 10k x20 | StreamFlex-style generated methodology | best checked topology / L1 final-clean | heap `0.18 s`, p99 `792 ns`, max `327334 ns`, deadline misses `4` | checked scoped direct epoch `0.17 s`, p99 `833 ns`, max `25167 ns`, deadline misses `0` | `5.6%` faster | L2 rows show timed GC/tail context; L1 intentionally omits GC reads | near tie | L1 latency/deadline win: checked direct epoch removes deadline misses and reduces max tail in this local row. |
| StreamFlex design throughput | generated methodology / object-retained stream design | framework API win / L1 final-clean | 20M x3 L1 `gc-heap` `30.90 s`, RSS `12.4 MB` | optimized `checked-epoch-stream` `19.25 s`, RSS `12.6 MB`; legacy control `21.32 s`; `checked-epoch-scoped` `23.41 s` | checked stream `37.7%` faster than heap and `9.7%` faster than legacy checked stream | L2 1M: heap median GC `100.234 ms`; checked scoped median GC `0 ms` | near tie at 20M L1 | Rift-native StreamFlex stable/transient/capsule throughput evidence; handle-backed checked stream is now the default label, not a user-selected experiment. |
| StreamFlex design pressure latency | generated methodology / object-retained stream design | framework API win / tail-latency win | heap-same-shape `202.148 ms`, median GC `21.606 ms`, max `1356958 ns`, `22` deadline misses | `checked-epoch-scoped` `192.432 ms`, median GC `0.794 ms`, `1` miss; `checked-epoch-stream` max `20875 ns`, `0` misses | scoped checked fastest; streaming checked best tail/deadline row | `-20.812 ms` versus same-shape heap median GC | similar RSS in pressure row | StreamFlex-style allocation-pressure latency evidence: report throughput, GC, max latency, and misses separately. |
| Stancu-style transactions 200k x20 | transaction methodology probe | best checked topology / L1 final-clean | heap `0.85 s`, RSS `7.8 MB` | checked scoped direct epoch `0.57 s`, RSS `7.9 MB` | `32.9%` faster | L2 rows show timed GC removal; L1 intentionally omits GC reads | near tie | L1 checked transaction-boundary win; local methodology probe, not official SPEC. |
| SPECjbb2005 workload port, 8 warehouses x20 | clean-room transaction workload port | best checked topology / L1 final-clean | heap `2.64 s`, RSS `12.4 MB`; L2 heap GC `15.125 ms` per inner 8w run | checked epoch scoped `2.21 s`, RSS `8.0 MB`; L2 checked GC `0 ms` | `16.3%` faster | L2 removes heap timed GC on transaction-local objects | about `-35%` | L1 checked transaction/epoch win; clean-room Stancu/SPECjbb-shaped port, not official SPECjbb2005. |
| SPECjbb2005 workload port, 4 warehouses | clean-room transaction workload port | handle-backed checked epoch promotion / L1+L2 gate | L1 heap `0.64 s`, RSS `7.9 MB`; L2 heap `67.378 ms`, GC `7.635 ms` | optimized checked epoch stream L1 `0.27 s`, RSS `6.8 MB`, L2 `51.168 ms`; legacy checked stream L1 `0.30 s`, L2 `56.371 ms`; checked scoped L1 `0.31 s`, L2 `54.146 ms`; rooted scoped L1 `0.34 s`, L2 `60.347 ms` | checked stream `57.8%` faster than heap and `10.0%` faster than legacy at L1 | L2 removes heap timed GC and reduces generic checked allocation path overhead | about `-14%` vs heap | First remaining-path audit win: backend-known checked allocation transfers from Dataflow/StreamFlex into the SPECjbb/Stancu transaction topology. Not official SPECjbb2005. |
| Common Crawl WET-shaped q1 | generated stream stressor | best checked topology / L1 final-clean | 1M x3 L1 heap `16.67 s`, RSS `409 MB`; L2 heap q2 GC `1632.232 ms` shows the same pressure regime | optimized checked Rift page-token `9.30 s`, RSS `63 MB`; legacy checked page-token `10.29 s`; checked SafeZone-backed page-token `12.88 s` | optimized checked Rift page-token `44.2%` faster than heap and `9.6%` faster than legacy | L2 q2 rows show material heap GC removal | L1 about `-85%` | Strong generated stream-object pressure win; not real-input proof. |
| Common Crawl WET-shaped q2 | generated stream/window stressor | best checked topology / L1 final-clean | 1M x3 L1 heap `16.23 s`, RSS `409 MB`; L2 heap GC `1632.232 ms` | optimized checked Rift page-token `9.76 s`, RSS `63 MB`; legacy checked page-token `11.06 s`; checked SafeZone-backed page-token `14.39 s` | optimized checked Rift page-token `39.9%` faster than heap and `11.8%` faster than legacy | L2 optimized checked page-token GC `20.904 ms`; heap `1632.232 ms` | L1 about `-85%` | Strong generated window/object pressure win; handle-backed checked page-token is now the default label. |
| NEXMark q3/q8/q9/q11 | Beam-default generated methodology | best checked topology / L1 final-clean | heap L1 `6.18/9.54/16.27/4.47 s`, RSS `75/75/147/75 MB` | checked L1 `5.86/9.21/15.03/4.36 s`, RSS `9.6/10.2/13.2/14.2 MB` | `2.5-7.6%` faster | L2 rows remain the GC source; L1 intentionally omits GC reads | large RSS drop vs heap | L1 checked generated-methodology wins across selected NEXMark rows; not real-input proof or exact Beam runner evidence. |
| LogHub HDFS v1 q2 | real file-backed Hadoop log | best checked topology / L1 final-clean | L2 heap `8227.369 ms`, GC `92.659 ms`, RSS `409 MB`; L1 heap `25.60 s`, RSS `409 MB` for 3 q2 iterations | L2 checked scoped page-token `7871.856 ms`, GC `0 ms`, RSS `395 MB`; L1 checked scoped page-token `25.56 s`, RSS `79 MB` | L1 elapsed tie; L2 `4.3%` faster | L2 `-92.659 ms` | L1 about `-81%` | L1 real-input RSS win with elapsed tie; L2 standard stats remain a modest throughput/GC win. Heap GC is only about 1-2% elapsed, so this is not flagship GC-heavy proof. |
| LogHub HDFS q3 template/session streaming-file | real-streaming-input HDFS log replay | checked page/window token / L1 final-clean plus L2 standard stats | L1 heap `26.88 s`, RSS `862 MB`; L2 heap `8546.791 ms`, GC `97.322 ms`, max GC `131.533 ms` | L1 checked scoped page-token `30.29 s`, RSS `130 MB`; L2 checked `8763.838 ms`, GC `44.517 ms`, max GC `58.455 ms` | L1 `12.7%` slower | L2 median `-52.805 ms`, max `-73.078 ms` | L1 about `-85%` | Real-streaming-input RSS/fixed-memory and GC-tail control. The richer q3/session query streams the HDFS file without preloading, but parser/template/session CPU dominates and checked page-token is not a throughput win. |
| LogHub Spark q3 template/session | real file-backed Spark logs, 61-file application subset | ceiling/control / L2 standard stats plus L1 RSS | L2 heap `7602.328 ms`, GC `140.934 ms`; L1 RSS `408 MB` | L2 checked scoped page-token `7534.013 ms`, GC `31.147 ms`; L1 RSS `56 MB` | L2 `0.9%` faster | L2 median `-109.787 ms` | L1 about `-86%` | Real-input modest/control row. Richer Spark template/session materialization cuts RSS and timed GC, but heap timed GC is still only about `1.9%` of elapsed and the row is parser/query dominated. Do not use the anomalous L1 elapsed from this run. |
| DSPBench Fraud q2 | real DSPBench credit-card replay | best checked topology / L1 final-clean | L1 heap `4.39 s`, RSS `358 MB`; L2 heap `801.790 ms`, GC `69.686 ms` | L1 checked scoped page-token `4.44 s`, RSS `59.5 MB`; L2 checked scoped `822.846 ms`, GC `15.554 ms` | L1 `1.1%` slower | L2 median `-54.132 ms` | L1 about `-83%` | Real-input checked RSS win but not elapsed win; trusted Streaming lower bound is fastest (`4.18 s`). |
| DSPBench Log q2 | real DSPBench bundled common-log input | best checked topology / L1 final-clean | L1 heap `8.89 s`, RSS `308 MB`; L2 heap `1750.291 ms`, GC `44.992 ms`, max GC `88.210 ms` | L1 checked scoped page-token `8.79 s`, RSS `47.6 MB`; L2 checked scoped `1733.654 ms`, GC `18.402 ms`, max GC `18.584 ms` | L1 `1.1%` faster | L2 median `-26.590 ms`; max `-69.626 ms` | L1 about `-85%` | Modest real-input elapsed/RSS/GC-tail win; still not flagship GC-heavy evidence. |
| Theodolite power q2 streaming-file | real-streaming-input UCI household power-meter trace | best checked topology / L1 final-clean plus L2 standard stats | L1 heap `4.33 s`, RSS `75.3 MB`; L2 heap `1054.432 ms`, GC `19.906 ms` | L1 optimized `checked-epoch-stream` `3.80 s`, RSS `15.9 MB`; legacy checked stream `3.83 s`; checked scoped `3.83 s`; L2 optimized checked stream `993.191 ms`, GC `0 ms` | L1 `12.2%` faster than heap and `0.8%` faster than legacy; L2 `5.8%` faster than heap and `1.3%` faster than legacy | L2 median `-19.906 ms` vs heap | L1 about `-79%` | Real-streaming-input Theodolite row after replacing `String.split` with a byte-field cursor and promoting checked stream allocation to handle-backed lowering. It is a modest real-streaming throughput/RSS/fixed-memory win over heap and a small remaining-path allocation-lowering win over legacy checked stream. The older parser-heavy streaming row is superseded because it inflated GC (`143.088 ms` heap GC) with parser allocation. Older preloaded/full-local row remains a control (`5.45 s` checked vs `5.46 s` heap). |
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
- **Real-input claim:** Yak LiveJournal is the strongest real-input epoch row.
  AskUbuntu `topwordreal` adds the first real text/top-word checked epoch win,
  now with a 20M-token scale-up that keeps the same L1 speedup and increases
  the RSS reduction.
  LogHub top templates is now a real-preloaded retained top-k row at both
  1M x20 and 5M x5, and `EpochTopKByKey` is the first reusable top-k API to
  pass the retained gate. The same matrix now has the first
  `real-streaming-input` candidate row over HDFS `streaming-file`: checked
  scoped reusable top-k is a near-tie/slight throughput win and large RSS win while
  removing timed heap GC. Yak generated topword provides a second generated
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
