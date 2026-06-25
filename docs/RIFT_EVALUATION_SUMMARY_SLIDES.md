# Rift Evaluation Summary Slides

Date: 2026-05-03
Last updated: 2026-06-01 15:20 CEST

Status: final talk-outline slide source. Use
`docs/PERFORMANCE_EVALUATION_REPORT.md` as the main narrative report and
`docs/report.html` as the generated presentation artifact.

## Slide 1: Thesis

Rift is a checked region-memory system for Scala Native that moves proven
epoch/page/window/transaction-local objects out of Immix and reclaims them in
bulk, while preserving heap fallback for unproven Scala code.

## Slide 2: Why This Is Hard

| Issue | Rift answer |
|---|---|
| Scala has mutable objects, subtyping, arrays, erased generics, closures, and virtual dispatch. | Heap fallback remains the default. Region placement requires a proven runtime owner. |
| Region bugs are use-after-free bugs. | Capture/separation checking, active handles, owner tokens, `HeapRoot`, and negative safety tests. |
| Immix is already strong. | Focus on retained transient graphs, RSS/fixed-memory pressure, and GC-tail-sensitive lifetimes. |

## Slide 3: System Shape

| Layer | What it does |
|---|---|
| Lifetime APIs | `epoch`, page/window token, retained query, transaction, stable/transient/capsule. |
| Static analysis | Proves which owner a value belongs to, or leaves the allocation on the heap. |
| Runtime backend | Rift streaming slabs or checked scoped/SafeZone-family regions. |
| Controls | Same-shape heap, summary-only, legacy checked, unsafe/rootless, and L4 profiles. |

## Slide 4: Region Syntax And Ergonomics

```scala
RiftRegion.epoch { region ?=>
  val item: Item^{region} = new Item(key, value)
  buffer.append(item)
}
```

The goal is ordinary Scala allocation syntax. Explicit allocation helpers still
exist, but the compiler now places many `new`, `Some`, `Option`, tuple, array,
generic wrapper, and closure objects into checked regions when the owner is
known.

## Slide 5: Region Inference Done

| Implemented | Examples |
|---|---|
| Expected-type local placement | `val x: T^{r} = new T(...)` |
| Branch/match placement | every path returns the same checked owner |
| Method/effect summaries | direct, returned-local, forwarding, branch/match, selected local factories |
| Owner-token call sites | `consume(using region)(new T(...))` |
| Framework/operator owners | page-token, epoch-buffer, buffer, priority queue, rank/table paths |
| Synthetic allocations | `Some`, `Option.apply`, `None`, `Tuple2`-`Tuple22`, arrays, generic `Cell` |
| Closure placement | nonescaping closure objects and narrow captured-owner closure-body allocations |
| Diagnostics | region, heap, unknown, and rejected placement decisions |

## Slide 6: Region Inference Left

| Remaining track | Work still needed |
|---|---|
| Closure/effect summaries | escaping-safe closures, closure-body effects, hidden owner capture, lambda environment rewriting |
| Type-only recovery | recover a runtime owner when `T^{r}` has a unique owner term; otherwise keep heap fallback |
| General summaries | more callees, forwarding wrappers, helper libraries, and selected framework boundaries |
| Polymorphic safety | conservative handling for virtual dispatch, mutation, callbacks, exceptions, erased generics, and generic containers |
| Boxes/libraries | primitive boxes, boxed keys, iterators, collection nodes, strings, buffers, parser helpers |
| Automatic scopes | prototype local-escape wrapping is default-off after reaching ordinary heap/library allocations too broadly; keep explicit lifetimes until allocation-site precision and close safety are proven |

## Slide 7: Static Safety

Negative coverage includes heap-retains-region, outer-retains-inner, closure
escape, widened `AnyRef`, generic hiding, unsafe array stores, mutable
reassignment, unrooted heap metadata, constructor `this` escape, stale
token/use-after-close, and child-after-parent-close.

Dynamic heap metadata requires `HeapRoot` unless static immutable safety is
proven. Runtime checks are only removed when compiler/runtime probes prove the
invariant.

## Slide 8: Evaluation Contract

| Level | Use |
|---|---|
| L1 final-clean | Headline elapsed/RSS. |
| L2 stats | GC/region counter interpretation. |
| L3 diagnostics | Allocation-stat and safety proof slices. |
| L4 profiles | Diagnostic bucket attribution only. |

Headline comparison is natural Immix heap versus checked Rift. Backend rows are
comparison rows under the same Rift system; unsafe/rootless rows are lower
bounds only.

## Slide 9: Latest Current-State Matrix

Completed run:

`/private/tmp/rift-eval-current-full-20260521`

It produced 19 summary files with no failure or mismatch markers. This was a
dirty working-tree run, so use it as latest engineering evidence, not clean
publication evidence.

## Slide 10: Real Or Local Input Results

| Benchmark | Immix heap | Checked Rift / best safe checked | Classification |
|---|---:|---:|---|
| DSPBench Fraud q2 10M | `208405.569 ms` | `187882.928 ms`; SafeZone `186988.431 ms` | real/local stream win |
| DSPBench Log q2 10M | `306392.943 ms` | `273860.718 ms` | real/local stream win |
| Theodolite q2 real | `2256.219 ms`, RSS `147.9 MB` | `2160.896 ms`, RSS `80.4 MB` | real time-series modest win |

## Slide 11: Generated, Methodology, And Microbenchmark Results

| Benchmark | Immix heap | Checked Rift / best safe checked | Classification |
|---|---:|---:|---|
| Broom aggregate 10M | `1071.498 ms`, RSS `148.7 MB` | `862.143 ms`, RSS `16.4 MB` | retained dataflow methodology win |
| Broom join 10M | `1043.463 ms`, RSS `76.9 MB` | `896.583 ms`, RSS `15.1 MB` | retained dataflow methodology win |
| StreamFlex throughput 10M | `5138.231 ms` | `3800.585 ms` | design-stressor win |
| Common Crawl q1 10M | `70410.059 ms` | `46491.537 ms` | generated stressor win |
| Common Crawl q2 10M | `67398.152 ms` | `46094.232 ms` | generated stressor win |
| NEXMark q5 fold API 1M | `470.288 ms` | `419.855 ms` | generated fold API gate |
| SPECjbb-style port | `1674.726 ms` | `1231.076 ms` | transaction-lifetime win |

## Slide 12: Honest Controls

| Row | Result | Lesson |
|---|---|---|
| GH Archive q2 | heap `3848.235 ms`, checked `3842.741 ms` | tie; parser/query floor dominates |
| NEXMark q9 | heap `8790.376 ms`, checked `7929.885 ms`, SafeZone `7639.168 ms` | checked beats heap, scoped backend best |
| Window fold | published 10M control regressed; current 1M focused rerun heap `99.302 ms`, checked `97.321 ms` | focused gate now passes narrowly; NEXMark q5 now has a generated-local fold API gate; other application fold rows still need gates |
| Object allocation | heap `263.639 ms`, checked Rift `161.281 ms`, checked SafeZone `133.532 ms` | allocation lowering works; backend substrate still matters |

## Slide 13: What Profiles Explain

Checked rows often show larger parser/hash/session percentages because GC has
disappeared. Separate:

- shared floors: input, parser, hashing, query mutator;
- real Rift overhead: allocation/init, token/handle plumbing, closure/capsule
  traversal, residual heap helpers;
- removed work: heap allocation/GC tracing and retained graph scanning.

Recent fixes removed DSPBench tuple returns, checked-loop boxed `Ref` captures,
and several accidental helper allocations through inference.

## Slide 14: What Has Been Built

- Checked region runtime and Scala Native compiler lowering.
- Staged region inference with diagnostics and runtime allocation-stat proofs.
- Checked APIs for epochs, page/window token paths, retained query shapes,
  buffers, priority queues, and selected rank/table/top-k helpers.
- Safety test coverage for the main heap/region and closure/container hazards.
- A broad benchmark/evidence suite spanning Broom, StreamFlex, Yak/Stancu-style
  rows, ReML-style kernels, Common Crawl, NEXMark, LogHub, GH Archive,
  DSPBench, Theodolite, and microbenchmarks.

## Slide 15: What Is Left

| Track | Remaining work |
|---|---|
| Full inference | broad closure/effect summaries, hidden owner capture, type-only recovery, polymorphic/library summaries |
| Boxes/libraries | primitive boxes, boxed keys, iterators, collection nodes, strings, buffers, parser helpers |
| Runtime checks | remove only after proof-gated active-handle/stale-token/lifetime probes |
| Performance | fold/traversal/capsule overhead, token plumbing, object init/zeroing, residual parser/helper heap allocation |
| Evidence | rerun latest selected matrix from a clean committed tree |
| Proof | mechanize the small-core containment and close/reset safety argument |

## Slide 16: Final Takeaway

Rift has reached a working checked-region system with meaningful Scala syntax,
static safety, inference, and benchmark wins against Immix. It is not yet full
ReML/MLKit inference, but it has the right architecture: proven allocations go
to regions, unproven allocations stay on the heap, and performance claims are
classified by whether the workload actually has region-friendly lifetime
structure.
