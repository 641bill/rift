#!/usr/bin/env bash
set -euo pipefail

JAVA_BIN="${HOTSPOT_RIFT_JAVA:-/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java}"
JAVAC_BIN="${HOTSPOT_RIFT_JAVAC:-${JAVA_BIN%/java}/javac}"
OUT_DIR="${HOTSPOT_RIFT_OUT_DIR:-/private/tmp/rift-hotspot-object-region-smoke}"
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)/tests/java"

mkdir -p "${OUT_DIR}/classes"

"${JAVAC_BIN}" \
  --add-exports java.base/jdk.internal.rift=ALL-UNNAMED \
  -d "${OUT_DIR}/classes" \
  "${SRC_DIR}/RiftHotSpotObjectRegionSmoke.java"

"${JAVA_BIN}" \
  -Xint \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+UseRiftRegions \
  -XX:+UseSerialGC \
  -XX:-UseCompressedOops \
  -XX:-UseCompactObjectHeaders \
  --add-exports java.base/jdk.internal.rift=ALL-UNNAMED \
  --add-opens java.base/jdk.internal.misc=ALL-UNNAMED \
  -cp "${OUT_DIR}/classes" \
  RiftHotSpotObjectRegionSmoke
