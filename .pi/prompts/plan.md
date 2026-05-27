---
description: Read project context and create an implementation plan
argument-hint: "[task description]"
---
## Task

$ARGUMENTS

## Instructions

1. **Read required project docs** (skip if already loaded in this session):
   - `docs/HANDOFF.md`
   - `docs/ROADMAP.md`
   - `docs/DESIGN.md`
   - `docs/status/CURRENT.md`

2. **Inspect current state**:
   - Run `git status` and `git diff --stat` in both parent repo and `scala-native-rift/`
   - Check recent commits with `git log --oneline -10`
   - Read any evidence or status files directly relevant to the task

3. **Create a plan** that includes:
   - **Goal**: what the task accomplishes and why it matters
   - **Prerequisites**: what must be true or already done before starting
   - **Steps**: concrete, ordered implementation steps with file paths and commands
   - **Validation**: how to verify correctness after each step (compile, tests, smoke runs)
   - **Risks**: what could go wrong and how to recover
   - **References**: links to relevant docs, evidence files, or prior commits

4. **Follow project rules**:
   - Preserve the distinction between validated and provisional results
   - Do not restart the project from scratch
   - Keep `main` focused on Scala Native evidence; backend work goes on `backend-portability`
   - Update `docs/status/CURRENT.md` for routine progress, `docs/HANDOFF.md` only at milestone boundaries
   - Treat `scala-native/` and `scala-parallel-collections-amordo/` as read-only references

5. **Write the plan** to `docs/status/PLAN.md` (or a more specific location if the task warrants it), with a `Last updated:` timestamp.
