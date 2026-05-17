# Benchmark Search Status

Last updated: 2026-05-17 02:54 CEST

Status: hot status file for GC-heavy benchmark search. Detailed provenance
stays in `evidence/GC_HEAVY_BENCHMARK_INVESTIGATION.md` and
`evidence/REAL_INPUT_BENCHMARK_SEARCH.md`.

## Current Lesson

Real input alone is not enough to create GC pressure. Scala Native Immix is a
strong mark-region baseline: it already uses bump-style allocation and
line/block reclamation, so short-lived parser/filter/count objects often do not
create much visible timed GC.

The next useful workloads must retain ordinary objects until a boundary:

- timestamped dataflow dictionaries;
- joins;
- sessions;
- graph/text epochs;
- transaction batches;
- event-correlation or alert windows;
- high-cardinality keyed state.

## Best Current Evidence

- Broom active-16 retained dataflow is the strongest GC-heavy methodology row.
- Broom q17 retained join/aggregate is now implemented as a TPC-H-Q17-like
  generated methodology row: active-16 20M checked Rift `9.67 s`, `50 MB` RSS,
  zero timed GC versus heap `14.45 s`, `232 MB`, L2 GC `1370.380 ms`.
- Yak LiveJournal is the strongest real-input epoch row.
- LogHub retained session/join is true streaming input but parser/hash
  dominated, so it is control evidence.
- GH Archive, Theodolite, DSPBench, and LogHub page/window rows remain
  modest/RSS/tail controls.

## Next Candidate Order

1. Broom/Naiad shopper-style JOIN-SELECT-JOIN if another generated
   prior-work-methodology shape is needed.
2. StreamFlex-style retained event-correlation / transaction-tracking latency.
3. Larger StackExchange/StackOverflow text epochs if data is feasible.
4. Larger SNAP/Twitter graph replay if disk/time is feasible.
5. Alibaba `machine_usage` trace for DSPBench Machine Outlier if provenance is
   pinned.
