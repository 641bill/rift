# Final Component Selection

Last updated: 2026-05-06 15:57 CEST

Status: selection policy for the final Rift story. This document classifies
components by evidence without deleting runtime code. Losing and unsafe modes
remain useful benchmark controls, but they should not be presented as
user-facing system components.

## Selection Rule

A component can be public only if it has:

- passing safety probes for its lifetime/reference boundary;
- at least one focused benchmark row and one application or literature-shaped
  row supporting its usefulness;
- correctness-equivalent heap and region runs;
- either a clear elapsed win over `gc-heap` and the best safe baseline, or a
  material GC/RSS/tail-latency win with no more than small elapsed overhead.

Rootless modes are never public safe components. They are lower-bound controls
for backend potential.

## Public Candidates

| Component | Status | Why |
|---|---|---|
| `checked-region-scoped` | Candidate | Same checked API over SafeZone-family scoped allocation. It is currently the leading checked backend candidate for append/page-token shapes. |
| `checked-region-stream` | Candidate/control | Existing checked Rift backend. Keep as the native checked baseline until scoped checked backend consistently dominates. |
| `checked-page-token` | Public candidate | Operator-owned page/event/window append path. It has focused wins and generated Common Crawl-shaped q1/q2 wins. |
| `PageTokenMapFilter` | Public candidate | Reusable SELECT/filter/project shape. Dataflow SELECT rows support it. |
| `RegionList` | Public candidate | Reusable linked-topology builder for region-friendly list graphs. |
| `TransactionRegion` | Candidate | Best checked StreamFlex-shaped multi-stage epoch path so far, but trusted Rift still wins. Keep candidate until more rows decide. |

## Internal Controls

| Component | Status | Reason |
|---|---|---|
| `region-scoped-rootless` | Internal lower bound | SafeZone-family allocation without GC root tracking. Unsafe without static root-free proof. |
| `region-hp-rootless` | Internal lower bound | Trusted Rift HP backend; useful backend potential, not checked safety. |
| `region-stream-rootless` | Internal lower bound | Trusted Rift streaming/reset backend; useful backend potential, not checked safety. |
| old/current SafeZone | Historical control | Useful provenance for the root-bookkeeping cliff, not a competitive final baseline. |

## Gated Or Rejected

| Component | Status | Reason |
|---|---|---|
| `EpochFold` | Gated | Correct, but true reusable Dataflow AGGREGATE row failed the speed gate. |
| `StreamWindowFold` | Gated | Correct/lower RSS, but focused 1M speed gate failed. |
| `StreamWindowRank` / `TableRank` | Gated | Correct/profilable, but rank/table CPU overhead dominates at 1M. |
| fixed chunk append | Rejected/control for sequential append | Correct, but slower than linked page-token and fair heap chunk control in current rows. |
| DEBS ranking/median operators | Deferred | Current evidence does not show ranking/median as primarily memory-management-bound. |

## Safety Checkpoint

The ReML-style generic heap-retention gap is now fixed at the current compiler
probe level: heap generic objects such as `Cell[Box^{region}]`, arrays of
region-captured values, and closures hiding generic region values are rejected
when stored into durable/static heap state. Local nonescaping polymorphic use
inside a region remains legal.

This is not a full arbitrary heap-object field analysis. The current fix
targets durable/static retention and known Rift-derived values. Broader heap
alias analysis and rootless checked backend eligibility remain future work.

## Default Reporting Path

Default benchmark/report tables should include:

- `gc-heap`;
- best safe/rooted baseline, usually `region-scoped-rooted`;
- best checked backend candidate, currently `checked-region-scoped` where it
  exists and `checked-region-stream` otherwise;
- best operator-specific candidate, such as `checked-page-token`;
- rootless modes only in explicit lower-bound/control sections.

Do not physically delete losing runtimes in this phase. Remove them from
default scripts and summary tables only after the final selection sweep.

## Runner Defaults

The parent evaluation runner and the main sandbox matrix scripts now use the
selection policy by default:

- default rows exclude current SafeZone and rootless/unsafe lower-bound modes;
- `RIFT_EVAL_INCLUDE_CONTROLS=1` or `RIFT_BENCH_INCLUDE_CONTROLS=1` re-enables
  current/rootless/trusted-control rows for provenance and lower-bound sweeps;
- explicit per-script mode variables such as `DATAFLOW_MODES`,
  `COMMON_CRAWL_WET_MODES`, `REML_MODES`, and `GITHUB_ARCHIVE_MODES` still
  override the defaults.

This is reporting-path pruning only. It does not delete runtime code or remove
the ability to reproduce older control matrices.

## Smoke Validation

Run id `2026-05-06-final-selection-smoke` validated the default reporting path
with:

```bash
RIFT_EVAL_RUN_ID=2026-05-06-final-selection-smoke \
RIFT_EVAL_SCALE=smoke \
RIFT_EVAL_SUITES="preflight core prior checked streams reml" \
RIFT_EVAL_ALLOW_DIRTY=1 \
bash scripts/run-performance-evaluation.sh
```

The run completed. It records `include_controls=0` in
`cache/perf-eval/2026-05-06-final-selection-smoke/environment.txt`, and the
generated summaries contain no default rootless/current-control rows. Treat it
as runner/default validation only because the repos were intentionally dirty.

## Clean Headline Selection

Run id `2026-05-06-final-selection-headline` completed the clean default
headline sweep:

```bash
RIFT_EVAL_RUN_ID=2026-05-06-final-selection-headline \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight core prior checked streams reml" \
bash scripts/run-performance-evaluation.sh
```

Source summary: `evidence/FINAL_SELECTION_HEADLINE_2026_05_06.md`.

Selection changes from this run:

- `checked-page-token` remains a public candidate. It wins focused append,
  generated Common Crawl-shaped q1/q2, GH Archive-shaped q1/q2, and Dataflow
  SELECT.
- `checked-region-scoped` remains a leading backend candidate for page-token
  shapes: it is fastest on focused page-token append and generated Common
  Crawl-shaped q1/q2.
- `checked-region-stream` remains necessary as a candidate/control backend: it
  is best for GH Archive-shaped q1/q2 and ReML-shaped `msort`/`msort-r`.
- `RegionList` is promoted as a strong linked-topology candidate: linked
  ListOfLists is heap `15820.172 ms`, improved SafeZone `10133.449 ms`, and
  checked builder `6053.235 ms`.
- `TransactionRegion` remains candidate, not final: throughput wins are
  present, but latency remains mixed.
- `StreamWindowFold`, `TableRank`, JOIN, rank/window/table-heavy structures,
  and parser-scratch shapes remain gated or negative.
