# Evaluation Classified Summary

Date: 2026-05-09
Last updated: 2026-05-11 01:08 CEST

Status: thesis-facing classified summary built from committed evidence.
Baseline commits for clean rows: parent `1cc3b2c`, child `13a3df1c7`.
Reusable top-k API rows include the increment hot-path follow-up after child
commit `bc9fd5979`, the Yak topword same-shape/L1 follow-up, and the larger
real HDFS 5M top-template scale-up from child `0773d4c17`.

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

## Classified Rows

| Benchmark / row | Input type | Comparison class | Heap/control row | Best safe checked row | Elapsed delta | GC delta | RSS delta | Allowed claim |
|---|---|---|---|---|---:|---:|---:|---|
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
| Dataflow SELECT/AGGREGATE/JOIN | Broom-style generated methodology | best checked topology | heap `27.775/50.837/30.387 ms`, GC `6.828/11.564/9.331 ms`, RSS `76 MB` | checked epoch scoped `19.691/34.676/19.762 ms`, GC `0 ms`, RSS `47 MB` | `29-35%` faster | removes timed heap GC | about `-38%` | Reusable direct epoch win across the full Dataflow operator family. |
| StreamFlex throughput 200k x20 | StreamFlex-style generated methodology | best checked topology / L1 final-clean | heap `0.79 s`, RSS `7.9 MB` | checked scoped direct epoch `0.58 s`, RSS `5.3 MB` | `26.6%` faster | L2 rows show timed GC removal; L1 intentionally omits GC reads | about `-33%` | L1 checked direct-epoch throughput win; direct epoch supersedes TransactionRegion for shared-batch pipeline throughput. |
| StreamFlex latency 10k x20 | StreamFlex-style generated methodology | best checked topology / L1 final-clean | heap `0.18 s`, p99 `792 ns`, max `327334 ns`, deadline misses `4` | checked scoped direct epoch `0.17 s`, p99 `833 ns`, max `25167 ns`, deadline misses `0` | `5.6%` faster | L2 rows show timed GC/tail context; L1 intentionally omits GC reads | near tie | L1 latency/deadline win: checked direct epoch removes deadline misses and reduces max tail in this local row. |
| Stancu-style transactions 200k x20 | transaction methodology probe | best checked topology / L1 final-clean | heap `0.85 s`, RSS `7.8 MB` | checked scoped direct epoch `0.57 s`, RSS `7.9 MB` | `32.9%` faster | L2 rows show timed GC removal; L1 intentionally omits GC reads | near tie | L1 checked transaction-boundary win; local methodology probe, not official SPEC. |
| SPECjbb2005 workload port, 8 warehouses x20 | clean-room transaction workload port | best checked topology / L1 final-clean | heap `2.64 s`, RSS `12.4 MB`; L2 heap GC `15.125 ms` per inner 8w run | checked epoch scoped `2.21 s`, RSS `8.0 MB`; L2 checked GC `0 ms` | `16.3%` faster | L2 removes heap timed GC on transaction-local objects | about `-35%` | L1 checked transaction/epoch win; clean-room Stancu/SPECjbb-shaped port, not official SPECjbb2005. |
| Common Crawl WET-shaped q1 | generated stream stressor | best checked topology | heap `5577.965 ms`, GC `1741.640 ms`, RSS `409 MB` | checked scoped page-token `3707.214 ms`, GC `30.693 ms`, RSS `464 MB` | `33.5%` faster | `-1711 ms` | about `+14%` | Strong generated stream-object pressure win; not real-input proof and not RSS win. |
| Common Crawl WET-shaped q2 | generated stream/window stressor | best checked topology | heap `5183.074 ms`, GC `1565.074 ms`, RSS `409 MB` | checked scoped page-token `3902.795 ms`, GC `27.027 ms`, RSS `464 MB` | `24.7%` faster | `-1538 ms` | about `+14%` | Strong generated window/object pressure win; not real-input proof and not RSS win. |
| NEXMark q3/q8/q9/q11 | Beam-default generated methodology | best checked topology / L1 final-clean | heap L1 `6.18/9.54/16.27/4.47 s`, RSS `75/75/147/75 MB` | checked L1 `5.86/9.21/15.03/4.36 s`, RSS `9.6/10.2/13.2/14.2 MB` | `2.5-7.6%` faster | L2 rows remain the GC source; L1 intentionally omits GC reads | large RSS drop vs heap | L1 checked generated-methodology wins across selected NEXMark rows; not real-input proof or exact Beam runner evidence. |
| LogHub HDFS v1 q2 | real file-backed Hadoop log | best checked topology / L1 final-clean | L2 heap `8227.369 ms`, GC `92.659 ms`, RSS `409 MB`; L1 heap `25.60 s`, RSS `409 MB` for 3 q2 iterations | L2 checked scoped page-token `7871.856 ms`, GC `0 ms`, RSS `395 MB`; L1 checked scoped page-token `25.56 s`, RSS `79 MB` | L1 elapsed tie; L2 `4.3%` faster | L2 `-92.659 ms` | L1 about `-81%` | L1 real-input RSS win with elapsed tie; L2 standard stats remain a modest throughput/GC win. Heap GC is only about 1-2% elapsed, so this is not flagship GC-heavy proof. |
| DSPBench Fraud q2 | real DSPBench credit-card replay | best checked topology / L1 final-clean | L1 heap `4.39 s`, RSS `358 MB`; L2 heap `801.790 ms`, GC `69.686 ms` | L1 checked scoped page-token `4.44 s`, RSS `59.5 MB`; L2 checked scoped `822.846 ms`, GC `15.554 ms` | L1 `1.1%` slower | L2 median `-54.132 ms` | L1 about `-83%` | Real-input checked RSS win but not elapsed win; trusted Streaming lower bound is fastest (`4.18 s`). |
| DSPBench Log q2 | real DSPBench bundled common-log input | best checked topology / L1 final-clean | L1 heap `8.89 s`, RSS `308 MB`; L2 heap `1750.291 ms`, GC `44.992 ms`, max GC `88.210 ms` | L1 checked scoped page-token `8.79 s`, RSS `47.6 MB`; L2 checked scoped `1733.654 ms`, GC `18.402 ms`, max GC `18.584 ms` | L1 `1.1%` faster | L2 median `-26.590 ms`; max `-69.626 ms` | L1 about `-85%` | Modest real-input elapsed/RSS/GC-tail win; still not flagship GC-heavy evidence. |
| GH Archive q1/q2 byte-slice | real GH Archive file-backed JSON-lines | best checked topology / L1 final-clean | q1 heap `13.17 s`, RSS `265 MB`; q2 heap `13.18 s`, RSS `244 MB`; L2 heap GC about `58/62 ms` | q1 checked scoped page-token `12.89 s`, RSS `101 MB`; q2 checked scoped page-token `12.87 s`, RSS `102 MB`; L2 checked GC `0 ms` | q1 `2.1%` faster; q2 `2.4%` faster | L2 removes visible but small heap GC | q1 about `-62%`; q2 about `-58%` | L1 modest real-input elapsed/RSS win. Not GC-heavy flagship evidence because L2 heap GC is only about `1.5-1.6%` of elapsed; byte-slice parser scratch removes the old parser allocation cliff. |
| LogHub top templates HDFS 1M x20 | real HDFS file-backed/preloaded replay | retained-object drop-anchor / L1 final-clean | `heap-retained-drop-anchor` `5.46 s`, RSS `205 MB`; L2 heap GC `31.161 ms` per 1M run | checked scoped retained top templates `4.84 s`, RSS `28 MB`; L2 checked GC `0 ms` | `11.4%` faster | L2 removes heap timed GC | about `-86%` | L1 real-input retained top-k throughput/RSS win; process includes one input load plus 20 replays. |
| LogHub top templates 1M | generated LogHub-shaped stressor | retained-object drop-anchor | `heap-retained-drop-anchor` `424.443 ms`, GC `126.371 ms`, RSS `408 MB` | checked scoped retained top templates `290.610 ms`, GC `0 ms`, RSS `304 MB` | `31.5%` faster | `-126.371 ms` | about `-25%` | Generated retained top-k memory-management and RSS win; supports a reusable top-k API candidate. |
| LogHub reusable EpochTopKByKey HDFS 1M x20 | real HDFS file-backed/preloaded replay | retained-object drop-anchor / reusable operator gate / L1 final-clean | `heap-retained-drop-anchor` `5.52 s`, RSS `205 MB`; L2 heap `111.704 ms`, GC `30.542 ms` | L1 `checked-scoped-epoch-topk-retained-no-traverse` `4.88 s`, RSS `28 MB`; L2 checked `82.170 ms`, GC `0 ms` | L1 `11.6%` faster; L2 `26.4%` faster | L2 removes heap timed GC | about `-86%` in L1 | L1 reusable checked top-k API passes real-input retained gate with a strong RSS win; report-facing API overhead versus benchmark-local checked is now about `1.7%`. |
| LogHub reusable EpochTopKByKey HDFS 5M x5 | real HDFS file-backed/preloaded replay | retained-object drop-anchor / reusable operator gate / L1 final-clean | L1 `heap-retained-drop-anchor` `19.04 s`, RSS `504 MB`; L2 heap `463.633 ms`, GC `62.421 ms` | L1 `checked-scoped-epoch-topk-retained-no-traverse` `18.26 s`, RSS `92 MB`; L2 checked `402.916 ms`, GC `0 ms` | L1 `4.1%` faster; L2 `13.1%` faster | L2 removes heap timed GC | about `-82%` in L1 | Larger real-input retained top-k scale-up: modest L1 throughput win, strong RSS win, and clear L2 GC removal. |
| LogHub reusable EpochTopKByKey 1M | generated LogHub-shaped stressor | retained-object drop-anchor / reusable operator gate | `heap-retained-drop-anchor` `397.788 ms`, GC `126.601 ms`, RSS `408 MB` | `checked-scoped-epoch-topk-retained-no-traverse` `274.914 ms`, GC `0 ms`, RSS `305 MB` | `30.9%` faster | `-126.601 ms` | about `-25%` | Reusable checked top-k API passes generated retained gate; same-run overhead versus benchmark-local checked is about `5.7%`. |

## Current Claims

- **Memory-management claim:** retained heap versus retained checked epoch rows
  show that checked regions can reclaim ordinary retained Scala objects faster
  and with less GC work when lifetimes are epoch-structured.
- **User-facing checked topology claim:** `RiftRegion.epoch { ... }` is now the
  default checked topology for batch/epoch workloads; page-token is the default
  checked topology for page/window append streams.
- **Generated stressor claim:** Common Crawl WET-shaped q1/q2 demonstrates the
  high-GC stream-object regime where checked page-token wins decisively.
- **Generated methodology claim:** NEXMark Beam-default-style q3/q8/q9/q11 now
  have L1 checked framework wins, but remain generated local-harness evidence.
- **Real-input claim:** Yak LiveJournal is the strongest real-input epoch row;
  LogHub top templates is now a real-preloaded retained top-k row at both
  1M x20 and 5M x5, and `EpochTopKByKey` is the first reusable top-k API to
  pass the retained gate.
  Yak topword provides a second generated-methodology top-k confirmation, while
  GH Archive byte-slice q1/q2, LogHub HDFS q2, and DSPBench Log q2 remain
  modest page/window rows.
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
