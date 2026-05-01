# Headline UnsafeZone-HP Core/Prior Sweep

Date: 2026-05-01

Status: clean 5-run headline medians for core runtime and prior-work
methodology rows with `unsafezone-hp` included. This supersedes the earlier
`UNSAFEZONE_HP_BASELINE_MATRIX.md` smoke rows for the covered benchmarks.

Run id: `2026-05-01-unsafezone-core-prior`

Raw logs: `cache/perf-eval/2026-05-01-unsafezone-core-prior/`

Command:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-unsafezone-core-prior \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight core prior" \
bash scripts/run-performance-evaluation.sh
```

Environment recorded by the run:

| Field | Value |
|---|---|
| Parent repo | `main` at `c4affc1dadb12034316c8fa01e2750f427fff025` |
| Implementation repo | `feature/rift` at `31fa902e00696f4f64008e5ee1fecafab78c3696` |
| CPU | Apple M4 Pro |
| Memory | `25769803776` bytes |
| Java | Temurin 17.0.18 |
| Scale | `headline` |
| Suites | `preflight core prior` |

Important caveat: this run captured raw logs under the run directory, but the
existing prior-work scripts still wrote several TSV summaries to their default
`/tmp` paths. The values below are parsed from the run logs. After this run,
`scripts/run-performance-evaluation.sh` was fixed so future prior-work runs
write `streamflex`, `yak`, and `stancu` summary TSVs under the run directory.

## Mode Labels

| Label | Meaning |
|---|---|
| `heap` | Scala Native Immix heap allocation. |
| `safezone-current` | SafeZone, `SAFEZONE_ROOTS_MODE=0`, 4 KiB pages. |
| `safezone-improved` | SafeZone, `SAFEZONE_ROOTS_MODE=1`, 4 KiB pages. |
| `unsafezone-hp` | Benchmark-only SafeZone no-root mode, `SAFEZONE_ROOTS_MODE=3`, `SAFEZONE_PAGE_SIZE=32768`. Unsafe. |
| `rift-hp` | Trusted Rift HPZone backend. |
| `rift-streaming` | Trusted Rift StreamingZone backend. |
| `rift-checked` | Checked Rift path where the benchmark exposes one. |

## Core Runtime Results

All rows are 5-run medians in milliseconds.

| Benchmark | heap | safezone-current | safezone-improved | unsafezone-hp | rift-hp | rift-streaming | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| GCBench runtime | 213.817 | 656.038 | 213.239 | 206.636 | 236.393 | n/a | UnsafeZone-HP is best by about 3% vs improved SafeZone; Rift HPZone loses here. |
| ListOfLists linked | 15191.230 | 132391.160 | 9914.397 | 9818.653 | 12400.062 | n/a | Improved SafeZone captures most of the win; UnsafeZone-HP is only slightly faster; Rift HP beats heap but loses to both. |
| ListOfLists flat | 1748.743 | 1778.891 | 1769.278 | 1766.060 | 1540.958 | n/a | Rift HPZone remains the clear winner for the flat layout. |
| ListOfLists chunked | 2585.021 | 5136.846 | 2433.118 | 2430.496 | 2640.031 | n/a | Improved/Unsafe SafeZone win; root removal beyond improved changes almost nothing. |
| Pipeline surrogate | 35.077 | 34.591 | 34.660 | 34.417 | 46.293 | 45.648 | CPU-bound/surrogate control; UnsafeZone-HP's tiny edge is not a case-study result. |

## Topology Results

All rows are 5-run medians in milliseconds.

### GCBench Topology

| Mode | Topology | Median ms |
|---|---|---:|
| heap | baseline | 232.412 |
| safezone-current | A | 223.448 |
| safezone-current | B | 613.792 |
| safezone-improved | A | 205.274 |
| safezone-improved | B | 436.140 |
| unsafezone-hp | A | 195.087 |
| unsafezone-hp | B | 190.631 |

Interpretation: UnsafeZone-HP is very strong in this topology harness,
especially topology B. Because roots are disabled, this is substrate evidence,
not safety evidence. Any mixed-reference shape using this mode requires a
static Rift-style safety story before becoming user-facing.

### ListOfLists Topology

| Mode | One region | Nested regions | Mixed/rooted |
|---|---:|---:|---:|
| heap | 14670.599 | n/a | n/a |
| safezone-current | 137142.885 | 10005.966 | 56389.800 |
| safezone-improved | 9696.183 | 9870.161 | 9928.715 |
| unsafezone-hp | 9643.194 | 9682.066 | 9878.433 |
| rift-hp | 12690.335 | 12675.184 | 14510.512 |

Interpretation: improved SafeZone already removes the largest root-bookkeeping
pathology. UnsafeZone-HP is consistently a little faster than improved
SafeZone, and both are materially faster than Rift HPZone in this linked
topology harness.

## Prior-Work Methodology Results

All rows are 5-run medians in milliseconds unless otherwise noted.

### Broom/Dataflow-Style Operators

| Operator | heap | safezone-current | safezone-improved | unsafezone-hp | rift-hp | rift-streaming | rift-checked |
|---|---:|---:|---:|---:|---:|---:|---:|
| SELECT | 28.258 | 25.928 | 22.501 | 21.957 | 27.588 | 27.785 | 24.413 |
| AGGREGATE | 48.849 | 48.190 | 40.124 | 39.434 | 49.106 | 49.026 | 44.146 |
| JOIN | 29.122 | 25.671 | 22.784 | 22.359 | 26.832 | 27.058 | 24.935 |

Interpretation: UnsafeZone-HP is fastest, but only slightly ahead of improved
SafeZone. Rift checked beats heap on SELECT/JOIN and is close on AGGREGATE, but
it loses to improved SafeZone. This points to SafeZone allocator/pool mechanics
as a strong candidate substrate for future checked Rift internals.

### StreamFlex-Style Pressure

| Row | heap | safezone-current | safezone-improved | unsafezone-hp | rift-hp | rift-streaming |
|---|---:|---:|---:|---:|---:|---:|
| Throughput elapsed ms | 42.712 | 40.421 | 39.920 | 39.591 | 46.436 | 46.108 |
| Latency elapsed ms | 9.806 | 10.712 | 10.733 | 10.247 | 12.687 | 11.629 |
| Deadline misses | 4 | 0 | 0 | 0 | 0 | 0 |

Interpretation: UnsafeZone-HP is fastest for throughput and removes misses,
but heap has the fastest latency median while missing deadlines. Rift removes
misses but loses elapsed time in this local methodology row.

### Yak-Style Rows

| Row | heap | safezone-current | safezone-improved | unsafezone-hp | rift-hp | rift-streaming | yak-runtime |
|---|---:|---:|---:|---:|---:|---:|---:|
| wordcount | 46.997 | 40.060 | 37.336 | 37.138 | 50.309 | 49.969 | 56.066 |
| graphstep | 45.500 | 45.483 | 40.572 | 39.869 | 52.046 | 52.171 | 58.425 |
| sort | 74.098 | 74.704 | 74.611 | 74.876 | 76.149 | 75.876 | 77.062 |
| topword | 70.370 | 63.870 | 59.286 | 58.686 | 68.848 | 68.959 | 75.976 |
| graphchi | 42.384 | 35.600 | 35.456 | 35.008 | 47.554 | 47.907 | 53.247 |
| promotion proxy | 80.314 | n/a | n/a | n/a | n/a | n/a | 127.188 |

Interpretation: SafeZone-family rows win most Yak-shaped workloads; the
UnsafeZone-HP improvement over improved SafeZone is small but consistent.
Rift's current trusted backends lose here. The sort row remains CPU-bound.

### Stancu-Style Transaction Boundary

| heap | safezone-current | safezone-improved | unsafezone-hp | rift-hp | rift-streaming |
|---:|---:|---:|---:|---:|---:|
| 44.141 | 33.258 | 33.720 | 33.335 | 51.380 | 51.478 |

Interpretation: the SafeZone family wins; UnsafeZone-HP does not meaningfully
improve over current/improved SafeZone here. Rift loses elapsed time.

## Key Findings

- `unsafezone-hp` validates the diagnostic hypothesis: if SafeZone root
  registration is disabled and pages are 32 KiB, SafeZone internals are often
  faster than current Rift HPZone on linked/allocation-heavy local harnesses.
- The margin over `safezone-improved` is usually small. The earlier SafeZone
  pathology is mostly fixed by root mode `1`; mode `3` is not a dramatic new
  speed tier except in GCBench topology B.
- Rift HPZone still has a real flat-layout win on ListOfLists, so the standalone
  Rift backend is not dominated everywhere.
- For Broom/Yak/Stancu-shaped rows, the strongest runtime direction is now:
  keep Rift's static/capture safety goal, but seriously consider reusing or
  matching SafeZone allocator/pool mechanics instead of continuing to tune the
  current standalone HPZone backend in isolation.
- `unsafezone-hp` is not safe. Any user-facing version needs Rift-style static
  boundary checking or a different root/scanning discipline.

## Next Actions

1. Run the stream and DEBS headline legs with `unsafezone-hp` included before
   changing runtime internals.
2. Compare `unsafezone-hp` against improved SafeZone on NEXMark, Yahoo,
   RIoTBench, Common Crawl WET-shaped, and bounded DEBS.
3. If the stream rows repeat the core/prior pattern, design a SafeZone-derived
   checked runtime backend or a Rift backend that borrows SafeZone's pool/page
   mechanics.
4. Do not add `unsafezone-streaming` until there is a real reset-capable
   SafeZone-derived lifecycle.
