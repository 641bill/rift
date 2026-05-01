# Rift Performance Evaluation Runbook

Date: 2026-05-01

Status: executable runbook for the thesis-grade performance sweep. This is
not a result pack; it defines how to collect comparable results.

## Objective

The performance evaluation answers three questions:

- where Rift beats Scala Native Immix and improved SafeZone;
- where checked Rift loses because operator/container overhead dominates;
- which stream/dataflow shapes justify reusable Rift APIs.

Improved SafeZone (`SAFEZONE_ROOTS_MODE=1`) is the main SafeZone baseline.
Current SafeZone (`SAFEZONE_ROOTS_MODE=0`) stays in the matrix for provenance.

## Preflight

Before a headline run:

1. Commit or stash both repositories.
2. Record active SHAs:

   ```sh
   git -C /Users/siyaoliu/rift rev-parse HEAD
   git -C /Users/siyaoliu/rift/scala-native-rift rev-parse HEAD
   ```

3. Compile:

   ```sh
   cd /Users/siyaoliu/rift
   RIFT_EVAL_SUITES=preflight bash scripts/run-performance-evaluation.sh
   ```

The runner refuses dirty repos unless `RIFT_EVAL_ALLOW_DIRTY=1` is set. Use
that override only for exploratory rows that will not become headline results.

## Standard Run Levels

| Level | Command | Intended use |
|---|---|---|
| Smoke | `RIFT_EVAL_SCALE=smoke RIFT_EVAL_SUITES="preflight streams"` | Fast correctness and wiring check. |
| Headline | `RIFT_EVAL_SCALE=headline RIFT_EVAL_SUITES="preflight core prior checked streams debs"` | Main 1M-level thesis sweep. |
| Full | `RIFT_EVAL_SCALE=full RIFT_EVAL_SUITES="streams"` | Only for candidates that pass the 1M gate. |

Latest smoke validation:

```sh
RIFT_EVAL_RUN_ID=2026-05-01-smoke-streams \
RIFT_EVAL_SCALE=smoke \
RIFT_EVAL_SUITES="preflight streams" \
bash scripts/run-performance-evaluation.sh
```

This completed and produced stream summary files under
`cache/perf-eval/2026-05-01-smoke-streams/`. Use it only as harness
validation, not performance evidence.

Latest headline subset:

```sh
RIFT_EVAL_RUN_ID=2026-05-01-headline-core-prior-checked \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight core prior checked" \
bash scripts/run-performance-evaluation.sh
```

This completed and is summarized in
`evidence/HEADLINE_CORE_PRIOR_CHECKED_2026_05_01.md`.

It was rerun with the same suites as
`2026-05-01-headline-core-prior-checked-rerun` and summarized in
`evidence/HEADLINE_CORE_PRIOR_CHECKED_RERUN_2026_05_01.md`. Prefer the rerun
for current core/prior/checked interpretation because it removed the obvious
linked ListOfLists heap outlier.

Do not routinely run all expensive pathological controls in one monolithic
job. The current-SafeZone linked/topology ListOfLists rows are valid but
dominated wall-clock time. Prefer separate jobs for:

- `core` with full pathological controls;
- `prior checked` for methodology and checked API gates;
- `streams`;
- `debs`.

Example:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-headline \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight core prior checked streams debs" \
DEBS2015_BOTH_INPUT=/tmp/debs2015-month1-1000000.csv \
bash scripts/run-performance-evaluation.sh
```

Raw logs and TSV summaries are written under:

```text
/Users/siyaoliu/rift/cache/perf-eval/<run-id>/
```

That directory is ignored by git. Only curated summaries belong in
`evidence/`.

## Suites

| Suite | Benchmarks | Main purpose |
|---|---|---|
| `core` | GCBench, ListOfLists, pipeline surrogate | Runtime-only and topology/layout baselines. |
| `prior` | Dataflow/Broom, StreamFlex, Yak, Stancu | Literature-methodology comparison. |
| `checked` | RegionBuffer, priority queues, window rank, append window, fold | Checked operator cost and readiness gates. |
| `safezone-cost` | SafeZone-family root-mode/page-size cost matrix | Decompose root bookkeeping, reclaim, page-size, and allocation costs before backend changes. |
| `streams` | NEXMark, Yahoo, RIoTBench, Wikimedia, Common Crawl WET, Linear Road | Stream/dataflow win-envelope search. |
| `debs` | DEBS RunBoth sample and instrumented matrices | Downstream application validation. |

The runner does not yet execute DSPBench, Theodolite, HiBench, ShuffleBench,
RiverBench, or BigDataBench. Those are candidate-onboarding tasks, not existing
local runners.

## Metrics To Record

Every matrix row should record:

- elapsed median/min/max;
- GC median, max, collections, and runs-with-GC;
- peak RSS bytes;
- checksum and output count;
- input label, requested count, and actual loaded count.

Rift rows should additionally record:

- Rift op ms;
- region object count;
- open/close/reset totals.

Latency workloads should additionally record:

- throughput;
- p50/p95/max sampled latency;
- deadline misses;
- bucket-close latency when available.

Allocation attribution rows should be single diagnostic runs after clean
medians are stable. Do not use attribution elapsed time as headline evidence.

## Data Source Policy

Use generated inputs only when the result is labeled as generated or
methodology evidence. Use real/preloaded inputs for validation when available:

- NEXMark Beam-default profile from the Apache Beam source release generator
  settings;
- Wikimedia pageviews/clickstream TSVs under `cache/benchmark-data`;
- decompressed Common Crawl `.warc.wet`;
- official Linear Road data-driver files;
- future real RIoTBench/DSPBench inputs only after provenance is documented.

Do not claim exact artifact reproduction unless the original generator,
configuration, and validation rules are used.

## Case-Study Gate

A workload becomes a serious Rift case study only if:

- checksum/output counts match across modes;
- Rift beats heap and improved SafeZone by about `>=10%`; or
- Rift materially cuts GC/RSS with `<=5%` elapsed overhead and better latency;
- checked mode uses a checked operator that has passed a focused gate.

If median/max GC is small and heap wins, record the row as a ceiling result and
move to the next candidate.

## Candidate Onboarding Order

1. DSPBench local-kernel triage: inspect the source/paper app list and choose
   the top three kernels with the clearest object churn plus window/epoch
   lifetime.
2. Real RIoTBench input: add `RIOTBENCH_INPUT` when clean public input is
   available.
3. Theodolite: port one local UC kernel without Kafka/Kubernetes.
4. HiBench streaming: local/preloaded controls only.
5. ShuffleBench, RiverBench, BigDataBench: lower-priority parser/routing
   controls if earlier candidates remain weak.

## Post-Run Checklist

After a headline run:

1. Copy or summarize relevant TSVs into benchmark-specific `evidence/*.md`
   files.
2. Update `evidence/EVALUATION_SUMMARY_TABLES.md`.
3. Update `evidence/SN_WIN_ENVELOPE.md`.
4. Update `evidence/ALL_PHASE_RESULTS.md`.
5. Update `docs/PERFORMANCE_EVALUATION_REPORT.md`.
6. Update `docs/HANDOFF.md` with SHAs, commands, results, caveats, and the
   next safe action.
