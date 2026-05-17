#!/usr/bin/env bash
set -euo pipefail

JAVA_BIN="${HOTSPOT_RIFT_JAVA:-/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java}"
JAVAC_BIN="${HOTSPOT_RIFT_JAVAC:-${JAVA_BIN%/java}/javac}"
OUT_DIR="${HOTSPOT_RIFT_OUT_DIR:-/private/tmp/rift-hotspot-config-gate-smoke}"
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)/tests/java"

mkdir -p "${OUT_DIR}/classes"

"${JAVAC_BIN}" \
  --add-exports java.base/jdk.internal.rift=ALL-UNNAMED \
  -d "${OUT_DIR}/classes" \
  "${SRC_DIR}/RiftHotSpotConfigGateSmoke.java"

"${JAVA_BIN}" \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+UseRiftRegions \
  --add-exports java.base/jdk.internal.rift=ALL-UNNAMED \
  -cp "${OUT_DIR}/classes" \
  RiftHotSpotConfigGateSmoke
