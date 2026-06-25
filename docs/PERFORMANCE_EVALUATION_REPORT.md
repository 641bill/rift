# Rift Project And Performance Evaluation Report

Date: 2026-05-03
Last updated: 2026-06-01 15:20 CEST

Status: final project wrap-up report source. This Markdown file is the
narrative source for `docs/report.html`; regenerate the HTML with
`python3 scripts/generate-report-html.py` after changing presentation text.
Detailed command provenance remains in `evidence/**`, `docs/status/CURRENT.md`,
and the result directories named below.

## 1. Executive Summary

Rift is a checked region-memory system for Scala Native. It keeps ordinary
Scala programs close to their natural object shape, but gives stream and
dataflow code a way to state that many objects share an epoch, page, window,
transaction, or retained-query lifetime. When the compiler and checked APIs can
prove the lifetime, those objects are allocated in regions and reclaimed in
bulk. Objects whose lifetime is durable, unknown, polymorphic, or heap-visible
stay on the Immix GC heap.

The central result is not that every workload beats Immix. Immix is already a
strong mark-region collector with bump-style allocation. Rift wins when the
program exposes a real lifetime boundary that avoids tracing retained transient
graphs, lowers resident memory, or reduces GC tail behavior. Parser-heavy and
primitive-array-heavy rows are often ties or controls.

The current Scala Native implementation has:

- A checked region runtime with scoped, streaming, page/window, retained epoch,
  and selected checked backend paths.
- Scala-facing checked APIs for epochs, page/window token operators, retained
  query shapes, buffers, priority queues, and StreamFlex-style stable/transient
  regions.
- Compiler lowering that can place many ordinary `new` allocations, arrays,
  `Some`/`Option`, tuples, generic wrappers, closure objects, and selected
  closure-body allocations into checked regions when ownership is proven.
- Capture/separation safety tests and runtime probes for heap-retains-region,
  outer-retains-inner, closure escape, widened `AnyRef`, generic hiding, unsafe
  array stores, mutable reassignment, unrooted heap metadata, constructor
  `this` escape, stale tokens, and child-after-parent-close.
- Benchmark evidence over methodology rows, generated stream stressors,
  real/local stream inputs, retained-state case studies, and microbenchmarks.

The latest broad current-state run completed at:

`/private/tmp/rift-eval-current-full-20260521`

It used a dirty working tree and should therefore be read as current engineering
evidence, not clean committed presentation evidence. The run produced 19
summary files, no failure or mismatch markers, and matching checksums/output
counts within each benchmark family.

Current implementation validation note, 2026-06-01: the latest child worktree
passes the compiler checked suite (`718/718`), the native runtime checked suite
(`322/322`), and `sandbox3_next` compile after broad automatic local-escape
scope insertion was gated behind explicit opt-in. The performance numbers below
remain the latest recorded engineering/presentation evidence; the
automatic-scope prototype is not promoted as performance or safety evidence.

## 2. System Model

Rift separates three concepts that are often conflated:

| Concept | Meaning |
|---|---|
| Lifetime boundary | Epoch, page, window, transaction, retained query, or capsule boundary. This is what the program means. |
| Safety discipline | Capture checking, owner tokens, active/closed handles, `HeapRoot`, and negative compiler/runtime tests. This is why bulk close is safe. |
| Backend lowering | Rift streaming slabs, checked scoped/SafeZone-family allocation, arrays/buffers, or heap fallback. This is how the implementation runs. |

The user-facing comparison is natural heap/GC versus checked Rift with the same
logical program, output, and lifetime boundary. Checked scoped and checked
stream are backend choices under the Rift umbrella. Unsafe/rootless modes,
summary-only lower bounds, same-shape heap controls, and legacy checked rows are
mechanism controls unless a table explicitly says otherwise.

## 3. Region Syntax And Ergonomics

Rift exposes region lifetimes through ordinary Scala APIs and capture-checked
types rather than a separate language:

```scala
RiftRegion.epoch { region ?=>
  val event: Event^{region} = new Event(key, value)
  consume(event)
}
```

Common shapes are:

| Shape | User intent | Current status |
|---|---|---|
| `RiftRegion.epoch { ... }` | Batch, graph step, dataflow epoch, transaction. | Implemented and benchmarked. |
| Page/window token APIs | Page, record group, time bucket, or key bucket owns many short-lived records. | Implemented for selected append/map/filter/count/rank-like helpers. |
| Retained epoch/query APIs | Natural objects are retained until notify/close, then bulk reclaimed. | Implemented for Broom/Dataflow-style retained rows and top-k/session rows. |
| Checked buffers and priority queues | Framework-owned containers store region-owned values. | Implemented for selected object, region, priority, indexed priority, and rank/table paths. |
| `HeapRoot` | Explicit bridge for durable heap metadata referenced by region objects. | Required unless static immutable safety is proven. |

The ergonomic goal is that users write ordinary `new` where possible. Explicit
allocation helpers remain available, but the compiler increasingly infers the
region allocation site from the expected captured type, owner-token argument, or
framework boundary.

## 4. Region Inference

Rift is ReML/MLKit-inspired, but it is not full Tofte/Talpin or ReML-style
whole-program region inference yet. The current system is best described as
capture-directed checked region placement with conservative heap fallback.

### 4.1 What Is Implemented

| Inference capability | Current status |
|---|---|
| Local expected-type placement | `val x: T^{r} = new T(...)` lowers into the checked region when `r` has a runtime owner term. |
| Immutable owner aliases | `val owner = region` is canonicalized to the checked runtime handle in validated local and method-return shapes. |
| Branch/match placement | Branch/match returned allocations are placed when all paths prove the same checked owner. |
| Method-return summaries | Direct, returned-local, branch, match, forwarding, and selected local factory results are summarized for methods with explicit checked region parameters. |
| Owner-token call-site placement | Arguments to checked owner-token methods can be placed through the actual runtime owner argument. |
| Framework/operator placement | Selected page-token, epoch-buffer, buffer, priority-queue, rank/table, and retained helpers recover the operator-owned region. |
| Synthetic allocations | `Some`, `Option.apply`, `None`, `Tuple2` through `Tuple22`, selected tuple/option factories, arrays, generic `Cell`, and wrapper records are covered in owner-proven shapes. |
| Closure object placement | Capture-free, captured-region, local, method-returned, wrapper-returned, array-stored, buffer-stored, and priority-queue-stored closure objects are covered when nonescaping and owner-proven. |
| Closure body effects | Narrow captured-owner closure bodies can allocate local/new, callee-returned, forwarded, branch/match, `Some`/`Option`, tuple, and selected-wrapper results into the same region. |
| Diagnostics | `-P:scalanative:riftInferReport` reports region, heap, unknown, and rejected decisions for audited placements. |

Heap fallback remains the default. The compiler does not region-place an
allocation when the owner is only type-level with no runtime handle, when a
closure may escape, when virtual dispatch or erased generics hide owner flow,
when mutable state can retarget the owner, when a heap object would retain a
region reference, or when dynamic heap metadata is not rooted.

Automatic compiler-inserted region creation/deallocation is not promoted. A
prototype local-escape wrapping path is now gated behind explicit opt-in after
it reached ordinary library/test heap allocations too broadly; the default
validated system keeps those allocations on the heap.

### 4.2 What Is Left For Full Region Inference

| Remaining inference track | Work still needed |
|---|---|
| Broad closure/effect summaries | Finish escaping-closure summaries where the closure value is safe, closure-body allocation effects, hidden owner capture, and lambda signature/environment rewriting. |
| Type-only owner recovery | Recover a runtime owner handle when the type proves `T^{r}` and a unique owner term is available; keep heap fallback otherwise. |
| General callee summaries | Extend method/effect summaries across more ordinary callees, simple forwarding wrappers, helper libraries, and selected framework boundaries. |
| Polymorphic and erased paths | Stay conservative across virtual dispatch, mutation, callbacks, exceptions, erased generics, and generic containers that can hide owner flow. |
| Primitive boxes and boxed keys | Add a safe `nir.Op.Box`/boxed-key placement story only if cache and identity semantics remain correct. |
| Library-created allocations | Cover iterators, collection nodes, parser helper records, strings, buffers, arrays, wrappers, and other high-frequency helper shapes through inference or checked-library support. |
| Evidence and diagnostics | Keep expanding positive allocation-stat tests and negative safety tests before relaxing runtime checks or promoting an inference claim. |

## 5. Static Safety Guarantees

The safety contract is:

- Region values must not outlive their owner.
- Heap and durable state cannot retain region references unless an explicit
  safe bridge such as `HeapRoot` is used.
- Parent/child region nesting must close in lifetime order.
- Open handles and tokens cannot be used after close.
- Region-owned arrays/containers cannot be used to hide unsafe heap metadata or
  wider owner flows.
- Constructor and closure paths cannot leak `this`, hidden owner references, or
  unrooted dynamic metadata.

The validation suite has negative tests for:

| Negative class | Purpose |
|---|---|
| heap-retains-region | Reject long-lived heap state storing region references. |
| outer-retains-inner | Reject outer regions retaining shorter-lived child objects. |
| closure escape | Reject closures that can outlive the owner they capture. |
| widened `AnyRef` escape | Reject region values hidden by widening. |
| generic container hiding | Reject owner flow hidden behind erased generic containers. |
| unsafe array stores | Reject storing heap/unrooted metadata into region-owned arrays. |
| mutable reassignment | Reject owner or value flows that mutation can retarget. |
| unrooted dynamic heap metadata | Require `HeapRoot` unless immutable/static safety is proven. |
| unsafe constructor `this` escape | Reject leaking a not-yet-owned region object. |
| stale token/use-after-close | Preserve runtime probes unless compiler proof is complete. |
| child-after-parent-close | Reject invalid lifetime order. |

Runtime checks have not been removed wholesale. They are only bypassed or
specialized where compiler/runtime probes prove the invariant for an
operator-owned path.

## 6. Runtime And Compiler Features Completed

Major completed implementation pieces:

| Area | What is implemented |
|---|---|
| Runtime allocator | Rift managed-object allocation, open/close/reset counters, stats-disabled fast path, reusable slab policy experiments, checked final-clean object allocation path. |
| Compiler lowering | Region allocation zones in NIR for proven class/array/factory allocations; inference phase for owner recovery and diagnostics; GenNIR owner attachment for selected factories, arrays, closures, wrappers, and method summaries. |
| Checked APIs | Scoped regions, open streaming handles, page-token helpers, retained epoch helpers, buffers, priority queues, rank/table helpers, top-k, append/window/fold paths. |
| Mutator parity | Removed accidental tuple returns in DSPBench update paths, callback `Ref` captures in checked loops, and several benchmark-framework source-shape artifacts. |
| Profiling support | L4 profile sweep harness, bucket classifier for parser/input/hash, query mutator, GC/meta, heap allocation, region allocation/init, token plumbing, traversal/capsule, and callback-ref shape. |
| Data input support | Compressed and archive-member streaming through `BenchmarkInputSupport`, including gzip, tar.gz, zip, zipdir, and 7z-style specs where configured. |
| Documentation/evidence | Status, roadmap, CPU profile report, inference lineage, checked-overhead matrix, benchmark matrices, and generated HTML report. |

## 7. Evaluation Protocol

Rift uses four measurement levels:

| Level | Meaning | Use |
|---|---|---|
| L1 final-clean | External elapsed/RSS without stats instrumentation. | Headline timing and memory when available. |
| L2 standard stats | GC and region counters enabled. | Interpretation of why a row wins or loses. |
| L3 diagnostics | Focused probes and allocation stats. | Compiler/runtime proof of placement or safety. |
| L4 profiles | Sampling profiles. | Diagnostic attribution only, never headline elapsed. |

The headline comparison is Immix heap versus checked Rift. Same-shape heap,
summary-only, legacy checked, unsafe/rootless, and profiling rows remain
controls.

## 8. Benchmark Classification

| Class | Benchmarks | What the class proves |
|---|---|---|
| Retained dataflow methodology | Broom aggregate/join/q17/shopper, Dataflow aggregate/join/select. | Whether natural retained object graphs benefit from checked bulk reclaim. |
| Generated/methodology stressors | Common Crawl WET-shaped, LogHub generated, NEXMark, StreamFlexDesign. | Whether page/window/epoch APIs remove allocation and GC pressure under controlled stream shapes. |
| Real/local stream inputs | Theodolite UCI household power, DSPBench Fraud/Log, selected LogHub/Wikimedia/Yak/AskUbuntu rows. | Whether public/local compressed inputs produce the same memory regime. |
| Prior-work-style ports | SPECjbb2005-style transaction port, ReML/MLKit-style local kernels. | Whether Rift covers the axes used by prior region systems. |
| Micro/overhead matrices | Object allocation, append window, window fold, buffers, priority queues. | What runtime/API overhead remains after GC is removed. |

## 9. Latest Performance Summary Versus Immix

The following numbers are from the latest full selected current-state matrix at
`/private/tmp/rift-eval-current-full-20260521`. Because the tree was dirty,
these are the freshest engineering numbers, not a clean committed artifact.

### 9.1 Real Or Local Input Rows

These rows use local/public input files or replay bundled real benchmark data.

| Benchmark | Brief description | Class | Immix heap | Checked Rift / best safe checked row | Interpretation |
|---|---|---|---:|---:|---|
| DSPBench Fraud q2 10M | Real DSPBench credit-card file replay. | Real/local stream | `208405.569 ms`, GC `38435.057 ms` | checked page-token `187882.928 ms`; checked SafeZone `186988.431 ms` | Checked is about 10% faster than heap; SafeZone backend slightly best. |
| DSPBench Log q2 10M | Real DSPBench HTTP log replay. | Real/local stream | `306392.943 ms`, GC `57338.467 ms` | checked page-token `273860.718 ms`, GC `24816.086 ms` | Checked Rift beats heap and SafeZone; strong real local row. |
| Theodolite q2 real | UCI household-power streaming-file row. | Real time-series | `2256.219 ms`, GC `98.145 ms`, RSS `147.9 MB` | checked stream `2160.896 ms`, GC `29.826 ms`, RSS `80.4 MB` | Modest time win, large RSS/GC reduction. |

### 9.2 Generated, Methodology, And Microbenchmark Rows

These rows are still useful, but they are not real-input proof. They test
specific memory-management shapes, prior-work axes, or runtime/API overheads.

| Benchmark | Brief description | Class | Immix heap | Checked Rift / best safe checked row | Interpretation |
|---|---|---|---:|---:|---|
| Broom aggregate 10M | Timestamped retained aggregate records. | Retained dataflow methodology | `1071.498 ms`, GC `149.051 ms`, RSS `148.7 MB` | checked Rift `862.143 ms`, GC `0`, RSS `16.4 MB` | Clear retained-object time/RSS/GC win. |
| Broom join 10M | Timestamped retained join records. | Retained dataflow methodology | `1043.463 ms`, GC `115.636 ms`, RSS `76.9 MB` | checked Rift `896.583 ms`, GC `0`, RSS `15.1 MB` | Clear retained-object win. |
| StreamFlexDesign throughput 10M | Stable state plus transient period objects. | Generated/design stressor | `5138.231 ms`, GC `1008.846 ms` | checked stream `3800.585 ms`, region ops `11.916 ms` | Strong throughput win; pressure-latency misses also drop `72 -> 4`. |
| Common Crawl q1 10M pages | Generated WET-shaped tokenization stressor. | Generated stream stressor | `70410.059 ms`, GC `17551.246 ms` | checked page-token `46491.537 ms`, GC `296.167 ms` | Strong generated object-pressure win. |
| Common Crawl q2 10M pages | Generated domain/window stressor. | Generated stream stressor | `67398.152 ms`, GC `17995.183 ms` | checked page-token `46094.232 ms`, GC `344.296 ms` | Strong generated page/window win. |
| NEXMark q3/q8/q11 | Generated Beam-default stream queries. | Generated methodology | q3 `2848.152`, q8 `4431.702`, q11 `2217.263 ms` | checked `2591.178`, `4157.367`, `2188.282 ms` | Modest checked wins; q9 is also faster than heap but SafeZone is best. |
| NEXMark q5 fold API 1M | Generated hot-auction window aggregate using `StreamWindowFold`. | Generated methodology / application API gate | `470.288 ms`, GC `29.921 ms`, RSS `289.9 MB` | checked fold API `419.855 ms`, GC `0`, RSS `219.5 MB` | Generated Q5 fold API gate passes; not exact Beam NEXMark evidence. |
| GH Archive q1/q2 | Generated GH Archive-shaped preloaded events. | Generated/preloaded control | q1 `3975.523`, q2 `3848.235 ms` | checked q1 `3822.250`, q2 `3842.741 ms` | Small win/tie; parser/query floor dominates. |
| LogHub q2 generated | Window counts over generated log-shaped events. | Generated stream/operator | `6677.914 ms`, GC `1517.648 ms` | checked epoch stream `2600.244 ms`, GC `0` | Very strong checked-lifetime/API win. |
| LogHub q3 generated | Template/session generated log query. | Generated stream/operator | `32867.576 ms`, GC `4695.691 ms` | checked epoch stream `26291.412 ms`, GC `1369.451 ms` | Strong win, but query/session CPU still large. |
| LogHub top templates | Generated retained top-k template records. | Retained/top-k | `3909.541 ms`, GC `746.918 ms` | checked scoped `3445.204 ms`, GC `0` | Modest time win and GC removal. |
| SPECjbb2005-style port | Clean-room transaction workload. | Prior-work-style port | `1674.726 ms`, GC `206.437 ms` | checked stream `1231.076 ms`, GC `0.593 ms` | Strong transaction-lifetime win. |
| Object allocation 10M | Primitive-field object allocation microbenchmark. | Runtime overhead | `263.639 ms`, GC `107.693 ms` | checked Rift `161.281 ms`; checked SafeZone `133.532 ms` | Allocation lowering is effective; SafeZone substrate remains a lower overhead backend for this shape. |
| Append window 10M | Checked append/page-token microbenchmark. | API overhead | `338.362 ms`, GC `88.807 ms` | checked Rift `252.007 ms` | Good operator-owned append win. |
| Window fold 10M | Checked fold microbenchmark. | API overhead | `898.906 ms`, GC `61.506 ms` | checked Rift `930.973 ms` | Regression/control: fold traversal/API overhead exceeds removed GC. |
| Window fold focused 1M rerun | Current validated rerun after redundant `putFoldInBucket` open-check removal. | API overhead | `99.302 ms`, GC `10.518 ms`, RSS `75.0 MB` | checked Rift `97.321 ms`, GC `0`, RSS `40.4 MB` | Focused gate now narrowly passes; NEXMark q5 has a generated-local fold API gate, while other application fold rows still need their own smokes/L1/L2. |

## 10. What The Profiles Say

The L4 profiles explain why checked rows sometimes appear to spend more samples
in parser/hash/session code even when they are faster overall. Removing GC
changes the denominator: parser, input, hashing, traversal, and query mutator
work become a larger fraction once GC disappears. The important distinction is:

- Shared floors: input decoding, parsing, hashing, and query logic that both
  heap and checked rows execute.
- Real Rift overhead: region allocation/init, token/handle plumbing,
  checked-callback closure plumbing, capsule traversal, reusable cursor work,
  and residual accidental heap allocations.
- Disappearing work: GC tracing/metadata, heap allocation paths, and retained
  object graph scans avoided by bulk close/reset.

Recent general fixes removed tuple allocations in DSPBench update paths,
reduced runtime allocation stats overhead, removed boxed callback `Ref` shapes
from checked loops, and expanded compiler inference so ordinary helper
allocations no longer accidentally stay on the heap when a checked owner is
proven.

## 11. What Has Been Achieved

Completed project outcomes:

- A working Scala Native checked-region runtime and compiler path.
- A staged capture-directed inference layer with runtime allocation-stat proof
  for ordinary `new`, arrays, options, tuples, generic cells, owner-token
  method arguments, closure objects, selected closure-body effects, and
  library wrapper factories.
- Static safety tests that preserve heap fallback for ambiguous cases and
  reject known unsound patterns.
- A broad benchmark suite aligned with Broom, StreamFlex, Yak, Stancu/SPECjbb,
  ReML/MLKit, Common Crawl, NEXMark, LogHub, GH Archive, DSPBench, Theodolite,
  and retained-object methodology.
- Multiple current rows where checked Rift beats Immix on elapsed time, RSS,
  and GC, including retained dataflow, StreamFlexDesign, Common Crawl-shaped
  stressors, LogHub generated rows, DSPBench Log/Fraud, Theodolite, and
  SPECjbb-style transactions.
- A clear diagnosis of remaining overhead buckets and which are shared floors
  versus real checked-framework costs.

## 12. What Is Left

The project is substantial but not complete. The next work should focus on:

| Area | Remaining work |
|---|---|
| Full region inference | Add broad closure/effect summaries, escaping-closure summaries, hidden owner capture, type-only owner recovery, polymorphic summaries, and library-boundary summaries. |
| Automatic scope inference | Rework or disable broad local-escape wrapping until allocation-site escape precision, library exclusion, exception-safe close, and runtime allocation-stat proof are in place. |
| Primitive boxes | Design a safe allocation-zone path for `nir.Op.Box` and boxed keys without breaking cache/identity semantics. |
| Library-created allocations | Extend inference or library support for iterators, collection nodes, strings, buffers, parser helpers, boxed keys, wrappers, and erased generic paths. |
| Runtime check removal | Remove checks only where compiler/runtime probes prove active-handle, stale-token, and lifetime invariants. |
| Backend selection | Automatically choose checked stream versus checked scoped backend per API/workload shape when evidence shows one is consistently better. |
| Performance polish | Reduce fold/traversal/capsule overhead, token/handle plumbing, object init/zeroing where definite initialization is proven, and residual heap allocation in parser/helper paths. |
| Clean final evidence | Rerun the latest selected matrix from a clean committed tree before using the current dirty-run numbers as final publication claims. |
| Mechanized proof | Finish the small-core proof story for containment, close/reset, heap roots, owner tokens, and closure/capability effects. |
| Non-Native backends | JVM, Scala.js, Wasm, and analysis-only remain design/prototype tracks, not validated performance backends. |

## 13. Claim Boundaries

Supported now:

- Checked regions can beat Immix when object lifetimes are real and exposed.
- Capture-directed inference substantially improves ergonomics by replacing
  many explicit allocation helper calls with ordinary `new`.
- The current safety discipline rejects the main unsound heap/region and
  closure/container hazards.
- Real/local rows show both strong wins and honest controls.

Not supported yet:

- Full ReML/MLKit-style whole-program region inference.
- Safe region placement for arbitrary primitive boxes, erased generic
  containers, virtual dispatch, mutable owner flows, or unknown libraries.
- Blanket runtime-check removal.
- Cross-backend performance claims beyond Scala Native.

## 14. Pointers

| Artifact | Purpose |
|---|---|
| `docs/report.html` | Generated presentation report. |
| `docs/RIFT_EVALUATION_SUMMARY_SLIDES.md` | Talk-outline slide source. |
| `docs/ROADMAP.md` | Long-form roadmap and implementation history. |
| `docs/REGION_INFERENCE_LINEAGE.md` | ReML/MLKit lineage and current inference boundary. |
| `evidence/RIFT_REGION_INFERENCE_MATRIX.md` | Inference feature/test matrix. |
| `evidence/CHECKED_OVERHEAD_REMOVAL_MATRIX.md` | Optimization and overhead-removal matrix. |
| `docs/CPU_PROFILE_REPORT.md` | Profile bucket interpretation. |
| `/private/tmp/rift-eval-current-full-20260521` | Latest full selected current-state matrix. |
