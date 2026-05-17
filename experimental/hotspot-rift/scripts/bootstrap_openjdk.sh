#!/usr/bin/env bash
set -euo pipefail

OPENJDK_DIR="${HOTSPOT_RIFT_OPENJDK_DIR:-/Users/siyaoliu/rift/cache/openjdk-rift}"
OPENJDK_REMOTE="${HOTSPOT_RIFT_OPENJDK_REMOTE:-https://github.com/openjdk/jdk.git}"
OPENJDK_BRANCH="${HOTSPOT_RIFT_OPENJDK_BRANCH:-master}"

if [ -e "${OPENJDK_DIR}/.git" ]; then
  echo "OpenJDK worktree already exists: ${OPENJDK_DIR}"
  git -C "${OPENJDK_DIR}" status --short
  exit 0
fi

mkdir -p "$(dirname "${OPENJDK_DIR}")"
echo "Cloning ${OPENJDK_REMOTE} (${OPENJDK_BRANCH}) into ${OPENJDK_DIR}"
git clone --branch "${OPENJDK_BRANCH}" "${OPENJDK_REMOTE}" "${OPENJDK_DIR}"
git -C "${OPENJDK_DIR}" status --short
