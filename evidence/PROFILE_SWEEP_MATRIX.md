# L4 Profile Sweep Matrix

Last updated: 2026-05-12 09:43 CEST

Status: profiling infrastructure and first representative sweep complete. This
file tracks representative external-profile sweeps for benchmark families. L4
profiles are diagnostic evidence only: they explain CPU/GC composition and must
not be used for headline elapsed/RSS claims.

## Harness

Child script:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
zsh sandbox/run_l4_profile_sweep.sh
```

Default cases are intentionally small:

- `streamflex-design-checked`
- `streamflex-design-heap`

Full representative sweep:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_CASES=all \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-$(date +%Y%m%d-%H%M%S) \
  zsh sandbox/run_l4_profile_sweep.sh
```

The harness links the requested benchmark main class when
`RIFT_PROFILE_BUILD=1`, starts the native binary, waits
`RIFT_PROFILE_DELAY_SECONDS`, and samples it for `RIFT_PROFILE_SECONDS`.
On macOS it uses `/usr/bin/sample`; on Linux it uses `perf record`.

Important macOS caveat: in the Codex sandbox, `/usr/bin/sample` requires
elevated process-inspection permission. Local terminal runs may not need that
approval.

## Representative Cases

| Case | Benchmark family | Purpose |
|---|---|---|
| `streamflex-design-checked` / `streamflex-design-heap` | StreamFlex design reproduction | Compare checked scoped allocation/zeroing and capsule/query work against heap allocation/object metadata. |
| `commoncrawl-q2-checked-scoped` / `commoncrawl-q2-heap` | Generated GC-heavy page/window stream | Explain allocation+append, token hashing, cursor traversal, and GC-heavy generated stream behavior. |
| `dspbench-fraud-q2-checked-scoped` / `dspbench-fraud-q2-heap` | Real DSPBench stream regression | Check whether parser/replay/predictor CPU still dominates real-input rows. |
| `loghub-hdfs-stream-topk-checked` / `loghub-hdfs-stream-topk-heap` | True real streaming-input retained top-k | Separate file streaming/template hashing/top-k work from GC and region allocation. |
| `streamit-filterbank-checked` / `streamit-filterbank-heap` | StreamIt/StreamFlex primitive control | Confirm primitive DSP kernels are compute/array dominated. |
| `streamit-beamformer-checked` / `streamit-beamformer-heap` | StreamIt/StreamFlex primitive control | Confirm primitive DSP kernels are compute/array dominated. BeamFormer uses a profile-only scale by default because large timing scales are too slow for routine L4 sweeps. |
| `yak-graphreal-checked-scoped` / `yak-graphreal-heap` | Real SNAP/Yak graph replay | Check whether the direct-epoch LiveJournal row is compute, input, allocation, or GC dominated. |
| `dataflow-aggregate-checked-scoped` / `dataflow-aggregate-epoch-fold` / `dataflow-aggregate-heap` | Broom/Dataflow aggregate | Explain why direct epoch wins but generic `EpochFold` remains gated. |
| `specjbb-checked-scoped` / `specjbb-heap` | Stancu/SPECjbb2005-workload port | Check whether transaction rows are dominated by object allocation, transaction proxy helpers, or GC. |
| `reml-msort-checked-scoped` / `reml-msort-heap` | ReML/MLKit-shaped allocation/list port | Compare local Scala Native list/sort CPU shape with checked scoped placement. |
| `reml-ratio-checked-scoped` / `reml-ratio-heap` | ReML/MLKit-shaped compute/list control | Check whether `ratio` is compute-bound or memory-management-bound. |

## Representative Sweep

Date/time: 2026-05-12 02:00-02:22 CEST.

Profile directories:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-representative`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-fixes`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-streamit-final`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml`

The sweep was split because the first pass exposed two harness issues:
DSPBench file-backed rows needed an explicit `DSPBENCH_INPUT`, and the
StreamIt BeamFormer default scale was too large for routine profiling. The
harness now provides the DSPBench bundled credit-card input by default and uses
profile-sized StreamIt controls.

| Case | Status | Scale | Profile artifact | Main interpretation |
|---|---|---:|---|---|
| `streamflex-design-checked` | `ok` | 20M generated events | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-representative/streamflex-design-checked.sample.txt` | Checked scoped StreamFlex-design time splits across `processCheckedPeriod`, stable-state query work, SafeZone/zone allocation, zeroing, and capsule add/drain. |
| `streamflex-design-heap` | `ok` | 20M generated events | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-representative/streamflex-design-heap.sample.txt` | Heap shares stable-state/query/capsule work and pays Immix allocator/object-metadata cost. |
| `commoncrawl-q2-checked-scoped` | `ok` | 2M generated WET-shaped pages | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-representative/commoncrawl-q2-checked-scoped.sample.txt` | Checked scoped q2 is split across close cursor traversal, append/linking, token hashing, SafeZone allocation/zeroing, and visible marker/root work. |
| `commoncrawl-q2-heap` | `ok` | 2M generated WET-shaped pages | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-representative/commoncrawl-q2-heap.sample.txt` | Heap q2 shows the same token/query and close traversal floor plus Immix allocation, object metadata, mark, and sweep frames. |
| `dspbench-fraud-q2-checked-scoped` | `ok` | 5M replayed real `credit-card.dat` events | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-fixes/dspbench-fraud-q2-checked-scoped.sample.txt` | Real DSPBench q2 is dominated by byte-line reading, stable hashing, CSV parsing, and predictor updates before region allocator costs. |
| `dspbench-fraud-q2-heap` | `ok` | 5M replayed real `credit-card.dat` events | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-fixes/dspbench-fraud-q2-heap.sample.txt` | Heap has the same parser/predictor floor plus Immix allocator and object metadata. |
| `loghub-hdfs-stream-topk-checked` | `ok` | 5M real streaming HDFS log lines | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-representative/loghub-hdfs-stream-topk-checked.sample.txt` | Real streaming LogHub top-k is parser/hash/token-bound; `EpochTopKByKey` and region allocation are small in the sampled window. |
| `loghub-hdfs-stream-topk-heap` | `ok` | 5M real streaming HDFS log lines | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-representative/loghub-hdfs-stream-topk-heap.sample.txt` | Heap has the same parser/hash/token floor with small Immix allocation/GC frames, explaining why this is modest/RSS evidence, not GC-heavy throughput evidence. |
| `streamit-filterbank-checked` | `ok` | 4096 iterations | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-streamit-final/streamit-filterbank-checked.sample.txt` | FilterBank is almost entirely numeric kernel work. Region/GC work is not visible as a meaningful bottleneck. |
| `streamit-filterbank-heap` | `ok` | 4096 iterations | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-streamit-final/streamit-filterbank-heap.sample.txt` | Same numeric-kernel result as checked; this supports keeping FilterBank as a methodology control. |
| `streamit-beamformer-checked` | `ok` | 256 frames | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-streamit-final/streamit-beamformer-checked.sample.txt` | BeamFormer is dominated by FIR filter state stepping; allocator/GC frames are tiny. |
| `streamit-beamformer-heap` | `ok` | 256 frames | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-streamit-final/streamit-beamformer-heap.sample.txt` | Same FIR-dominated CPU shape as checked. BeamFormer is not a GC-heavy memory-management proof in the current port. |
| `yak-graphreal-checked-scoped` | `ok` | 50M real LiveJournal edges | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/yak-graphreal-checked-scoped.sample.txt` | The current 2s sample catches gzip/file input parsing (`RealGraphInput.parseEdge`, zlib inflate, byte-line read) before the direct-epoch phase dominates. Treat this as input-path evidence; rerun with a processing-phase/preloaded profile before using it to tune epoch allocation. |
| `yak-graphreal-heap` | `ok` | 50M real LiveJournal edges | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/yak-graphreal-heap.sample.txt` | Same input-path caveat as checked scoped: the sample is dominated by graph input parsing/loading, not the heap-vs-region epoch body. |
| `dataflow-aggregate-checked-scoped` | `ok` | 20 x 500k docs | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/dataflow-aggregate-checked-scoped.sample.txt` | Direct checked scoped aggregate is short and mostly a tight aggregate loop plus SafeZone allocation/zeroing. |
| `dataflow-aggregate-epoch-fold` | `ok` | 20 x 500k docs | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/dataflow-aggregate-epoch-fold.sample.txt` | Generic `EpochFold` spends visible time in `findFoldInsertSlot`, `addFoldContribution`, fold table capacity/clear, append/cursor traversal, Rift allocation/stat paths, and `checkOpen`. This explains why it remains speed-gated. |
| `dataflow-aggregate-heap` | `ok` | 20 x 500k docs | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/dataflow-aggregate-heap.sample.txt` | Heap aggregate shows the same query/document construction floor plus Immix allocation, object metadata, mark, and sweep frames. |
| `specjbb-checked-scoped` | `ok` | 1M transactions | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/specjbb-checked-scoped.sample.txt` | The row is too short for a rich call graph; sampled time is mostly transaction proxy/count helpers (`txObjectCount`, `txByteProxy`, `txKind`). Use a larger/delayed profile before tuning allocation here. |
| `specjbb-heap` | `ok` | 1M transactions | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/specjbb-heap.sample.txt` | Similar short-profile shape to checked scoped, with a small number of heap allocator/object metadata samples. |
| `reml-msort-checked-scoped` | `ok` | 1M list size | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/reml-msort-checked-scoped.sample.txt` | The local Scala Native port is dominated by boxed `Integer` compare/valueOf, `ScalaRunTime` array apply/update, `java.util.Arrays` stable merge/insertion sort, plus allocation/zeroing/GC frames. This is a Scala object/boxing/sort-shape result, not a pure region allocator result. |
| `reml-msort-heap` | `ok` | 1M list size | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/reml-msort-heap.sample.txt` | Heap has nearly the same boxed sort shape, plus Immix allocation/object metadata/mark/sweep frames. |
| `reml-ratio-checked-scoped` | `ok` | 2M ratio count | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/reml-ratio-checked-scoped.sample.txt` | Checked scoped `ratio` is mostly `gcd` and arithmetic; region allocation is tiny in the sample. Treat as compute/control evidence. |
| `reml-ratio-heap` | `ok` | 2M ratio count | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/reml-ratio-heap.sample.txt` | Heap `ratio` is also mostly `gcd`; visible GC frames are secondary. |

Future additions should cover:

- A Yak LiveJournal processing-phase profile that avoids sampling only gzip/file
  parsing. Options are a longer delayed profile, a preloaded processing-only
  mode, or a generated graph-step profile when the question is epoch CPU rather
  than real input parsing.
- Larger/delayed SPECjbb2005-workload and ReML `ratio` rows if they become
  tuning targets; the current samples are useful controls but short.

## Smoke

Date/time: 2026-05-12 01:55 CEST.

Command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_CASES=streamflex-design-checked \
RIFT_PROFILE_SECONDS=2 \
RIFT_PROFILE_STREAMFLEX_EVENTS=5000000 \
RIFT_PROFILE_OUTPUT_DIR=/tmp/rift-profile-sweep-smoke \
  zsh sandbox/run_l4_profile_sweep.sh
```

Result:

| Case | Status | Tool | Profile |
|---|---|---|---|
| `streamflex-design-checked` | `ok` | `sample` | `/tmp/rift-profile-sweep-smoke/streamflex-design-checked.sample.txt` |

The smoke profile shows the same shape as the manual StreamFlex profile:
`processCheckedPeriod`, `scalanative_zone_alloc`/`_platform_memset`,
`StableState.classify`, and `StableState.recordEvent` are the early hot paths.

## Use In Evaluation

- L1 rows remain the source of headline elapsed/RSS.
- L2 rows remain the source of GC/region counters.
- L4 profile rows explain why a mode wins or loses.
- A benchmark family should get a profile when:
  - the checked row wins and we need to know why;
  - the checked row loses despite removing GC;
  - real-input rows remain parser/query dominated;
  - a new operator or backend optimization changes the CPU shape.
