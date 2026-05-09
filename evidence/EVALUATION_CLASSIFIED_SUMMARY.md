# Evaluation Classified Summary

Date: 2026-05-09
Last updated: 2026-05-09 23:55 CEST

Status: thesis-facing classified summary built from committed evidence.
Baseline commits for clean rows: parent `1cc3b2c`, child `13a3df1c7`.
Reusable top-k API rows come from child commit `9abac4833`.

## How To Read This Table

Every row has an explicit comparison class. Do not read all rows as a single
"heap vs Rift" claim.

Measurement level is separate from comparison class. Unless explicitly marked
otherwise, the rows in this file are L2 standard-stats rows: they report GC,
RSS, and region counters and are valid for interpretation, but they are not the
future L1 final-clean headline table. Initial L1 binary support exists for the
first representative matrices; report-grade L1 rows belong in
`evidence/FINAL_CLEAN_HEADLINE_RESULTS.md` once collected.

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
| GH Archive-shaped retained q2 | generated/preloaded stressor | retained-object drop-anchor | retained heap `257.377 ms`, GC `77.208 ms`, RSS `147 MB` | checked scoped retained `186.868 ms`, GC `0 ms`, RSS `15 MB` | `27.4%` faster | `-77.208 ms` | about `-90%` | Strong retained memory-management and RSS win; generated/preloaded, not real-input proof. |
| LogHub-shaped retained q2 | generated/indexable log stream | retained-object drop-anchor | retained heap `469.079 ms`, GC `64.060 ms`, RSS `813 MB` | checked scoped retained `402.821 ms`, GC `0 ms`, RSS `694 MB` | `14.1%` faster | `-64.060 ms` | about `-15%` | Retained throughput/GC win with lower RSS. |
| LogHub-shaped retained q3 | generated/indexable template/session stream | retained-object drop-anchor | retained heap `2244.266 ms`, GC `143.539 ms`, RSS `2291 MB` | checked scoped retained `2106.541 ms`, GC `0 ms`, RSS `2312 MB` | `6.1%` faster | `-143.539 ms` | about `+1%` | Mixed retained win: elapsed/GC improves, RSS does not. |
| DSPBench Fraud retained q2 | generated/indexable DSPBench-shaped stream | retained-object drop-anchor | retained heap `392.743 ms`, GC `35.631 ms`, RSS `576 MB` | checked scoped retained `370.746 ms`, GC `0 ms`, RSS `583 MB` | `5.6%` faster | `-35.631 ms` | about `+1%` | Modest retained throughput/GC win; not an RSS win. |
| DSPBench Fraud direct q2 | generated/indexable DSPBench-shaped stream | summary-only topology | natural heap `400.900 ms`; heap direct summary `272.251 ms` | checked scoped direct epoch `267.739 ms` | direct topology gives most of the win | heap direct has `0 ms` GC | n/a | Topology/operator lower bound; checked regions are close to same-shape heap. |
| GH Archive-shaped direct q2 | generated/preloaded stressor | summary-only topology | natural heap `287.380 ms`; heap direct summary `54.642 ms` | checked scoped direct epoch `56.013 ms` | checked is near same-shape heap | heap direct has `0 ms` GC | n/a | Almost entirely topology/operator evidence, not memory-placement evidence. |
| LogHub-shaped direct q2 | generated/indexable log stream | summary-only topology | natural heap `526.803 ms`; heap direct summary `191.601 ms` | checked scoped direct epoch `193.938 ms` | checked is near same-shape heap | heap direct has `0 ms` GC | n/a | Direct-aggregate topology evidence. |
| LogHub-shaped direct q3 | generated/indexable template/session stream | summary-only topology | natural heap `2225.364 ms`; heap direct summary `1779.064 ms` | checked scoped direct epoch `1792.397 ms` | checked is near same-shape heap | heap direct has `0 ms` GC | n/a | Topology evidence; richer query still CPU-heavy. |
| Yak LiveJournal graphreal 50M | real SNAP LiveJournal edge list replay | best checked topology | heap `2958.659 ms`, GC `400.484 ms`, RSS `3.91 GB` | `checked-epoch-scoped` `2008.320 ms`, GC `0 ms`, RSS `2.11 GB` | `32.1%` faster | `-400.484 ms` | about `-46%` | Strongest real-input prior-work-shaped checked epoch win; local graph replay, not exact Yak/GraphChi artifact. |
| Dataflow SELECT/AGGREGATE/JOIN | Broom-style generated methodology | best checked topology | heap `27.775/50.837/30.387 ms`, GC `6.828/11.564/9.331 ms`, RSS `76 MB` | checked epoch scoped `19.691/34.676/19.762 ms`, GC `0 ms`, RSS `47 MB` | `29-35%` faster | removes timed heap GC | about `-38%` | Reusable direct epoch win across the full Dataflow operator family. |
| StreamFlex throughput 1M | StreamFlex-style generated methodology | best checked topology | heap `216.853 ms`, GC `46.036 ms`, RSS `8.0 MB` | checked scoped direct epoch `157.334 ms`, GC `0 ms`, RSS `8.2 MB` | `27.4%` faster | `-46.036 ms` | about `+2%` | Direct epoch supersedes TransactionRegion for shared-batch pipeline throughput. |
| StreamFlex latency 200k | StreamFlex-style generated methodology | best checked topology | heap `200.924 ms`, GC `20.653 ms`, max `1065125 ns`, deadline misses `21` | checked scoped direct epoch `192.557 ms`, GC `1.570 ms`, max `887875 ns`, deadline misses `1` | `4.2%` faster | `-19.083 ms` | near tie | Latency/tail improvement; trusted Streaming remains the lower-bound max-tail control. |
| Stancu-style transactions 1M | transaction methodology probe | best checked topology | heap `220.951 ms`, GC `22.819 ms`, RSS `7.9 MB` | checked scoped direct epoch `155.863 ms`, GC `0.381 ms`, RSS `8.0 MB` | `29.5%` faster | `-22.438 ms` | near tie | Checked transaction-boundary win; local methodology probe, not official SPEC. |
| SPECjbb2005 workload port, 8 warehouses | clean-room transaction workload port | best checked topology | heap `129.674 ms`, GC `15.125 ms`, RSS `8.0 MB` | checked epoch scoped `108.649 ms`, GC `0 ms`, RSS `8.1 MB` | `16.2%` faster | `-15.125 ms` | near tie | Stancu/SPECjbb-shaped local port win; not official SPECjbb2005. |
| Common Crawl WET-shaped q1 | generated stream stressor | best checked topology | heap `5577.965 ms`, GC `1741.640 ms`, RSS `409 MB` | checked scoped page-token `3707.214 ms`, GC `30.693 ms`, RSS `464 MB` | `33.5%` faster | `-1711 ms` | about `+14%` | Strong generated stream-object pressure win; not real-input proof and not RSS win. |
| Common Crawl WET-shaped q2 | generated stream/window stressor | best checked topology | heap `5183.074 ms`, GC `1565.074 ms`, RSS `409 MB` | checked scoped page-token `3902.795 ms`, GC `27.027 ms`, RSS `464 MB` | `24.7%` faster | `-1538 ms` | about `+14%` | Strong generated window/object pressure win; not real-input proof and not RSS win. |
| LogHub HDFS v1 q2 | real file-backed Hadoop log | best checked topology | heap `8227.369 ms`, GC `92.659 ms`, RSS `409 MB` | checked scoped page-token `7871.856 ms`, GC `0 ms`, RSS `395 MB` | `4.3%` faster | `-92.659 ms` | about `-3%` | Modest real-input throughput/RSS/GC win; heap GC is only about 1-2% elapsed. |
| DSPBench Log q2 | real DSPBench bundled common-log input | best checked topology | heap `1750.291 ms`, GC `44.992 ms`, max GC `88.210 ms`, RSS `308 MB` | checked scoped page-token `1733.654 ms`, GC `18.402 ms`, max GC `18.584 ms`, RSS `322 MB` | `1.0%` faster | median `-26.590 ms`; max `-69.626 ms` | about `+5%` | Modest real-input throughput/GC-tail win; not RSS or flagship GC-heavy evidence. |
| LogHub top templates 1M | real-preloaded HDFS log | retained-object drop-anchor | `heap-retained-drop-anchor` `116.138 ms`, GC `31.161 ms`, RSS `146 MB` | checked scoped retained top templates `81.174 ms`, GC `0 ms`, RSS `150 MB` | `30.1%` faster | `-31.161 ms` | about `+3%` | Real-preloaded retained top-k throughput/GC win; not an RSS win and not parser/file-backed timing. |
| LogHub top templates 1M | generated LogHub-shaped stressor | retained-object drop-anchor | `heap-retained-drop-anchor` `424.443 ms`, GC `126.371 ms`, RSS `408 MB` | checked scoped retained top templates `290.610 ms`, GC `0 ms`, RSS `304 MB` | `31.5%` faster | `-126.371 ms` | about `-25%` | Generated retained top-k memory-management and RSS win; supports a reusable top-k API candidate. |
| LogHub reusable EpochTopKByKey 1M | real-preloaded HDFS log | retained-object drop-anchor / reusable operator gate | `heap-retained-drop-anchor` `123.024 ms`, GC `33.966 ms`, RSS `146 MB` | `checked-scoped-epoch-topk-retained-no-traverse` `95.267 ms`, GC `0 ms`, RSS `150 MB` | `22.6%` faster | `-33.966 ms` | about `+3%` | Reusable checked top-k API passes real-preloaded throughput/GC gate; benchmark-local checked path is still faster (`83.697 ms`). |
| LogHub reusable EpochTopKByKey 1M | generated LogHub-shaped stressor | retained-object drop-anchor / reusable operator gate | `heap-retained-drop-anchor` `463.578 ms`, GC `138.050 ms`, RSS `408 MB` | `checked-scoped-epoch-topk-retained-no-traverse` `341.905 ms`, GC `0 ms`, RSS `305 MB` | `26.3%` faster | `-138.050 ms` | about `-25%` | Reusable checked top-k API passes generated retained gate, with measurable abstraction overhead versus the benchmark-local path (`300.984 ms`). |

## Current Claims

- **Memory-management claim:** retained heap versus retained checked epoch rows
  show that checked regions can reclaim ordinary retained Scala objects faster
  and with less GC work when lifetimes are epoch-structured.
- **User-facing checked topology claim:** `RiftRegion.epoch { ... }` is now the
  default checked topology for batch/epoch workloads; page-token is the default
  checked topology for page/window append streams.
- **Generated stressor claim:** Common Crawl WET-shaped q1/q2 demonstrates the
  high-GC stream-object regime where checked page-token wins decisively.
- **Real-input claim:** Yak LiveJournal is the strongest real-input epoch row;
  LogHub top templates is now a strong real-preloaded retained top-k row, and
  `EpochTopKByKey` is the first reusable top-k API to pass the retained gate;
  LogHub HDFS q2 and DSPBench Log q2 remain modest page/window rows.
- **Non-claim:** summary-only/direct-aggregate rows are topology/operator lower
  bounds. They must not be described as pure memory-management wins.

## Next Evidence Rules

- A future memory-management claim must include a retained-object drop-anchor
  control if ordinary records survive until close.
- A future rank/top-k/median/join claim must first add natural heap,
  same-shape heap, and retained controls before application integration.
  Current candidate status is tracked in `evidence/OPERATOR_GATE_STATUS.md`.
- Unsafe/rootless/trusted rows may be reported only as lower bounds or backend
  potential, never as final safe-system evidence.
