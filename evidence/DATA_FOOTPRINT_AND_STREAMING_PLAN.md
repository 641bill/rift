# Data Footprint And Streaming Plan

Last updated: 2026-05-17 13:05 CEST

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

Measured on 2026-05-17:

| Path | Size | Classification | Replacement |
|---|---:|---|---|
| `/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows/Windows.log` | `26G` | extracted duplicate | stream `tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows.tar.gz!Windows.log` |
| `/Users/siyaoliu/rift/trip_data` | `27G` | local DEBS/NYC taxi CSV directory | no compressed local replacement in this repo; delete only if DEBS taxi reruns are not needed soon |
| `/Users/siyaoliu/rift/trip_fare` | `18G` | local DEBS/NYC taxi CSV directory | no compressed local replacement in this repo; delete only if DEBS taxi reruns are not needed soon |
| `/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1/HDFS.log` | `1.5G` | extracted duplicate | stream `tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1.tar.gz!HDFS.log` |
| `/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu-Posts.xml` | `1.3G` | extracted 7z member | keep for now unless `7z`/`unar` streaming is installed; current helper does not support `.7z` |
| `/Users/siyaoliu/rift/cache/tpch-sf1/lineitem.tbl` | `725M` | generated DBGEN table | can be deleted and regenerated from `cache/tpch-dbgen` |
| `/Users/siyaoliu/rift/cache/benchmark-data/loghub/BGL/BGL.log` | `709M` | extracted duplicate | stream `tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/BGL.tar.gz!BGL.log` |
| `/Users/siyaoliu/rift/cache/benchmark-data/common-crawl/...warc.wat` | `708M` | decompressed duplicate | use `.warc.wat.gz` directly |
| `/Users/siyaoliu/rift/cache/benchmark-data/linear-road/test-data/datafile3hours.dat` | `569M` | extracted duplicate | stream from `datadriverTestData.tar.gz` once runner commands are updated |
| `/Users/siyaoliu/rift/cache/benchmark-data/theodolite/real-power/household_power_consumption.txt` | `127M` | extracted duplicate | stream `zip:/Users/siyaoliu/rift/cache/benchmark-data/theodolite/real-power/household_power_consumption.zip!household_power_consumption.txt` |

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

The first delete command should reclaim roughly `30G` from extracted duplicates
while preserving compressed local sources. The taxi directories account for
about `45G` more, but they are not currently backed by compressed local copies
inside this repo.

## Runner Migration Notes

Existing benchmark infrastructure already has real streaming modes for several
families:

- `LOGHUB_TOP_INPUT_MODE=streaming-file`;
- `YAK_TEXT_INPUT_MODE=streaming-file`;
- `THEODOLITE_POWER_INPUT_MODE=streaming-file`;
- gzip-backed graph, GH Archive, Wikimedia, and Common Crawl paths through
  `BenchmarkInputSupport.openBinary`.

Use archive member specs in those same input variables when a compressed
archive is available. Examples:

```sh
LOGHUB_TOP_INPUT_MODE=streaming-file \
LOGHUB_TOP_INPUT='tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows.tar.gz!Windows.log'

THEODOLITE_POWER_INPUT_MODE=streaming-file \
THEODOLITE_POWER_INPUT='zip:/Users/siyaoliu/rift/cache/benchmark-data/theodolite/real-power/household_power_consumption.zip!household_power_consumption.txt'
```

The next implementation step, if we want fully extraction-free selected sweeps,
is to update default examples and selected-runner environment variables to use
archive member specs wherever possible.
