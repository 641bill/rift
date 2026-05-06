# ReML / MLKit Comparison Plan

Last updated: 2026-05-06 23:45 CEST

## Goal

Add a second thesis-grade comparison axis beside stream/dataflow workloads:
compare Rift with the MLKit/ReML lineage on safe region+GC execution for
higher-order, polymorphic, non-stream benchmark programs.

Reference: Martin Elsman, "Garbage-Collection Safety for Region-Based
Type-Polymorphic Programs", PLDI 2023.

## Evidence Classes

| Evidence class | Meaning | Claim boundary |
|---|---|---|
| Paper-reported ReML | Figure 9 benchmark table transcribed into `evidence/REML_COMPARISON_MATRIX.md`. | Use as literature anchor only; not local evidence. |
| Exact ReML artifact rerun | Original MLKit/ReML benchmarks run locally with `rg`, `rg-`, `r`, and MLton. | Required for direct cross-system timing claims. |
| Scala Native ReML-shaped ports | Local ports in `ReMLRegionMatrix`. | Valid Rift-vs-Scala-Native evidence, not exact ReML reproduction. |
| ReML-inspired safety probes | Compiler tests for polymorphic/higher-order GC-safety hazards. | Valid safety/design evidence even before full benchmark reproduction. |

## Implementation Status

Initial scaffold is implemented:

- `scala-native-rift/sandbox/src/main/scala-next/ReMLRegionMatrix.scala`
- `scala-native-rift/sandbox/run_reml_region_matrix.sh`
- `scala-native-rift/sandbox/REML_COMPARISON_MATRIX.md`

Tier 1 local ports are implemented for `fib37`, `tak`, `mandel`, `msort`,
`msort-r`, `life`, `fft`, and `ratio`. A reduced-size all-Tier-1 smoke run
matched checksums across `gc-heap`, `checked-region-stream`, and
`checked-region-scoped`. A 3-run Tier 1 headline matrix was collected on
2026-05-06 and is recorded in `evidence/REML_COMPARISON_MATRIX.md`.

The current Tier 1 results are useful but still only **Scala Native
ReML-shaped ports**:

- `msort`, `msort-r`, and `ratio` show real local region-vs-heap allocation,
  GC, and RSS effects.
- `fib37`, `tak`, `mandel`, and `life` are mostly compute/array controls with
  little or no timed GC.
- `fft` is a very small row at the current default and is better treated as an
  RSS/tiny-allocation control until scaled or matched to the MLKit input.

The matrix supports the canonical reporting modes:

- `gc-heap`
- `region-scoped-rooted`
- `checked-region-stream`
- `checked-region-scoped`

Rootless/trusted lower-bound controls (`region-scoped-rootless`,
`region-hp-rootless`, and `region-stream-rootless`) are still supported, but
they are no longer default rows. Run them with `RIFT_BENCH_INCLUDE_CONTROLS=1`
or explicit `REML_MODES`.

## Artifact Provenance Checkpoint

Local inspection, 2026-05-06:

- Cloned public MLKit repository into ignored cache:
  `/Users/siyaoliu/rift/cache/reml/mlkit`.
- Repository URL: `https://github.com/melsman/mlkit.git`.
- Inspected commit: `8561fe6ad949b84f83e8b78508b720ceccabe902`
  (`Modular storage mode analysis (#209)`).
- This is current MLKit HEAD, not yet the exact PLDI 2023 ReML configuration.
- `mlkit` and `mlton` executables are not currently installed on this machine,
  so no exact local run has been performed yet.
- Full history/tags were fetched. Relevant tags around the paper-era ReML
  release are:
  - `v4.7.4` -> `855248bf`, 2023-10-01, initial explicit region/effect
    annotation support;
  - `v4.7.5` -> `5f0f811d`, 2023-10-10, "ReML released as part of the
    distribution";
  - `v4.7.6` -> `71c2630e`, 2023-11-16, later datatype-unboxing release.

The clone contains many Figure 9-style benchmark sources under `test/` and
`kitdemo/`, including `fft.sml`, `msort.mlb`, `ratio-regions.sml`,
`tak.sml`, `tsp.sml`, `DLXSimulator.sml`, `nucleic.mlb`, `barnes-hut.mlb`,
`logic.mlb`, `ray.mlb`, `mpuz.sml`, `zern.sml`, and Mandelbrot/life/fib
variants. `test/all.tst` also groups several benchmark programs, and
`src/Tools/Benchmark` contains an MLKit benchmarking harness that records real
time, RSS, and GC count.

This makes exact reproduction plausible, but not complete. The next
provenance task is to determine whether the paper used a pre-release artifact,
`v4.7.5`, or another revision, then pin the command flags. The current public
source exposes MLKit options for region inference, garbage collection,
generational GC, and no-GC region execution, but the exact Figure 9 mapping of
`rg`, `rg-`, and `r` must be verified before running headline comparisons:

- `rg`: region inference plus tracing GC with GC-safety refinement;
- `rg-`: variant without the spurious-type-variable refinement;
- `r`: pure region inference/no tracing GC;
- `MLton`: optimizing SML baseline.

Until those runs exist, compare Rift to ReML only by paper-reported axes and by
local Scala Native port ratios.

Docker/toolchain status, 2026-05-06 23:45 CEST:

- `docker` CLI exists at `/usr/local/bin/docker`.
- `docker info` fails because the Docker daemon is not running.
- `mlkit` and `mlton` are not installed on the host.
- Therefore exact local MLKit/ReML timing is still blocked; no exact `rg`,
  `rg-`, `r`, or MLton row has been collected.

## Scala Native Port Closeness Policy

The local ports should be made as close as practical, but the evidence class
must remain honest. Exact reproduction requires the original SML source,
paper-era MLKit/ReML compiler configuration, and benchmark inputs. The current
Scala Native ports use the same broad algorithm families, not source-level
translations.

| Port | Current closeness | Fairness caveat / next check |
|---|---|---|
| `fib37` | Same recursive Fibonacci family and default `n=37`. | MLKit source candidates include `fib35`; exact source/config still needs pinning. |
| `tak` | Same Takeuchi-recursion family. | Default tuple `(18,12,6)` must be checked against the paper source. |
| `mandel` | Same Mandelbrot numeric family. | Grid/iteration defaults are local; compare with MLKit/Scala Native Mandelbrot configs before cross-system ratios. |
| `msort`, `msort-r` | Same linked-node sort/allocation family; reverse variant included. | Current default `REML_LIST_SIZE=100000`; MLKit source has benchmark-specific sizes, so exact reproduction must pin those. |
| `life` | Same Life/grid-update family. | Local implementation is array-heavy and mostly a compute/control row. |
| `fft` | Same complex-object FFT-style update family. | Current `REML_FFT_SIZE=16384` is tiny; scale or match MLKit input before strong claims. |
| `ratio` | Same rational-number allocation/reduction family. | Local data generator/checksum is Scala Native-specific; use relative heap-vs-region ratios only. |

Default local modes are selected for a fair safe-user comparison:

- `gc-heap`;
- `region-scoped-rooted`;
- `checked-region-stream`;
- `checked-region-scoped`.

Rootless/trusted controls remain available with `RIFT_BENCH_INCLUDE_CONTROLS=1`
or explicit `REML_MODES`, but they are lower-bound controls rather than safe
system rows.

## Safety Finding

The ReML-inspired probes now cover:

- local polymorphic consumer of a region value compiles;
- polymorphic identity cannot return a region value out of scope;
- polymorphic region object cannot store unrooted heap metadata;
- heap generic `Cell[Box^{region}]` cannot flow into durable/static heap
  state;
- generic cells widened to `AnyRef` cannot flow into durable/static heap
  state;
- heap arrays that store region-captured values cannot flow into
  durable/static heap state;
- escaping closures cannot hide generic region values in durable/static heap
  state.

The previously ignored probe is now active and passing. This is directly
related to the ReML paper's concern: region values can be hidden by
polymorphism in ways that matter to tracing-GC safety.

Design issue to fix:

- Generic heap allocations must preserve captures from their type arguments and
  constructor arguments. A value like `new Cell[Box^{region}](box)` should be
  treated as capturing `region` even if later widened to `AnyRef`.
- Durable heap/static locations must reject values whose capture set contains a
  region capability unless that capability is proven to outlive the location.
- Local polymorphic use should remain legal when the captured value does not
  escape the region scope.
- Current implementation note: the compiler now tracks known Rift-derived
  values flowing to durable/static heap state. Broader arbitrary heap-object
  field provenance remains open.

## Next Work

1. Extend the current durable/static polymorphic heap-retention check into a
   broader heap alias story, or explicitly document that boundary, before
   making stronger rootless checked safety claims.

2. Interpret Tier 1 by relative ratios, not raw ReML wall-clock:

   - region-vs-heap elapsed ratio;
   - RSS ratio;
   - GC time/count reduction;
   - checked overhead versus trusted/rooted rows.

3. Compare with existing Scala Native benchmarks where names overlap.
   `scala-native-benchmarks` includes a Mandelbrot-style benchmark, which
   overlaps the ReML `mandel` family. Use it as an additional Scala Native
   control only after documenting input/config differences.

4. Add Tier 2 only after Tier 1 is useful:

   - `b-hut`, `nucleic`, `ray`, `logic`, `zebra`, `kbc`, `tsp`, `mpuz`.

5. Continue exact artifact/source provenance:

   - record MLKit/ReML source URL or archive, commit/hash if available,
     compiler versions, MLton version, machine, commands, and run counts;
   - if found, add local MLKit/ReML reruns for `rg`, `rg-`, `r`, and MLton;
   - if not found, explicitly mark exact reproduction unavailable and keep
     Scala Native ports as methodology-shaped evidence.

## Claim Rules

- Do not write "Rift beats ReML" unless exact ReML artifacts are run locally.
- It is valid to write "Rift shows comparable or stronger relative
  region-vs-heap effects on Scala Native ports" if the local matrix supports
  that.
- It is valid to write "Rift fixed the current ReML-style durable/static
  generic heap-retention probe, but broader heap alias analysis remains open."
