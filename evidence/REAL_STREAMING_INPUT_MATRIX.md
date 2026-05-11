# Real Streaming Input Matrix

Date: 2026-05-11
Last updated: 2026-05-11 23:49 CEST

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

## Planned Conversions

| Candidate | First streaming query | Status |
|---|---|---|
| GH Archive | byte-slice NDJSON q1/q2 with event-time where cheap | next conversion target |
| Theodolite power | real power trace downsampling/window aggregation | next time-series target |
| StackExchange/StackOverflow | post text top-word/top-template by epoch | after LogHub/GH streaming controls |
| SNAP/Yak graph edge replay | direct `RiftRegion.epoch` edge-stream epochs | disk/time preflight first |
| DSPBench Fraud/Log | line-stream q2 regression rows | convert only if retained pressure remains material |
