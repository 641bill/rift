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
cp -f "$FORK/sandbox/PROFILE_SWEEP_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_APPEND_WINDOW_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/OBJECT_ALLOCATION_LOWERING_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_PAGE_TOKEN_APPEND_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_PAGE_TOKEN_COST_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_WINDOW_FOLD_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/NEXMARK_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/COMMON_CRAWL_WET_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/WIKIMEDIA_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/LINEAR_ROAD_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/YAHOO_AD_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/RIOTBENCH_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/STREAM_BENCHMARK_LADDER.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/STREAM_GC_BENCHMARK_CANDIDATES.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/UNSAFEZONE_HP_BASELINE_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/SAFEZONE_COST_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/SAFEZONE_HP_BACKEND_PROTOTYPE.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_SAFEZONE_BACKEND_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHECKED_OVERHEAD_REMOVAL_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/CHEAP_OPERATOR_FAMILY_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/DIRECT_EPOCH_TOPOLOGY_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/RETAINED_EPOCH_RECLAIM_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/SPECJBB2005_PORT_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/REALISTIC_STREAM_GC_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/REAL_INPUT_BENCHMARK_SEARCH.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/COMMON_CRAWL_LIKE_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/GITHUB_ARCHIVE_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/LOGHUB_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/LOGHUB_TOP_TEMPLATES_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/DSPBENCH_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/THEODOLITE_POWER_REGION_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/REML_COMPARISON_MATRIX.md" "$DEST/" 2>/dev/null || true
cp -f "$FORK/sandbox/SN_WIN_ENVELOPE.md" "$DEST/" 2>/dev/null || true

cp -f "$FORK/bench/debs2015/RESULTS.md" "$DEST/DEBS_RESULTS.md" 2>/dev/null || true
cp -f "$FORK/bench/debs2015/ATTRIBUTION.md" "$DEST/DEBS_ATTRIBUTION.md" 2>/dev/null || true

echo "Synced evidence into $DEST"
