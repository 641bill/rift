# Real Streaming Input Matrix

Date: 2026-05-11
Last updated: 2026-05-18 00:09 CEST

Status: started. This matrix records only rows that satisfy the
`real-streaming-input` protocol: no full-input preload, incremental source
replay, bounded active state, and matching checksum/output counts.

## Implemented Rows

### Theodolite Retained UC4 Hierarchy Windows, Streaming-File

Implementation:

- Matrix: `/Users/siyaoliu/rift/scala-native-rift/sandbox/src/main/scala-next/TheodolitePowerRegionMatrix.scala`
- Mode: `THEODOLITE_POWER_INPUT_MODE=streaming-file`
- Source:
  `zip:/Users/siyaoliu/rift/cache/benchmark-data/theodolite/real-power/household_power_consumption.zip!household_power_consumption.txt`
- Query: `q3-retained-uc4`, a local Theodolite UC4-style hierarchy/window
  aggregation over real UCI power-meter records.
- Object shape: one retained measurement plus twelve retained hierarchy
  contribution objects per usable record; durable aggregate arrays remain
  heap/control metadata.
- API/topology: checked `RiftRegion.epoch` stream and checked scoped epoch;
  this is not exact Theodolite artifact reproduction.

20k smoke:

All heap, checked stream, checked scoped, and rooted scoped rows matched
checksum `-2895454912458695581` and output count `6176`.

1M candidate row:

| Mode | L1 external s | L1 RSS bytes | L2 median ms | Median GC ms | Max GC ms | Runs with GC | Records | Checksum | Output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `heap-immix` | `9.42` | `183566336` | `2712.028` | `376.791` | `393.169` | `3/3` | `1000000` | `5496025699187626461` | `61760` |
| `checked-epoch-stream` | `7.77` | `31064064` | `2143.809` | `38.516` | `41.907` | `3/3` | `1000000` | `5496025699187626461` | `61760` |
| `checked-epoch-scoped` | `7.99` | `31113216` | `2189.232` | `43.837` | `48.301` | `3/3` | `1000000` | `5496025699187626461` | `61760` |
| `region-scoped-rooted` | `8.21` | `31129600` | `2299.931` | `44.424` | `49.323` | `3/3` | `1000000` | `5496025699187626461` | `61760` |

Full local row:

| Mode | L1 external s | L1 RSS bytes | L2 median ms | Median GC ms | Max GC ms | Runs with GC | Records | Checksum | Output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `heap-immix` | `16.85` | `207077376` | `4504.438` | `335.309` | `482.380` | `3/3` | `2049280` | `6053646443718331766` | `126608` |
| `checked-epoch-stream` | `14.06` | `26607616` | `3769.962` | `31.570` | `33.884` | `3/3` | `2049280` | `6053646443718331766` | `126608` |
| `checked-epoch-scoped` | `14.88` | `26689536` | `3865.198` | `39.062` | `54.579` | `3/3` | `2049280` | `6053646443718331766` | `126608` |
| `region-scoped-rooted` | `15.54` | `26640384` | `4104.244` | `37.961` | `37.991` | `3/3` | `2049280` | `6053646443718331766` | `126608` |

Heap-cap follow-up:

| Mode | Heap cap | Status | L1 external s | RSS bytes | Checksum | Output |
|---|---:|---|---:|---:|---:|---:|
| `heap-immix` | uncapped | completed | `16.85` | `207077376` | `6053646443718331766` | `126608` |
| `heap-immix` | `128M` | completed | `17.90` | `138821632` | `6053646443718331766` | `126608` |
| `heap-immix` | `64M` | failed | `9.87` | `72204288` | n/a | n/a |
| `checked-epoch-stream` | `64M` | completed | `14.27` | `26591232` | `6053646443718331766` | `126608` |

Interpretation:

- This is the strongest current true `real-streaming-input` retained-object
  row. The input remains compressed, is streamed through an archive-member
  reader, and no full parsed input array is retained.
- Heap GC is material in L2 and the L1 process RSS gap is large. Checked Rift
  wins throughput, RSS, and fixed-memory behavior.
- The checked rows still show small timed GC because the stream source,
  archive reader, and runtime control path allocate normal heap objects; the
  region-managed retained hierarchy objects are bulk-reclaimed.

### Yak AskUbuntu Topwordreal, Streaming-File

Implementation:

- Matrix: `/Users/siyaoliu/rift/scala-native-rift/sandbox/src/main/scala-next/YakRegionMatrix.scala`
- Mode: `YAK_TEXT_INPUT_MODE=streaming-file`
- Source: `7z:/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu.com.7z!Posts.xml`
  for new extraction-free runs; older rows used the derived
  `/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu-Posts.xml`
  or `.gz` copy from the same archive.
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

5M compressed-streaming scale-up:

| Mode | L1 external s | L1 RSS bytes | L2 median ms | Median GC ms | Region op ms | Records | Checksum |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gc-heap` | `6.74` | `41091072` | `2109.524` | `27.237` | `0.000` | `5000000` | `-1661295494911249805` |
| `region-scoped-rooted` | `6.39` | `15122432` | `2075.720` | `0.000` | `0.000` | `5000000` | `-1661295494911249805` |
| `checked-epoch-stream` | `6.42` | `15040512` | `2066.016` | `0.000` | `0.264` | `5000000` | `-1661295494911249805` |
| `checked-epoch-scoped` | `6.23` | `15007744` | `2061.736` | `0.000` | `0.000` | `5000000` | `-1661295494911249805` |

Interpretation:

- This is a true `real-streaming-input` row: the XML file is consumed during
  the benchmark and no full replay token array is retained.
- It is not GC-heavy at this scale. Heap median timed GC is `3.677 ms` on a
  `301.923 ms` L2 loop at 1M and `27.237 ms` on a `2109.524 ms` L2 loop at
  5M, so parser/token scanning remains the dominant cost.
- Checked epoch rows still remove timed heap GC, reduce L1 RSS from about
  `39.6 MB` to `13.0 MB` at 1M and from about `41 MB` to `15 MB` at 5M,
  while improving median L1 elapsed by about `5-8%`.
  Classify as
  modest real-streaming-input RSS/fixed-memory evidence, not as the flagship
  GC-heavy stream case study.

### Yak LiveJournal Graphreal, Streaming-File

Implementation:

- Matrix: `/Users/siyaoliu/rift/scala-native-rift/sandbox/src/main/scala-next/YakRegionMatrix.scala`
- Mode: `YAK_GRAPH_INPUT_MODE=streaming-file`
- Source:
  `/Users/siyaoliu/rift/cache/benchmark-data/yak/snap/soc-LiveJournal1.txt.gz`
- Query: stream SNAP LiveJournal edges from the compressed gzip file, allocate
  per-epoch `EdgeUpdate` objects, and apply them to durable heap vertex state.
- API/topology: direct `RiftRegion.epoch` over retained epoch records.
  Page-token, whole-run, and `EpochBuffer` graph controls remain preloaded-only
  because they require indexed replay over a bounded edge array.

20k smoke:

All modes matched checksum `-31772606416651040`.

1M compressed-streaming row:

| Mode | L1 external s | L1 RSS bytes | L2 median ms | Median GC ms | Region op ms | Records | Checksum |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gc-heap` | `0.88` | `76038144` | `287.882` | `8.190` | `0.000` | `1000000` | `3675910048719095437` |
| `region-scoped-rooted` | `0.85` | `22347776` | `281.376` | `0.000` | `0.000` | `1000000` | `3675910048719095437` |
| `checked-epoch-stream` | `0.81` | `22233088` | `283.582` | `0.000` | `0.116` | `1000000` | `3675910048719095437` |
| `checked-epoch-scoped` | `0.81` | `22331392` | `276.629` | `0.000` | `0.000` | `1000000` | `3675910048719095437` |

5M compressed-streaming row:

| Mode | L1 external s | L1 RSS bytes | L2 median ms | Median GC ms | Region op ms | Records | Checksum |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gc-heap` | `4.46` | `206307328` | `1416.564` | `42.500` | `0.000` | `5000000` | `978899966951504355` |
| `region-scoped-rooted` | `4.18` | `40091648` | `1358.500` | `0.000` | `0.000` | `5000000` | `978899966951504355` |
| `checked-epoch-stream` | `4.10` | `39911424` | `1327.994` | `0.000` | `0.440` | `5000000` | `978899966951504355` |
| `checked-epoch-scoped` | `4.07` | `40108032` | `1337.058` | `0.000` | `0.000` | `5000000` | `978899966951504355` |

20M compressed-streaming row:

| Mode | L1 external s | L1 RSS bytes | L2 median ms | Median GC ms | Region op ms | Records | Checksum |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gc-heap` | `18.32` | `577028096` | `6333.745` | `165.387` | `0.000` | `20000000` | `-5977224669223427032` |
| `region-scoped-rooted` | `17.78` | `101924864` | `5644.025` | `0.000` | `0.000` | `20000000` | `-5977224669223427032` |
| `checked-epoch-stream` | `17.59` | `101564416` | `5530.190` | `0.000` | `2.869` | `20000000` | `-5977224669223427032` |
| `checked-epoch-scoped` | `17.15` | `101679104` | `5812.138` | `0.000` | `0.000` | `20000000` | `-5977224669223427032` |

Interpretation:

- This is true real-streaming-input graph evidence: the compressed SNAP
  LiveJournal edge list is consumed inside the timed benchmark path and no
  full edge replay array is retained.
- The row gives strong RSS/fixed-memory evidence and a useful throughput win.
  At 20M streamed edges, checked scoped L1 is `17.15 s` versus heap
  `18.32 s`, and checked stream L2 is `5530.190 ms` versus heap `6333.745 ms`.
- Heap timed GC is visible but still below the `5%` flagship gate:
  `165.387 ms` inside `6333.745 ms` at 20M, about `2.6%`. Classify as
  real-streaming graph RSS/fixed-memory and throughput evidence, not a
  GC-time-heavy flagship.

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

Active-window heap-cap follow-up:

Command shape: `LOGHUB_INPUT_MODE=streaming-file`,
`LOGHUB_LINES=1000000`, `LOGHUB_LINES_PER_BUCKET=25000`,
`LOGHUB_LIVE_BUCKETS=16`, `LOGHUB_BENCHMARK_RUNS=1`, query
`q3-template-session`. This is a triage row, not a final 3-run presentation
median.

| Mode | Heap cap | Status | L1 external s | L2 ms | GC ms | GC collections | RSS bytes | Checksum | Output |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `gc-heap` | `512M` | ok | `17.87` | `8729.167` | `136.507` | `1` | `540786688` | `-7913633384189087996` | `283857` |
| `gc-heap` | `256M` | ok | `21.34` | `10725.843` | `1989.577` | `17` | `272449536` | `-7913633384189087996` | `283857` |
| `gc-heap` | `128M` | failed | `2.02` | n/a | n/a | n/a | `138838016` | n/a | n/a |
| `checked-page-token` | uncapped | ok | `17.87` | `8610.817` | `0.000` | `0` | `693813248` | `-7913633384189087996` | `283857` |

### LogHub HDFS Retained Session/Join, Streaming-File

Implementation:

- Matrix: `/Users/siyaoliu/rift/scala-native-rift/sandbox/src/main/scala-next/LogHubRetainedSessionMatrix.scala`
- Mode: direct streaming-file input through `LOGHUB_SESSION_INPUT`
- Source: `/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1/HDFS.log`
- Query: stream real HDFS log lines, derive session/join keys from the line,
  allocate retained ordinary objects, and close epoch/session state after the
  active-epoch boundary.
- API/topology: natural heap, checked direct Rift epoch/streaming region, and
  checked scoped backend.

1M active-16 L2 triage:

| Workload | Mode | L2 median ms | Median GC ms | Max GC ms | Runs with GC | Region op ms | Records | Bytes read | Checksum | Output |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| session | `heap-gc` | `6595.172` | `82.341` | `90.781` | `3/3` | `0.000` | `1000000` | `141557760` | `-4251312673673367471` | `831923` |
| session | `checked-rift` | `6578.258` | `5.572` | `5.858` | `3/3` | `0.885` | `1000000` | `141557760` | `-4251312673673367471` | `831923` |
| session | `checked-region-scoped` | `6997.852` | `63.979` | `67.797` | `3/3` | `0.000` | `1000000` | `141557760` | `-4251312673673367471` | `831923` |
| join | `heap-gc` | `6837.810` | `9.474` | `13.881` | `3/3` | `0.000` | `1000000` | `141557760` | `4282190220497908364` | `0` |
| join | `checked-rift` | `6927.376` | `6.731` | `7.516` | `3/3` | `1.624` | `1000000` | `141557760` | `4282190220497908364` | `0` |
| join | `checked-region-scoped` | `6681.557` | `77.349` | `77.610` | `3/3` | `0.000` | `1000000` | `141557760` | `4282190220497908364` | `0` |

Interpretation:

- This is true `real-streaming-input`: the HDFS file is consumed incrementally
  and no full parsed input is retained.
- It retains ordinary session/join objects until an epoch boundary, but the
  row is still not GC-heavy enough. Session heap GC is only about `1.2%` of
  median L2 elapsed, and join heap GC is about `0.1%`.
- Park it as retained streaming control evidence. The result supports the
  investigation lesson that real input plus retained objects is not sufficient
  if parsing, hashing, and query work dominate the full stream loop.

Interpretation:

- Increasing active windows exposes heap-cap pressure: the heap row slows
  materially at `256M` because GC rises to about `1.99 s`, and it fails at
  `128M`.
- The checked page-token row completes with matching checksum/output and zero
  timed heap GC, but the active-window configuration raises region RSS to about
  `694 MB`. This is therefore a heap-cap/GC-pressure triage result, not a
  clean RSS win.
- Next action: do not keep scaling this exact page-token q3 path blindly.
  Either add a retained session/join shape where region live payload is bounded
  more tightly, or move to Broom/StreamFlex-style retained joins and event
  correlation.

### LogHub Spark Retained Session, Archive-Wide Streaming

Implementation:

- Matrix: `/Users/siyaoliu/rift/scala-native-rift/sandbox/src/main/scala-next/LogHubRetainedSessionMatrix.scala`
- Mode: direct archive-wide streaming input through `LOGHUB_SESSION_INPUT`
- Source:
  `tar.gzcat:/Users/siyaoliu/rift/cache/benchmark-data/loghub/Spark.tar.gz`
- Query: concatenate regular file contents from the compressed Spark archive,
  stream log lines, allocate retained session objects, and close epoch/session
  state after the active-epoch boundary.
- API/topology: natural heap, checked direct Rift epoch/streaming region, and
  checked scoped backend.

Archive-source note: the first `tar.gzdir:/archive!prefix` attempt was
functionally correct but too slow for the Spark archive because it expanded to
thousands of per-member `tar.gz:/archive!member` scans. The retained-session
row now uses `tar.gzcat:` so the compressed archive is decompressed once and
streamed as one concatenated archive source.

20k smoke:

| Workload | Mode | L2 median ms | Median GC ms | RSS bytes | Records | Checksum | Output |
|---|---|---:|---:|---:|---:|---:|---:|
| session | `heap-gc` | `206.572` | `4.140` | `21544960` | `20000` | `-435595809917860422` | `17689` |
| session | `checked-rift` | `219.635` | `0.397` | `14843904` | `20000` | `-435595809917860422` | `17689` |
| session | `checked-region-scoped` | `204.379` | `1.276` | `14974976` | `20000` | `-435595809917860422` | `17689` |
| join | `heap-gc` | n/a | n/a | n/a | `20000` | matched | `0` |
| join | `checked-rift` | n/a | n/a | n/a | `20000` | matched | `0` |
| join | `checked-region-scoped` | n/a | n/a | n/a | `20000` | matched | `0` |

The join workload emits zero matches on this Spark stream, so the scale-up
uses `session` only.

1M active-16 L1 final-clean row:

| Mode | L1 external s | User s | Sys s | RSS bytes | Records | Checksum | Output | Retained proxy | Max live |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `heap-gc` | `27.62` | `21.94` | `0.28` | `390561792` | `1000000` | `-1938898183938054371` | `770310` | `1770310` | `714833` |
| `checked-rift` | `20.30` | `19.76` | `0.10` | `72908800` | `1000000` | `-1938898183938054371` | `770310` | `1770310` | `714836` |
| `checked-region-scoped` | `19.85` | `19.86` | `0.06` | `73023488` | `1000000` | `-1938898183938054371` | `770310` | `1770310` | `714836` |

1M active-16 L2 standard-stats row:

| Mode | L2 median ms | Min ms | Max ms | Records/sec | Median GC ms | Max GC ms | Runs with GC | Region op ms | Region objects | RSS bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `heap-gc` | `6642.276` | `6550.577` | `6643.644` | `150550.807` | `140.639` | `169.764` | `3/3` | `0.000` | `0` | `508149760` |
| `checked-rift` | `6396.869` | `6385.812` | `6434.709` | `156326.469` | `14.407` | `14.889` | `3/3` | `1.121` | `1770319` | `72941568` |
| `checked-region-scoped` | `6615.206` | `6575.994` | `6670.608` | `151166.857` | `196.520` | `199.531` | `3/3` | `0.000` | `1770319` | `73138176` |

Heap-cap follow-up:

| Mode | Heap cap | Status | L1 external s | RSS bytes | Checksum | Output |
|---|---:|---|---:|---:|---:|---:|
| `heap-gc` | uncapped | completed | `27.62` | `390561792` | `-1938898183938054371` | `770310` |
| `heap-gc` | `384M` | completed | `19.91` | `344850432` | `-1938898183938054371` | `770310` |
| `heap-gc` | `256M` | completed | `19.85` | `277676032` | `-1938898183938054371` | `770310` |
| `heap-gc` | `128M` | failed | `3.05` | `143409152` | n/a | n/a |
| `heap-gc` | `96M` | failed | `2.16` | `107020288` | n/a | n/a |
| `heap-gc` | `64M` | failed | `1.23` | `72761344` | n/a | n/a |

Interpretation:

- This is the strongest LogHub retained-session real-streaming row so far. It
  streams the compressed Spark archive without a permanent extracted copy.
- The result is a strong RSS/fixed-memory row: checked rows complete around
  `73 MB` RSS, while heap uses `278-391 MB` in successful L1 rows and fails
  below a `128M` heap cap.
- It is still not a pure GC-time flagship. Heap median timed GC is
  `140.639 ms` inside `6642.276 ms`, about `2.1%` of the measured L2 loop.
  The row is therefore real-streaming retained-object RSS/fixed-memory
  evidence, with a modest checked-Rift L2 throughput win.
- The scoped row is fastest in the L1 process table, but its L2 row still
  reports runtime/setup heap GC. Do not claim that checked scoped removes all
  GC on this row; use it as a best-safe-backend comparison.

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
