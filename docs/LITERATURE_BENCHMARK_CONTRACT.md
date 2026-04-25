# Rift Literature Benchmark Contract

Date: 2026-04-25

Status: extracted from local PDFs under `docs/literature/`. The PDFs are local
research references and are not committed as project source unless explicitly
requested.

## Purpose

This file translates the Broom, Yak, StreamFlex, and Stancu et al. papers into
concrete reproduction targets for Rift. It is not a claim that Rift has already
matched those systems. It is the comparison contract that keeps the benchmark
plan tied to prior work while the implementation continues.

The standard for new benchmarks is:

- Heap and Rift variants must run the same logical program.
- The intended variable is allocation placement and lifetime policy.
- Region-managed values may be ordinary Scala objects.
- Primitive-only layouts are allowed only when labeled as layout experiments or
  interim safety workarounds.
- Results must separate runtime-only effects, topology/layout effects, and
  application/operator evidence.

## Prior-Work Benchmark Targets

| System | Workload in paper | Original setup and metric | Reported effect | Rift reproduction target |
|---|---|---|---|---|
| Broom | List-of-lists allocator microbenchmark | Allocate/free 40 list-of-lists; each structure has `n` lists of `n` objects, `n=500..3000`. | Region runtime reduced time by about 59%. | Already covered locally by ListOfLists same-layout matrix; keep current/improved SafeZone and Rift HPZone baselines. |
| Broom | Emulated Naiad SELECT, AGGREGATE, JOIN vertices | Synthetic per-epoch inputs: documents receive 500k-600k new entries per epoch; authors receive 10-20 new entries per epoch; run after 40 epochs. | SELECT about 13%, AGGREGATE about 20%, JOIN about 36% runtime reduction. | Add a Broom-style dataflow matrix with ordinary Scala message/value objects allocated either on heap or in an epoch region. Label it methodology reproduction, not exact Naiad reproduction. |
| Broom | Naiad workflows and incremental SCC motivation | Naiad v0.4 on Mono; examples include TPC-H Q17, shopper workflow, and SCC over 15M vertices / 80M edges. | GC often accounts for 20%-40% of runtime and can create synchronization delays. | Use as motivation and future comparison. Exact artifact is unavailable, so do not claim exact reproduction. |
| Yak | Hyracks external sort, word count, distributed grep | 11-node cluster; YahooWebmap 72GB; data/control split with epochs at operator open/close. | Overall normalized runtime 0.14-0.64 vs Parallel Scavenge; GC time 0.02-0.11. | Started locally with word-count-style durable control metadata plus epoch-local data records. Still not Hyracks or distributed Yak. |
| Yak | Hadoop in-map combiner, top-word selector, distributed word filter | 11-node cluster; StackOverflow 37GB; epochs around map/reduce tasks. | Overall normalized runtime 0.73-0.89; GC time 0.17-0.26; app time sometimes higher. | Future: reproduce map/reduce task-shape locally only after the dataflow operator harness is stable. |
| Yak | GraphChi connected components, community detection, PageRank | One node; Sampletwitter-2010, 100M edges, 62M vertices; epochs around sub-intervals. | Overall normalized runtime 0.70-0.86; GC time 0.15-0.56. | Future: graph-processing benchmark with explicit sub-interval regions and a control/data split. |
| StreamFlex | StreamIt BeamFormer and FilterBank | Ovm and HotSpot Java baselines; 10,000 iterations. | StreamFlex reported substantially lower run time than Java baselines on those stream kernels. | Started locally with a StreamFlex-style throughput/latency matrix over ordinary Scala packet/event objects. Still not exact BeamFormer/FilterBank. |
| StreamFlex | IDS and event-correlation latency | Periodic stream processing; deadline miss and per-item latency measurements. | StreamFlex avoids large GC-induced deadline misses in the reported event-correlation case. | Started locally: collect per-event latency distributions, max-pause proxies, and deadline misses for heap/SafeZone/Rift modes. |
| Stancu et al. | SPECjbb2005 transaction regions | 7 annotations; each warehouse 100k iterations; young gen varied 1MB-256MB. | About 77%-78% memory region-freed; up to 22% speedup at small young gen; fewer young collections. | Started locally with a transaction-shaped accounting probe. Initial per-transaction regions lost; batching 64 transactions per region plus lower-overhead Rift counters gives a Rift-vs-heap win, but SafeZone remains faster. |

## Immediate Reproduction Order

1. Keep the local ListOfLists matrix as the Broom allocator microbenchmark
   reproduction.
2. Add a Broom-style SELECT/AGGREGATE/JOIN dataflow matrix in the Scala Native
   fork. It should use ordinary Scala objects for message records, aggregate
   entries, join entries, and output records.
3. Use that matrix to compare heap, current SafeZone, improved SafeZone, Rift
   HPZone, and Rift Streaming.
4. Add a StreamFlex-style throughput/latency matrix over ordinary Scala stream
   objects, with deadline-miss and tail-latency rows. This is methodology
   reproduction, not exact StreamFlex/Ovm.
5. Add Yak-style epoch/control-data benchmarks next, then Stancu-style
   annotation/accounting probes.
6. Continue DEBS Phase 5 only when changes preserve the same logical program:
   heap uses `new`, Rift uses `region.alloc` at the same lifetime boundary.

Current implementation note: step 2 is implemented in
`scala-native-rift/sandbox/src/main/scala-next/DataflowRegionMatrix.scala`, with
native-only local medians, peak RSS, current/improved SafeZone modes, and a
provisional 40-epoch x 500k-document single run recorded in
`scala-native-rift/sandbox/DATAFLOW_REGION_MATRIX.md` and synced to
`evidence/DATAFLOW_REGION_MATRIX.md`.

Step 4 is implemented in
`scala-native-rift/sandbox/src/main/scala-next/StreamFlexRegionMatrix.scala`.
It records default and allocation-pressure native-only medians in
`scala-native-rift/sandbox/STREAMFLEX_REGION_MATRIX.md`, synced to
`evidence/STREAMFLEX_REGION_MATRIX.md`. After the Rift allocation-counter fix,
the pressure run is the current StreamFlex-style signal: heap throughput is
`634.472 ms` with `141.804 ms` GC, while Rift HPZone/Streaming are
`331.740 ms`/`329.896 ms`. Heap has `89` latency deadline misses; Rift
Streaming has zero. This is not an exact StreamFlex/Ovm reproduction.

Step 5 is started in
`scala-native-rift/sandbox/src/main/scala-next/YakRegionMatrix.scala`. It
records default and epoch-pressure native-only medians in
`scala-native-rift/sandbox/YAK_REGION_MATRIX.md`, synced to
`evidence/YAK_REGION_MATRIX.md`. After the Rift allocation-counter fix, the
local Yak-style result is good but still mixed against improved SafeZone: Rift
Streaming is `199.156 ms` vs heap `243.522 ms` on wordcount and `209.528 ms`
vs heap `240.890 ms` on graphstep, close to improved SafeZone
(`194.933 ms`/`203.729 ms`). This supports the control/data split but is not
an exact Yak/Hyracks/Hadoop/GraphChi reproduction.

The Stancu-style probe is started in
`scala-native-rift/sandbox/src/main/scala-next/StancuRegionMatrix.scala`. It
records default and transaction-pressure native-only medians in
`scala-native-rift/sandbox/STANCU_REGION_MATRIX.md`, synced to
`evidence/STANCU_REGION_MATRIX.md`. The current local result has two findings:
per-transaction regions were too fine-grained, while batching 64 transactions
per region plus lower-overhead Rift allocation counters fixes the Rift-vs-heap
direction. At one million transactions, heap is `223.611 ms`, Rift HPZone is
`201.447 ms`, and Rift Streaming is `199.438 ms`; improved SafeZone is still
faster at `174.620 ms`. This is not SPECjbb2005 or Stancu et al.'s static
analysis.

## Metrics Required For Reproduction Claims

Every benchmark result intended for comparison should include:

- command and environment variables;
- run count and whether the result is median or single-run;
- elapsed time;
- GC collection count and GC collection duration;
- Rift region operation time and allocation/open/close/reset counters where
  applicable;
- memory/RSS when collected by the surrounding script;
- correctness checksum or output comparison;
- annotation count or explicit statement that the benchmark is still using
  trusted `HPZone` APIs;
- clear label: exact reproduction, methodology reproduction, surrogate, or
  local diagnostic.

## Current Contract Gaps

- The available Broom/Naiad implementation is not open in this workspace; exact
  Naiad numbers cannot be reproduced from the paper alone.
- Yak's original evaluation is distributed and JVM-specific. Rift now has a
  local control/data-space methodology harness, but it must not be presented as
  a replacement for Yak's cluster result or dynamic promotion/write-barrier
  safety story.
- StreamFlex's strongest axis is latency predictability. Rift now has a local
  methodology harness with per-event latency tails and deadline misses, but it
  does not run the original StreamIt/Ovm kernels or model scheduler/queuing
  delay.
- Stancu et al. measure annotation burden and region-freed memory. Rift now has
  a local accounting probe, but it does not yet have compiler-produced
  annotation counts, region-freed byte accounting, or safe API rejection
  reports.
