# Rift agent instructions

Last updated: 2026-05-17 02:47 CEST

## Repository roles

### Parent repo
This repository (`/Users/siyaoliu/rift`) is the project memory layer.
It contains:
- `docs/` project design, roadmap, handoff
- `evidence/` benchmark and result packs
- `scripts/` sync and helper scripts
- `proof/` future mechanization
- `tests/` future capture-check tests

### Child repos
- `scala-native-rift/` = active implementation repo
- `scala-native/` = reference-only old investigation repo and git worktree parent for `scala-native-rift/`
- `scala-parallel-collections-amordo/` = reference-only student repo

Do not do new implementation work in the reference repos.

## Required reading before work

Read these first:
- `docs/HANDOFF.md`
- `docs/ROADMAP.md`
- `docs/DESIGN.md`
- `docs/status/CURRENT.md`

If working on implementation, also inspect:
- `git status`
- `git diff --stat`
- recent commits

## Rules

1. Preserve the distinction between validated and provisional results.
2. Do not restart the project from scratch.
3. For routine turn-by-turn status, update `docs/status/CURRENT.md` or the
   relevant file under `docs/status/`. Update `docs/HANDOFF.md` only when
   finishing a substantial milestone or when a user explicitly asks for a
   handoff refresh.
4. Sync benchmark and result markdown from `scala-native-rift/` into `evidence/`.
5. Treat `scala-native/` and `scala-parallel-collections-amordo/` as read-only references unless explicitly told otherwise.
6. When modifying project docs or evidence markdown, update the document's `Last updated:` timestamp or add one near the top if it is missing.
7. Do not update `docs/PERFORMANCE_EVALUATION_REPORT.md` or regenerate
   `docs/report.html` unless presentation-facing claims, tables, or report text
   changed. See `docs/DOCUMENT_UPDATE_POLICY.md`.
