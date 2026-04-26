# REPORT — Scala 3 capture checking: what we can and can't express

**Status**: partially filled from the current Scala-next checked Rift API slice.
This is not a complete Phase 7 report yet.
**Checked compiler version**: `3.8.4-RC1-bin-20260402-44bbcdf-NIGHTLY`
via `ENABLE_EXPERIMENTAL_COMPILER=1` in the Scala Native fork.

This report documents, precisely, which patterns from Rift's design the shipping Scala 3 capture checker can and cannot express. If anything in this report contradicts the design, the design changes, not the report.

## 1 — Executive summary

Current result:

Scala-next capture checking supports the first Rift safe API slice:

- ordinary Scala object graphs allocated in `RiftRegion.scoped`;
- transient for-loop allocation inside a scoped region;
- nested scoped regions returning pure values;
- non-escaping closures that read scoped region values;
- higher-order helper functions that consume a region-allocated value and return
  a non-region value;
- rejection of direct return escape, heap retention through an object field, an
  inner scoped value escaping an outer scope, and streaming reset values
  escaping an epoch.
- conservative rejection of function values returned directly from checked
  `scoped`, `streaming`, and `reset` boundaries. This closes the previously
  observed returned-closure escape in the v1 API by rejecting that whole result
  shape for now.

Known gaps remain:

- The returned-closure gap is closed conservatively, not precisely. The API
  rejects direct function results even if a particular returned function is pure
  and does not capture region-local state. A future compiler/API extension
  should distinguish those cases.
- The checker slice does not enforce the full mixed-reference policy. In
  particular, unrooted region-to-GC ownership still needs either static
  rejection, explicit root handles, or GC-visible region metadata.
- The tests validate source-level capture behavior and allocation lowering.
  They do not yet prove safe close/reset mechanically.

Targeted command run on 2026-04-26:

```bash
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"
```

Result:

```text
Passed: Total 11, Failed 0, Errors 0, Passed 11
```

Runtime smoke command run on 2026-04-26:

```bash
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionTest scala.scalanative.memory.RiftRegionCheckedTest"
```

Result:

```text
Passed: Total 9, Failed 0, Errors 0, Passed 9
```

## 2 — The three hard patterns

### 2.1 — Pattern (a): region value through a for-loop

```scala
RiftRegion.scoped { rg ?=>
  var total = 0
  for i <- 1 to 1000 do
    val p = rg.alloc(new Box(i))
    total += 1
  total
}
```

- **Expectation**: compiles.
- **Result**: compiles.
- **Evidence**:
  `nscplugin/src/test/scala-next/scala/RiftRegionCheckedCompilerTest.scala`,
  `scopedForLoopAllocationCompiles`.
- **Notes**: this tests whether the `for` loop's closure-like translation keeps
  the region capability transient.

### 2.2 — Pattern (b): nested regions with outer-return

```scala
RiftRegion.scoped { outer ?=>
  RiftRegion.scoped { inner ?=>
    var sum = 0
    for i <- 1 to 100 do
      val p = inner.alloc(new Box(i))
      sum += 1
    sum
  }
}
```

- **Expectation**: compiles; the `inner` capability does not escape because the return value is a pure `Int`.
- **Result**: compiles for pure return values.
- **Evidence**:
  `nscplugin/src/test/scala-next/scala/RiftRegionCheckedCompilerTest.scala`,
  `nestedScopedRegionsReturningPureValueCompiles`.
- **Negative evidence**: returning an inner-region object to the outer scope
  fails in `innerScopedValueCannotEscapeOuterScope`.
- **Notes**: a dedicated positive test for returning an outer-region value from
  an inner block has not been added yet.

### 2.3 — Pattern (c): higher-order region-parameterized functions

Two sub-patterns, each with increasing difficulty:

**(c.i)** — helper takes a region + a consumer:

```scala
def withBox(using rg: RiftRegion.ScopedRegion^)(
    use: Box^{rg} => Int
): Int =
  val box: Box^{rg} = RiftRegion.alloc(new Box(40))
  use(box)
```

- **Expectation**: compiles.
- **Result**: compiles for a non-capturing result type (`Int`).
- **Evidence**:
  `nscplugin/src/test/scala-next/scala/RiftRegionCheckedCompilerTest.scala`,
  `scopedHigherOrderConsumerCompiles`.
- **Notes**: this is enough for many local helper/consumer patterns. It is not
  yet evidence for a fully capture-polymorphic collection API.

**(c.ii)** — helper returns a region-parameterized closure (the Tofte-Talpin / StreamFlex hard case):

```scala
// Desired: given a region, produce a map from Int to a region-allocated Array.
def memoInRegion(using rg: ScopedRegion): Int => Array[Int]^{rg} = ???
```

- **Expectation**: may require reach capabilities (`rg*`) or explicit capture-set parameters.
- **Result**: rejected conservatively for now. A direct probe where a returned
  closure captured only a region-local value compiled before the
  `CanReturnFromRegion` guard. The v1 checked API now rejects direct
  `Function0`-`Function22` results from `scoped`, `streaming`, and `reset`
  boundaries with the diagnostic `Rift checked regions cannot return function
  values yet`.
- **Notes**: the exact formulation matters. Document the minimal working
  version before using this shape in benchmark APIs. This is safe but
  conservative, and it is more restrictive than the final Rift target.

## 3 — Negative tests

Current checked compiler probes:

| Test | Expected failure | Result | Notes |
|---|---|---|---|
| `scopedValueCannotEscapeByReturn` | scoped value returned from `RiftRegion.scoped` | fails | Error text is not pinned yet; test only requires a compiler diagnostic. |
| `innerScopedValueCannotEscapeOuterScope` | inner scoped value returned through outer scope | fails | Covers nested-region leakage. |
| `closureCapturingScopedValueCannotEscape` | closure stored in heap state while capturing region handle | fails | Does not cover the harder closure-local-value-only escape gap. |
| `closureCapturingScopedValueCannotEscapeByReturn` | closure returned from scoped region while capturing region-local value | fails | Rejected by the v1 `CanReturnFromRegion` function-result guard. |
| `heapObjectCannotRetainScopedValue` | heap singleton retains scoped value | fails | Covers GC-to-region retention through heap state. |
| `streamingResetValueCannotEscapeEpoch` | value allocated inside reset epoch used after reset | fails | Covers reset boundary at source level. |

Still missing:

- a negative test for unrooted region-to-GC ownership;
- more tests with expected diagnostic text pinned to capture-specific wording;
- precise support for pure returned closures that provably do not capture
  region-local state.

## 4 — Interactions with Scala Native

Three specific concerns that Scala 3 (JVM) developers don't hit:

1. **Extern methods and capture sets.** The safe Scala API does not annotate C
   extern functions directly. Allocation goes through Scala wrappers whose
   result type captures the region capability, then lowers to the Rift runtime.
2. **`T^{rg}` at the NIR level.** The tests show the source program typechecks
   and NIR compilation succeeds, but this report has not yet archived
   `-Xprint:nir` output.
3. **Inlining and capture sets.** `RiftRegion.alloc` is inline, while
   `allocImpl` is noinline for lowering. The current tests pass through this
   path, but an explicit inline-stability test has not been added.

## 5 — Upstream issues filed

None filed from this report slice yet.

## 6 — Recommendations for Phase 8 writeup

Claim only the checked slice that is tested:

- scoped ordinary object graphs can be allocated and used without escape;
- streaming reset boundaries can reject direct epoch-value escape;
- local higher-order consumers are expressible.

Do not yet claim:

- precise support for returned closures; v1 rejects direct function results
  conservatively;
- complete mixed GC/region safety;
- automatic allocation inference;
- a mechanized proof.

The next Phase 8 design decision should be whether unrooted region-to-GC
references are rejected statically in safe APIs or represented through explicit
GC-visible root handles. The Phase 4 checksum mismatch is the concrete reason
this cannot be left implicit.
