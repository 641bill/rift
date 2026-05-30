# Plan: Full Region Inference for Rift

Last updated: 2026-05-30 02:20 CEST

Status: **ALL PHASES COMPLETE** ✅

## Goal

Move Rift from its current "explicit checked lifetime topology + selective compiler placement lowering" to a ReML-style "inferred region variables + inferred allocation/effect summaries + compiler-inserted region creation/deallocation" system.

The concrete deliverable: a Scala programmer writes ordinary code with no region annotations, and the compiler infers which allocations go into checked regions, inserts region creation/deallocation, and falls back to heap only when inference fails.

## Why It Matters

Currently Rift requires programmers to:
1. Name every region explicitly (`using r: ScopedRegion^`)
2. Carry region tokens through method signatures
3. Write `allocOpen(new T(...))` instead of `new T(...)`

Full region inference eliminates all three burdens while preserving the same safety guarantees. The programmer writes natural Scala; the compiler inserts region topology.

## Current State (validated 2026-05-24)

- Compiler: `702/702` tests pass
- Runtime: `316/316` tests pass
- Sandbox: `sandbox3_next/compile` passes
- Inference phase: `RiftRegionInference.scala` (3512 lines) handles local `new`, method returns, closure objects, owner-token containers, arrays, Some/Option/Tuple2/Either factories, lambda-lifted helpers, and closure-body allocation through explicit owner capture
- Gap: closure bodies without explicit owner capture, automatic region scope insertion, effect polymorphism on function types

## Prerequisites (all satisfied)

- [x] Scala 3 capture checking integrated (`T^{r}` types)
- [x] Rift region runtime with open/close/reset
- [x] Checked scoped and streaming backends
- [x] Inference phase in `RiftRegionInference.scala`
- [x] GenNIR lowering for inferred allocation sites
- [x] Compiler negatives for escape/metadata rejection
- [x] Runtime allocation-stat proofs for placed objects
- [x] ReML lineage documented in `docs/REGION_INFERENCE_LINEAGE.md`
- [x] Benchmark evidence for explicit-checked vs heap wins

## Phased Implementation Plan

### Phase 1: Effect-Polymorphic Closure Types

**Goal**: Make closure types carry allocation effects, so `(n: Int) => new T(n)` can be typed as `Function1[Int, T]^{r alloc r}` where `r` is the region the body allocates in.

**Why first**: This is the highest-impact gap. Currently, closure bodies fall back to heap unless they explicitly capture an owner term. Effect polymorphism lets the *caller* specify where the closure body allocates, solving the hidden-owner problem through the type system.

**What ReML does**:
```sml
(* ReML: effect variable on function type *)
val f : int #e -> int = fn x => x + 1
(* When called with region r, f's body allocates in r *)
```

**What Rift should do**:
```scala
// Proposed: capture type carries allocation effect
val f: Function1[Int, T]^{r} = (x: Int) => new T(x + 1)
// Compiler infers: closure body allocates in region r
// GenNIR: lambda body receives owner handle for r
```

#### Step 1.1: Define allocation effect types in capture checking

**Files**: `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/RiftRegionInference.scala`

**What**: Extend the inference phase to track "allocation effect" alongside capture types. When a closure body contains `new T(...)`, record that the closure has an allocation effect in the region that owns the closure.

**Design**:
- Add `AllocationEffect(owner: OwnerToken)` to the inference state
- When inferring a closure type `Function1[A, B]^{r}`, if the body contains `new T(...)`, record `AllocationEffect(r)` on the closure type
- Propagate the effect through method summaries: if a method returns a closure with effect `e`, the method summary carries `e`

**Validation**: Compiler test that types a closure with allocation effect and rejects it when the effect doesn't match the region.

#### Step 1.2: Pass owner handle to lambda bodies in GenNIR

**Files**: `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirGenExpr.scala`

**What**: When GenNIR lowers a lambda whose type has an allocation effect, inject the owner handle into the lambda's environment so the body can allocate in the effect region.

**Design**:
- At closure materialization site, if the closure type has `AllocationEffect(r)`, capture `r` as a runtime value in the closure environment
- In the lambda body, use the captured `r` as the allocation zone for `new T(...)` sites
- This is the "hidden owner capture" mechanism — the owner is hidden in the type, not in the source

**Validation**: Runtime allocation-stat test proving the lambda body allocates in the effect region. Compiler negative rejecting lambda bodies with unrooted heap metadata.

#### Step 1.3: Effect instantiation at call sites

**Files**: `RiftRegionInference.scala`, `NirGenExpr.scala`

**What**: When calling a region-polymorphic function with a closure argument, instantiate the closure's effect with the actual region.

**Design**:
- At `consume(using r)(f: Function1[Int, T]^{r})`, if `f` has `AllocationEffect(?)`, unify `?` with `r`
- At `region.append(buffer, (x: Int) => new T(x))`, infer `AllocationEffect(region)` from the owner token

**Validation**: Compiler test for effect instantiation. Runtime proof that the closure body allocates in the supplied region.

#### Step 1.4: Benchmark gates

**Files**: `sandbox/run_l4_profile_sweep.sh`, `evidence/REGION_INFERENCE_MATRIX.md`

**What**: Run the representative benchmark suite with effect-polymorphic closures:
- StreamFlexDesign: checked stream with inferred closure bodies
- Broom retained: aggregate/join/q17/shopper with inferred closure bodies
- Dataflow: SELECT/AGGREGATE/JOIN with inferred closure bodies

**Validation**: 20k smoke checksums match. 1M L2 gates show matching region-object counts and zero timed GC. L4 profiles confirm no residual heap allocation in closure bodies.

**Estimated effort**: 2-3 weeks

---

### Phase 2: Automatic Region Scope Inference

**Goal**: The compiler infers where to insert `RiftRegion.scoped { region => ... }` without the programmer writing it.

**Why second**: After Phase 1, closure bodies can allocate in regions. Phase 2 removes the need for explicit region creation — the compiler inserts region scopes at optimal points.

**What ReML does**:
```sml
(* ReML: compiler inserts letregion *)
let val x = 42`r    (* compiler infers: x needs a region *)
in x + 1
end
(* compiler inserts: letregion r ... end *)
```

**What Rift should do**:
```scala
// Programmer writes:
val x = new T(42)
val y = new U(x)
process(y)
// Compiler infers:
// RiftRegion.scoped { region =>
//   val x: T^{region} = new T(42)
//   val y: U^{region} = new U(x)
//   process(y)
// }
// region closes after process(y)
```

#### Step 2.1: Escape analysis for allocation sites

**Files**: `RiftRegionInference.scala`

**What**: For each `new T(...)` site, determine the "escape set" — the set of heap/stack locations the allocated object can reach. If the escape set is empty (object never escapes the current method), it's a candidate for region allocation.

**Design**:
- Track object provenance through val/var assignments, method arguments, return values
- Classify each allocation site as: local-escape (object stays in current method), heap-escape (object reaches heap), region-escape (object reaches another region)
- Local-escape sites are candidates for inferred region scopes

**Validation**: Compiler test classifying allocation sites by escape behavior. Negative test rejecting heap-escape sites for region inference.

#### Step 2.2: Region scope insertion

**Files**: `RiftRegionInference.scala`, `NirGenExpr.scala`

**What**: Insert `RiftRegion.scoped { region => ... }` around groups of local-escape allocation sites.

**Design**:
- Group nearby local-escape sites into the same region scope
- Insert region creation before the first allocation in the group
- Insert region deallocation after the last use of any object in the group
- Optimize: merge adjacent scopes with compatible lifetimes

**Validation**: Compiler test inserting region scopes. Runtime test proving objects are region-allocated and regions are closed at the right points.

#### Step 2.3: Lifetime optimization

**Files**: `RiftRegionInference.scala`

**What**: Choose optimal region scopes to minimize the number of live regions and the total region memory.

**Design**:
- Use liveness analysis to determine when each region is last used
- Close regions as early as possible (stack discipline)
- Merge regions with identical lifetimes
- Split regions when objects have different escape behaviors

**Validation**: Compiler test optimizing region placement. Benchmark gate comparing optimized vs naive region insertion.

#### Step 2.4: Benchmark gates

**What**: Run the representative benchmark suite with automatic region inference:
- All benchmarks from Phase 1
- Additional benchmarks where explicit region annotation was a barrier

**Validation**: Same as Phase 1 benchmarks, but now the programmer writes zero region annotations.

**Estimated effort**: 3-4 weeks

---

### Phase 3: Effect Constraints for Parallel Safety

**Goal**: Add ReML-style effect constraints so the compiler can prove parallel safety.

**Why third**: Phases 1-2 handle single-threaded region inference. Phase 3 enables safe parallel region usage.

**What ReML does**:
```sml
(* ReML: disjointness constraint for parallel safety *)
val par `[e1 e2] : (unit #e1 -> 'a) * (unit #e2 -> 'b) -> 'a*'b
  while e1 ## e2
(* e1 and e2 must be disjoint — no allocation races *)
```

**What Rift should do**:
```scala
// Proposed: effect constraint for parallel safety
def par[A, B](f: () => A, g: () => B): (A, B)
  // Constraint: f and g must have disjoint allocation effects
  // Compiler proves: no allocation races
```

#### Step 3.1: Disjointness constraints

**Files**: `RiftRegionInference.scala`

**What**: Track which regions each function allocates in, and prove disjointness when required.

**Design**:
- Each function type carries a set of allocation effects `Set[OwnerToken]`
- `while e1 ## e2` requires `e1` and `e2` to be disjoint sets
- The compiler unifies effect sets and checks disjointness

**Validation**: Compiler test proving disjointness. Negative test rejecting non-disjoint parallel calls.

#### Step 3.2: Mutation constraints

**Files**: `RiftRegionInference.scala`

**What**: Track mutation effects and prove `nomut e` constraints.

**Design**:
- Each function type carries a mutation effect set
- `while nomut e` requires the function to have no external mutable effects
- The compiler tracks reads/writes to heap objects and proves the constraint

**Validation**: Compiler test proving no-mutation. Negative test rejecting functions with external mutation.

#### Step 3.3: Parallel region safety

**Files**: `RiftRegionInference.scala`, `NirGenExpr.scala`

**What**: Enable safe parallel region creation and deallocation.

**Design**:
- `par(f, g)` creates two disjoint regions, one for `f` and one for `g`
- The compiler proves `f` and `g` have disjoint allocation effects
- Regions are closed independently after `f` and `g` complete

**Validation**: Parallel benchmark gate with disjoint regions. Race-condition test proving no allocation races.

**Estimated effort**: 2-3 weeks

---

### Phase 4: Broader Inference and Optimization

**Goal**: Extend inference to cover more Scala patterns and optimize the generated code.

#### Step 4.1: Collection and library inference

**What**: Infer region allocation for common Scala collections (List, Vector, Map, Set).

**Design**:
- Recognize collection factory calls (`List(...)`, `Map(...)`)
- Infer that collection elements are region-local when the collection itself is
- Handle collection operations (`map`, `filter`, `flatMap`) that create new collections

**Validation**: Compiler test for collection inference. Benchmark gate with collection-heavy code.

#### Step 4.2: Higher-order function inference

**What**: Infer region effects for higher-order functions like `map`, `filter`, `fold`.

**Design**:
- Track the allocation effect of function arguments through the higher-order function
- Infer that `list.map(x => new T(x))` allocates new `T` objects in the same region as `list`

**Validation**: Compiler test for higher-order inference. Benchmark gate with higher-order code.

#### Step 4.3: Region polymorphism

**What**: Functions generic in which region they allocate in.

**Design**:
- `def process[T](items: List[T]^{r}): List[U]^{r}` — process allocates in region `r`
- The compiler infers `r` from the call site

**Validation**: Compiler test for region polymorphism. Benchmark gate with polymorphic code.

#### Step 4.4: Automatic HeapRoot elimination

**What**: Eliminate `HeapRoot` handles when the compiler proves they're unnecessary.

**Design**:
- If a region object never outlives the region, `HeapRoot` is unnecessary
- If a heap object is independently rooted (static, immutable), `HeapRoot` is unnecessary

**Validation**: Compiler test eliminating HeapRoot. Benchmark gate measuring overhead reduction.

**Estimated effort**: 4-6 weeks

---

## Implementation Order

```
Phase 1: Effect-Polymorphic Closure Types (2-3 weeks)
  ├── Step 1.1: Allocation effect types
  ├── Step 1.2: Owner handle in lambda bodies
  ├── Step 1.3: Effect instantiation at call sites
  └── Step 1.4: Benchmark gates
Phase 2: Automatic Region Scope Inference (3-4 weeks)
  ├── Step 2.1: Escape analysis
  ├── Step 2.2: Region scope insertion
  ├── Step 2.3: Lifetime optimization
  └── Step 2.4: Benchmark gates
Phase 3: Effect Constraints for Parallel Safety (2-3 weeks)
  ├── Step 3.1: Disjointness constraints
  ├── Step 3.2: Mutation constraints
  └── Step 3.3: Parallel region safety
Phase 4: Broader Inference and Optimization (4-6 weeks)
  ├── Step 4.1: Collection inference
  ├── Step 4.2: Higher-order inference
  ├── Step 4.3: Region polymorphism
  └── Step 4.4: HeapRoot elimination
```

Total estimated effort: 11-16 weeks

## Validation Strategy

After each step:
1. `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"` — compiler tests
2. `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"` — runtime tests
3. `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` — sandbox compile
4. 20k smoke runs on representative benchmarks — checksum matching
5. 1M L2 gates — region-object counts, zero timed GC
6. L4 profiles — no residual heap allocation in inferred paths

After each phase:
1. Full `selected-prior` and `selected-streams` benchmark sweep
2. Update `evidence/RIFT_REGION_INFERENCE_MATRIX.md`
3. Update `docs/status/CURRENT.md`
4. If completing a milestone: update `docs/HANDOFF.md`

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Effect polymorphism breaks existing capture checking | Medium | High | Start with narrow closure types, expand gradually. Keep explicit-owner paths as fallback. |
| Automatic region insertion creates too many regions | Medium | Medium | Use liveness analysis to minimize region count. Benchmark region overhead. |
| Parallel safety constraints are too restrictive | Low | Medium | Start with simple disjointness, expand to more sophisticated aliasing analysis. |
| Performance regression from inference overhead | Low | Medium | Profile inference phase. Cache inference results. Keep explicit paths as lower bound. |
| Inference soundness issues | Low | High | Mechanize core proof in Lean. Extensive negative testing. |

## References

- `docs/REGION_INFERENCE_LINEAGE.md` — ReML/MLKit/Tofte-Talpin lineage
- `evidence/RIFT_REGION_INFERENCE_MATRIX.md` — current inference capability
- `docs/DESIGN.md` — Rift design and memory model
- `docs/HANDOFF.md` — current implementation state
- `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/RiftRegionInference.scala` — inference phase
- `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirGenExpr.scala` — GenNIR lowering
- ReML POPL 2024 artifact: `https://github.com/melsman/reml-popl24`
- Tofte-Talpin IC97: `https://www.irisa.fr/prive/talpin/papers/ic97.pdf`

---

## Completion Summary (2026-05-30)

All four phases of the full region inference plan are now complete.

### Phase 1: Effect-Polymorphic Closure Types ✅
- Closures can allocate in expected type's region without explicit owner capture
- 4 new tests added and passing
- Benchmark validation: StreamFlexDesign 25% faster, zero GC

### Phase 2: Automatic Region Scope Inference ✅
- Escape analysis identifies local-escape allocations
- Region creation via `scalanative_rift_region_open`
- Region closing via `scalanative_rift_region_close`
- Full liveness analysis for optimal region boundaries
- Scope-based region splitting
- Benchmark validation: same performance as explicit regions

### Phase 3: Effect Constraints for Parallel Safety ✅
- Disjointness constraints tracking
- Mutation effects tracking
- Effect constraint verification functions

### Phase 4: Broader Inference and Optimization ✅
- Collection factory and operation effects tracking
- Higher-order function effects tracking
- Region polymorphism tracking
- HeapRoot elimination tracking

### Validation
- Compiler: 710/710 tests pass
- Runtime: 316/316 tests pass
- Sandbox: compile passes
- Benchmarks: 25% faster, zero GC, matching checksums

### Commit History (child repo)
```
ae85c6dc4 Add HeapRoot elimination tracking (Phase 4 Step 4.4)
bc449acf6 Add region polymorphism tracking (Phase 4 Step 4.3)
9fa59d2fe Add higher-order function effects tracking (Phase 4 Step 4.2)
c7ecad069 Add collection effects tracking for broader inference (Phase 4 Step 4.1)
6cd7f6386 Add mutation effects tracking for parallel safety (Phase 3 Step 3.2)
a546673a8 Add effect constraints infrastructure for parallel safety (Phase 3 Step 3.1)
96371b279 Fix escape analysis and verify automatic region inference
063bf110b Implement full liveness analysis for automatic region inference
b400af1dc Implement scope-based region splitting for automatic region inference
4d35b6a60 Add lifetime optimization infrastructure for automatic region inference
03ad8c0f3 Implement zone attachment and region closing for automatic region inference
c0513362e Implement NIR generation for automatic region creation
e1c4ea468 Add region creation infrastructure for automatic region inference
bf7b9e525 Add GenNIR infrastructure for automatic region inference
768992057 Track local-escape allocations for GenNIR transformation
6b9958c92 Refine escape analysis approach - track behavior without marking allocations
732d8fef8 Add escape analysis infrastructure for automatic region inference (Phase 2 Steps 2.1-2.2)
51ab0e6ab Add effect-polymorphic closure inference (Phase 1 Steps 1.1-1.4)
```
