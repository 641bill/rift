# Rift Evaluation Summary Tables

Date: 2026-05-01
Last updated: 2026-05-07 22:34 CEST

Status: seeded summary pack for the comprehensive evaluation. Rows below are
current checked-in evidence unless marked pending rerun.

## Post Fast-Path Selected Sweep: 2026-05-07

Source: `evidence/POST_FAST_PATH_SELECTED_SWEEP_2026_05_07.md`

This is a post-fast-path evidence pass from the current dirty page-token
checkpoint, not a clean commit-bound headline sweep. It reruns selected rows
after `StreamAppendCursor.nextOrNull()`, page-token-owned batch close, and the
monotonic current-bucket fast path.

| Area | Main result | Interpretation |
|---|---|---|
| Focused page-token append | checked scoped page-token `27.549 ms`, checked Rift page-token `29.319 ms`, heap `36.920 ms` | batch-close/current-bucket fast path keeps linked page-token ahead of chunk-token |
| Dataflow SELECT | checked scoped page-token `18.572 ms`, checked Rift page-token `19.503 ms`, heap `28.942 ms`, improved SafeZone `22.463 ms` | reusable page-token SELECT remains a strong checked/operator win |
| Dataflow AGGREGATE | checked exact-array aggregate `38.198 ms`, heap `52.071 ms`, improved SafeZone `40.596 ms` | checked aggregate wins here, but this is not the reusable `EpochFold` row |
| Dataflow JOIN | improved SafeZone `23.459 ms`, checked Rift `24.183 ms`, heap `31.760 ms` | checked still beats heap, but improved SafeZone wins the same-run selected pass |
| NEXMark Beam-default q3/q8/q9/q11 | checked q3 `285.356 ms`, q8 `443.020 ms`, q9 `724.479 ms`, q11 `209.918 ms` | generated methodology rows remain positive; q9 has the largest selected GC reduction |
| Common Crawl-shaped q1 | checked scoped page-token `3840.668 ms`, checked Rift page-token `4069.265 ms`, trusted Streaming `4492.936 ms`, heap `5618.631 ms` with `1655.357 ms` GC | strongest checked generated object-pressure row; elapsed/GC win, not RSS win |
| Common Crawl-shaped q2 | checked scoped page-token `3839.158 ms`, checked Rift page-token `4041.548 ms`, trusted Streaming `4205.312 ms`, heap `5303.179 ms` with `1599.698 ms` GC | strongest checked generated window row; checked page-token now beats trusted Streaming |
| DSPBench Fraud q2 | checked scoped page-token `818.574 ms`, trusted Streaming `834.447 ms`, checked Rift page-token `851.488 ms`, heap `862.834 ms` | dirty direction check: checked scoped is fastest here, but use the committed-code row below for conservative reporting |

Selection consequence: `checked-page-token` and the SafeZone-backed scoped
checked backend are now stronger public candidates. `EpochFold`, TableRank,
chunk-token, and rank-heavy operators remain gated.

## Clean Post-Fast-Path Baseline And Cost Split: 2026-05-07

Source rows:

- `cache/perf-eval/2026-05-07-clean-post-fast-path-selected/`
- `cache/perf-eval/2026-05-07-page-token-cost-1m-baseline/`
- `cache/perf-eval/2026-05-07-page-token-cost-1m-safe-fast-path/`
- `cache/perf-eval/2026-05-07-page-token-focused-post-nodrain/`

| Area | Main result | Interpretation |
|---|---|---|
| Focused page-token append | checked scoped page-token `27.240 ms`, checked page-token `28.397 ms`, heap `36.722 ms` | clean committed rerun confirms the page-token headline path did not regress |
| Cost matrix append-only | checked scoped page-token `74.743 ms`, checked page-token `77.185 ms`, heap `78.130 ms` after no-drain and safe same-bucket tightening | no-drain close is safe, but not the main speedup; allocation/query CPU dominates |
| Cost matrix append-drain | checked scoped page-token `81.628 ms`, heap `83.447 ms` | cursor traversal remains a small cost; checked scoped is modestly faster while removing timed GC |
| Cost matrix append-aggregate | checked scoped page-token `82.623 ms`, heap `85.500 ms` | aggregate-on-append shape is competitive, but not a large standalone win |
| Dataflow clean selected | SELECT scoped page-token `18.326 ms`; checked RegionBuffer SELECT/AGG/JOIN `20.266/37.223/21.084 ms` vs heap `28.158/48.687/31.460 ms` | prior-work-shaped rows remain positive from the clean checkpoint |
| NEXMark clean selected | checked q3/q8/q9/q11 `285.666/436.804/733.083/212.092 ms` vs heap `308.049/461.542/791.244/214.268 ms` | generated Beam-default methodology rows remain modest checked wins |
| Common Crawl-shaped clean selected | q1 checked scoped page-token `3759.175 ms` vs heap `5466.724 ms`; q2 checked scoped rerun `3784.863 ms` vs heap `5213.380 ms` | generated GC-heavy stressor remains the strongest checked stream win |
| DSPBench Fraud q2 committed-code safe-fast-path | trusted Streaming `788.040 ms`, checked scoped page-token `810.770 ms`, heap `820.945 ms` | checked scoped remains a modest real-input/RSS win, but trusted is faster in this rerun |

## Page-Token Live-Length Bookkeeping Rerun: 2026-05-07

Source rows:

- `cache/checked-page-token-no-length-1m-2026-05-07/page-token/`
- `cache/checked-page-token-no-length-1m-2026-05-07/count-by-key/`
- `cache/dspbench-fraud-q2-page-token-no-length-1m-2026-05-07/`

| Area | Main result | Interpretation |
|---|---|---|
| Focused page-token cost split | checked scoped append-only/drain/aggregate `77.135/88.840/85.362 ms` vs heap `81.535/90.374/86.988 ms` | removing generic live-length bookkeeping is valid and keeps scoped page-token modestly positive, but it is not a large speedup |
| Focused count-by-key | checked scoped count-by-key `102.504 ms`, checked Rift count-by-key `104.813 ms`, heap `114.143 ms` with `15.091 ms` GC | no-drain aggregate remains the best focused win from this specific cleanup; checked scoped cuts RSS from `146604032` to `83279872` bytes |
| DSPBench Fraud q2 | trusted Streaming `832.012 ms`, checked scoped page-token `843.380 ms`, heap `842.739 ms` | real-input q2 is now a checked RSS/GC near-tie, not a checked throughput win; next optimization should target allocation lowering rather than bucket bookkeeping |

## Page-Token Owned Cursor Rerun: 2026-05-07

Source rows:

- `cache/checked-page-token-cost-nextowned-1m-2026-05-07/`
- `cache/dspbench-fraud-q2-nextowned-1m-2026-05-07/`
- `cache/common-crawl-page-token-nextowned-1m-2026-05-07/`

| Area | Main result | Interpretation |
|---|---|---|
| Focused page-token cost split | checked scoped append-only/drain/aggregate `73.590/83.997/81.296 ms` vs heap `79.786/87.198/84.703 ms` | `nextOwnedOrNull()` removes per-record link clearing under page-token static ownership; scoped checked improves by about `3.5-4.8 ms` versus the previous no-length rows |
| DSPBench Fraud q2 | trusted Streaming `785.682 ms`, checked scoped page-token `800.369 ms`, heap `807.974 ms` | real-input q2 becomes a modest checked elapsed/RSS win, while trusted Streaming remains the lower bound |
| Common Crawl-shaped q1 | checked scoped page-token `3643.680 ms`, checked Rift page-token `3877.427 ms`, heap `5392.344 ms` with `1577.850 ms` GC | strongest generated checked stream-object row improves; RSS remains a caveat |
| Common Crawl-shaped q2 | checked scoped page-token `3790.138 ms`, checked Rift page-token `4029.776 ms`, heap `5201.862 ms` with `1579.132 ms` GC | strongest generated checked window row remains positive after the owned-cursor cleanup |

## Page-Token Open-Allocation Rerun: 2026-05-07

Source rows:

- `cache/checked-page-token-openalloc-1m-default-2026-05-07/`
- `cache/checked-page-token-openalloc-1m-countbykey-2026-05-07/`
- `cache/dspbench-fraud-q2-openalloc-1m-2026-05-07/`
- `cache/common-crawl-shaped-openalloc-q1q2-1m-2026-05-07/`

| Area | Main result | Interpretation |
|---|---|---|
| Open checked allocation path | `OpenStreamingRegion`/`allocOpen` routes operator-owned page-token object allocation around generic checked `allocImpl/checkOpen` | static-safety cleanup is validated; public low-level checked APIs remain defensive |
| Focused page-token cost split | checked scoped append-only/drain/aggregate `73.632/83.177/82.198 ms` vs heap `76.295/85.873/84.354 ms` | modest focused wins; aggregate is not materially better than the prior owned-cursor row |
| Focused count-by-key | checked scoped count-by-key `95.946 ms` vs heap `103.946 ms`, with RSS `83296256` vs heap `146587648` bytes | clearest focused improvement from this checkpoint; still a modest operator win |
| DSPBench Fraud q2 | trusted Streaming `778.975 ms`, checked scoped page-token `797.782 ms`, heap `806.697 ms` | real-input q2 modest checked elapsed/RSS win remains; trusted Streaming is still the lower bound |
| Common Crawl-shaped q1 | checked scoped page-token `3707.214 ms`, checked Rift page-token `3933.900 ms`, heap `5577.965 ms` with `1741.640 ms` GC | generated object-pressure row stays strongest checked throughput/GC win; RSS is higher than heap |
| Common Crawl-shaped q2 | checked scoped page-token `3902.795 ms`, checked Rift page-token `4040.310 ms`, heap `5183.074 ms` with `1565.074 ms` GC | generated window row remains strong; open allocation is not the dominant reason for the win |

## DSPBench Log Processing Real-Input Follow-Up: 2026-05-07

Source rows:

- `cache/dspbench-log-smoke-2026-05-07/`
- `cache/dspbench-log-100k-2026-05-07/`
- `cache/dspbench-log-1m-2026-05-07/`

| Area | Main result | Interpretation |
|---|---|---|
| DSPBench Log q0 parse | trusted Streaming `1443.724 ms`, heap `1462.188 ms`, checked scoped page-token `1462.524 ms` | parser/replay dominated; trusted/SafeZone rows shave GC but checked scoped is tied with heap |
| DSPBench Log q1 status | improved SafeZone `1645.205 ms`, trusted Streaming `1647.471 ms`, checked scoped page-token `1654.431 ms`, heap `1669.816 ms` | modest safe/trusted throughput/GC row; checked scoped beats heap but not the faster safe/trusted rows |
| DSPBench Log q2 window | checked scoped page-token `1733.654 ms`, trusted Streaming `1737.469 ms`, heap `1750.291 ms`; heap max GC `88.210 ms` vs checked max GC `18.584 ms` | best log row: real-input modest checked throughput/GC-tail win, but RSS is higher and heap GC is only about `2.6%` of elapsed |

## Staged Headline Sweep: 2026-05-06

Source: `evidence/COMPREHENSIVE_SWEEP_2026_05_06.md`

Run ids:

- `2026-05-05-comprehensive-headline`
- `2026-05-05-comprehensive-headline-cont`

The first run completed compile/prior/checked rows and was stopped after it
entered an unwanted `current-safezone` cost row. The continuation completed
SafeZone-cost and stream rows with `current-default` excluded from
SafeZone-cost. Competitive rows skip current SafeZone by default.

| Area | Main result | Interpretation |
|---|---|---|
| Dataflow SELECT | scoped page-token `18.458 ms`, Rift page-token `20.479 ms`, heap `29.347 ms` with `7.304 ms` GC | reusable page-token SELECT remains a clear checked win |
| Dataflow AGGREGATE | current checked exact-array aggregate `40.098 ms`, heap `53.677 ms`; true `EpochFold` `92.923 ms` | checked aggregate row wins, but reusable `EpochFold` is still negative/gated |
| Dataflow JOIN | checked Rift `21.607 ms`, improved SafeZone `23.846 ms`, heap `33.438 ms` | checked beats heap and SafeZone in this rerun |
| StreamFlex | trusted Rift HP `36.436 ms`; scoped checked TransactionRegion `39.019 ms`; heap `42.860 ms`; improved SafeZone `41.327 ms` | TransactionRegion is the best checked StreamFlex shape; trusted Rift remains fastest |
| Object allocation lowering | checked SafeZone-backed `14.903 ms`, checked Rift `16.039 ms`, heap `21.885 ms` | focused checked allocation is not the remaining bottleneck |
| Checked append/window | scoped EpochBuffer `26.461 ms`, scoped page-token `26.883 ms`, heap Immix `36.944 ms` with `10.900 ms` GC | cheap checked append operators beat heap |
| StreamWindowRank | checked `344.918 ms`, heap `227.736 ms` | rank/index maintenance remains a negative control |
| NEXMark Beam-default | checked Rift fastest on q0/q1/q2/q3/q4/q5/q8/q9/q11; q9 checked `708.391 ms` vs heap `779.032 ms` | broad generated methodology win, mostly modest |
| Common Crawl-shaped q1 | checked SafeZone page-token `3696.284 ms`, checked Rift page-token `3905.285 ms`, heap `5350.531 ms` with `1517.640 ms` GC | strongest checked generated stream win |
| Common Crawl-shaped q2 | checked SafeZone page-token `3732.171 ms`, checked Rift page-token `3972.493 ms`, heap `5183.656 ms` with `1526.751 ms` GC | strongest checked generated window win |
| Common Crawl-shaped q3 | heap `10188.412 ms`; SafeZone-family rows can be much slower | parser-scratch shape is negative/mixed, not a case-study target |
| GH Archive-shaped | q1 trusted Streaming `246.174 ms` and q2 trusted HP `233.427 ms`; heap q1/q2 `286.721` / `268.717 ms` | generated GH-shaped row favors regions; still not real-input proof |
| GH Archive file-backed 2h, legacy string parser | q1 Streaming `7448.838 ms`, checked scoped page-token `7489.923 ms`, heap `7549.355 ms`; q2 Streaming `7442.005 ms`, checked scoped page-token `7498.263 ms`, heap `7641.540 ms` | real file-backed RSS/fixed-memory row: heap around `2.43 GB` RSS, region rows around `0.72-0.93 GB`; profile says parser/string/decompression dominates |
| GH Archive file-backed 2h, byte-slice parser | q1 heap `3806.120 ms`, Streaming `3626.219 ms`, checked scoped page-token `3629.193 ms`; q2 heap `3756.950 ms`, Streaming `3645.458 ms`, checked scoped page-token `3626.107 ms` | parser-scratch follow-up: real file-backed modest throughput/RSS/tail win; region rows use about `211 MB` RSS and zero timed GC vs heap about `290 MB` RSS with GC in 2/3 runs. Not GC-heavy: heap GC is only about `1.5-1.6%` of elapsed. |
| LogHub BGL real log | 1M q1 heap `5568.252 ms`, Streaming `5491.033 ms`, checked scoped page-token `5552.988 ms`; 1M q2 heap `5646.824 ms`, improved-32k `5509.481 ms`, checked scoped page-token `5636.357 ms`; full-file q2 heap `32161.391 ms`, Streaming `30899.595 ms`, checked scoped page-token `31165.087 ms` | real file-backed multi-million-line system-log control. Region rows remove timed GC and modestly improve selected rows; full-file q2 heap GC is `595.599 ms`, still under 2% of elapsed, so this is not the missing GC-heavy case. |
| DSPBench Spike/Fraud/Log real-input | Spike 1M over `sensors.dat`; Fraud 1M over `credit-card.dat`; Log 1M over `http-server.log` | Spike q1 checked scoped `1163.045 ms` vs heap `1187.525 ms`; open-allocation Fraud q2 checked scoped `797.782 ms` vs heap `806.697 ms`; Log q2 checked scoped `1733.654 ms` vs heap `1750.291 ms` | Fraud q2 and Log q2 are modest real-input checked/RSS or GC-tail rows. Neither is the missing flagship because trusted Streaming/SafeZone often remain competitive, RSS can rise, and heap GC is visible but not dominant. |
| ReML-shaped Tier 1 | checked stream `msort` `104.358 ms` vs heap `124.983 ms`; `msort-r` `104.929 ms` vs heap `126.163 ms`; checked scoped `ratio` `48.929 ms` vs heap `51.302 ms` | local Scala Native port evidence for MLKit/ReML lineage; not exact ReML reproduction |
| Linear Road | heap fastest or tied on q0/q1/q2 despite GC reduction in region modes | ceiling/control evidence |

Key SafeZone-cost decomposition from the corrected continuation:

| Benchmark/config | Median ms | Claim ms | Reclaim ms | Root add+remove ms | Interpretation |
|---|---:|---:|---:|---:|---|
| GCBench unsafe 32K | `697.984` | `0.977` | `1.321` | `0.000` | rootless lower bound |
| GCBench improved 32K | `703.092` | `2.556` | `1.326` | `1.596` | close to rootless |
| ListOfLists linked improved 32K | `32837.097` | `93.615` | `60.867` | `58.205` | faster than rootless in trace mode |
| ListOfLists linked rootless 32K | `33588.729` | `31.243` | `52.382` | `0.000` | root work gone, total still dominated elsewhere |
| Common Crawl q1 improved 32K | `8443.875` | `54.623` | `42.836` | `45.283` | trace-mode diagnostic |
| Common Crawl q1 rootless 32K | `8459.317` | `16.318` | `31.718` | `0.000` | rootless does not improve total in trace mode |

## Superseded Clean Reusable-Operator Sweep: 2026-05-05

Source: `evidence/COMPREHENSIVE_SWEEP_2026_05_05.md`

These rows are retained for provenance. Prefer the 2026-05-06 staged headline
sweep above where rows overlap.

Run ids:

- `2026-05-05-reusable-operators-preflight`
- `2026-05-05-reusable-operators-prior-checked-streams-smoke`
- `2026-05-05-reusable-operators-core-smoke-small`
- `2026-05-05-reusable-operators-prior-checked-headline`
- `2026-05-05-reusable-operators-streams-headline`

| Area | Main clean result | Interpretation |
|---|---|---|
| Dataflow SELECT | scoped `PageTokenMapFilter` `18.685 ms`; Rift `PageTokenMapFilter` `20.129 ms` | reusable page-token SELECT clears the gate |
| Dataflow AGGREGATE | true reusable `EpochFold` `94.378 ms`; current checked exact-array aggregate `39.759 ms` | `EpochFold` is correct but speed-gated |
| Checked append | scoped page-token `27.004 ms`, Rift page-token `28.341 ms`, heap `37.490 ms` | operator-owned checked append remains a win |
| Object allocation lowering | checked SafeZone-backed `15.166 ms`, checked Rift `16.734 ms`, heap `20.797 ms` | raw checked allocation is not the primary remaining bottleneck |
| Common Crawl-shaped q1 | scoped page-token `3654.143 ms`, Rift page-token `3856.625 ms`, heap `5313.928 ms` with `1517.397 ms` GC | strongest generated checked stream win |
| Common Crawl-shaped q2 | scoped page-token `3713.483 ms`, Rift page-token `3927.449 ms`, heap `5250.408 ms` with `1628.382 ms` GC | strongest generated checked window win |
| NEXMark Beam-default | checked q3 `278.455 ms`, q8 `429.087 ms`, q9 `711.256 ms`, q11 `211.000 ms` | modest generated methodology wins |
| GH Archive shaped q1 | Rift HP `246.205 ms`, checked page-token `250.705 ms`, heap `284.689 ms` | generated-shaped row wins; real-input case remains separate |
| Core smoke | fixed smoke dimensions completed | core headline remains the 2026-05-01 rerun unless a separate long core job is launched |

## Clean Headline Subset: 2026-05-01

Source: `evidence/HEADLINE_CORE_PRIOR_CHECKED_2026_05_01.md`

Run id: `2026-05-01-headline-core-prior-checked`

Superseding rerun: `evidence/HEADLINE_CORE_PRIOR_CHECKED_RERUN_2026_05_01.md`
with run id `2026-05-01-headline-core-prior-checked-rerun`.

Stream headline leg: `evidence/HEADLINE_STREAMS_2026_05_01.md`, run id
`2026-05-01-headline-streams`.

DEBS bounded 1M leg: `evidence/HEADLINE_DEBS_1M_2026_05_01.md`, run id
`2026-05-01-headline-debs-1m`.

UnsafeZone-HP DEBS bounded 1M leg:
`evidence/HEADLINE_UNSAFEZONE_DEBS_1M_2026_05_01.md`, run id
`2026-05-01-unsafezone-debs-1m`.

UnsafeZone-HP baseline checkpoint:
`evidence/UNSAFEZONE_HP_BASELINE_MATRIX.md`. First clean core/prior headline
medians with this mode are in
`evidence/HEADLINE_UNSAFEZONE_CORE_PRIOR_2026_05_01.md`, run id
`2026-05-01-unsafezone-core-prior`. It uses
`SAFEZONE_ROOTS_MODE=3 SAFEZONE_PAGE_SIZE=32768` as a benchmark-only SafeZone
no-root baseline.

UnsafeZone-HP stream leg:
`evidence/HEADLINE_UNSAFEZONE_STREAMS_2026_05_01.md`, run id
`2026-05-01-unsafezone-streams`.

SafeZone cost-decomposition headline:
`evidence/SAFEZONE_COST_MATRIX.md`, run id `2026-05-01-safezone-cost`. It
records `SAFEZONE_TRACE=1` pool counters alongside benchmark medians/RSS and
supersedes the earlier scaffold-only status.

Common Crawl-like expansion:
`evidence/COMMON_CRAWL_LIKE_MATRIX.md`. The WET-shaped runner now includes
`q2-domain-window` and `q3-parser-scratch`; 100k/1M generated follow-up rows
now exist for heap, SafeZone-family labels, UnsafeZone-HP, and trusted Rift.
The 2026-05-02 q1/q2 rerun after Rift fast-allocation counter cleanup
supersedes the earlier q1/q2 ordering. The checked `StreamAppendWindow`
q1/q2 follow-up validates safe record placement but does not clear the
application-scale performance gate.

Checked SafeZone-backed backend:
`evidence/CHECKED_SAFEZONE_BACKEND_MATRIX.md`. The v1 backend keeps the checked
Rift API but delegates object allocation to SafeZone internals. It passes the
focused append-window gate at 1M (`29.444 ms` vs current checked cursor
`30.922 ms`) and improves Common Crawl-like checked q1/q2 by `4.9-5.7%`, but
misses the application gate against trusted Rift/improved SafeZone.

Checked page/token append operator:
`evidence/CHECKED_PAGE_TOKEN_APPEND_MATRIX.md`. `StreamPageTokenAppendWindow`
is the first overhead-removal result after the report rewrite: it removes
operator-owned per-record child-bucket open checks, child-region lookups, and
now page-token-owned leftover-drain/monotonic close-open overhead. The latest
focused 1M fast-path row is `29.319 ms` (`27.549 ms` for the SafeZone-backed
variant) versus heap `36.920 ms`; chunk-token remains slower. Generated Common
Crawl-shaped q1/q2 still clear the checked application-shaped gate, and the
100k fast-path regression has checked SafeZone-backed page-token fastest on
both q1 (`370.758 ms`) and q2 (`377.482 ms`).

Object allocation lowering:
`evidence/OBJECT_ALLOCATION_LOWERING_MATRIX.md`. This new scaffold isolates
ordinary Scala object construction through heap, trusted Rift, checked Rift,
and checked SafeZone-backed allocation paths without stream-window or query
traversal. The first retained-buffer rows mixed in generic `RegionBuffer`
overhead; the refined retained-region-array rows show that raw checked
allocation is not the main bottleneck in this shape. At 10M, heap is
`271.121 ms` with `105.807 ms` median GC and about `971 MB` RSS; trusted HP is
`199.627 ms`, checked Rift is `165.774 ms`, and checked SafeZone-backed
allocation is `143.319 ms` with about `404 MB` RSS.

Cheap operator family checkpoint:
`evidence/CHEAP_OPERATOR_FAMILY_MATRIX.md`. `PageTokenMapFilter` and
`RegionList` are now real reusable APIs with passing safety probes.
Dataflow SELECT page-token is `19.881 ms`, and scoped-backend page-token is
`18.214 ms`, versus current checked `20.844 ms`, improved SafeZone/scoped
rooted `23.025 ms`, and heap `27.872 ms`. The RSS rerun keeps the ordering:
scoped page-token SELECT is `17.980 ms` with `30375936` RSS bytes versus heap
`27.932 ms` and `39288832` RSS bytes. The old Dataflow AGGREGATE reporting row
at `38.399-38.991 ms` is the exact-array checked aggregate path, not a true
reusable fold. The true `EpochFold` API is correct but failed its first speed
gate at `91.938 ms`. `RegionList` improves the ListOfLists checked builder to
`5927.385 ms`, versus the earlier benchmark-local checked builder around
`9.2-9.4 s` and heap around `14.8-15.4 s`. These are focused gates, not yet the
full comprehensive headline sweep; a clean committed rerun remains pending.

| Area | Main result | Interpretation |
|---|---|---|
| GCBench | heap `221.514 ms`, improved SafeZone `211.699 ms`, HPZone `245.217 ms` | Older HPZone GCBench win did not reproduce in this clean subset. |
| ListOfLists linked | heap `15842.502 ms`, improved SafeZone `10046.087 ms`, HPZone `12579.297 ms` | Rift beats heap but not improved SafeZone; current SafeZone remains pathological at `137223.310 ms`. |
| ListOfLists flat | heap `1770.286 ms`, HPZone `1571.557 ms` | Rift still wins on flat layout. |
| Dataflow checked | checked SELECT/AGGREGATE beat heap, but improved SafeZone is faster; JOIN heap wins | Local Broom-style evidence is weaker in this clean subset. |
| StreamFlex | region modes remove deadline misses, but SafeZone/heap win elapsed | Keep as latency-control evidence, not throughput win. |
| Yak/Stancu | improved SafeZone wins most rows; dynamic Yak-style proxy remains negative | Rift-vs-heap wins are not enough for final claims. |
| Checked operators | manual AppendWindow wins; page/token append wins; RegionBuffer exact-array controls show checked array `18.574 ms` versus fixed `ObjectBuffer` `25.788 ms` and growable buffer `29.968 ms`; fold/rank still fail speed gates | Prefer operator-owned array/chunk fast paths for known-size stream batches; keep fixed/growable buffers as ergonomic fallbacks. |
| UnsafeZone-HP | clean core/prior medians: GCBench `206.636 ms`, linked ListOfLists `9818.653 ms`, Dataflow SELECT `21.957 ms`, Yak topword `58.686 ms`, Stancu `33.335 ms` | SafeZone no-root internals usually beat improved SafeZone slightly and beat current Rift HPZone on linked/prior-work rows; still unsafe/substrate evidence only. |
| UnsafeZone-HP streams | Beam-default q0 `468.617 ms`, q3 unsafe `296.480 ms` vs checked `292.371 ms`, Common Crawl q1 `3971.051 ms`, Wikimedia q2 `155.768 ms` | UnsafeZone-HP is often the best SafeZone-family stream row, but still mostly only slightly ahead of improved SafeZone; it does not create a large safe Rift case-study win. |
| UnsafeZone-HP DEBS 1M | normal bounded RunBoth: unsafezone-hp `4639.791 ms`, heap `4861.406 ms`, improved SafeZone `5341.010 ms`, Streaming `4663.529 ms`, checked `4844.738 ms` | UnsafeZone-HP is fastest in the normal single-run row; instrumented row is a near-tie with trusted Rift. This is unsafe bounded control evidence, not a final checked application claim. |
| SafeZone cost matrix | improved-32k beats or matches unsafe-hp-32k on GCBench, linked ListOfLists, flat ListOfLists, and trace-mode Common Crawl q1; non-trace q1/q2 make unsafezone-hp competitive again | Root coalescing plus 32 KiB pages, not rootless mode alone, is the leading SafeZone-family direction. Keep rootless UnsafeZone-HP as a lower-bound comparator, not the only checked-backend target. |
| Common Crawl-like q1/q2/q3 | 1M q1 heap GC `1580.847 ms`, q2 heap GC `1561.851 ms`; q1 Rift HPZone `4386.590 ms` vs improved-32k `4608.641 ms`; q2 Rift Streaming `4164.288 ms` vs improved-32k `4425.273 ms`; q3 heap wins `10330.962 ms`; checked RSS rerun q1 `5088.712 ms`, q2 `5061.479 ms` | q1/q2 are GC-heavy trusted stream-object wins after removing default per-allocation Rift byte-counter atomics; q3 is a negative scratch-shape control. Checked q1/q2 beat heap and match output, but miss the gate against improved SafeZone/trusted Rift, so they are checked-overhead evidence rather than application wins. |
| Checked SafeZone-backed backend | AppendWindow 1M `rift-checked-safezone-32k` `29.444 ms` vs current checked cursor `30.922 ms`; Common Crawl q1 `4512.743 ms` vs current checked `4744.872 ms`; q2 `4431.865 ms` vs current checked `4698.903 ms` | Backend mechanics help focused checked append/window but the generic application q1/q2 path still missed the gate. |
| Checked page/token append operator | Focused 1M `rift-checked-page-token` `27.141 ms`, SafeZone-backed page-token `26.191 ms`; Common Crawl-shaped q1 page-token `3956.366 ms`, SafeZone-backed page-token `3728.286 ms`; q2 page-token `4039.855 ms`, SafeZone-backed page-token `3816.247 ms` | First checked generated Common Crawl-shaped application-gate pass. The result is generated stressor evidence, not real-input proof. |
| Object allocation lowering | 10M retained-region-array row: checked SafeZone-backed `143.319 ms`, checked Rift `165.774 ms`, trusted HP `199.627 ms`, heap `271.121 ms` with `105.807 ms` median GC | Region allocation/reclaim wins at scale; earlier checked gap was mostly generic `RegionBuffer` retention overhead. |
| Cheap operator family checkpoint | SELECT scoped page-token `18.214 ms` latest API rerun and `17.980 ms` / `30375936` RSS bytes in direct-binary run; true `EpochFold` `91.938 ms`; reusable `RegionList` ListOfLists builder `5927.385 ms` | First reusable API slice. `PageTokenMapFilter` and `RegionList` pass focused gates; `EpochFold` is correct but negative/gated. Superseded by the 2026-05-06 staged sweep where overlapping. |

The older seeded tables below are retained for provenance and comparison, but
this clean subset should be treated as the current headline evidence for
`core`, `prior`, and `checked` until another clean sweep supersedes it.

The rerun removed the obvious linked ListOfLists heap outlier but preserved the
main rankings: improved SafeZone remains the strongest baseline for GCBench,
linked/chunked ListOfLists, Dataflow, Yak, and Stancu rows; Rift remains clearly
useful on flat ListOfLists, manual AppendWindow, and prepend cursor.

The stream leg adds one genuinely GC-heavy detector row: generated Common Crawl
WET-shaped tokenization spends `1559.601 ms` in heap GC at 1M generated pages.
Rift cuts GC and beats heap there, but improved SafeZone remains faster. The
best checked stream row is NEXMark Beam-default Q3: checked Rift `295.166 ms`
versus heap `315.715 ms` and improved SafeZone `302.668 ms`. The DEBS bounded
1M leg is a single-run correctness/control row: trusted Streaming is
`4681.292 ms` versus heap `4987.579 ms`, while checked is `4882.562 ms`.

The UnsafeZone-HP core/prior leg adds a new runtime-substrate result:
`unsafezone-hp` is fastest on GCBench runtime (`206.636 ms`), GCBench topology
A/B (`195.087 ms` / `190.631 ms`), linked ListOfLists (`9818.653 ms`),
Dataflow SELECT/AGGREGATE/JOIN (`21.957` / `39.434` / `22.359 ms`), most
Yak-shaped rows, and StreamFlex throughput. The improvement over improved
SafeZone is usually small, which means root mode `1` already captures most of
the SafeZone fix. Current Rift HPZone still wins flat ListOfLists
(`1540.958 ms` vs heap `1748.743 ms` and unsafezone-hp `1766.060 ms`).

The UnsafeZone-HP stream leg extends that pattern to stream probes. It is best
or near-best on NEXMark Beam-default q0/q1/q4, Common Crawl WET-shaped q0/q1,
Wikimedia generated q0/q1/q2, and Linear Road q2. It still rarely beats
improved SafeZone by more than a few percent, and current Rift HPZone/Streaming
lose many of those same rows. The useful conclusion is runtime-substrate
direction, not a user-facing unsafe-region claim.

The SafeZone cost leg narrows the substrate direction. Current SafeZone's
large cliffs are still root-removal cliffs, but improved roots already remove
most of that cost. `SAFEZONE_PAGE_SIZE=32768` is a major factor: in traced
GCBench, `improved-32k` is `662.399 ms` versus `unsafe-hp-32k` at
`665.224 ms`; in linked ListOfLists, `improved-32k` is `32080.248 ms` versus
`unsafe-hp-32k` at `32970.802 ms`. Generated Common Crawl q1 is the warning
row: `unsafe-hp-32k` slows to `227556.451 ms` while `improved-32k` is
`8079.502 ms`, despite matching output and low root/reclaim counters. Treat
`unsafezone-hp` as a lower-bound control, not the next checked backend target.
The follow-up non-trace Common Crawl-like q1/q2 run did not reproduce the
unsafe trace pathology: q1 `unsafezone-hp` is `4665.711 ms` and q2 is
`4511.995 ms`, close to the best safe rows. A later Rift fast-path counter
cleanup changes the q1/q2 ordering further: 1M q1 `rift-hp` is `4386.590 ms`
and q2 `rift-streaming` is `4164.288 ms`, beating improved-32k and
UnsafeZone-HP. This makes Common Crawl-like q1/q2 the strongest current
trusted-Rift GC-heavy stream rows, while keeping SafeZone-family internals
relevant for backend comparison. The checked `StreamAppendWindow` follow-up is
correct but slower: in the RSS-complete 1M rerun, q1 `rift-checked` is
`5088.712 ms` versus heap `5670.270 ms`, improved-32k `4644.747 ms`, and
trusted HPZone `4403.007 ms`; q2 `rift-checked` is `5061.479 ms` versus heap
`5342.373 ms`, improved-32k `4444.954 ms`, and trusted HPZone `4258.549 ms`.

## Classification Legend

| Label | Meaning |
|---|---|
| Runtime allocator win | Rift improves allocation/reclaim without changing topology. |
| Unsafe substrate control | SafeZone allocator/pool mechanics with GC roots disabled; useful for diagnosis, not a safe user-facing mode. |
| Layout/topology win | Object graph shape or layout is the main effect. |
| Region-friendly operator win | Stream/dataflow data has structured lifetime and region placement wins. |
| Checked operator win | Checked API beats or nearly matches heap with lower GC/RSS. |
| Checked overhead | Checked container CPU/RSS overhead dominates. |
| CPU/I/O ceiling | GC is too small or heap is fastest. |
| Real-input validation | Public/official input changes or confirms generated-input behavior. |

## Core Runtime And Topology

| Benchmark | Scale | Best Rift | Heap | Improved SafeZone | Classification | Rerun status |
|---|---:|---:|---:|---:|---|---|
| GCBench | 5-run median | HPZone `236.393 ms` | `213.817 ms` | `213.239 ms`; unsafezone-hp `206.636 ms` | Unsafe substrate control | Clean UnsafeZone core/prior sweep |
| ListOfLists linked | 5-run median | HPZone `12400.062 ms` | `15191.230 ms` | `9914.397 ms`; unsafezone-hp `9818.653 ms` | Runtime + topology; SafeZone-family win | Clean UnsafeZone core/prior sweep |
| ListOfLists flat | 5-run median | HPZone `1540.958 ms` | `1748.743 ms` | `1769.278 ms`; unsafezone-hp `1766.060 ms` | Layout/topology win for Rift HPZone | Clean UnsafeZone core/prior sweep |
| ListOfLists chunked | 5-run median | HPZone `2640.031 ms` | `2585.021 ms` | `2433.118 ms`; unsafezone-hp `2430.496 ms` | SafeZone-family topology win | Clean UnsafeZone core/prior sweep |
| Pipeline surrogate | 5-run median | HPZone `46.293 ms`, Streaming `45.648 ms` | `35.077 ms` | `34.660 ms`; unsafezone-hp `34.417 ms` | CPU-bound ceiling | Clean UnsafeZone core/prior sweep |

## Prior-Work Methodology

| Benchmark | Scale | Best Rift / checked row | Heap | Improved SafeZone | Classification | Rerun status |
|---|---:|---:|---:|---:|---|---|
| Broom-style Dataflow SELECT | local docs | checked `24.413 ms`; HPZone `27.588 ms` | `28.258 ms` | `22.501 ms`; unsafezone-hp `21.957 ms` | Rift checked beats heap, SafeZone-family wins | Clean UnsafeZone core/prior sweep |
| Broom-style Dataflow AGGREGATE | local docs | checked `44.146 ms`; HPZone `49.106 ms` | `48.849 ms` | `40.124 ms`; unsafezone-hp `39.434 ms` | SafeZone-family win | Clean UnsafeZone core/prior sweep |
| Broom-style Dataflow JOIN | local docs | checked `24.935 ms`; HPZone `26.832 ms` | `29.122 ms` | `22.784 ms`; unsafezone-hp `22.359 ms` | Rift checked beats heap, SafeZone-family wins | Clean UnsafeZone core/prior sweep |
| StreamFlex pressure | throughput row | Streaming `46.108 ms`, HPZone `46.436 ms` | `42.712 ms` | `39.920 ms`; unsafezone-hp `39.591 ms` | SafeZone-family throughput win; Rift removes misses but loses elapsed | Clean UnsafeZone core/prior sweep |
| Yak top-word/filter | local methodology | Streaming `68.959 ms`, HPZone `68.848 ms` | `70.370 ms` | `59.286 ms`; unsafezone-hp `58.686 ms` | SafeZone-family win | Clean UnsafeZone core/prior sweep |
| Yak GraphChi-style | local methodology | Streaming `47.907 ms`, HPZone `47.554 ms` | `42.384 ms` | `35.456 ms`; unsafezone-hp `35.008 ms` | SafeZone-family win; Rift loses | Clean UnsafeZone core/prior sweep |
| Stancu-style tx boundary | 200k tx, 64/region | Streaming `51.478 ms`, HPZone `51.380 ms` | `44.141 ms` | `33.720 ms`; unsafezone-hp `33.335 ms` | SafeZone-family win; Rift loses | Clean UnsafeZone core/prior sweep |

## Checked Operator Costs

| Benchmark | Scale | Checked/Rift row | Heap row | Classification | Rerun status |
|---|---:|---:|---:|---|---|
| RegionBuffer decomposition | 10 x 100k records | checked array `18.574 ms`; fixed `ObjectBuffer` `25.788 ms`; growable buffer `29.968 ms`; pre-sized buffer `25.980 ms` | heap array `21.089 ms`; heap buffer `34.097 ms` | Checked array win; bounded/growable-buffer overhead | 2026-05-05 decomposition |
| RegionPriorityQueue | 500k records | checked `28.621 ms` | `27.369 ms` | Checked overhead | Pending clean sweep rerun |
| IndexedPriorityQueue | 1M events | checked `103.052 ms` | `100.254 ms` | Checked overhead | Pending clean sweep rerun |
| StreamWindowRank long-key | 1M events | checked-long `503.906 ms` | heap-long `358.988 ms` | Checked overhead | Pending clean sweep rerun |
| StreamWindowTableRank | 1M events | table-long `568.572 ms` | heap-long `437.702 ms` | Checked overhead, gated out | Profile pack only |
| AppendWindow cursor API | 1M events | cursor `34.708 ms` | `35.705 ms` | Checked operator win | Pending clean sweep rerun |
| SafeZone-backed AppendWindow backend | 1M events | checked SafeZone-backed `29.444 ms` | heap `35.511 ms`; current cursor `30.922 ms` | Backend-assisted checked operator win | 2026-05-03 focused gate passed |
| Checked page/token append operator | 1M events | checked page-token `27.141 ms`; SafeZone-backed page-token `26.191 ms` | heap `35.652 ms`; current checked `30.819 ms` | Checked operator-owned overhead-removal win | 2026-05-03 focused gate passed |
| Object allocation lowering | 100k/1M/10M retained-region-array records | 10M checked SafeZone-backed `143.319 ms`; checked Rift `165.774 ms`; trusted HP `199.627 ms` | 10M heap `271.121 ms`, GC median `105.807 ms`, RSS `971 MB` | Allocation/reclaim win at scale; generic checked container overhead isolated | 2026-05-05 refined focused rows validated |
| WindowFold additive API | 1M events | checked `118.726 ms` | `103.244 ms` | Checked aggregate overhead | Pending clean sweep rerun |

## Existing Stream/Application Evidence

| Benchmark | Scale | Best Rift / checked row | Heap | Improved SafeZone | Classification | Rerun status |
|---|---:|---:|---:|---:|---|---|
| DEBS RunBoth checked | full month, 3-run median | checked `66.804 s` | `67.122 s` | full-month pending | Near-tie, memory validation | Rerun only after clean sweep setup |
| DEBS RunBoth bounded 1M | single run | Streaming `4681.292 ms`, checked `4882.562 ms` | `4987.579 ms` | not run in this leg | Trusted win, checked modest win, correctness control | Current bounded single-run |
| DEBS RunBoth bounded 1M with UnsafeZone-HP | single run | unsafezone-hp `4639.791 ms`; Streaming `4663.529 ms`; checked `4844.738 ms` | `4861.406 ms` | improved SafeZone `5341.010 ms` | Unsafe substrate/control win; trusted Streaming close | Clean UnsafeZone DEBS leg |
| NEXMark Beam Q0 | 1M generated-profile | Streaming `475.161 ms`, checked `481.436 ms` | `521.508 ms` | `478.500 ms` | Trusted stream-object win; checked beats heap but not improved SafeZone | Clean stream sweep |
| NEXMark Beam Q1 | 1M generated-profile | Streaming `919.670 ms`, checked `945.372 ms` | `950.341 ms` | `929.887 ms` | Trusted modest win; checked does not win | Clean stream sweep |
| NEXMark Beam Q2 | 1M generated-profile | Streaming `563.282 ms`, checked `572.005 ms` | `586.607 ms` | `576.228 ms` | Modest trusted/checked stream row | Clean stream sweep |
| NEXMark Beam Q3 | 1M generated-profile | checked `295.166 ms` | `315.715 ms` | `302.668 ms` | Best checked stream row, below 10% gate | Clean stream sweep |
| NEXMark Beam Q8 | 1M generated-profile | checked `457.518 ms` | `470.798 ms` | `457.725 ms` | Checked near-tie with improved SafeZone | Clean stream sweep |
| NEXMark Beam Q11 | 1M generated-profile | HPZone `228.741 ms` | `218.774 ms` | `229.557 ms` | Heap wins elapsed; region rows reduce GC only | Clean stream sweep |
| Common Crawl WET-shaped Q1 | 1M generated pages / 137M token records | HPZone `4386.590 ms`, Streaming `4395.599 ms`; checked RSS rerun `5088.712 ms` | `5466.535 ms`; RSS rerun `5670.270 ms` | improved-32k `4608.641 ms`; RSS rerun `4644.747 ms` | GC-heavy trusted-Rift win after fast-allocation counter cleanup; checked beats heap but misses improved-SafeZone/trusted gate | 2026-05-02 follow-up |
| Common Crawl WET-shaped Q2 | 1M generated pages / 137M token records | Streaming `4164.288 ms`, HPZone `4176.919 ms`; checked RSS rerun `5061.479 ms` | `5267.784 ms`; RSS rerun `5342.373 ms` | improved-32k `4425.273 ms`; RSS rerun `4444.954 ms` | GC-heavy trusted-Rift stream/window win after counter cleanup; checked beats heap modestly but misses improved-SafeZone/trusted gate | 2026-05-02 follow-up |
| Common Crawl checked SafeZone-backed Q1/Q2 | 1M generated pages / 137M token records | q1 checked SafeZone-backed `4512.743 ms`; q2 `4431.865 ms` | q1 current checked `4744.872 ms`; q2 current checked `4698.903 ms` | q1 improved-32k `4570.772 ms`; q2 improved-32k `4362.405 ms` | Backend improves checked but does not clear application gate | 2026-05-03 follow-up |
| Common Crawl checked page-token Q1/Q2 | 1M generated pages / 137M token records | q1 checked page-token `3956.366 ms`, SafeZone-backed page-token `3728.286 ms`; q2 checked page-token `4039.855 ms`, SafeZone-backed page-token `3816.247 ms` | q1 heap `5412.618 ms`, current checked `4855.133 ms`; q2 heap `5252.803 ms`, current checked `4820.611 ms` | q1 improved-32k `4637.981 ms`; q2 improved-32k `4580.687 ms` | First checked generated application-gate pass; still generated stressor evidence | 2026-05-03 overhead-removal follow-up |
| Yahoo Q2 | 1M generated/preloaded | Streaming `106.415 ms` | `105.802 ms` | `106.425 ms` | Near-tie; cuts GC but heap elapsed wins | Clean stream sweep |
| RIoTBench q1 | 1M generated | Streaming `148.019 ms` | `135.750 ms` | `147.638 ms` | Heap wins in clean 1M row; earlier 100k positive weakened | Clean stream sweep |
| Wikimedia real clickstream | 1M events | Streaming `157.449 ms` | `126.800 ms` | `149.062 ms` | Real-input CPU ceiling | Parked control |
| Common Crawl real WET Q1/Q2 page-token control | current shard, actual q1 output `752797`, q2 output `18560` | q1 SafeZone-backed page-token `30.474 ms`; q2 SafeZone-backed page-token `30.783 ms` | q1 heap `32.215 ms`; q2 heap `31.227 ms` | q1 improved-32k `35.264 ms`; q2 improved-32k `35.888 ms` | Real-input ceiling/control: page-token wins modestly, but heap GC is `0.000 ms` with 0 GC runs | 2026-05-03 real WET control |
| Common Crawl real WAT Q4/Q5 page-token control | current WAT shard, q4 output `1006742`, q5 output `293020` | q4 SafeZone-backed page-token `31.792 ms`; q5 SafeZone-backed page-token `33.937 ms` | q4 heap `33.646 ms`; q5 heap `35.066 ms` | q4 improved-32k `39.551 ms`; q5 improved-32k `39.579 ms` | Real-input ceiling/control: link-object path wins modestly, but heap GC is `0.000 ms` with 0 GC runs | 2026-05-03 real WAT control |
| GH Archive Q1 fields, first 100k | 100k real JSON events / 1.3M event-field records | checked SafeZone-backed page-token `33.656 ms`; Streaming `35.161 ms` | heap `46.309 ms`, median GC `15.777 ms` | improved-32k `37.956 ms` | Promising first signal, but the original heap-expected harness contaminates RSS/GC state for region modes; use oracle rows for current interpretation | 2026-05-03 GH Archive row |
| GH Archive Q1 fields, 8-hour oracle | 1M real JSON events / 13M event-field records | Streaming rerun `340.820 ms`; checked SafeZone-backed page-token `348.817 ms` | heap `293.204 ms`, max GC `135.368 ms`, 1/3 runs with GC | improved-32k `374.923 ms` | Heap wins uncapped median by growing to ~1.7 GiB; regions remove GC tail but lose throughput | 2026-05-03 multi-hour oracle |
| GH Archive Q1 fields, 1G heap cap diagnostic | 1M real JSON events / 13M event-field records | compare to checked SafeZone-backed page-token `348.817 ms` from uncapped region row | heap `395.295 ms`, median GC `92.347 ms`, max GC `101.174 ms` | not rerun under cap; SafeZone crashed under 1G in a later process | Memory-budget diagnostic: checked region path beats heap when heap cannot grow freely | 2026-05-03 cap diagnostic |
| GH Archive Q2 repo window, 8-hour oracle | 1M real JSON events / 13M event-field records | Streaming `325.665 ms`; checked SafeZone-backed page-token `347.033 ms` | heap `271.880 ms`, max GC `136.353 ms`, 1/3 runs with GC | improved-32k `363.049 ms` | Heap wins median; repo-window aggregation CPU dominates despite GC tail | 2026-05-03 multi-hour oracle |
| GH Archive Q1 fields, file-backed byte-slice | 200k real JSON events / 2.6M event-field records, 2 hourly gzip files | Streaming `3626.219 ms`; checked SafeZone-backed page-token `3629.193 ms` | heap `3806.120 ms`, median GC `57.685 ms`, RSS `290177024` | not rerun in this subset | Byte-slice parser-scratch makes q1 a modest real-input throughput/RSS/tail win; region rows report zero timed GC and about `211 MB` RSS; not GC-heavy | 2026-05-07 byte parser follow-up |
| GH Archive Q2 repo window, file-backed byte-slice | 200k real JSON events / 2.6M event-field records, 2 hourly gzip files | Streaming `3645.458 ms`; checked SafeZone-backed page-token `3626.107 ms` | heap `3756.950 ms`, median GC `61.625 ms`, RSS `290193408` | not rerun in this subset | Byte-slice parser-scratch makes q2 a modest checked scoped page-token win; region rows report zero timed GC and about `211 MB` RSS | 2026-05-07 byte parser follow-up |
| LogHub BGL Q1 tokens | 1M real BGL lines / 13.4M line+token records | Streaming `5491.033 ms`, RSS `357679104`; checked scoped page-token `5552.988 ms` | heap `5568.252 ms`, median GC `99.271 ms`, RSS `408420352`; 256M cap heap `5807.256 ms`, median GC `194.609 ms` | improved-32k `5589.860 ms`, RSS `357842944` | Trusted Streaming is a modest throughput/RSS win; checked scoped page-token is near-tied but high-RSS. Heap GC is steady but still a small share of elapsed. | 2026-05-07 LogHub BGL follow-up |
| LogHub BGL Q2 window counts | full real BGL file, 4.75M lines / 66.9M line+token records | Streaming `30899.595 ms`; checked scoped page-token `31165.087 ms`, RSS `490946560` | heap `32161.391 ms`, GC `595.599 ms`, RSS `576012288` | improved-32k `31459.104 ms`, RSS `490258432` | Full-file real log modest throughput/RSS/tail win; not GC-heavy because heap GC is under 2% of elapsed. | 2026-05-07 LogHub BGL scale probe |
| Linear Road official Q1 | 1M events | HPZone `180.277 ms` | `162.668 ms` | recorded in source pack | Real-input CPU ceiling | Parked control |

## UnsafeZone-HP Stream Follow-Up

| Benchmark | Query | heap | improved SafeZone | unsafezone-hp | Best Rift | Classification |
|---|---|---:|---:|---:|---:|---|
| NEXMark Beam | q0 | 520.052 | 481.133 | 468.617 | HPZone `472.017` | Unsafe substrate stream win |
| NEXMark Beam | q3 | 316.626 | 297.962 | 296.480 | checked `292.371` | Best checked stream row, below gate |
| NEXMark Beam | q8 | 467.213 | 462.599 | 460.822 | checked `450.904` | Checked near-case-study row, below gate |
| NEXMark Beam | q11 | 218.200 | 226.184 | 223.644 | HPZone `226.909` | Heap wins elapsed |
| Common Crawl WET-shaped | q1 tokenization | 5466.535 | 4608.641 | 4640.245 | HPZone `4386.590` | Fast-allocation counter cleanup makes Rift fastest |
| Common Crawl WET-shaped | q2 domain window | 5267.784 | 4425.273 | 4437.924 | Streaming `4164.288` | Fast-allocation counter cleanup makes Rift fastest |
| Yahoo-style ad | q2 campaign window | 105.148 | 106.104 | 105.802 | HPZone `106.331` | Heap near-tie/win |
| RIoTBench-style | q0 parse | 113.022 | 111.307 | 109.020 | HPZone `111.418` | Unsafe modest win |
| Wikimedia generated | q2 clickstream | 160.500 | 159.147 | 155.768 | Streaming `162.253` | Unsafe wins; current Rift loses |
| Linear Road generated | q2 accidents | 206.491 | 205.889 | 201.977 | HPZone `209.727` | Unsafe modest win; current Rift loses |

## Common Crawl-Like Follow-Up

Source: `evidence/COMMON_CRAWL_LIKE_MATRIX.md`. Rows below are generated
WET-shaped 1M, 3-run medians. They supersede the earlier smoke-only q2/q3
status, but they do not replace real WET input controls.

| Query | Heap | Improved SafeZone | Improved 32K | UnsafeZone-HP | Best Rift | Classification |
|---|---:|---:|---:|---:|---:|---|
| q1 tokenization | `5466.535 ms`; GC `1580.847 ms` | n/a in fast-counter row | `4608.641 ms` | `4640.245 ms` | HPZone `4386.590 ms`; checked RSS rerun `5088.712 ms` | Trusted GC-heavy win; checked beats heap but fails improved-SafeZone/trusted gate. |
| q2 domain-window | `5267.784 ms`; GC `1561.851 ms` | n/a in fast-counter row | `4425.273 ms` | `4437.924 ms` | Streaming `4164.288 ms`; checked RSS rerun `5061.479 ms` | Trusted GC-heavy win; checked beats heap modestly but fails improved-SafeZone/trusted gate. |
| q3 parser-scratch | `10330.962 ms`; GC `859.220 ms` | `27715.527 ms` | `26535.424 ms` | `11065.693 ms` | Streaming `11206.504 ms` | Negative scratch-shape control; heap wins elapsed. |

## SafeZone Cost Decomposition

Source: `evidence/SAFEZONE_COST_MATRIX.md`, run id
`2026-05-01-safezone-cost`. These rows were collected with `SAFEZONE_TRACE=1`,
so they are diagnostic cost rows rather than normal elapsed headline rows.

| Benchmark | Best traced config | Current-default cost signal | Interpretation |
|---|---:|---:|---|
| GCBench | improved-32k `662.399 ms` | root remove `2168.263 ms` | 32 KiB pages plus improved roots match unsafe no-root. |
| ListOfLists linked | improved-32k `32080.248 ms` | root remove `627735.229 ms` | Current root removal is catastrophic; improved-32k beats unsafe-hp-32k. |
| ListOfLists flat | improved-32k `1692.936 ms` | no SafeZone claims/roots | Flat row is not root-bookkeeping-bound. |
| Dataflow SELECT/AGG/JOIN | unsafe-hp-32k `55.972` / `87.080` / `54.506 ms` | root remove `83.366 ms` shared | Unsafe and improved-32k are close; chunk roots also competitive. |
| Common Crawl q1 generated | improved-32k `8079.502 ms` | root remove `1326310.264 ms` | Root coalescing fixes current mode, while unsafe-hp-32k is a severe pathology. |

## New Candidate Ladder

| Candidate | Current status | First headline question | Gate |
|---|---|---|---|
| DSPBench | Not ported | Which 2-3 local kernels have highest stream object churn and clear epoch/window close? | Add only after triage doc records selected kernels and provenance. |
| Real RIoTBench input | Not wired | Does real sensor input keep q1 heap pressure while preserving improved-SafeZone comparison? | Add `RIOTBENCH_INPUT`; rerun q1/q2. |
| Theodolite | Not ported | Does a local UC kernel expose allocator pressure without Kafka/Kubernetes? | Port one UC only after DSPBench/RIoTBench. |
| HiBench streaming | Not ported | Do simple streaming controls reproduce CPU/GC ceilings? | Keep as controls, not primary evidence. |
| ShuffleBench / RiverBench / BigDataBench | Not ported | Are routing/parser-heavy streams better candidates? | Lower priority after earlier candidates. |

## Report Assembly Notes

Use this file as the source for compact report tables. Use individual
benchmark result packs for command provenance and caveats.
