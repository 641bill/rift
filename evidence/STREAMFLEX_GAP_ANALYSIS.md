# StreamFlex Gap Analysis

Last updated: 2026-05-12 01:30 CEST

Status: investigation note. This file explains why the current Rift
`StreamFlexDesignMatrix` shows a useful checked-region win but does not show
the same magnitude of speedup as the original StreamFlex paper. It is not a new
benchmark result.

## Short Answer

The current Rift row is already close to the speedup bound implied by its heap
GC share. On the 1M throughput row, heap spends `69-100 ms` of a
`477-509 ms` L2 run in GC. `checked-epoch-scoped` runs in `422.638 ms`.
Compared with the natural heap row, removing GC completely would put the
non-GC work around `409 ms`; Rift lands about `14 ms` above that. So the
remaining gap is mostly not reclaim/tracing time. It is allocation lowering,
object construction, linked-object traversal, and the fact that our benchmark
does not reproduce the full StreamFlex VM/runtime/scheduler design.

This means the current result should be reported as:

- a local StreamFlex-design reproduction;
- a checked-region throughput and tail-latency win;
- not an exact StreamFlex/Ovm artifact result;
- not evidence that Rift has matched StreamFlex's full system speedups.

## What StreamFlex Had That We Do Not Yet Have

The original StreamFlex system was not just a region allocator. It combined:

- a stream/filter language with a stricter typing discipline;
- fixed stable and transient memory regions per filter;
- VM-level allocation-area switching;
- VM rewriting for stable-class allocations and arrays;
- internally managed capsule pools in dedicated regions;
- Ovm real-time scheduling, priorities, and atomic sections;
- throughput and latency/deadline experiments where GC interference was a
  central cost.

The paper implementation describes each filter as having fixed-size stable and
transient regions, with region reclaim effectively resetting the allocation
pointer. It also reports VM support for stable-class allocation rewriting and
capsules managed internally with object pools in dedicated regions. This is
deeper than the current Rift benchmark-facing reproduction.

## What Rift Reproduces Today

`StreamFlexDesignMatrix` maps the main design concepts into Rift:

| StreamFlex idea | Current Rift row |
|---|---|
| Stable filter state | Heap arrays for thresholds, counters, and score totals. |
| Transient state | Per-period packet, feature, decision, and alert objects. |
| Capsule / transfer | Bounded primitive `AlertCapsule` export buffer. |
| Period | `RiftRegion.epoch` or SafeZone scope per period. |
| Throughput | Saturated generated event replay. |
| Latency | Per-event paced measurement with p50/p95/p99/p999/max and deadline misses. |

This is the right conceptual mapping, but it is still a simplified local
single-process benchmark. It does not implement StreamFlex's full filter graph
runtime, VM-managed capsule object pools, priority scheduler, or exact
BeamFormer/FilterBank artifacts.

## Quantitative Bound From Current Evidence

Current L2 throughput row, 1M events:

| Row | Median ms | Median GC ms | Approx non-GC ms |
|---|---:|---:|---:|
| `gc-heap` | `509.277` | `100.234` | `409.043` |
| `heap-same-shape` | `477.047` | `69.221` | `407.826` |
| `checked-epoch-scoped` | `422.638` | `0.000` | `422.638` |
| `checked-epoch-stream` | `443.363` | `0.000` | `443.363` |

Against `gc-heap`, the best possible speedup from removing only median GC is
about `509.277 / 409.043 = 1.25x`. The current checked scoped speedup is
`509.277 / 422.638 = 1.20x`. That captures most of the available GC-removal
headroom. The leftover gap is approximately `13-15 ms` of non-GC overhead.

Against `heap-same-shape`, the GC-removal bound is smaller:
`477.047 / 407.826 = 1.17x`, while checked scoped is
`477.047 / 422.638 = 1.13x`.

So if we want StreamFlex-scale headline speedups, we need one or more of:

- a heap baseline with larger GC/tail interference;
- a fixed-memory/heap-cap setting where heap cannot grow cheaply;
- lower checked allocation/object construction overhead;
- lower linked-object traversal cost;
- closer reproduction of StreamFlex's scheduler/capsule/runtime design.

## Current Implementation Costs

The current benchmark intentionally materializes ordinary objects, but it does
so with four linked-object stages:

1. `Packet`;
2. `Feature`;
3. `Decision`;
4. `Alert`.

Each stage builds a linked list and the next stage traverses it. Region close
does not traverse records, but the query itself still performs pointer chasing
through those lists. That traversal is computation, not GC, and regions do not
make it free. StreamFlex's original implementation is closer to a VM/runtime
for filter scheduling and memory areas; our row is a Scala Native object
pipeline.

Other current costs:

- checked allocation still lowers through `RiftRegion.allocOpen`, not a heap
  intrinsic;
- every transient object still pays object construction, header/RTTI setup, and
  field stores;
- `checked-epoch-stream` records region open/close/reset work and currently
  trails the SafeZone-backed scoped checked row on throughput;
- the capsule is a primitive export buffer, not a full ownership-transfer
  object-pool/channel runtime;
- latency mode uses per-event timing and per-event epochs, which is useful for
  tail evidence but not the same as StreamFlex's complete scheduler model.

## Why BeamFormer / FilterBank Do Not Close The Gap Yet

The local BeamFormer/FilterBank ports are useful StreamIt/StreamFlex-axis
controls, but the faithful shape is primitive-array DSP. The L2 rows show
little or no heap GC pressure. Therefore Rift cannot show a memory-management
win on those rows without adding a clearly labeled object-retained variant and
a same-shape heap control.

This is why `StreamFlexDesignMatrix` is the better current StreamFlex-design
row: it intentionally materializes transient stream objects and retains them
until the period boundary.

## Next Work To Close The Gap

1. **Profile current rows.** Use `samply` when available, or macOS `sample` as
   the fallback, on `StreamFlexDesignMatrix` throughput and pressure-latency
   rows. Confirm how much time is object construction, `allocOpen`, linked
   traversal, stable-state hashing/classification, and GC.
2. **Implement a closer capsule runtime.** Add an object-capsule variant with
   bounded capsule pools and explicit ownership/export boundaries, plus a
   same-shape heap control.
3. **Avoid linked-list cache misses where the API allows it.** A chunked or
   region-array transient buffer can be tested, but only with a same-shape heap
   control so the result is not a benchmark-local algorithm trick.
4. **Add heap-cap and deadline-stress rows.** StreamFlex is fundamentally about
   low latency and bounded memory. Heap caps and tighter paced deadlines may
   expose the larger GC-tail gap better than uncapped throughput.
5. **Lower allocation more intrinsically.** The checked allocation path should
   become closer to a direct bump-pointer fast path when the backend and open
   handle are statically known.
6. **Keep exact artifact claims separate.** Unless the original Ovm/StreamFlex
   artifact is run, the report should say "Rift-native StreamFlex design
   reproduction", not "Rift reproduces StreamFlex's exact numbers."

## Sources

- Local evidence: `evidence/STREAMFLEX_DESIGN_MATRIX.md`.
- StreamFlex paper PDF:
  <https://infoscience.epfl.ch/bitstreams/c5fd2b30-5712-4f80-9a98-6120b99b9987/download>.
- IBM Research publication page:
  <https://research.ibm.com/publications/streamflex-high-throughput-stream-programming-in-java--1>.
