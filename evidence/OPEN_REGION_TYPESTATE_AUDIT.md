# Open Region Typestate Audit

Date: 2026-05-11
Last updated: 2026-05-11 15:35 CEST

Status: implementation audit plus safety-probe checkpoint. This file records
which checked region helpers are allocation-capable active handles, which paths
remain defensive, and where root-free eligibility is still a design target
rather than a safety claim.

## Result

The first internal active/closed typestate slice is complete for the current
checked APIs:

- `OpenStreamingRegion` is the only checked handle accepted by `allocOpen`.
- Checked user code cannot call `close()` or `reset()` through an open epoch
  handle.
- `RiftRegion.epoch` open handles cannot escape to the parent stream.
- Generic/public `StreamingRegion` allocation remains defensive.
- Public stale bucket/region paths still throw after close for both Rift and
  SafeZone-backed checked regions.

No additional hot-path stale/open checks were removed in this checkpoint.
Page-token and epoch-buffer open helpers are operator-owned fast paths, but
their open handles are not yet statically linear: user code can bind the handle
inside the stream and the compiler does not prove it cannot be used after a
later operator close. That is acceptable for `allocOpen` in the current
benchmark/operator-owned code, but it is not enough to remove public defensive
checks.

## Helper Classification

| Helper/API | Classification | Allocation handle returned | Close owner | Current check policy |
|---|---|---|---|---|
| `RiftRegion.epoch { epoch ?=> ... }` | active-handle boundary | `OpenStreamingRegion` | `epoch` boundary implementation | `allocOpen` skips per-allocation `checkOpen`; compiler rejects user `close`/`reset` and parent escape. |
| `pageTokenAppendOpenRegionFor` | operator-owned active helper | `OpenStreamingRegion` | page-token bucket close helpers | `allocOpen` fast path allowed; public stale bucket/region APIs stay defensive. |
| `pageTokenMapFilterOpenRegionFor` | operator-owned active helper | `OpenStreamingRegion` | page-token map/filter close helpers | Same as page-token append. |
| `pageTokenCountByKeyOpenRegionFor` | operator-owned active helper | `OpenStreamingRegion` | page-token count-by-key close helpers | Same as page-token append; aggregate metadata closes without record traversal when query work is complete on append. |
| `epochBufferOpenRegionFor` | operator-owned active helper | `OpenStreamingRegion` | epoch-buffer close helpers | `allocOpen` fast path allowed; public buffer region access remains defensive. |
| `childStreaming` | public defensive child region | `StreamingRegion` | caller through `close()` | Generic `alloc` checks open; runtime probe rejects allocation after close. |
| `childWindow` / `childBucket` | public defensive owner-token helpers | `StreamingRegion` through child | structured child close helper | Generic `alloc` checks open; stale bucket probes remain required before any new check removal. |
| `transactionRegionFor` | public defensive transaction region | `StreamingRegion` | `closeTransactionRegion` | Not converted to `OpenStreamingRegion`; keep defensive until a transaction-owned open path is separately probed. |

## Metadata And Bridge Probes

The compiler suite now covers static/immutable metadata and `HeapRoot` bridge
handles through these open allocation shapes:

| Shape | Positive probes | Negative probes |
|---|---|---|
| Direct `RiftRegion.epoch` open allocation | static metadata, `HeapRoot` bridge | direct unrooted heap object through existing allocation guard |
| Page-token append open allocation | static metadata, `HeapRoot` bridge | unrooted dynamic heap metadata |
| Page-token map/filter open allocation | static metadata, `HeapRoot` bridge | unrooted dynamic heap metadata |
| Page-token count-by-key open allocation | static metadata, `HeapRoot` bridge | unrooted dynamic heap metadata |
| Epoch buffer open allocation | static metadata, `HeapRoot` bridge | unrooted dynamic heap metadata |
| ReML-style generic hiding | local polymorphic consumer accepted | generic heap retention, widened `AnyRef`, heap arrays, escaping closures rejected |

Important limitation: the operator metadata probes work when the event type is
defined inside the stream lifetime so the field capability is expressed as
`{stream}`. Event classes with externally inferred metadata root capabilities
still hit capture-precision limits in operator type parameters. Treat that as a
compiler/API design gap, not a runtime safety failure.

## Root-Free Eligibility Status

Root-free checked SafeZone-backed safety is still not claimed.

Required rejection coverage is now mostly present at the compiler-probe level:

- no unrooted dynamic heap references in checked allocation;
- no heap-retains-region;
- no outer-retains-inner escape in current owner-token shapes;
- no escaping closures hiding region values;
- no ReML-style generic hiding through containers, arrays, or `AnyRef`.

But root-free lowering also needs a positive eligibility mode that rejects
`HeapRoot` use and maps eligible checked code to a no-root backend. That mode
does not exist yet. Until it does, `safezone-rootless-32k` and any
rootless-checked row remain unsafe or lower-bound controls only.

## Runtime Probe Additions

New runtime probes validate stale public handles:

- `pageTokenAppendRegionRejectsAllocationAfterCloseAll`;
- `safeZoneBackedPageTokenAppendRegionRejectsAllocationAfterCloseAll`.

These complement the existing child-streaming, page-token partial close,
zero-record close, no-drain close, and epoch-buffer close tests.

## Validation

Validated on 2026-05-11:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`:
  `141/141` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`:
  `64/64` passed.
