# ReML / MLKit Comparison Plan

Last updated: 2026-05-06 14:37 CEST

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
`checked-region-scoped`; no headline medians have been collected yet.

The matrix supports the canonical reporting modes:

- `gc-heap`
- `region-scoped-rooted`
- `checked-region-stream`
- `checked-region-scoped`

Rootless/trusted lower-bound controls (`region-scoped-rootless`,
`region-hp-rootless`, and `region-stream-rootless`) are still supported, but
they are no longer default rows. Run them with `RIFT_BENCH_INCLUDE_CONTROLS=1`
or explicit `REML_MODES`.

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

2. Run a Tier 1 headline matrix after committing the scaffold:

   ```sh
   cd /Users/siyaoliu/rift/scala-native-rift
   REML_BENCHMARK_RUNS=3 \
   zsh sandbox/run_reml_region_matrix.sh
   ```

3. Interpret Tier 1 by relative ratios, not raw ReML wall-clock:

   - region-vs-heap elapsed ratio;
   - RSS ratio;
   - GC time/count reduction;
   - checked overhead versus trusted/rooted rows.

4. Compare with existing Scala Native benchmarks where names overlap.
   `scala-native-benchmarks` includes a Mandelbrot-style benchmark, which
   overlaps the ReML `mandel` family. Use it as an additional Scala Native
   control only after documenting input/config differences.

5. Add Tier 2 only after Tier 1 is useful:

   - `b-hut`, `nucleic`, `ray`, `logic`, `zebra`, `kbc`, `tsp`, `mpuz`.

6. Search for exact artifact/source provenance:

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
