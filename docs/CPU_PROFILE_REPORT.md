# Rift CPU Profiling Report

Last updated: 2026-05-12 13:35 CEST

Status: representative L4 profiling coverage is complete for the current
headline/tuning set. The first profile-driven implementation follow-up removed
sampled zone page-size/padding helpers from Yak graphstep. The completion pass
adds real text/top-k, richer LogHub, Theodolite, NEXMark Q8/Q9, larger
SPECjbb2005-workload, and ReML Tier-2 shaped profiles. The first
post-profiling allocation-path cleanup now disables Rift allocation counters in
`RIFT_FINAL_CLEAN=1` runs.

Reference: Scala Native official profiling guide:
<https://scala-native.org/en/stable/user/profiling.html>

## Purpose

Use profiling to explain remaining CPU cost after region allocation/reclaim has
already removed GC pressure. Profiling rows are diagnostic evidence, not
headline benchmark timing.

This report follows `evidence/MEASUREMENT_OVERHEAD_PROTOCOL.md`: `samply`,
macOS `sample`, and Linux `perf` are L4 external profiles. They can show CPU
composition and visible GC pause/collection frames, but their elapsed time is
not a headline timing result.

The current questions are:

- how much time is object construction versus allocator lowering;
- how much time is checked operator bookkeeping;
- how much time is traversal/checksum/output work shared with heap;
- whether SafeZone-backed checked rows spend time in root/page claim/reclaim;
- whether failed operators such as `EpochFold` and TableRank are losing in
  allocation, lookup/probe, callback/cursor, or aggregation logic.

## Profile Sweep Harness

`sandbox/run_l4_profile_sweep.sh` now provides the reusable L4 profiling entry
point in the child implementation repo. It native-links benchmark main classes,
runs the selected native binary, and samples it with macOS `/usr/bin/sample`
or Linux `perf`.

Default:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
zsh sandbox/run_l4_profile_sweep.sh
```

Representative sweep:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_CASES=all \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-$(date +%Y%m%d-%H%M%S) \
  zsh sandbox/run_l4_profile_sweep.sh
```

The current representative cases cover StreamFlex-design, generated Common
Crawl-shaped q2, DSPBench Fraud q2, LogHub HDFS/Spark/Windows top-k,
Theodolite power q2, StreamIt FilterBank/BeamFormer, Yak LiveJournal graph
replay, AskUbuntu top-word, Dataflow AGGREGATE, NEXMark Q8/Q9, the
SPECjbb2005-workload port, ReML-shaped Tier 1/Tier 2 ports, and a Yak graphstep
epoch-body profile. Details and smoke/full-sweep results are tracked in
`evidence/PROFILE_SWEEP_MATRIX.md`.

## Representative L4 Sweep Findings

The first representative sweep ran on 2026-05-12 using macOS `/usr/bin/sample`.
Raw profile artifacts are kept under:

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

Summary:

| Family | Profiled rows | Main finding | Optimization implication |
|---|---|---|---|
| StreamFlex design reproduction | `checked-epoch-scoped`, `gc-heap` | Checked scoped time splits across `processCheckedPeriod`, stable-state query work, SafeZone/zone allocation, zeroing, and capsule add/drain. Heap shares the query/capsule floor and pays Immix allocator/object metadata. | More close/open tuning is unlikely to explain the gap. The next useful work is transient object layout/count, allocation zeroing/alignment, or a closer capsule/runtime representation. |
| Generated Common Crawl-shaped q2 | checked scoped page-token, heap | Both modes spend heavily in required close traversal and token/hash query work. Checked scoped also shows SafeZone allocation/zeroing and marker/root frames; heap shows Immix allocation/mark/sweep frames. | This remains a good GC/object-pressure stressor, but further speedups require reducing allocation/object construction and traversal, not only reclaim. |
| DSPBench Fraud q2 real file-backed | checked scoped page-token, heap | The real row is dominated by byte-line reading, stable hashing, CSV parsing, and predictor updates. Allocator work is visible but not the leading sampled cost. | Fraud q2 is useful real-input regression/RSS evidence. It is not the flagship GC-heavy row unless parser/query CPU is made cheaper under fair heap and region controls. |
| LogHub HDFS streaming top-k | checked scoped top-k, heap retained/drop-anchor | The top sampled paths are streaming line read, stable hash, template-token parsing, and token counting. `EpochTopKByKey` and region allocation are small in the sampled window. | This explains why LogHub is a modest/RSS real-streaming row, not a GC-heavy throughput proof. |
| StreamIt FilterBank/BeamFormer | checked epoch, heap | FilterBank is almost entirely numeric kernel work; BeamFormer is almost entirely FIR filter state stepping. Allocator/GC frames are tiny. | Keep BeamFormer/FilterBank as StreamFlex/StreamIt methodology controls. They do not currently demonstrate region memory-management wins. |
| Yak LiveJournal graph replay | `checked-epoch-scoped`, `gc-heap` | The first 50M LiveJournal samples mostly catch gzip/file input parsing and byte-line read/inflate paths before the direct-epoch processing phase dominates. | This profile is useful input-path evidence, but it should not drive epoch allocator tuning. Add a processing-phase profile or preloaded processing-only profile before optimizing Yak. |
| Yak graphstep epoch body | `checked-epoch-scoped`, `gc-heap` | The generated 50M-message graphstep profile isolates the epoch processing body. The original checked scoped sample showed graphstep loop work plus `scalanative_zone_alloc`, `_platform_memset`, padding/page-size helpers, SafeZone-backed `allocUncheckedImpl`, and checksum. The post-allocator-cleanup sample removes `MemoryPool_page_size`, `Util_pad`, and `scalanative_zone_pad8` from the sampled checked stack. Heap has the same graphstep/message floor plus Immix allocation, object metadata, mark/sweep, and weak-reference marking; the sampled heap footprint is about `799.8M`. | This is the actionable Yak CPU profile. The first allocator bookkeeping cleanup is validated; the remaining checked cost is allocation body, object construction/mandatory zeroing, and SafeZone-backed allocation wrappers in a tight linked-object epoch, not bucket close/open bookkeeping. |
| AskUbuntu real text top-word | direct checked epoch, reusable checked `EpochTopKByKey`, natural heap, same-shape heap top-k | All four profiles are dominated by XML/text scanning: `RealTextInput.matchesAt`, `scanAttribute`, `tokenByte`, byte-line append/next-byte/read-line, and lower-casing. Region/top-k/GC frames are small in the sampled windows. | This explains why AskUbuntu is a real-input throughput/RSS win but not a huge-GC row. Further speed would come from a better streaming XML/text parser or byte-slice tokenizer, not from more region close/open tuning. |
| LogHub Spark/Windows top-k | checked scoped top-k and retained heap/drop-anchor | Spark and Windows both sample template scanning and hashing first: `tokenStartAfter`, `tokenSeparator`, `stableHash`, `countTokensFrom`, and byte-line reader paths. Checked and heap have almost identical parser/hash floors. | Reusable top-k is not the bottleneck in these real log rows. They remain retained-object/RSS/modest-throughput evidence; the parser/hash path hides most GC/region-management differences. |
| Theodolite power q2 | `checked-epoch-scoped`, `gc-heap` | Both modes are dominated by `BufferedReader.readLine`, UTF-8 decoding, `String.indexOf`, `StringBuilder.append0`, `parseMilliDecimal`, and `String.charAt`. | The UCI/Theodolite row is parser/string dominated. If this becomes a case study, the fair next optimization is a shared byte-line numeric parser for both heap and checked modes. |
| NEXMark Q8/Q9 | Q8 join API checked/heap, Q9 checked/heap | Q8 is operator/bucket CPU: bucket lookup, event kind, bucket start, append/consume record, plus small allocation. Q9 samples allocator paths plus Scala Native string/unsafe-array/boxing/unboxing helpers (`Allocator_Alloc`, `String.equals`, `USize`/`UInt.valueOf`, `UnsafeRichArray.at`, `Boxes.unboxToPtr`). | Q8/Q9 should remain operator-gated methodology rows. A reusable hash/join/top-k API would need to reduce the operator lookup/indexing path, not just change reclaim. |
| Larger SPECjbb2005-workload port | 8 warehouses x 1M transactions/warehouse | Checked scoped now samples transaction helper CPU (`txObjectCount`, `txByteProxy`, `txKind`), `processCheckedReceipt`, and visible `scalanative_zone_alloc`. Heap samples the same transaction helper floor plus `Allocator_Alloc`. | The larger profile is useful: transaction model/proxy helpers are significant, and allocation is visible but not the only bottleneck. Any optimization should simplify transaction object/proxy construction before claiming scheduler/runtime effects. |
| ReML Tier-2 shaped ports | `logic`, `ray`, `tsp` checked/heap | `ray` and `tsp` are mostly compute/geometry loops (`runHeapRay`/checked body, `runHeapTsp`/checked body, distance functions). `logic` at larger scale is allocation-sensitive: heap shows `buildHeapLogic`, `evalHeapLogic`, `Allocator_Alloc`, object metadata and memset; checked scoped unexpectedly shows heavy `Heap_IsWordInHeap`/`Marker_markRange` because the port still allocates per-build heap scratch arrays. | ReML-shaped rows need careful interpretation. `ray`/`tsp` are compute controls. `logic` reveals a port-shape issue: checked region nodes are not enough if heap scratch arrays remain in the hot loop. Fixing that would require a same-shape reusable scratch buffer or region-array policy, not a raw Rift-vs-ReML wall-clock claim. |
| Dataflow AGGREGATE | direct checked scoped, true `EpochFold`, heap | Direct checked scoped aggregate is mostly a tight aggregate loop plus SafeZone allocation/zeroing. Generic `EpochFold` spends time in fold-slot lookup/probing, contribution updates, fold-table clear/capacity, append/cursor traversal, Rift allocation/stat paths, and `checkOpen`. Heap shows Immix allocation/metadata/mark/sweep on top of the same query floor. | Keep direct `RiftRegion.epoch` as the Dataflow aggregate headline topology. Do not headline `EpochFold` until it is redesigned as a specialized operator-owned table or the generic lookup/cursor/allocation costs are removed. |
| SPECjbb2005-workload port | checked scoped transaction, heap | The 1M transaction samples are short and mostly hit transaction proxy/count helpers (`txObjectCount`, `txByteProxy`, `txKind`), with only small allocator/metadata samples. | Use larger or delayed profiles before tuning transaction allocation. Current evidence says the row is too short for reliable attribution. |
| ReML-shaped `msort` | checked scoped, heap | Both local Scala Native ports are dominated by boxed `Integer` compare/valueOf, `ScalaRunTime` array apply/update, and `java.util.Arrays` stable merge/insertion sort. Allocation/zeroing and Immix mark/sweep are visible but not isolated as the only bottleneck. | Interpret `msort` as a Scala object/boxing/list-sort comparison, not a pure allocator benchmark. If it becomes important, add a same-shape unboxed/control row rather than claiming raw Rift-vs-ReML wall-clock. |
| ReML-shaped `ratio` | checked scoped, heap | Both modes are mostly `gcd` and arithmetic. Region allocation and GC are small in the sampled windows. | Keep `ratio` as compute/control evidence in the ReML same-axes table. It is not a memory-management optimization target. |

## Profile-Guided Allocator Follow-Up

Date/time: 2026-05-12 11:24-11:31 CEST.

Child checkpoints:

- `6c23be380` (`Cache zone page size in allocator`)
- `9ee340950` (`Inline zone allocation padding`)

Commands:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_BUILD=1 \
RIFT_PROFILE_SECONDS=3 \
RIFT_PROFILE_DELAY_SECONDS=0.1 \
RIFT_PROFILE_CASES="yak-graphstep-checked-scoped yak-graphstep-heap" \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260512-yak-graphstep-post-zone-page-cache \
  zsh sandbox/run_l4_profile_sweep.sh

RIFT_PROFILE_BUILD=1 \
RIFT_PROFILE_SECONDS=3 \
RIFT_PROFILE_DELAY_SECONDS=0.1 \
RIFT_PROFILE_CASES="yak-graphstep-checked-scoped yak-graphstep-heap" \
RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260512-yak-graphstep-post-pad-macro \
  zsh sandbox/run_l4_profile_sweep.sh
```

Result:

| Checkpoint | Checked scoped sampled allocator finding | Interpretation |
|---|---|---|
| Baseline graphstep profile | `MemoryPool_page_size` and `Util_pad` were visible under `scalanative_zone_alloc`. | Page-size lookup and generic padding were avoidable allocator bookkeeping in the checked scoped epoch body. |
| `6c23be380` | `MemoryPool_page_size` disappeared, but the debug-build local helper `scalanative_zone_pad8` still appeared in the sample. | Caching page size worked; the inline helper was still callable in the native debug profile. |
| `9ee340950` | `MemoryPool_page_size`, `Util_pad`, and `scalanative_zone_pad8` are all absent. Remaining sampled checked frames are `scalanative_zone_alloc`, `_platform_memset`, and SafeZone-backed `allocUncheckedImpl` wrappers. | The first allocator bookkeeping cleanup is complete. Further speed work would need to address allocation lowering/object construction/zeroing rather than this page-size/padding path. |

Allocation-counter follow-up, 2026-05-12:

`scalanative_rift_region_alloc` and `scalanative_rift_region_alloc_raw` now skip
Rift raw/object/byte allocation counters automatically when
`RIFT_FINAL_CLEAN=1`. A focused 5M `ObjectAllocationLoweringMatrix`
`rift-checked-rift` gate improved from `87.999 ms` with
`RIFT_ALLOC_STATS=1` forced on to `76.345 ms` with final-clean counters
disabled, with matching checksum and no GC. This is a narrow L1/headline-mode
cleanup. L2/stat rows should keep allocation counters enabled when region object
counts are needed for interpretation.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`: `141/141`
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`: `64/64`, rerun after the macro change

## Profiling Rules

- Do not profile with `SAFEZONE_TRACE=1`, allocation attribution, or precise
  allocation counters enabled unless the row is explicitly diagnostic.
- Keep profile binaries and inputs identical to the corresponding benchmark
  row except for debug/symbol options required by the profiler.
- Record command, binary path, benchmark mode, input scale, environment,
  profiler tool, and whether the profile was sampled or instrumented.
- Do not use profiler elapsed time as a headline median.

## Samply Plan

Use `samply` as the preferred macOS flamegraph profiler when it is available.
It complements `/usr/bin/sample`: `sample` is fast and easy to script, while
`samply` gives an interactive profile UI and can expose both CPU composition
and visible GC pause/collection frames.

The profiling questions for `samply` are:

- how much time is in Immix GC pause/mark/sweep/collection frames;
- how much time is in region allocation, `scalanative_zone_alloc`,
  `scalanative_rift_region_alloc`, zeroing, alignment, or stats paths;
- how much time is in object construction and constructor field stores;
- how much time is in checked lowering such as `allocImpl`, `checkOpen`, or
  `allocUncheckedImpl`;
- how much time is in operator CPU: append/linking, cursor traversal,
  bucket-close callbacks, aggregation, hashing, parser work, and checksum/output
  logic.

Profiles must target the Scala Native binary directly, not `sbt run`, so sbt
and JVM launcher work do not pollute the profile:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" nativeLink
samply record <path-to-linked-sandbox-binary> <mode> <query>
```

First `samply` targets:

| Target | Modes | What to inspect |
|---|---|---|
| Generated Common Crawl-shaped q2 | `heap-immix`, `rift-checked-page-token`, `rift-checked-safezone-page-token` | Immix GC pause frames versus checked allocation/append/cursor/query CPU. |
| DSPBench Fraud q2 | `heap-immix`, `rift-trusted-streaming`, `rift-checked-safezone-page-token` | Whether the remaining real-input gap is parser/predictor CPU, cursor traversal, or allocation. |
| LogHub BGL q3 | `heap-immix`, `rift-trusted-streaming`, `rift-checked-safezone-page-token` | Whether richer real log template/session rows spend visible time in GC or mostly parser/hash/window CPU. |
| Focused page-token cost matrix | heap same-shape and checked scoped page-token rows | Fine-grained append, allocation, cursor, and close attribution without application parser noise. |

At the time of this note, `samply` was not on this shell's `PATH`; install or
expose it before running these rows. Keep resulting `samply` profiles under an
ignored cache directory and summarize only the findings in this report.

## Useful Scala Native Profiling Tips

- Treat Scala Native output as a native binary. Use platform profilers where
  available.
- Use `/usr/bin/time -l` on macOS for external real/user/sys time and peak RSS
  around the profiled binary. On Linux, the Scala Native guide recommends
  `/usr/bin/time --verbose` for elapsed time and memory consumption.
- Use `samply` when available for sampled profiles and flamegraph-style
  inspection of native Scala Native binaries; the Scala Native guide notes that
  `samply` supports Scala Native symbol demangling.
- Use Linux `perf` plus FlameGraph or `hotspot` when running on Linux. `hotspot`
  provides a flamegraph view, but the Scala Native guide notes that it does not
  demangle Scala Native symbols.
- Keep symbols/debug metadata available for attribution; separately rerun
  optimized non-profiled binaries for headline timing.

## First Profile Targets

| Target | Modes | Question |
|---|---|---|
| Common Crawl-shaped q1/q2 page-token | `gc-heap`, `rift-checked-page-token`, `rift-checked-safezone-page-token` | Confirm remaining time is parser/token traversal/object construction rather than allocator close. |
| Dataflow AGGREGATE | exact-array checked aggregate vs true `EpochFold` | Explain why reusable `EpochFold` is much slower than exact-array aggregate. |
| StreamFlex | trusted Rift HP/Streaming vs checked `TransactionRegion` and checked scoped transaction | Separate transaction-list CPU from region backend cost. |
| Common Crawl q3 parser scratch | heap, trusted Rift, checked page-token if applicable | Confirm negative row is parser/scratch CPU-bound. |
| ReML Tier 1 ports | `gc-heap`, checked modes on `msort`, `fft`, `ratio` | Separate allocation/object construction from benchmark compute/traversal. |
| DSPBench Fraud q2 | `rift-checked-safezone-page-token` versus heap/trusted rows | Explain why checked scoped page-token cuts GC/RSS but loses elapsed on the strongest DSPBench real-input row. |

## Results

| Date | Benchmark | Mode | Tool | Input/scale | Main hot symbols | Interpretation |
|---|---|---|---|---|---|---|
| 2026-05-06 | GH Archive q1-fields | `rift-checked-safezone-page-token` | macOS `/usr/bin/sample`, 10s sampled diagnostic | 2 hourly gzip JSON-line files, 200k real events, file-backed | `java.io.BufferedReader.readLine`, UTF-8 decoder loop, `AbstractStringBuilder.append0`, `String.charAt`, `BufferedReader.prepareRead`, `StringBuilder.append`, `GithubArchiveRegionMatrixHelpers.countJsonFields`, stable hashing, zlib inflate; allocator/GC present but lower | Remaining file-backed cost is parser/string/decompression dominated. Page-token already moves event/field records, but the current reader still creates heap strings/builders. Next optimization should be NDJSON byte/char-slice parser scratch before more region allocator tuning. |
| 2026-05-07 | GH Archive q1/q2 byte-slice follow-up | `heap-immix`, `rift-trusted-streaming`, `rift-checked-safezone-page-token` | non-profiled benchmark rerun | 2 hourly gzip JSON-line files, 200k real events, file-backed `GITHUB_ARCHIVE_FILE_PARSER=byte-slice` | n/a, implementation follow-up | Byte-slice parsing removes the measured parser-string cliff: q1 heap `3806.120 ms` vs checked scoped page-token `3629.193 ms`; q2 heap `3756.950 ms` vs checked scoped page-token `3626.107 ms`. Region rows report zero timed GC and about `211 MB` RSS versus heap about `290 MB`. |
| 2026-05-07 | DSPBench Fraud q2 | `heap-immix`, `safezone-improved-32k`, `rift-trusted-streaming`, checked page-token backends | instrumented `DSPBENCH_DIAG=1`, non-headline one-run diagnostic | 1M replayed real `credit-card.dat` transaction events, `594182` alert outputs | mode-specific append/allocation before the fast path: heap `189.524 ms`, SafeZone `134.630 ms`, trusted Streaming `135.167 ms`, checked Rift page-token `152.283 ms`, checked SafeZone page-token `150.169 ms`; checked close/cursor and bucket switch costs are about `6-7 ms` higher than unowned paths | Allocation+append is memory-management/operator overhead, but region rows are not slower there in this diagnostic. The first clean checked rows lost elapsed because of common checked operator overhead plus remaining parser/replay/predictor/checksum/traversal CPU. Diagnostic elapsed is not headline timing; use `DSPBENCH_REGION_MATRIX.md` for medians. |
| 2026-05-07 | DSPBench Fraud q2 after page-token fast path | `heap-immix`, `rift-trusted-streaming`, `rift-checked-page-token`, `rift-checked-safezone-page-token` | instrumented `DSPBENCH_DIAG=1`, non-headline one-run diagnostic plus 3-run medians | 1M replayed real `credit-card.dat` transaction events, `594182` alert outputs | dirty fast-path median: checked SafeZone page-token `818.574 ms` vs heap `862.834 ms`; committed-code median: trusted Streaming `788.040 ms`, checked SafeZone page-token `810.770 ms`, heap `820.945 ms`; diagnostic close/traverse remains checked `62.026-62.859 ms` vs heap `52.269 ms` and trusted Streaming `54.779 ms`; bucket switch/open remains checked `55.959-56.211 ms` vs heap `46.463 ms` and trusted Streaming `49.058 ms` | The fast path improves q2 enough that checked scoped is a modest clean win over heap, but trusted Streaming is fastest. The next remaining overhead is common checked page-token/query CPU, not allocation+append alone. |
| 2026-05-07 | Common Crawl-shaped q1/q2 page-token | `rift-checked-page-token`, `rift-checked-safezone-page-token` | instrumented `COMMON_CRAWL_WET_DIAG=1`, non-headline one-run diagnostic | 1M generated WET-shaped pages, `137000000` appended/closed records | q1 checked Rift: append `3444.176 ms`, close cursor `757.595 ms`, estimated bucket open `2.672 ms`; q1 checked scoped: append `3177.917 ms`, close cursor `760.700 ms`, estimated bucket open `9.829 ms`; q2 checked Rift: append `3515.311 ms`, close cursor `810.644 ms`, q2 aggregate `18.309 ms`; q2 checked scoped: append `3215.592 ms`, close cursor `802.633 ms`, q2 aggregate `18.347 ms` | The apparent `bucket_switch_ms` is mostly expired-bucket close work because `pageTokenAppendRegionFor` closes old buckets synchronously. After subtracting expired close, true bucket open/switch is only about `3-10 ms` at 1M. The remaining cost is dominated by allocation+append and required per-record close traversal; SafeZone-backed checked mainly wins by cheaper append/allocation, not by changing close traversal. |
| 2026-05-07 | DSPBench Fraud q2 committed-code diagnostic rerun | `heap-immix`, `rift-trusted-streaming`, `rift-checked-page-token`, `rift-checked-safezone-page-token` | instrumented `DSPBENCH_DIAG=1`, non-headline one-run diagnostic | 1M replayed real `credit-card.dat` transaction events, `4851373` appended/closed records | timed heap diagnostic: append `186.048 ms`, predict `84.626 ms`, close cursor `53.764 ms`, estimated bucket open `0.012 ms`; trusted Streaming: append `131.493 ms`, predict `86.917 ms`, close cursor `56.087 ms`, estimated bucket open `0.188 ms`; checked Rift page-token: append `150.361 ms`, predict `89.099 ms`, close cursor `64.032 ms`, estimated bucket open `0.299 ms`; checked scoped page-token: append `144.353 ms`, predict `91.120 ms`, close cursor `63.456 ms`, estimated bucket open `0.990 ms` | Region allocation+append is faster than heap in this one-run diagnostic, so the checked elapsed gap is not caused by allocation alone. Bucket open is negligible. The visible checked tax is mostly close cursor traversal plus common query/predictor/replay/checksum CPU; optimizing the region allocator further will not fix this row by itself. |
| 2026-05-07 | Page-token live-length bookkeeping follow-up | `rift-checked-page-token`, `rift-checked-safezone-page-token`, count-by-key variants | non-profiled focused/application rerun after source change | 1M focused page-token rows and 1M replayed real DSPBench Fraud q2 | focused `append-count-by-key`: heap `114.143 ms`, checked Rift `104.813 ms`, checked scoped `102.504 ms`; focused `append-only/drain/aggregate` scoped rows `77.135/88.840/85.362 ms` versus heap `81.535/90.374/86.988 ms`; Fraud q2 checked scoped `843.380 ms` versus heap `842.739 ms` and trusted Streaming `832.012 ms` | Skipping the generic append-window live-length counter is justified for operator-owned page-token APIs and keeps focused rows positive, especially count-by-key. It is not a large application speedup. A source-level `inline` helper was rejected by capture checking, so the next plausible checked-runtime optimization is generated allocation lowering that bypasses `allocImpl`/`checkOpen` where static operator ownership proves the region is open. |
| 2026-05-07 | Page-token owned cursor link-clearing follow-up | `rift-checked-page-token`, `rift-checked-safezone-page-token` | non-profiled focused/application rerun after source change | 1M focused page-token rows, 1M generated Common Crawl-shaped q1/q2, and 1M replayed real DSPBench Fraud q2 | focused checked scoped `append-only/drain/aggregate`: `73.590/83.997/81.296 ms`; Common Crawl q1/q2 checked scoped `3643.680/3790.138 ms` vs heap `5392.344/5201.862 ms`; Fraud q2 checked scoped `800.369 ms` vs heap `807.974 ms`, RSS `278577152` vs `358301696` | `nextOwnedOrNull()` removes per-record link clearing only for operator-owned page-token close. This is a small but real static-safety overhead removal: the parent refs are cleared and the child region dies, so clearing every link is unnecessary. It improves focused rows by about `3.5-4.8 ms` versus the previous no-length checkpoint and turns Fraud q2 into a modest checked elapsed/RSS win, while leaving trusted Streaming as the lower-bound winner. |
| 2026-05-07 | Common Crawl-shaped q2 checked page-token target profile | `rift-checked-safezone-page-token` | macOS `/usr/bin/sample`, 5s sampled diagnostic after delaying past the heap expected-control phase | 2M generated WET-shaped pages, q2 domain window; timed row `7719.982 ms`, `69.545 ms` GC, `1858678` outputs | top sampled paths: `closeRecords$5`/`StreamAppendCursor.nextOrNull`, `appendWindowOwnedOpen`/`appendPageToken`, `scalanative_zone_alloc` plus `_platform_memset`, `InputData.tokenHashAt`/`tokenHash`/`mix`, `MemorySafeZoneBackedRiftRegion.allocImpl` and `checkOpen`; physical footprint about `440 MB` | This confirms the checked scoped page-token path is split between required close traversal, append/linking, token-hash query work, and SafeZone allocation/zeroing. Bucket opening is not visible as a dominant path. The next low-level SafeZone-backed checks to investigate are allocation zeroing, `checkOpen`, and whether per-append `appendWindowOwnedOpen` can be further specialized, but traversal/query work is a large shared floor. |
| 2026-05-07 | Common Crawl-shaped q2 checked page-token target profile | `rift-checked-page-token` | macOS `/usr/bin/sample`, 5s sampled diagnostic after delaying past the heap expected-control phase | 2M generated WET-shaped pages, q2 domain window; timed row `8190.974 ms`, `38.480 ms` GC, `26.032 ms` Rift op, `13.804 ms` slow alloc, `274000000` region objects, `1858678` outputs | top sampled paths: `closeRecords$5`/`StreamAppendCursor.nextOrNull`, `appendWindowOwnedOpen`/`appendPageToken`, `scalanative_rift_region_alloc` and `scalanative_rift_region_alloc_raw`, `_platform_memset`, `scalanative_rift_normalize_align`, `scalanative_rift_stats_record_alloc_bytes`, `MemoryRiftRegion.allocImpl` and `checkOpen`, `InputData.tokenHashAt`/`tokenHash`/`mix`; physical footprint about `440 MB` | Compared with SafeZone-backed checked, the Rift backend shows extra sampled allocator normalization/stat-check work while the same close traversal and token-hash/query paths remain. This supports focusing on generated allocation lowering/stat-check elimination and `checkOpen` removal inside operator-owned paths before inventing another close/open optimization. |
| 2026-05-07 | Common Crawl-shaped q2 checked scoped after open allocation | `rift-checked-safezone-page-token` | macOS `/usr/bin/sample`, 5s sampled diagnostic after delaying past the heap expected-control phase | 3M generated WET-shaped pages, q2 domain window; timed row `12093.317 ms`, `93.269 ms` GC, `2788398` outputs | top sampled paths: `closeRecords$5`, `appendPageTokenOwnedOpen`/`appendPageToken`, `scalanative_zone_alloc` plus `_platform_memset`/`Util_pad`, `InputData.tokenHashAt`/`tokenHash`/`mix`, `StreamAppendCursor.nextOwnedOrNull`, and `MemorySafeZoneBackedRiftRegion.allocUncheckedImpl`; physical footprint about `440 MB` | This is the post-`allocOpen` target profile. `allocImpl/checkOpen` is no longer visible; the remaining SafeZone-backed checked costs are zone allocation/zeroing/alignment, append/linking, cursor traversal, and token-hash/query CPU. The next low-level optimization is not another `checkOpen` removal; it would need to reduce allocation zeroing/alignment or append/cursor traversal, both of which must preserve the same logical heap/Rift traversal shape. |
| 2026-05-07 | DSPBench Fraud q2 checked scoped after open allocation | `rift-checked-safezone-page-token` | macOS `/usr/bin/sample`, 3s sampled diagnostic after delaying past the heap expected-control phase | 5M replayed real `credit-card.dat` events, q2 alert window; timed row `4245.059 ms`, `72.687 ms` GC, `3308061` outputs | top sampled paths: `BenchmarkInputSupport.stableHash`, `ByteLineReader.append`/`nextByte`/`readLine`, `FraudPredictorState.update`, CSV comma/state parsing, `appendChecked`, `closeRecords$1`, `scalanative_zone_alloc`/`memset`, `appendPageTokenOwnedOpen`, and small residual GC allocation/mark/sweep paths; physical footprint about `263 MB` | The real-input Fraud q2 path is now dominated by file replay/parsing/hash and predictor/query work before allocator overhead. Region append/close still appears, but it is not the leading sampled cost. For this row, the best next engineering move is not another region allocation micro-optimization; either reduce parser/replay overhead with fair heap/region byte-slice controls or search the next real-input stream benchmark. |
| 2026-05-12 | StreamFlex design throughput | `checked-epoch-scoped` | macOS `/usr/bin/sample`, 5s sampled diagnostic | 20M generated events, `objects_per_event=8`, final-clean binary, SafeZone-backed checked epoch | top sampled paths: `processCheckedPeriod` (`1001` top-function samples), `StableState.classify` (`381`), `StableState.recordEvent` (`252`), `_platform_memset` (`247`), `MemorySafeZoneBackedStreamingRiftRegion.allocUncheckedImpl` (`218`), `MemorySafeZoneBackedRiftRegion.allocUncheckedImpl` (`201`), `mix`, `StableState.key`, `recordAlert`, `AlertCapsule.add`/`drainInto`; physical footprint about `5.7 MB` during sampled window | The checked StreamFlex-design row is split between shared query/pipeline work and region allocation/zeroing. `allocImpl/checkOpen` is not the dominant sampled path; the visible allocation cost is SafeZone/zone allocation plus zeroing. The next plausible optimizations are reducing transient object count/layout cost, using chunked/array-like transient buffers with same-shape heap controls, or making allocation/zeroing more intrinsic. |
| 2026-05-12 | StreamFlex design throughput | `gc-heap` | macOS `/usr/bin/sample`, 5s sampled diagnostic | 20M generated events, `objects_per_event=8`, final-clean binary | top sampled paths: `processHeapPeriod` (`769` top-function samples), `StableState.classify` (`285`), `StableState.recordEvent` (`233`), `scalanative_GC_alloc_small` (`221`), `_platform_memset` (`217`), `recordAlert`, `AlertCapsule.add`/`drainInto`, `mix`, `StableState.key`; physical footprint about `9.8 MB` during sampled window | Heap and checked spend substantial time in the same query/pipeline work. Heap adds Immix allocation/object-metadata cost; checked replaces that with SafeZone/zone allocation and zeroing. This supports the gap-analysis conclusion: current StreamFlex-design throughput is already close to the heap-GC-removal bound, and remaining speedups need allocation/layout/traversal work or stronger latency/heap-cap pressure rather than another close-time optimization. |

Profile artifact:

`/Users/siyaoliu/rift/cache/profile-gharchive-q1-checked-2026-05-06/sample.txt`

Additional profile artifacts:

- `/Users/siyaoliu/rift/cache/profile-common-crawl-q2-page-token-target-2026-05-07/sample.txt`
- `/Users/siyaoliu/rift/cache/profile-common-crawl-q2-rift-page-token-target-2026-05-07/sample.txt`
- `/Users/siyaoliu/rift/cache/profile-common-crawl-q2-openalloc-scoped-target-2026-05-07/sample.txt`
- `/Users/siyaoliu/rift/cache/profile-dspbench-fraud-q2-openalloc-scoped-real-target-2026-05-07/sample.txt`
- `/Users/siyaoliu/rift/cache/profile-streamflex-design-2026-05-12/checked-epoch-scoped.sample.txt`
- `/Users/siyaoliu/rift/cache/profile-streamflex-design-2026-05-12/gc-heap.sample.txt`

Note: earlier Common Crawl and DSPBench profile attempts sampled the harness's
built-in heap expected-control run or generated input by mistake. The target
profiles above delayed attachment until the actual checked mode was running and
record the input provenance explicitly.

Profiled benchmark row:

| Query | Mode | Median ms | GC ms | Max GC ms | Output count |
|---|---|---:|---:|---:|---:|
| q1-fields | `rift-checked-safezone-page-token` | `7393.602` | `192.570` | `193.221` | `2600000` |

Important caveat: `/usr/bin/sample` was diagnostic only. Use the non-profiled
3-run medians in `evidence/GITHUB_ARCHIVE_REGION_MATRIX.md` for headline
timing.

Future rows should include:
