# Fair Evaluation Protocol

Date: 2026-05-09
Last updated: 2026-05-11 14:48 CEST

Status: active evaluation contract for report, slides, and future benchmark
runs. This document is the reviewer-facing rulebook for deciding what a Rift
result can claim.

## Goal

Use reusable checked framework APIs as the headline unit of comparison. Manual
benchmark-local rewrites, primitive-only count arrays, and unsafe/rootless rows
are useful controls, but they are not final system evidence.

The core claim is:

> Rift provides checked stream-region APIs whose static capture/separation
> guarantees let the backend remove runtime GC/region bookkeeping, and those
> APIs win when workloads have structured epoch, page, or window lifetimes.

This is a memory-management claim first and an operator-library claim second.
Prior systems such as Broom, Yak, StreamFlex, Stancu et al., and ReML/MLKit
win by making lifetime boundaries visible to the allocator/collector. Rift
operators are headline-worthy only when they expose such a boundary through a
reusable checked API. The broader prior-work interpretation is tracked in
`docs/PRIOR_WORK_MEMORY_MANAGEMENT_INTERPRETATION.md`.

## Required Row Metadata

Every headline or summary row must state:

| Field | Required meaning |
|---|---|
| Input type | synthetic, generated methodology, generated stressor, real-preloaded, or real-file-backed |
| API/topology | for example natural heap, same-shape heap, `RiftRegion.epoch`, page/window token, retained epoch, `EpochTopKByKey` |
| Comparison class | one of the classes below |
| Measurement level | L1 final-clean, L2 standard stats, L3 diagnostic, or L4 external profile |
| Allowed claim | throughput, memory-management, RSS, tail-latency, topology/operator, lower-bound, or ceiling/control |

## Comparison Classes

| Class | Meaning | Allowed claim |
|---|---|---|
| natural heap baseline | ordinary GC heap program | practical end-to-end baseline only |
| same-shape heap control | heap uses the same epoch/page/window topology as the region row | separates topology from memory placement |
| summary-only topology | records update summaries on append and are not retained until close | operator/topology lower bound, not GC/reclaim evidence |
| retained-object memory-management | heap and region both retain ordinary records until close, then drop/close without user-level record traversal | fair heap GC reclaim versus region bulk-close/reset comparison |
| framework API win | result goes through a reusable checked API such as `RiftRegion.epoch`, page/window token, retained epoch, transaction/list API, or `EpochTopKByKey` | user-facing Rift evidence |
| unsafe/trusted lower bound | rootless or trusted modes without final checked user guarantee | backend potential only |
| ceiling/control | heap GC is not material or heap/baseline remains best | negative or boundary evidence |

Memory-management claims require retained heap/drop-anchor versus retained
checked-region rows. Summary-only rows must be described as topology/operator
evidence, even if they are much faster than natural heap.

When a table includes a `summary-only` or direct-aggregate lower bound, it must
include both sides of the same topology whenever implemented: the heap
same-shape row and the checked/region same-shape row. Do not list
`heap-direct-summary-only` by itself as the lower bound for a workload if
`checked-epoch-stream`, `checked-epoch-scoped`, or another checked framework
counterpart exists. Otherwise the table confuses "heap is fast under this
topology" with "this topology is fast for both heap and regions."

## Framework API Policy

Headline rows must use user-facing checked topologies:

- `RiftRegion.epoch { ... }` for batch, graph-step, transaction, Yak-style,
  StreamFlex-style, and Dataflow-style epoch workloads.
- Page/window token operators for page, bucket, and event-window records.
- Retained epoch controls when ordinary objects must survive until close and
  the claim is about reclaim.
- `EpochTopKByKey` as the first reusable checked top-k API candidate.

Benchmark-local manual arrays, primitive-only count loops, and direct
benchmark-specific linked structures are allowed only as lower bounds or
same-shape controls. They should guide API/backend work, not headline the final
system.

## Static Safety And Removed Runtime Work

For each checked API, the report must state the invariant and the runtime work
that the invariant removes.

| Static property | Runtime work that should not be needed in the checked fast path |
|---|---|
| region values cannot escape their region lifetime | no escape table and no Yak-style promotion barrier |
| heap cannot retain region values past close | no dynamic heap-to-region retention tracker |
| region-to-heap references require static/rooted proof | no blanket page roots where root-free eligibility is proven |
| outer regions cannot retain inner-region values | no close-time object graph scan |
| closures cannot hide escaping region captures | no runtime closure-capture tracker |
| active checked allocation handles cannot be closed/reset by user code | no hot-path open-state check inside the owning epoch/page/window allocation path |
| operator owns bucket/page tokens | no per-record stale-token or open-state check in the hot path |
| diagnostics are opt-in | no per-allocation tracing or attribution counters in headline rows |

Low-level public APIs stay defensive. Checks are removed only inside
operator-owned paths with compiler/runtime probes for stale-token,
heap-retains-region, region-to-heap, closure escape, and ReML-style polymorphic
heap retention.

## Measurement Levels

| Level | Purpose | Allowed instrumentation |
|---|---|---|
| L1 final-clean headline | final elapsed/RSS table | optimized non-profiled binary; no in-timed-section GC/region counter reads; external `/usr/bin/time -l` only |
| L2 standard stats | interpretation and current evidence tables | elapsed, GC median/max/runs-with-GC, RSS, region op time, opens/closes/resets, object/allocation counts |
| L3 diagnostic | bottleneck attribution | internal timers, allocation attribution, `*_DIAG`, `SAFEZONE_TRACE`, precise counters |
| L4 external profile | CPU composition and visible GC pauses | `samply`, macOS `sample`, or Linux `perf`; profiler elapsed is not headline timing |

If L1 and L2 elapsed disagree meaningfully, treat that as measurement overhead.
Use L1 for headline elapsed/RSS and L2-L4 only for interpretation.

## Prior-System Axes

Do not force all prior systems into one metric schema. Report each paper on its
own axes first, then add Rift's standardized local metrics.

| System line | Native axes to report |
|---|---|
| Broom/Dataflow | elapsed, GC share, operator lifetime boundary |
| Yak | app time, GC time, epoch topology, promotion/escape analogue, peak memory |
| StreamFlex | throughput, p95/max latency, deadline/tail events, GC pauses |
| Stancu/SPECjbb-style | transaction boundary, region-freed object proxy, GC count/time, annotation/API burden |
| ReML/MLKit | real time, RSS, GC count, region-vs-GC modes, safety/annotation burden |

Rift's standardized local metrics are elapsed, GC median/max, runs-with-GC,
RSS, region op time, opens/closes/resets, allocation/object count, and
checksum/output. For StreamFlex-style and other latency rows, also report
throughput, p50, p95, max latency, deadline misses, GC max, and runs-with-GC.
For Stancu/SPECjbb-style and representative checked API rows, also report API
burden: counts of `epoch`, page/window/token boundaries, `HeapRoot` handles,
and checked operator boundaries.

## Benchmark Acceptance

A row can become a representative public result only if:

- checksums/output counts match;
- it uses a checked framework API, or is clearly labeled as a control;
- it beats heap and the best safe baseline by about 10%, or materially lowers
  GC/RSS/tail latency with no more than 5% elapsed overhead;
- retained-object memory-management claims compare retained heap/drop-anchor
  against retained checked regions;
- no diagnostic/profiling/tracing/attribution elapsed is used as headline
  timing.

Rows that fail those gates remain useful as ceiling, lower-bound, or
operator-gate evidence.
