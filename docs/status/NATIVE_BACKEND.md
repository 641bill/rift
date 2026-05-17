# Native Backend Status

Last updated: 2026-05-17 02:54 CEST

Status: hot status file for Scala Native Rift runtime/compiler/benchmark work.
This file may be updated frequently by the Native backend fork.

## Ownership

Native backend owns:

- `scala-native-rift/nativelib/**`
- `scala-native-rift/nscplugin/**`
- `scala-native-rift/unit-tests/native/**`
- `scala-native-rift/sandbox/**`

Native backend should avoid:

- `scala-native-rift/experimental/portable-rift/**`

## Current Position

Scala Native is the only validated performance backend. The current evidence
compares checked Rift against Scala Native Immix, checked scoped backends,
legacy checked controls, and selected safe/unsafe lower bounds.

The portable backend prototype has been removed from `sandbox/`, so Native
benchmark matrices are no longer mixed with JVM/JS/Wasm/analysis-only
experiments.

## Latest Validation

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed
  after the portable prototype move.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed
  after adding Broom q17.
- Checked compiler/runtime suites passed before the move:
  `RiftRegionCheckedCompilerTest` `141/141`,
  `RiftRegionCheckedTest` `65/65`.

## Next Native Step

Continue the retained-object benchmark direction rather than parser-heavy real
log rows:

1. Optional shopper-style JOIN-SELECT-JOIN as a separate Broom/Naiad retained
   dataflow slice; or
2. StreamFlex-style retained event-correlation / transaction-tracking latency.
