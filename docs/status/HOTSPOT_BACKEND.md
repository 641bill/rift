# HotSpot Backend Status

Last updated: 2026-05-17 22:31 CEST

Status: hot status file for the custom HotSpot VM-fork track. This is separate
from the portable JVM library prototype.

## Ownership

HotSpot backend work owns:

- `experimental/hotspot-rift/**`;
- `docs/HOTSPOT_REGION_BACKEND_PLAN.md`;
- HotSpot-specific evidence files.

HotSpot backend work should not edit:

- `scala-native-rift/nativelib/**`;
- `scala-native-rift/nscplugin/**`;
- `scala-native-rift/sandbox/**`;
- `scala-native-rift/experimental/portable-rift/**`, unless the change is a
  shared API/test harness update.

## Branch Discipline

This status file is backend-owned and may be updated on the
`backend-portability` branch. To avoid conflicts with the Scala Native
benchmark/report lane on `main`, HotSpot work should stay in:

- `docs/HOTSPOT_REGION_BACKEND_PLAN.md`;
- `docs/status/HOTSPOT_BACKEND.md`;
- `evidence/HOTSPOT_REGION_BACKEND_STATUS.md`;
- `experimental/hotspot-rift/**`.

Do not edit these global presentation files from backend work unless the
change is intentionally promoted as thesis-facing context:

- `docs/PERFORMANCE_EVALUATION_REPORT.md`;
- `docs/report.html`;
- `evidence/EVALUATION_CLASSIFIED_SUMMARY.md`.

Shared status files such as `docs/HANDOFF.md`, `docs/ROADMAP.md`, and
`docs/status/CURRENT.md` should only receive short pointer updates from
`main`, for example a branch name, backend status file path, and commit SHA.
Detailed HotSpot progress belongs here and in
`evidence/HOTSPOT_REGION_BACKEND_STATUS.md`.

## Current State

- A VM-fork roadmap exists in `docs/HOTSPOT_REGION_BACKEND_PLAN.md`.
- The HotSpot experiment scaffold exists under `experimental/hotspot-rift/**`.
- Patch 1-3 VM control-plane stubs now exist in the OpenJDK worktree and are
  exported as `experimental/hotspot-rift/patches/01-rift-region-stubs.patch`.
- Patch 4 interpreter-only ordinary-object allocation is implemented and
  exported as
  `experimental/hotspot-rift/patches/02-interpreter-object-allocation.patch`.
  It redirects `new` into region memory only for explicitly registered,
  eligible final primitive-field classes under an active Rift region.
- Patch 5 interpreter store-guard safety is implemented and exported as
  `experimental/hotspot-rift/patches/03-interpreter-store-guard.patch`.
  It forces interpreter `new` through the runtime allocation hook when
  `-XX:+UseRiftRegions` is enabled, then rejects interpreter oop stores of a
  live region object into non-region memory. The object smoke now rejects
  static field, object-array, and heap-object-field retention of a region
  object.
- Patch 6 Unsafe/JNI store-guard safety is implemented and exported as
  `experimental/hotspot-rift/patches/04-unsafe-jni-store-guard.patch`.
  It guards `Unsafe.putReference`, `Unsafe.putReferenceVolatile`, JNI
  `SetObjectField`, and JNI `SetStaticObjectField`. This closes the first
  reflective `Field.set` retention hole found by the extended object smoke.
- Patch 7 explicit live verification is implemented and exported as
  `experimental/hotspot-rift/patches/05-explicit-verify-live.patch`.
  It adds the internal `RiftRegion.verifyLive(Object)` test/API-boundary hook,
  remembers closed region address ranges, rejects closed region objects through
  explicit verification and store guards, and prefers active ranges before
  closed ranges to avoid C-heap address-reuse false positives.
- `autoconf` was installed with Homebrew and preflight now passes for `git`,
  `bash`, `make`, `autoconf`, `clang`, Java `25.0.1`, and Homebrew.
- OpenJDK was cloned into `/Users/siyaoliu/rift/cache/openjdk-rift`.
- The worktree is on local branch `rift-jdk25` from `origin/jdk25`. The Rift
  patch stack is currently OpenJDK commit `c455daa9cef` (`Add Rift verifyLive
  VM hook`), with the Patch 1-6 base at `94e2a36f7b9` (`Prototype Rift region
  backend`).
  It is pushed to the user fork remote
  `git@github.com:641bill/jdk.git` as branch `rift-jdk25`, tracking
  `rift-github/rift-jdk25`. `origin` remains
  `https://github.com/openjdk/jdk.git` for upstream OpenJDK.
- Added an Xcode-derived devkit workflow:
  `experimental/hotspot-rift/scripts/create_macosx_devkit.sh` creates an
  OpenJDK macOS devkit from a local `Xcode.app`, and
  `experimental/hotspot-rift/scripts/build_openjdk.sh` accepts
  `HOTSPOT_RIFT_DEVKIT=/path/to/devkit`.
- Xcode 26.5 is now installed at `/Applications/Xcode.app` and selected as
  the active developer directory.
- The usable Metal Toolchain is mounted as a MobileAsset under
  `/var/run/com.apple.security.cryptexd/mnt/com.apple.MobileAsset.MetalToolchain-*`.
  The HotSpot build script now auto-detects `Metal.xctoolchain/usr/bin` and
  prepends it with `--with-toolchain-path`, so OpenJDK configure finds working
  `metal` and `metallib` before the Xcode stub.
- An Xcode-derived OpenJDK devkit was created:
  `/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode26.5-MacOSX26`.
  The devkit directory is about `5.8G`; the tarball is about `1.7G`.
- OpenJDK fastdebug `images` built successfully with the devkit and mounted
  Metal Toolchain. Built JDK:
  `/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java`.
- Built-JDK retained-object baseline smoke passed at
  `/private/tmp/rift-hotspot-smoke-built-20260517`: `heap-gc`, `1000000`
  records, internal elapsed `88.406 ms`, checksum `7351360`, output
  `1000000`, external `0.60 s` real, max RSS `159219712` bytes, using G1.
- Rift region smoke passed at `/private/tmp/rift-hotspot-region-smoke-20260517`:
  flag-off use rejects as expected, and flag-on open/enter/raw allocation/stats
  /leave/close lifecycle prints `enabled-ok`.
- Patch 4 object-region smoke passed at
  `/private/tmp/rift-hotspot-object-region-smoke-stable-20260517`:
  `RiftRegion.registerEligible(PrimitiveRecord.class)` succeeds,
  reference-field and non-final classes reject, `new PrimitiveRecord(...)`
  allocates one object in the active region, constructor/field stores preserve
  the checksum, close resets used bytes, and unregistered classes heap-fallback
  with zero region object allocations.
- Existing region smoke still passed after Patch 4 at
  `/private/tmp/rift-hotspot-region-smoke-stable-20260517`.
- A first Patch 5 idea, close-time whole-heap scanning with
  `Universe::heap()->object_iterate`, was tried and backed out. It crashed
  during ordinary close because that heap walk is not safe from the close path
  outside a safepoint. The accepted Patch 5 path now uses an interpreter
  oop-store guard instead.
- Flag-off built-JDK baseline smoke after the VM patch passed at
  `/private/tmp/rift-hotspot-smoke-after-rift-20260517`: `heap-gc`,
  `1000000` records, internal elapsed `109.222 ms`, checksum `7351360`,
  output `1000000`, external `0.82 s` real, max RSS `157515776` bytes.
- Flag-off built-JDK baseline smoke after Patch 4 passed at
  `/private/tmp/rift-hotspot-smoke-stable-after-object-20260517`: `heap-gc`,
  `1000000` records, internal elapsed `89.707 ms`, checksum `7351360`,
  output `1000000`, external `0.66 s` real, max RSS `158580736` bytes.
- Patch 5 object-region smoke passed at
  `/private/tmp/rift-hotspot-object-region-smoke-patch5-slownew-20260517`:
  `object-enabled-ok`, including direct `putstatic`, `aastore`, and
  `putfield` rejection tests for live region objects.
- Existing region smoke still passed after Patch 5 at
  `/private/tmp/rift-hotspot-region-smoke-patch5-slownew-20260517`.
- Flag-off built-JDK baseline smoke after Patch 5 passed at
  `/private/tmp/rift-hotspot-smoke-patch5-slownew-20260517`: `heap-gc`,
  `1000000` records, internal elapsed `123.329 ms`, checksum `7351360`,
  output `1000000`, external `0.47 s` real, max RSS `158171136` bytes.
- A stale post-close use experiment that called a VM verifier from the
  AArch64 interpreter receiver-load path was tried and backed out. It rebuilt,
  but crashed normal bootstrap/invoke execution before the smoke body ran.
  Stable object/lifecycle/baseline smokes passed again after backing it out:
  `/private/tmp/rift-hotspot-object-region-smoke-stable-after-stale-backout-20260517`,
  `/private/tmp/rift-hotspot-region-smoke-stable-after-stale-backout-20260517`,
  and `/private/tmp/rift-hotspot-smoke-stable-after-stale-backout-20260517`.
- Generic/container hiding smoke passed at
  `/private/tmp/rift-hotspot-object-region-smoke-generic-container-20260517`.
  The interpreter store guard rejects a region object widened to `Object` and
  stored through a generic heap cell, and rejects `ArrayList.add` retention in
  the current `-Xint` subset.
- Patch 6 object smoke passed at
  `/private/tmp/rift-hotspot-object-region-smoke-patch6c-20260517` with
  `object-enabled-ok`. The smoke now rejects reflective `Field.set`,
  `Unsafe.putReference`, `MethodHandle` setter, and anonymous closure capture
  retention attempts in addition to the Patch 5 direct/generic/container
  cases.
- Existing region lifecycle smoke passed after Patch 6 at
  `/private/tmp/rift-hotspot-region-smoke-patch6b-20260517`.
- Flag-off built-JDK baseline smoke after Patch 6 passed at
  `/private/tmp/rift-hotspot-smoke-patch6-20260517`: checksum `7351360`,
  output `1000000`, internal elapsed `11.938 ms`, external `0.10 s` real,
  max RSS `88489984` bytes.
- Patch 7 object smoke passed at
  `/private/tmp/rift-hotspot-object-region-smoke-patch7c-20260517` with
  `object-enabled-ok`. The smoke now verifies an active region object, closes
  the region, and then confirms `verifyLive` rejects the stale object when it
  is held only in a Java local variable.
- Existing region lifecycle smoke passed after Patch 7 at
  `/private/tmp/rift-hotspot-region-smoke-patch7c-20260517`.
- Flag-off built-JDK baseline smoke after Patch 7 passed at
  `/private/tmp/rift-hotspot-smoke-patch7c-20260517`: checksum `7351360`,
  output `1000000`, internal elapsed `12.636 ms`, external `0.11 s` real,
  max RSS `88653824` bytes.
- Stock-JDK retained-object baseline smoke passed at
  `/private/tmp/rift-hotspot-smoke-20260517`.

## Next Step

Extend the safety work beyond the current Patch 7 interpreter plus Unsafe/JNI
and explicit API-boundary subset. The next work should cover C1/C2 compiled
stores, native stores outside the guarded Unsafe/JNI entrypoints, explicit JVM
bridge/root rules before allowing reference fields, and GC/safepoint
integration. Automatic stale post-close use remains open: Patch 7 gives an
explicit verifier that Rift lowering can call, not a general object-use
barrier. Performance claims remain out of scope until GC/safepoint integration
is designed.
