# Rift Region Inference Matrix

Last updated: 2026-05-24 15:59 CEST

Status: compiler/runtime evidence for the Scala Native ReML-style placement
inference track. This file records inference capability, safety boundaries,
focused benchmark gates, validation, and remaining gaps. It is not headline
presentation evidence.

Current validation gate: on 2026-05-24 15:59 CEST, after the
lambda-lifted returned-local closure helper bridge was extended to direct
returned local allocations and helper-returned `Some(new T(...))`,
`Option(new T(...))`, `Tuple2(new A(...), new B(...))`, and
`Left(new T(...))`/`Right(new T(...))` wrappers, plus
direct `if`/`match` helper returns of fresh region-owned objects and one
branch/match-forwarded or immutable-alias-forwarded lexical helper result, and
helper-returned `Array[T^{r}]^{r}` values with region-owned element stores plus
primitive `Array[Int]^{r}` values, and after `Either` was added to the
explicit checked-region local method-summary path for direct and one-hop
branch/match-forwarded monomorphic and simple polymorphic method returns, the
closure-body callee-summary path also covers direct and selected-local
`Either` callee returns through an explicit captured owner term, and explicit
owner-token arguments, region-owned array stores, and checked
`ObjectBuffer`/`RegionBuffer` appends, plus ordinary checked priority queues,
and lexicographic checked priority queues cover direct and selected `Either`
factories, checked stream-rank/table-rank APIs cover selected and branch/match
`Either` factories, checked `RegionList` node fields cover selected and
branch/match `Either` factories, and after adding a primitive-box negative for
`Either[Int, Int]^{r}`, and after closure bodies returning `Either` wrappers
around inline or selected local closures gained allocation-stat proof, and
after explicit checked-region methods returning generic wrapper records around
inline or selected local closures gained allocation-stat proof, and after
simple direct and branch-forwarded checked-region methods returning those
generic wrapper records gained allocation-stat proof, and after method-returned
`Some(new Wrapper(new T(...)))` gained allocation-stat proof while
`Some(new Wrapper(closure))` was recorded as a source-capture fallback, and
after simple direct and branch-forwarded checked-region methods returning
`Some(Wrapper(payload))` gained allocation-stat proof while selected
`Option[Wrapper[T^{r}]^{r}]^{r}` aliases and match-forwarded
`Some(Wrapper(payload))` results were recorded as source-capture fallback, and
after direct and branch-forwarded `Option.apply(Wrapper(payload))` gained
allocation-stat proof, after direct and branch-forwarded
`Either(Wrapper(payload))` construction gained allocation-stat proof while
`Left.value`/`Right.value` nested wrapper extraction was recorded as
source-capture fallback, after direct and branch-forwarded
`Option(Either(payload))` construction gained allocation-stat proof, and after
direct and branch-forwarded `Either(Option(payload))` construction gained
allocation-stat proof, after selected-local `Either(Option(payload))`
method-return candidates gained allocation-stat proof, and after
`Tuple2(Wrapper(payload), Wrapper(payload))` method-summary tests recorded
source capture widening as an explicit fallback boundary. The checked compiler
suite passed `702/702`, the
checked runtime/allocation-stat suite passed `316/316`, and
`sandbox3_next` compile passed. The promoted
capability is bounded to unique
owner-typed local helper returns where NIR can resolve a concrete lowered
checked owner value, plus explicit checked-region method summaries with a
concrete owner parameter. Unresolved/type-only lowered owners stay on the heap.
Primitive boxes and boxed keys also stay on the heap for now because
`nir.Op.Box` has no allocation-zone operand and lowers through the standard
boxed runtime path.

Previous promoted gate: on 2026-05-21 21:46-21:50 CEST, after the
closure-body wrapper-returned exact-`Some(inlineClosure)` proof was added, the
checked compiler suite passed `595/595`, the checked runtime/allocation-stat
suite passed `262/262`, and the production sandbox compile gate passed again.
The same
sandbox compile also passed with `-P:scalanative:riftInferReport` in the
earlier stream-rank closure gate. Earlier 2026-05-21 LogHub/Wikimedia smokes,
1M x3 L2 gates, and focused L4 profiles remain benchmark/source-use evidence
for the inferred array source-placement slice. The newest Broom generated-array
1M x3 L2 gate extends that source-use evidence to generated retained dataflow
arrays. The newest closure array-store, owner-token closure-container,
stream-rank closure, match-forwarded method-returned array, and owner-token
array-argument/checked-buffer-array/checked-priority-queue-array plus
stream-rank direct-array slices are compiler/runtime allocation-stat capability
proofs, not elapsed-time claims. The current stream-rank direct-array proof
recovers result-local array element ownership from either explicit result
types or the prior checked `put` value type, so the direct put/peek test no
longer needs a result-local captured type ascription. The newest branch/match
array-store proof extends region-owned array stores to direct constructors and
synthetic factories returned by `if`/`match`, with unrooted metadata negatives
preserved. The newest `epochFoldRegionFor` proof extends the selected
child-region local-new mechanism to epoch-fold operator regions, and the
Dataflow aggregate epoch-fold control now exercises that proof with ordinary
`new` source placement. The fixed chunk-token append control now also exercises
the existing `chunkAppendRegionFor` child-owner proof with ordinary `new` in a
direct child-owner lexical scope. The newest boundary proof adds ordinary
`new` allocation-stat coverage for `epochBufferRegionFor` while keeping mutable
checked owner-slot aliases rejected and visible in the opt-in inference report.
The newest Theodolite retained-UC4 source-use proof exercises active
open-handle ordinary `new` placement in a real streaming row without changing
the scoped or legacy explicit-allocation controls. The newest selected
polymorphic owner-token proof validates explicitly region-typed selected local
`Cell[A^{r}]^{r}` candidates flowing into a polymorphic consumer, while keeping
untyped selected generic cells outside the accepted inference boundary because
capture checking loses the owner before the current post-capture inference
phase can repair it.
The newest closure/effect proof validates lambda-lifted local helpers inside
checked-owner closure bodies that return either a named local closure alias or
a named local direct allocation, plus common helper-returned
`Some(new T(...))`, `Option(new T(...))`, `Tuple2(new A(...), new B(...))`,
and `Left(new T(...))`/`Right(new T(...))` wrapper shapes, and direct
`if`/`match` helper returns of fresh region-owned
objects, plus one branch/match-forwarding helper that returns another inferred
lexical-owner helper result and the immutable alias-forwarding variant. Runtime
allocation stats prove the outer
closure, helper-returned local closure, and nested body object are
checked-region allocations for the closure-returning helper; the outer closure
plus helper-returned object are checked-region allocations for the direct-object
helper; and the outer closure, wrapper, and payloads are checked-region
allocations for the library-wrapper helpers. The direct `if`/`match` helper
proofs show the outer closure plus selected arm object are checked-region
allocations. The branch/match-forwarding proofs show the outer closure plus
forwarded result object are checked-region allocations, including the immutable
alias-forwarded local. The array proof shows the outer closure, helper-returned
array, and stored element object are checked-region allocations. Each case still
requires that the lowered helper has a concrete runtime owner handle. The
primitive-array proof shows the outer closure plus `Array[Int]` allocate in the
checked region and that returned primitive arrays still cannot escape to heap
state. Paired type-only helper cases stay heap fallback.
The previous wrapper proof validates region-owned closure bodies returning
either `Option.apply` or exact `Some` wrappers that contain an inline closure or
a selected immutable local closure alias.
This is the current safety baseline for the inference slices recorded below.

2026-05-24 lambda-lifted returned-local closure helper update: local helpers
inside checked-owner closure bodies can now return a named local closure alias
when the helper result type has a unique checked owner and the lowered helper
environment exposes a concrete runtime owner value. The source pass records
method-return owners by exact symbol, source span, and normalized source line,
and records closure-owner candidates by source span and source line. GenNIR
uses those summaries to attach the owner to local closure aliases returned
from the lowered helper, but only after `inferredRiftOwnerValue` resolves an
actual checked owner value. The closure capture checker now accepts a
lambda-lifted owner alias such as `owner$13` only when that capture and the
source owner resolve to the same lowered runtime value. Runtime allocation
stats prove the outer closure wrapper, helper-returned local closure wrapper,
and nested body object are checked-region allocations (`delta >= 3`). The
paired type-only helper case remains heap fallback when no runtime owner handle
is available (`delta < 3`). Compiler positives/negatives cover the helper
shape and unrooted heap metadata rejection. This is still not arbitrary hidden
owner recovery, escaping closure inference, mutable closure flow, virtual
effect summaries, or full lambda signature/environment rewriting.

2026-05-24 lambda-lifted returned-local direct allocation helper update: the
same source-line method-return bridge now reaches helper bodies that return a
named local direct allocation, for example
`def build(...) = { val x: T^{owner} = new T(...); x }`. The source pass
requires a unique lexical checked owner type plus a value-position use of that
owner in the helper body before recording the method-return candidate. GenNIR
then reuses the source-line method-return summary only if the lowered helper
environment resolves that owner to a concrete checked runtime handle. Runtime
allocation stats prove the outer closure wrapper plus helper-returned direct
object are checked-region allocations (`delta >= 2`). The paired type-only
helper case, where the owner appears only in types and no lowered owner handle
is available, remains heap fallback (`delta < 2`). Compiler positives and
negatives cover the helper shape and unrooted heap metadata rejection. This is
still not broad type-only owner recovery; it is a bounded runtime-owner-term
bridge for lambda-lifted helper returns.

2026-05-24 lambda-lifted returned-local synthetic factory helper update: local
helpers inside checked-owner closure bodies can also return named local
`Option[T^{owner}]^{owner}`, `Tuple2[A^{owner}, B^{owner}]^{owner}`, or
`Either[A^{owner}, B^{owner}]^{owner}` factory results initialized with
`Some(new T(...))`, `Option(new T(...))`,
`Tuple2(new A(...), new B(...))`, or
`Left(new A(...))`/`Right(new B(...))` under the same bounded bridge. The
source pass records the unique lexical checked owner only when the helper body
has a runtime owner-term use; GenNIR then places the wrapper and nested payloads
only after resolving a concrete lowered owner handle. Runtime allocation stats
prove the outer closure wrapper, helper-returned `Some`/`Option.apply`, and
nested payload are checked-region allocations (`delta >= 3`), prove the outer
closure wrapper, helper-returned `Tuple2`, and both nested payloads are
checked-region allocations (`delta >= 4`), and prove the outer closure wrapper,
selected `Left`/`Right` wrapper, and payload are checked-region allocations
(`delta >= 3`). Paired type-only helpers remain heap fallback
(`delta < 3` / `delta < 4`), and compiler negatives reject unrooted heap
metadata inside the returned factories. This extends the helper bridge to
additional library-created allocation shapes without claiming broad library
inference, primitive boxed paths, or erased generic summaries.

2026-05-24 checked-region `Either` method/effect-summary update: explicit
checked-region local methods can now return
`Either[A^{r}, B^{r}]^{r}` using direct `Left(new A(...))` or
`Right(new B(...))` construction, and one branch/match-forwarding helper can
return that method result while preserving the same owner. The source
inference pass treats `Left.apply` and `Right.apply` as direct region
constructors, and GenNIR lowers the selected case wrapper through the checked
region allocator only when the method result owner is concrete. Runtime
allocation stats prove direct method-returned `Either` wrapper plus payload
allocation (`delta >= 2`) and branch/match-forwarded method-returned `Either`
wrapper plus payload allocation (`delta >= 4`). Compiler negatives reject
unrooted heap metadata stored in a region-owned `Either` and reject retaining a
forwarded `Either[Node^{r}, Node^{r}]^{r}` in heap state through `AnyRef`.
This is a selected method/effect-summary extension, not arbitrary virtual
dispatch, erased generic forwarding, primitive boxed-key support, or broad
library allocation inference.

2026-05-24 polymorphic checked-region `Either` method/effect-summary update:
the selected `Either` method-summary path now covers simple polymorphic
factory signatures with explicit checked owner parameters, for example
`def make[A, B](using r)(left: A^{r}, right: B^{r}): Either[A^{r}, B^{r}]^{r}`,
plus one branch/match-forwarding wrapper over that factory. Runtime allocation
stats prove the direct polymorphic returned `Either` case and argument
payloads are checked-region allocations (`delta >= 3`) and prove the
branch/match-forwarded polymorphic `Either` results and selected payloads are
checked-region allocations (`delta >= 4`). Compiler negatives reject unrooted
heap arguments passed as `A^{r}` and reject heap retention through widened
`AnyRef`. This is a bounded explicit-owner polymorphic summary; erased
generic containers, virtual dispatch, callbacks, mutation, and unknown
libraries remain fallback/rejected.

2026-05-24 closure-body `Either` callee-summary update: a region-owned closure
body can now call an explicit checked-region callee returning
`Either[A^{r}, B^{r}]^{r}` when the closure body captures and passes the
concrete checked owner term. The proof covers a direct callee result such as
`if p then Left(new A(...)) else Right(new B(...))` and a selected-local callee
result where the callee constructs local `Left`/`Right` values and returns the
selected one. Runtime allocation stats prove the closure wrapper plus direct
callee-returned `Either` wrapper and payload are checked-region allocations
(`delta >= 3`) and prove the closure wrapper plus selected callee-returned
`Either` wrappers and payloads are checked-region allocations (`delta >= 5`).
Compiler negatives reject unrooted heap metadata through both direct and
selected `Either` callee results. This is another bounded closure/effect
summary over explicit checked owner calls, not arbitrary escaping-closure
inference or broad library callback inference.

2026-05-24 closure-body `Either` wrapped-closure update: a region-owned
closure body can now directly return `Left(inlineClosure)`/`Right(inlineClosure)`
or `Left(selectedClosure)`/`Right(selectedClosure)` when the wrapped closure
value and its nested body allocation both capture the same concrete checked
runtime owner term. Runtime allocation stats prove the outer closure wrapper,
`Left`/`Right` wrapper, wrapped closure value, and nested body allocation are
checked-region allocations for inline closures (`delta >= 4`) and selected
local closures (`delta >= 5`). Compiler negatives reject unrooted heap metadata
captured by either nested closure body through the `Either` wrapper. This
extends the prior `Option.apply(closure)` and exact `Some(closure)` wrapper
proofs to `Either`, but still requires an explicit owner capture and does not
infer escaping closures or arbitrary callback/library effects.

2026-05-24 owner-token and array-store `Either` update: the explicit
owner-token method-argument path and the region-owned array element-owner path
now cover `Either[A^{r}, B^{r}]^{r}` factories. Runtime allocation stats prove
inline owner-token `Either` wrapper plus payload allocation (`delta >= 2`),
selected owner-token `Either` candidates plus payload allocation
(`delta >= 4`), inline array-store `Either` wrapper plus payload allocation
alongside the region-owned array (`delta >= 3`), and selected array-store
`Either` candidates plus payloads alongside the region-owned array
(`delta >= 5`). Compiler negatives reject unrooted heap metadata in
owner-token `Either` arguments and in direct or selected array-store `Either`
values. This extends common synthetic/library wrapper placement; it does not
infer through arbitrary arrays, erased containers, primitive boxes, or unknown
libraries.

2026-05-24 checked-buffer `Either` update: checked `ObjectBuffer` and
`RegionBuffer` append boundaries now cover selected local and direct
branch/match `Either[A^{r}, B^{r}]^{r}` factories. The proof reuses the
existing framework owner-token path for `Some`/`Option.apply`/`Tuple2`:
when the buffer value type is captured by the checked owner and every
`Left`/`Right` candidate plus payload is safe for that owner, GenNIR places
the case wrapper and payload in the checked region. Runtime allocation stats
prove selected and branch/match checked-buffer `Either` wrappers plus payloads
are checked-region allocations (`delta >= 12`). Compiler positives cover
selected and branch/match `ObjectBuffer`/`RegionBuffer` appends; compiler
negatives reject unrooted heap metadata in selected and branch/match
checked-buffer `Either` stores. This extends explicit framework-container
wrapper placement, not arbitrary collection or erased-container inference.

2026-05-24 checked-priority-queue `Either` update: ordinary checked
`RegionPriorityQueue`, `RegionIndexedPriorityQueue`, and
`RegionLongIndexedPriorityQueue` owner-token boundaries now cover selected
local and direct branch/match `Either[A^{r}, B^{r}]^{r}` factories. The proof
reuses the same checked queue owner-token path already validated for
`Some`/`Option.apply`/`Tuple2`: every selected or branch/match `Left`/`Right`
candidate plus payload must be safe for the queue value owner before GenNIR
places it in the checked region. Runtime allocation stats prove selected and
branch/match checked-priority-queue `Either` wrappers plus payloads are
checked-region allocations (`delta >= 8`). Compiler positives cover plain,
indexed, and long-indexed queue placement; compiler negatives reject unrooted
heap metadata in selected and branch/match checked-priority-queue `Either`
stores. This extends explicit framework-container wrapper placement, not
arbitrary priority-queue or erased-container inference.

2026-05-24 lexicographic checked-priority-queue `Either` update: checked
`RegionIndexedPriorityQueueLexicographic` and
`RegionLongIndexedPriorityQueueLexicographic` owner-token boundaries now cover
selected local and direct branch/match `Either[A^{r}, B^{r}]^{r}` factories.
The proof uses the same lexicographic `put` owner-token path already validated
for `Some`/`Option.apply`/`Tuple2`: every selected or branch/match
`Left`/`Right` candidate plus payload must be safe for the queue value owner
before GenNIR places it in the checked region. Runtime allocation stats prove
selected and branch/match lexicographic checked-priority-queue `Either`
wrappers plus payloads are checked-region allocations (`delta >= 12`).
Compiler positives cover indexed and long-indexed lexicographic queue
placement; compiler negatives reject unrooted heap metadata in selected and
match lexicographic checked-priority-queue `Either` stores. This extends
explicit framework-container wrapper placement, not arbitrary priority-queue
or erased-container inference.

2026-05-24 checked stream-rank/table-rank `Either` update:
`putWindowRank`, `putWindowRankInBucket`, and `putTableRankInBucket`
owner-token boundaries now cover selected local and direct branch/match
`Either[A^{r}, B^{r}]^{r}` factories. The proof reuses the same checked
stream owner-token path already validated for `Some`/`Option.apply`/`Tuple2`:
every selected or branch/match `Left`/`Right` candidate plus payload must be
safe for the rank/table value owner before GenNIR places it in the checked
region. Runtime allocation stats prove selected and branch/match checked
stream-rank/table-rank `Either` wrappers plus payloads are checked-region
allocations (`delta >= 8`). Compiler positives cover indexed rank,
lexicographic long-indexed rank, and table-rank placement; compiler negatives
reject unrooted heap metadata in selected indexed-rank and match table-rank
`Either` stores. This extends explicit framework-container wrapper placement,
not arbitrary stream topology, priority-queue, erased-container, or
primitive-box inference.

2026-05-24 checked `RegionList` `Either` update: captured `RegionList` node
constructors now cover selected local and direct branch/match
`Either[A^{r}, B^{r}]^{r}` factories. The proof reuses the captured
`RegionList` node-field path already validated for `Some`/`Option.apply` and
`Tuple2`: every selected or branch/match `Left`/`Right` candidate plus payload
must be safe for the `prependRegionList` owner before GenNIR places it in the
checked region. Runtime allocation stats prove selected and branch/match
checked `RegionList` nodes, `Either` wrappers, and payloads are checked-region
allocations (`delta >= 10`). Compiler positives cover selected, branch, and
match node-field placement; compiler negatives reject unrooted heap metadata in
branch/match and selected nested `RegionList` `Either` fields. This extends
explicit collection-node wrapper placement, not arbitrary `RegionList`,
erased-container, or primitive-box inference.

2026-05-24 primitive-box audit update: primitive boxes and boxed keys remain
heap/library fallback. The current NIR operation is still
`nir.Op.Box(ty, obj)` with no allocation-zone or owner operand, and the lowerer
rewrites it through the standard boxed runtime call. That path may preserve
boxed primitive cache/identity behavior, so region placement needs a separate
zone-aware design before it is sound. Existing negatives already reject
`Option[Int]^{r}`, primitive tuple fields such as
`Tuple2[Int, T^{r}]^{r}`, and preboxed `Any` values entering a checked-region
wrapper; the new `eitherPrimitiveLiteralRequiresBoxingSupport` negative adds
the same guard for `Either[Int, Int]^{r}`. No runtime checks were removed.

2026-05-24 lambda-lifted direct-control-flow helper update: local helpers
inside checked-owner closure bodies can now directly return an `if` or `match`
expression whose selected arm constructs `T^{owner}`, for example
`def build(offset: Int): T^{owner} = if offset >= 0 then new T(...) else new T(...)`,
or the equivalent `match`, without first storing the result in a named local.
The source pass records the method-return owner only when the helper result
type has a unique lexical checked owner and the helper body has a runtime
owner-term use. GenNIR still attaches the allocation zone only after resolving
a concrete lowered owner handle. Runtime allocation stats prove the outer
closure wrapper plus selected branch/match object are checked-region
allocations (`delta >= 2`). The paired type-only direct-branch/direct-match
helpers remain heap fallback (`delta < 2`), and compiler negatives reject
unrooted heap metadata in every arm. This is a bounded direct-control-flow
helper summary, not arbitrary branch/match effect inference across unknown
callees.

2026-05-24 lambda-lifted forwarded-helper update: a lexical helper inside a
checked-owner closure body can now branch-forward or match-forward the result
of another
inferred lexical-owner helper, for example
`def build(offset: Int): T^{owner} = if offset >= 0 then allocate(offset) else allocate(0)`,
where `allocate` is already proven to return `T^{owner}` through the same
runtime-owner-term bridge. The forwarding summary is accepted only when the
forwarded callee/local summary has one owner, that owner matches the unique
lexical result owner, and the forwarding helper body contains a runtime owner
term. Runtime allocation stats prove the outer closure wrapper plus forwarded
result object are checked-region allocations (`delta >= 2`). The paired
type-only branch/match-forwarded helpers remain heap fallback (`delta < 2`), and the
compiler negative rejects unrooted heap metadata in the forwarded allocator.
Conflicting or ambiguous forwarded owners are rejected. This is one simple
method/effect-summary hop, not arbitrary virtual dispatch, callbacks,
exceptions, mutation, or erased-library forwarding.

2026-05-24 lambda-lifted alias-forwarded helper update: the same forwarded
helper summary now has explicit proof for immutable local aliases inside the
forwarding helper:
`val forwarded: T^{owner} = allocate(offset); forwarded`. The alias is accepted
only when the aliased helper result has one inferred owner, that owner matches
the unique lexical result owner, and the forwarding helper body has a runtime
owner-term use. Runtime allocation stats prove the outer closure wrapper plus
alias-forwarded result object are checked-region allocations (`delta >= 2`).
The paired type-only alias-forwarded helper remains heap fallback
(`delta < 2`), and the compiler negative rejects unrooted heap metadata in the
aliased allocator. Mutable aliases remain outside this proof.

2026-05-24 lambda-lifted returned-array helper update: local helpers inside
checked-owner closure bodies can now return a named local
`Array[T^{r}]^{r}` and store a region-owned element into it under the same
runtime-owner-term bridge. Runtime allocation stats prove the outer closure
wrapper, helper-returned array, and stored element object are checked-region
allocations (`delta >= 3`). The paired type-only helper remains heap fallback
(`delta < 3`), and the compiler negative rejects storing unrooted heap metadata
into the returned region-owned array. The accepted array result type must name
the original checked owner `r`; a local owner alias is used only as the runtime
owner term for lowered-handle recovery, not as a substitute array result owner.
This extends the helper bridge to a library/runtime allocation shape without
claiming broad array flow through arbitrary generic APIs.

2026-05-24 lambda-lifted returned-primitive-array helper update: local helpers
inside checked-owner closure bodies can now return `Array[Int]^{r}` under the
same runtime-owner-term bridge. Runtime allocation stats prove the outer
closure wrapper plus primitive array are checked-region allocations
(`delta >= 2`). The paired type-only primitive-array helper remains heap
fallback (`delta < 2`), and the compiler negative rejects retaining the
returned `Array[Int]^{r}` in heap state through a widened `AnyRef`. This covers
the common counter/scratch-array shape without changing boxed primitive paths.

2026-05-21 closure-body returned-closure update: a region-owned closure body
that directly returns another closure now has compiler/runtime proof that the
returned closure wrapper and its nested captured-owner body allocation can be
placed in the same checked region. The accepted shape requires the returned
closure to explicitly capture the runtime checked owner term; type-only hidden
owner capture remains heap fallback. Runtime allocation stats prove the outer
closure wrapper, returned inner wrapper, and nested `RiftCheckedLeaf` object
allocate in checked region memory (`delta >= 3`), and generated LLVM for the
proof shows all three allocations calling the region allocator rather than
`scalanative_GC_alloc_small`. A broader GenNIR fallback for arbitrary
owner-capturing closures was rejected: clean runtime safety tests showed it
could allocate stale-token assertion lambdas into already-closed regions before
`assertThrows` received them.

2026-05-21 named local closure-body returned-closure update: the named-local
variant is now validated first with an explicit captured local function type
such as `Function1[Int, Box^{owner}]^{owner}`, and then without that local
type ascription when the enclosing closure result type names an explicit
checked owner and the compiler can recover the same runtime owner term. Runtime
allocation stats prove the outer closure wrapper, named local inner wrapper,
and nested body object are all checked-region allocations (`delta >= 3`), and
generated LLVM for the untyped proof shows the local inner wrapper allocation
uses the region allocator instead of `scalanative_GC_alloc_small`. Hidden
type-only owner capture without a runtime handle, escaping returned closures,
mutable local closure flow, and the broad allocation-site fallback remain
rejected or heap fallback.

2026-05-21 stored closure-body allocation update: direct inline closures stored
into region-owned arrays and checked owner-token containers now preserve the
explicit checked owner for the closure wrapper and the closure body allocation
when the stored closure captures the same runtime owner term. The proof covers
direct region-owned array stores, `RiftRegion.append(region, ObjectBuffer, ...)`
inline closures, and selected local closures appended to `RegionBuffer`.
GenNIR now recognizes owner aliases such as `val owner = region`, and the
checked array-store path has a bounded erased-array fallback: if primitive
array update lowering has erased the element capture, the direct closure can
use the already inferred region-owned array object owner only when the closure
captures that exact runtime owner. Compiler negatives still reject stored
closures that capture unrooted heap metadata. Runtime allocation stats prove
the ObjectBuffer backing array plus closure/body allocation (`delta >= 3`),
RegionBuffer backing array plus selected closure/body allocation
(`delta >= 4`), and region-owned array plus closure/body allocation
(`delta >= 3`) are checked-region objects. This is not arbitrary escaping
closure inference and does not relax stale-token/use-after-close checks.

2026-05-21 priority-queue stored closure-body update: ordinary checked
`RegionPriorityQueue.push` now has explicit compiler/runtime proof for inline
and selected immutable local closure values whose bodies allocate through a
captured checked owner term. This validates the existing owner-token summary
path for priority-queue closure-body effects: the wrapper placement proof and
the body-local returned allocation both stay tied to the explicit runtime owner
handle. Runtime allocation stats prove backing queue arrays plus inline
closure/body allocation and selected closure/body allocation are checked-region
objects (`delta >= 4`). Compiler negatives still reject unrooted heap metadata
captured by the pushed closure body. This remains bounded to explicit
owner-token containers; hidden owner capture, escaping closure summaries,
mutable closure flow, and topology inference remain future work.

2026-05-21 wrapper-nested closure-body update: region-owned wrapper
constructors now propagate their proven checked owner to direct inline closures
and selected immutable local closures nested in constructor/factory arguments.
`RiftRegionInference` records those nested closure allocation sites under the
wrapper's direct allocation, including the common helper shape
`val selected = if flag then first else second; new Wrapper(selected)`.
GenNIR now attaches the owner to nested closure arguments before checking
region constructor arguments, so the closure object and its captured-owner body
allocation are lowered together. Runtime allocation stats prove wrapper plus
inline closure/body allocation (`delta >= 3`) and wrapper plus selected
closure/body allocation (`delta >= 4`) are checked-region objects. Compiler
negatives reject unrooted heap metadata captured by the nested closure body.
This is the first explicit "closure passed through a simple wrapper" proof; it
still requires a runtime checked owner term captured by the closure body and
does not implement hidden owner capture, escaping closure summaries, mutable
closure flow, or automatic topology inference.

2026-05-21 method-returned `Some(closure)` body update: explicit checked-region
methods can now return `Option[Function1[Int, T^{r}]^{r}]^{r}` as
`Some(closure)` while preserving the nested closure value owner and the
captured-owner body allocation. This validates the method-return factory
summary plus the nested-closure wrapper proof across a callee boundary, for
both direct inline closures and selected immutable local closure aliases.
Runtime allocation stats prove the method-returned `Some` plus inline
closure/body allocation (`delta >= 3`) and method-returned `Some` plus
selected closure/body allocation (`delta >= 4`) are checked-region objects.
Compiler negatives reject unrooted heap metadata captured by the nested
closure body. This is a library-wrapper/method-summary closure-effect proof;
it still requires an explicit checked-region method parameter and a runtime
owner term captured by the closure body.

2026-05-21 owner-token generic-wrapper closure-body update: explicit
owner-token method arguments now validate `new Wrapper[T^{r}](closure)` where
the wrapper value itself is `Wrapper[T^{r}]^{r}` and the closure body allocates
through a captured runtime owner term. The proof covers direct inline closures
and selected immutable local closure aliases flowing through the same method
argument boundary. Runtime allocation stats prove the wrapper plus inline
closure/body allocation (`delta >= 3`) and wrapper plus selected closure/body
allocation (`delta >= 4`) are checked-region objects. Compiler negatives reject
unrooted heap metadata captured by the nested closure body. This strengthens
the owner-token method-argument effect summary for simple wrappers, but still
does not infer escaping closure lifetimes or hidden/type-only owners without a
runtime handle.

## 2026-05-19 Profiling Note

No new inference capability was added in the mutator-parity cycle. The targeted
profiles did include `wikimedia-clickstream-checked-rift-inferred`; it currently
has the same high-level profile shape as explicit checked Rift. The immediate
implementation follow-up was a backend-neutral DSPBench scratch-field cleanup,
not a compiler inference milestone. Next inference work should be driven by
sampled accidental heap objects that remain frequent after this cleanup:
`Option`/`Some`, tuples, closures, iterators, boxed keys, wrappers, or other
synthetic allocations that satisfy existing escape/capture safety tests.

2026-05-20 update: the Wikimedia checked session source-shape cleanup removed
boxed `scala.runtime.*Ref` captures from checked top frames, but the post-fix
L4 profile still shows a checked region-body callback frame. A direct
`inline resetOpenHandle` experiment failed to compile because capture checking
lost the tracked `RiftOpenStreamingHandle` owner and widened it to `{any}` in
many benchmark bodies. Narrower internal `resetOpenHandleInline` probes now
pass for simple and non-inline-wrapper open-handle bodies, including
region-owned arrays and region-local element stores, when the final raw reset
is delegated to a non-inline helper. The minimized remaining failures are now
explicitly guarded: enclosing `inline def` wrappers lose the owner capture. A
later local branch/match-final inference slice now handles mixed runtime branches
where a captured expected type selects between inferred `new` and explicit
`allocateOpenHandle`; both the compiler and NIR lowering now visit
branch/match-returned construction sites. This makes inlineable checked
region-body callbacks a compiler ownership-preservation / effect-summary
target for the inference track, not a runtime-only
optimization. A practical session-path follow-up now avoids the rejected shape:
`checked-rift-inferred` session mode in `LogHubRetainedSessionMatrix` is split
out of the enclosing `inline def` wrapper and calls the internal inline reset
helper through a sandbox-only bridge. The first 1M Wikimedia split-only L2 row
is `1867.761 ms`, versus explicit checked Rift `1955.329 ms` and heap
`2044.334 ms`, with matching checksum/output. A follow-up state-local cleanup
moved the inferred loop counters inside the open-handle callback; the fresh 1M
row is `1927.010 ms`, versus explicit checked Rift `2015.182 ms` and heap
`2082.274 ms`, and L4 no longer samples boxed `scala.runtime.*Ref` top-frame
parameters. This is evidence that the inlineable reset-body direction is
useful, but it is still a source-shape workaround for one framework path rather
than full ownership-preserving compiler inlining.

2026-05-20 Dataflow update: `DataflowRegionMatrix` now has
`checked-epoch-stream-inferred` for direct epoch SELECT/AGGREGATE/JOIN. It keeps
the same active-handle checked direct-epoch topology and query logic as
`checked-epoch-stream`, but uses ordinary `new` where the captured expected
type proves the active owner. A 20k aggregate smoke matched checksum/output
across heap, explicit direct epoch, inferred direct epoch, and scoped direct
epoch; additional inferred direct-epoch SELECT and JOIN 20k smokes passed with
checksums `5222637068` and `7627482881`. The focused 20M x3 L2 aggregate gate
under
`/Users/siyaoliu/rift/cache/dataflow-inferred-direct-epoch-20m-20260520`
matched checksum `2584512318695`: heap `755.885 ms` with `177.424 ms` median
GC; explicit checked direct epoch `507.004 ms` with `2.724 ms` region op and
`21310740` region objects; inferred checked direct epoch `493.087 ms` with
`1.863 ms` region op and the same region object count; checked scoped direct
epoch `457.737 ms`. Because that L2 row counts Rift allocator stats for direct
Rift but not for scoped, it is interpretation evidence rather than a headline
backend-selection result. A sequential external L1 final-clean follow-up at 20
epochs x 5M docs x3 under
`/Users/siyaoliu/rift/cache/dataflow-inferred-direct-epoch-finalclean-100m-seq-20260520`
is heap `12.83 s`, RSS `2289 MB`; explicit checked direct epoch `6.43 s`, RSS
`168 MB`; inferred checked direct epoch `6.41 s`, RSS `168 MB`; checked scoped
direct epoch `6.33 s`, RSS `168 MB`, all with checksum `12894709366184`. This
is useful inference/source-plumbing evidence and narrows the final-clean direct
Rift versus scoped gap to about `1-2%`.

2026-05-20 StreamFlex update: `StreamFlexDesignMatrix` now has a focused
post-timing-guard comparison of explicit checked stream allocation versus
`checked-epoch-stream-inferred`. At 20M events x3, explicit checked stream is
`19.01 s`, while inferred checked stream is `18.16 s`, both at RSS `12.5 MB`
with matching checksum/output. L4 profile buckets remain nearly the same
between the two rows, so the inference win is source/lowering overhead rather
than a topology change. The remaining StreamFlex work is allocation
body/object construction and query pipeline execution.

2026-05-20 ReML-shaped stream update: `ReMLRegionMatrix` now has
`checked-region-stream-inferred` for `msort`, `msort-r`, `fft`, `ratio`,
`logic`, `ray`, and `tsp`. The new mode leaves the existing heap, explicit
checked stream, and checked scoped controls untouched, but runs the checked
Rift stream body through an `OpenStreamingRegion` epoch and uses ordinary
`new` for the ReML data-path records plus region-owned arrays. Focused native
smokes with small workload sizes matched checksums across heap, explicit
checked stream, and inferred checked stream for all seven workloads. Region
object counts matched explicit checked stream in each inferred row:
`msort/msort-r` `2000`, `fft` `3071`, `ratio` `2001`, `logic` `120`, `ray`
`17`, and `tsp` `289`. The inferred rows show one expected extra reset from
the epoch boundary. Sandbox compile, native link with `ReMLRegionMatrix` as the
main class, and sandbox compile with `-P:scalanative:riftInferReport` all
passed for this slice. This is ReML-style source-placement and allocation-stat
evidence, not an elapsed-time claim.

2026-05-21 stream-rank/table-rank selected-synthetic update: selected local
`Some(new T(...))`, `Option(new T(...))`, and
`Tuple2(new A(...), new B(...))` aliases can now be constrained by checked
stream-window rank/table-rank owner-token APIs. The accepted APIs are
`putWindowRank`, `putWindowRankInBucket`, and `putTableRankInBucket`, and the
framework `StreamingRegion` owner token is used only in this checked
rank/table context after every selected candidate allocation is proven
region-placeable. The corresponding rank/table element bounds now accept
captured object values (`T <: Object^`). Runtime allocation stats use a
setup-only versus selected-value differential after the stream region closes,
because per-region counters flush at close/reset; the proof observes
`delta >= 14` for the selected wrappers and nested direct payloads. Compiler
negatives reject unrooted heap metadata through indexed rank, long-key rank,
and table-rank boundaries, while the existing direct heap-object stream-rank
negatives keep parent `StreamingRegion` excluded from broad generic placement.
This is a narrow selected-alias/framework-owner proof, not automatic
stream-window bucket topology inference.

2026-05-21 stream-rank/table-rank branch/match-local update: checked stream
rank/table owner-token inference now recognizes non-direct local-selection
shapes such as `put...(if flag then first else second, ...)` and
`put...(selector match { case 0 => first; case _ => second }, ...)` when every
selected value is an immutable local direct allocation and the checked
rank/table context supplies the stream owner token. Compiler positives cover
`putWindowRank`, `putWindowRankInBucket`, and `putTableRankInBucket` for branch
and match-returned local values; negatives cover unrooted heap metadata through
selected candidates. The NIR checker also treats `if`, `match`, `Return`, and
Scala 3 lowered `Labeled` match-result expressions as known region values only
when every returned value is known region-local, and it conservatively treats
branch/match expressions as region-captured for heap-retention checking when
any branch carries a region capture. Runtime stats compare setup-only and
branch/match-value stream bodies after close/reset stat flush and observe
`delta >= 6` for the rank/table candidate objects. Direct local heap-looking
stream-rank/table values remain rejected.

2026-05-21 owner-token branch/match synthetic-factory update: direct
branch/match returned `Some(new T(...))`, `Option(new T(...))`, and
`Tuple2(new A(...), new B(...))` expressions can now be constrained at
owner-token boundaries without first naming each factory result in a local.
The validated boundaries are explicit owner-token method arguments and checked
`ObjectBuffer`/`RegionBuffer` appends, ordinary checked priority-queue
push/put calls, dense/long lexicographic checked priority-queue put overloads,
and checked stream-window rank/table-rank `putWindowRank`,
`putWindowRankInBucket`, and `putTableRankInBucket`. The inference pass marks
every returned direct factory app with the supplied checked owner, and NIR
store checking treats those attached apps as known region values when all
branch/match returns are proven. Compiler negatives reject unrooted heap
metadata through the direct branch/match factory path, including buffer and
queue stores. Runtime stats prove the executed `Some`/`Option.apply`/`Tuple2`
wrappers plus payloads allocate in checked region memory at explicit
owner-token method arguments, checked buffer appends, ordinary checked priority
queues, and checked stream rank/table APIs (`delta >= 7`). Mixed or
heap-looking branches still reject through the existing checked-object-buffer
or checked-allocation metadata checks.

2026-05-21 RegionList branch/match nested synthetic-factory update:
`RegionList` now accepts captured node element types (`T <: RegionListNode^`),
matching the checked buffer/priority-queue captured-element rule while keeping
`prependRegionList` values explicitly captured by the supplied owner token.
This lets branch/match-created list nodes contain region-owned synthetic
wrappers such as `Some(new T(...))`, `Option(new T(...))`, and
`Tuple2(new A(...), new B(...))` in their fields. The NIR safety check now
recursively validates direct region-placed constructors and factory apps under
`if`, `match`, `Return`, and Scala 3 lowered `Labeled` match-result forms, so
an outer region-owned node no longer hides an unrooted heap payload inside a
nested `Option` or tuple factory. Compiler negatives cover
`Option(metadata)` and `Tuple2(metadata, metadata)` nested in branch/match
RegionList node construction. Runtime stats prove the executed nodes,
wrappers, and payloads allocate in checked region memory (`delta >= 10`).

2026-05-21 RegionList selected-nested synthetic-factory update: owner-token
inference now walks inside already constrained direct constructors/factories
and constrains nested local aliases only when they are real multi-candidate
selected allocation aliases. This extends the RegionList node proof to
`new Node(selected)` where `selected` chooses between local
`Some(new T(...))`, `Option(new T(...))`, or
`Tuple2(new A(...), new B(...))` factory candidates. The restriction to
multi-candidate aliases is intentional: straight aliases of heap-looking
objects, such as `val tag = metadata`, are not retroactively region-placed.
Compiler negatives cover selected `Option(metadata)` nested in a RegionList
node, while the existing inline/block buffer/list/priority-queue metadata
negatives continue to reject. Runtime stats prove the executed nodes, selected
wrappers, and payload objects allocate in checked region memory
(`delta >= 17`).

2026-05-21 framework selected-nested synthetic-factory update: the same bounded
nested-alias helper is now explicitly proven for checked framework value
objects stored through `ObjectBuffer`/`RegionBuffer` appends and ordinary
checked priority-queue push/put APIs. Compiler positives cover
`new Node(selected)` where `selected` chooses between local `Some(new T(...))`,
`Option(new T(...))`, or `Tuple2(new A(...), new B(...))` candidates and the
owner token is supplied by the checked buffer or priority-queue call. Compiler
negatives reject selected nested `Option(metadata)`/`Tuple2(metadata,
metadata)` payloads through object buffers, region buffers, and priority
queues. Runtime allocation-stat proofs show the selected wrappers, payloads,
and containing value objects allocate in checked region memory for both buffers
and priority queues (`delta >= 17` each).

2026-05-21 reset-open-handle inferred-array update: direct `new Array[...]`
placement is now explicitly proven inside `resetOpenHandleInline` bodies for
captured object arrays and primitive arrays such as `Array[Int]^{region}`.
The negative test rejects unrooted heap metadata stores into an inferred region
array in that inline reset shape. `LogHubRetainedSessionMatrix` now applies the
proof to the inferred checked session/join paths by using ordinary `new Array`
for per-group checked arrays inside the inline reset callback; explicit checked
rows remain comparison controls for retained record construction and overall
source shape. 20k compressed Wikimedia clickstream-session and HDFS join smokes
matched heap/explicit/inferred/scoped checksum and output. The 1M x3 L2 gates
under `/Users/siyaoliu/rift/cache/loghub-wikimedia-inferred-array-1m-l2-20260521`
and `/Users/siyaoliu/rift/cache/loghub-join-inferred-array-1m-l2-20260521`
preserve matching checksum/output and identical explicit/inferred region-object
counts. The focused current-state L4 sweep under
`/Users/siyaoliu/rift/cache/profile-sweep-20260521-loghub-array-source`
matched checksum/output and shows the inferred Wikimedia path lower than
explicit checked in parser/input/hash (`477.00/s` versus `501.20/s`) and
query/session-loop (`80.80/s` versus `118.20/s`), with tiny region allocation
(`4.40/s`) and no callback-ref samples. This validates the affected inferred
source shape while preserving the conclusion that the remaining Wikimedia
overhead is parser/hash/session-loop work, not array allocation count.
A 2026-05-21 07:56 source audit found the inferred Wikimedia session path had
lagged this evidence and still used explicit `RiftAllocator.allocateOpenHandle`
for the per-group `entries`, `heads`, `tails`, and `counts` arrays. That path
now also uses ordinary `new Array` under the validated reset-open-handle owner.
Sandbox compile, native link, a fresh 20k compressed Wikimedia smoke, and a
fresh 1M x3 L2 Wikimedia gate all passed; the new 1M gate preserves checksum
`250002331971566003`, output `922453`, and identical explicit/inferred region
object counts (`1922465`), with inferred checked at `965.723 ms`.

2026-05-21 checked priority-queue direct-array update: the owner-token
array proof now also covers ordinary checked `RegionPriorityQueue`,
`RegionIndexedPriorityQueue`, `RegionLongIndexedPriorityQueue`, and the dense
and long-key lexicographic indexed priority-queue put overloads. A direct
`new Array[T^{region}]` pushed or put through the checked queue owner-token APIs
carries the queue owner through source-span inference. A later checked
`peek`/`pop`/`get` local is recorded as an owner-region value, and array
element-owner proof is preserved only when the recovered queue value type itself
captures the owner. Compiler positives cover pushing/putting and populating
`Array[T^{region}]^{region}` through ordinary, indexed, long-indexed, and
lexicographic indexed priority queues; negatives reject unrooted heap stores
through recovered `Array[Metadata]^{region}` for all queue families. Runtime
stats prove the ordinary pushed array and stored values allocate in checked
region memory (`delta >= 4`), separately prove the indexed plus long-indexed
arrays and stored values allocate in checked region memory (`delta >= 6`), and
separately prove the lexicographic indexed plus long-indexed arrays and stored
values allocate in checked region memory (`delta >= 6`). This is a framework
owner-token placement proof, not a claim about priority-queue elapsed time,
heap maintenance, or rank/table topology inference.

2026-05-21 closure array-store update: region-owned array stores now infer
closure objects as well as direct constructors and synthetic factories. Direct
inline closures and selected immutable local closure aliases stored into
`Array[Function1[Int, Int]^{region}]^{region}` inherit the array element's
checked owner. Runtime allocation stats prove the inline closure store path
allocates the inferred array plus closure object in checked region memory
(`delta >= 2`), and the selected-local path allocates the inferred array plus
both closure candidates in checked region memory (`delta >= 3`). The compiler
negative rejects a closure store that captures unrooted heap metadata. This is
 closure-object placement at an owner-proven array boundary; it does not claim
hidden owner capture, escaping closure summaries, or broader closure effect
inference.

2026-05-21 owner-token closure-container update: checked framework container
boundaries now reuse the same closure-owner proof path. Inline closure
arguments and selected immutable local closure aliases passed to checked
`ObjectBuffer`, `RegionBuffer`, and ordinary `RegionPriorityQueue` owner-token
APIs inherit the explicit checked owner supplied to the store operation.
Runtime allocation stats prove an ObjectBuffer inline closure value,
RegionBuffer selected closure candidates, and a priority-queue inline closure
value are materialized checked-region allocations. Compiler negatives reject
closures at those boundaries when they capture unrooted heap metadata. This is
 closure-object placement at explicit owner-token stores; it is not hidden owner
capture, broad closure/effect inference, or topology inference for every
framework operator.

2026-05-21 stream-rank closure update: checked stream-window rank/table-rank
owner-token APIs now have explicit closure-object proof. Inline closure values
passed to `putWindowRank`, selected immutable local closure aliases passed to
`putWindowRankInBucket`, and inline closure values passed to
`putTableRankInBucket` inherit the checked stream owner when the rank value
type is `Function1[...]^{stream}`. Runtime allocation stats use the same
setup-only differential used by the synthetic rank tests and prove the inserted
closure values add checked-region allocations (`delta >= 4`). Compiler
negatives reject direct and selected closure values that capture unrooted heap
metadata. This validates the helper expansion at the checked rank/table
framework boundary without claiming broad closure/effect inference or automatic
rank/table topology inference.

2026-05-20 Option/None update: the existing `Some(...)` factory placement now
has explicit compiler/runtime coverage for ordinary optional-result control
flow. `None` is accepted as the static empty option for
`Option[T^{r}]^{r}` without allocating region objects, and
`if flag then Some(new T(...)) else None` is validated both as a captured local
expected-type expression and as an explicit-region-parameter method result.
Runtime allocation stats prove the `Some` branch and payload are region
allocated while the `None` branch contributes no region objects. Compiler
negatives still reject `Some(unrootedHeapMetadata)` through the same
Some-or-None flow.

2026-05-20 polymorphic owner-token update: the owner-token method-argument
path now accepts a narrow polymorphic generic consumer shape,
`def consume[A](using r: ScopedRegion^)(cell: Cell[A^{r}]^{r})`. The concrete
bug was that polymorphic capture extraction could surface the local method
symbol as a candidate owner, so the constructor was classified as ambiguous
between `consume` and the actual `region` token and stayed on the heap. The
inference pass now filters method symbols out of allocation-owner candidates,
and NIR lowering recognizes type-applied constructors on the inferred direct
allocation path. Compiler negatives cover unrooted heap metadata and widened
`AnyRef` escape; runtime allocation stats prove the polymorphic `Cell` and
nested payload are region allocated.

2026-05-20 polymorphic method-summary update: explicit checked-region-parameter
methods can now carry a narrow polymorphic generic factory summary,
`def make[A](using r: ScopedRegion^)(value: A^{r}): Cell[A^{r}]^{r}`. The
inference phase records value parameters whose declared type is captured by a
checked owner parameter, and NIR accepts those recorded parameter symbols as
known region values when constructing returned region objects. A pre-erasure
call-boundary check rejects helper-returned heap objects passed to captured
method parameters, preserving the heap fallback/safety boundary for unproven
metadata. Runtime allocation stats prove both the returned `Cell` and its
payload are region allocated.

2026-05-20 forwarded polymorphic method-summary proof: the same explicit-owner
summary path is now directly covered for a true type-parameter wrapper,
`def wrap[A](using r: ScopedRegion^)(value: A^{r}): Cell[A^{r}]^{r} =
make[A](using r)(value)`, where `make` constructs the generic `Cell`. This did
not require a compiler implementation change: existing method-return summary
forwarding already preserves the captured owner and parameter proof through the
wrapper. Compiler negatives reject helper-returned heap metadata and widened
`AnyRef` escape, and runtime allocation stats prove the forwarded `Cell` plus
payload allocate in checked region memory.

2026-05-20 polymorphic `Option`/`Some` proof: the same explicit-owner
method-summary path is now directly covered for
`def make[A](using r: ScopedRegion^)(value: A^{r}): Option[A^{r}]^{r} =
Some(value)`. This slice did not require a compiler implementation change:
captured method parameters recorded for the previous generic `Cell` summary are
already sufficient for `Some(value)`. Compiler negatives reject helper-returned
heap metadata and widened `AnyRef` escape, and runtime allocation stats prove
the returned `Some` wrapper plus payload allocate in checked region memory.

2026-05-20 polymorphic `Tuple2` proof: the same path is now directly covered
for multiple captured method parameters and a common tuple factory:
`def make[A, B](using r: ScopedRegion^)(left: A^{r}, right: B^{r}):
Tuple2[A^{r}, B^{r}]^{r} = Tuple2(left, right)`. This also required no compiler
implementation change. Compiler negatives reject helper-returned heap metadata
and widened `AnyRef` escape, and runtime allocation stats prove the returned
`Tuple2` wrapper plus both payloads allocate in checked region memory.

2026-05-20 polymorphic `Option.apply` proof: the null-preserving factory path
is now directly covered for captured method parameters:
`def make[A](using r: ScopedRegion^)(value: A^{r}): Option[A^{r}]^{r} =
Option(value)`. This also required no compiler implementation change. Compiler
negatives reject helper-returned heap metadata and widened `AnyRef` escape, and
runtime allocation stats prove the non-null returned `Some` branch plus payload
allocate in checked region memory.

2026-05-20 branch/match polymorphic factory forwarding proof: true
type-parameter wrappers now forward polymorphic `Option.apply` and `Tuple2`
method summaries through simple `if` and `match` bodies when every path uses
the same explicit checked owner. This also required no compiler implementation
change: the existing forwarded method-return summary already handles
branch/match returned calls, and the captured method-parameter proof survives
the type-parameter wrapper. Compiler negatives reject helper-returned heap
metadata and widened `AnyRef` escape, and runtime allocation stats prove the
selected `Some`/`Tuple2` objects plus payloads allocate in checked region
memory.

2026-05-20 captured-owner closure-body proof: a narrow closure-body allocation
case is now implemented and extended to direct and immutable-local
method-returned closures plus direct and branch/match immutable-local
owner-token method arguments. When a region-owned closure explicitly captures
the same checked owner term named by its expected type, GenNIR records both the
runtime owner value and owner symbol and permits body-local ordinary `new` to
allocate through that captured owner. For
`def make(using r): Function1[Int, T^{r}]^{r} = (n: Int) => ...`, the returned
closure wrapper itself is also region allocated before return. For
`def make(using r): Function1[Int, T^{r}]^{r} = { val f = (n: Int) => ...; f }`,
the immutable local closure receives the same owner from the captured method
result. For `consume(using r)(f)` where `f` is an immutable local closure and
the parameter type is `Function1[Int, T^{r}]^{r}`, the local closure now
receives the supplied owner from the owner-token argument boundary; the same is
now covered for `consume(using r)(if flag then first else second)` and
`selector match` closure arguments when every selected local closure is
constrained by that owner. Direct inline closure arguments selected by `if` or
`match` are also tested for captured-owner body allocation. Captured local
expected types now use the same direct-returned-closure walk, so a local
branch/match-selected inline closure value can also place its explicitly
captured-owner body allocation. Runtime counters for these direct-inline native
shapes prove the selected body object is checked-region allocated; they do not
claim a materialized closure-wrapper allocation when the backend avoids one.
For materialized local and method-returned closure values, runtime allocation
stats prove both the closure object and the body-returned object allocate in
checked region memory, and generated LLVM confirms the direct method-returned
wrapper uses the region allocator instead of `GC_alloc_small`.
Compiler negatives reject unrooted heap metadata through the same
captured-owner body shape and reject an uncaptured `Function1` result that
captures an owner. This does not claim hidden owner capture,
lambda-signature rewriting, arbitrary escaping closure summaries, mutable
closure-local flow sensitivity, or broad closure effect inference.

## Current Implemented Capabilities

| Capability | Status | Evidence | Allowed claim |
|---|---:|---|---|
| Explicit captured direct `new` | Implemented | `val x: T^{region} = new T(...)` compiler/runtime tests | Direct ordinary construction can be lowered into checked regions when the expected type names the checked owner. |
| Immutable checked owner alias local `new` | Implemented owner-alias slice | `val owner = region; val x: T^{owner} = new T(...)` compiler/runtime allocation-stat tests | Immutable local aliases of checked owner handles can become owner constraints for ordinary `new`, reducing source plumbing and preparing later hidden-owner forwarding without changing the public API. |
| Method-returned local `new` through immutable checked owner alias | Implemented owner-alias canonicalization slice | `def make(using r): T^{r} = { val owner = r; val x: T^{owner} = new T(...); val y: T^{r} = x; y }` compiler/runtime allocation-stat tests | Owner aliases are canonicalized back to their underlying checked owner, so method-return summaries can use ergonomic local owner names without conflicting with result types that name the original region parameter. |
| Immutable local `new` constrained by captured val | Implemented | `val x = new T(...); val y: T^{region} = x` compiler/runtime tests | Local inference can use a captured expected type as an owner constraint. |
| Local block-shaped RHS final `new` constrained by captured val or annotation | Implemented | `val x = { val n = ...; new T(n) }; val y: T^{region} = x` and `val x: T^{region} = { ...; new T(...) }` compiler/runtime tests | Local inference and NIR lowering can place final direct allocations in non-empty local RHS blocks when the value is constrained by a checked owner. |
| Local branch/match-final `new` constrained by captured expected type | Implemented branch/match-final local slice | `val x: T^{region} = if p then new T(...) else new T(...)`, `selector match { case _ => new T(...) }`, and mixed `if p then new T(...) else allocateOpenHandle(region, new T(...))` compiler/runtime allocation-stat tests | Local captured expected types can now own direct construction sites returned from `if` and `match` shapes, and NIR lowering attaches the owner to those construction sites. This closes the mixed inferred/explicit runtime branch gap exposed by the inline reset probe while keeping unproven branches on the heap. |
| Selected immutable local direct-allocation alias | Implemented selected-local direct-allocation alias slice | `val first = new T(...); val second = new T(...); val selected = if flag then first else second; selected` through explicit checked-owner method returns, owner-token method arguments, `RiftRegion.prependRegionList(region, list, selected)`, `RiftRegion.append(region, objectBuffer, selected)`, `region.append(regionBuffer, selected)`, `RegionPriorityQueue.push`, `RegionIndexedPriorityQueue.put`, and `RegionLongIndexedPriorityQueue.put`, with compiler positives/negatives and runtime allocation-stat proof | Immutable local aliases that select between already-known direct allocation locals preserve the original allocation symbols, so later method-return, owner-token, or framework owner constraints can region-place each candidate object. The selected alias itself is also marked as a proven region value once every candidate has the same owner, so framework store checks accept it. Unrooted heap metadata in either candidate allocation is rejected, and mutable selected aliases remain fallback/rejected. |
| Selected immutable local synthetic-factory alias | Implemented proof over existing selected-local direct-region-construct slice | Explicit checked-owner methods returning selected local `Some(new T(...))`, `Option(new T(...))`, `Tuple2(new A(...), new B(...))`, and `Left(new A(...))`/`Right(new B(...))` factory values; owner-token method arguments consuming selected local `Some(new T(...))`, `Option(new T(...))`, `Tuple2(new A(...), new B(...))`, and `Either` factory values; region-owned array stores consuming selected local `Some(new T(...))`, `Option(new T(...))`, `Tuple2(new A(...), new B(...))`, and `Either` factory values; checked `ObjectBuffer`/`RegionBuffer` appends, ordinary plus lexicographic checked priority-queue push/put calls, and checked stream-window rank/table-rank `put` calls consuming the earlier selected factory aliases after relaxing their element bounds to captured `Object^`; compiler positives/negatives and runtime allocation-stat proofs `scopedRegionInfersMethodReturnedSelectedLocalSyntheticFactoryPlacement`, `scopedRegionInfersMethodArgumentSelectedLocalSyntheticFactoryPlacement`, `scopedRegionInfersMethodArgumentSelectedLocalEitherFactoryPlacement`, `scopedRegionInfersSelectedArrayStoreSyntheticFactoryPlacement`, `scopedRegionInfersSelectedArrayStoreEitherFactoryPlacement`, `scopedRegionInfersBufferSelectedLocalSyntheticFactoryPlacement`, `scopedRegionInfersPriorityQueueSelectedLocalSyntheticFactoryPlacement`, `scopedRegionInfersLexicographicPriorityQueueSelectedLocalSyntheticFactoryPlacement`, and `streamingRegionInfersWindowRankSelectedLocalSyntheticFactoryPlacement` | The selected-local alias machinery also preserves local symbols whose RHS is a recognized region construct factory, not only plain `new`. Later method-result, owner-token argument, array element-owner, checked buffer, ordinary checked priority-queue, checked lexicographic priority-queue, or checked stream-window rank/table-rank owner constraints can region-place each selected `Some`/`Option.apply`/`Tuple2`/`Either` candidate wrapper and nested direct payload object. Unrooted heap metadata in any selected factory remains rejected, broader `Option`/`Either` container flow still stays out of scope, and checked framework containers still require values captured by an explicit, context-proven owner token. |
| Immutable local `new` constrained by captured assignment | Implemented | `var y: T^{region}; val x = new T(...); y = x` compiler tests | Local inference can use captured assignment targets as owner constraints. |
| Local block-shaped RHS final `new` constrained by captured assignment | Implemented | `var y: T^{region}; y = { val n = ...; new T(n) }` compiler/runtime tests | Captured assignment constraints also place final direct allocations in non-empty local RHS blocks. |
| Immutable local `new` constrained by `RegionList` prepend | Implemented | checked `RegionList` compiler/runtime tests | Local inference can use an explicit checked linked-list owner. |
| Local block-shaped RHS final `new` constrained by `RegionList` prepend | Implemented | `val x = { ...; new T(...) }; prependRegionList(region, list, x)` compiler/runtime tests | Framework owner-token inference can place computed record construction blocks before checked list append. |
| Inline direct/block-final `new` constrained by `RegionList` prepend | Implemented | `prependRegionList(region, list, new T(...))` and `prependRegionList(region, list, { val n = ...; new T(n) })` compiler/runtime tests | Owner-token framework calls can now place direct or inline block-final argument construction into the checked region without requiring a temporary local. |
| Branch/match RegionList nodes with nested synthetic factories | Implemented captured-node/safety slice | `regionListInfersBranchMatchSyntheticFactoryPlacement` and `regionListInfersEitherFactoryPlacement` compiler positives; `inferredBranchRegionListOptionApplyCannotStoreUnrootedHeapMetadata`, `inferredMatchRegionListTupleCannotStoreUnrootedHeapMetadata`, and `inferredBranchRegionListEitherCannotStoreUnrootedHeapMetadata` negatives; runtime allocation-stat proofs `scopedRegionInfersRegionListBranchMatchSyntheticFactoryPlacement` and `scopedRegionInfersRegionListEitherFactoryPlacement` | Checked `RegionList` can now store captured node element types whose branch/match direct constructors contain region-owned `Some`/`Option.apply`/`Tuple2`/`Either` wrappers and nested payloads. Runtime stats prove the `Either` node/wrapper/payload path allocates in checked region memory (`delta >= 10`). The recursive NIR check rejects unrooted heap payloads hidden inside those nested factories. |
| Selected local synthetic factories nested in RegionList nodes | Implemented selected-nested RegionList slice | `regionListInfersSelectedNestedSyntheticFactoryPlacement` and `regionListInfersEitherFactoryPlacement` compiler positives; `inferredSelectedNestedRegionListOptionCannotStoreUnrootedHeapMetadata` and `inferredSelectedNestedRegionListEitherCannotStoreUnrootedHeapMetadata` negatives; runtime allocation-stat proofs `scopedRegionInfersRegionListSelectedNestedSyntheticFactoryPlacement` and `scopedRegionInfersRegionListEitherFactoryPlacement`; existing inline/block metadata negatives for arrays, buffers, lists, and priority queues remain passing | Checked `RegionList` node constructors can consume selected local `Some`/`Option.apply`/`Tuple2`/`Either` factory aliases in fields when the selected alias has multiple proven allocation candidates and `prependRegionList` supplies the owner. Simple heap aliases are not inferred. |
| Selected local synthetic factories nested in checked framework value objects | Implemented selected-nested framework slice | `buffersInferSelectedNestedSyntheticFactoryPlacement` and `regionPriorityQueuesInferSelectedNestedSyntheticFactoryPlacement` compiler positives; `inferredSelectedNestedObjectBufferOptionCannotStoreUnrootedHeapMetadata`, `inferredSelectedNestedRegionBufferTuple2CannotStoreUnrootedHeapMetadata`, and `inferredSelectedNestedRegionPriorityQueueTuple2CannotStoreUnrootedHeapMetadata` negatives; runtime allocation-stat proofs `scopedRegionInfersBufferSelectedNestedSyntheticFactoryPlacement` and `scopedRegionInfersPriorityQueueSelectedNestedSyntheticFactoryPlacement` | Checked buffer appends and ordinary checked priority-queue push/put calls can now place containing value objects whose fields consume selected local `Some`/`Option.apply`/`Tuple2` factory aliases, using only the explicit framework owner token. Simple heap aliases and unrooted metadata payloads remain rejected. |
| Direct `new` returned from explicit-region-parameter method | Implemented first slice | `def make(using r: ScopedRegion^): T^{r} = new T(...)` compiler/runtime tests | Simple local methods can allocate returned objects in a checked region when the method body has a runtime region handle parameter. |
| Inline direct `new` passed to a method argument captured by an in-scope checked owner | Implemented first call-site argument slice | `def consume(x: T^{region}): Int = ...; consume(new T(...))` compiler/runtime allocation-stat tests | The compiler can lower a direct method argument allocation into the checked region when the parameter type directly names an in-scope checked owner. |
| Inline direct `new` passed to owner-token method argument | Implemented owner-token call-site slice | `def consume(using r: ScopedRegion^)(x: T^{r}): Int = ...; consume(using region)(new T(...))` compiler/runtime allocation-stat tests | The compiler can lower a direct method argument allocation into the checked region when the callee parameter type names an explicit owner parameter and the fully applied call supplies the actual checked owner argument. This is a narrow call-site substitution slice, not full method/effect inference. |
| Inline closure object passed to owner-token method argument | Implemented owner-token synthetic call-site slice | `def consume(using r: ScopedRegion^)(f: Function1[Int, Int]^{r}): Int = ...; consume(using region)((n: Int) => n + 40)` compiler/runtime allocation-stat tests | The compiler can lower an inline closure object argument into the checked region when the callee parameter type names an explicit owner parameter and the fully applied call supplies the actual checked owner argument. This places the closure object, not arbitrary closure-body allocations. |
| Captured-owner closure-body local `new` | Implemented narrow closure-body slice | `val make: Function1[Int, Box^{region}]^{region} = (value: Int) => { val owner = region; val box: Box^{owner} = new Box(value); box }` compiler positive/negative tests and runtime allocation-stat test | A region-owned closure may explicitly capture the same checked owner term and use it to place a body-local returned allocation. This is a proven captured-owner body case, not hidden owner capture, escaping closure inference, or general closure effect summaries. |
| Local branch/match inline captured-owner closure body | Implemented direct-returned-closure local expected-type slice | `val make: Function1[Int, Box^{region}]^{region} = if flag then ((value: Int) => { val owner = region; new Box(value) }) else ...` compiler positives/negatives plus runtime allocation-stat test | Captured local expected types now visit branch/match direct inline closures and can place explicitly captured-owner body-local returned allocations in the checked region. Runtime stats prove the selected body object is region allocated; wrapper allocation is not claimed for this direct-inline native shape. |
| Owner-token branch/match inline captured-owner closure body | Implemented proof on existing direct-returned-closure argument path | `consume(using region)(if flag then ((value: Int) => { val owner = region; new Box(value) }) else ...)` and match equivalent compiler positives/negatives plus runtime allocation-stat tests | Direct inline closures selected by simple branch or match arguments can carry the supplied owner into explicitly captured body-local returned allocations. Runtime stats prove the selected body object is region allocated; the direct-inline native shape may not materialize a wrapper, so wrapper allocation is not claimed for this row. |
| Method-returned captured-owner closure wrapper and body `new` | Implemented direct-return closure slice | `def make(using r: ScopedRegion^): Function1[Int, Box^{r}]^{r} = (value: Int) => { val owner = r; val box: Box^{owner} = new Box(value); box }` compiler positive/negative tests, runtime allocation-stat test expecting closure wrapper plus body object, and LLVM sanity check for the wrapper allocator | Direct closures returned from explicit checked-owner methods can be allocated in that checked region when the method result type captures the owner and the closure captures the same owner term for its body allocation. Uncaptured `Function1` results and unrooted heap metadata remain rejected. This is a direct-return summary slice, not arbitrary escaping closure/effect inference. |
| Closure-body returned named-local captured-owner closure wrapper and nested body `new` | Implemented typed and untyped named-local closure-body slice | `val outer: Function1[Int, Function1[Int, Box^{region}]^{region}]^{region} = base => { val owner = region; val inner = value => { val box: Box^{owner} = new Box(base + value); box }; inner }` plus the explicitly typed local variant; compiler positives/negatives, runtime allocation-stat tests expecting outer wrapper plus named local inner wrapper plus nested body object, and LLVM sanity check for the untyped inner wrapper allocator | A region-owned closure body can return a named local closure and place that local wrapper plus its explicitly captured-owner body allocation into the checked region when the enclosing closure result type names an explicit checked owner, a unique runtime owner term is recoverable, and the local closure body captures that owner. Hidden owner capture, type-only owner recovery without a runtime handle, mutable local closure flow, escaping returned closures, and broad allocation-site closure fallback remain heap fallback/rejected. |
| Method-returned immutable local captured-owner closure wrapper and body `new` | Implemented returned-local closure slice | `def make(using r: ScopedRegion^): Function1[Int, Box^{r}]^{r} = { val makeBox = (value: Int) => { val owner = r; val box: Box^{owner} = new Box(value); box }; makeBox }` compiler positive/negative tests and runtime allocation-stat test expecting closure wrapper plus body object | Immutable local closure values returned from explicit checked-owner methods can inherit the captured method result owner even when the local closure val has no captured type ascription. The closure-body `new` is placed only when the closure explicitly captures the same owner term; mutable local closure flow and arbitrary escaping closure summaries remain heap fallback/rejected. |
| Owner-token method-argument immutable local captured-owner closure wrapper and body `new` | Implemented owner-token returned-local closure argument slice | `def consume(using r: ScopedRegion^)(makeBox: Function1[Int, Box^{r}]^{r}): Int = ...; val makeBox = (value: Int) => { val owner = region; val box: Box^{owner} = new Box(value); box }; consume(using region)(makeBox)` compiler positive/negative tests and runtime allocation-stat test expecting closure wrapper plus body object | Immutable local closure values passed to explicit checked owner-token method arguments can inherit the supplied checked owner even when the local closure val has no captured type ascription. The closure-body `new` is placed only when the closure explicitly captures the same owner term; unrooted heap metadata is rejected and mutable/arbitrary escaping closure summaries remain fallback/rejected. |
| Owner-token branch/match immutable local captured-owner closure argument | Implemented owner-token branch/match-local closure argument slice | `consume(using region)(if flag then first else second)` and `consume(using region)(selector match { ... })` where selected immutable local closures have body-local `new` values captured by `region`; compiler positive/negative tests and runtime allocation-stat tests expecting closure wrappers plus the selected body object | Branch- or match-selected immutable local closure values passed to explicit checked owner-token method arguments can inherit the supplied checked owner when the method parameter type names that owner. Each selected closure remains checked independently; unrooted heap metadata in any selected closure body is rejected, and broader mutable/arbitrary escaping closure summaries remain fallback/rejected. |
| Owner-token selected immutable local closure alias | Implemented selected-local closure alias slice | `val selected = if flag then first else second; consume(using region)(selected)` where `first` and `second` are immutable local closures with body-local `new` values captured by `region`; compiler positives/negatives and runtime allocation-stat test expecting selected closure wrappers plus the selected body object | Immutable local aliases that select between already-known immutable closure vals preserve the original closure allocation symbols, so owner-token argument inference can constrain each selected closure through the supplied checked owner. Unrooted heap metadata in either selected closure body is rejected. Mutable selected aliases and broader closure effect summaries remain fallback/rejected. |
| Method-returned selected immutable local closure alias | Implemented selected-local closure alias method-return slice | `def make(flag)(using r): Function1[Int, Box^{r}]^{r} = { val first = ...; val second = ...; val selected = if flag then first else second; selected }` compiler positives/negatives and runtime allocation-stat test expecting returned selected closure wrappers plus the selected body object | Explicit checked-owner methods can return an immutable alias selected between already-known immutable closure vals while preserving each original closure allocation symbol. The returned selected closure wrappers and explicitly captured-owner body allocation are checked-region allocated; unrooted heap metadata in either selected closure body is rejected. Mutable selected aliases and broader closure effect summaries remain fallback/rejected. |
| Forwarded captured-owner closure-body summaries | Implemented forwarding proof on existing summary machinery | `def wrap(using r): Function1[Int, Box^{r}]^{r} = make(using r)`, `if flag then make(using r) else make(using r)`, and `selector match { ... }` when `make` returns a closure whose body explicitly captures `r`, plus `val selected = if flag then first else second; val forwarded = selected; forwarded` method-returned selected local closures; compiler positives/negatives and runtime allocation-stat tests expecting wrapper/body or selected-wrapper/body objects | The existing forwarded-method and local-closure alias summaries preserve the captured owner through direct, branch, match, and immutable local alias hops. Runtime stats prove checked-region allocation for the materialized closure wrapper/body objects. This did not require a production compiler change and does not imply hidden owner capture, mutable selected closure flow, or broad escaping closure effect summaries. |
| Closure-body direct synthetic factory returns | Implemented direct closure-body factory-lowering slice | `val make: Function1[Int, Option[Box^{region}]^{region}]^{region} = value => { val owner = region; Some(new Box(value)) }` and `Function1[Int, Tuple2[Box^{region}, Box^{region}]^{region}]^{region} = value => Tuple2(new Box(value), new Box(1))`; compiler positives/negatives and runtime allocation-stat tests `scopedRegionInfersClosureBodyDirectOptionFactoryAllocationWithCapturedOwnerTerm` and `scopedRegionInfersClosureBodyDirectTupleFactoryAllocationWithCapturedOwnerTerm` | `GenNIR` now prepares direct returned region constructs for methods whose closure-body owner was already inferred, so direct closure-body `Some`/`Tuple2` factories and nested direct payloads receive the captured runtime owner before lowering. The first runtime attempt observed only the closure wrapper (`delta == 1`), proving this was a real lowering gap; the fixed runtime tests prove closure wrapper plus `Some` plus payload (`delta >= 3`) and closure wrapper plus `Tuple2` plus two payloads (`delta >= 4`). Unrooted heap metadata behind `Some(metadata)` or `Tuple2(metadata, metadata)` remains rejected. |
| Closure-body selected-local synthetic factory returns | Implemented selected-local closure-body factory-lowering slice | `val first = Some(new Box(value)); val second = Some(new Box(value + 1)); val selected = if value >= 0 then first else second; selected`, plus the equivalent selected `Tuple2(new A(...), new B(...))` shape; compiler positives/negatives and runtime allocation-stat tests `scopedRegionInfersClosureBodySelectedOptionFactoryAllocationWithCapturedOwnerTerm` and `scopedRegionInfersClosureBodySelectedTupleFactoryAllocationWithCapturedOwnerTerm` | `RiftRegionInference` records local direct region-construct factory apps when selected aliases constrain their allocation sites, and `GenNIR` resolves returned immutable local aliases in proven closure-body methods back to those direct factory RHSs before lowering. The first runtime attempt observed only the closure wrapper (`delta == 1`), proving selected local factory candidates still fell back to heap; the fixed runtime tests prove closure wrapper plus two `Some` candidates and two payloads (`delta >= 5`) and closure wrapper plus two `Tuple2` candidates and four payloads (`delta >= 7`). Selected `Some(metadata)` and `Tuple2(metadata, metadata)` with unrooted heap metadata remain rejected. |
| Closure-body optional `Option.apply` and Some/None returns | Implemented optional factory proof on closure-body factory lowering | `value => Option(new Box(value))` and `include => if include then Some(new Box(40)) else None`; compiler positives/negatives and runtime allocation-stat tests `scopedRegionInfersClosureBodyOptionApplyFactoryAllocationWithCapturedOwnerTerm` and `scopedRegionInfersClosureBodySomeOrNoneAllocationWithCapturedOwnerTerm` | Closure bodies now have explicit proof for null-preserving `Option.apply` and static-empty `None` semantics under the captured runtime owner. Runtime stats prove the non-null `Option.apply` branch allocates the `Some` wrapper and payload in checked region memory with the closure wrapper (`delta >= 3`), and the optional branch proof observes the closure wrapper plus `Some`/payload while `None` allocates no region object (`delta >= 3`). `Option(metadata)` and `if include then Some(metadata) else None` with unrooted heap metadata remain rejected. |
| Closure-body checked-region callee summaries with Option/Some factory returns | Implemented common library-wrapper callee proof | `def build(value)(using r): Option[Box^{r}]^{r} = Some(new Box(value)); def make(using r): Function1[Int, Option[Box^{r}]^{r}]^{r} = value => { val owner = r; build(value)(using owner) }`; compiler positive/negative and runtime allocation-stat test `scopedRegionInfersClosureBodyOptionMethodSummaryAllocationWithCapturedOwnerTerm` expecting closure wrapper plus `Some` plus payload | A region-owned closure body can call an explicit checked-region callee whose result is a recognized `Some(new T(...))` factory, and the callee summary preserves the captured runtime owner through the library-created wrapper and nested payload. `Some(metadata)` with unrooted heap metadata is rejected. This is a bounded `Option`/`Some` effect-summary proof, not broad library inference, boxed-key/primitive box placement, hidden/type-only owner recovery, or escaping closure inference. |
| Closure-body checked-region callee summaries with `Option.apply`/`Tuple2`/`Either` and selected factory returns | Implemented factory callee-summary source-span bridge | `def build(value)(using r): Option[Box^{r}]^{r} = Option(new Box(value))`, `def build(value)(using r): Tuple2[Box^{r}, Box^{r}]^{r} = Tuple2(new Box(value), new Box(1))`, `def build(value)(using r): Either[Box^{r}, Box^{r}]^{r} = Left(new Box(value))`, and selected immutable local aliases of these shapes called from a captured-owner closure body; compiler positives/negatives and runtime allocation-stat tests `scopedRegionInfersClosureBodyOptionApplyMethodSummaryAllocationWithCapturedOwnerTerm`, `scopedRegionInfersClosureBodyTupleMethodSummaryAllocationWithCapturedOwnerTerm`, `scopedRegionInfersClosureBodyEitherMethodSummaryAllocationWithCapturedOwnerTerm`, `scopedRegionInfersClosureBodySelectedOptionApplyMethodSummaryAllocationWithCapturedOwnerTerm`, `scopedRegionInfersClosureBodySelectedTupleMethodSummaryAllocationWithCapturedOwnerTerm`, and `scopedRegionInfersClosureBodySelectedEitherMethodSummaryAllocationWithCapturedOwnerTerm` | Method-local returned selected factory candidates now bridge their direct factory source spans with the inferred checked owner, so `GenNIR` can region-place callee-created `Option.apply`/`Tuple2`/`Either` wrappers and nested payloads before a region-owned closure body returns them. Runtime stats prove direct `Option.apply` (`delta >= 3`), direct `Tuple2` (`delta >= 4`), direct `Either` (`delta >= 3`), selected `Option.apply` candidates (`delta >= 5`), selected `Tuple2` candidates (`delta >= 7`), and selected `Either` candidates (`delta >= 5`) allocate in checked region memory. Direct and selected unrooted metadata variants remain rejected. This is bounded explicit-owner method/effect-summary coverage, not virtual dispatch, broad library inference, primitive boxed-key placement, hidden/type-only owner recovery, or topology inference. |
| Closure-body wrapper-returned inline closure through `Option.apply` | Implemented direct wrapper/closure-body proof | `val make: Function1[Int, Option[Function1[Int, Box^{region}]^{region}]^{region}]^{region} = base => { val owner = region; Option((value: Int) => { val box: Box^{owner} = new Box(base + value); box }) }`; compiler positive/negative and runtime allocation-stat test `scopedRegionInfersClosureBodyOptionApplyInlineClosureAllocationWithCapturedOwnerTerm` | A captured-owner closure body can return a library-created optional wrapper containing an inline closure whose own body allocation uses the same runtime owner. Runtime stats prove the outer closure wrapper, non-null `Option.apply` `Some` wrapper, inner closure wrapper, and inner body object allocate in checked region memory (`delta >= 4`). Unrooted heap metadata captured by the nested closure body remains rejected. Exact `Some(inlineClosure)` and selected wrapper aliases are claimed by the following rows. |
| Closure-body wrapper-returned inline closure through exact `Some` | Implemented exact-`Some` inline-wrapper proof | Same captured-owner inline-closure shape as the `Option.apply` row, but the closure body returns `Some((value: Int) => ...)` directly; compiler positive/negative and runtime allocation-stat test `scopedRegionInfersClosureBodySomeInlineClosureAllocationWithCapturedOwnerTerm` | The direct wrapper/closure-body proof also covers the exact `Some.apply` factory path. Runtime stats prove the outer closure wrapper, exact `Some` wrapper, inner closure wrapper, and nested body object allocate in checked region memory (`delta >= 4`). Unrooted heap metadata captured by the nested closure body remains rejected. |
| Closure-body wrapper-returned selected local closure through `Option.apply` | Implemented selected-wrapper closure/effect proof | `val make: Function1[Boolean, Option[Function1[Int, Box^{region}]^{region}]^{region}]^{region} = flag => { val owner = region; val first = value => { val box: Box^{owner} = new Box(value + 40); box }; val second = value => { val box: Box^{owner} = new Box(value + 41); box }; val selected = if flag then first else second; Option(selected) }`; compiler positive/negative and runtime allocation-stat test `scopedRegionInfersClosureBodyOptionApplySelectedClosureAllocationWithCapturedOwnerTerm` | A captured-owner closure body can return a library-created optional wrapper containing an immutable selected local closure alias when each candidate closure explicitly captures the same runtime checked owner. `RiftRegionInference` recovers the selected closure alias inside the wrapper, and `GenNIR` prepares local closure values/aliases before wrapper constructor safety checks. Runtime stats prove the outer closure wrapper, non-null `Option.apply` `Some` wrapper, both selected closure candidates, and selected body object allocate in checked region memory (`delta >= 5`). Unrooted heap metadata captured by either selected closure body remains rejected. |
| Closure-body wrapper-returned selected local closure through exact `Some` | Implemented exact-`Some` selected-wrapper proof | Same captured-owner selected-closure shape as the `Option.apply` row, but the closure body returns `Some(selected)` directly; compiler positive/negative and runtime allocation-stat test `scopedRegionInfersClosureBodySomeSelectedClosureAllocationWithCapturedOwnerTerm` | The selected-wrapper closure/effect proof also covers the exact `Some.apply` factory path. Runtime stats prove the outer closure wrapper, exact `Some` wrapper, both selected closure candidates, and selected body object allocate in checked region memory (`delta >= 5`). Unrooted heap metadata captured by either selected closure body remains rejected. |
| Closure-body wrapper-returned inline or selected local closure through `Either` | Implemented `Either` wrapped-closure proof | `val make: Function1[Int, Either[Function1[Int, Box^{region}]^{region}, Function1[Int, Box^{region}]^{region}]^{region}]^{region} = base => Left((value: Int) => { val owner = region; val box: Box^{owner} = new Box(...); box })` and selected local closure variant; compiler positives/negatives and runtime allocation-stat tests `scopedRegionInfersClosureBodyEitherInlineClosureBodyAllocation` and `scopedRegionInfersClosureBodyEitherSelectedClosureBodyAllocation` | The wrapper-returned closure/effect proof now covers `Left`/`Right` wrappers containing inline closures or selected local closure aliases. Runtime stats prove the outer closure wrapper, `Either` case wrapper, wrapped closure value, and nested body object allocate in checked region memory for inline closures (`delta >= 4`) and selected closures (`delta >= 5`). Unrooted heap metadata captured by nested closure bodies remains rejected. |
| Method-returned generic wrapper containing inline or selected local closure | Implemented simple wrapper method-summary proof | `def make(using r): Wrapper[Box^{r}]^{r} = { val owner = r; new Wrapper[Box^{r}]((value: Int) => { val box: Box^{owner} = new Box(value); box }) }` and selected local closure variant; compiler positives/negative and runtime allocation-stat tests `scopedRegionInfersMethodReturnedWrapperInlineClosureBodyAllocation` and `scopedRegionInfersMethodReturnedWrapperSelectedClosureBodyAllocation` | Explicit checked-region methods can return a small generic wrapper record whose field is an inline closure or immutable selected local closure alias, when the wrapper result owner and nested closure body owner resolve to the same concrete runtime owner. Runtime stats prove wrapper plus inline closure plus body object allocate in checked region memory (`delta >= 3`) and wrapper plus selected closure candidates plus selected body object allocate in checked region memory (`delta >= 4`). Unrooted heap metadata captured by the nested closure body remains rejected. |
| Forwarded method-returned generic wrapper containing inline or selected local closure | Implemented simple forwarded-wrapper method-summary proof | `def forward(using r): Wrapper[Box^{r}]^{r} = makeWrapper(using r)` and `if flag then makeWrapper(true)(using r) else makeWrapper(false)(using r)` where `makeWrapper` returns `Wrapper(closure)`; compiler positives/negative and runtime allocation-stat tests `scopedRegionInfersForwardedMethodReturnedWrapperInlineClosureBodyAllocation` and `scopedRegionInfersBranchForwardedMethodReturnedWrapperSelectedClosureBodyAllocation` | Direct and branch-forwarding checked-region methods can preserve the method-return summary for a generic wrapper record containing an inline or selected local closure, when every forwarded path has the same checked owner. Runtime stats prove the forwarded wrapper plus inline closure plus nested body object allocate in checked region memory (`delta >= 3`) and the branch-forwarded wrapper plus selected closure candidates plus selected body object allocate in checked region memory (`delta >= 4`). Unrooted heap metadata captured by the nested closure body remains rejected through the forwarded wrapper. |
| Inline `Some(new T(...))` passed to owner-token method argument | Implemented owner-token synthetic factory call-site slice | `def consume(using r: ScopedRegion^)(option: Option[T^{r}]^{r}): Int = ...; consume(using region)(Some(new T(...)))` compiler/runtime allocation-stat tests | The compiler can lower the inline `Some` factory object and nested direct payload construction into the checked region when the callee parameter type names an explicit owner parameter and the fully applied call supplies the actual checked owner argument. |
| Inline `Option.apply(new T(...))` passed to owner-token method argument | Implemented owner-token synthetic factory call-site slice | `def consume(using r: ScopedRegion^)(option: Option[T^{r}]^{r}): Int = ...; consume(using region)(Option(new T(...)))` compiler/runtime allocation-stat tests; unrooted-metadata negative | The same owner-token substitution path now covers null-preserving `Option.apply`: proven non-null direct payloads allocate the `Some` branch and nested value in the checked region, while unsafe heap metadata remains rejected. |
| Inline `Left(new T(...))`/`Right(new T(...))` passed to owner-token method argument | Implemented owner-token synthetic factory call-site slice | `def consume(using r: ScopedRegion^)(either: Either[T^{r}, T^{r}]^{r}): Int = ...; consume(using region)(Left(new T(...)))` compiler/runtime allocation-stat tests; unrooted-metadata negative | The same owner-token substitution path now covers direct `Either` case factories. Proven direct payloads allocate the selected `Left`/`Right` wrapper and nested value in the checked region, while unsafe heap metadata remains rejected. |
| Inline `Tuple2(new A(...), new B(...))` passed to owner-token method argument | Implemented owner-token synthetic factory call-site slice | `def consume(using r: ScopedRegion^)(pair: Tuple2[A^{r}, B^{r}]^{r}): Int = ...; consume(using region)(Tuple2(new A(...), new B(...)))` and tuple-literal compiler/runtime allocation-stat tests | The compiler can lower the inline `Tuple2` factory object and nested direct payload construction into the checked region when the callee parameter type names an explicit owner parameter and the fully applied call supplies the actual checked owner argument. Normal tuple syntax uses the same validated path. |
| Inline `TupleN(...)` factory placement, arities 2-22 | Implemented general tuple-factory slice, validated with Tuple3 | `Tuple3(new A(...), new B(...), new C(...))` compiler positives for region-owned array stores, owner-token method arguments, and explicit-region method returns; matching unrooted-heap-metadata negatives; runtime allocation-stat test proving a `Tuple3` plus three nested leaves are region allocated | The former `Tuple2`-only factory recognition now accepts `scala.TupleN.apply` for arities 2 through 22, while preserving the same proof boundary: one checked expected owner is required, nested direct values inherit that owner, and unproven tuple factories stay on the heap. Primitive/boxed tuple fields remain future boxed-key/object-boxing work. |
| Inline generic `Cell(new T(...))` passed to owner-token method argument | Implemented owner-token generic call-site slice | `def consume(using r: ScopedRegion^)(cell: Cell[T^{r}]^{r}): Int = ...; consume(using region)(new Cell(new T(...)))` compiler/runtime allocation-stat tests | The compiler can lower a narrow generic object argument plus its nested direct payload into the checked region when the callee parameter type names an explicit owner parameter and the fully applied call supplies the actual checked owner argument. This is not broad polymorphic effect inference. |
| Inline generic `Cell(new T(...))` passed to polymorphic owner-token method argument | Implemented narrow polymorphic owner-token call-site slice | `def consume[A](using r: ScopedRegion^)(cell: Cell[A^{r}]^{r}): Cell[A^{r}]^{r} = cell; consume[T](using region)(new Cell(new T(...)))` compiler positives/negatives and runtime allocation-stat test | The owner-token substitution path now handles one local polymorphic consumer shape when the fully applied call supplies the concrete type argument and checked owner token. Method symbols are excluded from allocation-owner candidates, so the only accepted owner is the actual checked token. This is still a narrow call-site slice, not full polymorphic region/effect inference. |
| Explicitly region-typed selected local generic `Cell` passed to polymorphic owner-token method argument | Implemented selected-local polymorphic owner-token proof | `val first: Cell[T^{region}]^{region} = new Cell[T^{region}](new T(...)); val second = ...; val selected = if flag then first else second; consume[T](using region)(selected)` compiler positive/boundary negative and runtime allocation-stat test | The owner-token substitution path can consume an immutable selected local generic `Cell` value when each candidate already carries the checked owner in its type. Runtime stats prove both candidate cells and nested payloads are region allocated. Untyped selected generic aliases remain rejected because capture checking loses the owner before post-capture inference can recover it safely. |
| Polymorphic method-returned generic `Cell` factory | Implemented narrow polymorphic method-summary slice | `def make[A](using r: ScopedRegion^)(value: A^{r}): Cell[A^{r}]^{r} = new Cell[A^{r}](value); make[T](using region)(new T(...))` compiler positives/negatives and runtime allocation-stat test | Explicit checked-region-parameter methods can now summarize one polymorphic generic factory shape and treat captured method parameters as proven region values inside the method body. Helper-returned heap arguments remain rejected at the call boundary. This is still a narrow explicit-owner method summary, not full polymorphic effect inference. |
| Forwarded polymorphic method-returned generic `Cell` factory | Implemented proof on existing polymorphic method-summary forwarding path | `def wrap[A](using r: ScopedRegion^)(value: A^{r}): Cell[A^{r}]^{r} = make[A](using r)(value)` compiler positives/negatives and runtime allocation-stat test | Explicit checked-region-parameter method summaries can forward a true type-parameter generic `Cell` result through a simple wrapper while preserving the captured owner and region-local payload proof. Helper-returned heap arguments and widened heap escape remain rejected. This is still narrow explicit-owner forwarding, not broad polymorphic effect inference. |
| Polymorphic method-returned `Option`/`Some` factory | Implemented proof on existing polymorphic method-summary path | `def make[A](using r: ScopedRegion^)(value: A^{r}): Option[A^{r}]^{r} = Some(value); make[T](using region)(new T(...))` compiler positives/negatives and runtime allocation-stat test | Explicit checked-region-parameter methods can now summarize this common polymorphic optional-result factory shape and treat the captured value parameter as a proven region value for the `Some` wrapper. Helper-returned heap arguments and widened heap/static escape remain rejected. This is still a narrow explicit-owner summary, not broad `Option` container/effect inference. |
| Polymorphic method-returned `Option.apply` factory | Implemented proof on existing polymorphic method-summary path | `def make[A](using r: ScopedRegion^)(value: A^{r}): Option[A^{r}]^{r} = Option(value); make[T](using region)(new T(...))` compiler positives/negatives and runtime allocation-stat test | Explicit checked-region-parameter methods can summarize the null-preserving `Option.apply` factory when the non-null value argument is already proven region-local. Helper-returned heap arguments and widened heap/static escape remain rejected. This is still a narrow explicit-owner summary, not broad `Option` container/effect inference. |
| Polymorphic method-returned `Tuple2` factory | Implemented proof on existing polymorphic method-summary path | `def make[A, B](using r: ScopedRegion^)(left: A^{r}, right: B^{r}): Tuple2[A^{r}, B^{r}]^{r} = Tuple2(left, right); make[L, R](using region)(new L(...), new R(...))` compiler positives/negatives and runtime allocation-stat test | Explicit checked-region-parameter methods can summarize this common polymorphic tuple-result factory shape and treat both captured value parameters as proven region values for the `Tuple2` wrapper. Helper-returned heap arguments and widened heap/static escape remain rejected. This is still a narrow explicit-owner summary, not broad polymorphic tuple/container effect inference. |
| Branch/match forwarded polymorphic `Option.apply` factory | Implemented proof on existing polymorphic method-summary forwarding path | `def branch[A](flag)(using r)(value: A^{r}): Option[A^{r}]^{r} = if flag then make[A](using r)(value) else make[A](using r)(value)` and match equivalent compiler positives/negatives plus runtime allocation-stat test | True type-parameter wrappers can forward the null-preserving `Option.apply` summary through simple branch/match control flow when every path uses the same explicit checked owner. Runtime stats prove the selected `Some` branches and payloads are region allocated. This is still narrow explicit-owner forwarding, not broad polymorphic container inference. |
| Branch/match forwarded polymorphic `Tuple2` factory | Implemented proof on existing polymorphic method-summary forwarding path | `def branch[A, B](flag)(using r)(left: A^{r}, right: B^{r}): Tuple2[A^{r}, B^{r}]^{r} = if flag then make[A, B](using r)(left, right) else make[A, B](using r)(left, right)` and match equivalent compiler positives/negatives plus runtime allocation-stat test | True type-parameter wrappers can forward polymorphic tuple-result summaries through simple branch/match control flow when every path uses the same explicit checked owner. Runtime stats prove the selected tuple wrappers and payloads are region allocated. This is still narrow explicit-owner forwarding, not broad polymorphic tuple/container effect inference. |
| Block-final direct `new` returned from explicit-region-parameter method | Implemented first slice | `def make(using r: ScopedRegion^): T^{r} = { val n = ...; new T(n) }` compiler/runtime tests | Simple method summaries can place a final direct allocation even when the method body has preceding local computation. |
| Forwarded region-returning method result | Implemented first slice | `def wrap(using r: ScopedRegion^): T^{r} = make(using r)` compiler/runtime tests | Simple wrapper methods can preserve inferred region-return summaries when both methods use explicit checked region parameters. |
| Forwarded local alias of region-returning method result | Implemented first slice | `def wrap(using r: ScopedRegion^): T^{r} = { val x = make(using r); x }` compiler/runtime tests | Simple wrapper methods can preserve inferred region-return summaries through one immutable method-local alias initialized from an already inferred region-returning call. |
| Forwarded branch/match region-returning method result | Implemented first slice | `if p then make(using r) else make(using r)` and `selector match { case _ => make(using r) }` compiler/runtime tests | Simple wrapper methods can preserve inferred region-return summaries through branch and match expressions when all paths share the same explicit checked owner. |
| Method-returned captured `Some(...)` factory allocation | Implemented first method/factory slice | `def make(using r): Some[T^{r}]^{r} = Some(new T(...))` and `def make(using r): Option[T^{r}]^{r} = Some(new T(...))` compiler/runtime tests | Method summaries can now carry a proven region-owned `Some` factory result, including the nested direct value construction, through either exact `Some` or widened `Option` result types. |
| Method-returned `None` and `Some(...)`/`None` optional result flow | Implemented method/factory optional-flow slice | `def make(using r): Option[T^{r}]^{r} = None` and `def make(flag)(using r): Option[T^{r}]^{r} = if flag then Some(new T(...)) else None` compiler/runtime allocation-stat tests | Explicit checked region-parameter methods can return the static empty option or a branch-selected `Some`/`None` optional result, with the `Some` branch region allocated and the `None` branch allocation-free. |
| Method-returned captured `Option.apply(...)` allocation | Implemented null-preserving method/factory slice | `def make(using r): Option[T^{r}]^{r} = Option(new T(...))` compiler positive and unrooted-metadata negative tests; runtime allocation-stat test proving the method-returned `Some` branch and nested payload are region allocated | Method summaries can now carry a proven region-owned `Option.apply` result: the non-null path lowers to a checked-region `Some` plus nested direct payload, while null remains the static `None` value. Primitive/boxed paths remain rejected until the boxing allocation can be placed safely. |
| Method-returned local `Option = Some(...)` factory allocation | Implemented method/factory returned-local slice | `def make(using r): Option[T^{r}]^{r} = { val option: Option[T^{r}]^{r} = Some(new T(...)); option }` compiler/runtime tests | Method summaries can now carry a named local `Option` factory result, not only a direct returned factory call. |
| Branch/match forwarded method-returned `Option = Some(...)` factory allocation | Implemented method/factory control-flow forwarding slice | `def wrap(flag)(using r): Option[T^{r}]^{r} = if flag then make(using r) else make(using r)` and match equivalent compiler/runtime allocation-stat tests | Method summaries now propagate proven region-owned `Some` factory results through simple branch and match wrappers, when every path forwards a value owned by the same explicit checked region parameter. Runtime stats prove the selected `Some` objects and nested values remain region allocated. |
| Method-returned captured `Tuple2(...)` factory allocation | Implemented first method/factory slice | `def make(using r): Tuple2[A^{r}, B^{r}]^{r} = Tuple2(new A(...), new B(...))` and tuple literal equivalent compiler/runtime tests | Method summaries can now carry a proven region-owned `Tuple2` factory result and nested direct field construction through explicit `Tuple2(...)` or normal tuple syntax. |
| Method-returned local `Tuple2(...)` factory allocation | Implemented method/factory returned-local slice | `def make(using r): Tuple2[A^{r}, B^{r}]^{r} = { val pair: Tuple2[A^{r}, B^{r}]^{r} = Tuple2(new A(...), new B(...)); pair }` compiler/runtime tests | Method summaries can now carry a named local tuple factory result, not only a direct returned `Tuple2(...)` or tuple literal. |
| Branch/match forwarded method-returned `Tuple2(...)` factory allocation | Implemented method/factory control-flow forwarding slice | `def wrap(flag)(using r): Tuple2[A^{r}, B^{r}]^{r} = if flag then make(using r) else make(using r)` and match equivalent compiler/runtime allocation-stat tests | Method summaries now propagate proven region-owned `Tuple2` factory results through simple branch and match wrappers, when every path forwards a value owned by the same explicit checked region parameter. Runtime stats prove the selected tuple objects and nested values remain region allocated. |
| Local immutable `new` returned from explicit-region-parameter method | Implemented first slice | `def make(using r: ScopedRegion^): T^{r} = { val x = new T(...); x }` and `OpenStreamingRegion` compiler/runtime tests | Simple method summaries can now constrain a method-local direct allocation through the returned local value, not only a bare returned `new`; this is validated for scoped regions and direct epochs. |
| Local block-shaped RHS final `new` returned from explicit-region-parameter method | Implemented first slice | `def make(using r: ScopedRegion^): T^{r} = { val x = { val n = ...; new T(n) }; x }` compiler/runtime tests | Method summaries can constrain a returned method-local value whose construction block does local setup before the final direct allocation. |
| Branch-returned direct `new` from explicit-region-parameter method | Implemented first slice | `def make(using r: ScopedRegion^): T^{r} = if p then new T(...) else new T(...)` compiler/runtime tests | The method-summary slice can place direct allocations in simple returned branch positions when both branches share the same explicit checked owner. |
| Branch-returned local `new` from explicit-region-parameter method | Implemented first slice | `def make(using r: ScopedRegion^): T^{r} = if p then { val x = new T(...); x } else { val y = new T(...); y }` compiler/runtime tests | The method-summary slice can place immutable locals returned from simple branch positions when both branch locals share the same explicit checked owner. |
| Branch/match-returned local block-shaped RHS final `new` from explicit-region-parameter method | Implemented first slice | `if p then { val x = { ...; new T(...) }; x } else ...` and match equivalent compiler/runtime tests | The method-summary slice can place construction-block locals returned from branch or match positions when every returned local shares the same explicit checked owner. |
| Match-returned direct/local `new` from explicit-region-parameter method | Implemented first slice | `selector match { case 0 => new T(...); case _ => new T(...) }` and returned-local match compiler/runtime tests | The method-summary slice can place direct or immutable-local allocations in simple returned match cases when all cases share the same explicit checked owner. |
| Immutable local `new` constrained by checked `ObjectBuffer`/`RegionBuffer` append | Implemented first slice | `RiftRegion.append(region, buffer, x)` and `region.append(buffer, x)` compiler/runtime tests | Owner-token framework append boundaries can infer data-path records into the checked region when the appended local is immutable. |
| Local block-shaped RHS final `new` constrained by checked `ObjectBuffer`/`RegionBuffer` append | Implemented first slice | `val x = { ...; new T(...) }; RiftRegion.append(region, buffer, x)` compiler/runtime tests for fixed and growable checked buffers | Owner-token buffer append boundaries can place computed record construction blocks into the checked region. |
| Inline direct/block-final `new` constrained by checked `ObjectBuffer`/`RegionBuffer` append | Implemented first slice | `RiftRegion.append(region, buffer, new T(...))`, `region.append(buffer, new T(...))`, and inline `{ val n = ...; new T(n) }` compiler/runtime tests for fixed and growable checked buffers | Owner-token buffer append boundaries can place direct or inline block-final argument construction into the checked region while preserving heap fallback for unproven calls. |
| Immutable local `new` constrained by checked priority-queue push/put | Implemented first slice | `RegionPriorityQueue`, `RegionIndexedPriorityQueue`, and `RegionLongIndexedPriorityQueue` compiler/runtime tests | Owner-token priority-queue boundaries can infer ordinary ranking candidates into the checked region when the candidate local is immutable and passed to explicit `push`/`put`. |
| Inline direct/block-final `new` constrained by checked priority-queue push/put | Implemented first slice | `region.push(queue, new T(...), priority)`, `region.push(queue, { val n = ...; new T(n) }, priority)`, `RiftRegion.push(...)`, and indexed/long-indexed `put` compiler/runtime tests | Scoped checked priority-queue boundaries can now place direct or inline block-final argument construction into the checked region without a temporary local. |
| Inline or selected closure object constrained by checked owner-token containers | Implemented closure container-owner slice | `RiftRegion.append(region, objectBuffer, (n: Int) => n + 40)`, `region.append(regionBuffer, selectedClosure)`, and `region.push(priorityQueue, (n: Int) => n + 40, priority)` compiler/runtime allocation-stat tests | Checked ObjectBuffer, RegionBuffer, and ordinary RegionPriorityQueue owner-token boundaries can now place closure objects in the supplied checked region when the value type carries that owner. Selected immutable local closure aliases preserve their closure allocation symbols. Unrooted heap captures remain rejected, and broader closure/effect inference remains out of scope. |
| Selected synthetic factory aliases constrained by checked stream-window rank/table-rank APIs | Implemented narrow framework-owner slice | `putWindowRank`, `putWindowRankInBucket`, and `putTableRankInBucket` compiler positives/negatives for selected local `Some(new T(...))`, `Option(new T(...))`, and `Tuple2(new A(...), new B(...))`; runtime allocation-stat proof `streamingRegionInfersWindowRankSelectedLocalSyntheticFactoryPlacement` | Checked stream rank/table APIs can now consume selected synthetic aliases whose wrappers and nested payloads are all proven owned by the same checked stream token. The inference path allows `StreamingRegion` only as this framework owner-token context, not as a general allocation owner, so direct heap objects and unrooted metadata remain rejected. |
| Inline or selected closure object constrained by checked stream-window rank/table-rank APIs | Implemented narrow framework-owner closure slice | `putWindowRank(stream, indexed, key, (n: Int) => n + 40, priority)`, `putWindowRankInBucket(stream, longIndexed, bucket, key, selectedClosure, priority)`, and `putTableRankInBucket(stream, table, bucket, key, (n: Int) => n + 1, priority)` compiler/runtime allocation-stat tests | Checked stream rank/table APIs can now consume closure values whose wrappers are proven owned by the checked stream token. Runtime differential proof shows the inserted closure values are region allocations. Unrooted heap captures remain rejected, and this does not infer arbitrary rank/table topology or closure effects. |
| Branch/match-local direct `new` aliases constrained by checked stream-window rank/table-rank APIs | Implemented narrow branch/match-local framework-owner slice | `putWindowRank`, `putWindowRankInBucket`, and `putTableRankInBucket` compiler positives for `if flag then first else second` and match expressions where all selected values are immutable local direct allocations; unrooted-metadata negatives; runtime allocation-stat proof `streamingRegionInfersWindowRankBranchMatchLocalNewPlacement` | Checked stream rank/table APIs can now consume non-direct branch or match expressions when every returned value is a proven local direct allocation owned by the checked stream token. Direct local heap-looking values still reject. |
| Direct arrays constrained by checked stream-window rank/table-rank APIs | Implemented narrow framework-owner direct-array slice | `putWindowRank`, `putWindowRankInBucket`, and `putTableRankInBucket` compiler positives for direct `new Array[T^{stream}]` values, unannotated `peekWindowRank`/`peekTableRank` result locals, and inline element stores; compiler negatives for `Array[Metadata]^{stream}` stores; runtime allocation-stat proof `streamingRegionInfersWindowRankInlineArrayPlacement` | Checked stream rank/table APIs can consume direct arrays owned by the checked stream token. Later element stores are inferred when the result local has an explicit captured array type or when the same immutable rank/table local has a prior checked `put` whose value type proves the array element captures the stream owner. Unrooted heap metadata remains rejected, and this does not infer arbitrary rank/table topology. |
| Direct branch/match synthetic factories constrained by owner-token boundaries | Implemented narrow owner-token branch/match factory slice | Explicit owner-token method-argument compiler positives/negatives and runtime proof `scopedRegionInfersMethodArgumentBranchMatchSyntheticFactoryPlacement`, plus focused `Either` owner-token tests; checked `ObjectBuffer`/`RegionBuffer` compiler positives/negatives and runtime proof `scopedRegionInfersBufferBranchMatchSyntheticFactoryPlacement`; ordinary checked priority-queue compiler positives/negatives and runtime proof `scopedRegionInfersPriorityQueueBranchMatchSyntheticFactoryPlacement`; dense/long lexicographic checked priority-queue compiler positives; checked stream-window rank/table-rank compiler positives/negatives and runtime proof `streamingRegionInfersWindowRankBranchMatchSyntheticFactoryPlacement` | Direct `if`/`match` expressions returning `Some(new T(...))`, `Option(new T(...))`, `Tuple2(new A(...), new B(...))`, or owner-token `Left(new A(...))`/`Right(new B(...))` can now be region placed when the owner-token boundary supplies one checked owner and every returned factory app is proven safe. Unrooted heap metadata remains rejected, including through checked buffer and priority-queue stores, and this is not broad Option/Either/container, priority-queue, or rank/table topology inference. |
| Selected or branch/match `Either` factories constrained by checked `ObjectBuffer`/`RegionBuffer` append | Implemented buffer/synthetic owner-token slice | `buffersInferEitherFactoryPlacement` compiler positive, `inferredSelectedObjectBufferEitherCannotStoreUnrootedHeapMetadata`, `inferredBranchObjectBufferEitherCannotStoreUnrootedHeapMetadata`, `inferredSelectedRegionBufferEitherCannotStoreUnrootedHeapMetadata`, and `inferredMatchRegionBufferEitherCannotStoreUnrootedHeapMetadata` negatives, plus runtime allocation-stat proof `scopedRegionInfersBufferEitherFactoryPlacement` | Checked buffer append boundaries now place selected local and direct branch/match `Left`/`Right` wrappers plus nested payloads when the buffer value type is captured by the checked framework owner token. Runtime stats prove the selected and branch/match buffer `Either` values allocate in checked region memory (`delta >= 12`). Unrooted heap metadata remains rejected, and this is not arbitrary collection or erased-container inference. |
| Selected or branch/match `Either` factories constrained by ordinary checked priority queues | Implemented priority-queue/synthetic owner-token slice | `regionPriorityQueuesInferEitherFactoryPlacement` compiler positive, `inferredSelectedRegionPriorityQueueEitherCannotStoreUnrootedHeapMetadata`, `inferredBranchRegionIndexedPriorityQueueEitherCannotStoreUnrootedHeapMetadata`, and `inferredSelectedRegionLongIndexedPriorityQueueEitherCannotStoreUnrootedHeapMetadata` negatives, plus runtime allocation-stat proof `scopedRegionInfersPriorityQueueEitherFactoryPlacement` | Plain, indexed, and long-indexed checked priority queues now place selected local and direct branch/match `Left`/`Right` wrappers plus nested payloads when the queue value type is captured by the checked queue owner token. Runtime stats prove these queue `Either` values allocate in checked region memory (`delta >= 8`). Unrooted heap metadata remains rejected, and this is not arbitrary priority-queue, lexicographic queue, or erased-container inference. |
| Selected or branch/match `Either` factories constrained by lexicographic checked priority queues | Implemented lexicographic priority-queue/synthetic owner-token slice | `regionLexicographicPriorityQueuesInferEitherFactoryPlacement` compiler positive, `inferredSelectedRegionIndexedPriorityQueueLexicographicEitherCannotStoreUnrootedHeapMetadata`, and `inferredMatchRegionLongIndexedPriorityQueueLexicographicEitherCannotStoreUnrootedHeapMetadata` negatives, plus runtime allocation-stat proof `scopedRegionInfersLexicographicPriorityQueueEitherFactoryPlacement` | Indexed and long-indexed lexicographic checked priority queues now place selected local and direct branch/match `Left`/`Right` wrappers plus nested payloads when the queue value type is captured by the checked queue owner token. Runtime stats prove these queue `Either` values allocate in checked region memory (`delta >= 12`). Unrooted heap metadata remains rejected, and this is not arbitrary priority-queue or erased-container inference. |
| Selected or branch/match `Either` factories constrained by checked stream-rank/table-rank APIs | Implemented stream-rank/synthetic owner-token slice | `streamWindowRanksInferEitherFactoryPlacement` compiler positive, `streamWindowIndexedRankSelectedEitherCannotStoreUnrootedHeapMetadata` and `streamWindowTableRankMatchEitherCannotStoreUnrootedHeapMetadata` negatives, plus runtime allocation-stat proof `streamingRegionInfersWindowRankEitherFactoryPlacement` | Checked `putWindowRank`, `putWindowRankInBucket`, and `putTableRankInBucket` boundaries now place selected local and direct branch/match `Left`/`Right` wrappers plus nested payloads when the rank/table value type is captured by the checked stream owner token. Runtime stats prove these stream-rank/table-rank `Either` values allocate in checked region memory (`delta >= 8`). Unrooted heap metadata remains rejected, and this is not arbitrary stream topology, erased-container, or primitive-box inference. |
| Branch/match direct constructors and synthetic factories stored into region-owned arrays | Implemented narrow array element-owner branch/match slice | `items(i) = if flag then new T(...) else new T(...)`, match-returned `Option(new T(...))`, branch-returned `Tuple2(new A(...), new B(...))`, and direct `Either` case factories compiler positives; branch-returned `Some(metadata)` and `Either(metadata)` compiler negatives; runtime allocation-stat proof `scopedRegionInfersBranchMatchArrayStoreFactoryPlacement` plus focused selected `Either` array-store proof | Region-owned array stores now propagate the unique array element owner to every direct constructor or recognized factory returned by an `if`/`match`, while still requiring the array element type to carry the checked owner. Unrooted heap metadata remains rejected, and this is not broad array/container flow through arbitrary APIs. |
| Local `new` constrained by page/window/transaction/epoch-buffer child-region owner | Implemented child-owner slice | `pageTokenAppendRegionFor`, `pageTokenMapFilterRegionFor`, `pageTokenCountByKeyRegionFor`, `epochBufferRegionFor`, `transactionRegionFor`, and `chunkAppendRegionFor` compiler/runtime tests with `val event: Event^{region} = new Event(...)`; checked append-window chunk-token source-use smoke | A local child-region token returned by selected checked page/window/bucket/epoch-buffer/transaction helpers can own ordinary `new` placement for independently expiring bucket-local, epoch-local, or transaction-local records. Parent `StreamingRegion` values remain excluded. |
| Local `new` constrained by epoch-fold child-region owner | Implemented epoch-fold child-owner slice | `epochFoldRegionFor` compiler positive/negative and runtime allocation-stat test with `val event: Event^{region} = new Event(...)`; Dataflow aggregate epoch-fold source-use smoke | The epoch-fold helper now participates in selected child-region owner inference, so fold-bucket records can use ordinary `new` under the returned child region and widen to the parent stream owner for `putEpochFold`. Parent `StreamingRegion` remains excluded from generic allocation-owner inference, and unrooted metadata remains rejected. |
| Local `new` constrained by open operator-owned child-region helper | Implemented open-child-owner slice | `pageTokenAppendOpenRegionFor`, `pageTokenMapFilterOpenRegionFor`, `pageTokenCountByKeyOpenRegionFor`, and `epochBufferOpenRegionFor` compiler/runtime allocation-stat tests with `val event: Event^{region} = new Event(...)` | Operator-owned open child-region helpers can now use ordinary `new` instead of explicit `allocOpen(new ...)` when the local active owner is statically known. This reduces source-level token plumbing while keeping public low-level APIs defensive. |
| Local `new` constrained by page-token Rift open-handle helper | Implemented internal page-token active-handle slice | `pageTokenAppendRiftOpenHandleFor` compiler/runtime allocation-stat tests with `val event: Event^{region} = new Event(...)` | The internal Rift-backed page-token append helper can own ordinary `new` placement through a raw `RiftOpenStreamingHandle`, reducing explicit allocation plumbing in operator-owned page-token paths. This remains an internal/provenance helper, not a public API expansion. |
| Internal inline reset-open-handle probe and session split | Implemented narrow internal probe plus one accepted framework-path use | `resetOpenHandleInline` compiler/runtime allocation-stat tests in `scala.scalanative.memory`; `LogHubRetainedSessionMatrix` `checked-rift-inferred` session split and state-local callback cleanup | Simple and non-inline-wrapper open-handle reset bodies can be inlined while preserving checked allocation, including region-owned arrays and region-local element stores, provided the final raw reset is delegated to a non-inline helper. The Wikimedia session inferred path now uses this shape through a sandbox-only bridge. The first split-only 1M L2 row improved to `1867.761 ms`; the accepted state-local follow-up is `1927.010 ms` in a fresh comparable pass and removes sampled boxed-ref top-frame parameters. Mixed runtime allocation branches inside this shape are now supported by the branch/match-final local inference slice; enclosing `inline def` wrappers remain rejected/unsupported, so broader LogHub/join callback inlining still needs compiler ownership preservation. |
| ReML-shaped checked stream inferred source mode | Implemented representative source-placement gate | `ReMLRegionMatrix checked-region-stream-inferred` smokes for `msort`, `msort-r`, `fft`, `ratio`, `logic`, `ray`, and `tsp`, compared against heap and explicit checked stream | ReML-shaped allocation workloads now exercise ordinary `new` placement through an `OpenStreamingRegion` epoch instead of requiring explicit `RiftRegion.alloc` at every data-path record site. Checksums match heap/explicit controls, and inferred region-object counts match explicit checked stream on the focused smoke. This validates source placement for representative ReML-style programs without claiming full ReML/MLKit inference or changing the presentation comparison. |
| Captured `Some(...)` factory allocation | Implemented first common Scala allocation shape | `val option: Some[T^{region}]^{region} = Some(value)` and `val option: Option[T^{region}]^{region} = Some(value)` compiler tests; runtime allocation-stat tests with `identityHashCode` forcing allocation | The compiler can lower a proven region-owned `scala.Some.apply` factory call into a checked-region `Some` allocation through exact `Some` or widened `Option` expected types. Unproven `Some(...)` calls remain normal heap factory calls. |
| `None` and local `Some(...)`/`None` optional result flow | Implemented static-empty plus local optional-flow slice | `val option: Option[T^{region}]^{region} = None` and `val option: Option[T^{region}]^{region} = if flag then Some(new T(...)) else None` compiler/runtime allocation-stat tests | `None` can satisfy a region-owned `Option` expected type without allocating a region object, while the `Some` branch of a local optional result is still region allocated when the expected type names one checked owner. |
| Captured `Option.apply(...)` allocation | Implemented null-preserving common Scala allocation shape | `val option: Option[T^{region}]^{region} = Option(new T(...))`, `Option(regionValue)`, and `Option(null)` compiler positives; `Option(metadata)` and `Option(40)` compiler negatives; runtime allocation-stat tests | Proven region-owned `scala.Option.apply` now lowers to a runtime null test: null returns static `None` with zero region allocations, non-null region-safe values allocate the `Some` object and any nested direct payload in the checked region. Heap fallback remains the default for unproven `Option.apply` calls. |
| Captured `Tuple2(...)`/tuple-literal allocation | Implemented common Scala allocation shape | `val pair: Tuple2[A^{region}, B^{region}]^{region} = Tuple2(a, b)` and `(a, b)` compiler tests; runtime allocation-stat tests with `identityHashCode` forcing allocation | The compiler can lower a proven region-owned `scala.Tuple2.apply`/tuple-literal allocation into a checked-region `Tuple2` object when both fields are safe region references. Primitive/boxed tuple fields remain future boxed-key/object-boxing work. |
| Captured `TupleN(...)` allocation, arities 2-22 | Implemented general tuple-factory shape, validated with Tuple3 | `Tuple3` compiler positives/negatives and runtime allocation-stat test with `identityHashCode` forcing materialization | The factory recognizer is no longer hard-coded to `Tuple2`; proven region-owned tuple factories up to `Tuple22` can use the checked-region allocation path, with Tuple3 added as the first higher-arity proof point. |
| Captured local generic object allocation | Implemented narrow ReML-style polymorphic slice | `val cell: Cell[T^{region}]^{region} = new Cell[T^{region}](value)` compiler tests; runtime allocation-stat test with `identityHashCode` forcing allocation | The compiler can lower a local generic object into a checked region when the expected type captures both the generic container and region-owned value argument. This is local expected-type placement, not broad polymorphic region/effect inference for escaping generic containers. |
| Method-returned captured generic object allocation | Implemented narrow method/polymorphic slice | `def make(using r): Cell[T^{r}]^{r} = new Cell[T^{r}](value)` compiler tests; runtime allocation-stat test with `identityHashCode` forcing allocation | Explicit checked region-parameter methods can now return a proven region-owned generic object, including its region-owned value argument. This extends the first method-summary slice without claiming broad polymorphic effect inference. |
| Method-returned local generic object allocation | Implemented narrow method/polymorphic returned-local slice | `def make(using r): Cell[T^{r}]^{r} = { val cell: Cell[T^{r}]^{r} = new Cell[T^{r}](value); cell }` compiler/runtime tests | Explicit checked region-parameter methods can return a named local generic object while preserving checked-region placement and runtime allocation proof. |
| Branch/match forwarded method-returned generic object allocation | Implemented narrow method/polymorphic control-flow forwarding slice | `def wrap(flag)(using r): Cell[T^{r}]^{r} = if flag then make(using r) else make(using r)` and match equivalent compiler/runtime allocation-stat tests | Explicit checked region-parameter method summaries can now propagate proven region-owned generic object results through simple branch and match wrappers when every path forwards a value owned by the same checked region parameter. Runtime stats prove the selected `Cell` and contained region-owned value are region allocated. |
| Captured region-owned array allocation | Implemented first array slice | `val items: Array[T^{region}]^{region} = new Array[T^{region}](n)` compiler/runtime allocation-stat tests with `identityHashCode` forcing materialization | The compiler can lower a proven region-owned array allocation into the checked region when the expected array type names the same checked owner. Region-object stores are allowed, unrooted heap-object stores are rejected, and heap/static escape is rejected. |
| Owner-token method-argument region-owned array allocation | Implemented owner-token array argument slice | `def consume(using r)(items: Array[T^{r}]^{r}); consume(using region)(new Array[T^{region}](n))` compiler/runtime allocation-stat tests, plus an unrooted heap-store negative | Direct `new Array` values passed to explicit checked owner-token method arguments now carry the supplied owner through GenNIR even after Scala lowers the source array construction to the runtime array factory. Runtime stats prove the array and inline stored region-local values allocate in checked region memory; unrooted heap stores through the array parameter remain rejected. |
| Checked `ObjectBuffer`/`RegionBuffer` direct region-owned array allocation and get-store propagation | Implemented framework owner-token array slice | `RiftRegion.append(region, objectBuffer, new Array[T^{region}](n)); val items = RiftRegion.get(region, objectBuffer, 0); items(0) = new T(...)`, plus `region.append(regionBuffer, new Array[T^{region}](n)); val items = region.get(regionBuffer, 0); items(0) = new T(...)` compiler/runtime allocation-stat tests and unrooted heap-store negatives through recovered arrays | Direct `new Array` values appended to checked `ObjectBuffer` and `RegionBuffer` now carry the supplied framework owner through the same source-span bridge as owner-token method arguments. `RiftRegionInference` also records checked-buffer `get` locals as owner-region values and preserves array element-owner proof when the recovered array element type is region captured. Runtime stats prove the appended arrays and inline stored region-local values allocate in checked region memory; `Array[Metadata]^{region}` remains region-owned but its unrooted heap element stores are rejected. |
| Checked priority-queue direct region-owned array allocation and peek/get-store propagation | Implemented framework owner-token array slice | `region.push(queue, new Array[T^{region}](n), priority); val items = region.peek(queue); items(0) = new T(...)`, plus indexed/long-indexed and lexicographic indexed/long-indexed `put` followed by `get` or `peek`, compiler/runtime allocation-stat tests, and unrooted heap-store negatives through recovered arrays | Direct `new Array` values pushed or put into ordinary, indexed, long-indexed, and lexicographic checked priority queues now carry the supplied framework owner through the same source-span bridge. `RiftRegionInference` records checked priority-queue `peek`/`pop`/`get` locals as owner-region values and preserves array element-owner proof only when the queue value type is region captured. Runtime stats prove the pushed/put arrays and inline stored region-local values allocate in checked region memory; `Array[Metadata]^{region}` remains region-owned but unrooted heap element stores are rejected. |
| Reset-open-handle direct region-owned array allocation | Implemented inline reset array proof and LogHub/Wikimedia source use | `resetOpenHandleInlineInfersDirectRegionArrayPlacement` compiler/runtime allocation-stat proof; `resetOpenHandleInlineInferredArrayRejectsUnrootedHeapMetadata` negative; `LogHubRetainedSessionMatrix` inferred session/join per-group arrays use ordinary `new Array` with explicit checked rows left as controls; 20k smokes and 1M x3 L2 Wikimedia/HDFS gates matched checksum/output | Direct region-owned arrays, including primitive arrays such as `Array[Int]^{region}`, can be written as ordinary `new Array` inside validated inline reset-open-handle bodies. Runtime stats prove arrays and contained records allocate in checked region memory, while unrooted heap stores remain rejected. The L2 gates preserve identical explicit/inferred region-object counts, so this is source-placement evidence rather than a region-object-count reduction. |
| Inline direct `new` stored into a region-owned array element | Implemented array element-owner slice | `items(0) = new T(...)` where `items: Array[T^{region}]^{region}` compiler/runtime allocation-stat tests | A fresh inline array-store value can inherit the array element's checked owner when the element type itself captures the region. This removes the previous need to name the stored object first for this narrow, owner-proven array pattern. |
| Inline `Some(new T(...))` stored into a region-owned array element | Implemented array/synthetic element-owner slice | `items(0) = Some(new T(...))` where `items: Array[Option[T^{region}]^{region}]^{region}` compiler/runtime allocation-stat tests | A proven region-owned array element can now place the stored `Some` factory object and nested direct value into the checked region. This is a narrow synthetic allocation store, not general Option/container flow inference. |
| Inline `Option.apply(new T(...))` stored into a region-owned array element | Implemented array/synthetic element-owner slice | `items(0) = Option(new T(...))` where `items: Array[Option[T^{region}]^{region}]^{region}` compiler/runtime allocation-stat tests; unrooted-metadata negative | A proven region-owned array element can now place the non-null `Option.apply` `Some` branch and nested direct value into the checked region. This reuses the same array element-owner proof and keeps broader Option/container flow inference out of scope. |
| Inline `Tuple2(new A(...), new B(...))` stored into a region-owned array element | Implemented array/synthetic element-owner slice | `items(0) = Tuple2(new A(...), new B(...))` where `items: Array[Tuple2[A^{region}, B^{region}]^{region}]^{region}` compiler/runtime allocation-stat tests | A proven region-owned array element can now place the stored `Tuple2` factory object and both nested direct values into the checked region. This extends the array element-owner path to a second common Scala factory shape without claiming general collection or tuple flow inference. |
| Inline or selected `Either` factory stored into a region-owned array element | Implemented array/synthetic element-owner slice | `items(0) = Left(new T(...))` and selected local `Either[T^{region}, T^{region}]^{region}` aliases where `items: Array[Either[T^{region}, T^{region}]^{region}]^{region}` compiler/runtime allocation-stat tests; unrooted-metadata negatives | A proven region-owned array element can now place stored `Left`/`Right` case wrappers and nested direct values into the checked region. The selected-local proof places both selected candidates before the store. This extends the array element-owner path to another common Scala wrapper without claiming general array/container flow through arbitrary APIs. |
| Inline or selected closure object stored into a region-owned array element | Implemented closure array-store slice | `items(0) = (n: Int) => n + 40` and `items(0) = selected` where `items: Array[Function1[Int, Int]^{region}]^{region}` compiler/runtime allocation-stat tests | Closure objects can inherit a region-owned array element's checked owner when the element type itself captures the region. Selected immutable local closure aliases preserve their closure allocation symbols. Unrooted heap captures remain rejected, and this does not imply escaping closure/effect inference. |
| Method-returned region-owned array allocation | Implemented method/array slice | `def make(using r): Array[T^{r}]^{r} = { val items: Array[T^{r}]^{r} = new Array[T^{r}](n); ...; items }` compiler/runtime allocation-stat tests | Explicit checked region-parameter methods can return a named region-owned array while preserving placement for the array and named region-local element objects. This extends the method-summary path to arrays without claiming broad array effect inference. |
| Forwarded method-returned region-owned array allocation | Implemented method/array forwarding slice | `def wrap(using r): Array[T^{r}]^{r} = make(using r)` and `{ val items = make(using r); items }` compiler/runtime allocation-stat tests | Method-return summaries now propagate through direct and one-local-alias wrapper methods for region-owned arrays. Runtime stats prove the forwarded array and element objects remain region allocated. |
| Branch/match forwarded method-returned region-owned array allocation | Implemented method/array control-flow forwarding slice | `def wrap(flag)(using r): Array[T^{r}]^{r} = if flag then make(using r) else make(using r)` and `selector match { case _ => make(using r) }` compiler/runtime allocation-stat tests | Method-return summaries now propagate through simple branch and match wrappers for region-owned arrays when every path forwards a result owned by the same explicit checked region parameter. Runtime stats now cover both the branch and match wrappers, proving the selected array and named region-local elements remain region allocated. |
| Direct nested construction arguments in region-owned constructors/factories | Implemented first nested slice | `new Wrapper(new T(...))`, `Some(new T(...))`, and `Tuple2(new A(...), new B(...))` compiler/runtime tests | When an allocation is already proven region-owned, direct nested construction arguments can be attached to the same checked region. Helper-returned heap objects remain rejected. |
| Active open-handle inferred `new` | Implemented first internal active-handle slice | `RiftRegion.epochOpenHandle` and `RiftRegion.resetOpenHandle` compiler/runtime tests | Operator-owned active-handle paths can use ordinary `new` while still allocating through the monomorphic Rift open handle when capture/separation proof gives a unique active owner. This is internal lowering, not a public API expansion. |
| Capture-free local closure object constrained by function capture type | Implemented synthetic-closure slice | `val f: Function1[Int, Int]^{region} = (n: Int) => n + 40` compiler/runtime allocation-stat tests | The compiler/NIR lowering recognizes function capture syntax such as `Int ->{region} Int`, resolves the local checked owner, and allocates a materialized capture-free closure object in the checked region. |
| Method-returned capture-free closure object | Implemented method/closure summary slice | `def make(using r): Function1[Int, Int]^{r} = { val f: Function1[Int, Int]^{r} = n => n + 40; f }` compiler/runtime allocation-stat tests | Explicit checked region-parameter methods can now return a local capture-free closure object while preserving checked-region placement and method-return ownership summary. This is closure-object placement only, not closure-body allocation placement. |
| Nonescaping closure object capturing a region value | Implemented first synthetic-closure slice | `val f: Function1[Int, Int]^{region} = (n: Int) => leaf.value + n` compiler/runtime allocation-stat tests, with materialization through a non-local function call | The NIR lowering can place a local closure object into the same checked region as its captured region value when the closure does not escape. This is closure-object placement, not full closure-body allocation/effect inference. |
| Method-returned closure object capturing a region value | Implemented method/closure summary slice | `def make(using r): Function1[Int, Int]^{r} = { val leaf: T^{r} = new T(...); val f: Function1[Int, Int]^{r} = n => leaf.value + n; f }` compiler/runtime allocation-stat tests | Explicit checked region-parameter methods can return a local closure object that captures a region-local value, with runtime allocation stats proving both the captured value and closure object are region allocated. This is still closure-object placement, not closure-body allocation. |
| Method-returned closure object through immutable checked owner alias | Implemented owner-alias method/closure slice | `def make(using r): Function1[Int, Int]^{r} = { val owner = r; val leaf: T^{owner} = new T(...); val f: Function1[Int, Int]^{owner} = n => leaf.value + n; f }` compiler/runtime allocation-stat tests | Method-return summaries can canonicalize an immutable local owner alias back to the explicit checked region parameter for returned closure objects. Runtime stats prove the alias-owned captured value and closure object are region allocated. |
| Forwarded method-returned closure object capturing a region value | Implemented method/closure forwarding slice | `def wrap(using r): Function1[Int, Int]^{r} = make(using r)`, where `make` returns a closure capturing `T^{r}`, compiler/runtime allocation-stat tests | Method-return summaries now propagate through a simple wrapper method for returned closure objects that capture region-local values. Runtime stats prove the original captured value and closure object remain region allocated after forwarding. This is still explicit-region-parameter forwarding, not broad closure-body/effect inference. |
| Forwarded local alias of method-returned closure object capturing a region value | Implemented method/closure local-forwarding slice | `def wrap(using r): Function1[Int, Int]^{r} = { val f = make(using r); f }`, where `make` returns a closure capturing `T^{r}`, compiler/runtime allocation-stat tests | Method-return summaries now propagate through one immutable method-local alias for returned closure objects that capture region-local values. Runtime stats prove the forwarded alias still refers to region-allocated captured value and closure object. |
| Forwarded branch/match method-returned closure object capturing a region value | Implemented method/closure control-flow forwarding slice | `def wrap(flag)(using r): Function1[Int, Int]^{r} = if flag then make(using r) else make(using r)` and match equivalent, compiler/runtime allocation-stat tests | Method-return summaries now propagate through simple branch and match wrappers for returned closure objects that capture region-local values, when every path forwards the same explicit checked owner. Runtime stats prove the selected path still region-allocates the captured value and closure object. |
| Inference diagnostics | Implemented | `-P:scalanative:riftInferReport` sandbox compile smoke | Opt-in diagnostics report `Region`, `Unknown`, and `Rejected` decisions without tripping `-Werror`. |

## Current Safety Boundaries

| Boundary | Status | Evidence |
|---|---:|---|
| Mutable direct-new locals are not inferred flow-sensitively | Enforced | compiler negative test |
| Immutable aliases of mutable checked owner slots are not inferred flow-sensitively | Enforced | compiler negative `epochBufferRegionFromMutableOwnerSlotDoesNotInferLocalNewPlacement`; opt-in inference report records the alias as rejected |
| Immutable checked owner alias allocation rejects unrooted heap metadata | Enforced | compiler negative test for `val owner = region; val x: T^{owner} = new T(metadata)` |
| Method-returned checked owner alias allocation rejects unrooted heap metadata | Enforced | compiler negative test for `def make(using r): T^{r} = { val owner = r; val x: T^{owner} = new T(metadata); val y: T^{r} = x; y }` |
| Generic `ObjectBuffer` append remains explicit | Enforced | existing object-buffer heap-object rejection tests still pass |
| Unrooted dynamic heap metadata is rejected in inferred region allocation | Enforced | compiler negative tests |
| Inferred region values cannot escape to durable heap/static state | Enforced | compiler negative tests |
| Helper-returned heap objects are not retroactively inferred | Enforced | compiler negative test |
| Outer-captured method returns without a region parameter stay heap fallback | Enforced by implementation boundary | inference records a heap fallback decision because no runtime region handle is available in the method body |
| Method direct-return region allocation rejects unrooted heap metadata | Enforced | compiler negative test with explicit `ScopedRegion^` parameter |
| Inline direct `new` method arguments reject unrooted heap metadata | Enforced | compiler negative test for `consume(new Entry(metadata))` where `consume` expects `Entry^{region}` and `metadata` is an unrooted heap object |
| Owner-token method argument inference rejects unrooted heap metadata | Enforced | compiler negative test for `consume(using region)(new Entry(metadata))` where `consume` expects `Entry^{r}` and `metadata` is an unrooted heap object |
| Owner-token closure argument inference rejects unrooted heap captures | Enforced | compiler negative test for `consume(using region)((n: Int) => metadata.value + n)` where `consume` expects `Function1[Int, Int]^{r}` and `metadata` is an unrooted heap object |
| Owner-token `Some(...)` argument inference rejects unrooted heap payloads | Enforced | compiler negative test for `consume(using region)(Some(metadata))` where `consume` expects `Option[Metadata]^{r}` and `metadata` is an unrooted heap object |
| Owner-token `Tuple2(...)` argument inference rejects unrooted heap payloads | Enforced | compiler negative test for `consume(using region)(Tuple2(metadata, metadata))` where `consume` expects `Tuple2[Metadata, Metadata]^{r}` and `metadata` is an unrooted heap object |
| Owner-token branch/match synthetic factory inference rejects unrooted heap payloads | Enforced | compiler negatives for `consume(using region)(if flag then Some(metadata) else Some(metadata))`, checked `ObjectBuffer`/`RegionBuffer` branch/match factory stores, checked priority-queue branch factory stores, and checked stream rank `Option(metadata)` branch expressions |
| Owner-token generic `Cell(...)` argument inference rejects unrooted heap payloads and generic hiding | Enforced | compiler negative tests for `consume(using region)(new Cell(metadata))` where `consume` expects `Cell[Metadata]^{r}`, plus retaining `Cell[T^{r}]^{r}` as widened `AnyRef` |
| Polymorphic owner-token generic `Cell(...)` argument inference rejects unrooted heap payloads and generic hiding | Enforced | compiler negative tests for `consume[A](using region)(new Cell(metadata))` where `consume` expects `Cell[A^{r}]^{r}`, plus retaining the polymorphic `Cell[T^{r}]^{r}` as widened `AnyRef` |
| Polymorphic method-returned generic `Cell` rejects helper-returned heap metadata and heap escape | Enforced | compiler negative tests for `make[A](using r)(value: A^{r}): Cell[A^{r}]^{r}` with a helper-returned heap metadata argument, plus retaining the returned `Cell[T^{r}]^{r}` as widened `AnyRef` |
| Forwarded polymorphic method-returned generic `Cell` rejects helper-returned heap metadata and heap escape | Enforced | compiler negative tests for `wrap[A](using r)(value: A^{r}): Cell[A^{r}]^{r} = make[A](using r)(value)` with a helper-returned heap metadata argument, plus retaining the forwarded `Cell[T^{r}]^{r}` as widened `AnyRef` |
| Polymorphic method-returned `Option`/`Some` rejects helper-returned heap metadata and heap escape | Enforced | compiler negative tests for `make[A](using r)(value: A^{r}): Option[A^{r}]^{r} = Some(value)` with a helper-returned heap metadata argument, plus retaining the returned `Option[T^{r}]^{r}` as widened `AnyRef` |
| Polymorphic method-returned `Option.apply` rejects helper-returned heap metadata and heap escape | Enforced | compiler negative tests for `make[A](using r)(value: A^{r}): Option[A^{r}]^{r} = Option(value)` with a helper-returned heap metadata argument, plus retaining the returned `Option[T^{r}]^{r}` as widened `AnyRef` |
| Polymorphic method-returned `Tuple2` rejects helper-returned heap metadata and heap escape | Enforced | compiler negative tests for `make[A, B](using r)(left: A^{r}, right: B^{r}): Tuple2[A^{r}, B^{r}]^{r}` with a helper-returned heap metadata argument, plus retaining the returned `Tuple2[L^{r}, R^{r}]^{r}` as widened `AnyRef` |
| Branch/match forwarded polymorphic `Option.apply` and `Tuple2` reject helper-returned heap metadata and heap escape | Enforced | compiler negative tests for branch/match wrappers that forward `make[A](using r)(value)` and `make[A, B](using r)(left, right)` with helper-returned heap metadata, plus retaining the forwarded `Option[T^{r}]^{r}` or `Tuple2[L^{r}, R^{r}]^{r}` as widened `AnyRef` |
| Method block-final direct-return region allocation rejects unrooted heap metadata | Enforced | compiler negative test with explicit `ScopedRegion^` parameter |
| Method returned-local region allocation rejects unrooted heap metadata | Enforced | compiler negative tests with explicit `ScopedRegion^` and `OpenStreamingRegion^` parameters and returned method-local values |
| Method branch-return region allocation rejects unrooted heap metadata | Enforced | compiler negative test with explicit `ScopedRegion^` parameter |
| Local branch/match-final region allocation rejects unrooted heap metadata | Enforced | compiler negative tests for `val x: T^{region} = if p then new T(metadata) else new T(metadata)` and `selector match { case _ => new T(metadata) }` |
| Method branch-returned-local region allocation rejects unrooted heap metadata | Enforced | compiler negative test with explicit `ScopedRegion^` parameter |
| Method match-return and match-returned-local region allocation reject unrooted heap metadata | Enforced | compiler negative tests with explicit `ScopedRegion^` parameter |
| Method-returned `Some(...)`/`Tuple2(...)` factory allocation rejects unrooted heap metadata | Enforced | compiler negative tests with explicit `ScopedRegion^` parameter, including exact `Some` and widened `Option` result types |
| Method-returned local `Option = Some(...)` factory allocation rejects unrooted heap metadata | Enforced | compiler negative test with explicit `ScopedRegion^` parameter |
| Local and method-returned `Some(...)`/`None` optional flows reject unrooted heap metadata | Enforced | compiler negative tests for `if flag then Some(metadata) else None` under captured local expected types and explicit `ScopedRegion^` method results |
| Branch/match forwarded method-returned `Option = Some(...)` rejects unrooted heap metadata and heap escape | Enforced | compiler negative tests where a branch wrapper forwards a producer that tries to return `Some(unrootedHeapMetadata)`, plus match-wrapper heap/static retention of the forwarded `Option[T^{r}]^{r}` |
| Method-returned local `Tuple2(...)` factory allocation rejects unrooted heap metadata | Enforced | compiler negative test with explicit `ScopedRegion^` parameter |
| Branch/match forwarded method-returned `Tuple2(...)` rejects unrooted heap metadata and heap escape | Enforced | compiler negative tests where a branch wrapper forwards a producer that tries to return `Tuple2(unrootedHeapMetadata, ...)`, plus match-wrapper heap/static retention of the forwarded `Tuple2[A^{r}, B^{r}]^{r}` |
| Buffer-append inferred region allocation rejects unrooted heap metadata | Enforced | compiler negative test |
| Inline owner-token direct/block-final allocation rejects unrooted heap metadata | Enforced | compiler negative tests for `ObjectBuffer`/`RegionBuffer` append and `RegionList` prepend |
| Inline owner-token block-final allocation rejects unrooted heap metadata | Enforced | compiler negative test for checked `RegionBuffer` append |
| Nested direct region-placed constructors/factories reject unrooted heap payloads | Enforced | compiler negatives cover RegionList branch/match nodes containing `Option(metadata)`, `Tuple2(metadata, metadata)`, or `Either(metadata)`; existing array, buffer, priority-queue, and rank/table inline factory negatives keep their allocation diagnostics |
| Nested selected aliases remain bounded to real selected allocation aliases | Enforced | compiler negatives `inferredSelectedNestedRegionListOptionCannotStoreUnrootedHeapMetadata`, `inferredSelectedNestedRegionListEitherCannotStoreUnrootedHeapMetadata`, `inferredSelectedNestedObjectBufferOptionCannotStoreUnrootedHeapMetadata`, `inferredSelectedNestedRegionBufferTuple2CannotStoreUnrootedHeapMetadata`, and `inferredSelectedNestedRegionPriorityQueueTuple2CannotStoreUnrootedHeapMetadata`; prior straight-alias negatives such as inline/block buffer/list/priority-queue metadata stores still reject |
| Page/window/transaction/epoch-fold child-region inferred allocation rejects unrooted heap metadata | Enforced | compiler negative tests for `pageTokenAppendRegionFor`, `pageTokenMapFilterRegionFor`, `pageTokenCountByKeyRegionFor`, `transactionRegionFor`, `chunkAppendRegionFor`, and `epochFoldRegionFor` child-region locals |
| Open child-region inferred allocation rejects unrooted heap metadata | Enforced | compiler negative tests for `pageTokenAppendOpenRegionFor`, `pageTokenMapFilterOpenRegionFor`, and `pageTokenCountByKeyOpenRegionFor`; runtime allocation-stat tests for page-token append/map-filter/count-by-key open child regions and epoch-buffer open regions |
| Page-token Rift open-handle inferred allocation rejects unrooted heap metadata | Enforced | compiler negative test for `pageTokenAppendRiftOpenHandleFor` plus runtime allocation-stat test proving the positive row actually allocates through the Rift open handle |
| Parent `StreamingRegion` remains excluded from generic inference | Enforced by current boundary | direct `Event^{stream} = new Event(...)` append remains rejected unless a child/open owner proves placement |
| Captured `Some(...)` region allocation rejects unrooted heap metadata | Enforced | compiler negative tests for exact `Some` and widened `Option` expected types |
| Captured `Some(...)` values cannot escape to heap/static state | Enforced | compiler negative tests for exact `Some` and widened `Option` expected types |
| Captured `Tuple2(...)`/tuple-literal region allocation rejects unrooted heap metadata | Enforced | compiler negative tests |
| Captured `Tuple2(...)` values cannot escape to heap/static state | Enforced | compiler negative test |
| Helper-returned heap arguments to captured `Tuple2(...)` are not retroactively inferred | Enforced | compiler negative test |
| Captured local generic object region allocation rejects unrooted heap metadata | Enforced | compiler negative test for `Cell[Metadata]^{region}` |
| Captured local generic object cannot escape through widened `AnyRef` | Enforced | compiler negative test for `Cell[T^{region}]^{region}` erased to `AnyRef` |
| Method-returned captured generic object rejects unrooted heap metadata and heap escape | Enforced | compiler negative tests for `Cell[Metadata]^{r}` factory and `Cell[T^{r}]^{r}` factory retained as `AnyRef` |
| Method-returned local generic object rejects unrooted heap metadata | Enforced | compiler negative test for returned-local `Cell[Metadata]^{r}` factory |
| Branch/match forwarded method-returned generic object rejects unrooted heap metadata and heap escape | Enforced | compiler negative tests where a branch wrapper forwards a `Cell[Metadata]^{r}` producer, plus match-wrapper heap/static retention of a forwarded `Cell[T^{r}]^{r}` |
| Helper-returned heap arguments to region-owned direct constructors are not retroactively inferred | Enforced | compiler negative test |
| Helper-returned heap objects are still rejected by checked buffers | Enforced | compiler negative tests for `ObjectBuffer`/`RegionBuffer` |
| Active open-handle inferred allocation rejects unrooted heap metadata | Enforced | compiler negative test |
| Capture-free region-owned closure object rejects unrooted heap captures | Enforced | compiler negative test for `val f: Function1[Int, Int]^{region} = n => metadata.value + n` |
| Owner-token container closure placement rejects unrooted heap captures | Enforced | compiler negative tests for checked ObjectBuffer append and RegionPriorityQueue push where the inferred closure captures unrooted heap metadata |
| Method-returned region-owned closure object rejects unrooted heap captures | Enforced | compiler negative test for `def make(using r): Function1[Int, Int]^{r} = { val metadata = new Metadata(...); val f: Function1[Int, Int]^{r} = n => metadata.value + n; f }` |
| Method-returned region-owned closure object through immutable checked owner alias rejects unrooted heap captures | Enforced | compiler negative test for `def make(using r): Function1[Int, Int]^{r} = { val owner = r; val metadata = new Metadata(...); val f: Function1[Int, Int]^{owner} = n => metadata.value + n; f }` |
| Forwarded method-returned region-owned closure object rejects unrooted heap captures | Enforced | compiler negative test where `wrap(using r): Function1[Int, Int]^{r}` forwards `make(using r)` and `make` tries to return a closure that captures unrooted heap metadata |
| Forwarded local alias of method-returned region-owned closure object rejects unrooted heap captures | Enforced | compiler negative test where `wrap(using r): Function1[Int, Int]^{r}` names `val f = make(using r); f` and `make` tries to return a closure that captures unrooted heap metadata |
| Forwarded branch/match method-returned region-owned closure object rejects unrooted heap captures | Enforced | compiler negative tests where branch and match wrappers forward `make(using r)` and `make` tries to return a closure that captures unrooted heap metadata |
| Region-allocated closure objects reject unrooted heap captures | Enforced | compiler negative test where a local closure captures both a region value and unrooted heap metadata |
| Region-owned array closure stores reject unrooted heap captures | Enforced | compiler negative for `Array[Function1[Int, Int]^{region}]^{region}` storing `(n: Int) => metadata.value + n` where `metadata` is an unrooted heap object |
| Captured-owner closure-body allocation rejects unrooted heap metadata | Enforced | compiler negative test where a region-owned closure captures the checked owner term but tries to construct a returned region object from an unrooted heap metadata object |
| `HeapRoot` remains the v1 bridge for dynamic heap metadata | Preserved | existing `HeapRoot` tests still pass |
| Inferred region-owned arrays reject unrooted heap stores and heap escape | Enforced | compiler negative tests for `Array[Metadata]^{region}` element stores and retaining `Array[T^{region}]^{region}` in heap/static state |
| Owner-token method-argument region-owned arrays reject unrooted heap stores | Enforced | compiler negative test where `consume(using r)(values: Array[Metadata]^{r}, metadata: Metadata)` stores unrooted heap metadata into the captured array argument |
| Inline direct `new` into a region-owned array is not inferred when the element type lacks a checked owner | Enforced | compiler negative test for `items: Array[Metadata]^{region}; items(0) = new Metadata(...)` |
| Inline `Some(...)` into a region-owned array rejects unrooted heap metadata payloads | Enforced | compiler negative test for `items: Array[Option[Metadata]^{region}]^{region}; items(0) = Some(metadata)` where `metadata` is an unrooted heap object |
| Inline `Tuple2(...)` into a region-owned array rejects unrooted heap metadata payloads | Enforced | compiler negative test for `items: Array[Tuple2[Metadata, Metadata]^{region}]^{region}; items(0) = Tuple2(metadata, metadata)` where `metadata` is an unrooted heap object |
| Inline or selected `Either(...)` into a region-owned array rejects unrooted heap metadata payloads | Enforced | compiler negative tests for `items: Array[Either[Metadata, Metadata]^{region}]^{region}; items(0) = Left(metadata)` and selected local `Left(metadata)`/`Right(metadata)` values where `metadata` is an unrooted heap object |
| Branch/match synthetic factories stored into region-owned arrays reject unrooted heap metadata | Enforced | compiler negative for `items: Array[Option[Metadata]^{region}]^{region}; items(0) = if flag then Some(metadata) else Some(metadata)` |
| Inline-reset inferred region arrays reject unrooted heap metadata | Enforced | compiler negative `resetOpenHandleInlineInferredArrayRejectsUnrootedHeapMetadata`; runtime positive `resetOpenHandleInlineInfersDirectRegionArrayPlacement` proves object arrays, primitive arrays, and entries allocate in checked region memory |
| Method-returned region-owned arrays reject unrooted heap stores and heap escape | Enforced | compiler negative tests for method-local `Array[Metadata]^{r}` stores and retaining a method-returned `Array[T^{r}]^{r}` as `AnyRef` in heap/static state |
| Forwarded method-returned region-owned arrays reject unrooted heap stores and heap escape | Enforced | compiler negative tests where a wrapper forwards a method-returned array whose producer attempts an unrooted heap store, plus heap/static retention of the forwarded array |
| Branch/match forwarded method-returned region-owned arrays reject unrooted heap stores and heap escape | Enforced | compiler negative tests where branch/match wrappers forward a method-returned array whose producer attempts an unrooted heap store, plus heap/static retention of the forwarded array |
| Inline or branch/match stores of fresh heap-looking objects into inferred region arrays remain rejected unless the array element type carries the checked owner | Enforced by current boundary | positive runtime tests store inline and branch/match returned `new T(...)` into `Array[T^{region}]^{region}`; compiler negatives reject `items(0) = new Metadata(...)` for `Array[Metadata]^{region}` and branch-returned factories containing unrooted metadata |
| Broad generic container/effect inference remains future work | Enforced by current boundary | The local, method-returned, returned-local, branch/match-forwarded, and explicitly region-typed selected owner-token `Cell[A]` slices plus the first captured array expected-type slices are validated, but untyped selected generic aliases, escaping generic containers, callbacks, arrays flowing through generic APIs, and hidden retention still require broader method/effect summaries |
| Priority-queue and stream-rank owner-token placement remain explicitly bounded | Enforced by current boundary | compiler/runtime tests cover scoped `RegionPriorityQueue`, `RegionIndexedPriorityQueue`, `RegionLongIndexedPriorityQueue`, dense/long lexicographic indexed queue overloads, selected synthetic aliases and selected/branch `Either` aliases at checked stream-window rank/table-rank `put` APIs, closure values at those checked rank/table APIs, branch/match-local direct allocation aliases at those rank/table APIs, direct arrays with result-local element ownership recovered from explicit result types or prior checked `put` value types, direct branch/match synthetic factories at explicit owner-token method arguments, checked buffers, checked priority queues, and checked rank/table APIs, plus selected-nested synthetic factories inside ordinary checked priority-queue value objects. Broader stream-window rank/table-rank operators and page/window child buckets beyond explicit child-region locals remain explicit |
| Broader closure-body and closure/effect inference remains future work | Enforced by current boundary | Captured-owner closure-body placement is implemented only when the closure explicitly captures the same checked owner term or when the lambda-lifted returned-local helper bridge can recover a unique owner-typed source summary and a concrete lowered runtime owner value. Covered shapes include direct, local, owner-token, branch/match direct-inline, materialized local closure, typed and untyped named local closure-body returned closures, lambda-lifted local helpers returning named local closure aliases, lambda-lifted local helpers returning named local direct allocations with a runtime owner term, lambda-lifted local helpers returning named local `Some(new T(...))`, `Option(new T(...))`, `Tuple2(new A(...), new B(...))`, or `Left(new A(...))`/`Right(new B(...))` wrappers with a runtime owner term, lambda-lifted local helpers directly returning `if`/`match` direct allocations with a runtime owner term, lambda-lifted local helpers branch/match-forwarding or immutable-alias-forwarding another inferred lexical-owner helper result with a runtime owner term, lambda-lifted local helpers returning `Array[T^{r}]^{r}` with region-owned element stores or primitive `Array[Int]^{r}` values with a runtime owner term, direct and selected-local closure-body `Some`/`Option.apply`/`Tuple2` factory returns, optional `Some`/`None` closure-body returns, owner-token selected immutable local closure aliases, method-returned selected immutable local closure aliases, direct/branch/match forwarded method-returned closures, one-hop forwarded selected local aliases, simple wrapper/`Some(closure)`/generic-wrapper nesting, method-returned generic wrappers containing inline or selected local closures, simple direct/branch-forwarded generic wrappers containing inline or selected local closures, method-returned and direct/branch-forwarded `Some(new Wrapper(new T(...)))` generic-wrapper payloads, direct/branch-forwarded `Either(new Wrapper(new T(...)))` construction, direct/branch-forwarded `Option(Either(new T(...)))` construction, direct/branch-forwarded and selected-local `Either(Option(new T(...)))` construction, closure-body `Option.apply`, exact `Some`, and `Either` wrappers containing inline closures or immutable selected local closure aliases, closure-body calls to explicit checked-region callees, closure-body calls through one simple forwarded checked-region callee, closure-body calls through branch/match forwarded checked-region callees, and closure-body calls to checked-region callees returning `Some`, `Option.apply`, `Tuple2`, `Either`, or selected `Option.apply`/`Tuple2`/`Either` factory values. Closure bodies whose owner exists only in types without a runtime handle, escaping closures, broader hidden owner capture beyond the current selected-wrapper receiver/environment preparation, generic wrapper closure fields nested under `Some(...)`, selected-local `Option[Wrapper[T^{r}]^{r}]^{r}` aliases, match-forwarded `Some(Wrapper(payload))` results, `Tuple2(Wrapper(payload), Wrapper(payload))` nested wrapper-payload method summaries, `Either(Wrapper(payload))` nested wrapper field extraction through `Left.value`/`Right.value`, alias/match-forwarded generic wrapper closure values, mutable selected aliases, arbitrary callbacks, primitive boxed-key paths, and broad cross-library effect summaries remain rejected or heap fallback. |
| Primitive boxing / boxed-key placement remains future work | Enforced by current NIR boundary plus primitive-boxing negatives | `Op.Box(ty, obj)` has no allocation-zone operand, unlike `Classalloc` and `Arrayalloc`; compiler negatives now reject `Option[Int]^{region}`, `Either[Int, Int]^{region}`, `Tuple2[Int, T^{region}]^{region}`, owner-token `Tuple2(40, new T(...))`, method-returned `Tuple2[Int, T^{r}]^{r}`, mixed primitive/unrooted-heap-metadata tuples, and preboxed `Any` values without `HeapRoot`; region-owned primitive boxes require a NIR/runtime lowering design instead of a small inference-only change |

## Validation

| Command | Result |
|---|---:|
| `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"` | Passed `702/702` on 2026-05-24 15:57 CEST |
| `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"` | Passed `316/316` on 2026-05-24 15:58 CEST |
| `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` | Passed on 2026-05-24 15:59 CEST |
| `LOGHUB_SESSION_OUTPUT_DIR=/tmp/loghub-array-inference-wikimedia-smoke ... zsh sandbox/run_loghub_retained_session_matrix.sh` | Passed 20k compressed Wikimedia clickstream-session; checksum `4440636879622788340`, output `18167` matched heap/explicit/inferred/scoped |
| `LOGHUB_SESSION_OUTPUT_DIR=/tmp/loghub-inferred-session-array-smoke ... zsh sandbox/run_loghub_retained_session_matrix.sh` | Passed fresh 20k compressed Wikimedia clickstream-session after the inferred session array-source audit; checksum `4260216346575211415`, output `18980` matched heap/explicit/inferred/scoped |
| `LOGHUB_SESSION_OUTPUT_DIR=/tmp/loghub-array-inference-join-smoke ... zsh sandbox/run_loghub_retained_session_matrix.sh` | Passed 20k compressed HDFS join; checksum `-1607483374812565358`, output `0` matched heap/explicit/inferred/scoped |
| `LOGHUB_SESSION_OUTPUT_DIR=/Users/siyaoliu/rift/cache/loghub-wikimedia-inferred-array-1m-l2-20260521 ... zsh sandbox/run_loghub_retained_session_matrix.sh` | Passed 1M x3 L2 Wikimedia clickstream-session; checksum `250002331971566003`, output `922453` matched; heap `1383.161 ms`, explicit checked `1341.892 ms`, inferred checked `1254.338 ms`, scoped checked `1344.536 ms`; explicit/inferred region objects both `1922465` |
| `LOGHUB_SESSION_OUTPUT_DIR=/Users/siyaoliu/rift/cache/loghub-wikimedia-inferred-session-array-complete-1m-l2-20260521 ... zsh sandbox/run_loghub_retained_session_matrix.sh` | Passed fresh 1M x3 L2 Wikimedia clickstream-session after replacing the remaining inferred session arrays with ordinary `new Array`; checksum `250002331971566003`, output `922453` matched; heap `1069.051 ms`, explicit checked `1052.706 ms`, inferred checked `965.723 ms`, scoped checked `1053.033 ms`; explicit/inferred region objects both `1922465` |
| `LOGHUB_SESSION_OUTPUT_DIR=/Users/siyaoliu/rift/cache/loghub-join-inferred-array-1m-l2-20260521 ... zsh sandbox/run_loghub_retained_session_matrix.sh` | Passed 1M x3 L2 HDFS join; checksum `4282190220497908364`, output `0` matched; heap `8031.714 ms`, explicit checked `7839.871 ms`, inferred checked `7772.096 ms`, scoped checked `7737.018 ms`; explicit/inferred region objects both `1000006` |
| `RIFT_PROFILE_OUTPUT_DIR=/Users/siyaoliu/rift/cache/profile-sweep-20260521-loghub-array-source ... zsh sandbox/run_l4_profile_sweep.sh` | Passed focused L4 sweep for Wikimedia and HDFS join heap/explicit/inferred/scoped rows; all checksum/output matched; Wikimedia inferred checked bucket summary is parser/input/hash `477.00/s`, query/session-loop `80.80/s`, region alloc/init `4.40/s`, callback-ref `0.00/s` |
| `REML_OUTPUT_DIR=/tmp/reml-region-smoke-framework-selected-nested REML_WORKLOADS=ratio REML_MODES="gc-heap checked-region-stream-inferred checked-region-scoped" zsh sandbox/run_reml_region_matrix.sh` | Previously passed in the 06:12-06:19 proof gate; not rerun in the inferred-array slice |
| `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" "set Compile / scalacOptions += \"-P:scalanative:riftInferReport\"" compile` | Passed after the stream-rank closure slice |

Latest allocation-stat proof:
`scopedRegionInfersSelectedMethodReturnedEitherOptionNestedPayloadAllocation`
observes checked-region allocation for explicit checked-region methods that
name both local candidate
`Either[Option[T^{r}]^{r}, Option[T^{r}]^{r}]^{r}` values as
`Left(Option(new T(...)))` and `Right(Option(new T(...)))`, select one, and
return the selected local. Runtime stats prove three selected direct/forwarded
calls allocate both local `Either` case wrappers, non-null `Option.apply`
`Some` branches, and nested payloads in checked region memory
(`delta >= 18`). Compiler positives cover the direct selected-local method
return and simple forwarded selected-local return, and a compiler negative
rejects unrooted heap metadata through the selected-local path.

Previous allocation-stat proof:
`scopedRegionInfersForwardedMethodReturnedEitherOptionNestedPayloadAllocation`
observes checked-region allocation for direct and branch-forwarded explicit
checked-region methods returning
`Either[Option[T^{r}]^{r}, Option[T^{r}]^{r}]^{r}` as
`Left(Option(new T(...)))` or `Right(Option(new T(...)))`. Runtime stats prove
three direct/forwarded `Either` case wrappers, non-null `Option.apply` `Some`
branches, and nested payloads allocate in checked region memory
(`delta >= 9`). Compiler positives cover direct and branch-forwarded
construction when the call-site result is ascribed with the captured owner,
and a compiler negative rejects unrooted heap metadata through the forwarded
path.

Previous allocation-stat proof:
`scopedRegionInfersForwardedMethodReturnedOptionEitherNestedPayloadAllocation`
observes checked-region allocation for direct and branch-forwarded explicit
checked-region methods returning
`Option[Either[T^{r}, T^{r}]^{r}]^{r}` as
`Option(Left(new T(...)))` or `Option(Right(new T(...)))`. Runtime stats prove
three direct/forwarded `Option.apply` non-null `Some` branches, selected
`Either` case wrappers, and nested payloads allocate in checked region memory
(`delta >= 9`). Compiler positives cover direct and branch-forwarded
construction when the call-site result is ascribed with the captured owner,
and a compiler negative rejects unrooted heap metadata through the forwarded
path.

Previous allocation-stat proof:
`scopedRegionInfersForwardedMethodReturnedEitherWrapperNestedPayloadAllocation`
observes checked-region allocation for direct and branch-forwarded explicit
checked-region methods returning
`Either[Wrapper[T^{r}]^{r}, Wrapper[T^{r}]^{r}]^{r}` as
`Left(new Wrapper[T^{r}](new T(...)))` or
`Right(new Wrapper[T^{r}](new T(...)))`. Runtime stats prove three
direct/forwarded `Either` case wrappers, wrapper records, and nested payloads
allocate in checked region memory (`delta >= 9`). Compiler positives cover
direct and branch-forwarded construction when the call-site result is ascribed
with the captured owner, and a compiler negative rejects unrooted heap metadata
through the forwarded path.

Latest boundary proof:
`inferredMethodReturnedEitherWrapperFieldExtractionCaptureWideningFallsBack`
records that extracting the nested wrapper through pattern matching currently
widens the synthesized `Left.value`/`Right.value` owner before Rift can recover
the nested payload owner. This keeps construction/forwarding promoted while
leaving field extraction to future lambda/environment or capture-preserving
library-summary work.

Previous allocation-stat proof:
`scopedRegionInfersForwardedMethodReturnedOptionWrapperNestedPayloadAllocation`
observes checked-region allocation for direct and branch-forwarded explicit
checked-region methods returning `Option[Wrapper[T^{r}]^{r}]^{r}` as
`Option(new Wrapper[T^{r}](new T(...)))`. Runtime stats prove three non-null
`Option.apply` `Some` branches, wrapper records, and nested payloads allocate
in checked region memory (`delta >= 9`). Compiler positives cover direct and
branch-forwarded `Option.apply(Wrapper(payload))`, and a compiler negative
rejects unrooted heap metadata through the forwarded path. This extends the
prior exact-`Some` wrapper-payload proof to the null-preserving library factory
without changing primitive-box, selected-alias, or match-forwarding boundaries.

Previous boundary proof:
`inferredMethodReturnedTupleWrapperCaptureWideningFallsBack` and
`inferredForwardedMethodReturnedTupleWrapperCaptureWideningFallsBack` record
that explicit checked-region methods returning
`Tuple2[Wrapper[T^{r}]^{r}, Wrapper[T^{r}]^{r}]^{r}` through
`Tuple2(new Wrapper(new T(...)), new Wrapper(new T(...)))` are currently
rejected by Scala capture typing before Rift lowering can prove a unique nested
payload owner. The existing unrooted-metadata negative for the analogous tuple
wrapper shape still rejects unsafe heap metadata. No runtime allocation-stat
proof is promoted for this tuple wrapper-payload shape.

Previous allocation-stat proof:
`scopedRegionInfersForwardedMethodReturnedSomeWrapperNestedPayloadAllocation`
observes checked-region allocation for direct and branch-forwarded explicit
checked-region methods returning `Option[Wrapper[T^{r}]^{r}]^{r}` as
`Some(new Wrapper[T^{r}](new T(...)))`. Runtime stats prove three
`Some`/wrapper/payload chains allocate in checked region memory
(`delta >= 9`). Compiler positives cover direct and branch-forwarded
`Some(Wrapper(payload))`, and a compiler negative rejects unrooted heap
metadata through the forwarded path. The selected-local alias variant remains
an expected source-capture fallback because `Option[Wrapper[T^{r}]^{r}]^{r}`
widens before Rift can recover the precise owner. The attempted match-forwarded
variant is now also recorded as source-capture fallback for the same nested
wrapper/option widening reason, with a compiler negative preserving the
boundary.

Previous allocation-stat proof:
`scopedRegionInfersMethodReturnedSomeWrapperNestedPayloadAllocation` observes
checked-region allocation for an explicit checked-region method returning
`Option[Wrapper[T^{r}]^{r}]^{r}` as
`Some(new Wrapper[T^{r}](new T(...)))`. Runtime stats prove the outer `Some`,
generic wrapper record, and nested direct payload allocate in checked region
memory (`delta >= 3`). Compiler positives/negatives cover the corresponding
source shape and reject unrooted heap metadata stored through the nested
wrapper payload. The attempted closure-field counterpart
`Some(new Wrapper(closure))`, plus alias/match-forwarded generic-wrapper
closure values, is deliberately recorded as safe fallback because Scala
capture checking widens the generic closure field before Rift can recover and
rewrite the owner-bearing lambda environment.

Previous allocation-stat proof:
`scopedRegionInfersForwardedMethodReturnedWrapperInlineClosureBodyAllocation`
and
`scopedRegionInfersBranchForwardedMethodReturnedWrapperSelectedClosureBodyAllocation`
observe checked-region allocation for simple forwarded explicit checked-region
methods returning a generic wrapper record whose field is an inline or selected
local closure. Runtime stats prove the direct-forwarded wrapper, inline
closure value, and nested body object allocate in checked region memory
(`delta >= 3`), and prove the branch-forwarded wrapper, selected closure
candidates, and selected body object allocate in checked region memory
(`delta >= 4`). The compiler negative
`inferredForwardedMethodReturnedWrapperClosureBodyCannotStoreUnrootedHeapMetadata`
rejects unrooted heap metadata captured by the nested closure body through the
forwarded wrapper. This extends simple forwarding method/effect-summary
coverage; it is not escaping closure inference, virtual-dispatch inference, or
broad library/container inference.

Previous allocation-stat proof:
`scopedRegionInfersMethodReturnedWrapperInlineClosureBodyAllocation` and
`scopedRegionInfersMethodReturnedWrapperSelectedClosureBodyAllocation` observe
checked-region allocation for explicit checked-region methods returning a
generic wrapper record whose field is an inline or selected local closure.
Runtime stats prove the wrapper, inline closure value, and nested body object
allocate in checked region memory (`delta >= 3`), and prove the wrapper,
selected closure candidates, and selected body object allocate in checked
region memory (`delta >= 4`). The compiler negative
`inferredMethodReturnedWrapperClosureBodyCannotStoreUnrootedHeapMetadata`
rejects unrooted heap metadata captured by the nested closure body through the
returned wrapper. This extends simple wrapper method/effect-summary coverage;
it is not escaping closure inference, virtual-dispatch inference, or broad
library/container inference.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodyEitherInlineClosureBodyAllocation` and
`scopedRegionInfersClosureBodyEitherSelectedClosureBodyAllocation` observe
checked-region allocation for captured-owner closure bodies returning
`Left`/`Right` wrappers around inline or selected local closures. Runtime stats
prove the outer closure wrapper, `Either` case wrapper, wrapped closure value,
and nested body object allocate in checked region memory for inline closures
(`delta >= 4`) and selected closures (`delta >= 5`). Compiler negatives
`inferredRegionOwnedClosureBodyEitherInlineClosureRejectsUnrootedMetadata` and
`inferredRegionOwnedClosureBodyEitherSelectedLocalClosureRejectsUnrootedMetadata`
reject unrooted heap metadata captured by the nested closure body. This extends
bounded closure-body wrapper/effect-summary coverage; it is not escaping
closure inference, broad callback inference, or broad library inference.

Previous allocation-stat proof:
`scopedRegionInfersRegionListEitherFactoryPlacement` observes checked-region
allocation for selected local and direct branch/match `Either` factories nested
inside checked `RegionList` node constructors. Runtime stats prove the
selected and branch/match `RegionList` nodes, `Left`/`Right` wrappers, and
nested payloads allocate in checked region memory (`delta >= 10`). Compiler
positives cover the same node-field placement shape, and compiler negatives
reject branch/match and selected nested `Either[Metadata, Metadata]^{region}`
fields with unrooted heap metadata. This extends explicit checked
collection-node synthetic placement; it is not arbitrary `RegionList`,
erased-container, or primitive-box inference.

Previous allocation-stat proof:
`streamingRegionInfersWindowRankEitherFactoryPlacement` observes
checked-region allocation for selected local and direct branch/match `Either`
factories put through checked `putWindowRank`, `putWindowRankInBucket`, and
`putTableRankInBucket` owner-token boundaries. Runtime stats prove the
selected and branch/match `Left`/`Right` wrappers plus nested payloads allocate
in checked region memory (`delta >= 8`). Compiler positives cover the same
rank/table placement shape, and compiler negatives reject selected indexed-rank
and match table-rank `Either[Metadata, Metadata]^{stream}` values with
unrooted heap metadata. This extends explicit checked framework-container
synthetic placement; it is not arbitrary stream topology, erased-container, or
primitive-box inference.

Previous allocation-stat proof:
`scopedRegionInfersLexicographicPriorityQueueEitherFactoryPlacement` observes
checked-region allocation for selected local and direct branch/match `Either`
factories put through checked `RegionIndexedPriorityQueueLexicographic` and
`RegionLongIndexedPriorityQueueLexicographic` owner-token boundaries. Runtime
stats prove the selected and branch/match `Left`/`Right` wrappers plus nested
payloads allocate in checked region memory (`delta >= 12`). Compiler positives
cover the same lexicographic queue placement shape, and compiler negatives
reject selected and match `Either[Metadata, Metadata]^{region}` values with
unrooted heap metadata. This extends explicit checked framework-container
synthetic placement; it is not arbitrary priority-queue, erased-container, or
primitive-box inference.

Previous allocation-stat proof:
`scopedRegionInfersPriorityQueueEitherFactoryPlacement` observes
checked-region allocation for selected local and direct branch/match `Either`
factories pushed or put through ordinary checked `RegionPriorityQueue`,
`RegionIndexedPriorityQueue`, and `RegionLongIndexedPriorityQueue`
owner-token boundaries. Runtime stats prove the selected and branch/match
`Left`/`Right` wrappers plus nested payloads allocate in checked region memory
(`delta >= 8`). Compiler positives cover the same queue placement shape, and
compiler negatives reject selected and branch/match
`Either[Metadata, Metadata]^{region}` values with unrooted heap metadata.
This extends explicit checked framework-container synthetic placement; it is
not arbitrary priority-queue, erased-container, or primitive-box inference.

Previous allocation-stat proof:
`scopedRegionInfersBufferEitherFactoryPlacement` observes checked-region
allocation for selected local and direct branch/match `Either` factories
appended through checked `ObjectBuffer` and `RegionBuffer` owner-token
boundaries. Runtime stats prove the selected and branch/match `Left`/`Right`
wrappers plus nested payloads allocate in checked region memory
(`delta >= 12`). Compiler positives cover the same checked-buffer placement
shape, and compiler negatives reject selected and branch/match
`Either[Metadata, Metadata]^{region}` values with unrooted heap metadata.
This extends explicit framework-container synthetic placement; it is not
arbitrary collection, erased-container, or primitive-box inference.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodySomeInlineClosureAllocationWithCapturedOwnerTerm`
observes checked-region allocation for a captured-owner closure body returning
exact `Some((value: Int) => ...)`, where the nested inline closure body
allocates under the same checked owner. Runtime stats prove the outer closure
wrapper, exact `Some` wrapper, inner closure wrapper, and nested body object
allocate in checked region memory (`delta >= 4`). The paired compiler negative
rejects unrooted heap metadata captured by the nested closure body through the
wrapper. This completes the exact-`Some` counterpart to the
`Option(inlineClosure)` wrapper proof; broad escaping closure inference and
type-only owner recovery remain future work.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodySomeSelectedClosureAllocationWithCapturedOwnerTerm`
observes checked-region allocation for a captured-owner closure body returning
`Some(selected)` where `selected` chooses between immutable local closures
whose bodies allocate under the same checked owner. Runtime stats prove the
outer closure wrapper, exact `Some` wrapper, both selected closure candidates,
and the selected body object allocate in checked region memory (`delta >= 5`).
The paired compiler negative rejects unrooted heap metadata captured by either
selected closure body through the wrapper. This completes the exact-`Some`
counterpart to the `Option(selected)` selected-wrapper proof; broad escaping
closure inference and type-only owner recovery remain future work.

Previous allocation-stat proof:
`scopedRegionInfersInlineRegionParamMethodArgumentEitherPlacement`,
`scopedRegionInfersMethodArgumentSelectedLocalEitherFactoryPlacement`,
`scopedRegionInfersInlineArrayStoreEitherFactoryPlacement`, and
`scopedRegionInfersSelectedArrayStoreEitherFactoryPlacement` observe
checked-region allocation for `Either` wrappers and payloads constrained by
explicit owner-token method arguments or region-owned array element types.
Runtime stats prove inline owner-token `Either` (`delta >= 2`), selected
owner-token `Either` candidates (`delta >= 4`), inline array-store `Either`
plus the array (`delta >= 3`), and selected array-store `Either` candidates
plus the array (`delta >= 5`) allocate in checked region memory. Compiler
negatives reject unrooted heap metadata in owner-token `Either` arguments and
direct/selected array-store `Either` values. This extends synthetic wrapper
coverage in explicit owner contexts; it is not arbitrary collection, erased
container, primitive box, or library allocation inference.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodyEitherMethodSummaryAllocationWithCapturedOwnerTerm`
and
`scopedRegionInfersClosureBodySelectedEitherMethodSummaryAllocationWithCapturedOwnerTerm`
observe checked-region allocation for explicit checked-region callees returning
direct or selected `Either` factory values from a captured-owner closure body.
Runtime stats prove the closure wrapper plus direct callee-created
`Either`/payload (`delta >= 3`) and selected callee-created `Either`
candidates plus payloads (`delta >= 5`) allocate in checked region memory.
Compiler negatives reject direct and selected
`Either[Metadata, Metadata]^{r}` results with unrooted heap metadata. This
extends the method/effect-summary boundary for explicit checked-region callees
and library-created factories; it is not broad library inference, primitive
boxed-key placement, hidden/type-only owner recovery, or automatic topology
inference.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodyOptionApplyMethodSummaryAllocationWithCapturedOwnerTerm`,
`scopedRegionInfersClosureBodyTupleMethodSummaryAllocationWithCapturedOwnerTerm`,
`scopedRegionInfersClosureBodySelectedOptionApplyMethodSummaryAllocationWithCapturedOwnerTerm`,
and `scopedRegionInfersClosureBodySelectedTupleMethodSummaryAllocationWithCapturedOwnerTerm`
observe checked-region allocation for explicit checked-region callees returning
direct or selected `Option.apply`/`Tuple2` factory values from a captured-owner
closure body. Runtime stats prove the closure wrapper plus callee-created
`Option.apply` non-null `Some`/payload (`delta >= 3`), direct
`Tuple2`/two payloads (`delta >= 4`), selected `Option.apply` candidates plus
payloads (`delta >= 5`), and selected `Tuple2` candidates plus payloads
(`delta >= 7`) allocate in checked region memory. Compiler negatives reject
direct and selected `Option(metadata)` and `Tuple2(metadata, metadata)` with
unrooted heap metadata. This extends the method/effect-summary boundary for
explicit checked-region callees and library-created factories; it is not broad
library inference, primitive boxed-key placement, hidden/type-only owner
recovery, or automatic topology inference.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodyOptionApplyFactoryAllocationWithCapturedOwnerTerm`
and `scopedRegionInfersClosureBodySomeOrNoneAllocationWithCapturedOwnerTerm`
observe checked-region allocation for optional closure-body factory results.
The `Option.apply` proof observes the closure wrapper plus the non-null
`Some` branch and payload in checked region memory (`delta >= 3`). The
Some/None proof calls both branches and observes the closure wrapper plus
`Some`/payload while `None` remains allocation-free (`delta >= 3`). Compiler
negatives reject `Option(metadata)` and
`if include then Some(metadata) else None` with unrooted heap metadata. This
extends closure-body synthetic factory coverage to null/empty-option semantics;
it is not broad library inference, primitive boxed-key placement,
hidden/type-only owner recovery, or automatic topology inference.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodySelectedOptionFactoryAllocationWithCapturedOwnerTerm`
and
`scopedRegionInfersClosureBodySelectedTupleFactoryAllocationWithCapturedOwnerTerm`
observe checked-region allocation for helper-style closure-body synthetic
factory values selected through immutable local aliases. The Option proof
materializes two `Some(new T(...))` candidates and observes the closure wrapper,
both `Some` wrappers, and both payloads in checked region memory (`delta >= 5`).
The tuple proof materializes two `Tuple2(new A(...), new B(...))` candidates
and observes the closure wrapper, both tuple wrappers, and all four payloads in
checked region memory (`delta >= 7`). The first runtime attempt observed only
the closure wrapper (`delta == 1`), so this was a real selected-local lowering
gap. Compiler negatives reject selected `Some(metadata)` and
`Tuple2(metadata, metadata)` with unrooted heap metadata. This is selected
local closure-body synthetic-factory effect-summary coverage; it is not broad
library inference, mutable selected aliases, primitive boxed-key placement,
hidden/type-only owner recovery, or automatic topology inference.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodyDirectOptionFactoryAllocationWithCapturedOwnerTerm`
and
`scopedRegionInfersClosureBodyDirectTupleFactoryAllocationWithCapturedOwnerTerm`
observe checked-region allocation for a captured-owner closure wrapper plus
direct closure-body synthetic factory results: `Some(new T(...))` allocates the
closure wrapper, `Some`, and nested payload in checked region memory
(`delta >= 3`), while `Tuple2(new A(...), new B(...))` allocates the closure
wrapper, tuple, and two nested payloads in checked region memory (`delta >= 4`).
The first runtime attempt observed only the closure wrapper (`delta == 1`),
which confirmed that this was a real GenNIR lowering gap rather than just a
missing test. Compiler negatives reject unrooted heap metadata behind
`Some(metadata)` and `Tuple2(metadata, metadata)`. This is direct closure-body
synthetic-factory effect-summary coverage; it is not broad library inference,
primitive boxed-key placement, hidden/type-only owner recovery, or automatic
topology inference.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodyOptionMethodSummaryAllocationWithCapturedOwnerTerm`
observes checked-region allocation for a region-owned closure wrapper plus a
method-returned `Some` wrapper plus the nested payload allocated by an explicit
checked-region callee invoked from the closure body (`delta >= 3`). The paired
compiler positive accepts
`build(value)(using owner): Option[T^{owner}]^{owner} = Some(new T(value))`
when the closure captures the same runtime owner term,
and the paired compiler negative rejects `Some(metadata)` with unrooted heap
metadata. This extends closure-body method/effect summary coverage to a common
library-created wrapper shape; it is not broad library inference, primitive
boxing, hidden owner capture, type-only owner recovery, or automatic topology
inference.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodyBranchForwardedMethodSummaryAllocationWithCapturedOwnerTerm`
and
`scopedRegionInfersClosureBodyMatchForwardedMethodSummaryAllocationWithCapturedOwnerTerm`
observe checked-region allocation for a region-owned closure wrapper plus the
executed result allocated by branch/match forwarded checked-region callees
(`delta >= 2`). Compiler positives accept `if` and `match` forwarding wrappers
when every path returns `build(...)(using owner): T^{owner}` from a
captured-owner closure body, and the compiler negative rejects unrooted heap
metadata through the branch-forwarded callee path. This extends method/effect
summary coverage through simple control flow; it is not virtual dispatch,
arbitrary callback/library inference, hidden owner capture, or automatic
topology inference.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodyForwardedMethodSummaryAllocationWithCapturedOwnerTerm`
observes checked-region allocation for a region-owned closure wrapper plus a
`RiftCheckedLeaf` allocated by an explicit checked-region callee reached
through one forwarding method (`delta >= 2`). The paired compiler positive
accepts `forward(value)(using owner): T^{owner} = build(value)(using owner)`
from a captured-owner closure body, and the paired negative rejects unrooted
heap metadata passed through the forwarded callee allocation. This extends the
direct callee proof by one method/effect summary hop; it is not hidden owner
capture, escaping closure inference, library-boundary inference, or automatic
topology inference.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodyMethodSummaryAllocationWithCapturedOwnerTerm`
observes checked-region allocation for a region-owned closure wrapper plus a
`RiftCheckedLeaf` allocated by an explicit checked-region callee invoked from
the closure body (`delta >= 2`). The paired compiler positive accepts
`build(value)(using owner): T^{owner}` when the closure captures the same
runtime checked owner term, and the paired negative rejects unrooted heap
metadata passed through the callee allocation. This is closure-body
method/effect-summary coverage; hidden owner capture, escaping closures, and
type-only owner recovery without a runtime handle remain outside the accepted
boundary.

Previous allocation-stat proof:
`scopedRegionInfersClosureBodyReturnedUntypedLocalClosureAllocationWithCapturedOwnerTerm`
observes checked-region allocation for the outer closure wrapper, the untyped
named local returned closure wrapper, and the nested `RiftCheckedLeaf` object
created by the returned closure body (`delta >= 3`). The paired compiler
positive accepts the same untyped source shape, and the paired negative rejects
unrooted heap metadata in the nested body allocation. The typed proof
`scopedRegionInfersClosureBodyReturnedTypedLocalClosureAllocationWithCapturedOwnerTerm`
remains as a control. Generated LLVM for `make$46$$anonfun$1` now calls the
region allocator for the untyped local inner wrapper rather than
`scalanative_GC_alloc_small`.

Previous allocation-stat proof:
`scopedRegionInfersForwardedMethodReturnedClosureBodyAllocationWithCapturedOwnerTerm`
observes checked-region allocation for a closure wrapper forwarded through a
method-return summary plus the closure-body object (`delta >= 2`). The branch
and match forwarding proofs
`scopedRegionInfersForwardedBranchMethodReturnedClosureBodyAllocationWithCapturedOwnerTerm`
and
`scopedRegionInfersForwardedMatchMethodReturnedClosureBodyAllocationWithCapturedOwnerTerm`
observe the same checked-region wrapper/body allocation through simple
control-flow wrappers (`delta >= 2`). The paired forwarded selected-local proof
`scopedRegionInfersMethodReturnedForwardedSelectedLocalClosureBodyAllocationWithCapturedOwnerTerm`
observes checked-region allocation for selected closure candidates plus the
selected body object (`delta >= 3`). Both proofs still require the closure body
to explicitly capture the runtime checked owner term.

Previous allocation-stat proof:
`scopedRegionInfersSelectedPolymorphicMethodArgumentGenericCellPlacement`
observes checked-region allocation for explicitly region-typed selected local
`Cell[A^{region}]^{region}` candidates flowing into a polymorphic owner-token
consumer `def consume[A](using r)(cell: Cell[A^{r}]^{r})` (`delta >= 4`). The
paired compiler negative records the current boundary: heap metadata/generic
selected-cell flows that do not carry the checked owner in the type are
rejected by capture checking before post-capture inference can recover an
owner.

Previous allocation-stat proof:
`epochBufferRegionInfersLocalNewPlacement` observes checked-region allocation
for two ordinary `new` records typed by `epochBufferRegionFor` and widened to
the parent stream owner before `appendEpochBuffer` (`delta >= 2`). The paired
compiler negative proves the mutable owner-slot source shape remains rejected:
an immutable alias loaded from a mutable checked owner slot is not inferred
flow-sensitively and the later checked buffer store still rejects the heap
fallback object.

Earlier allocation-stat proof:
`epochFoldInfersChildRegionLocalNewPlacement` observes checked-region
allocation for two ordinary `new` records typed by `epochFoldRegionFor` and
widened to the parent stream owner before `putEpochFold` (`delta >= 2`). The
paired compiler negative proves unrooted heap metadata in such epoch-fold
child-region records remains rejected.

Latest source-use proofs:
`DSPBenchRegionMatrix` now has `rift-checked-page-token-inferred` /
`checked-region-stream-inferred` for the file-backed checked page-token path.
It passes the selected `pageTokenAppendRiftOpenHandleFor` owner as a method
parameter, constructs `CheckedRecord` with ordinary `new` under that active
owner, widens the value to the parent stream owner, and appends through the
same page-token API. A focused 20k real Fraud/Log smoke matched heap,
explicit checked, and inferred checked checksum/output; inferred preserved the
explicit region-object counts (`80111` Fraud, `60000` Log). This validates
source use of the existing page-token open-handle proof; it does not add a new
compiler capability, L1/L2 elapsed claim, or L4 bucket claim.

`TheodolitePowerRegionMatrix` checked Rift handle paths now construct
`CheckedMeasurement` and `CheckedContribution` records with ordinary `new`
under the active `resetOpenHandle` owner in both streaming-file and preloaded
handle paths. A focused 20k real archive-member `q3-retained-uc4` smoke matched
heap, checked stream, and checked scoped checksum `-2895454912458695581` and
output `1544`; the checked stream row reported `260000` region objects. This
validates source use of the active-handle inference proof; it does not add a
new capability, L1/L2 elapsed claim, or L4 bucket claim.

`CheckedAppendWindowMatrix.runRiftCheckedChunkTokenBody` now opens each chunk
bucket with a direct `chunkAppendRegionFor` owner local, constructs records as
ordinary `new Record(...)` under that owner, and widens them to the parent
stream owner before `appendChunkToken`. A focused 20k append-window smoke
matched heap chunk and checked chunk-token checksum `-8639499034914970780`,
and the checked row reported `20632` region objects. The source shape avoids
mutable owner-slot inference; mutable owner flow remains out of scope.

`DataflowRegionMatrix.runCheckedAggregateEpochFold` now writes the per-record
fold contribution as ordinary `new CheckedAggregateEvent(...)` under the
`epochFoldRegionFor` child owner, then widens it to the parent stream owner
before `putEpochFold`. A focused 20k Dataflow aggregate smoke matched heap and
checked epoch-fold checksum `3276431580`, and the checked row reported `20004`
region objects. This validates source use of the epoch-fold inference proof;
it does not change the generic epoch-fold speed-gated status or add an L1/L2
elapsed claim.

Previous allocation-stat proof:
`scopedRegionInfersBranchMatchArrayStoreFactoryPlacement` observes checked-region
allocation for region-owned arrays plus branch/match direct store values:
`if flag then new T(...) else new T(...)`, match-returned
`Option(new T(...))`, and branch-returned `Tuple2(new A(...), new B(...))`
(`delta >= 9`). The paired compiler negative proves branch-returned
`Some(metadata)` still rejects unrooted heap metadata in a region-owned array.

Previous allocation-stat proof:
`streamingRegionInfersWindowRankInlineArrayPlacement` observes checked-region
allocation for direct `new Array[T^{stream}]` values inserted through
`putWindowRank`, `putWindowRankInBucket`, and `putTableRankInBucket`, then
recovered through unannotated `peekWindowRank`/`peekTableRank` result locals
using the prior checked `put` value type and populated with inline region-local
values (`delta >= 6`). The paired compiler negatives prove recovered
`Array[Metadata]^{stream}` values from indexed, long-key lexicographic, and
table-rank boundaries still reject unrooted heap element stores.

Earlier allocation-stat proof:
`scopedRegionInfersRegionBufferInlineArrayPlacement` observes checked-region
allocation for a direct `new Array[T^{region}]` appended to a checked
`RegionBuffer` through extension syntax, then recovered with `region.get` and
populated with inline stored region-local values (`delta >= 4`). The paired
compiler negative proves that recovered `Array[Metadata]^{region}` values from
the growable-buffer boundary still reject unrooted heap element stores.

Previous allocation-stat proof:
`scopedRegionInfersObjectBufferInlineArrayPlacement` observes checked-region
allocation for a direct `new Array[T^{region}]` appended to a checked
`ObjectBuffer`, then recovered with `RiftRegion.get` and populated with inline
stored region-local values (`delta >= 4`). The paired compiler negative proves
that `Array[Metadata]^{region}` recovered from the same framework boundary is
recognized as region-owned but still rejects unrooted heap element stores.

Previous allocation-stat proof:
`scopedRegionInfersInlineRegionParamMethodArgumentArrayPlacement` observes
checked-region allocation for a direct owner-token method-argument
`new Array[T^{r}]`, plus inline stored `T^{r}` values inside the consuming
method (`delta >= 3`). This proves the source-span owner bridge reaches the
lowered runtime array factory and does not only type-check the source shape.

Previous allocation-stat proof:
`scopedRegionInfersBranchForwardedMethodReturnedRegionOwnedArrayPlacement` and
`scopedRegionInfersMatchForwardedMethodReturnedRegionOwnedArrayPlacement`
observe checked-region allocation for method-returned `Array[T^{r}]^{r}`
values forwarded through simple branch and match wrappers. The tests prove the
selected array and its named region-local elements remain allocated in the
checked region (`delta >= 3`).

Previous allocation-stat proofs:
`streamingRegionInfersWindowRankClosurePlacement` observes checked-region
allocation for closure values inserted into checked stream-window rank and
table-rank APIs (`delta >= 4`) by comparing setup-only rank structures against
the same setup plus inserted closure values.
`scopedRegionInfersObjectBufferInlineClosurePlacement` observes checked-region
allocation for an ObjectBuffer backing array plus an inline closure value
(`delta >= 2`), `scopedRegionInfersRegionBufferSelectedClosurePlacement`
observes checked-region allocation for a RegionBuffer backing array plus both
selected local closure candidates (`delta >= 3`), and
`scopedRegionInfersPriorityQueueInlineClosurePlacement` observes
checked-region allocation for priority-queue backing arrays plus an inline
closure value (`delta >= 3`).
`scopedRegionInfersInlineArrayStoreClosurePlacement` observes checked-region
allocation for a region-owned `Array[Function1[Int, Int]^{region}]` plus an
inline stored closure object (`delta >= 2`), and
`scopedRegionInfersSelectedArrayStoreClosurePlacement` observes checked-region
allocation for the region-owned array plus selected local closure candidates
(`delta >= 3`).

Previous allocation-stat proof:
`resetOpenHandleInlineInfersDirectRegionArrayPlacement` observes checked-region
allocation for direct `new Array[Entry^{region}]`, direct `new Array[Int]`, and
ordinary `new Entry(...)` values inside an inline reset-open-handle body
(`delta >= 4`).

Previous allocation-stat proof:
`scopedRegionInfersRegionListBranchMatchSyntheticFactoryPlacement` observes
checked-region allocation for branch/match-created RegionList nodes containing
direct `Some(new T(...))`, `Option(new T(...))`, and
`Tuple2(new A(...), new B(...))` factory arguments. The proof observes the
executed nodes, wrappers, and payload objects as additional checked-region
allocations (`delta >= 10`).

Previous allocation-stat proof:
`streamingRegionInfersWindowRankBranchMatchLocalNewPlacement` observes
checked-region allocation for branch/match-local direct `new` candidates passed
through `putWindowRank`, `putWindowRankInBucket`, and
`putTableRankInBucket`. The runtime proof runs setup-only and branch/match-value
stream bodies, waits until each stream region has closed so allocation stats
flush, and observes the six rank/table candidate objects as additional
checked-region allocations (`delta >= 6`).

Latest synthetic-factory owner-token proof:
`scopedRegionInfersMethodArgumentBranchMatchSyntheticFactoryPlacement` and
`scopedRegionInfersBufferBranchMatchSyntheticFactoryPlacement`,
`scopedRegionInfersPriorityQueueBranchMatchSyntheticFactoryPlacement`, and
`streamingRegionInfersWindowRankBranchMatchSyntheticFactoryPlacement` observe
checked-region allocation for direct branch/match `Some(new T(...))`,
`Option(new T(...))`, and `Tuple2(new A(...), new B(...))` factory expressions
at explicit owner-token method arguments, checked fixed/growable buffers,
ordinary checked priority queues, and checked stream rank/table APIs. Each
runtime proof observes the executed wrappers plus payloads as additional
checked-region allocations (`delta >= 7`). Compiler coverage also includes the
dense and long-key checked lexicographic priority-queue overloads.

Previous allocation-stat proof:
`streamingRegionInfersWindowRankSelectedLocalSyntheticFactoryPlacement`
observes checked-region allocation for selected local `Some(new T(...))`,
`Option(new T(...))`, and `Tuple2(new A(...), new B(...))` factory aliases
passed through `putWindowRank`, `putWindowRankInBucket`, and
`putTableRankInBucket`. The runtime proof runs setup-only and selected-value
stream bodies, waits until each stream region has closed so allocation stats
flush, and observes the selected wrappers plus nested direct payload objects as
additional checked-region allocations (`delta >= 14`).

Previous allocation-stat proof:
`scopedRegionInfersLexicographicPriorityQueueSelectedLocalSyntheticFactoryPlacement`
observes checked-region allocation for selected local `Some(new T(...))`,
`Option(new T(...))`, and `Tuple2(new A(...), new B(...))` factory aliases put
through dense and long-key checked lexicographic priority queues. The runtime
proof forces both candidates for each factory shape and observes all wrappers
plus nested direct payload objects as checked-region allocations (`delta >= 14`).

Previous allocation-stat proof:
`scopedRegionInfersPriorityQueueSelectedLocalSyntheticFactoryPlacement` observes
checked-region allocation for selected local `Some(new T(...))`,
`Option(new T(...))`, and `Tuple2(new A(...), new B(...))` factory aliases
pushed or put into checked `RegionPriorityQueue`,
`RegionIndexedPriorityQueue`, and `RegionLongIndexedPriorityQueue` containers.
The runtime proof forces both candidates for each factory shape and observes
all wrappers plus nested direct payload objects as checked-region allocations
(`delta >= 14`). Earlier selected synthetic proofs cover the same factory set
for explicit-owner method returns, owner-token method arguments, region-owned
array-store boundaries, and checked fixed/growable buffers.

Earlier allocation-stat proof:
`scopedRegionInfersMethodArgumentSelectedLocalSyntheticFactoryPlacement`
observes checked-region allocation for owner-token method arguments that consume
selected local `Some(new T(...))` factory aliases and selected local
`Tuple2(new A(...), new B(...))` factory aliases, including both candidate
wrappers and all nested direct payload objects (`delta >= 10`).

Earlier allocation-stat proof:
`scopedRegionInfersMethodReturnedSelectedLocalSyntheticFactoryPlacement`
observes checked-region allocation for both selected local `Some(new T(...))`
factory candidates, both selected local `Tuple2(new A(...), new B(...))`
factory candidates, and all nested direct payload objects (`delta >= 10`).
This is proof coverage over the existing direct-region-construct selected-alias
path, not a new elapsed-time or profile-bucket claim.

Earlier allocation-stat proof:
`scopedRegionInfersPriorityQueueSelectedLocalNewPlacement` observes
checked-region allocation for both direct-allocation locals preserved through a
selected immutable alias and consumed by `RegionPriorityQueue.push`. This
extends the earlier ObjectBuffer, RegionList, and method-returned selected
direct-allocation proofs, method-returned selected closure alias, owner-token
selected-alias, owner-token direct-inline, branch-local, match-local, and local
direct-inline closure-body proofs.

Earlier no-zero allocation-stat proof:
`openHandleNoZeroSkipsDefinitelyInitializedInferredRecord`
now validates that ordinary `new` inferred under `epochOpenHandle` uses the
existing `RiftOpenStreamingHandle` no-zero path when the NIR proof sees all
fields definitely initialized before first use. The test allocates both a
metadata object and a record with a region-local reference field, observes at
least two zero-skipped objects, and observes zero zeroed objects. This is a
backend lowering proof for the already validated open-handle placement path,
not a broader checked-region no-zero expansion.

## Focused Allocation-Stat Gate

`ObjectAllocationLoweringMatrix` now has a focused scoped-region pair for
explicit versus inferred placement:

- `rift-checked-scoped-explicit`: the same scoped lifetime and object graph,
  with objects allocated through `RiftRegion.alloc(new ...)`;
- `rift-checked-scoped-inferred`: the same scoped lifetime and object graph,
  with ordinary `new` constrained by captured expected types.

20k smoke results, one run, no warmup:

| Shape | Mode | Median ms | Rift objects | Zero-skipped objects | Checksum | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| primitive | `heap-immix` | `0.346` | `0` | `0` | `-5014597496877744147` | Heap baseline; no region placement. |
| primitive | `rift-checked-scoped-explicit` | `0.446` | `20001` | `20001` | `-5014597496877744147` | Explicit scoped allocation places the full test graph in the region. |
| primitive | `rift-checked-scoped-inferred` | `0.422` | `20001` | `20001` | `-5014597496877744147` | Inferred ordinary `new` reaches the same region allocation count/checksum as explicit allocation. |
| reference | `heap-immix` | `0.354` | `0` | `0` | `6686416469483485743` | Heap baseline; no region placement. |
| reference | `rift-checked-scoped-explicit` | `0.368` | `20002` | `20002` | `6686416469483485743` | Explicit scoped allocation places records plus shared metadata holder in the region. |
| reference | `rift-checked-scoped-inferred` | `0.442` | `20002` | `20002` | `6686416469483485743` | Inferred ordinary `new` again matches explicit region allocation count/checksum. |

Allowed claim: the focused matrix proves ordinary inferred `new` is actually
being lowered into checked regions for the currently supported local/captured
forms. It is smoke-scale allocation-stat evidence, not a final elapsed-time
performance claim. Larger 5M/10M runs and representative benchmark rows are
still required for the performance part of the active goal.

Current post-page-token-child-owner rerun, 2026-05-19:

Source: `/private/tmp/rift-inference-object-20260519/summary.tsv`.

| Shape | Objects | Mode | Median ms | Median GC ms | Max GC ms | Runs with GC | Rift op ms | Rift objects | RSS bytes | Checksum |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| reference | `5M` | `heap-immix` | `309.217` | `232.842` | `364.856` | `2/3` | `0.000` | `0` | `485507072` | `3953966985786210233` |
| reference | `5M` | `rift-checked-scoped-explicit` | `81.741` | `0.000` | `0.000` | `0/3` | `2.263` | `5000002` | `203833344` | `3953966985786210233` |
| reference | `5M` | `rift-checked-scoped-inferred` | `84.749` | `0.000` | `0.000` | `0/3` | `3.358` | `5000002` | `203833344` | `3953966985786210233` |

Interpretation: the current focused gate still proves allocation placement and
GC/RSS reduction versus heap. Inferred placement is slightly slower than
explicit scoped allocation in this rerun, so the remaining optimization target
is source-shape overhead in the inferred path, not memory-safety correctness.

Scaled focused results, one warmup and three measured runs:

| Shape | Objects | Mode | Median ms | Median GC ms | Max GC ms | Runs with GC | Rift op ms | Rift slow alloc ms | Rift objects | Checksum |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| primitive | `5M` | `heap-immix` | `82.463` | `8.989` | `18.770` | `3/3` | `0.000` | `0.000` | `0` | `-1183547843768457859` |
| primitive | `5M` | `rift-checked-scoped-explicit` | `83.725` | `0.000` | `0.000` | `0/3` | `2.637` | `1.126` | `5000001` | `-1183547843768457859` |
| primitive | `5M` | `rift-checked-scoped-inferred` | `90.815` | `0.000` | `0.000` | `0/3` | `4.512` | `1.556` | `5000001` | `-1183547843768457859` |
| reference | `5M` | `heap-immix` | `327.140` | `247.341` | `380.140` | `2/3` | `0.000` | `0.000` | `0` | `3953966985786210233` |
| reference | `5M` | `rift-checked-scoped-explicit` | `88.500` | `0.000` | `0.000` | `0/3` | `4.335` | `1.327` | `5000002` | `3953966985786210233` |
| reference | `5M` | `rift-checked-scoped-inferred` | `85.566` | `0.000` | `0.000` | `0/3` | `3.458` | `1.254` | `5000002` | `3953966985786210233` |
| reference | `10M` | `heap-immix` | `311.993` | `144.468` | `573.218` | `2/3` | `0.000` | `0.000` | `0` | `-5323545140366634078` |
| reference | `10M` | `rift-checked-scoped-explicit` | `178.104` | `0.000` | `0.000` | `0/3` | `15.778` | `7.423` | `10000002` | `-5323545140366634078` |
| reference | `10M` | `rift-checked-scoped-inferred` | `173.009` | `0.000` | `0.000` | `0/3` | `14.892` | `6.783` | `10000002` | `-5323545140366634078` |

Interpretation:

- The reference-shaped gate is the first positive performance signal for the
  inference track: inferred ordinary `new` matches explicit region allocation
  counts and checksums, eliminates timed GC in the measured section, and is
  slightly faster than the explicit scoped source form at both 5M and 10M.
- The primitive-shaped 5M gate is a useful negative/control result: inferred
  allocation still places the right objects in the region, but the region
  mutator path is slower than both heap and explicit scoped allocation. This
  points to remaining hot-path work around constructor/init lowering,
  allocation-zone attachment, and debug-mode code shape rather than a safety
  failure.
- These rows are focused L2-style gates with internal counters, not L1
  final-clean headline timings. The representative gates below are the
  application-level evidence for the active inference slice.

## Representative Benchmark Gate: Broom Retained Dataflow

`BroomRetainedDataflowMatrix` now includes inferred variants for the
operator-owned checked Rift active-handle backend:

- `checked-rift`: existing explicit `RiftAllocator.allocateOpenHandle(new ...)`
  source form;
- `checked-rift-inferred`: same aggregate/join/q17/shopper logic, same active
  handle, but ordinary `new` for retained records/entries and ordinary
  `new Array` for generated per-group object arrays where the captured
  expected type proves the active owner.

The implementation also temporarily wires `checked-region-scoped-inferred` for
aggregate/join smoke. That row is useful for source compatibility, but the
SafeZone/scoped backend does not expose Rift allocation counters, so the active
`checked-rift-inferred` rows are the allocation-stat evidence.

20k smoke, one run, no warmup:

| Workload | Mode | Median ms | Rift objects | Checksum | Output | Interpretation |
|---|---|---:|---:|---:|---:|---|
| aggregate | `checked-rift` | `2.167` | `35222` | `2757946740166219268` | `15219` | Explicit checked Rift active-handle row. |
| aggregate | `checked-rift-inferred` | `1.957` | `35222` | `2757946740166219268` | `15219` | Inferred ordinary `new` matches explicit allocation count/output. |
| join | `checked-rift` | `1.972` | `20002` | `-4534341871053622537` | `12934` | Explicit checked Rift active-handle row. |
| join | `checked-rift-inferred` | `1.971` | `20002` | `-4534341871053622537` | `12934` | Inferred ordinary `new` matches explicit allocation count/output. |

Follow-up 20k smoke for the remaining generated retained workloads, one run,
no warmup:

| Workload | Mode | Median ms | Rift objects | Checksum | Output | Interpretation |
|---|---|---:|---:|---:|---:|---|
| q17 | `checked-rift` | `3.065` | `29293` | `-3480080246998936527` | `47` | Explicit checked Rift active-handle row. |
| q17 | `checked-rift-inferred` | `2.694` | `29293` | `-3480080246998936527` | `47` | Inferred `CheckedQ17Part`, `CheckedQ17PartEntry`, and `CheckedQ17LineItem` match explicit allocation count/output. |
| shopper | `checked-rift` | `3.638` | `22864` | `-1065252462135954499` | `2859` | Explicit checked Rift active-handle row. |
| shopper | `checked-rift-inferred` | `4.272` | `22864` | `-1065252462135954499` | `2859` | Inferred view/cart/purchase/candidate nodes match explicit allocation count/output. |

Current 1M representative gate, one warmup and three measured runs.
Source: `/private/tmp/rift-inference-broom-20260519/summary.tsv`.

| Workload | Mode | Median ms | Median GC ms | Rift objects | Checksum | Output |
|---|---|---:|---:|---:|---:|---:|
| aggregate | `heap-gc` | `100.245` | `13.241` | `0` | `2843352872537677199` | `708604` |
| aggregate | `checked-rift` | `87.046` | `0.000` | `1708634` | `2843352872537677199` | `708604` |
| aggregate | `checked-rift-inferred` | `86.895` | `0.000` | `1708634` | `2843352872537677199` | `708604` |
| join | `heap-gc` | `97.076` | `9.426` | `0` | `-5733395378394929899` | `681426` |
| join | `checked-rift` | `87.755` | `0.000` | `1000020` | `-5733395378394929899` | `681426` |
| join | `checked-rift-inferred` | `90.148` | `0.000` | `1000020` | `-5733395378394929899` | `681426` |

Current 20M q17/shopper representative gate, one warmup and three measured
runs. Source:
`/Users/siyaoliu/rift/cache/broom-inferred-q17-shopper-20m-l2-20260520/summary.tsv`.

| Workload | Mode | Median ms | Median GC ms | Region op ms | Rift objects | RSS bytes | Checksum | Output |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| q17 | `heap-gc` | `3692.841` | `345.640` | `0.000` | `0` | `258736128` | `-4967241567613708774` | `45598` |
| q17 | `checked-rift` | `2837.754` | `0.000` | `11.100` | `29150680` | `47333376` | `-4967241567613708774` | `45598` |
| q17 | `checked-rift-inferred` | `2905.336` | `0.000` | `13.286` | `29150680` | `47448064` | `-4967241567613708774` | `45598` |
| shopper | `heap-gc` | `4308.726` | `725.361` | `0.000` | `0` | `366444544` | `3163869112359651310` | `2856855` |
| shopper | `checked-rift` | `3998.612` | `0.000` | `28.606` | `22857035` | `65667072` | `3163869112359651310` | `2856855` |
| shopper | `checked-rift-inferred` | `3992.605` | `0.000` | `28.785` | `22857035` | `65667072` | `3163869112359651310` | `2856855` |

Generated array follow-up gate, one warmup and three measured runs. Source:
`/Users/siyaoliu/rift/cache/broom-inferred-arrays-1m-l2-20260521/summary.tsv`.
The explicit checked rows remain explicit active-handle allocation controls.

| Workload | Mode | Median ms | Median GC ms | Region op ms | Rift objects | RSS bytes | Checksum | Output |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| aggregate | `heap-gc` | `150.510` | `5.529` | `0.000` | `0` | `95985664` | `8854638383809110735` | `839789` |
| aggregate | `checked-rift` | `168.010` | `0.000` | `0.784` | `1839798` | `16433152` | `8854638383809110735` | `839789` |
| aggregate | `checked-rift-inferred` | `156.174` | `0.000` | `0.739` | `1839798` | `16424960` | `8854638383809110735` | `839789` |
| join | `heap-gc` | `186.877` | `45.041` | `0.000` | `0` | `190558208` | `3791171928160505090` | `591580` |
| join | `checked-rift` | `145.209` | `0.000` | `0.915` | `1000006` | `26611712` | `3791171928160505090` | `591580` |
| join | `checked-rift-inferred` | `141.424` | `0.000` | `0.905` | `1000006` | `26640384` | `3791171928160505090` | `591580` |
| q17 | `heap-gc` | `168.177` | `13.387` | `0.000` | `0` | `112652288` | `2687651214129999488` | `2093` |
| q17 | `checked-rift` | `155.803` | `0.000` | `0.688` | `1478215` | `16371712` | `2687651214129999488` | `2093` |
| q17 | `checked-rift-inferred` | `154.966` | `0.000` | `0.690` | `1478215` | `16416768` | `2687651214129999488` | `2093` |
| shopper | `heap-gc` | `278.103` | `48.462` | `0.000` | `0` | `199348224` | `-4704623849702867584` | `142731` |
| shopper | `checked-rift` | `249.488` | `0.000` | `1.640` | `1142743` | `32026624` | `-4704623849702867584` | `142731` |
| shopper | `checked-rift-inferred` | `248.765` | `0.000` | `1.617` | `1142743` | `32059392` | `-4704623849702867584` | `142731` |

Allowed claim: Broom now demonstrates inferred ordinary `new` placement across
all four generated retained workloads, including retained records and generated
per-group object arrays, without changing outputs, region allocation counts, or
GC behavior. The q17/shopper record expansion and the generated-array
follow-up are source placement and ergonomics results, not standalone speed
results. It is not enough to complete the performance success criterion alone:
the active goal still requires broader method/effect summaries, polymorphic
safety, synthetic placement, and topology inference before claiming full
ReML/MLKit inference.

## Representative Benchmark Gate: LogHub Retained Session/Join

`LogHubRetainedSessionMatrix` now includes `checked-rift-inferred` for the
retained session and retained join paths. The source-level difference is the
same as the Broom gate: the explicit row allocates retained records through
`RiftAllocator.allocateOpenHandle(new ...)`, while the inferred row uses
ordinary `new` whose expected captured type proves the active
`RiftOpenStreamingHandle` owner.

The run uses the compressed HDFS LogHub source directly:

```text
LOGHUB_SESSION_INPUT=tar.gz:/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1.tar.gz!HDFS.log
```

20k smoke, one run, no warmup:

| Workload | Mode | Median ms | Rift objects | Checksum | Output | Interpretation |
|---|---|---:|---:|---:|---:|---|
| session | `heap-gc` | `178.855` | `0` | `4592543530435702568` | `17218` | Natural heap row over compressed streaming input. |
| session | `checked-rift` | `175.720` | `37221` | `4592543530435702568` | `17218` | Explicit checked Rift active-handle row. |
| session | `checked-rift-inferred` | `175.380` | `37221` | `4592543530435702568` | `17218` | Inferred ordinary `new` matches explicit allocation count/output. |
| join | `heap-gc` | `174.631` | `0` | `-9003390628585301659` | `1577` | Natural heap row over compressed streaming input. |
| join | `checked-rift` | `175.615` | `20002` | `-9003390628585301659` | `1577` | Explicit checked Rift active-handle row. |
| join | `checked-rift-inferred` | `173.539` | `20002` | `-9003390628585301659` | `1577` | Inferred ordinary `new` matches explicit allocation count/output. |

Current 1M real HDFS session gate, one warmup and three measured runs.
Source: `/private/tmp/rift-inference-loghub-hdfs-session-20260519/summary.tsv`.

| Workload | Mode | Median ms | Median GC ms | Max GC ms | Runs with GC | Rift op ms | Rift objects | RSS bytes | Checksum | Output |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| session | `heap-gc` | `7829.601` | `43.508` | `66.022` | `3/3` | `0.000` | `0` | `185368576` | `1179603574147426498` | `831871` |
| session | `checked-rift` | `7794.832` | `0.000` | `0.303` | `1/3` | `0.873` | `1831886` | `41959424` | `1179603574147426498` | `831871` |
| session | `checked-rift-inferred` | `8020.670` | `0.000` | `0.302` | `1/3` | `0.938` | `1831886` | `43008000` | `1179603574147426498` | `831871` |

Allowed claim: this is the second representative benchmark family showing
that inferred ordinary `new` can replace explicit active-handle allocation
without changing logical output or region allocation counts. It is real
compressed streaming input, but not a strong GC-heavy performance row: heap GC
is less than `1%` of elapsed, so parser and archive/line-processing CPU
dominate. In the current 1M rerun, inferred checked Rift keeps the GC/RSS win
versus heap but is slower than explicit checked Rift; profile this source shape
before claiming inference has no application overhead.

Follow-up L4 profile, 2026-05-19:

Source:
`/private/tmp/rift-inference-loghub-profile-20260519-escalated/summary.tsv`.
The first sandboxed profile attempt could not attach to the process with
macOS `sample`; the rerun used the same cases with escalated profiler
permissions.

| Mode | Profile status | Top sampled functions | Region allocation samples | Interpretation |
|---|---|---|---:|---|
| `checked-rift` | ok | `containsAscii` `923`, `stableHash` `698`, `ByteLineReader.append` `265`, `tokenHash` `251`, `ByteLineReader.nextByte` `205` | `5` | Explicit active-handle row is dominated by shared LogHub parsing, token scanning, hashing, and byte-reader work. |
| `checked-rift-inferred` | ok | `containsAscii` `947`, `stableHash` `701`, `ByteLineReader.append` `273`, `tokenHash` `246`, `ByteLineReader.nextByte` `233` | `5` | Inferred active-handle row has the same profile shape. The current slowdown is not explained by a hot region allocator path. |

Profile conclusion: this row should not drive a benchmark-local parser/hash
rewrite. The next general inference/runtime targets remain broader placement
coverage and hot-path quality in rows where allocation is actually visible:
synthetic Scala allocations beyond `Some`/reference-safe tuple factories,
closure/iterator owner
summaries, constructor/init lowering, and operator-owned handle plumbing.

## Representative Benchmark Gate: StreamFlex Design Throughput

`StreamFlexDesignMatrix` now includes `checked-epoch-stream-inferred` for the
StreamFlex-style active-handle backend. The workload models stable heap state,
transient period records in a checked Rift epoch/reset region, and a bounded
capsule sink. The inferred row keeps the same topology and object graph as
`checked-epoch-stream`, but constructs transient `Packet`, `Feature`,
`Decision`, and `Alert` records with ordinary `new` under the active
`RiftOpenStreamingHandle` owner.

20k smoke, one run, no warmup:

| Workload | Mode | Median ms | Median GC ms | Rift objects | Checksum | Output |
|---|---|---:|---:|---:|---:|---:|
| throughput | `gc-heap` | `11.484` | `2.633` | `0` | `3496158305702065933` | `20013` |
| throughput | `checked-epoch-stream` | `8.270` | `0.536` | `500013` | `3496158305702065933` | `20013` |
| throughput | `checked-epoch-stream-inferred` | `11.874` | `0.810` | `500013` | `3496158305702065933` | `20013` |

Current 1M representative throughput gate, one warmup and three measured runs.
Source: `/private/tmp/rift-inference-streamflex-20260519/summary.tsv`.

| Workload | Mode | Median ms | Median GC ms | Max GC ms | Runs with GC | Rift op ms | Rift objects | Checksum | Output |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| throughput | `gc-heap` | `512.936` | `100.127` | `100.925` | `3/3` | `0.000` | `0` | `-7120610804659902001` | `997627` |
| throughput | `checked-epoch-stream` | `377.317` | `0.000` | `0.249` | `1/3` | `1.220` | `24997627` | `-7120610804659902001` | `997627` |
| throughput | `checked-epoch-stream-inferred` | `379.663` | `0.000` | `0.219` | `1/3` | `1.210` | `24997627` | `-7120610804659902001` | `997627` |

Allowed claim: this is the third representative benchmark family for the
current active-handle inference slice. It proves that ordinary inferred `new`
can replace explicit active-handle allocation in a StreamFlex-style
stable/transient/capsule workload while preserving checksum/output and region
allocation counts. The current 1M row is a positive heap-vs-region row and a
near-tie against explicit checked Rift: inferred checked Rift is about `0.6%`
slower than explicit checked Rift while preserving the region allocation count
and eliminating the heap row's measured GC in the timed section. The 20k smoke
remains a reminder that small rows are noisy and should not be overinterpreted.

## Full-File Follow-Up: Wikimedia Retained Clickstream

After the owner-token/generic inference milestone, the full-file Wikimedia
retained clickstream-session L2 row was rerun with an added
`checked-rift-inferred` mode.

Source: `/private/tmp/wikimedia-full-l2-inference-20260519/summary.tsv`.

| Mode | Median ms | GC ms | Region op ms | Region objects | RSS bytes | Checksum | Output |
|---|---:|---:|---:|---:|---:|---:|---:|
| `heap-gc` | `71819.469` | `5671.534` | `0.000` | `0` | `2806775808` | `3903090754337931261` | `33529413` |
| `checked-rift` | `70451.516` | `0.672` | `71.044` | `69391942` | `130547712` | `3903090754337931261` | `33529413` |
| `checked-rift-inferred` | `70022.499` | `0.696` | `79.254` | `69391942` | `130547712` | `3903090754337931261` | `33529413` |

Interpretation: the inferred row matches explicit checked Rift checksum,
output, RSS, and region object count, and is `429.017 ms` faster than explicit
checked Rift in this one-run L2 pass. Compared with heap, inferred checked Rift
removes about `5.67 s` of timed GC and cuts RSS from `2.81 GB` to `130.5 MB`,
but still has about `3.87 s` more non-GC work than heap (`3.79 s` excluding
measured region op time). This improves
the old full-file result but does not remove the main lesson: region placement
wins RSS/fixed-memory/GC predictability, while shared parsing/hash/object-shape
work still limits elapsed speedup. Keep this as full-file one-run evidence
until repeated as a 3-run median.

## Remaining Gaps

- No broad method, closure, or polymorphic effect summaries yet. The current
  method slice only handles direct-return allocation, returned immutable
  method-local allocation, returned method-local block-shaped RHS allocation,
  block-final direct allocation, simple forwarded
  method-return summaries, one forwarded local-alias wrapper shape, forwarded
  branch/match wrapper shapes, simple branch-returned direct allocation,
  simple branch-returned local allocation, branch/match-returned local
  block-shaped RHS allocation, and simple match-returned
  direct/local allocation, when the region owner is an explicit method
  parameter.
- First call-site method-argument placement is implemented for direct
  arguments whose parameter type names an in-scope checked owner, for example
  `def consume(x: T^{region}); consume(new T(...))`. A first owner-token
  substitution case is also implemented for the valid dependent parameter
  order `def consume(using r)(x: T^{r}); consume(using region)(new T(...))`.
  The same path now accepts one local polymorphic owner-token consumer shape
  with a fully applied type argument, while preserving heap fallback/rejection
  for unproven generic hiding and widened escapes. Broader method/effect-summary
  substitution for arbitrary callees remains future work.
- First page/window/transaction child-region local placement is implemented for locals
  returned by selected checked owner helpers: `pageTokenAppendRegionFor`,
  `pageTokenMapFilterRegionFor`, `pageTokenCountByKeyRegionFor`,
  `transactionRegionFor`, and `chunkAppendRegionFor`.
  `epochFoldRegionFor` now joins that selected helper set for epoch-fold bucket
  records: ordinary `new` values typed by the returned child region can be
  widened to the parent stream owner before `putEpochFold`, while unrooted
  metadata remains rejected.
  The newest open-child-owner slice also validates ordinary `new` through
  `pageTokenAppendOpenRegionFor`, `pageTokenMapFilterOpenRegionFor`,
  `pageTokenCountByKeyOpenRegionFor`, and `epochBufferOpenRegionFor`,
  replacing explicit `allocOpen(new ...)` in those operator-owned active paths.
  Broader automatic bucket/operator placement remains future work.
- Active open-handle inference is implemented for the first local/captured
  source forms and Broom aggregate/join representative rows. It is not yet
  propagated through all checked Rift streaming/page/window operators.
- No broad generic container placement yet. The current `ObjectBuffer` and
  `RegionBuffer` slices handle proven direct/synthetic/closure values at
  explicit owner-token append calls, not arbitrary container flows.
  A narrow local, method-returned, returned-local, and branch/match-forwarded `Cell[A]`
  expected-type placement slice is now accepted and runtime-proven, and
  explicitly region-typed selected local `Cell[A^{region}]^{region}` candidates
  are now runtime-proven through a polymorphic owner-token consumer
  `Cell[A^{r}]^{r}`. Untyped selected generic aliases remain outside the
  accepted boundary because capture checking loses the owner before the current
  post-capture inference phase can repair it. The first captured array
  expected-type slice is accepted and runtime-proven for local region-owned
  arrays, explicit-region-parameter method returns, and simple
  direct/local-alias/branch/match forwarding wrappers. Inline direct
  construction stores into `Array[T^{r}]^{r}` are now accepted when the element
  type carries the same checked owner, and the same element-owner rule is
  validated for `Some(new T(...))` stored into
  `Array[Option[T^{r}]^{r}]^{r}`. Broader generic retention,
  callbacks, arrays flowing through generic APIs, and hidden container flows
  still need stronger effect/capture summaries.
- No broad page/window child-bucket or stream-window rank/table-rank topology
  placement yet. Priority-queue owner-token inference is validated for the
  scoped `RegionPriorityQueue` family, and selected synthetic aliases are now
  validated at checked stream-window rank/table-rank APIs. The page-token
  append/map-filter/count-by-key child-region local slices plus the
  page-token/epoch-buffer open-child slices prove selected independently
  expiring child owners. Overlapping stream bucket operators still need
  broader owner proofs.
- No primitive/boxed tuple fields,
  broader Option container flows, iterators, boxed keys, temporary
  strings, or collection-wrapper placement yet. The validated common Scala
  allocation shapes so far are captured `Some(...)` through exact `Some` and
  widened `Option` expected types, allocation-free `None` under region-owned
  `Option` expected types, local and explicit-region-method
  `Some(new T(...))`/`None` optional-result flows, method-returned/returned-local `Some`
  factories, branch/match forwarded method-returned `Option = Some(...)`
  factories, inline `Some(new T(...))`/`Option(new T(...))` stores into
  region-owned arrays, closure objects stored into region-owned arrays and
  checked owner-token containers,
  plus reference-only captured tuple factories for `scala.TupleN.apply`
  arities 2 through 22, with Tuple3 validating the first higher-arity
  local/argument/method-return shapes, method-returned/returned-local
  `Tuple2(...)` factories, branch/match forwarded method-returned `Tuple2(...)`
  factories, and direct nested constructor arguments in proven region-owned
  constructors/factories. The current primitive tuple negatives deliberately
  reject `Tuple2[Int, T^{r}]^{r}`-style shapes because the primitive component
  becomes a heap box before the tuple constructor can store it safely in a
  checked region.
- Immutable checked owner aliases are now implemented for local values such as
  `val owner = region`, and runtime allocation stats prove `T^{owner}` direct
  construction is region allocated. This is alias tracking only; aliases do
  not create new runtime owner handles and do not by themselves solve closure
  body allocation. The newest canonicalization follow-up lets method-return
  summaries reconcile `T^{owner}` locals with `T^{r}` result types when
  `owner` is an immutable alias of `r`; runtime allocation stats prove the
  returned object is still region allocated.
- Two local synthetic-closure object slices are implemented. A local
  nonescaping closure can be allocated in the checked region either when a
  function-captured expected type proves the owner or when a captured
  region-local value proves the owner; unrooted heap captures are rejected in
  both paths. The method/closure follow-up now validates a capture-free local
  closure returned from an explicit checked region-parameter method, with
  runtime allocation stats proving the materialized closure object is region
  allocated and a compiler negative rejecting unrooted heap captures. The same
  method-return shape is now validated for closures that capture a
  region-local value, and runtime allocation stats prove both the captured
  value and returned closure object land in the checked region. Narrow
  captured-owner closure-body placement is implemented when the closure
  explicitly captures the same runtime checked owner term, and closure-object
  placement is now validated at owner-proven array-store boundaries for direct
  and selected immutable local closures plus explicit owner-token container
  boundaries for checked buffers and ordinary priority queues. Hidden owner
  capture remains future work when the owner appears only in types; escaping
  closures and broader closure effect summaries also remain future work.
- Inferred array allocation is validated for captured local arrays and
  explicit-region-parameter method-returned arrays, and direct/local-alias
  forwarding wrappers with expected types such as
  `Array[T^{region}]^{region}` or `Array[T^{r}]^{r}`. Runtime allocation
  stats prove those arrays and named region-local element objects are placed in
  Rift region memory. Inline array-store placement is now validated for
  direct objects, `Some`/`Option.apply`/`Tuple2` factories, and direct or
  selected immutable local closure objects when the array element type carries
  the checked owner. Arrays flowing through generic APIs still need stronger
  method/effect summaries.
- No compiler-inserted region boundaries yet.
- No performance sweep yet; this milestone is safety and compiler capability.

## Next Acceptance Target

The next milestone should extend method/closure allocation/effect summaries
beyond explicit-region-parameter direct returns, then add ReML-style probes
showing:

- local method returns region value safely in more expression forms when the
  runtime handle is explicit or inserted by a proven transformation;
- nonescaping closure captures region value safely;
- escaping closure is rejected;
- additional polymorphic consumers beyond the validated local owner-token
  `Cell[A^{r}]^{r}` shape are accepted only with explicit effect/owner
  summaries;
- widened/generic retained containers are rejected.
