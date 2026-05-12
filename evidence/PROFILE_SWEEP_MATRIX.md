# L4 Profile Sweep Matrix

Last updated: 2026-05-12 17:22 CEST

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
| `streamflex-design-checked-stream` | StreamFlex design reproduction | Profile the clean rerun winner: checked direct epoch over the Rift streaming backend. |
| `commoncrawl-q2-checked-rift` | Generated GC-heavy page/window stream | Profile the clean rerun winner: Rift-backed checked page-token q2. |
| `commoncrawl-q2-checked-scoped` / `commoncrawl-q2-heap` | Generated GC-heavy page/window stream | Explain allocation+append, token hashing, cursor traversal, and GC-heavy generated stream behavior. |
| `dspbench-fraud-q2-checked-scoped` / `dspbench-fraud-q2-heap` | Real DSPBench stream regression | Check whether parser/replay/predictor CPU still dominates real-input rows. |
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
