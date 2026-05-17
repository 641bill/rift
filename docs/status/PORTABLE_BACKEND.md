# Portable Backend Status

Last updated: 2026-05-17 02:47 CEST

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

## Current Prototype

Source:

`/Users/siyaoliu/rift/scala-native-rift/experimental/portable-rift/src/main/scala/rift/portable/PortableRiftBackendPrototype.scala`

Models:

- `scala-native-real-regions`
- `jvm-pool-arena`
- `scala-js-pool`
- `wasm-linear-memory`
- `analysis-only`

Current validation:

- standalone `scalac` compile passed;
- `scala run --server=false` smoke passed;
- stale-scope allocation is rejected in every model.

## Next Portable Step

Add a tiny standalone build or cross-build harness under
`experimental/portable-rift/**`, then test the same API on JVM first. Do not
claim JVM/JS/Wasm performance until backend-specific benchmark rows exist.
