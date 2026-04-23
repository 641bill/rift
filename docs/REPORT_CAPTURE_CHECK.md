# REPORT — Scala 3 capture checking: what we can and can't express

**Status**: draft. To be filled in during Phase 6.
**Pinned Scala version**: `3.8.0-RC3` (see `build.sbt`).

This report documents, precisely, which patterns from Rift's design the shipping Scala 3 capture checker can and cannot express. If anything in this report contradicts the design, the design changes, not the report.

## 1 — Executive summary

To be filled in once Phase 6 completes. Template:

> Scala 3.8 capture checking supports patterns (a), (b), and most of (c) without extension. Pattern (c.ii) — higher-order functions that return region-parameterized closures — requires [extension X / workaround Y / is expressible but awkward]. The design document has been updated at §N to reflect this.

## 2 — The three hard patterns

### 2.1 — Pattern (a): region value through a for-loop

```scala
Region.scoped { rg ?=>
  var total = 0
  for i <- 1 to 1000 do
    val p = rg.allocBytes(16)
    total += 1
  total
}
```

- **Expectation**: compiles.
- **Result**: TBD.
- **Notes**: this tests whether the `for`-loop's implicit closure over `rg` is correctly handled as transient capture.

### 2.2 — Pattern (b): nested regions with outer-return

```scala
Region.scoped { outer ?=>
  Region.scoped { inner ?=>
    var sum = 0
    for i <- 1 to 100 do
      val p = inner.allocBytes(16)
      sum += 1
    sum  // Int — no capture of inner
  }
}
```

- **Expectation**: compiles; the `inner` capability does not escape because the return value is a pure `Int`.
- **Result**: TBD.
- **Notes**: what happens if the inner block returns `Ptr[Byte]^{outer}`? Should compile. What if it returns `Ptr[Byte]^{inner}`? Should fail.

### 2.3 — Pattern (c): higher-order region-parameterized functions

Two sub-patterns, each with increasing difficulty:

**(c.i)** — helper takes a region + a consumer:

```scala
def withBuffer[T](using rg: ScopedRegion)(n: Int)(use: Ptr[Byte]^{rg} => T): T =
  val buf = rg.allocBytes(n)
  use(buf)
```

- **Expectation**: compiles.
- **Result**: TBD.

**(c.ii)** — helper returns a region-parameterized closure (the Tofte-Talpin / StreamFlex hard case):

```scala
// Desired: given a region, produce a map from Int to a region-allocated Array.
def memoInRegion(using rg: ScopedRegion): Int => Array[Int]^{rg} = ???
```

- **Expectation**: may require reach capabilities (`rg*`) or explicit capture-set parameters.
- **Result**: TBD.
- **Notes**: the exact formulation matters. Document the minimal working version.

## 3 — Negative tests

For each file in `tests/neg/`, record the error message Scala 3.8 produces. If the error is confusing or misleading, file an upstream issue on the Scala repository and link it here.

| Test file | Expected failure | Actual error message | Notes |
|---|---|---|---|
| `EscapeViaReturn.scala` | escape | — | — |
| `EscapeViaClosure.scala` | escape via closure | — | — |
| `UseAfterReset.scala` | separation/reset | — | — |

## 4 — Interactions with Scala Native

Three specific concerns that Scala 3 (JVM) developers don't hit:

1. **`@extern` methods and capture sets.** Do capture annotations survive the extern boundary? Specifically: can `RiftC.rift_alloc_slow` have a capture set, or does extern erase it?
2. **`Ptr[T]^{rg}` at the NIR level.** The capture annotation is erased at runtime, but does it survive the typer-to-NIR transformation in the compiler plugin? Verify with `-Xprint:nir`.
3. **`@alwaysinline` and capture sets.** If we mark an allocation wrapper `inline`, does the capture information survive inlining?

## 5 — Upstream issues filed

List each Scala (or Scala Native) issue filed during Phase 6. Format:

- `scala/scala3#NNNNN` — one-line description — status.

## 6 — Recommendations for Phase 8 writeup

To be filled in: what the thesis should claim about capture-checking integration, what it should not claim, what work is carved out as "requires a separate paper."
