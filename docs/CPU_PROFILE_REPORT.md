# Rift CPU Profiling Report

Last updated: 2026-05-21 13:46 CEST

Status: representative L4 profiling coverage is complete for the current
headline/tuning set. The first profile-driven implementation follow-up removed
sampled zone page-size/padding helpers from Yak graphstep. The completion pass
adds real text/top-k, richer LogHub, Theodolite, NEXMark Q8/Q9, larger
SPECjbb2005-workload, and ReML Tier-2 shaped profiles. The 2026-05-18 gap-fill
pass adds the newer Broom retained-dataflow rows, Theodolite retained UC4, and
LogHub retained session/join rows. The first post-profiling allocation-path
cleanup now disables Rift allocation counters in `RIFT_FINAL_CLEAN=1` runs.
The mutator-parity cleanups now remove per-record parser tuple allocation from
the LogHub/Wikimedia retained-session path, DSPBench file-backed parsers, boxed
outer-loop state from the checked Wikimedia and Theodolite callbacks, and the
Wikimedia inferred session path's remaining boxed loop state after the internal
inline reset split. The latest shared parser follow-ups fuse Wikimedia
clickstream TSV field hashing/count parsing/whole-line hashing into one byte
pass and replace the retained-UC4 `DelimitedByteFields` walk with a direct
byte-cursor field scan. These are heap-and-checked fairness cleanups, not
Rift-specific memory-management wins.

Reference: Scala Native official profiling guide:
<https://scala-native.org/en/stable/user/profiling.html>

Optimization literature note:
`docs/OPTIMIZATION_LITERATURE_NOTES.md` records the post-profile reading pass
over Blackburn-style zeroing/methodology work, HotSpot allocation and escape
analysis practice, StreamFlex/Yak/Broom/Stancu/ReML lessons, and
reference-capability design ideas. The short consequence for this report is
that `_platform_memset`, object construction, and allocation lowering are real
targets, but zeroing or allocation work can only be removed with compiler proof
or same-shape controls. L1 headline timing stays separate from L2/L3/L4
interpretation.

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

## 2026-05-19 Mutator-Parity Cycle

Artifacts:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260519-mutator-cycle`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260519-wikimedia-decompressed-control-rerun`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260519-dataflow-scaled`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260519-dspbench-postscratch-linked`

This pass compares heap, checked Rift, checked scoped, and inferred checked
rows where available, then classifies samples into coarse work buckets with
`scripts/profile-category-summary.py`. Bucket percentages are L4 diagnostic
evidence only. Because removing GC makes the remaining work a larger share of
samples, the useful comparison is absolute samples/sec plus the top-frame
symbols, not percentages alone.

One temporary decompressed-input control was run for Wikimedia clickstream:
`/private/tmp/rift-wikimedia-clickstream-control-20260519.tsv`, about `1.6G`.
It was deleted immediately after the control. The decompressed control did not
materially change the diagnosis: checked rows still showed higher visible
TSV/byte-line parse and hash sample rates than heap, so gzip/inflate alone is
not the explanation for the checked non-GC overhead.

Representative bucket snapshots:

| Row | Parser/input/hash samples/sec | Safepoint/GC/meta samples/sec | Allocation/init samples/sec | Main interpretation |
|---|---:|---:|---:|---|
| Wikimedia heap, compressed | `444.60` | `262.60` | small | Heap pays visible Immix work plus the same TSV/hash floor. |
| Wikimedia checked Rift, compressed | `631.00` | `203.40` residual | region alloc `2.80` | Region allocation is not the bottleneck; inspect checked session-loop/input shape and parser/hash attribution. |
| Wikimedia heap, decompressed control | `413.60` | `230.40` | small | Removing gzip did not remove the parser/hash floor. |
| Wikimedia checked Rift, decompressed control | `579.20` | `182.80` residual | region alloc `1.00` | Same diagnosis as compressed: checked-specific non-GC cost is not close/open. |
| Dataflow aggregate heap, scaled | `query 289.20` | `205.20` | heap alloc `61.80` | Heap has query work plus Immix allocation/metadata. |
| Dataflow aggregate checked scoped, scaled | `query 226.40` | `0.00` | region alloc `83.40`, token `7.80` | Shared query work is not slower here; remaining overhead is region allocation/token work. |
| Dataflow aggregate checked direct epoch, inferred profile | `query 239.20` | `0.00` | region alloc `66.00`, token `0.00` | Inferred direct epoch has no residual heap/GC bucket; remaining cost is query/mix plus Rift allocation/init. |
| Dataflow aggregate checked direct epoch, inferred + `cache-large` | `query 182.00` | `0.00` | region alloc `47.80`, token `0.00` | Larger slab reuse removes the hot-loop mmap/remap component at 100M scale. This is an opt-in throughput/RSS policy, not a lower-memory result. |
| Dataflow aggregate checked scoped, inferred comparison profile | `query 202.40` | `0.00` | region alloc `78.80`, token `10.20`, memset `18.00` | Scoped is fastest in the L2 gate, but the final-clean external timing narrows scoped versus inferred direct epoch to `6.33 s` versus `6.41 s` over 20 x 5M docs x3. Treat this as backend/code-shape selection, not accidental heap allocation. |
| DSPBench Fraud checked scoped, post scratch | parser `249.80` | `149.00` | heap alloc `140.60`, memset `59.00` | File-backed DSPBench is input/replay/runtime-allocation dominated; query-state tuples are gone but not the leading cost. |
| DSPBench Log checked scoped, post scratch | parser `241.20` | `190.20` | heap alloc `126.60`, memset `58.20` | Same as Fraud: useful as a real-input regression/control, not an allocator headline. |

2026-05-20 classifier corrections: the category helper now classifies
`LogHubRetainedSessionMatrixHelpers.*anonfun` top frames as query/session-loop
work before applying broad parser/input patterns. Scala Native mangled closure
symbols include parameter type names such as `StreamingByteLineSource`; without
this correction the checked Wikimedia session-loop closure was counted as
parser/input/hash merely because the source object appeared in the signature.
The helper also splits `scalanative_GC_yield` into a `safepoint_poll` bucket
instead of lumping it into GC mark/sweep metadata. In checked rows with very
low timed GC, those samples mostly mark runtime safepoint polling in hot loops,
not actual tracing work.

The helper now also reports `boxing_runtime` for
`scala.scalanative.runtime.Boxes` frames. The sampled boxing buckets are
currently tiny in the remaining checked real-input rows: DSPBench Fraud checked
scoped `1.60` samples/sec, DSPBench Log checked scoped `1.00`, Theodolite
retained UC4 checked Rift `1.20`, and LogHub retained join inferred checked
Rift `0.00`. Primitive boxing remains a valid future inference/lowering topic,
but it is not the next high-impact profile-driven optimization target for
these rows.

Implementation follow-up:

- `DSPBenchRegionMatrix` now avoids per-record tuple returns from
  `FraudPredictorState.update` and `LogStatusState.update`; state update
  results are stored in reusable scratch fields. This preserves the logical
  program shape for heap and checked rows and removes accidental shared
  mutator allocations.
- Fresh native-link validation plus generated/file-backed 20k smokes passed.
- Post-fix profiles under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260519-dspbench-postscratch-linked`
  contain no sampled `Tuple` frames in the DSPBench state-update path.

Current ranked optimization/evaluation table:

| Rank | Optimization / target | Evidence | Implementation status | Speed / RSS / GC effect | Risk | Next action |
|---:|---|---|---|---|---|---|
| 1 | Final-clean stats-disabled Rift object allocation fast path | StreamFlex checked stream and focused allocation profiles still sampled allocator-body work after earlier stats and slab-zeroed cleanup. | Implemented in `RiftRuntime.c`; stats-enabled diagnostic path kept. | Focused final-clean 5M checked Rift allocation improves `68.998 -> 64.485 ms`, same checksum and zero GC. StreamFlexDesign 20M x3 L1 transfer row is heap `32.71 s`, checked Rift stream `19.63 s`, checked scoped `26.04 s`, same checksum/output. | Low: no safety invariant removed; only bypasses stats accounting when `alloc_stats_enabled=false`. | Keep as accepted. Re-profile rows only if a future allocator change modifies the same path. |
| 2 | DSPBench accidental tuple/parser allocation cleanup | Post-sweep profiles and code audit found per-record tuple/result objects in file-backed parser/state update paths. | Implemented with reusable scratch records and state result fields. | Generated 1M x3 post-fix rows: Fraud heap `447.066 ms`, checked epoch stream/scoped `305.767/305.361 ms`; Log heap `417.961 ms`, checked epoch stream/scoped `273.882/273.639 ms`. Post-fix L4 profiles contain no sampled `Tuple` frames in the DSPBench state-update path. | Low/medium: backend-neutral parser/query shape change; must keep checksum/output parity. | Accepted as mutator-parity cleanup, not a Rift-specific memory-management claim. Do not tune further unless DSPBench becomes a headline row. |
| 3 | Wikimedia/LogHub checked session-loop and join source shape | Compressed and temporary decompressed controls both showed checked rows with higher parser/hash/session-loop sample rates than heap; pre-fix checked top frames exposed `scala.runtime.LongRef`, `BooleanRef`, and `IntRef` captures from outer mutable loop state. The minimized inline-reset probe also showed that the enclosing inline-wrapper source shape loses owner tracking. | Source-shape cleanup implemented for session modes: immutable base values, local EOF flag, reusable parsed-field scratch, and region-owned checked `counts` arrays. Internal `resetOpenHandleInline` probes now compile and runtime-prove simple/non-inline-wrapper open-handle bodies, including region-owned arrays. `checked-rift-inferred` session and join modes are now split out of the enclosing `inline def` wrapper and use a sandbox-only bridge to the internal inline reset helper; session also keeps mutable counters local to the open-handle callback. Public Rift APIs are unchanged. | Session 1M L2 rows matched checksum/output. Split-only session: heap `2044.334 ms`, checked Rift `1955.329 ms`, inferred checked Rift `1867.761 ms`, checked scoped `1972.133 ms`. State-local session: heap `2082.274 ms`, checked Rift `2015.182 ms`, inferred checked Rift `1927.010 ms`, checked scoped `1968.287 ms`. Fresh L4 state-local profile no longer shows boxed-ref top-frame parameters; query/session-loop is `56.00` samples/sec and region allocation is `3.80` samples/sec. Archive-backed join 1M L2: heap `8268.847 ms`, explicit checked `10102.728 ms`, inferred checked `8350.524 ms`, scoped `8389.309 ms`, all with matching checksum/output. Join L4 follow-up shows parser/input/hash is close across modes (`598.80` heap, `622.60` inferred checked samples/sec) and safepoint polling is also close (`~190` samples/sec); checked mark/sweep metadata is `0.00`, while the callback-ref-shape bucket is `12.60` samples/sec for inferred checked, marking generated closure bodies whose signatures carry `scala.runtime.*Ref`. | Low/medium for accepted cleanup and split framework paths; medium/high for general callback inlining because ownership preservation is still not solved for arbitrary enclosing inline wrappers. | Keep session and join splits. Next target is compiler ownership/effect-summary support for inlineable checked region-body callbacks beyond hand-split framework paths. |
| 4 | Theodolite checked stream callback boxed loop state | Pre-fix retained-UC4 checked Rift profile exposed `scala.runtime.IntRef`/`LongRef` in `runCheckedEpochStreamingHandle` because the region callback mutated outer `checksum`, `index`, `length`, and epoch counters. The later source-use audit found the checked handle path still spelled retained record placement as explicit `RiftAllocator.allocateOpenHandle(region, new ...)`. | Implemented with local primitive accumulators inside the checked epoch callback and a primitive-only `StreamingEpochOutcome` copied back after close. Query semantics and retained object placement are unchanged. A follow-up source-use slice now constructs retained `CheckedMeasurement` and `CheckedContribution` records with ordinary `new` under the active `resetOpenHandle` owner in both streaming-file and preloaded handle paths; scoped/open-region and legacy explicit-allocation controls remain unchanged. | 20k smoke and 1M L2 matched checksum/output. 1M L2 checked Rift improved from the earlier `2143.809 ms` row to `2049.682 ms`; checked scoped is `2061.617 ms`. Post-fix L4 has no sampled `IntRef`/`LongRef`/`ObjectRef`/`BooleanRef`; remaining samples are parser/input/hash, archive inflate, residual runtime allocation, and UC4 helper work. The active-handle source-use follow-up passed `sandbox3_next` compile plus a focused real archive-member 20k retained-UC4 smoke with checksum `-2895454912458695581`, output `1544`, checked stream `260000` region objects, and `0.556 ms` Rift op time. | Low/medium: accepted source-shape cleanup; one primitive outcome object per epoch remains a small heap allocation. The ordinary-`new` follow-up is source-use evidence for an already-proven active-handle inference path, not a new L1/L2 or L4 speed claim. | Keep the cleanup. Do not tune region close/open here; the follow-up byte-cursor parser cleanup is shared mutator fairness work and the remaining Rift-specific target is compiler callback ownership/effect summaries. |
| 5 | Narrow ReML-style placement for remaining high-frequency synthetic objects | Inference rows exist for `Some`, `Tuple2`, closure arguments, generic `Cell`, local/method-return shapes; Wikimedia inferred profile has the same shape as explicit checked Rift. | Partially implemented and validated by compiler/runtime allocation-stat tests. | Reduces explicit allocation boilerplate and proves placement, but current representative profiles have not shown a new elapsed win from inference alone. | Medium/high: polymorphic hiding, widened `AnyRef`, arrays, closure escape, and heap metadata hazards must remain rejected. | Continue only when profiles show frequent synthetic allocation in checked paths and safety probes already cover the shape. |
| 6 | Shared byte-line parser/hash cleanup | Real streaming rows, including Wikimedia and Theodolite UC4, are dominated by parsing, byte-line reading, hashing, and numeric extraction. The old Wikimedia clickstream parser sampled separate `tsvFieldHash`, `tsvFieldInt`, and `stableHash` top frames; the retained-UC4 path still sampled `DelimitedByteFields.readCurrent`/field-cursor work before numeric parsing. | Implemented for Wikimedia clickstream in `LogHubRetainedSessionMatrix`: field-0/1/2 FNV hashes, field-3 count parsing, and whole-line FNV hash now run in one byte pass; the dead old TSV helper functions were removed. Implemented for Theodolite retained UC4 in `TheodolitePowerRegionMatrix`: `parseCurrentLine` scans the semicolon byte line directly to fields `2`, `4`, `6`, `7`, and `8`, then calls the existing numeric parsers. Both changes are backend-neutral and apply to heap and checked rows. | Wikimedia 20k compressed smoke and 1M x3 L2 matched checksum/output; L4 no longer samples the old separate TSV/hash helpers. Theodolite 20k smoke and 1M x3 L2 also matched checksum/output; the accepted 1M gate under `/Users/siyaoliu/rift/cache/theodolite-bytecursor-parser-1m-l2-20260520` is heap `2325.524 ms`, checked stream `1965.787 ms`, checked scoped `1999.749 ms`, all checksum `5496025699187626461` and output `61760`. Theodolite L4 under `/Users/siyaoliu/rift/cache/profile-sweep-20260520-theodolite-bytecursor-parser` drops checked parser/input from `168.60/s` to `147.00/s`. | Medium: parser rewrites can invalidate prior evidence if checksums drift. A fully fused Theodolite numeric parser was rejected because it worsened the 1M gate. | Accepted as shared parser/hash fairness cleanup, not as a Rift-specific win. The remaining checked-specific target is callback/session-loop code shape and compiler owner/effect summaries. |
| 7 | StreamFlex callback-body source shape | StreamFlex post-fast-path profile originally showed `211.00/s` callback-ref-shaped samples in generated checked stream callback bodies. After the callback-local source cleanup and classifier correction, callback-ref samples drop to `0.00/s`; actual traversal/capsule remains small at `35.40/s`, while region allocation/init is `273.60/s` and query/body work is `491.60/s`. | Callback-local source-shape cleanup implemented and validated by compile, 20k smokes, L4, and 20M x3 L1. It is profile-clarity cleanup, not a speed win: checked stream is `19.98 s` versus the prior `19.63 s` checkpoint, while heap in the same run is `34.58 s`. | No new accepted speed claim beyond prior StreamFlex/page-token optimizations. The row still strongly beats heap, but the callback-local change itself is timing-neutral to slightly slower. | Low for the accepted source-shape cleanup; medium/high for future query/object pipeline changes if they alter operator shape. | Do not spend more time on counter-localization or capsule traversal based on this row. Next StreamFlex target is region allocation/init or query/object pipeline work with same-shape controls. |
| 8 | Broom retained checked callback source shape | The goal audit found large checked callback-ref-shaped top frames in Broom q17/shopper (`255.80/s` and `366.80/s`) from reset bodies reading mutable outer `checksum`, `processed`, and `group`. The retained records were already region-owned. | Implemented immutable per-group base values in `BroomRetainedDataflowMatrix.scala` so reset bodies capture primitives, not outer mutable refs. The same pattern was applied to aggregate/join checked helpers while preserving semantics. | 20k smokes matched checksum/output for q17, shopper, aggregate, and join across heap and checked Rift. Focused L4 under `/Users/siyaoliu/rift/cache/profile-sweep-20260520-broom-callback-local` drops callback-ref samples to `0.00/s` for q17 and shopper. Post-cleanup 20M active-16 timing rows: q17 checked Rift `9.45 s` L1 and `3229.305 ms` L2 versus heap `13.17 s` and `4782.648 ms`, RSS `56.0 MB` versus `233.3 MB`; shopper checked Rift `14.74 s` L1 and `5115.933 ms` L2 versus heap `17.55 s` and `6285.094 ms`, RSS `99.0 MB` versus `815.8 MB` L1. | Low/medium: source-shape cleanup only; no query rewrite. | Accepted as profile-clarity/mutator-parity cleanup. The timing rows show the post-cleanup retained-object advantage, but the isolated effect of the source-shape edit is the callback-ref bucket removal, not a standalone speed claim. |
| 9 | Broom q17/shopper/generated-array inferred source placement | Aggregate/join already exercised ordinary `new` under active checked owners, but q17/shopper still used explicit `RiftAllocator.allocateOpenHandle(new ...)` for high-frequency retained records, and generated Broom inferred paths still had explicit active-handle `new Array` plumbing for per-group object arrays. | `checked-rift-inferred` now covers q17 part/entry/lineitem records, shopper view/cart/purchase/candidate nodes, and generated object arrays in aggregate (`heads`/`tails`/`tables`), join (`left`/`right`), q17 (`tables`), and shopper (`views`/`carts`/`purchases`/`candidates`). TPC-H file-input q17 conservatively falls back to explicit checked allocation. | Compile/native link passed. 20k smokes matched heap/explicit/inferred checksum/output. The prior 20M q17/shopper L2 record slice preserved region objects/RSS; the new 1M generated-array L2 gate under `/Users/siyaoliu/rift/cache/broom-inferred-arrays-1m-l2-20260521` also matched checksum/output and preserved identical explicit/inferred region objects for aggregate `1839798`, join `1000006`, q17 `1478215`, and shopper `1142743`. No new L4 bucket reduction is claimed. | Low/medium for this source-placement expansion; medium for broader method/effect-summary inference. | Accepted as ReML-style placement evidence, not a speed optimization. Next inference target should be compiler method/effect summaries or profiled synthetic allocations, not more benchmark-local source plumbing. |

## Work-Bucket Explanation

This table is the compact answer to the current checked-overhead audit. Values
are active L4 samples/sec from `scripts/profile-category-summary.py`. They are
diagnostic profile evidence, not headline timing. "Real checked overhead" means
the checked row is doing visible extra non-GC work in absolute samples/sec or
in a checked-only bucket; "percentage inflation" means the bucket looks larger
mainly because the heap row's GC/metadata bucket disappeared.

| Family / representative row | Parser/input/hash | Query mutator | GC/meta and safepoints | Residual heap alloc/init | Region alloc/init, zeroing, token | Traversal/capsule | Other | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Wikimedia clickstream heap vs checked Rift, post fused-parser cleanup | Heap `418.20`, checked `496.60`, inferred `490.20`, scoped `512.40` | Heap `52.60`, checked `121.40`, inferred `74.20`, scoped `102.40` | Heap mark/sweep `93.60` plus safepoint `97.60`; checked mark/sweep `0.00`, safepoint `129.80`; inferred safepoint `177.20`; scoped mark/sweep `2.80`, safepoint `126.60` | Heap `5.00`; checked `0.00` | Checked region `2.60`, inferred `4.80`, scoped `6.20`; zeroing heap `1.00`, inferred `2.20`, scoped `1.40` | `0.00` | Heap `79.40`, checked `6.20` | The old separate `tsvFieldHash`/`tsvFieldInt`/`stableHash` top frames are gone, and 1M L2 elapsed drops for every row. The remaining parser/input bucket is a real shared TSV/gzip/byte-line floor; it is larger in checked partly because heap still spends samples in GC/metadata. Region allocation remains tiny. The remaining checked-specific overhead is query/session-loop callback shape, especially the explicit checked path; the split inferred path is closer to heap. |
| Dataflow aggregate, scaled direct/scoped | Heap parser `0.00`; checked `0.00` | Heap `298.60`; explicit direct `253.80`; inferred direct `239.20`; scoped `202.40`; cache-large inferred `182.00` | Heap GC metadata `245.80`; checked `0.00` | Heap `60.00`; checked `0.00` | Explicit direct region `70.60`; inferred direct `66.00`; scoped region `78.80`, token `10.20`, memset `18.00`; cache-large region `47.80` | `0.00` | Heap `188.20`; inferred direct `24.80` | Checked is not slower in shared query work. The real checked overhead is region allocation/init, scoped token/zeroing, and default slab remapping. `cache-large` proves part of the region-op cost is reusable-slab policy. |
| StreamFlexDesign checked stream after timing guard | Heap from same sweep family: query `136.00`, traversal `145.40`, heap alloc `156.40`, GC metadata `163.20`; checked: query `467.80`, traversal `30.20`, region `244.20`, other `25.40`; inferred checked query `464.40`, traversal `34.80`, region `251.00` | see previous cell | Heap GC/metadata and heap alloc disappear in checked | Checked heap alloc `0.00` | Region alloc/init is real at `244.20-251.00`; zeroing/token not sampled | Heap traversal `145.40`; checked `30.20-34.80` | Checked `22.40-25.40` | Checked is faster in L1 despite a larger query bucket. The larger query share is partly percentage/classification shift after heap GC/allocation disappear, but region allocation/object construction remains real checked work. Traversal/capsule is smaller than the older heap control and no longer the next target. |
| DSPBench Fraud real file-backed, post scratch | Heap parser `255.20`; checked `249.80` | Heap `1.00`; checked `1.20` | Heap mark/sweep `122.00`, safepoint `19.20`; checked mark/sweep `127.40`, safepoint `21.60` | Heap `136.40`; checked `140.60`; boxing checked `1.60` | Region/token `0.00`; memset heap `63.40`, checked `59.00` | `0.00` | Heap `135.40`; checked `142.20` | Checked is not slower because of Rift allocation. The row is dominated by shared file replay, zip/input, runtime allocation, and parser work; residual heap allocation is mostly library/runtime/input floor. |
| DSPBench Log real file-backed, post scratch | Heap parser `226.40`; checked `241.20` | Heap `5.40`; checked `4.60` | Heap mark/sweep `164.80`, safepoint `28.60`; checked mark/sweep `162.20`, safepoint `28.00` | Heap `113.60`; checked `126.60`; boxing checked `1.00` | Region/token `0.00`; memset heap `58.40`, checked `58.20` | `0.00` | Heap `147.60`; checked `117.20` | Same diagnosis as Fraud. The parser/state-update tuple cleanup removed benchmark tuple churn, but the remaining heap allocation is shared runtime/input work rather than checked-region placement failure. |
| Broom q17 generated retained | Heap query `346.20`, heap alloc `45.40`, GC metadata `83.60`, safepoint `100.40`; post-callback-cleanup explicit checked query `254.80`, region `20.60`, safepoint `68.80`; inferred checked query `252.40`, region `23.20`, safepoint `74.00`; callback-ref `0.00` | see previous cell | Heap GC disappears; checked safepoint remains lower than heap in the callback-local comparison, but explicit/inferred checked are similar | Checked heap alloc `0.00` | Explicit/inferred region `20.60/23.20`, memset `0.00/1.00` | `0.00` | Explicit/inferred checked `16.00/15.20` | The checked row is not residual-heap dominated. Inferred ordinary `new` preserves region placement and the same profile shape; remaining work is generated query body plus region allocation/init. |
| Broom shopper generated retained | Heap query `380.60`, heap alloc `50.00`, GC metadata `151.60`, safepoint `125.40`; post-callback-cleanup explicit checked query `391.60`, region `19.60`, safepoint `38.60`; inferred checked query `384.60`, region `19.80`, safepoint `37.20`; callback-ref `0.00` | see previous cell | Heap GC disappears; explicit/inferred checked have the same non-GC shape | Checked heap alloc `0.00` | Explicit/inferred region `19.60/19.80`, memset `5.00/4.00` | `0.00` | Explicit/inferred checked `73.20/75.80` | Same conclusion as q17: ordinary retained objects are region allocated in both explicit and inferred forms; the source-shape marker is gone, leaving query work and region allocation/init as the remaining checked buckets. |
| Theodolite retained UC4 real stream, post byte-cursor parser | Heap parser `133.80`, checked `147.00`, scoped `148.20` | Heap `49.80`, checked `23.40`, scoped `24.40` | Heap mark/sweep `43.40`, safepoint `51.40`; checked mark/sweep `20.40`, safepoint `48.40`; scoped mark/sweep `24.00`, safepoint `50.60` | Heap `25.60`; checked/scoped `19.00`; boxing checked `1.00`, scoped `1.40` | Checked region `6.20`, scoped `8.80`; memset heap `12.60`, checked `9.20`, scoped `13.40` | `0.00` | Heap `55.60`, checked `31.20`, scoped `34.20` | Real stream remains parser/numeric/archive dominated, but the shared parser bucket is lower than the post-loop-shape `168.60/s` checked-only follow-up. The checked rows are not region-lifecycle dominated; residual heap allocation is input/runtime floor, not retained-object placement failure. |

Immediate conclusion: the top shared floors are parser/input/hash for
Wikimedia, Theodolite, DSPBench, and LogHub-style rows. Broom q17/shopper no
longer have the large checked callback-ref source-shape bucket after the
focused cleanup. The top real checked overheads that remain evidence-backed
are StreamFlex/Dataflow region allocation and object construction, scoped token
and zeroing paths, and compiler ownership/effect summaries for inlineable
checked region-body callbacks. Parser/hash changes can be fairness cleanups
only if heap and checked are rerun together.

## Residual Heap Allocation Audit

This table classifies sampled or code-audited heap allocation that remains in
checked rows. The purpose is to separate accidental checked-loop/source shape
from shared parser/input floors and from durable heap state.

| Benchmark | Source file | Hot function / frame | Allocation shape | Owner / lifetime | Current placement | Classification | Proposed fix / status | Risk | Expected effect |
|---|---|---|---|---|---|---|---|---|---|
| Wikimedia clickstream session | `scala-native-rift/sandbox/src/main/scala-next/LogHubRetainedSessionMatrix.scala` | checked session body and `LogHubRetainedSessionMatrixHelpers.*anonfun` | `LongRef`/`BooleanRef`/`IntRef` closure boxes from mutable outer `checksum`, `processed`, `group`, `done`; checked `counts` array | Per group/epoch session state | Was heap before fix; gone from post-fix checked top frames; `counts` now region-owned | shared heap/parser fairness cleanup, fixed; `counts` was region-placeable now | Accepted cleanup: immutable base values, local EOF flag, reusable parsed scratch, and region-owned checked counts array | Low/medium; source-shape only, checksum/output gated | Removed accidental checked callback heap/runtime helper work; 1M L2 and 10M L4 match checksum/output. |
| Wikimedia clickstream parser/hash | `LogHubRetainedSessionMatrix.scala`, `BenchmarkInputSupport`, `ByteLineReader` | byte-line reader, fused `readClickstreamFieldsInto` | input buffers, byte fields, hash/key helper state | Shared input stream and durable parser scratch | Heap/shared runtime | shared heap/parser fairness cleanup, fixed for the old multi-pass TSV helper | Backend-neutral fused parser implemented: field hashes, count, and line hash are computed in one pass; compressed input remains default | Medium; parser changes can invalidate evidence if checksums drift | 20k smoke and 1M L2 matched checksums/output for heap/checked/inferred/scoped; old separate TSV/hash helper frames disappear. This reduces elapsed for both heap and checked, not region allocation overhead. |
| Wikimedia inferred session/join callbacks | `LogHubRetainedSessionMatrix.scala` | inferred `resetOpenHandleInline` session and join bodies | generated closure/source shape that can carry owner-token and `scala.runtime.*Ref` signatures; per-group checked arrays | Per checked region body | Callback is mostly code shape, not sampled heap allocation after cleanup; inferred per-group arrays are now ordinary `new Array` in checked region memory | region-placeable after inference/effect-summary work; direct inline-reset arrays are now region-placeable and fixed | General compiler ownership/effect summaries for arbitrary inlineable checked callbacks remain future work; current sandbox split is accepted for session/join paths, and direct inline-reset arrays are now source-placed | Medium/high for general callbacks; low for the direct-array source placement, which is checksum/output gated | Removes explicit inferred-array allocation plumbing; 20k compressed Wikimedia/HDFS smokes match heap/explicit/inferred/scoped checksum/output, and the follow-up 1M Wikimedia audit gate preserves identical explicit/inferred region objects (`1922465`) with inferred checked `965.723 ms`. Broader callback/source plumbing still needs owner/effect-summary preservation. |
| Broom q17 | `scala-native-rift/sandbox/src/main/scala-next/BroomRetainedDataflowMatrix.scala` | `runCheckedQ17` reset body, `BroomRetainedDataflowMatrixHelpers.*anonfun` | Pre-fix `LongRef`/`IntRef`-shaped outer-loop state in checked reset callback signature; generated `CheckedQ17Part`, `CheckedQ17PartEntry`, and `CheckedQ17LineItem` records; generated q17 table array | Timestamp group state and per-timestamp retained records/array | Callback state marker fixed; explicit and inferred record forms are region-owned; generated inferred table array now uses ordinary `new Array` and remains region-owned | region-placeable now, fixed for local primitive state, inferred retained records, and generated q17 array; general callback ownership remains future compiler work | Accepted cleanup plus inferred ordinary `new` for q17 retained records and generated table array; file-input q17 remains explicit for now | Low/medium; source-shape/source-placement cleanup, no query rewrite | Callback-ref drops to `0.00/s`; inferred q17 matches explicit region objects in the 20M record gate (`29150680`) and the 1M generated-array gate (`1478215`) with checksum/output parity. |
| Broom shopper | `scala-native-rift/sandbox/src/main/scala-next/BroomRetainedDataflowMatrix.scala` | `runCheckedShopper` reset body | Same pre-fix `LongRef`/`IntRef` source-shape marker plus view/cart/purchase/candidate retained nodes and generated per-group object arrays | Timestamp group state and retained join records/arrays | Callback state marker fixed; explicit and inferred node forms are region-owned; generated inferred arrays now use ordinary `new Array` and remain region-owned | region-placeable now, fixed for local primitive state, inferred retained nodes, and generated shopper arrays; general callback ownership remains future compiler work | Same immutable-base cleanup plus inferred ordinary `new` for retained shopper nodes and generated arrays | Low/medium | Callback-ref drops to `0.00/s`; inferred shopper matches explicit region objects in the 20M record gate (`22857035`) and the 1M generated-array gate (`1142743`) with checksum/output parity. |
| Dataflow aggregate direct/scoped | `scala-native-rift/sandbox/src/main/scala-next/DataflowRegionMatrix.scala` | direct epoch aggregate loop | retained aggregate records and arrays | Epoch-local records; summaries/config are durable heap/control state | Region for transient records; durable state on heap by design | region-placeable now, already placed; durable heap state | Keep inferred direct path; next target is allocation/init, no-zero proof, and opt-in `cache-large` for large direct epochs | Low for policy when opt-in; medium for deeper zero/init work | No residual heap bucket in checked direct rows; region-op drops from `66.00/s` to `47.80/s` with `cache-large`. |
| StreamFlexDesign | `scala-native-rift/sandbox/src/main/scala-next/StreamFlexDesignMatrix.scala` | checked stream throughput body, stable-state classify/update, capsule transfer | transient packets/features/decisions/alerts plus durable stable state/capsule arrays | Period-local transients; durable framework state | Transients region-owned; stable state/capsules durable heap/framework state | region-placeable now, already placed; durable heap state | Keep inferred checked stream; next work is allocation body/object construction and reusable framework representation, not parser or benchmark rewrite | Medium; object/layout changes affect multiple rows | Inferred source path already improves L1 `19.01 s -> 18.16 s`; remaining buckets are query `~464-468/s` and region alloc/init `~244-251/s`. |
| DSPBench Fraud/Log parser/replay | `scala-native-rift/sandbox/src/main/scala-next/DSPBenchRegionMatrix.scala`, `BenchmarkInputSupport` | file-backed parser, zip replay, byte reader | input/decompression/FileChannel/runtime allocation, buffers, residual runtime metadata, tiny boxing | Shared real-input replay and parser scratch | Heap/runtime in both heap and checked | library/runtime unavoidable for now; shared heap/parser fairness cleanup | Parser result tuples and state-update tuples already replaced with reusable scratch/result fields; further parser work must be backend-neutral | Medium; real-input parser changes need checksum/output gates | Current checked residual heap alloc is similar to heap (`140.60/136.40` Fraud, `126.60/113.60` Log), so further effect is modest and shared. |
| DSPBench page-token/scoped helpers | `DSPBenchRegionMatrix.scala`, page-token checked modes | page-token callback/helper state, SafeZone page/root bookkeeping; prior explicit `RiftAllocator.allocateOpenHandle(currentHandle, new CheckedRecord(...))` source plumbing in the Rift-backed page-token append path | Operator callback/control state and per-record checked page-token records | Heap/runtime or SafeZone internals for framework state; checked records are region-owned | library/runtime unavoidable for framework internals; checked records are region-placeable now and source-use fixed for the Rift page-token handle path | Added `rift-checked-page-token-inferred` / `checked-region-stream-inferred`: the selected page-token open handle is passed as a method parameter, `CheckedRecord` is constructed with ordinary `new`, and the record is widened to the parent stream owner before append. Existing explicit, legacy open-region, and scoped controls remain | Medium | Focused 20k file-backed Fraud/Log smokes matched heap/explicit/inferred checksum/output and preserved explicit/inferred region-object counts (`80111` Fraud, `60000` Log). This is source-use evidence only; profiles remain input/runtime dominated. |
| Theodolite retained UC4 checked loop | `scala-native-rift/sandbox/src/main/scala-next/TheodolitePowerRegionMatrix.scala` | `runCheckedEpochStreamingHandle`, `runCheckedEpochHandle` | pre-fix `IntRef`/`LongRef` boxes from mutable outer `checksum`, `index`, `length`, epoch counters; one `StreamingEpochOutcome` per epoch; retained `CheckedMeasurement`/`CheckedContribution` source placement | Per epoch stream state and per-record retained UC4 hierarchy objects | Boxes gone post-fix; `StreamingEpochOutcome` remains low-frequency heap result; retained records are checked-region objects and the handle paths now use ordinary `new` under the active owner | shared heap/parser fairness cleanup, fixed; durable heap state for epoch result; retained records are region-placeable now and source-use fixed | Accepted cleanup: local primitive accumulators plus primitive-only outcome object after close. Follow-up active-handle source-use: ordinary `new` for retained measurement/contribution records in streaming-file and preloaded handle paths; scoped/open-region and legacy explicit-allocation controls unchanged | Low/medium | 1M checked Rift L2 improved `2143.809 ms -> 2049.682 ms`; callback-ref bucket removed. The source-use smoke matched checksum `-2895454912458695581` and output `1544`, with checked stream `260000` region objects; no new elapsed/profile claim. |
| Theodolite input/numeric parser | `TheodolitePowerRegionMatrix.scala`, `BenchmarkInputSupport`, `ByteLineReader`, zip input | archive buffers, byte parsing, decimal extraction, residual runtime allocation; old `DelimitedByteFields` cursor work is now removed from retained UC4 | Shared input stream | Heap/runtime plus parser scratch in both heap and checked | shared parser/input floor; accepted byte-cursor cleanup | Backend-neutral direct byte-cursor parser implemented and validated with heap/checked reruns; a fully fused numeric parser variant was rejected as slower | Medium | Improves both heap and checked retained-UC4 rows; L4 checked parser/input drops `168.60/s -> 147.00/s`. Not a region-placement result. |
| Boxed keys / primitive boxes | Scala Native runtime, sampled as `scala.scalanative.runtime.Boxes` | primitive boxes, boxed helper paths | Depends on caller; often library/runtime helpers | Heap/runtime today | region-placeable only after library/runtime support | Keep as future inference/lowering topic; sampled buckets are tiny in current checked rows | Medium/high; boxing is tied to erased generics/runtime helpers | Not next target: DSPBench Fraud `1.60/s`, Log `1.00/s`, Theodolite post-fix `1.20/s`, LogHub join inferred `0.00/s`. |
| Option/Some, TupleN, closures, small wrappers | `nscplugin/.../RiftRegionInference.scala`, `NirGenExpr.scala`, tests | synthetic factory objects and closure environment objects | Proven region-local values under explicit owner/captured expected type | Region when proven; heap fallback otherwise | region-placeable after inference/effect-summary work; many slices implemented | Current implementation covers `Some`, `TupleN` arities 2-22, owner-token args, method returns, arrays including closure array-store values, checked owner-token container closure values, checked stream-rank closure values, and closure-object shapes with negative escape tests | Medium; unrooted heap metadata and widened escape remain hard boundaries | Reduces accidental heap allocation only where proof exists; do not claim full ReML/MLKit inference yet. |

## Wikimedia Clickstream Follow-Up

Date/time: 2026-05-18 17:25-17:27 CEST.

Artifacts:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260518-172522/wikimedia-clickstream-heap.sample.txt`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260518-172522/wikimedia-clickstream-checked-rift.sample.txt`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260518-172522/wikimedia-clickstream-checked-scoped.sample.txt`

Command shape:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
RIFT_PROFILE_CASES="wikimedia-clickstream-heap wikimedia-clickstream-checked-rift wikimedia-clickstream-checked-scoped" \
RIFT_PROFILE_SECONDS=15 \
RIFT_PROFILE_DELAY_SECONDS=2 \
RIFT_PROFILE_WIKIMEDIA_CLICKSTREAM_RECORDS=10000000 \
  zsh sandbox/run_l4_profile_sweep.sh
```

All three rows processed `10000000` Wikimedia clickstream rows and matched
checksum `8006060730683441349` / output count `9323019`.

| Row | Sampled footprint | Top sampled work | Interpretation |
|---|---:|---|---|
| `heap-gc` | about `1.0G` | `scalanative_GC_yield`, TSV field hashing/int parsing, stable hashing, byte-line read/append, Immix marker/heap-block frames. | Heap really pays GC/marking and high RSS, but parser/hash/input work is also a large shared floor. |
| `checked-rift` | about `126.8M` | `scalanative_GC_yield`, TSV field hashing/int parsing, stable hashing, byte-line read/append, checked session loop. | Checked Rift removes the large RSS footprint and most retained-object GC pressure, but the mutator still spends most samples in parsing/hashing and session-loop work, not region close. |
| `checked-region-scoped` | about `127.1M` | TSV field hashing/int parsing, stable hashing, byte-line read/append, checked scoped session loop, plus visible `Marker_markRange`, `Heap_IsWordInHeap`, and small `scalanative_zone_alloc` / SafeZone-backed allocation samples. | Scoped has similar RSS to checked Rift but still shows marker/root-range costs. This is a backend-selection/optimization target, not a separate user-facing system. |

The immediate optimization implication is not more bucket close/open tuning.
For this real streaming row, the visible shared floor is compressed input,
byte-line reading, TSV field hash/int extraction, and session-key stable
hashing. The checked-specific work to inspect next is object construction and
session-loop allocation/linking around `LogHubRetainedSessionMatrix.scala`
checked paths; scoped-specific work is marker/root-range cost. A fair
throughput optimization should improve the shared parser/hash path for both
heap and checked, or reduce checked object/session-loop overhead without
changing the query semantics.

## Wikimedia Loop-Shape Cleanup

Date/time: 2026-05-20 11:20-11:34 CEST.

Artifacts:

- `/Users/siyaoliu/rift/cache/loghub-wikimedia-loopshape-1m-20260520/summary.tsv`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-wikimedia-loopshape-priv`

The checked session loop previously captured outer mutable `checksum`,
`processed`, `group`, and `done` through the region callback. The sampled top
frame encoded those captures as `scala.runtime.LongRef`,
`scala.runtime.BooleanRef`, and `scala.runtime.IntRef` parameters. The cleanup
keeps the same query semantics but uses immutable base values and a local EOF
flag inside the checked group body; it also moves the per-group checked
`counts` array into the region.

Post-fix 1M L2 rows, all with checksum `250002331971566003` and output
`922453`:

| Mode | Median ms | GC median ms | Region op ms | RSS bytes | Interpretation |
|---|---:|---:|---:|---:|---|
| `heap-gc` | `2012.161` | `148.355` | `0.000` | `587350016` | Natural heap baseline, still pays visible retained-object GC/RSS. |
| `checked-rift` | `1990.483` | `0.169` | `2.511` | `123650048` | Explicit checked stream row; boxed-ref closure captures are gone. |
| `checked-rift-inferred` | `1939.183` | `0.262` | `3.667` | `124141568` | Same logical row with inferred data-path object placement. |
| `checked-region-scoped` | `1928.016` | `26.233` | `0.000` | `125124608` | Safe scoped backend comparison row. |

Corrected post-fix profile buckets for the 10M L4 run:

| Row | Parser/input/hash samples/sec | Query/session-loop samples/sec | Safepoint poll samples/sec | GC mark/sweep metadata samples/sec | Region alloc/init samples/sec |
|---|---:|---:|---:|---:|---:|
| heap | `410.60` | `44.40` | `160.40` | `106.80` | `0.00` |
| checked Rift | `529.20` | `92.40` | `204.20` | `0.00` | `3.80` |
| inferred checked Rift | `548.00` | `83.20` | `194.80` | `0.00` | `3.60` |
| checked scoped | `546.20` | `73.00` | `206.80` | `3.40` | `6.60` |

Interpretation: the accepted fix removed accidental boxed-ref loop state, but
it did not turn Wikimedia into an allocator-bound profile. The remaining
checked-specific overhead is the checked region-body/session-loop callback and
the same TSV/hash/byte-line parser floor. A direct experiment making
`resetOpenHandle` inlineable failed at compile time because capture checking
lost the tracked owner and widened the handle to `{any}` in many benchmark
bodies. A narrower internal helper can inline a simple body if the final raw
reset is delegated to a non-inline helper, but the real LogHub/Wikimedia
session and join bodies still fail because their region-local class/array graph
sees an empty owner capture set after inlining. That makes inlineable checked
callbacks a compiler ownership/effect-summary target, not a safe one-line
runtime API tweak.

## Wikimedia Inline-Reset State Cleanup

Date/time: 2026-05-20 13:36 CEST.

Artifacts:

- `/Users/siyaoliu/rift/cache/loghub-wikimedia-inline-reset-state-1m-20260520/summary.tsv`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-wikimedia-inline-reset-state-escalated`

After splitting the inferred session path out of the enclosing inline wrapper,
the next cleanup moved the inferred loop's mutable counters inside the
open-handle callback. This removes the remaining boxed mutable state from the
sampled top frames while keeping the parser, session tables, per-record
objects, and output semantics unchanged.

1M L2 rows, all with checksum `250002331971566003` and output `922453`:

| Mode | Median ms | GC median ms | Region op ms | RSS bytes | Interpretation |
|---|---:|---:|---:|---:|---|
| `heap-gc` | `2082.274` | `175.642` | `0.000` | `590102528` | Natural heap baseline in the same run. |
| `checked-rift` | `2015.182` | `0.157` | `3.011` | `123633664` | Explicit checked stream row. |
| `checked-rift-inferred` | `1927.010` | `0.161` | `3.125` | `126779392` | Inline-reset inferred path with state-local loop counters. |
| `checked-region-scoped` | `1968.287` | `23.875` | `0.000` | `124993536` | Safe scoped backend comparison row. |

Fresh L4 bucket summary for `checked-rift-inferred`:

| Parser/input/hash samples/sec | Query/session-loop samples/sec | Safepoint poll samples/sec | Region alloc/init samples/sec | Zeroing samples/sec |
|---:|---:|---:|---:|---:|
| `519.00` | `56.00` | `241.20` | `3.80` | `1.20` |

Interpretation: the state-local cleanup removes the remaining sampled
`scala.runtime.IntRef`/`LongRef`/`BooleanRef` checked-loop top-frame matches.
It does not change the main diagnosis: region allocation is not the bottleneck
for Wikimedia, and the dominant floor is still TSV byte-line parsing, field
hashing, stable hashing, and residual runtime safepoint/metadata work.

## Wikimedia Fused-Parser Cleanup

Date/time: 2026-05-20 19:08-19:10 CEST.

Artifacts:

- `/Users/siyaoliu/rift/cache/loghub-wikimedia-fused-parser-1m-20260520/summary.tsv`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260520-wikimedia-fused-parser`

The clickstream parser previously walked the same byte line repeatedly:
`tsvFieldHash` for fields 0, 1, and 2, `tsvFieldInt` for field 3, and a
separate whole-line `stableHash`. The cleanup keeps the same FNV hash and count
semantics but computes the three field hashes, count, and whole-line hash in
one pass over `StreamingByteLineSource.bytes`.

20k compressed smokes matched checksum/output across `heap-gc`,
`checked-rift`, `checked-rift-inferred`, and `checked-region-scoped`:
checksum `-5707858218641866390`, output `18036`.

1M x3 L2 rows, all with checksum `250002331971566003` and output `922453`:

| Mode | Median ms | GC median ms | Region op ms | Region objects | Interpretation |
|---|---:|---:|---:|---:|---|
| `heap-gc` | `1219.250` | `103.101` | `0.000` | `0` | Shared parser/hash cleanup also improves the natural heap baseline. |
| `checked-rift` | `1203.342` | `0.232` | `1.739` | `1922465` | Explicit checked still has query/callback source-shape overhead, but not region-allocation overhead. |
| `checked-rift-inferred` | `1124.139` | `0.232` | `1.809` | `1922465` | Fastest row in this gate; region object count matches explicit checked. |
| `checked-region-scoped` | `1216.653` | `30.300` | `0.000` | `0` | Scoped backend keeps the same checksum/output and benefits from the shared parser cleanup. |

Post-cleanup L4 bucket summary:

| Row | Parser/input/hash samples/sec | Query/session-loop samples/sec | Safepoint poll samples/sec | GC mark/sweep metadata samples/sec | Region alloc/init samples/sec |
|---|---:|---:|---:|---:|---:|
| heap | `418.20` | `52.60` | `97.60` | `93.60` | `0.00` |
| checked Rift | `496.60` | `121.40` | `129.80` | `0.00` | `2.60` |
| inferred checked Rift | `490.20` | `74.20` | `177.20` | `0.00` | `4.80` |
| checked scoped | `512.40` | `102.40` | `126.60` | `2.80` | `6.20` |

The old separate `tsvFieldHash`, `tsvFieldInt`, and standalone `stableHash`
top frames are gone from the post-cleanup profiles. The remaining parser/input
bucket is still large because real clickstream replay is genuinely byte-line,
gzip, and TSV dominated. This cleanup is therefore accepted as shared
mutator-parity/fairness work, not as a Rift-specific memory-management win.
The next Rift-specific Wikimedia target remains compiler/API support for
inlineable checked callbacks and owner/effect-summary preservation.

## Wikimedia / LogHub Inferred Array Source-Placement

Date/time: 2026-05-21 06:27-06:50 CEST.

The inferred checked session/join paths already used ordinary `new` for
retained records, but per-group checked arrays inside `resetOpenHandleInline`
still used explicit `RiftAllocator.allocateOpenHandle(region, new Array(...))`.
The new compiler/runtime proof covers ordinary direct `new Array` in inline
reset-open-handle bodies for captured object arrays and primitive
`Array[Int]^{region}`. The matching negative rejects unrooted heap metadata
stores into an inferred region array in that callback shape.

`LogHubRetainedSessionMatrix` now applies that proof only to
`checked-rift-inferred` session and join arrays. Explicit `checked-rift` rows
remain on explicit allocation calls as controls. Focused 20k compressed smokes
matched heap, explicit checked, inferred checked, and scoped checked:
Wikimedia clickstream-session checksum `4440636879622788340`, output `18167`;
LogHub HDFS join checksum `-1607483374812565358`, output `0`.

The follow-up 1M x3 L2 affected-row gate is:

| Workload | Heap | Explicit checked | Inferred checked | Scoped checked | Region-object check |
|---|---:|---:|---:|---:|---|
| Wikimedia clickstream-session | `1383.161 ms` | `1341.892 ms` | `1254.338 ms` | `1344.536 ms` | explicit/inferred both `1922465` |
| HDFS join | `8031.714 ms` | `7839.871 ms` | `7772.096 ms` | `7737.018 ms` | explicit/inferred both `1000006` |

The summary files are under
`/Users/siyaoliu/rift/cache/loghub-wikimedia-inferred-array-1m-l2-20260521`
and `/Users/siyaoliu/rift/cache/loghub-join-inferred-array-1m-l2-20260521`.
These rows validate the affected inferred source shape with matching
checksum/output and unchanged explicit/inferred region-object counts.

The focused current-state L4 sweep is under
`/Users/siyaoliu/rift/cache/profile-sweep-20260521-loghub-array-source`.
All rows matched checksum/output. Wikimedia bucket samples/sec:

| Mode | Parser/input/hash | Query/session loop | Region alloc/init | Safepoint poll | GC/meta | Callback-ref |
|---|---:|---:|---:|---:|---:|---:|
| heap | `341.80` | `58.00` | `0.00` | `105.20` | `124.60` | `0.00` |
| explicit checked | `501.20` | `118.20` | `3.60` | `119.00` | `0.00` | `0.00` |
| inferred checked | `477.00` | `80.80` | `4.40` | `172.80` | `0.00` | `0.00` |
| checked scoped | `493.00` | `106.60` | `6.00` | `136.80` | `3.00` | `0.00` |

This confirms that the latest inferred source path does not move the remaining
Wikimedia cost into region allocation or callback boxing. The main real work is
still byte-line/TSV/hash parsing plus the session-loop body. In this sample the
inferred checked path is lower than explicit checked in both parser/input/hash
and query/session-loop buckets, but heap still has a smaller parser/input/hash
sample rate and pays the visible GC/meta bucket instead. That keeps the top
two concrete causes for checked non-GC overhead unchanged: shared TSV/hash
input work is amplified in checked rows, and the checked session-loop callback
body still carries more visible mutator work than heap.

The same L4 sweep also profiled HDFS join. That row is short at 1M records, so
about half of each five-second sample is startup/idle and the row is diagnostic
only. The non-idle shape is still parser/input/hash plus safepoint polling:
heap parser/input/hash `578.60/s`; explicit checked `589.40/s`; inferred
checked `585.60/s`; scoped `585.60/s`. Inferred checked has `0.00/s`
callback-ref samples in this run, explicit checked has `6.60/s`, and scoped
has `14.20/s`; region allocation/init is not sampled.

## Shared ByteLineReader Chunked Input

Date/time: 2026-05-21 06:53-07:06 CEST.

The current LogHub/Wikimedia L4 profiles still sampled the shared byte-line
reader heavily, with top frames in the old per-byte `ByteLineReader.nextByte`
and `append` helpers. `BenchmarkInputSupport.ByteLineReader.readLine` now
scans each filled input buffer for newline bytes and copies contiguous spans
into the reusable line buffer with `System.arraycopy`. This preserves the same
line semantics, including CR trimming and EOF final-line handling, but removes
per-byte helper calls. The change is shared input plumbing for heap and checked
rows; it is not Rift-specific region overhead removal.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- Wikimedia 20k compressed smoke matched heap/explicit/inferred/scoped checksum
  `-7932171983828413881`, output `17518`.
- HDFS join 20k archive-member smoke matched heap/explicit/inferred/scoped
  checksum `-1607483374812565358`, output `0`. The tar reader still exits
  nonzero when closed at the record limit, but each row wrote a valid `RESULT`.
- Theodolite retained UC4 20k zip-backed smoke matched heap/checked-stream/
  checked-scoped checksum `-2895454912458695581`, output `6176`.

1M x3 L2 affected-row gates:

| Workload | Heap | Explicit checked | Inferred checked | Scoped checked | Summary |
|---|---:|---:|---:|---:|---|
| Wikimedia clickstream-session | `1061.907 ms` | `1041.414 ms` | `960.242 ms` | `1047.725 ms` | `/Users/siyaoliu/rift/cache/loghub-bytereader-wikimedia-1m-l2-20260521` |
| HDFS join | `7134.073 ms` | `7138.545 ms` | `7097.635 ms` | `7140.815 ms` | `/Users/siyaoliu/rift/cache/loghub-bytereader-join-1m-l2-20260521` |

The post-change L4 sweep is under
`/Users/siyaoliu/rift/cache/profile-sweep-20260521-bytereader-loghub`. All
rows matched checksum/output. The old `ByteLineReaderD8nextByte` and
`ByteLineReaderD6append` top frames are absent; samples now land in the
chunked `ByteLineReader.readLine` body. The coarse parser/input/hash bucket is
mixed and should not be reported as a uniform bucket reduction: Wikimedia
parser/input/hash is heap `385.80/s`, explicit checked `478.80/s`, inferred
checked `510.40/s`, and scoped `484.60/s`. The accepted effect is the L2
throughput improvement plus removal of the per-byte helper frames; the shared
parser/input floor remains the dominant real-input cost.

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
SPECjbb2005-workload port, ReML-shaped Tier 1/Tier 2 ports, Wikimedia
clickstream-session, Broom retained aggregate/join/q17/shopper, Theodolite
retained UC4, LogHub retained session/join, and a Yak graphstep epoch-body
profile. Details and smoke/full-sweep results are tracked in
`evidence/PROFILE_SWEEP_MATRIX.md`.

## 2026-05-18 Gap-Fill Profiles

Artifacts:

- `/Users/siyaoliu/rift/cache/profile-sweep-20260518-gap-fill`
- `/Users/siyaoliu/rift/cache/profile-sweep-20260518-loghub-retained-rerun`

The gap-fill pass covers the newer retained-object rows that were not present
in the first broad profile sweep. All rows completed with matching
checksum/output. The LogHub retained session/join profiles were rerun at 5M
records because the 1M sample mostly caught startup/exit noise. The macOS
`sample` output includes a long-lived process-exit checker thread reported as
`kevent`; that is ignored in the interpretation below.

| Family | Profiled rows | Main sampled work | Interpretation |
|---|---|---|---|
| Broom retained aggregate | `checked-rift`, `checked-region-scoped`, `heap-gc` at 20M active-16 | Checked Rift samples the aggregate loop plus `scalanative_rift_region_alloc_object_fast` / `scalanative_rift_region_alloc_nozero`; heap samples the same loop plus `Allocator_Alloc`, Immix bytemap/object metadata, marker, and sweep work. | This is the cleanest profile of the intended memory-management story: same logical retained dataflow shape, heap pays tracing/allocator metadata, checked Rift pays region allocation but avoids heap marking of retained transient records. |
| Broom Q17 and shopper | `checked-rift`, `checked-region-scoped`, `heap-gc` at 20M active-16 | Checked rows are dominated by the generated query loop and region allocation/zeroing; heap rows show the same query loops plus `Allocator_Alloc`, `GC_alloc_small`, `Heap_IsWordInHeap`, `Marker_Mark`, `Marker_markField`, and sweep metadata. | Q17/shopper support the same conclusion as aggregate/join. The remaining checked cost is allocation body, object construction/zeroing, and query logic, not close/open bookkeeping. |
| Theodolite retained UC4 | `checked-epoch-stream`, `checked-epoch-scoped`, `heap` over real UCI power stream | Both heap and checked are dominated by byte-line input, gzip inflate, decimal parsing, and UC4 hierarchy helper functions. Heap also samples `Allocator_Alloc`, object metadata, and `_platform_memset`; checked Rift samples the checked epoch body but not a large close/open path. The 2026-05-20 loop-shape follow-up removed sampled checked callback `IntRef`/`LongRef` parameters, and the later byte-cursor parser follow-up removed the retained-UC4 `DelimitedByteFields` walk. | This row is real-streaming and RSS/fixed-memory strong, but CPU is still input/parser dominated. The accepted loop-shape cleanup improves 1M checked Rift L2 from `2143.809 ms` to `2049.682 ms`; the accepted byte-cursor parser gate then reports heap `2325.524 ms`, checked stream `1965.787 ms`, and checked scoped `1999.749 ms`, with checked parser/input dropping from `168.60/s` to `147.00/s`. Further Rift-specific speed work should be compiler callback ownership/effect summaries or general allocation/init work, not region lifecycle tuning. |
| LogHub retained session/join | `checked-rift`, `checked-region-scoped`, `heap-gc` at 5M HDFS lines | Main-thread samples are `containsAscii`, `String.charAt`/`length`, `stableHash`, `tokenHash`, `tokenSeparator`, and byte-line reader paths. Region allocation and heap allocation are comparatively small in the sampled main-thread stack. | This confirms LogHub retained rows are parser/hash/string dominated. They remain useful real-streaming controls and RSS evidence, but they are not good allocator optimization targets. |

Practical consequence: topology is not the optimization story by itself. The
main story remains natural heap/GC versus checked Rift. Topology only explains
which checked lifetime boundary and backend were selected. For optimization,
Broom-style generated retained rows point at allocation/object initialization;
real streaming rows point at shared byte-slice parsing and hashing.

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
- `/Users/siyaoliu/rift/cache/profile-post-rerun-20260512-clean-winners`

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

## Post-Rerun Clean-Winner Profiles

Date/time: 2026-05-12 16:41-16:42 CEST.

This pass profiles the actual clean-rerun winners rather than the older default
cases: `checked-epoch-stream` for `StreamFlexDesignMatrix` and
`rift-checked-page-token` for generated Common Crawl-shaped q2.

Artifacts:

- `/Users/siyaoliu/rift/cache/profile-post-rerun-20260512-clean-winners/streamflex-design-checked-stream.sample.txt`
- `/Users/siyaoliu/rift/cache/profile-post-rerun-20260512-clean-winners/commoncrawl-q2-checked-rift.sample.txt`

Findings:

| Target | Main sampled frames | Interpretation |
|---|---|---|
| StreamFlexDesign `checked-epoch-stream` | `processCheckedPeriod`, `scalanative_rift_region_alloc_object_fast`, `_platform_memset`, `StableState.classify`, `StableState.recordEvent`, capsule add/drain, and `scalanative_rift_alloc_stats_enabled`. | The clean StreamFlex winner still spends time in allocation/object construction/zeroing plus stable-state and capsule CPU. It is not dominated by epoch reset/close. The remaining per-allocation stats-enabled check is now visible enough to treat as a small final-clean hot-path cleanup candidate. |
| Common Crawl-shaped q2 `rift-checked-page-token` | `closeRecords`, `appendPageTokenOwnedOpen`, `StreamAppendCursor.nextOwnedOrNull`, `scalanative_rift_region_alloc_object_fast`, `_platform_memset`, token hashing/query work, and `scalanative_rift_alloc_stats_enabled`. | The clean page-token winner still pays required cursor traversal and token/query CPU in addition to allocation/zeroing. Further bucket open/close bookkeeping work is unlikely to be the next large win; the useful targets are allocation lowering/zeroing/stat-check removal and, only where semantics allow, avoiding record traversal by maintaining append-time summaries. |

This profile pass does not change headline timing. It updates the optimization
priority: remove remaining final-clean per-allocation checks if practical,
then investigate object construction/zeroing or same-shape append-time summary
APIs before adding more page-token lifecycle tweaks.

## Region-Cached Allocation-Stats Follow-Up

Date/time: 2026-05-12 17:11-17:16 CEST.

The final-clean Rift runtime now caches allocation-stats mode on each
`scalanative_rift_region` at open. A post-change L4 sweep reran the two clean
winner targets:

- `/Users/siyaoliu/rift/cache/profile-post-region-cached-stats-20260512/streamflex-design-checked-stream.sample.txt`
- `/Users/siyaoliu/rift/cache/profile-post-region-cached-stats-20260512/commoncrawl-q2-checked-rift.sample.txt`

`scalanative_rift_alloc_stats_enabled` is no longer sampled in either profile.
The remaining StreamFlex-design samples are in `processCheckedPeriod`,
`scalanative_rift_region_alloc_object_fast`, `scalanative_rift_region_alloc`,
`_platform_memset`, stable-state classify/update work, and capsule add/drain.
The remaining Common Crawl-shaped q2 samples are in `closeRecords`,
`appendPageTokenOwnedOpen`, `StreamAppendCursor.nextOwnedOrNull`, region
allocation, `_platform_memset`, and token/hash/query work.

Focused allocation did not improve over the prior object-fast baseline
(`71.702 ms` versus `69.912 ms` for 5M objects), so this is a profile cleanup
and modest application-level win rather than a new focused allocation win.
The application gates moved slightly in the expected direction: page-token
checked Rift `25.007 -> 24.618 ms`, StreamFlex-design checked stream
`22.81 -> 22.55 s`, and Common Crawl-shaped q2 checked Rift `11.49 -> 11.39 s`.
The next optimizer targets remain object construction/zeroing, allocation-body
code shape, and same-shape operator summaries where query semantics allow them.

Post-current-slab-zeroed profile and rejected branch split, 2026-05-13:
the follow-up L4 sweep under
`/Users/siyaoliu/rift/cache/profile-post-slab-zeroed-20260513-escalated`
confirms that allocation and zeroing remain visible after the accepted
current-slab zeroed-state cache. StreamFlexDesign `checked-epoch-stream`
samples `processCheckedPeriod`, `scalanative_rift_region_alloc_object_fast`,
`scalanative_rift_region_alloc`, `_platform_memset`, and the streaming
`allocUncheckedImpl` wrapper. Common Crawl-shaped q2 still samples close
traversal, page-token append, `nextOwnedOrNull`, region allocation, and
`_platform_memset`. A C-only split between stats-disabled and stats-enabled
object helpers improved the focused 5M allocation row slightly (`68.561 ms`)
but regressed page-token and StreamFlexDesign gates, so it was reverted. The
next runtime target should be deeper allocation lowering or proven
initialization, not another final-clean stats-branch reshuffle.

Stats-disabled object allocation fast-path follow-up, 2026-05-20:
the allocator-body cleanup was revisited after the mutator-parity sweep. The
accepted change is narrower than the rejected C-only branch split: final-clean
managed-object allocation uses a no-stats inline helper only when the
region-local `alloc_stats_enabled` flag is false, while the stats-enabled
diagnostic path stays intact. Runtime checked tests passed (`152/152`).

Focused final-clean 5M `ObjectAllocationLoweringMatrix`:

| Row | Previous documented row | Post-change row | Interpretation |
|---|---:|---:|---|
| `rift-checked-rift` | `68.998 ms` | `64.485 ms` | Same checksum and zero GC; accepted focused allocation-body win. |
| `rift-checked-safezone-improved-32k` | n/a | `67.074 ms` | Backend comparison row from the same run. |

StreamFlexDesign 20M x3 L1 transfer gate:

| Mode | External real s | Checksum/output |
|---|---:|---|
| `gc-heap` | `32.71` | matched |
| `checked-epoch-stream` | `19.63` | matched |
| `checked-epoch-scoped` | `26.04` | matched |

Post-change L4 profile:
`/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-nostats-fastpath`.
The coarse bucket summary for `streamflex-design-checked-stream` is still split
between traversal/capsule (`1227` samples, `245.40/s`), region allocation/init
(`1225`, `245.00/s`), and query mutator (`1220`, `244.00/s`). This profile
does not produce headline timing, but it explains why the change improves
elapsed without changing the high-level sample composition: it removes
allocator-body constant cost rather than changing the operator topology.

Dataflow reuse-policy follow-up, 2026-05-20:
the inferred direct-epoch Dataflow profile still showed `mmap`/`munmap` and
`scalanative_rift_mmap_slab_bytes` samples. A focused final-clean policy gate
used `RIFT_REGION_REUSE_POLICY` at 20 epochs x 5M docs/epoch x3:

| Policy | External real s | RSS bytes | L2 mmap slabs | L2 mmap bytes | L2 region-op ms | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| `default` | `6.68`, then `6.44` | `167804928` | `17301` | `587546624` | `55.654` | Default retains less than one large epoch's slab working set, so later epochs remap slabs. |
| `cache-large` | `6.25`, then `6.24` | `167804928` | `20` | `21299200` | `9.627` | Throughput-biased reuse removes the remap cost at this scale without raising observed RSS in this row. |
| `prezero-large` | `6.24` in the first policy sweep | `167821312` | `20` | `21299200` | `60.471` | Prezeroing avoids remapping but moves work to reset/close; not accepted for Dataflow. |

The cache-large L4 profile is
`/Users/siyaoliu/rift/cache/profile-sweep-20260520-dataflow-cache-large/dataflow-aggregate-checked-stream-inferred.sample.txt`.
Its coarse buckets are query mutator `182.00/s`, region allocation/init
`47.80/s`, and other `17.80/s`, versus the prior default inferred direct
profile's query `239.20/s`, region allocation/init `66.00/s`, and other
`24.80/s`. This is the first concrete RSS/throughput policy result: it should
stay opt-in and be reported as a throughput tradeoff, not as a default or a
lower-memory claim.

Final-clean region-op timing guard follow-up, 2026-05-20:
the runtime now guards region open/close/reset/slow-allocation duration
accounting behind the region-local `alloc_stats_enabled` flag. This removes
`scalanative_rift_now_ns()` and `mach_absolute_time` from final-clean hot
paths while preserving L2/stat counters when stats are enabled.

Focused final-clean gates after relink:

| Case | Scale | External real s | RSS bytes | Interpretation |
|---|---:|---:|---:|---|
| StreamFlexDesign `checked-epoch-stream` | 20M events x3 | `19.01` | `12533760` | Improved over the previous post-fast-path checked stream checkpoint (`19.63 s`) with matching checksum/output. |
| StreamFlexDesign `checked-epoch-stream-inferred` | 20M events x3 | `18.16` | `12533760` | The ReML-style inferred-source path is faster than explicit `allocateOpenHandle` source plumbing while preserving the same checksum/output. |
| Dataflow inferred direct epoch, default | 20 x 5M docs x3 | `6.60` | `167821312` | No large standalone Dataflow win; this row remains policy and variance sensitive. |
| Dataflow inferred direct epoch, `cache-large` | 20 x 5M docs x3 | `6.29` | `167821312` | Cache-large remains the useful opt-in policy for large direct epochs. |

L2 sanity check at Dataflow 4 x 5M docs x3 still reports region counters:
median `476.545 ms`, `9.620 ms` region-op, `4.851 ms` slow alloc,
`20,262,148` region objects, and matching checksum. The guard therefore only
removes internal timing calls from stats-disabled L1.

The post-guard StreamFlex L4 profile is
`/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-timing-guard/streamflex-design-checked-stream.sample.txt`.
It has no sampled `mach_absolute_time`, `scalanative_rift_now_ns`, or
duration-accounting frames. Coarse active buckets are query mutator `467.80/s`,
region allocation/init `244.20/s`, traversal/capsule `30.20/s`, and other
`25.40/s`. The next real StreamFlex optimization target is therefore object
allocation/init and query/object pipeline work, not timer or close/open
accounting.

The inferred StreamFlex profile is
`/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-inferred-timing-guard/streamflex-design-checked-stream-inferred.sample.txt`.
Its bucket shape is nearly the same: query mutator `464.40/s`, region
allocation/init `251.00/s`, traversal/capsule `34.80/s`, and other `22.40/s`.
This confirms inference/source placement improves final-clean elapsed without
changing the remaining dominant work; allocation body/object construction and
query body remain the next optimization targets.

Backend-specific marker prototype follow-up, 2026-05-13:
a first attempt to make backend-known `allocOpen` lowering use marker traits
for Rift-open and SafeZone-open regions was rejected. Overloading the existing
`allocOpen` with marker-specific contextual parameters made generic checked
operator code ambiguous. Narrowing that to an experimental `allocRiftOpen`
mode compiled, but the focused allocation run crashed with a null allocation
path and also regressed the baseline row in the same binary. This points to a
compiler/NIR lowering problem rather than a Scala type-alias problem: the next
attempt should introduce an explicit backend-known allocation intrinsic or a
handle-level fast path, not rely on marker casts.

Handle-level allocation-lowering prototype, 2026-05-13:
the follow-up implemented a focused Rift-only open handle that lets NIR
lowering emit `scalanative_rift_region_alloc` directly instead of calling the
virtual `allocUncheckedImpl` wrapper. On the 5M object-allocation matrix, the
experimental `rift-checked-rift-open-handle` row ran at `59.777 ms`, compared
with `70.247 ms` for the same-binary current checked path and `68.998 ms` for
the accepted current-slab zeroed-cache baseline. This confirms the profile
diagnosis: allocation lowering/method-dispatch shape is still meaningful CPU
overhead. The prototype is not yet a final API; the next engineering step is
to fold this handle-level lowering into compiler-owned checked epoch/page-token
paths without exposing raw handles or weakening safety.

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

## Corresponding Heap/Rift Work Buckets

Heap and Rift rows can be compared by corresponding work category, but not by
raw `GC time` alone. For the same logical benchmark, parser, hashing, query,
state-update, checksum, and output work should be broadly comparable. The
memory-management categories differ by backend: heap pays allocation metadata,
safepoints, marking, sweeping, and heap-object zeroing; checked Rift pays region
allocation, object initialization, region handle/token plumbing, and bulk close
or reset. These costs appear partly in mutator time, so a row can improve by
more or less than the reported timed-GC delta.

The helper script `scripts/profile-category-summary.py` parses macOS
`/usr/bin/sample` output and buckets sampled top frames into:
`parser_input_hash`, `query_mutator`, `heap_alloc_init`,
`gc_mark_sweep_metadata`, `region_alloc_init`, `zeroing_memset`,
`startup_or_idle`, and `other`. This is an L4 diagnostic, not headline timing:
sampling is approximate, symbol bucketing is heuristic, and idle/startup frames
must be ignored when interpreting active work.

Representative active-work splits from the 2026-05-18 profile sweep:

| Benchmark/profile | Parser/input/hash | Query mutator | Heap alloc/init | Heap GC/metadata/safepoint | Region alloc/init | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| Wikimedia clickstream 10M, heap | `48.94%` | `4.17%` | `0.95%` | `32.62%` | n/a | Heap spends a large sampled share in GC/metadata, but parser/hash remains the shared floor. |
| Wikimedia clickstream 10M, checked Rift | `69.99%` | `0.04%` | `0.50%` | `24.81%` | `0.48%` | Checked row removes RSS and much timed GC, but remaining active work is dominated by the same parser/hash path plus residual safepoint/runtime frames. |
| Broom q17, heap | n/a | `55.10%` | `6.92%` | `29.23%` | n/a | This is a good retained-object allocator/GC stress row. |
| Broom q17, checked Rift | n/a | `64.82%` | n/a | `18.62%` | `13.32%` | Heap GC/metadata is replaced by region allocation/init; query work remains comparable. |
| Broom shopper, heap | n/a | `40.96%` | `5.25%` | `45.68%` | n/a | Strong prior-work-style retained-object pressure. |
| Broom shopper, checked Rift | n/a | `71.83%` | n/a | `7.18%` | `3.81%` | Checked Rift removes most sampled heap-GC/metadata pressure; remaining time is mostly the actual join/query loop. |
| Theodolite UC4, heap | `43.97%` | `10.74%` | `4.10%` | `24.56%` | n/a | Real stream has meaningful heap runtime work but is still parser/input heavy. |
| Theodolite UC4, checked Rift | `57.66%` | `6.60%` | `2.44%` | `21.66%` | `1.65%` | Checked row improves allocation/RSS behavior, but parsing and numeric extraction are still the dominant shared costs. |

The useful rule for future optimization is: if parser/query buckets are similar
but heap has a large GC/metadata bucket, Rift is doing the intended job. If
checked Rift has higher parser/query samples than heap, inspect code shape,
inlining, cache locality, or extra token/handle plumbing. If region allocation
or zeroing is visible, focus on backend-known allocation lowering, object
initialization/zeroing proof, or reusable-slab policy tuning.

First follow-up fix: `LogHubRetainedSessionMatrix` now parses log and Wikimedia
clickstream lines into one reusable scratch object instead of returning
`(Int, Int, Long)` per record, and it precomputes the clickstream parser branch
once per run. This removes an accidental shared mutator heap allocation from
heap, checked Rift, and checked scoped rows. It is a fairness/performance fix,
not a new memory-management claim.

Second follow-up fix: `DSPBenchRegionMatrix` now parses file-backed sensor,
fraud, and common-log records into reusable scratch records instead of returning
tuples. This removes accidental parser-side heap allocation from both heap and
checked rows. The remaining known tuple-producing hot path is predictor/status
state update output in DSPBench; that should be converted to scratch fields in
the next mutator-parity pass.

Future rows should include:
