# Real Streaming Input Matrix

Date: 2026-05-11
Last updated: 2026-05-13 13:09 CEST

Status: started. This matrix records only rows that satisfy the
`real-streaming-input` protocol: no full-input preload, incremental source
replay, bounded active state, and matching checksum/output counts.

## Implemented Rows

### LogHub HDFS Top Templates, Streaming-File

Implementation:

- Matrix: `/Users/siyaoliu/rift/scala-native-rift/sandbox/src/main/scala-next/LogHubTopTemplatesMatrix.scala`
- Mode: `LOGHUB_TOP_INPUT_MODE=streaming-file`
- Source: `/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1/HDFS.log`
- Query: retained template-token records per epoch, top template buckets per
  epoch, no close-time record traversal in retained/drop-anchor modes.
- API/topology: retained heap/drop-anchor control, checked retained epoch, and
  checked scoped `EpochTopKByKey`.

20k smoke:

| Mode | L1 external s | L2 median ms | GC ms | RSS bytes | Records | Bytes read | Checksum | Output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `heap-retained-drop-anchor` | `0.49` | `56.121` | `0.000` | `11730944` | `20000` | `3145728` | `8243024414237720723` | `128` |
| `checked-scoped-epoch-topk-retained-no-traverse` | `0.11` | `56.067` | `0.000` | `10436608` | `20000` | `3145728` | `8243024414237720723` | `128` |

1M first candidate row:

| Mode | L1 external s | L2 median ms | GC ms | Runs with GC | RSS bytes | Records | Bytes read | Checksum | Output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `heap-retained-drop-anchor` | `8.10` | `2765.068` | `32.681` | `3/3` | `75595776` | `1000000` | `141557760` | `4142347521733569598` | `1280` |
| `checked-scoped-epoch-retained-no-traverse` | `8.02` | `2672.825` | `0.000` | `0/3` | `12189696` | `1000000` | `141557760` | `4142347521733569598` | `1280` |
| `checked-scoped-epoch-topk-retained-no-traverse` | `8.06` | `2697.653` | `0.000` | `0/3` | `12173312` | `1000000` | `141557760` | `4142347521733569598` | `1280` |

Interpretation:

- This is the first true `real-streaming-input` Rift row: the HDFS log file is
  streamed directly inside each benchmark run, not preloaded into parsed arrays.
- The checked scoped retained/top-k rows remove timed heap GC and cut RSS
  sharply. The reusable checked top-k row is a near-tie/slight L1 throughput
  win over retained heap, while the benchmark-local checked retained path is
  slightly faster in the full streaming loop.
- Heap GC is still modest relative to the full streaming parse/query loop, so
  this is streaming-input retained-object/RSS evidence, not a flagship
  GC-heavy stream result yet.

5M scale-up candidate:

Command shape: `LOGHUB_TOP_INPUT_MODE=streaming-file`,
`LOGHUB_TOP_LINES=5000000`, `LOGHUB_TOP_LINES_PER_EPOCH=100000`,
`LOGHUB_TOP_BENCHMARK_RUNS=3`, modes `heap-retained-drop-anchor` and
`checked-scoped-epoch-topk-retained-no-traverse`.

| Mode | External s | L2 median ms | GC ms | Runs with GC | Records | Bytes read | Checksum | Output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `heap-retained-drop-anchor` | `66.63` | `13244.113` | `109.535` | `3/3` | `5000000` | `700448768` | `-6870681013829878964` | `1600` |
| `checked-scoped-epoch-topk-retained-no-traverse` | `66.95` | `13368.555` | `0.000` | `0/3` | `5000000` | `700448768` | `-6870681013829878964` | `1600` |

Interpretation: scaling the true streaming HDFS top-template row to 5M lines
confirms the same pattern more strongly. Checked scoped removes heap's timed
GC, but heap GC is only about `0.8%` of the per-run L2 median, and external
process time is a near-tie/slight checked loss because line streaming,
template hashing, and top-k query work dominate. This is useful streaming
ceiling/control evidence, not the missing GC-heavy stream flagship.

RSS caveat: this sandboxed run did not collect `/usr/bin/time -l` RSS because
the platform `time` command hit a sandboxed `sysctl kern.clockrate` failure.
Rerun L1 outside the sandbox before using the 5M row as a presentation table.

### GH Archive Byte-Slice q1/q2, Streaming-File

Implementation:

- Matrix: `/Users/siyaoliu/rift/scala-native-rift/sandbox/src/main/scala-next/GithubArchiveRegionMatrix.scala`
- Mode: `GITHUB_ARCHIVE_INPUT_MODE=streaming-file`
- Source: `/Users/siyaoliu/rift/cache/benchmark-data/gharchive/2026-04-01-0.json.gz`
- Parser: `GITHUB_ARCHIVE_FILE_PARSER=byte-slice`
- Queries: q1 field materialization and q2 repo-window aggregation.
- API/topology: heap linked buckets versus checked page-token buckets.

The older `file-backed` GH Archive mode already reread gzip JSON lines inside
each timed run and did not retain parsed arrays. The new `streaming-file` mode
is the explicit `real-streaming-input` label for the same bounded replay shape;
`file-backed` remains a legacy alias.

20k smoke:

| Query | Mode | External s | L2 median ms | GC ms | RSS bytes | Records | Checksum | Output |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| q1-fields | `gc-heap` | `1.26` | `390.712` | `0.000` | `30654464` | `20000` | `-6657681314549385601` | `260000` |
| q1-fields | `rift-checked-page-token` | `0.99` | `391.972` | `0.000` | `36208640` | `20000` | `-6657681314549385601` | `260000` |
| q2-repo-window | `gc-heap` | `0.99` | `388.237` | `0.000` | `30638080` | `20000` | `-6670490017219798393` | `3874` |
| q2-repo-window | `rift-checked-page-token` | `0.99` | `389.822` | `0.000` | `36208640` | `20000` | `-6670490017219798393` | `3874` |

100k L2 triage, 3 measured runs:

| Query | Mode | External s | L2 median ms | Median GC ms | Max GC ms | Runs with GC | RSS bytes | Records | Checksum | Output |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| q1-fields | `gc-heap` | `10.39` | `2325.844` | `0.000` | `71.641` | `1/3` | `169263104` | `100000` | `-3372776855869651174` | `1300000` |
| q1-fields | `rift-checked-page-token` | `9.62` | `1989.461` | `0.000` | `0.000` | `0/3` | `162054144` | `100000` | `-3372776855869651174` | `1300000` |
| q2-repo-window | `gc-heap` | `9.38` | `2151.431` | `0.000` | `72.159` | `1/3` | `169443328` | `100000` | `-1071649140102953205` | `15877` |
| q2-repo-window | `rift-checked-page-token` | `9.16` | `2016.085` | `0.000` | `0.000` | `0/3` | `162381824` | `100000` | `-1071649140102953205` | `15877` |

Interpretation:

- GH Archive now has an explicit true streaming-input q1/q2 path. It streams
  gzip NDJSON lines during each timed run and keeps memory bounded by active
  page/window buckets plus durable counters.
- The 100k triage is promising but modest: checked page-token removes heap's
  GC tail in the sampled runs and is faster on q1/q2, but median heap GC is
  still zero and parser/byte-slice extraction dominates external time.
- Classification: real-streaming-input page/window RSS/tail evidence, not a
  flagship GC-heavy stream row. Scale only if heap caps or larger multi-hour
  input expose material GC/RSS/tail pressure.

## Planned Conversions

| Candidate | First streaming query | Status |
|---|---|---|
| GH Archive | byte-slice NDJSON q1/q2 with event-time where cheap | explicit `streaming-file` q1/q2 smoke and 100k triage complete; scale only if heap caps or multi-hour input expose pressure |
| Theodolite power | real power trace downsampling/window aggregation | next time-series target |
| StackExchange/StackOverflow | post text top-word/top-template by epoch | after LogHub/GH streaming controls |
| SNAP/Yak graph edge replay | direct `RiftRegion.epoch` edge-stream epochs | disk/time preflight first |
| DSPBench Fraud/Log | line-stream q2 regression rows | convert only if retained pressure remains material |
