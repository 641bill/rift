# Benchmark Data Sources

Date: 2026-05-01
Last updated: 2026-05-07 01:23 CEST

Local data root:
`/Users/siyaoliu/rift/cache/benchmark-data`

This directory is under `cache/`, which is ignored by git. The reproducible
fetch script is tracked at `/Users/siyaoliu/rift/scripts/fetch-benchmark-data.sh`.
The ignored per-download manifest is
`/Users/siyaoliu/rift/cache/benchmark-data/MANIFEST.md`.

## Downloaded Sources

| Benchmark family | Local file | Bytes | Use |
|---|---|---:|---|
| Wikimedia pageviews | `/Users/siyaoliu/rift/cache/benchmark-data/wikimedia/pageviews-20260301-000000.gz` | 45940778 | Real hourly pageview TSV-like input for page/article count windows. |
| Wikimedia clickstream, small | `/Users/siyaoliu/rift/cache/benchmark-data/wikimedia/clickstream-svwiki-2026-03.tsv.gz` | 7261144 | Small real clickstream smoke input. |
| Wikimedia clickstream, large | `/Users/siyaoliu/rift/cache/benchmark-data/wikimedia/clickstream-enwiki-2026-03.tsv.gz` | 508757879 | Real clickstream input for the promising generated Q2/clickstream shape. |
| Common Crawl WET manifest | `/Users/siyaoliu/rift/cache/benchmark-data/common-crawl/CC-MAIN-2026-17/wet.paths.gz` | 200717 | April 2026 WET shard list. |
| Common Crawl WAT manifest | `/Users/siyaoliu/rift/cache/benchmark-data/common-crawl/CC-MAIN-2026-17/wat.paths.gz` | 200716 | April 2026 metadata shard list. |
| Common Crawl WARC manifest | `/Users/siyaoliu/rift/cache/benchmark-data/common-crawl/CC-MAIN-2026-17/warc.paths.gz` | 201605 | April 2026 raw WARC shard list. |
| Common Crawl WET sample | `/Users/siyaoliu/rift/cache/benchmark-data/common-crawl/CC-MAIN-2026-17/CC-MAIN-20260410081153-20260410111153-00000.warc.wet.gz` | 69654327 | First WET shard from the April 2026 path list; use for real WET parser/window tests. |
| Common Crawl WET sample, decompressed | `/Users/siyaoliu/rift/cache/benchmark-data/common-crawl/CC-MAIN-2026-17/CC-MAIN-20260410081153-20260410111153-00000.warc.wet` | 195287894 | Decompressed first WET shard. Use this path for Scala Native real WET runs because WET shards are concatenated gzip streams. |
| Linear Road generator | `/Users/siyaoliu/rift/cache/benchmark-data/linear-road/mitsim.tar.gz` | 102038974 | Official MITSIM generator bundle. |
| Linear Road data driver | `/Users/siyaoliu/rift/cache/benchmark-data/linear-road/datadriver.tar.gz` | 157231 | Official runtime data-driver binary bundle. |
| Linear Road data driver source | `/Users/siyaoliu/rift/cache/benchmark-data/linear-road/datadriver-src.tar.gz` | 157159 | Official data-driver source bundle. |
| Linear Road test data | `/Users/siyaoliu/rift/cache/benchmark-data/linear-road/datadriverTestData.tar.gz` | 116730944 | Official 20-second and 3-hour test input files. |
| Linear Road 20-second test data | `/Users/siyaoliu/rift/cache/benchmark-data/linear-road/test-data/datafile20seconds.dat` | 12669 | Extracted official Data Driver test input for smoke runs. |
| Linear Road 3-hour test data | `/Users/siyaoliu/rift/cache/benchmark-data/linear-road/test-data/datafile3hours.dat` | 596510942 | Extracted official Data Driver test input for larger Linear Road input runs. |
| Linear Road validator | `/Users/siyaoliu/rift/cache/benchmark-data/linear-road/validator.tar.gz` | 14218 | Official validator bundle. |
| Apache Beam source release | `/Users/siyaoliu/rift/cache/benchmark-data/apache-beam/apache-beam-2.73.0-source-release.zip` | 44900494 | Official Beam source archive containing the Java NEXMark generator, model, queries, and configuration. |
| Apache Beam source checksum | `/Users/siyaoliu/rift/cache/benchmark-data/apache-beam/apache-beam-2.73.0-source-release.zip.sha512` | 168 | Official SHA-512 checksum for the Beam source archive. |
| LogHub BGL archive | `/Users/siyaoliu/rift/cache/benchmark-data/loghub/BGL.tar.gz` | 62936967 | Real LogHub / LogPAI Blue Gene/L system log archive from the Zenodo-hosted LogHub dataset. |
| LogHub BGL extracted log | `/Users/siyaoliu/rift/cache/benchmark-data/loghub/BGL/BGL.log` | 743185031 | Extracted real BGL log; first `LogHubRegionMatrix` input with `4747963` lines. |

All downloaded `.gz` files passed `gzip -t`. The Linear Road and LogHub
tarballs were checked with `tar -tzf` or successfully extracted. The Apache
Beam source archive passed the official `sha512` check.

## Upstream Sources

- Wikimedia pageviews: `https://dumps.wikimedia.org/other/pageviews/2026/2026-03/`
- Wikimedia clickstream: `https://dumps.wikimedia.org/other/clickstream/2026-03/`
- Common Crawl April 2026 crawl: `https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/`
- Linear Road official tools: `https://www.cs.brandeis.edu/~linearroad/tools.html`
- Apache Beam releases: `https://beam.apache.org/get-started/downloads/`
- Apache Beam NEXMark docs:
  `https://beam.apache.org/documentation/sdks/java/testing/nexmark/`
- LogHub / LogPAI log datasets:
  `https://github.com/logpai/loghub`
- LogHub dataset table:
  `https://github.com/logpai/loghub/blob/master/docs/datasets.md`

## Apache Beam NEXMark

NEXMark has no static "real input" file: the benchmark data is
deterministically synthesized auction-stream data. The relevant artifact is
therefore the Beam source release containing the generator and configuration.
The downloaded `2.73.0` source archive contains these paths:

- `beam-2.73.0/sdks/java/testing/nexmark/src/main/java/org/apache/beam/sdk/nexmark/NexmarkConfiguration.java`
- `beam-2.73.0/sdks/java/testing/nexmark/src/main/java/org/apache/beam/sdk/nexmark/NexmarkLauncher.java`
- `beam-2.73.0/sdks/java/testing/nexmark/src/main/java/org/apache/beam/sdk/nexmark/NexmarkSuite.java`
- `beam-2.73.0/sdks/java/testing/nexmark/src/main/java/org/apache/beam/sdk/nexmark/sources/generator/GeneratorConfig.java`
- `beam-2.73.0/sdks/java/testing/nexmark/src/main/java/org/apache/beam/sdk/nexmark/sources/generator/Generator.java`
- `beam-2.73.0/sdks/java/testing/nexmark/src/main/java/org/apache/beam/sdk/nexmark/model/{Person,Auction,Bid,Event}.java`

The Beam docs list default workload knobs that matter for a fair Rift
comparison: 100000 generated events, 100 generator threads, sinusoidal event
rate, 100 concurrent auctions, 1000 concurrent persons, 10-second windows,
5-second sliding period, and hot-auction/bidder/seller skew. Those defaults
should become the next NEXMark-lite compatibility target before claiming exact
Beam NEXMark alignment.

## Already Local

DEBS 2015 taxi inputs were already present before this fetch under:

- `/Users/siyaoliu/rift/trip_data`
- `/Users/siyaoliu/rift/trip_fare`

Those directories are also ignored by git.

## No External Real Input Downloaded

- Broom/Naiad, StreamFlex, Yak, and Stancu-style matrices in this repo remain
  methodology/local reproductions unless paper-specific artifacts are later
  obtained.
- LogHub / LogPAI BGL has now been downloaded and wired into
  `LogHubRegionMatrix`. Other LogHub datasets such as HDFS, Spark, or
  Thunderbird remain optional follow-up inputs if their query shape
  materializes more per-record objects than the current BGL line/token/window
  path.

## Next Wiring Work

The downloaded files are not yet wired into the Scala Native benchmark
matrices. The next implementation step should add file-backed modes for:

- `WikimediaRegionMatrix`: `WIKIMEDIA_INPUT=...` and
  `WIKIMEDIA_INPUT_KIND=pageviews|clickstream`.
- `CommonCrawlWetMatrix`: `COMMON_CRAWL_WET_INPUT=...` for the real WET shard,
  plus a preloaded/in-memory control.
- `LinearRoadRegionMatrix`: `LINEAR_ROAD_INPUT=...` using
  `datadriverTestData.tar.gz` extracted test files, or a generated MITSIM file
  once the official generator is configured.

The first wiring pass is now implemented in the Scala Native sandbox:

- `NEXMARK_BEAM_DEFAULTS=1` selects a local generated profile aligned with the
  Beam NEXMark defaults; `NEXMARK_BEAM_SOURCE=...` records the Beam archive
  used as the configuration contract.
- `WIKIMEDIA_INPUT=...` with `WIKIMEDIA_INPUT_KIND=pageviews|clickstream`
  preloads real Wikimedia rows.
- `COMMON_CRAWL_WET_INPUT=...` preloads real WET conversion records; use the
  decompressed `.warc.wet` sample.
- `LINEAR_ROAD_INPUT=...` preloads official Linear Road Data Driver `.dat`
  position reports.
- `LOGHUB_INPUT=...` with `LOGHUB_INPUT_MODE=file-backed` streams extracted
  real LogHub `.log` files. First validated input:
  `/Users/siyaoliu/rift/cache/benchmark-data/loghub/BGL/BGL.log`.
