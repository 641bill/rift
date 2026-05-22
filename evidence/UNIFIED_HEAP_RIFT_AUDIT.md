# Unified Heap-vs-Rift Audit

Date: 2026-05-18
Last updated: 2026-05-18 17:59 CEST

Status: presentation/model audit. This file checks whether the current report,
runner defaults, and benchmark programs follow the unified comparison model:

```text
heap baseline:
  natural framework/program object shape on the GC heap

checked Rift:
  same logical program, output, operator semantics, and lifetime boundary
  short-lived data-path objects allocated in checked regions
  durable control state remains on the heap

appendix controls:
  same-shape heap controls
  summary-on-append lower bounds
  legacy checked controls
  unsafe/rootless lower bounds
```

## Result

The strongest current evidence can already be presented under this model.
Broom retained dataflow, Theodolite retained UC4, Wikimedia retained
clickstream-session, LogHub retained session, Yak LiveJournal, AskUbuntu
topword, Dataflow, StreamFlexDesign, Stancu/SPECjbb-style, and ReML-shaped
local ports all have a natural heap baseline and one or more safe checked Rift
rows.

The main cleanup requirement is presentation discipline: checked stream and
checked scoped are backend selections under the Rift umbrella, while
same-shape heap, drop-anchor, summary-only, legacy checked, and unsafe/rootless
rows should remain appendix/mechanism rows unless they are explicitly used to
answer a causality or backend-potential question.

## Backend Selection Rule

Use one user-facing system name: Rift. For each API/topology, choose the
fastest safe checked backend as the headline Rift row:

- `checked-region-stream` / `checked-rift`: checked API over the Rift streaming
  backend.
- `checked-region-scoped`: checked API over the rooted scoped/SafeZone-family
  backend.
- `checked-page-token` variants: checked operator-owned page/window backend.

If checked scoped beats checked stream, do not frame that as "Rift lost."
Treat it as evidence that automatic backend selection should choose scoped for
that shape, or as a profiling target for improving the Rift streaming backend.
Unsafe/rootless modes remain lower-bound controls only.

## Benchmark Program Audit

| Benchmark program / runner | Headline model status | Notes / action |
|---|---|---|
| `BroomRetainedDataflowMatrix.scala` | Follows model | Canonical modes are `heap-gc`, `checked-rift`, and `checked-region-scoped`. Aggregate, join, shopper, and q17 keep the same logical retained query across heap and checked rows. |
| `LogHubRetainedSessionMatrix.scala` | Follows model | Canonical modes are `heap-gc`, `checked-rift`, and `checked-region-scoped`. The Wikimedia and LogHub session workloads retain ordinary session/event objects and keep durable metadata on heap/control paths. |
| `TheodolitePowerRegionMatrix.scala` | Follows model | Rows compare heap with `checked-epoch-stream` and `checked-epoch-scoped`; q3 retained UC4 is the current strongest real-streaming retained-object row. |
| `YakRegionMatrix.scala` | Follows model for selected rows | Supports many historical modes, but presentation rows use natural heap versus checked epoch topology. Direct epoch is the right API shape; page-token rows are topology contrast/control. |
| `DataflowRegionMatrix.scala` | Mostly follows model | Selected/report rows should show natural heap versus best safe checked epoch/page-token backend. Older SafeZone/rootless/current aliases remain for controls. |
| `StreamFlexDesignMatrix.scala` | Follows model | Heap same-shape is useful because the matrix is a StreamFlex-design reproduction. Presentation should still headline heap versus checked Rift and report latency axes. |
| `SpecJbb2005PortMatrix` / Stancu rows | Follows model | Generated clean-room transaction workload; not real input or official SPEC. Headline is natural heap transaction objects versus checked epoch transaction regions. |
| `LogHubTopTemplatesMatrix.scala` | Mixed but classified | Contains `heap-natural`, summary-only, retained/drop-anchor, and top-k checked modes. Headline rows should use natural heap versus checked reusable top-k; same-shape/drop-anchor/summary rows are appendix controls. |
| `LogHubRegionMatrix.scala`, `GithubArchiveRegionMatrix.scala`, `DSPBenchRegionMatrix.scala` | Mixed but acceptable | These matrices contain direct-summary and retained-control modes. Selected runners keep controls out of default rows; reports must classify generated/real and headline/control status explicitly. |
| `CommonCrawlWetMatrix.scala`, `CheckedAppendWindowMatrix.scala`, `CheckedPageTokenCostMatrix.scala` | Focused/generated evidence | Strong for page/window token mechanics and generated object pressure. `CheckedPageTokenCostMatrix` is mechanism evidence, not headline application evidence. |
| `RetainedEpochReclaimMatrix.scala` | Appendix mechanism control | Useful for causality. It should not be presented as a user-facing benchmark by itself. |
| `ObjectAllocationLoweringMatrix.scala` | Optimization mechanism control | Useful for backend-known allocation, dirty-slab, and no-zero experiments. Not a user-facing benchmark. |
| `ReMLRegionMatrix.scala` | Follows same-axes comparison track | Keeps paper-style axes and local Scala Native ports. Do not claim raw Rift-vs-ReML wall-clock without exact same-machine artifacts. |
| `scripts/run-performance-evaluation.sh` | Mostly aligned | `selected-prior` and `selected-streams` default to heap, safe checked rows, and best safe backend rows. Controls remain behind `RIFT_EVAL_INCLUDE_CONTROLS=1` in most selected paths. Some raw names are still implementation aliases and should be normalized in evidence/report text. |

## Presentation Cleanup Status

Updated in this pass:

- `docs/PERFORMANCE_EVALUATION_REPORT.md` now states the unified
  heap-vs-Rift contract and backend selection rule.
- `docs/MEMORY_MODE_TAXONOMY.md` now says checked scoped and checked stream
  are backend choices under one Rift user-facing system.
- `docs/ROADMAP.md` now records automatic backend selection as the reporting
  rule and profiling target.
- `scripts/generate-report-html.py` now frames backend selection and controls
  according to the unified story.

Remaining presentation discipline:

- Keep `evidence/EVALUATION_CLASSIFIED_SUMMARY.md` as the detailed classified
  source, but when copying rows into slides/report HTML, choose the fastest
  safe checked backend as the headline Rift row.
- Keep older rootless/trusted/current SafeZone rows only in control sections.
- Keep summary-only/manual-array rows as lower bounds, not as Rift system wins.

## Wikimedia Profiling Follow-Up

The first required profiling target was Wikimedia retained clickstream-session,
because the full-file L2 row removes about `6.8 s` of timed heap GC, while the
checked non-GC path is about `5.1 s` slower than heap's non-GC path:

| Row | Heap L2 | Checked Rift L2 | Interpretation |
|---|---:|---:|---|
| Full-file Wikimedia | heap total `72.750 s`, GC `7.123 s`, non-GC about `65.627 s` | checked total `71.150 s`, GC `0.318 s`, region op `0.080 s`, non-GC about `70.752 s` | Region placement removes GC/RSS/fixed-memory pressure, but checked mutator work is higher. |

The 10M L4 profile has now run:

- profile directory:
  `/Users/siyaoliu/rift/cache/profile-sweep-20260518-172522`
- cases: `wikimedia-clickstream-heap`,
  `wikimedia-clickstream-checked-rift`,
  `wikimedia-clickstream-checked-scoped`
- all cases matched checksum `8006060730683441349` and output `9323019`.

First-order finding: the row is dominated by compressed input, byte-line
reading, TSV field hashing/int parsing, stable hashing, and session-loop work.
Heap also samples Immix marker/heap-block work and has about `1.0G` sampled
footprint. Checked Rift drops sampled footprint to about `126.8M`, but still
pays the shared parser/hash/session-loop floor. Checked scoped has similar RSS
and shows extra marker/root-range and small zone-allocation samples.

Next buckets to inspect or optimize:

- allocation lowering path and object header/field initialization;
- gzip/TSV parsing and string/hash cost;
- session-key hashing and aggregate dictionary updates;
- retained object linking/traversal;
- region reset/close and slab reuse policy;
- scoped backend paths that beat or trail the Rift streaming backend.

Profiles are L4 diagnostic evidence only. They should guide optimization but
must not replace L1 final-clean headline timing.

## Profile Coverage Update

The L4 harness now covers every current headline benchmark family at a
representative level, not every historical/control mode:

- prior broad sweep: StreamFlexDesign, Common Crawl, DSPBench, LogHub top-k,
  Yak, Dataflow, NEXMark, SPECjbb/Stancu, StreamIt controls, and ReML-shaped
  ports;
- 2026-05-18 Wikimedia follow-up: real retained clickstream session;
- 2026-05-18 gap-fill: Broom aggregate/join/q17/shopper, Theodolite retained
  UC4, and LogHub retained session/join.

The extra profiles strengthen the unified model rather than changing it.
Broom-style generated retained rows expose allocator/GC differences directly:
heap samples Immix allocation metadata, marking, and sweep; checked Rift
samples region allocation/object initialization and the same query loop. Real
streaming Theodolite and LogHub rows are dominated by input parsing, byte-line
scanning, numeric/string extraction, and hashing; they are still valuable RSS
and fixed-memory evidence, but they are not the best region-allocation tuning
benchmarks.
