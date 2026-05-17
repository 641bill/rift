# HotSpot Ordinary-Object Region Backend Plan

Date: 2026-05-17
Last updated: 2026-05-18 00:13 CEST

Status: long-term VM-fork roadmap with Patch 1-12 implemented through a narrow
interpreter-only object-allocation and store-guard prototype. Ordinary
Scala/JVM object allocation into Rift regions now works only for explicitly
registered, final/simple primitive-field classes under conservative VM flags.
The first store guards reject static, array, heap-object-field, reflective,
Unsafe, MethodHandle setter, and anonymous-closure retention of live region
objects in the currently covered interpreter/Unsafe/JNI subset. Patch 7 adds
an explicit `verifyLive` API-boundary verifier for stale post-close objects.
Patch 8 adds conservative C1 allocation through the runtime stub for eligible
records. Patch 9 adds conservative C1 compiled store guards. Patch 10 gates
unsupported C2/JVMCI compilation while Rift regions are enabled. GC
integration now has a first Serial-GC-only root handling prototype in Patch
11 for uncompressed primitive-field region objects. Patch 12 gates unsupported
VM configurations up front, so the prototype now fails cleanly unless it is
run with Serial GC, uncompressed oops, and non-compact object headers. True C2
allocation/stores, arrays as region allocations, reference fields inside
region objects, automatic stale-use barriers, other collectors, compressed
oops, and broad bridge/root handling are still future work.

The first GC/safepoint probe narrowed the next VM blocker: a live region object
survived a plain safepoint-only test in the current interpreter subset, but
`System.gc()` initially aborted fastdebug verification because root handling
required the object to be in the Java heap. Patch 11 fixes that narrow Serial
GC path by skipping marking/relocation for active Rift region roots. That is
not full GC integration; it is a collector-specific proof point for the
primitive-field-only subset.

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
  `30c3c0e49034` (`Gate unsupported Rift VM configs`), with the Patch 11 base
  at `8984cdb1241f` (`Skip Rift roots in Serial GC`), the Patch 10 base at
  `37f9d24dd561` (`Gate C2 under Rift regions`), the Patch 9 base at
  `f5bcc3f9629` (`Add C1 Rift store guards`), the Patch 8 base at
  `8cd8da1a443` (`Add C1 Rift region allocation path`), the Patch 7 base at
  `c455daa9cef` (`Add Rift verifyLive VM hook`), and the Patch 1-6 base at
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
- Patch 8 has been implemented and exported as
  `experimental/hotspot-rift/patches/06-c1-region-allocation.patch`;
- Patch 8 disables C1 inline fast allocation while `-XX:+UseRiftRegions` is
  enabled and sends `new` through `Runtime1::new_instance`;
- `Runtime1::new_instance` now allocates eligible classes into the active Rift
  region when one exists and otherwise falls back to normal heap allocation;
- the new C1 allocation smoke passes at
  `/private/tmp/rift-hotspot-c1-region-smoke-patch8-20260517`;
- interpreter object, region lifecycle, and flag-off baseline smokes pass
  after Patch 8 at `/private/tmp/rift-hotspot-object-region-smoke-patch8-20260517`,
  `/private/tmp/rift-hotspot-region-smoke-patch8-20260517`, and
  `/private/tmp/rift-hotspot-smoke-patch8-20260517`.
- Patch 9 has been implemented and exported as
  `experimental/hotspot-rift/patches/07-c1-store-guards.patch`;
- Patch 9 inserts a C1 runtime-stub call before compiled reference stores and
  rejects retaining live/closed Rift region objects in ordinary heap bases;
- C1 store-guard smoke passes at
  `/private/tmp/rift-hotspot-c1-store-guard-smoke-patch9c-20260517`;
- C1 allocation, interpreter object, region lifecycle, and flag-off baseline
  smokes pass after Patch 9 at
  `/private/tmp/rift-hotspot-c1-region-smoke-patch9-20260517`,
  `/private/tmp/rift-hotspot-object-region-smoke-patch9-20260517`,
  `/private/tmp/rift-hotspot-region-smoke-patch9-20260517`, and
  `/private/tmp/rift-hotspot-smoke-patch9-20260517`.
- Patch 10 has been implemented and exported as
  `experimental/hotspot-rift/patches/08-c2-safety-gate.patch`;
- Patch 10 gates C2/JVMCI compilation while `-XX:+UseRiftRegions` is enabled,
  so unsupported compiled paths cannot silently bypass the C1/interpreter
  allocation and store-guard subset;
- C2-gate smoke passes at
  `/private/tmp/rift-hotspot-c2-gate-smoke-patch10-20260517`;
- C1 store-guard, C1 allocation, interpreter object, region lifecycle, and
  flag-off baseline smokes pass after Patch 10 at
  `/private/tmp/rift-hotspot-c1-store-guard-smoke-patch10-20260517`,
  `/private/tmp/rift-hotspot-c1-region-smoke-patch10-20260517`,
  `/private/tmp/rift-hotspot-object-region-smoke-patch10-20260517`,
  `/private/tmp/rift-hotspot-region-smoke-patch10-20260517`, and
  `/private/tmp/rift-hotspot-smoke-patch10-20260517`.
- the first safepoint/GC probe passes the safepoint-only case and fails the
  explicit-GC case at
  `/private/tmp/rift-hotspot-safepoint-probe-patch10-20260517`;
- the explicit-GC failure is a fastdebug abort at
  `compressedOops.inline.hpp:87`: `assert(Universe::is_in_heap(v)) failed:
  object not in heap`.
- Patch 11 has been implemented and exported as
  `experimental/hotspot-rift/patches/09-serial-gc-region-roots.patch`;
- Patch 11 teaches Serial Full GC root marking, marking-stack work, and root
  pointer adjustment to recognize uncompressed Rift region oops and skip
  marking/relocating them in the current primitive-field-only subset;
- safepoint/GC probe now passes at
  `/private/tmp/rift-hotspot-safepoint-probe-patch11-20260518`;
- C2-gate, C1 store-guard, C1 allocation, interpreter object, region
  lifecycle, and flag-off baseline smokes pass after Patch 11 at
  `/private/tmp/rift-hotspot-c2-gate-smoke-patch11-20260518`,
  `/private/tmp/rift-hotspot-c1-store-guard-smoke-patch11-20260518`,
  `/private/tmp/rift-hotspot-c1-region-smoke-patch11-20260518`,
  `/private/tmp/rift-hotspot-object-region-smoke-patch11-20260518`,
  `/private/tmp/rift-hotspot-region-smoke-patch11-20260518`, and
  `/private/tmp/rift-hotspot-smoke-patch11-20260518`.
- Patch 12 has been implemented and exported as
  `experimental/hotspot-rift/patches/10-vm-config-gate.patch`;
- Patch 12 rejects unsupported VM configurations through the Rift runtime
  entrypoints unless `-XX:+UseSerialGC`, `-XX:-UseCompressedOops`, and
  `-XX:-UseCompactObjectHeaders` are active;
- config-gate smoke passes at
  `/private/tmp/rift-hotspot-config-gate-smoke-patch12-20260518`;
- region lifecycle, safepoint/GC, C2-gate, C1 store-guard, C1 allocation,
  interpreter object, and flag-off baseline smokes pass after Patch 12 at
  `/private/tmp/rift-hotspot-region-smoke-patch12-20260518`,
  `/private/tmp/rift-hotspot-safepoint-probe-patch12-20260518`,
  `/private/tmp/rift-hotspot-c2-gate-smoke-patch12-20260518`,
  `/private/tmp/rift-hotspot-c1-store-guard-smoke-patch12-20260518`,
  `/private/tmp/rift-hotspot-c1-region-smoke-patch12-20260518`,
  `/private/tmp/rift-hotspot-object-region-smoke-patch12-20260518`, and
  `/private/tmp/rift-hotspot-smoke-patch12-20260518`.

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

Next concrete step: generalize the GC/safepoint story beyond the current
explicitly gated Serial-GC, uncompressed-oop, primitive-field-only root-skip
prototype. Patch 10 prevents unsupported C2/JVMCI execution under
`UseRiftRegions`, so true C2 support can wait. Native stores outside the
guarded entrypoints, supported region-to-heap bridges, other collectors,
compressed oops, reference fields, and automatic stale-use protection still
need dedicated design before making any JVM backend safety or performance
claim.
