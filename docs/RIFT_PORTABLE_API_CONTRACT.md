# Rift Portable API Contract

Date: 2026-05-17
Last updated: 2026-05-17 02:36 CEST

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
