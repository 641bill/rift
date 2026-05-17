# Rift Portable API Contract

Date: 2026-05-17
Last updated: 2026-05-17 12:10 CEST

Status: contract draft. This document separates portable Scala-level Rift work
from Scala Native backend work so parallel forks do not edit the same files.

## Goal

Rift should expose a Scala-level lifetime topology model that can be checked
independently of the final allocation backend. Scala Native is the first
validated backend, but the front-end concepts should be reusable by JVM,
Scala.js, Wasm, and analysis-only experiments.

## Source-Level Concepts

The portable API contract should eventually cover these concepts:

| Concept | Meaning | Backend responsibility |
|---|---|---|
| `epoch { ... }` | Batch/step lifetime; all region-local values die at epoch close. | Native uses real region reset; JVM/JS may pool records; Wasm may reset an arena; analysis-only allocates normally. |
| `window { ... }` | Time/count window lifetime. | Backend must preserve active/closed discipline and bounded live state. |
| `page { ... }` | Page/record-group lifetime. | Backend may use page-token fast paths or local pools. |
| `transaction { ... }` | Transaction-local scratch lifetime. | Backend may pool request/line/receipt objects or use real regions. |
| `HeapRoot[A]` | Explicit bridge from region values to durable heap metadata. | Backend must keep mixed references explicit. |
| active/closed handle | Only active handles allocate; closed handles reject allocation/use. | Backend must enforce dynamically or prove statically. |
| capture/separation checks | Region values cannot escape their lifetime or be hidden in closures/generic containers. | Front end/checker owns this; backend can remove checks only after proof. |

## JVM-First V1 API Shape

The current portable prototype implements the first source-level shape in
ordinary Scala under `experimental/portable-rift/**`:

| API / type | V1 meaning |
|---|---|
| `Rift.epoch { scope => ... }` | Deterministic lifetime boundary with `try/finally` close. |
| `RiftScope.alloc(new Obj(...))` | Heap fallback allocation with active/closed runtime checks. |
| `RiftScope.borrow(pool)(init)` | Backend-owned reusable record path for JVM/Scala.js-style pooling. |
| `ObjectPool[A <: ReusableRecord]` | Explicit bounded reuse source for supported record-like values. |
| `HeapRoot[A]` | Explicit bridge for durable heap values. |
| `StaticMetadata[A]` | Stable metadata reference accepted by root-free-eligible experiments. |
| `RiftStats` | Portable opens/closes/allocation/reuse/arena counters. |

The JVM v1 backend is intentionally conservative. It does not claim that the
JVM places arbitrary Scala objects in regions. It proves the source-level API
shape, active/closed runtime discipline, and explicit record-pool lowering for
values that opt into `ReusableRecord`.

## HotSpot Ordinary-Object Backend Track

Supporting ordinary Scala/JVM objects off heap or outside the normal Java heap
is not a portable-library feature. It requires a HotSpot VM fork because normal
JVM objects are VM-managed `oop`s with object headers, class metadata, GC
barriers, stack-map/deoptimization behavior, monitors, identity, and reference
semantics.

The shared source contract stays the same:

- `epoch`, `window`, `page`, and `transaction` express lifetime topology;
- active handles allocate, closed handles reject use;
- `HeapRoot` is the explicit bridge for durable heap references;
- capture/separation checks reject heap-retains-region, closure escape,
  generic hiding, stale handles, and parent/child lifetime violations.

The HotSpot-specific lowering is different: checked allocations would go
through VM entrypoints into a VM-known region space that preserves normal
object layout and can be bulk-closed when the source-level invariants hold.
The detailed roadmap is tracked in `docs/HOTSPOT_REGION_BACKEND_PLAN.md`.

## Backend Ownership

| Area | Owner |
|---|---|
| `scala-native-rift/nativelib/**` | Native backend fork |
| `scala-native-rift/nscplugin/**` | Native backend fork |
| `scala-native-rift/unit-tests/native/**` | Native backend fork |
| `scala-native-rift/sandbox/**` | Native benchmark/evidence fork unless explicitly coordinated |
| `scala-native-rift/experimental/portable-rift/**` | Portable backend fork |
| `docs/RIFT_PORTABLE_API_CONTRACT.md` | Shared contract; edit carefully |
| `docs/SCALA_LEVEL_BACKEND_PLAN.md` | Shared design plan |

## Merge Rule

Portable work should not directly refactor `RiftRegion.scala` or compiler
lowering files. Instead:

1. extend the portable contract;
2. prototype in `experimental/portable-rift/**`;
3. add portable-specific tests/evidence;
4. only then coordinate an adapter in the Native fork.

Native work should not depend on the prototype internals. Native should keep
using the existing checked APIs until a stable portable API is agreed.

## Claim Discipline

- Scala Native performance rows remain the only validated Rift backend
  performance evidence.
- JVM/Scala.js/Wasm/analysis-only are experimental backend tracks.
- A non-Native backend may claim API/checking portability only after the
  portable harness compiles and tests on that backend.
- A non-Native backend may claim performance only after benchmark rows are run
  under the same L1/L2 measurement discipline as Native rows.
