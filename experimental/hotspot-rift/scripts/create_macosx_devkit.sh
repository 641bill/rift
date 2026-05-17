#!/usr/bin/env bash
set -euo pipefail

OPENJDK_DIR="${HOTSPOT_RIFT_OPENJDK_DIR:-/Users/siyaoliu/rift/cache/openjdk-rift}"
XCODE_APP="${HOTSPOT_RIFT_XCODE_APP:-/Applications/Xcode.app}"

if [ ! -d "${OPENJDK_DIR}" ]; then
  echo "Missing OpenJDK source: ${OPENJDK_DIR}" >&2
  echo "Run experimental/hotspot-rift/scripts/bootstrap_openjdk.sh first." >&2
  exit 1
fi

if [ ! -d "${XCODE_APP}" ]; then
  echo "Missing Xcode app: ${XCODE_APP}" >&2
  echo "Install or extract Xcode, or set HOTSPOT_RIFT_XCODE_APP=/path/to/Xcode.app" >&2
  exit 1
fi

if [ ! -x "${XCODE_APP}/Contents/Developer/usr/bin/xcodebuild" ]; then
  echo "Xcode app does not contain xcodebuild: ${XCODE_APP}" >&2
  exit 1
fi

echo "Creating OpenJDK macOS devkit from ${XCODE_APP}"
bash "${OPENJDK_DIR}/make/devkit/createMacosxDevkit.sh" "${XCODE_APP}"

echo
echo "Available devkits:"
find "${OPENJDK_DIR}/build/devkit" -maxdepth 1 -type d -name 'Xcode*' -print | sort
echo
echo "Use one with:"
echo "  HOTSPOT_RIFT_DEVKIT=<path-above> experimental/hotspot-rift/scripts/build_openjdk.sh"
