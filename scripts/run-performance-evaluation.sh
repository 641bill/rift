#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${RIFT_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
FORK="${RIFT_FORK:-$ROOT/scala-native-rift}"
RUN_ID="${RIFT_EVAL_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_ROOT="${RIFT_EVAL_RUN_ROOT:-$ROOT/cache/perf-eval/$RUN_ID}"
LOG_DIR="$RUN_ROOT/logs"
SUMMARY_DIR="$RUN_ROOT/summaries"
SUITES="${RIFT_EVAL_SUITES:-preflight}"
SCALE="${RIFT_EVAL_SCALE:-smoke}"

mkdir -p "$LOG_DIR" "$SUMMARY_DIR"

log() {
  printf '[rift-eval] %s\n' "$*"
}

suite_enabled() {
  local wanted="$1"
  [[ " $SUITES " == *" all "* || " $SUITES " == *" $wanted "* ]]
}

run_logged() {
  local name="$1"
  local dir="$2"
  shift 2
  local log_file="$LOG_DIR/$name.log"
  log "running $name"
  (
    cd "$dir"
    "$@"
  ) >"$log_file" 2>&1
  log "wrote $log_file"
}

record_environment() {
  {
    echo "run_id=$RUN_ID"
    echo "date_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "root=$ROOT"
    echo "fork=$FORK"
    echo "suites=$SUITES"
    echo "scale=$SCALE"
    echo
    echo "== uname =="
    uname -a
    echo
    echo "== cpu =="
    if command -v sysctl >/dev/null 2>&1; then
      sysctl -n machdep.cpu.brand_string 2>/dev/null || true
      sysctl -n hw.memsize 2>/dev/null || true
    fi
    echo
    echo "== parent git =="
    git -C "$ROOT" branch --show-current
    git -C "$ROOT" rev-parse HEAD
    git -C "$ROOT" status --short
    echo
    echo "== child git =="
    git -C "$FORK" branch --show-current
    git -C "$FORK" rev-parse HEAD
    git -C "$FORK" status --short
    echo
    echo "== java =="
    if command -v cs >/dev/null 2>&1; then
      local java_home
      java_home="$(cs java-home --jvm temurin:17)"
      "$java_home/bin/java" -version 2>&1 || true
    else
      java -version 2>&1 || true
    fi
  } >"$RUN_ROOT/environment.txt"
}

require_clean_repos() {
  if [[ "${RIFT_EVAL_ALLOW_DIRTY:-0}" == "1" ]]; then
    log "dirty repos allowed by RIFT_EVAL_ALLOW_DIRTY=1"
    return
  fi
  if [[ -n "$(git -C "$ROOT" status --short)" ]]; then
    echo "parent repo is dirty; commit/stash first or set RIFT_EVAL_ALLOW_DIRTY=1" >&2
    exit 1
  fi
  if [[ -n "$(git -C "$FORK" status --short)" ]]; then
    echo "scala-native-rift repo is dirty; commit/stash first or set RIFT_EVAL_ALLOW_DIRTY=1" >&2
    exit 1
  fi
}

set_scale_defaults() {
  case "$SCALE" in
    smoke)
      export RIFT_EVAL_EVENTS="${RIFT_EVAL_EVENTS:-20000}"
      export RIFT_EVAL_RUNS="${RIFT_EVAL_RUNS:-1}"
      export RIFT_EVAL_LISTBENCH_N="${RIFT_EVAL_LISTBENCH_N:-200}"
      export RIFT_EVAL_LISTBENCH_STRUCTURES="${RIFT_EVAL_LISTBENCH_STRUCTURES:-1}"
      export RIFT_EVAL_CHECKED_EPOCHS="${RIFT_EVAL_CHECKED_EPOCHS:-1}"
      export RIFT_EVAL_CHECKED_RECORDS_PER_EPOCH="${RIFT_EVAL_CHECKED_RECORDS_PER_EPOCH:-20000}"
      export RIFT_EVAL_CHECKED_PQ_RECORDS_PER_EPOCH="${RIFT_EVAL_CHECKED_PQ_RECORDS_PER_EPOCH:-20000}"
      export RIFT_EVAL_CHECKED_IPQ_EPOCHS="${RIFT_EVAL_CHECKED_IPQ_EPOCHS:-1}"
      export RIFT_EVAL_CHECKED_IPQ_EVENTS_PER_EPOCH="${RIFT_EVAL_CHECKED_IPQ_EVENTS_PER_EPOCH:-20000}"
      ;;
    headline)
      export RIFT_EVAL_EVENTS="${RIFT_EVAL_EVENTS:-1000000}"
      export RIFT_EVAL_RUNS="${RIFT_EVAL_RUNS:-5}"
      export RIFT_EVAL_LISTBENCH_N="${RIFT_EVAL_LISTBENCH_N:-3000}"
      export RIFT_EVAL_LISTBENCH_STRUCTURES="${RIFT_EVAL_LISTBENCH_STRUCTURES:-40}"
      export RIFT_EVAL_CHECKED_EPOCHS="${RIFT_EVAL_CHECKED_EPOCHS:-10}"
      export RIFT_EVAL_CHECKED_RECORDS_PER_EPOCH="${RIFT_EVAL_CHECKED_RECORDS_PER_EPOCH:-100000}"
      export RIFT_EVAL_CHECKED_PQ_RECORDS_PER_EPOCH="${RIFT_EVAL_CHECKED_PQ_RECORDS_PER_EPOCH:-50000}"
      export RIFT_EVAL_CHECKED_IPQ_EPOCHS="${RIFT_EVAL_CHECKED_IPQ_EPOCHS:-8}"
      export RIFT_EVAL_CHECKED_IPQ_EVENTS_PER_EPOCH="${RIFT_EVAL_CHECKED_IPQ_EVENTS_PER_EPOCH:-125000}"
      ;;
    full)
      export RIFT_EVAL_EVENTS="${RIFT_EVAL_EVENTS:-10000000}"
      export RIFT_EVAL_RUNS="${RIFT_EVAL_RUNS:-3}"
      export RIFT_EVAL_LISTBENCH_N="${RIFT_EVAL_LISTBENCH_N:-3000}"
      export RIFT_EVAL_LISTBENCH_STRUCTURES="${RIFT_EVAL_LISTBENCH_STRUCTURES:-40}"
      export RIFT_EVAL_CHECKED_EPOCHS="${RIFT_EVAL_CHECKED_EPOCHS:-10}"
      export RIFT_EVAL_CHECKED_RECORDS_PER_EPOCH="${RIFT_EVAL_CHECKED_RECORDS_PER_EPOCH:-1000000}"
      export RIFT_EVAL_CHECKED_PQ_RECORDS_PER_EPOCH="${RIFT_EVAL_CHECKED_PQ_RECORDS_PER_EPOCH:-500000}"
      export RIFT_EVAL_CHECKED_IPQ_EPOCHS="${RIFT_EVAL_CHECKED_IPQ_EPOCHS:-8}"
      export RIFT_EVAL_CHECKED_IPQ_EVENTS_PER_EPOCH="${RIFT_EVAL_CHECKED_IPQ_EVENTS_PER_EPOCH:-1250000}"
      ;;
    *)
      echo "unknown RIFT_EVAL_SCALE=$SCALE; use smoke, headline, or full" >&2
      exit 1
      ;;
  esac
}

run_compile() {
  run_logged compile "$FORK" env ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
}

run_core() {
  run_logged gcbench-runtime "$FORK" env GCBENCH_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" zsh sandbox/run_gcbench_runtime_matrix.sh
  run_logged gcbench-topology "$FORK" env GCBENCH_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" zsh sandbox/run_gcbench_topology_matrix.sh
  run_logged listoflists-runtime "$FORK" env LISTBENCH_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" LISTBENCH_N="$RIFT_EVAL_LISTBENCH_N" LISTBENCH_STRUCTURES="$RIFT_EVAL_LISTBENCH_STRUCTURES" zsh sandbox/run_listoflists_runtime_matrix.sh
  run_logged listoflists-flat "$FORK" env LISTBENCH_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" LISTBENCH_N="$RIFT_EVAL_LISTBENCH_N" LISTBENCH_STRUCTURES="$RIFT_EVAL_LISTBENCH_STRUCTURES" zsh sandbox/run_listoflists_flat_matrix.sh
  run_logged listoflists-chunked "$FORK" env LISTBENCH_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" LISTBENCH_N="$RIFT_EVAL_LISTBENCH_N" LISTBENCH_STRUCTURES="$RIFT_EVAL_LISTBENCH_STRUCTURES" zsh sandbox/run_listoflists_chunked_matrix.sh
  run_logged listoflists-topology "$FORK" env LISTBENCH_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" LISTBENCH_N="$RIFT_EVAL_LISTBENCH_N" LISTBENCH_STRUCTURES="$RIFT_EVAL_LISTBENCH_STRUCTURES" zsh sandbox/run_listoflists_topology_matrix.sh
  run_logged pipeline-runtime "$FORK" env PIPELINE_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" zsh sandbox/run_pipeline_runtime_matrix.sh
}

run_prior_work() {
  run_logged dataflow "$FORK" env DATAFLOW_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" zsh sandbox/run_dataflow_region_matrix.sh
  run_logged streamflex "$FORK" env STREAMFLEX_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" STREAMFLEX_OUTPUT_DIR="$SUMMARY_DIR/streamflex" zsh sandbox/run_streamflex_region_instrumented_matrix.sh
  run_logged yak "$FORK" env YAK_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" YAK_OUTPUT_DIR="$SUMMARY_DIR/yak" zsh sandbox/run_yak_region_instrumented_matrix.sh
  run_logged stancu "$FORK" env STANCU_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" STANCU_OUTPUT_DIR="$SUMMARY_DIR/stancu" zsh sandbox/run_stancu_region_instrumented_matrix.sh
}

run_checked() {
  run_logged object-allocation-lowering "$FORK" env OBJECT_ALLOC_OBJECTS="$RIFT_EVAL_EVENTS" OBJECT_ALLOC_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" OBJECT_ALLOC_OUTPUT_DIR="$SUMMARY_DIR/object-allocation-lowering" zsh sandbox/run_object_allocation_lowering_matrix.sh
  run_logged checked-region-buffer "$FORK" env CHECKED_BUFFER_EPOCHS="$RIFT_EVAL_CHECKED_EPOCHS" CHECKED_BUFFER_RECORDS_PER_EPOCH="$RIFT_EVAL_CHECKED_RECORDS_PER_EPOCH" CHECKED_BUFFER_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" zsh sandbox/run_checked_region_buffer_matrix.sh
  run_logged checked-priority-queue "$FORK" env CHECKED_PQ_EPOCHS="$RIFT_EVAL_CHECKED_EPOCHS" CHECKED_PQ_RECORDS_PER_EPOCH="$RIFT_EVAL_CHECKED_PQ_RECORDS_PER_EPOCH" CHECKED_PQ_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" zsh sandbox/run_checked_region_priority_queue_matrix.sh
  run_logged checked-indexed-priority-queue "$FORK" env CHECKED_IPQ_EPOCHS="$RIFT_EVAL_CHECKED_IPQ_EPOCHS" CHECKED_IPQ_EVENTS_PER_EPOCH="$RIFT_EVAL_CHECKED_IPQ_EVENTS_PER_EPOCH" CHECKED_IPQ_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" zsh sandbox/run_checked_region_indexed_priority_queue_matrix.sh
  run_logged checked-stream-window-rank "$FORK" env CHECKED_SWR_EVENTS="$RIFT_EVAL_EVENTS" CHECKED_SWR_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" zsh sandbox/run_checked_stream_window_rank_matrix.sh
  run_logged checked-append-window "$FORK" env CHECKED_APPEND_EVENTS="$RIFT_EVAL_EVENTS" CHECKED_APPEND_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" CHECKED_APPEND_OUTPUT_DIR="$SUMMARY_DIR/checked-append-window" zsh sandbox/run_checked_append_window_matrix.sh
  run_logged checked-window-fold "$FORK" env CHECKED_FOLD_EVENTS="$RIFT_EVAL_EVENTS" CHECKED_FOLD_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" CHECKED_FOLD_OUTPUT_DIR="$SUMMARY_DIR/checked-window-fold" zsh sandbox/run_checked_window_fold_matrix.sh
}

run_safezone_cost() {
  run_logged safezone-cost "$FORK" env SAFEZONE_COST_RUNS="$RIFT_EVAL_RUNS" SAFEZONE_COST_COMMON_CRAWL_PAGES="$RIFT_EVAL_EVENTS" SAFEZONE_COST_OUTPUT_DIR="$SUMMARY_DIR/safezone-cost" zsh sandbox/run_safezone_cost_matrix.sh
}

run_streams() {
  run_logged nexmark-local "$FORK" env NEXMARK_EVENTS="$RIFT_EVAL_EVENTS" NEXMARK_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" NEXMARK_OUTPUT_DIR="$SUMMARY_DIR/nexmark-local" zsh sandbox/run_nexmark_region_matrix.sh
  run_logged nexmark-beam-default "$FORK" env NEXMARK_BEAM_DEFAULTS=1 NEXMARK_EVENTS="$RIFT_EVAL_EVENTS" NEXMARK_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" NEXMARK_OUTPUT_DIR="$SUMMARY_DIR/nexmark-beam-default" zsh sandbox/run_nexmark_region_matrix.sh
  run_logged yahoo-ad "$FORK" env YAHOO_AD_EVENTS="$RIFT_EVAL_EVENTS" YAHOO_AD_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" YAHOO_AD_OUTPUT_DIR="$SUMMARY_DIR/yahoo-ad" zsh sandbox/run_yahoo_ad_region_matrix.sh
  run_logged riotbench "$FORK" env RIOTBENCH_EVENTS="$RIFT_EVAL_EVENTS" RIOTBENCH_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" RIOTBENCH_OUTPUT_DIR="$SUMMARY_DIR/riotbench" zsh sandbox/run_riotbench_region_matrix.sh
  run_logged wikimedia "$FORK" env WIKIMEDIA_EVENTS="$RIFT_EVAL_EVENTS" WIKIMEDIA_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" WIKIMEDIA_OUTPUT_DIR="$SUMMARY_DIR/wikimedia" zsh sandbox/run_wikimedia_region_matrix.sh
  run_logged common-crawl-wet "$FORK" env COMMON_CRAWL_WET_PAGES="$RIFT_EVAL_EVENTS" COMMON_CRAWL_WET_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" COMMON_CRAWL_WET_OUTPUT_DIR="$SUMMARY_DIR/common-crawl-wet" zsh sandbox/run_common_crawl_wet_matrix.sh
  run_logged common-crawl-page-token "$FORK" env COMMON_CRAWL_WET_PAGES="$RIFT_EVAL_EVENTS" COMMON_CRAWL_WET_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window" COMMON_CRAWL_WET_MODES="heap-immix safezone-improved-32k safezone-rootless-32k rift-trusted-hp rift-trusted-streaming rift-checked-rift rift-checked-page-token rift-checked-safezone-improved-32k rift-checked-safezone-page-token" COMMON_CRAWL_WET_OUTPUT_DIR="$SUMMARY_DIR/common-crawl-page-token" zsh sandbox/run_common_crawl_wet_matrix.sh
  run_logged github-archive "$FORK" env GITHUB_ARCHIVE_EVENTS="$RIFT_EVAL_EVENTS" GITHUB_ARCHIVE_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" GITHUB_ARCHIVE_QUERIES="q1-fields q2-repo-window" GITHUB_ARCHIVE_HEAP_CAPS="uncapped 2G 1400M 1G" GITHUB_ARCHIVE_OUTPUT_DIR="$SUMMARY_DIR/github-archive" zsh sandbox/run_github_archive_region_matrix.sh
  run_logged linear-road "$FORK" env LINEAR_ROAD_EVENTS="$RIFT_EVAL_EVENTS" LINEAR_ROAD_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" LINEAR_ROAD_OUTPUT_DIR="$SUMMARY_DIR/linear-road" zsh sandbox/run_linear_road_region_matrix.sh
}

run_debs() {
  if [[ -z "${DEBS2015_BOTH_INPUT:-}" ]]; then
    log "skipping DEBS; set DEBS2015_BOTH_INPUT for bounded or full-month runs"
    return
  fi
  run_logged debs-runboth "$FORK" env DEBS2015_BOTH_OUTPUT_DIR="$RUN_ROOT/debs-runboth" zsh bench/debs2015/run_both_sample_matrix.sh
  run_logged debs-runboth-instrumented "$FORK" env DEBS2015_BOTH_OUTPUT_DIR="$RUN_ROOT/debs-runboth-instrumented" zsh bench/debs2015/run_both_instrumented_matrix.sh
}

main() {
  set_scale_defaults
  record_environment
  require_clean_repos
  if suite_enabled preflight; then
    run_compile
  fi
  if suite_enabled core; then
    run_core
  fi
  if suite_enabled prior; then
    run_prior_work
  fi
  if suite_enabled checked; then
    run_checked
  fi
  if suite_enabled safezone-cost; then
    run_safezone_cost
  fi
  if suite_enabled streams; then
    run_streams
  fi
  if suite_enabled debs; then
    run_debs
  fi
  find "$SUMMARY_DIR" -name summary.tsv -print | sort >"$RUN_ROOT/summary-files.txt"
  log "complete: $RUN_ROOT"
}

main "$@"
