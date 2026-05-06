# Rift CPU Profiling Report

Last updated: 2026-05-07 00:16 CEST

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

## Results

| Date | Benchmark | Mode | Tool | Input/scale | Main hot symbols | Interpretation |
|---|---|---|---|---|---|---|
| 2026-05-06 | GH Archive q1-fields | `rift-checked-safezone-page-token` | macOS `/usr/bin/sample`, 10s sampled diagnostic | 2 hourly gzip JSON-line files, 200k real events, file-backed | `java.io.BufferedReader.readLine`, UTF-8 decoder loop, `AbstractStringBuilder.append0`, `String.charAt`, `BufferedReader.prepareRead`, `StringBuilder.append`, `GithubArchiveRegionMatrixHelpers.countJsonFields`, stable hashing, zlib inflate; allocator/GC present but lower | Remaining file-backed cost is parser/string/decompression dominated. Page-token already moves event/field records, but the current reader still creates heap strings/builders. Next optimization should be NDJSON byte/char-slice parser scratch before more region allocator tuning. |
| 2026-05-07 | GH Archive q1/q2 byte-slice follow-up | `heap-immix`, `rift-trusted-streaming`, `rift-checked-safezone-page-token` | non-profiled benchmark rerun | 2 hourly gzip JSON-line files, 200k real events, file-backed `GITHUB_ARCHIVE_FILE_PARSER=byte-slice` | n/a, implementation follow-up | Byte-slice parsing removes the measured parser-string cliff: q1 heap `3806.120 ms` vs checked scoped page-token `3629.193 ms`; q2 heap `3756.950 ms` vs checked scoped page-token `3626.107 ms`. Region rows report zero timed GC and about `211 MB` RSS versus heap about `290 MB`. |

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
