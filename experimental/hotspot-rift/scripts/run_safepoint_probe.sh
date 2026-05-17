#!/usr/bin/env bash
set -euo pipefail

JAVA_BIN="${HOTSPOT_RIFT_JAVA:-/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java}"
JAVAC_BIN="${HOTSPOT_RIFT_JAVAC:-${JAVA_BIN%/java}/javac}"
OUT_DIR="${HOTSPOT_RIFT_OUT_DIR:-/private/tmp/rift-hotspot-safepoint-probe}"
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)/tests/java"

mkdir -p "${OUT_DIR}/classes"

"${JAVAC_BIN}" \
  --add-exports java.base/jdk.internal.rift=ALL-UNNAMED \
  -d "${OUT_DIR}/classes" \
  "${SRC_DIR}/RiftHotSpotSafepointProbe.java"

COMMON_FLAGS=(
  -Xint
  -XX:+UnlockExperimentalVMOptions
  -XX:+UseRiftRegions
  -XX:+UseSerialGC
  -XX:-UseCompressedOops
  -XX:-UseCompactObjectHeaders
  --add-exports java.base/jdk.internal.rift=ALL-UNNAMED
  -cp "${OUT_DIR}/classes"
)

"${JAVA_BIN}" "${COMMON_FLAGS[@]}" RiftHotSpotSafepointProbe safepoint \
  >"${OUT_DIR}/safepoint.out" \
  2>"${OUT_DIR}/safepoint.err"

set +e
"${JAVA_BIN}" "${COMMON_FLAGS[@]}" RiftHotSpotSafepointProbe system-gc \
  >"${OUT_DIR}/system-gc.out" \
  2>"${OUT_DIR}/system-gc.err"
GC_STATUS=$?
set -e

cat "${OUT_DIR}/safepoint.out"

if [[ "${GC_STATUS}" -eq 0 ]]; then
  cat "${OUT_DIR}/system-gc.out"
  echo "system-gc-probe-status=passed"
else
  echo "system-gc-probe-status=failed:${GC_STATUS}"
  if [[ -s "${OUT_DIR}/system-gc.err" ]]; then
    tail -n 40 "${OUT_DIR}/system-gc.err"
  fi
fi
