# HotSpot Ordinary-Object Region Backend Plan

Date: 2026-05-17
Last updated: 2026-05-17 22:31 CEST

Status: long-term VM-fork roadmap with Patch 1-7 implemented through a narrow
interpreter-only object-allocation and store-guard prototype. Ordinary
Scala/JVM object allocation into Rift regions now works only for explicitly
registered, final/simple primitive-field classes under conservative VM flags.
The first store guards reject static, array, heap-object-field, reflective,
Unsafe, MethodHandle setter, and anonymous-closure retention of live region
objects in the currently covered interpreter/Unsafe/JNI subset. Patch 7 adds
an explicit `verifyLive` API-boundary verifier for stale post-close objects.
GC integration, C1/C2 fast paths, arrays as region allocations, reference
fields inside region objects, automatic stale-use barriers, and broad
bridge/root handling are still future work.

## Goal

Support Rift checked lifetime topologies on the JVM while preserving ordinary
JVM object layout for selected region allocations:

```scala
Rift.epoch { region =>
  val e = new Event(...)
  // lowered to region allocation by the Scala compiler/plugin + HotSpot fork
}
```

The target is stronger than the current portable JVM prototype. The existing
prototype uses heap fallback and explicit object pools. A HotSpot region
backend would allocate normal object layouts in a VM-known region space and
bulk-close that space when Rift's static capture/separation checks prove that
no unsafe references remain.

## Why A HotSpot Fork Is Needed

Ordinary Scala/JVM objects are HotSpot `oop`s. They have VM-owned object
headers, identity, class metadata, GC metadata, reference fields, monitor
state, stack-map/deoptimization behavior, and write-barrier requirements. A
library cannot place arbitrary `new Foo(...)` objects in native memory while
keeping them fully ordinary JVM objects.

Therefore Rift has two JVM tracks:

| Track | What it can support | Status |
|---|---|---|
| Portable JVM library | Source-level `epoch` API, active/closed checks, object pools, FFM/off-heap handles for restricted records, normal heap fallback. | Prototype. |
| HotSpot region fork | Ordinary object layout allocated in VM-known region memory with checked bulk close/reset. | Planned VM research track. |

## V1 VM Design

The first HotSpot milestone should be deliberately narrow:

- fork OpenJDK/HotSpot from a stable JDK line and keep all Rift changes behind
  `-XX:+UseRiftRegions`;
- initially disable compressed oops if needed, or reserve Rift region memory
  inside an address range compatible with compressed references;
- allocate normal object layouts in a VM-known Rift region space, not arbitrary
  `malloc` memory;
- add VM/runtime entrypoints for `RiftRegion.open`, region allocation, and
  `RiftRegion.close`;
- lower checked Scala `new` inside `Rift.epoch` to the region allocation
  entrypoint;
- support final/simple classes first, then broaden only after correctness
  tests pass;
- preserve normal constructor execution after allocation.

## Safety Invariants

V1 should reject mixed-reference cases rather than support every object graph:

- heap object may not retain a region object;
- static/global state may not retain a region object;
- region object may point to heap data only through explicit `HeapRoot`;
- inner region object may not outlive its parent;
- closed region object cannot be accessed;
- escaping closures and generic containers that hide region values are rejected;
- debug VM mode checks heap-to-region stores with a barrier or verifier.

These are the same source-level invariants Rift already needs on Scala Native.
The HotSpot fork exists to make those proofs useful for ordinary JVM object
allocation and bulk close.

## HotSpot Work Items

1. **Buildable fork baseline**
   - Build OpenJDK locally and run a small HotSpot/JTReg smoke suite with no
     Rift changes.
   - Add a guarded `UseRiftRegions` flag and no-op runtime stubs.

2. **Region memory space**
   - Add a VM-known region allocation space compatible with `oop` decoding.
   - Track region handles, active/closed state, high-water marks, and reset
     accounting.
   - Keep region pages outside normal heap collection in v1 unless explicitly
     marked active.

3. **Allocation path**
   - Add an allocation entrypoint that takes a region handle, class metadata,
     and object size.
   - Create normal object headers and field layout.
   - Run normal constructors after allocation.
   - Add debug checks for allocation through closed handles.

4. **Reference safety and barriers**
   - Reject heap-to-region stores in debug/product-safe mode unless a future
     remembered-set design is explicitly added.
   - Allow region-to-heap only through `HeapRoot` or immutable/static metadata.
   - Add verifier tests for static fields, arrays, object fields, closures, and
     generic containers.

5. **GC and safepoints**
   - Ensure active region objects referenced from stacks are valid across
     safepoints.
   - Keep closed regions unreachable from heap and bulk-freeable without
     tracing.
   - In v1, avoid supporting region objects as durable heap roots.

6. **Scala lowering**
   - Reuse the source-level Rift API and capture/separation checker.
   - Lower only checked region allocations to the HotSpot entrypoint.
   - Fall back to heap or reject unsupported allocation shapes.

7. **Evaluation**
   - Start with small correctness tests, then retained-object benchmarks:
     Broom retained dataflow, StreamFlex retained event-correlation latency,
     Yak graph/text epochs, and SPECjbb/Stancu-style transactions.
   - Report real time, throughput, p95/max latency where relevant, RSS, GC
     count/time, region close/reset time, and checksum/output.

## Non-Goals For V1

- Do not support arbitrary unsafe off-heap `oop` addresses outside VM-known
  memory.
- Do not support heap-retains-region with remembered sets in the first
  milestone.
- Do not support reflection-heavy, monitor-heavy, weak-reference, or
  serialization-sensitive region objects as headline cases.
- Do not claim compatibility with all HotSpot GCs until tested per collector.

## Success Criteria

The first credible HotSpot result is:

- a small suite of ordinary JVM object allocations into Rift regions;
- checked rejection of heap-retains-region and use-after-close cases;
- bulk region close without tracing every object;
- matching checksum/output on one retained-object benchmark;
- lower GC work, RSS, or tail latency than natural heap/GC on that benchmark.

Until then, HotSpot regions remain a planned VM research backend, while Scala
Native remains Rift's validated performance backend.

## Execution Checkpoint

The first scaffold now exists under `experimental/hotspot-rift/**`.

Completed:

- local prerequisite preflight script;
- OpenJDK bootstrap/build scripts;
- baseline retained-object Java smoke workload;
- baseline smoke runner with `/usr/bin/time -l` and `-Xlog:gc*`;
- patch roadmap for `UseRiftRegions`, VM-known region space, object allocation,
  and reference safety.

Observed on 2026-05-17:

- `git`, `bash`, `make`, `autoconf`, `clang`, Java `25.0.1`, and Homebrew are
  available after installing `autoconf`;
- stock-JDK baseline smoke passed at
  `/private/tmp/rift-hotspot-smoke-20260517`;
- OpenJDK is cloned at `/Users/siyaoliu/rift/cache/openjdk-rift`;
- the worktree uses local branch `rift-jdk25` from `origin/jdk25`;
- the current Rift VM stack is committed locally as OpenJDK commit
  `c455daa9cef` (`Add Rift verifyLive VM hook`), with the Patch 1-6 base at
  `94e2a36f7b9` (`Prototype Rift region backend`);
- the OpenJDK worktree remote `rift-github` points at
  `git@github.com:641bill/jdk.git`, and branch `rift-jdk25` is pushed there
  while tracking `rift-github/rift-jdk25`;
- `origin` still points at `https://github.com/openjdk/jdk.git` for upstream
  OpenJDK;
- Xcode 26.5 was installed and an OpenJDK macOS devkit was created at
  `/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode26.5-MacOSX26`;
- `experimental/hotspot-rift/scripts/build_openjdk.sh` now prepends the
  mounted Metal Toolchain MobileAsset path with `--with-toolchain-path`, so
  configure finds working `metal`/`metallib`;
- the clean fastdebug `images` build passed, producing
  `/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java`;
- built-JDK baseline smoke passed at
  `/private/tmp/rift-hotspot-smoke-built-20260517`;
- Patch 1-3 has been implemented in the OpenJDK worktree and exported as
  `experimental/hotspot-rift/patches/01-rift-region-stubs.patch`;
- the patch adds `-XX:+UseRiftRegions`, `jdk.internal.rift.RiftRegion`,
  per-thread current-region state, active/closed handles, and a VM-owned raw
  bump/reset arena for lifecycle/stats testing;
- the patched fastdebug VM builds;
- `experimental/hotspot-rift/scripts/run_region_smoke.sh` passes at
  `/private/tmp/rift-hotspot-region-smoke-20260517` with `disabled-ok` and
  `enabled-ok`;
- flag-off built-JDK baseline smoke after patch passes at
  `/private/tmp/rift-hotspot-smoke-after-rift-20260517`.
- Patch 4 has been implemented and exported as
  `experimental/hotspot-rift/patches/02-interpreter-object-allocation.patch`;
- Patch 4 adds `RiftRegion.registerEligible(Class<?>)`, class-shape
  validation for final primitive-field classes, an interpreter `_new` hook,
  region object allocation/counting, and debug heap-membership hooks needed for
  the smoke test;
- `experimental/hotspot-rift/scripts/run_object_region_smoke.sh` passes at
  `/private/tmp/rift-hotspot-object-region-smoke-stable-20260517` with
  `object-enabled-ok`;
- the existing region smoke still passes after Patch 4 at
  `/private/tmp/rift-hotspot-region-smoke-stable-20260517`;
- flag-off baseline smoke after Patch 4 passes at
  `/private/tmp/rift-hotspot-smoke-stable-after-object-20260517`.
- Patch 5 has been implemented and exported as
  `experimental/hotspot-rift/patches/03-interpreter-store-guard.patch`;
- Patch 5 adds an interpreter oop-store guard that rejects storing a live
  region oop into non-region memory through the covered interpreter paths;
- Patch 5 also forces interpreter `new` through the runtime allocation hook
  while `-XX:+UseRiftRegions` is enabled, so resolved classes do not silently
  bypass region allocation through the normal TLAB fast path;
- `experimental/hotspot-rift/scripts/run_object_region_smoke.sh` passes at
  `/private/tmp/rift-hotspot-object-region-smoke-patch5-slownew-20260517`
  with `object-enabled-ok`, including direct `putstatic`, `aastore`, and
  `putfield` rejection tests;
- the existing region smoke still passes after Patch 5 at
  `/private/tmp/rift-hotspot-region-smoke-patch5-slownew-20260517`;
- flag-off baseline smoke after Patch 5 passes at
  `/private/tmp/rift-hotspot-smoke-patch5-slownew-20260517`.
- generic/container hiding smoke passes at
  `/private/tmp/rift-hotspot-object-region-smoke-generic-container-20260517`,
  covering widened generic-cell retention and `ArrayList.add` retention in the
  interpreter subset.
- Patch 6 has been implemented and exported as
  `experimental/hotspot-rift/patches/04-unsafe-jni-store-guard.patch`;
- a pre-Patch-6 probe showed reflective `Field.set` could retain a live Rift
  region object in heap state and then crash fastdebug verification;
- Patch 6 adds checks to `Unsafe.putReference`,
  `Unsafe.putReferenceVolatile`, JNI `SetObjectField`, and JNI
  `SetStaticObjectField`;
- `experimental/hotspot-rift/scripts/run_object_region_smoke.sh` now passes at
  `/private/tmp/rift-hotspot-object-region-smoke-patch6c-20260517`, covering
  reflective `Field.set`, `Unsafe.putReference`, `MethodHandle` setter, and
  anonymous closure capture retention attempts;
- region lifecycle smoke passes after Patch 6 at
  `/private/tmp/rift-hotspot-region-smoke-patch6b-20260517`;
- flag-off baseline smoke after Patch 6 passes at
  `/private/tmp/rift-hotspot-smoke-patch6-20260517`.
- a stale post-close use experiment using an AArch64 interpreter
  receiver-load VM hook was tried and backed out after crashing normal
  bootstrap/invoke execution. The stable Patch 5 worktree was rebuilt and
  object/lifecycle/baseline smokes passed again at
  `/private/tmp/rift-hotspot-object-region-smoke-stable-after-stale-backout-20260517`,
  `/private/tmp/rift-hotspot-region-smoke-stable-after-stale-backout-20260517`,
  and `/private/tmp/rift-hotspot-smoke-stable-after-stale-backout-20260517`.
- Patch 7 has been implemented and exported as
  `experimental/hotspot-rift/patches/05-explicit-verify-live.patch`;
- Patch 7 adds internal `RiftRegion.verifyLive(Object)` and VM-side
  `RiftRegionRuntime::verify_live_oop`, remembers closed region address
  ranges, and rejects closed region objects through explicit verification and
  store guards;
- active regions are checked before remembered closed ranges so C-heap
  address reuse does not make an active region object look stale;
- object-region smoke passes after Patch 7 at
  `/private/tmp/rift-hotspot-object-region-smoke-patch7c-20260517`;
- region lifecycle smoke passes after Patch 7 at
  `/private/tmp/rift-hotspot-region-smoke-patch7c-20260517`;
- flag-off baseline smoke after Patch 7 passes at
  `/private/tmp/rift-hotspot-smoke-patch7c-20260517`.

Patch 4 limitations:

- object allocation is interpreter-only;
- only explicitly registered eligible classes are redirected into region
  memory;
- unregistered classes heap-fallback in this prototype so incidental VM/JDK
  allocations inside an active region still work;
- supported classes must be final/simple and have only primitive instance
  fields;
- first correctness uses `-Xint -XX:+UseSerialGC -XX:-UseCompressedOops
  -XX:-UseCompactObjectHeaders`;
- region oops are not yet scanned by GC and must not survive region close;
- reference-safety enforcement exists only for the current interpreter
  oop-store subset.

Patch 5 false start:

- a close-time whole-heap scan with `Universe::heap()->object_iterate` was
  tested and removed;
- it crashed during ordinary close because the heap walk is not safe from that
  path outside a safepoint;
- the next safety implementation should use store/barrier hooks or an explicit
  safepoint VM operation.

Patch 5-6 accepted path:

- interpreter `do_oop_store` now calls `RiftRegionRuntime::verify_oop_store`
  before non-null oop stores;
- Unsafe/JNI object-store entrypoints now call the same verifier before
  storing;
- live region oops stored into non-region memory throw
  `IllegalStateException`;
- direct smoke tests cover `putstatic`, `aastore`, and `putfield` retention
  rejection, plus reflective, Unsafe, MethodHandle setter, and anonymous
  closure capture routes in the covered subset.

Next concrete step: extend reference safety beyond the current interpreter plus
Unsafe/JNI plus explicit verifier subset. Add tests and VM checks for C1/C2
barriers, native stores outside the guarded entrypoints, supported
region-to-heap bridges, and GC/safepoint behavior before making any JVM
backend safety or performance claim. Patch 7 is an API-boundary stale-use
verifier, not a general object-use barrier; automatic stale-use protection
still needs a dedicated Rift lowering pattern or a deeper
barrier/deoptimization design after the GC/safepoint plan is clearer.
