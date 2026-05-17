# HotSpot Rift Experiment

Last updated: 2026-05-17 23:57 CEST

Status: scaffold and exported Patch 1-10 artifacts for the custom HotSpot
VM-fork backend. This directory does not contain an OpenJDK checkout. It
contains the scripts, patch notes, exported patches, and smoke tests used to
create and validate one.

## Goal

Prototype ordinary JVM object allocation into VM-known Rift regions. This is
separate from the portable JVM library backend, which uses object pools and
heap fallback.

## Directory Layout

| Path | Purpose |
|---|---|
| `scripts/check_prereqs.sh` | Local prerequisite preflight. Does not clone or build. |
| `scripts/bootstrap_openjdk.sh` | Clone an OpenJDK worktree for the HotSpot fork. |
| `scripts/create_macosx_devkit.sh` | Create an OpenJDK macOS devkit from a local `Xcode.app`. |
| `scripts/build_openjdk.sh` | Configure and build a fastdebug JDK from that worktree. |
| `scripts/run_baseline_smoke.sh` | Run the Java smoke workload on a selected JDK. |
| `scripts/run_region_smoke.sh` | Run active/closed handle and raw arena lifecycle smoke. |
| `scripts/run_object_region_smoke.sh` | Run ordinary-object allocation and heap-retention rejection smoke. |
| `scripts/run_c1_object_region_smoke.sh` | Run the conservative C1 region-allocation smoke. |
| `scripts/run_c1_store_guard_smoke.sh` | Run the conservative C1 compiled-store guard smoke. |
| `scripts/run_c2_gate_smoke.sh` | Run the conservative C2/JVMCI safety-gate smoke. |
| `scripts/run_safepoint_probe.sh` | Probe safepoint-only and explicit-GC behavior for live region objects. |
| `tests/java/RiftHotSpotBaselineSmoke.java` | Baseline retained-object workload for stock/patched JDKs. |
| `tests/java/RiftHotSpotRegionSmoke.java` | Region lifecycle smoke. |
| `tests/java/RiftHotSpotObjectRegionSmoke.java` | Object-region allocation and store-guard smoke. |
| `tests/java/RiftHotSpotC1RegionAllocationSmoke.java` | C1 allocation smoke for registered primitive-field records. |
| `tests/java/RiftHotSpotC1StoreGuardSmoke.java` | C1 `putstatic`/`putfield`/`aastore` store-guard smoke. |
| `tests/java/RiftHotSpotSafepointProbe.java` | Safepoint/GC probe for live registered region objects. |
| `patches/README.md` | First HotSpot patch roadmap. |

## Default Locations

Scripts default to:

- OpenJDK source: `/Users/siyaoliu/rift/cache/openjdk-rift`
- Build name: `rift-fastdebug`
- Smoke output: `/private/tmp/rift-hotspot-smoke`
- Optional Xcode app: `/Applications/Xcode.app`
- Optional devkit: set `HOTSPOT_RIFT_DEVKIT=/path/to/devkit`

Override with:

```sh
HOTSPOT_RIFT_OPENJDK_DIR=/path/to/jdk \
HOTSPOT_RIFT_BUILD_NAME=rift-fastdebug \
HOTSPOT_RIFT_OUT_DIR=/private/tmp/rift-hotspot-smoke
```

## Commands

Preflight:

```sh
experimental/hotspot-rift/scripts/check_prereqs.sh
```

Clone OpenJDK:

```sh
experimental/hotspot-rift/scripts/bootstrap_openjdk.sh
```

Build fastdebug JDK:

```sh
experimental/hotspot-rift/scripts/build_openjdk.sh
```

Create an Xcode-derived OpenJDK devkit, then build from that devkit:

```sh
experimental/hotspot-rift/scripts/create_macosx_devkit.sh
HOTSPOT_RIFT_DEVKIT=/Users/siyaoliu/rift/cache/openjdk-rift/build/devkit/Xcode... \
  experimental/hotspot-rift/scripts/build_openjdk.sh
```

Current macOS note: Xcode 26.5 is installed and the OpenJDK devkit build works
by combining the Xcode-derived devkit with the mounted Metal Toolchain
MobileAsset. The build script auto-detects the mounted
`Metal.xctoolchain/usr/bin` path and prepends it with `--with-toolchain-path`.

If the MobileAsset path disappears after reboot, rerun:

```sh
sudo xcodebuild -runFirstLaunch
xcodebuild -downloadComponent MetalToolchain
xcrun -sdk macosx --find metallib
```

Then rerun the devkit/build commands.

Run baseline smoke with the current `java`:

```sh
experimental/hotspot-rift/scripts/run_baseline_smoke.sh
```

Run baseline smoke with a built JDK:

```sh
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
  experimental/hotspot-rift/scripts/run_baseline_smoke.sh
```

Run object-region smoke with a built JDK:

```sh
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
  experimental/hotspot-rift/scripts/run_object_region_smoke.sh
```

Run C1 allocation smoke with a built JDK:

```sh
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
  experimental/hotspot-rift/scripts/run_c1_object_region_smoke.sh
```

Run C1 store-guard smoke with a built JDK:

```sh
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
  experimental/hotspot-rift/scripts/run_c1_store_guard_smoke.sh
```

Run C2/JVMCI safety-gate smoke with a built JDK:

```sh
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
  experimental/hotspot-rift/scripts/run_c2_gate_smoke.sh
```

Run safepoint/GC probe with a built JDK:

```sh
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
  experimental/hotspot-rift/scripts/run_safepoint_probe.sh
```

## Claim Discipline

The current patched HotSpot is a prototype. It proves a narrow interpreter-mode
ordinary-object allocation path for explicitly registered final primitive-field
classes, plus heap-retention rejection for the covered interpreter,
Unsafe/JNI, reflection, MethodHandle, and closure-capture smoke routes. It does
not yet prove broad JVM Rift safety or performance. Patch 7 adds an explicit
`RiftRegion.verifyLive(Object)` test hook for API-boundary stale-use checks,
and Patch 8 adds conservative C1 allocation through the runtime stub for
eligible records. Patch 9 adds conservative C1 compiled store guards for
reference stores. Patch 10 gates C2/JVMCI compilation while
`-XX:+UseRiftRegions` is enabled, so unsupported compiled paths cannot silently
bypass the C1/interpreter region allocation and store-guard subset. GC
scanning remains the next hard blocker: the safepoint probe shows plain
safepoint-only live region object use works in the narrow interpreter subset,
but `System.gc()` with a live region object aborts fastdebug verification at
`compressedOops.inline.hpp:87` because the VM still assumes root oops are in
the Java heap. True C2 allocation/stores, native stores outside guarded
entrypoints, reference fields, arrays as region allocations, bridge/root rules,
and automatic arbitrary stale-use barriers remain open.
