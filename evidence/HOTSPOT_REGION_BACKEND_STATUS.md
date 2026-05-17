# HotSpot Region Backend Status

Date: 2026-05-17
Last updated: 2026-05-17 23:57 CEST

Status: VM-fork Patch 1-10 evidence. Patch 4 proves a narrow
interpreter-only ordinary-object allocation prototype for explicitly
registered final primitive-field classes. Patch 5 adds an interpreter oop-store
guard that rejects heap retention of live region objects for static fields,
object arrays, and object fields in the supported subset. Patch 6 extends store
guards to Unsafe/JNI object-store entrypoints used by reflection and low-level
libraries. Patch 7 adds an explicit `verifyLive` VM hook for API-boundary
stale-use checks and teaches store guards to reject closed region objects.
Patch 8 adds conservative C1 allocation through the runtime allocation stub.
Patch 9 adds conservative C1 compiled store guards for reference stores. Patch
10 gates unsupported C2/JVMCI compilation while Rift regions are enabled.
This is still not a performance-ready JVM Rift backend because GC integration,
true C2 allocation/stores, arrays as region allocations, reference fields
inside region objects, and automatic broad post-close stale-use handling are
not implemented.

The first safepoint/GC probe now confirms the immediate GC blocker: a live
region object survives a plain safepoint-only check in the current interpreter
subset, but `System.gc()` aborts fastdebug verification because compressed-oop
root handling still requires the value to be in the Java heap.

## Scaffold

Source:

`/Users/siyaoliu/rift/experimental/hotspot-rift/**`

Implemented scaffold:

- HotSpot experiment README and ownership notes;
- prerequisite preflight script;
- OpenJDK bootstrap script;
- OpenJDK fastdebug build script;
- stock/patched-JDK baseline smoke script;
- retained-object Java baseline smoke workload;
- patch roadmap for `UseRiftRegions`, region space, simple object allocation,
  and reference safety checks.

## Preflight

Command:

```text
experimental/hotspot-rift/scripts/check_prereqs.sh
```

Result on 2026-05-17:

| Tool | Status | Observed |
|---|---|---|
| `git` | OK | `/usr/bin/git`, Apple Git `2.50.1` |
| `bash` | OK | `/bin/bash`, GNU bash `3.2.57` |
| `make` | OK | `/usr/bin/make`, GNU Make `3.81` |
| `autoconf` | Initially missing, then installed | Homebrew `autoconf 2.73` |
| `clang` | OK | Apple clang `21.0.0` |
| `java` | OK | OpenJDK `25.0.1` via jenv |
| `brew` | OK | Homebrew `5.1.10` checked separately |

Follow-up:

- `brew install autoconf` succeeded on 2026-05-17.
- Preflight then passed for `git`, `bash`, `make`, `autoconf`, `clang`, Java
  `25.0.1`, and Homebrew.

Interpretation:

- The first prerequisite blocker is fixed.
- The Xcode/Metal blocker is now worked around by using an Xcode-derived
  devkit plus the mounted Metal Toolchain MobileAsset path.

## Baseline Smoke

Command:

```text
HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-smoke-20260517 \
HOTSPOT_RIFT_RECORDS=200000 \
experimental/hotspot-rift/scripts/run_baseline_smoke.sh
```

Result: passed on 2026-05-17 with escalation because `/usr/bin/time -l`
requires macOS `sysctl` access outside the sandbox.

Output:

`/private/tmp/rift-hotspot-smoke-20260517`

Row:

| Mode | Records | Epoch size | Active timestamps | Internal elapsed ms | Checksum | Output | External real s | Max RSS MB | GC pauses |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `heap-gc` | `200000` | `10000` | `16` | `6.392` | `1759552` | `200000` | `0.08` | `53.8` | `0` |

Interpretation:

- The HotSpot scaffold can compile and run a retained-object baseline workload
  on the stock JVM.
- This is only baseline harness evidence. It does not allocate objects into
  Rift regions.

## OpenJDK Baseline Build

Clone command:

```text
experimental/hotspot-rift/scripts/bootstrap_openjdk.sh
```

Result: passed on 2026-05-17.

OpenJDK worktree:

`/Users/siyaoliu/rift/cache/openjdk-rift`

Initial clone was `master` at:

`22b46872d0d647c9ef9f4414b4685afa8313926d`

That branch is JDK 27 and requires a boot JDK 26 or 27. The machine currently
has Java `25.0.1`, so the worktree was switched to a local branch:

```text
git -C cache/openjdk-rift checkout -B rift-jdk25 origin/jdk25
```

Current branch and commit:

```text
rift-jdk25
37f9d24dd561 Gate C2 under Rift regions
```

Patch 9 base commit:

```text
f5bcc3f9629 Add C1 Rift store guards
```

Patch 8 base commit:

```text
8cd8da1a443 Add C1 Rift region allocation path
```

Patch 7 base commit:

```text
c455daa9cef Add Rift verifyLive VM hook
```

Patch 1-6 base commit:

```text
94e2a36f7b9 Prototype Rift region backend
```

The local OpenJDK worktree is now pushed to the user fork:

```text
rift-github  git@github.com:641bill/jdk.git
branch       rift-jdk25 -> rift-github/rift-jdk25
```

`origin` still points at `https://github.com/openjdk/jdk.git` for upstream
OpenJDK. The same changes are also exported as parent-repo patch files under
`experimental/hotspot-rift/patches/**`.

Devkit command:

```text
experimental/hotspot-rift/scripts/create_macosx_devkit.sh
```

Result: passed on 2026-05-17.

Created devkit:

```text
/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode26.5-MacOSX26
```

The Xcode 26.5 `metal` executable is a stub unless the Metal Toolchain
MobileAsset is selected. The build script now auto-detects the mounted
MobileAsset path:

```text
/var/run/com.apple.security.cryptexd/mnt/com.apple.MobileAsset.MetalToolchain-v17.6.42.0.RyYM4f/Metal.xctoolchain/usr/bin
```

Build command:

```text
HOTSPOT_RIFT_DEVKIT=/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode26.5-MacOSX26 \
  experimental/hotspot-rift/scripts/build_openjdk.sh
```

Result: passed on 2026-05-17 with escalation because configure needs `sysctl`
and the build uses `/dev/fd`.

First configure attempt:

- branch: `master` / JDK 27;
- blocker: boot JDK must be 26 or 27, but installed boot JDK is `25.0.1`.

Earlier blocked configure attempts:

- branch: `rift-jdk25`;
- boot JDK: accepted, Java `25.0.1`;
- script updated to pass `--enable-headless-only`;
- blocker: OpenJDK configure still required working `metal`/`metallib`.

Observed active developer directory:

```text
/Library/Developer/CommandLineTools
```

Earlier observed error:

```text
XCode tool 'metal' neither found in path nor with xcrun
```

Built JDK:

```text
/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java
```

Version:

```text
openjdk version "25-internal" 2025-09-16
OpenJDK Runtime Environment (fastdebug build 25-internal-adhoc.siyaoliu.openjdk-rift)
OpenJDK 64-Bit Server VM (fastdebug build 25-internal-adhoc.siyaoliu.openjdk-rift, mixed mode)
```

Interpretation:

- The OpenJDK baseline source, devkit, and fastdebug image are now available
  locally.
- Patch 1-3 can now start from a validated fastdebug VM baseline, not more
  toolchain setup.

## Built-JDK Baseline Smoke

Command:

```text
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-smoke-built-20260517 \
experimental/hotspot-rift/scripts/run_baseline_smoke.sh
```

Result: passed on 2026-05-17 with escalation because `/usr/bin/time -l`
requires macOS `sysctl` access outside the sandbox.

Output:

```text
/private/tmp/rift-hotspot-smoke-built-20260517
```

Row:

| Mode | Records | Epoch size | Active timestamps | Internal elapsed ms | Checksum | Output | External real s | Max RSS MB | GC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `heap-gc` | `1000000` | `10000` | `16` | `88.406` | `7351360` | `1000000` | `0.60` | `151.8` | G1, no pause row in smoke log |

## Rift VM Patch 1-3 Smoke

Patch file:

```text
experimental/hotspot-rift/patches/01-rift-region-stubs.patch
```

OpenJDK worktree:

```text
/Users/siyaoliu/rift/cache/openjdk-rift
```

Implemented in the OpenJDK worktree:

- experimental `-XX:+UseRiftRegions` flag gated by
  `-XX:+UnlockExperimentalVMOptions`;
- internal Java test surface `jdk.internal.rift.RiftRegion`;
- native VM entrypoints for `open`, `enter`, `leave`, `close`, `current`,
  raw arena allocation, and stats;
- per-thread current Rift region state in `JavaThread`;
- active/closed handle checks and nested-region rejection;
- VM-owned raw bump/reset arena with high-water, open/close/reset, and
  allocation counters.

Important limitation:

- no ordinary Java object allocation is redirected yet;
- the raw arena is C-heap test memory, not an `oop` region space;
- `new` bytecodes and HotSpot allocation paths remain unchanged.

Build command:

```text
HOTSPOT_RIFT_DEVKIT=/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode26.5-MacOSX26 \
  experimental/hotspot-rift/scripts/build_openjdk.sh
```

Result: passed on 2026-05-17 after fixing VM/JNI thread-state handling in the
internal stats native.

Region smoke command:

```text
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-region-smoke-20260517 \
experimental/hotspot-rift/scripts/run_region_smoke.sh
```

Result:

```text
disabled-ok
enabled-ok
```

The smoke covers:

- flag-off use rejects with `UnsupportedOperationException`;
- flag-on open/enter/raw allocation/stats/leave/close lifecycle;
- nested-region rejection;
- inactive allocation rejection;
- closed-handle enter and double-close rejection;
- `epoch` convenience path with deterministic close/reset.

Flag-off built-JDK baseline after patch:

```text
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-smoke-after-rift-20260517 \
experimental/hotspot-rift/scripts/run_baseline_smoke.sh
```

Result: passed on 2026-05-17.

| Mode | Records | Epoch size | Active timestamps | Internal elapsed ms | Checksum | Output | External real s | Max RSS MB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `heap-gc` | `1000000` | `10000` | `16` | `109.222` | `7351360` | `1000000` | `0.82` | `150.2` |

Interpretation:

- Patch 1-3 prove the guarded VM control plane: flag, region handle lifecycle,
  thread-current region state, raw arena accounting, and flag-off behavior.
- This remains mechanism evidence only. It does not prove ordinary object
  allocation, GC integration, barrier safety, or performance.

## Rift VM Patch 4 Object Allocation Smoke

Patch file:

```text
experimental/hotspot-rift/patches/02-interpreter-object-allocation.patch
```

Implemented in the OpenJDK worktree:

- internal `RiftRegion.registerEligible(Class<?>)` test API;
- eligibility validation for final/simple classes with primitive instance
  fields only;
- interpreter `_new` hook that tries region allocation when
  `-XX:+UseRiftRegions` is enabled and the current Java thread has an active
  Rift region;
- fallback to normal heap allocation for unregistered classes in this
  prototype, so incidental JDK allocations inside active regions do not break
  the smoke;
- region object allocation counter in the stats array at index `12`;
- debug heap-membership hooks for this prototype so the interpreter can invoke
  methods on region oops.

Object smoke command:

```text
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-object-region-smoke-20260517 \
experimental/hotspot-rift/scripts/run_object_region_smoke.sh
```

First correctness flags used by the smoke:

```text
-Xint -XX:+UnlockExperimentalVMOptions -XX:+UseRiftRegions
-XX:+UseSerialGC -XX:-UseCompressedOops -XX:-UseCompactObjectHeaders
```

Result:

```text
object-enabled-ok
```

The smoke covers:

- `PrimitiveRecord` eligibility registration succeeds;
- reference-field and non-final classes reject at registration;
- `new PrimitiveRecord(7, 11, 3.5)` allocates one object in the active region;
- constructor execution and field stores produce checksum `21`;
- active stats show nonzero region bytes and one object allocation;
- close resets used bytes while retaining high-water/object-allocation stats;
- unregistered classes heap-fallback in the prototype and do not increment the
  region object allocation counter.

Regression smokes after Patch 4:

| Smoke | Output | Result |
|---|---|---|
| Region lifecycle | `/private/tmp/rift-hotspot-region-smoke-stable-20260517` | `disabled-ok`, `enabled-ok` |
| Object allocation | `/private/tmp/rift-hotspot-object-region-smoke-stable-20260517` | `object-enabled-ok` |
| Flag-off baseline | `/private/tmp/rift-hotspot-smoke-stable-after-object-20260517` | checksum `7351360`, output `1000000`, internal elapsed `89.707 ms`, external `0.66 s`, max RSS `158580736` bytes |

Interpretation:

- Patch 4 proves constructor-preserving redirection of a narrow `new` subset
  into a VM-owned Rift region in interpreter mode.
- It is mechanism evidence only. Region oops are not yet GC-scanned or barrier
  protected, so tests must avoid safepoints/GC while region objects are live
  and must not dereference region objects after close.
- Unregistered-class heap fallback is a prototype convenience, not the final
  safety policy for checked Rift lowering.

## Patch 5 Safety Probe And Store Guard

Attempted on 2026-05-17 and backed out before the stable checkpoint:

- close-time heap scanning with `Universe::heap()->object_iterate`;
- negative object-smoke tests for static, array, and heap-object retention of
  a region object.

Result:

- the VM rebuild succeeded, but the object smoke crashed during the normal
  close path before the negative tests could run;
- with compressed class pointers enabled, fastdebug failed in
  `compressedKlass.inline.hpp` while `RiftRegionHeapObjectClosure` was walking
  heap objects;
- with compressed class pointers disabled, the same close-time heap-iteration
  approach segfaulted in the verifier closure.

Interpretation:

- ordinary `object_iterate` from `RiftRegion.close` is not a valid safety
  mechanism; it can walk unparseable heap/TLAB state outside a safepoint and
  trips existing HotSpot assumptions before it can report a clean error;
- Patch 5 should use a real write/store barrier path or a safepoint VM
  operation, not an ad hoc close-time heap scan;
- the failed probe was removed from the current OpenJDK worktree, and the
  stable object/lifecycle smokes pass again.

Implemented after the failed scan:

Patch file:

```text
experimental/hotspot-rift/patches/03-interpreter-store-guard.patch
```

Implemented in the OpenJDK worktree:

- interpreter `do_oop_store` calls a Rift VM verifier before non-null oop
  stores;
- `RiftRegionRuntime::verify_oop_store` rejects storing a live region oop into
  non-region memory;
- interpreter `_new` is forced through the runtime allocation hook whenever
  `-XX:+UseRiftRegions` is enabled, so resolved classes do not bypass the
  region allocation hook via the normal TLAB fast path;
- object smoke negative tests now use direct bytecodes, not lambdas, for
  `putstatic`, `aastore`, and `putfield`.

Validation commands:

```text
HOTSPOT_RIFT_DEVKIT=/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode26.5-MacOSX26 \
  experimental/hotspot-rift/scripts/build_openjdk.sh

HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-object-region-smoke-patch5-slownew-20260517 \
  experimental/hotspot-rift/scripts/run_object_region_smoke.sh

HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-region-smoke-patch5-slownew-20260517 \
  experimental/hotspot-rift/scripts/run_region_smoke.sh

HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-smoke-patch5-slownew-20260517 \
  experimental/hotspot-rift/scripts/run_baseline_smoke.sh
```

Validation results:

| Smoke | Output | Result |
|---|---|---|
| Object allocation + store guard | `/private/tmp/rift-hotspot-object-region-smoke-patch5-slownew-20260517` | `object-enabled-ok` |
| Region lifecycle | `/private/tmp/rift-hotspot-region-smoke-patch5-slownew-20260517` | `disabled-ok`, `enabled-ok` |
| Flag-off baseline | `/private/tmp/rift-hotspot-smoke-patch5-slownew-20260517` | checksum `7351360`, output `1000000`, internal elapsed `123.329 ms`, external `0.47 s`, max RSS `158171136` bytes |
| Stable rebuild after stale-use experiment backout | `/private/tmp/rift-hotspot-object-region-smoke-stable-after-stale-backout-20260517` | `object-enabled-ok` |
| Stable lifecycle after stale-use experiment backout | `/private/tmp/rift-hotspot-region-smoke-stable-after-stale-backout-20260517` | `disabled-ok`, `enabled-ok` |
| Stable flag-off baseline after stale-use experiment backout | `/private/tmp/rift-hotspot-smoke-stable-after-stale-backout-20260517` | checksum `7351360`, output `1000000`, internal elapsed `126.743 ms`, external `0.48 s`, max RSS `158973952` bytes |
| Generic/container hiding smoke | `/private/tmp/rift-hotspot-object-region-smoke-generic-container-20260517` | `object-enabled-ok` |

Patch 5 smoke coverage:

- registered final primitive-field objects allocate in the active VM region in
  interpreter mode;
- constructor execution and primitive field stores still preserve the checksum;
- unregistered classes still heap-fallback in this prototype;
- storing a live region object into a static field is rejected;
- storing a live region object into an object array is rejected;
- storing a live region object into a heap object field is rejected.
- storing a widened region object through a generic heap cell is rejected;
- storing a live region object into `ArrayList`'s heap backing storage is
  rejected in interpreter mode.

Patch 5 limitations:

- the guard is interpreter-only and currently implemented on AArch64 template
  interpreter oop-store paths;
- C1/C2, native stores outside the guarded entrypoints, and compiled fast
  allocation paths are not covered;
- forcing `_new` through the runtime hook under `-XX:+UseRiftRegions` is a
  correctness-first prototype choice, not a performance policy;
- region objects are still not GC-scanned, so performance and broad safety
  claims remain out of scope;
- stale post-close object use and supported region-to-heap bridge rules remain
  future work.

Stale-use experiment:

- A follow-up attempt added a `rift_oop_use` VM guard from the AArch64
  interpreter receiver-load path in `TemplateTable::prepare_invoke`.
- The VM rebuilt, but normal bootstrap/invoke execution crashed before the
  smoke body ran. The first crash corrupted the interpreter return-state
  selection; saving the obvious return-state register still left crashes in
  `Klass::external_name()` while throwing an invoke-related VM error.
- The invoke-load hook was backed out. The stable Patch 5 store-guard worktree
  was rebuilt and the object/lifecycle/baseline smokes above passed.

Interpretation:

- stale post-close use needs a less invasive design than calling into the VM
  from every interpreter receiver load;
- candidate designs are a dedicated checked bytecode/helper emitted only by
  Rift lowering, a debug-only verifier at explicit region API boundaries, or a
  deeper barrier/deoptimization strategy after GC/safepoint integration;
- the current accepted Patch 5 scope remains heap-retention rejection, not
  post-close use rejection.

## Patch 6: Unsafe/JNI Store Guards

Patch file:

`experimental/hotspot-rift/patches/04-unsafe-jni-store-guard.patch`

Implementation:

- `Unsafe.putReference` and `Unsafe.putReferenceVolatile` now call
  `RiftRegionRuntime::verify_oop_store` before storing;
- JNI `SetObjectField` and JNI `SetStaticObjectField` now call the same
  verifier before storing;
- the object-region smoke now tests reflective `Field.set`,
  `Unsafe.putReference`, `MethodHandle` setter, and anonymous closure capture
  retention attempts.

Pre-patch finding:

- Extending the smoke first showed that reflective `Field.set` could store a
  live Rift region object into a heap holder. The Java assertion then left the
  illegal heap-to-region reference live, and fastdebug verification aborted
  because the heap contained an oop outside the Java heap. This is the exact
  safety hole Patch 6 closes for the reflected/Unsafe route.

Validation commands:

```text
HOTSPOT_RIFT_DEVKIT=/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode26.5-MacOSX26 \
  experimental/hotspot-rift/scripts/build_openjdk.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-object-region-smoke-patch6c-20260517 \
  experimental/hotspot-rift/scripts/run_object_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-region-smoke-patch6b-20260517 \
  experimental/hotspot-rift/scripts/run_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-smoke-patch6-20260517 \
  experimental/hotspot-rift/scripts/run_baseline_smoke.sh
```

Validation results:

| Smoke | Output | Result |
|---|---|---|
| Object allocation + interpreter/Unsafe/JNI store guards | `/private/tmp/rift-hotspot-object-region-smoke-patch6c-20260517` | `object-enabled-ok` |
| Region lifecycle | `/private/tmp/rift-hotspot-region-smoke-patch6b-20260517` | `disabled-ok`, `enabled-ok` |
| Flag-off baseline | `/private/tmp/rift-hotspot-smoke-patch6-20260517` | checksum `7351360`, output `1000000`, internal elapsed `11.938 ms`, external `0.10 s`, max RSS `88489984` bytes |

Patch 6 smoke coverage:

- registered final primitive-field objects allocate in the active VM region in
  interpreter mode;
- direct `putstatic`, `aastore`, and `putfield` heap retention is rejected;
- widened generic-cell retention and `ArrayList.add` retention are rejected;
- reflective `Field.set` retention is rejected through the Unsafe/JNI guarded
  path;
- direct reflective access to `jdk.internal.misc.Unsafe.putReference` retention
  is rejected;
- `MethodHandle` setter retention is rejected in the current `-Xint` smoke;
- anonymous closure capture of a live region object is rejected in the current
  `-Xint` smoke.

Patch 6 limitations:

- C1/C2 compiled stores are not covered;
- native code that stores object references outside the guarded Unsafe/JNI
  entrypoints is not covered;
- region object arrays, reference fields inside region objects, and
  region-to-heap bridge/root rules are still unsupported;
- stale post-close object use is still unsupported;
- region oops are still not GC-scanned, so performance and broad safety claims
  remain out of scope.

## Patch 7: Explicit Live Verifier

Patch file:

`experimental/hotspot-rift/patches/05-explicit-verify-live.patch`

Implementation:

- `jdk.internal.rift.RiftRegion.verifyLive(Object)` now exposes an internal VM
  test/API-boundary verifier;
- `RiftRegionRuntime::verify_live_oop` rejects objects whose address belongs
  to a closed Rift region;
- closed region address ranges are remembered after close/reset so explicit
  verification and store guards can identify stale region objects;
- region lookup now prefers active ranges before remembered closed ranges,
  avoiding false stale matches when the C heap reuses an old region address;
- `verify_oop_store` uses the known-range lookup, so heap stores of closed
  region objects are rejected along with live region objects.

Pre-patch finding:

- The first closed-range lookup tried for Patch 7 could falsely reject an
  active region object because `malloc` reused an address range from a previous
  closed region. The accepted implementation uses a two-pass lookup: active
  regions first, then closed remembered ranges only if no active region owns
  the address.

Validation commands:

```text
HOTSPOT_RIFT_DEVKIT=/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode26.5-MacOSX26 \
  experimental/hotspot-rift/scripts/build_openjdk.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-object-region-smoke-patch7c-20260517 \
  experimental/hotspot-rift/scripts/run_object_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-region-smoke-patch7c-20260517 \
  experimental/hotspot-rift/scripts/run_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-smoke-patch7c-20260517 \
  experimental/hotspot-rift/scripts/run_baseline_smoke.sh
```

Validation results:

| Smoke | Output | Result |
|---|---|---|
| Object allocation + explicit live verifier | `/private/tmp/rift-hotspot-object-region-smoke-patch7c-20260517` | `object-enabled-ok` |
| Region lifecycle | `/private/tmp/rift-hotspot-region-smoke-patch7c-20260517` | `disabled-ok`, `enabled-ok` |
| Flag-off baseline | `/private/tmp/rift-hotspot-smoke-patch7c-20260517` | checksum `7351360`, output `1000000`, internal elapsed `12.636 ms`, external `0.11 s`, max RSS `88653824` bytes |

Patch 7 smoke coverage:

- active region objects pass `RiftRegion.verifyLive`;
- after close, the same region object is rejected by `verifyLive` when held in
  a Java local variable;
- the smoke avoids storing that stale object in heap state, because the Patch
  5/6 store guards correctly reject heap retention first;
- unregistered heap objects and `null` pass `verifyLive`.

Patch 7 limitations:

- `verifyLive` is explicit. It is suitable for Rift-lowered API boundaries and
  VM tests, but it is not an automatic arbitrary object-use barrier;
- closed address-range memory can still be reused by the C allocator. The
  active-first lookup avoids active-region false positives, but this remains a
  prototype mechanism until region memory is integrated with a VM-managed
  address space and GC/safepoints;
- C1/C2 compiled stores, native stores outside guarded Unsafe/JNI entrypoints,
  GC scanning, arrays, reference fields, and bridge/root rules remain future
  work.

## Patch 8: C1 Region Allocation

Patch file:

`experimental/hotspot-rift/patches/06-c1-region-allocation.patch`

Implementation:

- C1 disables inline fast allocation while `-XX:+UseRiftRegions` is enabled;
- C1 `new` bytecodes route through the existing `Runtime1::new_instance` stub;
- `Runtime1::new_instance` asks `RiftRegionRuntime::allocate_instance` first
  when the Java thread has an active Rift region;
- unregistered or unsupported classes still fall back to normal heap
  allocation in this prototype;
- added `RiftHotSpotC1RegionAllocationSmoke` and
  `experimental/hotspot-rift/scripts/run_c1_object_region_smoke.sh`.

Validation commands:

```text
HOTSPOT_RIFT_DEVKIT=/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode26.5-MacOSX26 \
  experimental/hotspot-rift/scripts/build_openjdk.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-c1-region-smoke-patch8-20260517 \
  experimental/hotspot-rift/scripts/run_c1_object_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-object-region-smoke-patch8-20260517 \
  experimental/hotspot-rift/scripts/run_object_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-region-smoke-patch8-20260517 \
  experimental/hotspot-rift/scripts/run_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-smoke-patch8-20260517 \
  experimental/hotspot-rift/scripts/run_baseline_smoke.sh
```

Validation results:

| Smoke | Output | Result |
|---|---|---|
| C1 region allocation | `/private/tmp/rift-hotspot-c1-region-smoke-patch8-20260517` | `c1-allocation-ok` |
| Interpreter object allocation + safety subset | `/private/tmp/rift-hotspot-object-region-smoke-patch8-20260517` | `object-enabled-ok` |
| Region lifecycle | `/private/tmp/rift-hotspot-region-smoke-patch8-20260517` | `disabled-ok`, `enabled-ok` |
| Flag-off baseline | `/private/tmp/rift-hotspot-smoke-patch8-20260517` | checksum `7351360`, output `1000000`, internal elapsed `12.124 ms`, external `0.10 s`, max RSS `88752128` bytes |

Patch 8 smoke coverage:

- the `allocateOne` helper is warmed and then run with C1-only compilation
  settings;
- inside an active Rift region, `10000` registered final primitive-field
  records allocate through C1 into region memory;
- active records pass `RiftRegion.verifyLive`;
- region stats report `10000` object allocations and nonzero used bytes.

Patch 8 limitations:

- this is a correctness-first C1 route and disables C1 inline fast allocation
  under `UseRiftRegions`;
- C1 compiled stores are not guarded yet;
- C2 allocation and C2 compiled stores are not covered;
- GC/safepoint integration remains absent, so no JVM performance claim should
  be made from this patch.

## Patch 9: C1 Compiled Store Guards

Patch file:

`experimental/hotspot-rift/patches/07-c1-store-guards.patch`

Implementation:

- C1 `StoreField` and object `StoreIndexed` generation inserts a runtime-stub
  call before the actual reference store while `-XX:+UseRiftRegions` is
  enabled;
- the stub receives the stored value and destination base object;
- `RiftRegionRuntime::verify_oop_store_to_base` rejects storing a live or
  closed Rift region object into an ordinary heap base;
- stores into a live Rift region base are allowed by this local check, although
  reference fields remain outside the supported region-object subset;
- added `RiftHotSpotC1StoreGuardSmoke` and
  `experimental/hotspot-rift/scripts/run_c1_store_guard_smoke.sh`.

False start:

- The first implementation called the C++ runtime function directly from C1
  LIR. Fastdebug asserted because the call did not use the expected C1
  runtime-stub JavaThread convention. The accepted implementation adds a real
  C1 stub id and AArch64 stub entry before calling the VM runtime function.

Validation commands:

```text
HOTSPOT_RIFT_DEVKIT=/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode26.5-MacOSX26 \
  experimental/hotspot-rift/scripts/build_openjdk.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-c1-store-guard-smoke-patch9c-20260517 \
  experimental/hotspot-rift/scripts/run_c1_store_guard_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-c1-region-smoke-patch9-20260517 \
  experimental/hotspot-rift/scripts/run_c1_object_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-object-region-smoke-patch9-20260517 \
  experimental/hotspot-rift/scripts/run_object_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-region-smoke-patch9-20260517 \
  experimental/hotspot-rift/scripts/run_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-smoke-patch9-20260517 \
  experimental/hotspot-rift/scripts/run_baseline_smoke.sh
```

Validation results:

| Smoke | Output | Result |
|---|---|---|
| C1 compiled store guard | `/private/tmp/rift-hotspot-c1-store-guard-smoke-patch9c-20260517` | `c1-store-guard-ok` |
| C1 region allocation | `/private/tmp/rift-hotspot-c1-region-smoke-patch9-20260517` | `c1-allocation-ok` |
| Interpreter object allocation + safety subset | `/private/tmp/rift-hotspot-object-region-smoke-patch9-20260517` | `object-enabled-ok` |
| Region lifecycle | `/private/tmp/rift-hotspot-region-smoke-patch9-20260517` | `disabled-ok`, `enabled-ok` |
| Flag-off baseline | `/private/tmp/rift-hotspot-smoke-patch9-20260517` | checksum `7351360`, output `1000000`, internal elapsed `12.467 ms`, external `0.11 s`, max RSS `88670208` bytes |

Patch 9 smoke coverage:

- C1-compiled `putstatic` rejects storing a live region object into static
  heap state;
- C1-compiled `putfield` rejects storing a live region object into a heap
  holder object;
- C1-compiled `aastore` rejects storing a live region object into a heap object
  array;
- the test deliberately avoids closure/lambda capture of the region object so
  the compiled store paths are the operation being tested.

Patch 9 limitations:

- C2 allocation and C2 compiled stores are not covered;
- native stores outside the current Unsafe/JNI entrypoints are not covered;
- region object reference fields and region arrays are not supported;
- GC/safepoint integration is still absent, so no JVM performance claim should
  be made from this patch.

## Patch 10: C2/JVMCI Safety Gate

Patch file:

`experimental/hotspot-rift/patches/08-c2-safety-gate.patch`

Implementation:

- `CompileBroker::compile_method` returns without compiling when
  `-XX:+UseRiftRegions` is enabled and the selected compiler is C2 or JVMCI;
- C1 and interpreter execution remain available for the current supported
  region allocation and store-guard subset;
- added `experimental/hotspot-rift/scripts/run_c2_gate_smoke.sh`.

Interpretation:

- This is a safety gate, not a C2 implementation. It prevents unsupported
  C2/JVMCI allocation and store paths from silently bypassing the prototype's
  C1/interpreter checks while Rift regions are enabled.

Validation commands:

```text
HOTSPOT_RIFT_DEVKIT=/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode26.5-MacOSX26 \
  experimental/hotspot-rift/scripts/build_openjdk.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-c2-gate-smoke-patch10-20260517 \
  experimental/hotspot-rift/scripts/run_c2_gate_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-c1-store-guard-smoke-patch10-20260517 \
  experimental/hotspot-rift/scripts/run_c1_store_guard_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-c1-region-smoke-patch10-20260517 \
  experimental/hotspot-rift/scripts/run_c1_object_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-object-region-smoke-patch10-20260517 \
  experimental/hotspot-rift/scripts/run_object_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-region-smoke-patch10-20260517 \
  experimental/hotspot-rift/scripts/run_region_smoke.sh

HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-smoke-patch10-20260517 \
  experimental/hotspot-rift/scripts/run_baseline_smoke.sh
```

Validation results:

| Smoke | Output | Result |
|---|---|---|
| C2/JVMCI safety gate | `/private/tmp/rift-hotspot-c2-gate-smoke-patch10-20260517` | `c2-gate-ok` |
| C1 compiled store guard | `/private/tmp/rift-hotspot-c1-store-guard-smoke-patch10-20260517` | `c1-store-guard-ok` |
| C1 region allocation | `/private/tmp/rift-hotspot-c1-region-smoke-patch10-20260517` | `c1-allocation-ok` |
| Interpreter object allocation + safety subset | `/private/tmp/rift-hotspot-object-region-smoke-patch10-20260517` | `object-enabled-ok` |
| Region lifecycle | `/private/tmp/rift-hotspot-region-smoke-patch10-20260517` | `disabled-ok`, `enabled-ok` |
| Flag-off baseline | `/private/tmp/rift-hotspot-smoke-patch10-20260517` | checksum `7351360`, output `1000000`, internal elapsed `11.123 ms`, external `0.08 s`, max RSS `88440832` bytes |

Patch 10 smoke coverage:

- tiered compilation is enabled with `TieredStopAtLevel=4`;
- compile commands request compilation of the C1 allocation and store-guard
  smoke methods;
- C2/JVMCI requests are rejected by the VM gate, and the supported C1/runtime
  subset still executes correctly.

Patch 10 limitations:

- no C2 region allocation exists yet;
- no C2 store barrier exists yet;
- no GC/safepoint integration is added by this patch;
- performance claims remain out of scope.

## Safepoint/GC Probe

Probe files:

- `experimental/hotspot-rift/tests/java/RiftHotSpotSafepointProbe.java`
- `experimental/hotspot-rift/scripts/run_safepoint_probe.sh`

Purpose:

- separate plain safepoint behavior from explicit GC behavior for a live
  registered primitive-field region object;
- keep explicit-GC failure as characterization evidence instead of treating it
  as a passing regression smoke.

Command:

```text
HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-safepoint-probe-patch10-20260517 \
  experimental/hotspot-rift/scripts/run_safepoint_probe.sh
```

Result:

| Probe | Output | Result |
|---|---|---|
| Plain safepoint-only | `/private/tmp/rift-hotspot-safepoint-probe-patch10-20260517/safepoint.out` | `safepoint-probe-ok` |
| Explicit `System.gc()` | `/private/tmp/rift-hotspot-safepoint-probe-patch10-20260517/system-gc.out` | process abort, status `134` |

Observed explicit-GC failure:

```text
Internal Error (.../compressedOops.inline.hpp:87)
assert(Universe::is_in_heap(v)) failed: object not in heap 0x0000000bb703d410
```

Interpretation:

- active region objects can still be used across a simple safepoint-only path
  in the narrow interpreter subset;
- GC root processing/verification still assumes root oops point into the Java
  heap, so region oops are not yet safe across explicit GC;
- this makes GC/safepoint integration the next correctness blocker before
  broad JVM safety, true C2 support, or performance claims.

## Next Required Step

1. Design and prototype GC/safepoint root handling for active region objects.
   Patch 10 only gates C2; it does not make region oops acceptable to GC root
   processing.
2. Decide the first supported bridge/root rule for JVM region-to-heap
   references before allowing reference fields.
3. Add GC/safepoint integration before any region object may survive a
   safepoint in a broader program.
4. Keep compressed oops, compact object headers, broad C2 support, and
   performance claims out of scope until the safety story covers more than the
   current interpreter/C1 subset.
