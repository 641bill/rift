# Current Rift Status

Last updated: 2026-05-22 08:54 CEST

Status: hot status file. Update this file for routine turn-by-turn progress
instead of editing `docs/HANDOFF.md`, `docs/ROADMAP.md`,
`docs/PERFORMANCE_EVALUATION_REPORT.md`, or `docs/report.html`.

## Current Work Split

| Track | Current owner boundary | Latest status |
|---|---|---|
| Native backend | `scala-native-rift/nativelib/**`, `nscplugin/**`, `unit-tests/native/**`, `sandbox/**` | Scala Native remains the only validated performance backend. Native sandbox compile passed after portable prototype extraction. |
| Backend portability | parent branch `backend-portability` | JVM/HotSpot/Scala.js/Wasm portability docs, prototype evidence, and `experimental/**` patch exports are isolated on `backend-portability` at `065b521`. Keep `main` focused on Scala Native evidence unless backend results are intentionally promoted to presentation context. |
| Benchmark search | parent `evidence/**` plus child sandbox result files | Broom q17 retained join/aggregate and Broom shopper are complete generated methodology rows. SPECjbb/Stancu-style 8M transaction scaling is recorded as generated clean-room methodology evidence, not real-input proof. LogHub Spark archive-wide retained session, Yak LiveJournal streaming graph, AskUbuntu streaming text, and the new named Wikimedia retained clickstream-session row are all recorded as compressed real-streaming evidence. The strongest real-streaming retained-object rows are now Theodolite retained UC4 and Wikimedia retained clickstream-session. |
| Presentation report | `docs/PERFORMANCE_EVALUATION_REPORT.md` and generated `docs/report.html` | Do not edit/regenerate unless presentation claims or tables change. |

## Current-State Full Matrix

- A full selected current-state matrix completed on the dirty working tree at
  `/private/tmp/rift-eval-current-full-20260521`. Treat this as engineering
  evidence for the next optimization choices, not clean presentation evidence.
- Suites: `preflight`, `selected-prior`, `selected-streams`, `checked`, and
  `reml`. The run wrote `19` summary files listed in
  `/private/tmp/rift-eval-current-full-20260521/summary-files.txt`.
- No failure, mismatch, exception, OOM, killed-process, or nonzero row-status
  markers were found by the post-run log scan. Checksums/output counts matched
  within each benchmark family.
- Notable new DSPBench full-scale results: Fraud q2 heap `208405.569 ms`,
  checked page-token `187882.928 ms`, checked SafeZone page-token
  `186988.431 ms`; Log q2 heap `306392.943 ms`, checked page-token
  `273860.718 ms`, checked SafeZone page-token `282953.459 ms`.
- Final wrap-up report pass completed: `docs/PERFORMANCE_EVALUATION_REPORT.md`
  and `docs/RIFT_EVALUATION_SUMMARY_SLIDES.md` were rewritten as concise final
  narrative/talk sources, `docs/ROADMAP.md` received a 2026-05-22 wrap-up
  status section, `scripts/generate-report-html.py` was refreshed with the
  latest headline cards/tables, and `docs/report.html` was regenerated.
- Follow-up report organization pass completed: presentation-facing reports now
  avoid the removed lifetime-atlas discussion, split latest performance rows into
  real/local input versus generated/methodology/microbenchmark evidence, and
  give region inference its own done/left section.

## Active Profiling / Mutator-Parity Cycle

Goal: explain checked Rift non-GC overhead with whole-benchmark profiles, then
apply only general optimizations that preserve the natural heap/GC versus
checked Rift comparison.

Current validated slice:

- Targeted L4 sweep completed for Wikimedia clickstream, Broom q17/shopper,
  Theodolite retained UC4, StreamFlexDesign, DSPBench Fraud, and scaled
  Dataflow aggregate. Artifacts are under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260519-mutator-cycle` and
  `/Users/siyaoliu/rift/cache/profile-sweep-20260519-dataflow-scaled`.
- The required one-at-a-time decompressed-input control was run for Wikimedia
  clickstream. Temporary file:
  `/private/tmp/rift-wikimedia-clickstream-control-20260519.tsv`, size about
  `1.6G`; it was removed after the control run. The control artifacts are under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260519-wikimedia-decompressed-control-rerun`.
  The diagnosis did not change: checked rows still spend most visible samples
  in TSV/byte-line parsing and hashing, so gzip/inflate is not the whole floor.
- `sandbox/run_l4_profile_sweep.sh` now includes
  `wikimedia-clickstream-checked-rift-inferred` plus DSPBench Log q2 profile
  cases, so the representative sweep can cover inferred checked rows and both
  DSPBench Fraud/Log.
- `scripts/profile-category-summary.py` now reports coarse work buckets plus
  `samples_per_sec`. The buckets are diagnostic heuristics; they should not be
  used as headline timing.
- First implementation slice: `DSPBenchRegionMatrix` no longer returns
  per-record tuples from `FraudPredictorState.update` or
  `LogStatusState.update`. The state objects expose reusable scratch result
  fields instead. This is a backend-neutral mutator-parity cleanup, not a
  benchmark-specific algorithm rewrite.
- Second implementation slice: the Rift runtime now uses a stats-disabled
  final-clean managed-object allocation fast path when the region-local
  `alloc_stats_enabled` flag is false. The stats-enabled diagnostic path stays
  intact; the accepted evidence is final-clean L1/focused allocation evidence,
  not profiler or allocation-stats timing.
- Third implementation slice: the Wikimedia checked session loop no longer
  captures outer mutable `checksum`, `processed`, `group`, and `done` through
  boxed `scala.runtime.*Ref` state in the region callback. The checked group
  body now uses immutable base values plus a local EOF flag, keeps parser
  output in a reusable scratch object, and region-allocates the per-group
  checked `counts` array.
- Fourth implementation slice: the Theodolite retained-UC4 checked streaming
  loop no longer captures outer mutable `checksum`, `index`, `length`, and
  epoch counters through boxed `scala.runtime.*Ref` state in the checked epoch
  callback. The epoch body now uses local primitive accumulators and returns a
  primitive-only `StreamingEpochOutcome` after close.
- The profile bucket classifier now treats
  `LogHubRetainedSessionMatrixHelpers.*anonfun` top frames as query/session-loop
  work before broad parser/input matching. This avoids misclassifying checked
  session-loop frames as parser/input/hash only because their mangled
  signature contains `StreamingByteLineSource`.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- Fresh `DSPBenchRegionMatrix` native link passed.
- DSPBench generated 20k smoke passed for `fraud-q2-alert-window` and
  `log-q2-window` across `heap-immix`, `rift-checked-safezone-page-token`,
  `checked-epoch-stream`, and `checked-epoch-scoped`.
- DSPBench file-backed 20k smoke passed for `fraud-q2-alert-window` and
  `log-q2-window` across `heap-immix` and
  `rift-checked-safezone-page-token`.
- DSPBench generated 1M x3 post-fix L2 control is under
  `/Users/siyaoliu/rift/cache/dspbench-mutator-parity-generated-1m-20260519-linked`.
  Direct checked epoch rows remain materially faster than heap for Fraud q2
  (`~305 ms` vs heap `447 ms`) and Log q2 (`~274 ms` vs heap `418 ms`);
  page-token checked is mixed (`486 ms` Fraud, `386 ms` Log), which reinforces
  that topology/backend selection matters under the unified Rift story.
- Post-fix DSPBench L4 artifacts are under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260519-dspbench-postscratch-linked`;
  no `Tuple` frames remain in the sampled DSPBench state-update path.
- Runtime checked-region safety passed after the stats-disabled allocation
  fast path: `tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest`
  reported `152/152` passing.
- Final current-state validation before closing the profiling/optimization
  cycle: `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed at 2026-05-20 00:13 CEST, and
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed at 2026-05-20 00:14 CEST with `152/152` tests passing.
- Focused final-clean allocation gate after the fast path:
  `/Users/siyaoliu/rift/cache/object-allocation-nostats-fastpath-finalclean-5m-20260520`.
  `rift-checked-rift` ran at `64.485 ms` for 5M objects, versus the previous
  documented `68.998 ms` current-slab-zeroed row; checksum matched and GC was
  zero.
- StreamFlexDesign transfer gate after the fast path:
  `/Users/siyaoliu/rift/cache/streamflex-design-nostats-fastpath-20m-20260520`.
  At 20M events x3 L1, heap was `32.71 s`, checked Rift stream was `19.63 s`,
  and checked scoped was `26.04 s`, all with matching checksum/output.
- Post-change L4 StreamFlex profile:
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-nostats-fastpath`.
  Sample buckets are still split across capsule/traversal (`~32%`),
  region allocation/init (`~32%`), and query mutator (`~32%`). The speedup is
  therefore a constant-cost allocator-body cleanup, not a topology change.
- Wikimedia loop-shape validation:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed after the source-shape cleanup. 20k smoke matched checksum/output
  across `heap-gc`, `checked-rift`, `checked-rift-inferred`, and
  `checked-region-scoped`. Post-cleanup 1M L2 rows are under
  `/Users/siyaoliu/rift/cache/loghub-wikimedia-loopshape-1m-20260520`:
  heap `2012.161 ms`, checked Rift `1990.483 ms`, inferred checked Rift
  `1939.183 ms`, and checked scoped `1928.016 ms`, all with checksum
  `250002331971566003` and output `922453`.
- Post-cleanup Wikimedia L4 profiles are under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-wikimedia-loopshape-priv`.
  Boxed `LongRef`/`BooleanRef`/`IntRef` checked-loop top-frame parameters are
  gone. Region allocation is still tiny (`~3.6-3.8` samples/sec), so the
  remaining cost is TSV/hash/input plus the checked session-loop callback.
- A direct `inline resetOpenHandle` experiment was tried and rejected: sandbox
  compile failed because capture checking lost the tracked open-handle owner
  and widened it to `{any}` in many benchmark bodies. This is now a compiler
  ownership-preservation/inference target, not a safe runtime-only patch.
- The first internal callback-inlining probe is now validated:
  `resetOpenHandleInline` can inline simple and non-inline-wrapper
  open-handle reset bodies while preserving region allocation when the final
  raw reset is delegated to a non-inline helper. The positive probes now cover
  both linked region records and region-owned arrays with region-local element
  stores, with runtime allocation stats proving that the array and entries
  land in Rift region memory. The minimized failing shape is now precise:
  putting the same region-local class/array graph inside an enclosing
  `inline def` still fails capture checking with an empty owner capture set,
  and a mixed runtime branch between inferred `new` and explicit
  `allocateOpenHandle` also remains rejected. Compiler validation passed
  `333/333`, runtime validation passed `155/155`, and sandbox compile passed.
- Follow-up implementation slice: `checked-rift-inferred` session mode in
  `LogHubRetainedSessionMatrix` is now split out of the enclosing
  `runCheckedSessionImpl` `inline def` and uses a sandbox-only bridge to the
  internal inline reset helper. This keeps public Rift APIs unchanged and keeps
  the query semantics identical. 20k Wikimedia smoke matched checksum/output
  across `heap-gc`, `checked-rift`, and `checked-rift-inferred`. The first 1M
  x3 L2 split-only row is under
  `/Users/siyaoliu/rift/cache/loghub-wikimedia-inline-reset-1m-20260520`:
  heap `2044.334 ms`, explicit checked Rift `1955.329 ms`,
  inferred checked Rift `1867.761 ms`, and checked scoped `1972.133 ms`, all
  with checksum `250002331971566003` and output `922453`. A follow-up
  state-local cleanup moved the inferred session loop's mutable counters inside
  the open-handle callback. Its fresh 1M x3 L2 row is under
  `/Users/siyaoliu/rift/cache/loghub-wikimedia-inline-reset-state-1m-20260520`:
  heap `2082.274 ms`, explicit checked Rift `2015.182 ms`, inferred checked
  Rift `1927.010 ms`, and checked scoped `1968.287 ms`, all with the same
  checksum/output. The corresponding L4 profile is under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-wikimedia-inline-reset-state-escalated`;
  it no longer has sampled `scala.runtime.IntRef`/`LongRef`/`BooleanRef`
  top-frame matches, region allocation remains tiny (`3.80` samples/sec), and
  query/session-loop samples remain near the split-only row (`56.00`
  samples/sec). The inferred path is accepted as a checked-framework/source
  shape optimization for the session row; join and broader compiler
  ownership/effect-summary support remain open.
- New inference slice: local branch/match-final construction sites now inherit a
  captured expected region type. The compiler inference phase and NIR lowering
  both visit branch/match-returned construction sites, so shapes such as
  `val x: T^{region} = if p then new T(...) else new T(...)` and the mixed
  `if p then new T(...) else RiftAllocator.allocateOpenHandle(region, ...)`
  form used in the inline-reset probe are now supported. The same tested
  lowering now covers local `match` expressions with captured expected types.
  Safety coverage includes negative unrooted-heap-metadata branch/match tests
  and runtime allocation-stat tests proving selected branch/match objects are
  region allocated. Validation passed: compiler `337/337`, runtime
  checked-region `158/158`,
  sandbox compile, and a 20k Wikimedia retained-session smoke across
  `heap-gc`, `checked-rift`, `checked-rift-inferred`, and
  `checked-region-scoped` with matching checksum/output. This is an inference
  capability milestone, not a new presentation benchmark result.
- Follow-up source-shape use: `checked-rift-inferred` join in
  `LogHubRetainedSessionMatrix` is now split out of the enclosing inline
  wrapper and uses the same sandbox-only inline reset bridge as the session
  path. The explicit `checked-rift` join remains on the old non-inline helper
  path for comparison. A compressed archive-member HDFS 20k smoke matched
  checksum/output across `heap-gc`, `checked-rift`, `checked-rift-inferred`,
  and `checked-region-scoped`. The 1M x3 L2 archive-backed follow-up is under
  `/Users/siyaoliu/rift/cache/loghub-join-inline-inferred-1m-20260520`:
  heap `8268.847 ms`, explicit checked Rift `10102.728 ms`, inferred checked
  Rift `8350.524 ms`, and checked scoped `8389.309 ms`, all with checksum
  `4282190220497908364` and output `0`. This is accepted as another
  checked-framework/source-shape cleanup: it removes the rejected enclosing
  inline-wrapper shape from the inferred join path and makes inferred join
  comparable to heap/scoped in this archive-backed control. It is not a
  real-input GC-heavy win because heap GC is only `42.256 ms` of the L2 median.
- Follow-up L4 join profile is under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-loghub-join-inline-inferred`.
  Heap, explicit checked Rift, inferred checked Rift, and checked scoped all
  matched checksum/output on the same 1M compressed HDFS archive-member input.
  Coarse samples/sec are very close across modes: parser/input/hash is heap
  `598.80`, explicit checked `629.40`, inferred checked `622.60`, and scoped
  `612.20`; safepoint-poll samples are also similar (`~190` samples/sec),
  while checked mark/sweep metadata is `0.00`. The new `callback_ref_shape`
  bucket is explicit checked `17.00`, inferred checked `12.60`, and scoped
  `31.20` samples/sec, versus heap `0.00`. This marks generated closure bodies
  whose signatures carry `scala.runtime.*Ref`; it is source-shape evidence, not
  direct allocation time. Region allocation is not the bottleneck for this row.
- StreamFlexDesign callback-local source-shape probe: after the callback-ref
  classifier showed `211.00` samples/sec in checked stream callback-ref-shaped
  bodies, the checked throughput loop was refactored so checksum/output/drop
  counters live inside the `streamingOpenHandle` callback. Sandbox compile
  passed, and 20k smokes for `checked-epoch-stream` and
  `checked-epoch-stream-inferred` matched checksum/output. L4 follow-up under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-callback-local`
  drops the callback-ref bucket to `0.00` samples/sec. After the profile helper
  was corrected to classify `StreamFlexDesignMatrixHelpers.*anonfun` as query
  body work, the same profile is traversal/capsule `35.40`, region alloc/init
  `273.60`, and query mutator `491.60` samples/sec. The 20M x3 L1 gate under
  `/Users/siyaoliu/rift/cache/streamflex-design-callback-local-20m-20260520`
  is heap `34.58 s` and checked stream `19.98 s`, both with matching
  checksum/output. Treat this as source-shape/profile-clarity cleanup, not as a
  new speed claim; the next StreamFlex target is allocation/init or query/object
  pipeline work, not capsule/traversal.
- Dataflow direct-epoch inferred-allocation gate:
  `DataflowRegionMatrix` now has `checked-epoch-stream-inferred` for direct
  epoch SELECT/AGGREGATE/JOIN. The mode keeps the same direct-epoch topology
  and query logic as `checked-epoch-stream`, but uses ordinary `new` in the
  active-handle-owned paths where the captured expected type proves the owner.
  A 20k aggregate smoke matched checksum/output across heap, explicit direct
  epoch, inferred direct epoch, and scoped direct epoch; additional inferred
  direct-epoch SELECT and JOIN 20k smokes also passed with checksums
  `5222637068` and `7627482881`. The focused 20M x3 L2 aggregate gate is under
  `/Users/siyaoliu/rift/cache/dataflow-inferred-direct-epoch-20m-20260520`:
  heap `755.885 ms` with `177.424 ms` median GC; explicit checked direct epoch
  `507.004 ms`, `2.724 ms` region op, and `21310740` region objects; inferred
  checked direct epoch `493.087 ms`, `1.863 ms` region op, and the same region
  object count; checked scoped direct epoch `457.737 ms`. All rows matched
  checksum `2584512318695`. The L2 row has counters enabled for direct Rift
  but not for scoped, so it is interpretation evidence rather than the final
  backend-selection answer.
  A sequential external L1 final-clean follow-up at 20 epochs x 5M docs x3 is
  under
  `/Users/siyaoliu/rift/cache/dataflow-inferred-direct-epoch-finalclean-100m-seq-20260520`:
  heap `12.83 s`, RSS `2289 MB`; explicit checked direct epoch `6.43 s`,
  RSS `168 MB`; inferred checked direct epoch `6.41 s`, RSS `168 MB`; checked
  scoped direct epoch `6.33 s`, RSS `168 MB`. All rows matched checksum
  `12894709366184`. This validates inferred ordinary `new` as a small
  source-plumbing/overhead cleanup for Dataflow, and it narrows the direct Rift
  versus scoped gap to about `1-2%` in final-clean timing rather than the larger
  L2/stat-instrumented gap.
  Follow-up L4 profiles are under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-dataflow-inferred-direct-escalated`.
  Inferred direct epoch has no residual heap allocation or GC metadata bucket;
  it is mostly query/mix (`239.20` samples/sec) plus Rift allocation/init
  (`66.00`). Explicit direct epoch is similar but slightly higher (`253.80`
  query, `70.60` region alloc/init). Checked scoped still wins the L2 gate
  despite visible SafeZone allocation/zeroing samples (`78.80` region alloc,
  `18.00` memset, `10.20` token), so the remaining issue is backend/code-shape
  selection rather than accidental heap allocation in the inferred direct row.
- Dataflow direct-epoch reuse-policy diagnosis:
  the runtime already has the requested `RIFT_REGION_REUSE_POLICY` knob. A
  focused 100M final-clean gate on inferred checked direct epoch shows the
  throughput/RSS tradeoff is real only at scales where a single epoch exceeds
  the default slab-retention budget. Repeat L1 rows under
  `/Users/siyaoliu/rift/cache/dataflow-reuse-policy-inferred-100m-repeat-20260520`
  were default `6.68/6.44 s` versus `cache-large` `6.25/6.24 s`, with the same
  `167804928` RSS and matching checksum. The confirming 100M L2 counter row
  under
  `/Users/siyaoliu/rift/cache/dataflow-reuse-policy-inferred-l2-100m-counters-20260520`
  explains the win: default maps `17301` slabs, `587546624` bytes, and spends
  `55.654 ms` in Rift region ops; `cache-large` maps only `20` slabs,
  `21299200` bytes, and spends `9.627 ms` in region ops. `prezero-large` also
  avoids remapping but raises region-op time to `60.471 ms`, so prezeroing is
  not accepted for this row. L4 cache-large profiling under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-dataflow-cache-large`
  reduces region allocation/init samples from `66.00/s` to `47.80/s`; residual
  `munmap` samples are shutdown cleanup, not the hot epoch loop. This is an
  opt-in throughput policy result, not a lower-memory win.
- Dataflow L2 instrumentation now reports Rift raw bytes, slow allocation
  count, `mmap` slab/byte totals, TLS reuse, and pool reuse, matching the
  Common Crawl page-token diagnostics. `sandbox/run_l4_profile_sweep.sh` also
  accepts `RIFT_PROFILE_EXTRA_ENV`, so profiling policy variants no longer
  require adding one-off profile cases.
- StreamFlexDesign reuse-policy cross-check:
  `/Users/siyaoliu/rift/cache/streamflex-reuse-policy-20m-20260520` shows only
  a tiny movement from default `19.74 s` to `cache-large` `19.64 s`, with the
  same `12550144` RSS and matching checksum/output. This confirms the policy is
  most useful for large-epoch slab-remap pressure, not a universal StreamFlex
  allocation/init fix.
- Final-clean region-op timing guard:
  `RiftRuntime.c` now guards `scalanative_rift_now_ns()` and region
  open/close/reset/slow-allocation duration accounting behind the region-local
  `alloc_stats_enabled` flag. L2/stat rows still collect region-op timings when
  stats are enabled, but `RIFT_FINAL_CLEAN=1` no longer pays internal timing
  calls in the hot path. Validation passed after the runtime change:
  `sandbox3_next/compile`, checked compiler suite `337/337`, and checked
  runtime suite `158/158`. Focused L1 gates after relink: StreamFlexDesign
  checked stream 20M x3 is `19.01 s`, RSS `12.5 MB`, checksum/output matched;
  Dataflow inferred direct epoch 20 x 5M docs x3 is `6.60 s` default and
  `6.29 s` with `RIFT_REGION_REUSE_POLICY=cache-large`, both RSS `168 MB` and
  matching checksum. A Dataflow L2 sanity row still reports counters
  (`476.545 ms`, `9.620 ms` region-op, `4.851 ms` slow alloc), proving the
  guard only affects stats-disabled final-clean mode. StreamFlex L4 post-guard
  profile is under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-timing-guard`:
  no `mach_absolute_time`, `scalanative_rift_now_ns`, or duration-accounting
  frames were sampled. The remaining checked StreamFlex cost is now real work:
  query mutator `467.80` samples/sec, region allocation/init `244.20`
  samples/sec, traversal/capsule `30.20` samples/sec, and other `25.40`
  samples/sec.
- StreamFlex inferred-allocation follow-up:
  `sandbox/run_l4_profile_sweep.sh` now includes
  `streamflex-design-checked-stream-inferred`. The 20M x3 L1 inferred row
  under
  `/Users/siyaoliu/rift/cache/streamflex-timing-guard-20m-20260520` is
  `18.16 s`, RSS `12.5 MB`, with matching checksum/output, versus explicit
  checked stream `19.01 s`. The L4 profile under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-streamflex-inferred-timing-guard`
  has nearly the same coarse shape as explicit checked stream: query mutator
  `464.40` samples/sec, region allocation/init `251.00`, traversal/capsule
  `34.80`, and other `22.40`. This validates the inference/source-placement
  row as a real final-clean speedup, while also showing that the remaining
  large bucket is still allocator/object construction plus query body work, not
  residual explicit `allocateOpenHandle` source plumbing.
- ReML-shaped inferred stream source-placement follow-up:
  `ReMLRegionMatrix` now has `checked-region-stream-inferred` for `msort`,
  `msort-r`, `fft`, `ratio`, `logic`, `ray`, and `tsp`. The new row keeps the
  existing heap, explicit checked stream, and checked scoped rows intact, but
  runs the checked stream body through an `OpenStreamingRegion` epoch and uses
  ordinary `new` for the ReML data-path records and region-owned arrays. This
  is a source-placement/inference gate, not a presentation timing claim.
  Validation passed: `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`,
  native link with `ReMLRegionMatrix` as the main class, and sandbox compile
  with `-P:scalanative:riftInferReport`. Heap, explicit checked stream, and
  inferred checked stream matched checksums for all seven workloads. Inferred
  region-object counts matched explicit checked stream:
  `msort/msort-r` `2000`, `fft` `3071`, `ratio` `2001`, `logic` `120`, `ray`
  `17`, and `tsp` `289`; inferred rows have one expected extra epoch reset.
- Tuple factory inference generalization:
  the compiler/NIR path that placed proven `Tuple2(...)` factory allocations
  now accepts `scala.TupleN.apply` for arities 2 through 22. The same safety
  gate applies: the expected type must name one checked owner, nested direct
  values are attached to that owner, unrooted heap metadata rejects, and
  unproven tuple factories remain normal heap allocations. New Tuple3
  compiler tests cover local array-store, owner-token method-argument,
  method-return, and unrooted-heap-metadata negative shapes. Runtime checked
  allocation stats prove a `Tuple3` and its three nested leaves are region
  allocated. Validation passed: checked compiler suite `343/343`, runtime
  checked-region suite `159/159`, and `sandbox3_next/compile`.
- Wikimedia fused-parser fairness cleanup:
  `LogHubRetainedSessionMatrix.readClickstreamFieldsInto` now computes
  source/target/link-kind FNV hashes, count, and whole-line FNV hash in one
  byte pass instead of calling separate `tsvFieldHash`, `tsvFieldInt`, and
  `stableHash` helpers. This is backend-neutral parser/hash cleanup for heap
  and checked rows, not a Rift-specific memory-management win. Validation
  passed `sandbox3_next/compile`, `LogHubRetainedSessionMatrix` native link,
  and a 20k compressed Wikimedia smoke across `heap-gc`, `checked-rift`,
  `checked-rift-inferred`, and `checked-region-scoped`, all with checksum
  `-5707858218641866390` and output `18036`. The 1M x3 L2 gate under
  `/Users/siyaoliu/rift/cache/loghub-wikimedia-fused-parser-1m-20260520`
  matched checksum/output and reports heap `1219.250 ms`, explicit checked
  `1203.342 ms`, inferred checked `1124.139 ms`, and scoped `1216.653 ms`.
  Focused L4 under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-wikimedia-fused-parser`
  shows the old separate TSV/hash helper frames are gone; parser/input remains
  the shared floor and region allocation remains tiny (`2.60-6.20` samples/sec).
- Theodolite loop-shape validation:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed after the source-shape cleanup. 20k `q3-retained-uc4` smoke matched
  checksum/output across `heap-immix`, `checked-epoch-stream`, and
  `checked-epoch-scoped`. The 1M x3 L2 follow-up is under
  `/Users/siyaoliu/rift/cache/theodolite-loopshape-1m-20260520`: heap
  `2464.646 ms`, checked Rift stream `2049.682 ms`, and checked scoped
  `2061.617 ms`, all with checksum `5496025699187626461` and output `61760`.
  Post-cleanup L4 is under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-theodolite-loopshape`;
  boxed `IntRef`/`LongRef` checked-loop top-frame parameters are gone.
- Theodolite byte-cursor parser cleanup:
  `TheodolitePowerRegionMatrix.parseCurrentLine` now scans the semicolon
  byte line directly to locate fields `2`, `4`, `6`, `7`, and `8` instead of
  using the reusable `DelimitedByteFields` cursor before numeric parsing. This
  is backend-neutral shared parser/input cleanup, not Rift-specific
  memory-management work. A fully fused numeric parser variant was tried and
  rejected because it worsened the 1M gate. The accepted version passed
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`; 20k
  heap/checked stream/checked scoped smokes under
  `/Users/siyaoliu/rift/cache/theodolite-bytecursor-parser-smoke-20260520`
  matched checksum `-2895454912458695581` and output `6176`. The 1M x3 L2
  gate under `/Users/siyaoliu/rift/cache/theodolite-bytecursor-parser-1m-l2-20260520`
  matched checksum `5496025699187626461` and output `61760`: heap
  `2325.524 ms`, checked stream `1965.787 ms`, checked scoped `1999.749 ms`.
  Focused L4 under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-theodolite-bytecursor-parser`
  drops checked parser/input from the prior post-loop-shape `168.60/s` to
  `147.00/s`; region allocation remains small at `6.20/s`.

Goal audit checkpoint:

- Profiling coverage is present for the requested representative set:
  Wikimedia clickstream, Broom q17/shopper, Theodolite UC4, StreamFlexDesign,
  DSPBench Fraud/Log, and Dataflow aggregate. Where available, the matrix
  includes heap, checked Rift, checked scoped, and inferred checked rows; Broom
  and Theodolite checked-scoped coverage is in the 2026-05-18 gap-fill, while
  Wikimedia inferred coverage is in the 2026-05-19 mutator-parity sweep.
- The temporary decompressed-input control is verified removed:
  `/private/tmp/rift-wikimedia-clickstream-control-20260519.tsv` no longer
  exists; compressed Wikimedia input remains the default source.
- `docs/CPU_PROFILE_REPORT.md` now has the requested ranked optimization table
  with optimization, evidence, implementation status, speed/RSS/GC effect,
  risk, and next action.
- `scripts/profile-category-summary.py` now splits `scalanative_GC_yield` into
  `safepoint_poll` instead of grouping it with mark/sweep metadata. This
  clarifies that Wikimedia/LogHub checked rows have high safepoint polling in
  hot parser/session loops but no visible checked mark/sweep metadata bucket.
- `scripts/profile-category-summary.py` now also splits
  `scala.scalanative.runtime.Boxes` into a `boxing_runtime` bucket. Current
  checked real-input profile rows show only tiny sampled boxing buckets:
  DSPBench Fraud `1.60` samples/sec, DSPBench Log `1.00`, Theodolite retained
  UC4 `1.20`, and LogHub retained join inferred `0.00`. Primitive boxing is
  still a future ReML-style lowering topic, but current evidence does not make
  it the next high-impact optimization target.
- `docs/CPU_PROFILE_REPORT.md` now has a goal-shaped work-bucket table for
  Wikimedia, Dataflow aggregate, StreamFlexDesign, DSPBench Fraud/Log, Broom
  q17/shopper, and Theodolite UC4. It records active samples/sec for
  parser/input/hash, query, GC/meta/safepoints, residual heap allocation,
  region allocation/init, zeroing/token work, traversal/capsule, and other,
  and states whether checked Rift is doing real extra work or mostly showing a
  larger percentage because heap GC disappeared.
- The residual heap allocation audit in `docs/CPU_PROFILE_REPORT.md` is now
  split by allocation shape and owner/lifetime. Current high-confidence
  classifications: DSPBench and Theodolite residual heap allocation is mostly
  shared input/runtime floor; Dataflow and StreamFlex transient records are
  already region-placed; Wikimedia and Theodolite boxed callback state is
  fixed; Broom q17/shopper showed a large checked callback-ref source-shape
  marker and were selected for the next safe mutator-parity cleanup.
- Broom retained checked callback source-shape cleanup: checked reset bodies
  now capture immutable per-group `baseChecksum`, `baseProcessed`, and
  `baseGroup` values instead of reading mutable outer loop vars inside the
  checked callback. The q17/shopper target shapes are fixed, and the same
  source-shape pattern was applied to aggregate/join checked helpers in the
  already-open Broom inferred-allocation file.
- Broom validation after the cleanup:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed. 20k smokes matched checksum/output for q17, shopper, aggregate, and
  join across `heap-gc` and `checked-rift`. Focused L4 under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-broom-callback-local`
  completed for q17/shopper checked Rift and dropped `callback_ref_shape` from
  the prior q17/shopper `255.80/366.80` samples/sec to `0.00/0.00`; remaining
  checked buckets are q17 query `163.20`, region `29.20`, safepoint `48.60`,
  and shopper query `332.60`, region `17.00`, safepoint `38.60`.
- Broom post-cleanup L1/L2 rows are under
  `/Users/siyaoliu/rift/cache/broom-callback-local-20m-l1-rss-20260520` and
  `/Users/siyaoliu/rift/cache/broom-callback-local-20m-l2-20260520`. At 20M
  active-16, q17 checked Rift is `9.45 s` L1 and `3229.305 ms` L2 versus heap
  `13.17 s` and `4782.648 ms`, with RSS `56.0 MB` versus `233.3 MB` and zero
  timed checked GC. Shopper checked Rift is `14.74 s` L1 and `5115.933 ms` L2
  versus heap `17.55 s` and `6285.094 ms`, with RSS `99.0 MB` versus
  `815.8 MB` in L1 and zero timed checked GC. These rows report the
  post-cleanup retained-object result; the isolated effect of the source-shape
  edit remains the L4 callback-ref bucket removal.
- Broom inferred q17/shopper source-placement follow-up:
  `checked-rift-inferred` now covers q17 `CheckedQ17Part`,
  `CheckedQ17PartEntry`, and `CheckedQ17LineItem` plus shopper
  view/cart/purchase/candidate nodes with ordinary `new` under the same active
  open-handle owner. The initial q17/shopper slice left generated arrays
  explicit; the later Broom generated-array follow-up now covers aggregate,
  join, q17, and shopper generated object arrays with ordinary `new Array` in
  inferred rows. TPC-H file-input q17 conservatively falls back to explicit
  checked allocation. Compile passed; 20k q17/shopper smokes matched heap,
  explicit checked, and inferred checked checksum/output. The 20M active-16 L2 gate is
  under `/Users/siyaoliu/rift/cache/broom-inferred-q17-shopper-20m-l2-20260520`:
  q17 explicit/inferred checked both allocate `29150680` region objects with
  zero timed GC, inferred `2905.336 ms` versus explicit `2837.754 ms`;
  shopper explicit/inferred both allocate `22857035` region objects, inferred
  `3992.605 ms` versus explicit `3998.612 ms`. L4 under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260520-broom-inferred-q17-shopper`
  shows the same bucket shape as explicit checked, so this is accepted as
  ReML-style source-placement evidence, not as a speed optimization.
- Narrow closure-body inference slice:
  GenNIR now records the checked owner symbol as well as the runtime owner value
  for region-owned closures whose expected type names exactly one captured owner
  present in the closure environment. A region-owned closure may therefore
  explicitly capture that same checked owner term and use it inside the lambda
  body for ordinary `new`, e.g. `val owner = region; val box: Box^{owner} =
  new Box(value)`. The allowance is deliberately narrow: closure captures still
  reject unrooted heap metadata, and body allocation is only accepted when the
  closure has a runtime owner handle. Later validation gates extended this
  coverage without weakening the closure-capture boundary.

Current interpretation:

- Broom retained rows remain the cleanest allocation/reclaim methodology
  profiles: heap pays allocator/GC metadata and checked Rift pays region
  allocation/init. The latest audit/cleanup removes the q17/shopper
  outer-loop `LongRef`/`IntRef` callback source-shape markers, so deeper Broom
  claims should now focus on generated query body, allocation/init, and
  constructor/no-zero evidence rather than residual heap placement. The
  q17/shopper inferred source-placement expansion proves the ordinary-`new`
  source form for the retained records but does not reduce those remaining
  buckets.
- Real streaming rows are often input/parser/hash dominated. For these rows,
  shared byte-line parsing/hashing improvements are valid fairness cleanups,
  but they are not Rift-specific memory-management wins.
- DSPBench post-scratch profiles still show heap allocation/init and metadata
  samples, but the split profile shows they are shared input/runtime costs:
  Fraud checked/heap heap-allocation samples are `140.60/136.40` per second,
  and Log checked/heap are `126.60/113.60`. This is not a checked-Rift-specific
  residual allocation issue.
- The polymorphic `Option[A^{r}]^{r}`/`Some(value)`,
  `Option[A^{r}]^{r}`/`Option(value)`, and
  `Tuple2[A^{r}, B^{r}]^{r}` factory proofs, plus a forwarded
  `wrap[A](using r)(value: A^{r}) = make[A](using r)(value)` generic `Cell`
  proof, now cover more high-frequency synthetic/allocation-summary shapes on
  the existing explicit-owner method-summary path. True type-parameter branch
  and match wrappers are also covered for polymorphic `Option.apply` and
  `Tuple2` method summaries. Closure-body allocation now has one accepted
  explicit-owner-capture case, but hidden owner capture/lambda signature
  rewriting and escaping closure effect summaries remain open. The next likely
  general targets are compiler support for inlineable checked region-body
  callbacks without losing capture tracking, object construction/init where
  proof is available, and remaining synthetic shapes that still show up in
  checked rows. StreamFlex capsule/query work is now a real operator-work floor
  unless a reusable API changes the representation.

## Latest Validation

- Current validation gate for the active compiler/runtime/inference tree passed
  on 2026-05-21 19:28-19:30 CEST:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  reported `565/565`;
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/clean" "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  reported `247/247`;
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed. The earlier
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" "set Compile / scalacOptions += \"-P:scalanative:riftInferReport\"" compile`
  gate passed after the stream-rank closure slice and was not rerun for this
  closure-body branch/match forwarded-callee summary proof slice. This is the current
  safety/allocation-stat/sandbox compile evidence
  after adding compiler positives/negatives and runtime allocation-stat proof
  for selected immutable aliases of ordinary direct allocations through method
  returns, owner-token method arguments, `RegionList`/`ObjectBuffer`/
  `RegionBuffer` owner-token framework calls, and checked priority-queue
  `push`/`put` calls; selected immutable aliases of `Some(new T(...))`,
  `Option(new T(...))`, and `Tuple2(new A(...), new B(...))` factory locals
  returned from explicit-owner methods or passed to owner-token method
  arguments; selected immutable aliases of `Some(new T(...))`,
  `Option(new T(...))`, and `Tuple2(new A(...), new B(...))` factory locals
  stored into region-owned array elements or appended to checked
  `ObjectBuffer`/`RegionBuffer` containers whose element bound now accepts
  captured object types, and pushed/put into checked priority queues whose
  element bounds now also accept captured object types, including the
  lexicographic `RegionIndexedPriorityQueue` and
  `RegionLongIndexedPriorityQueue` overloads; selected immutable aliases of
  `Some(new T(...))`, `Option(new T(...))`, and
  `Tuple2(new A(...), new B(...))` passed through checked stream-window
  rank/table-rank APIs (`putWindowRank`, `putWindowRankInBucket`, and
  `putTableRankInBucket`) whose element bounds now accept captured object
  types; branch-local and match-local ordinary direct allocations passed
  through the same checked stream-window rank/table-rank APIs while direct
  local heap-looking rank/table values remain rejected; direct branch/match
  `Some(new T(...))`, `Option(new T(...))`, and
  `Tuple2(new A(...), new B(...))` factory expressions passed through
  explicit owner-token method arguments, checked `ObjectBuffer`/`RegionBuffer`
  appends, ordinary checked priority-queue push/put calls, dense/long
  lexicographic priority-queue put overloads, and checked stream-window
  rank/table-rank APIs while unrooted heap metadata remains rejected;
  checked `RegionList` prepend now accepts captured node element types
  (`T <: RegionListNode^`) and branch/match-created list nodes whose direct
  constructor arguments contain `Some(new T(...))`, `Option(new T(...))`, or
  `Tuple2(new A(...), new B(...))`, while nested unrooted heap metadata is
  recursively rejected; checked `RegionList` node constructors can now also
  consume selected local aliases of those synthetic factories in constructor
  fields when the alias selects multiple allocation candidates, while simple
  heap-object aliases such as `val tag = metadata` remain rejected; plus
  direct, local, branch, match, owner-token selected-alias, and
  method-returned selected-alias closure-body shapes where
  a region-owned closure explicitly captures the same checked owner term and
  allocates a returned body-local object through that owner; and direct inline
  or selected immutable local closure objects stored into region-owned array
  elements, checked buffers, and ordinary `RegionPriorityQueue` owner-token
  APIs, including priority-queue closure-body allocation when the pushed
  closure captures the same runtime owner; plus direct inline and selected
  immutable local closures nested inside a region-owned wrapper constructor
  or method-returned `Some` wrapper whose closure body allocates through the
  same captured runtime owner, plus direct `new Wrapper(closure)` values passed
  through explicit owner-token method arguments; plus region-owned closure
  bodies that call explicit checked-region methods such as
  `build(value)(using owner): T^{owner}` and return that callee-allocated
  region value, including a simple forwarding wrapper
  `forward(value)(using owner) = build(value)(using owner)` and branch/match
  forwarding wrappers where every path forwards the same checked owner. The
  negative tests reject unrooted
  heap metadata through the same shapes; broader
  closure-body/effect inference remains future work. A follow-up owner-token
  container slice now also places inline and selected immutable local closure
  objects consumed by checked `ObjectBuffer`, `RegionBuffer`, and ordinary
  `RegionPriorityQueue` owner-token APIs; compiler negatives reject unrooted
  heap captures, and runtime allocation stats prove the materialized closure
  objects are checked-region allocations. The latest stream-rank follow-up now
  proves the same closure-object placement at checked stream-window rank and
  table-rank APIs (`putWindowRank`, `putWindowRankInBucket`, and
  `putTableRankInBucket`): inline and selected immutable local closure values
  are region allocated when the value type carries the stream owner, while
  unrooted heap captures are rejected. The newest method-array validation
  follow-up adds direct runtime allocation-stat proof for match-forwarded
  method-returned region-owned arrays, closing the earlier branch-only runtime
  proof gap. The owner-token array-argument follow-up fixes the lowered
  `new Array` path for captured method arguments:
  `consume(using r)(new Array[T^{r}](...))` now carries the supplied checked
  owner through GenNIR, and runtime stats prove the array plus inline stored
  region values allocate in checked region memory. The newest checked
  framework follow-up extends the same source-span owner bridge to
  `ObjectBuffer` and `RegionBuffer` direct array appends, records checked-buffer
  `get` results as owner-region values for later stores, and preserves array
  element-owner proof when the recovered array element type is region captured.
  Runtime stats prove the appended direct arrays and inline stored region values
  allocate in checked region memory; unrooted heap stores through recovered
  arrays remain rejected. No L1/L2 elapsed or L4 bucket reduction is claimed
  for these direct-array proof slices. The latest epoch-fold child-region
  follow-up adds ordinary `new` placement under `epochFoldRegionFor`, proves
  the records allocate in checked region memory, and preserves the unrooted
  metadata rejection; it is also a capability proof, not an elapsed/profile
  claim.
- Existing open-handle no-zero proof now has direct runtime allocation-stat
  coverage for inferred ordinary `new`: `epochOpenHandle` allocates a
  definitely initialized reference-field record and its metadata through the
  inferred checked owner, with `zeroSkipped >= 2` and `zeroed == 0`. This proves
  the current `RiftOpenStreamingHandle` no-zero path reaches ordinary
  inference-produced class allocations, including non-null region-local
  reference fields.
- A broader attempt to add late-lowered virtual no-zero methods for checked
  scoped/open-region owners was rejected during validation: those methods were
  introduced after reachability/linking, so the generated method tables did not
  contain them and the runtime crashed. Future checked-region no-zero expansion
  must use an already reachable call target, a direct raw-handle lowering, or a
  linker-aware NIR design; do not reintroduce the late virtual-method approach.
- Option inference coverage:
  `None` is now validated as the static empty value for
  `Option[T^{region}]^{region}` without allocating region objects, and
  `if flag then Some(new T(...)) else None` is validated for local captured
  expected types plus explicit-region-parameter method results. Runtime
  allocation stats prove that the `Some` branch and payload are region
  allocated while the `None` branch contributes no region allocation. Compiler
  negatives reject `Some(unrootedHeapMetadata)` through the same optional flow.
  `Option(new T(...))` is now lowered as a null-preserving branch: the
  non-null path allocates a checked-region `Some` plus nested payload, while
  `Option(null)` returns the static `None` value and allocates no region
  object. The same `Option.apply(new T(...))` direct-construction path is now
  runtime-proven for owner-token method arguments and region-owned array
  element stores. Negatives keep `Option(unrootedHeapMetadata)` and
  `Option(primitive)` boxed paths rejected. This expands the narrow ordinary
  `Option.apply` source shape without claiming broader Option container/effect
  inference.
- Primitive/boxed tuple-field boundary:
  `Tuple2[Int, T^{region}]^{region}`, owner-token
  `consume(using region)(Tuple2(40, new T(...)))`, and explicit-region
  method-returned `Tuple2[Int, T^{r}]^{r}` remain rejected today because the
  primitive field is erased through boxing and the `Op.Box` path has no checked
  allocation zone. New compiler negatives also prove that adding a primitive
  literal does not allow unrooted heap metadata and that a preboxed `Any` value
  cannot enter a region tuple without `HeapRoot`. This is an enforced heap
  fallback/safety result, not a new placement optimization.
- Recent inference slice:
  checked owner-token container boundaries now reuse the closure owner proof
  path for `ObjectBuffer`, `RegionBuffer`, and ordinary `RegionPriorityQueue`
  value arguments. Inline closures such as
  `RiftRegion.append(region, buffer, (n: Int) => n + 40)` and selected
  immutable local closure aliases such as
  `val selected = if flag then first else second; region.append(buffer, selected)`
  inherit the supplied checked owner at those framework boundaries. Runtime
  allocation stats prove ObjectBuffer inline closure placement, RegionBuffer
  selected closure placement, and priority-queue inline closure placement; new
  compiler negatives reject unrooted heap metadata captures. This is
  closure-object placement at explicit owner-token stores, not broad
  closure/effect inference or hidden owner capture.
- Previous inference slice:
  internal `resetOpenHandleInline` is now validated for simple and
  non-inline-wrapper open-handle reset bodies, including region-owned arrays.
  Runtime allocation stats prove that the objects and arrays allocated in the
  inline body still land in the checked region. Guard tests record the current
  limits: enclosing `inline def` wrappers lose the open-handle owner capture,
  while later branch/match-final inference now covers mixed runtime branches
  between inferred `new` and explicit allocation when both sides share the same
  checked owner. Fresh validation passed with compiler `337/337`, runtime
  `158/158`, and sandbox compile on 2026-05-20 14:51 CEST, plus the 1M
  Wikimedia session L2 follow-up for the split inferred path.
- Previous inference slice:
  inline `Tuple2(new A(...), new B(...))` stores into region-owned array
  elements are now validated for
  `items(i) = Tuple2(new A(...), new B(...))` when `items` has type
  `Array[Tuple2[A^{region}, B^{region}]^{region}]^{region}`. Runtime
  allocation stats prove the array, stored `Tuple2`, and both nested payloads
  are region allocated, while `Tuple2(metadata, metadata)` with unrooted heap
  metadata is rejected. Validation passed with compiler `328/328`, runtime
  `153/153`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  inline generic `Cell(new T(...))` objects passed to owner-token method
  arguments are now validated for the shape
  `def consume(using r: RiftRegion.ScopedRegion^)(cell: Cell[T^{r}]^{r}); consume(using region)(new Cell(new T(...)))`.
  Runtime allocation stats prove both the generic `Cell` object and nested
  payload are region allocated. Compiler negatives reject unrooted heap
  payloads such as `new Cell(metadata)` and reject generic hiding/heap escape
  through widened `AnyRef`. Validation passed with compiler `326/326`,
  runtime `152/152`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Newest inference slice:
  inline `Tuple2(new A(...), new B(...))` factory objects passed to
  owner-token method arguments are now validated for the shape
  `def consume(using r: RiftRegion.ScopedRegion^)(pair: Tuple2[A^{r}, B^{r}]^{r}); consume(using region)(Tuple2(new A(...), new B(...)))`.
  Tuple literal syntax is covered by the same compiler path. Runtime
  allocation stats prove the `Tuple2` object and both nested payloads are
  region allocated, and compiler negatives reject unrooted heap payloads such
  as `Tuple2(metadata, metadata)`. Validation passed with compiler `323/323`,
  runtime `151/151`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  inline `Some(new T(...))` factory objects passed to owner-token method
  arguments are now validated for the shape
  `def consume(using r: RiftRegion.ScopedRegion^)(option: Option[T^{r}]^{r}); consume(using region)(Some(new T(...)))`.
  The previously implemented owner-token call-site substitution and nested
  factory attachment now have direct compiler/runtime coverage: runtime
  allocation stats prove both the `Some` object and nested payload are region
  allocated, and compiler negatives reject unrooted heap payloads such as
  `Some(metadata)`. Validation passed with compiler `320/320`, runtime
  `150/150`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  inline closure objects passed to owner-token method arguments are now
  validated for the narrow call-site shape
  `def consume(using r: RiftRegion.ScopedRegion^)(f: Function1[Int, Int]^{r}); consume(using region)((n: Int) => n + 40)`.
  The same fully applied call-site owner substitution used by direct
  constructor arguments now attaches the checked owner to the closure object.
  Runtime allocation stats prove the inline closure object is region
  allocated, and compiler negatives reject unrooted heap metadata captures in
  the inferred closure argument. This still does not place arbitrary
  closure-body allocations. Validation passed with compiler `318/318`,
  runtime `149/149`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  owner-token method argument inference is now validated for the narrow valid
  call-site shape
  `def consume(using r: RiftRegion.ScopedRegion^)(x: T^{r}); consume(using region)(new T(...))`.
  The inference phase flattens fully applied curried calls and substitutes the
  callee owner parameter `r` with the actual checked owner argument `region`.
  Runtime allocation stats prove the inline argument object is region
  allocated, and compiler negatives reject unrooted dynamic heap metadata in
  the inferred argument object. Validation passed with compiler `316/316`,
  runtime `148/148`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  inline direct method arguments are now validated for the narrow call-site
  shape `def consume(x: T^{region}); consume(new T(...))`, where the parameter
  type names an in-scope checked owner. Runtime allocation stats prove the
  argument object is region allocated, and compiler negatives reject unrooted
  heap metadata in the inferred argument object. Owner-token argument mapping
  is covered by the newer slice above. Validation passed with compiler
  `314/314`, runtime `147/147`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  inline synthetic `Some(new T(...))` stores into region-owned array elements
  are now validated for `items(i) = Some(new T(...))` when `items` has type
  `Array[Option[T^{region}]^{region}]^{region}`. Runtime allocation stats
  prove the array, stored `Some`, and nested value are region allocated, while
  `Some(metadata)` with unrooted heap metadata is rejected. Validation passed
  with compiler `312/312`, runtime `146/146`, sandbox compile, and sandbox
  compile with `-P:scalanative:riftInferReport`.
- Previous inference slice:
  inline direct construction into region-owned array elements is now
  validated for `items(i) = new T(...)` when `items` has type
  `Array[T^{region}]^{region}`. The inference uses the array element owner,
  not just the array object's owner, so heap-looking element arrays such as
  `Array[Metadata]^{region}` still reject inline `new Metadata(...)` stores.
  Runtime allocation stats prove the array plus inline stored values are
  region allocated. Validation passed with compiler `310/310`, runtime
  `145/145`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  branch/match forwarded method-returned generic `Cell[A]` allocation is now
  validated. Wrapper methods can return branch or match expressions whose
  paths all forward a method-returned `Cell[T^{r}]^{r}` produced by
  `new Cell[T^{r}](value)`. Runtime allocation stats prove the selected
  generic cells and contained region-local values remain region allocated, and
  compiler negatives reject unrooted heap metadata plus heap/static retention
  through the forwarded generic path. Validation passed with compiler
  `308/308`, runtime `144/144`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  branch/match forwarded method-returned `Tuple2(...)` factory allocation is
  now validated. Wrapper methods can return branch or match expressions whose
  paths all forward a method-returned `Tuple2[A^{r}, B^{r}]^{r}` produced by
  `Tuple2(new A(...), new B(...))`. Runtime allocation stats prove the
  selected tuple objects and nested region-local values remain region
  allocated, and compiler negatives reject unrooted heap metadata plus
  heap/static retention through the branch/match wrapper path. Validation
  passed with compiler `304/304`, runtime `143/143`, sandbox compile, and
  sandbox compile with `-P:scalanative:riftInferReport`.
- Previous inference slice:
  branch/match forwarded method-returned `Option = Some(...)` factory
  allocation is now validated. Wrapper methods can return
  `if flag then make(using r) else make(using r)` or a simple match whose
  cases all forward a method-returned `Option[T^{r}]^{r}` produced by
  `Some(new T(...))`. Runtime allocation stats prove the selected `Some`
  objects and nested region-local values remain region allocated, and compiler
  negatives reject unrooted heap metadata plus heap/static retention through
  the branch/match wrapper path. Validation passed with compiler `300/300`,
  runtime `142/142`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  branch/match forwarded method-returned region-owned arrays are now
  validated. Wrapper methods can return
  `if flag then make(using r) else make(using r)` or a simple match whose
  cases all forward `make(using r)`, while preserving `Array[T^{r}]^{r}`
  ownership. This extends the previous direct/local-alias wrapper slice.
  Runtime allocation stats prove the selected array and named region-local
  element objects remain region allocated, and compiler negatives reject
  unrooted heap-object stores plus heap/static retention through the
  branch/match wrapper path. Validation passed with compiler `296/296`,
  runtime `141/141`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  forwarded method-returned region-owned arrays are validated for direct
  wrapper and one immutable method-local alias wrapper forms, preserving
  `Array[T^{r}]^{r}` ownership and runtime-proven region allocation for the
  forwarded array and named region-local element objects.
- Previous inference slice:
  method-returned region-owned arrays are now validated. A method with an
  explicit checked region parameter can return a named
  `Array[T^{r}]^{r}` allocated with ordinary `new Array[...]`, with named
  `T^{r}` element objects stored into it. Runtime allocation stats prove the
  returned array and element objects are region allocated, while compiler
  negatives reject unrooted heap-object stores and heap/static retention of the
  returned array. The validation set now passes compiler `288/288`, runtime
  `139/139`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  captured region-owned arrays are now validated for the first local
  expected-type shape. Code can write
  `val items: Array[T^{region}]^{region} = new Array[T^{region}](n)`;
  compiler positives accept storing named `T^{region}` values and storing the
  array in a region-owned object, while compiler negatives reject unrooted heap
  stores and heap/static escape. Runtime allocation stats prove the inferred
  arrays and named region-local elements are actually region allocated. The
  validation set now passes compiler `285/285`, runtime `138/138`, sandbox
  compile, and sandbox compile with `-P:scalanative:riftInferReport`. Inline
  `items(i) = new T(...)` remains deliberately rejected unless the stored value
  is first proven region-local.
- Previous inference slice:
  method-returned closure objects through immutable checked owner aliases are
  now validated. A method can use `val owner = r`, allocate a captured record
  as `T^{owner}`, construct a closure as `Function1[Int, Int]^{owner}`, and
  return it as `Function1[Int, Int]^{r}`; the inference summary canonicalizes
  the local owner alias back to the explicit checked region parameter. Runtime
  allocation stats prove both the alias-owned captured value and closure object
  are region allocated, and a compiler negative rejects unrooted heap metadata
  captures through the alias. Validation passed with compiler `281/281`,
  runtime `137/137`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`.
- Previous inference slice:
  forwarded method-returned closures that capture a region-local value are now
  validated through both direct wrapper and immutable method-local alias
  wrapper shapes, plus branch and match wrappers. A wrapper method
  `def wrap(using r): Function1[Int, Int]^{r} = make(using r)` preserves the
  inferred closure-return summary from `make`, and
  `def wrap(using r): Function1[Int, Int]^{r} = { val f = make(using r); f }`
  preserves the same summary through one immutable local. Runtime allocation
  stats prove both the original captured value and closure object are still
  region allocated after forwarding. The same result is validated for
  `if flag then make(using r) else make(using r)` and for a two-arm match
  wrapper when every path forwards the same explicit checked owner. Compiler
  negatives reject direct, local-alias, branch, and match forwarded shapes when
  the closure captures unrooted heap metadata. Validation passed with compiler
  `279/279`, runtime `136/136`, sandbox compile, and sandbox
  compile with `-P:scalanative:riftInferReport`. Primitive boxing was checked
  as a possible next synthetic allocation target, but it is deferred because
  NIR `Op.Box(ty, obj)` currently has no allocation-zone operand.
- Previous inference slice:
  method-returned closures that capture a region-local value are now
  validated. A method with an explicit checked region parameter can construct
  a region-local value, return a local `Function1[Int, Int]^{r}` closure that
  captures it, and runtime allocation stats prove both the captured value and
  closure object are region allocated. Validation passed with compiler
  `271/271`, runtime `132/132`, sandbox compile, and sandbox compile with
  `-P:scalanative:riftInferReport`. This is still closure-object placement;
  closure-body allocation remains deferred until a runtime owner handle can be
  passed or synthesized safely for the generated lambda body.
- Previous inference slice:
  method-returned capture-free closure objects are now validated. A method with
  an explicit checked region parameter can return a local
  `Function1[Int, Int]^{r}` closure object, runtime allocation stats prove the
  materialized closure object is region allocated, and a compiler negative
  rejects unrooted heap metadata captures in that returned-closure path.
  Validation passed with compiler `270/270`, runtime `131/131`, sandbox
  compile, and sandbox compile with `-P:scalanative:riftInferReport`.
  Closure-body allocation remains deferred.
- Previous inference slice:
  immutable checked owner aliases are now canonicalized. Code of the form
  `val owner = region; val leaf: T^{owner} = new T(...)` is accepted as a
  checked owner constraint, and method summaries can now reconcile
  `T^{owner}` locals with `T^{r}` result types when `owner` aliases `r`.
  Compiler negatives reject unrooted dynamic heap metadata through both the
  local alias and method-returned alias paths, and runtime allocation stats
  prove the objects are actually region allocated. Validation passed with
  compiler `268/268`, runtime `130/130`, sandbox compile, and sandbox compile
  with `-P:scalanative:riftInferReport`. A closure-body allocation experiment
  was investigated but not promoted: diagnostics can mark a body-local `new`
  from a captured type, but the generated lambda body lacks a runtime region
  handle unless Rift passes/synthesizes a hidden owner handle or rewrites the
  lambda signature safely.
- Region-inference lineage note:
  `docs/REGION_INFERENCE_LINEAGE.md` now records the investigation/evaluation
  boundary for the Tofte/Talpin -> MLKit -> ReML lineage. Rift is described as
  ReML/MLKit-inspired, but currently implemented as explicit checked lifetime
  topology plus capture/separation safety plus selective compiler placement
  lowering. The document also records what is borrowed directly, what should
  not be copied mechanically into Scala, what is implemented now, what is not
  implemented, and the staged roadmap toward method/closure effect summaries
  and broader automatic placement. The explicit long-term optimization goal is
  to reproduce ReML/MLKit-style automatic region inference as far as Scala
  Native allows: remove accidental heap allocations, make hot checked region
  paths monomorphic and inlineable, reduce operator-owned token/handle
  plumbing, improve proven region-local construction/init paths, and remove
  runtime bookkeeping only under capture/separation proof.
- ReML-style placement inference:
  `scala-native-rift/nscplugin` now has a pre-NIR
  `RiftRegionInference` phase. It marks direct `new T(...)` sites whose
  expected type is captured by an explicit checked `ScopedRegion` or
  `OpenStreamingRegion`; GenNIR lowers those marked sites into the matching
  Rift allocation zone. Parent `StreamingRegion` captures are intentionally
  excluded in v1 because page/window operators need child-bucket placement, not
  just parent-stream placement. The M1 local-inference slice now handles
  immutable local direct `new` values constrained by captured val definitions,
  captured assignments, or checked `RegionList` prepend calls. The inference
  and lowering path now also handles local block-shaped RHS values whose final
  expression is a direct `new`, for example
  `val x: T^{region} = { val n = ...; new T(n) }` and the captured-val
  variant `val x = { ...; new T(...) }; val y: T^{region} = x`. Captured
  assignments from the same block-shaped RHS form are now covered too.
  The inference
  core records `Region`, `Unknown`, and `Rejected` decisions, exposed through
  opt-in `-P:scalanative:riftInferReport`. Generic `ObjectBuffer` append
  remains explicit for now so dynamic heap metadata still requires `HeapRoot`.
  The next method-summary slice now handles direct `new` returned from a local
  method when the method has an explicit runtime checked region parameter,
  e.g. `def make(using r: RiftRegion.ScopedRegion^): T^{r} = new T(...)`.
  The same slice also handles the returned-local block form
  `def make(using r: RiftRegion.ScopedRegion^): T^{r} = { val x = new T(...); x }`.
  Returned-local method inference is validated for both checked scoped regions
  and direct epoch/open-streaming regions. The returned-local method form now
  also accepts a method-local block-shaped RHS whose final expression is a
  direct allocation:
  `def make(using r): T^{r} = { val x = { ...; new T(...) }; x }`.
  Simple branch-returned direct allocation is also covered:
  `def make(using r: RiftRegion.ScopedRegion^): T^{r} = if p then new T(...) else new T(...)`.
  The branch-returned local form is now covered too:
  `def make(using r: RiftRegion.ScopedRegion^): T^{r} = if p then { val x = new T(...); x } else { val y = new T(...); y }`.
  Match-returned direct and local allocation forms are now covered under the
  same rule:
  `selector match { case 0 => new T(...); case _ => new T(...) }` and
  `selector match { case 0 => { val x = new T(...); x }; case _ => ... }`.
  Branch- and match-returned local forms now also accept block-shaped local
  RHS construction whose final expression is a direct allocation, for example
  `if p then { val x = { ...; new T(...) }; x } else ...`.
  Method bodies whose final expression is a direct `new` in a non-empty block
  are also covered:
  `def make(using r: RiftRegion.ScopedRegion^): T^{r} = { val n = ...; new T(n) }`.
  Method-summary forwarding is now covered for the first wrapper shape:
  `def wrap(using r: RiftRegion.ScopedRegion^): T^{r} = make(using r)`,
  where `make` is already inferred as region-returning and `wrap` has its own
  explicit checked region parameter.
  The same forwarding slice now covers the common local-alias wrapper shape:
  `def wrap(using r: RiftRegion.ScopedRegion^): T^{r} = { val x = make(using r); x }`.
  Forwarded calls through simple branch and match wrappers are now validated
  too:
  `if p then make(using r) else make(using r)` and
  `selector match { case _ => make(using r) }`.
  Method summaries now also carry captured `Some(...)` and `Tuple2(...)`
  factory results when the method has an explicit checked region parameter,
  including nested direct value construction inside the factory call.
  Helpers whose captured return type only mentions an outer region remain heap
  fallback for now because the generated method body has no runtime region
  handle. The next framework-boundary slice also infers immutable local
  direct `new` values at explicit owner-token buffer append calls:
  `RiftRegion.append(region, buffer, x)` for checked `ObjectBuffer` and
  `RegionBuffer`; the same rule now covers extension syntax
  `region.append(buffer, x)`. RegionList, ObjectBuffer, and RegionBuffer
  owner-token calls now also infer block-shaped local RHS values whose final
  expression is a direct allocation. The next framework-boundary slice now also covers scoped
  checked priority-queue owner-token calls: immutable local direct `new`
  values passed to `RegionPriorityQueue.push`,
  `RegionIndexedPriorityQueue.put`, or `RegionLongIndexedPriorityQueue.put`
  are inferred into the explicit owner region when the push/put call carries
  the checked owner token. This is validated by runtime allocation stats, not
  only by compiler acceptance. The newest small owner-token slice also covers
  inline direct and block-final construction at checked list/fixed-buffer/
  growable-buffer boundaries:
  `prependRegionList(region, list, new T(...))`,
  `prependRegionList(region, list, { ...; new T(...) })`,
  `RiftRegion.append(region, buffer, new T(...))`,
  `region.append(buffer, { ...; new T(...) })`, and scoped checked
  priority-queue `push`/`put` calls with `new T(...)` or
  `{ ...; new T(...) }` value arguments.
  Runtime allocation stats prove the inline forms are region allocated, and
  compiler negatives reject unrooted dynamic heap metadata in the direct or
  block-final constructor arguments.
  The first page/window/transaction child-owner slice is now validated too: a
  local child region returned by `pageTokenAppendRegionFor`,
  `pageTokenMapFilterRegionFor`, `pageTokenCountByKeyRegionFor`,
  `transactionRegionFor`, or `chunkAppendRegionFor` can own
  `val event: Event^{region} = new Event(...)`, so bucket-local and
  transaction-local records can use ordinary `new` without treating the parent
  `StreamingRegion` as a generic allocation owner.
  The next open-child-owner slice is now validated for operator-owned active
  helpers too: `pageTokenAppendOpenRegionFor`,
  `pageTokenMapFilterOpenRegionFor`, `pageTokenCountByKeyOpenRegionFor`, and
  `epochBufferOpenRegionFor` can own ordinary `new` placement for records typed
  as `T^{region}`, replacing explicit `allocOpen(new ...)` in those paths.
  Compiler negatives reject unrooted dynamic heap metadata through the open
  page-token helpers, and runtime allocation counters prove the page-token and
  epoch-buffer records are actually allocated in Rift region memory.
  The newest internal page-token active-handle slice validates the raw
  Rift-backed helper used by operator-owned append internals:
  `pageTokenAppendRiftOpenHandleFor` can own
  `val event: Event^{region} = new Event(...)`, runtime stats prove the event
  is allocated through the `RiftOpenStreamingHandle`, and a compiler negative
  rejects unrooted dynamic heap metadata. This reduces source plumbing for
  page-token internals without exposing the raw handle as a public API.
  The first common Scala allocation shape is now
  covered too: captured `Some(...)` factory calls are lowered into checked
  regions when the expected type is `Some[T^{region}]^{region}` or the common
  widened form `Option[T^{region}]^{region}` and the argument is safe for
  region storage; unproven `Some(...)` calls remain heap fallback. `None`
  is validated as the allocation-free empty `Option` value for narrow
  local and explicit-region-method optional-result flows, and proven
  `Option.apply(...)` now lowers to `None` for null or a checked-region
  `Some` for non-null region-safe values, including owner-token arguments and
  region-owned array stores. Captured
  `Tuple2(...)` is now covered as the second common Scala allocation shape when the expected type is
  `Tuple2[A^{region}, B^{region}]^{region}` and both fields are safe
  region-local references; normal tuple syntax `(a, b)` is validated through
  the same lowered `Tuple2` path. Primitive/boxed tuple fields remain future
  boxed-key/object-boxing work. The nested-direct-construction slice now
  attaches direct constructor/factory arguments to the same proven checked
  owner, so `new Wrapper(new T(...))`, `Some(new T(...))`, and
  `Option(new T(...))`/`Tuple2(new A(...), new B(...))` are region allocated
  end to end when the outer allocation is captured by the checked region.
  Helper-returned heap arguments remain rejected rather than retroactively
  inferred.
  A narrow ReML-style generic local object slice is now validated:
  `val cell: Cell[T^{region}]^{region} = new Cell[T^{region}](value)` is
  inferred into the checked region when the expected type and value argument
  name the same checked owner. Compiler negatives reject widened `AnyRef`
  escape and unrooted dynamic heap metadata in the generic cell; a runtime
  allocation-stat test proves the `Cell` object is actually region allocated.
  The same narrow generic slice is validated through explicit checked
  region-parameter methods: a local `make(using r): Cell[T^{r}]^{r}` factory
  can return a region-owned generic cell, with compiler negatives for heap
  escape and unrooted dynamic heap metadata.
  Returned-local generic cells are validated too: a method may name the
  `Cell[T^{r}]^{r}` in a local before returning it, and runtime stats still
  prove region allocation.
  The newest method/factory slice also covers returned local `Option`
  factories, so `def make(using r): Option[T^{r}]^{r} = { val x = Some(new T(...)); x }`
  is allocation-stat validated instead of requiring a direct returned
  `Some(...)` expression.
  The same returned-local factory slice now covers captured `Tuple2(...)`
  values, so `def make(using r): Tuple2[A^{r}, B^{r}]^{r} = { val x = Tuple2(new A(...), new B(...)); x }`
  is allocation-stat validated too.
  The first synthetic-closure object slice is now validated for nonescaping
  local closures that capture a region value: the NIR lowering can allocate
  the closure object in the same checked region as the captured value, and a
  compiler negative rejects closure objects that would also capture unrooted
  dynamic heap metadata. This is closure-object placement only; closure-body
  allocation placement, escaping closures, and broader closure effect
  summaries remain future work.
  The newest closure slice promotes capture-free local closures from compiler
  acceptance to runtime allocation proof: function capture syntax such as
  `Int ->{region} Int` is now parsed as a checked owner constraint, GenNIR can
  attach the local owner for
  `val f: Function1[Int, Int]^{region} = (n: Int) => n + 40`, runtime stats
  prove the materialized closure object is region allocated, and a compiler
  negative rejects unrooted heap metadata captures in this capture-free-owner
  path.
  Capability evidence is tracked in `evidence/RIFT_REGION_INFERENCE_MATRIX.md`.
- New inference probes:
  annotated local `new` inside `RiftRegion.scoped` and `RiftRegion.epoch`
  compiles and is treated as a known region value; local direct `new` through a
  captured val, local block-shaped RHS final `new`, or checked `RegionList`
  compiles and is region allocated;
  captured assignment inference compiles; direct-return, returned-local,
  block-final direct-return, forwarded method-return, forwarded-local-alias
  method-return, forwarded branch/match method-return, simple branch-return,
  branch-returned-local, match-return, and match-returned-local methods with
  explicit `ScopedRegion^` or `OpenStreamingRegion^` parameters compile and
  are region allocated where tested; branch/match returned-local block-shaped
  RHS construction is also covered by runtime allocation-stat tests;
  `RegionList`, `ObjectBuffer`, and `RegionBuffer` owner-token append calls,
  including extension syntax, infer immutable local direct `new` values and
  tested block-shaped RHS final `new` values; direct inline and inline
  block-final `new` arguments to checked `RegionList`, `ObjectBuffer`, and
  `RegionBuffer` owner-token calls are also region allocated and protected by
  unrooted-metadata negatives; scoped
  `RegionPriorityQueue`, `RegionIndexedPriorityQueue`, and
  `RegionLongIndexedPriorityQueue` owner-token push/put calls now infer
  immutable local direct `new` values plus direct and block-final inline `new`
  value arguments;
  page-token/transaction child-region locals returned by
  `pageTokenAppendRegionFor`, `pageTokenMapFilterRegionFor`,
  `pageTokenCountByKeyRegionFor`, `transactionRegionFor`, and
  `chunkAppendRegionFor` now infer ordinary `new` values captured by that local
  child owner, with negative tests for unrooted dynamic heap metadata;
  open child-region locals returned by `pageTokenAppendOpenRegionFor`,
  `pageTokenMapFilterOpenRegionFor`, `pageTokenCountByKeyOpenRegionFor`, and
  `epochBufferOpenRegionFor` now infer ordinary `new` values captured by that
  local active owner, with compiler negatives for unrooted dynamic heap
  metadata and runtime allocation-stat tests proving region placement;
  `pageTokenAppendRiftOpenHandleFor` now covers the internal raw
  `RiftOpenStreamingHandle` page-token append path with the same positive
  allocation-stat proof and unrooted-metadata negative;
  captured
  `Some(...)` factory calls now compile and are region allocated through exact
  `Some` and widened `Option` expected types when forced observable by runtime
  stats; captured `Option.apply(...)` now compiles and preserves
  `Option(null) == None` while region-allocating the non-null `Some` branch
  in local, method-return, owner-token argument, and array-store contexts;
  captured `Tuple2(...)` factory calls and tuple literals now compile and are
  region allocated when forced observable by runtime stats; method-returned
  captured `Some(...)`/`Option(...) = Some(...)`/`Option.apply(...)`,
  returned-local `Option = Some(...)`, `Tuple2(...)`, and returned-local
  `Tuple2(...)` factory calls now compile and are region
  allocated when forced observable by runtime stats; inline
  `new` arguments nested inside captured ordinary constructors and factories
  are also region allocated when forced observable by runtime stats; mutable
  local direct `new` is not inferred;
  helper-returned heap objects are not retroactively inferred;
  unrooted dynamic heap metadata in an inferred region allocation, including
  the method-return, block-final method-return, returned-local method,
  direct branch-return method, branch-returned-local method, direct match-return method,
  match-returned-local method, buffer-append slices, priority-queue slices, and
  captured and method-returned `Some(...)`, `Option.apply(...)`,
  widened-`Option`, and `Tuple2(...)` factory forms is rejected;
  helper-returned heap
  arguments to captured `Tuple2(...)` and region-owned direct constructors are
  also rejected;
  local generic `Cell[A]` expected-type placement is now runtime-proven and
  rejects widened `AnyRef` escape plus unrooted heap metadata; method-returned
  returned-local, and branch/match-forwarded `Cell[A]` factories have the same
  escape and metadata rejection coverage;
  inline direct `new` stores into `Array[T^{region}]^{region}` are now
  runtime-proven and still reject heap-looking element types without a checked
  element owner;
  inline `Some(new T(...))` stores into
  `Array[Option[T^{region}]^{region}]^{region}` are now runtime-proven and
  still reject unrooted heap metadata payloads; inline
  `Option(new T(...))` stores into the same region-owned array element shape
  are now runtime-proven too;
  inline `Tuple2(new A(...), new B(...))` stores into
  `Array[Tuple2[A^{region}, B^{region}]^{region}]^{region}` are now
  runtime-proven and still reject unrooted heap metadata payloads;
  inline direct `new` passed to method parameters typed as `T^{region}`,
  owner-token forms `def consume(using r)(x: T^{r})`, inline closure objects
  passed to owner-token `Function1[...]^{r}` parameters, and inline
  `Some(new T(...))` values passed to owner-token `Option[T^{r}]^{r}`
  parameters, inline `Option(new T(...))` values passed to owner-token
  `Option[T^{r}]^{r}` parameters, and inline
  `Tuple2(new A(...), new B(...))` values passed to owner-token tuple
  parameters are now runtime-proven and still reject unrooted heap metadata in
  the argument object, closure capture, `Some`/`Option.apply` payload, or tuple
  payload; inline generic `Cell(new T(...))` owner-token arguments are
  now runtime-proven too, and reject both unrooted heap payloads and widened
  `AnyRef` generic hiding/heap escape;
  local nonescaping closures that capture a region value are now runtime-proven
  as region-allocated closure objects, and unrooted heap metadata captures in
  that proven closure-object path are rejected;
  capture-free local closures with a `FunctionN...->{region}...` expected type
  are now runtime-proven as region-allocated closure objects, and unrooted heap
  metadata captures in that expected-type owner path are rejected;
  inferred region values still cannot escape
  to durable heap state. Generic checked buffers still reject helper-returned
  heap objects and require `HeapRoot` for dynamic heap metadata.
- Validation after inference slice:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed with `367/367`.
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed with `167/167`.
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" "set Compile / scalacOptions += \"-P:scalanative:riftInferReport\"" compile`
  also passed, confirming the opt-in diagnostics mode does not trip `-Werror`.
  Current L2 performance reruns for the inference track are recorded in
  `evidence/RIFT_REGION_INFERENCE_MATRIX.md` with sources under
  `/private/tmp/rift-inference-*-20260519`. The focused 5M reference-shaped
  allocation gate shows inferred scoped allocation matching explicit region
  object count/RSS/checksum and removing heap GC, but running slightly slower
  than explicit scoped allocation (`84.749 ms` versus `81.741 ms`). Broom
  retained aggregate/join at 1M confirms inferred active-handle allocation
  matches explicit checked Rift checksums/output and region object counts;
  aggregate is a near tie/slightly faster than explicit, while join is a small
  inferred-overhead row. StreamFlexDesign throughput at 1M confirms inferred
  checked epoch stream matches explicit region object count and output while
  eliminating heap GC; it is a near tie against explicit (`379.663 ms` versus
  `377.317 ms`). Real HDFS LogHub retained session at 1M confirms the same
  allocation/RSS/GC reduction versus heap, but inferred checked Rift is slower
  than explicit and slightly slower than heap (`8020.670 ms` versus heap
  `7829.601 ms`), so it is now the main profile target for inferred-path
  overhead.
  Targeted L4 profiling of LogHub HDFS session explicit versus inferred
  checked Rift now completed under `/private/tmp/rift-inference-loghub-profile-20260519-escalated`.
  Both rows have the same sampled shape: `containsAscii`, `stableHash`,
  `String.charAt`/`length`, `ByteLineReader`, and `tokenHash` dominate, while
  `scalanative_rift_region_alloc_object_fast` appears only five times in each
  sample. The inferred slowdown is therefore not currently a region allocator
  hotspot; treat this as shared parser/hash domination and continue with
  general inference/runtime work rather than a LogHub-specific rewrite.
  Full-file Wikimedia retained clickstream-session was rerun as a focused L2
  inference follow-up under
  `/private/tmp/wikimedia-full-l2-inference-20260519/summary.tsv`. Heap is
  `71819.469 ms`, GC `5671.534 ms`, RSS `2.81 GB`; explicit checked Rift is
  `70451.516 ms`, GC `0.672 ms`, region-op `71.044 ms`, RSS `130.5 MB`;
  inferred checked Rift is `70022.499 ms`, GC `0.696 ms`, region-op
  `79.254 ms`, RSS `130.5 MB`. The inferred row matches explicit checked Rift
  checksum/output and `69391942` region objects, and is `429.017 ms` faster
  than explicit checked Rift in this one-run L2 pass. It is useful full-file
  feasibility evidence, but not a report-grade median.
  The follow-up direct-array inference slice is now promoted for captured
  local arrays: `val xs: Array[T^{region}]^{region} = new Array[T^{region}](n)`
  has compiler positives, unsafe-store/escape negatives, and runtime
  allocation-stat proof. Broader array flows, including inline construction
  directly inside array stores and arrays passed through generic APIs, remain
  future method/effect-summary work.
  A ReML-style local generic `Cell[A]` placement probe has now been restored
  as a narrow expected-type slice with explicit safety tests, and the same
  shape is validated as direct and returned-local method factory results when
  the method has an explicit checked region parameter. Broader polymorphic
  generic placement remains future method/effect-summary work.
  The first page/window/transaction child-owner slice is now implemented for
  `pageTokenAppendRegionFor`, `pageTokenMapFilterRegionFor`,
  `pageTokenCountByKeyRegionFor`, `transactionRegionFor`, and
  `chunkAppendRegionFor`: a local child-region token can own ordinary `new`
  placement for records typed as `T^{region}`, and runtime allocation stats
  prove the event object lands in Rift region memory.
  The open-child-owner follow-up now covers `pageTokenAppendOpenRegionFor`,
  `pageTokenMapFilterOpenRegionFor`, `pageTokenCountByKeyOpenRegionFor`, and
  `epochBufferOpenRegionFor`: ordinary `new` records typed as `T^{region}` are
  region allocated through the active open owner, so operator-owned paths can
  remove explicit `allocOpen(new ...)` source plumbing where the owner is
  statically known.
  The previously deferred scoped priority-queue owner-token slice is now
  implemented for the `RegionPriorityQueue`, `RegionIndexedPriorityQueue`, and
  `RegionLongIndexedPriorityQueue` families. The first page-token
  child-region-local slice is validated for `pageTokenAppendRegionFor`,
  `pageTokenMapFilterRegionFor`, and `pageTokenCountByKeyRegionFor`;
  stream-window rank/table-rank placement is now covered only for selected
  local synthetic factory aliases at checked rank/table owner-token APIs.
  Broader stream-window rank/table-rank topology and page/window child-bucket
  placement remain future work because they need a separate proof that the
  chosen owner is the independently expiring child region, not just the parent
  stream.
  The first closure-object placement slice is now validated for local
  nonescaping closures that capture a region value. A later captured-owner
  closure-body slice also places a body-local returned allocation when the
  region-owned closure explicitly carries the same checked owner term. Hidden
  owner capture remains deferred: when the owner appears only in types, the
  generated lambda body still needs a safe owner-capture or signature-rewrite
  design. Capture-free expected-type closure placement, method-returned closure
  objects, and simple method-returned closure objects now support immutable
  checked owner aliases, and forwarded method-returned closure objects are
  validated through direct calls, one immutable local alias, branch wrappers,
  and match wrappers. Escaping-closure summaries remain future synthetic-closure
  owner/effect work.
- Focused inferred-allocation matrix gate:
  `ObjectAllocationLoweringMatrix` now includes
  `rift-checked-scoped-explicit` and `rift-checked-scoped-inferred`, which use
  the same checked scoped lifetime and object graph but differ in source style:
  explicit `RiftRegion.alloc(new ...)` versus ordinary inferred `new`. 20k
  smoke rows passed for both primitive and reference record shapes. Primitive:
  heap checksum `-5014597496877744147` with `0` region objects; explicit and
  inferred scoped rows both allocate `20001` region objects with matching
  checksum. Reference: heap checksum `6686416469483485743` with `0` region
  objects; explicit and inferred scoped rows both allocate `20002` region
  objects with matching checksum. This is allocation-stat proof for the
  supported inferred ordinary-`new` slice, not final performance evidence.
  Sandbox diagnostics compile with `-P:scalanative:riftInferReport` passed
  after the matrix modes were added.
  The focused gate has now been scaled to 5M primitive/reference and 10M
  reference rows with one warmup and three measured runs. At 5M primitive,
  inferred scoped allocation still places `5000001` objects in the region and
  removes timed GC, but is slower than explicit scoped allocation
  (`90.815 ms` versus `83.725 ms`) and heap (`82.463 ms`). Treat this as a
  hot-path/control result. At 5M reference, inferred scoped allocation places
  `5000002` objects in the region, matches checksum, and runs `85.566 ms`
  versus heap `327.140 ms` with `247.341 ms` median timed GC. At 10M reference,
  inferred scoped allocation places `10000002` objects in the region and runs
  `173.009 ms` versus heap `311.993 ms` with `144.468 ms` median timed GC.
  These are focused L2-style gates, not L1 headline timings; the next active
  goal step is to add/run representative benchmark rows that exercise inferred
  ordinary `new`.
- Active open-handle inference slice:
  `RiftRegionInference` now recognizes the internal
  `RiftOpenStreamingHandle` as a valid checked allocation owner. This lets
  operator-owned checked Rift paths use ordinary `new` when the expected type
  is captured by the active handle; it does not expose a new public API.
  Compiler probes for `epochOpenHandle` inferred locals, inline owner-token
  direct construction, and unrooted metadata rejection passed as part of
  `RiftRegionCheckedCompilerTest` (latest suite `248/248`). Runtime allocation-stat probes
  for both `epochOpenHandle`/`resetOpenHandle` inferred locals and inline
  owner-token construction passed as part of `RiftRegionCheckedTest`
  (latest suite `119/119`), proving actual region allocation. The latest runtime count also
  includes local and method-returned captured `Some(...)` through widened
  `Option` expected types, returned-local `Option = Some(...)` factories,
  `Tuple2(...)` factories, returned-local `Tuple2(...)` factories, normal tuple syntax, and
  the narrow local, method-returned, returned-local, and branch/match-forwarded generic `Cell[A]`
  expected-type placement slices, plus the page-token
  append/map-filter/count-by-key child-region local placement slices.
- Representative inference benchmark gate:
  `BroomRetainedDataflowMatrix` now has `checked-rift-inferred` for aggregate,
  join, q17, and shopper. It keeps the same checked Rift active-handle topology
  and query logic as `checked-rift`, but uses ordinary `new` for retained
  records/entries where the captured type proves the active owner. 20k smoke
  rows matched explicit checked Rift checksums/output and region object counts:
  aggregate `35222`, join `20002`, q17 `29293`, and shopper `22864` region
  objects. The current aggregate/join 1M gate also matched:
  aggregate heap `100.245 ms` with `13.241 ms` median timed GC, checked Rift
  `87.046 ms`, inferred checked Rift `86.895 ms`, both with `1708634` region
  objects and zero timed GC; join heap `97.076 ms` with `9.426 ms` median timed
  GC, checked Rift `87.755 ms`, inferred checked Rift `90.148 ms`, both with
  `1000020` region objects and zero timed GC. The 20M q17/shopper follow-up
  also matched region object counts and outputs; q17 inferred is slightly
  slower than explicit checked in L2, while shopper is tied. This is
  representative evidence for inferred ordinary `new`, not a claim of complete
  ReML/MLKit inference.
- Second representative inference benchmark gate:
  `LogHubRetainedSessionMatrix` now has `checked-rift-inferred` for retained
  session and retained join over the compressed HDFS source
  `tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1.tar.gz!HDFS.log`.
  The mode keeps the same active-handle checked Rift topology and query logic
  as `checked-rift`, but uses ordinary `new` for retained session/join records
  where the captured expected type proves the active
  `RiftOpenStreamingHandle` owner. 20k smoke rows matched heap and explicit
  checked Rift checksums/output and region object counts: session
  `37221` region objects, join `20002`. The current 1M HDFS session gate also
  matched: heap `7829.601 ms` with `43.508 ms` median timed GC and `185 MB`
  RSS; checked Rift `7794.832 ms` with `1831886` region objects and `42 MB`
  RSS; inferred checked Rift `8020.670 ms` with the same region object count
  and `43 MB` RSS. This is the second
  representative benchmark family for inferred ordinary `new`, but it is not
  a GC-heavy row: compressed-file parsing dominates and heap GC is below
  `1%` of elapsed. It remains a real-input source-ergonomics and RSS/GC
  reduction row, plus a profile target because inferred checked Rift is slower
  than explicit checked Rift here.
- Third representative inference benchmark gate:
  `StreamFlexDesignMatrix` now has `checked-epoch-stream-inferred` for the
  active-handle StreamFlex-style backend. It keeps the same stable heap state,
  transient period records, reset/epoch boundary, and capsule sink as
  `checked-epoch-stream`, but uses ordinary `new` for transient `Packet`,
  `Feature`, `Decision`, and `Alert` records. Sandbox compile passed after this
  change. 20k throughput smoke matched heap/explicit checksums and output;
  inferred and explicit checked rows both allocated `500013` region objects.
  The current 1M throughput gate also matched checksum/output and region
  object counts: heap `512.936 ms` with `100.127 ms` median timed GC,
  checked epoch stream `377.317 ms` with `24997627` region objects, and inferred
  checked epoch stream `379.663 ms` with the same `24997627` region objects. This
  completes the current target of three representative benchmark families for
  the active-handle inference slice. The broader ReML-style goal remains open:
  closure/body placement, broader polymorphic safety, page/window inference
  beyond explicit child-region locals, array-store safety, and regression
  profiling are still incomplete.
- LogHub/Wikimedia retained-session mutator parity fix:
  `LogHubRetainedSessionMatrix` no longer allocates a Scala tuple per parsed
  line. The parser now writes key/value/hash into one reusable scratch object
  and precomputes the clickstream-vs-log parser branch per run. This removes an
  accidental per-record heap allocation from heap, checked Rift, and checked
  scoped rows without changing query semantics.
- Validation after that fix:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed. 20k compressed HDFS retained-session smoke passed for `heap-gc`,
  `checked-rift`, and `checked-region-scoped` with matching checksum
  `8111821357966847529` and output `19260`. 20k retained-join smoke passed for
  the same modes with matching checksum `-1607483374812565358` and output `0`.
- DSPBench file-backed parser mutator-parity fix:
  `DSPBenchRegionMatrix` no longer returns `(Int, Int, Long)` or
  `(Int, Int, Int, Int, Long)` from its file-backed parsers. Sensor, Fraud, and
  common-log parsers now write into reusable scratch records. This removes
  another accidental parser-side heap allocation shared by heap and checked
  rows.
- Validation after the DSPBench parser fix:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed. 20k compressed DSPBench smoke passed for `fraud-q2-alert-window` and
  `log-q2-window`, modes `heap-immix` and
  `rift-checked-safezone-page-token`, with matching checksums/output:
  Fraud checksum `-1399594498030869762`, output `98`; Log checksum
  `2172779649197205352`, output `5`.
- Portable prototype standalone compile:
  `scalac -d /tmp/portable-rift-classes experimental/portable-rift/src/main/scala/rift/portable/PortableRiftBackendPrototype.scala`
  passed.
- Portable prototype smoke:
  `scala run --server=false ... --main-class rift.portable.PortableRiftBackendPrototype`
  passed.
- Native sandbox compile after extraction:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- Native sandbox compile after q17:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- Native sandbox compile after archive-wide LogHub input support:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- Native sandbox compile after Yak `YAK_GRAPH_INPUT_MODE=streaming-file`:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- Broom q17 20M active-16: checked Rift `9.67 s`, `49.9 MB`, zero timed GC
  versus heap `14.45 s`, `231.7 MB`, L2 GC `1370.380 ms`.
- SPECjbb/Stancu-style 8M generated transaction row: L1 heap `4.89 s`
  versus checked epoch stream `4.35 s` and checked epoch scoped `3.95 s`;
  L2 heap `1379.590 ms` with `164.932 ms` GC / `520` collections versus
  checked epoch stream `996.765 ms`, `0.515 ms` GC, and `4.075 ms` region-op.
- LogHub Spark archive-wide retained session, 1M active-16 over compressed
  `tar.gzcat:/Users/siyaoliu/rift/cache/benchmark-data/loghub/Spark.tar.gz`:
  L1 heap `27.62 s`, RSS `391 MB`; checked Rift `20.30 s`, RSS `73 MB`;
  checked scoped `19.85 s`, RSS `73 MB`. L2 heap GC is `140.639 ms` inside
  `6642.276 ms`, so this is strong real-streaming RSS/fixed-memory evidence
  but not a GC-time flagship. Heap caps pass at `256M` and fail at `128M`.
- AskUbuntu true streaming text, 5M tokens over compressed
  `7z:/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu.com.7z!Posts.xml`:
  L1 checked epoch scoped `6.23 s`, RSS `15 MB`, versus heap `6.74 s`,
  RSS `41 MB`; L2 heap GC is only `27.237 ms` inside `2109.524 ms`, so this
  remains modest RSS/fixed-memory text evidence rather than a GC-heavy row.
- Yak LiveJournal true streaming graph, 20M edges over compressed
  `/Users/siyaoliu/rift/cache/benchmark-data/yak/snap/soc-LiveJournal1.txt.gz`:
  L1 checked epoch scoped `17.15 s`, RSS `102 MB`, versus heap `18.32 s`,
  RSS `577 MB`; L2 checked epoch stream `5530.190 ms`, GC `0 ms`, region op
  `2.869 ms`, versus heap `6333.745 ms`, GC `165.387 ms`. This is strong
  real-streaming graph RSS/fixed-memory and throughput evidence, but heap GC is
  still only about `2.6%` of L2 elapsed. One-run cap probes: heap passes
  `128M` and fails `64M`; checked epoch stream/scoped pass `64M` and `32M`.
- Wikimedia enwiki retained clickstream-session, 1M rows over compressed
  `/Users/siyaoliu/rift/cache/benchmark-data/wikimedia/clickstream-enwiki-2026-03.tsv.gz`:
  L1 checked Rift `5.81 s`, RSS `138 MB`, versus heap `6.50 s`,
  RSS `784 MB`; L2 heap `2038.262 ms`, GC `150.157 ms`, while checked Rift
  is `1952.438 ms`, GC `9.237 ms`, region op `1.871 ms`. Heap caps fail even
  at `512M`; checked rows pass at `128M` and `64M`. Use this as
  real-streaming retained clickstream throughput/RSS/GC/fixed-memory evidence
  over public Wikimedia data, not an official Wikimedia benchmark artifact.
- Wikimedia retained clickstream-session 5M scale-up:
  L1 checked Rift `27.86 s`, RSS `138 MB`, versus heap `28.77 s`,
  RSS `1.54 GB`; L2 checked Rift `9486.647 ms`, GC `46.492 ms`, region op
  `10.699 ms`, versus heap `9459.416 ms`, GC `334.176 ms`, max GC
  `1066.487 ms`. Heap caps fail at `1G`, `768M`, and `512M`; checked Rift and
  checked scoped pass under a `64M` GC heap cap. Classify this as 5M
  scale-up RSS/fixed-memory and GC-tail evidence, with only a modest L1
  throughput win and essentially tied L2 loop throughput.
- Wikimedia retained clickstream-session 10M 3-run scale-up:
  L1 checked Rift `59.37 s`, RSS `138 MB`, versus heap `62.52 s`,
  RSS `1.80 GB`; L2 checked Rift `19635.995 ms`, GC `96.069 ms`, region op
  `24.329 ms`, versus heap `20103.863 ms`, GC `851.023 ms`. Heap caps fail at
  `1G`, `768M`, and `512M`; checked Rift and checked scoped pass under a
  `64M` GC heap cap. This is now report-grade real-streaming retained
  clickstream throughput/RSS/GC/fixed-memory scale-up evidence.
- Wikimedia retained clickstream-session full-file feasibility:
  one-run L1 checked Rift `69.87 s`, RSS `136 MB`, versus heap `74.23 s`,
  RSS `2.30 GB`; one-run L2 checked Rift `71149.579 ms`, GC `318.165 ms`,
  region op `79.786 ms`, versus heap `72750.014 ms`, GC `7122.811 ms`.
  This processed all `35862259` compressed rows with matching checksum/output.
  Keep the 10M x3 row as the report-grade median until the full-file row is
  repeated.
- Real-streaming evidence is now consolidated in the compact representative
  table at the top of `evidence/REAL_STREAMING_INPUT_MATRIX.md`: Theodolite
  retained UC4, LogHub Spark retained session, Wikimedia retained clickstream,
  Yak LiveJournal streaming graph, and AskUbuntu streaming text are classified
  with L1 elapsed/RSS, L2 GC/region interpretation, heap-cap status,
  checksum/output, and allowed claim.
- `docs/PERFORMANCE_EVALUATION_REPORT.md`, `docs/RIFT_EVALUATION_SUMMARY_SLIDES.md`,
  and generated `docs/report.html` include the Wikimedia scale-up in
  presentation-facing summaries, not only in the raw evidence files.
- `docs/MEMORY_MODE_TAXONOMY.md` and `docs/PERFORMANCE_EVALUATION_REPORT.md`
  now explicitly distinguish region memory lifetime from program reachability:
  summary-on-append rows allocate in a region but do not retain prior records
  for later traversal, retained epochs store objects behind an epoch-local or
  safely cleared bucket anchor, and page/window/bucket tokens are
  operator-managed dynamic child epochs.
- The presentation story is now unified around the prior-work-style contract:
  natural heap/GC program versus checked Rift with the same logical program,
  output, operator semantics, and lifetime boundary. Short-lived data-path
  objects move into checked regions; durable control state remains heap
  allocated. Same-shape heap controls, summary lower bounds, legacy checked,
  and unsafe/rootless modes stay in appendix/mechanism tables. ReML-style
  automatic placement inference is recorded as a staged Scala Native compiler
  plan: first infer `new` allocation placement inside explicit checked
  lifetimes, then framework boundary inference, then method/closure effect
  summaries.
- `evidence/UNIFIED_HEAP_RIFT_AUDIT.md` now records the benchmark-program
  audit for that model. The rule is: present one user-facing Rift system, pick
  the fastest safe checked backend for each API/topology, and treat checked
  scoped versus checked stream as backend selection. Rows where scoped beats
  stream feed the profiling/optimization queue instead of becoming a separate
  system story. The first profiling target after this cleanup is Wikimedia
  retained clickstream-session, because it removes large timed GC/RSS pressure
  but still has higher checked non-GC mutator cost.
- Wikimedia clickstream L4 profiling has now run at 10M rows for `heap-gc`,
  `checked-rift`, and `checked-region-scoped`. Artifacts live in
  `/Users/siyaoliu/rift/cache/profile-sweep-20260518-172522`. All cases
  matched checksum/output. The first-order finding is that parser/input/hash
  work dominates: TSV field hashing/int parsing, stable hashing, byte-line
  read/append, and session-loop work are the main sampled frames. Heap also
  samples Immix marker/heap-block work and has about `1.0G` sampled footprint;
  checked rows are about `127M`. Checked scoped additionally shows
  marker/root-range and small zone-allocation samples.
- The L4 profile harness now also covers the newer retained-object rows:
  Broom aggregate/join/q17/shopper, Theodolite retained UC4, and LogHub
  retained session/join. Gap-fill artifacts live in
  `/Users/siyaoliu/rift/cache/profile-sweep-20260518-gap-fill` and
  `/Users/siyaoliu/rift/cache/profile-sweep-20260518-loghub-retained-rerun`.
  Broom profiles expose the intended memory-management split: checked Rift
  pays region allocation/object initialization while heap pays allocator
  metadata, marking, sweep, and high RSS. Real streaming Theodolite/LogHub
  profiles are still dominated by input parsing, byte-line reading, numeric or
  string extraction, and hashing. This makes parser/hash improvements useful
  shared optimizations, while the Rift-specific low-level target remains
  allocation/object initialization rather than close/open bookkeeping.
- Previous checked suites also passed:
  `RiftRegionCheckedCompilerTest` `141/141`,
  `RiftRegionCheckedTest` `65/65`.

## Latest Validated Compiler Slice

- ReML-style owner-token call-site inference now accepts a narrow
  polymorphic consumer shape:
  `def consume[A](using r: ScopedRegion^)(cell: Cell[A^{r}]^{r})`.
  The bug was that polymorphic capture extraction could treat the local method
  symbol itself as a candidate owner, producing an ambiguous `consume` versus
  `region` decision and leaving the allocation on the heap. The inference pass
  now excludes method symbols from allocation-owner candidates, and NIR
  lowering recognizes type-applied constructors on the same inferred-region
  path as ordinary constructors.
- Safety coverage added: polymorphic owner-token generic `Cell` placement
  compiles; widened `AnyRef` escape is rejected; unrooted heap metadata through
  the polymorphic generic path is rejected. Runtime allocation stats prove the
  polymorphic `Cell` object and nested payload are region allocated.
- Validation at 2026-05-20 20:07-20:19 CEST:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `370/370`;
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/clean" "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `168/168`; and
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed. This is an inference capability/safety slice, not a new benchmark
  timing result.
- Follow-up ReML-style method-summary slice: local polymorphic factories of
  the shape
  `def make[A](using r: ScopedRegion^)(value: A^{r}): Cell[A^{r}]^{r}`
  now carry an inferred region-return summary. The inference pass records
  method parameters whose declared type is captured by a checked owner
  parameter, and NIR treats those recorded parameter symbols as known region
  values when constructing returned region objects. A pre-erasure call-boundary
  safety gate rejects helper-returned heap objects passed to captured method
  parameters, so unproven heap metadata still requires `HeapRoot` or another
  accepted proof.
- Validation at 2026-05-20 20:25-20:39 CEST:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `373/373`;
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/clean" "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `169/169`; and
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed. This is another compiler-placement/safety proof, not a new L1/L2
  benchmark row.
- Follow-up forwarded polymorphic method-summary proof: a wrapper
  `def wrap[A](using r: ScopedRegion^)(value: A^{r}): Cell[A^{r}]^{r} =
  make[A](using r)(value)` is now covered with compiler positives/negatives
  and runtime allocation stats. The runtime proof forces the returned `Cell`
  and payload allocations and observes at least two region objects. The helper
  metadata and widened `AnyRef` escape negatives preserve the heap fallback
  boundary. Validation passed at 2026-05-20 21:03-21:06 CEST with compiler
  `385/385`, runtime `173/173`, and `sandbox3_next` compile. No compiler
  implementation change was needed for this slice.
- Follow-up branch/match polymorphic method-summary proof: true
  type-parameter wrappers now forward polymorphic `Option.apply` and `Tuple2`
  factory summaries through simple `if` and `match` bodies when every path uses
  the same explicit checked owner. Runtime allocation stats prove the selected
  `Some`/`Tuple2` objects and payloads are region allocated; compiler
  negatives reject helper-returned heap metadata and widened `AnyRef` escape.
  Validation passed at 2026-05-20 21:13-21:15 CEST with compiler `391/391`,
  runtime `175/175`, and `sandbox3_next` compile. No compiler implementation
  change was needed for this slice.
- Follow-up method-returned closure-body inference slice: direct closures
  returned from explicit checked-owner methods can now be region allocated
  when the returned `Function1` type is captured by that owner and the closure
  explicitly captures the same owner term for a body-local returned `new`.
  Runtime allocation stats prove both the closure wrapper and the closure-body
  leaf allocate in checked region memory. Safety coverage includes a negative
  unrooted-metadata body test and a negative direct-return closure escape test
  for uncaptured `Function1` results. A full native-link ReML smoke for
  `ratio` matched heap and checked-scoped checksums. Validation passed at
  2026-05-20 22:47-22:50 CEST with compiler `396/396`, runtime `177/177`,
  `sandbox3_next` compile, and generated LLVM confirming `make$39` uses the
  region allocator for the `Lambda$192` closure wrapper. The slice also added
  a narrow internal allocator-forwarder exception so `RiftRegion.scala` can
  compile its runtime allocator wrappers without weakening user-code
  `HeapRoot`/metadata checks.
- Follow-up method-returned local-closure inference slice: immutable local
  closure values returned from explicit checked-owner methods now inherit the
  captured method result owner even when the local closure val itself has no
  explicit captured type ascription. The same captured owner enables the
  proven closure-body returned `new` case when the closure explicitly captures
  the owner term. Compiler negatives still reject unrooted heap metadata
  captured into the returned local closure body. Validation passed at
  2026-05-20 22:59-23:04 CEST with compiler `398/398`, runtime `178/178`,
  `sandbox3_next` compile, and a focused ReML `ratio` native smoke whose heap
  and checked-scoped checksums both matched `-8648687106320575011`.
- Follow-up owner-token local-closure argument inference slice: immutable
  local closure values passed to explicit checked owner-token method arguments
  now inherit the supplied owner even when the local closure val itself has no
  captured type ascription. This extends the inline closure argument path to
  the common named-local helper shape. The same captured owner enables the
  proven closure-body returned `new` case when the closure explicitly captures
  the owner term. Compiler negatives still reject unrooted heap metadata
  captured into the local closure body. Validation passed at
  2026-05-20 23:11-23:18 CEST with compiler `400/400`, runtime `179/179`,
  `sandbox3_next` compile, and a focused ReML `ratio` native smoke whose heap
  and checked-scoped checksums both matched `-8648687106320575011`.
- Follow-up owner-token branch/match-local closure argument inference slice:
  branch- or match-selected immutable local closure values passed to explicit
  checked owner-token method arguments now inherit the supplied owner as well.
  This covers `consume(using region)(if flag then first else second)` and
  matching `selector match` forms when each selected value is a local closure
  and the parameter type is captured by the owner token. Compiler negatives
  still reject unrooted heap metadata captured into any selected closure body.
  Runtime allocation stats prove the local closure wrappers and selected body
  allocations are checked-region objects. Validation passed at
  2026-05-20 23:36-23:45 CEST with compiler `404/404`, runtime `181/181`,
  `sandbox3_next` compile, and a focused ReML `ratio` native smoke whose heap
  and checked-scoped checksums both matched `-8648687106320575011`.
- Follow-up owner-token branch/match inline closure-body proof:
  direct inline closure arguments selected by `if` or `match` now have explicit
  compiler positives/negatives for the captured-owner body allocation shape,
  e.g. `consume(using region)(if flag then ((n: Int) => ...) else ...)`.
  Runtime allocation stats prove the selected closure body object is
  checked-region allocated. The direct-inline native shape observed only one
  region allocation, so this proof does not claim that a closure wrapper is
  materialized and counted when the backend can avoid it. Validation passed at
  2026-05-20 23:50-23:55 CEST with compiler `408/408`, runtime `183/183`,
  and `sandbox3_next` compile.
- Follow-up local branch/match inline closure-body proof:
  captured local expected types now use the same direct-returned-closure walk
  as method returns and owner-token arguments, so shapes such as
  `val make: Function1[...]^{region} = if flag then ... else ...` can place the explicitly
  captured-owner body allocation in the checked region. Runtime allocation
  stats prove the selected body-returned object is checked-region allocated;
  as with direct inline method arguments, wrapper allocation is not claimed
  when the native shape does not count a separately materialized wrapper. A
  selected-alias form such as `val selected = if flag then first else second`
  followed by `consume(using region)(selected)` was the next target.
  Validation passed at 2026-05-21 00:03-00:15 CEST with compiler `410/410`,
  runtime `184/184`, `sandbox3_next` compile, and a checksum-matching ReML
  `ratio` smoke.
- Follow-up selected local closure alias inference slice:
  immutable local aliases that select between already-known immutable closure
  vals now preserve the original closure allocation symbols. This covers
  `val selected = if flag then first else second; consume(using region)(selected)`
  when `first` and `second` are local closures and the owner-token parameter
  type names the supplied checked owner. Compiler negatives still reject
  unrooted heap metadata captured into either selected closure body. Runtime
  allocation stats prove both selected closure wrappers and the selected
  body-returned object are checked-region allocated. Validation passed at
  2026-05-21 00:21-00:28 CEST with compiler `412/412`, runtime `185/185`,
  `sandbox3_next` compile, and a checksum-matching ReML `ratio` smoke.
- Follow-up method-returned selected local closure alias inference slice:
  explicit checked-owner methods can now return an immutable alias selected
  between local closures, preserving the original closure allocation symbols
  through the method-return summary. This covers
  `def make(flag)(using r): Function1[...]^{r} = { val first = ...; val second = ...; val selected = if flag then first else second; selected }`
  when each local closure explicitly captures the same checked owner term for
  its body allocation. Runtime allocation stats prove the returned selected
  closure wrappers and selected body-returned object are checked-region
  allocated; compiler negatives reject unrooted heap metadata captured by
  either selected closure body. Validation passed at 2026-05-21 00:33-00:40 CEST
  with compiler `414/414`, runtime `186/186`, `sandbox3_next` compile, and a
  checksum-matching ReML `ratio` smoke.
- Follow-up closure-body/effect-summary forwarding proof:
  no production compiler change was needed for this slice; the existing
  closure alias and forwarded-method summary machinery already preserves the
  captured-owner body effect through four more shapes. New compiler positives
  cover `def wrap(using r): Function1[Int, Box^{r}]^{r} = make(using r)` when
  `make` returns a closure whose body explicitly captures `r`, and
  branch/match wrappers such as
  `if flag then make(using r) else make(using r)` and
  `selector match { case 0 => make(using r); case _ => make(using r) }`.
  The same proof covers
  `val selected = if flag then first else second; val forwarded = selected; forwarded`
  for method-returned selected local closures. The paired negatives still
  reject unrooted heap metadata captured into the closure body. Runtime
  allocation stats prove the forwarded method-returned closure wrapper plus
  body object (`delta >= 2`), branch/match forwarded closure wrapper plus body
  object (`delta >= 2`), and the forwarded selected local closure
  candidates plus selected body object (`delta >= 3`) allocate in checked
  region memory. Validation passed at 2026-05-21 14:31-14:35 CEST with compiler
  `536/536`, runtime `229/229`, and `sandbox3_next` compile. This remains a
  captured-runtime-owner proof, not hidden owner capture or broad escaping
  closure effect inference.
- Follow-up selected local direct-allocation alias inference slice:
  immutable local aliases that select between ordinary direct-allocation locals
  now preserve the original allocation symbols, matching the closure alias
  treatment for plain object records. This covers method-returned
  `val selected = if flag then first else second; selected` and owner-token
  method arguments such as `consume(using region)(selected)` when `first` and
  `second` are direct `new` locals. Runtime allocation stats prove both
  selected candidate objects are checked-region allocated; compiler negatives
  reject unrooted heap metadata stored through either candidate allocation.
  The follow-up framework proof covers `RiftRegion.prependRegionList(region,
  list, selected)`: the selected alias itself is marked as a proven region
  value once every candidate allocation has the same owner, so the framework
  store checker no longer treats it as a heap object. The latest follow-up adds
  the same compiler proof for `RiftRegion.append(region, objectBuffer,
  selected)` and `region.append(regionBuffer, selected)`, with unrooted
  metadata negatives, plus a runtime allocation-stat proof for ObjectBuffer.
  The latest follow-up covers checked priority queues too: selected local
  direct allocations now flow through `RegionPriorityQueue.push`,
  `RegionIndexedPriorityQueue.put`, and `RegionLongIndexedPriorityQueue.put`,
  with an unrooted-metadata negative and a runtime allocation-stat proof for
  the plain priority queue. Validation passed at 2026-05-21 01:30-01:38 CEST
  with compiler `426/426`, runtime `190/190`, `sandbox3_next` compile, and a
  checksum-matching ReML `ratio` smoke.
- Follow-up selected local synthetic-factory alias proof:
  the selected-alias machinery is now explicitly guarded for high-frequency
  synthetic factory shapes, not only plain object records. Compiler positives
  cover explicit-owner methods returning
  `val selected = if flag then first else second; selected` where `first` and
  `second` are local `Some(new T(...))` or
  `Tuple2(new A(...), new B(...))` factory results. Compiler negatives reject
  unrooted heap metadata through the same selected `Some` and `Tuple2` shapes.
  Runtime allocation stats prove both candidate wrappers and their nested
  payload objects allocate in checked region memory (`delta >= 10` for two
  `Some` candidates plus two `Tuple2` candidates). Validation passed at
  2026-05-21 01:46-01:53 CEST with compiler `430/430`, runtime `191/191`,
  `sandbox3_next` compile, and a checksum-matching ReML `ratio` smoke.
- Follow-up owner-token selected local synthetic-factory alias proof:
  the same selected `Some(new T(...))` and
  `Tuple2(new A(...), new B(...))` factory aliases are now covered at
  owner-token method-argument boundaries such as
  `consume(using region)(selected)`. Compiler positives and unrooted-metadata
  negatives cover both selected factory shapes, and runtime allocation stats
  prove both candidate wrappers and nested payloads allocate in checked region
  memory when the selected value is consumed by an owner-token method argument
  (`delta >= 10`). Validation passed at 2026-05-21 01:58-02:05 CEST with
  compiler `434/434`, runtime `192/192`, `sandbox3_next` compile, and a
  checksum-matching ReML `ratio` smoke.
- Follow-up array-store selected local synthetic-factory alias proof:
  selected local `Some(new T(...))`, `Option(new T(...))`, and
  `Tuple2(new A(...), new B(...))` factory aliases are now covered when stored
  into region-owned array elements. Compiler positives cover all three selected
  factory shapes, compiler negatives reject unrooted heap metadata through the
  same array-store boundary, and runtime allocation stats prove all selected
  factory wrappers plus nested direct payloads allocate in checked region
  memory (`delta >= 14`; array allocation itself is already covered by earlier
  array-placement tests). Validation passed at 2026-05-21 02:10-02:19 CEST
  with compiler `438/438`, runtime `193/193`, `sandbox3_next` compile, and a
  checksum-matching ReML `ratio` smoke.
- Follow-up selected `Option.apply` method/owner-token proof:
  selected local `Option(new T(...))` factory aliases are now explicitly
  covered for explicit-owner method returns and owner-token method arguments,
  closing the proof gap between the existing direct `Option.apply` support and
  the selected-alias `Some`/`Tuple2` method slices. Compiler positives and
  unrooted-metadata negatives cover both boundaries, and the existing runtime
  allocation-stat proofs now force selected `Some`, `Option.apply`, and
  `Tuple2` candidates with nested payloads (`delta >= 14`) for returned and
  consumed aliases. Validation passed at 2026-05-21 02:25-02:32 CEST with
  compiler `442/442`, runtime `193/193`, `sandbox3_next` compile, and a
  checksum-matching ReML `ratio` smoke across heap, inferred checked stream,
  and checked scoped rows.
- Follow-up captured-object checked buffer proof:
  `ObjectBuffer` and `RegionBuffer` element bounds now accept captured object
  types (`T <: Object^`) rather than only uncaptured `Object`, while append/get
  still require the owner-token value type `T^{owner}`. This lets checked
  framework buffers hold selected local synthetic factory values such as
  `Some(new T(...))`, `Option(new T(...))`, and
  `Tuple2(new A(...), new B(...))` when the wrapper and payload are owned by
  the same checked region. Compiler positives cover selected factory aliases
  appended to both fixed and growable checked buffers; negatives reject
  unrooted heap metadata through selected `Some`/`Option.apply`/`Tuple2`
  buffer appends and keep inner-region values from flowing into outer buffers.
  Runtime allocation stats prove the selected buffer wrappers plus nested
  payloads allocate in checked region memory (`delta >= 28`). Validation
  passed at 2026-05-21 02:45-02:51 CEST with compiler `450/450`, runtime
  `194/194`, `sandbox3_next` compile, and a checksum-matching ReML `ratio`
  smoke across heap, inferred checked stream, and checked scoped rows.
- Follow-up captured-object priority-queue proof:
  `RegionPriorityQueue`, `RegionIndexedPriorityQueue`, and
  `RegionLongIndexedPriorityQueue` element bounds now accept captured object
  types (`T <: Object^`) while push/put/peek/get/pop APIs still use explicit
  owner-token value types. Compiler positives cover selected local
  `Some(new T(...))`, `Option(new T(...))`, and
  `Tuple2(new A(...), new B(...))` factory aliases pushed or put into the
  three checked priority-queue families. Compiler negatives reject unrooted
  heap metadata through selected queue `Some`/`Option.apply`/`Tuple2` values
  and keep inner-region values from flowing into outer queues. Runtime
  allocation stats prove the selected priority-queue wrappers plus nested
  payloads allocate in checked region memory (`delta >= 14`). Validation
  passed at 2026-05-21 02:58-03:05 CEST with compiler `454/454`, runtime
  `195/195`, `sandbox3_next` compile, and a checksum-matching ReML `ratio`
  smoke across heap, inferred checked stream, and checked scoped rows.
- Follow-up lexicographic captured-object priority-queue proof:
  The dense and long-key lexicographic checked priority-queue factories and
  four-priority `put` overloads now have explicit selected-synthetic proof on
  top of the captured-object bounds. Compiler positives cover selected local
  `Some(new T(...))` and `Option(new T(...))` aliases put into
  `RegionIndexedPriorityQueueLexicographic`, plus selected local
  `Tuple2(new A(...), new B(...))` aliases put into
  `RegionLongIndexedPriorityQueueLexicographic`. Compiler negatives reject
  unrooted heap metadata through both lexicographic queue boundaries. Runtime
  allocation stats prove the selected lexicographic queue wrappers plus nested
  payloads allocate in checked region memory (`delta >= 14`). Validation
  passed at 2026-05-21 03:12-03:19 CEST with compiler `457/457`, runtime
  `196/196`, `sandbox3_next` compile, and a checksum-matching ReML `ratio`
  smoke across heap, inferred checked stream, and checked scoped rows.
- Follow-up stream-window rank/table-rank selected synthetic proof:
  `StreamWindowIndexedRank`, `StreamWindowLongIndexedRank`, and
  `StreamWindowTableRank` element bounds now accept captured object types
  (`T <: Object^`) while `putWindowRank`, `putWindowRankInBucket`, and
  `putTableRankInBucket` still constrain stored values through the checked
  stream owner token. Compiler positives cover selected local
  `Some(new T(...))`, `Option(new T(...))`, and
  `Tuple2(new A(...), new B(...))` aliases at those APIs. Compiler negatives
  reject unrooted heap metadata through the same boundaries, and the existing
  direct heap-object stream-rank negatives remain in force so parent
  `StreamingRegion` is not a generic allocation owner. Runtime allocation
  stats prove the selected rank/table wrappers plus nested payloads allocate in
  checked region memory (`delta >= 14`, measured after the stream region
  closes so per-region counters are flushed). Validation passed at
  2026-05-21 03:53-03:58 CEST with compiler `461/461`, runtime `197/197`,
  `sandbox3_next` compile, and a checksum-matching ReML `ratio` smoke across
  heap, inferred checked stream, and checked scoped rows.
- Follow-up stream-window rank/table-rank branch/match-local
  direct-allocation proof: checked stream rank/table owner-token inference now
  also handles common non-direct local-selection shapes such as
  `put...(if flag then first else second, ...)` and
  `put...(selector match { case 0 => first; case _ => second }, ...)` when
  every selected value is an immutable local direct allocation and the checked
  rank/table context supplies the stream owner token. Compiler positives cover
  `putWindowRank`, `putWindowRankInBucket`, and `putTableRankInBucket` for the
  branch form plus `putWindowRank`, `putWindowRankInBucket`, and
  `putTableRankInBucket` for match-returned local values; negatives reject
  unrooted heap metadata stored through the selected candidates. The NIR
  safety checker now treats `if`, `match`, `Return`, and Scala 3 lowered
  `Labeled` match-result expressions as known region values only when every
  returned value is known region-local, and conservatively detects
  region-captured values in branch/match expressions for heap-retention checks.
  Direct heap-looking rank/table values remain rejected. Runtime allocation
  stats prove the branch/match rank/table candidate objects allocate in
  checked region memory (`delta >= 6`). Validation passed at
  2026-05-21 04:39-04:44 CEST with compiler `468/468`, runtime `198/198`,
  `sandbox3_next` compile, and a
  checksum-matching ReML `ratio` smoke across heap, inferred checked stream,
  and checked scoped rows.
- Follow-up owner-token branch/match direct synthetic-factory proof:
  `RiftRegionInference` now walks direct branch/match returned region
  constructs at owner-token boundaries instead of only a single direct
  construct or a named selected local. This covers direct
  `if`/`match` expressions that return `Some(new T(...))`,
  `Option(new T(...))`, or `Tuple2(new A(...), new B(...))` through explicit
  owner-token method arguments, checked `ObjectBuffer`/`RegionBuffer` appends,
  ordinary checked priority-queue push/put calls, dense/long lexicographic
  priority-queue put overloads, and the checked stream-window rank/table-rank
  APIs. `NirGenExpr` now also treats attached direct synthetic
  factory apps as known region values when checking branch/match store safety,
  so mixed heap-looking branches still fall back to the existing object-buffer
  rejection while fully proven branches lower to checked region allocations.
  Compiler negatives reject unrooted heap metadata through the direct
  branch/match factory path. Runtime allocation stats prove the
  owner-token method-argument, checked buffer, ordinary checked priority-queue,
  and stream rank/table branch/match `Some`/`Option.apply`/`Tuple2` factories
  plus executed payloads allocate in checked region memory (`delta >= 7` in
  each focused proof). Validation passed at 2026-05-21 05:13-05:21 CEST with
  compiler `479/479`, runtime `202/202`, `sandbox3_next` compile, and a
  checksum-matching ReML `ratio`
  smoke across heap, inferred checked stream, and checked scoped rows. No
  elapsed or L4 bucket reduction is claimed for this inference-coverage slice.
- Follow-up RegionList branch/match nested synthetic-factory proof:
  `RegionList` now uses the same captured element bound shape as checked
  buffers and queues (`T <: RegionListNode^`), so nodes whose fields contain
  captured synthetic wrappers can be stored through `prependRegionList`.
  `NirGenExpr` now recursively validates payloads of direct region-placed
  constructors and factory apps under `if`, `match`, and lowered match-result
  forms. This closes the exposed safety hole where a branch-created
  RegionList node containing `Option(metadata)` or `Tuple2(metadata, ...)`
  could be trusted because the outer node was region-owned. Compiler positives
  cover branch/match-created RegionList nodes containing `Some(new T(...))`,
  `Option(new T(...))`, and `Tuple2(new A(...), new B(...))`; negatives reject
  the corresponding unrooted heap metadata payloads. Runtime allocation stats
  prove the executed RegionList nodes, wrappers, and payloads allocate in
  checked region memory (`delta >= 10`). Validation passed at
  2026-05-21 05:39-05:45 CEST with compiler `482/482`, runtime `203/203`,
  `sandbox3_next` compile, and a checksum-matching ReML `ratio` smoke across
  heap, inferred checked stream, and checked scoped rows. No elapsed or L4
  bucket reduction is claimed.
- Follow-up RegionList selected-nested synthetic-factory proof:
  the owner-token inference pass now walks inside already constrained direct
  constructors/factories and constrains nested local aliases only when they are
  real multi-candidate selected allocation aliases. This covers
  `val selected = if flag then Some(new T(...)) else Some(new T(...));
  prependRegionList(region, list, new Node(selected))` without making straight
  heap aliases such as `val tag = metadata` region-placeable. Compiler
  positives cover selected local `Some`/`Option.apply`/`Tuple2` factories
  nested in RegionList node fields; the new negative rejects selected
  `Option(metadata)` nested in a RegionList node, and the older inline/block
  buffer/list/priority-queue metadata negatives still pass. Runtime allocation
  stats prove the executed RegionList nodes, selected wrappers, and payloads
  allocate in checked region memory (`delta >= 17`). Validation passed at
  2026-05-21 05:56-06:02 CEST with compiler `484/484`, runtime `204/204`,
  `sandbox3_next` compile, and a checksum-matching ReML `ratio` smoke across
  heap, inferred checked stream, and checked scoped rows. No elapsed or L4
  bucket reduction is claimed.
- Follow-up framework selected-nested synthetic-factory proof:
  the same bounded nested-alias helper is now explicitly covered for checked
  `ObjectBuffer`/`RegionBuffer` and ordinary checked priority-queue owner-token
  APIs when a framework-owned value object contains selected local
  `Some`/`Option.apply`/`Tuple2` factory aliases. New compiler positives cover
  buffer appends and `RegionPriorityQueue`/`RegionIndexedPriorityQueue`/
  `RegionLongIndexedPriorityQueue` push/put calls with `new Node(selected)`.
  New negatives reject selected nested `Option(metadata)`/`Tuple2(metadata,
  metadata)` payloads through object buffers, region buffers, and priority
  queues. Runtime stats prove selected wrappers, payloads, and containing value
  objects allocate in checked region memory for buffers and priority queues
  (`delta >= 17` each). Validation passed at 2026-05-21 06:12-06:19 CEST with
  compiler `489/489`, runtime `206/206`, `sandbox3_next` compile, and a
  checksum-matching ReML `ratio` smoke across heap, inferred checked stream,
  and checked scoped rows. The smoke medians were heap `48.219 ms`, inferred
  checked `46.521 ms`, and scoped checked `44.333 ms`; the non-fatal JVM
  CodeHeap warning recurred during compile. No elapsed or L4 bucket reduction is
  claimed for this micro-inference proof.
- Follow-up reset-open-handle inferred-array proof and Wikimedia source use:
  ordinary `new Array[...]` placement is now explicitly proven inside
  `resetOpenHandleInline` bodies, including captured object arrays and
  primitive arrays such as `Array[Int]^{region}`. The negative test rejects
  storing unrooted heap metadata into an inferred region array in the same
  callback shape. The inferred LogHub/Wikimedia session and join paths now use
  ordinary `new Array` for their per-group checked arrays inside the inline
  reset body; explicit checked rows keep the old `RiftAllocator.allocateOpenHandle`
  arrays as controls. Validation passed at 2026-05-21 06:27-06:36 CEST with
  compiler `491/491`, runtime `207/207`, and `sandbox3_next` compile. Focused
  20k compressed smokes matched heap, explicit checked, inferred checked, and
  scoped checksums/output for Wikimedia clickstream-session
  (`4440636879622788340`, output `18167`) and LogHub HDFS join
  (`-1607483374812565358`, output `0`). Follow-up 1M x3 L2 gates also matched
  checksum/output. Wikimedia clickstream-session under
  `/Users/siyaoliu/rift/cache/loghub-wikimedia-inferred-array-1m-l2-20260521`
  is heap `1383.161 ms`, explicit checked `1341.892 ms`, inferred checked
  `1254.338 ms`, and scoped checked `1344.536 ms`; explicit and inferred both
  report `1922465` region objects. HDFS join under
  `/Users/siyaoliu/rift/cache/loghub-join-inferred-array-1m-l2-20260521` is
  heap `8031.714 ms`, explicit checked `7839.871 ms`, inferred checked
  `7772.096 ms`, and scoped checked `7737.018 ms`; explicit and inferred both
  report `1000006` region objects. This removes more explicit allocation
  plumbing from inferred checked paths and validates the affected source shape
  at L2. The focused current-state L4 sweep under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260521-loghub-array-source`
  matched checksum/output across all profiled modes. For Wikimedia, the
  inferred checked row has lower parser/input/hash samples/sec than explicit
  checked (`477.00/s` versus `501.20/s`) and lower query/session-loop samples
  (`80.80/s` versus `118.20/s`), while region allocation remains tiny
  (`4.40/s`) and callback-ref samples remain `0.00/s`. HDFS join remains
  parser/input/hash dominated and the 1M profile is short enough that about
  half of the sample is startup/idle, so it is kept as diagnostic only:
  inferred checked has parser/input/hash `585.60/s`, safepoint polling
  `180.20/s`, callback-ref `0.00/s`, and no sampled region allocation/init.
  A 2026-05-21 07:56 source audit found the inferred Wikimedia session path
  still had explicit `RiftAllocator.allocateOpenHandle(region, new Array(...))`
  for `entries`, `heads`, `tails`, and `counts`; these are now ordinary
  `new Array` sites under the same validated reset-open-handle owner. Sandbox
  compile and native link passed. A fresh 20k compressed Wikimedia smoke under
  `/tmp/loghub-inferred-session-array-smoke` matched checksum
  `4260216346575211415` and output `18980` across heap, explicit checked,
  inferred checked, and scoped; the fresh 1M x3
  L2 gate under
  `/Users/siyaoliu/rift/cache/loghub-wikimedia-inferred-session-array-complete-1m-l2-20260521`
  matched checksum `250002331971566003` and output `922453`, with heap
  `1069.051 ms`, explicit checked `1052.706 ms`, inferred checked
  `965.723 ms`, scoped `1053.033 ms`, and explicit/inferred region objects
  both `1922465`. This is source-plumbing completion for the existing array
  inference proof, not a new region-object-count reduction.
- Follow-up shared `ByteLineReader` chunked line-read cleanup:
  `BenchmarkInputSupport.ByteLineReader.readLine` now scans each filled input
  buffer for newlines and copies contiguous spans into the reusable line
  buffer instead of calling per-byte `nextByte` and `append` helpers. This is a
  heap-and-checked parser/input fairness cleanup, not a Rift-specific
  memory-management optimization. Sandbox compile passed after an initial
  sandbox denial on the sbt boot lock was rerun with approved `sbt`
  escalation. Native smokes matched checksum/output for compressed Wikimedia
  clickstream-session (`/tmp/loghub-bytereader-smoke-wikimedia`, checksum
  `-7932171983828413881`, output `17518`), archive-backed HDFS join
  (`/tmp/loghub-bytereader-smoke-join`, checksum `-1607483374812565358`,
  output `0`; tar early-close status remains non-fatal because each row wrote
  `RESULT`), and zip-backed Theodolite retained UC4
  (`/tmp/theodolite-bytereader-smoke`, checksum `-2895454912458695581`,
  output `6176`). The 1M x3 L2 Wikimedia gate under
  `/Users/siyaoliu/rift/cache/loghub-bytereader-wikimedia-1m-l2-20260521`
  is heap `1061.907 ms`, explicit checked `1041.414 ms`, inferred checked
  `960.242 ms`, and scoped checked `1047.725 ms`, all with matching checksum
  `250002331971566003` and output `922453`. The HDFS join gate under
  `/Users/siyaoliu/rift/cache/loghub-bytereader-join-1m-l2-20260521` is heap
  `7134.073 ms`, explicit checked `7138.545 ms`, inferred checked
  `7097.635 ms`, and scoped checked `7140.815 ms`, all with checksum
  `4282190220497908364` and output `0`. Focused L4 under
  `/Users/siyaoliu/rift/cache/profile-sweep-20260521-bytereader-loghub`
  confirms the old `ByteLineReader.nextByte`/`append` top frames are gone; the
  coarse parser/input/hash bucket remains the shared floor and does not show a
  uniform samples/sec drop across modes.
- Follow-up region-owned array closure-store inference proof:
  `RiftRegionInference` now applies the existing checked array element-owner
  proof to closure objects, not only direct constructors and
  `Some`/`Option.apply`/`TupleN` factories. Direct inline closures and selected
  immutable local closure aliases stored into
  `Array[Function1[Int, Int]^{region}]^{region}` inherit the array element
  owner; NIR then region-allocates the materialized closure object while
  preserving the existing unrooted heap-capture rejection. Compiler positives
  cover inline and selected-local closure stores, and the negative rejects a
  closure that captures unrooted heap metadata. Runtime allocation stats prove
  the array plus inline closure (`delta >= 2`) and the array plus selected
  local closure candidates (`delta >= 3`) are checked-region allocations.
  Validation passed at 2026-05-21 07:17-07:21 CEST: compiler `494/494`,
  runtime checked `209/209`, `sandbox3_next` compile, and sandbox compile with
  `-P:scalanative:riftInferReport`. This is a ReML-style synthetic allocation
  coverage slice; no elapsed or L4 bucket reduction is claimed.
- Follow-up checked owner-token closure-container proof:
  `ObjectBuffer`, `RegionBuffer`, and ordinary `RegionPriorityQueue` owner-token
  store APIs now reuse the closure owner proof from method arguments and
  region-owned arrays. Inline closures and selected immutable local closure
  aliases inherit the supplied owner when the value type is
  `Function1[...]^{region}`. Compiler positives cover ObjectBuffer inline
  append, RegionBuffer selected-local append, and priority-queue inline push;
  compiler negatives reject unrooted heap captures at ObjectBuffer and
  priority-queue boundaries. Runtime allocation stats prove ObjectBuffer inline
  closure placement (`delta >= 2`), RegionBuffer selected closure placement
  (`delta >= 3`), and priority-queue inline closure placement (`delta >= 3`).
  Validation passed at 2026-05-21 07:33-07:35 CEST: compiler `499/499`,
  runtime checked `212/212`, `sandbox3_next` compile, and sandbox compile with
  `-P:scalanative:riftInferReport`. This is a compiler/runtime capability
  proof, not an elapsed-time or L4 bucket claim.
- Follow-up checked stream-rank closure proof:
  the same closure-object placement is now explicitly validated for checked
  stream-window rank and table-rank owner-token APIs. Compiler positives cover
  inline closure insertion into `StreamWindowIndexedRank`, selected immutable
  local closure insertion into `StreamWindowLongIndexedRank`, and inline
  closure insertion into `StreamWindowTableRank`. Compiler negatives reject
  unrooted heap captures for direct and selected closure values at those
  boundaries. Runtime allocation stats compare setup-only rank structures with
  inserted closure values and prove the extra closure objects are checked-region
  allocations (`delta >= 4`). Validation passed at 2026-05-21 07:45-07:48 CEST:
  compiler `502/502`, runtime checked `213/213`, `sandbox3_next` compile, and
  sandbox compile with `-P:scalanative:riftInferReport`. This is a bounded
  framework-owner proof, not broad stream-rank topology inference.
- Follow-up Broom generated inferred-array source placement:
  `BroomRetainedDataflowMatrix` inferred generated rows now use ordinary
  `new Array` for aggregate `heads`/`tails`/`tables`, join `left`/`right`,
  generated q17 `tables`, and shopper `views`/`carts`/`purchases`/`candidates`.
  Explicit checked rows remain explicit allocation controls, and file-backed
  q17 remains explicit. Validation passed: `sandbox3_next` compile,
  `BroomRetainedDataflowMatrix` native link, 20k heap/explicit/inferred smokes
  for aggregate/join/q17/shopper, and the 1M x3 L2 gate under
  `/Users/siyaoliu/rift/cache/broom-inferred-arrays-1m-l2-20260521`.
  The L2 rows matched checksum/output and preserved identical
  explicit/inferred region objects: aggregate `1839798`, join `1000006`,
  q17 `1478215`, shopper `1142743`. Median elapsed was aggregate explicit
  `168.010 ms` versus inferred `156.174 ms`, join `145.209 ms` versus
  `141.424 ms`, q17 `155.803 ms` versus `154.966 ms`, and shopper
  `249.488 ms` versus `248.765 ms`. This is source-placement completion for
  generated Broom arrays, not a new L4 bucket or region-object-count claim.
- Follow-up runtime allocation-stat proof for method/effect summaries:
  the compiler already accepted branch and match wrappers that forward a
  method-returned `Array[T^{r}]^{r}` produced under an explicit checked region
  parameter. The runtime suite now also proves the match-forwarded shape
  actually allocates the returned array and contained leaves in checked region
  memory, matching the existing branch-forwarded runtime proof. This is a
  validation coverage slice for the current method-summary inference path, not
  a benchmark elapsed-time claim.
- Follow-up checked priority-queue direct-array proof:
  `RiftRegionInference` now records checked priority-queue `peek`/`pop`/`get`
  locals as owner-region values and remembers recovered array element owners
  only when the queue value type itself captures the checked owner. This extends
  the direct array owner-token bridge from `ObjectBuffer`/`RegionBuffer` to
  ordinary `RegionPriorityQueue` push/peek paths. Compiler positives cover
  pushing `new Array[T^{region}]` and then storing inline region values through
  `region.peek(queue)`. The negative rejects unrooted heap metadata stores
  through recovered `Array[Metadata]^{region}`. Runtime allocation stats prove
  the queue-backed array and inline stored leaves allocate in checked region
  memory (`delta >= 4`). Validation passed at 2026-05-21 09:43-09:47 CEST:
  compiler `510/510`, runtime checked `218/218`, and `sandbox3_next` compile.
  This is a framework-owner inference capability proof; no elapsed or L4 bucket
  reduction is claimed yet.
- Follow-up indexed priority-queue direct-array proof:
  the same checked priority-queue result propagation now has explicit coverage
  for `RegionIndexedPriorityQueue` and `RegionLongIndexedPriorityQueue`.
  Compiler positives cover `put(new Array[T^{region}](...))` followed by
  `get`/`peek` and inline region-value element stores. Negatives reject
  unrooted heap metadata stores through recovered `Array[Metadata]^{region}` for
  both indexed and long-indexed queues. Runtime allocation stats prove the
  indexed and long-indexed pushed arrays plus stored leaves allocate in checked
  region memory (`delta >= 6`). Validation passed at 2026-05-21
  09:53-09:56 CEST: compiler `513/513`, runtime checked `219/219`, and
  `sandbox3_next` compile. This is proof coverage for the general
  framework-owner path, not a priority-queue timing claim.
- Follow-up lexicographic priority-queue direct-array proof:
  dense and long-key lexicographic priority-queue `put` overloads now have the
  same explicit direct-array coverage. Compiler positives cover
  `regionIndexedPriorityQueueLexicographic` and
  `regionLongIndexedPriorityQueueLexicographic` storing
  `new Array[T^{region}]`, followed by `get`/`peek` and inline region-value
  element stores. Negatives reject unrooted heap metadata stores through
  recovered `Array[Metadata]^{region}` for both lexicographic queue families.
  Runtime allocation stats prove the lexicographic indexed and long-indexed
  arrays plus stored leaves allocate in checked region memory (`delta >= 6`).
  Validation passed at 2026-05-21 10:01-10:03 CEST: compiler `516/516`,
  runtime checked `220/220`, and `sandbox3_next` compile. This is capability
  proof for a remaining framework overload family; no elapsed or L4 bucket
  reduction is claimed.
- Follow-up stream-rank direct-array proof:
  checked stream-window rank/table-rank APIs now have bounded direct-array
  coverage for `putWindowRank`, `putWindowRankInBucket`, and
  `putTableRankInBucket`. Direct `new Array[T^{stream}]` values are constrained
  by the checked stream owner, and later `peekWindowRank`/`peekTableRank`
  result locals can recover an array element owner from either an explicit
  captured result type or the prior checked `put` value type recorded on the
  same immutable rank/table local. This removes the explicit result-local
  ascription requirement for the direct-array put/peek path while still
  requiring the array element type itself to capture the checked stream owner.
  Compiler positives cover indexed, long-key lexicographic, and table-rank
  arrays followed by inline region-value element stores. Compiler negatives
  reject unrooted heap metadata stores through recovered
  `Array[Metadata]^{stream}` for indexed, long-key lexicographic, and
  table-rank results. Runtime allocation stats prove the rank/table arrays plus
  stored leaves allocate in checked region memory (`delta >= 6`). Validation
  passed at 2026-05-21 11:00 CEST: compiler `520/520`, runtime checked
  `221/221`, and `sandbox3_next` compile. This is a framework-owner capability
  proof; no elapsed or L4 bucket reduction is claimed.
- Follow-up branch/match array-store proof:
  region-owned array stores now mark every direct constructor or synthetic
  factory returned by an `if`/`match`, not only a single direct RHS. This covers
  `items(i) = if flag then new T(...) else new T(...)`, match-returned
  `Option(new T(...))`, and branch-returned `Tuple2(new A(...), new B(...))`
  when the array element type proves one checked owner. Compiler positives
  cover direct object, `Option.apply`, and `Tuple2` branch/match stores;
  compiler negatives reject branch-returned `Some(metadata)` with unrooted
  heap metadata; runtime allocation stats prove the executed arrays, wrappers,
  and payloads allocate in checked region memory (`delta >= 9`). Validation
  passed at 2026-05-21 11:06-11:08 CEST: compiler `522/522`, runtime checked
  `222/222`, and `sandbox3_next` compile. This is a ReML-style array/container
  capability proof; no elapsed or L4 bucket reduction is claimed.
- Follow-up epoch-fold child-region proof:
  `epochFoldRegionFor` now participates in the checked child-region owner
  inference used by page-token, map/filter, count-by-key, epoch-buffer,
  transaction, and chunk-append helpers. Ordinary `new` records typed under
  the returned fold child region can be widened to the parent stream owner and
  passed to `putEpochFold`, while unrooted heap metadata in those records
  remains rejected. Compiler positives/negatives cover the source shape and
  runtime allocation stats prove two epoch-fold records allocate in checked
  region memory (`delta >= 2`). Validation passed at 2026-05-21 11:14-11:16
  CEST: compiler `524/524`, runtime checked `223/223`, and `sandbox3_next`
  compile. This is operator-owned source-placement/API coverage; no elapsed or
  L4 bucket reduction is claimed.
- Follow-up Dataflow epoch-fold source-use proof:
  `DataflowRegionMatrix.runCheckedAggregateEpochFold` now uses ordinary
  `new CheckedAggregateEvent(...)` under the `epochFoldRegionFor` child owner
  and widens the resulting child-owned event to the parent stream owner before
  `putEpochFold`. This removes the remaining explicit
  `RiftRegion.alloc(new ...)(using region)` source plumbing from that generic
  fold control path without changing query semantics. Validation passed at
  2026-05-21 11:22-11:27 CEST: `sandbox3_next` compile, then a focused
  Dataflow aggregate smoke with `DATAFLOW_EPOCHS=2`,
  `DATAFLOW_DOCS_PER_EPOCH=10000`, `DATAFLOW_WARMUPS=0`,
  `DATAFLOW_BENCHMARK_RUNS=1`, and
  `DATAFLOW_MODES="gc-heap checked-epoch-fold"` matched checksum
  `3276431580` for heap and checked epoch-fold; the checked row reported
  `20004` region objects. This is source-use validation for the epoch-fold
  inference proof, not a new elapsed/profile claim, and generic epoch-fold
  remains a speed-gated control.
- Follow-up chunk-token child-region source-use proof:
  `CheckedAppendWindowMatrix.runRiftCheckedChunkTokenBody` now processes one
  chunk bucket under a direct `chunkAppendRegionFor` owner local and constructs
  records with ordinary `new` typed as `Record^{region}` before widening them
  to the parent stream owner for `appendChunkToken`. The older mutable
  `currentRegion` source shape is avoided because the current inference pass
  intentionally does not infer mutable owner-slot flow. Validation passed at
  2026-05-21 11:36-11:41 CEST: `sandbox3_next` compile, then a focused
  append-window smoke with `CHECKED_APPEND_EVENTS=20000`,
  `CHECKED_APPEND_EVENTS_PER_BUCKET=5000`, `CHECKED_APPEND_WARMUPS=0`,
  `CHECKED_APPEND_BENCHMARK_RUNS=1`, and
  `CHECKED_APPEND_MODES="heap-immix-chunk rift-checked-chunk-token"` matched
  checksum `-8639499034914970780`; the checked row reported `20632` region
  objects. This is source-use validation for the existing chunk child-region
  inference proof, not a new elapsed/profile claim, and fixed-chunk append
  remains a control path rather than a headline topology.
- Follow-up mutable owner-slot boundary proof:
  `epochBufferRegionFor` now has direct compiler/runtime coverage for ordinary
  `new Event(...)` records typed under the returned child owner and widened to
  the parent stream owner before `appendEpochBuffer`. The paired negative keeps
  the rejected mutable-owner-slot shape explicit:
  `var currentRegion = ...; currentRegion = epochBufferRegionFor(...);
  val region = currentRegion; val event: Event^{region} = new Event(...)`
  does not infer flow-sensitively and still falls back to heap, where the
  checked buffer store rejects it as an unrooted heap object. The opt-in
  inference report now records this alias as rejected. Validation passed at
  2026-05-21 11:48-11:54 CEST: compiler `526/526`, runtime checked `224/224`,
  and `sandbox3_next` compile. This is a safety/diagnostic boundary and
  allocation-stat proof, not a new elapsed/profile claim.
- Follow-up Theodolite active-handle source-use proof:
  `TheodolitePowerRegionMatrix` checked Rift handle paths now construct
  `CheckedMeasurement` and `CheckedContribution` records with ordinary `new`
  under the active `resetOpenHandle` owner. The scoped/open-region controls and
  legacy explicit-allocation controls remain unchanged. Validation passed at
  2026-05-21 11:58-12:05 CEST: `sandbox3_next` compile, then a focused real
  archive-member retained-UC4 smoke over 20k records matched checksum
  `-2895454912458695581` and output `1544` for heap, checked stream, and
  checked scoped rows. The checked stream row reported `260000` region objects
  and `0.556 ms` Rift op time. This validates source use of the existing
  active-open-handle ordinary-`new` inference path, not a new L1/L2 or profile
  claim.
- Follow-up audit closure:
  `docs/CPU_PROFILE_REPORT.md` now folds the Theodolite active-handle
  source-use proof into the ranked optimization table and residual heap
  allocation audit. The audit now distinguishes the still-durable
  low-frequency `StreamingEpochOutcome` heap result from retained
  measurement/contribution records, which are region-placeable now and are
  exercised with ordinary `new` in the checked handle paths. No benchmark or
  presentation claim changed.
- Follow-up DSPBench page-token source-use proof:
  `DSPBenchRegionMatrix` now exposes
  `rift-checked-page-token-inferred` / `checked-region-stream-inferred`.
  The mode uses the same checked page-token topology as
  `rift-checked-page-token`, but constructs `CheckedRecord` with ordinary
  `new` under the selected `pageTokenAppendRiftOpenHandleFor` owner and widens
  it to the parent stream owner before `appendPageToken`. Validation passed at
  2026-05-21 13:39-13:46 CEST: `sandbox3_next` compile, native link, and a
  focused 20k real file-backed Fraud/Log smoke. Fraud matched checksum
  `-1399594498030869762` and output `98`; Log matched checksum
  `2172779649197205352` and output `5`. The inferred rows preserved the
  explicit checked region-object counts (`80111` Fraud, `60000` Log). This is
  source-use validation for the existing page-token open-handle inference
  proof, not a new elapsed/profile claim.
- Follow-up selected polymorphic owner-token proof:
  compiler/runtime tests now cover explicitly region-typed selected local
  `Cell[A^{region}]^{region}` candidates flowing into a polymorphic
  owner-token consumer `def consume[A](using r)(cell: Cell[A^{r}]^{r})`.
  Runtime allocation stats prove both selected candidate cells and nested
  payloads allocate in checked-region memory (`delta >= 4`). The paired
  negative records the current boundary: untyped selected generic cells and
  heap-metadata flows are rejected by capture checking before the current
  post-capture inference phase can safely recover an owner. Validation passed
  at 2026-05-21 14:07-14:12 CEST: compiler `528/528`, runtime checked
  `225/225`, and `sandbox3_next` compile. This is a safety/capability proof,
  not a new elapsed/profile claim.
- Follow-up closure-body returned-closure proof:
  a region-owned closure body that directly returns another closure can now
  carry the checked owner through the returned closure wrapper and into the
  nested body allocation when the returned closure explicitly captures the
  runtime owner term. The runtime allocation-stat proof observes the outer
  closure wrapper, returned inner wrapper, and nested `RiftCheckedLeaf`
  allocation in checked region memory (`delta >= 3`), and generated LLVM shows
  all three use the region allocator instead of `scalanative_GC_alloc_small`.
  Validation passed at 2026-05-21 15:24-15:29 CEST: compiler `540/540`,
  clean runtime checked-region `230/230`, and `sandbox3_next` compile. A broad
  fallback that allocated arbitrary owner-capturing closures was tried and
  rejected because stale-token tests proved it can allocate assertion lambdas
  into already-closed regions before `assertThrows` receives them. The local
  named returned-closure wrapper remained open at this direct-return gate; it
  was not claimed as validated there.
- Follow-up named local closure-body returned-closure proof:
  a named local closure returned from a region-owned closure body is now
  runtime-proven as checked-region allocated when the enclosing closure result
  type names an explicit checked owner, the compiler can resolve a unique
  runtime owner term, and the returned local closure body captures that owner.
  The previous typed local proof required an explicit local function type
  `Function1[..., T^{owner}]^{owner}`. The new untyped proof removes that local
  type-ascription requirement for the same explicit-owner shape by recording
  the enclosing closure body owner from the closure result type and recovering
  the local wrapper owner in GenNIR only when it resolves to that same runtime
  owner value. Runtime allocation stats observe the outer closure wrapper, the
  untyped named local inner wrapper, and the nested `RiftCheckedLeaf`
  allocation in checked-region memory (`delta >= 3`); generated LLVM for the
  proof now routes the untyped local inner wrapper through the region allocator
  instead of `scalanative_GC_alloc_small`. Validation passed at
  2026-05-21 17:22-17:24 CEST: compiler `542/542`, clean runtime
  checked-region `232/232`, and `sandbox3_next` compile. Hidden/type-only owner
  capture without a runtime handle, escaping returned closures, mutable local
  closure flow, and the broad arbitrary owner-capturing closure fallback remain
  rejected or heap fallback. This is a compiler/runtime allocation-stat proof,
  not a new elapsed/profile claim.
- Follow-up stored-closure body allocation proof:
  direct inline closures stored into region-owned arrays and checked
  owner-token buffers now carry their explicit checked owner through both the
  closure wrapper and the closure-body allocation when the stored closure
  captures the same runtime owner term. The GenNIR safety path now recovers
  owner aliases (`val owner = region`) and, for erased primitive array update
  trees, falls back to the already inferred region-owned array object owner
  only when the direct closure captures that same runtime owner. Runtime
  allocation stats prove checked-region allocation for
  `ObjectBuffer` inline closure bodies (`delta >= 3`), selected
  `RegionBuffer` closure bodies (`delta >= 4`), and direct region-owned array
  closure-body stores (`delta >= 3`). The paired compiler negative still
  rejects unrooted heap metadata captured by the stored closure. Validation
  passed at 2026-05-21 17:48-17:50 CEST: compiler `546/546`, clean runtime
  checked-region `235/235`, and `sandbox3_next` compile. This is a
  compiler/runtime allocation-stat proof, not a new elapsed/profile claim.
- Follow-up priority-queue stored closure-body proof:
  ordinary checked `RegionPriorityQueue.push` now has explicit compiler and
  runtime allocation-stat coverage for inline and selected immutable local
  closures whose bodies allocate values owned by a captured checked owner term.
  The proof reuses the checked owner-token summary path validated for closure
  wrapper placement; no new benchmark-local rewrite or broad escaping-closure
  inference is claimed. Runtime allocation stats prove the backing queue
  arrays plus closure/body allocations are checked-region objects for inline
  and selected local closure paths (`delta >= 4`). The paired compiler
  negative rejects unrooted heap metadata captured by the pushed closure body.
  Validation passed at 2026-05-21 17:57-18:00 CEST: compiler `549/549`, clean
  runtime checked-region `237/237`, and `sandbox3_next` compile. This is a
  compiler/runtime allocation-stat proof, not a new elapsed/profile claim.
- Follow-up wrapper-nested closure-body proof:
  direct inline closures and selected immutable local closures nested inside
  a region-owned wrapper constructor now inherit the wrapper's proven checked
  owner. `RiftRegionInference` records nested closure allocation sites under
  the direct wrapper allocation, and GenNIR attaches the owner to those nested
  closure arguments before constructor-argument safety checking. The closure
  body allocation is still accepted only when the closure captures the same
  runtime checked owner term, so hidden/type-only owner cases without a handle
  remain heap fallback or rejection. Runtime allocation stats prove the wrapper
  object plus inline closure/body allocation (`delta >= 3`) and wrapper plus
  selected local closure/body allocation (`delta >= 4`) are checked-region
  objects. The paired compiler negative rejects unrooted heap metadata captured
  by the nested closure body. Validation passed at 2026-05-21 18:15-18:21 CEST:
  compiler `552/552`, clean runtime checked-region `239/239`, and
  `sandbox3_next` compile. This is a compiler/runtime allocation-stat proof,
  not a new elapsed/profile claim.
- Follow-up method-returned `Some(closure)` body proof:
  explicit checked-region methods can now return a region-owned `Some`
  containing an inline or selected immutable local closure, and the nested
  closure body can allocate through the same captured runtime owner. This uses
  the method-return factory summary together with the nested-closure wrapper
  proof, so it validates a library-created wrapper across a callee boundary
  without adding a benchmark-local rewrite. Runtime allocation stats prove the
  method-returned `Some` plus inline closure/body allocation (`delta >= 3`) and
  method-returned `Some` plus selected closure/body allocation (`delta >= 4`)
  are checked-region objects. The paired compiler negative rejects unrooted
  heap metadata captured by the nested closure body. Validation passed at
  2026-05-21 18:26-18:28 CEST: compiler `555/555`, clean runtime
  checked-region `241/241`, and `sandbox3_next` compile. This is a
  compiler/runtime allocation-stat proof, not a new elapsed/profile claim.
- Follow-up owner-token generic-wrapper closure-body proof:
  explicit owner-token method arguments now have compiler/runtime proof for
  generic wrapper values containing inline or selected immutable local
  closures. The method parameter type `Wrapper[T^{r}]^{r}` supplies the checked
  owner, the direct wrapper allocation is placed in that region, and nested
  closure arguments plus their captured-owner body allocations inherit the same
  owner. Runtime allocation stats prove method-argument wrapper plus inline
  closure/body allocation (`delta >= 3`) and wrapper plus selected closure/body
  allocation (`delta >= 4`) are checked-region objects. The paired compiler
  negative rejects unrooted heap metadata captured by the nested closure body.
  Validation passed at 2026-05-21 18:33-18:35 CEST: compiler `558/558`, clean
  runtime checked-region `243/243`, and `sandbox3_next` compile. This is a
  compiler/runtime allocation-stat proof, not a new elapsed/profile claim.
- Follow-up closure-body callee-summary proof:
  region-owned closure bodies can now return values produced by an explicit
  checked-region callee such as `build(value)(using owner): T^{owner}` when
  the closure captures the same runtime checked owner term. Runtime allocation
  stats prove the closure wrapper plus the callee-allocated body result are
  checked-region objects (`delta >= 2`). The paired compiler negative rejects
  unrooted heap metadata flowing through the callee allocation. Validation
  passed at 2026-05-21 18:39-18:42 CEST: compiler `560/560`, clean runtime
  checked-region `244/244`, and `sandbox3_next` compile. This is method/effect
  summary coverage, not hidden owner capture, escaping closure inference,
  topology inference, or a new elapsed/profile claim.
- Follow-up closure-body forwarded-callee summary proof:
  the same captured-owner closure body can now call a simple forwarding method
  such as `forward(value)(using owner): T^{owner} = build(value)(using owner)`
  and return the forwarded callee result. Runtime allocation stats prove the
  closure wrapper plus forwarded callee-allocated result are checked-region
  objects (`delta >= 2`), and compiler negatives reject unrooted heap metadata
  flowing through the forwarded callee. Validation passed at
  2026-05-21 19:20-19:22 CEST: compiler `562/562`, clean runtime
  checked-region `245/245`, and `sandbox3_next` compile. A stricter type-only
  fallback experiment was attempted but backed out because the current
  compiler phase does not expose enough stable runtime-owner structure without
  regressing the validated untyped local returned-closure proof; type-only
  owner recovery remains a separate future slice.
- Follow-up closure-body branch/match forwarded-callee summary proof:
  the captured-owner closure body can now call branch and match forwarding
  methods where every path returns a value produced by the same explicit
  checked-region callee owner, such as `if flag then build(value)(using owner)
  else build(value + 1)(using owner)` or an equivalent `selector match`.
  Runtime allocation stats prove the closure wrapper plus executed
  branch/match callee result are checked-region objects (`delta >= 2`), and
  the compiler negative rejects unrooted heap metadata flowing through the
  branch-forwarded callee. Validation passed at 2026-05-21 19:28-19:30 CEST:
  compiler `565/565`, clean runtime checked-region `247/247`, and
  `sandbox3_next` compile. This is control-flow method/effect-summary
  coverage, not broad virtual dispatch, arbitrary callback/library inference,
  hidden/type-only owner recovery, topology inference, or a new elapsed/profile
  claim.
- Follow-up closure-body Option/Some callee-summary proof:
  the captured-owner closure body can now call an explicit checked-region
  method that returns a library-created `Option[T^{owner}]^{owner}` value,
  such as `build(value)(using owner) = Some(new T(value))`. Runtime allocation
  stats prove the closure wrapper, `Some`, and nested payload are checked-region
  objects (`delta >= 3`), and the compiler negative rejects unrooted heap
  metadata hidden behind `Some(metadata)`. Validation passed at
  2026-05-21 19:36-19:38 CEST: compiler `567/567`, clean runtime
  checked-region `248/248`, and `sandbox3_next` compile. This extends the
  closure-body effect-summary proof to a common library-created wrapper shape;
  it is not broad library inference, primitive boxing, hidden/type-only owner
  recovery, topology inference, or a new elapsed/profile claim.
- Follow-up closure-body direct synthetic-factory proof:
  `GenNIR` now prepares direct returned region constructs in methods whose
  closure body owner was already inferred, so captured-owner closure bodies can
  return `Some(new T(...))` and `Tuple2(new A(...), new B(...))` without leaving
  those factory objects and nested payloads on the heap. The first runtime
  attempt exposed the real gap: compiler positives passed, but runtime stats
  saw only the closure wrapper (`delta == 1`). After the lowering fix, runtime
  stats prove the closure wrapper plus `Some`/payload (`delta >= 3`) and the
  closure wrapper plus `Tuple2`/two payloads (`delta >= 4`) are checked-region
  objects. Compiler negatives reject unrooted heap metadata hidden behind
  `Some(metadata)` and `Tuple2(metadata, metadata)`. Validation passed at
  2026-05-21 19:52-19:54 CEST: compiler `571/571`, clean runtime
  checked-region `250/250`, and `sandbox3_next` compile. This is direct
  closure-body synthetic-factory effect-summary coverage, not broad library
  inference, primitive boxed-key placement, hidden/type-only owner recovery,
  topology inference, or a new elapsed/profile claim.
- Follow-up closure-body selected-local synthetic-factory proof:
  captured-owner closure bodies can now use a more ordinary helper shape where
  local `Some(new T(...))` or `Tuple2(new A(...), new B(...))` candidates are
  created, selected through an immutable local alias, and returned. The first
  runtime attempt again exposed a real lowering gap: compiler positives and
  negatives passed, but runtime stats saw only the closure wrapper
  (`delta == 1`). `RiftRegionInference` now records local direct factory apps
  when selected aliases constrain them, and `GenNIR` resolves returned
  immutable aliases in proven closure-body methods back to those direct factory
  RHSs before lowering. Runtime stats prove the closure wrapper plus two
  `Some` candidates and two payloads (`delta >= 5`) and the closure wrapper
  plus two `Tuple2` candidates and four payloads (`delta >= 7`) are
  checked-region objects. Compiler negatives reject selected
  `Some(metadata)` and `Tuple2(metadata, metadata)` with unrooted heap
  metadata. Validation passed at 2026-05-21 20:09-20:10 CEST: compiler
  `575/575`, clean runtime checked-region `252/252`, and `sandbox3_next`
  compile. This broadens closure-body synthetic helper coverage, not escaping
  closure inference, hidden/type-only owner recovery, primitive boxed-key
  placement, topology inference, or a new elapsed/profile claim.
- Follow-up closure-body optional factory proof:
  captured-owner closure bodies now have explicit compiler/runtime proof for
  `Option(new T(...))` and `if include then Some(new T(...)) else None`.
  Runtime stats prove the closure wrapper plus `Option.apply` non-null `Some`
  branch and payload are checked-region objects (`delta >= 3`), and the
  optional branch proof observes the closure wrapper plus `Some`/payload while
  `None` remains allocation-free (`delta >= 3`). Compiler negatives reject
  `Option(metadata)` and `if include then Some(metadata) else None` with
  unrooted heap metadata. Validation passed at 2026-05-21 20:15-20:17 CEST:
  compiler `579/579`, clean runtime checked-region `254/254`, and
  `sandbox3_next` compile. This extends closure-body synthetic factory
  coverage to null/empty-option semantics, not broad library inference,
  primitive boxed-key placement, hidden/type-only owner recovery, topology
  inference, or a new elapsed/profile claim.
- Follow-up closure-body factory callee-summary proof:
  captured-owner closure bodies can now call explicit checked-region callees
  that return `Option(new T(...))`, `Tuple2(new A(...), new B(...))`, or
  selected immutable local aliases of those same factory shapes. The compiler
  fix is general: method-local returned selected factory candidates now bridge
  their direct factory source spans just like closure-body selected locals, so
  `GenNIR` can attach the callee's checked runtime owner to every wrapper and
  nested payload allocation. Runtime stats prove closure wrapper plus
  `Option.apply`/payload (`delta >= 3`), closure wrapper plus `Tuple2`/two
  payloads (`delta >= 4`), selected `Option.apply` candidates plus payloads
  (`delta >= 5`), and selected `Tuple2` candidates plus payloads
  (`delta >= 7`) allocate in checked-region memory. Compiler negatives reject
  `Option(metadata)`, `Tuple2(metadata, metadata)`, and selected variants with
  unrooted heap metadata. Validation passed at 2026-05-21 20:26-20:28 CEST:
  compiler `587/587`, clean runtime checked-region `258/258`, and
  `sandbox3_next` compile. This is method/effect-summary and library-wrapper
  source-placement coverage, not broad library inference, primitive boxed-key
  placement, hidden/type-only owner recovery, topology inference, or a new
  elapsed/profile claim.
- Follow-up closure-body wrapper-returned inline-closure proof:
  captured-owner closure bodies can now return a library wrapper containing an
  inline closure value via `Option((n: Int) => new T(...))`, where the nested
  closure body explicitly captures the same checked runtime owner. Runtime
  stats prove the outer closure wrapper, non-null `Option.apply` `Some`
  wrapper, inner closure wrapper, and nested body allocation are
  checked-region objects (`delta >= 4`). The compiler negative rejects
  unrooted heap metadata captured by the nested closure body through the
  wrapper. Validation passed at 2026-05-21 20:53-20:55 CEST: compiler
  `589/589`, clean runtime checked-region `259/259`, and `sandbox3_next`
  compile. The exact-`Some` inline and selected-wrapper follow-ups below close
  the direct exact-factory counterpart; broader escaping closure summaries
  remain future work. No elapsed/profile claim is made for this proof slice.
- Follow-up closure-body wrapper-returned selected-closure proof:
  captured-owner closure bodies can now return `Option(selected)` where
  `selected` is an immutable local alias choosing between local closure values
  whose bodies explicitly capture the same checked runtime owner. The compiler
  fix has two parts: `RiftRegionInference` recovers immutable selected closure
  aliases nested in region-owned wrapper construction, and `GenNIR` prepares
  direct/local closure values plus selected aliases before checking the wrapper
  constructor. Runtime stats prove the outer closure wrapper, non-null
  `Option.apply` `Some` wrapper, both selected closure candidates, and the
  selected body allocation are checked-region objects (`delta >= 5`). The
  paired compiler negative rejects unrooted heap metadata captured by either
  selected closure body. Validation passed at 2026-05-21 21:28-21:31 CEST:
  compiler `591/591`, clean runtime checked-region `260/260`, and
  `sandbox3_next` compile. This is a bounded selected-wrapper closure/effect
  summary and hidden receiver/environment preparation slice, not broad
  escaping-closure inference, type-only owner recovery, primitive boxed-key
  placement, topology inference, or a new elapsed/profile claim.
- Follow-up closure-body exact-`Some(selected)` wrapper proof:
  the same selected local closure-body wrapper proof is now validated for the
  exact `Some(selected)` spelling, not only null-preserving `Option(selected)`.
  This matters because `Some.apply` and `Option.apply` are distinct library
  factory paths even though both create a `Some` in the non-null case. Runtime
  stats prove the outer closure wrapper, exact `Some` wrapper, both selected
  closure candidates, and selected body allocation are checked-region objects
  (`delta >= 5`). The compiler negative rejects unrooted heap metadata captured
  by either selected closure body. Validation passed at 2026-05-21
  21:37-21:38 CEST: compiler `593/593`, runtime checked-region
  `261/261`, and `sandbox3_next` compile. This is another bounded
  selected-wrapper closure/effect-summary proof, not broad escaping-closure
  inference or a new elapsed/profile claim.
- Follow-up closure-body exact-`Some(inlineClosure)` wrapper proof:
  the direct inline-closure wrapper proof is now validated for exact
  `Some((n: Int) => new T(...))`, not only `Option((n: Int) => new T(...))`.
  Runtime stats prove the outer closure wrapper, exact `Some` wrapper, inner
  closure wrapper, and nested body allocation are checked-region objects
  (`delta >= 4`). The compiler negative rejects unrooted heap metadata captured
  by the nested closure body. Validation passed at 2026-05-21 21:46-21:50 CEST:
  compiler `595/595`, runtime checked-region `262/262`, and `sandbox3_next`
  compile. This is a bounded closure-body wrapper/effect-summary proof and a
  library-created allocation placement proof, not broad escaping-closure
  inference, hidden/type-only owner recovery, topology inference, or a new
  elapsed/profile claim.

## Immediate Next Choices

1. If continuing backend portability, switch to `backend-portability` first;
   do not mix HotSpot/JVM prototype churn into `main`.
2. If continuing Native evidence, the current local compressed real-streaming
   ladder is mostly classified, and the Wikimedia named clickstream-session row
   now has a 10M 3-run median plus one-run full-file feasibility. The next
   useful step is either a full-file 3-run median if machine time allows, or a
   provenance/disk preflight for truly larger StackOverflow/Twitter-2010 data.
3. If preparing presentation, update `PERFORMANCE_EVALUATION_REPORT.md` and
   regenerate `report.html`; otherwise leave them alone.
