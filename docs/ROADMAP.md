# Rift Roadmap

Status: revised from the active fork state, benchmark notes, handoff, and the
literature-review comparison contract.

Active worktree: `/Users/siyaoliu/rift/scala-native-rift`

Branch: `feature/rift`

Current merge state is tracked in `docs/HANDOFF.md`; the substantive roadmap
revision began at implementation commit `ddbba577aecd4c0adc741cbf7085ee93548c46b4`.

## 1. Roadmap Principles

The roadmap separates four questions:

- Can the runtime path itself beat current SafeZone, improved SafeZone, and
  heap on same-layout workloads?
- Which effects come from runtime, topology, and layout?
- Can real stream/dataflow workloads move dominant data operations into regions?
- Can the safe API be justified by static capture checking and a mechanized
  containment proof?

The roadmap also keeps prior-work comparison anchors visible. Rift is not done
when it beats old SafeZone on one benchmark. It must eventually explain its
position relative to Broom, StreamFlex, Yak, Stancu-style static hybrid
analysis, Tofte-Talpin/MLKit, Hallenberg-Elsman typed regions, and
Reggio/Verona capabilities.

## 2. Status Summary

| Phase | Status | Evidence | Main remaining work |
|---|---|---|---|
| Phase 0: baseline and comparison contract | Mostly complete, not sealed | `sandbox/PHASE0_BASELINES.md`; literature review now read as design constraint. | Commit/provenance boundary, Commix gaps, pipeline remains surrogate. |
| Phase 1: standalone allocator bootstrap | Done as provenance | `/Users/siyaoliu/rift/rift-bootstrap/bench/microbench/results.md`. | Do not continue active design there unless validating bootstrap artifacts. |
| Phase 2: in-tree runtime/compiler path | Partially done | `RiftRuntime.c/h`, `RiftRegion`, plugin lowering, `RiftRegionTest`. | Header/API cleanup, broader tests, commit boundary, stats ABI decision. |
| Phase 3: runtime-only evaluation | Done enough for current claim | GCBench and ListOfLists medians show Rift wins over heap and improved SafeZone. | Add Commix where relevant; avoid overclaiming pipeline. |
| Phase 4: topology/layout decomposition | Done enough to move on | `PHASE4_LAYOUT.md`, `PHASE4_TOPOLOGY.md`, `PHASE4_EXIT.md`. | Carry safety finding into Phase 6; chunked layout still not clear Rift win vs improved SafeZone. |
| Phase 5: application evidence | In progress, not complete | DEBS Q1/Q2 scaffold runs and outputs match on bounded real-data samples; RunBoth uses a shared byte parser and region-backed input buffer; Rift modes now region-allocate Q1/Q2 window entries, Q2 median scratch, ranking objects, reusable top-k result arrays, Q2 bounded cell tables, Q1 primitive route-table arrays, Q1 ranking-index arrays, Q2 latest-empty taxi arrays, Q2 ranking-index arrays, Q2 taxi-id table entries/bytes, RunBoth output snapshots, Q2 incremental median heap arrays, and RunBoth latency buffers. The current 1M byte-output 3-run medians are heap `4640.593 ms`, HPZone `4524.706 ms`, and Streaming `4522.308 ms`; GC collection medians are heap `21.025 ms`, HPZone `0.685 ms`, and Streaming `0.635 ms`; heap RSS is `159907840` bytes vs `116785152` bytes for HPZone/Streaming. A 1M allocation-attribution run shows heap at `6,025,143` GC allocation calls, `235,159,552` rounded bytes, and `171.868 ms` allocation-call time, versus about `0.56M` calls, `10.5 MB`, and `12.8-12.9 ms` in Rift modes. | SafeZone/Commix modes, full-month scale, safe API boundaries, and remaining Q2 rank/output/control work if needed. |
| Phase 6: literature-aligned methodology evidence | Started | `DATAFLOW_REGION_MATRIX.md`, `STREAMFLEX_REGION_MATRIX.md`, `YAK_REGION_MATRIX.md`, and `STANCU_REGION_MATRIX.md` now cover Broom-style dataflow, StreamFlex-style latency/throughput, Yak-style control/data epochs including grouped sort, top-word/filter, and GraphChi-like subinterval updates plus runtime and memory-API-level promotion/escape proxies, and Stancu-style transaction accounting. | Keep these labeled as methodology reproductions, not exact paper artifacts. The Yak top-word/filter result is a strong local Rift-vs-heap and modest Rift-vs-improved-SafeZone result; GraphChi-like subintervals show Rift-vs-heap but not Rift-vs-improved-SafeZone; grouped sort is a modest same-program allocation-placement win; runtime promotion is negative on elapsed time and motivates static checked boundaries. Build fair Rift-backed collection/operator API before claiming a Broom/parallel-collections API comparison. |
| Phase 7: capture-checked safe API | Started | `RiftRegion.scoped`/`streaming` APIs exist; compiler probes now pass for scoped object graphs, for-loop allocation, nested scoped regions, local higher-order consumers, non-escaping closures, return escape rejection, heap retention rejection, nested-region leak rejection, streaming reset escape rejection, conservative returned-function rejection, explicit `HeapRoot` region-to-GC metadata handles, direct unrooted heap-object constructor-argument rejection, region-local alias acceptance, heap-alias rejection, heap-field-selection rejection, explicitly region-captured constructor-field reuse, plain `T^` field-reuse rejection, region-owned array checks, the explicit-owner `ObjectBuffer` checked container, reset epoch arrays, top-word-style rooted metadata buffers, GraphChi-style rooted heap metadata, rejection of reset-epoch values stored into an outer streaming buffer, and mutable local linked-list heads with provenance-preserving assignments. `docs/REPORT_CAPTURE_CHECK.md` records the slice. | More pinned diagnostics, static-heap policy, richer containers, and a better ergonomics story for field/container provenance beyond local linked-list heads. |
| Phase 8: native GC/region integration hardening | Started | Safety bug found for unrooted region-to-GC references; v1 explicit `HeapRoot` handles now retain heap metadata through a GC-visible list on the live region object, and checked lowering rejects direct unrooted heap-object constructor arguments, unsafe region-array stores, unsafe `ObjectBuffer` heap stores, and mutable-head retagging from heap values while allowing region-to-region object graphs, simple region-local aliases, stable constructor fields explicitly captured by `{region}`, region arrays with explicitly captured element types, explicit-owner object buffers, and provenance-preserving mutable linked-list heads. | Extend or deliberately limit the mixed-reference rule for static immutable heap referents and richer containers; decide whether plain `T^` field reuse and method-style container operations need a compiler extension or explicit owner-token APIs. |
| Phase 9: Lean mechanization | Open | Design target only; older proof pack is not active in fork. | Core calculus and proofs without `sorry`. |
| Phase 10: writing | Not started beyond notes | Handoff and result packs exist. | Paper/thesis narrative after evidence stabilizes. |

Phase 0 is not "final." It is complete enough for GCBench and ListOfLists, but
not for a final pipeline or application story.

## 3. Phase 0: Baseline And Comparison Contract

Goal: establish trustworthy local baselines and explicit prior-work comparison
targets before making claims.

Completed:

- GCBench 5-run matrix: Immix, current SafeZone, improved SafeZone, Rift HPZone.
- ListOfLists 5-run matrix: Immix, current SafeZone, improved SafeZone, Rift
  HPZone.
- GCBench topology rerun.
- Cleaned raw-array pipeline surrogate.
- Literature-review comparison contract covering Broom, StreamFlex, Yak,
  Stancu et al., Tofte-Talpin/MLKit, Hallenberg-Elsman-Tofte,
  Reggio/Verona, and Pony/Orca.

Key local baseline medians:

| Benchmark | Immix | Current SafeZone | Improved SafeZone | Rift HPZone |
|---|---:|---:|---:|---:|
| GCBench | 203.514 ms | 684.517 ms | 223.770 ms | 161.641 ms |
| ListOfLists linked | 15085.511 ms | 138171.998 ms | 10132.854 ms | 6951.331 ms |

Exit criteria:

- Baseline commands are checked in.
- Results state run counts and environment variables.
- Surrogates are labeled as surrogates.
- The comparison section in `DESIGN.md` stays visible in future docs.

Remaining:

- Add Commix where it is a meaningful comparison.
- Stabilize current uncommitted work into a commit or patch boundary.
- Do not treat the pipeline surrogate as a tracked-source reproduction.

## 4. Phase 1: Standalone Allocator Bootstrap

Goal: prove the slab allocator core before in-tree integration.

Status: done as historical provenance, not active architecture.

Evidence:

- Old bootstrap tree: `/Users/siyaoliu/rift/rift-bootstrap`.
- Recorded microbench results show Rift HPZone allocation around `2.1 ns`
  p50 and close/free around `3000 ns` p50 for 100000 allocations.

Do not redo:

- Do not restart implementation from the standalone scaffold.
- Use it only for provenance or focused allocator sanity checks.

## 5. Phase 2: In-Tree Runtime And Compiler Path

Goal: make Rift a real Scala Native runtime/compiler path.

Completed or partially completed:

- `nativelib/src/main/resources/scala-native/rift/RiftRuntime.c`
- `nativelib/src/main/resources/scala-native/rift/RiftRuntime.h`
- `nativelib/src/main/scala/scala/scalanative/memory/RiftRegion.scala`
- `nativelib/src/main/scala/scala/scalanative/runtime/RiftAllocator.scala`
- Scala 2/3 companion surface.
- Compiler primitive and lowering for `region.alloc(new T(...))`.
- `RiftRegionTest` recorded as passing `5/5`.
- SafeZone baseline correction in `MemoryPool.c`, `Zone.c`, and
  `GCRoots.c`.

Exit criteria:

- Full API/header consistency, including stats functions or an explicit choice
  to keep them private.
- Dedicated compiler-plugin regression tests.
- Broader Scala Native test subset beyond `RiftRegionTest`.
- No untracked implementation files for the core runtime/API.

Risks:

- `RiftRuntime.h` does not currently declare all stats functions used by Scala
  externs.

## 6. Phase 3: Runtime-Only Evaluation

Goal: establish whether the runtime claim stands before relying on layout or
library redesign.

Completed enough:

- GCBench: Rift HPZone `161.641 ms` vs heap `203.514 ms` and improved SafeZone
  `223.770 ms`.
- ListOfLists linked: Rift HPZone `6951.331 ms` vs heap `15085.511 ms` and
  improved SafeZone `10132.854 ms`.

Interpretation:

- Same-layout runtime wins exist.
- Old SafeZone pathologies reproduce in the current fork for linked one-region
  shapes.
- Improved SafeZone is much stronger and must remain a baseline.
- The cleaned pipeline does not currently show Rift separation.

Remaining:

- Add Commix where supported.
- Keep the runtime claim scoped to workloads where measurements support it.
- Do not use layout-specialized results to prove same-layout runtime speed.

## 7. Phase 4: Topology And Layout Decomposition

Goal: separate allocator wins from topology wins and data-layout wins.

Completed enough:

- Linked, chunked, and flat ListOfLists layout study.
- One-region, nested, and mixed rooted topology study.
- Exit summary tying runtime, layout, topology, and safety findings together.

Key results:

| Mode | Linked ms | Chunked ms | Flat ms |
|---|---:|---:|---:|
| Immix heap | 15260.875 | 2636.480 | 1766.295 |
| current SafeZone | 136016.922 | 4835.904 | 1735.453 |
| improved SafeZone | 9824.936 | 2369.108 | 1743.161 |
| Rift HPZone | 7278.150 | 2463.674 | 1515.091 |

Key findings:

- Layout is first-order for every runtime.
- Rift still has a runtime win on linked allocation-heavy structures.
- The flat Rift cliff was a runtime bug and was fixed.
- The first chunked layout does not clearly beat improved SafeZone.
- Mixed rooted heap-values is not a Rift win.
- Unrooted region-to-GC references are unsafe because the GC does not scan Rift
  regions.

Exit criteria:

- Phase 4 is complete enough to move to Phase 5.
- The safety finding must be tested and designed around in Phase 7/8.

## 8. Phase 5: Application Evidence And DEBS 2015

Goal: produce real application-level evidence that region memory reduces the
dominant allocation and GC costs in a streaming workload.

Current status:

- `bench/debs2015` scaffold exists.
- Q1 and Q2 run simultaneously on sorted bounded real NYC taxi samples.
- Heap, Rift HPZone, and Rift Streaming outputs match after stripping only the
  measured latency column.
- Instrumented runs report GC collection counters, RSS, and Rift counters.
  With `SCALANATIVE_GC_ALLOC_STATS=1`, they also report heap allocation-call
  counts, rounded heap bytes, and measured heap allocation-call time.
- The RunBoth hot path now uses a shared byte parser. Heap mode uses a heap
  input byte buffer; Rift modes allocate the same run-lifetime input buffer in
  a region. The parser avoids `String.split`, per-row `Option`, per-row `Trip`,
  per-row line strings, and per-row taxi/timestamp substrings in the RunBoth
  path.
- Q1 now uses a shared bucketed-window implementation for heap and Rift. Heap
  allocates the same bucket-entry class with `new`; Rift allocates it with
  `region.alloc` and closes the per-timestamp region at bucket eviction.
- Q2 now uses the same shared-backend shape for profit-window and empty-taxi
  window entries. Heap allocates the same entry classes with `new`; Rift
  allocates them with `region.alloc` and closes each per-timestamp region at
  window eviction.

Current limitation:

- Current Rift DEBS region-allocates Q1 and Q2 window entries using the same
  bucketed algorithms as heap.
- Q1 replaced boxed route-count and route-rank `HashMap`s with a shared
  primitive open-addressed route table. Heap allocates the backing arrays with
  `new`; Rift modes allocate them in the run-lifetime ranking/control region.
- Q1 replaced the heap `TreeSet` ranking index with a shared indexed binary
  heap over ordinary `RankedRoute` Scala objects. Heap allocates the index
  arrays with `new`; Rift modes allocate those arrays, plus `RankedRoute`,
  `Route`, and `Cell` objects, in the run-lifetime ranking/control region.
- Q2 replaced boxed per-cell `HashMap` tables for active profits, empty counts,
  latest sequence, and current ranked area with fixed arrays over the bounded
  grid key space. Heap allocates those arrays and `ProfitStats` with `new`;
  Rift modes allocate them in the run-lifetime ranking/control region.
- Q2 replaced `latestEmptyByTaxi` with a growable dense array indexed by the
  existing `TaxiIds` integer key. Heap allocates the array with `new`; Rift
  modes allocate it in the run-lifetime ranking/control region.
- Q2 replaced the heap `TreeSet` ranking index with a shared indexed binary
  heap over `ProfitableArea` objects. Heap allocates the index arrays with
  `new`; Rift modes allocate them in the run-lifetime ranking/control region.
- Q2 replaced durable taxi-id `String` interning and a heap `HashMap` with a
  shared byte-backed taxi-id table. Heap allocates the table, entries, and
  taxi-id byte arrays with `new`; Rift modes allocate them in the run-lifetime
  ranking/control region. This avoids unscanned region-to-GC `String`
  references in Rift entries.
- RunBoth latency collectors now use shared primitive buffers. Heap uses heap
  arrays; Rift modes allocate backing arrays in the snapshot region and copy
  final metrics arrays out before region close.
- Returned top-k arrays are cached by exact size and reused. In Rift modes the
  cached arrays are region-allocated; RunBoth previous-output snapshots also
  have a heap/Rift allocation-placement split, with Rift snapshots allocated in
  a run-lifetime snapshot region.
- Output formatting now writes directly to `Writer` through shared code and
  avoids hot per-row `StringBuilder.toString` and Q2 `f""` formatting.
- Q2 median scratch arrays are region-backed in Rift modes and reused with
  capacity growth. Q2 ranking uses packed primitive cell keys internally.
- Q2 top-10 extraction now uses a shared conservative cache. Heap and Rift use
  the same invalidation logic; Rift's difference remains allocation placement
  for the region-managed ranking/control state.
- Therefore current DEBS has bounded-sample Rift wins and lower RSS, plus
  allocation-attribution evidence that heap allocation work drops when
  structured-lifetime objects move into regions. It does not yet establish the
  final application claim because the controls below remain open.

Current provisional evidence:

| Run | Heap | Rift HPZone | Rift Streaming |
|---|---:|---:|---:|
| 1M RunBoth elapsed | 21658.215 ms | 22314.989 ms | 22184.467 ms |
| 1M instrumented elapsed | 22827.882 ms | 22366.285 ms | 22810.687 ms |
| 1M instrumented GC time | 1051.752 ms | 1003.171 ms | 1012.489 ms |
| 100k after Q2 windows, elapsed | 1837.501 ms | 1794.929 ms | 1843.627 ms |
| 100k after Q2 windows, region objects | 0 | 294284 | 294284 |
| 100k after Q2 profit values, elapsed | 1816.773 ms | 1791.195 ms | 1802.942 ms |
| 100k after Q2 median scratch, elapsed | 1881.304 ms | 1920.875 ms | 1937.911 ms |
| 100k after Q2 median scratch, region resets | 0 | 171197 | 171197 |
| 100k after per-trip scratch reset, elapsed | 1748.744 ms | 1775.350 ms | 1768.716 ms |
| 100k after per-trip scratch reset, region resets | 0 | 87438 | 87438 |
| 100k after primitive Q2 ranking keys, elapsed | 1813.074 ms | 1863.806 ms | 1832.249 ms |
| 100k phase share after primitive Q2 ranking keys, Q2 process | 48.6% | 48.8% | 48.9% |
| 100k after region-backed input buffer, elapsed | 1557.171 ms | 1703.600 ms | 1591.372 ms |
| 100k after region-backed input buffer, read+parse share | 9.6% | 8.8% | 9.4% |
| 1M after region-backed input buffer, elapsed | 18692.484 ms | 17789.410 ms | 17280.431 ms |
| 1M after region-backed input buffer, GC time | 731.171 ms | 644.394 ms | 643.015 ms |
| 1M median after region-backed input buffer, elapsed | 17047.611 ms | 17119.396 ms | 17210.458 ms |
| 1M median after region-backed input buffer, GC time | 684.338 ms | 640.062 ms | 628.808 ms |
| 1M single after region ranking/result snapshots, elapsed | 16363.012 ms | 17243.387 ms | 17301.238 ms |
| 1M single after region ranking/result snapshots, GC time | 601.615 ms | 503.198 ms | 529.115 ms |
| 1M single after region ranking/result snapshots, Rift op time | 0.000 ms | 933.640 ms | 936.641 ms |
| 1M single after region ranking/result snapshots, peak RSS | 1148436480 | 1088684032 | 1088618496 |
| 100k 3-run median after reusable ranking arrays, elapsed | 1286.990 ms | 1262.091 ms | 1265.775 ms |
| 100k 3-run median after reusable ranking arrays, GC time | 61.087 ms | 35.098 ms | 35.855 ms |
| 100k 3-run median after reusable ranking arrays, Rift op time | 0.000 ms | 1.430 ms | 1.420 ms |
| 1M 3-run median after reusable ranking arrays, elapsed | 14633.019 ms | 14234.470 ms | 14392.097 ms |
| 1M 3-run median after reusable ranking arrays, GC time | 513.199 ms | 457.726 ms | 478.912 ms |
| 1M 3-run median after reusable ranking arrays, Rift op time | 0.000 ms | 13.003 ms | 14.166 ms |
| 1M 3-run median after reusable ranking arrays, peak RSS | 813105152 | 876101632 | 876101632 |
| 100k 3-run median after Q2 cell tables, elapsed | 1037.748 ms | 997.997 ms | 983.928 ms |
| 100k 3-run median after Q2 cell tables, GC time | 45.193 ms | 33.453 ms | 32.947 ms |
| 100k 3-run median after Q2 cell tables, Rift op time | 0.000 ms | 1.745 ms | 1.349 ms |
| 100k 3-run median after Q2 cell tables, peak RSS | 217137152 | 172113920 | 172097536 |
| 1M 3-run median after Q2 cell tables, elapsed | 11471.085 ms | 11442.637 ms | 11477.431 ms |
| 1M 3-run median after Q2 cell tables, GC time | 478.636 ms | 419.658 ms | 428.339 ms |
| 1M 3-run median after Q2 cell tables, Rift op time | 0.000 ms | 11.759 ms | 11.421 ms |
| 1M 3-run median after Q2 cell tables, peak RSS | 609730560 | 490766336 | 490799104 |
| 100k 3-run median after Q1 primitive route table, elapsed | 1067.019 ms | 1031.787 ms | 1026.118 ms |
| 100k 3-run median after Q1 primitive route table, GC time | 46.067 ms | 31.820 ms | 32.090 ms |
| 100k 3-run median after Q1 primitive route table, Rift op time | 0.000 ms | 1.911 ms | 1.877 ms |
| 100k 3-run median after Q1 primitive route table, peak RSS | 217038848 | 174833664 | 174833664 |
| 1M 3-run median after Q1 primitive route table, elapsed | 11957.721 ms | 11659.223 ms | 11739.195 ms |
| 1M 3-run median after Q1 primitive route table, GC time | 463.555 ms | 397.162 ms | 398.268 ms |
| 1M 3-run median after Q1 primitive route table, Rift op time | 0.000 ms | 15.102 ms | 15.164 ms |
| 1M 3-run median after Q1 primitive route table, peak RSS | 433209344 | 381222912 | 381190144 |
| 100k 3-run median after Q2 latest-empty taxi table, elapsed | 1072.361 ms | 1005.303 ms | 996.131 ms |
| 100k 3-run median after Q2 latest-empty taxi table, GC time | 47.078 ms | 31.095 ms | 31.187 ms |
| 100k 3-run median after Q2 latest-empty taxi table, Rift op time | 0.000 ms | 2.161 ms | 2.136 ms |
| 100k 3-run median after Q2 latest-empty taxi table, peak RSS | 217071616 | 174964736 | 174964736 |
| 1M 3-run median after Q2 latest-empty taxi table, elapsed | 11649.547 ms | 11263.680 ms | 11188.144 ms |
| 1M 3-run median after Q2 latest-empty taxi table, GC time | 487.774 ms | 381.099 ms | 382.734 ms |
| 1M 3-run median after Q2 latest-empty taxi table, Rift op time | 0.000 ms | 14.536 ms | 14.991 ms |
| 1M 3-run median after Q2 latest-empty taxi table, peak RSS | 609304576 | 381501440 | 381501440 |
| 100k 3-run median after Q2 array-backed ranking, elapsed | 1005.710 ms | 965.099 ms | 947.514 ms |
| 100k 3-run median after Q2 array-backed ranking, GC time | 45.375 ms | 30.805 ms | 30.700 ms |
| 100k 3-run median after Q2 array-backed ranking, Rift op time | 0.000 ms | 1.981 ms | 1.932 ms |
| 100k 3-run median after Q2 array-backed ranking, peak RSS | 216858624 | 176029696 | 176013312 |
| 1M 3-run median after Q2 array-backed ranking, elapsed | 11202.975 ms | 10808.901 ms | 10804.756 ms |
| 1M 3-run median after Q2 array-backed ranking, GC time | 423.932 ms | 348.901 ms | 344.376 ms |
| 1M 3-run median after Q2 array-backed ranking, Rift op time | 0.000 ms | 14.861 ms | 14.684 ms |
| 1M 3-run median after Q2 array-backed ranking, peak RSS | 431718400 | 383631360 | 383631360 |
| 100k 3-run median after Q2 taxi-id table, elapsed | 793.461 ms | 787.594 ms | 785.273 ms |
| 100k 3-run median after Q2 taxi-id table, GC time | 18.122 ms | 23.902 ms | 19.621 ms |
| 100k 3-run median after Q2 taxi-id table, Rift op time | 0.000 ms | 1.443 ms | 1.421 ms |
| 100k 3-run median after Q2 taxi-id table, peak RSS | 199983104 | 69402624 | 69402624 |
| 1M 3-run median after Q2 taxi-id table, elapsed | 9876.359 ms | 9676.525 ms | 9667.365 ms |
| 1M 3-run median after Q2 taxi-id table, GC time | 376.602 ms | 358.127 ms | 270.482 ms |
| 1M 3-run median after Q2 taxi-id table, Rift op time | 0.000 ms | 13.216 ms | 13.915 ms |
| 1M 3-run median after Q2 taxi-id table, peak RSS | 431751168 | 169312256 | 169295872 |
| 100k 3-run median after Q1 indexed ranking, elapsed | 903.449 ms | 874.280 ms | 863.219 ms |
| 100k 3-run median after Q1 indexed ranking, GC time | 19.414 ms | 18.821 ms | 18.578 ms |
| 100k 3-run median after Q1 indexed ranking, Rift op time | 0.000 ms | 1.820 ms | 1.778 ms |
| 100k 3-run median after Q1 indexed ranking, peak RSS | 184090624 | 43024384 | 43024384 |
| 1M 3-run median after Q1 indexed ranking, elapsed | 9746.536 ms | 9441.064 ms | 9442.026 ms |
| 1M 3-run median after Q1 indexed ranking, GC time | 312.151 ms | 320.025 ms | 306.311 ms |
| 1M 3-run median after Q1 indexed ranking, Rift op time | 0.000 ms | 10.528 ms | 10.094 ms |
| 1M 3-run median after Q1 indexed ranking, peak RSS | 431669248 | 108445696 | 108969984 |
| 100k 3-run median after output snapshots, elapsed | 829.612 ms | 811.389 ms | 815.476 ms |
| 100k 3-run median after output snapshots, GC time | 18.383 ms | 18.242 ms | 20.286 ms |
| 100k 3-run median after output snapshots, Rift op time | 0.000 ms | 1.615 ms | 1.604 ms |
| 100k 3-run median after output snapshots, peak RSS | 184107008 | 44613632 | 44597248 |
| 1M 3-run median after output snapshots, elapsed | 8983.464 ms | 8815.087 ms | 8836.488 ms |
| 1M 3-run median after output snapshots, GC time | 290.712 ms | 292.155 ms | 296.305 ms |
| 1M 3-run median after output snapshots, Rift op time | 0.000 ms | 10.053 ms | 10.061 ms |
| 1M 3-run median after output snapshots, peak RSS | 431652864 | 119865344 | 119898112 |
| 100k 3-run median after Q2 incremental medians, elapsed | 619.735 ms | 626.609 ms | 610.258 ms |
| 100k 3-run median after Q2 incremental medians, GC time | 8.091 ms | 5.839 ms | 5.781 ms |
| 100k 3-run median after Q2 incremental medians, Rift op time | 0.000 ms | 1.518 ms | 1.573 ms |
| 100k 3-run median after Q2 incremental medians, peak RSS | 97370112 | 40173568 | 40173568 |
| 1M 3-run median after Q2 incremental medians, elapsed | 5976.447 ms | 5794.879 ms | 5948.755 ms |
| 1M 3-run median after Q2 incremental medians, GC time | 67.086 ms | 59.658 ms | 55.056 ms |
| 1M 3-run median after Q2 incremental medians, Rift op time | 0.000 ms | 10.737 ms | 11.172 ms |
| 1M 3-run median after Q2 incremental medians, peak RSS | 305758208 | 113950720 | 113934336 |
| 100k single after Q2 top-10 cache, elapsed | 628.690 ms | 550.082 ms | 553.841 ms |
| 100k single after Q2 top-10 cache, top-10 recomputes | 4189 | 4189 | 4189 |
| 100k single after Q2 top-10 cache, top-candidate comparisons | 144949 | 144949 | 144949 |
| 1M single after Q2 top-10 cache, elapsed | 5367.670 ms | 5149.720 ms | 5191.038 ms |
| 1M single after Q2 top-10 cache, GC time | 68.932 ms | 35.475 ms | 35.887 ms |
| 1M single after Q2 top-10 cache, Rift op time | 0.000 ms | 11.813 ms | 12.376 ms |
| 1M single after Q2 top-10 cache, peak RSS | 305627136 | 116604928 | 116588544 |
| 1M single after Q2 top-10 cache, top-10 recomputes | 29983 | 29983 | 29983 |
| 100k 3-run median after Q2 top-10 cache, elapsed | 607.176 ms | 571.465 ms | 590.900 ms |
| 100k 3-run median after Q2 top-10 cache, GC time | 9.254 ms | 5.348 ms | 5.093 ms |
| 100k 3-run median after Q2 top-10 cache, Rift op time | 0.000 ms | 2.677 ms | 2.620 ms |
| 100k 3-run median after Q2 top-10 cache, peak RSS | 102350848 | 41500672 | 41500672 |
| 1M 3-run median after Q2 top-10 cache, elapsed | 6192.692 ms | 5697.948 ms | 5657.424 ms |
| 1M 3-run median after Q2 top-10 cache, GC time | 70.762 ms | 36.231 ms | 36.288 ms |
| 1M 3-run median after Q2 top-10 cache, Rift op time | 0.000 ms | 18.824 ms | 21.925 ms |
| 1M 3-run median after Q2 top-10 cache, peak RSS | 304463872 | 116588544 | 96239616 |
| 1M single allocation attribution, GC alloc calls | 19924383 | 14462042 | 14462060 |
| 1M single allocation attribution, GC alloc bytes | 679841024 | 455349920 | 455350304 |
| 1M single allocation attribution, GC alloc time | 582.629 ms | 385.807 ms | 384.031 ms |

Immediate next step:

- Preserve benchmark fairness before adding more region code. Heap and Rift
  variants should be the same logical program with allocation/lifetime policy
  as the variable, not separate hand-specialized algorithms.
- The input-buffer median rerun is complete. The single-run Rift win after the
  byte-reader change did not hold as a median: Rift reduced GC time, but region
  operation time offset it.
- The first ranking/result-region experiment showed that resettable top-k
  snapshot regions are the wrong lifetime shape.
- The follow-up reusable ranking-array backend removed that reset churn and made
  Rift region-operation time small again. The current 1M 3-run median has Rift
  HPZone faster than heap, but this remains bounded-sample evidence with an RSS
  tradeoff and missing SafeZone/Commix modes.
- The Q2 cell-table step replaced boxed per-cell maps with a shared bounded
  array layout. It improves both heap and Rift, and Rift modes place those
  arrays and `ProfitStats` in a region. The 1M HPZone median is only slightly
  faster than heap, but it reduces median GC by about `59 ms` and peak RSS by
  about `119 MB` with low Rift operation time.
- The Q1 route-table step replaced boxed route maps and immutable `RouteState`
  churn with a shared primitive table. It lowers Q1 processing and GC/RSS, but
  total elapsed remains Q2-dominated and is not a clean cross-checkpoint speedup
  over the Q2-cell-table median.
- The Q2 latest-empty taxi-table step replaced a heap map with a shared dense
  array over existing taxi IDs. It improves Q2 processing and gives the
  strongest bounded-sample DEBS result so far, while keeping Rift operation time
  around `15 ms` at 1M.
- The Q2 array-backed ranking step replaced Java `TreeSet` ranking nodes with a
  shared indexed heap over ordinary `ProfitableArea` objects. Heap and Rift use
  the same ranking algorithm; Rift modes allocate the ranking index arrays in
  the run-lifetime ranking/control region. The 1M HPZone median is
  `394.074 ms` faster than heap and Rift operation time stays around `15 ms`.
- The Q2 taxi-id table step replaced heap `HashMap`/`String` taxi-id metadata
  with a shared byte-backed table. Heap and Rift use the same table; Rift modes
  allocate table arrays, entries, and taxi-id byte copies in the run-lifetime
  ranking/control region. The 1M medians are now heap `9876.359 ms`, HPZone
  `9676.525 ms`, and Streaming `9667.365 ms`, with Streaming GC at
  `270.482 ms` vs heap `376.602 ms` and peak RSS around `169 MB` for Rift.
  Because the byte-backed representation also improves heap, cross-checkpoint
  elapsed improvements are not pure Rift effects.
- The Q1 indexed-ranking step replaced the remaining Q1 heap `TreeSet` ranking
  nodes with a shared indexed heap over ordinary `RankedRoute` objects. Heap
  and Rift use the same ranking algorithm; Rift modes allocate ranking arrays
  and the ranking object graph in the run-lifetime ranking/control region. The
  1M medians are heap `9746.536 ms`, HPZone `9441.064 ms`, and Streaming
  `9442.026 ms`; peak RSS drops from `431669248` bytes to about `108-109 MB`
  in Rift modes. GC time is mixed: Streaming is slightly below heap, HPZone is
  slightly above heap.
- The output-snapshot placement step moved Q1/Q2 previous-output snapshots into
  a run-lifetime region in Rift modes while keeping the changed-output logic
  shared. It is valid placement evidence but not a clean GC-time win: 1M
  medians are heap `8983.464 ms`, HPZone `8815.087 ms`, and Streaming
  `8836.488 ms`, with GC roughly flat/slightly higher in Rift and RSS around
  `120 MB`.
- The Q2 incremental-median step replaced dirty-cell copy/sort recomputation
  with shared per-cell two-heap median maintenance. Heap and Rift use the same
  Q2 algorithm; Rift modes allocate the `ProfitStats` and median heap arrays in
  the run-lifetime ranking/control region. The 1M medians are heap
  `5976.447 ms`, HPZone `5794.879 ms`, and Streaming `5948.755 ms`; HPZone is
  `181.568 ms` faster than heap, Streaming is `27.692 ms` faster, GC drops to
  `59.658 ms`/`55.056 ms`, and RSS is about `114 MB` for Rift.
- The Q2 rank/output attribution step adds change-check timers, snapshot
  timers, rank comparison/swap counters, top-candidate comparison counters,
  and changed-output comparison counters. On the 100k validation run, snapshots
  are about `0.7 ms`, Q2 changed checks are about `18-19 ms`, and
  top-candidate extraction accounts for about `4.45M` of `5.08M` Q2 rank
  comparisons. A small binary top-candidate heap was tried and rejected before
  commit because it increased comparisons.
- The Q2 top-10 cache step is the first fix based on those attribution
  counters. It keeps heap and Rift on the same logical query algorithm and
  avoids recomputing the top-10 frontier when the rank update cannot affect the
  cached result. The 100k single-run validation reduced top-candidate
  comparisons from `4.45M` to `144949`; the 1M single-run validation recomputed
  top 10 `29983` times out of `1000000` calls. The 3-run medians confirm the
  direction at bounded scale: at 1M, heap is `6192.692 ms`, HPZone is
  `5697.948 ms`, and Streaming is `5657.424 ms`; GC drops from `70.762 ms` to
  about `36 ms`, and Rift RSS is much lower. One 1M HPZone run was slower than
  heap, so this is still bounded-sample evidence, not final DEBS proof.
- The GC heap allocation-attribution step adds a separate diagnostic axis for
  memory-management overhead. `gc_time_ns` is only collection time; attribution
  mode shows the cost of ordinary heap allocator calls as well. At 1M, Rift
  removes about `5.46M` heap allocation calls and `224 MB` of rounded heap
  allocation requests, and measured heap allocation-call time falls by about
  `197-199 ms`. Because this mode times every heap allocation, its elapsed
  timings are diagnostic rather than headline throughput numbers.
- Next, continue moving dominant heap control/collection state only where the
  heap and Rift paths remain the same logical program and the lifetime boundary
  is explicit.

Implementation substeps:

- Treat input/parser cleanup as shared noise reduction unless the only
  allocation-placement difference is explicit, as with the current heap input
  buffer vs Rift region input buffer.
- Keep Q1 heap and Rift algorithms aligned. Any future Q1 optimization must be
  shared by both modes unless the only difference is allocation placement.
- Q2 profit and empty-taxi windows now have heap and Rift backends over the
  same algorithm.
- Q2 active profit values now live in window entries instead of a heap
  `ArrayBuffer`; Q2 median scratch arrays are region-backed in Rift modes and
  reused rather than reset per processed trip.
- Q1 route-table arrays now have a heap/Rift allocation-placement split over
  the same primitive open-addressed layout. Q1 still uses a heap `TreeSet` for
  ranking order. This is trusted HPZone benchmark code, not the final safe
  mixed-reference story.
- Q1/Q2 ranking objects now have a heap/Rift allocation-placement split.
- Q2 bounded cell tables now have a heap/Rift allocation-placement split over
  the same fixed-array layout. This is acceptable Phase 5 evidence because Q2's
  grid key space is bounded by the benchmark and both modes use the same
  logical structure.
- Q2 latest-empty taxi state now has a heap/Rift allocation-placement split over
  the same growable dense-array layout.
- Q2 ranking now has a heap/Rift allocation-placement split over the same
  indexed-heap layout. The ranked values are ordinary `ProfitableArea` Scala
  objects; the ranking index arrays are region-backed in Rift modes.
- Q2 taxi-id metadata now has a heap/Rift allocation-placement split over a
  shared byte-backed hash table. This deliberately avoids storing heap `String`
  references in region entries.
- Q1 ranking now has a heap/Rift allocation-placement split over a shared
  indexed-heap layout. The ranked values are ordinary `RankedRoute`, `Route`,
  and `Cell` Scala objects; the ranking index arrays and objects are
  region-backed in Rift modes.
- Primitive keys and packed cell/route IDs remain acceptable only as shared
  noise cleanup or as temporary boundaries where mixed-reference safety is not
  implemented.
- RunBoth input bytes now have a heap/Rift allocation-placement split over the
  same byte parser. Single-query Q1/Q2 runners still use the older file input
  path and are not the source of Phase 5 input-buffer evidence.
- Do not add more reset-per-event region scratch paths; the superseded
  snapshot-result experiment showed they can replace GC as the bottleneck.
- Do not add a separate hand-specialized heap-only Q1/Q2 implementation. The
  useful Q1 indexed-ranking checkpoint kept heap and Rift on the same logical
  algorithm, then changed allocation placement by mode.
- Use primitive keys and packed cell/route IDs only when the change is shared
  across modes or needed to avoid unsafe region-to-GC references.
- Keep heap roots explicit for any heap object referenced from region memory.
- Rerun 100k and 1M instrumented matrices with medians after each change that
  looks promising in a single run. The superseded resettable snapshot-result
  numbers are diagnostic only; the current reusable-array backend has 100k and
  1M medians.
- Add Commix and improved SafeZone modes where meaningful.
- Scale to full-month joined/sorted data only after the bounded samples have a
  stable region-heavy implementation.

Exit criteria:

- Both queries run simultaneously and correctly.
- Results include medians for throughput, p50/p99/p99.9 latency, GC time, RSS,
  and Rift operation time.
- At least one Rift mode reduces GC time or tail latency for a reason traceable
  to region-backed application data structures.
- The writeup separates runtime-only, topology/layout, and application effects.

Do not claim Phase 5 success until these criteria are met.

## 9. Phase 6: Literature-Aligned Methodology And API Evidence

Goal: compare Rift against literature-shaped workloads while preserving the
separation between runtime-only effects, topology/layout effects, and
static-safety ambitions. These are local methodology reproductions unless an
original artifact is available.

Current status:

- `evidence/DATAFLOW_REGION_MATRIX.md` records Broom-style
  SELECT/AGGREGATE/JOIN methodology workloads over ordinary Scala objects.
- `evidence/STREAMFLEX_REGION_MATRIX.md` records StreamFlex-style throughput
  and per-event latency/deadline-miss workloads.
- `evidence/YAK_REGION_MATRIX.md` records Yak-style word-count, graph-step,
  external-sort-shaped grouped sort, top-word/filter, GraphChi-like subinterval
  updates, and promotion/escape epoch/control-data
  split workloads. It now includes a `yak-runtime` proxy for a pure
  runtime-managed epoch discipline on Scala Native and a
  `RiftRegion.RuntimeEpoch` memory API for rare escaping data objects.
  Top-word/filter gives a strong local raw Rift-vs-heap win and a modest
  Rift-vs-improved-SafeZone win; GraphChi-like subintervals give a strong
  Rift-vs-heap win but still trail improved SafeZone; grouped sort gives a
  modest raw Rift-vs-heap win while sorting dominates elapsed time; the
  promotion proxy removes measured heap GC but is slower than heap on elapsed
  time at the current pressure size.
- `evidence/STANCU_REGION_MATRIX.md` records Stancu-style
  transaction/accounting workloads. A 2026-04-26 boundary sweep confirms that
  one transaction per region is too fine-grained, while 64 transactions per
  region gives a Rift-vs-heap win; SafeZone remains faster.
- `sandbox/PIPELINE_PARCOLL_COMPARISON.md` records the amordo
  `ZoneParVector` benchmark and the Rift raw-array surrogate.
- The comparison is explicitly not apples-to-apples.

Required work:

- Keep the Broom/Yak/StreamFlex/Stancu harnesses clearly labeled as
  methodology reproductions and avoid comparing absolute speedups to paper
  systems with unavailable artifacts.
- Build a `RiftParVector`, region-backed stage buffer, or equivalent
  collection/operator API.
- Reproduce the amordo pipeline shape using the Rift API, not raw arrays.
- Compare heap `ParVector`, amordo `ZoneParVector`, SafeZone, and Rift under the
  same logical API.
- Track annotation burden, release/reset ergonomics, and any capture-checking
  rejection/fallback cases.

Exit criteria:

- Literature-shaped benchmark notes include commands, run counts, data sizes,
  medians, GC/Rift operation metrics, RSS where collected, and caveats.
- Rift has a fair Broom/parallel-collections API comparison, not only a raw
  array surrogate.
- Results state whether wins come from allocator runtime, topology/lifetime
  boundaries, data layout, or lower-level array loops.

## 10. Phase 7: Capture-Checked Safe API

Goal: make `Scoped` and `Streaming` regions safe by construction rather than by
convention.

Required work:

- Define user-facing safe APIs for scoped and streaming regions. First slice is
  implemented as `RiftRegion.scoped`, `RiftRegion.streaming`, and
  `RiftRegion.reset`.
- Add positive compile/run tests for for-loops, nested regions, and
  higher-order code. Compiler probes now cover for-loop allocation, nested
  scoped regions, and a local higher-order consumer.
- Add negative compile tests for return escape, closure capture escape,
  cross-region leakage, use-after-reset, GC-to-region fields, and unrooted
  region-to-GC ownership. Current probes cover return escape, a heap singleton
  retaining a scoped value, a closure that captures the region handle, nested
  inner-region leakage, streaming reset escape, returned function values, and
  the positive explicit-root path for region-to-GC metadata. Direct unrooted
  heap-object constructor arguments are now rejected in checked Rift allocation
  lowering; simple region-local aliases are allowed, while heap aliases and
  heap field selections are rejected. Stable constructor fields with source
  type `T^{region}` are allowed; plain `T^` fields selected from a region owner
  are rejected by Scala capture checking when `T^{region}` is required.
  Region-owned arrays are allowed when reference elements are explicitly
  captured, for example `Array[T^{region}]^{region}`; stores into known region
  arrays reject unrooted heap objects. Mutable local linked-list heads are
  allowed when their observed assignments are `null`, direct Rift allocations,
  or already-known region values; assigning a heap object drops the provenance
  and is rejected if the head is later stored into region memory.
- Create or update `REPORT_CAPTURE_CHECK.md` with exact checker behavior. The
  first report slice is filled in from the 2026-04-26 targeted compiler run.
- Decide whether current Scala 3 capture checking is enough or whether the fork
  needs a small compiler extension.

Exit criteria:

- Positive cases compile and run.
- Negative cases fail for capture/safety reasons, not incidental type errors.
- Any checker limitation is documented and reflected in the design. Current
  documented limitations are conservative rejection of direct function results,
  incomplete static-heap/higher-level-container mixed-reference modeling,
  limited ergonomics for plain selected fields and array element captures,
  local-only mutable-head provenance, and mostly unpinned diagnostic text.

Comparison obligation:

- Show why the API is less restrictive than StreamFlex and Reggio but safer
  than Broom and HPZone.
- Count annotations and compare qualitatively to Stancu-style `@RegionScope`
  and Reggio capability annotations.

## 11. Phase 8: Native GC/Region Integration Hardening

Goal: resolve mixed GC-region safety and native-runtime compatibility.

Required decisions:

- Should safe regions forbid owning region-to-GC references?
- Should Rift expose explicit GC-root handles for heap values stored in regions?
  First v1 answer: yes, through `RiftRegion.HeapRoot[T]` and
  `RiftRegion.root(value)`.
- Should region metadata be scanned by the GC?
- Should typed-region metadata eventually support BIBOP-style layout or
  tag-free scanning?

Required tests:

- Region-to-GC reference retained only by region memory must fail statically or
  be kept alive by explicit root/scan machinery. The explicit-root path now has
  compiler and runtime smoke coverage; direct unrooted heap-object constructor
  arguments and simple heap aliases/field selections now fail in checked
  allocation lowering. Stable constructor fields explicitly captured by
  `{region}` are allowed. Stores into known region-owned arrays are checked.
  Mutable local region heads preserve provenance across `null`, direct Rift
  allocations, and known region values, but heap assignment invalidates that
  provenance.
- GC-to-region references through heap fields must fail for safe regions.
- HPZone versions of these cases must be labeled unsafe/trusted.

Exit criteria:

- The mixed reference story is explicit in design, tests, and benchmarks.
- Native/non-moving assumptions remain valid.
- No copying collector is introduced into Scala Native's C interop path.

## 12. Phase 9: Lean Mechanization

Goal: mechanize the core safety story.

Required model:

- Syntax for functions, closures, allocation, region open, close, reset, and
  capture sets.
- Two-space store: GC heap plus region heaps.
- Typing judgment with capture sets.
- Operational semantics for allocation and close/reset.
- A model of GC fallback sufficient to state containment.

Required theorems:

- Progress.
- Preservation.
- Containment.
- Safe close/reset.

Exit criteria:

- Core theorems are proved without `sorry`.
- The model covers at least one higher-order closure case, because that is where
  the literature review identifies prior proof fragility.

## 13. Phase 10: Writing

Goal: turn the artifact into a defensible research narrative.

Expected structure:

- Literature gap and comparison contract.
- Baseline correction and why old SafeZone numbers were incomplete.
- In-tree runtime/compiler implementation.
- Runtime-only evidence.
- Topology/layout decomposition.
- Application evidence from region-heavy DEBS and collection operators.
- Capture-checking safety.
- Lean proof.
- Limitations and failure cases.

Do not write the conclusion before Phase 5, Phase 7, and Phase 9 have real
evidence.

## 14. Immediate Safe Next Action

After these docs, the safest technical next action is:

1. Preserve the Q2 top-10 cache medians as the latest bounded Phase 5 evidence.
   They are stronger than the prior single-run checkpoint but still not final
   full-DEBS evidence.
2. Use the new allocation-attribution counters to choose the next DEBS target:
   remaining heap allocation pressure is now a first-class metric alongside
   collection time, RSS, phase timers, and Rift op time.
3. For literature-methodology hardening, Yak now has local Hyracks-, Hadoop-,
   and GraphChi-shaped probes. The next step should either add safety probes
   for these object patterns or return to DEBS controls, rather than adding
   another synthetic Yak variant immediately.
4. Decide whether the next DEBS target is rank maintenance/output attribution
   or whether Phase 7 should take priority with safe API probes for the region
   object patterns already used by DEBS and the literature harnesses.
5. If continuing DEBS, keep the fair-backend rule: same logical query
   algorithm, heap backend with `new`, Rift backend with `region.alloc` and
   region close/reset at the same lifetime boundary.
6. Rerun 100k and 1M instrumented medians after every further DEBS change.
   Use `SCALANATIVE_GC_ALLOC_STATS=1` selectively for attribution, not as a
   default headline benchmark.

Do not move straight to new runtime micro-optimizations unless the DEBS
diagnosis points there.

## 15. Unsafe Assumptions To Avoid

- Rift already has final DEBS application proof. The bounded-sample top-cache
  medians are encouraging application evidence, but SafeZone/Commix,
  full-month scale, and safe API controls are still missing.
- `gc_time_ns` captures all memory-management cost. It captures collection
  time only; heap allocation-call cost now has its own opt-in diagnostic
  counters.
- Allocation-attribution elapsed timings are headline results. They are
  intentionally perturbing and should be used for diagnosis.
- SafeZone is solved or irrelevant.
- Layout wins prove allocator wins.
- The raw-array pipeline surrogate is a Broom or `ZoneParVector` replacement.
- Region-to-GC references are safe just because region memory is live.
- Full automatic region inference is realistic for all Scala code.
- Reggio-style capabilities can be copied without paying annotation or topology
  costs.
- The active `origin` remote is the intended `641bill` fork.
