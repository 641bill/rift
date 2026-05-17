# Portable Rift Backend Prototype

Date: 2026-05-16
Last updated: 2026-05-17 02:39 CEST

Status: prototype smoke evidence. This is not JVM/Scala.js/Wasm performance
evidence. It records the first pure-Scala facade that separates Rift's
Scala-level lifetime model from backend-specific allocation strategies.

## Prototype

Source:

`/Users/siyaoliu/rift/scala-native-rift/experimental/portable-rift/src/main/scala/rift/portable/PortableRiftBackendPrototype.scala`

Ownership boundary:

`/Users/siyaoliu/rift/scala-native-rift/experimental/portable-rift/README.md`

Portable API contract:

`/Users/siyaoliu/rift/docs/RIFT_PORTABLE_API_CONTRACT.md`

Implemented model:

| Backend kind | Prototype behavior |
|---|---|
| `scala-native-real-regions` | Models real Scala Native region allocation by counting fresh region allocations under an active epoch. |
| `jvm-pool-arena` | Uses explicit reusable object pools released at epoch close. |
| `scala-js-pool` | Same pooling model, intended as a JavaScript allocation-reduction backend sketch. |
| `wasm-linear-memory` | Uses a resettable byte-array arena to model linear-memory bump/reset allocation. |
| `analysis-only` | Checks active/closed scope discipline but falls back to ordinary heap allocation. |

The prototype also includes a stale-scope probe: allocation after epoch close
must throw `IllegalStateException` for every backend model.

## Validation

Compile:

```text
scalac -d /tmp/portable-rift-classes \
  experimental/portable-rift/src/main/scala/rift/portable/PortableRiftBackendPrototype.scala
```

Result: passed on 2026-05-17 after moving the prototype out of `sandbox/`.

Earlier sandbox compile before extraction:

```text
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
```

Result: passed on 2026-05-16.

Native sandbox compile after extraction:

```text
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
```

Result: passed on 2026-05-17. The sandbox now compiles without the portable
prototype source, confirming the ownership split does not break the Native
benchmark project.

Checked compiler suite:

```text
ENABLE_EXPERIMENTAL_COMPILER=1 sbt \
  "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"
```

Result: passed on 2026-05-17, `141/141`.

Checked runtime suite:

```text
ENABLE_EXPERIMENTAL_COMPILER=1 sbt \
  "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"
```

Result: passed on 2026-05-17, `65/65`.

Smoke run:

```text
scala run --server=false \
  experimental/portable-rift/src/main/scala/rift/portable/PortableRiftBackendPrototype.scala \
  --main-class rift.portable.PortableRiftBackendPrototype
```

Result: passed on 2026-05-17 after extraction.

Earlier sandbox smoke before extraction also passed:

```text
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" \
  "set Compile / mainClass := Some(\"PortableRiftBackendPrototype\")" run
```

Observed output:

```text
scala-native-real-regions checksum=247228032 staleRejected=true opens=3 closes=3 heapFallbackAllocs=0 pooledAllocs=20000 pooledReuses=0 arenaBytes=0
jvm-pool-arena checksum=247228032 staleRejected=true opens=3 closes=3 heapFallbackAllocs=0 pooledAllocs=10000 pooledReuses=10000 arenaBytes=0
scala-js-pool checksum=247228032 staleRejected=true opens=3 closes=3 heapFallbackAllocs=0 pooledAllocs=10000 pooledReuses=10000 arenaBytes=0
wasm-linear-memory checksum=2646988032 staleRejected=true opens=3 closes=3 heapFallbackAllocs=20000 pooledAllocs=0 pooledReuses=0 arenaBytes=480000
analysis-only checksum=247228032 staleRejected=true opens=3 closes=3 heapFallbackAllocs=20000 pooledAllocs=0 pooledReuses=0 arenaBytes=0
```

Interpretation:

- JVM/Scala.js models reuse pooled records across epochs.
- Wasm model resets linear-memory cursor at close and records arena bytes.
- Analysis-only model validates active/closed region discipline but allocates
  normally.
- This is a source/API prototype only. It does not prove non-Native allocation
  speedups and does not implement capture checking outside the current Scala
  Native compiler path.
