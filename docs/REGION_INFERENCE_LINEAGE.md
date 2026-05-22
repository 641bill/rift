# Region Inference Lineage And Rift Adaptation

Last updated: 2026-05-21 21:50 CEST

Status: design investigation and roadmap note. This document records how Rift
relates to the Tofte/Talpin, MLKit, and ReML region-inference lineage. It is
not a claim that Rift already implements the full lineage.

## Summary

Rift is inspired by the Tofte/Talpin -> MLKit -> ReML line of region-based
memory-management work, but it does not currently implement that full
algorithmic system.

Current Rift is closer to:

```text
explicit checked lifetime topology
+ Scala capture/separation safety
+ selective compiler placement lowering
```

It is not yet:

```text
whole-program region inference
+ inferred region variables
+ inferred allocation/effect summaries
+ compiler-inserted region creation/deallocation
+ full polymorphic region/effect constraints
```

The implemented Scala Native inference slices are deliberately narrow:

- 2026-05-20 profiling found a related but distinct inference/ownership
  problem: making checked region-body callbacks inlineable would reduce
  callback/session-loop overhead, but a direct `inline resetOpenHandle`
  experiment failed because capture checking widened the open handle owner to
  `{any}` in many valid benchmark bodies. This is not a runtime-only patch; it
  belongs on the ReML-style inference/effect-summary roadmap as
  ownership-preserving inlining of checked region bodies. Narrower internal
  `resetOpenHandleInline` probes now work for simple and non-inline-wrapper
  open-handle bodies, including region-owned arrays and region-local element
  stores, by delegating the final raw reset to a non-inline helper. The current
  limits are also explicit: enclosing `inline def` wrappers still lose the
  open-handle owner capture, and mixed runtime branches between inferred
  `new` and explicit `allocateOpenHandle` remain rejected rather than
  unsafely inferred. The current practical workaround is to avoid that rejected
  source shape in reusable checked paths: the Wikimedia
  `checked-rift-inferred` session mode is split out of the enclosing inline
  wrapper and uses a sandbox-only bridge to the internal inline reset helper,
  improving the 1M L2 row without changing public APIs or query semantics. A
  follow-up state-local cleanup moved mutable loop counters inside the
  open-handle callback; fresh L4 no longer samples boxed
  `scala.runtime.*Ref` top-frame parameters. The next inference slice now
  handles local branch/match-final construction under captured expected types,
  including mixed inferred `new` versus explicit `allocateOpenHandle` branches.
  Theodolite retained UC4 now exercises the active open-handle ordinary-`new`
  source form for measurement and contribution records in the real
  streaming-file path, while keeping scoped/open-region and legacy explicit
  allocation controls unchanged.
  Broader callback inlining, especially enclosing inline-wrapper ownership
  preservation for join-style paths, still belongs on the compiler
  ownership/effect-summary track.

- 2026-05-20 closure-body follow-up: Rift now supports one narrow
  ReML-style closure-body allocation case plus direct and immutable-local
  method-returned closure variants and immutable-local owner-token method
  arguments. If a region-owned closure explicitly captures the same checked
  owner term named by its expected type, GenNIR records the owner symbol as
  well as the runtime owner value and can place a body-local returned `new`
  through that owner. For closures returned from explicit checked-owner
  methods, the closure wrapper is also placed in the checked region when the
  method result type is captured by that owner; this now includes
  `{ val f = (n: Int) => ...; f }` shapes without a captured type ascription on
  `f`. For owner-token calls, a named immutable local closure passed to
  `consume(using r)(f)` now inherits the supplied owner when the parameter type
  is captured by `r`, and the same proof covers simple branch/match arguments
  such as `consume(using r)(if flag then first else second)` or a matching
  `selector match` when every selected local closure is constrained by that
  owner. For materialized returned/local closure values, runtime counters prove
  wrapper and body allocations are checked-region objects, and compiler
  negatives reject unrooted heap metadata plus uncaptured escaping `Function1`
  results.
  Direct inline closures selected by `if` or `match` also have compiler and
  runtime proof for the explicitly captured owner body allocation; the runtime
  proof only claims the selected body object because that native shape observed
  no separately counted materialized wrapper. The same direct-inline
  branch/match body proof is now covered for captured local expected types,
  not only owner-token method arguments. Immutable selected-alias shapes such
  as `val selected = if flag then first else second` followed by
  `consume(using r)(selected)` now preserve the original closure-local symbols,
  so the materialized selected closures and selected body allocation can be
  checked-region allocated. The same selected-alias map now feeds explicit
  checked-owner method returns, so
  `def make(flag)(using r) = { val first = ...; val second = ...; val selected = if flag then first else second; selected }`
  can return region-owned selected closure wrappers and still place the
  explicitly captured-owner body allocation. Mutable selected aliases still
  remain future work.
  The 2026-05-21 forwarding proof confirms the same captured-owner body effect
  survives one extra summary hop without a production compiler change:
  `def wrap(using r) = make(using r)` preserves the returned closure wrapper and
  body allocation; simple branch/match wrappers over `make(using r)` do the
  same; and `val selected = ...; val forwarded = selected; forwarded`
  preserves selected local closure candidates through the method-return
  summary. Runtime allocation counters prove the direct/branch/match wrapper
  body objects and
  selected-wrapper/body objects are checked-region allocations; unrooted heap
  metadata negatives still reject the corresponding body captures.
  A subsequent direct returned-closure proof validates the next closure-body
  summary hop: when an owner-proven closure body directly returns another
  closure that explicitly captures the same runtime checked owner term, the
  returned closure wrapper and its nested captured-owner body allocation are
  both checked-region allocations. The deliberately attempted broad fallback
  for arbitrary owner-capturing closures was rejected by stale-token runtime
  probes, because closure construction itself can then allocate into an
  already-closed region before the program reaches the intended checked
  operation. A named-local follow-up validates that specific local-wrapper
  variant first with an explicit captured local function type and then without
  that local type ascription, as long as the enclosing closure result type names
  an explicit checked owner and GenNIR can recover the same runtime owner term.
  Runtime counters prove the outer closure wrapper, named local wrapper, and
  nested body object are all checked-region allocations.
  The next stored-closure follow-up extends that same explicit-owner body
  effect to direct inline closures stored through region-owned arrays and
  checked owner-token containers. The array path remains deliberately bounded:
  when primitive array update lowering erases the element capture, GenNIR may
  use the already inferred region-owned array object owner only if the stored
  closure captures the same runtime owner, including simple owner aliases such
  as `val owner = region`. Runtime counters prove the direct array store,
  ObjectBuffer append, and selected RegionBuffer append variants allocate the
  closure wrapper and body object in checked-region memory; unrooted metadata
  captured by the stored closure still rejects. The follow-up priority-queue
  proof validates the same owner-token closure-body effect for ordinary
  `RegionPriorityQueue.push`: inline and selected immutable local closure
  values can allocate captured-owner body objects in the checked region, and
  the paired negative rejects unrooted metadata captured by the pushed closure
  body. The newest simple-wrapper proof carries that owner through
  region-owned constructor/factory arguments as well: direct inline closures
  and selected immutable local closure aliases nested inside `new Wrapper(...)`
  inherit the wrapper's proven checked owner, and runtime counters prove the
  wrapper, closure wrapper, and captured-owner body allocation are checked-region
  objects. The same proof now crosses an explicit checked-region method
  boundary for the library wrapper `Some(closure)`: method-returned inline and
  selected local closure values retain the method result owner, and runtime
  counters prove the `Some`, closure wrapper, and body allocation are
  checked-region objects. The follow-up owner-token proof covers generic
  wrappers passed as checked method arguments too:
  `consume(using r)(new Wrapper[T^{r}](closure))` now validates wrapper,
  closure, and captured-owner body allocation under the owner supplied by the
  method parameter. The newest closure-body callee-summary proof extends the
  body effect by one explicit checked-region callee: a region-owned closure may
  call `build(value)(using owner): T^{owner}` and return the callee-allocated
  value when the same runtime owner term is captured by the closure body.
  Runtime counters prove the closure wrapper plus callee-allocated result are
  checked-region objects, and the paired negative rejects unrooted heap
  metadata flowing through the callee allocation. The newest follow-up adds one
  simple forwarding hop:
  `forward(value)(using owner): T^{owner} = build(value)(using owner)` can be
  called from the same captured-owner closure body, with runtime counters again
  proving the closure wrapper plus forwarded callee-allocated result are
  checked-region objects. The newest follow-up validates simple control-flow
  forwarding too: branch and match wrappers whose every path returns
  `build(...)(using owner): T^{owner}` preserve the same closure-body effect,
  and runtime counters prove the executed branch/match callee result is
  checked-region allocated.
  This is not hidden owner capture, lambda-signature rewriting, arbitrary
  escaping closure summaries, mutable local closure flow sensitivity, or broad
  closure effect inference.

- 2026-05-21 selected direct-allocation alias follow-up: the same immutable
  selected-alias idea now covers ordinary direct-allocation locals, not just
  closures. A helper can create `val first = new T(...)`, `val second =
  new T(...)`, then return or pass `val selected = if flag then first else
  second`; when a later explicit checked-owner method result or owner-token
  argument type supplies the owner, Rift preserves the original allocation
  symbols and places each candidate object in the checked region. The same
  proof now reaches a framework owner-token boundary:
  `RiftRegion.prependRegionList(region, list, selected)` marks the selected
  alias itself as a proven region value once every candidate has the same
  owner, so the framework store checker no longer treats the alias as heap
  metadata. The same framework proof now covers checked object and region
  buffer appends (`RiftRegion.append(region, objectBuffer, selected)` and
  `region.append(regionBuffer, selected)`) plus checked priority-queue
  owner-token calls (`RegionPriorityQueue.push`,
  `RegionIndexedPriorityQueue.put`, and `RegionLongIndexedPriorityQueue.put`).
  Runtime allocation stats prove the plain priority-queue selected object is
  region allocated. Compiler negatives reject unrooted heap metadata stored by
  either candidate, and mutable selected aliases remain future flow-sensitive
  work.
  A follow-up proof applies the same selected-local mechanism to recognized
  synthetic factory construction sites returned from explicit-owner methods:
  selected local `Some(new T(...))`, `Option(new T(...))`, and
  `Tuple2(new A(...), new B(...))` candidates now have compiler
  positives/negatives and runtime allocation-stat proof that both selected
  wrappers and their nested direct payloads allocate in checked region memory.
  The same proof now also covers owner-token method arguments that consume the
  selected local `Some`, `Option.apply`, or `Tuple2` alias, region-owned array
  stores that consume selected local `Some`, `Option.apply`, or `Tuple2`
  aliases, and checked `ObjectBuffer`/`RegionBuffer` appends after relaxing
  those buffer element bounds from uncaptured `Object` to captured `Object^`.
  The same captured-object element-bound rule now applies to
  `RegionPriorityQueue`, `RegionIndexedPriorityQueue`, and
  `RegionLongIndexedPriorityQueue`, so selected local `Some`, `Option.apply`,
  and `Tuple2` aliases can be pushed or put through those checked owner-token
  boundaries as well. A further proof covers the dense and long-key
  lexicographic indexed priority-queue `put` overloads with the same selected
  `Some`, `Option.apply`, and `Tuple2` aliases. The buffer and queue APIs still
  require the explicit owner-token value type `T^{owner}`, so inner-region
  values remain rejected when appended or pushed to an outer container. This is
  still factory-specific placement proof, not general `Option` container-flow
  inference.
  `RegionList` now follows the same captured-element direction with
  `T <: RegionListNode^`: branch/match-created list nodes can contain
  region-owned `Some(new T(...))`, `Option(new T(...))`, or
  `Tuple2(new A(...), new B(...))` fields when `prependRegionList` supplies
  the owner token. The NIR checker now recursively validates direct
  region-placed constructor/factory payloads, so the outer region-owned node
  cannot hide unrooted heap metadata inside a nested synthetic factory.
  A follow-up selected-nested proof covers the helper form where a RegionList
  node field receives `val selected = if flag then Some(new T(...)) else
  Some(new T(...))` or the equivalent `Option.apply`/`Tuple2` selected alias.
  This nested inference is deliberately limited to multi-candidate selected
  allocation aliases; straight heap aliases such as `val tag = metadata`
  remain rejected.
  The same selected-nested boundary now has explicit checked-framework proof for
  `ObjectBuffer`/`RegionBuffer` appends and ordinary checked priority-queue
  push/put calls where a containing value object receives the selected synthetic
  alias. The proof still relies on an explicit framework owner token and
  rejects unrooted heap metadata nested inside the selected wrapper.
  Inline reset-open-handle bodies now also have explicit proof for ordinary
  `new Array` placement, including primitive arrays such as
  `Array[Int]^{region}`. This lets inferred checked LogHub/Wikimedia paths
  remove explicit per-group array allocation calls while preserving explicit
  checked rows as controls. The follow-up 1M x3 L2 Wikimedia session and HDFS
  join gates preserve checksum/output and identical explicit/inferred
  region-object counts, so this is source-shape evidence rather than a claim
  that region-object volume changed. A later source audit completed the
  inferred Wikimedia session case by replacing the remaining explicit
  `entries`, `heads`, `tails`, and `counts` array allocations with ordinary
  `new Array`; the fresh 1M x3 Wikimedia gate again preserved matching
  checksum/output and identical explicit/inferred region-object counts.
  The owner-token array proof now also reaches checked framework
  `ObjectBuffer`, `RegionBuffer`, ordinary `RegionPriorityQueue`,
  `RegionIndexedPriorityQueue`, `RegionLongIndexedPriorityQueue`, and the
  indexed priority-queue lexicographic overloads: a direct
  `new Array[T^{region}]` appended or pushed through
  `RiftRegion.append(region, buffer, ...)`, `region.append(buffer, ...)`, or
  checked priority-queue `push`/`put` carries the framework owner through
  source-span inference. Later checked buffer `get` or priority-queue
  `peek`/`pop`/`get` locals are remembered as region-owned arrays for store
  checking. Checked stream-window rank/table-rank `putWindowRank`,
  `putWindowRankInBucket`, and `putTableRankInBucket` now have the same bounded
  direct-array proof. Rank result element stores are inferred when the result
  local has an explicit captured array type or when a prior checked `put`
  against the same immutable rank/table local recorded a value type whose array
  element captures the stream owner. `Array[Metadata]^{region}` and
  `Array[Metadata]^{stream}` remain protected and reject unrooted heap metadata
  stores. This is still owner-token/framework placement proof, not full
  array/container flow inference.

- 2026-05-20 StreamFlexDesign now has direct evidence that this inference path
  matters outside compiler microtests: at 20M events x3,
  `checked-epoch-stream-inferred` runs `18.16 s` versus explicit
  `checked-epoch-stream` at `19.01 s`, with the same RSS and
  checksum/output. The profile bucket shape remains nearly identical, so this
  is a source/lowering overhead reduction rather than a different topology.
  The remaining StreamFlex bottleneck is allocator body/object construction
  plus query-pipeline work.

- 2026-05-20/21 Broom retained dataflow now covers all four generated retained
  workloads with the ordinary-`new` active-handle source form. Aggregate/join
  were already wired; q17 now infers region placement for
  `CheckedQ17Part`, `CheckedQ17PartEntry`, and `CheckedQ17LineItem`, and
  shopper infers placement for view/cart/purchase/candidate nodes. The
  2026-05-21 follow-up extends the same generated-source pattern to per-group
  object arrays: aggregate `heads`/`tails`/`tables`, join `left`/`right`,
  generated q17 `tables`, and shopper `views`/`carts`/`purchases`/`candidates`
  now use ordinary `new Array` in `checked-rift-inferred`. TPC-H file-input q17
  stays on the explicit path until separately audited. The 20M active-16
  q17/shopper retained-record gate and the 1M generated-array gate both
  preserve checksum/output, explicit/inferred region allocation counts, low
  RSS, and zero timed GC. L4 buckets were not rerun for the array follow-up;
  this is source-placement evidence, not a speed result or a claim of full
  ReML/MLKit inference.

- Direct `new T(...)` can be lowered into a checked region when the expected
  type is explicitly captured by a checked `ScopedRegion` or
  `OpenStreamingRegion`, for example `val x: T^{region} = new T(...)`.
- For Rift-backed active open handles, the existing no-zero lowering now has a
  runtime allocation-stat proof for ordinary inference-produced `new`:
  definitely initialized record objects, including region-local reference
  fields, can skip redundant object-body zeroing when all fields are proven
  stored before first use. A broader scoped/open-region no-zero experiment via
  newly introduced virtual methods was rejected because those methods were not
  reachable during linking and were absent from generated method tables. This
  keeps no-zero as a backend proof on already placed allocations, not a
  shortcut around lifetime inference.
- Immutable local aliases of checked owner handles can also act as owner
  constraints, for example `val owner = region; val x: T^{owner} = new T(...)`.
  Runtime allocation counters prove that the object is placed in the checked
  region, and compiler negatives reject unrooted dynamic heap metadata through
  the alias. Owner aliases are now canonicalized to their underlying handle, so
  method-return summaries can reconcile local `T^{owner}` values with result
  types that name the original parameter, such as `T^{r}`. This is still a
  lexical immutable-owner proof: an immutable alias loaded from a mutable
  checked owner slot is explicitly rejected rather than inferred
  flow-sensitively. This reduces source plumbing without adding a public API.
- An immutable local direct `new` can be inferred as region-owned for the
  checked `RegionList` prepend topology when the append call supplies the
  explicit region owner.
- Immutable local direct `new` can be inferred through captured local val/var
  constraints, for example `val x = new T(...); val y: T^{region} = x`, while
  mutable direct-new locals and helper-returned heap objects remain heap
  fallback/rejection cases.
- The same local slice now handles block-shaped RHS forms whose final
  expression is a direct allocation, for example
  `val x: T^{region} = { val n = ...; new T(n) }` and
  `val x = { ...; new T(...) }; val y: T^{region} = x`. Captured assignment
  constraints are covered for the same block-shaped RHS form.
- A first method-summary slice can infer direct `new` returned from a local
  method when the method has an explicit captured region handle parameter, for
  example `def make(using r: ScopedRegion^): T^{r} = new T(...)`. Captured
  return types that mention only an outer region remain heap fallback for now,
  because the generated method body has no runtime region handle to allocate
  through.
- The same method slice also handles the common block shape
  `def make(using r: ScopedRegion^): T^{r} = { val x = new T(...); x }`,
  so a method-local immutable direct allocation can be constrained by the
  captured result type when the final returned value is that local. The slice
  is validated for checked scoped regions and direct epoch/open-streaming
  regions.
- The returned-local method slice also handles a method-local block-shaped RHS
  whose final expression is a direct allocation, for example
  `def make(using r: ScopedRegion^): T^{r} = { val x = { val n = ...; new T(n) }; x }`.
- The method slice also handles simple branch-returned direct allocations, for
  example `if p then new T(...) else new T(...)`, when both branches share the
  same explicit checked region result owner.
- The method slice also handles branch-returned local allocations, for example
  `if p then { val x = new T(...); x } else { val y = new T(...); y }`, when
  the method result has the same explicit checked region owner.
- The same method slice now handles simple match-returned direct and local
  allocations under the same explicit checked-region-parameter rule.
- Branch- and match-returned local allocations now also accept block-shaped
  local RHS construction whose final expression is a direct allocation, for
  example `if p then { val x = { ...; new T(...) }; x } else ...`.
- The same method slice also handles direct allocations that are the final
  expression of a method block with preceding local computation, for example
  `def make(using r: ScopedRegion^): T^{r} = { val n = ...; new T(n) }`.
- A first forwarding-summary case is also implemented:
  `def wrap(using r: ScopedRegion^): T^{r} = make(using r)` can preserve the
  inferred region-return fact when `make` is already inferred and the wrapper
  has its own explicit checked region parameter.
- The same forwarding-summary slice also handles one immutable local-alias
  wrapper shape:
  `def wrap(using r: ScopedRegion^): T^{r} = { val x = make(using r); x }`.
- Forwarded branch and match wrappers are also validated when every returned
  path calls an already inferred region-returning method with the same explicit
  checked owner.
- Owner-token framework append calls can infer immutable local direct `new`
  values for checked `ObjectBuffer` and `RegionBuffer`, for example
  `val x = new T(...); RiftRegion.append(region, buffer, x)` and
  `region.append(buffer, x)`. The same owner-token rule now also covers
  validated block-shaped local RHS construction for `RegionList`,
  `ObjectBuffer`, and `RegionBuffer`.
- The owner-token framework slice now also covers direct and inline block-final
  argument construction for the scoped checked list/fixed-buffer/growable-buffer paths, for example
  `RiftRegion.prependRegionList(region, list, new T(...))`,
  `RiftRegion.append(region, buffer, new T(...))`,
  `region.append(buffer, new T(...))`, and
  `region.append(buffer, { val n = ...; new T(n) })`. These are validated by
  runtime allocation counters and by negative unrooted-metadata tests.
- Owner-token framework push/put calls can infer immutable local direct `new`
  values for the scoped checked priority-queue family:
  `RegionPriorityQueue`, `RegionIndexedPriorityQueue`, and
  `RegionLongIndexedPriorityQueue`. This is validated by runtime allocation
  stats, not only by type acceptance.
- The priority-queue owner-token slice now also accepts direct and inline
  block-final argument construction in `push`/`put` calls, so a queue candidate
  can be written as
  `region.push(queue, new T(...), priority)` or
  `RiftRegion.put(region, indexedQueue, key, { ...; new T(...) }, priority)`
  without a temporary local.
- The first page/window/transaction child-owner slice is validated for child-region locals
  returned by checked owner helpers such as `pageTokenAppendRegionFor`,
  `pageTokenMapFilterRegionFor`, `pageTokenCountByKeyRegionFor`,
  `epochBufferRegionFor`, `transactionRegionFor`, and `chunkAppendRegionFor`. This
  lets code write
  `val region = pageTokenAppendRegionFor(...); val event: Event^{region} = new Event(...)`
  and have the event allocated in that independently expiring child bucket or
  transaction-local region. `epochBufferRegionFor` now has the same ordinary
  `new` allocation-stat proof for records widened to the parent stream owner
  before `appendEpochBuffer`.
  Parent `StreamingRegion` values remain excluded; only locals known to come
  from checked child-region helpers are accepted as `StreamingRegion` owners.
  Mutable owner-slot flow remains out of scope: code that stores a child owner
  in a `var`, later reads it through `val region = currentRegion`, and then
  constructs `new Event(...)` under that alias stays heap fallback and is
  rejected by the checked buffer store.
- `epochFoldRegionFor` now joins that selected helper set: an epoch-fold record
  typed by the returned child region can be written with ordinary `new` and
  widened to the parent stream owner for `putEpochFold`; unrooted metadata
  remains rejected. This is still selected helper placement, not automatic
  topology inference for every fold/rank/window operator.
- The open-child-owner follow-up extends that idea to selected active helpers:
  `pageTokenAppendOpenRegionFor`, `pageTokenMapFilterOpenRegionFor`,
  `pageTokenCountByKeyOpenRegionFor`, and `epochBufferOpenRegionFor`. Code can
  now write
  `val region = pageTokenMapFilterOpenRegionFor(...); val event: Event^{region} = new Event(...)`
  instead of `allocOpen(new Event(...))(using region)`, and runtime counters
  prove the records are region allocated. Compiler negatives reject unrooted
  dynamic heap metadata through the open page-token helper family. This is a
  small step toward reducing token/handle plumbing in operator-owned paths
  while keeping public APIs defensive.
- The page-token Rift open-handle follow-up validates the raw Rift-backed
  helper shape used inside operator-owned paths:
  `pageTokenAppendRiftOpenHandleFor(...)` can own
  `val event: Event^{region} = new Event(...)`, runtime allocation counters
  prove the event lands in Rift region memory, and a compiler negative rejects
  unrooted dynamic heap metadata through that helper. This keeps the raw
  `RiftOpenStreamingHandle` internal while proving that page-token internals
  can use ordinary `new` on the monomorphic active-handle path.
- The first common Scala allocation shape is implemented for captured
  `Some(...)`: when the expected type is `Some[T^{region}]^{region}` or the
  common widened form `Option[T^{region}]^{region}` and the argument is legal
  for region storage, `scala.Some.apply` is lowered into a checked-region
  `Some` allocation. Heap fallback remains the default for unproven
  `Some(...)` calls, and unrooted dynamic heap metadata is rejected.
  `None`/`Option.apply(...)` are now covered by the next optional-shape slice:
  null returns the static empty option, while non-null region-safe values lower
  to checked-region `Some` allocation.
- The next common Scala allocation shape is implemented for captured
  `Tuple2(...)` and normal tuple syntax: when the expected type is
  `Tuple2[A^{region}, B^{region}]^{region}` and both fields are legal for
  region storage, `scala.Tuple2.apply` or the equivalent `(a, b)` tuple syntax
  is lowered into a checked-region `Tuple2` allocation. Primitive tuple fields
  remain future boxed-key/object boxing work because the current proof does not
  place the boxed primitive object in the same region. This boundary is now
  compiler-tested: `Tuple2[Int, T^{region}]^{region}`-style shapes,
  owner-token primitive tuple arguments, method-returned primitive tuples,
  mixed primitive/unrooted-heap-metadata tuples, and preboxed `Any` values all
  stay rejected until the boxing path has a checked allocation-zone design.
- That tuple factory recognizer is now generalized from `Tuple2` to
  `scala.TupleN.apply` for arities 2 through 22. Tuple3 is the first validated
  higher-arity proof point: compiler positives cover local array-store,
  owner-token method-argument, and explicit-region method-return shapes;
  negatives reject unrooted heap metadata; and runtime allocation counters
  prove the `Tuple3` object plus three nested region-local leaves are allocated
  in the checked region. This is still expected-type placement for proven
  reference-safe tuple fields, not boxed-key or primitive-field placement.
- The method-summary path now also carries captured `Some(...)` and
  `Tuple2(...)` factory results when the method has an explicit checked region
  parameter, for example
  `def make(using r): Some[T^{r}]^{r} = Some(new T(...))`,
  `def make(using r): Option[T^{r}]^{r} = Some(new T(...))`, and
  `def make(using r): Tuple2[A^{r}, B^{r}]^{r} = Tuple2(new A(...), new B(...))`
  and the tuple-literal equivalent.
  Runtime allocation counters prove both the factory object and nested direct
  values are region allocated.
- The method-summary path now also carries a returned local `Option` value
  initialized from `Some(...)`, for example
  `def make(using r): Option[T^{r}]^{r} = { val x = Some(new T(...)); x }`.
  This covers a common source shape where user code names a factory result
  before returning it.
- The first call-site method-argument slice is validated for direct arguments
  whose parameter type names an in-scope checked owner, for example
  `def consume(x: T^{region}): Int = ...; consume(new T(...))`. Runtime
  counters prove the argument object is region allocated, and unrooted heap
  metadata in the inferred argument object is rejected.
- The call-site slice now also supports a narrow owner-token method shape,
  `def consume(using r: ScopedRegion^)(x: T^{r}): Int = ...;
  consume(using region)(new T(...))`. The inference phase flattens the fully
  applied call, maps the callee owner parameter `r` to the actual checked owner
  argument `region`, and places the inline `new` into that region. This is the
  first validated call-site owner substitution case, not full method/effect
  inference for arbitrary polymorphic or higher-order callees.
- The same owner-token call-site substitution now handles inline closure
  object arguments, for example
  `def consume(using r: ScopedRegion^)(f: Function1[Int, Int]^{r}) = ...;
  consume(using region)((n: Int) => n + 40)`. Runtime allocation counters prove
  the materialized closure object is allocated in the checked region, and
  compiler negatives reject unrooted heap metadata captures. This remains
  closure-object placement; closure-body allocation placement still needs a
  hidden owner handle or effect summary for the generated lambda body.
- The same closure-object proof now reaches checked owner-token container
  stores. `ObjectBuffer`, `RegionBuffer`, and ordinary `RegionPriorityQueue`
  can consume inline closures or selected immutable local closure aliases when
  the value type carries the supplied checked owner. Runtime allocation
  counters prove the materialized closure objects are region allocations, and
  compiler negatives reject unrooted heap captures. This is still explicit
  owner-token store placement, not broad closure/effect or topology inference.
- Checked stream-window rank/table-rank owner-token APIs now have the same
  bounded closure-object proof. Inline closures in `putWindowRank`, selected
  immutable local closure aliases in `putWindowRankInBucket`, and inline
  closures in `putTableRankInBucket` can be placed when their value type is
  captured by the checked stream owner. Runtime allocation counters prove the
  inserted closure values are region allocations, and unrooted heap captures
  are rejected. This remains explicit framework-owner placement, not automatic
  rank/table topology inference.
- The owner-token call-site path now also has direct coverage for inline
  `Some(new T(...))` factory arguments:
  `def consume(using r: ScopedRegion^)(option: Option[T^{r}]^{r}) = ...;
  consume(using region)(Some(new T(...)))`. Runtime allocation counters prove
  both the `Some` object and nested payload object are region allocated, and
  compiler negatives reject unrooted heap payloads such as `Some(metadata)`.
- The same owner-token path is now validated for null-preserving
  `Option.apply(new T(...))` arguments, with the non-null `Some` branch and
  nested direct payload allocated in the checked region and unrooted metadata
  rejected.
- The same call-site path now has direct coverage for inline
  `Tuple2(new A(...), new B(...))` factory arguments and normal tuple syntax:
  `def consume(using r: ScopedRegion^)(pair: Tuple2[A^{r}, B^{r}]^{r}) = ...;
  consume(using region)(Tuple2(new A(...), new B(...)))`. Runtime allocation
  counters prove the `Tuple2` object and both nested payload objects are region
  allocated, and compiler negatives reject unrooted heap payloads such as
  `Tuple2(metadata, metadata)`.
- The same owner-token call-site path now covers a narrow generic object
  argument shape:
  `def consume(using r: ScopedRegion^)(cell: Cell[T^{r}]^{r}) = ...;
  consume(using region)(new Cell(new T(...)))`. Runtime allocation counters
  prove both the generic `Cell` object and nested payload are region allocated.
  Compiler negatives reject unrooted heap payloads and widened `AnyRef`
  retention of the generic cell. This is still owner-token call-site
  substitution plus expected-type placement, not broad polymorphic
  region/effect inference.
- The owner-token call-site path now also accepts one narrow local
  polymorphic consumer shape:
  `def consume[A](using r: ScopedRegion^)(cell: Cell[A^{r}]^{r}) = ...;
  consume[T](using region)(new Cell(new T(...)))`. The fix is deliberately
  conservative: method symbols are not legal allocation owners, so polymorphic
  capture extraction cannot mistake the callee itself for a region token.
  Runtime counters prove the polymorphic `Cell` object and nested payload are
  region allocated; widened `AnyRef` escape and unrooted dynamic heap metadata
  remain rejected. This is a first polymorphic owner-token call-site case, not
  full ReML-style polymorphic effect inference.
- The same polymorphic owner-token consumer boundary is now tested for
  selected immutable local candidates when the candidates are explicitly typed
  as checked-region values:
  `val selected = if flag then first else second;
  consume[T](using region)(selected)`, where `first` and `second` have type
  `Cell[T^{region}]^{region}`. Runtime counters prove both candidate cells and
  nested payloads are region allocated. Untyped selected generic cells remain
  rejected because capture checking loses the owner before the current
  post-capture inference phase can recover it safely.
- A matching narrow polymorphic method-summary case is now validated for
  explicit checked owner parameters:
  `def make[A](using r: ScopedRegion^)(value: A^{r}): Cell[A^{r}]^{r} =
  new Cell[A^{r}](value)`. The compiler records captured method parameters as
  region values for the method body, and the call boundary rejects
  helper-returned heap objects that are not already proven region-local. Runtime
  counters prove the returned `Cell` and payload allocate in the checked
  region. This is still explicit-owner method-summary inference, not broad
  polymorphic effect inference.
- That polymorphic method-summary case is also validated through a simple true
  type-parameter wrapper:
  `def wrap[A](using r: ScopedRegion^)(value: A^{r}): Cell[A^{r}]^{r} =
  make[A](using r)(value)`. No compiler implementation change was needed; the
  existing forwarding summary preserves the captured owner and parameter proof.
  Runtime counters prove the forwarded `Cell` and payload allocate in the
  checked region, while helper-returned heap metadata and widened heap/static
  escape remain rejected. This is still narrow explicit-owner forwarding, not
  broad polymorphic effect inference.
- The same explicit-owner polymorphic method-summary path is now directly
  covered for the common optional-result factory:
  `def make[A](using r: ScopedRegion^)(value: A^{r}): Option[A^{r}]^{r} =
  Some(value)`. No new compiler implementation was needed for this proof; the
  captured method-parameter summary used by the generic `Cell` factory also
  proves the `Some(value)` argument. Runtime counters prove the `Some` wrapper
  and payload allocate in the checked region, while helper-returned heap
  metadata and widened heap/static escape remain rejected. This is still narrow
  explicit-owner summary inference, not broad polymorphic `Option` effect
  inference.
- The null-preserving `Option.apply` method-summary path is now directly
  covered for captured method parameters:
  `def make[A](using r: ScopedRegion^)(value: A^{r}): Option[A^{r}]^{r} =
  Option(value)`. Runtime counters prove the non-null `Some` branch and payload
  allocate in the checked region, while helper-returned heap metadata and
  widened heap/static escape remain rejected. This is still narrow
  explicit-owner summary inference, not broad polymorphic `Option` container
  inference.
- The same path is now directly covered for a polymorphic tuple-result factory
  with multiple captured method parameters:
  `def make[A, B](using r: ScopedRegion^)(left: A^{r}, right: B^{r}): Tuple2[A^{r}, B^{r}]^{r} =
  Tuple2(left, right)`. Runtime counters prove the `Tuple2` wrapper and both
  payloads allocate in the checked region, while helper-returned heap metadata
  and widened heap/static escape remain rejected. This is still narrow
  explicit-owner summary inference, not broad polymorphic tuple/container
  effect inference.
- The polymorphic synthetic-factory path is also validated through true
  type-parameter branch and match wrappers for `Option.apply` and `Tuple2`.
  Shapes such as
  `if flag then make[A](using r)(value) else make[A](using r)(value)` and the
  matching `Tuple2[A, B]` form preserve the same explicit checked owner when
  every path forwards through that owner. Runtime counters prove the selected
  `Some`/`Tuple2` objects and payloads allocate in the checked region, while
  helper-returned heap metadata and widened heap/static escape remain rejected.
  This is still narrow explicit-owner forwarding, not full polymorphic
  effect inference.
- The method-summary path now also forwards proven region-owned `Some`
  factory results through simple branch and match wrappers, for example
  `def wrap(flag)(using r): Option[T^{r}]^{r} = if flag then make(using r) else make(using r)`
  and `selector match { case 0 => make(using r); case _ => make(using r) }`.
  Runtime allocation counters prove the selected `Some` objects and nested
  values remain region allocated, and compiler negatives preserve unrooted
  metadata and heap/static escape rejection.
- The same returned-local method/factory slice now covers captured `Tuple2`
  values, for example
  `def make(using r): Tuple2[A^{r}, B^{r}]^{r} = { val x = Tuple2(new A(...), new B(...)); x }`.
  Runtime allocation counters prove the named tuple and nested values are
  allocated in the checked region.
- The same method/factory summary now forwards proven region-owned `Tuple2`
  factory results through simple branch and match wrappers, for example
  `def wrap(flag)(using r): Tuple2[A^{r}, B^{r}]^{r} = if flag then make(using r) else make(using r)`.
  Runtime allocation counters prove the selected tuple objects and nested
  values remain region allocated, and compiler negatives preserve unrooted
  metadata and heap/static escape rejection.
- A narrow ReML-style polymorphic local object slice is validated for
  ordinary generic classes when the expected type names the checked owner, for
  example `val c: Cell[T^{region}]^{region} = new Cell[T^{region}](x)`.
  This is not broad polymorphic inference: it covers local construction with a
  proven region-owned value argument, rejects widened `AnyRef` escape, and
  rejects unrooted dynamic heap metadata in the generic cell.
- The same narrow generic slice is also validated through explicit checked
  region-parameter methods, for example
  `def make(using r): Cell[T^{r}]^{r} = new Cell[T^{r}](x)`, with runtime
  allocation counters proving both the returned generic cell and its
  region-owned value are allocated in the checked region.
- The generic method slice also handles returned-local generic cells, for
  example
  `def make(using r): Cell[T^{r}]^{r} = { val c: Cell[T^{r}]^{r} = new Cell[T^{r}](x); c }`,
  with runtime counters proving the named `Cell` and its region-owned value
  are allocated in the checked region.
- Branch/match forwarding wrappers for generic cells are now validated, for
  example
  `def wrap(flag)(using r): Cell[T^{r}]^{r} = if flag then make(using r) else make(using r)`.
  This keeps the same explicit checked owner through simple control-flow
  wrappers and runtime counters prove the selected `Cell` and contained
  region-owned value are region allocated. Compiler negatives preserve
  rejection of unrooted heap metadata and heap/static escape through the
  forwarded generic result.
- The first array slice is validated for captured local arrays when the
  expected array type names the checked owner, for example
  `val items: Array[T^{region}]^{region} = new Array[T^{region}](n)`.
  Runtime allocation counters prove the array and named region-local element
  objects are placed in Rift region memory. Compiler negatives reject unrooted
  heap-object stores into the region-owned array and reject heap/static escape.
- Inline direct construction into a region-owned array is now validated for the
  narrow owner-proven shape `items(i) = new T(...)` where the array has type
  `Array[T^{region}]^{region}`. The array element type must itself carry the
  checked owner; `Array[Metadata]^{region}` plus `items(i) = new Metadata(...)`
  remains rejected rather than hiding an unproven heap-looking element in a
  region-owned container.
- The same array element-owner rule is now validated for a narrow synthetic
  store shape:
  `items(i) = Some(new T(...))` where `items` has type
  `Array[Option[T^{region}]^{region}]^{region}`. Runtime counters prove the
  array, stored `Some`, and nested direct value are region allocated. A store
  such as `items(i) = Some(metadata)` still rejects unrooted heap metadata.
- The same synthetic array-store proof now covers
  `items(i) = Option(new T(...))`: `Option.apply` keeps null-to-`None`
  semantics, and the non-null `Some` branch plus nested direct payload are
  allocated in the checked region.
- The array element-owner rule is also validated for the corresponding tuple
  factory shape:
  `items(i) = Tuple2(new A(...), new B(...))` where `items` has type
  `Array[Tuple2[A^{region}, B^{region}]^{region}]^{region}`. Runtime counters
  prove the array, stored `Tuple2`, and both nested direct values are region
  allocated. A store such as `items(i) = Tuple2(metadata, metadata)` still
  rejects unrooted heap metadata.
- The direct array-store rule now also walks simple branch/match RHS values:
  `items(i) = if flag then new T(...) else new T(...)`,
  match-returned `Option(new T(...))`, and branch-returned
  `Tuple2(new A(...), new B(...))` record every returned constructor/factory
  under the same checked array element owner. A branch such as
  `if flag then Some(metadata) else Some(metadata)` still rejects unrooted
  heap metadata.
- The same owner-proven array boundary now covers closure objects:
  `items(i) = (n: Int) => n + 40` and selected immutable local closure aliases
  can be placed when `items` has type
  `Array[Function1[Int, Int]^{region}]^{region}`. Runtime counters prove the
  materialized closure objects are region allocated, and closures that capture
  unrooted heap metadata remain rejected. This is closure-object placement at
  an explicit array element-owner boundary, not hidden owner capture or broad
  closure effect inference.
- Owner-token method arguments now cover direct array arguments too, for
  example
  `def consume(using r)(items: Array[T^{r}]^{r}); consume(using region)(new Array[T^{region}](n))`.
  The implementation bridges the owner proof from the source array construction
  to the lowered runtime array factory, so runtime counters prove both the
  array and inline stored region-local elements are checked-region allocations.
  Unrooted heap stores through the captured array parameter remain rejected.
- The method-summary path also carries named region-owned arrays returned from
  explicit checked region-parameter methods, for example
  `def make(using r): Array[T^{r}]^{r} = { val items = new Array[T^{r}](n); items }`.
  Runtime allocation counters prove both the array and named region-local
  elements are region allocated. Compiler negatives reject unrooted heap-object
  stores inside the method and reject heap/static retention of the returned
  array.
- The same method-array summary now propagates through simple wrappers:
  `def wrap(using r): Array[T^{r}]^{r} = make(using r)` and
  `def wrap(using r): Array[T^{r}]^{r} = { val items = make(using r); items }`.
  Runtime allocation counters prove the forwarded array and element objects
  remain region allocated, and compiler negatives preserve the same
  unrooted-store and heap/static escape boundaries.
- The method-array forwarding summary now also propagates through simple
  branch and match wrappers, for example
  `def wrap(flag)(using r): Array[T^{r}]^{r} = if flag then make(using r) else make(using r)`
  and `selector match { case 0 => make(using r); case _ => make(using r) }`,
  when every path forwards a value owned by the same explicit checked region
  parameter. Runtime allocation counters prove the selected array and named
  region-local elements are region allocated, and compiler negatives preserve
  unrooted-store and heap/static escape rejection.
  The 2026-05-21 08:17-08:18 validation gate explicitly covers both branch and
  match forwarded method-returned array runtime proofs.
- Region-owned direct construction now recursively places direct nested
  construction arguments in the same checked region, for example
  `new Wrapper(new T(...))`, `Some(new T(...))`, and
  `Tuple2(new A(...), new B(...))`. Helper-returned heap values are still
  rejected unless explicitly rooted or otherwise proven.
- The first synthetic-closure object slice is validated for local nonescaping
  closures that capture a region value, for example
  `val f: Function1[Int, Int]^{region} = (n: Int) => leaf.value + n`.
  The closure object is allocated in the same checked region as the captured
  value when materialized, and unrooted dynamic heap metadata captures are
  rejected in that proven path. This is not closure-body allocation placement,
  returned-closure inference, or broad closure effect inference.
- The capture-free closure follow-up validates the other local closure shape:
  `val f: Function1[Int, Int]^{region} = (n: Int) => n + 40`. The compiler
  now treats function capture syntax such as `Int ->{region} Int` as a region
  owner constraint, GenNIR resolves the local checked owner, runtime allocation
  counters prove the materialized closure object is region allocated, and a
  compiler negative rejects a closure that would capture unrooted heap
  metadata. This is still local closure-object placement only.
- The method/closure follow-up validates returning a capture-free local closure
  object from an explicit checked region-parameter method, for example
  `def make(using r): Function1[Int, Int]^{r} = { val f: Function1[Int, Int]^{r} = n => n + 40; f }`.
  Runtime allocation counters prove the returned closure object is region
  allocated, and unrooted heap metadata captures are rejected. This is a narrow
  method-return summary for closure objects, not broad closure effect
  inference. The same method-return shape is now validated for a closure that
  captures a region-local value constructed in the method; runtime counters
  prove both the captured value and returned closure object are region
  allocated. The same method-return shape now works when the method body uses
  an immutable owner alias, for example
  `val owner = r; val f: Function1[Int, Int]^{owner} = ...; f`; the summary
  canonicalizes the alias back to the explicit checked region parameter.
  That method-return summary now also propagates through a simple wrapper
  method:
  `def wrap(using r): Function1[Int, Int]^{r} = make(using r)`. Runtime
  allocation counters prove the forwarded closure object and its captured
  region-local value still land in the checked region, while a compiler
  negative rejects the same forwarded shape when the closure captures unrooted
  heap metadata. The same forwarding evidence now covers the immutable
  method-local alias form
  `def wrap(using r): Function1[Int, Int]^{r} = { val f = make(using r); f }`.
  It also covers simple branch and match wrappers when every path forwards the
  same explicit checked owner, for example
  `if flag then make(using r) else make(using r)` and
  `selector match { case 0 => make(using r); case _ => make(using r) }`.
- A narrow closure-body allocation shape is now promoted: when a region-owned
  closure explicitly captures the same checked owner term named by its expected
  type, the generated lambda has a runtime owner handle and can place a
  body-local returned allocation such as
  `val owner = region; val leaf: T^{owner} = new T(...)`. Runtime allocation
  counters prove both the closure object and body allocation are checked-region
  objects, and a compiler negative rejects unrooted heap metadata through the
  same shape. The earlier limitation still applies when the owner appears only
  in types: hidden owner capture, lambda-signature rewriting, escaping closure
  summaries, and broad closure effect inference remain future work.
- `-P:scalanative:riftInferReport` emits an opt-in placement report with
  `Region`, `Unknown`, and `Rejected` decisions.
- `ObjectAllocationLoweringMatrix` now has a focused explicit-versus-inferred
  scoped allocation gate. The 20k primitive and reference smoke rows show
  inferred ordinary `new` producing the same checked-region allocation counts
  and checksums as explicit `RiftRegion.alloc(new ...)`. The current 5M
  reference-shaped rerun also shows the inferred source form matching explicit
  region object counts/RSS and eliminating timed GC, while running slightly
  slower than explicit scoped allocation. This is allocation-stat and
  focused-gate evidence for the supported source shapes, not yet a final
  application-level performance claim.
- The first active-handle slice is implemented for internal
  `RiftOpenStreamingHandle` owners. This matters for operator-owned checked
  Rift paths: the benchmark source can use ordinary `new`, while lowering still
  allocates through the monomorphic active handle. Broom retained-dataflow
  aggregate and join now have `checked-rift-inferred` rows that match explicit
  checked Rift checksums, outputs, region allocation counts, and zero-GC
  behavior at 1M records. The latest rerun makes aggregate a near tie/slightly
  faster than explicit and join a small inferred-overhead row.
- LogHub retained session/join now provides the second representative
  active-handle source-ergonomics row. It uses compressed real HDFS LogHub input
  directly from `tar.gz`, and `checked-rift-inferred` matches explicit checked
  Rift checksums, outputs, and region allocation counts at 20k and 1M records.
  This validates the inference shape on a real streaming parser/operator path,
  but it is not GC-heavy evidence because archive parsing and line processing
  dominate heap GC. In the current 1M rerun it is also the main regression
  target: inferred checked Rift keeps the GC/RSS win versus heap but is slower
  than explicit checked Rift. Targeted macOS `sample` profiles of explicit and
  inferred checked Rift show the same top CPU shape: token scanning, stable
  hashing, string character access, and byte-line reading dominate; the Rift
  region allocation fast path has only a handful of samples in both rows. That
  makes LogHub a poor target for region-allocation micro-tuning, and a better
  reminder that parser/hash-heavy real input can hide memory-management wins.
- StreamFlexDesign throughput now provides the third representative
  active-handle row. The inferred mode keeps the StreamFlex-style
  stable/transient/capsule design intact and replaces explicit active-handle
  allocation with ordinary `new` for transient period records. At 1M events,
  inferred checked Rift matches explicit checked Rift region allocation counts
  and checksums, eliminates the heap row's timed GC, and is a near tie against
  the explicit active-handle source form.

Arbitrary generic buffers, broader page/window operator inference,
primitive/boxed tuple fields, broader Option container flows, iterators,
arrays flowing through generic APIs, broader method/closure summaries, and
whole-module inference are still future work. The narrow `None` pattern is now
covered: a static empty `Option` can satisfy `Option[T^{r}]^{r}` without
allocating a region object, and a local or explicit-region-method
`if flag then Some(new T(...)) else None` flow places only the `Some` branch
and payload in the region. The null-preserving `Option.apply(...)` shape is
also covered for proven local and explicit-region-method results:
`Option(null)` allocates nothing, while `Option(new T(...))` places the `Some`
branch and nested payload in the checked region. The same direct-construction
proof is validated through owner-token method arguments and region-owned array
stores, with unrooted metadata rejected in both contexts.
The implemented array slice is intentionally narrow: captured local arrays,
explicit-region-parameter method-returned arrays, and direct/local-alias/
branch/match forwarding wrappers with expected types such as
`Array[T^{region}]^{region}` or `Array[T^{r}]^{r}` are validated, and inline
or simple branch/match direct element construction is now covered for
`Array[T^{region}]^{region}`. The first synthetic array-store shapes,
`Some(new T(...))`, `Option(new T(...))`, and `Tuple2(new A(...), new B(...))`,
are also covered when the array element type proves the corresponding
region-owned wrapper ownership, including direct `if`/`match` RHS forms.
Generic array flows, broader Option flows, heap-looking element types, and
arrays crossing unproven method/container boundaries still need stronger
effect summaries.
The implemented call-site argument slice is similarly narrow: it can use an
already in-scope owner named in the parameter type, but it does not yet infer
region/effect substitutions for arbitrary polymorphic or curried helper APIs.
The newest generic `Cell[A]` owner-token argument test covers only the fully
applied shape whose parameter type explicitly says `Cell[T^{r}]^{r}` and whose
call supplies the actual checked owner argument.
The first polymorphic owner-token consumer proof extends that same boundary to
`Cell[A^{r}]^{r}` when the call supplies both the concrete type argument and
the actual checked owner token. The selected-local follow-up covers explicitly
region-typed selected candidates, but broader polymorphic helper summaries and
untyped selected generic aliases remain future work.
The first polymorphic method-return proof covers the corresponding explicit
owner factory `make[A](using r)(value: A^{r}): Cell[A^{r}]^{r}` and adds a
call-boundary rejection for helper-returned heap values flowing into captured
method parameters.
Priority-queue owner-token placement is only implemented for the scoped queue
family above. The current page/window/transaction child-owner slices cover
explicit child-region locals from the append, map/filter, count-by-key,
transaction, chunk-append, and epoch-fold owner helpers plus open page-token/epoch-buffer
active helpers and the internal `pageTokenAppendRiftOpenHandleFor` raw-handle
helper, not automatic placement for every stream-window rank/table-rank or
bucket operator path.
The newest selected synthetic owner-token proof covers the narrow
stream-window rank/table-rank API shape: selected local `Some(new T(...))`,
`Option(new T(...))`, and `Tuple2(new A(...), new B(...))` aliases can flow
through `putWindowRank`, `putWindowRankInBucket`, and `putTableRankInBucket`
when the checked rank/table context supplies the stream owner token. This uses
`StreamingRegion` only as a framework owner token for that proven call
boundary; it is not broad parent-stream allocation inference or automatic
child-bucket topology inference.
The follow-up branch/match-local proof covers the same checked rank/table API
family for `if flag then first else second` and Scala 3 lowered match-result
forms when every returned value is an immutable local direct allocation. The
NIR checker accepts `if`, `match`, `Return`, and `Labeled` match-result
expressions only when every returned value is known region-local, and unrooted
heap metadata in any selected candidate remains rejected. Direct local
heap-looking rank/table values remain outside the validated claim.
The direct branch/match synthetic-factory proof removes the need to name every
factory result before an owner-token call: explicit owner-token method
arguments, checked `ObjectBuffer`/`RegionBuffer` appends, ordinary checked
priority-queue push/put calls, dense/long lexicographic checked priority-queue
put overloads, and the checked rank/table API family now accept direct
`if`/`match` expressions returning `Some(new T(...))`,
`Option(new T(...))`, or `Tuple2(new A(...), new B(...))` when every returned
factory app is proven owned by the supplied checked owner. This is still
owner-token placement for recognized factory shapes, not broad
Option/container inference, priority-queue topology inference, or rank/table
topology inference.
Broader generic containers and polymorphic effect summaries remain future work:
the current `Cell[A]` slice is local, method-returned, returned-local,
branch/match-forwarded, narrow owner-token polymorphic-consumer expected-type
placement, and explicitly region-typed selected owner-token candidates, and
the array slice is local plus
explicit-region-parameter method-returned and simple-wrapper expected-type
placement; neither is inference for escaping containers, arrays through
generic APIs, callbacks, or hidden generic retention. Closure support is only
partially started: the validated slices place materialized local nonescaping
closure objects either from a function-captured expected type or from a captured
region-local value, including explicit-region-parameter method returns and
owner-alias method returns, plus simple forwarded method returns through direct
calls or one immutable local alias, branch, or match. Captured-owner
closure-body placement is implemented only when the closure explicitly carries
the runtime checked owner handle, now including direct/local, branch/match
direct-inline, owner-token selected-alias, and method-returned selected-alias
body proofs, plus direct/branch/match forwarded method-returned closures and
forwarded selected local aliases. Closure-object placement is also validated at the
region-owned array-store boundary for direct inline closures and selected
immutable local closure aliases. Hidden owner capture, mutable selected closure
aliases, escaping closures, and broader closure effect summaries remain future
work.
Plain direct-allocation locals also preserve immutable selected aliases through
method-return, owner-token, `RegionList`, and checked buffer framework
constraints, but mutable selected aliases and flow-sensitive reassignment
remain future work.
Primitive boxing and boxed-key placement are also future work: the current NIR
`Op.Box(ty, obj)` has no allocation-zone operand, unlike `Classalloc` and
`Arrayalloc`, so region-owned boxes need a deliberate NIR/runtime lowering
design rather than a small inference-only extension.

## Optimization Goal

Rift's long-term inference goal is to reproduce ReML/MLKit-style automatic
region inference as much as Scala Native and Scala capture/separation checking
allow. The purpose is practical, not aesthetic: optimize away unnecessary
accidental heap allocations and make proven region-local data-path code cheaper
than the corresponding heap path.

The target optimization outcomes are:

- Place ordinary and compiler-generated Scala allocations in regions whenever
  capture/effect constraints prove a bounded lifetime.
- Keep hot region paths monomorphic, direct, and inlineable so checked
  placement does not pay generic allocation or virtual dispatch costs.
- Reduce token/handle plumbing in operator-owned paths by deriving the owner
  from checked framework boundaries where the compiler can prove it.
- Improve object construction and initialization paths for proven
  region-local record-like objects without violating Scala semantics.
- Remove stale-token, root-tracking, heap-to-region bookkeeping, close-time
  scans, and similar runtime work only when capture/separation facts prove
  the object graph is region-local and bulk-reclaimable.
- Leave every unproven allocation on the GC heap, with diagnostics explaining
  the missing proof.

## Prior Work Anchors

The lineage that matters most for Rift is:

- Tofte and Talpin's [Region-Based Memory Management](https://www.sciencedirect.com/science/article/pii/S0890540196926139):
  the foundational region-inference system, later tested in the ML Kit with
  Regions.
- Tofte, Birkedal, Elsman, and Hallenberg's
  [A Retrospective on Region-Based Memory Management](https://citeseerx.ist.psu.edu/document?doi=26a389559005fe2c8a33503783834be67258b986&repid=rep1&type=pdf):
  the retrospective view that region inference is both a type-theoretic idea
  and an experimentally tuned implementation discipline.
- Elsman et al.'s PLDI 2023
  [Garbage-Collection Safety for Region-Based Type-Polymorphic Programs](https://pldi23.sigplan.org/details/pldi-2023-pldi/10/Garbage-Collection-Safety-for-Region-Based-Type-Polymorphic-Programs):
  the key warning for Rift's generic/polymorphic cases. Region values hidden
  behind type parameters, widened references, or higher-order code must remain
  safe during GC and must not become dangling references.
- Elsman et al.'s POPL 2024
  [Explicit Effects and Effect Constraints in ReML](https://popl24.sigplan.org/details/POPL-2024-popl-research-papers/81/Explicit-Effects-and-Effect-Constraints-in-ReML):
  the most relevant model for future Rift diagnostics and summaries, because
  it makes region/memory-management effects explicit and constraint based.

## What Rift Borrows

Rift should directly borrow these principles:

- Region variables appear in types.
- Allocation placement is a type/effect property, not just a runtime choice.
- Region lifetimes are checked statically.
- Polymorphic functions need region/effect summaries.
- Region management and tracing GC can be complementary.
- Region inference must be evaluated experimentally, not only proved
  theoretically.

These points match Rift's current thesis direction: use static lifetime
topology to move short-lived data-path objects into regions while keeping
durable control state and unpredictable lifetimes on the GC heap.

## What Rift Should Not Copy Literally

Rift should not mechanically copy the MLKit algorithm.

Reasons:

- MLKit/ReML target Standard ML / ReML, while Rift targets Scala.
- Scala has classes, mutable fields, subtyping, arrays, null, constructors,
  exceptions, closures, iterators, erased generics, and a large heap-oriented
  standard library.
- Rift has Scala 3 capture checking, which gives a different safety foundation
  than classic Hindley-Milner-style region inference.
- Rift's important topologies are stream/dataflow oriented: epoch,
  page/window/bucket, transaction, retained timestamp state, and dataflow
  operator state.
- Scala Native already has Immix GC. Rift's goal is not to replace GC
  everywhere, but to place structured short-lived data-path objects in checked
  regions where the lifetime is clear.

The right formulation is:

```text
Rift should be ReML/MLKit-inspired,
but capture-checking-native and stream/dataflow-oriented.
```

## Where Rift Is Today

Implemented:

```scala
RiftRegion.scoped { region ?=>
  val x: Node^{region} = new Node(...)
}
```

The compiler can lower the `new Node(...)` allocation into `region` because
the expected type says `Node^{region}`.

Also implemented for the first local operator shape:

```scala
RiftRegion.scoped { region ?=>
  val list = RiftRegion.regionList[Node]()
  val x = new Node(...)
  RiftRegion.prependRegionList(region, list, x)
}
```

The compiler can infer `x` as region-owned because the `RegionList` prepend
call supplies an explicit checked owner and the local is immutable.

Also implemented for local captured constraints:

```scala
RiftRegion.scoped { region ?=>
  val x = new Node(...)
  val y: Node^{region} = x
}
```

The compiler can infer `x` as region-owned because the later captured expected
type supplies a unique checked owner. The same applies to assignment into a
captured local variable. This local slice also handles a non-empty block whose
final expression is the direct allocation, including captured-assignment use.
This is still local inference, not method/effect summary inference.
Direct nested construction in a proven region-owned constructor is also
lowered:

```scala
RiftRegion.scoped { region ?=>
  final class Wrapper(val node: Node^{region})
  val wrapper: Wrapper^{region} =
    new Wrapper(new Node(...))
}
```

Also implemented for the first method shape:

```scala
RiftRegion.scoped { region ?=>
  def make(using r: RiftRegion.ScopedRegion^): Node^{r} =
    new Node(...)
  val x = make(using region)
}
```

The compiler can lower the direct `new` inside `make` because the method
summary has a concrete checked region parameter available at runtime. The same
slice also handles a returned immutable local, for scoped regions and for
direct epoch `OpenStreamingRegion` handles. The returned local may also be
initialized by a non-empty construction block whose final expression is the
direct allocation:

```scala
RiftRegion.scoped { region ?=>
  def make(using r: RiftRegion.ScopedRegion^): Node^{r} =
    val x = new Node(...)
    x
  val y = make(using region)
}
```

```scala
RiftRegion.scoped { region ?=>
  def make(using r: RiftRegion.ScopedRegion^): Node^{r} =
    val x =
      val value = 40
      new Node(value)
    x
  val y = make(using region)
}
```

This is not yet full method inference: a helper such as
`def make(): Node^{region} = new Node(...)` is not lowered by this slice,
because the method body does not carry a runtime handle for `region`.

Also implemented for simple branch returns:

```scala
RiftRegion.scoped { region ?=>
  def make(flag: Boolean)(using r: RiftRegion.ScopedRegion^): Node^{r} =
    if flag then new Node(1) else new Node(2)
  val x = make(true)(using region)
}
```

Returned `new` sites are marked only when the result type has a unique checked
owner supplied by an explicit region parameter. The same rule also covers a
direct allocation used as the final expression of a non-empty method block,
and immutable locals returned through branch or match cases when those locals
are initialized by a construction block ending in a direct allocation.

Also implemented for the first generic owner-token buffer shape:

```scala
RiftRegion.scoped { region ?=>
  val buffer = RiftRegion.objectBuffer[Node](1)
  val x = new Node(...)
  RiftRegion.append(region, buffer, x)
}
```

The compiler can infer `x` as region-owned because the explicit append
signature supplies the checked owner. Helper-returned heap objects and inferred
objects with unrooted dynamic heap metadata remain rejected. This does not yet
cover arbitrary container APIs or unconstrained heap collections.

Also implemented for the first common Scala factory allocation:

```scala
RiftRegion.scoped { region ?=>
  val node: Node^{region} = new Node(...)
  val option: Option[Node^{region}]^{region} = Some(node)
}
```

The compiler recognizes the proven region-owned `scala.Some.apply` call and
lowers it to a checked-region `Some` allocation, both for exact `Some` expected
types and for the common widened `Option` expected type. This is intentionally
narrow: `None` and proven `Option.apply(...)` are now separately covered, but
unconstrained `Option(...)`, generic container flows, and heap-visible
`Some(...)` values remain heap fallback or rejection cases.
Direct nested construction is also placed:

```scala
RiftRegion.scoped { region ?=>
  val option: Some[Node^{region}]^{region} =
    Some(new Node(...))
}
```

Also implemented for the second common Scala factory allocation:

```scala
RiftRegion.scoped { region ?=>
  val left: Node^{region} = new Node(...)
  val right: Node^{region} = new Node(...)
  val pair: Tuple2[Node^{region}, Node^{region}]^{region} =
    (left, right)
}
```

The compiler recognizes the proven region-owned `scala.TupleN.apply` call
through the same path originally validated for `Tuple2`, then lowers that
object to a checked-region tuple allocation. The first higher-arity validation
is `Tuple3`; the tuple slice remains deliberately reference-only today:
primitive tuple fields such as `Tuple2(node, 2)` would
introduce a boxed heap object today, so boxed primitive keys/fields stay on the
future synthetic-allocation track until their boxes are proven region-local too.
The compiler suite now records that boundary with negative tests for direct,
owner-token argument, and explicit-region method-return tuple shapes.
Direct nested construction is covered here too:

```scala
RiftRegion.scoped { region ?=>
  val pair: Tuple2[Node^{region}, Node^{region}]^{region} =
    Tuple2(new Node(...), new Node(...))
}
```

Not implemented yet:

- Full inference for `val x = new T(...)` inside arbitrary region scopes.
- Region placement for primitive/boxed tuple fields,
  broader Option container flows, iterators, closures, temporary strings,
  boxed keys, and collection wrappers.
- Broad inferred method summaries, including outer-captured return owners
  without explicit region parameters.
- Inferred region parameters.
- Broader page/window child-region placement beyond explicit child-region
  locals returned by checked owner helpers.
- Broader stream-window rank/table-rank owner-token/topology placement beyond
  the selected synthetic aliases, closure values, branch/match-local direct
  allocation aliases, direct arrays with result-local element ownership
  recovered from explicit result types or prior checked `put` value types, and
  direct branch/match synthetic factories already proven at checked rank/table
  APIs.
- Direct branch/match synthetic-factory placement beyond the currently proven
  owner-token method, checked RegionList node, checked buffer, checked
  priority-queue, and checked rank/table API boundaries.
- Full polymorphic effect constraints.
- Compiler-inserted region creation/deallocation.
- ReML-style whole-module inference.

## Roadmap Meaning

"Following the lineage" for Rift should mean the following staged path:

1. **Explicit captured allocation placement.**
   Direct `new` is placed into a known checked region when the expected
   captured type proves the placement. This is implemented for `ScopedRegion`
   and `OpenStreamingRegion`.

2. **Local owner-constrained inference.**
   Local direct `new` may be placed in a region when a checked API use gives a
   unique owner and escape/capture checks agree. Implemented cases now include
   captured val/assignment constraints, local block-shaped RHS final
   allocations, branch/match returned-local construction blocks, and
   `RegionList` prepend.

3. **Allocation/effect summaries for methods.**
   Infer summaries such as "allocates result in region `r`" and "does not let
   the result escape". A first direct-return method slice is implemented when
   `r` is an explicit method parameter, including simple wrapper forwarding
   plus local-alias, branch, and match wrapper shapes; broader summaries and
   hidden runtime region-parameter insertion are still open.

4. **Framework/operator signature inference.**
  Use checked `epoch`, `page`, `window`, transaction, and dataflow operator
  signatures to infer data-path placement while durable control state remains
  heap allocated. The first owner-token buffer append cases are implemented;
  block-shaped local construction before `RegionList`/`ObjectBuffer`/
  `RegionBuffer` append is covered, as are inline block-final construction
  arguments at those checked boundaries; scoped checked priority-queue push/put
  boundaries are also implemented for immutable direct-new locals, selected
  direct-allocation aliases, and inline block-final construction values. The
  selected synthetic alias proof now reaches checked stream-window rank/table
  `put` APIs, and the same API family accepts branch/match-local direct
  allocation aliases when every returned value is proven region-local. Direct
  branch/match `Some(new T(...))`, `Option(new T(...))`, and
  `Tuple2(new A(...), new B(...))` factory expressions are also validated at
  explicit owner-token method arguments, checked `RegionList` node
  construction through `prependRegionList`, checked `ObjectBuffer`/
  `RegionBuffer` appends, ordinary and lexicographic checked priority-queue
  APIs, and those checked rank/table APIs.
  Selected synthetic aliases nested inside checked `RegionList` node fields
  are also covered when they are real multi-candidate allocation aliases.
  Child-window/page, broader stream-window rank/table-rank topology, and
  broader operator APIs remain open.

5. **Common Scala allocation lowering.**
   Tuples, `Option`, small closures, iterators, boxed keys, temporary records,
   and wrappers can move into regions only when capture/escape checking proves
   the object cannot outlive the region. Narrow captured `Some(...)`, including
   widened `Option[T] = Some(...)`, and reference-safe `TupleN(...)` factory
   slices for arities 2 through 22 are implemented, with Tuple3 validating the
   first higher-arity shape. The narrow static-empty/optional-result slice for
   `None` and `if flag then Some(new T(...)) else None` is also implemented,
   and proven `Option.apply(...)` now preserves null-to-`None` semantics while
   region-allocating the non-null `Some` branch.
   Direct nested construction arguments in proven region-owned
   constructors/factories are also implemented. Local
  nonescaping closure-object placement is implemented both when a
  function-captured expected type proves the owner and when a captured
  region-local value proves the owner; explicit-region-parameter method
  returns and simple forwarded method returns are also implemented for
  closure objects. A narrow captured-owner closure-body shape is also
  implemented, and direct plus typed and untyped named-local closure-body
  returned closures now have validated one-hop effect-summary proofs when the
  returned closure explicitly captures the runtime owner term and a unique
  runtime owner handle is recoverable. Closure bodies can now also allocate
  direct and selected-local `Some(new T(...))`/`Option(new T(...))` and
  `Tuple2(new A(...), new B(...))` factory results under that same captured
  runtime owner, including optional `if ... then Some(new T(...)) else None`
  results, and they can call explicit checked-region callees, simple and
  branch/match forwarded callees, and checked-region factory-returning callees
  for `Some`, `Option.apply`, `Tuple2`, and selected immutable local
  `Option.apply`/`Tuple2` aliases. A closure body can also return
  `Option.apply` or exact `Some` containing an inline closure or an immutable
  selected local closure alias whose nested body allocation uses the same
  runtime owner. The selected-wrapper case includes a bounded GenNIR prepass
  for local closure values and selected aliases under a proven closure
  value/body owner. Broader Option container flows, primitive/boxed tuple
  fields, hidden owner capture beyond that bounded receiver/environment
  preparation, escaping closures, mutable local closure flow, and broad closure
  effect summaries remain open.

6. **Polymorphic safety.**
   ReML's GC-safety work becomes critical here. Generic containers and hidden
   region captures must not escape through widened types such as `AnyRef`.

7. **Effect constraints and diagnostics.**
   ReML-style explicit effects are useful for explaining why an allocation
   stayed on heap or why a method needs a region/effect bound.

8. **Automatic topology inference, cautiously.**
   Infer placement inside existing `epoch`, `window`, and `page` APIs first.
   Full insertion of region boundaries is later and riskier.

## Current Evaluation Stance

Rift should be evaluated as a hybrid checked lifetime-topology system, not as a
completed MLKit/ReML clone.

Allowed current claim:

```text
Rift has started a Scala Native, capture-checking-based adaptation of
ReML-style region placement. It already supports explicit captured allocation
placement, local owner-constrained linked-list/captured-val inference, first
explicit-region-parameter method-return and wrapper-forwarding inference cases,
owner-token buffer/priority-queue boundaries including selected direct-allocation
aliases plus method-returned and owner-token selected local
`Some`/`Option.apply`/`Tuple2` factory aliases plus selected synthetic factory
array stores, checked buffer appends, and checked priority-queue push/put calls,
including dense and long-key lexicographic indexed queue puts, direct
branch/match plus selected-nested `Some`/`Option.apply`/`Tuple2` factory
expressions at checked owner-token method, RegionList node, buffer,
priority-queue, and rank/table API boundaries, including selected-nested
synthetic aliases inside framework-owned value objects, and a narrow captured
`Some(...)`/widened-`Option` plus reference-safe `TupleN(...)` factory
allocation slice, direct nested constructor arguments in proven
region-owned constructors and factories, a narrow generic `Cell[A]` placement
slice including owner-token and narrow polymorphic owner-token method
arguments plus one explicit-owner polymorphic method-return factory, and a
first nonescaping region-capturing closure-object placement slice plus narrow
direct and typed/untyped named-local closure-body returned-closure summaries,
including direct and selected-local closure-body `Some`/`Option.apply`/`Tuple2`
factory results, optional `Some`/`None` closure-body results, explicit
checked-region callees, simple branch/match forwarded callees, and checked-region
factory-returning callees for `Some`, `Option.apply`, `Tuple2`, and selected
immutable local `Option.apply`/`Tuple2` aliases when the closure body captures
the same runtime owner term, plus direct `Option.apply` and exact `Some`
wrappers containing inline closures or immutable selected local closure aliases
whose nested body allocation captures that owner.
```

Disallowed current claim:

```text
Rift implements full Tofte/Talpin, MLKit, or ReML whole-program region
inference.
```

The next serious research/engineering milestone is broader method and closure
allocation/effect summaries, especially summaries that can either pass runtime
region handles explicitly or explain why an outer-captured helper stayed on the
heap.
