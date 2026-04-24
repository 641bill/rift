#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/siyaoliu/rift"
FORK="$ROOT/scala-native-rift"
DEST="$ROOT/evidence"

mkdir -p "$DEST"

cp -f "$FORK/sandbox/PHASE0_BASELINES.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/PHASE4_LAYOUT.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/PHASE4_TOPOLOGY.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/PHASE4_EXIT.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/PIPELINE_PARCOLL_COMPARISON.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/DATAFLOW_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true

cp -f "$FORK/bench/debs2015/RESULTS.md" "$DEST/DEBS_RESULTS.md" 2>/dev/null || true
cp -f "$FORK/bench/debs2015/ATTRIBUTION.md" "$DEST/DEBS_ATTRIBUTION.md" 2>/dev/null || true

echo "Synced evidence into $DEST"
