# Real Streaming Input Matrix

Date: 2026-05-11
Last updated: 2026-05-16 17:45 CEST

Status: started. This matrix records only rows that satisfy the
`real-streaming-input` protocol: no full-input preload, incremental source
replay, bounded active state, and matching checksum/output counts.

## Implemented Rows

### Yak AskUbuntu Topwordreal, Streaming-File

Implementation:

- Matrix: `/Users/siyaoliu/rift/scala-native-rift/sandbox/src/main/scala-next/YakRegionMatrix.scala`
- Mode: `YAK_TEXT_INPUT_MODE=streaming-file`
- Source: `/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu-Posts.xml`
- Query: stream Stack Exchange `Posts.xml` lines, scan `Title` and `Body`
  attributes, tokenize ASCII words into epoch-local `WordRecord` objects, and
  compute per-epoch top-word checksums.
- API/topology: direct `RiftRegion.epoch` over retained epoch records. The
  reusable `EpochTopKByKey` streaming path is not wired yet.

20k smoke:

| Mode | L1 external s | L2 median ms | GC ms | RSS bytes | Records | Checksum |
|---|---:|---:|---:|---:|---:|---:|
| `gc-heap` | `0.02` | `7.299` | `0.190` | `9584640` | `20000` | `-1562585445518255472` |
| `region-scoped-rooted` | `0.02` | `7.016` | `0.269` | `9551872` | `20000` | `-1562585445518255472` |
| `checked-epoch-scoped` | `0.02` | `7.258` | `0.273` | `9551872` | `20000` | `-1562585445518255472` |
| `checked-epoch-stream` | `0.02` | `7.008` | `0.283` | `9584640` | `20000` | `-1562585445518255472` |

1M first candidate row:

| Mode | L1 external s | L2 median ms | GC ms | RSS bytes | Records | Checksum |
|---|---:|---:|---:|---:|---:|---:|
| `gc-heap` | `0.96` | `301.923` | `3.677` | `39649280` | `1000000` | `8501908365116000626` |
| `region-scoped-rooted` | `0.91` | `296.793` | `0.000` | `12943360` | `1000000` | `8501908365116000626` |
| `checked-epoch-scoped` | `0.91` | `296.119` | `0.000` | `12943360` | `1000000` | `8501908365116000626` |
| `checked-epoch-stream` | `0.90` | `294.197` | `0.000` | `12943360` | `1000000` | `8501908365116000626` |

Interpretation:

- This is a true `real-streaming-input` row: the XML file is consumed during
  the benchmark and no full replay token array is retained.
- It is not GC-heavy at this scale. Heap median timed GC is `3.677 ms` on a
  `301.923 ms` L2 loop, so parser/token scanning remains the dominant cost.
- Checked epoch rows still remove timed heap GC, reduce L1 RSS from about
  `39.6 MB` to `13.0 MB`, and improve median L1 elapsed by about `5-6%`.
  Classify as
  modest real-streaming-input RSS/fixed-memory evidence, not as the flagship
  GC-heavy stream case study.

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

### LogHub Windows Top Templates, Streaming-File

Implementation:

- Matrix: `/Users/siyaoliu/rift/scala-native-rift/sandbox/src/main/scala-next/LogHubTopTemplatesMatrix.scala`
- Mode: `LOGHUB_TOP_INPUT_MODE=streaming-file`
- Source: `/Users/siyaoliu/rift/cache/benchmark-data/loghub/Windows/Windows.log`
- Query: retained template-token records per epoch, top template buckets per
  epoch, no close-time record traversal in retained/drop-anchor modes.
- API/topology: natural heap, retained heap/drop-anchor, checked retained
  scoped epoch, and checked scoped `EpochTopKByKey`.

The local Windows file has `114,608,388` lines, so it gives a larger
same-machine real streaming source than HDFS without fetching new data.

1M candidate row:

| Mode | L1 external s | L1 RSS bytes | L2 median ms | Median GC ms | Max GC ms | Runs with GC | Records | Bytes read | Checksum | Output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `heap-natural` | `12.68` | `147046400` | `4240.088` | `26.020` | `28.598` | `3/3` | `1000000` | `242221056` | `-164656507663075219` | `1280` |
| `heap-retained-drop-anchor` | `12.68` | `147013632` | `4255.379` | `30.532` | `55.161` | `3/3` | `1000000` | `242221056` | `-164656507663075219` | `1280` |
| `checked-scoped-epoch-retained-no-traverse` | `12.64` | `14499840` | `4235.391` | `0.000` | `0.000` | `0/3` | `1000000` | `242221056` | `-164656507663075219` | `1280` |
| `checked-scoped-epoch-topk-retained-no-traverse` | `12.64` | `14483456` | `4226.219` | `0.000` | `0.000` | `0/3` | `1000000` | `242221056` | `-164656507663075219` | `1280` |

Heap-cap follow-up:

| Mode | Heap cap | Status | L1 external s | RSS bytes | Checksum | Output |
|---|---:|---|---:|---:|---:|---:|
| `heap-natural` | `128M` | completed | `13.29` | `138133504` | `-164656507663075219` | `1280` |
| `heap-natural` | `64M` | completed | `13.20` | `71106560` | `-164656507663075219` | `1280` |
| `heap-retained-drop-anchor` | `64M` | completed | `13.20` | `71122944` | `-164656507663075219` | `1280` |
| `checked-scoped-epoch-topk-retained-no-traverse` | uncapped | completed | `12.73` | `14499840` | `-164656507663075219` | `1280` |

Interpretation:

- This is true real-streaming-input evidence over a much larger local LogHub
  source. It does not preload parsed rows.
- Checked scoped retained/top-k rows are near ties on elapsed and cut L1 RSS
  about `90%` versus uncapped heap.
- Heap completes at a `64M` cap, so this is not a heap-failure row. The cap
  still leaves heap around `71 MB` RSS and slightly slower than the checked
  top-k row at about `14.5 MB`.
- Heap GC remains below `1%` of measured L2 work. This is RSS/fixed-memory
  streaming evidence, not the missing GC-heavy stream flagship.
- Use L1 RSS for presentation. The L2 harness computes a heap baseline for
  checksum validation in the same process before checked modes, which can
  inflate external RSS for checked L2 rows.

### LogHub HDFS q3 Template/Session, Streaming-File

Implementation:

- Matrix: `/Users/siyaoliu/rift/scala-native-rift/sandbox/src/main/scala-next/LogHubRegionMatrix.scala`
- Mode: `LOGHUB_INPUT_MODE=streaming-file`
- Source: `/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1/HDFS.log`
- Query: richer `q3-template-session`, which allocates a base log record,
  template-token records, and a session-candidate record for each streamed
  line, then counts session summaries per bucket/window.
- API/topology: checked scoped page/window token over real streaming log
  replay. Direct epoch/indexable modes remain generated-only for this matrix.

1M L2 standard-stats row:

| Mode | L2 median ms | Median GC ms | Max GC ms | Runs with GC | RSS bytes | Records | Checksum | Output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `gc-heap` | `8546.791` | `97.322` | `131.533` | `2/3` | `1144930304` | `1000000` | `1444622413215935538` | `81897` |
| `region-scoped-rooted` | `8567.481` | `53.908` | `60.798` | `2/3` | `693338112` | `1000000` | `1444622413215935538` | `81897` |
| `checked-page-token` | `8763.838` | `44.517` | `58.455` | `2/3` | `693305344` | `1000000` | `1444622413215935538` | `81897` |

1M L1 final-clean row:

| Mode | L1 external s | User s | Sys s | RSS bytes | Records | Checksum | Output |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gc-heap` | `26.88` | `26.50` | `0.29` | `861995008` | `1000000` | `1444622413215935538` | `81897` |
| `region-scoped-rooted` | `30.17` | `29.78` | `0.27` | `130220032` | `1000000` | `1444622413215935538` | `81897` |
| `checked-page-token` | `30.29` | `30.08` | `0.15` | `130252800` | `1000000` | `1444622413215935538` | `81897` |

Interpretation:

- This is true streaming-input replay: the HDFS file is consumed during each
  timed run, not preloaded into parsed arrays.
- It is a large RSS/fixed-memory win and a GC-tail reduction, but not a
  throughput win. Checked scoped page-token is about `12.7%` slower than heap
  in L1 while cutting RSS from about `862 MB` to about `130 MB`.
- L2 confirms heap GC is visible but not dominant: `97.322 ms` median GC on an
  `8546.791 ms` heap loop. Parser/template/session query CPU dominates.
- Decision: keep as richer LogHub streaming session/template control evidence
  and park unless heap caps, latency, or a more naturally retained session
  workload exposes larger fixed-memory pressure.

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

### Theodolite Power q2, Streaming-File

Implementation:

- Matrix: `/Users/siyaoliu/rift/scala-native-rift/sandbox/src/main/scala-next/TheodolitePowerRegionMatrix.scala`
- Mode: `THEODOLITE_POWER_INPUT_MODE=streaming-file`
- Source: `/Users/siyaoliu/rift/cache/benchmark-data/theodolite/real-power/household_power_consumption.txt`
- Query: q2 hierarchical aggregation over real UCI household power-meter
  measurements.
- API/topology: natural heap, rooted SafeZone scoped epochs, checked scoped
  `RiftRegion.epoch`, and checked stream epoch with handle-backed allocation.
- Parser: shared byte-line reader plus reusable semicolon-delimited byte-field
  cursor. This supersedes the first streaming-file row that used
  `BufferedReader.readLine()` plus `String.split`.

1M L2 triage, 3 measured runs:

| Mode | External s | L2 median ms | Median GC ms | Max GC ms | Runs with GC | RSS bytes | Records | Checksum | Output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gc-heap` | `4.89` | `1054.432` | `19.906` | `20.980` | `3/3` | `75284480` | `1000000` | `7683095093045065342` | `40960` |
| `checked-epoch-stream-legacy` | `4.71` | `1006.176` | `0.000` | `0.000` | `0/3` | `78495744` | `1000000` | `7683095093045065342` | `40960` |
| `checked-epoch-stream` | `4.74` | `993.191` | `0.000` | `0.000` | `0/3` | `78495744` | `1000000` | `7683095093045065342` | `40960` |
| `checked-epoch-stream-open-handle` | `4.72` | `1002.330` | `0.000` | `0.000` | `0/3` | `78512128` | `1000000` | `7683095093045065342` | `40960` |
| `checked-epoch-scoped` | `4.72` | `995.167` | `0.000` | `0.000` | `0/3` | `78512128` | `1000000` | `7683095093045065342` | `40960` |
| `region-scoped-rooted` | `4.72` | `1009.541` | `0.000` | `0.000` | `0/3` | `78528512` | `1000000` | `7683095093045065342` | `40960` |

1M L1 final-clean, 3 query iterations per external process:

| Mode | External real s | External user s | External sys s | RSS bytes | Records | Checksum | Output |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gc-heap` | `4.33` | `4.18` | `0.09` | `75300864` | `1000000` | `7683095093045065342` | `40960` |
| `checked-epoch-stream-legacy` | `3.83` | `3.76` | `0.04` | `15908864` | `1000000` | `7683095093045065342` | `40960` |
| `checked-epoch-stream` | `3.80` | `3.73` | `0.04` | `15892480` | `1000000` | `7683095093045065342` | `40960` |
| `checked-epoch-stream-open-handle` | `3.80` | `3.73` | `0.04` | `15892480` | `1000000` | `7683095093045065342` | `40960` |
| `checked-epoch-scoped` | `3.83` | `3.76` | `0.04` | `15974400` | `1000000` | `7683095093045065342` | `40960` |
| `region-scoped-rooted` | `3.90` | `3.82` | `0.04` | `15925248` | `1000000` | `7683095093045065342` | `40960` |

Interpretation:

- Theodolite now has an explicit true streaming-input row: the real power
  trace is parsed inside each benchmark run, with no parsed total-input arrays.
- The byte-field cursor removes the old parser allocation cliff: heap L2 drops
  from `2479.703 ms` / `143.088 ms` GC in the first streaming-file row to
  `1007.030 ms` / `19.932 ms` GC. This is important methodology evidence:
  parser allocation can create misleading GC pressure if it is not controlled.
- The optimized 1M q2 row remains a real streaming RSS/fixed-memory and modest
  throughput win for the epoch topology: optimized checked stream is L1
  `3.80 s` versus heap `4.33 s`, while cutting RSS from about `75 MB` to about
  `16 MB`.
- L2 shows the region rows remove timed heap GC once the parser is byte-based:
  optimized checked stream is `993.191 ms`, GC `0`, versus heap
  `1054.432 ms`, GC `19.906 ms`.
- The handle-backed checked stream promotion is a small but positive
  remaining-path allocation-lowering win: L1 improves `3.83 s -> 3.80 s`
  versus the legacy generic checked stream path, and L2 improves
  `1006.176 ms -> 993.191 ms`.
- Classification: real-streaming-input checked epoch RSS/fixed-memory and
  modest-throughput evidence, plus modest backend-lowering evidence. It is
  cleaner than the first streaming-file row but no longer looks GC-heavy,
  which is the point: after parser allocation is controlled, the real
  time-series query is mostly source/query CPU plus retained measurement
  objects.

## Planned Conversions

| Candidate | First streaming query | Status |
|---|---|---|
| GH Archive | byte-slice NDJSON q1/q2 with event-time where cheap | explicit `streaming-file` q1/q2 smoke and 100k triage complete; scale only if heap caps or multi-hour input expose pressure |
| Theodolite power | real power trace downsampling/window aggregation | explicit `streaming-file` q2 1M L1/L2 complete; keep as real-streaming throughput/RSS/fixed-memory evidence |
| StackExchange/StackOverflow | post text top-word/top-template by epoch | AskUbuntu streaming-file 1M complete; larger StackExchange/StackOverflow remains next data candidate |
| SNAP/Yak graph edge replay | direct `RiftRegion.epoch` edge-stream epochs | disk/time preflight first |
| DSPBench Fraud/Log | line-stream q2 regression rows | convert only if retained pressure remains material |
