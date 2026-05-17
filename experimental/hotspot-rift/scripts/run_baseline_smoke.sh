#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUT_DIR="${HOTSPOT_RIFT_OUT_DIR:-/private/tmp/rift-hotspot-smoke}"
JAVA_BIN="${HOTSPOT_RIFT_JAVA:-java}"
RECORDS="${HOTSPOT_RIFT_RECORDS:-1000000}"
EPOCH_SIZE="${HOTSPOT_RIFT_EPOCH_SIZE:-10000}"
ACTIVE="${HOTSPOT_RIFT_ACTIVE_TIMESTAMPS:-16}"

mkdir -p "${OUT_DIR}/classes" "${OUT_DIR}/gc" "${OUT_DIR}/time"

javac -d "${OUT_DIR}/classes" "${ROOT_DIR}/tests/java/RiftHotSpotBaselineSmoke.java"

TIME_OUT="${OUT_DIR}/time/baseline.txt"
GC_LOG="${OUT_DIR}/gc/baseline.log"
ROW_OUT="${OUT_DIR}/baseline.tsv"

/usr/bin/time -l -o "${TIME_OUT}" \
  "${JAVA_BIN}" \
    -Xms1g -Xmx1g -XX:+UseG1GC \
    "-Xlog:gc*:file=${GC_LOG}:time,level,tags" \
    -cp "${OUT_DIR}/classes" \
    RiftHotSpotBaselineSmoke \
    "${RECORDS}" "${EPOCH_SIZE}" "${ACTIVE}" \
  > "${ROW_OUT}"

echo "baseline smoke output: ${OUT_DIR}"
echo "rows: ${ROW_OUT}"
echo "time: ${TIME_OUT}"
echo "gc: ${GC_LOG}"
