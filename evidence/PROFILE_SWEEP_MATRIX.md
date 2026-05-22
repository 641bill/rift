# L4 Profile Sweep Matrix

Last updated: 2026-05-21 07:06 CEST

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

Use `RIFT_PROFILE_EXTRA_ENV="NAME=value ..."` to inject policy or scale
knobs into a profile case without adding a one-off case branch. This is used
for the Dataflow `RIFT_REGION_REUSE_POLICY=cache-large` profile.

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
| `streamflex-design-checked-stream` / `streamflex-design-checked-stream-inferred` | StreamFlex design reproduction | Profile the clean rerun winner and its ReML-style inferred allocation variant: checked direct epoch over the Rift streaming backend. |
| `commoncrawl-q2-checked-rift` | Generated GC-heavy page/window stream | Profile the clean rerun winner: Rift-backed checked page-token q2. |
| `commoncrawl-q2-checked-scoped` / `commoncrawl-q2-heap` | Generated GC-heavy page/window stream | Explain allocation+append, token hashing, cursor traversal, and GC-heavy generated stream behavior. |
| `dspbench-fraud-q2-checked-scoped` / `dspbench-fraud-q2-heap` | Real DSPBench stream regression | Check whether parser/replay/predictor CPU still dominates real-input rows. |
| `dspbench-log-q2-checked-scoped` / `dspbench-log-q2-heap` | Real DSPBench stream regression | Check whether parser/replay/status-window CPU still dominates real-input rows. |
| `loghub-hdfs-stream-topk-checked` / `loghub-hdfs-stream-topk-heap` | True real streaming-input retained top-k | Separate file streaming/template hashing/top-k work from GC and region allocation. |
| `yak-topwordreal-*` | Real Stack Exchange text/top-word | Compare natural heap, same-shape heap top-k, direct checked epoch, and reusable checked top-k CPU composition. |
| `loghub-spark-topk-*` / `loghub-windows-topk-*` | Richer real LogHub top-template rows | Check whether larger Spark/Windows real logs expose top-k or parser/hash bottlenecks. |
| `theodolite-power-q2-*` | Real UCI/Theodolite-style power stream | Check whether time-series q2 is region/GC-bound or parser/string-bound. |
| `nexmark-q8-*` / `nexmark-q9-*` | NEXMark hash/join/top-k methodology controls | Profile hash/join and winning-bid style operator costs before designing reusable operators. |
| `streamit-filterbank-checked` / `streamit-filterbank-heap` | StreamIt/StreamFlex primitive control | Confirm primitive DSP kernels are compute/array dominated. |
| `streamit-beamformer-checked` / `streamit-beamformer-heap` | StreamIt/StreamFlex primitive control | Confirm primitive DSP kernels are compute/array dominated. BeamFormer uses a profile-only scale by default because large timing scales are too slow for routine L4 sweeps. |
| `yak-graphreal-checked-scoped` / `yak-graphreal-heap` | Real SNAP/Yak graph replay | Check whether the direct-epoch LiveJournal row is compute, input, allocation, or GC dominated. |
| `yak-graphstep-checked-scoped` / `yak-graphstep-heap` | Yak epoch-body processing proxy | Profile the graph epoch allocation/traversal body without gzip/file parsing. |
| `dataflow-aggregate-checked-scoped` / `dataflow-aggregate-epoch-fold` / `dataflow-aggregate-heap` | Broom/Dataflow aggregate | Explain why direct epoch wins but generic `EpochFold` remains gated. |
| `specjbb-checked-scoped` / `specjbb-heap` | Stancu/SPECjbb2005-workload port | Check whether transaction rows are dominated by object allocation, transaction proxy helpers, or GC. |
| `specjbb-large-checked-scoped` / `specjbb-large-heap` | Larger Stancu/SPECjbb2005-workload profile | Use a longer transaction row to make allocation/helper attribution reliable. |
| `reml-msort-checked-scoped` / `reml-msort-heap` | ReML/MLKit-shaped allocation/list port | Compare local Scala Native list/sort CPU shape with checked scoped placement. |
| `reml-ratio-checked-scoped` / `reml-ratio-heap` | ReML/MLKit-shaped compute/list control | Check whether `ratio` is compute-bound or memory-management-bound. |
| `reml-logic-*` / `reml-ray-*` / `reml-tsp-*` | ReML/MLKit-shaped Tier-2 ports | Classify local Tier-2 ports as allocation-sensitive or compute/control. |
| `broom-aggregate-*` / `broom-join-*` / `broom-q17-*` / `broom-shopper-*` | Broom/Naiad-style retained dataflow | Profile the newer retained-object methodology rows where heap pays tracing/metadata and checked Rift bulk-closes timestamp regions. |
| `theodolite-power-uc4-*` | Real UCI/Theodolite-style retained hierarchy stream | Profile the real streaming retained UC4 case study, including whether parser/numeric extraction or region allocation dominates. |
| `loghub-retained-session-*` / `loghub-retained-join-*` | Real LogHub retained session/join controls | Check whether retained real log session/join rows are allocator-bound or parser/hash/string-bound. |
| `wikimedia-clickstream-heap` / `wikimedia-clickstream-checked-rift` / `wikimedia-clickstream-checked-rift-inferred` / `wikimedia-clickstream-checked-scoped` | Real Wikimedia retained clickstream-session | Explain why checked Rift removes GC/RSS/fixed-memory pressure but still has higher non-GC mutator cost than heap in the full-file feasibility row, and compare the current inferred checked path. |

## 2026-05-19 Mutator-Parity Sweep

Profile directories:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260519-mutator-cycle`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260519-wikimedia-decompressed-control-rerun`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260519-dataflow-scaled`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260519-dspbench-postscratch-linked`

Command shapes:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260519-mutator-cycle \
RIFT_PROFILE_SECONDS=5 \
RIFT_PROFILE_DELAY_SECONDS=1 \
RIFT_PROFILE_CASES="wikimedia-clickstream-heap wikimedia-clickstream-checked-rift wikimedia-clickstream-checked-rift-inferred wikimedia-clickstream-checked-scoped broom-q17-heap broom-q17-checked-rift broom-shopper-heap broom-shopper-checked-rift theodolite-power-uc4-heap theodolite-power-uc4-checked-rift streamflex-design-heap streamflex-design-checked-stream dspbench-fraud-q2-heap dspbench-fraud-q2-checked-scoped dataflow-aggregate-heap dataflow-aggregate-checked-scoped" \
  zsh sandbox/run_l4_profile_sweep.sh
```

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260519-wikimedia-decompressed-control-rerun \
RIFT_PROFILE_SECONDS=5 \
RIFT_PROFILE_DELAY_SECONDS=1 \
RIFT_PROFILE_WIKIMEDIA_CLICKSTREAM_INPUT=/private/tmp/rift-wikimedia-clickstream-control-20260519.tsv \
RIFT_PROFILE_WIKIMEDIA_CLICKSTREAM_RECORDS=10000000 \
RIFT_PROFILE_CASES="wikimedia-clickstream-heap wikimedia-clickstream-checked-rift wikimedia-clickstream-checked-rift-inferred" \
  zsh sandbox/run_l4_profile_sweep.sh
```

The temporary decompressed input was
`/private/tmp/rift-wikimedia-clickstream-control-20260519.tsv`, about `1.6G`;
it was removed after the run. The compressed source remains the default input.

| Case group | Status | Scale | Profile artifacts | Main interpretation |
|---|---|---:|---|---|
| Wikimedia clickstream compressed | `ok` for heap, checked Rift, inferred checked Rift, checked scoped | 10M real compressed TSV rows | `/Users/siyaoliu/rift/cache/profile-sweep-20260519-mutator-cycle/wikimedia-clickstream-*.sample.txt` | Checked rows remove the retained-object RSS/GC problem, but parser/hash/session-loop samples dominate. The inferred checked row currently has the same profile shape as explicit checked Rift. |
| Wikimedia clickstream decompressed control | `ok` for heap, checked Rift, inferred checked Rift | 10M real decompressed TSV rows, temp file deleted | `/Users/siyaoliu/rift/cache/profile-sweep-20260519-wikimedia-decompressed-control-rerun/wikimedia-clickstream-*.sample.txt` | Decompression is not the sole floor: checked rows still show higher parser/hash sample rates than heap after removing gzip. |
| Broom q17/shopper | `ok` for heap and checked Rift | 20M generated retained methodology rows | `/Users/siyaoliu/rift/cache/profile-sweep-20260519-mutator-cycle/broom-*.sample.txt` | Heap pays allocator/GC metadata; checked Rift pays region allocation/init and query work. These remain the cleanest retained-object memory-management profiles. |
| Theodolite retained UC4 | `ok` for heap and checked Rift | full real UCI power stream | `/Users/siyaoliu/rift/cache/profile-sweep-20260519-mutator-cycle/theodolite-power-uc4-*.sample.txt`; follow-ups `/Users/siyaoliu/rift/cache/profile-sweep-20260520-theodolite-loopshape/theodolite-power-uc4-checked-rift.sample.txt` and `/Users/siyaoliu/rift/cache/profile-sweep-20260520-theodolite-bytecursor-parser/theodolite-power-uc4-*.sample.txt` | Real streaming row remains parser/numeric-field dominated; region allocation is visible but not the primary CPU sink. The 2026-05-20 loop-shape follow-up removes sampled checked callback `IntRef`/`LongRef` parameters. The later byte-cursor parser follow-up drops checked parser/input from `168.60/s` to `147.00/s` as shared parser fairness cleanup. |
| StreamFlexDesign | `ok` for heap and checked stream | 20M generated StreamFlex-design events | `/Users/siyaoliu/rift/cache/profile-sweep-20260519-mutator-cycle/streamflex-design-*.sample.txt` | Checked stream shows region allocation/init plus stable-state/capsule CPU; this is the most promising Rift-specific optimization target. |
| DSPBench Fraud/Log post-scratch | `ok` for heap and checked scoped | 200k real compressed DSPBench replay events | `/Users/siyaoliu/rift/cache/profile-sweep-20260519-dspbench-postscratch-linked/dspbench-*.sample.txt` | After tuple-return cleanup, sampled state-update `Tuple` frames are gone. The rows remain input/replay/runtime-allocation dominated and are better treated as regression/control evidence. |
| Dataflow aggregate scaled | `ok` for heap and checked scoped | 20 epochs x 5M docs/epoch | `/Users/siyaoliu/rift/cache/profile-sweep-20260519-dataflow-scaled/dataflow-aggregate-*.sample.txt` | Checked scoped does not show slower shared query work in absolute samples/sec; remaining overhead is region allocation/token work versus heap GC/metadata. |
| Dataflow aggregate direct/inferred follow-up | `ok` for heap, explicit direct epoch, inferred direct epoch, checked scoped | 20 epochs x 5M docs/epoch | `/Users/siyaoliu/rift/cache/profile-sweep-20260520-dataflow-inferred-direct-escalated/dataflow-aggregate-*.sample.txt`; final-clean timing in `/Users/siyaoliu/rift/cache/dataflow-inferred-direct-epoch-finalclean-100m-seq-20260520` | Inferred direct epoch has no residual heap allocation or GC metadata bucket; it is mostly query/mix (`239.20` samples/sec) plus Rift allocation/init (`66.00`). Explicit direct epoch is similar but slightly higher (`253.80` query, `70.60` region alloc/init). Scoped has visible SafeZone allocation/zeroing samples (`78.80` region alloc/init, `18.00` memset, `10.20` token), but the final-clean external timing shows all checked backends are close: explicit direct `6.43 s`, inferred direct `6.41 s`, scoped `6.33 s`, versus heap `12.83 s`. This is a backend/code-shape selection issue rather than residual heap placement. |
| Dataflow direct epoch `cache-large` reuse policy | `ok` for inferred checked direct epoch | 20 epochs x 5M docs/epoch | `/Users/siyaoliu/rift/cache/profile-sweep-20260520-dataflow-cache-large/dataflow-aggregate-checked-stream-inferred.sample.txt`; L1 repeat `/Users/siyaoliu/rift/cache/dataflow-reuse-policy-inferred-100m-repeat-20260520`; L2 counters `/Users/siyaoliu/rift/cache/dataflow-reuse-policy-inferred-l2-100m-counters-20260520` | `cache-large` cuts final-clean real time from default `6.68/6.44 s` to `6.25/6.24 s` with unchanged RSS on this row. L2 explains the mechanism: default maps `17301` slabs and spends `55.654 ms` region-op; `cache-large` maps `20` slabs and spends `9.627 ms` region-op. The profile's region allocation/init bucket drops from `66.00/s` to `47.80/s`. `prezero-large` is rejected for this row because it raises region-op time to `60.471 ms`. |

The 2026-05-20 goal audit in `docs/CPU_PROFILE_REPORT.md` now expands these
profile rows into the required work-bucket and residual-allocation
classification. The main new cross-row finding was that Broom q17/shopper were
not residual-heap-placement failures, but still carried checked callback-ref
source-shape markers (`255.80/s` and `366.80/s`) before the follow-up cleanup.

## 2026-05-20 Broom Callback-Local Follow-Up

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-broom-callback-local`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 \
RIFT_PROFILE_BUILD=1 \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260520-broom-callback-local \
RIFT_PROFILE_SECONDS=5 \
RIFT_PROFILE_DELAY_SECONDS=1 \
RIFT_PROFILE_CASES="broom-q17-checked-rift broom-shopper-checked-rift" \
  zsh sandbox/run_l4_profile_sweep.sh
```

Both checked Rift rows completed with matching existing checksum/output for the
20M generated retained rows.

| Case | Status | Callback-ref samples/sec | Query mutator samples/sec | Region alloc/init samples/sec | Safepoint poll samples/sec | Main interpretation |
|---|---|---:|---:|---:|---:|---|
| `broom-q17-checked-rift` | `ok` | `0.00` | `163.20` | `29.20` | `48.60` | The prior `LongRef`/`IntRef` callback source-shape marker is gone. Remaining checked work is generated query body plus region allocation/init. |
| `broom-shopper-checked-rift` | `ok` | `0.00` | `332.60` | `17.00` | `38.60` | Same source-shape cleanup result for shopper. No evidence that retained shopper nodes stayed on the heap. |

Timing/counter follow-up:

- `/Users/siyaoliu/rift/cache/broom-callback-local-20m-l1-rss-20260520/summary.tsv`
- `/Users/siyaoliu/rift/cache/broom-callback-local-20m-l2-20260520/summary.tsv`

At 20M active-16, q17 checked Rift is `9.45 s` L1 and `3229.305 ms` L2 versus
heap `13.17 s` and `4782.648 ms`; shopper checked Rift is `14.74 s` L1 and
`5115.933 ms` L2 versus heap `17.55 s` and `6285.094 ms`. Checksums/output
match per workload. These rows confirm the post-cleanup retained-object
advantage; the profile-specific source-shape effect is the callback-ref bucket
dropping to zero.

## 2026-05-20 Broom Inferred Q17/Shopper Follow-Up

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-broom-inferred-q17-shopper`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260520-broom-inferred-q17-shopper \
RIFT_PROFILE_SECONDS=5 \
RIFT_PROFILE_CASES="broom-q17-checked-rift broom-q17-checked-rift-inferred broom-shopper-checked-rift broom-shopper-checked-rift-inferred" \
  zsh sandbox/run_l4_profile_sweep.sh
```

The inferred rows completed with matching checksum/output and matching region
allocation counters in the companion 20M L2 timing run:
`/Users/siyaoliu/rift/cache/broom-inferred-q17-shopper-20m-l2-20260520/summary.tsv`.

| Case | Status | Query mutator samples/sec | Region alloc/init samples/sec | Safepoint poll samples/sec | Zeroing samples/sec | Other samples/sec | Main interpretation |
|---|---|---:|---:|---:|---:|---:|---|
| `broom-q17-checked-rift` | `ok` | `254.80` | `20.60` | `68.80` | `0.00` | `16.00` | Explicit checked source shape after callback-local cleanup. |
| `broom-q17-checked-rift-inferred` | `ok` | `252.40` | `23.20` | `74.00` | `1.00` | `15.20` | Same profile shape as explicit checked; direct `new` is lowered to checked region allocation. |
| `broom-shopper-checked-rift` | `ok` | `391.60` | `19.60` | `38.60` | `5.00` | `73.20` | Explicit checked source shape after callback-local cleanup. |
| `broom-shopper-checked-rift-inferred` | `ok` | `384.60` | `19.80` | `37.20` | `4.00` | `75.80` | Same profile shape as explicit checked; no residual heap-placement signal. |

Interpretation: the q17/shopper inferred expansion is source-placement evidence,
not a profile win. It proves the ordinary-`new` source form preserves region
placement and removes explicit allocation API plumbing for these high-frequency
retained records, while the remaining L4 buckets stay dominated by generated
query body, safepoints, and region allocation/init.

## 2026-05-20 Wikimedia Loop-Shape Follow-Up

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-wikimedia-loopshape-priv`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260520-wikimedia-loopshape-priv \
RIFT_PROFILE_SECONDS=5 \
RIFT_PROFILE_DELAY_SECONDS=1 \
RIFT_PROFILE_WIKIMEDIA_CLICKSTREAM_RECORDS=10000000 \
RIFT_PROFILE_CASES="wikimedia-clickstream-heap wikimedia-clickstream-checked-rift wikimedia-clickstream-checked-rift-inferred wikimedia-clickstream-checked-scoped" \
  zsh sandbox/run_l4_profile_sweep.sh
```

All four cases completed and matched checksum/output:
checksum `8006060730683441349`, output `9323019`, records read `10000000`.
The first sandboxed attempt could not attach macOS `sample`; the successful
run used elevated process-inspection permission.

| Case group | Status | Scale | Profile artifacts | Main interpretation |
|---|---|---:|---|---|
| Wikimedia clickstream post loop-shape cleanup | `ok` for heap, checked Rift, inferred checked Rift, checked scoped | 10M real compressed TSV rows | `/Users/siyaoliu/rift/cache/profile-sweep-20260520-wikimedia-loopshape-priv/wikimedia-clickstream-*.sample.txt` | Boxed `LongRef`/`BooleanRef`/`IntRef` closure parameters no longer appear in checked top frames. Region allocation remains tiny; remaining checked cost is TSV/hash/input plus the checked session-loop callback. |

## 2026-05-20 Wikimedia Fused-Parser Follow-Up

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-wikimedia-fused-parser`

Timing/counter companion:

- `/Users/siyaoliu/rift/cache/loghub-wikimedia-fused-parser-1m-20260520/summary.tsv`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260520-wikimedia-fused-parser \
RIFT_PROFILE_CASES="wikimedia-clickstream-heap wikimedia-clickstream-checked-rift wikimedia-clickstream-checked-rift-inferred wikimedia-clickstream-checked-scoped" \
  zsh sandbox/run_l4_profile_sweep.sh
```

All four profile rows completed on 10M compressed Wikimedia clickstream rows
with checksum `8006060730683441349` and output `9323019`.

| Case | Status | Parser/input/hash samples/sec | Query/session-loop samples/sec | Safepoint poll samples/sec | Region alloc/init samples/sec | Main interpretation |
|---|---|---:|---:|---:|---:|---|
| `wikimedia-clickstream-heap` | `ok` | `418.20` | `52.60` | `97.60` | `0.00` | Heap still pays the shared byte-line/gzip/TSV floor plus Immix metadata (`93.60/s`). |
| `wikimedia-clickstream-checked-rift` | `ok` | `496.60` | `121.40` | `129.80` | `2.60` | Region allocation remains tiny; explicit checked still has the largest session-loop callback bucket. |
| `wikimedia-clickstream-checked-rift-inferred` | `ok` | `490.20` | `74.20` | `177.20` | `4.80` | Split inferred checked path keeps the same region object count as explicit checked and has lower query/session-loop samples. |
| `wikimedia-clickstream-checked-scoped` | `ok` | `512.40` | `102.40` | `126.60` | `6.20` | Scoped shares the parser floor and has small SafeZone/metadata residue. |

The top-frame shape changed as intended: old separate `tsvFieldHash`,
`tsvFieldInt`, and standalone `stableHash` frames disappear, replaced by the
single fused `readClickstreamFieldsInto` pass. This is a shared parser/hash
fairness cleanup, not a checked-region allocation result. The 1M x3 L2 gate
confirms elapsed moved for every row: heap `1219.250 ms`, checked Rift
`1203.342 ms`, inferred checked Rift `1124.139 ms`, and checked scoped
`1216.653 ms`, all with checksum `250002331971566003` and output `922453`.

## 2026-05-20 Theodolite Loop-Shape Follow-Up

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-theodolite-loopshape`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260520-theodolite-loopshape \
RIFT_PROFILE_SECONDS=5 \
RIFT_PROFILE_DELAY_SECONDS=1 \
RIFT_PROFILE_CASES="theodolite-power-uc4-checked-rift" \
RIFT_PROFILE_THEODOLITE_POWER_RECORDS=1000000 \
  zsh sandbox/run_l4_profile_sweep.sh
```

The checked Rift row completed and matched checksum/output:
checksum `5496025699187626461`, output `61760`, records `1000000`.

| Case | Status | Scale | Profile artifact | Main interpretation |
|---|---|---:|---|---|
| `theodolite-power-uc4-checked-rift` post loop-shape cleanup | `ok` | 1M real compressed UCI power rows | `/Users/siyaoliu/rift/cache/profile-sweep-20260520-theodolite-loopshape/theodolite-power-uc4-checked-rift.sample.txt` | Boxed `IntRef`/`LongRef`/`ObjectRef`/`BooleanRef` callback parameters no longer appear. Coarse buckets are parser/input/hash `168.60 samples/sec`, runtime safepoint/metadata residual `71.20`, heap allocation/init `23.20`, region allocation/init `8.60`, zeroing `10.20`, and query mutator `26.00`. Remaining CPU is mostly source/archive/parser/runtime floor, not region open/close. |

## 2026-05-20 Theodolite Byte-Cursor Parser Follow-Up

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-theodolite-bytecursor-parser`

Timing/counter companion:

- `/Users/siyaoliu/rift/cache/theodolite-bytecursor-parser-1m-l2-20260520/summary.tsv`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_CASES="theodolite-power-uc4-heap theodolite-power-uc4-checked-rift theodolite-power-uc4-checked-scoped" \
RIFT_PROFILE_SECONDS=5 \
RIFT_PROFILE_DELAY_SECONDS=1 \
RIFT_PROFILE_THEODOLITE_POWER_RECORDS=1000000 \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260520-theodolite-bytecursor-parser \
  zsh sandbox/run_l4_profile_sweep.sh
```

All three rows completed on 1M compressed real UCI power records with checksum
`5496025699187626461` and output `61760`.

| Case | Status | Parser/input/hash samples/sec | Query mutator samples/sec | Safepoint poll samples/sec | GC mark/sweep metadata samples/sec | Heap alloc/init samples/sec | Region alloc/init samples/sec | Main interpretation |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `theodolite-power-uc4-heap` | `ok` | `133.80` | `49.80` | `51.40` | `43.40` | `25.60` | `0.00` | Heap still pays shared byte-line/gzip/decimal parsing plus Immix/runtime work. |
| `theodolite-power-uc4-checked-rift` | `ok` | `147.00` | `23.40` | `48.40` | `20.40` | `19.00` | `6.20` | Checked parser/input drops from the prior post-loop-shape `168.60/s`; region allocation remains small. |
| `theodolite-power-uc4-checked-scoped` | `ok` | `148.20` | `24.40` | `50.60` | `24.00` | `19.00` | `8.80` | Scoped has the same shared parser floor and low checked-region lifecycle signal. |

The code change is backend-neutral: `TheodolitePowerRegionMatrix.parseCurrentLine`
now scans the semicolon-delimited byte line directly to fields `2`, `4`, `6`,
`7`, and `8`, then uses the existing byte numeric parsers. A fully fused
numeric parser variant was tried and rejected because the 1M gate regressed.
The accepted 1M x3 L2 gate is heap `2325.524 ms`, checked stream
`1965.787 ms`, and checked scoped `1999.749 ms`, all with matching
checksum/output. This is shared parser/input fairness cleanup, not a
Rift-specific region-allocation result.

## 2026-05-20 LogHub Retained Join Inline-Reset Follow-Up

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-loghub-join-inline-inferred`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260520-loghub-join-inline-inferred \
RIFT_PROFILE_SECONDS=5 \
RIFT_PROFILE_DELAY_SECONDS=2 \
RIFT_PROFILE_LOGHUB_HDFS_INPUT='tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1.tar.gz!HDFS.log' \
RIFT_PROFILE_LOGHUB_SESSION_RECORDS=1000000 \
RIFT_PROFILE_CASES="loghub-retained-join-heap loghub-retained-join-checked-rift loghub-retained-join-checked-rift-inferred loghub-retained-join-checked-scoped" \
  zsh sandbox/run_l4_profile_sweep.sh
```

All four rows completed and matched checksum/output: checksum
`4282190220497908364`, output `0`, records `1000000`.

| Case | Status | Parser/input/hash samples/sec | Callback-ref-shape samples/sec | Safepoint poll samples/sec | GC mark/sweep metadata samples/sec | Main interpretation |
|---|---|---:|---:|---:|---:|---|
| `loghub-retained-join-heap` | `ok` | `598.80` | `0.00` | `177.00` | `13.60` | Heap is dominated by HDFS archive-member parsing/hash plus runtime safepoints; heap allocation and actual mark/sweep metadata appear only as tiny top-frame slices. |
| `loghub-retained-join-checked-rift` | `ok` | `629.40` | `17.00` | `192.20` | `0.00` | Explicit checked is not region-allocation dominated in the profile. The L2 median had high variance, so this row remains a control. |
| `loghub-retained-join-checked-rift-inferred` | `ok` | `622.60` | `12.60` | `189.80` | `0.00` | Inferred checked has nearly the same parser/hash/profile shape as heap/scoped and stays close to them in the L2 row. The callback-ref-shape bucket marks samples in generated closure bodies whose signatures carry `scala.runtime.*Ref`; it is a source-shape marker, not direct allocation time. |
| `loghub-retained-join-checked-scoped` | `ok` | `612.20` | `31.20` | `193.80` | `0.00` | Scoped backend has the same parser/hash floor with more sampled callback-ref-shaped checked body work. |

## 2026-05-20 StreamFlex Callback-Local Follow-Up

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-callback-local`

The checked StreamFlex throughput loop was refactored to keep mutable
checksum/output/drop counters inside the checked open-handle callback. The
20k smoke matched checksum/output for `checked-epoch-stream` and
`checked-epoch-stream-inferred`.

| Case | Status | Callback-ref samples/sec | Traversal/capsule samples/sec | Region alloc/init samples/sec | Query mutator samples/sec | Main interpretation |
|---|---|---:|---:|---:|---:|---|
| `checked-epoch-stream` before callback-local source shape | previous profile | `211.00` | `34.40` | `245.00` | `244.00` | The callback-ref bucket mostly marked generated closure-body shape. |
| `checked-epoch-stream` after callback-local source shape | `ok` | `0.00` | `35.40` | `273.60` | `491.60` | The source shape removes `scala.runtime.*Ref` callback signatures from sampled top frames. After classifying `StreamFlexDesignMatrixHelpers.*anonfun` as query body work, actual capsule/traversal remains small; the remaining targets are query/object pipeline work and region allocation/init. This is profile-clarity cleanup, not a speed claim. |

## Wikimedia Clickstream Follow-Up

Date/time: 2026-05-18 17:25-17:27 CEST.

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260518-172522`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_CASES="wikimedia-clickstream-heap wikimedia-clickstream-checked-rift wikimedia-clickstream-checked-scoped" \
RIFT_PROFILE_SECONDS=15 \
RIFT_PROFILE_DELAY_SECONDS=2 \
RIFT_PROFILE_WIKIMEDIA_CLICKSTREAM_RECORDS=10000000 \
  zsh sandbox/run_l4_profile_sweep.sh
```

All three cases completed and matched checksum/output:
checksum `8006060730683441349`, output `9323019`, records read `10000000`.

| Case | Status | Scale | Profile artifact | Main interpretation |
|---|---|---:|---|---|
| `wikimedia-clickstream-heap` | `ok` | 10M real compressed TSV rows | `/Users/siyaoliu/rift/cache/profile-sweep-20260518-172522/wikimedia-clickstream-heap.sample.txt` | Sampled footprint is about `1.0G`. Top sampled work includes `scalanative_GC_yield`, TSV field hash/int parsing, `stableHash`, byte-line read/append, and Immix marker/heap-block frames. |
| `wikimedia-clickstream-checked-rift` | `ok` | 10M real compressed TSV rows | `/Users/siyaoliu/rift/cache/profile-sweep-20260518-172522/wikimedia-clickstream-checked-rift.sample.txt` | Sampled footprint is about `126.8M`. Top sampled work is TSV field hash/int parsing, `stableHash`, byte-line read/append, and the checked session loop; region close is not the visible bottleneck. |
| `wikimedia-clickstream-checked-scoped` | `ok` | 10M real compressed TSV rows | `/Users/siyaoliu/rift/cache/profile-sweep-20260518-172522/wikimedia-clickstream-checked-scoped.sample.txt` | Sampled footprint is about `127.1M`. It shares the parser/hash/input floor and also shows `Marker_markRange`, `Heap_IsWordInHeap`, small `scalanative_zone_alloc`, and SafeZone-backed allocation samples. |

Interpretation:

- The profile supports the existing L2 explanation: checked Rift removes most
  retained-object GC/RSS pressure, but real clickstream throughput still has a
  large parser/hash/input floor.
- The next optimization target for this row is not close/open bookkeeping. The
  likely fruitful targets are byte-slice TSV field extraction, stable hashing,
  and checked session-loop object construction/linking. Shared parser/hash
  changes must improve both heap and checked rows; checked-only changes should
  preserve the same logical query and output.
- Scoped-specific marker/root-range samples explain why scoped and stream
  should be treated as backend selections under Rift. When scoped wins, either
  choose it automatically for that shape or use the profile to improve the
  Rift streaming backend.

## Retained-Object Gap-Fill Sweep

Date/time: 2026-05-18 17:44-17:52 CEST.

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260518-gap-fill`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_CASES="broom-aggregate-checked-rift broom-aggregate-checked-scoped broom-aggregate-heap ... loghub-retained-join-heap" \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260518-gap-fill \
RIFT_PROFILE_SECONDS=8 \
RIFT_PROFILE_DELAY_SECONDS=1 \
  zsh sandbox/run_l4_profile_sweep.sh
```

All Broom and Theodolite rows completed with matching checksum/output. The
1M LogHub retained rows completed but produced mostly startup/exit samples, so
the LogHub retained rows were rerun at 5M records below.

| Case group | Status | Scale | Profile artifacts | Main interpretation |
|---|---|---:|---|---|
| Broom aggregate active-16 | `ok` for `checked-rift`, `checked-region-scoped`, `heap-gc` | 20M generated retained records | `/Users/siyaoliu/rift/cache/profile-sweep-20260518-gap-fill/broom-aggregate-*.sample.txt` | Checked Rift samples the aggregate loop plus region allocation (`scalanative_rift_region_alloc_object_fast`, `scalanative_rift_region_alloc_nozero`). Heap samples the same loop plus Immix allocator/object metadata, bytemap, marker, and sweep frames. |
| Broom join active-16 | `ok` for `checked-rift`, `checked-region-scoped`, `heap-gc` | 20M generated retained records | `/Users/siyaoliu/rift/cache/profile-sweep-20260518-gap-fill/broom-join-*.sample.txt` | Same retained-object shape as aggregate. The useful profile signal is allocator/object initialization and heap marking/metadata, not timestamp close bookkeeping. |
| Broom Q17 active-16 | `ok` for `checked-rift`, `checked-region-scoped`, `heap-gc` | 20M generated TPC-H-Q17-like records | `/Users/siyaoliu/rift/cache/profile-sweep-20260518-gap-fill/broom-q17-*.sample.txt` | Checked Rift samples generated Q17 query work plus region allocation/nozero. Heap samples generated Q17 work plus `Allocator_Alloc`, `GC_alloc_small`, `ObjectMeta_SetAllocated`, bytemap, and `Heap_IsWordInHeap`. |
| Broom shopper active-16 | `ok` for `checked-rift`, `checked-region-scoped`, `heap-gc` | 20M generated shopper records | `/Users/siyaoliu/rift/cache/profile-sweep-20260518-gap-fill/broom-shopper-*.sample.txt` | Heap has large marker/heap metadata samples (`Heap_IsWordInHeap`, `Marker_Mark`, `Marker_markField`, sweep). Checked Rift is dominated by the shopper loop plus small region allocation/memset. |
| Theodolite retained UC4 | `ok` for `checked-epoch-stream`, `checked-epoch-scoped`, `heap` | full local real UCI power stream, `2049280` records | `/Users/siyaoliu/rift/cache/profile-sweep-20260518-gap-fill/theodolite-power-uc4-*.sample.txt` | Both heap and checked are dominated by byte-line reading, gzip inflate, delimited-field extraction, and `parseMilliDecimal`; heap additionally samples `Allocator_Alloc`, object metadata, and `_platform_memset`. |

## LogHub Retained Rerun

Date/time: 2026-05-18 17:53-17:59 CEST.

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260518-loghub-retained-rerun`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_CASES="loghub-retained-session-checked-rift loghub-retained-session-checked-scoped loghub-retained-session-heap loghub-retained-join-checked-rift loghub-retained-join-checked-scoped loghub-retained-join-heap" \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260518-loghub-retained-rerun \
RIFT_PROFILE_SECONDS=8 \
RIFT_PROFILE_DELAY_SECONDS=0.1 \
RIFT_PROFILE_LOGHUB_SESSION_RECORDS=5000000 \
  zsh sandbox/run_l4_profile_sweep.sh
```

All six rows completed and matched checksum/output. In macOS `sample`, a
long-lived process-exit checker thread appears as a large `kevent` entry; it is
not benchmark CPU. The main-thread samples show the same result for session and
join: `containsAscii`, `String.charAt`/`length`, `stableHash`, `tokenHash`,
`tokenSeparator`, and byte-line reader paths dominate. Allocation and region
frames are small in the visible main-thread stack. Treat LogHub retained
session/join as real-streaming parser/hash/RSS evidence, not a strong allocator
optimization target.

## Representative Sweep

Date/time: 2026-05-12 02:00-02:22 CEST.

Profile directories:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-representative`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-fixes`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-streamit-final`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-yak-graphstep`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-yak-graphstep-post-zone-page-cache`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-yak-graphstep-post-pad-macro`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-real`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-synthetic`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-nexmark-rerun`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-reml-logic-checked-rerun`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-reml-logic-heap-rerun`

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
| `yak-graphstep-checked-scoped` | `ok` | 10 x 5M generated graph messages | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-yak-graphstep/yak-graphstep-checked-scoped.sample.txt` | This is the processing-body profile that the real LiveJournal sample could not isolate. Checked scoped is dominated by the graphstep loop, `scalanative_zone_alloc`, `_platform_memset`, padding/page-size helpers, SafeZone-backed `allocUncheckedImpl`, and checksum. |
| `yak-graphstep-heap` | `ok` | 10 x 5M generated graph messages | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-yak-graphstep/yak-graphstep-heap.sample.txt` | Heap has the same graphstep loop and message construction floor, plus Immix allocator/object metadata, mark/sweep, and weak-reference marking paths. The sampled physical footprint is about `799.8M`, much higher than the checked scoped graphstep sample. |
| `dataflow-aggregate-checked-scoped` | `ok` | 20 x 500k docs | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/dataflow-aggregate-checked-scoped.sample.txt` | Direct checked scoped aggregate is short and mostly a tight aggregate loop plus SafeZone allocation/zeroing. |
| `dataflow-aggregate-epoch-fold` | `ok` | 20 x 500k docs | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/dataflow-aggregate-epoch-fold.sample.txt` | Generic `EpochFold` spends visible time in `findFoldInsertSlot`, `addFoldContribution`, fold table capacity/clear, append/cursor traversal, Rift allocation/stat paths, and `checkOpen`. This explains why it remains speed-gated. |
| `dataflow-aggregate-heap` | `ok` | 20 x 500k docs | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/dataflow-aggregate-heap.sample.txt` | Heap aggregate shows the same query/document construction floor plus Immix allocation, object metadata, mark, and sweep frames. |
| `specjbb-checked-scoped` | `ok` | 1M transactions | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/specjbb-checked-scoped.sample.txt` | The row is too short for a rich call graph; sampled time is mostly transaction proxy/count helpers (`txObjectCount`, `txByteProxy`, `txKind`). Use a larger/delayed profile before tuning allocation here. |
| `specjbb-heap` | `ok` | 1M transactions | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/specjbb-heap.sample.txt` | Similar short-profile shape to checked scoped, with a small number of heap allocator/object metadata samples. |
| `reml-msort-checked-scoped` | `ok` | 1M list size | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/reml-msort-checked-scoped.sample.txt` | The local Scala Native port is dominated by boxed `Integer` compare/valueOf, `ScalaRunTime` array apply/update, `java.util.Arrays` stable merge/insertion sort, plus allocation/zeroing/GC frames. This is a Scala object/boxing/sort-shape result, not a pure region allocator result. |
| `reml-msort-heap` | `ok` | 1M list size | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/reml-msort-heap.sample.txt` | Heap has nearly the same boxed sort shape, plus Immix allocation/object metadata/mark/sweep frames. |
| `reml-ratio-checked-scoped` | `ok` | 2M ratio count | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/reml-ratio-checked-scoped.sample.txt` | Checked scoped `ratio` is mostly `gcd` and arithmetic; region allocation is tiny in the sample. Treat as compute/control evidence. |
| `reml-ratio-heap` | `ok` | 2M ratio count | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-epoch-reml/reml-ratio-heap.sample.txt` | Heap `ratio` is also mostly `gcd`; visible GC frames are secondary. |
| `yak-graphstep-checked-scoped` post page-size cache | `ok` | 10 x 5M generated graph messages | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-yak-graphstep-post-zone-page-cache/yak-graphstep-checked-scoped.sample.txt` | `MemoryPool_page_size` is gone from the checked scoped sample, but the local helper `scalanative_zone_pad8` is still sampled. |
| `yak-graphstep-heap` post page-size cache | `ok` | 10 x 5M generated graph messages | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-yak-graphstep-post-zone-page-cache/yak-graphstep-heap.sample.txt` | Heap profile remains the same-shape control: graphstep loop plus Immix allocation/marking/zeroing. |
| `yak-graphstep-checked-scoped` post pad macro | `ok` | 10 x 5M generated graph messages | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-yak-graphstep-post-pad-macro/yak-graphstep-checked-scoped.sample.txt` | `MemoryPool_page_size`, `Util_pad`, and `scalanative_zone_pad8` are all absent. Remaining checked scoped samples are allocator body, `_platform_memset`, and SafeZone-backed `allocUncheckedImpl` wrappers. |
| `yak-graphstep-heap` post pad macro | `ok` | 10 x 5M generated graph messages | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-yak-graphstep-post-pad-macro/yak-graphstep-heap.sample.txt` | Heap profile remains the control: shared graphstep loop plus Immix allocation/object metadata/marking. |

## Profiling Completion Sweep

Date/time: 2026-05-12 12:31-12:41 CEST.

This pass fills the representative gaps after the first sweep. It does not
turn every historical/control benchmark into a profile target; it covers the
families that can affect the next tuning decisions.

| Case | Status | Scale | Profile artifact | Main interpretation |
|---|---|---:|---|---|
| `yak-topwordreal-checked-scoped` | `ok` | 20M real AskUbuntu tokens | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-real/yak-topwordreal-checked-scoped.sample.txt` | Dominated by XML/text scanning (`matchesAt`, `scanAttribute`, `tokenByte`) and byte-line reader paths. Region allocation is not the leading sampled cost. |
| `yak-topwordreal-topk-scoped` | `ok` | 20M real AskUbuntu tokens | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-real/yak-topwordreal-topk-scoped.sample.txt` | Same parser/token floor as direct epoch. Reusable top-k is not the dominant sampled cost. |
| `yak-topwordreal-heap` | `ok` | 20M real AskUbuntu tokens | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-real/yak-topwordreal-heap.sample.txt` | Natural heap has the same XML/text parsing floor; this explains why real text rows are modest throughput wins but strong RSS wins. |
| `yak-topwordreal-heap-topk` | `ok` | 20M real AskUbuntu tokens | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-real/yak-topwordreal-heap-topk.sample.txt` | Same-shape heap top-k remains parser dominated. |
| `loghub-spark-topk-checked` | `ok` | 2M real Spark log lines, 3 files | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-real/loghub-spark-topk-checked.sample.txt` | Byte-line read, `tokenStartAfter`, `stableHash`, token separator, and token counting dominate. |
| `loghub-spark-topk-heap` | `ok` | 2M real Spark log lines, 3 files | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-real/loghub-spark-topk-heap.sample.txt` | Same parser/hash floor as checked. Heap GC is not the dominant CPU path. |
| `loghub-windows-topk-checked` | `ok` | 5M real Windows streaming log lines | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-real/loghub-windows-topk-checked.sample.txt` | Template scanning and hashing dominate; top-k/region costs are secondary. |
| `loghub-windows-topk-heap` | `ok` | 5M real Windows streaming log lines | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-real/loghub-windows-topk-heap.sample.txt` | Same parser/hash floor. This supports classifying Windows as modest/RSS evidence rather than a GC-heavy throughput proof. |
| `theodolite-power-q2-checked-scoped` | `ok` | 2M real power records x 20 L1 loops | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-real/theodolite-power-q2-checked-scoped.sample.txt` | Dominated by `BufferedReader`, UTF-8 decode, `String.indexOf`, `StringBuilder`, decimal parsing, and `String.charAt`. |
| `theodolite-power-q2-heap` | `ok` | 2M real power records x 20 L1 loops | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-real/theodolite-power-q2-heap.sample.txt` | Same string/parser floor as checked. Theodolite q2 should stay a parser-heavy control unless a shared byte parser is added. |
| `nexmark-q8-checked` | `ok` | 5M generated events | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-synthetic/nexmark-q8-checked.sample.txt` | Short but useful checked join sample: join bucket body, event-kind/bucket-start logic, and small memset samples. |
| `nexmark-q8-heap` | `ok` | 25M generated events rerun | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-nexmark-rerun/nexmark-q8-heap.sample.txt` | Heap join is bucket lookup/consume/append/event-kind CPU with small allocator samples. |
| `nexmark-q9-checked` | `ok` | 5M generated events | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-synthetic/nexmark-q9-checked.sample.txt` | Allocation and Scala Native helper overhead are visible: `Allocator_Alloc`, `String.equals`, `USize`/`UInt.valueOf`, unsafe array access, and unboxing. |
| `nexmark-q9-heap` | `ok` | 5M generated events | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-synthetic/nexmark-q9-heap.sample.txt` | Same helper/array/string shape as checked, plus heap allocation/zeroing. |
| `specjbb-large-checked-scoped` | `ok` | 8 warehouses x 1M transactions/warehouse | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-synthetic/specjbb-large-checked-scoped.sample.txt` | Transaction helper/proxy work is significant (`txObjectCount`, `txByteProxy`, `processCheckedReceipt`), with visible `scalanative_zone_alloc`. |
| `specjbb-large-heap` | `ok` | 8 warehouses x 1M transactions/warehouse | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-synthetic/specjbb-large-heap.sample.txt` | Same transaction-helper floor plus `Allocator_Alloc`; allocation matters, but transaction model helpers are also hot. |
| `reml-logic-checked-scoped` | `ok` | 5M iterations rerun | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-reml-logic-checked-rerun/reml-logic-checked-scoped.sample.txt` | Checked region nodes are not enough to remove heap pressure: per-build heap scratch arrays still trigger `Heap_IsWordInHeap` and `Marker_markRange`, with smaller zone allocation samples. |
| `reml-logic-heap` | `ok` | 5M iterations rerun | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-reml-logic-heap-rerun/reml-logic-heap.sample.txt` | Heap logic shows `buildHeapLogic`, `evalHeapLogic`, `Allocator_Alloc`, object metadata, and memset. |
| `reml-ray-checked-scoped` | `ok` | 256 spheres x 100k rays | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-synthetic/reml-ray-checked-scoped.sample.txt` | Mostly ray compute body; memory management is not the leading cost. |
| `reml-ray-heap` | `ok` | 256 spheres x 100k rays | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-synthetic/reml-ray-heap.sample.txt` | Mostly `runHeapRay`; compute/control evidence. |
| `reml-tsp-checked-scoped` | `ok` | 1024 points x 1024 starts | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-synthetic/reml-tsp-checked-scoped.sample.txt` | Mostly TSP/distance loop. |
| `reml-tsp-heap` | `ok` | 1024 points x 1024 starts | `/Users/siyaoliu/rift/cache/profile-sweep-20260512-completion-synthetic/reml-tsp-heap.sample.txt` | Mostly TSP/distance loop; compute/control evidence. |

Remaining useful additions:

- A Yak LiveJournal processing-phase profile that avoids sampling only gzip/file
  parsing. The generated graphstep profile now covers epoch CPU; a delayed or
  preloaded real LiveJournal profile is still useful if tuning must preserve
  real-input provenance in the profile itself.
- `samply` flamegraphs for the same representative rows if `samply` becomes
  available on this shell; use those to inspect visible GC pauses interactively.
- No further broad profiling sweep is needed before the next optimization pass.

## Post-Rerun Clean-Winner Profiles

Date/time: 2026-05-12 16:41-16:42 CEST.

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-post-rerun-20260512-clean-winners`

Command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-post-rerun-20260512-clean-winners \
RIFT_PROFILE_CASES="streamflex-design-checked-stream commoncrawl-q2-checked-rift" \
RIFT_PROFILE_SECONDS=8 \
RIFT_PROFILE_DELAY_SECONDS=0.5 \
RIFT_PROFILE_BUILD=1 \
RIFT_PROFILE_STREAMFLEX_EVENTS=20000000 \
RIFT_PROFILE_COMMON_CRAWL_PAGES=2000000 \
  zsh sandbox/run_l4_profile_sweep.sh
```

| Case | Status | Scale | Profile artifact | Main interpretation |
|---|---|---:|---|---|
| `streamflex-design-checked-stream` | `ok` | 20M generated StreamFlex-design events | `/Users/siyaoliu/rift/cache/profile-post-rerun-20260512-clean-winners/streamflex-design-checked-stream.sample.txt` | The clean checked-stream winner is not close/open dominated. Samples are concentrated in `processCheckedPeriod`, `scalanative_rift_region_alloc_object_fast`, `_platform_memset`, `StableState.classify`, `StableState.recordEvent`, capsule add/drain, and the remaining per-allocation `scalanative_rift_alloc_stats_enabled` check. |
| `commoncrawl-q2-checked-rift` | `ok` | 2M generated WET-shaped pages | `/Users/siyaoliu/rift/cache/profile-post-rerun-20260512-clean-winners/commoncrawl-q2-checked-rift.sample.txt` | The clean Rift page-token winner spends most sampled time in close cursor traversal, page-token append/linking, region object allocation/zeroing, token hashing/query work, and the same remaining allocation-stats enable check. This reinforces that the next speed work is allocation lowering/zeroing/stat-check removal or reducing required record traversal, not more bucket close/open bookkeeping. |

## Post Region-Cached Stats Profiles

Date/time: 2026-05-12 17:11-17:16 CEST.

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-post-region-cached-stats-20260512`

Command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-post-region-cached-stats-20260512 \
RIFT_PROFILE_CASES="streamflex-design-checked-stream commoncrawl-q2-checked-rift" \
RIFT_PROFILE_SECONDS=4 \
RIFT_PROFILE_DELAY_SECONDS=0.5 \
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_STREAMFLEX_EVENTS=20000000 \
RIFT_PROFILE_COMMON_CRAWL_PAGES=2000000 \
  zsh sandbox/run_l4_profile_sweep.sh
```

| Case | Status | Scale | Profile artifact | Main interpretation |
|---|---|---:|---|---|
| `streamflex-design-checked-stream` | `ok` | 20M generated StreamFlex-design events | `/Users/siyaoliu/rift/cache/profile-post-region-cached-stats-20260512/streamflex-design-checked-stream.sample.txt` | `scalanative_rift_alloc_stats_enabled` is no longer sampled. Remaining samples are allocation body, `_platform_memset`, stable-state classify/update work, and capsule add/drain. |
| `commoncrawl-q2-checked-rift` | `ok` | 2M generated WET-shaped pages | `/Users/siyaoliu/rift/cache/profile-post-region-cached-stats-20260512/commoncrawl-q2-checked-rift.sample.txt` | `scalanative_rift_alloc_stats_enabled` is no longer sampled. Remaining samples are close cursor traversal, page-token append/linking, region allocation, `_platform_memset`, and token/hash/query work. |

Interpretation: caching allocation-stats mode at region open removes the
profiled helper from clean final paths. Focused object allocation is mixed, so
the accepted claim is profile cleanup plus modest application improvement, not
a new focused allocation win.

## Post Stats-Disabled Object Fast-Path Profile

Date/time: 2026-05-20 00:00 CEST.

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-nostats-fastpath`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-nostats-fastpath \
RIFT_PROFILE_SECONDS=5 \
RIFT_PROFILE_DELAY_SECONDS=1 \
RIFT_PROFILE_STREAMFLEX_EVENTS=20000000 \
RIFT_PROFILE_CASES="streamflex-design-checked-stream" \
  zsh sandbox/run_l4_profile_sweep.sh
```

| Case | Status | Scale | Profile artifact | Main interpretation |
|---|---|---:|---|---|
| `streamflex-design-checked-stream` | `ok` | 20M generated StreamFlex-design events | `/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-nostats-fastpath/streamflex-design-checked-stream.sample.txt` | Coarse buckets are traversal/capsule `1227` samples (`245.40/s`), region allocation/init `1225` (`245.00/s`), query mutator `1220` (`244.00/s`), and other `145` (`29.00/s`). The L1 transfer gate improved, but the sample mix remains balanced; this is allocator-body constant-cost cleanup, not a new topology or query-shape change. |

## Post Final-Clean Region-Op Timing Guard Profile

Date/time: 2026-05-20 16:05 CEST.

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-timing-guard`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_CASES="streamflex-design-checked-stream" \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-timing-guard \
RIFT_PROFILE_EXTRA_ENV="STREAMFLEX_DESIGN_EVENTS=20000000 STREAMFLEX_DESIGN_BENCHMARK_RUNS=1 STREAMFLEX_DESIGN_WARMUPS=0" \
  zsh sandbox/run_l4_profile_sweep.sh
```

| Case | Status | Scale | Profile artifact | Main interpretation |
|---|---|---:|---|---|
| `streamflex-design-checked-stream` | `ok` | 20M generated StreamFlex-design events | `/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-timing-guard/streamflex-design-checked-stream.sample.txt` | No `mach_absolute_time`, `scalanative_rift_now_ns`, or duration-accounting frames are sampled after guarding region-op timing behind stats-enabled mode. Coarse buckets are query mutator `467.80/s`, region allocation/init `244.20/s`, traversal/capsule `30.20/s`, and other `25.40/s`, so the remaining optimization target is allocator/object pipeline work, not timer bookkeeping. |
| `streamflex-design-checked-stream-inferred` | `ok` | 20M generated StreamFlex-design events | `/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-inferred-timing-guard/streamflex-design-checked-stream-inferred.sample.txt` | The inferred allocation row keeps the same dominant bucket shape as explicit checked stream: query mutator `464.40/s`, region allocation/init `251.00/s`, traversal/capsule `34.80/s`, and other `22.40/s`. Since L1 improves to `18.16 s` from explicit checked `19.01 s`, this is an inferred-source/lowering speedup rather than a topology change. |

## Post LogHub Inferred Array Source Profile

Date/time: 2026-05-21 06:45-06:50 CEST.

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260521-loghub-array-source`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260521-loghub-array-source \
RIFT_PROFILE_SECONDS=5 \
RIFT_PROFILE_DELAY_SECONDS=1 \
RIFT_PROFILE_WIKIMEDIA_CLICKSTREAM_RECORDS=10000000 \
RIFT_PROFILE_CASES="wikimedia-clickstream-heap wikimedia-clickstream-checked-rift wikimedia-clickstream-checked-rift-inferred wikimedia-clickstream-checked-scoped loghub-retained-join-heap loghub-retained-join-checked-rift loghub-retained-join-checked-rift-inferred loghub-retained-join-checked-scoped" \
  zsh sandbox/run_l4_profile_sweep.sh
```

All eight cases completed with matching checksum/output.

| Case | Status | Scale | Bucket summary | Main interpretation |
|---|---|---:|---|---|
| `wikimedia-clickstream-heap` | `ok` | 10M compressed real Wikimedia rows | parser/input/hash `341.80/s`, query/session loop `58.00/s`, safepoint `105.20/s`, GC/meta `124.60/s`, heap alloc/init `2.80/s` | Heap has the same TSV/hash/session floor plus visible GC/metadata work. The parser/input/hash bucket is lower than checked rows in absolute samples/sec, not merely larger by proportion. |
| `wikimedia-clickstream-checked-rift` | `ok` | 10M compressed real Wikimedia rows | parser/input/hash `501.20/s`, query/session loop `118.20/s`, region alloc/init `3.60/s`, safepoint `119.00/s`, GC/meta `0.00/s` | Explicit checked removes the GC/meta bucket but still shows higher parser/input/hash and session-loop samples/sec than heap. Region allocation is not the bottleneck. |
| `wikimedia-clickstream-checked-rift-inferred` | `ok` | 10M compressed real Wikimedia rows | parser/input/hash `477.00/s`, query/session loop `80.80/s`, region alloc/init `4.40/s`, safepoint `172.80/s`, callback-ref `0.00/s` | Current inferred source shape is lower than explicit checked in parser/input/hash and session-loop buckets, with no callback-ref marker and tiny region allocation. The remaining overhead is still TSV/hash/input plus session-loop body; the profile does not show a token/handle or region-allocation bottleneck. |
| `wikimedia-clickstream-checked-scoped` | `ok` | 10M compressed real Wikimedia rows | parser/input/hash `493.00/s`, query/session loop `106.60/s`, region alloc/init `6.00/s`, safepoint `136.80/s`, token/handle `1.00/s` | Scoped checked has the same parser/session-loop shape with slightly visible SafeZone/token work. |
| `loghub-retained-join-*` | `ok` | 1M compressed HDFS archive-member rows | heap/explicit/inferred/scoped parser/input/hash `578.60/589.40/585.60/585.60/s`; safepoint `178.80/175.40/180.20/168.60/s`; callback-ref `0.00/6.60/0.00/14.20/s` | The join run is short enough that startup/idle is about half the sample, so this row is diagnostic only. The active work remains parser/input/hash plus safepoint polling; inferred checked removes the small callback-ref marker visible in explicit checked for this run. |

## Post ByteLineReader Chunked Input Profile

Date/time: 2026-05-21 07:03-07:06 CEST.

Profile directory:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260521-bytereader-loghub`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=0 \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260521-bytereader-loghub \
RIFT_PROFILE_SECONDS=5 \
RIFT_PROFILE_DELAY_SECONDS=1 \
RIFT_PROFILE_WIKIMEDIA_CLICKSTREAM_RECORDS=10000000 \
RIFT_PROFILE_CASES="wikimedia-clickstream-heap wikimedia-clickstream-checked-rift wikimedia-clickstream-checked-rift-inferred wikimedia-clickstream-checked-scoped loghub-retained-join-heap loghub-retained-join-checked-rift loghub-retained-join-checked-rift-inferred loghub-retained-join-checked-scoped" \
  zsh sandbox/run_l4_profile_sweep.sh
```

All eight cases completed with matching checksum/output.

| Case | Status | Scale | Bucket summary | Main interpretation |
|---|---|---:|---|---|
| `wikimedia-clickstream-heap` | `ok` | 10M compressed real Wikimedia rows | parser/input/hash `385.80/s`, query/session loop `60.00/s`, safepoint `81.40/s`, GC/meta `101.80/s`, heap alloc/init `7.00/s` | The old per-byte `ByteLineReader.nextByte`/`append` top frames are absent; sampled input work is now the chunked `readLine` body plus TSV/hash parsing. |
| `wikimedia-clickstream-checked-rift` | `ok` | 10M compressed real Wikimedia rows | parser/input/hash `478.80/s`, query/session loop `133.20/s`, region alloc/init `6.00/s`, safepoint `115.60/s`, GC/meta `0.00/s` | Explicit checked still removes GC/meta but has higher parser/session-loop samples/sec than heap. Region allocation remains tiny. |
| `wikimedia-clickstream-checked-rift-inferred` | `ok` | 10M compressed real Wikimedia rows | parser/input/hash `510.40/s`, query/session loop `94.80/s`, region alloc/init `5.40/s`, safepoint `110.60/s`, callback-ref `0.00/s` | The inferred row keeps the lower query/session-loop shape relative to explicit checked, but the coarse parser bucket does not uniformly fall in this five-second sample. Treat L2 timing as the accepted throughput evidence. |
| `wikimedia-clickstream-checked-scoped` | `ok` | 10M compressed real Wikimedia rows | parser/input/hash `484.60/s`, query/session loop `118.00/s`, region alloc/init `8.60/s`, safepoint `119.60/s`, token/handle `0.00/s` | Same shared parser/input floor with small scoped allocation/zeroing samples. |
| `loghub-retained-join-*` | `ok` | 1M compressed HDFS archive-member rows | heap/explicit/inferred/scoped parser/input/hash `578.80/573.00/583.20/569.20/s`; safepoint `171.40/182.20/177.00/176.80/s`; callback-ref `0.00/11.20/0.00/19.00/s` | The join profile remains startup/idle-contaminated because the run is short; active work is still archive/input parsing plus safepoint polling. The useful evidence for the reader change is the 1M L2 gate, not this bucket mix. |

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
