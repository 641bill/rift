#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${RIFT_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
FORK="${RIFT_FORK:-$ROOT/scala-native-rift}"
DEST="${RIFT_EVIDENCE:-$ROOT/evidence}"

mkdir -p "$DEST"

cp -f "$FORK/sandbox/PHASE0_BASELINES.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/PHASE4_LAYOUT.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/PHASE4_TOPOLOGY.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/PHASE4_EXIT.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/PIPELINE_PARCOLL_COMPARISON.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/DATAFLOW_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/STREAMFLEX_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/YAK_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/STANCU_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_REGION_BUFFER_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_REGION_PRIORITY_QUEUE_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_REGION_INDEXED_PRIORITY_QUEUE_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_STREAM_WINDOW_RANK_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/TABLERANK_PROFILE.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_APPEND_WINDOW_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_WINDOW_FOLD_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/NEXMARK_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/COMMON_CRAWL_WET_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/STREAM_BENCHMARK_LADDER.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/SN_WIN_ENVELOPE.md" "$DEST/" 2>/dev/null || true

cp -f "$FORK/bench/debs2015/RESULTS.md" "$DEST/DEBS_RESULTS.md" 2>/dev/null || true
cp -f "$FORK/bench/debs2015/ATTRIBUTION.md" "$DEST/DEBS_ATTRIBUTION.md" 2>/dev/null || true

echo "Synced evidence into $DEST"
