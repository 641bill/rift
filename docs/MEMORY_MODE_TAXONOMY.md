# Rift Memory Mode Taxonomy

Date: 2026-05-03
Last updated: 2026-05-08 17:52 CEST

Status: canonical reporting-name contract for future reports and benchmark
tables. Older benchmark labels and code symbols remain accepted as aliases
during migration.

## Naming Rule

Mode names should expose two separate axes:

1. safety surface: GC heap, SafeZone, trusted Rift, or checked Rift;
2. runtime backend: Immix, SafeZone root strategy, Rift HP, or Rift Streaming.

Result tables should expose a third axis separately when it affects the row:
logical lifetime topology or operator shape. Examples are whole-run region,
epoch region, window/page-token append, transaction region, region list, or
rank/table structure. Do not hide topology inside backend names.

Avoid names such as `UnsafeZone-HP` in new prose. They hide the mechanism and
make unsafe lower-bound rows sound like a user-facing system.

## Preferred Reporting Names

Use these names in new prose, summary tables, and slides. They describe the
programming model and backend without exposing old implementation labels.

| Reporting name | Main implementation aliases | Meaning |
|---|---|---|
| `gc-heap` | `heap`, `heap-immix` | Normal Scala Native Immix GC heap. |
| `region-scoped-rooted` | `safezone-improved-32k`, `safezone-improved` | SafeZone-family scoped region backend with coalesced GC-root bookkeeping; main rooted scoped baseline. |
| `region-scoped-rootless` | `safezone-rootless-32k`, `unsafezone-hp` | SafeZone-family scoped backend with root tracking disabled; unsafe lower-bound only. |
| `region-stream-rootless` | `rift-trusted-streaming`, `rift-streaming` | Trusted Rift streaming/reset backend without checked user-level proof. |
| `region-hp-rootless` | `rift-trusted-hp`, `rift-hp`, `HPZone` | Trusted Rift HP backend without checked user-level proof. |
| `checked-region-stream` | `rift-checked-rift`, `rift-checked` | Checked Rift API over the Rift streaming/HP implementation path. |
| `checked-region-scoped` | `rift-checked-safezone-improved-32k`, `rift-checked-safezone-32k` | Checked Rift API over rooted SafeZone-family scoped allocation. |
| `checked-page-token` | `rift-checked-page-token`, `rift-checked-safezone-page-token` | Operator-owned checked append/window fast path for page/event/bucket-owned records. |

The project name remains Rift, but the descriptive system concept for
presentation is **checked stream regions**: safe APIs and reusable operators on
top of a choice of region backends.

## Topology Names

Use these in a separate `Topology/operator` column when a benchmark has several
checked shapes over the same backend:

| Topology/operator name | Meaning |
|---|---|
| `whole-run` | One region for the full timed computation. Safe when captures do not escape, but it gives up intermediate reclaim and can have heap-like RSS. |
| `epoch` | One region per batch/epoch, closed or reset at the epoch boundary. This is the right shape for Yak-style control/data splits. |
| `window` | Region lifetime follows a sliding/tumbling window or child bucket. |
| `page-token` | Operator-owned page/event/bucket append path; fastest when data naturally belongs to page/window buckets, not a universal checked topology. |
| `transaction` | Batch of operations committed/exported at a transaction boundary. |
| `region-list` | Linked object topology where a whole list/list-of-lists region dies together. |

User-facing design target:

```scala
Rift.stream {
  epoch { /* epoch-local data */ }
  window(...) { /* window-local data */ }
  page { /* page or record-group-local data */ }
}
```

## Implementation Labels And Aliases

The table below preserves older labels that appear in raw logs and scripts.
Use the reporting names above in rollups unless quoting raw output.

| Canonical name | Deprecated aliases | Meaning | Safety status |
|---|---|---|---|
| `heap-immix` | `heap` | Normal Scala Native Immix GC heap. | Safe by GC. |
| `safezone-current` | current SafeZone | SafeZone roots mode 0, old per-page GC-root bookkeeping. | SafeZone-level safety; slow baseline. |
| `safezone-improved` | improved SafeZone | SafeZone roots mode 1, coalesced root bookkeeping. | Main SafeZone baseline. |
| `safezone-improved-32k` | improved-32k | SafeZone roots mode 1 with 32 KiB pages. | Main SafeZone backend candidate. |
| `safezone-chunk-roots` | safezone-chunk | SafeZone roots mode 2, chunk-root strategy. | SafeZone backend candidate. |
| `safezone-rootless-32k` | UnsafeZone-HP, unsafezone-hp | SafeZone allocator with GC root tracking disabled and 32 KiB pages. | Unsafe lower-bound only. |
| `rift-trusted-hp` | rift-hp, HPZone | Rift HP backend used directly/trusted. | No checked user-level guarantee. |
| `rift-trusted-streaming` | rift-streaming | Rift streaming/reset backend used directly/trusted. | No checked user-level guarantee. |
| `rift-checked-rift` | rift-checked/current checked | Checked Rift API over Rift backend. | Intended safe Rift surface. |
| `rift-checked-safezone-improved-32k` | rift-checked-safezone-32k | Checked Rift API over SafeZone improved roots + 32 KiB pages. | Safe checked backend prototype. |
| `rift-checked-safezone-rootless-32k` | rift-checked-rootfree-safezone-hp | Checked API over rootless SafeZone. | Benchmark-only lower bound until root-free mixed-reference policy is proven. |

## Reporting Rules

- Use canonical names in new result tables and summaries.
- If a raw script still emits an old label, explain it once in the source
  result pack and use the canonical name in rollups.
- `safezone-rootless-32k` and `rift-checked-safezone-rootless-32k` are never
  safety claims.
- `safezone-improved` and `safezone-improved-32k` are the fair SafeZone
  baselines, not `safezone-current`.
- `rift-trusted-*` rows measure backend potential; only `rift-checked-*` rows
  support the checked user-facing Rift claim.

## Current Fastest-Mode Map

| Condition | Current fastest or strongest row | Interpretation |
|---|---|---|
| Tiny/no-GC workloads | usually `gc-heap` | Region setup and metadata cannot pay off when GC is not material. |
| Old SafeZone root-heavy rows | `region-scoped-rooted` | Root coalescing removes the old SafeZone cliff. |
| Linked object topology | `region-scoped-rootless`, `region-scoped-rooted`, or staged checked builder | SafeZone-family allocator/pool mechanics are strong; rootless is unsafe; checked builder needs clean medians. |
| Flat region-friendly layout | `region-hp-rootless` | Rift slab/bump path wins on favorable topology. |
| Focused append-window checked backend | `checked-region-scoped` | Backend mechanics help when the operator is simple. |
| Focused page/event append | `checked-page-token` | Operator ownership removes per-record checks/lookups. |
| Yak-style real graph replay | `checked-region-scoped` or `checked-region-stream` with `epoch` topology | The 50M LiveJournal topology/API-backed runs show epoch checked rows beat heap strongly while preserving low RSS; page-token is slower because Yak is not page/window-shaped. `RiftRegion.epoch { ... }` is now the reusable checked API for this direct linked-epoch topology and also covers local Yak-shaped `wordcount`, `graphstep`, `topword`, and `graphchi`; `EpochBuffer` is correct but slower. |
| Generated Common Crawl WET-shaped q1/q2 | `region-hp-rootless`, `region-stream-rootless`, and `checked-page-token` | Strongest trusted and checked generated GC-heavy stream evidence. |
| Dataflow SELECT staged probe | `checked-page-token` over scoped backend | First cheap SELECT/filter/project family row; clean medians pending. |
| Checked Common Crawl-like q1/q2 | `checked-page-token` over scoped backend | First checked generated application-gate pass; real-input proof remains open. |
| Rank/table-heavy checked operators | often `gc-heap` or `region-scoped-rooted` | Current checked containers are too expensive. |
| Parser scratch / CPU-heavy rows | usually `gc-heap` | Region placement does not help when CPU/cache dominates. |
