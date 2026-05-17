# Rift Document Update Policy

Date: 2026-05-17
Last updated: 2026-05-17 02:47 CEST

Status: active policy for reducing conflicts between the Native backend fork
and the portable-backend fork.

## Goal

Avoid editing the same large narrative files on every round. Routine work
should update small status files. Large docs should change only at milestones
or when presentation content changes.

## Hot Status Files

Use these for frequent updates:

| File | Owner / use |
|---|---|
| `docs/status/CURRENT.md` | Current round status, newest validation, next action. Update often. |
| `docs/status/NATIVE_BACKEND.md` | Scala Native runtime/compiler/benchmark status. Native fork owns. |
| `docs/status/PORTABLE_BACKEND.md` | JVM/Scala.js/Wasm/analysis-only prototype status. Portable fork owns. |
| `docs/status/BENCHMARK_SEARCH.md` | GC-heavy benchmark search and real-input triage. Shared, but prefer append-only entries. |

## Stable Narrative Files

Do not update these on every round:

| File | Update only when |
|---|---|
| `docs/HANDOFF.md` | A substantial milestone finishes, a new branch/fork owner changes, or a user explicitly asks for a handoff refresh. |
| `docs/ROADMAP.md` | The actual roadmap changes, a phase completes, or priorities are reordered. |
| `docs/PERFORMANCE_EVALUATION_REPORT.md` | Presentation-facing claims/tables/interpretation change. |
| `docs/report.html` | Only regenerate after changing `docs/PERFORMANCE_EVALUATION_REPORT.md`. Never hand-edit. |
| `docs/DESIGN.md` | Design model changes, not routine benchmark/status updates. |

## Evidence Files

Evidence files remain the source for benchmark provenance:

- update evidence when a benchmark/result/source investigation changes;
- keep `Last updated:` timestamps current;
- avoid mixing provisional and validated rows in the same table without labels;
- sync child sandbox evidence into parent `evidence/` only after the row is
  stable enough to record.

## Fork Ownership

| Area | Owner |
|---|---|
| `scala-native-rift/nativelib/**`, `nscplugin/**`, `unit-tests/native/**` | Native backend fork |
| `scala-native-rift/sandbox/**` | Native benchmark fork unless explicitly coordinated |
| `scala-native-rift/experimental/portable-rift/**` | Portable backend fork |
| `docs/RIFT_PORTABLE_API_CONTRACT.md` | Shared contract; edit carefully |

## Rule Of Thumb

If the update only answers "what happened this turn?", put it in
`docs/status/CURRENT.md`.

If the update changes "what should we present or claim?", update the report and
regenerate `report.html`.

If the update changes "what should we do next?", update `docs/ROADMAP.md`.

If the update gives someone enough context to resume after a long pause, update
`docs/HANDOFF.md`.
