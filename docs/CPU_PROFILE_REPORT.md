# Rift CPU Profiling Report

Last updated: 2026-05-07 16:38 CEST

Status: profiling runbook plus first sampled profile row and the first
profile-driven implementation follow-up. The sampled GH Archive row identified
`BufferedReader`/UTF-8/`StringBuilder` parser allocation as the avoidable cost;
the follow-up byte-slice file-backed parser now validates that direction.

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

Profile artifact:

`/Users/siyaoliu/rift/cache/profile-gharchive-q1-checked-2026-05-06/sample.txt`

Profiled benchmark row:

| Query | Mode | Median ms | GC ms | Max GC ms | Output count |
|---|---|---:|---:|---:|---:|
| q1-fields | `rift-checked-safezone-page-token` | `7393.602` | `192.570` | `193.221` | `2600000` |

Important caveat: `/usr/bin/sample` was diagnostic only. Use the non-profiled
3-run medians in `evidence/GITHUB_ARCHIVE_REGION_MATRIX.md` for headline
timing.

Future rows should include:
