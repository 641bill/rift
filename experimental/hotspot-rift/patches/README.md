# HotSpot Patch Roadmap

Last updated: 2026-05-18 00:24 CEST

This directory holds patch notes and exported patches for the HotSpot
ordinary-object Rift backend. Patch 1-13 are now exported. Patch 4 is a narrow
interpreter-only object-allocation prototype; Patch 5 adds the first
interpreter store guard; Patch 6 extends store checks to Unsafe/JNI paths used
by reflection; Patch 7 adds an explicit live-object verifier for API-boundary
stale-use checks; Patch 8 adds a conservative C1 allocation route for eligible
`new` bytecodes; Patch 9 adds conservative C1 compiled store guards; Patch 10
gates unsupported C2/JVMCI compilation while Rift regions are enabled; Patch
11 adds a first Serial GC root-handling prototype for live primitive-field
region objects; Patch 12 rejects unsupported collector/header configurations
up front; Patch 13 adds explicit heap-root bridge handles for GC-visible heap
metadata referenced by primitive fields. This is still not a complete safe JVM
Rift backend.

## Patch 0: Build Baseline

Expected result:

- clean OpenJDK checkout builds with `fastdebug`;
- baseline smoke runs on the produced JDK;
- no Rift VM changes yet.

## Patch 1-3: VM Flag, Active Handles, And Raw Arena

Patch file:

`01-rift-region-stubs.patch`

Implemented:

- guarded experimental `-XX:+UseRiftRegions` flag;
- internal Java test surface `jdk.internal.rift.RiftRegion`;
- native VM entrypoints for `open`, `enter`, `leave`, `close`, `current`,
  `allocateRaw`, and `stats`;
- `JavaThread` current-region state;
- active/closed handle checks, nested-region rejection, stale/inactive
  allocation rejection;
- VM-owned raw bump/reset arena and lifecycle counters.

Validation:

- patched fastdebug OpenJDK image builds;
- `experimental/hotspot-rift/scripts/run_region_smoke.sh` passes with
  `disabled-ok` and `enabled-ok`;
- flag-off built-JDK baseline smoke still passes.

Limitations:

- no ordinary `oop` allocation is redirected;
- no HotSpot allocation path is intercepted;
- no reference-barrier safety exists yet.

## Patch 4: Simple Object Allocation

Patch file:

`02-interpreter-object-allocation.patch`

Implemented:

- `RiftRegion.registerEligible(Class<?>)` internal VM test surface;
- class eligibility validation for final/simple primitive-field classes;
- interpreter `_new` hook that redirects registered eligible classes to the
  active region allocation path;
- region object allocation counter in `RiftRegion.stats`;
- debug heap-membership hooks so the interpreter smoke can invoke methods on a
  region object;
- constructors still run normally;
- unregistered classes heap-fallback in this prototype so incidental JDK/VM
  allocations inside an active region still work.

Validation:

- patched fastdebug OpenJDK image builds;
- `experimental/hotspot-rift/scripts/run_object_region_smoke.sh` passes with
  `object-enabled-ok`;
- the Patch 1-3 region smoke still passes after Patch 4;
- flag-off built-JDK baseline smoke still passes after Patch 4.

First correctness flags:

```text
-Xint -XX:+UseSerialGC -XX:-UseCompressedOops -XX:-UseCompactObjectHeaders
```

Unsupported in this patch:

- arrays;
- reference fields;
- monitors;
- weak references;
- reflection-heavy objects;
- C1/C2 fast allocation paths;
- heap-to-region retention.

Important limitation:

Patch 4 does not make region objects safe across arbitrary safepoints or GC.
It has no heap-to-region store barrier, no reference-field support, no arrays,
no C1/C2 allocation path, and no post-close stale-use protection beyond the
region-handle lifecycle checks. Treat it as object-allocation mechanism
evidence only.

## Patch 5: Reference Safety Checks

Patch file:

`03-interpreter-store-guard.patch`

Implemented:

- interpreter `do_oop_store` calls a Rift verifier before non-null oop stores;
- live region oops cannot be stored into non-region memory through the
  covered interpreter store paths;
- interpreter `_new` is forced through the runtime hook when
  `-XX:+UseRiftRegions` is enabled, so resolved classes do not bypass region
  allocation through the normal TLAB fast path;
- direct `putstatic`, `aastore`, and `putfield` negative tests reject
  heap retention of a live region object.
- widened generic-cell retention and `ArrayList.add` retention are rejected in
  the interpreter subset.

Validation:

- patched fastdebug OpenJDK image builds;
- `experimental/hotspot-rift/scripts/run_object_region_smoke.sh` passes with
  `object-enabled-ok`;
- the Patch 1-3 region smoke still passes after Patch 5;
- flag-off built-JDK baseline smoke still passes after Patch 5.

Implementation note:

- A close-time whole-heap scan using `Universe::heap()->object_iterate` was
  tried and removed. It crashed outside a safepoint, so Patch 5 should be built
  on real store/barrier hooks or an explicit safepoint VM operation.
- The accepted Patch 5 implementation is an interpreter-only store guard, not a
  full HotSpot barrier implementation. C1/C2, some native/reflection routes,
  stale post-close object use, and GC scanning remain future work.
- A follow-up stale-use experiment that called a VM verifier from the generic
  AArch64 interpreter receiver-load path was tried and backed out. It crashed
  normal bootstrap/invoke execution, so stale-use checking should use a
  dedicated Rift lowering helper, explicit API-boundary verifier, or deeper
  barrier/deoptimization design instead.

## Patch 6: Unsafe/JNI Store Guards

Patch file:

`04-unsafe-jni-store-guard.patch`

Implemented:

- `Unsafe.putReference` and `Unsafe.putReferenceVolatile` verify live Rift
  region oops before storing;
- JNI `SetObjectField` and `SetStaticObjectField` verify live Rift region oops
  before storing;
- the object-region smoke now covers reflective `Field.set`,
  `Unsafe.putReference`, `MethodHandle` setter, and anonymous closure capture
  retention attempts.

Validation:

- patched fastdebug OpenJDK image builds;
- `experimental/hotspot-rift/scripts/run_object_region_smoke.sh` passes at
  `/private/tmp/rift-hotspot-object-region-smoke-patch6c-20260517` with
  `object-enabled-ok`;
- the Patch 1-3 region smoke still passes at
  `/private/tmp/rift-hotspot-region-smoke-patch6b-20260517`;
- flag-off built-JDK baseline smoke still passes at
  `/private/tmp/rift-hotspot-smoke-patch6-20260517`.

Implementation note:

- A pre-Patch-6 probe showed that reflective `Field.set` could retain a region
  object and then crash fastdebug verification because the heap contained a
  non-heap region oop. Patch 6 closes that route through the Unsafe/JNI store
  entrypoints used by the reflective path.
- This is still not a complete store-barrier design. C1/C2 compiled stores,
  native code outside these entrypoints, reflection routes not backed by these
  calls, stale post-close object use, and GC scanning remain future work.

## Patch 7: Explicit Live Verifier

Patch file:

`05-explicit-verify-live.patch`

Implemented:

- `RiftRegion.verifyLive(Object)` internal VM test surface;
- `RiftRegionRuntime::verify_live_oop` for explicit API-boundary stale-use
  checks;
- closed region address ranges are remembered after close/reset so an explicit
  verifier can reject objects from closed Rift regions;
- store guards now use the same known-range lookup and reject closed region
  objects as well as live region objects;
- active regions are matched before closed ranges, avoiding false positives
  when the C heap reuses an old region address.

Validation:

- patched fastdebug OpenJDK image builds;
- `experimental/hotspot-rift/scripts/run_object_region_smoke.sh` passes at
  `/private/tmp/rift-hotspot-object-region-smoke-patch7c-20260517` with
  `object-enabled-ok`;
- the Patch 1-3 region smoke still passes at
  `/private/tmp/rift-hotspot-region-smoke-patch7c-20260517`;
- flag-off built-JDK baseline smoke still passes at
  `/private/tmp/rift-hotspot-smoke-patch7c-20260517`.

Implementation note:

- Patch 7 is not an automatic arbitrary object-use barrier. It gives Rift
  lowering and VM tests an explicit verifier to call at API boundaries after a
  region closes. A complete design still needs GC/safepoint integration and
  compiled-path barrier coverage.

## Patch 8: C1 Region Allocation

Patch file:

`06-c1-region-allocation.patch`

Implemented:

- C1 disables inline fast allocation while `-XX:+UseRiftRegions` is enabled
  and routes `new` bytecodes through the existing C1 runtime allocation stub;
- `Runtime1::new_instance` now asks `RiftRegionRuntime::allocate_instance`
  first when the current Java thread has an active Rift region;
- unsupported or unregistered classes still fall back to normal heap
  allocation in this prototype;
- added `RiftHotSpotC1RegionAllocationSmoke` and
  `run_c1_object_region_smoke.sh` to verify C1 allocation of registered
  primitive-field records into an active Rift region.

Validation:

- patched fastdebug OpenJDK image builds;
- C1 allocation smoke passes at
  `/private/tmp/rift-hotspot-c1-region-smoke-patch8-20260517` with
  `c1-allocation-ok`;
- interpreter object-region smoke still passes at
  `/private/tmp/rift-hotspot-object-region-smoke-patch8-20260517`;
- region lifecycle smoke still passes at
  `/private/tmp/rift-hotspot-region-smoke-patch8-20260517`;
- flag-off built-JDK baseline smoke still passes at
  `/private/tmp/rift-hotspot-smoke-patch8-20260517`.

Implementation note:

- Patch 8 is correctness-first and intentionally disables C1 fast allocation
  under `UseRiftRegions`. It does not yet add C1/C2 compiled store barriers or
  C2 allocation support.

## Patch 9: C1 Store Guards

Patch file:

`07-c1-store-guards.patch`

Implemented:

- C1 reference stores call a Rift runtime stub before `putstatic`,
  `putfield`, and object-array stores;
- the stub passes the stored value and destination base object to
  `RiftRegionRuntime::verify_oop_store_to_base`;
- the verifier rejects a live or closed Rift region object when the destination
  base is ordinary heap state, while allowing stores whose destination base is
  itself a live Rift region object;
- added `RiftHotSpotC1StoreGuardSmoke` and
  `run_c1_store_guard_smoke.sh`.

Validation:

- patched fastdebug OpenJDK image builds;
- C1 store-guard smoke passes at
  `/private/tmp/rift-hotspot-c1-store-guard-smoke-patch9c-20260517` with
  `c1-store-guard-ok`;
- C1 allocation smoke still passes at
  `/private/tmp/rift-hotspot-c1-region-smoke-patch9-20260517`;
- interpreter object-region smoke still passes at
  `/private/tmp/rift-hotspot-object-region-smoke-patch9-20260517`;
- region lifecycle smoke still passes at
  `/private/tmp/rift-hotspot-region-smoke-patch9-20260517`;
- flag-off built-JDK baseline smoke still passes at
  `/private/tmp/rift-hotspot-smoke-patch9-20260517`.

Implementation note:

- Patch 9 covers C1-generated reference stores only. C2 allocation/stores,
  native stores outside the guarded Unsafe/JNI entrypoints, reference fields in
  supported region objects, arrays as region allocations, and GC/safepoint
  integration remain future work.

## Patch 10: C2 Safety Gate

Patch file:

`08-c2-safety-gate.patch`

Implemented:

- `CompileBroker::compile_method` rejects C2 and JVMCI compilation requests
  while `-XX:+UseRiftRegions` is enabled;
- C1 and interpreter execution remain available for the supported prototype
  subset;
- added `run_c2_gate_smoke.sh`, which forces tiered compilation up to level 4
  and confirms the C1 allocation and C1 store-guard smokes still pass.

Validation:

- patched fastdebug OpenJDK image builds;
- C2-gate smoke passes at
  `/private/tmp/rift-hotspot-c2-gate-smoke-patch10-20260517` with
  `c2-gate-ok`;
- C1 store-guard smoke still passes at
  `/private/tmp/rift-hotspot-c1-store-guard-smoke-patch10-20260517`;
- C1 allocation smoke still passes at
  `/private/tmp/rift-hotspot-c1-region-smoke-patch10-20260517`;
- interpreter object-region smoke still passes at
  `/private/tmp/rift-hotspot-object-region-smoke-patch10-20260517`;
- region lifecycle smoke still passes at
  `/private/tmp/rift-hotspot-region-smoke-patch10-20260517`;
- flag-off built-JDK baseline smoke still passes at
  `/private/tmp/rift-hotspot-smoke-patch10-20260517`.

Implementation note:

- Patch 10 does not implement C2 region allocation or C2 store barriers. It is
  a conservative safety gate so the prototype cannot silently run unsupported
  C2/JVMCI paths under `UseRiftRegions`.

## Patch 11: Serial GC Region Roots

Patch file:

`09-serial-gc-region-roots.patch`

Implemented:

- Serial Full GC root marking, marking-stack work, and root pointer adjustment
  recognize uncompressed Rift region oops while `-XX:+UseRiftRegions` is
  enabled;
- the current prototype skips marking/relocating those roots because supported
  region objects are primitive-field-only and live in non-GC-managed Rift
  region memory;
- added validation through `run_safepoint_probe.sh`, which now confirms both a
  plain safepoint and explicit `System.gc()` with a live region object pass.

Validation:

- patched fastdebug OpenJDK image builds;
- safepoint/GC probe passes at
  `/private/tmp/rift-hotspot-safepoint-probe-patch11-20260518` with
  `safepoint-probe-ok`, `system-gc-probe-ok`, and
  `system-gc-probe-status=passed`;
- C2-gate smoke still passes at
  `/private/tmp/rift-hotspot-c2-gate-smoke-patch11-20260518`;
- C1 store-guard smoke still passes at
  `/private/tmp/rift-hotspot-c1-store-guard-smoke-patch11-20260518`;
- C1 allocation smoke still passes at
  `/private/tmp/rift-hotspot-c1-region-smoke-patch11-20260518`;
- interpreter object-region smoke still passes at
  `/private/tmp/rift-hotspot-object-region-smoke-patch11-20260518`;
- region lifecycle smoke still passes at
  `/private/tmp/rift-hotspot-region-smoke-patch11-20260518`;
- flag-off baseline smoke still passes at
  `/private/tmp/rift-hotspot-smoke-patch11-20260518`.

Implementation note:

- Patch 11 is deliberately Serial-GC-only and primitive-field-only. It does
  not scan references inside region objects, does not support region object
  arrays, does not support compressed oops, and does not make other collectors
  aware of region memory. It proves the first active-region root handling path,
  not broad JVM GC integration.

## Patch 12: VM Configuration Gate

Patch file:

`10-vm-config-gate.patch`

Implemented:

- the Rift runtime entrypoints now reject unsupported VM configurations while
  `-XX:+UseRiftRegions` is enabled;
- the prototype currently requires `-XX:+UseSerialGC`,
  `-XX:-UseCompressedOops`, and `-XX:-UseCompactObjectHeaders`;
- added `RiftHotSpotConfigGateSmoke` and `run_config_gate_smoke.sh`, which
  run with the default unsupported collector/header settings and expect a
  clean `UnsupportedOperationException` instead of a later VM crash.

Validation:

- patched fastdebug OpenJDK image builds;
- configuration-gate smoke passes at
  `/private/tmp/rift-hotspot-config-gate-smoke-patch12-20260518` with
  `config-gate-ok`;
- region lifecycle smoke still passes at
  `/private/tmp/rift-hotspot-region-smoke-patch12-20260518`;
- safepoint/GC probe still passes at
  `/private/tmp/rift-hotspot-safepoint-probe-patch12-20260518`;
- C2-gate smoke still passes at
  `/private/tmp/rift-hotspot-c2-gate-smoke-patch12-20260518`;
- C1 store-guard smoke still passes at
  `/private/tmp/rift-hotspot-c1-store-guard-smoke-patch12-20260518`;
- C1 allocation smoke still passes at
  `/private/tmp/rift-hotspot-c1-region-smoke-patch12-20260518`;
- interpreter object-region smoke still passes at
  `/private/tmp/rift-hotspot-object-region-smoke-patch12-20260518`;
- flag-off baseline smoke still passes at
  `/private/tmp/rift-hotspot-smoke-patch12-20260518`.

Implementation note:

- Patch 12 does not broaden collector support. It narrows the accepted runtime
  configuration to match the implementation that is actually covered by Patch
  11.

## Patch 13: Heap-Root Bridge Handles

Patch file:

`11-heap-root-handles.patch`

Implemented:

- `RiftRegion.createHeapRoot(Object)`, `resolveHeapRoot(long)`, and
  `releaseHeapRoot(long)` internal VM test-surface entrypoints;
- VM-side heap roots are JNI global handles, so the ordinary heap object stays
  visible to GC and is updated normally across collection;
- creating a heap-root handle for a Rift region object is rejected;
- the supported region object still has only primitive fields, so it stores
  the bridge as a `long` handle rather than an unscanned heap `oop` field;
- object-region smoke now validates resolving the bridge before and after
  `System.gc()`, then closes the region and confirms the region record is
  stale.

Validation:

- patched fastdebug OpenJDK image builds;
- object-region smoke passes at
  `/private/tmp/rift-hotspot-object-region-smoke-patch13-20260518` with
  `object-enabled-ok`;
- safepoint/GC probe still passes at
  `/private/tmp/rift-hotspot-safepoint-probe-patch13-20260518`;
- configuration-gate smoke still passes at
  `/private/tmp/rift-hotspot-config-gate-smoke-patch13-20260518`;
- C2-gate smoke still passes at
  `/private/tmp/rift-hotspot-c2-gate-smoke-patch13-20260518`;
- C1 store-guard smoke still passes at
  `/private/tmp/rift-hotspot-c1-store-guard-smoke-patch13-20260518`;
- C1 allocation smoke still passes at
  `/private/tmp/rift-hotspot-c1-region-smoke-patch13-20260518`;
- region lifecycle smoke still passes at
  `/private/tmp/rift-hotspot-region-smoke-patch13-20260518`;
- flag-off baseline smoke still passes at
  `/private/tmp/rift-hotspot-smoke-patch13-20260518`.

Implementation note:

- Patch 13 is a bridge/root rule prototype, not reference-field support.
  Region objects are still primitive-field-only, and arbitrary heap references
  inside region objects remain rejected until the VM can scan/update those
  fields or the source checker proves a safe immutable/static case.
