# Rift agent instructions

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

If working on implementation, also inspect:
- `git status`
- `git diff --stat`
- recent commits

## Rules

1. Preserve the distinction between validated and provisional results.
2. Do not restart the project from scratch.
3. Update `docs/HANDOFF.md` when finishing a substantial milestone.
4. Sync benchmark and result markdown from `scala-native-rift/` into `evidence/`.
5. Treat `scala-native/` and `scala-parallel-collections-amordo/` as read-only references unless explicitly told otherwise.
