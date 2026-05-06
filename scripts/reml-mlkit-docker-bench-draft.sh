#!/usr/bin/env bash
set -euo pipefail

ROOT="${RIFT_ROOT:-/Users/siyaoliu/rift}"
MLKIT_TAG="${MLKIT_TAG:-v4.7.5}"
RUN_ID="${RIFT_REML_RUN_ID:-$(date -u '+%Y%m%dT%H%M%SZ')}"
WORKLOADS="${REML_WORKLOADS:-msort fft ratio}"
RUNS="${REML_RUNS:-3}"
MLKIT_DIR="$ROOT/cache/reml/mlkit"
RUN_DIR="$ROOT/cache/reml/runs/$RUN_ID"

mkdir -p "$RUN_DIR"

if [ ! -d "$MLKIT_DIR/.git" ]; then
  echo "Missing MLKit clone at $MLKIT_DIR" >&2
  exit 1
fi

cat > "$RUN_DIR/README.txt" <<EOF
ReML / MLKit draft benchmark
run_id=$RUN_ID
mlkit_tag=$MLKIT_TAG
workloads=$WORKLOADS
runs=$RUNS

IMPORTANT: This is a draft runner. The mode mapping is source-inspected but
not yet paper-confirmed.

Draft modes:
  rg       = MLKit default region inference + tracing GC
  rg-minus = MLKit -disable_spurious_type_variables
  r        = MLKit -no_gc
  mlton    = MLton baseline
EOF

docker run --rm --platform linux/amd64 \
  -v "$ROOT:/rift" \
  -w "/rift/cache/reml/mlkit" \
  -e "MLKIT_TAG=$MLKIT_TAG" \
  -e "RUN_ID=$RUN_ID" \
  -e "WORKLOADS=$WORKLOADS" \
  -e "RUNS=$RUNS" \
  ubuntu:20.04 \
  bash -lc '
    set -euo pipefail
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y build-essential autoconf automake git time libgmp-dev mlton

    git checkout "$MLKIT_TAG"
    ./autobuild
    ./configure --prefix="/rift/cache/reml/mlkit-install-$MLKIT_TAG"
    make -j"$(nproc)" mlkit
    make mlkit_libs
    export SML_LIB=/rift/cache/reml/mlkit

    outdir="/rift/cache/reml/runs/$RUN_ID"
    {
      echo "tool,version"
      printf "mlkit,"
      ./bin/mlkit -V | tr "\n" " "
      printf "\nmlton,"
      mlton 2>&1 | head -n 1 | tr "\n" " "
      printf "\n"
    } > "$outdir/tool-versions.csv"

    source_for() {
      case "$1" in
        msort) echo "test/msort.mlb" ;;
        fft) echo "test/fft.sml" ;;
        ratio) echo "test/ratio-regions.sml" ;;
        tak) echo "test/tak.sml" ;;
        tsp) echo "test/tsp.sml" ;;
        mandel) echo "test/kitmandelbrot.sml" ;;
        life) echo "test/life.sml" ;;
        logic) echo "test/logic.mlb" ;;
        ray) echo "test/ray.mlb" ;;
        nucleic) echo "test/nucleic.mlb" ;;
        bhut) echo "test/barnes-hut.mlb" ;;
        *) echo "unknown workload: $1" >&2; return 1 ;;
      esac
    }

    mlkit_flags_for() {
      case "$1" in
        rg) echo "" ;;
        rg-minus) echo "-disable_spurious_type_variables" ;;
        r) echo "-no_gc" ;;
        *) return 1 ;;
      esac
    }

    echo "workload,mode,run,exit_code" > "$outdir/results-index.csv"

    for workload in $WORKLOADS; do
      src="$(source_for "$workload")"
      for mode in rg rg-minus r; do
        flags="$(mlkit_flags_for "$mode")"
        exe="$outdir/${workload}-${mode}.exe"
        echo "Compiling $workload $mode with MLKit flags: ${flags:-<default>}"
        ./bin/mlkit $flags -o "$exe" "$src" > "$outdir/${workload}-${mode}.compile.out" 2> "$outdir/${workload}-${mode}.compile.err"
        for i in $(seq 1 "$RUNS"); do
          set +e
          /usr/bin/time -v "$exe" -report_gc > "$outdir/${workload}-${mode}.run${i}.out" 2> "$outdir/${workload}-${mode}.run${i}.err"
          code=$?
          set -e
          echo "$workload,$mode,$i,$code" >> "$outdir/results-index.csv"
        done
      done

      exe="$outdir/${workload}-mlton.exe"
      echo "Compiling $workload with MLton"
      mlton -output "$exe" "$src" > "$outdir/${workload}-mlton.compile.out" 2> "$outdir/${workload}-mlton.compile.err"
      for i in $(seq 1 "$RUNS"); do
        set +e
        /usr/bin/time -v "$exe" > "$outdir/${workload}-mlton.run${i}.out" 2> "$outdir/${workload}-mlton.run${i}.err"
        code=$?
        set -e
        echo "$workload,mlton,$i,$code" >> "$outdir/results-index.csv"
      done
    done
  '

echo "Draft ReML/MLKit benchmark outputs: $RUN_DIR"
