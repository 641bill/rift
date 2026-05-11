# API Burden Summary

Date: 2026-05-11
Last updated: 2026-05-12 01:03 CEST

Status: representative reporting artifact. These counts are code-level burden
summaries for the presentation rows, not a language-level annotation calculus.
They exist so Stancu/SPECjbb-style comparisons can discuss how much lifetime
structure the user or benchmark author must expose to get checked region
benefits.

## Counting Rule

Count the reusable checked boundary the programmer writes, not every runtime
open/close event:

- `epoch`: one `RiftRegion.epoch { ... }` boundary in the hot loop shape;
- `page/window/token`: one page/window/token operator family boundary, such as
  page-token append or count-by-key;
- `HeapRoot`: explicit bridge/root handles used by the row's record type;
- `checked operator`: reusable non-primitive checked operator boundary, such
  as `EpochTopKByKey`, page-token map/filter, or retained epoch helper.

Do not count benchmark-local primitive arrays or manual summary-only loops as
Rift API burden. Those rows remain lower-bound controls under
`docs/FAIR_EVALUATION_PROTOCOL.md`.

## Representative Rows

| Benchmark row | Input type | API/topology | epoch | page/window/token | HeapRoot | checked operator | Interpretation |
|---|---|---|---:|---:|---:|---:|---|
| Yak LiveJournal `graphreal` | real-preloaded SNAP graph | `RiftRegion.epoch` direct epoch | 1 | 0 | 0 | 0 | Low API burden for an epochal graph replay; exposes Yak-style data epoch directly. |
| AskUbuntu `topwordreal` direct epoch | real-file-backed Stack Exchange text | `RiftRegion.epoch` direct epoch | 1 | 0 | 0 | 0 | Best current real text row; top-k state is benchmark-local durable control, so classify against same-shape controls. |
| AskUbuntu `topwordreal` top-k | real-file-backed Stack Exchange text | `EpochTopKByKey` in checked epoch | 1 | 0 | 0 | 1 | Reusable top-k API burden; wins RSS and modest elapsed versus heap but trails direct epoch. |
| LogHub HDFS top templates | real-preloaded logs | `EpochTopKByKey` retained epoch | 1 | 0 | 0 | 1 | Strong reusable retained top-k row with large RSS win. |
| Dataflow SELECT/AGGREGATE/JOIN | generated methodology | `RiftRegion.epoch` direct epoch | 1 | 0 | 0 | 0 | Broom-style rows expose operator lifetime through one epoch boundary. |
| StreamFlex throughput/latency | generated methodology | `RiftRegion.epoch` direct epoch | 1 | 0 | 0 | 0 | Lifetime boundary is stream batch/epoch; latency metrics carry the StreamFlex-style claim. |
| StreamFlex design stable/transient/capsule | generated methodology | `RiftRegion.epoch` per-period transient region plus bounded capsule export | 1 | 0 | 0 | 0 | Same low checked-boundary burden as direct epoch, but the benchmark explicitly models StreamFlex stable state and capsule transfer. |
| Stancu/SPECjbb-style transactions | generated methodology / clean-room port | `RiftRegion.epoch` transaction boundary | 1 | 0 | 0 | 0 | Transaction-local data uses one checked epoch boundary; report with region-freed proxy. |
| Common Crawl-shaped q1/q2 | generated stressor | checked page-token | 0 | 1 | 0 | 1 | Page/window stream burden: user exposes page/bucket lifetime to the operator. |
| GH Archive q1/q2 | real-file-backed NDJSON | checked scoped page-token | 0 | 1 | 0 | 1 | Modest real-input RSS/elapsed row; not a flagship GC-heavy result. |
| ReML-shaped `msort`/`ratio` | Scala Native port | checked scoped/stream region | 1 | 0 | 0 | 0 | Same-axes comparison rows; exact annotation burden differs from MLKit/ReML and must be reported separately. |

## Current Interpretation

The lowest-burden winning shape is direct checked epoch: one boundary exposes a
batch, transaction, or graph-step lifetime, and the compiler rejects escapes.
Page/window token has higher API burden because users must expose the
bucket/window key, but it is the right shape for page/event streams. `HeapRoot`
burden is currently low in representative rows because most wins keep durable
metadata primitive or static; future mixed-reference workloads must count it
explicitly before claiming root-free eligibility. The open-region probe update
confirms that `HeapRoot` is accepted through direct epoch and operator-owned
page/epoch-buffer allocation paths, but root-free-eligible rows must reject
`HeapRoot` explicitly before making a rootless safety claim.
