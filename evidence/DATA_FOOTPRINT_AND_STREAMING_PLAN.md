# Data Footprint And Streaming Plan

Last updated: 2026-05-17 13:30 CEST

Status: active disk-space triage note. This file separates benchmark inputs
that must stay local from extracted duplicates that can be replaced by
compressed streaming.

## Finding

Streaming input is necessary for bounded memory during a benchmark run, but it
does not by itself save disk space. To save disk space, the benchmark should
read either:

- compressed local files directly (`.gz`);
- a member inside a compressed archive without extracting it;
- or a remote/pipe source in a future adapter.

`BenchmarkInputSupport` now supports these input forms:

- plain path;
- plain `.gz` path, decompressed as it is read;
- `tar.gz:/absolute/path/archive.tar.gz!member/path`;
- `zip:/absolute/path/archive.zip!member/path`.

## Current Biggest Files

Measured on 2026-05-17 after compressed cleanup:

| Path | Size | Classification | Replacement |
|---|---:|---|---|
| `/Users/siyaoliu/rift/trip_data` | `10G` | compressed DEBS/NYC taxi monthly CSVs | `join_nyc_taxi_sample.sh` defaults to `.csv.gz` when plain `.csv` is absent |
| `/Users/siyaoliu/rift/trip_fare` | `6.9G` | compressed DEBS/NYC taxi monthly CSVs | `join_nyc_taxi_sample.sh` defaults to `.csv.gz` when plain `.csv` is absent |
| `/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows.tar.gz` | `1.6G` | compressed LogHub source | stream `tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows.tar.gz!Windows.log` |
| `/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu.com.7z` | `1.0G` | original compressed StackExchange dump | keep as provenance source |
| `/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu-Posts.xml.gz` | `369M` | gzip-converted benchmark input | usable by `YAK_TEXT_INPUT_MODE=streaming-file` |
| `/Users/siyaoliu/rift/cache/tpch-sf1/lineitem.tbl.gz` | `225M` | compressed DBGEN table | usable by `BROOM_Q17_INPUT_MODE=tpch-file` after `BroomRetainedDataflowMatrix` switched to `BenchmarkInputSupport.openText` |
| `/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/mhealth/MHEALTHDATASET/*.log.gz` | `~73M` | gzip-converted MHEALTH subject logs | `RiotBenchRegionMatrix` scans `.log.gz` as well as `.log` |
| `/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1.tar.gz` | `154M` | compressed LogHub source | stream `tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1.tar.gz!HDFS.log` |
| `/Users/siyaoliu/rift/cache/tpch-sf0.1/lineitem.tbl.gz` | `21M` | compressed DBGEN table | same as SF1 |

Non-benchmark disk use:

| Path | Size | Note |
|---|---:|---|
| `/Users/siyaoliu/rift/.git` | `17G` | repository history/worktrees; not benchmark data |
| `/Users/siyaoliu/rift/cache/openjdk-rift` | `2.2G` | HotSpot/backend experiment clone, unrelated to current Scala Native benchmark runs |
| `/Users/siyaoliu/rift/scala-native-rift` | `5.9G` | build outputs and implementation repo |

## Cleanup Commands

Inventory:

```sh
scripts/benchmark-data-footprint.sh
```

Dry-run cleanup:

```sh
scripts/cleanup-benchmark-data.sh
```

Delete extracted duplicates that have compressed streaming replacements:

```sh
RIFT_CLEAN_DATA=1 scripts/cleanup-benchmark-data.sh
```

Optional larger deletes:

```sh
RIFT_CLEAN_DATA=1 RIFT_CLEAN_REGENERABLE=1 scripts/cleanup-benchmark-data.sh
RIFT_CLEAN_DATA=1 RIFT_CLEAN_TAXI=1 scripts/cleanup-benchmark-data.sh
RIFT_CLEAN_DATA=1 RIFT_CLEAN_OPENJDK=1 scripts/cleanup-benchmark-data.sh
```

The first delete command has already reclaimed roughly `30G` from extracted
duplicates while preserving compressed local sources. A second cleanup converted
DEBS/NYC taxi CSVs, TPC-H DBGEN tables, AskUbuntu `Posts.xml`, and MHEALTH
subject logs to `.gz` in place. Disk availability improved from about `72G` to
about `102G` free across the two cleanup passes.

## Runner Migration Notes

Existing benchmark infrastructure already has real streaming modes for several
families:

- `LOGHUB_TOP_INPUT_MODE=streaming-file`;
- `YAK_TEXT_INPUT_MODE=streaming-file`;
- `THEODOLITE_POWER_INPUT_MODE=streaming-file`;
- gzip-backed graph, GH Archive, Wikimedia, and Common Crawl paths through
  `BenchmarkInputSupport.openBinary`.
- DEBS/NYC taxi sample generation through `join_nyc_taxi_sample.sh`, which now
  selects `.csv.gz` defaults when the plain monthly `.csv` files are absent.
- TPC-H Q17 file-backed Broom rows through `BenchmarkInputSupport.openText`,
  so `part.tbl.gz` and `lineitem.tbl.gz` are valid inputs.
- RIoTBench MHEALTH directory inputs after `RiotBenchRegionMatrix` was extended
  to scan `.log.gz` subject logs.

Use archive member specs in those same input variables when a compressed
archive is available. Examples:

```sh
LOGHUB_TOP_INPUT_MODE=streaming-file \
LOGHUB_TOP_INPUT='tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows.tar.gz!Windows.log'

THEODOLITE_POWER_INPUT_MODE=streaming-file \
THEODOLITE_POWER_INPUT='zip:/Users/siyaoliu/rift/cache/benchmark-data/theodolite/real-power/household_power_consumption.zip!household_power_consumption.txt'

YAK_TEXT_INPUT_MODE=streaming-file \
YAK_TEXT_INPUT=/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu-Posts.xml.gz

BROOM_Q17_INPUT_MODE=tpch-file \
BROOM_TPCH_PART_INPUT=/Users/siyaoliu/rift/cache/tpch-sf1/part.tbl.gz \
BROOM_TPCH_LINEITEM_INPUT=/Users/siyaoliu/rift/cache/tpch-sf1/lineitem.tbl.gz
```

The next implementation step, if we want fully extraction-free selected sweeps,
is to update default examples and selected-runner environment variables to use
archive member specs wherever possible.
