#!/usr/bin/env bash
set -euo pipefail

JAVA_BIN="${HOTSPOT_RIFT_JAVA:-/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java}"
JAVAC_BIN="${HOTSPOT_RIFT_JAVAC:-${JAVA_BIN%/java}/javac}"
OUT_DIR="${HOTSPOT_RIFT_OUT_DIR:-/private/tmp/rift-hotspot-c1-store-guard-smoke}"
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)/tests/java"

mkdir -p "${OUT_DIR}/classes"

"${JAVAC_BIN}" \
  --add-exports java.base/jdk.internal.rift=ALL-UNNAMED \
  -d "${OUT_DIR}/classes" \
  "${SRC_DIR}/RiftHotSpotC1StoreGuardSmoke.java"

"${JAVA_BIN}" \
  -Xbatch \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+UseRiftRegions \
  -XX:+UseSerialGC \
  -XX:-UseCompressedOops \
  -XX:-UseCompactObjectHeaders \
  -XX:+TieredCompilation \
  -XX:TieredStopAtLevel=1 \
  -XX:CompileThreshold=100 \
  -XX:CompileCommand=compileonly,RiftHotSpotC1StoreGuardSmoke.storeStatic \
  -XX:CompileCommand=compileonly,RiftHotSpotC1StoreGuardSmoke.storeField \
  -XX:CompileCommand=compileonly,RiftHotSpotC1StoreGuardSmoke.storeArray \
  --add-exports java.base/jdk.internal.rift=ALL-UNNAMED \
  -cp "${OUT_DIR}/classes" \
  RiftHotSpotC1StoreGuardSmoke
