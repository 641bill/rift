# Portable Backend Status

Last updated: 2026-05-17 12:10 CEST

Status: hot status file for JVM/Scala.js/Wasm/analysis-only Rift experiments.
This file may be updated frequently by the portable-backend fork.

## Ownership

Portable backend owns:

- `scala-native-rift/experimental/portable-rift/**`
- portable-specific evidence files;
- portable sections of `docs/SCALA_LEVEL_BACKEND_PLAN.md` when the plan changes.

Portable backend should avoid:

- `scala-native-rift/nativelib/**`
- `scala-native-rift/nscplugin/**`
- `scala-native-rift/unit-tests/native/**`
- `scala-native-rift/sandbox/**`

Shared contract:

- `docs/RIFT_PORTABLE_API_CONTRACT.md`
- `docs/HOTSPOT_REGION_BACKEND_PLAN.md` for the separate VM-fork roadmap.

## Current Prototype

Source:

`/Users/siyaoliu/rift/scala-native-rift/experimental/portable-rift/src/main/scala/rift/portable/**`

Models:

- `scala-native-real-regions`
- `jvm-pool-arena`
- `scala-js-pool`
- `wasm-linear-memory`
- `analysis-only`

Current implementation:

- reusable API in code: `Rift.epoch`, `RiftScope.alloc`, `RiftScope.borrow`,
  `HeapRoot`, `StaticMetadata`, `ObjectPool`, `ReusableRecord`, backend
  selection, and stats;
- JVM-first backends: `heap-gc`, `analysis-only`, and `jvm-pool-arena`;
- compiled stubs/examples: `scala-js-pool`, `wasm-linear-memory`, and
  `scala-native-real-regions` model;
- smoke runner and tiny JVM microbenchmark harness are available.

Current validation:

- `scala-cli compile --server=false experimental/portable-rift` passed;
- `scala-cli test --server=false experimental/portable-rift` passed, `10/10`
  MUnit tests;
- `PortableRiftSmoke` passed with stale-scope allocation rejected in every
  backend model;
- `PortableRiftMicrobench` produced matching checksum/output across `heap-gc`,
  `analysis-only`, and `jvm-pool-arena`.
- `experimental/portable-rift/scripts/run_jvm_gate.sh` produced a compact
  retained-object gate at
  `/private/tmp/portable-rift-jvm-gate-20260517-clean-smoke`, with separate JVM
  executions, `/usr/bin/time -l` RSS, and `-Xlog:gc*` logs.

Current interpretation:

- The portable pool backend is functionally working: 500k-record gates show
  `10000` fresh pooled allocations and `490000` pooled reuses.
- The current tiny JVM rows are not performance wins. Natural heap and
  analysis-only are faster, likely because HotSpot escape analysis and scalar
  replacement remove most short-lived allocation cost, while explicit pooling
  adds bookkeeping and retained pool RSS.
- The next JVM experiment should use a retained graph that cannot be scalarized
  away, or add an explicit `-XX:-DoEscapeAnalysis` stress control to separate
  API/runtime overhead from HotSpot optimization effects.

## Next Portable Step

Add a non-scalarizable JVM retained graph or escape-analysis-off stress row,
then rerun the same gate. Do not claim Scala.js/Wasm performance until
backend-specific benchmark rows exist.

## HotSpot Track Note

The user requested a custom JVM/HotSpot route for ordinary Scala objects in
regions. That is now separated from the portable library prototype:

- portable JVM library: current `experimental/portable-rift/**` prototype with
  object pools, FFM/off-heap handles later, and heap fallback;
- HotSpot VM fork: planned research backend where normal JVM object layouts
  are allocated in VM-known Rift region memory and bulk-closed under
  capture/separation proof.

The VM-fork roadmap is in `docs/HOTSPOT_REGION_BACKEND_PLAN.md`. Do not mix
that work into `experimental/portable-rift/**` unless it is only a shared API
or test harness change.
