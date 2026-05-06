# Rift CPU Profiling Report

Last updated: 2026-05-06 13:30 CEST

Status: profiling runbook and empty report scaffold. No profile rows have been
collected yet.

Reference: Scala Native official profiling guide:
<https://scala-native.org/en/stable/user/profiling.html>

## Purpose

Use profiling to explain remaining CPU cost after region allocation/reclaim has
already removed GC pressure. Profiling rows are diagnostic evidence, not
headline benchmark timing.

The current questions are:

- how much time is object construction versus allocator lowering;
- how much time is checked operator bookkeeping;
- how much time is traversal/checksum/output work shared with heap;
- whether SafeZone-backed checked rows spend time in root/page claim/reclaim;
- whether failed operators such as `EpochFold` and TableRank are losing in
  allocation, lookup/probe, callback/cursor, or aggregation logic.

## Profiling Rules

- Do not profile with `SAFEZONE_TRACE=1`, allocation attribution, or precise
  allocation counters enabled unless the row is explicitly diagnostic.
- Keep profile binaries and inputs identical to the corresponding benchmark
  row except for debug/symbol options required by the profiler.
- Record command, binary path, benchmark mode, input scale, environment,
  profiler tool, and whether the profile was sampled or instrumented.
- Do not use profiler elapsed time as a headline median.

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

## Results

No profile rows collected yet.

Future rows should include:

| Date | Benchmark | Mode | Tool | Input/scale | Main hot symbols | Interpretation |
|---|---|---|---|---|---|---|
