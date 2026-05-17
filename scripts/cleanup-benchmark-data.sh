#!/usr/bin/env bash
set -euo pipefail

ROOT="${RIFT_ROOT:-/Users/siyaoliu/rift}"
DO_CLEAN="${RIFT_CLEAN_DATA:-0}"

say_action() {
  local path="$1"
  if [[ -e "$path" ]]; then
    du -sh "$path" 2>/dev/null || true
    if [[ "$DO_CLEAN" == "1" ]]; then
      rm -rf "$path"
      echo "removed  $path"
    else
      echo "dry-run  $path"
    fi
  fi
}

cat <<EOF
# Rift benchmark data cleanup

Mode: $(if [[ "$DO_CLEAN" == "1" ]]; then echo "delete"; else echo "dry-run"; fi)
Root: $ROOT

This removes extracted/generated benchmark data that can be replaced by
compressed streaming specs or regenerated inputs. Run with RIFT_CLEAN_DATA=1
to actually delete the dry-run list.

EOF

echo "## Extracted duplicates with compressed archives retained"
safe_paths=(
  "$ROOT/cache/benchmark-data/loghub/Windows"
  "$ROOT/cache/benchmark-data/loghub/HDFS_1"
  "$ROOT/cache/benchmark-data/loghub/BGL"
  "$ROOT/cache/benchmark-data/loghub/Spark"
  "$ROOT/cache/benchmark-data/common-crawl/CC-MAIN-2026-17/CC-MAIN-20260410081153-20260410111153-00000.warc.wet"
  "$ROOT/cache/benchmark-data/common-crawl/CC-MAIN-2026-17/CC-MAIN-20260410081153-20260410111153-00000.warc.wat"
  "$ROOT/cache/benchmark-data/common-crawl/CC-MAIN-2026-17/wet.paths.txt"
  "$ROOT/cache/benchmark-data/common-crawl/CC-MAIN-2026-17/wat.paths.txt"
  "$ROOT/cache/benchmark-data/common-crawl/CC-MAIN-2026-17/warc.paths.txt"
  "$ROOT/cache/benchmark-data/linear-road/test-data"
  "$ROOT/cache/benchmark-data/theodolite/real-power/household_power_consumption.txt"
)
for path in "${safe_paths[@]}"; do
  say_action "$path"
done

if [[ "${RIFT_CLEAN_REGENERABLE:-0}" == "1" ]]; then
  echo
  echo "## Regenerable DBGEN TPC-H scale data"
  echo "Broom Q17 can now generate temporary DBGEN part/lineitem tables per run"
  echo "with BROOM_Q17_INPUT_MODE=tpch-dbgen, so cached TPC-H table directories"
  echo "are optional."
  for path in "$ROOT/cache"/tpch-sf*; do
    say_action "$path"
  done
fi

if [[ "${RIFT_CLEAN_DERIVED_ARCHIVE_INPUTS:-0}" == "1" ]]; then
  echo
  echo "## Derived archive-member inputs"
  echo "Delete these only after using the original compressed archive specs:"
  echo "- YAK_TEXT_INPUT=7z:.../askubuntu.com.7z!Posts.xml"
  echo "- RIOTBENCH_INPUT=zipdir:.../mhealth_dataset.zip!MHEALTHDATASET"
  say_action "$ROOT/cache/benchmark-data/yak/stackexchange/askubuntu-Posts.xml.gz"
  say_action "$ROOT/cache/benchmark-data/riot-bench/mhealth/MHEALTHDATASET"
fi

if [[ "${RIFT_CLEAN_DSPBENCH_SOURCE:-0}" == "1" ]]; then
  echo
  echo "## DSPBench expanded source checkout"
  echo "Delete only after the pinned DSPBench source ZIP is present and runners"
  echo "use zip:...!member specs."
  say_action "$ROOT/cache/benchmark-data/dspbench/source"
fi

if [[ "${RIFT_CLEAN_TAXI:-0}" == "1" ]]; then
  echo
  echo "## Very large DEBS/NYC taxi directories"
  echo "Delete only if DEBS taxi reruns are not needed locally or official"
  echo "trip_data.7z/trip_fare.7z archives are present."
  say_action "$ROOT/trip_data"
  say_action "$ROOT/trip_fare"
fi

if [[ "${RIFT_CLEAN_OPENJDK:-0}" == "1" ]]; then
  echo
  echo "## Non-Scala-Native backend clone"
  echo "This is unrelated to current Scala Native benchmark execution."
  say_action "$ROOT/cache/openjdk-rift"
fi

cat <<'EOF'

Useful follow-ups:

- RIFT_CLEAN_DATA=1 scripts/cleanup-benchmark-data.sh
- RIFT_CLEAN_DATA=1 RIFT_CLEAN_REGENERABLE=1 scripts/cleanup-benchmark-data.sh
- RIFT_CLEAN_DATA=1 RIFT_CLEAN_DERIVED_ARCHIVE_INPUTS=1 scripts/cleanup-benchmark-data.sh
- RIFT_CLEAN_DATA=1 RIFT_CLEAN_DSPBENCH_SOURCE=1 scripts/cleanup-benchmark-data.sh
- RIFT_CLEAN_DATA=1 RIFT_CLEAN_TAXI=1 scripts/cleanup-benchmark-data.sh
- RIFT_CLEAN_DATA=1 RIFT_CLEAN_OPENJDK=1 scripts/cleanup-benchmark-data.sh
EOF
