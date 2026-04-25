# DEBS JVM vs Scala Native Backend Note

Date: 2026-04-26

Evidence level: mixed. This is not a new Rift implementation branch and does
not change DEBS semantics.

- Validated checked-in evidence: the RunBoth heap/Rift output-snapshot medians
  in `scala-native-rift/bench/debs2015/RESULTS.md`; heap and Rift outputs
  matched after stripping only the measured latency column.
- Checked-in Java probe evidence: single-run and intentionally not DEBS Q1/Q2
  equivalent. Use it only for JVM GC/live-set intuition on the same bounded CSV
  inputs.
- New local same-Scala-source control: single-run and provisional. It compares
  heap mode only, with JVM no-op stubs for Scala Native APIs, and is meant to
  expose backend/runtime/library costs rather than Rift effects.

## Question

The JVM same-input comparison is much faster than Scala Native. The immediate
question is whether that is a GC-vs-region result or a backend/runtime/library
result.

## Controls Run

Inputs:

- `/tmp/debs2015-month1-100000.csv`
- `/tmp/debs2015-month1-1000000.csv`

Temporary same-Scala-source JVM control:

- copied `sandbox/src/main/scala-next/debs2015/*.scala` to
  `/tmp/debs-jvm-same-source`
- added no-op JVM stubs for `scala.scalanative.memory.RiftRegion`,
  `scala.scalanative.runtime.RiftAllocator`, and a `GC` stub backed by JVM
  `GarbageCollectorMXBean`
- ran heap mode only with Scala CLI `3.7.3` on Temurin 17
- compared outputs with the existing Scala Native binary after stripping only
  the measured latency column

The 100k and 1M JVM heap outputs matched the native heap outputs after removing
the latency column.

Native control:

- existing linked binary:
  `/Users/siyaoliu/rift/scala-native-rift/sandbox/.3-next/target/scala-3.8.4-RC1-bin-20260402-44bbcdf-NIGHTLY/native/debs2015.Debs2015RunBoth`
- heap mode only

Checked-in Java probe control:

- harness: `bench/debs2015/jvm/DebsJvmGcProbe.java`
- not the same Scala source and not full DEBS Q1/Q2 logic
- useful only for asking whether HotSpot necessarily spends large time in GC on
  the same bounded input shape

## Results

Single-run same-Scala-source control rows:

| Input | Backend | Elapsed ms | GC ms | Read ms | Parse ms | Q1 process ms | Q1 output ms | Q2 process ms | Q2 output ms | Q2 median computes | Q2 values sorted |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100k | JVM heap, same Scala source | 257.196 | 0.000 | 13.377 | 33.098 | 62.582 | 10.878 | 87.623 | 7.974 | 171197 | 1365087 |
| 100k | Scala Native heap | 945.495 | 21.151 | 42.780 | 111.986 | 160.746 | 59.328 | 460.578 | 68.182 | 171197 | 1365087 |
| 1M | JVM heap, same Scala source | 1690.157 | 2.000 | 80.299 | 199.858 | 376.286 | 48.374 | 792.539 | 49.598 | 1757976 | 19156244 |
| 1M | Scala Native heap | 11253.201 | 326.076 | 436.457 | 1165.136 | 1675.542 | 571.755 | 6612.424 | 390.369 | 1757976 | 19156244 |

Checked-in RunBoth output-snapshot 1M 3-run medians:

| Mode | Elapsed ms | GC ms | Q1 process ms | Q2 process ms | Rift op ms | Rift alloc objects | Peak RSS bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| heap | 8983.464 | 290.712 | 1253.609 | 5393.901 | 0.000 | 0 | 431652864 |
| Rift HPZone | 8815.087 | 292.155 | 1209.080 | 5221.554 | 10.053 | 5561840 | 119865344 |
| Rift Streaming | 8836.488 | 296.305 | 1216.835 | 5233.309 | 10.061 | 5561840 | 119898112 |

Checked-in Java probe single-run rows most relevant to this question:

| Input | JVM heap | Mode | Elapsed ms | GC collections | GC ms | Heap used bytes | Max window | Taxi IDs |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 1M | default | window | 532.061 | 8 | 6 | 126348456 | 9301 | 9244 |
| 1M | 8 MB | window | 1864.021 | 1109 | 1322 | 4358976 | 9301 | 9244 |

The direct 1M native same-source run was slower than the latest checked-in 1M
output-snapshot heap median (`11253.201 ms` vs `8983.464 ms`), but both native
numbers lead to the same diagnosis: GC is not large enough to explain the JVM
gap.

## Diagnosis

This is mainly a JVM-vs-Scala-Native backend/runtime/library gap, not a
GC-vs-region result.

- Native heap is already much slower than the same Scala query on the JVM:
  `945.495 ms` versus `257.196 ms` at 100k, and `11253.201 ms` versus
  `1690.157 ms` at 1M. Rift is not involved in that comparison.
- Subtracting measured GC still leaves almost the full gap. In the direct 1M
  control, native heap spent `326.076 ms` in GC out of `11253.201 ms`; JVM heap
  spent `2.000 ms` in GC out of `1690.157 ms`.
- Within Scala Native, the checked-in 1M heap/Rift medians do not show a
  GC-driven region win: heap GC was `290.712 ms`, Rift HPZone GC was
  `292.155 ms`, and Rift Streaming GC was `296.305 ms`. Region bookkeeping was
  `10.053 ms` for HPZone and `10.061 ms` for Streaming at 1M, which is far too
  small to explain the JVM/native separation.
- The sandbox native build is configured for diagnosis: `nativeConfig` enables
  checks, dumps, and source-level debugging. The linked binary has DWARF debug
  flags, and generated LLVM contains widespread `noinline` functions. HotSpot
  can inline and optimize this workload aggressively; the current native
  benchmark binary is not a release-style backend comparison.
- The biggest native phase gap is Q2 processing. The 1M control records
  `1757976` median recomputations and `19156244` double values sorted.
- Scala Native `java.util.Arrays.sort(Array[Double], from, to)` is implemented
  in Scala as a stable merge/insertion sort through `Ordering[Double]`, with
  `@noinline` entry points and a fresh temp array for larger ranges. HotSpot's
  `java.util.Arrays.sort(double[])` is a tuned primitive implementation. This
  makes Q2 median sorting a likely first-order backend-library cost.
- Read/parse loops are also much slower natively in the 1M control: JVM
  `80.299 ms` read and `199.858 ms` parse, versus Scala Native `436.457 ms`
  read and `1165.136 ms` parse. That is consistent with byte-array bounds
  checks, less inlining, and no JIT range check elimination.
- Output formatting is also slower natively in this control. At 1M, JVM Q1/Q2
  output was `48.374 ms` and `49.598 ms`, while Scala Native Q1/Q2 output was
  `571.755 ms` and `390.369 ms`; output remains secondary after Q2 processing.
- The hot path is mostly arrays and primitive data. Scala collection overhead is
  not the leading suspect in this specific control; array sorting, byte parsing,
  output formatting, bounds checks, inlining, and optimizer/codegen are more
  plausible first-order costs.
- The Java probe supports the narrower GC point only. With the default JVM heap,
  the 1M window probe reported `6 ms` GC out of `532.061 ms`; with `-Xmx8m`, it
  reported `1322 ms` GC out of `1864.021 ms`. That demonstrates that HotSpot GC
  can become the bottleneck under forced heap pressure, not that the checked-in
  Java probe is a fair RunBoth baseline.

## Recommendations

1. Do not interpret the fast JVM row as evidence against Rift. It shows that
   the current DEBS native binary is dominated by Scala Native backend/library
   costs before GC-vs-region effects can be isolated.
2. Add a `releaseFast` or `releaseFull` Scala Native DEBS control before making
   any JVM-vs-native claim. Keep it separate from Rift implementation work.
3. Add narrow same-source controls for `Trip.parseInto`, small
   `Arrays.sort(Array[Double], 0, n)` median buffers, Q2 rank/median update, and
   output formatting. Run each on JVM and Scala Native release mode.
4. Treat Q2 median maintenance as the next DEBS algorithmic hotspot. A
   semantic-preserving primitive median structure or native-friendly primitive
   sort helper should be classified as shared backend cleanup, not a Rift-only
   speed chase.
5. For the thesis, keep the Rift claim scoped to within-Scala-Native
   comparisons: heap, improved SafeZone, and Rift under the same backend/build
   mode. The current DEBS evidence still supports "bounded-sample application
   evidence is provisional"; it does not undermine the same-layout Rift runtime
   results from GCBench/ListOfLists.
