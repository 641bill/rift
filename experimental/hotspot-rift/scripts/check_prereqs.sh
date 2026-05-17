#!/usr/bin/env bash
set -euo pipefail

echo "HotSpot Rift prerequisite preflight"
echo "date: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo

check() {
  local name="$1"
  shift
  if command -v "$1" >/dev/null 2>&1; then
    printf "OK   %-16s %s\n" "$name" "$(command -v "$1")"
    "$@" 2>&1 | head -n 1 | sed "s/^/     /" || true
  else
    printf "MISS %-16s %s\n" "$name" "$1"
  fi
}

check "git" git --version
check "bash" bash --version
check "make" make --version
check "autoconf" autoconf --version
check "clang" clang --version
check "java" java -version

echo
echo "Environment"
echo "  HOTSPOT_RIFT_OPENJDK_DIR=${HOTSPOT_RIFT_OPENJDK_DIR:-/Users/siyaoliu/rift/cache/openjdk-rift}"
echo "  HOTSPOT_RIFT_BUILD_NAME=${HOTSPOT_RIFT_BUILD_NAME:-rift-fastdebug}"
echo
echo "Notes"
echo "  OpenJDK builds need Xcode command line tools, autoconf, make, and a boot JDK."
echo "  This script does not clone, configure, or build OpenJDK."
