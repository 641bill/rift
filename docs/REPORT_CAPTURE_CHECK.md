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
- explicit heap-root handles for region objects that need to refer to heap
  metadata. `RiftRegion.root(value)` returns a `HeapRoot[T]` retained through
  the live region object's GC-visible root list.
- static heap metadata has a narrow checked path: top-level/module singleton
  references and immutable vals selected from those modules may be stored in
  region objects, while mutable static vars are still rejected.
- rejection of direct unrooted heap-object constructor arguments in checked
  Rift allocation lowering. Ordinary region-to-region object graph references
  still compile, and simple local aliases of known region values are propagated.
- selected stable constructor fields can be reused when their field type is
  explicitly tied to the region capability, for example a local
  `Pair(val leaf: Leaf^{region})`. Plain `Leaf^` fields remain rejected by
  Scala capture checking when the result is required to be `Leaf^{region}`.
- region-owned arrays can be used as checked containers when both the array
  object and reference element type are explicitly region-captured, for example
  `Array[Leaf^{region}]^{region}`. Stores into known region arrays are checked
  so unrooted heap objects cannot be retained by region memory; `HeapRoot`
  values are allowed.
- `RiftRegion.ObjectBuffer` is the first checked higher-level container
  primitive. It region-allocates the backing object array and keeps only heap
  control metadata. Operations use an owner-token API, either
  `RiftRegion.append(region, buffer, value)` or the lighter
  `region.append(buffer, value)` extension syntax, so the current checker can
  reject direct heap stores and inner-region values stored into an outer
  buffer.
- `RiftRegion.RegionBuffer` extends the same owner-token checked-container
  rule to growable buffers. Growth allocates the replacement backing object
  array in the owner region, copies existing references, and relies on region
  close/reset to reclaim old backing arrays. Compiler probes cover region
  objects, explicit `HeapRoot` handles, direct heap-store rejection, and
  inner-region-to-outer-buffer rejection; the native smoke covers actual
  growth.
- `RiftRegion.RegionPriorityQueue` extends the owner-token checked-container
  rule to ranking/top-k state. Values live in a region-owned object array,
  priorities live in a parallel region-owned `Long` array, and `push` is
  guarded so direct heap values are rejected unless wrapped in `HeapRoot`.
- `RiftRegion.RegionIndexedPriorityQueue` extends the same rule to dense-key
  mutable ranking state. `put` is guarded like `push`; `get`, `contains`,
  `updatePriority`, `peek`, and `pop` let checked stream code fetch ordinary
  region objects by key, mutate their fields, and update ranking priority
  without allocating a new object every refresh. The lexicographic priority
  overloads use the same value-store guard while allowing Q1-style
  count/time/sequence/key tie-breakers.
- `RiftRegion.StreamWindowIndexedRank` composes dense-key ranking with
  stream-bucket child regions. Bucket-owned rank entries are unlinked before
  the child bucket closes, close-with-entry callbacks let operators clean side
  tables during framework unlinking, and direct heap values are rejected through
  the same checked put guard.
- The first literature-shaped safe API probes now compile: streaming reset
  epochs can process region-owned arrays of ordinary record objects, a
  top-word-style `ObjectBuffer` can store records that refer to heap metadata
  through explicitly rooted handles, and a GraphChi-style subinterval update
  can use rooted durable heap vertex metadata.
- The reset boundary now has an explicit negative probe for a subtle epoch
  escape: a value allocated inside `RiftRegion.reset` cannot be stored into an
  outer streaming-region `ObjectBuffer` and then read after reset.
- The checked mixed-reference guard is intentionally limited to the checked
  `RiftRegion.ScopedRegion`/`RiftRegion.StreamingRegion` API surface.
  Low-level `RiftRegion.open(...)` remains a trusted benchmark/runtime API; a
  regression test confirms it can still allocate linked benchmark objects.
- Mutable region-owned linked-list builders now work in checked code when the
  mutable head is built from `null`, direct Rift allocations, or values already
  known to be region-owned. Assigning a heap object to that head removes the
  region-owned provenance and is rejected if later stored into region memory.
- `RiftRegion.childWindow` now has a structured close boundary. User code calls
  `RiftRegion.closeChildWindow(parent, window) { cleanup }`; direct
  `window.close()` is not public user API and is rejected by the compiler
  probe. Reusing a child window after close is rejected at runtime.
- `RiftRegion.ChildBucket` adds a reusable checked stream-bucket wrapper over
  the child-window pattern. User code allocates with `childBucket`, obtains the
  owner-token child region with `childBucketRegion(parent, bucket)`, and closes
  with `closeChildBucket(parent, bucket) { cleanup }`. Direct raw-window access
  through `bucket.window` is rejected.

Known gaps remain:

- The returned-closure gap is closed conservatively, not precisely. The API
  rejects direct function results even if a particular returned function is pure
  and does not capture region-local state. A future compiler/API extension
  should distinguish those cases.
- The new unrooted heap-reference rejection is still a conservative compiler
  lowering guard, not full alias analysis. It covers direct constructor
  arguments in checked Rift allocation and allows values known to be allocated
  in the same region, simple local aliases of those values, primitives/null,
  `HeapRoot` handles, static module singletons, immutable static/module vals,
  and stable primary-constructor field selections whose source type is
  explicitly region-captured. It also checks stores into known region arrays
  and the current owner-token `ObjectBuffer`/`RegionBuffer`/
  `RegionPriorityQueue`/`RegionIndexedPriorityQueue`/stream-window rank APIs.
  Broader
  cases such as plain `T^` fields, richer static-field provenance, and plain
  receiver-style collection/container abstractions still need a more precise
  policy or compiler extension.
- Mutable linked-list support is provenance-based rather than path-sensitive.
  It tracks observed local assignments to mutable heads, but it is not a full
  dataflow or alias analysis for arbitrary mutable containers.
- The tests validate source-level capture behavior, allocation lowering, and
  the current child-window close boundary. They do not yet prove full
  affine/linear safe close/reset mechanically.

Targeted command run on 2026-04-28:

```bash
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"
```

Result:

```text
Passed: Total 58, Failed 0, Errors 0, Passed 58
```

Runtime smoke command run on 2026-04-27:

```bash
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionTest scala.scalanative.memory.RiftRegionCheckedTest"
```

Result:

```text
Passed: Total 15, Failed 0, Errors 0, Passed 15
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
| `scopedValueCannotEscapeByReturn` | scoped value returned from `RiftRegion.scoped` | fails | Pins the expected scope-leak diagnostic. |
| `innerScopedValueCannotEscapeOuterScope` | inner scoped value returned through outer scope | fails | Covers nested-region leakage. |
| `closureCapturingScopedValueCannotEscape` | closure stored in heap state while capturing region handle | fails | Does not cover the harder closure-local-value-only escape gap. |
| `closureCapturingScopedValueCannotEscapeByReturn` | closure returned from scoped region while capturing region-local value | fails | Rejected by the v1 `CanReturnFromRegion` function-result guard. |
| `heapObjectCannotRetainScopedValue` | heap singleton retains scoped value | fails | Covers GC-to-region retention through heap state. |
| `rootedHeapValueCanBeStoredInScopedObject` | region object stores explicit `HeapRoot` for heap metadata | compiles | Covers the v1 explicit-root policy for region-to-GC references. |
| `staticModuleCanBeStoredInScopedObject` | region object stores a static module singleton | compiles | Covers independently rooted static metadata. |
| `staticValCanBeStoredInScopedObject` | region object stores an immutable heap object selected from a static module val | compiles | Covers immutable module-held heap metadata. |
| `staticVarCannotBeStoredInScopedObject` | region object stores a heap object read from a mutable static module var | fails | A mutable static var can stop rooting the object later, so it still requires `HeapRoot`. |
| `directHeapValueCannotBeStoredInScopedObject` | region object constructor receives a direct unrooted heap object | fails | Covers the v1 lowering guard for the simplest unsafe region-to-GC ownership shape. |
| `regionAllocatedAliasCanBeStoredInScopedObject` | region object constructor receives a local alias of a known region value | compiles | Keeps normal local aliasing usable for ordinary region object graphs. |
| `heapAliasCannotBeStoredInScopedObject` | region object constructor receives a local alias of a heap object | fails | Prevents simple aliasing from bypassing the direct heap-reference guard. |
| `heapFieldSelectionCannotBeStoredInScopedObject` | region object constructor receives a field selected from a heap object | fails | Prevents heap field selection from bypassing the direct heap-reference guard. |
| `explicitRegionParamFieldCanBeStoredInScopedObject` | stable constructor field with type `Leaf^{region}` is reused in another region object | compiles | Covers the supported selected-field path. |
| `explicitRegionParamFieldAliasCanBeStoredInScopedObject` | alias of a stable constructor field with type `Leaf^{region}` is reused | compiles | Covers selected-field alias propagation after the source checker proves the region capture. |
| `plainRegionOwnerParamFieldCannotBeStoredAsRegionValue` | plain `Leaf^` field from a region-local owner is reused where `Leaf^{region}` is required | fails | Current Scala capture checking gives the field its own capability; this is a real ergonomics limitation. |
| `regionOwnedArrayCanBeStoredInScopedObject` | region object stores a region-owned array with region-captured element type | compiles | Covers array-as-container constructor use. |
| `regionOwnedArrayCanStoreRegionObject` | region-owned array stores a region-allocated object | compiles | Requires `Array[Leaf^{region}]^{region}` rather than just `Array[Leaf]^{region}`. |
| `regionOwnedArrayCannotStoreHeapObject` | region-owned array stores an unrooted heap object | fails | Covers the new array-store guard. |
| `heapArrayCannotBeStoredInScopedObject` | region object stores a heap array | fails | Prevents heap containers from becoming region-owned implicitly. |
| `regionOwnedArrayCanStoreHeapRoot` | region-owned array stores explicit `HeapRoot` handles | compiles | Covers the safe heap-metadata container path. |
| `objectBufferCanStoreRegionObjects` | companion owner-token `ObjectBuffer` append stores region objects | compiles | First checked higher-level container primitive. |
| `objectBufferCannotStoreHeapObject` | companion owner-token `ObjectBuffer` append stores direct heap object | fails | Uses the Rift append lowering guard; heap metadata must use `HeapRoot`. |
| `objectBufferOwnerMethodsCanStoreRegionObjects` | owner-token extension methods store/read region objects with `region.append/get/length` | compiles | Ergonomic method syntax over the same checked owner-token rule. |
| `objectBufferOwnerMethodsCannotStoreHeapObject` | owner-token extension append stores direct heap object | fails | Confirms extension syntax is guarded like the companion function. |
| `objectBufferCanStoreHeapRoot` | companion owner-token `ObjectBuffer` append stores `HeapRoot` handles | compiles | Covers heap metadata through the checked buffer API. |
| `objectBufferCannotStoreInnerScopedValue` | outer buffer stores value allocated in inner region | fails | Explicit owner token lets capture checking reject cross-region storage. |
| `objectBufferCannotEscapeScopedRegion` | checked buffer escapes owning region | fails | Covers the heap-control/region-data boundary. |
| `regionBufferCanGrowAndStoreRegionObjects` | growable owner-token `RegionBuffer` stores region objects and grows | compiles | Extends the checked container story beyond fixed-capacity buffers. |
| `regionBufferCannotStoreHeapObject` | growable `RegionBuffer` append stores direct heap object | fails | Confirms the append lowering guard covers growable buffers too. |
| `regionBufferCanStoreHeapRoot` | growable `RegionBuffer` stores explicit `HeapRoot` handles | compiles | Covers durable heap metadata through a growable checked buffer. |
| `regionBufferCannotStoreInnerScopedValue` | outer growable buffer stores value allocated in inner region | fails | Confirms owner tokens still prevent cross-region storage after growth support. |
| `regionPriorityQueueCanStoreRegionObjects` | owner-token `RegionPriorityQueue` stores and pops region objects by priority | compiles | Adds the first checked ranking/top-k container primitive. |
| `regionPriorityQueueCannotStoreHeapObject` | checked priority-queue push stores direct heap object | fails | Confirms the push lowering guard covers ranking containers. |
| `regionPriorityQueueCanStoreHeapRoot` | checked priority queue stores explicit `HeapRoot` handles | compiles | Covers durable heap metadata through ranking/top-k containers. |
| `regionPriorityQueueCannotStoreInnerScopedValue` | outer priority queue stores value allocated in inner region | fails | Confirms owner tokens still prevent cross-region storage for ranking state. |
| `regionIndexedPriorityQueueCanUpdatePriority` | indexed priority queue stores region objects, fetches by key, and updates rank priority | compiles | Adds durable dense-key ranking state for mutable stream records. |
| `regionIndexedPriorityQueueCanReplaceValueForKey` | indexed priority queue replaces the value for an existing key | compiles | Covers keyed replacement without growing logical queue length. |
| `regionIndexedPriorityQueueCannotStoreHeapObject` | indexed priority-queue `put` stores direct heap object | fails | Confirms the `put` lowering guard covers indexed ranking containers. |
| `regionIndexedPriorityQueueCanStoreHeapRoot` | indexed priority queue stores explicit `HeapRoot` handles | compiles | Covers durable heap metadata through keyed ranking containers. |
| `regionIndexedPriorityQueueCannotStoreInnerScopedValue` | outer indexed priority queue stores value allocated in inner region | fails | Confirms owner tokens still prevent cross-region storage for keyed ranking state. |
| `streamingResetRegionArrayEpochCompiles` | reset epoch processes a region-owned array of ordinary records | compiles | Models sort/dataflow epoch records through the supported checked array shape. |
| `topwordBufferCanStoreRecordsWithRootedMetadata` | top-word-style buffer stores records that carry rooted heap metadata | compiles | Covers durable heap metadata via `HeapRoot` inside a higher-level checked buffer. |
| `graphChiSubintervalCanUseRootedHeapVertexMetadata` | GraphChi-style subinterval record refers to durable heap vertex metadata through `HeapRoot` | compiles | Covers the safe data/control split for graph updates. |
| `graphChiSubintervalCannotStoreUnrootedHeapVertex` | GraphChi-style subinterval record stores direct heap vertex metadata | fails | Confirms durable heap metadata still needs `HeapRoot`. |
| `streamingResetValueCannotBeStoredInOuterBuffer` | reset epoch value is stored into an outer streaming buffer and read after reset | fails | Important epoch-boundary regression probe. |
| `trustedOpenAllocationAllowsBenchmarkLinkedObjects` | trusted `RiftRegion.open(RiftRegion.HPZone)` allocates linked objects | compiles | Documents the intended split: `open` is trusted/unsafe; `scoped` and `streaming` are checked. |
| `checkedMutableLinkedListBuilderCompiles` | mutable scoped linked-list head is initialized from `null` and updated only from Rift allocations | compiles | Covers ordinary linked region object builders without falling back to arrays. |
| `mutableRegionHeadCannotBeRetaggedFromHeapObject` | mutable region head is assigned a heap object and then stored into a region object | fails | Confirms heap assignment drops region-owned provenance. |
| `streamingResetValueCannotEscapeEpoch` | value allocated inside reset epoch used after reset | fails | Covers reset boundary at source level. |

Still missing:

- broader negative probes beyond the current set; all current negative compiler
  probes now pin an expected capture/safety diagnostic substring;
- broader mixed-reference tests for plain `T^` selected fields, static
  immutable heap values, and higher-level collection/container abstractions;
- richer mutable-shape tests beyond the local linked-list head case;
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
- local higher-order consumers are expressible;
- local mutable linked-list heads are supported when assignments are `null`,
  Rift allocations, or known region values, and heap assignments drop the
  tracked region provenance.

Do not yet claim:

- precise support for returned closures; v1 rejects direct function results
  conservatively;
- complete mixed GC/region safety. `HeapRoot` gives an explicit safe path for
  region-to-GC metadata, and direct unrooted constructor arguments are now
  rejected in checked Rift allocation lowering. Static module singletons and
  immutable static/module vals are supported, while mutable static vars are
  rejected. Stable constructor fields whose source types are explicitly tied to
  `{region}` are supported, but plain `T^` selected fields, richer static-field
  provenance, and general collection aliases are not fully modeled yet.
  Region-owned arrays are supported only with
  explicit element captures such as `Array[Leaf^{region}]^{region}`.
  `ObjectBuffer` is supported only through owner-token APIs; both companion
  functions and `region.append/get/length` extension methods are covered.
  `RegionBuffer` uses the same owner-token policy for growable buffers.
- full dataflow analysis for arbitrary mutable structures; the current mutable
  linked-list support is a local provenance rule only.
- automatic allocation inference;
- a mechanized proof.

The next Phase 8 design decision is how far to extend the allocation rule after
the first `HeapRoot`, direct-constructor-argument guard, static-root path, and
owner-token buffer path: aliases, field selections, richer static-field
provenance, and richer container values need either a checked policy or
trusted-only labeling. Simple region-local aliases are currently propagated;
heap aliases and heap field selections are rejected; explicitly
region-captured constructor fields and arrays are
accepted. The Phase 4 checksum mismatch is the concrete reason this cannot be
left implicit.
