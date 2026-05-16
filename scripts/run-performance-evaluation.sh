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
INCLUDE_CONTROLS="${RIFT_EVAL_INCLUDE_CONTROLS:-0}"

mkdir -p "$LOG_DIR" "$SUMMARY_DIR"

log() {
  printf '[rift-eval] %s\n' "$*"
}

suite_enabled() {
  local wanted="$1"
  [[ " $SUITES " == *" all "* || " $SUITES " == *" $wanted "* ]]
}

include_controls() {
  [[ "$INCLUDE_CONTROLS" == "1" || "$INCLUDE_CONTROLS" == "true" || "$INCLUDE_CONTROLS" == "yes" ]]
}

selected_modes() {
  local final_modes="$1"
  local control_modes="$2"
  if include_controls; then
    printf '%s %s' "$final_modes" "$control_modes"
  else
    printf '%s' "$final_modes"
  fi
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
    echo "include_controls=$INCLUDE_CONTROLS"
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
  local dataflow_modes streamflex_modes yak_modes stancu_modes
  dataflow_modes="$(selected_modes "heap improved-safezone rift-checked checked-page-token checked-page-token-scoped" "current-safezone unsafezone-hp rift-hp rift-streaming checked-epoch-fold")"
  streamflex_modes="$(selected_modes "heap improved-safezone rift-checked-safezone-transaction-region" "current-safezone unsafezone-hp rift-hp rift-streaming rift-checked-epoch-buffer rift-checked-safezone-epoch-buffer rift-checked-transaction-region")"
  yak_modes="$(selected_modes "heap improved-safezone yak-runtime" "current-safezone unsafezone-hp rift-hp rift-streaming heap-promotion yak-runtime-promotion")"
  stancu_modes="$(selected_modes "heap improved-safezone" "current-safezone unsafezone-hp rift-hp rift-streaming")"

  run_broom
  run_logged dataflow "$FORK" env DATAFLOW_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" DATAFLOW_MODES="$dataflow_modes" zsh sandbox/run_dataflow_region_matrix.sh
  run_logged streamflex "$FORK" env STREAMFLEX_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" STREAMFLEX_MODES="$streamflex_modes" STREAMFLEX_OUTPUT_DIR="$SUMMARY_DIR/streamflex" zsh sandbox/run_streamflex_region_instrumented_matrix.sh
  run_logged yak "$FORK" env YAK_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" YAK_MODES="$yak_modes" YAK_OUTPUT_DIR="$SUMMARY_DIR/yak" zsh sandbox/run_yak_region_instrumented_matrix.sh
  run_logged stancu "$FORK" env STANCU_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" STANCU_MODES="$stancu_modes" STANCU_OUTPUT_DIR="$SUMMARY_DIR/stancu" zsh sandbox/run_stancu_region_instrumented_matrix.sh
}

run_broom() {
  local broom_modes
  broom_modes="$(selected_modes "heap-gc checked-rift checked-region-scoped" "")"
  run_logged broom-retained-dataflow "$FORK" env BROOM_RECORDS="$RIFT_EVAL_EVENTS" BROOM_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" BROOM_WARMUPS=0 BROOM_MODES="$broom_modes" BROOM_OUTPUT_DIR="$SUMMARY_DIR/broom-retained-dataflow" zsh sandbox/run_broom_retained_dataflow_matrix.sh
}

run_selected_prior() {
  local df_epochs df_docs_per_epoch
  local streamflex_latency_events streamflex_pressure_events
  local specjbb_warehouses specjbb_iterations
  local yak_epochs yak_records_per_epoch yak_sort_records_per_epoch
  local yak_graphchi_edges_per_subinterval yak_workload

  df_epochs=10
  if (( RIFT_EVAL_EVENTS < 100000 )); then
    df_epochs=2
  fi
  df_docs_per_epoch=$(( RIFT_EVAL_EVENTS / df_epochs ))
  if (( df_docs_per_epoch < 1000 )); then
    df_docs_per_epoch=1000
  fi

  streamflex_latency_events=$(( RIFT_EVAL_EVENTS / 20 ))
  if (( streamflex_latency_events < 1000 )); then
    streamflex_latency_events=1000
  fi
  streamflex_pressure_events=$(( RIFT_EVAL_EVENTS / 10 ))
  if (( streamflex_pressure_events < 5000 )); then
    streamflex_pressure_events=5000
  fi

  specjbb_warehouses=4
  specjbb_iterations=$(( RIFT_EVAL_EVENTS / specjbb_warehouses ))
  if (( specjbb_iterations < 1000 )); then
    specjbb_iterations=1000
  fi

  yak_epochs=10
  if (( RIFT_EVAL_EVENTS < 100000 )); then
    yak_epochs=2
  fi
  yak_records_per_epoch=$(( RIFT_EVAL_EVENTS / yak_epochs ))
  if (( yak_records_per_epoch < 1000 )); then
    yak_records_per_epoch=1000
  fi
  yak_sort_records_per_epoch=$(( yak_records_per_epoch / 5 ))
  if (( yak_sort_records_per_epoch < 1000 )); then
    yak_sort_records_per_epoch=1000
  fi
  yak_graphchi_edges_per_subinterval=$(( yak_records_per_epoch / 20 ))
  if (( yak_graphchi_edges_per_subinterval < 1000 )); then
    yak_graphchi_edges_per_subinterval=1000
  fi

  run_broom
  run_logged selected-dataflow "$FORK" env DATAFLOW_EPOCHS="$df_epochs" DATAFLOW_DOCS_PER_EPOCH="$df_docs_per_epoch" DATAFLOW_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" DATAFLOW_MODES="gc-heap region-scoped-rooted checked-epoch-stream checked-epoch-scoped checked-page-token checked-page-token-scoped" zsh sandbox/run_dataflow_region_matrix.sh
  run_logged selected-streamflex-design "$FORK" env STREAMFLEX_DESIGN_EVENTS="$RIFT_EVAL_EVENTS" STREAMFLEX_DESIGN_LATENCY_EVENTS="$streamflex_latency_events" STREAMFLEX_DESIGN_PRESSURE_LATENCY_EVENTS="$streamflex_pressure_events" STREAMFLEX_DESIGN_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" STREAMFLEX_DESIGN_WARMUPS=0 STREAMFLEX_DESIGN_MODES="gc-heap region-scoped-rooted checked-epoch-scoped checked-epoch-stream" STREAMFLEX_DESIGN_OUTPUT_DIR="$SUMMARY_DIR/streamflex-design" zsh sandbox/run_streamflex_design_matrix.sh
  for yak_workload in wordcount graphstep topword graphchi sort; do
    run_logged "selected-yak-${yak_workload}" "$FORK" env YAK_WORKLOAD="$yak_workload" YAK_EPOCHS="$yak_epochs" YAK_RECORDS_PER_EPOCH="$yak_records_per_epoch" YAK_MESSAGES_PER_EPOCH="$yak_records_per_epoch" YAK_SORT_RECORDS_PER_EPOCH="$yak_sort_records_per_epoch" YAK_GRAPHCHI_EDGES_PER_SUBINTERVAL="$yak_graphchi_edges_per_subinterval" YAK_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" YAK_WARMUPS=0 YAK_MODES="heap region-scoped-rooted checked-epoch-stream checked-epoch-scoped" YAK_OUTPUT_DIR="$SUMMARY_DIR/yak-${yak_workload}" zsh sandbox/run_yak_region_instrumented_matrix.sh
  done
  run_logged selected-specjbb2005 "$FORK" env SPECJBB_WAREHOUSES="$specjbb_warehouses" SPECJBB_ITERATIONS_PER_WAREHOUSE="$specjbb_iterations" SPECJBB_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" SPECJBB_WARMUPS=0 SPECJBB_MODES="gc-heap region-scoped-rooted checked-epoch-stream checked-epoch-scoped" SPECJBB_OUTPUT_DIR="$SUMMARY_DIR/specjbb2005-port" zsh sandbox/run_specjbb2005_port_matrix.sh
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
  local nexmark_modes simple_stream_modes common_wet_modes common_page_token_modes linear_modes
  nexmark_modes="$(selected_modes "heap safezone-improved rift-checked" "safezone-current unsafezone-hp rift-hp rift-streaming")"
  simple_stream_modes="$(selected_modes "heap safezone-improved" "safezone-current unsafezone-hp rift-hp rift-streaming")"
  common_wet_modes="$(selected_modes "heap-immix safezone-improved-32k rift-checked-safezone-improved-32k" "safezone-current safezone-improved safezone-chunk-roots safezone-rootless-32k rift-trusted-hp rift-trusted-streaming")"
  common_page_token_modes="$(selected_modes "heap-immix safezone-improved-32k rift-checked-page-token rift-checked-safezone-page-token" "safezone-rootless-32k rift-trusted-hp rift-trusted-streaming rift-checked-rift rift-checked-safezone-improved-32k")"
  linear_modes="$(selected_modes "heap safezone-improved" "safezone-current unsafezone-hp rift-hp rift-streaming")"

  run_logged nexmark-local "$FORK" env NEXMARK_EVENTS="$RIFT_EVAL_EVENTS" NEXMARK_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" NEXMARK_MODES="$nexmark_modes" NEXMARK_OUTPUT_DIR="$SUMMARY_DIR/nexmark-local" zsh sandbox/run_nexmark_region_matrix.sh
  run_logged nexmark-beam-default "$FORK" env NEXMARK_BEAM_DEFAULTS=1 NEXMARK_EVENTS="$RIFT_EVAL_EVENTS" NEXMARK_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" NEXMARK_MODES="$nexmark_modes" NEXMARK_OUTPUT_DIR="$SUMMARY_DIR/nexmark-beam-default" zsh sandbox/run_nexmark_region_matrix.sh
  run_logged yahoo-ad "$FORK" env YAHOO_AD_EVENTS="$RIFT_EVAL_EVENTS" YAHOO_AD_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" YAHOO_AD_MODES="$simple_stream_modes" YAHOO_AD_OUTPUT_DIR="$SUMMARY_DIR/yahoo-ad" zsh sandbox/run_yahoo_ad_region_matrix.sh
  run_logged riotbench "$FORK" env RIOTBENCH_EVENTS="$RIFT_EVAL_EVENTS" RIOTBENCH_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" RIOTBENCH_MODES="$simple_stream_modes" RIOTBENCH_OUTPUT_DIR="$SUMMARY_DIR/riotbench" zsh sandbox/run_riotbench_region_matrix.sh
  run_logged wikimedia "$FORK" env WIKIMEDIA_EVENTS="$RIFT_EVAL_EVENTS" WIKIMEDIA_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" WIKIMEDIA_MODES="$simple_stream_modes" WIKIMEDIA_OUTPUT_DIR="$SUMMARY_DIR/wikimedia" zsh sandbox/run_wikimedia_region_matrix.sh
  run_logged common-crawl-wet "$FORK" env COMMON_CRAWL_WET_PAGES="$RIFT_EVAL_EVENTS" COMMON_CRAWL_WET_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" COMMON_CRAWL_WET_MODES="$common_wet_modes" COMMON_CRAWL_WET_OUTPUT_DIR="$SUMMARY_DIR/common-crawl-wet" zsh sandbox/run_common_crawl_wet_matrix.sh
  run_logged common-crawl-page-token "$FORK" env COMMON_CRAWL_WET_PAGES="$RIFT_EVAL_EVENTS" COMMON_CRAWL_WET_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window" COMMON_CRAWL_WET_MODES="$common_page_token_modes" COMMON_CRAWL_WET_OUTPUT_DIR="$SUMMARY_DIR/common-crawl-page-token" zsh sandbox/run_common_crawl_wet_matrix.sh
  run_logged github-archive "$FORK" env GITHUB_ARCHIVE_EVENTS="$RIFT_EVAL_EVENTS" GITHUB_ARCHIVE_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" GITHUB_ARCHIVE_QUERIES="q1-fields q2-repo-window" GITHUB_ARCHIVE_HEAP_CAPS="uncapped 2G 1400M 1G" GITHUB_ARCHIVE_OUTPUT_DIR="$SUMMARY_DIR/github-archive" zsh sandbox/run_github_archive_region_matrix.sh
  run_logged linear-road "$FORK" env LINEAR_ROAD_EVENTS="$RIFT_EVAL_EVENTS" LINEAR_ROAD_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" LINEAR_ROAD_MODES="$linear_modes" LINEAR_ROAD_OUTPUT_DIR="$SUMMARY_DIR/linear-road" zsh sandbox/run_linear_road_region_matrix.sh
}

run_reml() {
  local reml_modes
  reml_modes="$(selected_modes "gc-heap region-scoped-rooted checked-region-stream checked-region-scoped" "region-scoped-rootless region-hp-rootless region-stream-rootless")"
  run_logged reml-region "$FORK" env REML_BENCHMARK_RUNS="$RIFT_EVAL_RUNS" REML_MODES="$reml_modes" REML_OUTPUT_DIR="$SUMMARY_DIR/reml-region" zsh sandbox/run_reml_region_matrix.sh
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
  if suite_enabled broom; then
    run_broom
  fi
  if suite_enabled selected-prior; then
    run_selected_prior
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
  if suite_enabled reml; then
    run_reml
  fi
  if suite_enabled debs; then
    run_debs
  fi
  find "$SUMMARY_DIR" -name summary.tsv -print | sort >"$RUN_ROOT/summary-files.txt"
  log "complete: $RUN_ROOT"
}

main "$@"
