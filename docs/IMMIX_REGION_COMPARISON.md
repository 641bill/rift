# Immix And Regions: Why Scala Native Heap Pressure Can Be Low

Date: 2026-05-16
Last updated: 2026-05-16 19:31 CEST

Status: investigation note. This explains why Scala Native Immix can make
natural heap/GC baselines strong, why some real-input rows show little GC time,
and where Rift regions should still win.

## Summary

Scala Native's default heap collector, Immix, is not a weak baseline. Immix is a
mostly-precise mark-region tracing collector in Scala Native, and the original
Immix paper describes a mark-region family that combines space efficiency, fast
collection, and mutator performance by allocating and reclaiming memory in
coarse blocks and finer-grained lines.

This makes Immix closer to regions than a naive mark-sweep collector:

- allocation is bump-pointer-like in contiguous free holes;
- reclamation happens at block/line granularity rather than per-object free;
- dead objects usually are not individually traversed;
- opportunistic evacuation can reduce fragmentation;
- if the heap is large enough, many short-lived stream objects die before a
  collection is forced.

Therefore, real streaming input does not automatically create visible GC
pressure. A parser/filter/count loop that allocates records briefly and then
drops them may be handled well by Immix. Rift should expect strong wins only
when lifetime topology lets it avoid tracing large retained transient graphs,
reduce peak RSS/fixed-memory failures, or remove GC latency tails.

## Mechanism Comparison

| Mechanism | Immix heap | Rift regions |
|---|---|---|
| Allocation fast path | Bump allocation inside free lines/holes or blocks. | Bump allocation inside an explicitly opened region/slab. |
| Reclamation unit | Free lines/blocks discovered after tracing live objects. | Whole region/epoch/page/window reset or close. |
| Dead object processing | Dead objects are usually not individually freed. | Dead region objects are never individually freed. |
| Live object cost | Must trace reachable heap objects during collection. | Region-local objects need no GC tracing if static rules prevent unsafe heap roots. |
| Fragmentation control | Line/block reuse plus opportunistic evacuation. | Region internal fragmentation is bounded by region topology/slab policy. |
| Lifetime knowledge | Dynamic: collector discovers reachability at GC time. | Static/programmatic: epoch/window/page/transaction boundary is explicit. |
| Best case | Short-lived or compact live objects with enough heap headroom. | Many objects die together at a known boundary. |
| Weak case | Large retained object graph, tight heap cap, GC tail sensitivity. | Sparse regions, wrong topology, excessive live region payload. |

## Why This Lowers Observed GC Pressure

Immix reduces *visible collection pressure*, not allocation pressure itself.
The heap program still allocates, but timed GC can remain small when:

- the heap has enough headroom to postpone collection;
- objects die before the next collection;
- live-set size is small compared with total allocated bytes;
- the workload updates compact durable state rather than retaining ordinary
  record objects;
- parser/hash/query CPU dominates the timed section.

This matches our current evidence:

- GH Archive, LogHub retained session/join, Theodolite, and DSPBench real rows
  are often parser/hash/query dominated.
- Generated Common Crawl-shaped rows and Broom retained dataflow rows create
  many ordinary retained objects and show much stronger GC/RSS pressure.
- Yak LiveJournal shows the expected epochal win because real graph updates
  naturally share a batch/epoch lifetime.

## What This Means For Rift Claims

Rift should not argue that Scala Native heap/Immix is bad. The stronger claim
is:

> Immix is already region-like enough to make simple real streaming rows cheap.
> Rift adds static, programmer-visible lifetime topology, so when objects
> naturally die at epoch/page/window/transaction boundaries, the backend can
> avoid tracing retained transient graphs and bulk-close them directly.

This gives three distinct evaluation tracks:

1. **Scala Native memory-management evidence:** checked Rift versus Immix on
   retained object graphs and heap caps.
2. **Prior-work methodology evidence:** Broom/Naiad and StreamFlex-shaped rows
   where prior systems expected GC pressure or latency tails.
3. **Backend portability evidence:** the Scala-level topology/checking model
   should be reusable on JVM, Scala.js, Wasm, and analysis-only backends even
   when allocation lowering differs.

## Backend Implication

If no public real-input stream becomes strongly GC-heavy under Immix, the next
step is not to weaken the baseline. It is to be explicit:

- real-input rows can still show RSS, fixed-memory, and latency-tail wins;
- GC-heavy throughput rows may be prior-work-methodology or generated
  retained-object rows;
- JVM/Scala.js/Wasm prototypes should test whether the same Scala-level Rift
  API can reduce allocation rate, object churn, or tail latency on other
  backend runtimes.

## Sources

- Stephen Blackburn and Kathryn McKinley, "Immix: A Mark-Region Garbage
  Collector with Space Efficiency, Fast Collection, and Mutator Performance",
  PLDI 2008:
  <https://openresearch-repository.anu.edu.au/items/32c6080b-51ee-433e-981d-e5960787a3fb>
- Scala Native sbt documentation, garbage collector section:
  <https://scala-native.org/en/stable/user/sbt.html#garbage-collectors>
- Scala Native runtime / GC settings:
  <https://scala-native.org/en/stable/user/runtime.html>
- Garbage Collection Handbook, mark-region / Immix discussion:
  <https://www.oreilly.com/library/view/the-garbage-collection/9781000883688/chapter-117.html>
