#!/usr/bin/env bash
set -euo pipefail

OPENJDK_DIR="${HOTSPOT_RIFT_OPENJDK_DIR:-/Users/siyaoliu/rift/cache/openjdk-rift}"
BUILD_NAME="${HOTSPOT_RIFT_BUILD_NAME:-rift-fastdebug}"
BOOT_JDK="${HOTSPOT_RIFT_BOOT_JDK:-}"
DEVKIT="${HOTSPOT_RIFT_DEVKIT:-}"
METAL_TOOLCHAIN_PATH="${HOTSPOT_RIFT_METAL_TOOLCHAIN_PATH:-}"

if [ ! -d "${OPENJDK_DIR}" ]; then
  echo "Missing OpenJDK source: ${OPENJDK_DIR}" >&2
  echo "Run experimental/hotspot-rift/scripts/bootstrap_openjdk.sh first." >&2
  exit 1
fi

cd "${OPENJDK_DIR}"

CONFIGURE_ARGS=(
  "--with-debug-level=fastdebug"
  "--with-jvm-variants=server"
  "--with-conf-name=${BUILD_NAME}"
  "--disable-warnings-as-errors"
  "--enable-headless-only"
)

if [ -n "${BOOT_JDK}" ]; then
  CONFIGURE_ARGS+=("--with-boot-jdk=${BOOT_JDK}")
fi

if [ -n "${DEVKIT}" ]; then
  if [ ! -f "${DEVKIT}/devkit.info" ]; then
    echo "HOTSPOT_RIFT_DEVKIT does not look like an OpenJDK devkit: ${DEVKIT}" >&2
    echo "Expected ${DEVKIT}/devkit.info" >&2
    exit 1
  fi
  CONFIGURE_ARGS+=("--with-devkit=${DEVKIT}")
fi

if [ -z "${METAL_TOOLCHAIN_PATH}" ]; then
  METAL_TOOLCHAIN_PATH="$(
    find /var/run/com.apple.security.cryptexd/mnt \
      -path '*Metal.xctoolchain/usr/bin' \
      -type d \
      -print 2>/dev/null | head -n 1 || true
  )"
fi

if [ -n "${METAL_TOOLCHAIN_PATH}" ]; then
  if [ ! -x "${METAL_TOOLCHAIN_PATH}/metal" ] || [ ! -x "${METAL_TOOLCHAIN_PATH}/metallib" ]; then
    echo "HOTSPOT_RIFT_METAL_TOOLCHAIN_PATH is missing metal/metallib: ${METAL_TOOLCHAIN_PATH}" >&2
    exit 1
  fi
  CONFIGURE_ARGS+=("--with-toolchain-path=${METAL_TOOLCHAIN_PATH}")
fi

echo "Configuring OpenJDK in ${OPENJDK_DIR}"
bash configure "${CONFIGURE_ARGS[@]}"

echo "Building images for ${BUILD_NAME}"
make images CONF_NAME="${BUILD_NAME}"

echo "Built JDK:"
echo "  ${OPENJDK_DIR}/build/${BUILD_NAME}/jdk/bin/java"
"${OPENJDK_DIR}/build/${BUILD_NAME}/jdk/bin/java" -version
