# Rift Region Reuse Policy Matrix

Date: 2026-05-15
Last updated: 2026-05-15 20:26 CEST

Status: focused and selected-application evidence for
`RIFT_REGION_REUSE_POLICY`. This file separates the clear allocator signal from
the current application-transfer signal.

## Policy Knob

Canonical environment variable:

`RIFT_REGION_REUSE_POLICY`

Supported values:

- `default`
- `bulk-zero-retained`
- `cache-small`
- `cache-large`
- `prezero-large`

`RIFT_ZERO_REUSED_SLABS=1` remains an alias for `bulk-zero-retained`. The
default remains memory-conservative. These modes change bounded non-huge slab
reuse/zeroing policy only; huge slabs, explicit close semantics, and safety
checks are unchanged.

## Focused Allocation Gate

Mode:
`ObjectAllocationLoweringMatrix`, `rift-checked-rift-open-handle`, primitive
record shape, 5-run medians.

| Objects | Policy | Median ms | Region op ms | Slow alloc ms | RSS bytes | Interpretation |
|---:|---|---:|---:|---:|---:|---|
| 5M | `default` | 67.822 | 2.780 | 1.217 | 203849728 | Baseline. |
| 5M | `bulk-zero-retained` | 69.909 | 5.553 | 1.177 | 203849728 | Slower in this policy family after the newer canonical implementation. |
| 5M | `cache-small` | 65.161 | 0.472 | 0.030 | 204062720 | Positive focused allocator signal. |
| 5M | `cache-large` | 63.566 | 0.437 | 0.000 | 204062720 | Best focused policy. |
| 5M | `prezero-large` | 67.521 | 3.257 | 0.000 | 204079104 | More close/reset work; not best. |
| 10M | `default` | 149.609 | 17.445 | 7.564 | 404029440 | Baseline. |
| 10M | `bulk-zero-retained` | 155.161 | 21.729 | 7.455 | 404029440 | Slower than default at this gate. |
| 10M | `cache-small` | 134.237 | 6.597 | 4.832 | 404029440 | Positive. |
| 10M | `cache-large` | 130.250 | 0.894 | 0.000 | 404209664 | Best; about `13%` faster than default. |
| 10M | `prezero-large` | 133.345 | 6.818 | 0.000 | 404209664 | Positive versus default, but behind `cache-large`. |

Conclusion: `cache-large` is a real focused allocation win. It should remain an
opt-in throughput-biased policy candidate, not a default, until representative
application gates improve.

## Selected Application Gates

### StreamFlexDesign 1M Throughput

Mode: `checked-epoch-stream`, L1 final-clean. The first run that included build
work was discarded; the warm rerun is the relevant comparison.

| Policy | L1 external real s | RSS bytes | L2 median ms | L2 region op ms | Interpretation |
|---|---:|---:|---:|---:|---|
| `default` | 0.93 | 7913472 | 373.053 | 1.330 | Baseline. |
| `cache-large` | 0.93 | 7913472 | 372.851 | 1.247 | Neutral. |

Conclusion: the StreamFlexDesign row is dominated by stable-state/query CPU,
capsule add/drain, linked traversal, and allocation body. The reuse policy does
not move this representative row yet.

### Dataflow AGGREGATE

Mode: `checked-epoch-stream`, L1 final-clean. Small 10 x 100k x 3 gate and
larger 20 x 500k x 1 gate both matched checksums.

Small gate:

| Policy | External real s | RSS bytes | Checksum |
|---|---:|---:|---:|
| `default` | 0.08 | 10797056 | 163835709480 |
| `cache-small` | 0.08 | 10797056 | 163835709480 |
| `cache-large` | 0.08 | 10797056 | 163835709480 |
| `bulk-zero-retained` | 0.08 | 10813440 | 163835709480 |
| `prezero-large` | 0.08 | 10813440 | 163835709480 |

Larger one-pass gate:

| Policy | External real s | RSS bytes | Checksum |
|---|---:|---:|---:|
| `default` | 0.20 | 23625728 | 1460601341601 |
| `cache-large` | 0.20 | 23625728 | 1460601341601 |
| `bulk-zero-retained` | 0.19 | 23642112 | 1460601341601 |

Conclusion: no reliable application signal. This row is too short and dominated
by query/array work after the handle-backed allocation promotion.

### Generated Common Crawl-Shaped Q2

Mode: `rift-checked-page-token`, generated WET-shaped `q2-domain-window`,
1M pages, L1 final-clean, one run per policy, matching checksum
`1076064953308107199` and output count `929230`.

| Policy | External real s | RSS bytes | Interpretation |
|---|---:|---:|---|
| `default` | 3.09 | 63242240 | Baseline. |
| `cache-large` | 3.09 | 63258624 | Neutral. |
| `bulk-zero-retained` | 3.11 | 63242240 | Slightly slower in this one-pass gate. |
| `prezero-large` | 3.10 | 63258624 | Neutral/slightly slower. |

Conclusion: the canonical reuse policies do not improve this page-token row in
the current one-pass gate. The older `RIFT_ZERO_REUSED_SLABS=1` application win
should be treated as policy-history evidence until reproduced under the
canonical policy matrix.

## Current Decision

Keep `cache-large` as a focused allocator optimization and an explicit
throughput/RSS tradeoff control. Do not promote any reuse policy to a default or
headline application mode yet. The next higher-value optimization/evaluation
work is:

1. audit remaining generic allocation paths where profiles still show
   allocation lowering is material;
2. continue compiler-proven constructor/field-store/no-zero lowering;
3. simplify traversal/capsule paths where profiles show application CPU;
4. search for retained-object GC-heavy workloads identified in
   `evidence/GC_HEAVY_BENCHMARK_INVESTIGATION.md`.
