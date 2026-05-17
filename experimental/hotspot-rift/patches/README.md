# HotSpot Patch Roadmap

Last updated: 2026-05-17 16:42 CEST

This directory holds patch notes and exported patches for the HotSpot
ordinary-object Rift backend. Patch 1-5 are now exported. Patch 4 is a narrow
interpreter-only object-allocation prototype; Patch 5 adds the first
interpreter store guard. This is still not a complete safe JVM Rift backend.

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
  full HotSpot barrier implementation. C1/C2, native/Unsafe/reflection stores,
  stale post-close object use, and GC scanning remain future work.
- A follow-up stale-use experiment that called a VM verifier from the generic
  AArch64 interpreter receiver-load path was tried and backed out. It crashed
  normal bootstrap/invoke execution, so stale-use checking should use a
  dedicated Rift lowering helper, explicit API-boundary verifier, or deeper
  barrier/deoptimization design instead.
