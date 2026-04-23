# How to drive this project with Codex

This file is the operating manual for using Codex on Rift after the project pivoted from "standalone runtime beside Scala Native" to "fork-first runtime work inside Scala Native."

## 1 — What Codex needs up front

Every new session should establish four things clearly:

1. **The design pack**: `DESIGN.md`, `ROADMAP.md`, `CODEX.md`.
2. **The implementation target**: the Scala Native fork at `git@github.com:641bill/scala-native.git`, branch `feature/rift`.
3. **The current phase and last trustworthy result**: not just "what we hoped was true," but what has actually been rerun and accepted.
4. **One concrete deliverable**: a code change, benchmark rerun, or proof step.

Codex is useful for implementation, reruns, and focused debugging. It is much less reliable at maintaining the research framing on its own. Keep the framing in the docs and make the prompt specific.

## 2 — Session template

Use this shape:

```text
Project: Rift, a hybrid region-GC system for Scala Native.

Read these first, in order:
  1. DESIGN.md
  2. ROADMAP.md
  3. CODEX.md

Implementation target:
  - repo: git@github.com:641bill/scala-native.git
  - branch: feature/rift

Current phase: <phase>
Last trusted result: <one sentence>
This session's goal: <single concrete deliverable>
Success criterion: <measurable check>

Rules:
- Do not change public APIs without explicit approval.
- Do not treat a provisional benchmark claim as settled unless you rerun it.
- When comparing performance, include Immix and the improved SafeZone baseline if the workload is relevant.
- Record exact commands, env vars, and run counts for every result that goes into a markdown table.
- If the design is unclear, stop and ask. Do not invent.
```

## 3 — How to frame the work now

The current project has three evaluation layers. Codex should know which layer a session belongs to:

1. **Runtime-only**: same workload shape, same data structure, different allocator/runtime path.
2. **Topology/layout**: nested regions, chunked storage, segmented buffers, operator-local regions.
3. **Safety/proof**: capture checking and Lean.

Do not let Codex blur these layers together in its writeup. If a speedup came from topology or layout, say so. If a result is runtime-only, preserve that.

## 4 — Baseline discipline

Codex must not benchmark against a straw man.

When a benchmark session touches SafeZone or region performance, the comparison set should normally include:

1. Immix
2. current SafeZone
3. improved SafeZone variant if available in the fork
4. Rift

If one of those cannot be run, the session should say why.

Also:

- A single run is not enough for a headline claim.
- If a benchmark had a known artifact before, rerun after fixing the artifact.
- If a result sounds too good or too bad, first suspect the harness.

## 5 — Suggested prompts by phase

### Phase 0 — baseline correction

> Goal: rerun the selected SafeZone and Immix benchmarks inside the fork, record exact env vars and commands, and update the baseline table. Treat any surprising result as provisional until rerun.

### Phase 1 — bootstrap allocator

> Goal: implement or fix the slab allocator and close/reset path in the standalone `native/` harness. This is only a bootstrap step; keep the code small and measurable. Success is a clean build plus a working microbenchmark.

### Phase 2 — in-tree integration

> Goal: port the allocator path into the Scala Native fork and wire a minimal Scala-facing API that can allocate and reclaim managed objects through Rift. Success is an end-to-end Scala Native test running through the new path.

### Phase 3 — runtime-only benchmarks

> Goal: rerun GCBench, BenchmarkListOfLists, or the cleaned pipeline benchmark with identical workload structure across Immix, current SafeZone, improved SafeZone, and Rift. Success is a table with medians and exact commands, plus a short note separating runtime cost from topology/layout.

### Phase 4 — topology and layout study

> Goal: add one topology experiment or one region-shaped layout variant and measure its incremental effect relative to the runtime-only baseline. Success is a table that attributes the win to topology, layout, or both.

### Phase 5 — DEBS 2015

> Goal: implement or benchmark one DEBS query configuration. Success is correctness plus measured throughput, latency, and memory breakdown under the agreed comparison set.

### Phase 6 — capture checking

> Goal: add or fix one positive or negative capture-check test, then run the harness and document the result in `REPORT_CAPTURE_CHECK.md` if Scala rejects an expected pattern.

### Phase 7 — Lean

> Goal: advance one proof file by replacing a `sorry`, tightening a lemma statement, or fixing a broken dependency chain. Success is that the Lean target compiles and the theorem state got strictly better.

## 6 — What Codex should not do

Do not let Codex:

- Rewrite the research claim from scratch while implementing code.
- Treat "SafeZone got much better after a roots-mode fix" as evidence that Rift is unnecessary.
- Treat "layout matters" as evidence that runtime work no longer matters.
- Invent benchmark results, medians, or proof progress.
- Hide an unexpected result because it complicates the story.
- Claim a benchmark is runtime-only if the workload shape changed.

## 7 — When Codex gets stuck

The main failure modes are predictable:

**The runtime compiles but the numbers are nonsense.**  
Add counters, timers, or assertions around the exact hot path. Suspect the harness before writing a thesis explanation.

**A benchmark result changed dramatically after a small code edit.**  
Check env vars, benchmark configuration, and whether an optimizer or boxing artifact changed.

**Codex silently introduces a new design decision.**  
Reject it unless the prompt explicitly asked for it. This project already has enough moving parts.

**The capture checker rejects something that looks reasonable.**  
Record the exact error. That is a research finding, not automatically a bug in the test.

## 8 — Hand-off format

Each Codex session should end with:

1. What changed
2. What was run
3. What the result actually was
4. Any unexpected finding
5. The next concrete session to run

If the session produced benchmark numbers, include the exact command and the comparison set used. If it produced a surprising result, the next session should usually be a rerun or diagnosis, not a blind move to the next roadmap item.
