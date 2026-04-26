# Rift All-Phase Results Rollup

Date: 2026-04-26

This file gathers the current numeric and validation evidence across all
roadmap phases. It is a rollup, not the primary raw log. Prefer the source files
listed below for command provenance and detailed interpretation.

## Source Files

| Area | Source |
|---|---|
| Phase 0 baselines | `evidence/PHASE0_BASELINES.md` |
| Phase 1 bootstrap allocator | `/Users/siyaoliu/rift/rift-bootstrap/bench/microbench/results.md` |
| Phase 4 layout | `evidence/PHASE4_LAYOUT.md` |
| Phase 4 topology | `evidence/PHASE4_TOPOLOGY.md` |
| Phase 4 exit summary | `evidence/PHASE4_EXIT.md` |
| Phase 5 DEBS | `evidence/DEBS_RESULTS.md` |
| Phase 6 Broom-style dataflow | `evidence/DATAFLOW_REGION_MATRIX.md` |
| Phase 6 StreamFlex-style stream latency | `evidence/STREAMFLEX_REGION_MATRIX.md` |
| Phase 6 Yak-style control/data split | `evidence/YAK_REGION_MATRIX.md` |
| Phase 6 Stancu-style transaction accounting | `evidence/STANCU_REGION_MATRIX.md` |
| Phase 6 pipeline / parallel collections | `evidence/PIPELINE_PARCOLL_COMPARISON.md` |
| Current roadmap status | `docs/ROADMAP.md` |
| Handoff / caveats | `docs/HANDOFF.md` |

## Evidence Levels

| Level | Meaning |
|---|---|
| Validated | Multiple-run medians or passing tests with commands recorded. |
| Partially validated | Correctness or smoke validation exists, but broader coverage or medians are missing. |
| Provisional | Single-run, surrogate, uncommitted-patch, or reconstructed evidence. |
| Open | Planned work with no numeric evidence yet. |

## Phase Status Summary

| Phase | Status | Evidence level | Data in this rollup |
|---|---|---|---|
| Phase 0: baseline and comparison contract | Mostly complete, not sealed | Validated with caveats | GCBench, ListOfLists, GCBench topology, pipeline surrogate |
| Phase 1: standalone allocator bootstrap | Done as provenance | Validated bootstrap microbench | C allocator microbench |
| Phase 2: in-tree runtime/compiler path | Partially done | Partially validated | RiftRegionTest and integration status, no standalone perf table |
| Phase 3: runtime-only evaluation | Done enough for current claim | Validated with caveats | Same-layout GCBench/ListOfLists runtime medians |
| Phase 4: topology/layout decomposition | Done enough to move on | Validated/provisional mix | Layout, topology, targeted runtime follow-up, safety finding |
| Phase 5: application evidence | In progress | Partially validated/provisional | DEBS correctness and single-run instrumented matrices |
| Phase 6: literature-aligned methodology evidence | Started | Validated methodology medians with caveats | Broom-style dataflow, StreamFlex-style latency/throughput, Yak-style control/data, Stancu-style transaction accounting |
| Phase 6b: Broom / parallel collections API evidence | Open | Provisional surrogate only | amordo comparison and Rift raw-array surrogate |
| Phase 7: capture-checked safe API | Started | Compiler-probe evidence, no benchmark data | 24 targeted checked-API compiler probes plus Phase 4 safety finding |
| Phase 8: native GC/region integration hardening | Started | Runtime/API smoke evidence, no benchmark data | Explicit `HeapRoot` path plus direct unrooted heap-constructor/alias/field-selection/array-store rejection and explicit `{region}` constructor-field/array reuse |
| Phase 9: Lean mechanization | Open | No data | None |
| Phase 10: writing | Not started beyond notes | No data | None |

## Phase 0: Baselines

Environment:

- `ENABLE_EXPERIMENTAL_COMPILER=1`
- `JAVA_HOME="$(cs java-home --jvm temurin:17)"`
- Scala Native project: `sandbox3_next`
- Phase 0 source commit recorded as `ddbba577aecd4c0adc741cbf7085ee93548c46b4`

### GCBench

Config:

- stretch depth `18`
- long-lived depth `16`
- array size `500000`
- min depth `4`
- max depth `16`
- depth step `2`
- batch size `1`
- runs `5`

| Mode | Key env | Median ms |
|---|---|---:|
| Immix heap | `-` | 203.514 |
| current SafeZone | `SAFEZONE_ROOTS_MODE=0` | 684.517 |
| improved SafeZone | `SAFEZONE_ROOTS_MODE=1` | 223.770 |
| Rift HPZone | `-` | 161.641 |

### BenchmarkListOfLists

Workload:

- `n=3000`
- `structures=40`
- runs `5`
- linked outer and inner lists
- each inner element has a separate `BasicObject`

| Mode | Key env | Median ms |
|---|---|---:|
| Immix heap | `-` | 15085.511 |
| current SafeZone | `SAFEZONE_ROOTS_MODE=0` | 138171.998 |
| improved SafeZone | `SAFEZONE_ROOTS_MODE=1` | 10132.854 |
| Rift HPZone | `-` | 6951.331 |

### GCBench Topology Rerun

Config:

- runs `5`
- `SAFEZONE_PAGE_SIZE=4096`
- `SAFEZONE_BATCH_SIZE=1`
- topology A: long-lived tree on GC heap, short-lived trees in inner SafeZones
- topology B: long-lived tree in outer SafeZone, short-lived trees in inner SafeZones

| Mode | Key env | Median ms |
|---|---|---:|
| heap baseline | `SAFEZONE_PAGE_SIZE=4096 SAFEZONE_BATCH_SIZE=1` | 213.082 |
| current SafeZone topology A | `SAFEZONE_ROOTS_MODE=0 SAFEZONE_PAGE_SIZE=4096 SAFEZONE_BATCH_SIZE=1` | 236.542 |
| current SafeZone topology B | `SAFEZONE_ROOTS_MODE=0 SAFEZONE_PAGE_SIZE=4096 SAFEZONE_BATCH_SIZE=1` | 635.247 |
| improved SafeZone topology A | `SAFEZONE_ROOTS_MODE=1 SAFEZONE_PAGE_SIZE=4096 SAFEZONE_BATCH_SIZE=1` | 211.319 |
| improved SafeZone topology B | `SAFEZONE_ROOTS_MODE=1 SAFEZONE_PAGE_SIZE=4096 SAFEZONE_BATCH_SIZE=1` | 436.749 |

### Cleaned Pipeline Surrogate

Config:

- `PIPELINE_SIZE=2000000`
- `PIPELINE_WORKERS=4`
- `PIPELINE_WARMUPS=1`
- runs `5`

| Mode | Key env | Median ms |
|---|---|---:|
| heap baseline | `PIPELINE_SIZE=2000000 PIPELINE_WORKERS=4` | 4.924 |
| current SafeZone pipeline | `SAFEZONE_ROOTS_MODE=0 PIPELINE_SIZE=2000000 PIPELINE_WORKERS=4` | 5.344 |
| improved SafeZone pipeline | `SAFEZONE_ROOTS_MODE=1 PIPELINE_SIZE=2000000 PIPELINE_WORKERS=4` | 5.055 |
| Rift HPZone pipeline | `PIPELINE_SIZE=2000000 PIPELINE_WORKERS=4` | 5.089 |

Caveat: this is a cleaned surrogate, not a tracked-source reproduction of the
old pipeline benchmark.

## Phase 1: Standalone Allocator Bootstrap

Source: `/Users/siyaoliu/rift/rift-bootstrap/bench/microbench/results.md`

Command:

```sh
cd /Users/siyaoliu/rift/rift-bootstrap
make -C native clean bench
./bench/microbench/microbench
```

Environment:

- compiler: `clang`
- flags: `-O2 -march=native -Wall -Werror -std=c11 -fPIC`

| Benchmark | Mode | p50 | p99 |
|---|---|---:|---:|
| per-allocation | `malloc/free` | 11.3 ns/alloc | 13.9 ns/alloc |
| per-allocation | `rift HPZone` | 2.1 ns/alloc | 2.9 ns/alloc |
| close path, total for 100000 allocations | `malloc/free` | 1210000 ns | 1507000 ns |
| close path, total for 100000 allocations | `rift HPZone` | 3000 ns | 11000 ns |

Caveat: this is bootstrap provenance only. Active implementation work is in the
Scala Native fork, not `rift-bootstrap`.

## Phase 2: In-Tree Runtime And Compiler Path

Numeric benchmark table: none specific to Phase 2.

Recorded validation:

| Item | Status |
|---|---|
| `RiftRuntime.c/h` in-tree runtime path | Partially done |
| `RiftRegion` Scala API surface | Partially done |
| compiler lowering for `region.alloc(new T(...))` | Partially done |
| `RiftRegionTest` | recorded as passing `5/5` |
| stats ABI / header cleanup | still open |
| full Scala Native test suite | not recorded |

## Phase 3: Runtime-Only Evaluation

Phase 3 uses the same-layout runtime matrices recorded in Phase 0. The current
supported runtime-only claim is restricted to these workloads.

| Benchmark | Immix heap ms | current SafeZone ms | improved SafeZone ms | Rift HPZone ms |
|---|---:|---:|---:|---:|
| GCBench | 203.514 | 684.517 | 223.770 | 161.641 |
| ListOfLists linked | 15085.511 | 138171.998 | 10132.854 | 6951.331 |

Interpretation:

- Rift HPZone is fastest on these same-layout runtime-only matrices.
- Improved SafeZone materially changes the baseline and must be included.
- Pipeline evidence remains a surrogate and should not be treated as a Phase 3
  API-level win.

## Phase 4: Layout Decomposition

Source: `evidence/PHASE4_LAYOUT.md`

Worktree caveat:

- The layout numbers use local runtime changes in `RiftRuntime.c`.
- Fresh mmapped slabs skip redundant zeroing.
- Huge slabs avoid the synchronous `MAP_POPULATE` plus `MADV_HUGEPAGE` path.
- Reused regular slabs are zeroed once when acquired.
- `reset` zeroes the retained first slab before rewinding.

### Layout Medians

| Mode | Linked median ms | Chunked median ms | Flat median ms |
|---|---:|---:|---:|
| Immix heap | 15260.875 | 2636.480 | 1766.295 |
| current SafeZone | 136016.922 | 4835.904 | 1735.453 |
| improved SafeZone | 9824.936 | 2369.108 | 1743.161 |
| Rift HPZone | 7278.150 | 2463.674 | 1515.091 |

### Layout Speedup Versus Linked Baseline

| Mode | Linked / chunked | Linked / flat |
|---|---:|---:|
| Immix heap | 5.789x | 8.640x |
| current SafeZone | 28.129x | 78.375x |
| improved SafeZone | 4.147x | 5.636x |
| Rift HPZone | 2.954x | 4.804x |

### Chunked Samples

| Mode | Samples ms | Median ms |
|---|---|---:|
| Immix heap | `2599.345, 2631.367, 2636.480, 2671.267, 2729.787` | 2636.480 |
| current SafeZone | `4797.329, 4828.114, 4835.904, 4844.056, 4850.852` | 4835.904 |
| improved SafeZone | `2356.089, 2364.000, 2369.108, 2377.596, 2390.583` | 2369.108 |
| Rift HPZone | `2447.758, 2453.996, 2463.674, 2480.406, 2634.740` | 2463.674 |

### Flat Samples

| Mode | Samples ms | Median ms |
|---|---|---:|
| Immix heap | `1673.328, 1681.196, 1766.295, 1942.462, 2234.381` | 1766.295 |
| current SafeZone | `1720.359, 1721.386, 1735.453, 1748.697, 2038.046` | 1735.453 |
| improved SafeZone | `1736.687, 1737.146, 1743.161, 1752.375, 1772.330` | 1743.161 |
| Rift HPZone | `1508.332, 1511.957, 1515.091, 1528.668, 1549.264` | 1515.091 |

### Runtime Fix Effects

| Finding | Before | After | Change |
|---|---:|---:|---:|
| flat Rift median | 15468.496 ms | 1515.091 ms | 10.210x faster |
| chunked Rift median | 2489.530 ms | 2463.674 ms | 1.010x faster |

### Targeted Front-Path Follow-Up

| Layout | Previous Rift median ms | Follow-up Rift median ms | Change |
|---|---:|---:|---:|
| Linked | 7278.150 | 6638.949 | 1.096x faster |
| Chunked | 2463.674 | 2390.390 | 1.031x faster |

| Layout | Runs | Samples ms | Median ms |
|---|---:|---|---:|
| Linked | 3 | `6594.762, 6638.949, 6748.837` | 6638.949 |
| Chunked | 3 | `2388.869, 2390.390, 2444.058` | 2390.390 |

## Phase 4: Topology Decomposition

Source: `evidence/PHASE4_TOPOLOGY.md`

### Medium Topology Results

Config:

- `LISTBENCH_N=1000`
- `LISTBENCH_STRUCTURES=10`
- `LISTBENCH_BENCHMARK_RUNS=3`

| Mode | Topology | Median ms | Samples ms |
|---|---|---:|---|
| Immix heap | full heap graph | 439.726 | `435.604, 439.726, 587.636` |
| current SafeZone | one-region | 680.573 | `677.231, 680.573, 682.756` |
| current SafeZone | nested | 274.131 | `273.128, 274.131, 277.934` |
| current SafeZone | mixed rooted heap-values | 430.501 | `422.986, 430.501, 459.668` |
| improved SafeZone | one-region | 267.049 | `266.148, 267.049, 274.443` |
| improved SafeZone | nested | 273.335 | `273.195, 273.335, 274.984` |
| improved SafeZone | mixed rooted heap-values | 274.278 | `273.265, 274.278, 298.503` |
| Rift HPZone | one-region | 199.429 | `198.963, 199.429, 208.259` |
| Rift HPZone | nested | 206.730 | `206.014, 206.730, 211.459` |
| Rift HPZone | mixed rooted heap-values | 337.418 | `306.932, 337.418, 407.252` |

### Report-Scale Topology Results

Config:

- `LISTBENCH_N=3000`
- `LISTBENCH_STRUCTURES=40`
- `LISTBENCH_BENCHMARK_RUNS=3`

| Mode | Topology | Median ms | Samples ms |
|---|---|---:|---|
| Immix heap | full heap graph | 14755.580 | `14704.328, 14755.580, 16224.723` |
| current SafeZone | one-region | 136016.922 | from linked 5-run baseline; skipped here |
| current SafeZone | nested | 10289.097 | `10275.936, 10289.097, 10305.335` |
| current SafeZone | mixed rooted heap-values | 55554.702 | `55108.631, 55554.702, 55558.918` |
| improved SafeZone | one-region | 9767.048 | `9743.167, 9767.048, 9787.080` |
| improved SafeZone | nested | 9929.699 | `9912.121, 9929.699, 9933.331` |
| improved SafeZone | mixed rooted heap-values | 9877.914 | `9870.536, 9877.914, 10611.134` |
| Rift HPZone | one-region | 7256.426 | `7251.278, 7256.426, 7300.764` |
| Rift HPZone | nested | 7314.201 | `7295.217, 7314.201, 7372.917` |
| Rift HPZone | mixed rooted heap-values | 11695.748 | `10716.691, 11695.748, 11829.713` |

### Phase 4 Safety Finding

The first unrooted Rift mixed topology failed:

```text
CHECKSUM_MISMATCH name=rift-mixed actual=13763975568 expected=9990000000
```

Interpretation:

- Rift regions are not scanned by the GC.
- Region objects must not be the only references keeping GC heap objects alive.
- Mixed GC-plus-region setups need explicit heap roots, GC-scanned region
  metadata, or the opposite reference direction.
- This finding is input to Phase 7 and Phase 8.

## Phase 5: DEBS 2015 Application Evidence

Source: `evidence/DEBS_RESULTS.md`

Global caveat:

- These are application-harness results, not final Phase 5 headline numbers.
- Most DEBS rows are single-run measurements, not medians.
- Heap and Rift outputs match after stripping only the measured latency column
  in the recorded matrix runs.
- Raw monthly DEBS files are not monotonic by dropoff timestamp; bounded
  samples use joined streams sorted by dropoff time.

### Real-Data RunBoth

| Input | Mode | Events | Parsed | Elapsed ms | Throughput events/s | Q1 p99.9 ms | Q1 max ms | Q2 p99.9 ms | Q2 max ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 10k | heap | 10000 | 10000 | 243.575 | 41055.173 | 0 | 3 | 1 | 3 |
| 10k | Rift HPZone | 10000 | 10000 | 251.410 | 39775.738 | 0 | 0 | 1 | 8 |
| 10k | Rift Streaming | 10000 | 10000 | 241.298 | 41442.582 | 0 | 0 | 1 | 3 |
| 100k | heap | 100000 | 100000 | 2087.796 | 47897.405 | 0 | 0 | 1 | 1 |
| 100k | Rift HPZone | 100000 | 100000 | 2128.833 | 46974.086 | 0 | 3 | 1 | 10 |
| 100k | Rift Streaming | 100000 | 100000 | 2131.800 | 46908.722 | 0 | 3 | 1 | 1 |
| 1M | heap | 1000000 | 1000000 | 21658.215 | 46171.857 | 0 | 92 | 2 | 69 |
| 1M | Rift HPZone | 1000000 | 1000000 | 22314.989 | 44812.928 | 0 | 1 | 2 | 37 |
| 1M | Rift Streaming | 1000000 | 1000000 | 22184.467 | 45076.585 | 0 | 45 | 2 | 94 |

Notes:

- The first 100k heap attempt with full rescans/sorts took `246360.864 ms`
  (`405.909 events/s`).
- Incremental ranking made the 100k matrix practical.

### Instrumented RunBoth Baseline

| Input | Mode | Elapsed ms | Throughput events/s | GC collections | GC time ms | Rift op ms | Rift alloc objects | Rift opens/closes | Rift mmap bytes | Peak RSS bytes |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 100k | heap | 2018.887 | 49532.241 | 8 | 86.696 | 0.000 | 0 | 0 / 0 | 0 | 348684288 |
| 100k | Rift HPZone | 2021.861 | 49459.394 | 8 | 83.432 | 1.036 | 98005 | 1513 / 1513 | 1015808 | 343670784 |
| 100k | Rift Streaming | 2018.424 | 49543.610 | 8 | 83.035 | 1.004 | 98005 | 1513 / 1513 | 1015808 | 343638016 |
| 1M | heap | 22827.882 | 43806.080 | 21 | 1051.752 | 0.000 | 0 | 0 / 0 | 0 | 1148780544 |
| 1M | Rift HPZone | 22366.285 | 44710.151 | 21 | 1003.171 | 9.350 | 979699 | 10730 / 10730 | 3342336 | 1152122880 |
| 1M | Rift Streaming | 22810.687 | 43839.101 | 21 | 1012.489 | 10.390 | 979699 | 10730 / 10730 | 3342336 | 1152122880 |

### Parser Fast-Path And Reusable Trip

| Run | Mode | Elapsed ms | Throughput events/s | GC collections | GC time ms | Rift op ms | Rift alloc objects | Rift opens/closes | Rift mmap bytes | Peak RSS bytes |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 100k scanner parser | heap | 1747.245 | 57232.949 | 8 | 82.372 | 0.000 | 0 | 0 / 0 | 0 | 289832960 |
| 100k scanner parser | Rift HPZone | 1740.999 | 57438.279 | 8 | 79.988 | 0.931 | 98005 | 1513 / 1513 | 1015808 | 290881536 |
| 100k scanner parser | Rift Streaming | 1737.477 | 57554.730 | 8 | 81.272 | 0.933 | 98005 | 1513 / 1513 | 1015808 | 290881536 |
| 1M scanner parser | heap | 18705.857 | 53459.192 | 20 | 814.550 | 0.000 | 0 | 0 / 0 | 0 | 1148502016 |
| 1M scanner parser | Rift HPZone | 18655.414 | 53603.742 | 19 | 737.705 | 6.452 | 979699 | 10730 / 10730 | 3342336 | 1123303424 |
| 1M scanner parser | Rift Streaming | 18684.802 | 53519.433 | 19 | 731.286 | 6.255 | 979699 | 10730 / 10730 | 3342336 | 1121910784 |
| 100k reusable trip | heap | 1829.605 | 54656.601 | 8 | 83.608 | 0.000 | 0 | 0 / 0 | 0 | 289849344 |
| 100k reusable trip | Rift HPZone | 1869.124 | 53501.013 | 8 | 87.922 | 1.207 | 98005 | 1513 / 1513 | 1015808 | 290897920 |
| 100k reusable trip | Rift Streaming | 1836.948 | 54438.121 | 8 | 82.415 | 1.098 | 98005 | 1513 / 1513 | 1015808 | 290897920 |
| 1M reusable trip | heap | 18744.558 | 53348.818 | 19 | 758.444 | 0.000 | 0 | 0 / 0 | 0 | 1056587776 |
| 1M reusable trip | Rift HPZone | 18533.989 | 53954.926 | 19 | 738.969 | 6.034 | 979699 | 10730 / 10730 | 3342336 | 1012613120 |
| 1M reusable trip | Rift Streaming | 18662.839 | 53582.417 | 18 | 779.228 | 5.923 | 979699 | 10730 / 10730 | 3342336 | 1151827968 |

Interpretation:

- Scanner parser improved all modes.
- Reusable trip did not produce a stable elapsed-time win in single runs.
- These are shared noise-reduction changes, not Rift-specific application
  wins.

### Shared Q1/Q2 Region Placement Steps

| Step | Mode | Elapsed ms | Throughput events/s | GC collections | GC time ms | Rift op ms | Rift alloc objects | Rift opens/closes | Rift mmap bytes | Peak RSS bytes |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 100k shared Q1 buckets | heap | 1860.007 | 53763.236 | 8 | 85.489 | 0.000 | 0 | 0 / 0 | 0 | 289849344 |
| 100k shared Q1 buckets | Rift HPZone | 1837.997 | 54407.064 | 8 | 82.502 | 1.111 | 98005 | 1513 / 1513 | 1015808 | 290881536 |
| 100k shared Q1 buckets | Rift Streaming | 1833.573 | 54538.332 | 8 | 81.977 | 1.090 | 98005 | 1513 / 1513 | 1015808 | 290881536 |
| 100k shared Q2 windows | heap | 1837.501 | 54421.745 | 8 | 90.119 | 0.000 | 0 | 0 / 0 | 0 | 289832960 |
| 100k shared Q2 windows | Rift HPZone | 1794.929 | 55712.509 | 8 | 80.709 | 2.323 | 294284 | 4545 / 4545 | 2555904 | 292372480 |
| 100k shared Q2 windows | Rift Streaming | 1843.627 | 54240.908 | 8 | 85.730 | 2.479 | 294284 | 4545 / 4545 | 2555904 | 292388864 |
| 100k Q2 profit entries source of truth | heap | 1816.773 | 55042.642 | 8 | 88.809 | 0.000 | 0 | 0 / 0 | 0 | 289816576 |
| 100k Q2 profit entries source of truth | Rift HPZone | 1791.195 | 55828.658 | 8 | 82.747 | 2.421 | 294284 | 4545 / 4545 | 2555904 | 292372480 |
| 100k Q2 profit entries source of truth | Rift Streaming | 1802.942 | 55464.905 | 8 | 83.438 | 2.676 | 294284 | 4545 / 4545 | 2555904 | 292356096 |

### Q2 Median Scratch

| Step | Mode | Elapsed ms | Throughput events/s | GC collections | GC time ms | Rift op ms | Rift alloc objects | Rift resets | Rift opens/closes | Rift mmap bytes | Peak RSS bytes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 100k per-median scratch reset | heap | 1881.304 | 53154.619 | 8 | 89.754 | 0.000 | 0 | 0 | 0 / 0 | 0 | 289767424 |
| 100k per-median scratch reset | Rift HPZone | 1920.875 | 52059.615 | 8 | 83.657 | 52.162 | 465481 | 171197 | 4546 / 4546 | 2588672 | 292405248 |
| 100k per-median scratch reset | Rift Streaming | 1937.911 | 51601.955 | 8 | 83.435 | 52.375 | 465481 | 171197 | 4546 / 4546 | 2588672 | 292388864 |
| 100k per-trip scratch reset | heap | 1748.744 | - | - | 84.364 | 0.000 | 0 | 0 | - | - | 289816576 |
| 100k per-trip scratch reset | Rift HPZone | 1775.350 | - | - | 79.702 | 28.004 | 465481 | 87438 | - | - | 292421632 |
| 100k per-trip scratch reset | Rift Streaming | 1768.716 | - | - | 78.562 | 27.830 | 465481 | 87438 | - | - | 292438016 |

Interpretation:

- Per-trip scratch reset cut Rift resets from `171197` to `87438`.
- Rift region-operation time dropped from about `51.5 ms` to about `28 ms`.

### Phase Breakdown Before Scratch Batching

| Mode | Elapsed ms | Read % | Parse % | Q1 process % | Q1 output % | Q2 process % | Q2 output % | GC % | Rift op % | Rift resets |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 1857.565 | 15.8 | 7.0 | 13.2 | 4.3 | 48.4 | 9.2 | 4.8 | 0.0 | 0 |
| Rift HPZone | 1897.927 | 15.4 | 6.9 | 14.5 | 3.3 | 48.2 | 9.5 | 4.5 | 2.7 | 171197 |
| Rift Streaming | 1906.186 | 15.3 | 6.8 | 13.8 | 3.4 | 49.6 | 9.1 | 4.5 | 2.7 | 171197 |

Interpretation:

- Q2 processing is the dominant measured phase at roughly `48-50%`.
- Read plus parse is about `22%`.
- Q2 output is about `9%`.
- GC and Rift bookkeeping are not the sole bottlenecks.

### Primitive Q2 Ranking Keys

| Mode | Elapsed ms | Q2 process ms | Q2 output ms | GC ms | Rift op ms | Rift resets | Region objects | Peak RSS bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 1813.074 | 880.566 | 155.863 | 90.540 | 0.000 | 0 | 0 | 289816576 |
| Rift HPZone | 1863.806 | 909.965 | 160.252 | 84.775 | 28.815 | 87438 | 465481 | 292421632 |
| Rift Streaming | 1832.249 | 895.328 | 156.544 | 82.728 | 28.681 | 87438 | 465481 | 292405248 |

Caveat: this is a fairness/noise cleanup, not a Rift-specific win. It removes
accidental heap `Cell` and cell-id string allocation from the shared Q2 path.

### Latest DEBS Placement Checkpoints

Source of truth: `evidence/DEBS_RESULTS.md`. The rollup below records the
latest median-backed bounded-sample checkpoints after the reusable ranking,
bounded table, taxi-id, output-snapshot, and Q2 incremental-median work.

| Checkpoint | Mode | Elapsed ms | GC ms | Q1 process ms | Q2 process ms | Q2 output ms | Rift op ms | Region objects | Peak RSS bytes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1M output snapshots | heap | 8983.464 | 290.712 | 1253.609 | 5393.901 | 323.657 | 0.000 | 0 | 431652864 |
| 1M output snapshots | Rift HPZone | 8815.087 | 292.155 | 1209.080 | 5221.554 | 337.780 | 10.053 | 5561840 | 119865344 |
| 1M output snapshots | Rift Streaming | 8836.488 | 296.305 | 1216.835 | 5233.309 | 349.659 | 10.061 | 5561840 | 119898112 |
| 1M Q2 incremental medians | heap | 5976.447 | 67.086 | 1387.651 | 2027.508 | 419.937 | 0.000 | 0 | 305758208 |
| 1M Q2 incremental medians | Rift HPZone | 5794.879 | 59.658 | 1351.446 | 1905.210 | 377.610 | 10.737 | 5494550 | 113950720 |
| 1M Q2 incremental medians | Rift Streaming | 5948.755 | 55.056 | 1403.377 | 1922.138 | 386.790 | 11.172 | 5494550 | 113934336 |

Common Q2 incremental-median diagnostics at 1M:

| Q2 rank fixes | Median sort computes | Median values sorted | Median reads | Median heap adds | Median heap removes | Median rebalances |
|---:|---:|---:|---:|---:|---:|---:|
| 3252279 | 0 | 0 | 3320865 | 981885 | 981883 | 898934 |

Interpretation:

- Q2 incremental medians are now median-backed, not only a single-run
  diagnostic.
- The improvement is shared algorithmic cleanup plus allocation placement:
  heap and Rift use the same two-heap median maintenance, while Rift allocates
  the median/control arrays and related ordinary Scala objects in regions.
- Rift still does not prove final DEBS success because SafeZone/Commix,
  full-month scale, and safe API boundaries remain open. The remaining DEBS
  bottleneck is Q2 rank/output work rather than Rift allocator overhead.

## Phase 6: Literature-Aligned Methodology Evidence

Sources:

- `evidence/DATAFLOW_REGION_MATRIX.md`
- `evidence/STREAMFLEX_REGION_MATRIX.md`
- `evidence/YAK_REGION_MATRIX.md`
- `evidence/STANCU_REGION_MATRIX.md`

These are local methodology reproductions. They do not claim the original
Broom/Naiad, StreamFlex/Ovm, Yak/Hyracks/Hadoop/GraphChi, or Stancu/SPECjbb2005
artifacts are available or reproduced.

### Latest Interpretable Signals

| Literature shape | Local harness | Best current Rift signal | Main caveat |
|---|---|---|---|
| Broom dataflow vertices | SELECT/AGGREGATE/JOIN over ordinary epoch-local Scala objects | Post-counter-fix 10 x 100k medians show HPZone ahead of heap and improved SafeZone on SELECT, AGGREGATE, and JOIN; Broom-scale 40 x 500k is still single-run. | Methodology reproduction, not exact Naiad/Broom. |
| StreamFlex stream latency | Throughput and per-event latency/deadline-miss workloads | Pressure rerun shows Rift throughput around `330 ms` vs heap `634 ms`; Streaming has zero deadline misses in that run. | Does not run StreamIt/Ovm kernels or model scheduler/queueing delay. |
| Yak control/data split | Wordcount and graphstep epoch-local data objects with durable heap control state | Pressure rerun shows Streaming near improved SafeZone and faster than heap: `199.156 ms` vs heap `243.522 ms` on wordcount, `209.528 ms` vs heap `240.890 ms` on graphstep. | Not distributed Yak and no dynamic promotion/write barrier. |
| Stancu transaction accounting | Warehouse transaction-shaped object graph with durable heap state | Boundary sweep confirms a Rift-vs-heap win only when transaction regions are coarse enough: at 200k transactions, 64 tx/region gives Streaming `38.844 ms` vs heap `43.189 ms`. | Not SPECjbb2005 or static analysis; SafeZone remains faster. |

### Stancu Boundary Sweep, 2026-04-26

Configuration:

- `STANCU_TRANSACTIONS=200000`
- `STANCU_ITEMS_PER_TX=8`
- `STANCU_WAREHOUSES=64`
- `STANCU_PRODUCTS=4096`
- runs `3`, warmups `1`

| Tx per region | Heap ms | Improved SafeZone ms | Rift HPZone ms | Rift Streaming ms | Rift Streaming op ms | Interpretation |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 44.592 | 62.564 | 63.257 | 50.487 | 3.922 | Too fine-grained; Rift does not beat heap. |
| 64 | 43.189 | 37.057 | 39.522 | 38.844 | 0.060 | Best measured boundary; Rift beats heap but not SafeZone. |
| 512 | 45.315 | 38.436 | 40.025 | 39.717 | 0.065 | Still a Rift-vs-heap win, but not better than 64. |

The Stancu-style evidence should therefore be described as a coarse-boundary
Rift-vs-heap accounting result. It is not evidence that a high
region-candidate object fraction alone is enough, and it is not a static
annotation/inference result.

## Phase 6b: Broom / Parallel Collections API Evidence

Source: `evidence/PIPELINE_PARCOLL_COMPARISON.md`

### amordo `BroomPipelineBenchmark`

Config:

- records: `100000`
- keys: `64`
- runs: `5`

| Mode | Samples ms | Median ms |
|---|---|---:|
| ZoneParVector explicit stage release | `56.981, 58.105, 55.068, 54.566, 53.553` | 55.07 |
| on-heap ParVector | `24.349, 27.479, 31.290, 37.257, 30.753` | 30.75 |
| ZoneParVector region per stage | `30.360, 30.689, 31.898, 29.868, 29.758` | 30.36 |

### Rift Raw-Array Pipeline Surrogate

Config:

- `PIPELINE_SIZE=100000`
- `PIPELINE_KEYS=64`
- `PIPELINE_BENCHMARK_RUNS=5`
- `PIPELINE_WARMUPS=1`

| Mode | Samples ms | Median ms |
|---|---|---:|
| Immix heap raw arrays | `1.771, 1.831, 1.845, 1.870, 1.888` | 1.845 |
| current SafeZone raw arrays | `1.962, 1.969, 1.976, 2.113, 2.114` | 1.976 |
| improved SafeZone raw arrays | `1.884, 1.906, 1.907, 1.915, 1.999` | 1.907 |
| Rift HPZone raw arrays | `2.487, 2.490, 2.502, 2.593, 2.705` | 2.502 |
| Rift Streaming raw arrays | `2.505, 2.549, 2.652, 2.838, 2.881` | 2.652 |

Caveat:

- The raw-array Rift pipeline is not apples-to-apples with
  `ZoneParVector`/`ParVector`.
- The fair next comparison requires a `RiftParVector` or equivalent API-level
  region-backed collection.

## Phase 7: Capture-Checked Safe API

Numeric benchmark data: none yet. Compiler-probe evidence now exists for the
first checked API slice.

Targeted command:

```bash
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"
```

Result on 2026-04-26:

```text
Passed: Total 29, Failed 0, Errors 0, Passed 29
```

Runtime smoke command:

```bash
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionTest scala.scalanative.memory.RiftRegionCheckedTest"
```

Result on 2026-04-26:

```text
Passed: Total 12, Failed 0, Errors 0, Passed 12
```

Covered source-level patterns:

| Pattern | Evidence |
|---|---|
| scoped ordinary object graph | passes compiler probe |
| scoped for-loop allocation | passes compiler probe |
| nested scoped regions returning pure values | passes compiler probe |
| local higher-order consumer of region value | passes compiler probe |
| non-escaping closure using scoped value | passes compiler probe |
| scoped value returned from scope | rejected |
| inner-region value escaping outer scope | rejected |
| heap singleton retaining scoped value | rejected |
| closure stored in heap state while capturing region handle | rejected |
| closure returned from checked scoped region | rejected conservatively by direct function-result guard |
| region object stores heap metadata via `HeapRoot` | passes compiler probe and native runtime smoke |
| direct unrooted heap object stored through checked Rift allocation constructor | rejected |
| local alias of known region value stored through checked Rift allocation constructor | passes compiler probe |
| local alias of heap object stored through checked Rift allocation constructor | rejected |
| field selected from heap object stored through checked Rift allocation constructor | rejected |
| stable constructor field explicitly captured by `{region}` reused through checked Rift allocation constructor | passes compiler probe |
| local alias of stable constructor field explicitly captured by `{region}` reused through checked Rift allocation constructor | passes compiler probe |
| plain `T^` field selected from region owner reused where `T^{region}` is required | rejected by Scala capture checking |
| region-owned array with explicitly captured element type stored through checked Rift allocation constructor | passes compiler probe |
| region-owned array stores region object | passes compiler probe |
| region-owned array stores unrooted heap object | rejected by Rift array-store guard |
| heap array stored through checked Rift allocation constructor | rejected |
| region-owned array stores explicit `HeapRoot` handle | passes compiler probe and native runtime smoke |
| explicit-owner `ObjectBuffer` stores region objects | passes compiler probe and native runtime smoke |
| explicit-owner `ObjectBuffer` stores direct heap object | rejected by Rift append lowering guard |
| explicit-owner `ObjectBuffer` stores `HeapRoot` handle | passes compiler probe and native runtime smoke |
| outer `ObjectBuffer` stores inner-region value | rejected by explicit owner-token type |
| checked `ObjectBuffer` escapes owning region | rejected |
| streaming reset value escaping epoch | rejected |

Relevant evidence carried from Phase 4:

| Finding | Data |
|---|---|
| unrooted mixed Rift topology failed | `CHECKSUM_MISMATCH name=rift-mixed actual=13763975568 expected=9990000000` |
| implication | capture/safe API must reject or specially handle unrooted region-to-GC references |

Open work:

- Returned closures are rejected conservatively; precise support for pure
  returned functions remains open.
- Explicit `HeapRoot` handles now cover the safe region-to-GC metadata path.
  Direct unrooted heap-object constructor arguments are now rejected in checked
  Rift allocation lowering; simple region-local aliases are propagated, while
  heap aliases and heap field selections are rejected. Stable constructor
  fields explicitly captured by `{region}` are accepted. Region-owned arrays
  are accepted when reference elements are explicitly captured, and stores into
  known region arrays reject unrooted heap objects. `RiftRegion.ObjectBuffer`
  is now a checked but explicit-owner first container primitive: it keeps heap
  control metadata, region-allocates the backing object array, and requires
  calls such as `RiftRegion.append(region, buffer, value)`. Plain `T^`
  selected fields, static immutable heap referents, and ergonomic method-style
  containers still need a more complete mixed-reference policy or ergonomics
  story.
- Most diagnostic strings are not pinned to capture-specific text yet.
- Broader runtime tests and mixed-reference tests remain open.

## Phase 8: Native GC/Region Integration Hardening

Numeric benchmark data: none yet. Runtime/API smoke evidence exists for the
explicit-root path, and compiler evidence exists for the direct unrooted
heap-object constructor-argument/alias/field-selection/array-store rejection
and explicit `{region}` constructor-field/array reuse.

Known design constraint:

- Rift region memory is not GC-scanned.
- `RiftRegion.root(value)` creates a `HeapRoot[T]` retained by a GC-visible list
  on the live region object and cleared on reset/close.
- Region-to-GC references need explicit roots, scanning, or rejection. The
  current checked lowering rejects direct unrooted heap-object constructor
  arguments, simple heap aliases, and heap field selections, and it propagates
  simple aliases of known region values. It allows stable constructor fields
  whose source type is explicitly captured by `{region}`. It does not yet model
  plain `T^` selected fields or static immutable referents. Region-owned arrays
  require explicit element capture such as `Array[T^{region}]^{region}`; more
  general container provenance remains open.
- The Phase 4 mixed-topology checksum mismatch is the current concrete
  evidence for this risk.

Open decisions:

- Decide how far to extend static rejection for region-to-GC references.
- Root heap objects explicitly.
- Add GC-scanned region metadata.
- Restrict allowed reference directions.

## Phase 9: Lean Mechanization

Numeric data: none.

Status:

- Design target only in the active fork.
- Older proof pack is not active in the Scala Native fork.
- Required future results are proof artifacts, not runtime measurements.

## Phase 10: Writing

Numeric data: none.

Status:

- Handoff, roadmap, design, and this result rollup exist.
- Paper/thesis claims should wait for stronger Phase 5, Phase 7, and Phase 9
  evidence.

## Current Cross-Phase Takeaways

- Runtime-only Rift wins are credible on GCBench and linked ListOfLists.
- Improved SafeZone is a serious baseline and cannot be omitted.
- Layout and topology effects are large and must be separated from allocator
  effects.
- Mixed GC-plus-region data is safety-sensitive because Rift regions are not
  scanned by the GC.
- DEBS correctness is partially validated on bounded sorted real-data samples.
- DEBS now has stronger bounded-sample evidence after Q2 incremental medians:
  HPZone is faster than heap at 1M with much lower RSS, but this is still not
  final application evidence without SafeZone/Commix, full-month scale, and
  safe API controls.
- Latest DEBS phase breakdown shows Q2 rank/output work still dominates more
  than Rift bookkeeping alone.
- The pipeline/parallel-collections story is still a surrogate until a fair
  Rift-backed collection API exists.
