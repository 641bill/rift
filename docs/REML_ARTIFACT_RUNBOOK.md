# ReML / MLKit Exact Artifact Runbook

Last updated: 2026-05-06 16:14 CEST

Status: setup/runbook for exact ReML/MLKit reproduction. No exact local timing
rows have been collected yet.

## Goal

Run the MLKit/ReML benchmark programs locally in the paper-style modes and
compare against Rift only after source, flags, tools, and inputs are pinned.

This is separate from `ReMLRegionMatrix`, which is a Scala Native port matrix.

## Current Provenance

The public MLKit repository has been cloned into ignored cache:

```text
/Users/siyaoliu/rift/cache/reml/mlkit
```

Repository:

```text
https://github.com/melsman/mlkit.git
```

Inspected HEAD:

```text
8561fe6ad949b84f83e8b78508b720ceccabe902
```

Relevant tags fetched:

| Tag | Commit | Date | Why it matters |
|---|---|---|---|
| `v4.7.4` | `855248bf` | 2023-10-01 | initial explicit region/effect annotation support |
| `v4.7.5` | `5f0f811d` | 2023-10-10 | `NEWS.md` says ReML released as part of distribution |
| `v4.7.6` | `71c2630e` | 2023-11-16 | later datatype-unboxing release |

Current local tool status:

```text
mlkit: not installed
mlton: not installed
```

## Benchmark Sources Found

The repo contains many Figure 9-style programs:

| Paper family | Candidate source path |
|---|---|
| `DLX` | `test/DLXSimulator.sml` |
| `b-hut` | `test/barnes-hut.mlb`, `test/barnes-hut/*.sml` |
| `fft` | `test/fft.sml` |
| `life` | `test/life.sml`, `test/kitlife35u.sml` |
| `logic` | `test/logic.mlb` |
| `mandel` | `test/kitmandelbrot.sml` |
| `mpuz` | `test/mpuz.sml` |
| `msort` / `msort-r` | `test/msort.mlb`, `test/msort.sml`, `kitdemo/msort.mlb` |
| `nucleic` | `test/nucleic.mlb` |
| `prof` | `test/professor.sml`, `test/professor2.sml` |
| `ratio` | `test/ratio-regions.sml` |
| `ray` | `test/ray.mlb` |
| `simple` | `test/kitsimple.sml` |
| `tak` | `test/tak.sml` |
| `tsp` | `test/tsp.sml` |
| `zern` | `test/zern.sml` |

Open mapping gaps:

- paper `fib37` versus available `fib35` sources;
- `lexgen`, `mlyacc`, `vliw`, `kbc`, and `zebra` exact sources/configs;
- exact input sizes for each benchmark;
- exact paper command-line mapping for `rg`, `rg-`, and `r`.

## Proposed Reproduction Order

1. Pin source revision.
   - Start with `v4.7.5` because it is the first public tag whose `NEWS.md`
     says ReML is released.
   - Also test whether the paper authors used a pre-release commit or artifact.

2. Install or build tools.
   - Need `mlkit` and `mlton`.
   - Record tool versions, install method, and binary paths.

3. Smoke compile three programs.
   - `test/msort.mlb`
   - `test/fft.sml`
   - `test/ratio-regions.sml`

4. Verify mode flags.
   - `rg`: region inference plus tracing GC with GC-safety refinement.
   - `rg-`: same but without the spurious-type-variable refinement.
   - `r`: pure region inference/no tracing GC.
   - `MLton`: optimizing SML baseline.

5. Run exact medians.
   - At least 3 runs for every program/mode.
   - Record real time, RSS, GC count, command line, source revision, and
     output/checksum where available.

6. Compare to Rift.
   - Do not compare raw wall-clock as the primary claim unless tools and source
     configs are exact and local.
   - Compare relative effects: region-vs-heap speedup, RSS reduction, GC
     count/time reduction, and safety/annotation burden.

## Claim Boundary

Until the above is complete:

- paper Figure 9 numbers are literature-reported evidence;
- MLKit source inspection is provenance evidence;
- Scala Native `ReMLRegionMatrix` rows are local port evidence;
- only exact local MLKit/ReML runs can justify direct speed comparisons.
