# L4 Profile Sweep Matrix

Last updated: 2026-05-12 01:55 CEST

Status: profiling infrastructure started. This file tracks representative
external-profile sweeps for benchmark families. L4 profiles are diagnostic
evidence only: they explain CPU/GC composition and must not be used for
headline elapsed/RSS claims.

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
| `streamit-beamformer-checked` / `streamit-beamformer-heap` | StreamIt/StreamFlex primitive control | Confirm primitive DSP kernels are compute/array dominated. |

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
