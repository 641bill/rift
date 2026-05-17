# Portable Rift Backend Prototype

Date: 2026-05-16
Last updated: 2026-05-17 03:09 CEST

Status: prototype smoke evidence. This is not JVM/Scala.js/Wasm performance
evidence. It records the first pure-Scala facade that separates Rift's
Scala-level lifetime model from backend-specific allocation strategies.

## Prototype

Source:

`/Users/siyaoliu/rift/scala-native-rift/experimental/portable-rift/src/main/scala/rift/portable/**`

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

The 2026-05-17 JVM-first split adds:

- `Rift.epoch { scope => ... }`;
- `RiftScope.alloc`, `RiftScope.borrow`, and `RiftScope.allocBytes`;
- `HeapRoot` and `StaticMetadata`;
- `ObjectPool[A <: ReusableRecord]`;
- JVM `heap-gc`, `analysis-only`, and `jvm-pool-arena` modes;
- Scala.js pool and Wasm linear-memory model stubs/examples;
- MUnit runtime-discipline tests;
- `PortableRiftMicrobench` for retained epoch and Broom-style aggregate smoke
  rows.

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

JVM-first module compile:

```text
scala-cli compile --server=false experimental/portable-rift
```

Result: passed on 2026-05-17 after the API/backend split.

JVM-first test suite:

```text
scala-cli test --server=false experimental/portable-rift
```

Result: passed on 2026-05-17, `10/10` MUnit tests. The sandboxed first
attempt failed because Scala CLI could not acquire the Coursier cache lock; the
rerun with approved cache/network access passed.

JVM microbench smoke:

```text
scala-cli run --server=false experimental/portable-rift \
  --main-class rift.portable.PortableRiftMicrobench -- \
  --workload broom-aggregate --records 100000 \
  --epoch-size 10000 --active-timestamps 4 --runs 2
```

Result: passed on 2026-05-17. `heap-gc`, `analysis-only`, and
`jvm-pool-arena` all produced checksum `398184912` and output `100000`. The
pool backend reported `10000` fresh pooled allocations and `90000` pooled
reuses in each run. These are smoke/evidence-harness rows, not performance
claims.

JVM retained-object gate script:

```text
PORTABLE_RIFT_OUT_DIR=/private/tmp/portable-rift-jvm-gate-20260517-clean-smoke \
PORTABLE_RIFT_RECORDS=500000 \
PORTABLE_RIFT_RUNS=2 \
PORTABLE_RIFT_WARMUPS=1 \
PORTABLE_RIFT_JAVA_HEAP=1g \
experimental/portable-rift/scripts/run_jvm_gate.sh
```

Result: passed on 2026-05-17 with escalation because `/usr/bin/time -l` needs
macOS `sysctl` access outside the sandbox. Output directory:

`/private/tmp/portable-rift-jvm-gate-20260517-clean-smoke`

The runner uses:

- separate JVM process per workload/mode;
- `-Xms1g -Xmx1g -XX:+UseG1GC`;
- `-Xlog:gc*:file=...`;
- `/usr/bin/time -l -o ...`;
- no default `System.gc()` in the timed harness.

Compact result summary:

| Workload | Mode | Internal run ms | External real s | Max RSS MB | GC pauses | Checksum/output | Allocation stats |
|---|---:|---:|---:|---:|---:|---|---|
| retained-epoch | `heap-gc` | `3.236`, `4.172` | `2.21` | `113.4` | `1` | matched | `500000` heap fallback allocs |
| retained-epoch | `analysis-only` | `3.239`, `4.230` | `2.18` | `113.6` | `1` | matched | `500000` heap fallback allocs |
| retained-epoch | `jvm-pool-arena` | `10.390`, `8.292` | `2.22` | `115.9` | `1` | matched | `10000` fresh pooled, `490000` reuses |
| broom-aggregate | `heap-gc` | `1.112`, `1.010` | `2.18` | `90.1` | `0` | matched | `500000` heap fallback allocs |
| broom-aggregate | `analysis-only` | `1.044`, `0.988` | `2.15` | `90.7` | `0` | matched | `500000` heap fallback allocs |
| broom-aggregate | `jvm-pool-arena` | `10.713`, `10.413` | `2.46` | `116.8` | `1` | matched | `10000` fresh pooled, `490000` reuses |

Interpretation:

- This gate validates the JVM evidence harness, separate backend modes,
  external RSS capture, GC logging, and pool reuse accounting.
- It is not a JVM performance win. The current pool path is slower and can use
  more RSS on tiny retained shapes.
- Likely reason: HotSpot scalar replacement/escape analysis makes these simple
  heap rows extremely cheap, while explicit pooling adds ArrayBuffer/bookkeeping
  and keeps a pool live.
- Next JVM experiment should use a retained object graph that cannot be
  scalarized, or add an `-XX:-DoEscapeAnalysis` stress control before making
  any performance claim.

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
