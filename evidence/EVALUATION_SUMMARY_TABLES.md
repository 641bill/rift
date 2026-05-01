# Rift Evaluation Summary Tables

Date: 2026-05-01

Status: seeded summary pack for the comprehensive evaluation. Rows below are
current checked-in evidence before the next clean headline sweep unless marked
pending rerun.

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

SafeZone cost-decomposition scaffold:
`evidence/SAFEZONE_COST_MATRIX.md`. This is the required next measurement
before SafeZone-family optimization or a checked SafeZone-HP backend. It
records `SAFEZONE_TRACE=1` pool counters alongside benchmark medians/RSS.

Common Crawl-like expansion:
`evidence/COMMON_CRAWL_LIKE_MATRIX.md`. The WET-shaped runner now includes
`q2-domain-window` and `q3-parser-scratch`; current rows are smoke validation
only, not headline evidence.

| Area | Main result | Interpretation |
|---|---|---|
| GCBench | heap `221.514 ms`, improved SafeZone `211.699 ms`, HPZone `245.217 ms` | Older HPZone GCBench win did not reproduce in this clean subset. |
| ListOfLists linked | heap `15842.502 ms`, improved SafeZone `10046.087 ms`, HPZone `12579.297 ms` | Rift beats heap but not improved SafeZone; current SafeZone remains pathological at `137223.310 ms`. |
| ListOfLists flat | heap `1770.286 ms`, HPZone `1571.557 ms` | Rift still wins on flat layout. |
| Dataflow checked | checked SELECT/AGGREGATE beat heap, but improved SafeZone is faster; JOIN heap wins | Local Broom-style evidence is weaker in this clean subset. |
| StreamFlex | region modes remove deadline misses, but SafeZone/heap win elapsed | Keep as latency-control evidence, not throughput win. |
| Yak/Stancu | improved SafeZone wins most rows; dynamic Yak-style proxy remains negative | Rift-vs-heap wins are not enough for final claims. |
| Checked operators | manual AppendWindow wins; prepend cursor wins its fair control; RegionBuffer/cursor/fold/rank do not clear speed gates | Focus on cheaper checked operator implementations before application claims. |
| UnsafeZone-HP | clean core/prior medians: GCBench `206.636 ms`, linked ListOfLists `9818.653 ms`, Dataflow SELECT `21.957 ms`, Yak topword `58.686 ms`, Stancu `33.335 ms` | SafeZone no-root internals usually beat improved SafeZone slightly and beat current Rift HPZone on linked/prior-work rows; still unsafe/substrate evidence only. |
| UnsafeZone-HP streams | Beam-default q0 `468.617 ms`, q3 unsafe `296.480 ms` vs checked `292.371 ms`, Common Crawl q1 `3971.051 ms`, Wikimedia q2 `155.768 ms` | UnsafeZone-HP is often the best SafeZone-family stream row, but still mostly only slightly ahead of improved SafeZone; it does not create a large safe Rift case-study win. |
| UnsafeZone-HP DEBS 1M | normal bounded RunBoth: unsafezone-hp `4639.791 ms`, heap `4861.406 ms`, improved SafeZone `5341.010 ms`, Streaming `4663.529 ms`, checked `4844.738 ms` | UnsafeZone-HP is fastest in the normal single-run row; instrumented row is a near-tie with trusted Rift. This is unsafe bounded control evidence, not a final checked application claim. |
| SafeZone cost matrix | scaffold and smoke only | Cost counters now exist for root-mode/page-size decomposition. Do not optimize SafeZone or add `rift-checked-safezone-hp` until this has headline rows. |

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
| RegionBuffer | 1M records | checked `28.654 ms` | `33.825 ms` | Checked operator win | Pending clean sweep rerun |
| RegionPriorityQueue | 500k records | checked `28.621 ms` | `27.369 ms` | Checked overhead | Pending clean sweep rerun |
| IndexedPriorityQueue | 1M events | checked `103.052 ms` | `100.254 ms` | Checked overhead | Pending clean sweep rerun |
| StreamWindowRank long-key | 1M events | checked-long `503.906 ms` | heap-long `358.988 ms` | Checked overhead | Pending clean sweep rerun |
| StreamWindowTableRank | 1M events | table-long `568.572 ms` | heap-long `437.702 ms` | Checked overhead, gated out | Profile pack only |
| AppendWindow cursor API | 1M events | cursor `34.708 ms` | `35.705 ms` | Checked operator win | Pending clean sweep rerun |
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
| Common Crawl WET-shaped Q1 | 1M generated pages / 137M token records | HPZone `4301.536 ms` | `4770.503 ms` | `4066.435 ms` | GC-heavy detector; Rift beats heap but not improved SafeZone | Clean stream sweep |
| Yahoo Q2 | 1M generated/preloaded | Streaming `106.415 ms` | `105.802 ms` | `106.425 ms` | Near-tie; cuts GC but heap elapsed wins | Clean stream sweep |
| RIoTBench q1 | 1M generated | Streaming `148.019 ms` | `135.750 ms` | `147.638 ms` | Heap wins in clean 1M row; earlier 100k positive weakened | Clean stream sweep |
| Wikimedia real clickstream | 1M events | Streaming `157.449 ms` | `126.800 ms` | `149.062 ms` | Real-input CPU ceiling | Parked control |
| Common Crawl real WET Q1 | 10k pages | Streaming `15.651 ms` | `12.079 ms` | `16.093 ms` | Real-input CPU ceiling | Parked control |
| Linear Road official Q1 | 1M events | HPZone `180.277 ms` | `162.668 ms` | recorded in source pack | Real-input CPU ceiling | Parked control |

## UnsafeZone-HP Stream Follow-Up

| Benchmark | Query | heap | improved SafeZone | unsafezone-hp | Best Rift | Classification |
|---|---|---:|---:|---:|---:|---|
| NEXMark Beam | q0 | 520.052 | 481.133 | 468.617 | HPZone `472.017` | Unsafe substrate stream win |
| NEXMark Beam | q3 | 316.626 | 297.962 | 296.480 | checked `292.371` | Best checked stream row, below gate |
| NEXMark Beam | q8 | 467.213 | 462.599 | 460.822 | checked `450.904` | Checked near-case-study row, below gate |
| NEXMark Beam | q11 | 218.200 | 226.184 | 223.644 | HPZone `226.909` | Heap wins elapsed |
| Common Crawl WET-shaped | q1 tokenization | 4743.205 | 4028.067 | 3971.051 | HPZone `4322.349` | GC-heavy, Unsafe/SafeZone win |
| Yahoo-style ad | q2 campaign window | 105.148 | 106.104 | 105.802 | HPZone `106.331` | Heap near-tie/win |
| RIoTBench-style | q0 parse | 113.022 | 111.307 | 109.020 | HPZone `111.418` | Unsafe modest win |
| Wikimedia generated | q2 clickstream | 160.500 | 159.147 | 155.768 | Streaming `162.253` | Unsafe wins; current Rift loses |
| Linear Road generated | q2 accidents | 206.491 | 205.889 | 201.977 | HPZone `209.727` | Unsafe modest win; current Rift loses |

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
