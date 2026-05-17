# Data Footprint And Streaming Plan

Last updated: 2026-05-17 15:08 CEST

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
- `zip:/absolute/path/archive.zip!member/path`;
- `7z:/absolute/path/archive.7z!member/path`;
- `zipdir:/absolute/path/archive.zip!directory/prefix` for multi-file ZIP
  datasets such as MHEALTH.

TPC-H DBGEN tables are now also optional cache artifacts: the Broom Q17 runner
can use `BROOM_Q17_INPUT_MODE=tpch-dbgen` to generate `part.tbl` and
`lineitem.tbl` into a temporary directory for the current matrix case, stream
them in the benchmark, and delete the temporary files afterwards. That keeps
TPC-H evidence reproducible without persisting `cache/tpch-sf*` table
directories.

## Current Biggest Files

Measured on 2026-05-17 after compressed cleanup:

| Path | Size | Classification | Replacement |
|---|---:|---|---|
| `/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows.tar.gz` | `1.6G` | compressed LogHub source | stream `tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows.tar.gz!Windows.log` |
| `/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu.com.7z` | `1.0G` | original compressed StackExchange dump | keep as provenance source |
| `/Users/siyaoliu/rift/cache/benchmark-data/dspbench/DSPBench-00c20da828faf2b960fdb697c61d34cb25461875.zip` | `380M` | compressed DSPBench source archive | keep as provenance source for Spike/Fraud/Log sample inputs |
| `/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu-Posts.xml.gz` | `357M` | derived gzip-converted benchmark input | replace with `7z:/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu.com.7z!Posts.xml` |
| `/Users/siyaoliu/rift/cache/tpch-sf1` | `218M` | cached generated DBGEN tables | replace with per-run `BROOM_Q17_INPUT_MODE=tpch-dbgen` |
| `/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/mhealth/MHEALTHDATASET/*.log.gz` | `~73M` | derived gzip-converted MHEALTH subject logs | replace with `zipdir:/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/mhealth/mhealth_dataset.zip!MHEALTHDATASET` |
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
RIFT_CLEAN_DATA=1 RIFT_CLEAN_DERIVED_ARCHIVE_INPUTS=1 scripts/cleanup-benchmark-data.sh
RIFT_CLEAN_DATA=1 RIFT_CLEAN_DSPBENCH_SOURCE=1 scripts/cleanup-benchmark-data.sh
RIFT_CLEAN_DATA=1 RIFT_CLEAN_TAXI=1 scripts/cleanup-benchmark-data.sh
RIFT_CLEAN_DATA=1 RIFT_CLEAN_OPENJDK=1 scripts/cleanup-benchmark-data.sh
```

The first delete command has already reclaimed roughly `30G` from extracted
duplicates while preserving compressed local sources. A second cleanup converted
TPC-H DBGEN tables, AskUbuntu `Posts.xml`, and MHEALTH subject logs to `.gz`
in place. The local DEBS/NYC taxi `.csv.gz` directories were removed after
finding the official Internet Archive `.7z` archives (`trip_data.7z` about
`3.8G`, `trip_fare.7z` about `1.6G`). Disk availability improved from about
`72G` to about `119G` free across the cleanup passes. The expanded DSPBench
checkout (`920M`) was then replaced by the pinned `380M` source ZIP and
removed after archive-backed smokes passed. Place the official DEBS archives
at:

- `/Users/siyaoliu/rift/cache/benchmark-data/debs2015/trip_data.7z`
- `/Users/siyaoliu/rift/cache/benchmark-data/debs2015/trip_fare.7z`

## Runner Migration Notes

Existing benchmark infrastructure already has real streaming modes for several
families:

- `LOGHUB_TOP_INPUT_MODE=streaming-file`;
- `YAK_TEXT_INPUT_MODE=streaming-file`;
- `THEODOLITE_POWER_INPUT_MODE=streaming-file`;
- gzip-backed graph, GH Archive, Wikimedia, and Common Crawl paths through
  `BenchmarkInputSupport.openBinary`.
- DEBS/NYC taxi sample generation through `join_nyc_taxi_sample.sh`, which now
  selects plain monthly `.csv`, monthly `.csv.gz`, or official `.7z` archive
  members in that order.
- TPC-H Q17 file-backed Broom rows through `BenchmarkInputSupport.openText`;
  cached `part.tbl.gz` and `lineitem.tbl.gz` are valid inputs, but
  `BROOM_Q17_INPUT_MODE=tpch-dbgen` avoids keeping those cached tables.
- RIoTBench MHEALTH inputs through either extracted `.log`/`.log.gz` subject
  logs or the original ZIP with `zipdir:...!MHEALTHDATASET`.
- DSPBench Spike/Fraud/Log inputs through the pinned GitHub source ZIP with
  `zip:/Users/siyaoliu/rift/cache/benchmark-data/dspbench/DSPBench-00c20da828faf2b960fdb697c61d34cb25461875.zip!DSPBench-00c20da828faf2b960fdb697c61d34cb25461875/...`.

Use archive member specs in those same input variables when a compressed
archive is available. Examples:

```sh
LOGHUB_TOP_INPUT_MODE=streaming-file \
LOGHUB_TOP_INPUT='tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows.tar.gz!Windows.log'

THEODOLITE_POWER_INPUT_MODE=streaming-file \
THEODOLITE_POWER_INPUT='zip:/Users/siyaoliu/rift/cache/benchmark-data/theodolite/real-power/household_power_consumption.zip!household_power_consumption.txt'

YAK_TEXT_INPUT_MODE=streaming-file \
YAK_TEXT_INPUT='7z:/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu.com.7z!Posts.xml'

BROOM_Q17_INPUT_MODE=tpch-dbgen \
BROOM_TPCH_SCALE=1 \
zsh /Users/siyaoliu/rift/scala-native-rift/sandbox/run_broom_retained_dataflow_matrix.sh

RIOTBENCH_INPUT='zipdir:/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/mhealth/mhealth_dataset.zip!MHEALTHDATASET' \
RIOTBENCH_INPUT_KIND=mhealth

DEBS2015_LIMIT=1000000 \
DEBS2015_TRIP_DATA_ARCHIVE=/Users/siyaoliu/rift/cache/benchmark-data/debs2015/trip_data.7z \
DEBS2015_TRIP_FARE_ARCHIVE=/Users/siyaoliu/rift/cache/benchmark-data/debs2015/trip_fare.7z \
DEBS2015_JOINED_OUTPUT=/tmp/debs2015-month1-1000000.csv \
zsh /Users/siyaoliu/rift/scala-native-rift/bench/debs2015/join_nyc_taxi_sample.sh
```

The next implementation step, if we want fully extraction-free selected sweeps,
is to update default examples and selected-runner environment variables to use
archive member specs wherever possible.
