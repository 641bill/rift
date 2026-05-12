# L4 Profile Sweep Matrix

Last updated: 2026-05-12 02:35 CEST

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

## Representative Sweep

Date/time: 2026-05-12 02:00-02:22 CEST.

Profile directories:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-representative`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-fixes`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-streamit-final`

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

Future additions should cover:

- Yak LiveJournal direct epoch, but only at a scale long enough to sample
  without making the profile run impractical.
- Dataflow SELECT/AGGREGATE/JOIN once native-link runner support is normalized.
- SPECjbb2005/Stancu transaction port after the next transaction-scale row.
- ReML Tier 1 allocation/list ports when the comparison table needs CPU
  explanation.

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
