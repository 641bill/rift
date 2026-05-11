# Benchmark Data Sources

Date: 2026-05-01
Last updated: 2026-05-11 11:56 CEST

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
| LogHub HDFS v1 archive | `/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1.tar.gz` | 161924221 | Real LogHub / LogPAI Hadoop distributed file-system log archive from the Zenodo-hosted LogHub v7 dataset. SHA-256: `6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169`. |
| LogHub HDFS v1 extracted log | `/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1/HDFS.log` | 1576383671 | Extracted real HDFS log with `11175629` lines; used for the 2026-05-08 `LogHubRegionMatrix` q1/q2/q3 follow-up. |
| LogHub Spark archive | `/Users/siyaoliu/rift/cache/benchmark-data/loghub/Spark.tar.gz` | 183474743 | Real LogHub / LogPAI Spark log archive from Zenodo record `8196385`; fetched for the 2026-05-11 richer LogHub top-template search. |
| LogHub Spark extracted logs | `/Users/siyaoliu/rift/cache/benchmark-data/loghub/Spark` | directory | Extracted real Spark logs, `3852` `.log` files, `33236604` total lines, about `2.7G` extracted. First top-template follow-up used the largest container logs. |
| SNAP Twitter ego graph | `/Users/siyaoliu/rift/cache/benchmark-data/yak/snap/twitter_combined.txt.gz` | 10634845 | Real SNAP Twitter ego-network combined edge list. Used for the first `YakRegionMatrix graphreal` row. SHA-256: `d9f99b0e6a53b9204b8c215f41b3c10fb99a1e1e783858c012b06d0d3d4bd129`. |
| SNAP LiveJournal graph | `/Users/siyaoliu/rift/cache/benchmark-data/yak/snap/soc-LiveJournal1.txt.gz` | 259619239 | Real SNAP LiveJournal directed social graph, `68993777` edge-list lines. Used for larger `YakRegionMatrix graphreal` rows. SHA-256: `d7bcd5a87b88c896c35fdb9611e804c3f4033c39b58c4c9ea3ba53c680d516d8`. |
| Theodolite source clone | `/Users/siyaoliu/rift/cache/benchmark-data/theodolite/source` | directory | Ignored local clone of `cau-se/theodolite`; inspected commit `dfa768a25eec3c3f5a57b7d4839a0c255fd6fa7d`. Theodolite provides official UC2/UC4 stream benchmark methodology and load generators, but no static real input file in the repo. |
| DSPBench source clone | `/Users/siyaoliu/rift/cache/benchmark-data/dspbench/source` | directory | Ignored local clone of `GMAP/DSPBench` for real-input stream benchmark triage; inspected commit `00c20da828faf2b960fdb697c61d34cb25461875`. |
| RIoTBench source clone | `/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/source` | directory | Ignored local clone of `dream-lab/riot-bench`; inspected commit `c86414f7f926ed5ae0fab756bb3d82fbfb6e5bf7`. |
| UCI MHEALTH archive | `/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/mhealth/mhealth_dataset.zip` | 75503476 | Public MHEALTH sensor dataset used as the RIoTBench FIT-style real-input candidate. SHA-256: `16ad0ce709f3f00df18f348610d15bce0884b79e2143f57f446493673f02b8e0`. |
| UCI MHEALTH extracted logs | `/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/mhealth/MHEALTHDATASET` | directory | Ten real subject logs, `1215745` total rows, `216M` extracted. |

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
- LogHub Zenodo v7:
  `https://zenodo.org/records/3227177`
- LogHub Spark/Windows/Thunderbird Zenodo record:
  `https://zenodo.org/records/8196385`
- SNAP Twitter ego graph:
  `https://snap.stanford.edu/data/ego-Twitter.html`
- SNAP Twitter-2010 graph:
  `https://snap.stanford.edu/data/twitter-2010.html`
- Stack Exchange data dump:
  `https://archive.org/download/stackexchange`
- Theodolite benchmark source:
  `https://github.com/cau-se/theodolite`
- Theodolite benchmark overview:
  `https://www.theodolite.rocks/theodolite-benchmarks/`
- DSPBench paper/source:
  `https://zenodo.org/records/4671407` and `https://github.com/GMAP/DSPBench`
- RIoTBench source:
  `https://github.com/dream-lab/riot-bench`
- UCI MHEALTH dataset:
  `https://archive.ics.uci.edu/dataset/319/mhealth+dataset`

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
- SPECjbb2005 is retired and JVM-based. If a licensed SPECjbb2005 kit is
  obtained, keep it under ignored cache at
  `/Users/siyaoliu/rift/cache/benchmark-data/specjbb2005/`; record provenance
  here but do not commit licensed source or bytecode. Scala Native evidence
  should be labeled as a SPECjbb2005-workload port or
  Stancu/SPECjbb2005 methodology reproduction, not an official SPEC result.
- LogHub / LogPAI BGL and HDFS v1 have now been downloaded and wired into
  `LogHubRegionMatrix`. Spark has also been downloaded and smoke-tested in
  `LogHubTopTemplatesMatrix`; Windows and Thunderbird remain optional follow-up
  inputs if their query shape materializes more per-record objects than the
  current BGL/HDFS/Spark line-template paths.
- Theodolite source has now been cloned for methodology inspection. It
  includes UC1-UC4 implementations and load generators; the official
  generator simulates industrial active-power measurements, so local use would
  be generated methodology evidence unless paired with a separate real
  industrial-energy trace.
- DSPBench source has now been cloned into ignored cache, and Spike Detection
  plus Fraud Detection are wired into `DSPBenchRegionMatrix`. The bundled
  `dspbench-threads` data includes `sensors.dat` (`79999` usable lines in the
  local parser), `credit-card.dat` (`185000` lines), and `stocks.csv`
  (`411` lines). Treat replayed rows as real-record replay, not fresh
  full-scale real input.
- RIoTBench source has now been cloned into ignored cache. Its bundled real
  SenML samples are tiny (`SYS_sample_data_senml.csv` has `1000` lines,
  `TAXI_sample_data_senml.csv` has `999`, and `FIT_sample_data_senml.csv`
  has `45`), so they are useful for provenance but not for headline rows.
  RIoTBench's FIT configuration points to MHEALTH-style data, so the UCI
  MHEALTH dataset was downloaded as the real-input IoT scale candidate.

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
- `DSPBenchRegionMatrix` now runs Spike Detection q0/q1/q2 over
  `/Users/siyaoliu/rift/cache/benchmark-data/dspbench/source/dspbench-threads/data/sensors.dat`.
  It also runs Fraud Detection q0/q1/q2 over
  `/Users/siyaoliu/rift/cache/benchmark-data/dspbench/source/dspbench-threads/data/credit-card.dat`.
  Fraud q2 is the strongest DSPBench real-input row so far, but checked scoped
  page-token remains speed-gated.
- `RiotBenchRegionMatrix` now accepts `RIOTBENCH_INPUT_KIND=mhealth` and a
  directory path:
  `/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/mhealth/MHEALTHDATASET`.
  It preloads up to `RIOTBENCH_EVENTS` real MHEALTH sensor rows from the
  subject logs.
