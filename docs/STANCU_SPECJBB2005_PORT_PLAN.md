# Stancu / SPECjbb2005 Workload Port Plan

Date: 2026-05-08
Last updated: 2026-05-08 21:20 CEST

Status: planning document. No SPECjbb2005 workload port has been implemented
yet.

## Decision

The final Stancu comparison target should be a **SPECjbb2005 workload port /
methodology reproduction**, not an official SPECjbb2005 run on Scala Native.

The official SPECjbb2005 artifact is a JVM benchmark. It ships bytecode and
source for JVM use; the user guide treats the benchmark as a Java program run
with `spec.jbb.JBBmain`, and compliant/public SPEC results use the provided
bytecodes rather than recompiling the benchmark. Scala Native cannot execute
that official Java bytecode artifact directly. A Scala Native result therefore
has to be reported as a port or methodology reproduction.

## Evidence Classes

| Evidence class | What it can claim | What it cannot claim |
|---|---|---|
| Official JVM control | Runs the official SPECjbb2005 kit on a JVM, if the licensed artifact is available locally. | Does not measure Rift/Scala Native. |
| Scala Native workload port | Runs a documented Scala/Scala Native implementation of the SPECjbb2005 transaction workload shape. | Not an official SPEC result and not comparable as raw `SPECjbb2005 bops`. |
| Stancu paper-axis reproduction | Matches the axes Stancu et al. report: warehouse range, fixed iteration count, transaction region boundaries, region-freed fraction, young-gen sensitivity, collections, annotation/API burden. | Not their exact compiler/runtime unless the Stancu implementation or equivalent analysis is reproduced. |
| Current local Stancu matrix | Transaction-shaped accounting probe with checked direct epoch rows. | Not SPECjbb2005 and not Stancu's static analysis. |

## Stancu Paper Contract To Match

The ISMM 2015 paper evaluates a hybrid Java memory-management system on
SPECjbb2005. The comparison contract for Rift is:

- workload: SPECjbb2005 server-side Java middle-tier transaction workload;
- configuration: warehouses 4 through 8;
- measurement: 100,000 iterations per warehouse in their modified run;
- annotation burden: 7 `@RegionScope` annotations in 12,581 LOC;
- region shape: parent transaction-dispatcher region plus child regions for
  transaction types;
- memory result: about 78% of total memory region-freed, peak region memory
  below 1 MB in their configuration;
- heap sensitivity: old generation fixed at 512 MB, young generation varied
  from 1 MB to 256 MB;
- reported axes: execution time, GC time, young collections, region-freed
  memory, max region stack size, and annotation count.

## Scala Native Port Target

The port should preserve the transaction workload semantics that matter for
memory management rather than trying to reproduce SPEC compliance machinery.

Required shape:

- one or more warehouses with durable heap state;
- one driver/worker stream of transaction requests per warehouse or a
  deterministic single-process equivalent for first measurements;
- transaction-specific ordinary Scala object graphs for request, order,
  line-item, payment/status/stock-level, and output/verification data where the
  official workload creates temporary middle-tier objects;
- durable warehouse tables, stock/customer/order indexes, random generator
  state, and aggregate counters kept on the heap or primitive arrays;
- temporary transaction objects allocated in `RiftRegion.epoch { ... }` or a
  transaction-type child region and bulk-reclaimed at the transaction or batch
  boundary;
- same logical program across `gc-heap`, `region-scoped-rooted`,
  `checked-region-stream`, and `checked-region-scoped`; only allocation
  placement/lifetime policy differs.

The first implementation should be single-process and deterministic. A
multi-warehouse/threaded variant can follow after correctness and memory
placement are validated.

## Implementation Stages

1. **Acquire or inspect sources without committing them.**
   Place any licensed SPECjbb2005 kit under
   `/Users/siyaoliu/rift/cache/benchmark-data/specjbb2005/`, which is ignored
   by git. Record provenance in `evidence/BENCHMARK_DATA_SOURCES.md`, but do
   not commit licensed source or bytecode.

2. **Run an optional JVM control.**
   If the official kit is available, run the JVM benchmark only as an external
   baseline and to validate workload parameters. Label it `official-jvm-control`
   or `paper-method-control`, not a Scala Native/Rift result.

3. **Build `SpecJbb2005PortMatrix`.**
   Add a Scala Native sandbox matrix that starts with one deterministic
   transaction core and then expands to the Stancu paper range: warehouses 4..8
   and 100k iterations per warehouse.

4. **Add allocation-placement modes.**
   Use the reporting taxonomy: `gc-heap`, `region-scoped-rooted`,
   `checked-region-stream`, `checked-region-scoped`, and optional explicit
   lower-bound controls only when needed.

5. **Add Stancu-style metrics.**
   Record elapsed, GC time/count, RSS, correctness checksum, allocated logical
   transaction objects, region-freed byte/object proxy, max live region
   payload, region enter/exit count, and annotation/API-boundary count.

6. **Run young-generation / heap-budget controls.**
   Scala Native does not expose the same young/old generation knobs as the
   Stancu JVM setup. Use the closest honest controls: `GC_MAXIMUM_HEAP_SIZE`
   caps, total RSS, GC time/count, and scale-up rows. Report that this is a
   Scala Native analogue, not a direct young-generation match.

7. **Compare to current `StancuRegionMatrix`.**
   Keep the existing local matrix as a small diagnostic row. Promote the
   SPECjbb2005 port only if it shows the same checked direct-epoch direction
   on a richer workload.

## Success Criteria

A successful port should show at least one of:

- checked/scoped regions beat `gc-heap` and `region-scoped-rooted` on elapsed
  time for the ported transaction workload;
- checked/scoped regions materially cut GC time/count or RSS with no more than
  5% elapsed overhead;
- heap caps or scale-up rows show region modes complete with lower RSS or
  fewer GC tails;
- the measured region-freed fraction is in the same qualitative range as
  Stancu's claim that most transaction-local memory is region-allocatable.

## Claim Boundaries

Allowed wording:

- "SPECjbb2005-workload Scala Native port."
- "Stancu/SPECjbb2005 methodology reproduction."
- "Rift reproduces the transaction-lifetime shape and reports the same axes."

Forbidden wording until proven:

- "official SPECjbb2005 result";
- "SPECjbb2005 bops";
- "exact Stancu reproduction";
- "Rift beats Stancu" based only on cross-language wall-clock.

## Links

- SPECjbb2005 overview and retired benchmark page:
  `https://www.spec.org/jbb2005/`
- SPECjbb2005 user guide:
  `https://www.spec.org/jbb2005/docs/UserGuide.html`
- Stancu et al., "Safe and Efficient Hybrid Memory Management for Java":
  `https://codrutstancu.com/papers/p81-stancu.pdf`
