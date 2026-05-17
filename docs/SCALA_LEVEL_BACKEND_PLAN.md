# Scala-Level Rift Backend Plan

Date: 2026-05-16
Last updated: 2026-05-17 02:36 CEST

Status: planning document. This is not implemented backend evidence. It records
the intended long-term split between Rift's Scala-level safety/topology model
and backend-specific allocation strategies.

## Motivation

Current Rift evidence is on Scala Native, where the compiler and runtime can
allocate ordinary Scala objects into region slabs and bulk-close/reset them.
This is the right first backend, but it is not the full design space.

The front-end ideas are mostly Scala-level:

- `epoch`, `page`, `window`, and `transaction` lifetime topologies;
- capture/separation checking for region escapes;
- explicit heap/region bridge handles such as `HeapRoot`;
- active/closed region handle discipline;
- static rejection of closure escape, generic hiding, heap-retains-region, and
  parent/child lifetime violations.

Those checks should be reusable across Scala backends. What changes by backend
is the lowering: real region allocation on Scala Native, pooling/arenas or
off-heap handles on the JVM, object reuse on Scala.js, linear-memory arenas on
Wasm, or analysis-only checking with ordinary heap allocation.

This matters for evaluation. Scala Native's Immix baseline is already a strong
heap collector, so public real-input workloads may not always expose large GC
time. If no stronger real-input GC-heavy row is found, the thesis still has a
valid core: checked Scala lifetime topologies can be compiled to real region
allocation on Scala Native, and the same source-level checks can guide other
backend lowerings.

## Backend Tracks

| Track | Purpose | First lowering target | Evidence status |
|---|---|---|---|
| Scala Native | Main validated implementation backend. | Real region allocator, backend-known checked allocation, proof-gated no-zero, bulk close/reset. | Active implementation and benchmark evidence. |
| JVM | Experimental portability backend. | Same Scala API and checks; object pools, scoped arenas for selected record-like classes, reusable arrays/buffers, optional off-heap/foreign-memory arenas, normal heap fallback. | Planned. |
| Scala.js | Portability and allocation-reduction experiment. | Object pooling and lifetime-bounded reuse for generated JS objects where semantics allow. | Planned. |
| Wasm | Natural arena backend. | Linear-memory bump allocation and reset for region-shaped values and buffers. | Planned. |
| Analysis-only | Front-end safety proof independent of allocation placement. | Run capture/separation checks but allocate normally on the target heap. | Planned. |

## Prototype Location

The first pure-Scala backend-facade prototype is intentionally isolated from
the Scala Native sandbox:

`scala-native-rift/experimental/portable-rift/src/main/scala/rift/portable/PortableRiftBackendPrototype.scala`

It models a shared `epoch` scope, active/closed scope checks, heap fallback
allocation, explicit reusable object pools for JVM/Scala.js-like lowerings, a
simple Wasm linear-memory arena, and analysis-only checking. It is not a full
backend implementation and does not claim that non-Native platforms can place
arbitrary Scala objects in real regions.

The fork ownership boundary and portable API contract are tracked in
`docs/RIFT_PORTABLE_API_CONTRACT.md`. Prototype smoke evidence is recorded in
`evidence/PORTABLE_BACKEND_PROTOTYPE.md`.

## JVM Experiment Rules

The JVM track should not claim that HotSpot can place arbitrary Scala objects
into Rift regions. V1 should be explicit and conservative:

- preserve the same source-level checked APIs;
- keep capture/separation errors identical where possible;
- lower only supported record-like classes or buffers to pools/arenas;
- use normal heap allocation for unsupported shapes;
- compare against HotSpot GCs only as cross-runtime context, not as a direct
  replacement for Scala Native Immix rows.

Promising JVM experiment rows:

- Broom/Naiad-style retained dataflow;
- StreamFlex-style retained event-correlation/latency rows;
- StackExchange top-word/text epochs;
- SPECjbb/Stancu-style transaction batches.

## Claim Discipline

Until another backend exists, public claims remain:

- **validated:** Scala Native checked regions versus Scala Native heap/Immix;
- **planned:** Scala-level API/safety model should be portable;
- **experimental future work:** JVM/Scala.js/Wasm/analysis-only lowerings.

Do not state that Rift already works on JVM, Scala.js, or Wasm. State that the
front-end safety model is designed to be inherited, while allocation and memory
reclamation are backend-specific.
