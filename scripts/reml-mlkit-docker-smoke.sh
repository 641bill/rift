#!/usr/bin/env bash
set -euo pipefail

ROOT="${RIFT_ROOT:-/Users/siyaoliu/rift}"
MLKIT_TAG="${MLKIT_TAG:-v4.7.5}"
RUN_ID="${RIFT_REML_RUN_ID:-$(date -u '+%Y%m%dT%H%M%SZ')}"
MLKIT_DIR="$ROOT/cache/reml/mlkit"
RUN_DIR="$ROOT/cache/reml/runs/$RUN_ID"

mkdir -p "$RUN_DIR"

if [ ! -d "$MLKIT_DIR/.git" ]; then
  echo "Missing MLKit clone at $MLKIT_DIR" >&2
  echo "Run: git clone https://github.com/melsman/mlkit.git $MLKIT_DIR" >&2
  exit 1
fi

cat > "$RUN_DIR/README.txt" <<EOF
ReML / MLKit Docker smoke
run_id=$RUN_ID
mlkit_tag=$MLKIT_TAG
root=$ROOT

This smoke builds MLKit from the requested public tag in an amd64 Linux
container, then compiles a small set of benchmark sources. It is setup
evidence only. It does not yet claim exact Figure 9 reproduction because the
paper mode flags rg/rg-/r still need verification.
EOF

docker run --rm --platform linux/amd64 \
  -v "$ROOT:/rift" \
  -w "/rift/cache/reml/mlkit" \
  ubuntu:20.04 \
  bash -lc "
    set -euo pipefail
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y build-essential autoconf automake git time libgmp-dev mlton
    git checkout '$MLKIT_TAG'
    ./autobuild
    ./configure --prefix=/rift/cache/reml/mlkit-install-$MLKIT_TAG
    make -j\"\$(nproc)\" mlkit
    make mlkit_libs
    ./bin/mlkit -V | tee /rift/cache/reml/runs/$RUN_ID/mlkit-version.txt
    mlton 2>&1 | head -n 5 | tee /rift/cache/reml/runs/$RUN_ID/mlton-version.txt
    export SML_LIB=/rift/cache/reml/mlkit
    ./bin/mlkit -o /rift/cache/reml/runs/$RUN_ID/msort-mlkit.exe test/msort.mlb
    ./bin/mlkit -o /rift/cache/reml/runs/$RUN_ID/fft-mlkit.exe test/fft.sml
    ./bin/mlkit -o /rift/cache/reml/runs/$RUN_ID/ratio-mlkit.exe test/ratio-regions.sml
  "

echo "MLKit smoke outputs: $RUN_DIR"
