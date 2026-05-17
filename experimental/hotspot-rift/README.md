# HotSpot Rift Experiment

Last updated: 2026-05-18 00:48 CEST

Status: scaffold and exported Patch 1-13 artifacts for the custom HotSpot
VM-fork backend, plus a first Scala-facing smoke wrapper over the internal VM
entrypoints. This directory does not contain an OpenJDK checkout. It contains
the scripts, patch notes, exported patches, and smoke tests used to create and
validate one.

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
| `scripts/run_config_gate_smoke.sh` | Run the unsupported VM-configuration rejection smoke. |
| `scripts/run_safepoint_probe.sh` | Probe safepoint-only and explicit-GC behavior for live region objects. |
| `scripts/run_scala_region_smoke.sh` | Compile and run the first Scala-facing Rift wrapper smoke on the patched JDK. |
| `tests/java/RiftHotSpotBaselineSmoke.java` | Baseline retained-object workload for stock/patched JDKs. |
| `tests/java/RiftHotSpotConfigGateSmoke.java` | Unsupported collector/header mode rejection smoke. |
| `tests/java/RiftHotSpotRegionSmoke.java` | Region lifecycle smoke. |
| `tests/java/RiftHotSpotObjectRegionSmoke.java` | Object-region allocation and store-guard smoke. |
| `tests/java/RiftHotSpotC1RegionAllocationSmoke.java` | C1 allocation smoke for registered primitive-field records. |
| `tests/java/RiftHotSpotC1StoreGuardSmoke.java` | C1 `putstatic`/`putfield`/`aastore` store-guard smoke. |
| `tests/java/RiftHotSpotSafepointProbe.java` | Safepoint/GC probe for live registered region objects. |
| `tests/scala/riftjvm/Rift.scala` | Minimal Scala wrapper around `jdk.internal.rift.RiftRegion`. |
| `tests/scala/riftjvm/RiftJvmScalaSmoke.scala` | Scala source-level epoch/allocation/heap-root smoke. |
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

Run unsupported VM-configuration gate smoke with a built JDK:

```sh
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
  experimental/hotspot-rift/scripts/run_config_gate_smoke.sh
```

Run safepoint/GC probe with a built JDK:

```sh
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
  experimental/hotspot-rift/scripts/run_safepoint_probe.sh
```

Run the Scala-facing wrapper smoke with a built JDK:

```sh
HOTSPOT_RIFT_JAVA=/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java \
  experimental/hotspot-rift/scripts/run_scala_region_smoke.sh
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
bypass the C1/interpreter region allocation and store-guard subset. Patch 11
adds a first Serial-GC-only root handling path for active uncompressed Rift
region oops: the safepoint probe now passes both plain safepoint and explicit
`System.gc()` cases for primitive-field region objects. Patch 12 gates the VM
configuration up front: the prototype now requires `-XX:+UseSerialGC`,
`-XX:-UseCompressedOops`, and `-XX:-UseCompactObjectHeaders` whenever
`UseRiftRegions` is used. Patch 13 adds an explicit heap-root bridge handle:
region objects can store a primitive `long` handle to GC-visible heap metadata,
while direct heap `oop` reference fields remain rejected. Heap-root handles are
manual test-surface handles for now and must be released explicitly. This is
still narrow: true C2 allocation/stores, other collectors, compressed oops,
native stores outside guarded entrypoints, reference fields, arrays as region
allocations, broad bridge/root rules, and automatic arbitrary stale-use
barriers remain open. The Scala wrapper smoke proves only source-level
reachability of the VM mechanism: Scala 3 code can call `Rift.epoch`, register
eligible primitive-field Scala classes, allocate one into the active VM
region, and use the explicit heap-root bridge. It is not yet capture-checker
integration or a performance benchmark.
