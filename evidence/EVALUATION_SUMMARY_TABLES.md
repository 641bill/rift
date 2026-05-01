# Rift Evaluation Summary Tables

Date: 2026-05-01

Status: seeded summary pack for the comprehensive evaluation. Rows below are
current checked-in evidence before the next clean headline sweep unless marked
pending rerun.

## Clean Headline Subset: 2026-05-01

Source: `evidence/HEADLINE_CORE_PRIOR_CHECKED_2026_05_01.md`

Run id: `2026-05-01-headline-core-prior-checked`

| Area | Main result | Interpretation |
|---|---|---|
| GCBench | heap `221.514 ms`, improved SafeZone `211.699 ms`, HPZone `245.217 ms` | Older HPZone GCBench win did not reproduce in this clean subset. |
| ListOfLists linked | heap `15842.502 ms`, improved SafeZone `10046.087 ms`, HPZone `12579.297 ms` | Rift beats heap but not improved SafeZone; current SafeZone remains pathological at `137223.310 ms`. |
| ListOfLists flat | heap `1770.286 ms`, HPZone `1571.557 ms` | Rift still wins on flat layout. |
| Dataflow checked | checked SELECT/AGGREGATE beat heap, but improved SafeZone is faster; JOIN heap wins | Local Broom-style evidence is weaker in this clean subset. |
| StreamFlex | region modes remove deadline misses, but SafeZone/heap win elapsed | Keep as latency-control evidence, not throughput win. |
| Yak/Stancu | improved SafeZone wins most rows; dynamic Yak-style proxy remains negative | Rift-vs-heap wins are not enough for final claims. |
| Checked operators | manual AppendWindow wins; prepend cursor wins its fair control; RegionBuffer/cursor/fold/rank do not clear speed gates | Focus on cheaper checked operator implementations before application claims. |

The older seeded tables below are retained for provenance and comparison, but
this clean subset should be treated as the current headline evidence for
`core`, `prior`, and `checked` until another clean sweep supersedes it.

## Classification Legend

| Label | Meaning |
|---|---|
| Runtime allocator win | Rift improves allocation/reclaim without changing topology. |
| Layout/topology win | Object graph shape or layout is the main effect. |
| Region-friendly operator win | Stream/dataflow data has structured lifetime and region placement wins. |
| Checked operator win | Checked API beats or nearly matches heap with lower GC/RSS. |
| Checked overhead | Checked container CPU/RSS overhead dominates. |
| CPU/I/O ceiling | GC is too small or heap is fastest. |
| Real-input validation | Public/official input changes or confirms generated-input behavior. |

## Core Runtime And Topology

| Benchmark | Scale | Best Rift | Heap | Improved SafeZone | Classification | Rerun status |
|---|---:|---:|---:|---:|---|---|
| GCBench | 5-run median | HPZone `161.641 ms` | `203.514 ms` | `223.770 ms` | Runtime allocator win | Pending clean sweep rerun |
| ListOfLists linked | 5-run median | HPZone `6951.331 ms` | `15085.511 ms` | `10132.854 ms` | Runtime + topology win | Pending clean sweep rerun |
| ListOfLists flat | 3-run median | HPZone `1515.091 ms` | `1766.295 ms` | not headline | Layout/topology win | Pending clean sweep rerun |
| Pipeline surrogate | 5-run median | HPZone `5.089 ms` | `4.924 ms` | `5.055 ms` | CPU-bound ceiling | Keep as surrogate only |

## Prior-Work Methodology

| Benchmark | Scale | Best Rift / checked row | Heap | Improved SafeZone | Classification | Rerun status |
|---|---:|---:|---:|---:|---|---|
| Broom-style Dataflow SELECT | 10 x 100k docs | checked `18.865 ms` | `36.868 ms` | recorded in source pack | Checked operator win | Pending clean sweep rerun |
| Broom-style Dataflow AGGREGATE | 10 x 100k docs | checked `36.003 ms` | `51.474 ms` | recorded in source pack | Checked operator win | Pending clean sweep rerun |
| Broom-style Dataflow JOIN | 10 x 100k docs | checked `18.736 ms` | `32.170 ms` | recorded in source pack | Checked operator win | Pending clean sweep rerun |
| StreamFlex pressure | throughput row | Streaming `329.896 ms` | `634.472 ms` | recorded in source pack | Region-friendly latency/throughput win | Pending clean sweep rerun |
| Yak top-word/filter | 40 x 250k records | Streaming `262.980 ms` | `311.527 ms` | `271.273 ms` | Region-friendly operator win | Pending clean sweep rerun |
| Yak GraphChi-style | 40 x 16 x 15625 edges | Streaming `236.388 ms` | `302.599 ms` | `228.252 ms` | Rift beats heap, not improved SafeZone | Pending clean sweep rerun |
| Stancu-style tx boundary | 200k tx, 64/region | Streaming `38.844 ms` | `43.189 ms` | SafeZone faster | Boundary-sensitive allocator win | Pending clean sweep rerun |

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
| NEXMark Beam Q0 | 1M generated-profile | HPZone `467.895 ms` | `548.184 ms` | `482.774 ms` | Trusted stream-object win | Pending clean sweep rerun |
| NEXMark Beam Q1 | 1M generated-profile | HPZone `538.451 ms`, checked `557.251 ms` | `579.038 ms` | `561.787 ms` | Promising stream-map row | Pending clean sweep rerun |
| NEXMark Beam Q3 | 1M generated-profile | checked `287.169 ms` | `304.190 ms` | `293.586 ms` | Best checked stream row | Pending clean sweep rerun |
| NEXMark Beam Q8 | 1M generated-profile | checked `315.545 ms` | `331.599 ms` | `326.569 ms` | Modest checked join/window win | Pending clean sweep rerun |
| NEXMark Beam Q11 | 1M generated-profile | HPZone `226.862 ms` | `255.418 ms` | `237.400 ms` | Trusted session-window win | Pending clean sweep rerun |
| Yahoo Q2 | 1M generated/preloaded | HPZone `105.216 ms` | `104.512 ms` | `108.173 ms` | Cuts GC but heap elapsed wins | Keep as control |
| RIoTBench q1 | 100k generated | HPZone `14.516 ms`, Streaming `14.445 ms` | `16.643 ms` | `13.980 ms` | Heap pressure, SafeZone stronger | Needs real input |
| Wikimedia real clickstream | 1M events | Streaming `157.449 ms` | `126.800 ms` | `149.062 ms` | Real-input CPU ceiling | Parked control |
| Common Crawl real WET Q1 | 10k pages | Streaming `15.651 ms` | `12.079 ms` | `16.093 ms` | Real-input CPU ceiling | Parked control |
| Linear Road official Q1 | 1M events | HPZone `180.277 ms` | `162.668 ms` | recorded in source pack | Real-input CPU ceiling | Parked control |

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
