#!/usr/bin/env bash
set -euo pipefail

JAVA_BIN="${HOTSPOT_RIFT_JAVA:-/Users/siyaoliu/rift/cache/openjdk-rift/build/rift-fastdebug/jdk/bin/java}"
JAVA_HOME_DIR="$(cd "$(dirname "${JAVA_BIN}")/.." && pwd)"
OUT_DIR="${HOTSPOT_RIFT_OUT_DIR:-/private/tmp/rift-hotspot-scala-region-smoke}"
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)/tests/scala"

mkdir -p "${OUT_DIR}"

scala-cli compile "${SRC_DIR}" \
  --server=false \
  --java-home "${JAVA_HOME_DIR}" \
  --print-class-path \
  > "${OUT_DIR}/classpath.txt"

SCALA_CP="$(tail -n 1 "${OUT_DIR}/classpath.txt")"

"${JAVA_BIN}" \
  -Xint \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+UseRiftRegions \
  -XX:+UseSerialGC \
  -XX:-UseCompressedOops \
  -XX:-UseCompactObjectHeaders \
  --add-exports=java.base/jdk.internal.rift=ALL-UNNAMED \
  -cp "${SCALA_CP}" \
  riftjvm.RiftJvmScalaSmoke
