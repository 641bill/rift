#!/usr/bin/env bash
set -euo pipefail

ROOT="${RIFT_ROOT:-/Users/siyaoliu/rift}"
THRESHOLD="${RIFT_DATA_FOOTPRINT_THRESHOLD:-20M}"

echo "# Rift benchmark data footprint"
echo
echo "Root: $ROOT"
echo "Threshold: $THRESHOLD"
echo

echo "## Top-level directories"
du -sh "$ROOT"/* "$ROOT"/.??* 2>/dev/null | sort -hr | head -80
echo

echo "## Benchmark data directories"
du -sh \
  "$ROOT/cache" \
  "$ROOT/cache/benchmark-data" \
  "$ROOT/cache/benchmark-data"/* \
  "$ROOT/cache"/tpch-* \
  "$ROOT/trip_data" \
  "$ROOT/trip_fare" 2>/dev/null | sort -hr
echo

echo "## Large benchmark input files"
find \
  "$ROOT/cache/benchmark-data" \
  "$ROOT/cache"/tpch-* \
  "$ROOT/trip_data" \
  "$ROOT/trip_fare" \
  -type f -size +"$THRESHOLD" -print0 2>/dev/null |
  xargs -0 du -h 2>/dev/null |
  sort -hr |
  head -200
echo

cat <<'EOF'
## Compressed streaming specs supported by BenchmarkInputSupport

Plain .gz files can be used directly as input paths.

Archive members can be streamed without extracting the full dataset:

- tar.gz:/absolute/path/archive.tar.gz!member/path/in/archive
- zip:/absolute/path/archive.zip!member/path/in/archive
- 7z:/absolute/path/archive.7z!member/path/in/archive
- zipdir:/absolute/path/archive.zip!directory/prefix

Examples:

- tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows.tar.gz!Windows.log
- tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1.tar.gz!HDFS.log
- tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/BGL.tar.gz!BGL.log
- zip:/Users/siyaoliu/rift/cache/benchmark-data/theodolite/real-power/household_power_consumption.zip!household_power_consumption.txt
- 7z:/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu.com.7z!Posts.xml
- zip:/Users/siyaoliu/rift/cache/benchmark-data/dspbench/DSPBench-00c20da828faf2b960fdb697c61d34cb25461875.zip!DSPBench-00c20da828faf2b960fdb697c61d34cb25461875/dspbench-threads/data/credit-card.dat
- zipdir:/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/mhealth/mhealth_dataset.zip!MHEALTHDATASET
- BROOM_Q17_INPUT_MODE=tpch-dbgen BROOM_TPCH_SCALE=1 zsh /Users/siyaoliu/rift/scala-native-rift/sandbox/run_broom_retained_dataflow_matrix.sh
- /Users/siyaoliu/rift/cache/benchmark-data/debs2015/trip_data.7z
- /Users/siyaoliu/rift/cache/benchmark-data/debs2015/trip_fare.7z
EOF
