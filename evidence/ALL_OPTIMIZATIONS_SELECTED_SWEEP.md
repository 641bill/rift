# All-Optimizations Selected Sweep

Date: 2026-05-16
Last updated: 2026-05-16 01:55 CEST

Status: clean selected follow-up after the current handle-backed checked
allocation promotions. These rows are not a full benchmark-suite rerun. They
are a compact regression/confirmation set for the current optimized defaults:
direct checked epoch, checked page-token, and retained checked epoch.

Child baseline for this sweep:
`/Users/siyaoliu/rift/scala-native-rift` on `feature/rift`, after child
commit `7ae7616d1` (`Promote LogHub retained epoch allocation`).

## Claim Scope

- L1 rows use `RIFT_FINAL_CLEAN=1` and external `/usr/bin/time -l` elapsed/RSS.
- L2 rows use standard benchmark counters for GC/region interpretation.
- Legacy rows are controls for the old generic checked allocation path.
- Generated rows remain generated stressor/methodology evidence, not real-input
  proof.
- GH Archive q2 has a notable L1/L2 ordering difference; use L1 as headline
  timing and L2 only for GC/region interpretation.

## L1 Final-Clean Results

| Benchmark | Input type | API/topology | Mode | External real | Max RSS | Checksum/output | Allowed claim |
|---|---|---|---|---:|---:|---|---|
| StreamFlexDesign throughput 1M x3 | generated StreamFlex-design methodology | direct checked epoch | `gc-heap` | `1.82 s` | `12435456` | checksum `-7120610804659902001`, output `997627` | Natural heap baseline. |
| StreamFlexDesign throughput 1M x3 | generated StreamFlex-design methodology | legacy checked epoch | `checked-epoch-stream-legacy` | `1.09 s` | `8060928` | checksum `-7120610804659902001`, output `997627` | Legacy generic checked allocation control. |
| StreamFlexDesign throughput 1M x3 | generated StreamFlex-design methodology | optimized checked epoch | `checked-epoch-stream` | `0.88 s` | `7913472` | checksum `-7120610804659902001`, output `997627` | Framework API win: `51.6%` faster than heap and `19.3%` faster than legacy checked stream, with lower RSS. |
| StreamFlexDesign throughput 1M x3 | generated StreamFlex-design methodology | checked scoped epoch | `checked-epoch-scoped` | `1.16 s` | `7946240` | checksum `-7120610804659902001`, output `997627` | Safe checked scoped backend control. |
| Common Crawl WET-shaped q2 100k x3 | generated stream/window stressor | natural heap baseline | `heap-immix` | `2.06 s` | `408600576` | checksum `3466044082282182830`, output `92994` | Heap baseline. |
| Common Crawl WET-shaped q2 100k x3 | generated stream/window stressor | legacy checked page-token | `rift-checked-page-token-legacy` | `1.07 s` | `63324160` | checksum `3466044082282182830`, output `92994` | Legacy generic checked allocation control. |
| Common Crawl WET-shaped q2 100k x3 | generated stream/window stressor | optimized checked page-token | `rift-checked-page-token` | `0.96 s` | `63324160` | checksum `3466044082282182830`, output `92994` | Generated page/window win: `53.4%` faster than heap and `10.3%` faster than legacy, with about `84.5%` lower RSS than heap. |
| Common Crawl WET-shaped q2 100k x3 | generated stream/window stressor | checked scoped page-token | `rift-checked-safezone-page-token` | `1.32 s` | `63422464` | checksum `3466044082282182830`, output `92994` | Safe checked scoped page-token control. |
| GH Archive-shaped q2 1M x3 | generated/preloaded NDJSON-shaped event stream | natural heap baseline | `heap-immix` | `1.24 s` | `206569472` | checksum `7294087528134281006`, output `163487` | Heap baseline. |
| GH Archive-shaped q2 1M x3 | generated/preloaded NDJSON-shaped event stream | legacy checked page-token | `rift-checked-page-token-legacy` | `0.85 s` | `44924928` | checksum `7294087528134281006`, output `163487` | Legacy generic checked allocation control. |
| GH Archive-shaped q2 1M x3 | generated/preloaded NDJSON-shaped event stream | optimized checked page-token | `rift-checked-page-token` | `0.80 s` | `44924928` | checksum `7294087528134281006`, output `163487` | Generated/preloaded page-token win: `35.5%` faster than heap and `5.9%` faster than legacy, with about `78.3%` lower RSS than heap. |
| GH Archive-shaped q2 1M x3 | generated/preloaded NDJSON-shaped event stream | checked scoped page-token | `rift-checked-safezone-page-token` | `1.01 s` | `45006848` | checksum `7294087528134281006`, output `163487` | Safe checked scoped page-token control. |
| LogHub top templates 1M x3 | generated retained top-template stream | same-shape retained heap | `heap-retained-drop-anchor` | `1.74 s` | `407355392` | checksum `-761408849270161430`, output `1280` | Retained heap/drop-anchor baseline. |
| LogHub top templates 1M x3 | generated retained top-template stream | legacy checked retained epoch | `checked-epoch-retained-no-traverse-legacy` | `0.75 s` | `36225024` | checksum `-761408849270161430`, output `1280` | Legacy generic checked allocation control. |
| LogHub top templates 1M x3 | generated retained top-template stream | optimized checked retained epoch | `checked-epoch-retained-no-traverse` | `0.69 s` | `36192256` | checksum `-761408849270161430`, output `1280` | Retained-object memory-management win: `60.3%` faster than retained heap and `8.0%` faster than legacy, with about `91.1%` lower RSS than retained heap. |
| LogHub top templates 1M x3 | generated retained top-template stream | checked scoped retained epoch | `checked-scoped-epoch-retained-no-traverse` | `0.80 s` | `36257792` | checksum `-761408849270161430`, output `1280` | Safe checked scoped retained control. |

## L2 Interpretation Results

| Benchmark | Heap L2 | Optimized checked L2 | Legacy checked L2 | Interpretation |
|---|---|---|---|---|
| StreamFlexDesign throughput 1M | `512.645 ms`, GC `98.871 ms`, `118` max collections | `354.761 ms`, GC `0 ms`, rift-op `1.226 ms`, objects `24997627` | `414.123 ms`, GC `0 ms`, rift-op `1.221 ms` | Optimized checked stream removes timed heap GC and reduces generic checked allocation overhead. |
| Common Crawl WET-shaped q2 100k | `509.988 ms`, GC `144.632 ms`, `2` max collections | `357.114 ms`, GC `0 ms`, rift-op `0.991 ms`, objects `13700000` | `391.640 ms`, GC `0 ms`, rift-op `0.997 ms` | Optimized checked page-token is faster than legacy and removes the heap GC component. |
| GH Archive-shaped q2 1M | `272.399 ms`, GC `78.374 ms`, `3` max collections | `284.103 ms`, GC `2.456 ms`, rift-op `0.614 ms`, objects `7502145` | `303.351 ms`, GC `2.464 ms`, rift-op `0.619 ms` | L2 instrumentation changes ordering versus L1; still shows optimized checked improves over legacy and cuts GC/RSS. |
| LogHub top templates 1M | `428.971 ms`, GC `129.966 ms`, `3` max collections | `266.924 ms`, GC `0 ms`, rift-op `1.380 ms`, objects `15509744` | `288.788 ms`, GC `0 ms`, rift-op `1.419 ms` | Retained checked epoch wins on elapsed, GC, and RSS versus retained heap and legacy checked. |

## Raw Run Directories

L1:

- `/private/tmp/rift-allopt-streamflex-20260516/summary.tsv`
- `/private/tmp/rift-allopt-commoncrawl-q2-20260516/summary.tsv`
- `/private/tmp/rift-allopt-gharchive-q2-20260516/summary.tsv`
- `/private/tmp/rift-allopt-loghub-retained-20260516/summary.tsv`

L2:

- `/private/tmp/rift-allopt-streamflex-l2-20260516/summary.tsv`
- `/private/tmp/rift-allopt-commoncrawl-q2-l2-20260516/summary.tsv`
- `/private/tmp/rift-allopt-gharchive-q2-l2-20260516/summary.tsv`
- `/private/tmp/rift-allopt-loghub-retained-l2-20260516/summary.tsv`

## Commands

```sh
cd /Users/siyaoliu/rift/scala-native-rift

RIFT_FINAL_CLEAN=1 \
STREAMFLEX_DESIGN_OUTPUT_DIR=/private/tmp/rift-allopt-streamflex-20260516 \
STREAMFLEX_DESIGN_BUILD=1 \
STREAMFLEX_DESIGN_WORKLOAD=throughput \
STREAMFLEX_DESIGN_EVENTS=1000000 \
STREAMFLEX_DESIGN_BENCHMARK_RUNS=3 \
STREAMFLEX_DESIGN_WARMUPS=1 \
STREAMFLEX_DESIGN_MODES="gc-heap checked-epoch-stream-legacy checked-epoch-stream checked-epoch-scoped" \
zsh sandbox/run_streamflex_design_matrix.sh

STREAMFLEX_DESIGN_OUTPUT_DIR=/private/tmp/rift-allopt-streamflex-l2-20260516 \
STREAMFLEX_DESIGN_BUILD=0 \
STREAMFLEX_DESIGN_WORKLOAD=throughput \
STREAMFLEX_DESIGN_EVENTS=1000000 \
STREAMFLEX_DESIGN_BENCHMARK_RUNS=3 \
STREAMFLEX_DESIGN_WARMUPS=1 \
STREAMFLEX_DESIGN_MODES="gc-heap checked-epoch-stream-legacy checked-epoch-stream checked-epoch-scoped" \
zsh sandbox/run_streamflex_design_matrix.sh

RIFT_FINAL_CLEAN=1 \
COMMON_CRAWL_WET_OUTPUT_DIR=/private/tmp/rift-allopt-commoncrawl-q2-20260516 \
COMMON_CRAWL_WET_BUILD=1 \
COMMON_CRAWL_WET_QUERIES="q2-domain-window" \
COMMON_CRAWL_WET_PAGES=100000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=3 \
COMMON_CRAWL_WET_WARMUPS=1 \
COMMON_CRAWL_WET_MODES="heap-immix rift-checked-page-token-legacy rift-checked-page-token rift-checked-safezone-page-token" \
zsh sandbox/run_common_crawl_wet_matrix.sh

COMMON_CRAWL_WET_OUTPUT_DIR=/private/tmp/rift-allopt-commoncrawl-q2-l2-20260516 \
COMMON_CRAWL_WET_BUILD=0 \
COMMON_CRAWL_WET_QUERIES="q2-domain-window" \
COMMON_CRAWL_WET_PAGES=100000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=3 \
COMMON_CRAWL_WET_WARMUPS=1 \
COMMON_CRAWL_WET_MODES="heap-immix rift-checked-page-token-legacy rift-checked-page-token rift-checked-safezone-page-token" \
zsh sandbox/run_common_crawl_wet_matrix.sh

RIFT_FINAL_CLEAN=1 \
GITHUB_ARCHIVE_OUTPUT_DIR=/private/tmp/rift-allopt-gharchive-q2-20260516 \
GITHUB_ARCHIVE_BUILD=1 \
GITHUB_ARCHIVE_QUERIES="q2-repo-window" \
GITHUB_ARCHIVE_EVENTS=1000000 \
GITHUB_ARCHIVE_BENCHMARK_RUNS=3 \
GITHUB_ARCHIVE_WARMUPS=1 \
GITHUB_ARCHIVE_MODES="heap-immix rift-checked-page-token-legacy rift-checked-page-token rift-checked-safezone-page-token" \
zsh sandbox/run_github_archive_region_matrix.sh

GITHUB_ARCHIVE_OUTPUT_DIR=/private/tmp/rift-allopt-gharchive-q2-l2-20260516 \
GITHUB_ARCHIVE_BUILD=0 \
GITHUB_ARCHIVE_QUERIES="q2-repo-window" \
GITHUB_ARCHIVE_EVENTS=1000000 \
GITHUB_ARCHIVE_BENCHMARK_RUNS=3 \
GITHUB_ARCHIVE_WARMUPS=1 \
GITHUB_ARCHIVE_MODES="heap-immix rift-checked-page-token-legacy rift-checked-page-token rift-checked-safezone-page-token" \
zsh sandbox/run_github_archive_region_matrix.sh

RIFT_FINAL_CLEAN=1 \
LOGHUB_TOP_OUTPUT_DIR=/private/tmp/rift-allopt-loghub-retained-20260516 \
LOGHUB_TOP_BUILD=1 \
LOGHUB_TOP_LINES=1000000 \
LOGHUB_TOP_LINES_PER_EPOCH=25000 \
LOGHUB_TOP_BENCHMARK_RUNS=3 \
LOGHUB_TOP_WARMUPS=1 \
LOGHUB_TOP_INPUT_MODE=generated \
LOGHUB_TOP_MODES="heap-retained-drop-anchor checked-epoch-retained-no-traverse-legacy checked-epoch-retained-no-traverse checked-scoped-epoch-retained-no-traverse" \
zsh sandbox/run_loghub_top_templates_matrix.sh

LOGHUB_TOP_OUTPUT_DIR=/private/tmp/rift-allopt-loghub-retained-l2-20260516 \
LOGHUB_TOP_BUILD=0 \
LOGHUB_TOP_LINES=1000000 \
LOGHUB_TOP_LINES_PER_EPOCH=25000 \
LOGHUB_TOP_BENCHMARK_RUNS=3 \
LOGHUB_TOP_WARMUPS=1 \
LOGHUB_TOP_INPUT_MODE=generated \
LOGHUB_TOP_MODES="heap-retained-drop-anchor checked-epoch-retained-no-traverse-legacy checked-epoch-retained-no-traverse checked-scoped-epoch-retained-no-traverse" \
zsh sandbox/run_loghub_top_templates_matrix.sh
```
