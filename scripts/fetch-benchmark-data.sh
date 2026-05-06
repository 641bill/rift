#!/usr/bin/env bash
set -euo pipefail

ROOT="${RIFT_ROOT:-/Users/siyaoliu/rift}"
DATA_ROOT="${RIFT_BENCH_DATA_ROOT:-$ROOT/cache/benchmark-data}"
MANIFEST="$DATA_ROOT/MANIFEST.md"
BEAM_VERSION="${RIFT_BEAM_VERSION:-2.73.0}"

mkdir -p "$DATA_ROOT"

fetch() {
  local url="$1"
  local dest="$2"
  mkdir -p "$(dirname "$dest")"
  if [[ -s "$dest" ]]; then
    echo "present  $dest"
  else
    echo "fetch    $url"
    curl -L --fail --continue-at - --retry 3 --retry-delay 5 --output "$dest" "$url"
  fi
  printf '%s\n' "$url" > "$dest.url"
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$dest" > "$dest.sha256"
  fi
}

bytes() {
  if [[ -e "$1" ]]; then
    wc -c < "$1" | tr -d ' '
  else
    printf 'missing'
  fi
}

record() {
  local label="$1"
  local path="$2"
  local source="$3"
  printf '| %s | `%s` | %s | %s |\n' "$label" "$path" "$(bytes "$path")" "$source" >> "$MANIFEST"
}

fetch_wikimedia() {
  local dir="$DATA_ROOT/wikimedia"
  fetch "https://dumps.wikimedia.org/other/pageviews/2026/2026-03/pageviews-20260301-000000.gz" \
    "$dir/pageviews-20260301-000000.gz"
  fetch "https://dumps.wikimedia.org/other/clickstream/2026-03/clickstream-svwiki-2026-03.tsv.gz" \
    "$dir/clickstream-svwiki-2026-03.tsv.gz"
  if [[ "${RIFT_FETCH_LARGE:-1}" == "1" ]]; then
    fetch "https://dumps.wikimedia.org/other/clickstream/2026-03/clickstream-enwiki-2026-03.tsv.gz" \
      "$dir/clickstream-enwiki-2026-03.tsv.gz"
  else
    echo "skip     enwiki clickstream; set RIFT_FETCH_LARGE=1 to fetch it"
  fi
}

fetch_common_crawl() {
  local dir="$DATA_ROOT/common-crawl/CC-MAIN-2026-17"
  fetch "https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/wet.paths.gz" "$dir/wet.paths.gz"
  fetch "https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/wat.paths.gz" "$dir/wat.paths.gz"
  fetch "https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/warc.paths.gz" "$dir/warc.paths.gz"

  gzip -dc "$dir/wet.paths.gz" > "$dir/wet.paths.txt"
  gzip -dc "$dir/wat.paths.gz" > "$dir/wat.paths.txt"
  gzip -dc "$dir/warc.paths.gz" > "$dir/warc.paths.txt"

  if [[ "${RIFT_FETCH_COMMON_CRAWL_SAMPLE:-1}" == "1" ]]; then
    local wet_path
    wet_path="$(sed -n '1p' "$dir/wet.paths.txt")"
    if [[ -n "$wet_path" ]]; then
      local wet_gz="$dir/$(basename "$wet_path")"
      fetch "https://data.commoncrawl.org/$wet_path" "$wet_gz"
      gzip -dc "$wet_gz" > "${wet_gz%.gz}"
    fi
  else
    echo "skip     Common Crawl WET sample; set RIFT_FETCH_COMMON_CRAWL_SAMPLE=1 to fetch it"
  fi

  if [[ "${RIFT_FETCH_COMMON_CRAWL_WAT_SAMPLE:-0}" == "1" ]]; then
    local wat_path
    wat_path="$(sed -n '1p' "$dir/wat.paths.txt")"
    if [[ -n "$wat_path" ]]; then
      local wat_gz="$dir/$(basename "$wat_path")"
      fetch "https://data.commoncrawl.org/$wat_path" "$wat_gz"
      gzip -dc "$wat_gz" > "${wat_gz%.gz}"
    fi
  else
    echo "skip     Common Crawl WAT sample; set RIFT_FETCH_COMMON_CRAWL_WAT_SAMPLE=1 to fetch it"
  fi
}

fetch_linear_road() {
  local dir="$DATA_ROOT/linear-road"
  fetch "https://www.cs.brandeis.edu/~linearroad/files/mitsim.tar.gz" "$dir/mitsim.tar.gz"
  fetch "https://www.cs.brandeis.edu/~linearroad/files/datadriver.tar.gz" "$dir/datadriver.tar.gz"
  fetch "https://www.cs.brandeis.edu/~linearroad/files/datadriver-src.tar.gz" "$dir/datadriver-src.tar.gz"
  fetch "https://www.cs.brandeis.edu/~linearroad/files/datadriverTestData.tar.gz" "$dir/datadriverTestData.tar.gz"
  fetch "https://www.cs.brandeis.edu/~linearroad/files/validator.tar.gz" "$dir/validator.tar.gz"
  mkdir -p "$dir/test-data"
  tar -xzf "$dir/datadriverTestData.tar.gz" -C "$dir/test-data"
}

fetch_beam_nexmark() {
  local dir="$DATA_ROOT/apache-beam"
  fetch "https://downloads.apache.org/beam/$BEAM_VERSION/apache-beam-$BEAM_VERSION-source-release.zip" \
    "$dir/apache-beam-$BEAM_VERSION-source-release.zip"
  fetch "https://downloads.apache.org/beam/$BEAM_VERSION/apache-beam-$BEAM_VERSION-source-release.zip.sha512" \
    "$dir/apache-beam-$BEAM_VERSION-source-release.zip.sha512"
  if command -v shasum >/dev/null 2>&1; then
    (
      cd "$dir"
      shasum -a 512 -c "apache-beam-$BEAM_VERSION-source-release.zip.sha512"
    )
  fi
}

fetch_gharchive() {
  if [[ "${RIFT_FETCH_GHARCHIVE_SAMPLE:-0}" != "1" ]]; then
    echo "skip     GH Archive sample; set RIFT_FETCH_GHARCHIVE_SAMPLE=1 to fetch it"
    return
  fi

  local hours="${RIFT_GHARCHIVE_HOURS:-${RIFT_GHARCHIVE_HOUR:-2026-04-01-0}}"
  local dir="$DATA_ROOT/gharchive"
  local hour
  for hour in $hours; do
    fetch "https://data.gharchive.org/${hour}.json.gz" "$dir/${hour}.json.gz"
  done
}

fetch_loghub() {
  if [[ "${RIFT_FETCH_LOGHUB_SAMPLE:-0}" != "1" ]]; then
    echo "skip     LogHub sample; set RIFT_FETCH_LOGHUB_SAMPLE=1 to fetch it"
    return
  fi

  local dir="$DATA_ROOT/loghub"
  local datasets="${RIFT_LOGHUB_DATASETS:-HDFS BGL}"
  local dataset
  for dataset in $datasets; do
    case "$dataset" in
      HDFS)
        fetch "https://zenodo.org/records/1147681/files/HDFS.tar.gz?download=1" \
          "$dir/HDFS.tar.gz"
        mkdir -p "$dir/HDFS"
        tar -xzf "$dir/HDFS.tar.gz" -C "$dir/HDFS"
        ;;
      BGL)
        fetch "https://zenodo.org/records/1147681/files/BGL.tar.gz?download=1" \
          "$dir/BGL.tar.gz"
        mkdir -p "$dir/BGL"
        tar -xzf "$dir/BGL.tar.gz" -C "$dir/BGL"
        ;;
      *)
        echo "unknown LogHub dataset '$dataset'; expected HDFS or BGL" >&2
        exit 1
        ;;
    esac
  done
}

write_manifest() {
  cat > "$MANIFEST" <<EOF
# Rift Benchmark Data Manifest

Generated by \`scripts/fetch-benchmark-data.sh\`.

Data root: \`$DATA_ROOT\`

These files are local benchmark inputs or source bundles. They live under
\`cache/\`, which is ignored by git.

| Dataset | Local file | Bytes | Source |
|---|---|---:|---|
EOF

  record "Wikimedia pageviews, one hour" "$DATA_ROOT/wikimedia/pageviews-20260301-000000.gz" "https://dumps.wikimedia.org/other/pageviews/2026/2026-03/"
  record "Wikimedia clickstream svwiki, March 2026" "$DATA_ROOT/wikimedia/clickstream-svwiki-2026-03.tsv.gz" "https://dumps.wikimedia.org/other/clickstream/2026-03/"
  record "Wikimedia clickstream enwiki, March 2026" "$DATA_ROOT/wikimedia/clickstream-enwiki-2026-03.tsv.gz" "https://dumps.wikimedia.org/other/clickstream/2026-03/"
  record "Common Crawl WET path list" "$DATA_ROOT/common-crawl/CC-MAIN-2026-17/wet.paths.gz" "https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/"
  record "Common Crawl WAT path list" "$DATA_ROOT/common-crawl/CC-MAIN-2026-17/wat.paths.gz" "https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/"
  record "Common Crawl WARC path list" "$DATA_ROOT/common-crawl/CC-MAIN-2026-17/warc.paths.gz" "https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/"
  local first_wet
  first_wet="$(find "$DATA_ROOT/common-crawl/CC-MAIN-2026-17" -maxdepth 1 -name 'CC-MAIN-*.warc.wet.gz' | sort | sed -n '1p')"
  if [[ -n "$first_wet" ]]; then
    record "Common Crawl first WET shard sample" "$first_wet" "https://data.commoncrawl.org/"
    record "Common Crawl first WET shard decompressed" "${first_wet%.gz}" "https://data.commoncrawl.org/"
  fi
  local first_wat
  first_wat="$(find "$DATA_ROOT/common-crawl/CC-MAIN-2026-17" -maxdepth 1 -name 'CC-MAIN-*.warc.wat.gz' | sort | sed -n '1p')"
  if [[ -n "$first_wat" ]]; then
    record "Common Crawl first WAT shard sample" "$first_wat" "https://data.commoncrawl.org/"
    record "Common Crawl first WAT shard decompressed" "${first_wat%.gz}" "https://data.commoncrawl.org/"
  fi
  record "Linear Road MITSIM generator" "$DATA_ROOT/linear-road/mitsim.tar.gz" "https://www.cs.brandeis.edu/~linearroad/tools.html"
  record "Linear Road data driver binary" "$DATA_ROOT/linear-road/datadriver.tar.gz" "https://www.cs.brandeis.edu/~linearroad/tools.html"
  record "Linear Road data driver source" "$DATA_ROOT/linear-road/datadriver-src.tar.gz" "https://www.cs.brandeis.edu/~linearroad/tools.html"
  record "Linear Road test input data" "$DATA_ROOT/linear-road/datadriverTestData.tar.gz" "https://www.cs.brandeis.edu/~linearroad/tools.html"
  record "Linear Road 20-second test input" "$DATA_ROOT/linear-road/test-data/datafile20seconds.dat" "https://www.cs.brandeis.edu/~linearroad/tools.html"
  record "Linear Road 3-hour test input" "$DATA_ROOT/linear-road/test-data/datafile3hours.dat" "https://www.cs.brandeis.edu/~linearroad/tools.html"
  record "Linear Road validator" "$DATA_ROOT/linear-road/validator.tar.gz" "https://www.cs.brandeis.edu/~linearroad/tools.html"
  record "Apache Beam source release with Java NEXMark" "$DATA_ROOT/apache-beam/apache-beam-$BEAM_VERSION-source-release.zip" "https://beam.apache.org/get-started/downloads/"
  record "Apache Beam source SHA-512" "$DATA_ROOT/apache-beam/apache-beam-$BEAM_VERSION-source-release.zip.sha512" "https://beam.apache.org/get-started/downloads/"
  local gharchive_sample
  while IFS= read -r gharchive_sample; do
    if [[ -n "$gharchive_sample" ]]; then
      record "GH Archive hourly JSON events" "$gharchive_sample" "https://www.gharchive.org/"
    fi
  done < <(find "$DATA_ROOT/gharchive" -maxdepth 1 -name '*.json.gz' 2>/dev/null | sort)
  local loghub_archive
  while IFS= read -r loghub_archive; do
    if [[ -n "$loghub_archive" ]]; then
      record "LogHub archive" "$loghub_archive" "https://zenodo.org/records/1147681"
    fi
  done < <(find "$DATA_ROOT/loghub" -maxdepth 1 \( -name '*.tar.gz' -o -name '*.zip' \) 2>/dev/null | sort)
  local loghub_log
  while IFS= read -r loghub_log; do
    if [[ -n "$loghub_log" ]]; then
      record "LogHub extracted log" "$loghub_log" "https://github.com/logpai/loghub"
    fi
  done < <(find "$DATA_ROOT/loghub" -type f \( -name '*.log' -o -name '*.txt' \) 2>/dev/null | sort)
}

fetch_wikimedia
fetch_common_crawl
fetch_linear_road
fetch_beam_nexmark
fetch_gharchive
fetch_loghub
write_manifest

echo "Wrote $MANIFEST"
