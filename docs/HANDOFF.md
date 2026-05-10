# Rift Project Handoff

Date: 2026-05-03
Last updated: 2026-05-10 17:37 CEST

Active worktree for this update:
`/Users/siyaoliu/rift/scala-native-rift`

Active implementation branch for this update:
`feature/rift`

Latest implementation checkpoint:
`54bf38c45` (`Add final-clean GH Archive support`)

Latest parent evidence checkpoint:
current parent commit (`Record GH Archive final-clean rows`)

Latest comprehensive sweep checkpoint:
Staged headline runs completed after the TransactionRegion checkpoint. Source
summary: `evidence/COMPREHENSIVE_SWEEP_2026_05_06.md`.

Latest reporting-principle update:
`docs/BENCHMARK_CATALOG.md` and `docs/PERFORMANCE_EVALUATION_REPORT.md` now
make comparison classes explicit. Report rows as natural heap baseline,
same-shape heap control, summary-only topology, retained-object drop-anchor,
best checked topology, or unsafe/trusted lower bound before interpreting
speedups. In prose, use `heap-retained-drop-anchor` for
`heap-epoch-retained-no-traverse` when clarity matters: heap can drop the
bucket anchor in O(1), but the retained heap objects still remain for GC
trace/reclaim, whereas checked regions bulk close/reset the allocation area.
This makes retained heap vs retained checked epoch the fair memory-management
comparison, while summary-only direct rows remain topology/operator evidence.

Latest classified evaluation summary:
`evidence/EVALUATION_CLASSIFIED_SUMMARY.md` is now the first-stop rollup for
reporting. It classifies each representative row by benchmark, input type,
comparison class, heap/control row, best safe checked row, elapsed delta, GC
delta, RSS delta, and allowed claim. Use it to keep the paper and slides
unambiguous: summary-only/direct-aggregate rows are topology/operator lower
bounds; retained heap versus retained checked epoch rows are memory-management
claims; direct `RiftRegion.epoch` rows are reusable checked topology claims;
page-token rows are page/window stream claims; rootless/trusted rows remain
lower-bound controls.

Latest fair-evaluation and measurement protocol:
`docs/FAIR_EVALUATION_PROTOCOL.md` now defines the formal comparison contract:
headline rows must use reusable checked framework APIs or be labeled controls,
and memory-management claims require retained heap/drop-anchor versus retained
checked-region comparisons. `evidence/MEASUREMENT_OVERHEAD_PROTOCOL.md` adds
measurement levels: L1 final-clean headline timing, L2 standard stats, L3
diagnostics, and L4 external profiles. Initial L1 final-clean binary support is
now implemented for `RetainedEpochReclaimMatrix`, `YakRegionMatrix`,
`DataflowRegionMatrix`, `CommonCrawlWetMatrix`, `ReMLRegionMatrix`,
`StreamFlexRegionMatrix`, `StancuRegionMatrix`,
`SpecJbb2005PortMatrix`, `LogHubTopTemplatesMatrix`, `LogHubRegionMatrix`,
`DSPBenchRegionMatrix`, `NexmarkRegionMatrix`, and
`GithubArchiveRegionMatrix`.
Set `RIFT_FINAL_CLEAN=1` or `RIFT_EVAL_MEASUREMENT_LEVEL=L1`; the binary skips
internal timing/GC/region stat reads and prints only minimal checksum/output
metadata. A tiny retained-epoch L1 smoke matched heap and checked checksums.
The retained runner now records external real/user/sys time and max RSS in its
summary. The first focused 1M retained L1 row was collected from clean child
`f1aa55484`: heap retained/drop-anchor total process time is `0.70 s` median
for 20 iterations, checked stream retained is `0.50 s`, and checked scoped
retained is `0.47 s`, with matching checksum/output. The broader report-grade
L1 headline sweep is still pending and belongs in
`evidence/FINAL_CLEAN_HEADLINE_RESULTS.md`.
Follow-up child commit `7573d7577` extends external real/user/sys/RSS summary
columns to the Dataflow, Yak, Common Crawl WET-shaped, and ReML runner scripts.
Tiny L1 smokes were run for each current binary and matched checksums; those
smokes validate runner plumbing only, not headline performance. The first
Dataflow representative L1 rows were also collected for SELECT/AGGREGATE/JOIN.
At 1M x20, checked epoch scoped is `0.38/0.69/0.39 s` median total process time
versus heap `0.62/1.10/0.55 s` and region-scoped-rooted
`0.46/0.79/0.46 s`; checksums are `131080080920`, `163835709480`, and
`193232836790`.
Yak LiveJournal now also has an L1 real-input total-process row from child
`7573d7577`. It uses the real SNAP LiveJournal gzipped edge list, 50M replayed
edges, 10 epochs x 5M edges, and five replay iterations per external process.
The row includes one input preload plus five replays per process. Median total
process time is heap `18.79 s`, region-scoped-rooted `16.93 s`, and checked
epoch scoped `16.12 s`; max RSS is about `2.77 GB` for heap and `612 MB` for
the rooted/checked region rows. Checksum matched:
`-6048644965681588176`.
Generated Common Crawl-shaped q1/q2 also now have L1 page-token rows from
child `7573d7577`. At 1M pages, q1 has heap `5.68 s`,
safezone-improved-32k `5.42 s`, checked page-token stream `4.02 s`, and
checked scoped page-token `4.51 s`; q2 has heap `5.53 s`,
safezone-improved-32k `5.39 s`, checked page-token stream `4.16 s`, and
checked scoped page-token `4.75 s`. Checksums/output counts matched. This is a
generated stressor row, not real-input proof; L1 shows the Rift streaming
page-token backend is fastest for this shape, while the SafeZone-backed checked
page-token remains a heap/rooted win but not the fastest checked backend.

Child `c5bbc498f` adds the same final-clean plumbing to StreamFlex and
Stancu-style matrices. Under `RIFT_FINAL_CLEAN=1`, both binaries now skip
warmups, heap-expected replay, GC/Rift stat reads, and internal elapsed medians,
then print minimal `measurement_level=L1 final_clean=1` result lines. Their
runners now record external real/user/sys time and max RSS. Small smokes
matched checksums across heap, improved SafeZone, and checked scoped rows.
Representative L1 rows are now recorded in
`evidence/FINAL_CLEAN_HEADLINE_RESULTS.md`: StreamFlex direct-epoch throughput
is a checked framework win (`0.58 s` checked scoped direct epoch versus
`0.79 s` heap and `0.77 s` improved SafeZone for 20 x 200k events);
StreamFlex direct-epoch latency is also favorable (`0.17 s` checked with zero
misses versus `0.18 s` heap with four deadline misses); Stancu transactions are
a checked framework win (`0.57 s` checked scoped direct epoch versus `0.85 s`
heap and `0.71 s` improved SafeZone for 20 x 200k transactions).
Child `678a6eb41` adds the same L1 plumbing to `SpecJbb2005PortMatrix`.
The 8-warehouse representative row is checked epoch scoped `2.21 s` versus
heap `2.64 s` and rooted scoped region `2.48 s` for 20 inner iterations, with
RSS about `8.0 MB` versus heap `12.4 MB`. This is a clean-room
SPECjbb2005-workload port, not official SPECjbb2005.
Child `3598efe29` adds L1 plumbing to `LogHubTopTemplatesMatrix`. The real
HDFS 1M x20 row is reusable checked top-k scoped `5.05 s` and about `28 MB`
RSS versus retained heap `5.46 s` and about `205 MB` RSS. The benchmark-local
checked retained path is still faster at `4.84 s`, so the top-k API remains
passed but has an overhead target before broader integration.
Child `fe8f0d853` adds L1 plumbing to `LogHubRegionMatrix`. The HDFS q2
page/window row was rerun as 1M real HDFS lines x3 q2 iterations per process,
three external repeats. L1 final-clean timing is an elapsed tie but strong RSS
win: checked scoped page-token is `25.56 s` and about `79 MB` RSS versus heap
`25.60 s` and about `409 MB` RSS. The L2 row remains the source for GC
interpretation: checked scoped page-token is `7871.856 ms` versus heap
`8227.369 ms`, removing heap's `92.659 ms` median timed GC.
Child `95f4f4d71` adds L1 plumbing to `DSPBenchRegionMatrix`. Fraud/Log q2
were rerun as 1M real DSPBench sample replay x5 q2 iterations per process,
three external repeats. Fraud q2 is a checked RSS win but not a checked elapsed
win: checked scoped page-token is `4.44 s` and about `59.5 MB` RSS versus heap
`4.39 s` and about `358 MB`; trusted Streaming is the lower-bound elapsed
winner at `4.18 s`. Log q2 is a modest checked elapsed/RSS win: checked scoped
page-token is `8.79 s` and about `47.6 MB` RSS versus heap `8.89 s` and about
`308 MB`; trusted Streaming is still fastest at `8.51 s`.
Child `dffe178a0` adds L1 plumbing to `NexmarkRegionMatrix`. Beam-default-style
q3/q8/q9/q11 were rerun as 1M generated events x20 iterations per process,
three external repeats. Checked Rift wins all four selected generated
methodology rows: q3/q8/q9/q11 are `5.86/9.21/15.03/4.36 s` versus heap
`6.18/9.54/16.27/4.47 s` and improved SafeZone `6.38/10.13/18.10/5.11 s`.
RSS is also much lower than heap. This is generated local-harness evidence,
not real-input proof or exact Beam runner evidence.
Child `54bf38c45` adds L1 plumbing to `GithubArchiveRegionMatrix`. The
two-hour real file-backed byte-slice q1/q2 rows were rerun as 200k real GH
Archive events x3 query iterations per process, three external repeats.
Checked scoped page-token is a modest elapsed/RSS win: q1 is `12.89 s` and
about `101 MB` RSS versus heap `13.17 s` and about `265 MB`; q2 is `12.87 s`
and about `102 MB` RSS versus heap `13.18 s` and about `244 MB`. L2 rows
remain the GC interpretation source and show heap GC around `1.5-1.6%` of
elapsed, so GH Archive remains a useful real-input modest/RSS row rather than
the missing flagship GC-heavy real-input case.
Follow-up L1 retained q2 rows were also collected from the clean child state.
For generated/preloaded GH Archive-shaped q2, each external process ran 20
1M-event iterations. Retained heap is `4.62 s` and about `147 MB` RSS; checked
stream retained is `3.65 s` and about `16 MB`; checked scoped retained is
`3.44 s` and about `16 MB`. The summary-only lower bound is `1.28 s` and
remains topology evidence only. This strengthens the retained-object
memory-management claim in L1 without turning GH Archive file-backed into a
GC-heavy real-input flagship.

Latest ReML/MLKit PLDI-style table:
`evidence/REML_MLKIT_PLDI_TABLE.md` is now the dedicated thesis-facing table.
It recreates the PLDI Figure 9 paper-reported columns and adds local Scala
Native Tier 1 port ratios where available. L1 final-clean Tier 1 rows are now
recorded from child `7573d7577`: `msort` checked stream is `2.06 s` total for
20 iterations versus heap `2.46 s`; `msort-r` checked stream is `2.05 s`
versus heap `2.25 s`; `ratio` checked scoped is `0.91 s` versus heap
`0.93 s` and cuts RSS from about `80 MB` to `16 MB`. `fib37`/`life` are
near-tie controls, and `tak`/`fft`/`mandel` are too short under the current
configuration for headline timing. Exact MLKit/ReML artifact timing is still
open, so do not make raw cross-language "Rift beats ReML" claims.

Latest operator-gate status:
`evidence/OPERATOR_GATE_STATUS.md` records the current gate state for
hash/window join, top-k, mutable keyed rank, median/percentile, and
hash/group-aggregate operators. The immediate decision is conservative:
NEXMark Q8 has the best join evidence because fair heap and checked join API
controls already exist, but it remains gated because the packed checked join
API is lower-RSS yet slower than the specialized heap join API at 1M. LogHub
top templates are the preferred next top-k/rank candidate if we resume
operator work, because real HDFS input is already wired.

Latest LogHub top-template retained matrix:
Child commit `2393a69c4` adds `LogHubTopTemplatesMatrix` and
`sandbox/run_loghub_top_templates_matrix.sh`. It is the first concrete top-k
candidate under the new gate rules. Generated 1M rows show checked scoped
retained top templates `290.610 ms`, `0 ms` GC, and `304 MB` RSS versus
retained heap `424.443 ms`, `126.371 ms` GC, and `408 MB` RSS. Real HDFS
preloaded 1M rows show checked scoped retained top templates `81.174 ms`,
`0 ms` GC, and `150 MB` RSS versus retained heap `116.138 ms`, `31.161 ms` GC,
and `146 MB` RSS. Interpretation: this advances LogHub top templates from
"candidate" to "promising retained top-k operator shape."

Latest reusable top-k API checkpoint:
Child commit `9abac4833` adds `RiftRegion.EpochTopKByKey`, lifting the LogHub
retained top-template shape into a reusable checked epoch operator. It keeps
parent-owned primitive counts and top-k scratch arrays while ordinary
token/template records live in `RiftRegion.epoch`, so close/reclaim still does
not traverse retained records. Generated 1M top-k API rows show checked scoped
`341.905 ms`, `0 ms` GC, and `305 MB` RSS versus retained heap `463.578 ms`,
`138.050 ms` GC, and `408 MB` RSS. Real HDFS preloaded 1M rows show checked
scoped top-k `95.267 ms`, `0 ms` GC, and `150 MB` RSS versus retained heap
`123.024 ms`, `33.966 ms` GC, and `146 MB` RSS. Interpretation: the reusable
API passes the retained top-k gate, but it trails the benchmark-local manual
count-array path (`300.984 ms` generated, `83.697 ms` real HDFS). The next
top-k work should profile or inline the update/getter path before application
integration. L1 final-clean real HDFS x20 rows now confirm the reusable API
direction with external timing/RSS: checked top-k scoped `5.05 s` and about
`28 MB` RSS versus retained heap `5.46 s` and about `205 MB` RSS.

Latest clean retained/direct-epoch rerun:
After committing child `918c7d4c1` and parent `ab570b1`, the retained-object
and representative direct-epoch rows were rerun from clean commits. The clean
retained focused 1M row is now: retained heap `36.233 ms`, `10.109 ms` median
timed GC, and `21.3 MB` RSS; checked retained stream `27.703 ms`, `0 ms` GC,
and `4.8 MB` RSS; checked retained scoped `24.274 ms`, `0 ms` GC, and `4.9 MB`
RSS. This is the clean report-ready memory-management comparison: heap and
checked regions both retain ordinary Scala objects until the epoch boundary,
and neither traverses records at close. Clean application retained rows also
support the claim: GH Archive-shaped q2 checked retained scoped is
`186.868 ms` vs retained heap `257.377 ms` and cuts RSS from about `147 MB` to
`15 MB`; LogHub q2 checked retained scoped is `402.821 ms` vs retained heap
`469.079 ms`; DSPBench Fraud q2 checked retained scoped is `370.746 ms` vs
retained heap `392.743 ms`, removing `35.631 ms` median timed GC but with
slightly higher RSS.

The clean representative direct-epoch rerun confirms the topology story:
SNAP LiveJournal `graphreal` at 50M replayed edges has heap `2958.659 ms`,
`400.484 ms` timed GC, and `3.91 GB` RSS; checked epoch scoped is
`2008.320 ms`, `0 ms` GC, and `2.11 GB` RSS; checked epoch stream is
`2064.867 ms`, `0 ms` GC, and `2.11 GB` RSS. Dataflow
SELECT/AGGREGATE/JOIN are `19.691/34.676/19.762 ms` for checked epoch scoped
versus heap `27.775/50.837/30.387 ms`. StreamFlex throughput is `157.334 ms`
for checked scoped direct epoch versus heap `216.853 ms`; Stancu-style
transactions are `155.863 ms` for checked scoped direct epoch versus heap
`220.951 ms`. These remain L2 standard-stats interpretation rows. For final
elapsed/RSS, use the L1 rows in `evidence/FINAL_CLEAN_HEADLINE_RESULTS.md`:
StreamFlex direct epoch `0.58 s` versus heap `0.79 s`, and Stancu direct epoch
`0.57 s` versus heap `0.85 s`.

Latest direct-epoch extension and same-shape control:
Checked direct-epoch modes were added to DSPBench generated q2, GH
Archive-shaped q2, and LogHub generated q2/q3 where bucket summaries can be
represented as primitive metadata after the region epoch closes. NEXMark
Q3/Q8/Q9/Q11 were reviewed and left on page-token/join/window topology because
their state affects later events. A `heap-direct-epoch` same-shape aggregate
control was added on 2026-05-09. 1M generated/indexable rows now separate
operator topology from memory placement: DSPBench Fraud q2 is heap
`400.900 ms`, heap-direct `272.251 ms`, checked scoped direct epoch
`267.739 ms`; DSPBench Log q2 is heap `372.174 ms`, heap-direct
`227.036 ms`, checked scoped direct epoch `230.374 ms`; GH Archive-shaped q2
is heap `287.380 ms`, heap-direct `54.642 ms`, checked scoped direct epoch
`56.013 ms`; LogHub-shaped q2 is heap `526.803 ms`, heap-direct
`191.601 ms`, checked scoped direct epoch `193.938 ms`; LogHub-shaped q3 is
heap `2225.364 ms`, heap-direct `1779.064 ms`, checked scoped direct epoch
`1792.397 ms`. Interpretation: these are strong direct-aggregate
topology/operator wins. Checked regions are close to same-shape heap, and
Fraud q2 still gives a small checked-region win over same-shape heap, but the
large deltas should not be presented as pure placement wins. File-backed
DSPBench/LogHub and file-backed GH Archive still use page-token modes.

Latest retained-epoch memory-management control:
`RetainedEpochReclaimMatrix` was added on 2026-05-09 with four modes:
`heap-direct-summary-only`, `heap-epoch-retained-no-traverse`,
`checked-epoch-retained-no-traverse`, and
`checked-scoped-epoch-retained-no-traverse`. The retained modes keep ordinary
Scala records linked and alive until epoch close, update primitive summaries on
append, and do not traverse records at close beyond O(1) head/tail anchor
touches. Focused 1M rows now show a clear memory-management win:
retained heap `36.233 ms`, `10.109 ms` median timed GC, and `21.3 MB` RSS;
checked retained stream `27.703 ms`, `0 ms` GC, and `4.8 MB` RSS; checked
retained scoped `24.274 ms`, `0 ms` GC, and `4.9 MB` RSS. DSPBench Fraud q2
1M retained controls also separate topology from reclaim: summary-only lower
bound `286.318 ms`; retained heap `392.743 ms` with `35.631 ms` median timed
GC; checked retained stream `383.628 ms`; checked retained scoped `370.746 ms`.
GH Archive-shaped q2 retained controls are stronger: retained heap
`257.377 ms`, `77.208 ms` GC, and `147 MB` RSS versus checked retained scoped
`186.868 ms`, `0 ms` GC, and `15 MB` RSS. LogHub generated q2 retained shows
checked retained scoped `402.821 ms` versus retained heap `469.079 ms`, while
LogHub q3 is a mixed but still positive checked scoped row (`2106.541 ms`
versus retained heap `2244.266 ms`).
Interpretation: summary-only direct epoch remains topology evidence, while
retained heap vs retained checked epoch is fair Rift memory-management
evidence. Fraud q2 is a throughput/GC win, not an RSS win, because checked
retained RSS is slightly higher than retained heap in that row.

Latest page-token fast-path checkpoint:
On 2026-05-07, `StreamPageTokenAppendWindow` got a batch-close/current-bucket
fast path: `StreamAppendCursor.nextOrNull()`, page-token-owned close without
the generic leftover-drain loop, and a monotonic same-bucket region fast path
when the current bucket is the only live bucket.
Validation passed `sandbox3_next/compile`, `RiftRegionCheckedCompilerTest`
`118/118`, and `RiftRegionCheckedTest` `50/50`. Focused 1M append rows:
heap `36.920 ms`, checked Rift page-token `29.319 ms`, checked SafeZone-backed
page-token `27.549 ms`; chunk-token remains slower. DSPBench Fraud q2 had a
dirty fast-path direction check where checked SafeZone-backed page-token was
fastest (`818.574 ms` vs heap `862.834 ms`), but the later clean
committed-code rerun is more conservative: trusted Streaming `788.040 ms`,
checked SafeZone-backed page-token `810.770 ms`, and heap `820.945 ms`, with
checked RSS about `279 MB` vs heap `358 MB`. Generated Common Crawl-shaped 100k q1/q2
also strengthened: checked SafeZone-backed page-token is fastest on q1
(`370.758 ms`) and q2 (`377.482 ms`). Treat these as post-fast-path evidence;
older Fraud q2 checked-loses rows remain useful as pre-optimization baseline.

Latest post-fast-path selected sweep:
`evidence/POST_FAST_PATH_SELECTED_SWEEP_2026_05_07.md` records a selected 1M
rerun from the current dirty page-token checkpoint. Dataflow SELECT remains a
strong reusable operator row: scoped checked page-token `18.572 ms` versus
heap `28.942 ms` and improved SafeZone `22.463 ms`. NEXMark Beam-default q3,
q8, q9, and q11 all have checked Rift fastest in the same-run selected pass.
Generated Common Crawl-shaped 1M q1/q2 now have checked SafeZone-backed
page-token fastest on both q1 (`3840.668 ms` vs heap `5618.631 ms`) and q2
(`3839.158 ms` vs heap `5303.179 ms`); heap spends about `1.6 s` in timed GC
on each. This strengthens checked page-token and checked scoped backend as
public candidates, but because the sweep is dirty it should be rerun from a
clean commit before final paper tables.

Latest clean page-token cost checkpoint:
The dirty page-token fast-path work was committed in child commit
`236422fea` and parent commit `af9deb9`. A clean selected rerun then confirmed
the direction: focused append has heap `36.722 ms`, checked page-token
`28.397 ms`, and checked scoped page-token `27.240 ms`; Dataflow SELECT clean
scoped page-token is `18.326 ms`; NEXMark q3/q8/q9/q11 keep checked Rift
fastest in the selected rows; generated Common Crawl-shaped q1 checked scoped
page-token is `3759.175 ms` vs heap `5466.724 ms`, and q2 rerun is
`3784.863 ms` vs heap `5213.380 ms`. A new
`CheckedPageTokenCostMatrix` splits same-shape costs into `append-only`,
`append-drain`, and `append-aggregate`. The no-drain close API is safe and the
runtime suite passes `51/51`, but the 1M cost matrix shows no-drain close is
not the main remaining bottleneck. The committed-code DSPBench Fraud q2 rerun
is more conservative than the dirty run: trusted Streaming `788.040 ms`,
checked scoped page-token `810.770 ms`, heap `820.945 ms`, with checked RSS about
`279 MB` vs heap `358 MB`.

Latest owned-cursor page-token checkpoint:
On 2026-05-07, `StreamAppendCursor.nextOwnedOrNull()` was added for
operator-owned page-token close callbacks. It advances without clearing each
record link; generic `next()`/`nextOrNull()` remain defensive. Static safety
justification: page-token close clears parent bucket refs before the callback,
the callback cannot retain region records, and the child region closes
immediately after cleanup. Validation passed `sandbox3_next/compile`,
`RiftRegionCheckedCompilerTest` `120/120`, and `RiftRegionCheckedTest`
`52/52`. Focused 1M checked scoped page-token improved to
`73.590/83.997/81.296 ms` on append-only/drain/aggregate, compared with the
previous no-length rows `77.135/88.840/85.362 ms`. DSPBench Fraud q2 now has
checked scoped page-token `800.369 ms` vs heap `807.974 ms`, with RSS
`278577152` vs heap `358301696`; trusted Streaming remains fastest at
`785.682 ms`. Generated Common Crawl-shaped 1M q1/q2 has checked scoped
page-token `3643.680/3790.138 ms` vs heap `5392.344/5201.862 ms`, cutting
timed GC from about `1.58 s` to about `32 ms`.

Latest real-input search checkpoint:
On 2026-05-08, the official RIoTBench source was cloned into ignored cache
at `/Users/siyaoliu/rift/cache/benchmark-data/riot-bench/source`, commit
`c86414f7f926ed5ae0fab756bb3d82fbfb6e5bf7`. The bundled RIoTBench SenML
samples are tiny (`45-1000` rows), so UCI MHEALTH was downloaded as the
RIoTBench/FIT-style real input. `RiotBenchRegionMatrix` now accepts
`RIOTBENCH_INPUT_KIND=mhealth` and a directory of subject logs. The MHEALTH
dataset has `1215745` rows. A 1M q1/q2 pass matched checksums but showed zero
timed heap GC: q1 heap `117.977 ms`, SafeZone `121.024 ms`, trusted Streaming
`119.077 ms`; q2 heap `109.589 ms`, SafeZone `107.194 ms`, trusted Streaming
`110.760 ms`. Decision: MHEALTH is provenance-clean RIoTBench evidence but a
ceiling/control row, not the missing GC-heavy real stream case.

Continuation on 2026-05-08 added two more real-input search artifacts:
Theodolite source and LogHub HDFS v1. Theodolite was cloned into ignored cache
at `/Users/siyaoliu/rift/cache/benchmark-data/theodolite/source`, commit
`dfa768a25eec3c3f5a57b7d4839a0c255fd6fa7d`. It has good UC2/UC4
downsampling/hierarchical-aggregation methodology, but the official load
generator simulates active-power records, so it should be paired with a real
industrial-energy trace before becoming real-input evidence. LogHub HDFS v1
was downloaded from Zenodo v7 and extracted to
`/Users/siyaoliu/rift/cache/benchmark-data/loghub/HDFS_1/HDFS.log`
(`11175629` lines, `1576383671` bytes). A 20k smoke passed, then a 1M q1/q2/q3
run completed over heap, improved SafeZone-32k, trusted Streaming, and checked
scoped page-token. HDFS q2 is the best new row: checked scoped page-token
`7871.856 ms` and trusted Streaming `7871.713 ms` versus heap `8227.369 ms`;
heap median GC is `92.659 ms`, and checked/scoped rows lower RSS. This is a
useful real-input modest throughput/RSS/GC win, but still not the missing
flagship because heap GC remains only about 1-2% of elapsed.

Latest Yak real-input checkpoint:
On 2026-05-08, `YakRegionMatrix` added `graphreal`, a real edge-list replay
over the SNAP Twitter ego graph at
`/Users/siyaoliu/rift/cache/benchmark-data/yak/snap/twitter_combined.txt.gz`.
The input has `2420766` edges and SHA-256
`d9f99b0e6a53b9204b8c215f41b3c10fb99a1e1e783858c012b06d0d3d4bd129`.
The benchmark preloads real source/destination pairs into primitive control
arrays, maps vertex IDs into the configured vertex space, and replays them as
epoch-local `EdgeUpdate` objects. A 20k smoke matched checksums. The 1M 3-run
median has `gc-heap` `31.202 ms`, median timed GC `5.267 ms`, RSS
`74792960`; `region-scoped-rooted` `23.919 ms`; `region-hp-rootless`
`24.383 ms`; `region-stream-rootless` `24.315 ms`; `yak-runtime-proxy`
internal control `27.566 ms`. Region rows report zero timed GC and about
`42.2 MB` RSS. A 2M follow-up also matched checksums: `gc-heap`
`63.454 ms`, RSS `172523520`; `region-scoped-rooted` `47.967 ms`;
`region-hp-rootless` `48.474 ms`; `region-stream-rootless` `49.557 ms`;
region RSS about `65 MB`. The 2M `gc-heap` median GC is `0.000 ms` but one
timed heap run collected for `16.857 ms`.
Interpretation: this proved the real-edge input path, but LiveJournal below is
now the stronger Yak-shaped real-input row. Twitter ego remains useful as a
small smoke/regression input.

LiveJournal follow-up:
On 2026-05-08, SNAP LiveJournal was downloaded to
`/Users/siyaoliu/rift/cache/benchmark-data/yak/snap/soc-LiveJournal1.txt.gz`
(`68993777` edge-list lines, SHA-256
`d7bcd5a87b88c896c35fdb9611e804c3f4033c39b58c4c9ea3ba53c680d516d8`).
`graphreal` 5M and 10M 3-run medians matched checksums, including the new
checked page-token modes. At 5M replayed real edges, `region-stream-rootless`
is `130.716 ms`, `region-scoped-rooted` `139.264 ms`,
`checked-region-scoped` `146.845 ms`, and `checked-region-stream`
`150.667 ms`, versus `gc-heap` `173.832 ms`; `gc-heap` median GC is
`33.456 ms`, with RSS `322699264` versus about `190 MB` for region rows. At
10M, `region-scoped-rooted` is fastest at `249.543 ms`,
`region-stream-rootless` is `257.299 ms`, `checked-region-scoped` is
`272.072 ms`, `checked-region-stream` is `286.336 ms`, and `gc-heap` is
`319.560 ms` with `51.987 ms` median timed GC and RSS `605569024`; region RSS
is about `328.6 MB`. The first 50M follow-up made the timing less short-run
dominated and showed checked page-token also beats heap. A second 10M/50M
topology follow-up then split checked whole-run, checked epoch, and checked
page-token. In the latest clean 50M rerun, `gc-heap` is `2958.659 ms`, median
GC `400.484 ms`, RSS `3913564160`; low-RSS epoch rows are
`checked-epoch-scoped` `2008.320 ms`, `checked-epoch-stream` `2064.867 ms`,
`region-scoped-rooted` `2351.582 ms`, and `region-stream-rootless`
`2499.975 ms`, all around `2.11 GB` RSS. Page-token checked rows still beat
heap but are slower for Yak: `checked-page-token-scoped` `2586.919 ms`,
`checked-page-token-stream` `2746.897 ms`. This replaces
Twitter ego as the best real-input Yak-style row and clarifies the design:
checked regions need explicit user-visible topology (`epoch`, `window`,
`page`), not one universal checked operator. It remains local graph replay
rather than exact Yak/GraphChi artifact evidence.

Reusable Yak epoch follow-up:
`EpochBuffer` is now wired into `graphreal` through `checked-epoch-buffer-scoped`
and `checked-epoch-buffer-stream`. The reusable API is correct and still beats
heap in an earlier LiveJournal follow-up, but it trailed the direct linked
epoch path. Interpretation: the reusable checked epoch API shape is right, but
the implementation should lower to the direct linked-epoch path rather than
the generic `EpochBuffer` append/cursor machinery.
`RiftRegion.epoch { ... }` is now implemented as the reusable checked linked
epoch block. It provides an `OpenStreamingRegion` so epoch-local objects can
use `allocOpen`; on the Rift streaming backend it resets at the epoch boundary,
and on the SafeZone-backed checked backend it opens/closes a scoped child
region. `checked-epoch-*` Yak modes now route through this API. Validation
after this API/test update: `sandbox3_next/compile` passed,
`RiftRegionCheckedCompilerTest` passed `123/123`, `RiftRegionCheckedTest`
passed `55/55`, and a 2-epoch SNAP Twitter `graphreal` smoke matched checksums
across heap, checked epoch, and reusable `EpochBuffer` modes. A 10M
LiveJournal API-backed rerun then confirmed the reusable linked-epoch direction:
`checked-epoch-scoped` `417.426 ms`, `checked-epoch-stream` `425.983 ms`, and
`gc-heap` `599.428 ms`, with region rows around `459 MB` RSS versus heap
`606 MB`. A clean 50M rerun also passed: `checked-epoch-scoped` is
`2008.320 ms`, `checked-epoch-stream` is `2064.867 ms`, and `gc-heap` is
`2958.659 ms` with `400.484 ms` timed GC; region RSS is about `2.11 GB` versus
heap `3.91 GB`.
The same reusable `RiftRegion.epoch` topology now covers local Yak-shaped
`wordcount`, `graphstep`, `sort`, `topword`, and `graphchi`; at 10M logical
objects, `checked-epoch-scoped` is fastest among measured heap/rooted/streaming
rows for wordcount/graphstep/topword/graphchi. `sort` is now covered by a
checked region-captured array topology and remains CPU-bound/modest.

Reusable Dataflow epoch follow-up:
The same direct `RiftRegion.epoch { ... }` topology is now wired into
`DataflowRegionMatrix` as `checked-epoch-scoped` and `checked-epoch-stream`.
A 2-epoch x 1000-doc smoke matched heap checksums for SELECT, AGGREGATE, and
JOIN. The 1M 3-run matrix at 10 epochs x 100k documents then showed direct
checked scoped epoch as the fastest full-operator row:
`19.691/34.676/19.762 ms` for SELECT/AGGREGATE/JOIN versus heap
`27.775/50.837/30.387 ms` and region-scoped rooted
`22.971/39.665/22.619 ms`; heap timed GC was
`6.828/11.564/9.331 ms`. The SELECT-only checked scoped page-token row remains
a useful control, but it does not cover AGGREGATE/JOIN. The old
generic `checked-epoch-fold` aggregate remains speed-gated at `93.491 ms`.
This confirms the next implementation sequence: apply direct epoch topology to
other epoch-shaped workloads before designing new operator families.

Reusable Yak sort array follow-up:
The previous remaining Yak direct-epoch gap, `sort`, is now wired through a
checked region-captured array topology. The checked path allocates
`Array[SortRecord^{epoch}]^{epoch}` plus region-owned `SortRecord` objects
inside `RiftRegion.epoch`, sorts the array, and consumes it before closing the
epoch. A 2-epoch x 1000-record smoke matched heap checksums. The 1M
grouped-sort 3-run matrix gives `checked-epoch-stream` `230.000 ms`,
`checked-epoch-scoped` `230.799 ms`, trusted streaming `231.458 ms`, improved
SafeZone `233.068 ms`, and heap `235.554 ms` with `3.333 ms` timed GC.
Interpretation: this closes the checked topology gap and validates
region-owned arrays, but sort is mostly CPU-bound and should be reported as a
modest coverage win rather than a flagship GC result.

Reusable StreamFlex direct epoch follow-up:
The same `RiftRegion.epoch { ... }` topology is now wired into
`StreamFlexRegionMatrix` as `rift-checked-direct-epoch` and
`rift-checked-safezone-direct-epoch`. The direct checked path preserves the
four-stage logical StreamFlex pipeline but allocates ordinary linked packet,
decoded, classified, and alert objects inside one checked epoch block per
batch/event, instead of using four stacked `EpochBuffer`s or one
`TransactionRegion` with framework-owned lists. A 20k smoke matched heap
checksums. The 200k throughput/10k latency matrix gives scoped direct epoch
`32.029 ms` throughput and `9.636 ms` latency, both fastest in that same-run
matrix. The 1M throughput rerun gives scoped direct epoch `163.339 ms`, direct
stream epoch `185.550 ms`, trusted Streaming `182.246 ms`, improved SafeZone
`208.653 ms`, heap `218.582 ms` with `44.681 ms` timed GC, and scoped checked
`TransactionRegion` `205.929 ms`. Interpretation: `TransactionRegion` remains
a useful multi-list control, but direct checked epoch is now the right
reusable StreamFlex-shaped topology when all temporary stage objects share one
batch lifetime.

Reusable Stancu direct epoch follow-up:
`StancuRegionMatrix` now accepts `rift-checked-direct-epoch` and
`rift-checked-safezone-direct-epoch`. The checked path uses one
`RiftRegion.epoch { ... }` block per transaction batch; ordinary transaction
line/order objects live in the epoch, while stock, revenue, and customer
accounting arrays remain durable heap control state. A 20k smoke matched
heap checksums. The 200k matrix gives scoped direct epoch `31.638 ms`, direct
stream epoch `35.196 ms`, improved SafeZone `37.468 ms`, trusted Streaming
`44.880 ms`, and heap `45.211 ms`. The 1M matrix gives scoped direct epoch
`160.198 ms`, direct stream epoch `174.137 ms`, improved SafeZone
`186.122 ms`, trusted Streaming `219.668 ms`, and heap `225.798 ms` with
`23.901 ms` timed GC. Interpretation: this turns the local Stancu-style row
from a trusted/SafeZone-family story into a checked direct-epoch win. It is
still local methodology evidence, not exact Stancu/SPECjbb2005 reproduction.

SPECjbb2005-workload port checkpoint:
The official SPECjbb2005 artifact is a JVM benchmark, so it cannot be an
official Scala Native/Rift run. The new `SpecJbb2005PortMatrix` is therefore a
documented clean-room Scala Native workload port, not an official SPEC result.
It covers warehouses 4 through 8 with 100,000 transactions per warehouse and
64 transactions per epoch. Checksums match across all modes. L1 final-clean
8-warehouse rows from child `678a6eb41` show checked epoch scoped `2.21 s`
versus heap `2.64 s` and rooted scoped region `2.48 s` for 20 inner
iterations, with RSS about `8.0 MB` versus heap `12.4 MB`. The L2 scale row
for 8 warehouses remains the GC interpretation source:
`checked-epoch-scoped` is `108.649 ms`, `checked-epoch-stream` is
`114.651 ms`, and heap is `129.674 ms` with `15.125 ms` timed GC. The port
records Stancu-style axes including region-freed object/byte proxy, max live
region payload proxy, GC time/count, RSS, and annotation/API-boundary count.
Use `evidence/SPECJBB2005_PORT_MATRIX.md` and
`docs/STANCU_SPECJBB2005_PORT_PLAN.md`.

ReML/MLKit table checkpoint:
`evidence/REML_COMPARISON_MATRIX.md` now includes a paper-style combined
snapshot: paper-reported ReML/MLKit columns on the left and local Scala Native
port ratios on the right. Exact MLKit/ReML artifact rerun remains open and is
not required for the current table, but it is still required before any raw
cross-language "Rift beats ReML" timing claim.

Validation for the SPECjbb/ReML update:

- child `git diff --check`: passed;
- parent `git diff --check`: passed;
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`:
  passed before the SPECjbb scale rows;
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`:
  passed `123/123`;
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`:
  passed `59/59`.

Clean direct-epoch sweep:
After checkpointing child commit `918c7d4c1` and parent commit `ab570b1`, a
clean representative direct-epoch sweep was run and recorded in
`evidence/DIRECT_EPOCH_TOPOLOGY_MATRIX.md`. Main rows: 50M LiveJournal checked
epoch scoped `2008.320 ms`, `0.000 ms` GC, about `2.11 GB` RSS versus heap
`2958.659 ms`, `400.484 ms` GC, about `3.91 GB` RSS; Dataflow
SELECT/AGGREGATE/JOIN checked epoch scoped `19.691/34.676/19.762 ms` versus
heap `27.775/50.837/30.387 ms`; StreamFlex 1M scoped checked direct epoch
`157.334 ms` versus heap `216.853 ms`; Stancu 1M scoped checked direct epoch
`155.863 ms` versus heap `220.951 ms`. This is now the canonical clean
representative direct-epoch evidence pack.

Important interpretation note: timed GC is collection time only, not total
memory-management cost. In HDFS q2, checked scoped page-token is about
`355 ms` faster than heap, while heap timed GC is only `92.659 ms`. The rest
of the gap should be attributed cautiously to mutator-side memory behavior:
heap allocation path overhead, heap growth/metadata effects, RSS/cache
locality, object lifetime placement, and region append/close bookkeeping.
Future reports should keep direct GC metrics separate from allocation/RSS and
diagnostic append/bucket/traversal attribution instead of implying timed GC
alone explains elapsed speedups.

Latest open-allocation page-token checkpoint:
On 2026-05-07, checked page-token operators gained an internal
`RiftRegion.OpenStreamingRegion` marker plus `RiftRegion.allocOpen(...)`.
The Scala Native lowering now routes `Classalloc(OpenStreamingRegion)` through
`RiftRegion.allocUncheckedImpl(...)`, avoiding the generic checked
`allocImpl/checkOpen` path only for operator-owned page-token buckets that are
known open by construction. Generic public checked allocation remains
defensive. Validation passed `RiftRegionCheckedCompilerTest` `120/120`,
`RiftRegionCheckedTest` `52/52`, and `sandbox3_next/compile`; a linker
reachability fix was required so the lowered dynamic method table entry for
`allocUncheckedImpl` is non-null. Focused 1M rows are modest: checked scoped
page-token is `73.632/83.177/82.198 ms` on append-only/drain/aggregate versus
heap `76.295/85.873/84.354 ms`; checked scoped count-by-key is `95.946 ms`
versus heap `103.946 ms`. DSPBench Fraud q2 improves slightly to checked
scoped `797.782 ms` versus heap `806.697 ms` and trusted Streaming
`778.975 ms`, with checked RSS `278.5 MB` versus heap `358.3 MB`. Generated
Common Crawl-shaped 1M q1/q2 remains strong: checked scoped page-token is
`3707.214/3902.795 ms` versus heap `5577.965/5183.074 ms`; heap spends
`1741.640/1565.074 ms` in timed GC while checked scoped spends
`30.693/27.027 ms`. Interpretation: removing `checkOpen` is a real static
safety cleanup but not the dominant remaining cost. Page-token wins now come
mostly from the operator-owned lifetime shape and scoped backend; remaining
costs are object construction, append/linking, cursor/query traversal, and
shared application CPU. Sources: `evidence/CHECKED_PAGE_TOKEN_COST_MATRIX.md`,
`evidence/DSPBENCH_REGION_MATRIX.md`, and `evidence/COMMON_CRAWL_WET_MATRIX.md`.

Latest post-open-allocation profiling checkpoint:
On 2026-05-07, macOS `/usr/bin/sample` target profiles were captured after
delaying past each harness's built-in heap expected-control phase. Generated
Common Crawl-shaped q2 checked scoped at 3M pages (`12093.317 ms`,
`93.269 ms` GC, `2788398` outputs) now shows `allocUncheckedImpl` rather than
`allocImpl/checkOpen`; the remaining sampled paths are `closeRecords`,
`appendPageTokenOwnedOpen`/`appendPageToken`, `scalanative_zone_alloc` plus
`memset`/alignment, `StreamAppendCursor.nextOwnedOrNull`, and token-hash/query
work. Real DSPBench Fraud q2 checked scoped at 5M replayed `credit-card.dat`
events (`4245.059 ms`, `72.687 ms` GC, `3308061` outputs) is dominated by
`ByteLineReader` parsing/replay, `stableHash`, `FraudPredictorState.update`,
CSV/state parsing, append, and close traversal. Interpretation: `checkOpen`
has been removed from the targeted checked allocation path; the next code step
should not be another open-check patch. Either profile/reduce append/cursor
layout/zeroing with a fair heap same-shape control, or resume the real-input
benchmark search. Source: `docs/CPU_PROFILE_REPORT.md`.

Latest DSPBench Log Processing checkpoint:
On 2026-05-07, `DSPBenchRegionMatrix` added a third real-input DSPBench
candidate using the bundled Spark Log Processing `http-server.log` file
(`55000` real common-log lines). New query tiers are `log-q0-parse`,
`log-q1-status`, and `log-q2-window`. The runner now selects the log input for
`log-*` queries. Compile passed, and 20k smoke plus 100k/1M 3-run medians
matched checksums/output counts across heap, improved SafeZone, trusted
Streaming, and checked scoped page-token. At 1M, q2 is the best log row:
checked scoped page-token is fastest (`1733.654 ms` vs heap `1750.291 ms` and
trusted Streaming `1737.469 ms`) and cuts heap max GC from `88.210 ms` to
`18.584 ms`; however heap GC is only about `2.6%` of elapsed and region RSS is
higher (`322.0 MB` vs heap `307.8 MB`). Interpretation: keep DSPBench Log q2
as a real-input modest throughput/GC-tail control and page-token regression
row, not as the flagship GC-heavy case. Sources:
`evidence/DSPBENCH_REGION_MATRIX.md`,
`evidence/REAL_INPUT_BENCHMARK_SEARCH.md`, and
`evidence/EVALUATION_SUMMARY_TABLES.md`.

Latest LogHub richer real-input checkpoint:
On 2026-05-08, `LogHubRegionMatrix` added `q3-template-session`, a richer BGL
query that parses message suffixes into template buckets, derives session
buckets from node/template fields, allocates template-token and
session-candidate records, and counts sessions by window. Compile passed, and
20k smoke plus 100k/1M medians matched checksums/output counts across heap,
improved SafeZone-32k, trusted Streaming, and checked scoped page-token. At 1M
real BGL lines, heap is `8683.558 ms`, median/max GC `84.166/117.946 ms`, RSS
`290242560`; trusted Streaming is `8615.627 ms`, median GC `21.841 ms`, RSS
`236814336`; checked scoped page-token is `8722.008 ms`, median GC `34.865 ms`,
RSS `236961792`. Interpretation: q3 validates richer real log object placement
and cuts RSS/tails, but heap GC is still under 1% of elapsed and checked scoped
does not win throughput. Park LogHub q3 as real-input modest/control evidence;
continue toward RIoTBench/Theodolite-style IoT records, larger provenance-clean
machine/security traces, or another real stream with naturally heavier
intermediate object materialization. Sources:
`evidence/LOGHUB_REGION_MATRIX.md`,
`evidence/REAL_INPUT_BENCHMARK_SEARCH.md`, and
`evidence/EVALUATION_SUMMARY_TABLES.md`.

Latest page-token attribution checkpoint:
Child diagnostics now include `estimated_bucket_open_ms` for DSPBench and
Common Crawl page-token rows, because raw bucket-switch timing includes
expired-bucket close work. Non-headline one-run diagnostics show bucket
open/switch itself is not the bottleneck. On generated Common Crawl-shaped 1M
q1/q2, estimated bucket open is about `3-10 ms`, while allocation+append is
about `3.18-3.52 s` and close-cursor traversal about `0.76-0.81 s` for
`137M` records. On real DSPBench Fraud q2, estimated bucket open is below
`1 ms`; trusted Streaming append is `131.493 ms`, checked scoped page-token
append is `144.353 ms`, heap append is `186.048 ms`, and checked close cursor
is about `63.456 ms` versus trusted `56.087 ms`. Interpretation: region
allocation+append is already faster than heap in the Fraud diagnostic; the
remaining checked gap is cursor/node traversal plus common query/replay CPU,
not bucket opening. Source docs:
`docs/CPU_PROFILE_REPORT.md`, `evidence/CHECKED_OVERHEAD_REMOVAL_MATRIX.md`,
`evidence/COMMON_CRAWL_LIKE_MATRIX.md`, and
`evidence/DSPBENCH_REGION_MATRIX.md`.

Latest append-time aggregate/no-drain checkpoint:
`RiftRegion.PageTokenCountByKey[T]` is now implemented as a reusable checked
page-token aggregate operator. Ordinary records still live in child bucket
regions, but parent-owned primitive arrays track per-key counts/sums during
append, so close can emit summaries without walking every record. Safety
validation passed: `sandbox3_next/compile`, `RiftRegionCheckedCompilerTest`
`120/120`, and `RiftRegionCheckedTest` `52/52`. The compiler guard was fixed
for this API because the checked value is not the last argument. Focused
`append-count-by-key` 100k rows did not beat heap (`heap-same-shape`
`8.906 ms`, checked SafeZone-backed count-by-key `9.836 ms`). At 1M, the
shape is a modest win: heap `105.915 ms` with `14.026 ms` GC, checked Rift
count-by-key `98.761 ms` with `0.000 ms` GC, and checked SafeZone-backed
count-by-key `97.860 ms` with `0.000 ms` GC. Interpretation: append-time
aggregate/no-drain is a valid reusable operator direction, but not a broad
checked-overhead solution. Use it only where the query naturally updates
aggregate metadata on append and can close buckets without per-record
traversal. Source: `evidence/CHECKED_PAGE_TOKEN_COST_MATRIX.md`.

Latest page-token live-length bookkeeping checkpoint:
Page-token, `PageTokenMapFilter`, and `PageTokenCountByKey` appends now use a
page-token-owned helper that skips the underlying generic append-window
`totalLength` counter while preserving per-bucket `appendLength` for close and
cursor logic. Generic `StreamAppendWindow` and `EpochBuffer` length APIs remain
defensive and unchanged. Validation passed: `sandbox3_next/compile`,
`RiftRegionCheckedCompilerTest` `120/120`, and `RiftRegionCheckedTest`
`52/52`; 20k smoke matched checksums. A source-level `inline` version was
tried and rejected by capture checking, so the likely next speed target is
compiler/runtime allocation lowering rather than source-level helper inlining.
Focused 1M rows are modest: checked scoped page-token is `77.135/88.840/85.362
ms` on append-only/drain/aggregate versus heap `81.535/90.374/86.988 ms`, and
checked scoped count-by-key is `102.504 ms` versus heap `114.143 ms`. The
DSPBench Fraud q2 application control did not become a representative checked
throughput win: heap is `842.739 ms`, trusted Streaming `832.012 ms`, checked
Rift page-token `854.207 ms`, and checked SafeZone-backed page-token
`843.380 ms`; checked scoped still cuts RSS (`278.6 MB` vs heap `358.3 MB`)
and timed GC (`15.245 ms` vs heap `72.387 ms`). Interpretation: the
bookkeeping removal is justified but not a large speedup. Do not keep shaving
bucket open/close counters unless a profile points there; next checked work
should target the generated `allocImpl`/`checkOpen` allocation path under
operator-owned static safety. Sources:
`evidence/CHECKED_PAGE_TOKEN_COST_MATRIX.md`,
`evidence/DSPBENCH_REGION_MATRIX.md`, and `docs/CPU_PROFILE_REPORT.md`.

Latest count-by-key application-gate checkpoint:
Common Crawl-shaped q2 now has opt-in `rift-checked-count-by-key` and
`rift-checked-safezone-count-by-key` modes. They preserve the record
materialization shape but update domain counts during append and close buckets
without record drain. Compile passed, and the 20k smoke matched
checksum/output count across heap, existing page-token, and count-by-key
modes. The 100k 3-run application gate failed: existing checked page-token is
faster than count-by-key. q2 heap is `525.285 ms` with `151.164 ms` GC;
checked page-token is `433.051 ms`; checked count-by-key is `476.665 ms`;
checked SafeZone-backed page-token is `406.413 ms`; checked SafeZone-backed
count-by-key is `450.289 ms`. Decision: keep `PageTokenCountByKey` as a
focused modest-win operator and application-gated control. Do not replace the
Common Crawl q2 page-token row with it unless a future workload has close-time
traversal much more expensive than per-record primitive count updates. Source:
`evidence/COMMON_CRAWL_LIKE_MATRIX.md`.

Latest CPU profile checkpoint:
Two macOS `/usr/bin/sample` diagnostics were captured for generated Common
Crawl-shaped q2 at 2M pages after delaying past the harness's built-in heap
expected-control phase. Artifacts:
`/Users/siyaoliu/rift/cache/profile-common-crawl-q2-page-token-target-2026-05-07/sample.txt`
and
`/Users/siyaoliu/rift/cache/profile-common-crawl-q2-rift-page-token-target-2026-05-07/sample.txt`.
The checked SafeZone-backed page-token timed row was `7719.982 ms` with
`69.545 ms` GC and about `440 MB` physical footprint; top sampled paths are
`closeRecords`/`StreamAppendCursor.nextOrNull`, `appendWindowOwnedOpen` /
`appendPageToken`, `scalanative_zone_alloc`/`memset`,
`MemorySafeZoneBackedRiftRegion.allocImpl/checkOpen`, and token-hash/query
work. The checked Rift page-token timed row was `8190.974 ms` with
`38.480 ms` GC, `26.032 ms` Rift op, and `274000000` region objects; top
sampled paths add `scalanative_rift_region_alloc/raw`,
`scalanative_rift_normalize_align`, `scalanative_rift_stats_record_alloc_bytes`,
and `MemoryRiftRegion.allocImpl/checkOpen`. Interpretation: bucket opening is
not the hot path; remaining overhead is allocation zeroing/lowering/stat
checks, operator append/linking, close traversal, and shared token-hash/query
CPU. Source: `docs/CPU_PROFILE_REPORT.md`.

Latest final-selection sweep checkpoint:
Clean run `2026-05-06-final-selection-headline` completed after committing the
safety/default-runner checkpoint. Source summary:
`evidence/FINAL_SELECTION_HEADLINE_2026_05_06.md`. It ran from parent
`72dc1dfb974cc1620dc950a8ff2fb104233ec8b0` and child
`458c556d20698887d753fc29969847dc29ac8cb4` with `include_controls=0`.
Key outcomes: checked scoped page-token wins focused append and generated
Common Crawl-shaped q1/q2; checked page-token wins generated GH Archive-shaped
q1/q2; checked builder wins linked ListOfLists; ReML-shaped Tier 1 medians now
exist; generic fold/join/rank-heavy operators remain gated.

Latest ReML/MLKit comparison checkpoint:
Phase 6c has been scaffolded as a separate comparison track. New files:
`docs/REML_COMPARISON_PLAN.md`,
`evidence/REML_COMPARISON_MATRIX.md`,
`scala-native-rift/sandbox/REML_COMPARISON_MATRIX.md`,
`scala-native-rift/sandbox/run_reml_region_matrix.sh`, and
`scala-native-rift/sandbox/src/main/scala-next/ReMLRegionMatrix.scala`.
The evidence file transcribes the Elsman 2023 ReML Figure 9 table as
paper-reported/not-rerun data, while the Scala Native matrix implements Tier 1
ReML-shaped ports (`fib37`, `tak`, `mandel`, `msort`, `msort-r`, `life`,
`fft`, `ratio`). A reduced-size all-Tier-1 smoke run matched checksums across
`gc-heap`, `checked-region-stream`, and `checked-region-scoped`, and the
`ratio` port was fixed to retain allocated region objects so checked
allocation is not optimized away. A direct Tier 1 3-run median matrix was run
on 2026-05-06. The meaningful local allocation/RSS rows are `msort`
(`checked-region-stream` `104.358 ms` vs heap `124.983 ms`), `msort-r`
(`104.929 ms` vs heap `126.163 ms`), and `ratio` (`checked-region-scoped`
`48.929 ms` vs heap `51.302 ms`, with RSS cut from about `44 MB` to
`16 MB`). `fib37`, `tak`, `mandel`, and `life` are mostly compute/control
rows. These are Scala Native ReML-shaped ports, not exact ReML reproduction.

ReML exact-artifact reproduction update:
The public MLKit repository has been cloned into ignored cache at
`/Users/siyaoliu/rift/cache/reml/mlkit`, full history/tags were fetched, and
the inspected HEAD is `8561fe6ad949b84f83e8b78508b720ceccabe902`. The clone
contains many Figure 9-style benchmark sources under `test/` and `kitdemo/`.
Relevant tags are `v4.7.4` (`855248bf`, initial explicit region/effect
annotation support), `v4.7.5` (`5f0f811d`, ReML released), and `v4.7.6`
(`71c2630e`, later datatype-unboxing release). This makes exact reproduction
plausible, but no local `mlkit`/`mlton` executables are installed yet and the
paper labels `rg`, `rg-`, and `r` still need verified command mappings. Do not
claim raw "Rift beats ReML" until those exact local runs exist.
`scripts/reml-mlkit-docker-smoke.sh` now provides the first reproducible
amd64-container smoke scaffold for building MLKit from `v4.7.5` and compiling
`msort`, `fft`, and `ratio`. Docker is installed on this machine but the daemon
was not running when checked again on 2026-05-06 23:45 CEST, so the smoke
script has not been executed.
`scripts/reml-mlkit-docker-bench-draft.sh` adds a draft benchmark runner for
`rg`, `rg-`, `r`, and `MLton` using a source-inspected mapping
(`mlkit`, `mlkit -disable_spurious_type_variables`, `mlkit -no_gc`, and
`mlton`). Treat any rows from it as provisional until the paper/artifact flag
mapping is confirmed.

ReML-inspired safety checkpoint:
The checked compiler suite now includes local polymorphic consumer acceptance,
polymorphic identity escape rejection, durable/static generic heap-cell
retention rejection, widened `AnyRef` rejection, heap-array retention
rejection, escaping-closure hiding rejection, and polymorphic unrooted
heap-value constructor rejection. The previously ignored ReML-style generic
heap-retention probe is now active and passing. This fixes the current probe
gap, but it is still not a full arbitrary heap alias analysis; do not make
rootless checked safety claims until root-free eligibility is separately
proved.

Latest safety/component-selection checkpoint:
`nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirGenExpr.scala` now
tracks heap values derived from known Rift region allocations/factories and
rejects storing those values into durable/static heap state. The fix keeps
local nonescaping polymorphic heap objects legal inside a region scope and
scopes the diagnostic away from Java/Scala platform-library implementation
classes. `docs/FINAL_COMPONENT_SELECTION.md` records the public/internal
component split: checked scoped backend and checked page-token are public
candidates; rootless modes stay internal lower-bound controls; `EpochFold`,
`TableRank`, rank-heavy structures, and chunk append remain gated/rejected.
Validation after this change:
`RiftRegionCheckedCompilerTest` passed `118/118`, `RiftRegionCheckedTest`
passed `49/49`, and `sandbox3_next/compile` passed.

Design/report update after the ReML discussion:
`docs/DESIGN.md` now records the erased-generic heap-retention rule as active
current compiler evidence: generic heap allocations derived from region values
must not flow into durable/static heap state, while local nonescaping
polymorphic use remains legal. `docs/REML_COMPARISON_PLAN.md` now separates
the fixed probe, the broader heap-alias open work, Tier 1 Scala Native rows,
exact MLKit/ReML artifact reproduction, and overlapping Scala Native benchmark
controls such as Mandelbrot. `docs/LITERATURE_BENCHMARK_CONTRACT.md` now says
to compare each prior system on its own reported axes, then show Rift's local
metrics separately. `docs/CPU_PROFILE_REPORT.md` now has the first
Scala Native-guided profile row and a profile-driven implementation follow-up:
the GH Archive string parser was identified as the dominant file-backed cost,
then a byte-slice file-backed parser was added and measured.

Completed run ids:

- `2026-05-05-comprehensive-headline`
- `2026-05-05-comprehensive-headline-cont`

Important correction: the first run completed compile/prior/checked rows but
was stopped after it entered an unwanted `current-safezone` row inside
SafeZone-cost. The continuation reran SafeZone-cost with `current-default`
excluded and completed streams. Core runtime/topology long rows were not
rerun in this pass; use the earlier clean core evidence for those until a
separate current-skipped core sweep exists.

Latest representative 1M rows:

| Area | Result | Interpretation |
|---|---|---|
| Dataflow SELECT | scoped `PageTokenMapFilter` `18.458 ms`, `checked-page-token` `20.479 ms`, heap `29.347 ms` | reusable page-token SELECT remains the fastest Dataflow SELECT path |
| Dataflow AGGREGATE | true `EpochFold` `92.923 ms` vs current checked exact-array aggregate `40.098 ms` | `EpochFold` is correct but speed-gated/negative |
| Dataflow JOIN | checked Rift `21.607 ms`, improved SafeZone `23.846 ms`, heap `33.438 ms` | checked JOIN wins in the latest prior-work pass |
| Checked append | scoped EpochBuffer `26.461 ms`, scoped page-token `26.883 ms`, heap `36.944 ms` | focused operator-owned append paths still clear the gate |
| StreamFlex direct checked epoch | 1M throughput: scoped direct epoch `163.339 ms`, direct stream epoch `185.550 ms`, trusted Streaming `182.246 ms`, improved SafeZone `208.653 ms`, heap `218.582 ms`, scoped checked TransactionRegion `205.929 ms` | direct epoch supersedes TransactionRegion for the current StreamFlex-shaped pipeline; use specialized multi-list operators only when direct linked epoch cannot express the shape |
| Stancu direct checked epoch | 1M transactions: scoped direct epoch `160.198 ms`, direct stream epoch `174.137 ms`, improved SafeZone `186.122 ms`, trusted Streaming `219.668 ms`, heap `225.798 ms` | direct epoch is now the best local Stancu-style transaction-boundary row; durable accounting arrays remain heap metadata |
| Common Crawl-shaped q1 | scoped page-token `3696.284 ms`, Rift page-token `3905.285 ms`, heap `5350.531 ms` with `1517.640 ms` GC | strongest checked generated stream win |
| Common Crawl-shaped q2 | scoped page-token `3732.171 ms`, Rift page-token `3972.493 ms`, heap `5183.656 ms` with `1526.751 ms` GC | strongest checked generated window win |
| LogHub BGL q2 full-file | checked scoped page-token `31165.087 ms`, trusted Streaming `30899.595 ms`, heap `32161.391 ms` with `595.599 ms` GC | real-input modest throughput/RSS/tail control, not a GC-heavy flagship |
| NEXMark Beam-default | checked q3 `282.629 ms`, q8 `432.391 ms`, q9 `708.391 ms` | modest generated methodology wins |
| Object allocation lowering | checked SafeZone-backed `14.903 ms`, checked Rift `16.039 ms`, heap `21.885 ms` | raw checked allocation is not the main remaining bottleneck |

Profiling update:
The diagnostic layer should use the official Scala Native profiling workflow
for native binaries (`/usr/bin/time`, native profilers, and `samply` where
available) before more operator/runtime tuning. The first sampled profile row
is now recorded in `docs/CPU_PROFILE_REPORT.md`: GH Archive file-backed q1 with
`rift-checked-safezone-page-token` is dominated by `BufferedReader`, UTF-8
decoder/StringBuilder/String operations, field counting/hashing, and gzip
inflate. Allocator/GC symbols are present but not dominant. This made parser
scratch/byte-slice JSON field extraction the right GH Archive technical
target; that path is now implemented as `GITHUB_ARCHIVE_FILE_PARSER=byte-slice`.
Treat profile runs as attribution evidence, not headline timing.

Latest GH Archive real-input checkpoint:
The legacy string-parser file-backed rows remain useful provenance, but the
current GH Archive checkpoint is the byte-slice parser path. Two hourly gzip
JSON-line files were run file-backed at 200k events with
`GITHUB_ARCHIVE_FILE_PARSER=byte-slice`. q1 heap is `3806.120 ms`, RSS
`290177024`, median GC `57.685 ms`; trusted Streaming is `3626.219 ms`, RSS
`211075072`, zero timed GC; checked scoped page-token is `3629.193 ms`, RSS
`211238912`, zero timed GC. q2 heap is `3756.950 ms`, RSS `290193408`, median
GC `61.625 ms`; trusted Streaming is `3645.458 ms`; checked scoped page-token
is `3626.107 ms`, both with about `211 MB` RSS and zero timed GC.
Interpretation: byte-slice parser scratch turns GH Archive into a modest
real-input throughput/RSS/tail win, not a GC-heavy case study. Heap GC is only
about `58-62 ms` inside roughly `3.8 s` elapsed at the current 200k/two-hour
scale.

Latest LogHub real-input checkpoint:
`LogHubRegionMatrix` now exists in the sandbox and supports generated smoke
input plus real file-backed LogHub logs. The BGL archive was downloaded into
ignored benchmark data; extracted input:
`/Users/siyaoliu/rift/cache/benchmark-data/loghub/BGL/BGL.log`
(`4747963` lines, `743185031` bytes). Generated 20k smoke matched checksums
between heap and checked scoped page-token. Real BGL 100k and 1M q1/q2 rows
also matched output counts/checksums across heap, improved SafeZone-32k,
trusted Streaming, and checked scoped page-token. At 1M, q1 heap is
`5568.252 ms`, median GC `99.271 ms`, RSS `408420352`, while trusted
Streaming is `5491.033 ms` and checked scoped page-token is `5552.988 ms`.
At 1M q2, heap is `5646.824 ms`, median GC `157.198 ms`; improved SafeZone-32k
is `5509.481 ms`, trusted Streaming `5605.787 ms`, and checked scoped
page-token `5636.357 ms`. Heap caps at `256M` roughly double q1/q2 GC to
about `195-200 ms`. A full-file q2 single-run probe loaded all `4747963` BGL
lines: heap `32161.391 ms`, GC `595.599 ms`, RSS `576012288`; trusted
Streaming `30899.595 ms`, GC `0.000 ms`; checked scoped page-token
`31165.087 ms`, GC `0.000 ms`, RSS `490946560`. Interpretation: LogHub BGL is
useful real-input modest throughput/RSS/fixed-memory evidence, but still not
the missing GC-heavy stream case because heap GC remains under 2% of elapsed
at full-file scale.

Latest real-input benchmark-search checkpoint:
`evidence/REAL_INPUT_BENCHMARK_SEARCH.md` now tracks the next flagship search
for a real GC-heavy stream benchmark. The immediate candidate family is
DSPBench, not another DEBS/TableRank tuning pass. `GMAP/DSPBench` is cloned in
ignored cache at `/Users/siyaoliu/rift/cache/benchmark-data/dspbench/source`,
commit `00c20da828faf2b960fdb697c61d34cb25461875`. The first local
single-process Spike Detection matrix is implemented in
`scala-native-rift/sandbox/src/main/scala-next/DSPBenchRegionMatrix.scala`
with runner `scala-native-rift/sandbox/run_dspbench_region_matrix.sh` and
result pack `evidence/DSPBENCH_REGION_MATRIX.md`. It uses
`dspbench-threads/data/sensors.dat` (`79999` usable lines) and reports replay
counts explicitly. 20k smoke matched checksums/output counts. At 1M, heap GC
is real but still small: q0 `10.880 ms`, q1 `21.421 ms`, q2 `32.793 ms`.
Best rows are modest: checked scoped page-token q1 is `1163.045 ms` vs heap
`1187.525 ms`, while q2 trusted Streaming is `1258.164 ms` vs heap
`1271.677 ms`; checked scoped q2 is slightly slower. Fraud Detection q0/q1/q2
is now implemented over `dspbench-threads/data/credit-card.dat` (`185000`
lines). The first 1M Fraud q2 matrix made trusted Streaming the strongest row:
heap `801.790 ms`, median GC `69.686 ms`, RSS `358252544`; trusted Streaming
`763.819 ms`, median GC `12.492 ms`, RSS `282460160`. That made checked q2 a
checked-overhead diagnostic. The dirty page-token fast-path rerun made checked
scoped page-token fastest (`818.574 ms`) versus heap `862.834 ms`, but the
committed-code rerun is more conservative: trusted Streaming `788.040 ms`,
checked scoped page-token `810.770 ms`, and heap `820.945 ms`,
with checked RSS about `279 MB` versus heap `358 MB`. A follow-up heap-cap
rerun at 1M q2
before the fast path shows heap
caps `512M` and `384M` do not materially change heap behavior; `256M` lowers
RSS to `272449536` but raises the max GC tail to `101.267 ms`. The useful next
action is to keep Fraud q2 as a regression row for common checked close/open
overhead. A diagnostic-only checked run added `DSPBENCH_DIAG=1`: it appended
and closed `4851373` records, with visible timing in allocation+append,
predictor CPU, close cursor traversal, and bucket switch/open-close. The
diagnostic elapsed is not headline evidence because
per-record timers perturb the row.

The pre-fast-path diagnostic was then extended across all Fraud q2 modes.
Mode-specific
allocation+append times were: heap `189.524 ms`, SafeZone improved
`134.630 ms`, trusted Streaming `135.167 ms`, checked Rift page-token
`152.283 ms`, and checked SafeZone page-token `150.169 ms`. This means
allocation+append is memory overhead, but region allocation is not slower than
heap in this diagnostic. The checked gap is now mostly common checked
operator/traversal/open-close overhead plus remaining parser/replay/predictor
and checksum CPU.

Active update:
Cheap checked page/token append operator implemented and measured; real WAT
link-metadata control, GH Archive real NDJSON, and LogHub real BGL matrices are
now added. Follow-up scaffold added for allocation-lowering decomposition and
heap-budget reporting.

Reusable operator-family update:
`PageTokenMapFilter[T]`, `EpochFold[T]`, `RegionList[T]`, and
`EpochBuffer[T]` now exist as
named checked APIs in `RiftRegion`, with compiler/runtime probes. Dataflow
SELECT now uses `PageTokenMapFilter` instead of the lower-level page-token
primitive directly; its 1M-shape 3-run row remains strong
(`checked-page-token` `19.881 ms`, scoped backend `18.214 ms`, heap
`27.872 ms`). `RegionList` replaced the benchmark-local ListOfLists checked
builder and improved the focused 3-run row to `5927.385 ms`. `EpochFold` is
correct but currently a negative/gated result: the first true reusable
Dataflow AGGREGATE row is `92.923 ms`, much slower than the exact-array
checked aggregate path. Do not use `EpochFold` as headline evidence until it is
optimized or redesigned. `EpochBuffer` is the new batch/epoch append-drain
operator: it matched checksums at 20k/100k/1M and at 1M beats the fair
`heap-epoch` control by removing a `5.707 ms` GC component.

StreamFlex EpochBuffer follow-up:
`StreamFlexRegionMatrix` now accepts `rift-checked-epoch-buffer` and
`rift-checked-safezone-epoch-buffer`. The script default omits
`current-safezone`; pass it explicitly only for provenance. The checked
EpochBuffer rows match checksum but do not beat heap/improved/trusted Rift at
default 200k throughput. Root cause is clear: the implementation stacks four
independent epoch buffers per batch/event, so it opens/closes four child
regions for packets, decoded records, classified records, and alerts. This is
useful negative evidence and points directly at the next operator:
`TransactionRegion` or a multi-list epoch operator that opens one child region
per transaction/batch and owns several internal lists.

StreamFlex TransactionRegion follow-up:
`RiftRegion.TransactionRegion` and typed `TransactionList[T]` are now
implemented, with compiler/runtime probes. The operator owns one active child
region and several internal append lists, so a multi-stage batch pipeline can
drain packets, decoded records, classified records, and alerts before one
transaction close. A first array-indexed list implementation was too slow; the
hot path was changed so each typed list handle owns its own `head`/`tail`/
`length` fields. Validation passed: sandbox compile, checked compiler suite
`110/110`, and checked native runtime suite `49/49`. In the latest staged
headline StreamFlex throughput row, checked TransactionRegion improves over
stacked checked EpochBuffer (`45.620 ms` vs `47.934 ms`) and scoped checked
TransactionRegion is the best checked row (`39.019 ms`), faster than heap
(`42.860 ms`) and improved SafeZone (`41.327 ms`). Trusted Rift HP/Streaming
remain faster around `36.4 ms`, so this is a partial checked-operator win and
not a reason to claim StreamFlex solved.

Validation for reusable operator update:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"
```

Results: compile passed; checked compiler suite passed `108/108`; checked
native runtime suite passed `48/48` after the `EpochBuffer` probes.

Comprehensive staged sweep:
Completed a clean staged headline sweep after adding explicit mode-list
controls for prior-work runners and parent orchestration defaults. The first
run (`2026-05-05-comprehensive-headline`) completed compile/prior/checked rows
and was stopped when SafeZone-cost entered an unwanted `current-safezone` row.
The continuation (`2026-05-05-comprehensive-headline-cont`) reran SafeZone-cost
with `current-default` excluded and completed stream/application rows. Source
summary: `evidence/COMPREHENSIVE_SWEEP_2026_05_06.md`.

Report/taxonomy/benchmark-catalog update:
`docs/PERFORMANCE_EVALUATION_REPORT.md` is now the single high-level project
report for presentation and planning. It summarizes the design target, canonical
mode names, what was implemented, what runtime overhead has actually been
removed, representative benchmark tables, wins/losses, realistic stream
benchmark ladder, and next engineering plan. `docs/RIFT_EVALUATION_SUMMARY_SLIDES.md`
is the matching markdown slide outline. `docs/BENCHMARK_CATALOG.md` is the
separate guide to what each benchmark measures, which inputs are generated or
real, and which rows are runtime-only, checked-operator, stream-stressor, or
ceiling/control evidence. The report now explicitly records that region
allocation removes tracing/reclaim cost but not object-construction,
allocation-lowering, or operator/query CPU cost; it also defines page/token
append and classifies wins as uncapped-throughput, fixed-memory, RSS, or
tail-latency evidence.

Latest checkpoint:
`RiftRegion.StreamPageTokenAppendWindow[T]` now exists as an experimental
checked operator-owned append path for page/token/window stream workloads. It
allocates ordinary Scala records in child bucket regions, but user code does
not receive reusable `StreamBucket` tokens for hot append. The operator owns
bucket lookup, child-region caching, append, and close. Public low-level
`StreamAppendWindow` APIs remain defensive.

The page/token path removes these runtime costs from the checked hot path:
per-record `bucket.child.checkOpen()`, per-record `streamBucketRegion(...)`
lookup, and stale-current `isOpen` checks in the operator-owned fast path.
New runtime probes reject stale bucket-region access after close-before and
close-all, and a new compiler probe rejects passing a direct heap record to
`appendPageToken`.

Validation for this update:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"
```

Results: compile passed; checked compiler suite passed `98/98`; checked native
runtime suite passed `43/43`.

Focused page/token append gate: passed. At 1M events,
`rift-checked-page-token` is `27.141 ms` versus current `rift-checked-rift`
`30.819 ms` and heap `35.652 ms`; the SafeZone-backed page-token row is
`26.191 ms`. All rows matched checksum.

Generated Common Crawl-shaped q1/q2 gate: passed. At 1M q1,
`rift-checked-page-token` is `3956.366 ms` versus current checked
`4855.133 ms`, trusted HPZone `4367.265 ms`, improved SafeZone-32k
`4637.981 ms`, and heap `5412.618 ms`. The SafeZone-backed page-token row is
`3728.286 ms`. At 1M q2, `rift-checked-page-token` is `4039.855 ms` versus
current checked `4820.611 ms`, trusted Streaming `4212.494 ms`, improved
SafeZone-32k `4580.687 ms`, and heap `5252.803 ms`. The SafeZone-backed
page-token row is `3816.247 ms`. All q1/q2 rows matched checksum/output count.

Interpretation: this is the first checked Common Crawl-shaped application gate
that passes. It directly supports the static-safety overhead-removal story:
when a checked operator owns the lifetime boundary, it can remove redundant
dynamic checks and lookup work. Caveat: these are generated WET-shaped stressor
rows, not real Common Crawl input proof.

Real WET control: ran the existing preloaded Common Crawl WET shard with q1/q2
and page-token modes. At the actual loaded scale, q1 produced `752797` token
records and q2 produced `18560` outputs. Heap timed GC was `0.000 ms` in every
row. SafeZone-backed page-token is fastest (`30.474 ms` q1 and `30.783 ms`
q2), but this is a ceiling/control row, not GC-heavy evidence. The next real
input step remains larger/multiple WET/WAT shards or a different real
NDJSON/log-style workload.

Real WAT control: added WAT link extraction queries to
`CommonCrawlWetMatrix`: `q4-wat-links` materializes page plus URL/link records,
and `q5-wat-link-domain-window` aggregates link domains at bucket close. The
input is
`/Users/siyaoliu/rift/cache/benchmark-data/common-crawl/CC-MAIN-2026-17/CC-MAIN-20260410081153-20260410111153-00000.warc.wat`.
At 50k requested pages, q4 produced `1006742` page/link records and q5
produced `293020` outputs. Heap still reported `0.000 ms` timed GC in every
run. SafeZone-backed page-token was fastest on q4 (`31.792 ms` vs heap
`33.646 ms`) and q5 (`33.937 ms` vs heap `35.066 ms`). A 100k requested-page
q4 one-run probe also stayed heap-GC-zero: heap `43.274 ms`, SafeZone-backed
page-token `42.226 ms`, output count `1339183`. Interpretation: real WAT is a
useful correctness/real-input control and modest checked-backend win, but not
the missing GC-heavy real-data case study.

GH Archive real NDJSON control: added
`GithubArchiveRegionMatrix` and `sandbox/run_github_archive_region_matrix.sh`.
The matrix now supports comma-separated `GITHUB_ARCHIVE_INPUTS`; the local
sample contains eight real hourly files from `2026-04-01-0` through
`2026-04-01-7`. Queries are `q0-events`, `q1-fields`, and `q2-repo-window`;
q1/q2 allocate ordinary event/field records with bucket lifetimes and reuse
the page-token checked operator path. The first 100k q1 row showed a real GC
signal and region win: heap `46.309 ms`, median GC `15.777 ms`, max GC
`58.617 ms`, checked SafeZone-backed page-token `33.656 ms`. That row used
the original heap-expected harness, so it remains a promising first signal but
not the clean RSS/GC interpretation. The runner now uses a no-allocation
checksum oracle. In the cleaner 8-hour 1M oracle row, q1 heap wins uncapped
median elapsed (`293.204 ms`) while collecting in 1/3 runs with max GC
`135.368 ms` and about `1.74 GB` RSS; trusted Streaming reruns at
`340.820 ms` and checked SafeZone-backed page-token is `348.817 ms`, both with
no timed GC. With `GC_MAXIMUM_HEAP_SIZE=1G`, heap q1 slows
to `395.295 ms` with median GC `92.347 ms`, making the checked region row
faster as a memory-budget diagnostic. q2 remains heap-fastest in median
(`271.880 ms` uncapped; `279.959 ms` at `1400M`) despite max-GC outliers,
because repo aggregation CPU dominates. Interpretation: GH Archive is now a
memory-budget/tail-latency candidate, not an uncapped throughput case-study
win.

GH Archive file-backed q1 follow-up:
`GithubArchiveRegionMatrix` now accepts
`GITHUB_ARCHIVE_INPUT_MODE=file-backed`, which rereads and parses the gzip JSON
lines inside every timed run instead of preloading primitive metadata. A 20k
smoke matched checksums. The first 100k q1 3-run row over
`2026-04-01-0.json.gz` matched checksums and reports heap `3999.933 ms`,
`158.149 ms` median GC, and `1218805760` bytes RSS; improved SafeZone-32k
`3924.979 ms`, `107.125 ms` median GC, and `674807808` bytes RSS; trusted
Streaming `3908.972 ms`, `73.055 ms` median GC, and `495943680` bytes RSS;
checked SafeZone-backed page-token `3937.394 ms`, `106.248 ms` median GC, and
`674791424` bytes RSS. Interpretation: this is a real-data RSS win and modest
region throughput win, but not yet a decisive checked case study because
parser/string allocation still happens on the heap. Next GH Archive work is
file-backed q2 plus heap caps and per-run tail reporting.

GH Archive file-backed q2 follow-up:
The first 100k q2 file-backed cap/tail run also matched checksums. Uncapped
heap is `3995.632 ms`, `158.277 ms` median GC, and `1218428928` bytes RSS.
Heap with `2G` and `1400M` caps still completes at `4066.670 ms` and
`3983.441 ms`; heap with `1G` fails with signal 11 at `1077067776` bytes RSS.
Improved SafeZone-32k is `3934.094 ms`, `105.445 ms` median GC, and
`672088064` bytes RSS. Trusted Streaming is `3906.291 ms`, `81.402 ms` median
GC, `0.112 ms` median Rift op time, and `673644544` bytes RSS. Checked
SafeZone-backed page-token is `3921.127 ms`, `106.352 ms` median GC, and
`673824768` bytes RSS. Interpretation: with parsing timed, q2 is no longer a
pure heap-fastest aggregation ceiling; region rows modestly improve elapsed/RSS
and the `1G` heap cap fails. Parser/string allocation still keeps GC visible in
all successful rows. Next GH Archive step is q1 file-backed heap caps and
larger/multi-hour rows only if the machine can tolerate the memory footprint.

GH Archive file-backed q1 heap-cap follow-up:
The q1 cap run also matched checksums. Heap is `4014.909 ms`, `157.495 ms`
median GC, and `1218822144` bytes RSS uncapped; heap with `2G` is
`4005.975 ms`, `149.868 ms` median GC, and `1168179200` bytes RSS; heap with
`1400M` is `4093.234 ms`, `166.523 ms` median GC, `201.304 ms` max GC, and
`1168162816` bytes RSS; heap with `1G` fails with signal 11 at `1076805632`
bytes RSS. Improved SafeZone-32k is `4000.812 ms`, `105.804 ms` median GC,
and `673808384` bytes RSS. Trusted Streaming is `3995.238 ms`, `82.368 ms`
median GC, `0.293 ms` median Rift op time, and `673611776` bytes RSS. Checked
SafeZone-backed page-token is `4023.883 ms`, `113.334 ms` median GC, and
`674742272` bytes RSS. Interpretation: q1 file-backed is mainly an RSS and
fixed-memory win; trusted Streaming slightly beats uncapped heap, while
checked scoped page-token is a near tie/slight elapsed loss with about 45%
lower RSS. Parser/string heap allocation remains visible in all rows.

Allocation-lowering matrix: added `ObjectAllocationLoweringMatrix` and
`sandbox/run_object_allocation_lowering_matrix.sh`, then validated the
refined retained-region-array shape at 20k smoke, 100k, 1M, and 10M. This focused
matrix allocates ordinary small Scala objects through `heap-immix`,
`rift-trusted-hp`, `rift-trusted-streaming`, `rift-checked-rift`, and
`rift-checked-safezone-improved-32k` without stream-window, ranking, or query
traversal work. The rejected construct-only smoke is still recorded as a
pitfall: the optimizer could remove checked allocations from Rift allocation
counters. In the retained rows, checksums match and checked Rift reports
nonzero object allocations.

Follow-up refinement: the first retained-buffer version still mixed generic
checked `RegionBuffer` overhead into an allocation-lowering matrix. The matrix
now uses a region-owned array, `Array[CheckedRecord^{region}]^{region}`, in
checked rows. This keeps allocated objects live without the generic buffer API.
An attempted lowering fast path through `RiftRegion.allocImpl` failed during
native lowering because Scala Native metadata does not expose `allocImpl` as a
valid method lookup entry on `RiftRegion` or its checked subtraits; that probe
was reverted and should not be repeated without changing method-table metadata.

Refined key rows: at 100k, checked Rift is `1.576 ms` and checked
SafeZone-backed is `1.395 ms` versus heap `1.691 ms`. At 1M, checked Rift is
`16.100 ms` and checked SafeZone-backed is `14.347 ms` versus heap
`20.429 ms` with `5.745 ms` median GC. At 10M, heap becomes GC/RSS-bound:
heap is `271.121 ms` with `105.807 ms` median GC and about `971 MB` RSS;
trusted HP is `199.627 ms`, checked Rift is `165.774 ms`, and checked
SafeZone-backed allocation is `143.319 ms` at about `404 MB` RSS.
Interpretation: region allocation/reclaim wins when heap pressure is real, and
the earlier checked gap was mostly generic `RegionBuffer` retention overhead.
The next performance target is generic checked buffers/operators, not raw
allocation first.

Checked RegionBuffer decomposition: `CheckedRegionBufferMatrix` now compares
growable buffers, fixed-capacity `ObjectBuffer`, and exact-array controls. At
10 x 100k records with initial capacity `16`, `rift-checked-array` is
`18.574 ms`, fixed `ObjectBuffer` is `25.788 ms`, and growable
`RegionBuffer` is `29.968 ms`; heap shows the same broad shape, with
`heap-array` `21.089 ms` versus `heap-buffer` `34.097 ms`. Pre-sizing the
buffer to `100000` improves `rift-checked-buffer` to `25.980 ms`, roughly tied
with `ObjectBuffer` at `25.408 ms`, but still behind `rift-checked-array` at
`18.466 ms`. Interpretation: growth/copy matters, but generic buffer
access/layout/dispatch is still substantial. Known-size or page/batch-shaped
checked operators should prefer operator-owned array/chunk fast paths;
`ObjectBuffer` is the bounded ergonomic fallback and `RegionBuffer` remains
the growable fallback until a focused layout/access patch narrows the gap.

Fixed-chunk append follow-up: `StreamChunkAppendWindow[T]` now exists as an
experimental checked operator-owned fixed-chunk append path, with compiler and
runtime probes. It is correct but failed the focused speed gate. At 1M,
`rift-checked-page-token` is `28.452 ms` and SafeZone-backed page-token is
`27.214 ms`, while `rift-checked-chunk-token` is `34.273 ms` and
SafeZone-backed chunk-token is `33.108 ms`; `heap-immix-chunk` is also slower
than normal heap (`45.363 ms` versus `37.748 ms`). Interpretation: chunks add
extra object/array allocation and control overhead in the sequential
append/drain shape. Keep chunk-token as a negative/control row; do not move it
into Common Crawl, GH Archive, or DEBS unless a workload needs page-local
random access or substantially larger per-bucket payloads.

Heap-budget runner support: `sandbox/run_github_archive_region_matrix.sh` now
adds `heap_cap` and `status` columns. `GITHUB_ARCHIVE_HEAP_CAPS` can run
multiple heap caps such as `uncapped 2G 1400M 1G`; failed capped processes are
recorded as failed rows instead of aborting the whole matrix. Region rows can
also be run under caps with `GITHUB_ARCHIVE_REGION_HEAP_CAPS` for diagnostics,
but claims should be judged by completion and total RSS, not only GC heap size.

New evidence:

- `evidence/OBJECT_ALLOCATION_LOWERING_MATRIX.md`
- updated `evidence/CHECKED_REGION_BUFFER_MATRIX.md`
- `evidence/CHECKED_PAGE_TOKEN_APPEND_MATRIX.md`
- updated `evidence/CHECKED_OVERHEAD_REMOVAL_MATRIX.md`
- updated `evidence/COMMON_CRAWL_LIKE_MATRIX.md`
- updated `evidence/REALISTIC_STREAM_GC_MATRIX.md`
- new `evidence/GITHUB_ARCHIVE_REGION_MATRIX.md`
- new `docs/BENCHMARK_CATALOG.md`
- updated `docs/PERFORMANCE_EVALUATION_REPORT.md`
- updated `docs/RIFT_EVALUATION_SUMMARY_SLIDES.md`

Previous checkpoint:
`RiftRegion.streamingSafeZone(...)` now exists as a benchmark-only checked
backend entrypoint. It returns a checked `StreamingRegion`, delegates checked
object allocation to `SafeZoneAllocator`, and makes child buckets opened from
that parent use the same SafeZone-backed backend. Normal
`RiftRegion.streaming(...)` is unchanged. V1 supports object allocation and
close; raw byte allocation and reset throw `UnsupportedOperationException`.

The implementation also fixes checked-region class allocation lowering: zoned
`Classalloc` now retags the allocation receiver to the `SafeZone` trait before
calling `allocImpl`, so allocations through narrow checked types such as
`StreamingRegion` link correctly. New runtime tests cover SafeZone-backed
checked allocation, child bucket cursor close, allocation-after-close
rejection, and raw allocation/reset rejection.

Focused append-window gate: passed. At 1M events,
`rift-checked-safezone-32k` is `29.444 ms` versus current
`rift-checked-api-cursor` at `30.922 ms`, with matching checksum and no RSS
regression. The 100k row is `2.944 ms` versus current checked cursor
`3.136 ms`.

Common Crawl-like q1/q2 follow-up: improved checked mode but missed the
application gate. At 1M q1, `rift-checked-safezone-32k` is `4512.743 ms`
versus current `rift-checked` at `4744.872 ms`, improved SafeZone-32k at
`4570.772 ms`, and trusted HPZone at `4278.440 ms`. At 1M q2,
`rift-checked-safezone-32k` is `4431.865 ms` versus current checked
`4698.903 ms`, improved SafeZone-32k `4362.405 ms`, and trusted HPZone
`4075.431 ms`. All q1/q2 rows matched checksum/output count.

Interpretation: SafeZone-family allocator mechanics help the reusable checked
append-window backend, but the application-scale checked path still has
material `StreamAppendWindow` container/API overhead. Treat
`rift-checked-safezone-32k` as backend feasibility evidence, not a final
checked application-speed claim. Do not move it into DEBS, TableRank, or
broader application claims before the checked overhead split is understood.

Validation for this update:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"

CHECKED_APPEND_BUILD=0 \
CHECKED_APPEND_EVENTS=1000000 \
CHECKED_APPEND_BENCHMARK_RUNS=3 \
CHECKED_APPEND_WARMUPS=1 \
CHECKED_APPEND_MODES="heap rift-checked-api-cursor rift-checked-safezone-32k safezone-improved-32k unsafezone-hp" \
CHECKED_APPEND_OUTPUT_DIR=/Users/siyaoliu/rift/cache/checked-safezone-append-2026-05-03-1m \
zsh sandbox/run_checked_append_window_matrix.sh

COMMON_CRAWL_WET_BUILD=0 \
COMMON_CRAWL_WET_PAGES=1000000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=3 \
COMMON_CRAWL_WET_WARMUPS=1 \
COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window" \
COMMON_CRAWL_WET_MODES="heap safezone-improved-32k unsafezone-hp rift-hp rift-streaming rift-checked rift-checked-safezone-32k" \
COMMON_CRAWL_WET_OUTPUT_DIR=/Users/siyaoliu/rift/cache/common-crawl-checked-safezone-2026-05-03-1m \
zsh sandbox/run_common_crawl_wet_matrix.sh
```

Evidence files:

- `docs/MEMORY_MODE_TAXONOMY.md`
- `docs/PERFORMANCE_EVALUATION_REPORT.md`
- `docs/RIFT_EVALUATION_SUMMARY_SLIDES.md`
- `evidence/CHECKED_PAGE_TOKEN_APPEND_MATRIX.md`
- `evidence/CHECKED_SAFEZONE_BACKEND_MATRIX.md`
- `evidence/CHECKED_OVERHEAD_REMOVAL_MATRIX.md`
- `evidence/REALISTIC_STREAM_GC_MATRIX.md`
- `evidence/SAFEZONE_HP_BACKEND_PROTOTYPE.md`
- `evidence/COMMON_CRAWL_LIKE_MATRIX.md`

Mode naming update:
new docs and scripts should use `heap-immix`, `safezone-improved-32k`,
`safezone-rootless-32k`, `rift-trusted-hp`, `rift-trusted-streaming`,
`rift-checked-rift`, and `rift-checked-safezone-improved-32k`. Older labels
remain accepted as aliases in the checked append-window and Common Crawl-like
runners.

Canonical-name smoke validation:

```sh
cd /Users/siyaoliu/rift/scala-native-rift

CHECKED_APPEND_EVENTS=20000 \
CHECKED_APPEND_BENCHMARK_RUNS=1 \
CHECKED_APPEND_WARMUPS=0 \
CHECKED_APPEND_MODES="heap-immix rift-checked-rift rift-checked-safezone-improved-32k safezone-rootless-32k" \
CHECKED_APPEND_OUTPUT_DIR=/Users/siyaoliu/rift/cache/canonical-checked-append-smoke-2026-05-03 \
zsh sandbox/run_checked_append_window_matrix.sh

COMMON_CRAWL_WET_PAGES=2000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=1 \
COMMON_CRAWL_WET_WARMUPS=0 \
COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window" \
COMMON_CRAWL_WET_MODES="heap-immix safezone-improved-32k safezone-rootless-32k rift-trusted-hp rift-trusted-streaming rift-checked-rift rift-checked-safezone-improved-32k" \
COMMON_CRAWL_WET_OUTPUT_DIR=/Users/siyaoliu/rift/cache/canonical-common-crawl-smoke-2026-05-03 \
zsh sandbox/run_common_crawl_wet_matrix.sh
```

Both canonical-mode smokes matched checksums/output counts. These are wiring
checks only, not headline benchmark rows.

Previous update:
Checked Common Crawl-like q1/q2 `StreamAppendWindow` follow-up implemented and
measured after the Rift fast-allocation counter cleanup.

Latest checkpoint:
`CommonCrawlWetMatrix` now has an opt-in `rift-checked` mode for q1/q2. It
allocates ordinary page/line/token `CheckedRecord` objects in checked
child-bucket regions and retains them through the reusable
`RiftRegion.StreamAppendWindow` cursor API. A helper that hid the region
provenance of a checked record was rejected by the compiler, so the final
implementation appends records immediately at the allocation site; keep that as
positive owner-token safety evidence.

The checked q1/q2 100k and 1M rows match heap checksum/output count. The 1M
RSS-complete rerun shows checked q1 at `5088.712 ms` versus heap
`5670.270 ms`, improved SafeZone-32k `4644.747 ms`, and trusted HPZone
`4403.007 ms`. Checked q2 is `5061.479 ms` versus heap `5342.373 ms`,
improved SafeZone-32k `4444.954 ms`, and trusted HPZone `4258.549 ms`. Heap GC
is about `1.6-1.7 s`; checked GC is about `20-25 ms`; checked Rift op time is
about `11 ms`.

A separate 2k q0/q3 smoke also matched heap checksum/output count, confirming
the new checked runner paths compile and execute outside the q1/q2 headline
rows.

Interpretation: checked Common Crawl-like q1/q2 validates safe placement of
`137000000` ordinary stream records into checked regions and beats heap, but it
does not clear the case-study gate because improved SafeZone and trusted Rift
are much faster. The remaining gap is checked `StreamAppendWindow`
append/cursor/container overhead in hot loops, not region allocation or
close/reclaim. Do not use these rows as checked application-speed claims.

Validation for this checked follow-up:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest" "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"

COMMON_CRAWL_WET_PAGES=2000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=1 \
COMMON_CRAWL_WET_WARMUPS=0 \
COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window" \
COMMON_CRAWL_WET_MODES="heap rift-hp rift-checked" \
COMMON_CRAWL_WET_OUTPUT_DIR=/Users/siyaoliu/rift/cache/common-crawl-like-checked-smoke-2026-05-02 \
zsh sandbox/run_common_crawl_wet_matrix.sh

COMMON_CRAWL_WET_BUILD=0 \
COMMON_CRAWL_WET_PAGES=2000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=1 \
COMMON_CRAWL_WET_WARMUPS=0 \
COMMON_CRAWL_WET_QUERIES="q0-parse q3-parser-scratch" \
COMMON_CRAWL_WET_MODES="heap rift-checked" \
COMMON_CRAWL_WET_OUTPUT_DIR=/Users/siyaoliu/rift/cache/common-crawl-like-checked-smoke-q0q3-2026-05-02 \
zsh sandbox/run_common_crawl_wet_matrix.sh

COMMON_CRAWL_WET_PAGES=100000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=3 \
COMMON_CRAWL_WET_WARMUPS=1 \
COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window" \
COMMON_CRAWL_WET_MODES="heap safezone-improved-32k unsafezone-hp rift-hp rift-streaming rift-checked" \
COMMON_CRAWL_WET_OUTPUT_DIR=/Users/siyaoliu/rift/cache/common-crawl-like-checked-2026-05-02-100k \
zsh sandbox/run_common_crawl_wet_matrix.sh

COMMON_CRAWL_WET_BUILD=0 \
COMMON_CRAWL_WET_PAGES=1000000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=3 \
COMMON_CRAWL_WET_WARMUPS=1 \
COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window" \
COMMON_CRAWL_WET_MODES="heap safezone-improved-32k unsafezone-hp rift-hp rift-streaming rift-checked" \
COMMON_CRAWL_WET_OUTPUT_DIR=/Users/siyaoliu/rift/cache/common-crawl-like-checked-2026-05-02-1m-rss \
zsh sandbox/run_common_crawl_wet_matrix.sh
```

Previous checkpoint:
The previous Common Crawl-like q1/q2 results were distorted by Rift's default
per-allocation global allocated-byte statistics. `RiftRuntime.c` now keeps
allocation counts and total raw bytes locally on the region fast path and
flushes total bytes at close/reset. Precise active allocated-byte
current/peak counters are opt-in with `RIFT_PRECISE_ALLOC_STATS=1`.

The focused Common Crawl-like 100k and 1M q1/q2 reruns matched checksums and
output counts across heap, improved SafeZone-32k, UnsafeZone-HP, Rift HP, and
Rift Streaming. At 1M, q1 `rift-hp` is `4386.590 ms` versus heap
`5466.535 ms`, improved-32k `4608.641 ms`, and unsafezone-hp `4640.245 ms`.
q2 `rift-streaming` is `4164.288 ms` versus heap `5267.784 ms`,
improved-32k `4425.273 ms`, and unsafezone-hp `4437.924 ms`. Heap GC is about
`1.56-1.58 s`; Rift/SafeZone-family GC is about `20-31 ms`. Rift allocated
`137000000` region objects and `6576000000` raw region bytes in each 1M q1/q2
row, with about `10-11 ms` measured Rift op time.

This is now the strongest trusted-Rift GC-heavy stream evidence. It is not an
RSS win at 1M: heap RSS is lower than the region-family rows in these
measurements. The precise-stats control confirms the diagnosis: 100k q1
`rift-hp` is `439.129 ms` by default but `473.750 ms` with
`RIFT_PRECISE_ALLOC_STATS=1`. Keep precise active-byte stats for diagnostics,
not headline timing.

Validation for the 2026-05-02 update:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionTest" "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"

COMMON_CRAWL_WET_PAGES=100000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=3 \
COMMON_CRAWL_WET_WARMUPS=1 \
COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window" \
COMMON_CRAWL_WET_MODES="heap safezone-improved-32k unsafezone-hp rift-hp rift-streaming" \
COMMON_CRAWL_WET_OUTPUT_DIR=/Users/siyaoliu/rift/cache/common-crawl-like-fastalloc-2026-05-02-100k \
zsh sandbox/run_common_crawl_wet_matrix.sh

COMMON_CRAWL_WET_BUILD=0 \
COMMON_CRAWL_WET_PAGES=1000000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=3 \
COMMON_CRAWL_WET_WARMUPS=1 \
COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window" \
COMMON_CRAWL_WET_MODES="heap safezone-improved-32k unsafezone-hp rift-hp rift-streaming" \
COMMON_CRAWL_WET_OUTPUT_DIR=/Users/siyaoliu/rift/cache/common-crawl-like-fastalloc-2026-05-02-1m \
zsh sandbox/run_common_crawl_wet_matrix.sh

RIFT_PRECISE_ALLOC_STATS=1 \
COMMON_CRAWL_WET_BUILD=0 \
COMMON_CRAWL_WET_PAGES=100000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=3 \
COMMON_CRAWL_WET_WARMUPS=1 \
COMMON_CRAWL_WET_QUERIES="q1-tokenize" \
COMMON_CRAWL_WET_MODES="rift-hp" \
COMMON_CRAWL_WET_OUTPUT_DIR=/Users/siyaoliu/rift/cache/common-crawl-like-precise-stats-2026-05-02-100k \
zsh sandbox/run_common_crawl_wet_matrix.sh
```

Previous checkpoint:
The real-input stream benchmark ladder has now been wired, measured, and
recorded. NEXMark Beam-default generated-profile rows show the only new
positive signal: Q1 has a useful trusted-region win and Q8 has a modest checked
win. The real/preloaded Wikimedia, Common Crawl WET, and Linear Road rows are
ceiling results under the current probes: heap is fastest and measured timed GC
is `0.000 ms` in the timed sections. These rows should stay as regression and
win-envelope evidence, not application case-study claims. The next engineering
step should return to focused checked-operator overhead reduction, with
NEXMark Beam-default Q1/Q8 retained as application-profile checks.

Current checkpoint:
The stream-GC refocus plan is implemented and checkpointed. DaCapo,
Renaissance, and SPECjbb2015 are now explicitly de-prioritized as primary Rift
evidence because their lifetimes are not stream-structured. The active search
space is GC-heavy stream/dataflow workloads with page, batch, window, epoch, or
operator close boundaries. The implementation adds max-GC/outlier reporting to
existing stream matrices, expands NEXMark with Q3/Q4/Q9/Q11, adds a
Yahoo-style ad-stream matrix, and adds a first RIoTBench-style IoT
ETL/statistics matrix. The new application-style probes are useful controls,
but the strongest next engineering direction is still checked operator
overhead reduction, with NEXMark Q3/Q8, Yahoo Q2, and RIoTBench q1 retained as
profile/regression rows.

The comprehensive performance-evaluation package is now added in the parent
repo. `scripts/run-performance-evaluation.sh` records environment/SHAs and
runs the selected suites into ignored `cache/perf-eval/<run-id>/` logs,
`evidence/PERF_EVAL_RUNBOOK.md` defines the run discipline and gates,
`evidence/EVALUATION_SUMMARY_TABLES.md` seeds compact tables from current
evidence, and `docs/PERFORMANCE_EVALUATION_REPORT.md` provides the report
scaffold. A stream smoke and a first clean headline subset have now run.

UnsafeZone-HP has now been implemented as a benchmark-only substrate control.
SafeZone root mode `3` disables page/chunk root add/remove, and benchmark
label `unsafezone-hp` maps to binary mode `safezone` with
`SAFEZONE_ROOTS_MODE=3 SAFEZONE_PAGE_SIZE=32768`. There is intentionally no
`unsafezone-streaming` mode yet because SafeZone close/reclaim is not Rift
Streaming reset. Existing root modes `0`, `1`, and `2` are unchanged. This is
unsafe by design and should not be treated as a user-facing API or safety
claim. Tracked evidence: `evidence/UNSAFEZONE_HP_BASELINE_MATRIX.md`.

The first clean UnsafeZone-HP core/prior headline sweep has now run and is
tracked in `evidence/HEADLINE_UNSAFEZONE_CORE_PRIOR_2026_05_01.md`:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-unsafezone-core-prior \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight core prior" \
bash scripts/run-performance-evaluation.sh
```

This completed successfully with raw logs under
`cache/perf-eval/2026-05-01-unsafezone-core-prior/`. The main result is that
UnsafeZone-HP usually beats improved SafeZone slightly and beats current Rift
HPZone on linked/prior-work local harnesses: GCBench runtime `206.636 ms`,
linked ListOfLists `9818.653 ms`, Dataflow SELECT/AGGREGATE/JOIN
`21.957` / `39.434` / `22.359 ms`, Yak topword `58.686 ms`, and Stancu
`33.335 ms`. Current Rift HPZone still wins flat ListOfLists (`1540.958 ms`
versus heap `1748.743 ms` and unsafezone-hp `1766.060 ms`). Treat this as
runtime-substrate evidence, not safety evidence: rootless SafeZone is unsafe.

One harness issue was fixed after this run: the parent evaluation runner now
passes `STREAMFLEX_OUTPUT_DIR`, `YAK_OUTPUT_DIR`, and `STANCU_OUTPUT_DIR`, so
future prior-work runs keep their summary TSVs under the run directory instead
of writing them to `/tmp`.

The first UnsafeZone-HP stream headline sweep has also run and is tracked in
`evidence/HEADLINE_UNSAFEZONE_STREAMS_2026_05_01.md`:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-unsafezone-streams \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight streams" \
bash scripts/run-performance-evaluation.sh
```

This completed successfully after rerunning with permission for sbt's
user-level boot lock. Raw logs and summary TSVs are under
`cache/perf-eval/2026-05-01-unsafezone-streams/`. The pattern matches the
core/prior sweep: UnsafeZone-HP is often the best SafeZone-family stream row
and sometimes best overall, but usually only slightly ahead of improved
SafeZone. Important rows: NEXMark Beam-default q0 unsafezone-hp `468.617 ms`
versus heap `520.052 ms` and improved SafeZone `481.133 ms`; NEXMark q3
checked `292.371 ms` versus unsafezone-hp `296.480 ms`; NEXMark q8 checked
`450.904 ms` versus unsafezone-hp `460.822 ms`; Common Crawl WET-shaped q1
unsafezone-hp `3971.051 ms` versus heap `4743.205 ms`, improved SafeZone
`4028.067 ms`, and Rift HPZone `4322.349 ms`. This strengthens the
SafeZone-substrate hypothesis, not a user-facing unsafe-region claim.

The bounded DEBS 1M UnsafeZone-HP leg has also run and is tracked in
`evidence/HEADLINE_UNSAFEZONE_DEBS_1M_2026_05_01.md`:

```sh
cd /Users/siyaoliu/rift
DEBS2015_BOTH_INPUT=/tmp/debs2015-month1-1000000.csv \
RIFT_EVAL_RUN_ID=2026-05-01-unsafezone-debs-1m \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight debs" \
bash scripts/run-performance-evaluation.sh
```

Outputs matched for Q1/Q2 in both normal and instrumented legs. Normal
single-run row: unsafezone-hp `4639.791 ms`, heap `4861.406 ms`, improved
SafeZone `5341.010 ms`, Rift HPZone `4738.989 ms`, Rift Streaming
`4663.529 ms`, checked `4844.738 ms`. Instrumented row is close: Rift
Streaming `4691.125 ms`, Rift HPZone `4694.310 ms`, unsafezone-hp
`4720.234 ms`, heap `4705.254 ms`. Treat this as bounded runtime-substrate
evidence and correctness control, not a full-month or checked-API win.

The post-UnsafeZone measurement scaffold is now implemented. The new
`sandbox/run_safezone_cost_matrix.sh` runner builds selected native benchmark
mains, runs SafeZone-family configurations with `SAFEZONE_TRACE=1`, and writes
benchmark results plus SafeZone pool trace counters to a TSV. It is documented
in `evidence/SAFEZONE_COST_MATRIX.md`. Use it before optimizing either
SafeZone internals or a checked SafeZone-derived backend: the goal is to
separate root add/remove cost, page-size effects, reclaim/sort bookkeeping,
and general allocator/pool mechanics.

The Common Crawl WET-shaped matrix now includes `q2-domain-window` and
`q3-parser-scratch` in addition to `q0-parse` and `q1-tokenize`. This expansion
is documented in `evidence/COMMON_CRAWL_LIKE_MATRIX.md`. The later checked
q1/q2 follow-up uses the focused `StreamAppendWindow` cursor API and validates
safe record placement at scale, but misses the application performance gate
against improved SafeZone and trusted Rift.

`evidence/SAFEZONE_HP_BACKEND_PROTOTYPE.md` records the intended checked
SafeZone-family direction. At this older checkpoint, no checked SafeZone-backed
backend code had been added yet; the 2026-05-03 update above supersedes that
status with the implemented `rift-checked-safezone-32k` prototype. The v1 rule
should still reject unsupported mixed-reference cases rather than falling back
silently, so performance rows are not accidentally mixed with rootful or
unsafe behavior.

Validation for the SafeZone-cost scaffold update:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"

COMMON_CRAWL_WET_PAGES=2000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=1 \
COMMON_CRAWL_WET_WARMUPS=0 \
COMMON_CRAWL_WET_QUERIES="q2-domain-window q3-parser-scratch" \
COMMON_CRAWL_WET_MODES="heap safezone-improved unsafezone-hp rift-hp" \
COMMON_CRAWL_WET_OUTPUT_DIR=/tmp/common-crawl-like-smoke \
zsh sandbox/run_common_crawl_wet_matrix.sh

SAFEZONE_COST_BUILD=0 \
SAFEZONE_COST_RUNS=1 \
SAFEZONE_COST_BENCHES="common-crawl-q1" \
SAFEZONE_COST_CONFIGS="improved-default:1: unsafe-hp-32k:3:32768" \
SAFEZONE_COST_COMMON_CRAWL_PAGES=2000 \
SAFEZONE_COST_OUTPUT_DIR=/tmp/safezone-cost-smoke \
zsh sandbox/run_safezone_cost_matrix.sh
```

The compile passed, the checked compiler suite remained `96/96`, and the
checked runtime suite remained `38/38` at that checkpoint. The current
2026-05-03 runtime suite is `40/40`. The Common Crawl smoke matched
checksums/output counts across modes. The SafeZone cost smoke produced trace
rows for improved SafeZone and UnsafeZone-HP; at this tiny scale it is a
format/mechanics check only, not headline evidence.

SafeZone cost headline checkpoint:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-safezone-cost \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight safezone-cost" \
bash scripts/run-performance-evaluation.sh
```

This completed successfully with raw logs under
`cache/perf-eval/2026-05-01-safezone-cost/` and summary TSV at
`cache/perf-eval/2026-05-01-safezone-cost/summaries/safezone-cost/summary.tsv`.
Tracked interpretation is in `evidence/SAFEZONE_COST_MATRIX.md`.

Main findings:

- Current SafeZone's cliff is still per-page root removal. In traced linked
  ListOfLists, current root removal records `627735.229 ms`; improved mode
  reduces that to `116.420 ms`.
- `SAFEZONE_PAGE_SIZE=32768` explains much of the UnsafeZone-HP improvement.
  In GCBench, both `unsafe-hp-32k` and `improved-32k` cut claim calls from
  `215240` to `53790`, and `improved-32k` is slightly faster
  (`662.399 ms`) than `unsafe-hp-32k` (`665.224 ms`) in the traced row.
- Linked ListOfLists also favors `improved-32k` (`32080.248 ms`) over
  `unsafe-hp-32k` (`32970.802 ms`) in the traced row.
- Generated Common Crawl q1 exposes a serious trace-mode `unsafe-hp-32k`
  pathology: `227556.451 ms` despite low root/reclaim counters and matching
  output, while `improved-32k` is `8079.502 ms`.
- Chunk-root mode is competitive on Dataflow/Common Crawl and should remain a
  safer intermediate candidate.

Decision from this run: do not implement `rift-checked-safezone-hp` on top of
rootless UnsafeZone-HP alone. The leading safe backend candidate is improved
SafeZone with explicit 32 KiB/page-size or chunk-root configuration, with
rootless UnsafeZone-HP kept as the unsafe lower-bound comparator.

Common Crawl-like non-trace follow-up:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
COMMON_CRAWL_WET_PAGES=100000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=3 \
COMMON_CRAWL_WET_WARMUPS=1 \
COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window q3-parser-scratch" \
COMMON_CRAWL_WET_MODES="heap safezone-improved safezone-improved-32k safezone-chunk unsafezone-hp rift-hp rift-streaming" \
COMMON_CRAWL_WET_OUTPUT_DIR=/Users/siyaoliu/rift/cache/common-crawl-like-2026-05-01-100k \
zsh sandbox/run_common_crawl_wet_matrix.sh

COMMON_CRAWL_WET_PAGES=1000000 \
COMMON_CRAWL_WET_BENCHMARK_RUNS=3 \
COMMON_CRAWL_WET_WARMUPS=1 \
COMMON_CRAWL_WET_QUERIES="q1-tokenize q2-domain-window q3-parser-scratch" \
COMMON_CRAWL_WET_MODES="heap safezone-improved safezone-improved-32k safezone-chunk unsafezone-hp rift-hp rift-streaming" \
COMMON_CRAWL_WET_OUTPUT_DIR=/Users/siyaoliu/rift/cache/common-crawl-like-2026-05-01-1m \
zsh sandbox/run_common_crawl_wet_matrix.sh
```

All rows matched checksums/output counts. Summaries are recorded in
`evidence/COMMON_CRAWL_LIKE_MATRIX.md`.

Key 1M rows:

| Query | Heap | Best SafeZone family | Best current Rift | Interpretation |
|---|---:|---:|---:|---|
| q1-tokenize, 2026-05-01 | `5531.233 ms`, GC `1575.099 ms` | unsafezone-hp `4665.711 ms`; improved-32k `4674.258 ms` | HPZone `4966.111 ms` | Superseded for Rift ordering by the 2026-05-02 fast-counter cleanup. |
| q2-domain-window, 2026-05-01 | `5344.266 ms`, GC `1606.364 ms` | improved-32k `4471.463 ms`; unsafezone-hp `4511.995 ms` | HPZone `4738.091 ms` | Superseded for Rift ordering by the 2026-05-02 fast-counter cleanup. |
| q1-tokenize, 2026-05-02 | `5466.535 ms`, GC `1580.847 ms` | improved-32k `4608.641 ms`; unsafezone-hp `4640.245 ms` | HPZone `4386.590 ms` | GC-heavy trusted-Rift win after removing default per-allocation byte-counter atomics. |
| q2-domain-window, 2026-05-02 | `5267.784 ms`, GC `1561.851 ms` | improved-32k `4425.273 ms`; unsafezone-hp `4437.924 ms` | Streaming `4164.288 ms` | GC-heavy trusted-Rift stream/window win after counter cleanup. |
| q3-parser-scratch | `10330.962 ms`, GC `859.220 ms` | unsafezone-hp `11065.693 ms` | Streaming `11206.504 ms` | Negative scratch-shape control; heap wins elapsed. |

The trace-mode `unsafe-hp-32k` q1 pathology did not reproduce in non-trace q1
or q2. Treat it as an instrumentation-sensitive warning. The 2026-05-02
counter cleanup changes the q1/q2 conclusion: Common Crawl-like q1/q2 now
argue that current Rift's allocator fast path can beat improved SafeZone on
large token/window streams when diagnostic allocation-byte atomics are out of
the default fast path. SafeZone-family internals remain important comparison
and possible backend material, but no longer dominate this particular
workload.

Latest execution checkpoint:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-smoke-streams \
RIFT_EVAL_SCALE=smoke \
RIFT_EVAL_SUITES="preflight streams" \
bash scripts/run-performance-evaluation.sh
```

This passed. It compiled the sandbox and ran the smoke stream suite for
NEXMark local, NEXMark Beam-default profile, Yahoo-style ad stream,
RIoTBench-style IoT, Wikimedia, Common Crawl WET-shaped, and Linear Road-shaped
matrices. The run wrote ignored raw logs and summaries under
`cache/perf-eval/2026-05-01-smoke-streams/`. Checksums/output counts matched
within each query/matrix. Treat this as harness validation only; it is not
headline performance evidence.

The first headline subset also passed:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-headline-core-prior-checked \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight core prior checked" \
bash scripts/run-performance-evaluation.sh
```

Tracked summary: `evidence/HEADLINE_CORE_PRIOR_CHECKED_2026_05_01.md`.
This run materially weakens several older positive rows: GCBench HPZone did
not beat heap/improved SafeZone, linked ListOfLists HPZone beat heap but lost
to improved SafeZone, Dataflow checked SELECT/AGGREGATE beat heap but lost to
improved SafeZone, and JOIN was won by heap. The clearest checked win in this
subset is manual AppendWindow (`33.754 ms` vs heap `38.671 ms`), with
prepend-cursor also winning its fair heap-prepend control. Treat older
core/prior/checked positives as provenance until revalidated or explained.

The same subset was rerun after the user reduced visible background work:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-headline-core-prior-checked-rerun \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight core prior checked" \
bash scripts/run-performance-evaluation.sh
```

Tracked summary:
`evidence/HEADLINE_CORE_PRIOR_CHECKED_RERUN_2026_05_01.md`. The rerun removed
the obvious linked ListOfLists heap outlier from the first run, but it did not
restore the older positive runtime/methodology claims. GCBench HPZone still
loses, linked ListOfLists HPZone still loses to improved SafeZone while beating
heap, Dataflow checked still loses to improved SafeZone, and AppendWindow
manual/prepend-cursor remain the clearest checked wins.

The missing headline stream and bounded DEBS legs have now also run:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-headline-streams \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight streams" \
bash scripts/run-performance-evaluation.sh

DEBS2015_BOTH_INPUT=/tmp/debs2015-month1-1000000.csv \
RIFT_EVAL_RUN_ID=2026-05-01-headline-debs-1m \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight debs" \
bash scripts/run-performance-evaluation.sh
```

Tracked summaries:
`evidence/HEADLINE_STREAMS_2026_05_01.md` and
`evidence/HEADLINE_DEBS_1M_2026_05_01.md`. The stream leg passed all matrix
checksums/output-count checks. The DEBS leg completed both normal and
instrumented RunBoth scripts and reported output equality. The strongest new
stream finding is not a clean Rift case-study win: generated Common Crawl
WET-shaped Q1 tokenization is genuinely GC-heavy (`1559.601 ms` heap GC at 1M
generated pages), and Rift beats heap while cutting GC to about `20.5 ms`, but
improved SafeZone is still faster. The best checked stream row remains
NEXMark Beam-default Q3: checked `295.166 ms` versus heap `315.715 ms` and
improved SafeZone `302.668 ms`, below the `>=10%` case-study gate. The
bounded DEBS 1M single run has trusted Streaming `4681.292 ms`, heap
`4987.579 ms`, and checked `4882.562 ms`; use it as bounded correctness/control
evidence, not as a median or full-month replacement.

UnsafeZone-HP validation checkpoint:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
GCBENCH_BENCHMARK_RUNS=1 zsh sandbox/run_gcbench_runtime_matrix.sh
NEXMARK_EVENTS=20000 \
NEXMARK_BENCHMARK_RUNS=1 \
NEXMARK_QUERIES=q3 \
NEXMARK_MODES="heap safezone-current safezone-improved unsafezone-hp rift-hp" \
NEXMARK_OUTPUT_DIR=/tmp/nexmark-unsafezone-smoke \
zsh sandbox/run_nexmark_region_matrix.sh
DEBS2015_BOTH_MODES="heap safezone-current safezone-improved unsafezone-hp rift-hp" \
DEBS2015_BOTH_OUTPUT_DIR=/tmp/debs2015-unsafezone-sample \
zsh bench/debs2015/run_both_sample_matrix.sh
```

These passed. GCBench confirmed root mode `3` plus 32 KiB pages and produced a
single-run smoke row: unsafezone-hp `250.579 ms` versus heap `267.363 ms`,
improved SafeZone `263.200 ms`, and Rift HPZone `291.065 ms`. NEXMark Q3 20k
matched checksum/output count across all tested modes and recorded
unsafezone-hp `5.659 ms`. DEBS RunBoth sample matched heap output for Q1 and
Q2 after stripping latency. These are smoke rows only; run headline medians
before using UnsafeZone-HP for claims.

Files added or changed:

- `scala-native-rift/sandbox/run_nexmark_region_matrix.sh`
- `scala-native-rift/sandbox/NEXMARK_REGION_MATRIX.md`
- `scala-native-rift/sandbox/run_common_crawl_wet_matrix.sh`
- `scala-native-rift/sandbox/COMMON_CRAWL_WET_MATRIX.md`
- `scala-native-rift/sandbox/src/main/scala-next/WikimediaRegionMatrix.scala`
- `scala-native-rift/sandbox/run_wikimedia_region_matrix.sh`
- `scala-native-rift/sandbox/WIKIMEDIA_REGION_MATRIX.md`
- `scala-native-rift/sandbox/src/main/scala-next/LinearRoadRegionMatrix.scala`
- `scala-native-rift/sandbox/run_linear_road_region_matrix.sh`
- `scala-native-rift/sandbox/LINEAR_ROAD_REGION_MATRIX.md`
- `scala-native-rift/sandbox/src/main/scala-next/YahooAdRegionMatrix.scala`
- `scala-native-rift/sandbox/run_yahoo_ad_region_matrix.sh`
- `scala-native-rift/sandbox/YAHOO_AD_REGION_MATRIX.md`
- `scala-native-rift/sandbox/src/main/scala-next/RiotBenchRegionMatrix.scala`
- `scala-native-rift/sandbox/run_riotbench_region_matrix.sh`
- `scala-native-rift/sandbox/RIOTBENCH_REGION_MATRIX.md`
- `scala-native-rift/sandbox/STREAM_GC_BENCHMARK_CANDIDATES.md`
- `scala-native-rift/sandbox/STREAM_BENCHMARK_LADDER.md`
- `scala-native-rift/sandbox/SN_WIN_ENVELOPE.md`
- `scala-native-rift/sandbox/UNSAFEZONE_HP_BASELINE_MATRIX.md`
- `scala-native-rift/nativelib/src/main/resources/scala-native/zone/MemoryPool.c`
- `scala-native-rift/nativelib/src/main/resources/scala-native/zone/MemoryPool.h`
- `scala-native-rift/nativelib/src/main/resources/scala-native/zone/LargeMemoryPool.c`
- `evidence/YAHOO_AD_REGION_MATRIX.md`
- `evidence/RIOTBENCH_REGION_MATRIX.md`
- `evidence/STREAM_GC_BENCHMARK_CANDIDATES.md`
- `evidence/COMMON_CRAWL_WET_MATRIX.md`
- `evidence/NEXMARK_REGION_MATRIX.md`
- `evidence/WIKIMEDIA_REGION_MATRIX.md`
- `evidence/LINEAR_ROAD_REGION_MATRIX.md`
- `evidence/STREAM_BENCHMARK_LADDER.md`
- `evidence/SN_WIN_ENVELOPE.md`
- `evidence/ALL_PHASE_RESULTS.md`
- `evidence/UNSAFEZONE_HP_BASELINE_MATRIX.md`
- `evidence/HEADLINE_UNSAFEZONE_CORE_PRIOR_2026_05_01.md`
- `evidence/HEADLINE_UNSAFEZONE_STREAMS_2026_05_01.md`
- `evidence/HEADLINE_UNSAFEZONE_DEBS_1M_2026_05_01.md`
- `evidence/PERF_EVAL_RUNBOOK.md`
- `evidence/EVALUATION_SUMMARY_TABLES.md`
- `evidence/HEADLINE_STREAMS_2026_05_01.md`
- `evidence/HEADLINE_DEBS_1M_2026_05_01.md`
- `docs/PERFORMANCE_EVALUATION_REPORT.md`
- `docs/ROADMAP.md`
- `scripts/sync-evidence.sh`
- `scripts/run-performance-evaluation.sh`

Validation for this checkpoint:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- The same compile was rerun before committing the stream-GC benchmark probes.
  It passed on `/Users/siyaoliu/rift/scala-native-rift` at commit
  `b74658903584f30474f6ce0c1fec21164b95dbab`.
- The comprehensive evaluation runner has now completed clean headline legs for
  `core prior checked`, `streams`, and bounded 1M `debs`. The full-month DEBS
  control has not been rerun under this exact sweep discipline.
- The comprehensive evaluation runner has also completed a clean headline
  `preflight core prior` leg with UnsafeZone-HP included. The resulting core
  and prior-work tables are now tracked, and the summary-output routing bug for
  future prior-work runs is fixed.
- The comprehensive evaluation runner has completed a clean headline
  `preflight streams` leg with UnsafeZone-HP included. Stream summaries are now
  self-contained under the run directory and tracked in the parent evidence.
- The comprehensive evaluation runner has completed a bounded DEBS 1M
  `preflight debs` leg with UnsafeZone-HP included. Outputs matched; the row is
  single-run bounded evidence.
- NEXMark corrected SafeZone 100k follow-up matched checksum/output count for
  Q1/Q5/Q8 across `heap`, `safezone-current`, `safezone-improved`,
  `rift-checked`, `rift-hp`, and `rift-streaming`.
- Common Crawl WET-shaped 5k smoke matched checksum/output count for Q0/Q1
  across `heap`, current SafeZone, `rift-hp`, and `rift-streaming`.
- Common Crawl WET-shaped corrected 100k Q1 3-run medians matched checksum and
  output count in default-bucket and small-bucket controls across `heap`,
  `safezone-current`, `safezone-improved`, `rift-hp`, and `rift-streaming`.
- Wikimedia generated TSV-shaped 20k smoke matched checksum/output count across
  Q0/Q1/Q2 and all modes.
- Wikimedia generated TSV-shaped 100k and 1M 3-run medians matched
  checksum/output count across Q0/Q1/Q2 and all modes.
- Wikimedia 10M Q2 single-run scale check matched checksum/output count across
  all modes.
- Linear Road generated 20k smoke matched checksum/output count across Q0/Q1/Q2
  and all modes.
- Linear Road generated 100k and 1M 3-run medians matched checksum/output count
  across Q0/Q1/Q2 and all modes.
- No Linear Road 10M scale check was run because no 1M row cleared the
  continuation gate.
- NEXMark Beam-default 100k 3-run medians matched checksum/output count across
  Q0/Q1/Q2/Q5/Q8 and all modes; the 1M Q1/Q2/Q8 subset also matched.
- Wikimedia real `clickstream-enwiki-2026-03.tsv.gz` Q2 100k and 1M 3-run
  medians matched checksum/output count across heap, current/improved SafeZone,
  HPZone, and Streaming.
- Common Crawl decompressed WET Q1 tokenization 10k and larger-shard rows
  matched checksum/output count across all modes. The 50k request loaded only
  `21425` usable pages and should not be treated as headline 50k evidence.
- Post-refocus Common Crawl real WET Q0 parse 10k medians matched
  checksum/output count and recorded max-GC/runs-with-GC; heap was fastest and
  max timed GC was zero.
- Linear Road official `datafile3hours.dat` Q0/Q1/Q2 100k and 1M 3-run
  medians matched checksum/output count across all modes.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed
  after adding the Yahoo and RIoTBench-style matrices.
- Yahoo-style ad stream 20k smoke matched checksum/output count across all
  modes/queries; 100k 3-run medians matched across all modes/queries; 1M Q2
  3-run medians matched across all modes.
- Expanded NEXMark Beam-default 1M rows matched checksum/output count for
  Q0/Q3/Q4/Q5/Q9/Q11 in the recorded runs.
- RIoTBench-style IoT 20k smoke matched checksum/output count across all modes
  and queries; 100k 3-run medians also matched across all modes and queries.

New evidence:

| Matrix | Scale | Main result | Interpretation |
|---|---:|---|---|
| NEXMark Q1 roots control | 100k | heap `54.378 ms`, current SafeZone `57.561 ms`, improved SafeZone `54.777 ms`, HPZone `53.008 ms` | Improved SafeZone closes the old SafeZone gap; trusted Rift is modestly fastest. |
| NEXMark Q5 roots control | 100k | heap `33.043 ms`, improved SafeZone `32.435 ms`, HPZone `32.865 ms`, checked `34.993 ms` | Improved SafeZone is fastest; Q5 remains non-winning for checked Rift. |
| NEXMark Q8 roots control | 100k | heap `29.598 ms`, improved SafeZone `29.919 ms`, Streaming `28.766 ms`, checked `29.146 ms` | Near-tie; Streaming is slightly fastest. |
| Common Crawl WET q1 default buckets | 100k pages / 13.7M records | heap `427.942 ms` with `149.149 ms` GC; improved SafeZone `381.006 ms`; Streaming `403.935 ms` | Heap pressure is real, but improved SafeZone beats trusted Rift. |
| Common Crawl WET q1 small buckets | 100k pages / 13.7M records | heap `386.807 ms`; improved SafeZone `381.109 ms`; HPZone `406.536 ms`, Streaming `419.779 ms` | Tighter lifetimes keep improved SafeZone fastest and heap competitive. |
| Wikimedia Q2 clickstream | 1M events / 2M records | heap `159.746 ms`, improved SafeZone `147.936 ms`, HPZone `147.163 ms`; heap GC `35.238 ms`, HPZone GC `2.206 ms` | Promising generated row, but not a 10% win over improved SafeZone. |
| Wikimedia Q2 clickstream | 10M events / 20M records, single run | heap `1459.438 ms`, improved SafeZone `1473.088 ms`, HPZone `1462.015 ms` | Lower GC, but elapsed is a near-tie; not a headline case study. |
| Linear Road Q1 tolls | 1M events / 2M records | heap `170.464 ms`, improved SafeZone `196.138 ms`, HPZone `191.896 ms`; heap GC `24.819 ms`, HPZone GC `0.000 ms` | Rift removes GC and beats improved SafeZone, but heap remains fastest. |
| Linear Road Q2 accidents | 1M events / 2M records | heap `194.520 ms`, improved SafeZone `215.808 ms`, HPZone `203.793 ms`; heap GC `27.604 ms`, HPZone GC `0.000 ms` | Same ceiling result: lower GC, no elapsed win over heap. |
| NEXMark Beam-default Q1 | 1M generated-profile events | heap `579.038 ms`, improved SafeZone `561.787 ms`, checked `557.251 ms`, HPZone `538.451 ms` | Best new positive row; generated Beam-default profile, not Beam runner evidence. |
| NEXMark Beam-default Q8 | 1M generated-profile events | heap `331.599 ms`, improved SafeZone `326.569 ms`, checked `315.545 ms` | Modest checked win; below case-study margin. |
| NEXMark Beam-default Q0 | 1M generated-profile events | heap `548.184 ms`, improved SafeZone `482.774 ms`, checked `497.319 ms`, HPZone `467.895 ms` | Strong trusted stream-object row; checked beats heap but not improved SafeZone. |
| NEXMark Beam-default Q3 | 1M generated-profile events | heap `304.190 ms`, improved SafeZone `293.586 ms`, checked `287.169 ms` | Best new checked expanded-query row. |
| NEXMark Beam-default Q11 | 1M generated-profile events | heap `255.418 ms`, improved SafeZone `237.400 ms`, checked `240.065 ms`, HPZone `226.862 ms` | Trusted session-window win; checked not better than improved SafeZone. |
| Yahoo-style ad Q2 | 1M generated/preloaded events | heap `104.512 ms`, improved SafeZone `108.173 ms`, HPZone `105.216 ms`, Streaming `105.961 ms` | Cuts median GC from `6.253 ms` to `2.1-2.4 ms`, but heap elapsed is still slightly fastest. |
| RIoTBench-style q1 | 100k generated sensor events | heap `16.643 ms`, improved SafeZone `13.980 ms`, HPZone `14.516 ms`, Streaming `14.445 ms` | Heap GC pressure exists and Rift beats heap, but improved SafeZone remains the stronger baseline. |
| Wikimedia real enwiki Q2 | 1M events / 2M outputs | heap `126.800 ms`, improved SafeZone `149.062 ms`, Streaming `157.449 ms`; median GC `0.000 ms` | Real TSV row is heap-fastest; one heap timed run collected `67.236 ms`, but the median is zero. |
| Common Crawl real WET Q1 | 10k pages / 349709 token records | heap `12.079 ms`, improved SafeZone `16.093 ms`, Streaming `15.651 ms`; median GC `0.000 ms` | Real WET preloaded row is heap-fastest. |
| Linear Road official Q1/Q2 | 1M events / 2M outputs | q1 heap `162.668 ms` vs HPZone `180.277 ms`; q2 heap `167.811 ms` vs Streaming `198.863 ms`; median GC `0.000 ms` | Official preloaded input is a ceiling result; each 1M heap query had one collection outlier. |

Current conclusion:
Common Crawl WET, generated/real Wikimedia, generated/official Linear Road,
Yahoo-style ad stream, and RIoTBench-style IoT are useful memory-pressure
detectors and regression controls, but none currently clears the case-study
gate against heap and improved SafeZone. NEXMark Beam-default Q3/Q8 are the
useful checked profile rows, while Q0/Q1/Q11 are trusted-runtime profile rows;
all are still generated-profile evidence. The next step should be focused
checked-operator overhead work, not more application-specific tuning.

Benchmark data-source checkpoint:
Real input/source bundles have now been downloaded into ignored local cache
storage and recorded in `evidence/BENCHMARK_DATA_SOURCES.md`. The local data
root is `/Users/siyaoliu/rift/cache/benchmark-data`. Downloaded artifacts
include a Wikimedia March 2026 pageviews hour, Swedish and English Wikimedia
March 2026 clickstream TSVs, Common Crawl April 2026 WET/WAT/WARC path lists,
one real Common Crawl WET shard, and the official Linear Road MITSIM, data
driver, test-data, and validator bundles. The official Apache Beam `2.73.0`
source release is also downloaded and SHA-512 verified; it contains the Java
NEXMark generator/configuration under `sdks/java/testing/nexmark`.

The first Scala Native input-wiring pass is now implemented:

- `NEXMARK_BEAM_DEFAULTS=1` switches `NexmarkRegionMatrix` to a Beam-default
  generated profile and records `NEXMARK_BEAM_SOURCE`.
- `WIKIMEDIA_INPUT` plus `WIKIMEDIA_INPUT_KIND=pageviews|clickstream` preloads
  real Wikimedia rows.
- `COMMON_CRAWL_WET_INPUT` preloads real WET conversion records. Use the
  decompressed `.warc.wet` sample from the cache; the compressed shard remains
  provenance because Common Crawl WET is a concatenated gzip stream.
- `LINEAR_ROAD_INPUT` preloads official Linear Road Data Driver `.dat` position
  reports.

Validation for this wiring pass:

| Matrix | Input | Smoke |
|---|---|---|
| NEXMark | `NEXMARK_BEAM_DEFAULTS=1`, 20k Q1 | heap/HPZone matched checksum/output count |
| Wikimedia | real `clickstream-svwiki-2026-03.tsv.gz`, 20k Q2 | heap/HPZone matched checksum/output count |
| Common Crawl WET | decompressed first April 2026 WET shard, 100 pages Q1 | heap/HPZone matched checksum/output count |
| Linear Road | official `datafile20seconds.dat`, Q1 | heap/HPZone matched checksum/output count |

Prior checked-operator checkpoint:
`RiftRegion.StreamWindowFold[T]` adds an experimental checked additive
stream-window fold primitive, backed by parent-owned primitive aggregate
tables and child-bucket region records. The implementation lives in
`scala-native-rift/nativelib/src/main/scala-next/scala/scalanative/memory/RiftRegion.scala`;
the focused matrix lives in
`scala-native-rift/sandbox/src/main/scala-next/CheckedWindowFoldMatrix.scala`
and is run by `scala-native-rift/sandbox/run_checked_window_fold_matrix.sh`.

The focused gate failed, so Common Crawl WET, NEXMark Q5 fold integration, and
DEBS fold integration remain blocked:

| Scale | Mode | Median ms | GC ms | Rift op ms | RSS bytes | Interpretation |
|---:|---|---:|---:|---:|---:|---|
| 100k | heap | `9.263` | `0.000` | `0.000` | `21102592` | fair heap control |
| 100k | rift-checked | `11.999` | `0.000` | `0.060` | `14958592` | lower RSS, slower elapsed |
| 1M | heap | `103.244` | `11.910` | `0.000` | `75022336` | fair heap control |
| 1M | rift-checked | `118.726` | `0.000` | `0.175` | `40402944` | zero measured GC and lower RSS, but failed speed gate |
| 1M | rift-trusted-hp | `104.919` | `0.000` | `0.117` | `46841856` | close to heap, not a win |
| 1M | rift-trusted-streaming | `106.088` | `0.000` | `0.120` | `46956544` | close to heap, not a win |

Validation for the fold checkpoint:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"` passed `96/96`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"` passed `38/38`.
- 20k smoke, 100k 3-run, and 1M 3-run `CheckedWindowFoldMatrix` rows matched checksum across all modes.

Interpretation:

- The memory-management direction is useful: checked fold removes measured GC
  and cuts 1M RSS from `75022336` to `40402944` bytes.
- The elapsed gate fails: checked fold is `118.726 ms` versus heap
  `103.244 ms`.
- The next implementation step should profile/reduce checked aggregate-table
  overhead before using this API in Common Crawl WET or NEXMark Q5.

Previous NEXMark checkpoint:
`NexmarkRegionMatrix` adds the first non-DEBS NEXMark-style stream-processing
ladder. The benchmark lives in
`scala-native-rift/sandbox/src/main/scala-next/NexmarkRegionMatrix.scala` and
is run by `scala-native-rift/sandbox/run_nexmark_region_matrix.sh`. It covers
Q0 passthrough, Q1 bid currency conversion, Q2 low-output selection, Q5
hot-auction windowing, and Q8 new-user/new-auction window joins over
deterministic ordinary Scala `Person`/`Auction`/`Bid` style records. Modes are
`heap`, `rift-checked`, `rift-hp`, and `rift-streaming`; the focused Q8
follow-up adds Q8-only `heap-join-api` and `rift-checked-join-api` modes.
SafeZone is intentionally deferred.

This checkpoint completed both requested pre-real-data follow-ups:

- `RiftRegion.StreamJoinWindow[T]` factors the Q8 two-sided join/window shape
  into a checked API over child-bucket append windows. It owns parent-region
  primitive left/right count arrays and appends ordinary Scala records through
  checked `putJoinLeftInBucket`, `putJoinRightInBucket`, and
  `putJoinOutputInBucket` methods. The compiler guard rejects direct unrooted
  heap values passed through those methods.
- `NEXMARK_Q5_DIAG=1` adds opt-in Q5 counters for append/remove counts,
  closed buckets, sample scans, top-scan entries/time, and final live records.
  Diagnostic elapsed rows are not headline evidence.
- A fair specialized heap Q8 join control was added after the first Q8 API
  numbers proved too optimistic against the generic heap runner. This is now a
  do-not-redo lesson: any API that specializes the query loop needs an equally
  specialized heap control.
- The latest checkpoint adds packed-count Q8 join-window fast paths:
  `putJoinLeftInBucketAndCounts`, `putJoinRightInBucketAndCounts`,
  `removeJoinLeftAndCounts`, and `removeJoinRightAndCounts`. These reduce
  repeated count lookups in the checked Q8 API and narrow the 1M gap, but the
  API still does not pass the fair speed gate.

Validation for the NEXMark-lite checkpoint:

- 20k smoke matched checksum/output count across all four queries and all four
  modes.
- 100k and 1M 3-run medians matched checksum/output count across all modes.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- After packed `StreamJoinWindow` counts, `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"` passed `94/94`.
- After `StreamJoinWindow`, `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"` passed `37/37`.

Current NEXMark-lite 1M medians:

| Query | Heap | Checked | HPZone | Streaming | Interpretation |
|---|---:|---:|---:|---:|---|
| q0 passthrough | `197.059 ms` | `197.494 ms` | `194.113 ms` | `196.232 ms` | near tie; GC/RSS reduction but little elapsed ceiling |
| q1 conversion | `384.595 ms` | `374.767 ms` | `384.774 ms` | `371.404 ms` | first broader stream-map win |
| q2 selection | `297.053 ms` | `287.808 ms` | `294.806 ms` | `305.249 ms` | checked elapsed/GC win, but checked RSS is higher than heap |
| q5 hot items | `350.941 ms` | `355.100 ms` | `356.015 ms` | `356.588 ms` | not a window-aggregate win yet |
| q8 window join | `322.210 ms` | `291.832 ms` | `305.338 ms` | `305.410 ms` | strongest NEXMark-lite checked win so far |

Focused Q8 join API 1M medians:

| Mode | Median ms | GC ms | Rift op ms | RSS bytes | Interpretation |
|---|---:|---:|---:|---:|---|
| heap | `327.102` | `27.578` | `0.000` | `146669568` | generic heap runner |
| heap-join-api | `17.393` | `0.000` | `0.000` | `146391040` | fair specialized heap control, packed follow-up run |
| rift-checked | `312.551` | `8.867` | `0.139` | `149733376` | generic checked runner |
| rift-checked-join-api | `20.987` | `0.000` | `0.062` | `124157952` | packed checked API; lower GC/RSS, slower than specialized heap |

Q5 follow-up:

- Clean 1M control after diagnostics: heap `361.882 ms`, checked
  `393.415 ms`, HPZone `364.071 ms`, Streaming `369.280 ms`.
- Diagnostic 1M counters match across modes: `1000000` adds/removes,
  `40` closed buckets, `123` samples, `8060928` top-scan entries, final live
  records `0`.
- Top scan time is about `45 ms` in every mode, so the Q5 checked loss is
  checked per-entry/window-container CPU and live-window footprint, not region
  open/close cost or top scanning alone.

Treat all of this as local methodology evidence, not exact Apache Beam
NEXMark. The next step should reduce reusable checked operator overhead or
design a fair heap/Rift Q5 aggregate-maintenance API before moving to
Wikimedia/Linear Road/Common Crawl.

Status: active research fork. The Phase 5 input-boundary checkpoint, reusable
ranking backend, Q2 bounded cell-table checkpoint, Q1 primitive route-table
checkpoint, Q2 latest-empty taxi-table checkpoint, Q2 array-backed ranking
checkpoint, Q2 taxi-id table checkpoint, Q1 indexed-ranking checkpoint,
RunBoth output-snapshot placement checkpoint, packed Grid cell-key diagnostic
checkpoint, JVM same-input GC probe, JVM RunBoth cross-check, literature
benchmark contract, Broom-style dataflow methodology harness, and Q2
incremental median heap checkpoint are merged into `feature/rift`.
The first Phase 7 checked-region hard-pattern probe slice is also committed:
for-loop scoped allocation, nested scoped regions, local higher-order
consumers, nested-region escape rejection, and conservative returned-function
rejection now have compiler-test coverage. The current Phase 8 slices add the
explicit `RiftRegion.HeapRoot` path for checked region-to-GC metadata handles
and reject direct unrooted heap-object constructor arguments in checked Rift
allocation lowering. Simple region-local aliases are now propagated; heap
aliases and heap field selections are rejected. Stable constructor fields whose
source types are explicitly captured by `{region}` are accepted; plain `T^`
field reuse is rejected by Scala capture checking when `T^{region}` is
required. Static module singletons and immutable module vals are accepted as
independently rooted heap metadata; mutable static vars are rejected.
Region-owned arrays are accepted when reference elements are explicitly
captured, and stores into known region arrays reject unrooted heap objects. The
first checked collection primitive, `RiftRegion.ObjectBuffer`,
region-owns its backing object array while keeping heap control metadata; its
v1 operations are owner-token based, including the companion function form
`RiftRegion.append(region, buffer, value)` and the extension method form
`region.append(buffer, value)`, and reject direct heap stores or inner-region
values stored into an outer buffer in compiler probes. `RiftRegion.RegionBuffer`
extends that checked-container story to a growable owner-token buffer: growth
allocates a new backing object array in the owning region, copies references,
and leaves old backing arrays for region close/reset reclamation. Compiler and
runtime probes cover growth, region objects, `HeapRoot` handles, direct heap
store rejection, and inner-region-to-outer-buffer rejection.
`RiftRegion.RegionPriorityQueue` adds a checked ranking/top-k container:
values live in region-owned object arrays, priorities live in parallel
region-owned `Long` arrays, and owner-token `push/peek/pop` APIs reject direct
heap values unless they are explicitly rooted. Compiler probes cover region
objects, direct heap rejection, `HeapRoot`, and inner-region rejection for the
priority queue. `RiftRegion.RegionIndexedPriorityQueue` adds the next reusable
ranking primitive: dense-key `put/get/contains/updatePriority/peek/pop`
operations let checked stream code create an ordinary Scala object once per key
inside a region, mutate it on later events, and update its rank without
per-refresh object churn. Compiler probes cover keyed update, keyed
replacement, direct heap rejection, `HeapRoot`, and inner-region rejection for
the indexed queue. A focused
checked-container methodology harness, `CheckedRegionBufferMatrix`, now
compares a heap growable object buffer against checked `RegionBuffer` under the
same epoch-local record workload. The first literature-shaped checked operator
set is also in place: `DataflowRegionMatrix` has checked `rift-checked` modes
for SELECT, AGGREGATE, and JOIN using `RiftRegion.streaming/reset`,
`RegionBuffer` output buffers, and region-owned aggregate tables.
The StreamFlex-style throughput/latency, Yak-style epoch/control/data including
grouped sort, top-word/filter, GraphChi-like subintervals, and
runtime/promotion proxies, and Stancu-style
transaction/accounting methodology
harnesses are also committed locally. The latest checkpoint narrows checked
allocation guards to the
`ScopedRegion`/`StreamingRegion` safe API surface, leaves low-level
`RiftRegion.open(...)` benchmark allocation explicitly trusted, and replaces
RunBoth's generic latency `ArrayBuffer[Long]` collectors with shared primitive
buffers whose Rift backing arrays live in the existing run snapshot region.
The current latest checkpoint adds Q2 rank/output attribution counters and
phase timers: rank-heap comparisons/swaps, top-candidate comparisons,
changed-output checks, and Q1/Q2 change/snapshot timings.
The newest Phase 5 checkpoint adds a shared Q2 top-10 cache so the heap/Rift
logical query still returns top-k on every event but only recomputes the heap
frontier when a rank update can affect the cached top 10. The cache checkpoint
now has 100k and 1M 3-run medians recorded.
The latest implementation checkpoint adds opt-in GC heap allocation
attribution with `SCALANATIVE_GC_ALLOC_STATS=1`. It records heap allocation
calls, rounded heap bytes requested, and measured heap allocation-call time.
On the 1M bounded DEBS sample, the attribution run shows heap at
`19,924,383` GC allocation calls, `679,841,024` allocated bytes, and
`582.629 ms` measured GC allocation-call time, versus Rift HPZone at
`14,462,042` calls, `455,349,920` bytes, and `385.807 ms`, and Rift Streaming
at `14,462,060` calls, `455,350,304` bytes, and `384.031 ms`. This is
diagnostic evidence, not a headline throughput run, because attribution times
every heap allocation and perturbs elapsed timings.
The next diagnostic checkpoint refines this into C-side phase buckets. A
Scala-side phase-counter attempt was rejected because reading counters in the
hot loop allocated and polluted the data. The clean C-side 1M buckets show
that Rift has nearly eliminated Q1/Q2 process and snapshot heap allocation
(`3.28M` to `21.5k` Q1 process calls, `2.09M` to `46.9k` Q2 process calls,
and snapshot heap allocation to zero), while Q1/Q2 output construction still
accounts for about `14.39M` heap allocation calls in both heap and Rift modes.
The latest DEBS checkpoint acts on that finding: RunBoth now uses a shared
byte-oriented output writer. Heap mode uses a heap byte buffer; Rift modes
place the reusable byte buffer in the run snapshot region. Output rows and
query semantics are unchanged. The 1M non-attribution 3-run medians are now
heap `4640.593 ms`, HPZone `4524.706 ms`, and Streaming `4522.308 ms`; GC
collection medians are heap `21.025 ms`, HPZone `0.685 ms`, and Streaming
`0.635 ms`.
The newest checkpoint median-backs checked RunBoth integration. The 100k/1M
matrix over `heap`, `rift-hp`, `rift-streaming`, and `rift-checked` completed
with matching outputs. At 1M, heap is `5363.257 ms`, trusted HPZone is
`5224.005 ms`, trusted Streaming is `5209.104 ms`, and checked is
`5043.240 ms`; GC medians are heap `21.226 ms`, HPZone `0.834 ms`, Streaming
`0.862 ms`, and checked `2.473 ms`. Treat this as bounded-sample Phase 5/7
evidence, not final DEBS proof.
The selective checked allocation-attribution diagnostic then showed the 1M
checked path dropping heap allocation calls from `6025149` to `752568`, rounded
heap bytes from `235159840` to `28785632`, and measured heap allocation-call
time from `173.578 ms` to `20.514 ms` versus heap. This is diagnostic evidence
only because the allocation counters perturb timing.
The latest implementation checkpoint adds Rift mapped-memory, active-region,
and active-requested-byte counters. A 100k heap/checked validation run matched
outputs and reported checked peak mapped bytes `31817728`, peak active mapped
bytes `31670272`, and peak active requested bytes `29575648`. A full-month
checked-only diagnostic reported RSS `1086668800` bytes, peak mapped bytes
`906346496`, peak active mapped bytes `904790016`, peak active requested bytes
`823153856`, final active bytes `0`, and final mapped bytes `134479872`
against a `128 MiB` pool cap. This means the full-month checked RSS regression
is mostly live region payload under current lifetimes, not closed-slab pool
retention or extreme slab fragmentation. Treat it as a single-run memory
attribution diagnostic, not a new headline performance median.
The newest checkpoint adds opt-in per-region-family attribution and fixes the
dominant lifetime mismatch it exposed. With `DEBS2015_RIFT_FAMILY_STATS=1`,
full-month checked attribution showed the checked parent stream carrying
`808569032` peak active requested bytes. Q1 checked rank object graphs were
logically tied to the latest route event but physically parent-lived. They now
allocate in the current Q1 child bucket through
`RiftRegion.childBucketRegion(stream, bucket.child)`. Full-month checked-only
diagnostics after the change show active requested peak falling from
`823153856` to `180948200` bytes, active mapped peak from `904790016` to
`261816320` bytes, and RSS from `1086668800` to `613318656` bytes. A 1M
non-family heap/checked sanity control matched outputs and measured heap
`4353.927 ms`, `19.662 ms` GC, `160088064` bytes RSS versus checked
`4209.383 ms`, `2.124 ms` GC, and `66715648` bytes RSS. These are still
single-run controls.
The follow-up full-month heap/checked 3-run control after the Q1 rank lifetime
fix also matched outputs. Its median is a near-tie on elapsed time: heap
`67.122 s` versus checked `66.804 s`. The memory result is stronger: checked
median RSS is now `613.3 MiB`, close to heap `595.9 MiB` and far below the
prior checked `866.6 MiB` median. GC collection time drops from `0.285 s` heap
to `0.117 s` checked, while checked pays `0.779 s` median Rift region-op time
and is slower in Q1/Q2 process CPU phases. Treat this as full-month memory
validation and near-tie throughput evidence, not a large application speedup.
One attempted Q1 CPU fix was rejected and documented: a route-lifetime
child-bucket probe reduced 100k checked Q1 rank creation back to heap scale
(`64672`) but opened `69220` child regions, raised RSS to `113721344` bytes,
and did not improve elapsed time. Do not pursue one child region per active
route; the next Q1 design needs shared arenas or output/rank snapshots without
per-route regions.
Another narrower Q1 same-second reuse probe was also rejected. The idea was to
mutate an existing checked rank object when a route was refreshed within the
same dropoff-second bucket, because that object would already have the right
child lifetime. A 100k diagnostic compile/run showed no useful effect:
`rift-checked` still created `98005` Q1 rank objects for `98005` rank refreshes.
The code change was backed out to avoid carrying an extra hot-path branch.
The latest checkpoint adds a closeable SafeZone DEBS control. `Q1SafeZone` and
`Q2SafeZone` use the same Q1/Q2 bucket/ranking algorithms as heap and trusted
Rift, but allocate Q1/Q2 data structures through explicit `SafeZone.open()` /
`SafeZone.close(zone)` scopes. Single-run 100k and 1M controls matched heap
output for current SafeZone (`SAFEZONE_ROOTS_MODE=0`) and improved SafeZone
(`SAFEZONE_ROOTS_MODE=1`); 1M now has 3-run medians. In the 1M improved-roots
median matrix, SafeZone is slower than heap (`5576.947 ms` versus
`5029.882 ms`) and checked Rift (`4702.930 ms`) while using less RSS than heap
(`103.1 MiB` versus `153.7 MiB`) but more than checked Rift (`63.6 MiB`).
Improved roots mode cuts SafeZone close time versus current roots mode
(`34.876 ms` median versus `118.124 ms`), but Q1/Q2 process CPU remains slower.
Treat this as median-backed bounded control evidence, not full-month evidence.
The latest checkpoint adds opt-in DEBS process CPU diagnostics behind
`DEBS2015_PROCESS_DIAGNOSTICS=1`, so normal timing runs do not inherit the hot
Q1 comparison counters. The gated 1M diagnostic matched outputs and showed
checked Rift still faster/lower-RSS than heap and SafeZone, with the same Q2
operation counts as heap and a deliberate Q1 rank-object refresh count of
`979699` versus heap's `573523` rank creations. The gated full-month diagnostic
also matched outputs and explains the remaining checked process limit: Q2 rank
fixes, median reads, rank comparisons, profit entries, and empty entries are
identical between heap and checked, while Q1 checked rank creations rise from
`6195167` to `14487771` because checked rank objects are refreshed into the
current child-bucket lifetime. Treat these rows as perturbing attribution
evidence, not headline throughput. The follow-up Q1 window-rank arena reduces
this churn without one child region per route. The next implementation-facing
work is to generalize that pattern into reusable checked APIs and explain the
lower checked rank/container CPU overhead and stronger close discipline;
full-month SafeZone controls are optional rather than blocking that CPU work.
The newest general-framework checkpoint adds `RegionPriorityQueue` and
`CheckedRegionPriorityQueueMatrix` as a reusable checked ranking/top-k
primitive. The focused compiler suite now passes `58/58`; `sandbox3_next`
compiles; small heap/Rift priority-queue smoke runs match checksum; and the
default local matrix records heap `27.369 ms`, `2.160 ms` GC, `26.5 MB` RSS
versus checked `28.621 ms`, `0.000 ms` GC, `0.279 ms` Rift op, and `17.0 MB`
RSS. Treat this as API/safety evidence, not a speed claim: it generalizes the
ranking-container direction, but Q1 still needs richer tie-breaking and durable
indexed state.
The latest general-framework checkpoint adds `RegionIndexedPriorityQueue` and
`CheckedRegionIndexedPriorityQueueMatrix` for durable dense-key ranking state.
The focused compiler suite now passes `63/63`; `sandbox3_next/compile` passes;
the small heap/Rift indexed-queue smoke runs match checksum; and the default
local matrix records heap `100.254 ms`, `2.201 ms` GC, `22.1 MB` RSS versus
checked `103.052 ms`, `0.000 ms` GC, `0.406 ms` Rift op, and `26.3 MB` RSS.
Treat this as API/safety evidence, not a speed claim: it validates the
fetch/mutate/update state shape needed to reduce Q1/Q2 rank-refresh churn
without inventing a DEBS-only algorithm. Remaining work is richer tie-breaking,
hash/non-dense key support, and integration into real operators.
The newest focused framework checkpoint adds `CheckedStreamWindowRankMatrix`.
It exercises `StreamWindowIndexedRank` in a stream-window workload where
ordinary Scala records live in checked child bucket regions while parent-owned
rank state tracks dense keys. Heap and checked modes matched checksums. The
default 1M-event median is a deliberate caution, not a speed claim: heap
`199.762 ms`, checked `254.050 ms`, checked Rift op `0.369 ms`, heap RSS
`145833984` bytes, and checked RSS `93585408` bytes. This validates the
general bucket-region rank pattern and shows the next work should reduce
checked container CPU overhead or add richer rank APIs before wholesale DEBS Q1
integration.
The latest Phase 5 checkpoint applies the same lifetime idea to real DEBS Q1:
checked Q1 now separates per-second event buckets from coarser rank arenas
whose lifetime matches the Q1 window. Routes refreshed inside the same rank
arena mutate their existing ordinary Scala `CheckedRankedRoute` object graph;
routes crossing an arena boundary allocate a new rank graph in the later arena.
This preserves the heap/Rift logical query algorithm while changing allocation
placement/lifetime. The 1M non-diagnostic heap/checked 3-run median is a
near-tie: heap `4601.532 ms`, `20.335 ms` GC, `153.7 MiB` RSS versus checked
`4610.413 ms`, `2.304 ms` GC, `63.9 MiB` RSS and `7.577 ms` Rift op time. A
single full-month scale check matched outputs and measured heap `72.445 s`,
`304.485 ms` GC, `594.4 MiB` RSS versus checked `72.556 s`, `86.404 ms` GC,
`447.8 MiB` RSS and `949.899 ms` Rift op time. Full-month checked Q1 rank
objects fall from the previous checked `14487771` per-refresh shape to
`8842434`; heap creates `6195167`. Treat this as a successful lifetime/memory
checkpoint and a reusable arena pattern, not as a final DEBS speed claim.
The newest framework checkpoint lifts that pattern into
`RiftRegion.StreamBucketArena` and migrates checked Q1 rank buckets onto the
reusable owner-token API. `RiftRegion.streamBucketFor`,
`streamBucketRegion`, `closeStreamBucketsBefore`, and `closeAllStreamBuckets`
now provide the checked stream-bucket primitive. The focused compiler suite now
passes `65/65`, the native checked runtime test passes `16/16`, and sample plus
100k RunBoth `heap`/`rift-checked` controls matched outputs. Treat this as a
Phase 7 API/correctness checkpoint, not a new DEBS median.
The latest framework checkpoint adds `RiftRegion.StreamWindowIndexedRank`,
which composes `StreamBucketArena` with the checked
`RegionIndexedPriorityQueue`. It gives stream operators a reusable dense-key
rank collection whose values can be ordinary Scala objects allocated in
child-window regions and widened through the parent stream owner token. The
new `putWindowRankInBucket` insertion path records which child bucket owns a
dense key, and `closeWindowRankBucketsBefore`/`closeAllWindowRankBuckets`
automatically remove tracked keys from parent-owned rank state before closing
the child bucket. The follow-up entry-cleanup API adds
`closeWindowRankBucketsBeforeWithEntries` and
`closeAllWindowRankBucketsWithEntries`, so stream operators can clean
side tables during framework unlinking instead of maintaining a duplicate
bucket-local key list. The focused compiler suite now passes `72/72`; the
native checked runtime suite passes `23/23`.
The follow-up remove-with-value close primitive validates already-popped-key
cleanup but does not yet reduce the focused checked CPU gap; the next useful
stream-window-rank direction is a lower-overhead rank API rather than another
narrow queue tweak. The newest lexicographic priority API adds Q1-style
count/time/sequence/key tie-breakers to the same dense-key checked rank/window
shape.
The newest framework checkpoint adds `RiftRegion.RegionLongIndexedPriorityQueue`,
a standalone hash-keyed checked rank queue for arbitrary `Long` keys. Its
values, heap keys, priorities, and open-addressed index table are region-owned
arrays, and its owner-token `put` overloads use the same checked value-store
guard as the dense indexed queue. This removes the standalone dense-remapping
blocker for packed route keys, but stream-window close-discipline integration
and lower checked-container CPU overhead remain open. The focused compiler
suite now passes `76/76`, and the native checked runtime suite passes `25/25`.
The follow-up framework checkpoint adds `RiftRegion.StreamWindowLongIndexedRank`,
which composes the long-key queue with `StreamBucketArena` close discipline.
Bucket-owned arbitrary `Long` keys are tracked in a region-owned owner table
and removed from parent rank state before the child bucket closes. The focused
compiler suite now passes `80/80`, and the native checked runtime suite passes
`28/28`. This is still API/safety evidence, not a DEBS performance row.
The latest focused matrix checkpoint adds `heap-long` and `rift-checked-long`
modes to `CheckedStreamWindowRankMatrix` so the long-key stream-window API is
measured before DEBS integration. Checksums match at 20k, 100k, and 1M. The
checked long-key mode now uses the no-entry close helper because rank state
owns lookup in that shape. The 100k median is heap-long `37.045 ms`,
`0.000 ms` GC, `38.8 MB` RSS versus `rift-checked-long` `49.450 ms`,
`0.000 ms` GC, `0.178 ms` Rift op, and `33.9 MB` RSS. The default 1M median
is heap-long `358.988 ms`, `6.973 ms` GC, `111.4 MB` RSS versus
`rift-checked-long` `503.906 ms`, `5.470 ms` GC, `0.491 ms` Rift op, and
`128.3 MB` RSS. Treat this as functional API evidence and an overhead warning:
the packed-key/dense-remap blocker is gone, but broad Q1 integration should
wait for a lower-overhead checked rank/window pass.
The next checked-rank checkpoint added fused `StreamWindowTableRank`, but its
focused 1M gate failed and the Q1 prototype was backed out of DEBS. A profile
pack showed combined lookup/probe/replacement/heap-maintenance overhead rather
than Rift open/close/allocation cost, so TableRank remains framework evidence
only. The latest cheap-operator checkpoint then added
`CheckedAppendWindowMatrix` and a reusable `RiftRegion.StreamAppendWindow`
API. The manual checked child-bucket append shape wins at 1M
(`32.261 ms` versus heap `35.513 ms`, with lower RSS). The first reusable
per-entry close API did not pass, but cached bucket/region use plus
`StreamAppendCursor` close clears the focused 1M API gate
(`34.708 ms` versus same-run heap `35.705 ms`). Checked Q1 event-window
entries now use that cursor-close API and match heap output on sample/100k
Q1 and RunBoth controls plus a 1M 3-run RunBoth control. The 1M median is
heap `4559.928 ms` versus checked `4514.165 ms`, with RSS `153.8 MiB` versus
`91.7 MiB`. Treat this as bounded application-path evidence, not final
full-DEBS proof. The follow-up Q2 profit/empty-window migration uses the same
cursor-close API and matches output through 1M medians, but the 1M elapsed
median is a near tie and checked RSS rises to `142.4 MiB`, so it is API
unification rather than a stronger speed result.

A recent Phase 5 diagnostic checkpoint adds opt-in Q2 CPU substep timers
behind `DEBS2015_Q2_CPU_DIAGNOSTICS=1`. Heap and checked Q2 now emit matching
`diag_q2_cpu_*` buckets for eviction, taxi lookup, previous-empty removal,
profit/empty path updates, rank updates, and top-10 extraction when the flag is
set. The 100k and 1M diagnostic RunBoth rows matched outputs. At 1M, checked
Q2 process time is `1327.500 ms` versus heap `1438.062 ms`, with recorded Q2
CPU substeps `1142.533 ms` versus heap `1246.509 ms`; Q2 operation counts
remain aligned. Treat this strictly as attribution evidence because the probes
insert `System.nanoTime()` calls in the hot path. The bounded same-operation
Q2 overhead concern is not currently reproduced; the next implementation focus
should be lower-overhead/richer checked rank APIs and stronger close
discipline.
A Scala-next checked Rift-region API slice has been reviewed and
merged into `feature/rift` at `79953ad8d`; its source branch was
`codex/safe-region-api-checked-slice` at `e8c3b961d`. The Q2 incremental
median branch was merged at `255522fbc`, and Stancu boundary evidence was
merged at `fecdb105e`. A docs/evidence-only coordinator note was then committed
at `ff37eecba`, and the fair JVM RunBoth cross-check was cherry-picked onto
current `feature/rift` at `346a5bd6e`. The Q2 incremental-median checkpoint
now has 100k and 1M 3-run medians recorded at `accf7a5f`; the Phase 7
hard-pattern compiler probes were then committed at `9e2a451d9`, followed by
the returned-function guard at `183469749`, the explicit `HeapRoot` handle at
`b748895cf`, and direct unrooted heap-object constructor-argument rejection at
`60d9fb33a`. Region-local alias propagation and heap-alias/heap-field-selection
rejection were then committed at `a0b653ef6`; explicit `{region}` constructor
field provenance was committed at `7b1a2c5f8`; checked region-array store
guards were committed at `8800e0613`; the explicit-owner checked
`ObjectBuffer` API was committed at `171431848`; checked guard narrowing plus
RunBoth region-backed latency buffers were committed at `a7632c1be`; Q2
rank/output attribution was committed at `84f3694a0`; Q2 cached top-10
extraction was committed at `1663befb3`; Q2 top-cache medians were recorded at
`2593b6574`; opt-in GC allocation attribution counters were committed at
`64b927b22`; checked mutable region list builders were committed at
`d397289e2`; checked `ObjectBuffer` owner methods were committed at
`69e0be59`; checked negative diagnostics were pinned at `7704265c`; checked
static heap metadata was committed at `bed92644`; checked `RegionBuffer` was
committed at `664c489e1`; the checked `RegionBuffer` matrix was committed at
`d86a68000`; checked Dataflow SELECT was committed at `69233e542`; checked
Dataflow AGGREGATE/JOIN was committed at `4ab5b898b`; checked
`RegionPriorityQueue` was committed at `07ad90177`; checked
`RegionIndexedPriorityQueue` was committed at `be42ea22c`; checked Q1
window-rank arenas were committed at `088fe2a59`; the reusable checked
`StreamBucketArena` API was committed at `cd9b86a0a`; checked
`StreamWindowIndexedRank` was committed at `4f310d21f`; checked
stream-window rank matrix evidence was committed at `d6fb94cd3`; Q2 CPU
substep diagnostics were committed at `de2134712`; and
`StreamWindowIndexedRank` auto cleanup was committed at `a70ce412e2`. The
entry-cleanup checkpoint was committed at `87fbc088a6`; the hash-keyed checked
rank queue was committed at `87c0d5cf3b`; and the long-key checked
stream-window rank API was committed at `7cde2473c2`. The
checked API is not a
complete compiler capture-checking implementation. The fork is ahead of
`origin/feature/rift` unless pushed.

Parent repo state for this update:

- `/Users/siyaoliu/rift` on `main`
- parent merge head before this coordinator cleanup: `56ae14c`
  (`Merge JVM native backend note`)
- merged parent handoff/evidence branches include checked API (`22619f5` and
  `7b2a653`), Q2 incremental median (`5250918`), Stancu boundary evidence
  (`fde1ac1`), and JVM-vs-native backend note (`56ae14c`).

Worker provenance notes:

- Q2 incremental median implementation was developed in Codex worktree
  `/Users/siyaoliu/.codex/worktrees/8d31/rift/scala-native-rift` on
  `codex/q2-median-rank-finish` at `26ba3a3b`.
- JVM RunBoth comparison implementation was developed on implementation branch
  `codex/jvm-debs-comparison` at `2ccb474d9` and cherry-picked onto current
  `feature/rift` as `346a5bd6e`.
- Benchmark-note work was developed in Codex memory-layer worktree
  `/Users/siyaoliu/.codex/worktrees/ba3c/rift`; its local ignored
  implementation clone validated notes at implementation commit `4be6f0a63`.

## 1. Project Objective

Rift is now a fork-first hybrid region-GC memory system for Scala Native. The target is not a standalone arena library beside Scala Native. The target is an in-tree Scala Native runtime/compiler experiment that combines:

- A fast region slab allocator and close/reset path inside the fork.
- Scala-facing region APIs, currently `RiftRegion` with `HPZone`, `Scoped`, and `Streaming` kind constants.
- Compiler-plugin support so `region.alloc(new T(...))` lowers into Rift allocation, analogous to SafeZone allocation.
- Safe APIs based on Scala 3 capture checking, planned but not yet implemented as a complete Phase 6 story.
- Region-friendly data layouts and stream operators, because layout/topology effects are first-order.
- A Lean model and proof plan, planned but not integrated in this fork yet.

The framing changed from "replace SafeZone with a standalone faster region runtime" to "build in the Scala Native fork, compare against both current SafeZone and an improved SafeZone baseline, and report runtime, topology, and layout effects separately."

Current evaluation standard:

- Compare against Immix heap, current SafeZone (`SAFEZONE_ROOTS_MODE=0`), improved SafeZone (`SAFEZONE_ROOTS_MODE=1`), and Rift where applicable.
- Use medians for headline claims.
- Mark single-run application measurements as provisional.
- Do not claim an application-level win unless the application path is actually using region memory for the operations that dominate allocation and GC pressure.
- Separate runtime-only wins from topology/layout wins and from DEBS application evidence.

## 2. Current Workspace / Repo State

Use this worktree for this active Rift session:

- `/Users/siyaoliu/rift/scala-native-rift`
- branch: `feature/rift`
- current implementation commit at this handoff update:
  `8690d06d3df6d3299e0c474064f2bac78c35e261c`
- `origin`: `git@github.com:641bill/scala-native.git`
- `upstream`: `https://github.com/scala-native/scala-native.git`

Other directories exist but should not be used for active implementation unless explicitly requested:

| Path | Purpose / status |
|---|---|
| `/Users/siyaoliu/rift/Claude_output` | Revised design pack: `DESIGN.md`, `ROADMAP.md`, `CODEX.md`, README, proof/capture templates. Read-only framing source. |
| `/Users/siyaoliu/rift/rift-bootstrap` | Old standalone bootstrap runtime and microbench. Useful provenance for Phase 1, not active architecture. |
| `/Users/siyaoliu/rift/scala-native` | Reference-only old investigation repo and git worktree metadata anchor for `scala-native-rift`. Do not continue Rift work there. |
| `/Users/siyaoliu/rift/scala-parallel-collections-amordo` | External/amordo parallel-collections worktree used for the `ZoneParVector` comparison. |
| `/Users/siyaoliu/rift/trip_data` and `/Users/siyaoliu/rift/trip_fare` | Downloaded DEBS/NYC taxi split datasets. |
| `/tmp/debs2015-month1-100000.csv` and `/tmp/debs2015-month1-1000000.csv` | Joined/sorted bounded DEBS inputs generated during Phase 5. |

Repo-layout quirks:

- The worktree is a Git worktree; `.git` is a file pointing at the real metadata directory. `project/Settings.scala` was patched so generated hooks use the actual git metadata directory rather than assuming `.git/` is a directory.
- The active branch contains committed Rift runtime/compiler/benchmark work,
  the Phase 5 input-boundary checkpoint, the reusable ranking backend, the Q2
  bounded cell-table checkpoint, the Q1 primitive route-table checkpoint, and
  the Q2 latest-empty taxi-table checkpoint, and the Q2 array-backed ranking
  checkpoint. The current implementation branch also has the checked API
  slice, the committed Q2 incremental median heap checkpoint, and the Stancu
  boundary evidence checkpoint.
- Always inspect `git status --short --untracked-files=all` and `git diff --stat`
  before continuing.

At the 2026-04-26 checked-API update, the implementation slice was merged into
`feature/rift` at `79953ad8d` after review. Recheck before continuing; if an
implementation worktree is dirty, inspect the diff rather than assuming it
belongs to a previous phase.

## 3. Revised Project Framing

The authoritative revised docs are in `/Users/siyaoliu/rift/Claude_output`:

- `/Users/siyaoliu/rift/Claude_output/DESIGN.md`
- `/Users/siyaoliu/rift/Claude_output/ROADMAP.md`
- `/Users/siyaoliu/rift/Claude_output/CODEX.md`

Main design changes:

- Standalone library story was rejected. The real costs and opportunities are inside Scala Native: SafeZone root bookkeeping, runtime allocation paths, GC/root interactions, and NIR lowering.
- Rift should live in a Scala Native fork and use the fork's runtime/compiler surface.
- Improved SafeZone is part of the baseline, not an irrelevant competitor. `SAFEZONE_ROOTS_MODE=1` materially changes SafeZone performance.
- Runtime work still matters. It is not acceptable to say "regions only win after changing data structures" if the allocator/runtime path is slow.
- Layout and topology matter enough that they must be measured separately.
- Closed-source Naiad/Broom artifacts cannot be reproduced exactly. Use workload methodology, not unavailable artifacts.

Baseline story changed:

- Old SafeZone headlines such as "SafeZone is 8x slower" are incomplete.
- In-fork reruns show current SafeZone can be pathological, but improved SafeZone can be near heap or substantially better than current SafeZone on the same workload.
- Rift has runtime-only wins on linked allocation-heavy structures, but not every cleaned/surrogate benchmark is a Rift win.
- Current DEBS evidence now includes bounded-sample elapsed/RSS wins and
  allocation-attribution diagnostics, but not a final application claim:
  SafeZone, controlled full-month performance, safe API boundaries, and broader
  provenance controls are still open.

## 4. Work Completed In This Session

### 4.1 Documentation And Framing

Completed and validated by file inspection:

- Revised design pack exists in `/Users/siyaoliu/rift/Claude_output`.
- `sandbox/PHASE0_BASELINES.md` records trusted Phase 0 medians and exact commands.
- `sandbox/PHASE4_LAYOUT.md`, `sandbox/PHASE4_TOPOLOGY.md`, and `sandbox/PHASE4_EXIT.md` record Phase 4 layout/topology findings.
- `sandbox/PIPELINE_PARCOLL_COMPARISON.md` records the amordo `ZoneParVector` comparison and labels the Rift pipeline as a raw-array surrogate.
- `bench/debs2015/README.md` and `bench/debs2015/RESULTS.md` record Phase 5 scaffold, commands, real-data runs, and instrumentation results.

Files touched:

- `sandbox/PHASE0_BASELINES.md`
- `sandbox/PHASE4_LAYOUT.md`
- `sandbox/PHASE4_TOPOLOGY.md`
- `sandbox/PHASE4_EXIT.md`
- `sandbox/PIPELINE_PARCOLL_COMPARISON.md`
- `bench/debs2015/README.md`
- `bench/debs2015/RESULTS.md`
- `docs/HANDOFF.md`
- `AGENTS.md`
- `CLAUDE.md`

Validation:

- Docs were reconstructed from checked-in/untracked notes, command outputs, and generated summary TSVs.

### 4.2 SafeZone Baseline Correction

Completed and partially validated:

- Added configurable SafeZone page size via `SAFEZONE_PAGE_SIZE`.
- Added SafeZone roots mode via `SAFEZONE_ROOTS_MODE`.
- Added SafeZone trace counters via `SAFEZONE_TRACE`.
- Changed root removal/reclaim behavior to support coalesced root removal and alternative root-registration strategies.
- Fixed `GC_Roots_RemoveByRange` so fully covered root ranges are handled correctly.

Files touched:

- `nativelib/src/main/resources/scala-native/gc/immix_commix/GCRoots.c`
- `nativelib/src/main/resources/scala-native/zone/MemoryPool.c`
- `nativelib/src/main/resources/scala-native/zone/MemoryPool.h`
- `nativelib/src/main/resources/scala-native/zone/LargeMemoryPool.c`
- `nativelib/src/main/resources/scala-native/zone/Zone.c`

Why it was done:

- The previous SafeZone investigation showed root bookkeeping was dominating some close paths.
- Phase 0 requires comparing against an improved SafeZone baseline, not only current SafeZone.

Validation:

- `sandbox/PHASE0_BASELINES.md` records 5-run medians.
- Notes state the first `SAFEZONE_ROOTS_MODE=1` GCBench attempt crashed until `GC_Roots_RemoveByRange` was fixed.
- Full Scala Native test suite has not been run.

### 4.3 Rift Runtime Integration

Completed and partially validated:

- Added in-tree Rift runtime under `nativelib/src/main/resources/scala-native/rift`.
- Runtime uses 32 KB slabs, mmap-backed allocation, TLS cache up to 8 slabs, and a global Treiber stack.
- Runtime supports region open/close/reset, raw allocation, managed object allocation, slab pool resident counters, and recently added operation counters/timers.
- Runtime fixes from Phase 4:
  - Fresh mmapped slabs are marked zero-filled.
  - Fresh zero-filled slabs skip redundant per-object `memset`.
  - Huge slabs avoid synchronous `MAP_POPULATE` and `MADV_HUGEPAGE`.
  - Reused regular slabs are zeroed once when acquired from TLS/global pool.
  - `reset` zeroes the retained first slab before reuse.
- Phase 6 evidence hardening moved Rift allocation-count stats out of the
  per-object atomic hot path. Regions now accumulate raw/object/slow allocation
  counts locally and flush them at reset/close. This preserved allocation
  counters while removing instrumentation overhead that distorted small-object
  Stancu/StreamFlex/Yak results.

Files touched:

- `nativelib/src/main/resources/scala-native/rift/RiftRuntime.c`
- `nativelib/src/main/resources/scala-native/rift/RiftRuntime.h`

Validation:

- `sbt "tests3/testOnly scala.scalanative.memory.RiftRegionTest"` is recorded as passing `5/5` in `sandbox/PHASE4_EXIT.md`.
- `zsh bench/debs2015/run_both_instrumented_matrix.sh` rebuilt and linked the native DEBS runner successfully after adding counters.
- Full C warnings build of this in-tree runtime has not been separately recorded.

Important caveat:

- The newest stats functions are defined in `RiftRuntime.c` and exposed through Scala externs, but they are not declared in `RiftRuntime.h` yet. The Scala Native build links successfully, but the C header is incomplete for external C users.

### 4.3.1 GC Heap Allocation Attribution

Completed and partially validated at implementation commit `64b927b22`:

- Added opt-in GC heap allocation attribution behind
  `SCALANATIVE_GC_ALLOC_STATS=1`.
- Added counters for heap allocation calls, rounded heap bytes requested, and
  nanoseconds spent in measured GC allocation entry points.
- Surfaced the counters through `scala.scalanative.runtime.GC`.
- Extended `Debs2015RunBoth` and the instrumented matrix summary to emit
  `gc_alloc_total`, `gc_alloc_bytes_total`, and `gc_alloc_time_ns`.

Files touched:

- `nativelib/src/main/resources/scala-native/gc/shared/jmx.c`
- `nativelib/src/main/resources/scala-native/gc/shared/jmx.h`
- `nativelib/src/main/resources/scala-native/gc/shared/ScalaNativeGC.h`
- `nativelib/src/main/resources/scala-native/gc/immix/ImmixGC.c`
- `nativelib/src/main/resources/scala-native/gc/commix/CommixGC.c`
- `nativelib/src/main/resources/scala-native/gc/boehm/gc.c`
- `nativelib/src/main/resources/scala-native/gc/none/gc.c`
- `nativelib/src/main/scala/scala/scalanative/runtime/GC.scala`
- `sandbox/src/main/scala-next/debs2015/Debs2015RunBoth.scala`
- `bench/debs2015/run_both_instrumented_matrix.sh`
- `bench/debs2015/RESULTS.md`

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" "set Compile / mainClass := Some(\"debs2015.Debs2015Smoke\")" run` passed.
- 100k and 1M `SCALANATIVE_GC_ALLOC_STATS=1` RunBoth instrumented matrices
  completed and matched heap/Rift outputs after stripping only measured latency.
- `git diff --check` passed before the implementation commit.

Interpretation:

- Collection time alone understates heap allocation cost. In the 1M attribution
  run, Rift reduces collection time by about `31 ms`, but measured heap
  allocation-call time by about `197-199 ms`.
- At 1M, Rift removes about `5.46M` GC heap allocation calls and about `224 MB`
  of rounded heap allocation requests by placing structured-lifetime objects
  in regions.
- Attribution mode times every allocation call and uses atomic counters, so use
  it as diagnosis, not as headline elapsed-time evidence.

### 4.4 Scala API Surface

Completed and partially validated:

- Added `RiftRegion` Scala facade.
- Added `RiftAllocator` extern bindings and compiler intrinsic marker.
- Added Scala 3 extension method `region.alloc(new T(...))`.
- Added Scala 2 no-op version-specific companion.
- Extended `SafeZone` trait to expose `isOpen`, `isClosed`, `checkOpen`, `close`, `handle`, and private `allocImpl`, so Rift can share the allocation-zone lowering shape.

Files touched:

- `nativelib/src/main/scala/scala/scalanative/memory/RiftRegion.scala`
- `nativelib/src/main/scala/scala/scalanative/runtime/RiftAllocator.scala`
- `nativelib/src/main/scala-3/scala/scalanative/memory/RiftRegionCompanionScalaVersionSpecific.scala`
- `nativelib/src/main/scala-2/scala/scalanative/memory/RiftRegionCompanionScalaVersionSpecific.scala`
- `nativelib/src/main/scala/scala/scalanative/memory/SafeZone.scala`

Validation:

- `RiftRegionTest` passes according to Phase 4 notes.
- GCBench/ListOfLists/Pipeline/DEBS harnesses exercised `region.alloc`.
- A first Scala-next `Scoped`/`Streaming` checked API slice exists and now has
  targeted compiler/runtime tests. It is not yet the complete safety story.

### 4.5 Compiler / Plugin Changes

Completed and partially validated:

- Added a `RIFT_ALLOC` primitive.
- Added `RuntimeRiftAllocator_allocate` definitions.
- Generalized `SafeZoneInstance` attachment to `AllocationZoneInstance`.
- Taught `NirGenExpr` to attach the Rift region handle to object/array allocation trees.

Files touched:

- `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirDefinitions.scala`
- `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirGenExpr.scala`
- `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirPrimitives.scala`

Validation:

- The benchmark and test harnesses compile/link through Scala Native.
- No dedicated compiler-plugin regression suite has been run.

### 4.6 Checked Rift Region API Slice

Completed in the Codex worktree clone on 2026-04-26, committed on implementation
branch `codex/safe-region-api-checked-slice` at `e8c3b961d`, then reviewed and
merged into `feature/rift` at `79953ad8d`:

- Added Scala-next replacements for `RiftRegion` and `RiftAllocator` that use
  `language.experimental.captureChecking`.
- Added `RiftRegion.scoped { region ?=> ... }`, which opens a `Scoped` runtime
  region, passes a `ScopedRegion^` capability to the body, and closes the
  region in `finally`.
- Added `RiftRegion.streaming { region ?=> ... }`, which opens a `Streaming`
  runtime region, passes a `StreamingRegion^` capability to the body, and closes
  it in `finally`.
- Added `RiftRegion.reset { region ?=> ... }` for streaming epochs. The region
  is reset in `finally` after the body succeeds or throws, and checked uses
  cannot return region-local values from the reset block.
- Added `RiftRegion.HeapRoot[T]` and `RiftRegion.root(value)` as the v1
  explicit root-handle path for safe region-to-GC metadata references. The live
  region object keeps heap roots in a GC-visible list and clears them on
  reset/close.
- In Scala-next, `RiftRegion.alloc(new T(...))` returns `T^{region}` for the
  implicit region, and inherited `region.alloc(new T(...))` returns `T^{this}`.
  `RiftRegion` overrides `allocImpl`, so the inherited checked member allocation
  still uses the Rift allocator path.
- Added `trustedOpen` as an explicit alias for `open`; the existing `open`,
  raw allocation, direct `reset()`, and `HPZone` mode remain trusted benchmark
  APIs, not safe APIs.

Tests added:

- `unit-tests/native/src/test/scala-next/scala/scala/scalanative/memory/RiftRegionCheckedTest.scala`
  positive runtime tests for ordinary region object graphs, non-escaping closure
  capture, checked streaming reset, and reset after an exception in an epoch.
- `nscplugin/src/test/scala-next/scala/RiftRegionCheckedCompilerTest.scala`
  compiler tests for positive object-graph/closure cases and negative return
  escape, closure-retains-region-handle-in-heap, heap-retains-region-value, and
  reset-epoch escape cases. The 2026-04-26 hard-pattern update added compiler
  probes for scoped for-loop allocation, nested scoped regions returning a pure
  value, a local higher-order consumer, inner-region escape rejection, returned
  function rejection, the explicit `HeapRoot` region-to-GC metadata path,
  direct unrooted heap-object constructor-argument rejection, region-local
  alias acceptance, heap-alias rejection, heap-field-selection rejection,
  explicit `{region}` constructor-field reuse, and plain `T^` field-reuse
  rejection. The container update added probes for region-owned arrays,
  region-array stores of region values, rejection of unrooted heap stores into
  region arrays, rejection of heap arrays stored in region objects, and
  region-array stores of `HeapRoot` handles. The checked collection update
  added `RiftRegion.ObjectBuffer` probes for storing region objects, rejecting
  direct heap objects, storing `HeapRoot` handles, rejecting inner-region
  values stored into an outer buffer, and rejecting buffer escape. The owner
  method update adds `region.append/get/length` probes for the same checked
  owner-token rule, including rejection of direct heap stores. The latest
  guard-boundary update adds a regression probe that trusted
  `RiftRegion.open(RiftRegion.HPZone)` allocation can still build linked
  benchmark objects without the checked mixed-reference guard. The newest
  checked-API update adds mutable local linked-list head probes: provenance is
  preserved across `null`, direct Rift allocations, and known region values,
  while heap-object assignment drops that provenance and is rejected before
  storage into region memory. The current checked-container update adds
  `RiftRegion.RegionBuffer` probes for growable region-backed buffers: storing
  region objects, storing `HeapRoot` handles, rejecting direct heap objects,
  and rejecting values from an inner scoped region stored into an outer buffer.
- `unit-tests/native/src/test/scala-next/scala/scala/scalanative/memory/RiftRegionCheckedTest.scala`
  now includes runtime smoke cases for a region object containing an explicit
  `HeapRoot` handle and region-owned arrays containing region values plus
  `HeapRoot` handles, plus `ObjectBuffer` smokes that store region objects
  and explicit `HeapRoot` handles through the owner-token API and through
  `region.append/get/length` owner methods. The latest
  runtime slice adds top-word-style buffered records with rooted metadata and
  GraphChi-style subinterval updates through a mutable region-owned linked
  update list. The current runtime slice adds a `RegionBuffer` smoke that
  grows from capacity one, stores region objects and explicit `HeapRoot`
  metadata, and reads them through owner-token methods.
- `unit-tests/native/src/test/scala-next/scala/scala/scalanative/memory/RiftRegionTest.scala`
  is a Scala-next replacement of the existing Rift runtime test with
  `captureChecking` enabled, so the old HPZone/runtime tests still run under the
  experimental checked API source set without changing the general Scala-3
  source.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project nativelib3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"` now passes `52/52`; this includes the earlier literature-shaped safe API probes plus raw child-streaming bucket-event graph acceptance, child-handle escape rejection, `ChildWindow` bucket-event graph acceptance, `ChildWindow` escape rejection, owner-token child-region widening, and direct user `ChildWindow.close()` rejection.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionTest scala.scalanative.memory.RiftRegionCheckedTest"` passed `18/18` after adding top-word, GraphChi, mutable linked-list, owner-token `ObjectBuffer` method, static heap-metadata, and growable `RegionBuffer` runtime smokes.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed after adding `CheckedRegionBufferMatrix`.
- `CHECKED_BUFFER_EPOCHS=2 CHECKED_BUFFER_RECORDS_PER_EPOCH=1000 CHECKED_BUFFER_BENCHMARK_RUNS=1 CHECKED_BUFFER_WARMUPS=0 CHECKED_BUFFER_OUTPUT_DIR=/tmp/checked-region-buffer-smoke zsh sandbox/run_checked_region_buffer_matrix.sh` native-linked and passed checksum equality for heap and `rift-checked`.
- `CHECKED_BUFFER_BUILD=0 CHECKED_BUFFER_OUTPUT_DIR=/tmp/checked-region-buffer-default zsh sandbox/run_checked_region_buffer_matrix.sh` recorded default local 3-run medians: heap `33.825 ms` with `7.611 ms` GC, `rift-checked` `28.654 ms` with `0.000 ms` GC and `0.301 ms` Rift op time. Treat this as focused checked-container evidence, not DEBS evidence.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed after adding Dataflow SELECT `rift-checked`.
- `DATAFLOW_OPERATOR=select DATAFLOW_EPOCHS=2 DATAFLOW_DOCS_PER_EPOCH=1000 DATAFLOW_BENCHMARK_RUNS=1 DATAFLOW_WARMUPS=0 DATAFLOW_OUTPUT_DIR=/tmp/dataflow-checked-select-smoke zsh sandbox/run_dataflow_region_instrumented_matrix.sh` native-linked and passed checksum equality across heap, SafeZone, trusted Rift, and checked Rift SELECT rows.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed after adding checked Dataflow AGGREGATE/JOIN.
- `DATAFLOW_EPOCHS=2 DATAFLOW_DOCS_PER_EPOCH=1000 DATAFLOW_BENCHMARK_RUNS=1 DATAFLOW_WARMUPS=0 DATAFLOW_OUTPUT_DIR=/tmp/dataflow-checked-all-smoke zsh sandbox/run_dataflow_region_instrumented_matrix.sh` native-linked and passed checksum equality across heap, SafeZone, trusted Rift, and checked Rift for SELECT, AGGREGATE, and JOIN.
- `DATAFLOW_BUILD=0 DATAFLOW_OUTPUT_DIR=/tmp/dataflow-checked-all-default zsh sandbox/run_dataflow_region_instrumented_matrix.sh` recorded default local medians where checked Rift is fastest in all three operators: SELECT `18.865 ms`, AGGREGATE `36.003 ms`, and JOIN `18.736 ms`, all with `0.000 ms` measured GC and low Rift op time.

Exact current safety boundary:

- Checked: region-local object and array allocation through the Scala-next
  `scoped`, `streaming`, and `reset` context-function boundaries; direct return
  of a region-local value; storing a region-local value in ordinary heap state;
  storing a closure that captures the region handle in ordinary heap state; and
  returning region-local values from a reset epoch. Direct function results
  from checked boundaries are rejected conservatively because returned closures
  may hide region-local captures. Region objects may refer to heap metadata
  through explicit `HeapRoot` handles retained by the live region object.
  Checked streaming can process region-owned arrays inside a reset epoch and
  rejects storing reset-epoch values into an outer streaming `ObjectBuffer`.
  The v1 checked API can express top-word-style buffers and GraphChi-style
  rooted durable heap metadata. It can also build mutable linked region-object
  lists through a local head when observed assignments preserve region
  provenance (`null`, direct Rift allocations, or known region values). A heap
  assignment to that head drops the provenance and is rejected if the value is
  later stored into region memory.
  Direct unrooted heap-object constructor arguments in checked Rift allocation
  lowering are rejected while region-to-region object graph references still
  compile. Simple local aliases of known region values are propagated; simple
  heap aliases and heap field selections are rejected. Static module
  singletons and immutable module vals can be stored as independently rooted
  heap metadata; mutable static vars are rejected. Stable constructor fields
  whose source types are explicitly captured by `{region}` can be reused in
  checked Rift allocations. Region-owned arrays can be used when reference
  elements are explicitly captured, for example `Array[T^{region}]^{region}`;
  array stores into known region arrays reject unrooted heap objects and accept
  region values or `HeapRoot` handles. `RiftRegion.ObjectBuffer` is the first
  checked higher-level container: the buffer object is heap control metadata
  captured by the owning region, its backing array is allocated in the region,
  and append/get/length operations require the owner token, for example
  `RiftRegion.append(region, buffer, value)` or `region.append(buffer, value)`.
  `RiftRegion.RegionBuffer` is the growable checked variant. It keeps the same
  owner-token rule, starts with a region-owned backing array, allocates larger
  backing arrays in the owner region on growth, and leaves old arrays to be
  reclaimed with the region rather than individually freed.
  This owner token is intentional in v1 because plain `buffer.append(value)`
  could not prove the same-region relation precisely enough with the current
  checker.
- Trusted/unsafe: `HPZone`, `open`/`trustedOpen`, raw pointer allocation,
  direct `region.reset()`, benchmark APIs, and all existing DEBS/dataflow
  harnesses using manual `RiftRegion.open`.
- Still open: direct returned functions are rejected even when they are pure;
  precise returned-closure support would require stronger capture evidence. The
  direct unrooted heap-reference rejection is a compiler-lowering guard for
  constructor arguments, not full alias analysis; plain `T^` selected fields,
  richer static-field provenance, and plain receiver-style containers still
  need a checked policy or trusted-only labeling. Mutable local linked-list heads are
  covered only by the current provenance rule, not full dataflow analysis for
  arbitrary mutable structures. Safe checked code should use `HeapRoot` for
  heap metadata until those cases are modeled.

### 4.7 Build-System Fix

Completed and validated for this worktree:

- `project/Settings.scala` now resolves the real git metadata directory when `.git` is a worktree pointer file.

Why it was done:

- The active worktree uses a `.git` file, and hook-generation code assumed `.git/hooks` existed.

Validation:

- sbt builds now proceed in this worktree.

### 4.8 Benchmark Harness Additions

Completed and validated by recorded benchmark runs:

- Added generic benchmark runner and configs.
- Added GCBench runtime matrix and topology matrix.
- Added ListOfLists runtime, flat, chunked, topology, and report-subset matrices.
- Added cleaned pipeline raw-array runtime matrix.
- Added Broom-style dataflow SELECT/AGGREGATE/JOIN methodology matrix.
- Added StreamFlex-style stream throughput/latency methodology matrix.
- Added Yak-style epoch/control-data methodology matrix, including runtime and
  promotion/escape proxies.
- Added Stancu-style transaction/accounting methodology matrix.
- Added scripts to run matrices with Immix/current SafeZone/improved SafeZone/Rift modes.
- Added DEBS Q1/Q2 implementation and sample/real-data runners.

Key files:

- `sandbox/src/main/scala-next/BenchmarkRunner.scala`
- `sandbox/src/main/scala-next/GCBenchRuntimeMatrix.scala`
- `sandbox/src/main/scala-next/GCBenchTopologyMatrix.scala`
- `sandbox/src/main/scala-next/ListOfListsRuntimeMatrix.scala`
- `sandbox/src/main/scala-next/ListOfListsFlatMatrix.scala`
- `sandbox/src/main/scala-next/ListOfListsChunkedMatrix.scala`
- `sandbox/src/main/scala-next/ListOfListsTopologyMatrix.scala`
- `sandbox/src/main/scala-next/PipelineRuntimeMatrix.scala`
- `sandbox/src/main/scala-next/DataflowRegionMatrix.scala`
- `sandbox/src/main/scala-next/StreamFlexRegionMatrix.scala`
- `sandbox/src/main/scala-next/YakRegionMatrix.scala`
- `sandbox/src/main/scala-next/StancuRegionMatrix.scala`
- `sandbox/run_gcbench_runtime_matrix.sh`
- `sandbox/run_gcbench_topology_matrix.sh`
- `sandbox/run_listoflists_runtime_matrix.sh`
- `sandbox/run_listoflists_flat_matrix.sh`
- `sandbox/run_listoflists_chunked_matrix.sh`
- `sandbox/run_listoflists_topology_matrix.sh`
- `sandbox/run_listoflists_topology_report_subset.sh`
- `sandbox/run_pipeline_runtime_matrix.sh`
- `sandbox/run_dataflow_region_matrix.sh`
- `sandbox/run_streamflex_region_instrumented_matrix.sh`
- `sandbox/run_yak_region_instrumented_matrix.sh`
- `sandbox/run_stancu_region_instrumented_matrix.sh`

Validation:

- Results are recorded in `sandbox/PHASE0_BASELINES.md`, `sandbox/PHASE4_LAYOUT.md`, `sandbox/PHASE4_TOPOLOGY.md`, `sandbox/PHASE4_EXIT.md`, and `sandbox/PIPELINE_PARCOLL_COMPARISON.md`.
- The dataflow matrix compiles and has smoke plus local 3-run median results in
  `sandbox/DATAFLOW_REGION_MATRIX.md`. It is methodology reproduction evidence,
  not exact Naiad/Broom artifact reproduction.
- The StreamFlex matrix compiles and has smoke, default 3-run medians, and one
  allocation-pressure 3-run median in `sandbox/STREAMFLEX_REGION_MATRIX.md`.
  It is methodology reproduction evidence, not exact StreamFlex/Ovm artifact
  reproduction.
- The Yak matrix compiles and has smoke, default 3-run medians,
  epoch-pressure 3-run medians, grouped-sort, top-word/filter, and
  GraphChi-style subinterval medians, runtime-proxy medians, and
  promotion/escape proxy medians in
  `sandbox/YAK_REGION_MATRIX.md`. It is methodology
  reproduction evidence, not exact Yak/Hyracks/Hadoop/GraphChi artifact
  reproduction.
- The Stancu matrix compiles and has smoke, default 3-run medians, and one
  transaction-pressure 3-run median in `sandbox/STANCU_REGION_MATRIX.md`. It is
  methodology/accounting evidence, not exact SPECjbb2005 or Stancu static
  analysis reproduction. A 2026-04-26 boundary-sensitivity rerun at 200k
  transactions now records `STANCU_TX_PER_REGION=1`, `64`, and `512`, confirming
  that the weak per-transaction result was a boundary-granularity problem.

### 4.9 DEBS 2015 Work

Completed and partially validated:

- Implemented DEBS parser/grid/Q1/Q2 scaffold.
- Added heap and Rift-bucket Q1 modes.
- Added heap and Rift-window Q2 modes over the same bucketed algorithm.
- Added RunBoth runner for simultaneous Q1 and Q2.
- Added sample matrices and real-data join script.
- Added direct-native instrumented matrix with RSS, GC stats, and Rift op counters.

Files:

- `bench/debs2015/*`
- `sandbox/src/main/scala-next/debs2015/*`

Important bug fixes:

- Q1 originally stored heap `Route` objects in Rift region entries. That is unsafe because Rift regions are not GC-scanned; a heap object reachable only from region memory can be collected. Q1 now stores packed `Long` route keys in region entries.
- Q1 and Q2 originally did full rescans/sorts per event. 100k heap run took `246360.864 ms` (`405.909 events/s`). Incremental ranking with `TreeSet` reduced 100k runs to about `2.0-2.1 s`.
- `join_nyc_taxi_sample.sh` was adjusted to handle bounded-read pipeline behavior and sort by dropoff timestamp.

Validation:

- 10k, 100k, and 1M RunBoth matrices matched heap/Rift outputs after stripping only final measured-latency column.
- 100k and 1M instrumented matrices also matched.

Current limitation:

- Q1/Q2 window entries, Q2 active profit values, the RunBoth input byte
  buffer, Q1/Q2 ranking objects, top-k result arrays, and Q2 incremental
  median heap state now have heap/Rift allocation-placement boundaries in the
  current worktree.
- The resettable ranking/result experiment was not a performance win and was
  replaced by reusable top-k arrays. Do not reintroduce per-event resettable
  snapshot regions.
- Q2 per-cell maps, Q1 route maps, Q1 ranking state, Q2 latest-empty taxi
  state, Q2 ranking index arrays, Q2 taxi-id metadata, and RunBoth output
  snapshots now have shared heap/Rift structures with region-backed
  arrays/entries in Rift modes.
- Latency backing arrays are now region-backed in Rift modes, with final
  metrics arrays copied out before region close. SafeZone modes, broader Commix controls,
  controlled full-month performance, Q2 rank-maintenance cost,
  output-phase variance, and safe API boundaries remain open.
- Therefore Rift DEBS still depends on GC and does not provide final
  application-level evidence, but the latest bounded-sample rows include Q2
  top-cache medians plus allocation-attribution diagnostics that show lower
  heap allocation calls/bytes/time in Rift modes.

## 5. Benchmark And Validation Summary

Common environment for fork-local runs:

- `ENABLE_EXPERIMENTAL_COMPILER=1`
- `JAVA_HOME="$(cs java-home --jvm temurin:17)"`
- `PATH="$JAVA_HOME/bin:$PATH"`
- Scala Native project: `sandbox3_next`
- Head commit for recorded result packs: `ddbba577aecd4c0adc741cbf7085ee93548c46b4`

### Phase 1 Bootstrap Microbench

Source: `/Users/siyaoliu/rift/rift-bootstrap/bench/microbench/results.md`

Command:

```sh
cd /Users/siyaoliu/rift/rift-bootstrap
make -C native clean bench
./bench/microbench/microbench
```

| Metric | malloc/free | Rift HPZone |
|---|---:|---:|
| per-allocation p50 | 11.3 ns/alloc | 2.1 ns/alloc |
| per-allocation p99 | 13.9 ns/alloc | 2.9 ns/alloc |
| close/free p50 for 100000 allocations | 1210000 ns | 3000 ns |
| close/free p99 for 100000 allocations | 1507000 ns | 11000 ns |

Status: completed and validated in the standalone bootstrap tree, not the active fork.

### GCBench Runtime Matrix

Source: `sandbox/PHASE0_BASELINES.md`

Command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
GCBENCH_BENCHMARK_RUNS=5 zsh sandbox/run_gcbench_runtime_matrix.sh
```

Config:

- stretch depth `18`
- long-lived depth `16`
- array size `500000`
- min depth `4`
- max depth `16`
- depth step `2`
- batch size `1`
- runs `5`

| Mode | Key env | Median ms | Status |
|---|---|---:|---|
| Immix heap | `-` | 203.514 | trusted Phase 0 median |
| current SafeZone | `SAFEZONE_ROOTS_MODE=0` | 684.517 | trusted Phase 0 median |
| improved SafeZone | `SAFEZONE_ROOTS_MODE=1` | 223.770 | trusted Phase 0 median |
| Rift HPZone | `-` | 161.641 | trusted Phase 0 median |

Interpretation:

- Runtime-only Rift is faster than heap and both SafeZone baselines on this GCBench harness.
- Improved SafeZone closes most of the current SafeZone gap.

### ListOfLists Runtime Matrix

Source: `sandbox/PHASE0_BASELINES.md`

Command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
zsh sandbox/run_listoflists_runtime_matrix.sh
```

Workload:

- `n=3000`
- `structures=40`
- linked outer and inner nodes
- each inner node points at a separate `BasicObject`
- runs `5`

| Mode | Key env | Median ms | Status |
|---|---|---:|---|
| Immix heap | `-` | 15085.511 | trusted Phase 0 median |
| current SafeZone | `SAFEZONE_ROOTS_MODE=0` | 138171.998 | trusted Phase 0 median |
| improved SafeZone | `SAFEZONE_ROOTS_MODE=1` | 10132.854 | trusted Phase 0 median |
| Rift HPZone | `-` | 6951.331 | trusted Phase 0 median |

Interpretation:

- The linked runtime-only story is strong: Rift beats heap and improved SafeZone.
- Current SafeZone remains pathological on this shape.

### GCBench Topology Rerun

Source: `sandbox/PHASE0_BASELINES.md`

Command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
zsh sandbox/run_gcbench_topology_matrix.sh
```

Config:

- `SAFEZONE_PAGE_SIZE=4096`
- `SAFEZONE_BATCH_SIZE=1`
- runs `5`

Definitions:

- topology A: long-lived tree on GC heap, short-lived trees in inner SafeZones.
- topology B: long-lived tree in outer SafeZone, short-lived trees in inner SafeZones.

| Mode | Key env | Median ms |
|---|---|---:|
| heap baseline | `SAFEZONE_PAGE_SIZE=4096 SAFEZONE_BATCH_SIZE=1` | 213.082 |
| current SafeZone topology A | `SAFEZONE_ROOTS_MODE=0 SAFEZONE_PAGE_SIZE=4096 SAFEZONE_BATCH_SIZE=1` | 236.542 |
| current SafeZone topology B | `SAFEZONE_ROOTS_MODE=0 SAFEZONE_PAGE_SIZE=4096 SAFEZONE_BATCH_SIZE=1` | 635.247 |
| improved SafeZone topology A | `SAFEZONE_ROOTS_MODE=1 SAFEZONE_PAGE_SIZE=4096 SAFEZONE_BATCH_SIZE=1` | 211.319 |
| improved SafeZone topology B | `SAFEZONE_ROOTS_MODE=1 SAFEZONE_PAGE_SIZE=4096 SAFEZONE_BATCH_SIZE=1` | 436.749 |

Interpretation:

- Topology changes conclusions. Topology A can be near heap parity even for current SafeZone, while topology B remains much slower.
- Improved SafeZone topology A is near heap.

### Phase 4 Layout Study

Source: `sandbox/PHASE4_LAYOUT.md`

Commands:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
LISTBENCH_CHUNK_SIZE=32 LISTBENCH_BENCHMARK_RUNS=5 zsh sandbox/run_listoflists_chunked_matrix.sh
LISTBENCH_BENCHMARK_RUNS=5 zsh sandbox/run_listoflists_flat_matrix.sh
```

| Mode | Linked median ms | Chunked median ms | Flat median ms |
|---|---:|---:|---:|
| Immix heap | 15260.875 | 2636.480 | 1766.295 |
| current SafeZone | 136016.922 | 4835.904 | 1735.453 |
| improved SafeZone | 9824.936 | 2369.108 | 1743.161 |
| Rift HPZone | 7278.150 | 2463.674 | 1515.091 |

Follow-up Rift-only checks after regular-slab zeroing:

| Layout | Previous Rift median ms | Follow-up Rift median ms |
|---|---:|---:|
| Linked | 7278.150 | 6638.949 |
| Chunked | 2463.674 | 2390.390 |

Interpretation:

- Layout is a first-order effect.
- Rift remains strong on linked one-region layout.
- Rift flat cliff was a runtime bug and is fixed.
- Rift does not yet clearly beat improved SafeZone on the first chunked layout.

### Phase 4 Topology Sweep

Source: `sandbox/PHASE4_TOPOLOGY.md`

Report-scale command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
LISTBENCH_BENCHMARK_RUNS=3 zsh sandbox/run_listoflists_topology_report_subset.sh
```

| Mode | Topology | Median ms |
|---|---|---:|
| Immix heap | full heap graph | 14755.580 |
| current SafeZone | one-region | 136016.922 |
| current SafeZone | nested | 10289.097 |
| current SafeZone | mixed rooted heap-values | 55554.702 |
| improved SafeZone | one-region | 9767.048 |
| improved SafeZone | nested | 9929.699 |
| improved SafeZone | mixed rooted heap-values | 9877.914 |
| Rift HPZone | one-region | 7256.426 |
| Rift HPZone | nested | 7314.201 |
| Rift HPZone | mixed rooted heap-values | 11695.748 |

Interpretation:

- Rift one-region/nested are fastest in this linked topology harness.
- Current SafeZone nested mostly fixes the old root-bookkeeping pathology.
- Improved SafeZone makes topology much less important for that runtime.
- Rooted mixed topology is not a Rift win.

### Pipeline Benchmark Status

Source: `sandbox/PHASE0_BASELINES.md` and `sandbox/PIPELINE_PARCOLL_COMPARISON.md`

Pipeline surrogate command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
zsh sandbox/run_pipeline_runtime_matrix.sh
```

Config in Phase 0:

- `PIPELINE_SIZE=2000000`
- `PIPELINE_WORKERS=4`
- `PIPELINE_WARMUPS=1`
- runs `5`

| Mode | Median ms |
|---|---:|
| heap baseline | 4.924 |
| current SafeZone pipeline | 5.344 |
| improved SafeZone pipeline | 5.055 |
| Rift HPZone pipeline | 5.089 |

Provenance caveat:

- No tracked original pipeline benchmark survived in the fork history.
- This is a cleaned raw-array surrogate derived from a surviving local scaffold.
- It fixes a checksum-capture artifact by using per-worker primitive sums.
- It is not a parallel-collections API comparison.

Amordo parallel-collections comparison:

```sh
cd /Users/siyaoliu/rift/scala-parallel-collections-amordo
JAVA_HOME="$(cs java-home --jvm temurin:17)" PATH="$JAVA_HOME/bin:$PATH" \
  sbt "junitNative/testOnly scala.collection.parallel.immutable.BroomPipelineBenchmark"
```

| Mode | Median ms |
|---|---:|
| ZoneParVector explicit stage release | 55.07 |
| on-heap ParVector | 30.75 |
| ZoneParVector region per stage | 30.36 |

Rift raw-array 100k comparison:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
PIPELINE_SIZE=100000 PIPELINE_KEYS=64 PIPELINE_BENCHMARK_RUNS=5 PIPELINE_WARMUPS=1 \
  zsh sandbox/run_pipeline_runtime_matrix.sh
```

| Mode | Median ms |
|---|---:|
| Immix heap raw arrays | 1.845 |
| current SafeZone raw arrays | 1.976 |
| improved SafeZone raw arrays | 1.907 |
| Rift HPZone raw arrays | 2.502 |
| Rift Streaming raw arrays | 2.652 |

Interpretation:

- Raw-array Rift is much faster than `ZoneParVector` because it is a lower-level kernel, not because it replaced the collection API.
- Within the raw-array surrogate, Rift is not a win at 100k.
- Fair next comparison requires a Rift-backed collection with the same API shape as `ParVector`/`ZoneParVector`.

### Broom-Style Dataflow Methodology Matrix

Sources:

- `docs/LITERATURE_BENCHMARK_CONTRACT.md`
- `sandbox/DATAFLOW_REGION_MATRIX.md`
- `evidence/DATAFLOW_REGION_MATRIX.md`

Compile/check command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
```

Smoke command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
DATAFLOW_EPOCHS=2 DATAFLOW_DOCS_PER_EPOCH=1000 DATAFLOW_BENCHMARK_RUNS=1 DATAFLOW_WARMUPS=0 \
  zsh sandbox/run_dataflow_region_matrix.sh
```

Local median command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
DATAFLOW_BENCHMARK_RUNS=3 DATAFLOW_WARMUPS=1 \
  zsh sandbox/run_dataflow_region_matrix.sh
```

Native-only instrumented median command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
DATAFLOW_BENCHMARK_RUNS=3 DATAFLOW_WARMUPS=1 \
DATAFLOW_OUTPUT_DIR=/tmp/dataflow-region-instrumented-fixed \
  zsh sandbox/run_dataflow_region_instrumented_matrix.sh
```

Local median configuration:

- `DATAFLOW_EPOCHS=10`
- `DATAFLOW_DOCS_PER_EPOCH=100000`
- `DATAFLOW_AUTHORS_PER_EPOCH=20`
- `DATAFLOW_KEY_SPACE=65536`
- `DATAFLOW_AUTHOR_KEY_SPACE=256`
- `DATAFLOW_SELECT_MODULO=8`
- runs `3`, warmups `1`

| Operator | Mode | Median elapsed ms | Median GC ms | Median Rift op ms | Median region objects |
|---|---|---:|---:|---:|---:|
| SELECT | heap | 28.398 | 7.131 | 0.000 | 0 |
| SELECT | current SafeZone | 26.413 | 0.000 | 0.000 | 0 |
| SELECT | improved SafeZone | 23.600 | 0.000 | 0.000 | 0 |
| SELECT | Rift HPZone | 21.614 | 0.000 | 0.051 | 1124990 |
| SELECT | Rift Streaming | 24.445 | 0.000 | 0.046 | 1124990 |
| AGGREGATE | heap | 59.906 | 19.908 | 0.000 | 0 |
| AGGREGATE | current SafeZone | 51.568 | 0.000 | 0.000 | 0 |
| AGGREGATE | improved SafeZone | 43.216 | 0.000 | 0.000 | 0 |
| AGGREGATE | Rift HPZone | 41.870 | 0.000 | 0.273 | 1627152 |
| AGGREGATE | Rift Streaming | 48.003 | 0.000 | 0.320 | 1627152 |
| JOIN | heap | 28.347 | 7.415 | 0.000 | 0 |
| JOIN | current SafeZone | 27.032 | 0.000 | 0.000 | 0 |
| JOIN | improved SafeZone | 24.079 | 0.000 | 0.000 | 0 |
| JOIN | Rift HPZone | 21.481 | 0.000 | 0.075 | 1078279 |
| JOIN | Rift Streaming | 36.120 | 0.000 | 0.046 | 1078279 |

Peak RSS by mode for the same native-only run:

| Mode | Peak RSS bytes |
|---|---:|
| heap | 40042496 |
| current SafeZone | 47038464 |
| improved SafeZone | 47005696 |
| Rift HPZone | 46891008 |
| Rift Streaming | 46874624 |

Interpretation:

- This is the first current benchmark harness that directly follows the Broom
  operator methodology: epoch-local SELECT, AGGREGATE, and JOIN data objects
  are allocated on heap or in regions with the same logical program.
- It uses ordinary Scala object graphs in regions: document records, selected
  outputs, aggregate entries, author entries, join outputs, and table arrays.
- The local controlled workload shows material GC removal because the data
  objects are intentionally epoch-local and allocation-heavy.
- Improved SafeZone is a strong baseline in this harness. In the post-counter
  rerun, Rift HPZone is fastest on all three operators, but Rift Streaming is
  inconsistent and regressed on JOIN.
- Rift operation time remains small in this harness.

Caveats:

- This is not an exact Naiad/Broom reproduction. The original artifact is not
  available in the workspace.
- The local median size is smaller than the Broom paper's 40-epoch,
  500k-600k document-per-epoch vertex experiment.
- The benchmark currently uses trusted `HPZone`/`Streaming` APIs, not the
  future safe capture-checked API.

Provisional Broom-scale single-run command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
DATAFLOW_EPOCHS=40 DATAFLOW_DOCS_PER_EPOCH=500000 DATAFLOW_BENCHMARK_RUNS=1 DATAFLOW_WARMUPS=0 \
  zsh sandbox/run_dataflow_region_matrix.sh

DATAFLOW_BUILD=0 DATAFLOW_EPOCHS=40 DATAFLOW_DOCS_PER_EPOCH=500000 \
DATAFLOW_BENCHMARK_RUNS=1 DATAFLOW_WARMUPS=0 \
DATAFLOW_OUTPUT_DIR=/tmp/dataflow-region-instrumented-broom-scale \
  zsh sandbox/run_dataflow_region_instrumented_matrix.sh
```

| Operator | Mode | Elapsed ms | GC ms | Rift op ms | Region objects |
|---|---|---:|---:|---:|---:|
| SELECT | heap | 623.761 | 207.058 | 0.000 | 0 |
| SELECT | current SafeZone | 766.753 | 0.000 | 0.000 | 0 |
| SELECT | improved SafeZone | 463.303 | 0.000 | 0.000 | 0 |
| SELECT | Rift HPZone | 451.041 | 0.000 | 2.109 | 22500066 |
| SELECT | Rift Streaming | 452.422 | 0.000 | 1.848 | 22500066 |
| AGGREGATE | heap | 859.726 | 269.652 | 0.000 | 0 |
| AGGREGATE | current SafeZone | 924.995 | 0.000 | 0.000 | 0 |
| AGGREGATE | improved SafeZone | 618.133 | 0.000 | 0.000 | 0 |
| AGGREGATE | Rift HPZone | 620.342 | 0.000 | 2.048 | 22621480 |
| AGGREGATE | Rift Streaming | 630.151 | 0.000 | 2.112 | 22621480 |
| JOIN | heap | 602.540 | 184.929 | 0.000 | 0 |
| JOIN | current SafeZone | 748.152 | 0.000 | 0.000 | 0 |
| JOIN | improved SafeZone | 470.770 | 0.000 | 0.000 | 0 |
| JOIN | Rift HPZone | 447.803 | 0.000 | 0.968 | 21563289 |
| JOIN | Rift Streaming | 448.956 | 0.000 | 0.867 | 21563289 |

Peak RSS by mode for the same native-only run:

| Mode | Peak RSS bytes |
|---|---:|
| heap | 290504704 |
| current SafeZone | 226590720 |
| improved SafeZone | 226607104 |
| Rift HPZone | 226361344 |
| Rift Streaming | 226344960 |

Interpretation:

- This single run uses the paper-scale input shape of 40 epochs and 500k
  documents per epoch, but it is still a local synthetic harness.
- It is useful as a stress/provenance checkpoint because heap GC time becomes
  hundreds of milliseconds while Rift GC remains zero, but it is not a
  headline median.
- Improved SafeZone is a strong baseline here too; Rift is slightly faster on
  SELECT and JOIN in this single run, while improved SafeZone is slightly
  faster on AGGREGATE.

### StreamFlex-Style Throughput/Latency Matrix

Sources:

- `docs/LITERATURE_BENCHMARK_CONTRACT.md`
- `sandbox/STREAMFLEX_REGION_MATRIX.md`
- `evidence/STREAMFLEX_REGION_MATRIX.md`

Compile/check command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
```

Smoke command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
STREAMFLEX_EVENTS=2000 STREAMFLEX_LATENCY_EVENTS=500 STREAMFLEX_BENCHMARK_RUNS=1 STREAMFLEX_WARMUPS=0 \
  zsh sandbox/run_streamflex_region_instrumented_matrix.sh
```

Default native-only median command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
STREAMFLEX_BUILD=0 STREAMFLEX_BENCHMARK_RUNS=3 STREAMFLEX_WARMUPS=1 \
STREAMFLEX_OUTPUT_DIR=/tmp/streamflex-region-instrumented \
  zsh sandbox/run_streamflex_region_instrumented_matrix.sh
```

Pressure native-only median command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
STREAMFLEX_BENCHMARK_RUNS=3 STREAMFLEX_WARMUPS=1 \
STREAMFLEX_EVENTS=1000000 STREAMFLEX_OBJECTS_PER_EVENT=8 \
STREAMFLEX_LATENCY_EVENTS=50000 STREAMFLEX_LATENCY_OBJECTS_PER_EVENT=64 \
STREAMFLEX_PERIOD_NS=80000 \
STREAMFLEX_OUTPUT_DIR=/tmp/streamflex-region-pressure-fixed \
  zsh sandbox/run_streamflex_region_instrumented_matrix.sh
```

Default local median configuration:

- `STREAMFLEX_EVENTS=200000`
- `STREAMFLEX_OBJECTS_PER_EVENT=4`
- `STREAMFLEX_LATENCY_EVENTS=10000`
- `STREAMFLEX_LATENCY_OBJECTS_PER_EVENT=16`
- `STREAMFLEX_PERIOD_NS=80000`
- runs `3`, warmups `1`

| Workload | Mode | Median elapsed ms | Median GC ms | Median Rift op ms | Deadline misses |
|---|---|---:|---:|---:|---:|
| throughput | heap | 41.444 | 8.944 | 0.000 |  |
| throughput | current SafeZone | 41.263 | 0.000 | 0.000 |  |
| throughput | improved SafeZone | 47.436 | 0.000 | 0.000 |  |
| throughput | Rift HPZone | 37.638 | 0.000 | 0.131 |  |
| throughput | Rift Streaming | 37.683 | 0.000 | 0.082 |  |
| latency | heap | 9.982 | 1.218 | 0.000 | 4 |
| latency | current SafeZone | 11.478 | 0.000 | 0.000 | 0 |
| latency | improved SafeZone | 11.827 | 0.000 | 0.000 | 0 |
| latency | Rift HPZone | 10.340 | 0.000 | 0.526 | 0 |
| latency | Rift Streaming | 10.334 | 0.000 | 0.172 | 0 |

Pressure local median configuration:

- `STREAMFLEX_EVENTS=1000000`
- `STREAMFLEX_OBJECTS_PER_EVENT=8`
- `STREAMFLEX_LATENCY_EVENTS=50000`
- `STREAMFLEX_LATENCY_OBJECTS_PER_EVENT=64`
- `STREAMFLEX_PERIOD_NS=80000`
- runs `3`, warmups `1`

| Workload | Mode | Median elapsed ms | Median GC ms | Median Rift op ms | p99 ns | p999 ns | Max ns | Deadline misses |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| throughput | heap | 634.472 | 141.804 | 0.000 |  |  |  |  |
| throughput | current SafeZone | 409.749 | 0.000 | 0.000 |  |  |  |  |
| throughput | improved SafeZone | 412.827 | 0.000 | 0.000 |  |  |  |  |
| throughput | Rift HPZone | 331.740 | 0.000 | 1.237 |  |  |  |  |
| throughput | Rift Streaming | 329.896 | 0.000 | 0.835 |  |  |  |  |
| latency | heap | 169.331 | 29.931 | 0.000 | 2792 | 327625 | 467958 | 89 |
| latency | current SafeZone | 174.989 | 0.757 | 0.000 | 3542 | 8166 | 299042 | 1 |
| latency | improved SafeZone | 181.317 | 0.827 | 0.000 | 4250 | 13625 | 310084 | 6 |
| latency | Rift HPZone | 143.955 | 0.525 | 2.927 | 3250 | 3625 | 247500 | 1 |
| latency | Rift Streaming | 157.792 | 0.496 | 1.106 | 3541 | 6917 | 28209 | 0 |

Interpretation:

- This is the first local StreamFlex-style harness for Rift: ordinary Scala
  packet/event objects are allocated on heap, in SafeZone, or in Rift regions
  with the same logical pipeline.
- The pressure run reproduces the relevant axis from StreamFlex rather than the
  exact artifact: heap has large p999/max latency and `89` deadline misses,
  while Rift Streaming has zero misses and low region-op time.
- SafeZone also removes almost all GC time, but in the pressure rerun it keeps
  occasional latency misses and is slower than Rift on throughput. HPZone has
  one deadline miss in the fixed rerun, so keep latency claims mode-specific.
- Streaming has lower region-op time than HPZone in latency mode because it
  opens once and resets across events.

Caveats:

- This is not an exact StreamFlex/Ovm reproduction. It does not run StreamIt
  BeamFormer/FilterBank or model full scheduler/queuing delay.
- The benchmark currently uses trusted `HPZone`/`Streaming` APIs, not the
  future safe capture-checked API.

### Yak-Style Epoch/Control-Data Matrix

Sources:

- `docs/LITERATURE_BENCHMARK_CONTRACT.md`
- `sandbox/YAK_REGION_MATRIX.md`
- `evidence/YAK_REGION_MATRIX.md`

Compile/check command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
```

Smoke command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
YAK_EPOCHS=2 YAK_RECORDS_PER_EPOCH=1000 YAK_MESSAGES_PER_EPOCH=1000 \
YAK_BENCHMARK_RUNS=1 YAK_WARMUPS=0 \
  zsh sandbox/run_yak_region_instrumented_matrix.sh
```

Default native-only median command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
YAK_BUILD=0 YAK_BENCHMARK_RUNS=3 YAK_WARMUPS=1 \
YAK_OUTPUT_DIR=/tmp/yak-region-instrumented \
  zsh sandbox/run_yak_region_instrumented_matrix.sh
```

Pressure native-only median command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
YAK_BENCHMARK_RUNS=3 YAK_WARMUPS=1 \
YAK_EPOCHS=40 YAK_RECORDS_PER_EPOCH=250000 YAK_MESSAGES_PER_EPOCH=250000 \
YAK_OUTPUT_DIR=/tmp/yak-region-pressure-fixed \
  zsh sandbox/run_yak_region_instrumented_matrix.sh
```

Promotion/escape pressure command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
YAK_BUILD=0 YAK_WORKLOAD=promotion YAK_BENCHMARK_RUNS=3 YAK_WARMUPS=1 \
YAK_EPOCHS=40 YAK_RECORDS_PER_EPOCH=250000 YAK_ESCAPE_MODULO=1000 \
YAK_OUTPUT_DIR=/tmp/yak-promotion-pressure \
  zsh sandbox/run_yak_region_instrumented_matrix.sh
```

Grouped-sort pressure command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
YAK_BUILD=0 YAK_WORKLOAD=sort YAK_BENCHMARK_RUNS=3 YAK_WARMUPS=1 \
YAK_EPOCHS=10 YAK_SORT_RECORDS_PER_EPOCH=100000 \
YAK_OUTPUT_DIR=/tmp/yak-sort-pressure \
  zsh sandbox/run_yak_region_instrumented_matrix.sh
```

Top-word/filter pressure command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
YAK_BUILD=0 YAK_WORKLOAD=topword YAK_BENCHMARK_RUNS=3 YAK_WARMUPS=1 \
YAK_EPOCHS=40 YAK_RECORDS_PER_EPOCH=250000 \
YAK_OUTPUT_DIR=/tmp/yak-topword-pressure \
  zsh sandbox/run_yak_region_instrumented_matrix.sh
```

GraphChi-style subinterval pressure command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
YAK_BUILD=0 YAK_WORKLOAD=graphchi YAK_BENCHMARK_RUNS=3 YAK_WARMUPS=1 \
YAK_EPOCHS=40 YAK_GRAPHCHI_SUBINTERVALS=16 \
YAK_GRAPHCHI_EDGES_PER_SUBINTERVAL=15625 \
YAK_OUTPUT_DIR=/tmp/yak-graphchi-pressure \
  zsh sandbox/run_yak_region_instrumented_matrix.sh
```

Default local median configuration:

- `YAK_EPOCHS=20`
- `YAK_RECORDS_PER_EPOCH=100000`
- `YAK_MESSAGES_PER_EPOCH=100000`
- runs `3`, warmups `1`

| Workload | Mode | Median elapsed ms | Median GC ms | Median Rift op ms | Logical data objects |
|---|---|---:|---:|---:|---:|
| wordcount | heap | 51.961 | 12.062 | 0.000 | 2000000 |
| wordcount | current SafeZone | 41.143 | 0.000 | 0.000 | 2000000 |
| wordcount | improved SafeZone | 40.005 | 0.000 | 0.000 | 2000000 |
| wordcount | Rift HPZone | 42.075 | 0.000 | 0.053 | 2000000 |
| wordcount | Rift Streaming | 41.873 | 0.000 | 0.053 | 2000000 |
| graphstep | heap | 56.235 | 9.283 | 0.000 | 2000000 |
| graphstep | current SafeZone | 47.417 | 0.000 | 0.000 | 2000000 |
| graphstep | improved SafeZone | 46.859 | 0.000 | 0.000 | 2000000 |
| graphstep | Rift HPZone | 48.126 | 0.000 | 0.077 | 2000000 |
| graphstep | Rift Streaming | 46.909 | 0.000 | 0.072 | 2000000 |

Pressure local median configuration:

- `YAK_EPOCHS=40`
- `YAK_RECORDS_PER_EPOCH=250000`
- `YAK_MESSAGES_PER_EPOCH=250000`
- runs `3`, warmups `1`

| Workload | Mode | Median elapsed ms | Median GC ms | Median Rift op ms | Logical data objects |
|---|---|---:|---:|---:|---:|
| wordcount | heap | 243.522 | 32.850 | 0.000 | 10000000 |
| wordcount | current SafeZone | 228.260 | 0.000 | 0.000 | 10000000 |
| wordcount | improved SafeZone | 194.933 | 0.000 | 0.000 | 10000000 |
| wordcount | Rift HPZone | 224.415 | 0.000 | 0.346 | 10000000 |
| wordcount | Rift Streaming | 199.156 | 0.000 | 0.258 | 10000000 |
| graphstep | heap | 240.890 | 38.498 | 0.000 | 10000000 |
| graphstep | current SafeZone | 273.608 | 0.000 | 0.000 | 10000000 |
| graphstep | improved SafeZone | 203.729 | 0.000 | 0.000 | 10000000 |
| graphstep | Rift HPZone | 213.454 | 0.000 | 0.409 | 10000000 |
| graphstep | Rift Streaming | 209.528 | 0.000 | 0.408 | 10000000 |

Interpretation:

- This is the first local Yak-style harness for Rift: heap control arrays remain
  durable while epoch-local word-count tokens or graph messages are allocated
  on heap, in SafeZone, or in Rift regions.
- Rift removes measured heap GC and beats heap on both workloads.
- Improved SafeZone is faster than Rift in the pressure run, so the current
  result supports the Yak control/data split but not a Rift-over-improved-
  SafeZone claim.
- Rift operation time is small: below `0.5 ms` even for ten million region
  objects per workload.

Grouped-sort local median configuration:

- `YAK_EPOCHS=10`
- `YAK_SORT_RECORDS_PER_EPOCH=100000`
- runs `3`, warmups `1`

| Mode | Median elapsed ms | Median GC ms | Median Rift op ms | Rift objects | Peak RSS bytes |
|---|---:|---:|---:|---:|---:|
| heap | 237.354 | 3.463 | 0.000 | 0 | 22446080 |
| current SafeZone | 234.644 | 0.000 | 0.000 | 0 | 24674304 |
| improved SafeZone | 236.047 | 0.000 | 0.000 | 0 | 24674304 |
| Rift HPZone | 227.393 | 0.283 | 0.047 | 1000000 | 24002560 |
| Rift Streaming | 232.658 | 0.307 | 0.030 | 1000000 | 24002560 |
| Yak-runtime proxy | 242.517 | 0.306 | 0.032 | 1000000 | 24002560 |

Interpretation:

- This adds an external-sort-shaped Yak methodology workload: durable group
  totals stay on heap while ordinary per-epoch `SortRecord` objects move into
  heap/SafeZone/Rift according to the selected memory policy.
- Sorting dominates elapsed time, so heap GC is only `3.463 ms`; the local
  HPZone win (`227.393 ms` vs heap `237.354 ms`) is real but modest.
- The result is a fair same-program allocation-placement check, not a dramatic
  Yak-scale GC-pressure result and not exact Hyracks evidence.

Top-word/filter local median configuration:

- `YAK_EPOCHS=40`
- `YAK_RECORDS_PER_EPOCH=250000`
- runs `3`, warmups `1`

| Mode | Median elapsed ms | Median GC ms | Median Rift op ms | Rift objects | Peak RSS bytes |
|---|---:|---:|---:|---:|---:|
| heap | 311.527 | 44.949 | 0.000 | 0 | 75038720 |
| current SafeZone | 326.680 | 0.000 | 0.000 | 0 | 83116032 |
| improved SafeZone | 271.273 | 0.000 | 0.000 | 0 | 83116032 |
| Rift HPZone | 266.478 | 0.000 | 0.416 | 10000000 | 82968576 |
| Rift Streaming | 262.980 | 0.000 | 0.401 | 10000000 | 82935808 |
| Yak-runtime proxy | 292.179 | 0.000 | 0.418 | 10000000 | 82935808 |

Interpretation:

- This adds a Hadoop-like top-word/filter methodology workload: durable global
  counts and reusable combiner arrays stay on the heap, while per-record stream
  objects are epoch-local.
- This is the strongest current Yak-shaped local result: Streaming is
  `262.980 ms` vs heap `311.527 ms` and improved SafeZone `271.273 ms`, with
  heap spending `44.949 ms` in measured GC.
- It is still not Hadoop/Yak artifact evidence.

GraphChi-style subinterval local median configuration:

- `YAK_EPOCHS=40`
- `YAK_GRAPHCHI_SUBINTERVALS=16`
- `YAK_GRAPHCHI_EDGES_PER_SUBINTERVAL=15625`
- runs `3`, warmups `1`

| Mode | Median elapsed ms | Median GC ms | Median Rift op ms | Rift objects | Peak RSS bytes |
|---|---:|---:|---:|---:|---:|
| heap | 302.599 | 58.498 | 0.000 | 0 | 12468224 |
| current SafeZone | 232.621 | 0.000 | 0.000 | 0 | 13008896 |
| improved SafeZone | 228.252 | 0.000 | 0.000 | 0 | 12959744 |
| Rift HPZone | 237.091 | 0.000 | 0.430 | 10000000 | 12943360 |
| Rift Streaming | 236.388 | 0.000 | 0.400 | 10000000 | 12910592 |
| Yak-runtime proxy | 270.159 | 0.000 | 0.411 | 10000000 | 12910592 |

Interpretation:

- This adds a GraphChi-like subinterval methodology workload: durable vertex
  values stay on heap, while per-subinterval edge-update objects are
  region-local.
- Streaming is `236.388 ms` vs heap `302.599 ms` and removes `58.498 ms` of
  measured heap GC, but improved SafeZone is still faster at `228.252 ms`.
- It is still not GraphChi/Yak artifact evidence.

Promotion/escape local median configuration:

- `YAK_EPOCHS=40`
- `YAK_RECORDS_PER_EPOCH=250000`
- `YAK_ESCAPE_MODULO=1000`
- runs `3`, warmups `1`

| Mode | Median elapsed ms | Median GC ms | Median Rift op ms | Rift objects | Barrier checks | Remembered refs | Promoted objects | Peak RSS bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 424.768 | 43.745 | 0.000 | 0 | 0 | 0 | 0 | 576045056 |
| Yak-runtime proxy | 513.465 | 0.000 | 0.736 | 20000000 | 10000000 | 10000 | 20000 | 220692480 |

Interpretation:

- The promotion workload is now the closest local Yak model: it keeps durable
  control metadata on heap, places epoch-local token/child data objects in a
  runtime epoch, routes heap/control writes through `RiftRegion.RuntimeEpoch`,
  and promotes rare escaping data through a `RuntimePromoter` hook.
- Yak-runtime removes measured heap GC and reduces RSS versus heap while
  preserving the same logical program and checksum, but it is slower in elapsed
  time. This is a negative result for dynamic promotion/barrier discipline on
  Scala Native and supports the static checked-boundary direction.
- This still is not exact Yak. It lacks Hyracks/Hadoop/GraphChi, distributed
  execution, actual field-write barriers, stack scanning, object movement, and
  STW epoch-end coordination.

Caveats:

- This is not an exact Yak reproduction. It does not run Hyracks, Hadoop, or
  GraphChi. The promotion workload now exercises a Rift memory-API-level
  runtime epoch, but it still does not implement Yak's full runtime machinery.
- The benchmark currently uses trusted `HPZone`/`Streaming` APIs, not the
  future safe capture-checked API.

### Stancu-Style Transaction/Accounting Matrix

Sources:

- `docs/LITERATURE_BENCHMARK_CONTRACT.md`
- `sandbox/STANCU_REGION_MATRIX.md`
- `evidence/STANCU_REGION_MATRIX.md`

Compile/check command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile
```

Smoke command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
STANCU_TRANSACTIONS=2000 STANCU_BENCHMARK_RUNS=1 STANCU_WARMUPS=0 \
STANCU_TX_PER_REGION=64 \
  zsh sandbox/run_stancu_region_instrumented_matrix.sh
```

Default native-only median command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
STANCU_BUILD=0 STANCU_BENCHMARK_RUNS=3 STANCU_WARMUPS=1 \
STANCU_TX_PER_REGION=64 \
STANCU_OUTPUT_DIR=/tmp/stancu-region-instrumented \
  zsh sandbox/run_stancu_region_instrumented_matrix.sh
```

Pressure native-only median command:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
STANCU_BUILD=0 STANCU_BENCHMARK_RUNS=3 STANCU_WARMUPS=1 \
STANCU_TRANSACTIONS=1000000 STANCU_TX_PER_REGION=64 \
STANCU_OUTPUT_DIR=/tmp/stancu-region-pressure \
  zsh sandbox/run_stancu_region_instrumented_matrix.sh
```

Default local median configuration:

- `STANCU_TRANSACTIONS=200000`
- `STANCU_ITEMS_PER_TX=8`
- `STANCU_TX_PER_REGION=64`
- runs `3`, warmups `1`

| Mode | Median elapsed ms | Median GC ms | Median Rift op ms | Logical region objects | Region-candidate objects | Escaped objects |
|---|---:|---:|---:|---:|---:|---:|
| heap | 43.871 | 4.483 | 0.000 | 1800000 | 99.76% | 0 |
| current SafeZone | 37.313 | 0.000 | 0.000 | 1800000 | 99.76% | 0 |
| improved SafeZone | 34.412 | 0.000 | 0.000 | 1800000 | 99.76% | 0 |
| Rift HPZone | 40.308 | 0.000 | 0.186 | 1800000 | 99.76% | 0 |
| Rift Streaming | 40.126 | 0.000 | 0.063 | 1800000 | 99.76% | 0 |

Pressure local median configuration:

- `STANCU_TRANSACTIONS=1000000`
- `STANCU_ITEMS_PER_TX=8`
- `STANCU_TX_PER_REGION=64`
- runs `3`, warmups `1`

| Mode | Median elapsed ms | Median GC ms | Median Rift op ms | Logical region objects | Region-candidate objects | Escaped objects |
|---|---:|---:|---:|---:|---:|---:|
| heap | 223.611 | 23.924 | 0.000 | 9000000 | 99.95% | 0 |
| current SafeZone | 173.976 | 0.307 | 0.000 | 9000000 | 99.95% | 0 |
| improved SafeZone | 174.620 | 0.315 | 0.000 | 9000000 | 99.95% | 0 |
| Rift HPZone | 201.447 | 0.000 | 0.772 | 9000000 | 99.95% | 0 |
| Rift Streaming | 199.438 | 0.000 | 0.317 | 9000000 | 99.95% | 0 |

Heavier local median configuration:

- `STANCU_TRANSACTIONS=500000`
- `STANCU_ITEMS_PER_TX=32`
- `STANCU_TX_PER_REGION=64`
- runs `3`, warmups `1`

| Mode | Median elapsed ms | Median GC ms | Median Rift op ms | Logical region objects | Region-candidate objects | Escaped objects |
|---|---:|---:|---:|---:|---:|---:|
| heap | 387.420 | 40.579 | 0.000 | 16500000 | 99.97% | 0 |
| current SafeZone | 333.532 | 0.000 | 0.000 | 16500000 | 99.97% | 0 |
| improved SafeZone | 328.298 | 0.000 | 0.000 | 16500000 | 99.97% | 0 |
| Rift HPZone | 364.288 | 0.000 | 1.077 | 16500000 | 99.97% | 0 |
| Rift Streaming | 341.879 | 0.000 | 0.588 | 16500000 | 99.97% | 0 |

Interpretation:

- The original per-transaction result was a useful negative result. The
  accounting looked favorable, but the boundary was too fine-grained and Rift
  allocation counters paid atomics in the hot allocation path.
- The fixed result batches `64` transactions per region and flushes Rift
  allocation stats at reset/close. Rift now beats heap and removes measured
  heap GC, but SafeZone remains faster on this small transaction probe.
- The 2026-04-26 boundary sweep makes that attribution explicit at 200k
  transactions: with one transaction per region, HPZone is `63.257 ms` and
  Streaming is `50.487 ms` versus heap `44.592 ms`; with 64 transactions per
  region, HPZone is `39.522 ms` and Streaming is `38.844 ms` versus heap
  `43.189 ms`; with 512 transactions per region, Streaming is `39.717 ms`
  versus heap `45.315 ms`. The 64-transaction boundary is the best measured
  point in this local sweep.
- This means "region-candidate fraction" is not sufficient as a research claim.
  The lifetime boundary must be coarse enough and the runtime statistics path
  must stay out of hot per-object allocation.

Caveats:

- This is not SPECjbb2005 and not Stancu et al.'s static analysis.
- `explicit_region_boundaries=1` in the result pack is a manual accounting
  field for the benchmark's one logical placement site, not a compiler-produced
  annotation count.
- The harness does not yet test compiler inference or capture-check rejection
  cases.

### DEBS 2015 Status

Source: `bench/debs2015/RESULTS.md`

Input preparation:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
DEBS2015_LIMIT=1000000 DEBS2015_JOINED_OUTPUT=/tmp/debs2015-month1-1000000.csv \
  zsh bench/debs2015/join_nyc_taxi_sample.sh
```

RunBoth matrix:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
DEBS2015_BOTH_INPUT=/tmp/debs2015-month1-1000000.csv \
DEBS2015_BOTH_OUTPUT_DIR=/tmp/debs2015-runboth-month1-1000000 \
  zsh bench/debs2015/run_both_sample_matrix.sh
```

1M non-instrumented single-run rows:

| Q1 mode | Events | Elapsed ms | Throughput events/s | Q1 p99.9 ms | Q1 max ms | Q2 p99.9 ms | Q2 max ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| heap | 1000000 | 21658.215 | 46171.857 | 0 | 92 | 2 | 69 |
| Rift HPZone | 1000000 | 22314.989 | 44812.928 | 0 | 1 | 2 | 37 |
| Rift Streaming | 1000000 | 22184.467 | 45076.585 | 0 | 45 | 2 | 94 |

Instrumented matrix:

```sh
cd /Users/siyaoliu/rift/scala-native-rift
DEBS2015_BOTH_BUILD=0 \
DEBS2015_BOTH_INPUT=/tmp/debs2015-month1-1000000.csv \
DEBS2015_BOTH_OUTPUT_DIR=/tmp/debs2015-runboth-instrumented-1000000 \
  zsh bench/debs2015/run_both_instrumented_matrix.sh
```

1M instrumented single-run rows from current binary:

| Q1 mode | Elapsed ms | Throughput events/s | GC collections | GC time ms | Rift op ms | Rift alloc objects | Rift opens/closes | Rift mmap bytes | Peak RSS bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 22827.882 | 43806.080 | 21 | 1051.752 | 0.000 | 0 | 0 / 0 | 0 | 1148780544 |
| Rift HPZone | 22366.285 | 44710.151 | 21 | 1003.171 | 9.350 | 979699 | 10730 / 10730 | 3342336 | 1152122880 |
| Rift Streaming | 22810.687 | 43839.101 | 21 | 1012.489 | 10.390 | 979699 | 10730 / 10730 | 3342336 | 1152122880 |

100k instrumented rows:

| Q1 mode | Elapsed ms | Throughput events/s | GC collections | GC time ms | Rift op ms | Rift alloc objects | Rift opens/closes | Rift mmap bytes | Peak RSS bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 2018.887 | 49532.241 | 8 | 86.696 | 0.000 | 0 | 0 / 0 | 0 | 348684288 |
| Rift HPZone | 2021.861 | 49459.394 | 8 | 83.432 | 1.036 | 98005 | 1513 / 1513 | 1015808 | 343670784 |
| Rift Streaming | 2018.424 | 49543.610 | 8 | 83.035 | 1.004 | 98005 | 1513 / 1513 | 1015808 | 343638016 |

Correctness:

- 10k, 100k, and 1M heap/Rift outputs match after stripping only the final latency column.

Caveats:

- The region-backed input-buffer checkpoint now has three-run medians:
  - 1M heap elapsed `17047.611 ms`, GC `684.338 ms`.
  - 1M Rift HPZone elapsed `17119.396 ms`, GC `640.062 ms`, Rift op `288.815 ms`.
  - 1M Rift Streaming elapsed `17210.458 ms`, GC `628.808 ms`, Rift op `288.920 ms`.
- The first ranking/result-output experiment is single-run diagnostic evidence:
  - 1M heap elapsed `16363.012 ms`, GC `601.615 ms`, RSS `1148436480`.
  - 1M Rift HPZone elapsed `17243.387 ms`, GC `503.198 ms`, Rift op `933.640 ms`, RSS `1088684032`.
  - 1M Rift Streaming elapsed `17301.238 ms`, GC `529.115 ms`, Rift op `936.641 ms`, RSS `1088618496`.
- Interpretation: region ranking/result objects reduce GC and can reduce RSS,
  but the current resettable snapshot-region design makes region operations
  visible enough to lose elapsed time. This is not Phase 5 success.
- The reusable ranking backend fixed the reset shape:
  - 1M heap median elapsed `14633.019 ms`, GC `513.199 ms`, RSS `813105152`.
  - 1M Rift HPZone median elapsed `14234.470 ms`, GC `457.726 ms`, Rift op `13.003 ms`, RSS `876101632`.
  - 1M Rift Streaming median elapsed `14392.097 ms`, GC `478.912 ms`, Rift op `14.166 ms`, RSS `876101632`.
- The Q2 bounded cell-table checkpoint replaced boxed per-cell maps with fixed
  arrays over the bounded Q2 grid key space. Heap and Rift use the same logical
  layout; Rift allocates the arrays and `ProfitStats` in a run-lifetime region:
  - 1M heap median elapsed `11471.085 ms`, GC `478.636 ms`, RSS `609730560`.
  - 1M Rift HPZone median elapsed `11442.637 ms`, GC `419.658 ms`, Rift op `11.759 ms`, RSS `490766336`.
  - 1M Rift Streaming median elapsed `11477.431 ms`, GC `428.339 ms`, Rift op `11.421 ms`, RSS `490799104`.
  - Outputs matched on sample, 100k, and 1M matrices after stripping only the
    measured latency column.
- The Q1 primitive route-table checkpoint replaced boxed Q1 route-count and
  route-rank maps with a shared primitive open-addressed table. Heap allocates
  the backing arrays with `new`; Rift modes allocate them in a run-lifetime
  ranking/control region:
  - 1M heap median elapsed `11957.721 ms`, GC `463.555 ms`, RSS `433209344`.
  - 1M Rift HPZone median elapsed `11659.223 ms`, GC `397.162 ms`, Rift op `15.102 ms`, RSS `381222912`.
  - 1M Rift Streaming median elapsed `11739.195 ms`, GC `398.268 ms`, Rift op `15.164 ms`, RSS `381190144`.
  - Q1 process improves versus the Q2-cell-table checkpoint, but total elapsed
    remains Q2-dominated and is not a clean cross-checkpoint speedup.
- The Q2 latest-empty taxi-table checkpoint replaced `latestEmptyByTaxi` with a
  shared growable dense array over existing taxi IDs. Heap allocates the array
  with `new`; Rift modes allocate it in the run-lifetime ranking/control region:
  - 1M heap median elapsed `11649.547 ms`, GC `487.774 ms`, RSS `609304576`.
  - 1M Rift HPZone median elapsed `11263.680 ms`, GC `381.099 ms`, Rift op `14.536 ms`, RSS `381501440`.
  - 1M Rift Streaming median elapsed `11188.144 ms`, GC `382.734 ms`, Rift op `14.991 ms`, RSS `381501440`.
- The Q2 array-backed ranking checkpoint replaced the heap `TreeSet` ranking
  index with a shared indexed binary heap over ordinary `ProfitableArea`
  objects. Heap allocates the index arrays with `new`; Rift modes allocate them
  in the run-lifetime ranking/control region:
  - 1M heap median elapsed `11202.975 ms`, GC `423.932 ms`, RSS `431718400`.
  - 1M Rift HPZone median elapsed `10808.901 ms`, GC `348.901 ms`, Rift op `14.861 ms`, RSS `383631360`.
  - 1M Rift Streaming median elapsed `10804.756 ms`, GC `344.376 ms`, Rift op `14.684 ms`, RSS `383631360`.
- The Q2 taxi-id table checkpoint replaced durable taxi-id `String` interning
  and a heap `HashMap` with a shared byte-backed table. Heap allocates table
  arrays, entries, and taxi-id byte copies with `new`; Rift modes allocate them
  in the run-lifetime ranking/control region:
  - 100k heap median elapsed `793.461 ms`, GC `18.122 ms`, RSS `199983104`.
  - 100k Rift HPZone median elapsed `787.594 ms`, GC `23.902 ms`, Rift op `1.443 ms`, RSS `69402624`.
  - 100k Rift Streaming median elapsed `785.273 ms`, GC `19.621 ms`, Rift op `1.421 ms`, RSS `69402624`.
  - 1M heap median elapsed `9876.359 ms`, GC `376.602 ms`, RSS `431751168`.
  - 1M Rift HPZone median elapsed `9676.525 ms`, GC `358.127 ms`, Rift op `13.216 ms`, RSS `169312256`.
  - 1M Rift Streaming median elapsed `9667.365 ms`, GC `270.482 ms`, Rift op `13.915 ms`, RSS `169295872`.
  - This was the strongest bounded-sample DEBS result before the Q1
    indexed-ranking checkpoint, but it still lacks SafeZone controls,
    controlled full-month performance, and safe API enforcement.
- The Q1 indexed-ranking checkpoint replaced the remaining Q1 heap `TreeSet`
  ranking nodes with a shared indexed heap over ordinary `RankedRoute`
  objects. Heap allocates ranking arrays with `new`; Rift modes allocate those
  arrays and the `RankedRoute`/`Route`/`Cell` object graph in the run-lifetime
  ranking/control region:
  - 100k heap median elapsed `903.449 ms`, GC `19.414 ms`, RSS `184090624`.
  - 100k Rift HPZone median elapsed `874.280 ms`, GC `18.821 ms`, Rift op `1.820 ms`, RSS `43024384`.
  - 100k Rift Streaming median elapsed `863.219 ms`, GC `18.578 ms`, Rift op `1.778 ms`, RSS `43024384`.
  - 1M heap median elapsed `9746.536 ms`, GC `312.151 ms`, RSS `431669248`.
  - 1M Rift HPZone median elapsed `9441.064 ms`, GC `320.025 ms`, Rift op `10.528 ms`, RSS `108445696`.
  - 1M Rift Streaming median elapsed `9442.026 ms`, GC `306.311 ms`, Rift op `10.094 ms`, RSS `108969984`.
  - This is now the strongest bounded-sample DEBS memory-footprint result:
    Rift peak RSS is about `108-109 MB` versus heap `431669248` bytes. GC time
    is mixed, so do not present it as a clean GC-time win.
- The RunBoth output-snapshot placement checkpoint moved Q1/Q2 previous-output
  snapshots into a run-lifetime region in Rift modes. Heap still allocates the
  same snapshot arrays with `new`; Rift allocates Q1/Q2 arrays and Q2
  `Snapshot` objects in the snapshot region:
  - 100k heap median elapsed `829.612 ms`, GC `18.383 ms`, RSS `184107008`.
  - 100k Rift HPZone median elapsed `811.389 ms`, GC `18.242 ms`, Rift op `1.615 ms`, RSS `44613632`.
  - 100k Rift Streaming median elapsed `815.476 ms`, GC `20.286 ms`, Rift op `1.604 ms`, RSS `44597248`.
  - 1M heap median elapsed `8983.464 ms`, GC `290.712 ms`, RSS `431652864`.
  - 1M Rift HPZone median elapsed `8815.087 ms`, GC `292.155 ms`, Rift op `10.053 ms`, RSS `119865344`.
  - 1M Rift Streaming median elapsed `8836.488 ms`, GC `296.305 ms`, Rift op `10.061 ms`, RSS `119898112`.
  - This is valid placement evidence but not a clean GC-time win. It also
    increases Rift RSS versus the Q1 indexed-ranking checkpoint because
    snapshots remain live until the run-lifetime snapshot region closes.
- The Q2 incremental-median checkpoint replaced dirty-cell copy/sort median
  recomputation with a shared per-cell two-heap median structure. Heap and Rift
  use the same Q2 algorithm; Rift modes allocate `ProfitStats` and median heap
  arrays in the run-lifetime ranking/control region:
  - 100k heap median elapsed `619.735 ms`, GC `8.091 ms`, RSS `97370112`.
  - 100k Rift HPZone median elapsed `626.609 ms`, GC `5.839 ms`, Rift op `1.518 ms`, RSS `40173568`.
  - 100k Rift Streaming median elapsed `610.258 ms`, GC `5.781 ms`, Rift op `1.573 ms`, RSS `40173568`.
  - 1M heap median elapsed `5976.447 ms`, GC `67.086 ms`, RSS `305758208`.
  - 1M Rift HPZone median elapsed `5794.879 ms`, GC `59.658 ms`, Rift op `10.737 ms`, RSS `113950720`.
  - 1M Rift Streaming median elapsed `5948.755 ms`, GC `55.056 ms`, Rift op `11.172 ms`, RSS `113934336`.
  - Median copy/sort is eliminated: `diag_q2_median_computes=0` and
    `diag_q2_median_values_sorted=0` at both 100k and 1M. Q2 rank fixes remain
    high at `3.252M` for 1M, so Q2 rank/output work remains the next DEBS
    target.
- The Q2 top-10 cache checkpoint keeps heap and Rift on the same logical
  query but avoids recomputing the top-10 frontier when an update cannot affect
  the cached result:
  - 100k heap median elapsed `607.176 ms`, GC `9.254 ms`, RSS `102350848`.
  - 100k Rift HPZone median elapsed `571.465 ms`, GC `5.348 ms`, Rift op `2.677 ms`, RSS `41500672`.
  - 100k Rift Streaming median elapsed `590.900 ms`, GC `5.093 ms`, Rift op `2.620 ms`, RSS `41500672`.
  - 1M heap median elapsed `6192.692 ms`, GC `70.762 ms`, RSS `304463872`.
  - 1M Rift HPZone median elapsed `5697.948 ms`, GC `36.231 ms`, Rift op `18.824 ms`, RSS `116588544`.
  - 1M Rift Streaming median elapsed `5657.424 ms`, GC `36.288 ms`, Rift op `21.925 ms`, RSS `96239616`.
  - Top-10 recomputes `29983` times out of `1000000` logical calls at 1M.
- The GC heap allocation-attribution checkpoint adds
  `SCALANATIVE_GC_ALLOC_STATS=1` as a diagnostic mode:
  - 1M heap: `19,924,383` GC allocation calls, `679,841,024` rounded bytes,
    and `582.629 ms` measured GC allocation-call time.
  - 1M Rift HPZone: `14,462,042` calls, `455,349,920` bytes, and `385.807 ms`.
  - 1M Rift Streaming: `14,462,060` calls, `455,350,304` bytes, and `384.031 ms`.
  - This explains why elapsed speedup can be larger than the GC collection-time
    delta. The attribution mode itself perturbs elapsed time and should not be
    used as the headline throughput comparison.
- The phase-level GC allocation-attribution checkpoint keeps the same opt-in
  diagnostic mode but moves phase bucketing into the C allocation hook:
  - A Scala-side phase-counter attempt was rejected and should not be used as
    evidence because reading counters in the hot loop allocated and polluted
    parse/change buckets.
  - Clean 1M C-side buckets: heap Q1 process `3,284,649` calls and Q2 process
    `2,088,994` calls; Rift HPZone/Streaming Q1 process `21,512` calls and Q2
    process `46,869` calls.
  - Snapshot heap allocation falls from heap `157,054` calls / `12,147,840`
    bytes to zero in Rift modes.
  - Q1/Q2 output remains the dominant heap churn: about `14.39M` allocation
    calls at 1M in both heap and Rift modes. This points to shared output-row
    scratch/formatting as the next fair DEBS target.
- The byte-output checkpoint replaces RunBoth's `BufferedWriter`/`Writer`
  character path with a shared `OutputSupport.ByteRowWriter`:
  - Heap mode uses a heap byte buffer; Rift modes allocate the reusable byte
    buffer in the existing run snapshot region. Durable `FileOutputStream`
    handles remain heap objects.
  - `Debs2015Smoke`, 100k/1M attribution matrices, and 100k/1M non-attribution
    3-run median matrices passed; heap/Rift outputs matched.
  - Clean 1M attribution after byte output: heap `6,025,143` heap allocation
    calls / `235,159,552` bytes / `171.868 ms` allocation-call time; HPZone
    `562,793` calls / `10,537,200` bytes / `12.923 ms`; Streaming `562,813`
    calls / `10,537,584` bytes / `12.801 ms`.
  - Non-attribution 1M medians after byte output: heap `4640.593 ms`, HPZone
    `4524.706 ms`, Streaming `4522.308 ms`; GC collection medians are
    `21.025 ms`, `0.685 ms`, and `0.635 ms`.

### Smoke Tests / Unit Tests / Compile Checks

Recorded as run:

- `sbt "tests3/testOnly scala.scalanative.memory.RiftRegionTest"` passes `5/5` in Phase 4 notes.
- `zsh bench/debs2015/run_both_instrumented_matrix.sh` rebuilt and linked the native DEBS runner after the latest counter additions.
- 100k and 1M instrumented DEBS matrices run to completion and outputs match.
- After the byte-reader change, 100k and 1M RunBoth matrices parsed all rows
  and matched outputs across heap, Rift HPZone, and Rift Streaming.
- After the reusable ranking backend and Q2 cell-table checkpoint,
  `Debs2015Q2Smoke` passed, `Debs2015RunBoth` native-linked, and sample/100k/1M
  instrumented matrices matched outputs across heap, Rift HPZone, and Rift
  Streaming.
- After the Q1 primitive route-table checkpoint, `Debs2015Q1Smoke` passed,
  `Debs2015RunBoth` native-linked, and 100k/1M instrumented matrices matched
  outputs across heap, Rift HPZone, and Rift Streaming.
- After the Q2 latest-empty taxi-table checkpoint, `Debs2015Q2Smoke` passed,
  `Debs2015RunBoth` native-linked, and 100k/1M instrumented matrices matched
  outputs across heap, Rift HPZone, and Rift Streaming.
- After the Q2 array-backed ranking checkpoint, `Debs2015Q2Smoke` passed,
  `Debs2015RunBoth` native-linked, and sample/100k/1M instrumented matrices
  matched outputs across heap, Rift HPZone, and Rift Streaming.
- After the Q2 taxi-id table checkpoint, `Debs2015Q1Smoke` and
  `Debs2015Q2Smoke` passed; sample, 100k median, and 1M median RunBoth
  matrices matched outputs across heap, Rift HPZone, and Rift Streaming.
- After the Q1 indexed-ranking checkpoint, `Debs2015Q1Smoke` and
  `Debs2015Q2Smoke` passed; sample, 100k median, and 1M median RunBoth
  matrices matched outputs across heap, Rift HPZone, and Rift Streaming.
- After the RunBoth output-snapshot placement checkpoint, compile, sample,
  100k median, and 1M median RunBoth matrices matched outputs across heap,
  Rift HPZone, and Rift Streaming.
- The JVM same-input GC probe in `bench/debs2015/jvm/DebsJvmGcProbe.java`
  processed the same 100k/1M joined CSVs with JVM-managed per-row objects and
  a bounded 30-minute window. It is not a full JVM Q1/Q2 port. It shows default
  JVM heap GC time is tiny on 1M (`6 ms` in window mode), while constrained
  heap headroom makes GC dominate (`1322 ms` at `-Xmx8m`).

Not yet run or not recorded:

- Full Scala Native test suite.
- Full compiler-plugin regression suite beyond the focused checked test.
- Median-backed Commix DEBS matrix.
- Improved SafeZone DEBS matrix where meaningful.

## 6. Key Findings So Far

SafeZone and baselines:

- Current SafeZone can still be very slow on linked one-region shapes.
- Improved SafeZone (`SAFEZONE_ROOTS_MODE=1`) substantially changes the baseline. On ListOfLists runtime matrix it reduces median wall time from `138171.998 ms` to `10132.854 ms`.
- SafeZone can be near heap on some flat/contiguous shapes, but that is workload-specific, not a universal conclusion.

Rift runtime:

- Rift has a real runtime-only win on linked allocation-heavy workloads:
  - GCBench: `161.641 ms` vs heap `203.514 ms` and improved SafeZone `223.770 ms`.
  - ListOfLists linked: `6951.331 ms` vs heap `15085.511 ms` and improved SafeZone `10132.854 ms`.
- The flat-layout Rift cliff was a runtime bug in the huge-allocation path; after fixing it, flat Rift is best in the recorded layout table.
- Regular slab zeroing mattered for linked and chunked follow-ups.

Topology and safety:

- Topology can change results by an order of magnitude.
- Unrooted Rift mixed topology produced a checksum mismatch because region memory is not GC-scanned. Region-to-GC references are allowed only if heap referents are otherwise rooted or visible to the GC.
- The Q1 DEBS crash/failure mode reinforced the same safety rule: storing heap objects in Rift region entries is unsafe if the region is the only owner.

Pipeline:

- The cleaned raw-array pipeline does not currently show a Rift win.
- The amordo `ZoneParVector` comparison is not apples-to-apples; Rift raw arrays are lower-level than parallel collection APIs.

Broom-style dataflow:

- The new `DataflowRegionMatrix` is the first local methodology benchmark that
  moves ordinary Scala dataflow objects into regions without changing the
  logical SELECT/AGGREGATE/JOIN programs.
- At 10 epochs x 100k documents, the native-only instrumented medians show heap
  GC time while current SafeZone, improved SafeZone, HPZone, and Streaming all
  report zero measured GC in timed runs. After the Rift allocation-counter fix,
  HPZone is strongest on all three local operators, while Streaming is mixed:
  SELECT heap `28.398 ms`, improved SafeZone `23.600 ms`, HPZone `21.614 ms`;
  AGGREGATE heap `59.906 ms`, improved SafeZone `43.216 ms`, HPZone
  `41.870 ms`; JOIN heap `28.347 ms`, improved SafeZone `24.079 ms`, HPZone
  `21.481 ms`, Streaming `36.120 ms`.
- A provisional 40-epoch x 500k-document native-only single run shows the same
  allocation-sensitive shape at a Broom-like input scale: SELECT heap
  `623.761 ms` with `207.058 ms` GC vs improved SafeZone `463.303 ms` and
  HPZone `451.041 ms`; AGGREGATE heap `859.726 ms` with `269.652 ms` GC vs
  improved SafeZone `618.133 ms` and HPZone `620.342 ms`; JOIN heap
  `602.540 ms` with `184.929 ms` GC vs improved SafeZone `470.770 ms` and
  HPZone `447.803 ms`.
- This strengthens the hypothesis that region placement can help when the
  workload is allocation-heavy with clear epoch lifetimes. It does not settle
  DEBS, where Q2 rank/output CPU work still dominates after the incremental
  median fix.
- The result is a Broom-style methodology reproduction, not exact Naiad/Broom
  evidence. Improved SafeZone is a serious baseline in this harness and must
  stay in comparison tables.

StreamFlex-style stream latency:

- The new `StreamFlexRegionMatrix` is a local methodology benchmark for the
  StreamFlex axes: throughput, per-event latency tails, deadline misses, and GC
  pressure.
- At the default local size, heap reports `8.944 ms` median GC time in
  throughput and four latency deadline misses. Rift HPZone and Streaming report
  zero median GC time and zero deadline misses, with throughput medians
  `37.638 ms` and `37.683 ms` versus heap `41.444 ms`.
- Under the allocation-pressure configuration, heap throughput is
  `634.472 ms` with `141.804 ms` median GC time. Rift HPZone is `331.740 ms`
  with `1.237 ms` region-op time, and Rift Streaming is `329.896 ms` with
  `0.835 ms` region-op time.
- The pressure latency run shows the clearest StreamFlex-style result: heap
  has p999 `327625 ns`, max `467958 ns`, and `89` deadline misses; Rift HPZone
  has p999 `3625 ns`, max `247500 ns`, and one miss; Rift Streaming has p999
  `6917 ns`, max `28209 ns`, and zero misses.
- This strengthens the latency-predictability argument for region-managed
  stream data, but it is not an exact StreamFlex/Ovm reproduction and does not
  include scheduler/queuing delay.

Yak-style control/data split:

- The new `YakRegionMatrix` is a local methodology benchmark for Yak's core
  observation: durable control metadata has generational behavior, while the
  data path creates many epoch-local objects.
- At the default local size, heap spends `12.062 ms` GC on `wordcount` and
  `9.283 ms` GC on `graphstep`; Rift removes that GC and beats heap on elapsed
  time. Improved SafeZone is the fastest or effectively tied.
- At the pressure size after the Rift allocation-counter fix, heap spends
  `32.850 ms` GC on `wordcount` and `38.498 ms` GC on `graphstep`. Rift
  HPZone/Streaming remove measured heap GC and beat heap; Streaming is close
  to improved SafeZone (`199.156 ms` vs `194.933 ms` for wordcount and
  `209.528 ms` vs `203.729 ms` for graphstep).
- A new `yak-runtime` mode adds a local runtime-safety proxy: epoch-local data
  objects are allocated in a reusable Rift streaming region through a dynamic
  epoch object with lifecycle checks. In the 2026-04-26 pressure run it beats
  heap and removes measured heap GC: `211.585 ms` vs heap `255.335 ms` on
  wordcount and `234.914 ms` vs heap `321.660 ms` on graphstep.
- The runtime proxy is slower than raw Rift Streaming in that run, especially
  on graphstep (`234.914 ms` vs `214.947 ms`), which gives a concrete
  runtime-safety overhead baseline.
- A grouped-sort workload now adds an external-sort-shaped operator. At 10 x
  100k records, HPZone is `227.393 ms` vs heap `237.354 ms`, but heap GC is
  only `3.463 ms`, so the signal is a modest allocation-placement win rather
  than a Yak-scale GC-pressure reproduction.
- A top-word/filter workload now adds a Hadoop-like task shape. At 40 x 250k
  records, Streaming is `262.980 ms` vs heap `311.527 ms` and improved SafeZone
  `271.273 ms`, while heap records `44.949 ms` of measured GC. This is the
  strongest local Yak-shaped Rift result so far.
- A GraphChi-like subinterval workload now adds the graph-processing task
  shape. At 40 epochs x 16 subintervals x 15625 edge updates, Streaming is
  `236.388 ms` vs heap `302.599 ms`, with heap at `58.498 ms` measured GC.
  Improved SafeZone remains faster at `228.252 ms`.
- A new `promotion` workload adds rare escaping data objects and
  memory-API-level barrier accounting. With 40 x 250k records and
  `YAK_ESCAPE_MODULO=1000`, Yak-runtime is `513.465 ms` vs heap `424.768 ms`,
  with 10M barrier checks, 10k remembered refs, 20k promoted objects, zero
  measured heap GC, and lower RSS (`220692480` vs `576045056` bytes).
  This is a negative elapsed-time result for dynamic promotion on Scala Native.
- This supports the control/data split as a local methodology result, but it
  weakens any claim that Rift currently surpasses improved SafeZone on
  Yak-shaped epoch workloads.
- The result is not exact Yak evidence: it lacks Hyracks/Hadoop/GraphChi,
  distributed execution, and full Yak dynamic object movement, stack scanning,
  field-write barriers, and STW comparisons.

Stancu-style annotation/accounting:

- The new `StancuRegionMatrix` is a local transaction-shaped accounting probe,
  not SPECjbb2005 and not Stancu et al.'s static analysis.
- It reports a high region-candidate object fraction: `99.76%` at default
  size and `99.95%` at pressure size, with `explicit_region_boundaries=1` and
  `escaped_region_objects=0`.
- The first per-transaction result was negative: high candidate fraction alone
  did not beat heap when Rift paid one reset/open/close boundary per
  transaction and the runtime counted each allocation with atomics.
- The current fixed result batches `64` transactions per region and moves Rift
  allocation statistics out of the per-object atomic hot path. At pressure
  size, heap is `223.611 ms` with `23.924 ms` GC; Rift HPZone is
  `201.447 ms` with zero GC and `0.772 ms` region-op time; Rift Streaming is
  `199.438 ms` with zero GC and `0.317 ms` region-op time.
- SafeZone remains stronger on this probe: current SafeZone is `173.976 ms`
  and improved SafeZone is `174.620 ms` at pressure size.
- This now supports a Rift-vs-heap Stancu-style accounting story, but not a
  Rift-vs-SafeZone story. Boundary granularity and instrumentation overhead
  were the key corrections.

DEBS:

- Q1/Q2 correctness is established for bounded sorted real-data samples up to 1M rows.
- The first 100k heap attempt was dominated by rescans/sorts (`246360.864 ms`), then improved to about `2 s` after incremental ranking.
- Current DEBS Rift modes region-allocate Q1 bucket entries and Q2 profit/empty-taxi window entries using the same bucketed algorithms as heap.
- A 100k phase breakdown before the byte reader showed Q2 processing at roughly
  `48-50%` of elapsed time and read+parse around `22%`. After the byte reader,
  read+parse is roughly `9-10%`, while Q2 processing is still the dominant
  phase at roughly `57-64%` in the latest 100k/1M single runs.
- Batching Q2 median scratch reset per processed trip reduced Rift resets from
  `171197` to `87438` and Rift region-op time from about `51.5 ms` to about
  `28 ms` on the 100k sample.
- The 1M byte-reader median rerun corrected the earlier single-run optimism:
  heap `17047.611 ms`, Rift HPZone `17119.396 ms`, Rift Streaming
  `17210.458 ms`. Rift reduced GC time by about `44-56 ms`, but Rift operation
  time was about `289 ms`.
- The first ranking/result-region experiment moved ordinary Scala
  `RankedRoute`/`Route`/`Cell` and `ProfitableArea` objects into regions and
  allocated top-k arrays in resettable snapshot regions. On a 1M single run it
  reduced HPZone GC time from heap `601.615 ms` to `503.198 ms` and RSS from
  `1148436480` to `1088684032`, but elapsed time worsened because Rift op time
  reached `933.640 ms`.
- The reusable ranking-array backend fixed that lifetime shape: on the 1M
  3-run median HPZone elapsed `14234.470 ms` vs heap `14633.019 ms`, with
  HPZone Rift op `13.003 ms`.
- The Q2 cell-table checkpoint moved bounded Q2 per-cell control tables out of
  boxed `HashMap`s and into fixed arrays. In Rift modes those arrays and
  `ProfitStats` are region-allocated. On the 1M 3-run median HPZone elapsed
  `11442.637 ms` vs heap `11471.085 ms`, GC time fell from `478.636 ms` to
  `419.658 ms`, and peak RSS fell from `609730560` to `490766336`.
- The Q1 route-table checkpoint moved Q1 route-count and route-rank maps into a
  shared primitive table. In Rift modes the table arrays are region-allocated.
  On the 1M 3-run median HPZone elapsed `11659.223 ms` vs heap `11957.721 ms`,
  GC time fell from `463.555 ms` to `397.162 ms`, and peak RSS fell from
  `433209344` to `381222912`. This is stronger evidence for placement, but not
  a total-elapsed breakthrough because Q2 processing remains dominant.
- The Q2 latest-empty taxi-table checkpoint moved latest empty-taxi state from a
  heap `HashMap` into a shared dense array. In Rift modes that array is
  region-allocated. On the 1M 3-run median HPZone elapsed `11263.680 ms` vs
  heap `11649.547 ms`, GC time fell from `487.774 ms` to `381.099 ms`, and peak
  RSS fell from `609304576` to `381501440`.
- The Q2 array-backed ranking checkpoint moved Q2 ranking index state from a
  heap `TreeSet` into a shared indexed heap. In Rift modes that index is
  region-allocated and the ranked values remain ordinary region-allocated
  `ProfitableArea` Scala objects. On the 1M 3-run median HPZone elapsed
  `10808.901 ms` vs heap `11202.975 ms`, GC time fell from `423.932 ms` to
  `348.901 ms`, and peak RSS fell from `431718400` to `383631360`.
- The Q2 taxi-id table checkpoint moved durable taxi-id metadata from heap
  `String` plus `HashMap` entries into a shared byte-backed hash table. In Rift
  modes the table arrays, entries, and taxi-id byte copies are region-allocated
  without region-to-heap `String` references. On the 1M 3-run median Streaming
  elapsed `9667.365 ms` vs heap `9876.359 ms`, GC time fell from
  `376.602 ms` to `270.482 ms`, and peak RSS fell from `431751168` to
  `169295872`.
- The Q1 indexed-ranking checkpoint moved Q1 ranking index state from a heap
  `TreeSet` into a shared indexed heap over ordinary `RankedRoute` Scala
  objects. In Rift modes the ranking arrays and `RankedRoute`/`Route`/`Cell`
  object graph are region-allocated. On the 1M 3-run median HPZone elapsed
  `9441.064 ms` vs heap `9746.536 ms`, Streaming elapsed `9442.026 ms`, and
  peak RSS fell from `431669248` to about `108-109 MB`.
- The RunBoth output-snapshot placement checkpoint moved Q1/Q2 previous-output
  snapshots into a run-lifetime Rift region. At 1M, HPZone elapsed
  `8815.087 ms` vs heap `8983.464 ms`, but GC time was not materially lower
  and Rift RSS rose to about `120 MB` because snapshots are retained until
  close. This is placement evidence, not a bottleneck win.
- The Q2 incremental-median checkpoint removed the dirty median copy/sort path
  from both heap and Rift. At 1M, HPZone elapsed `5794.879 ms` vs heap
  `5976.447 ms`, Streaming elapsed `5948.755 ms`, GC fell from `67.086 ms` to
  `59.658 ms`/`55.056 ms`, and Rift RSS was about `114 MB` versus heap
  `305758208` bytes. Median sort computes and values sorted are now zero.
- The Q2 top-10 cache checkpoint is the current median-backed DEBS result. At
  1M, HPZone elapsed `5697.948 ms` vs heap `6192.692 ms`, Streaming elapsed
  `5657.424 ms`, GC collection time fell from `70.762 ms` to about `36 ms`,
  and Rift RSS fell from `304463872` bytes to `116588544`/`96239616` bytes.
- The GC allocation-attribution run shows that `gc_time_ns` was only part of
  the memory-management story: at 1M, Rift removes about `5.46M` heap
  allocation calls and about `224 MB` of rounded heap allocation requests, and
  measured GC allocation-call time falls by about `197-199 ms`.
- The clean phase-attribution run shows where that came from and what remains:
  Q1/Q2 process and snapshot allocation mostly moved out of the GC heap in Rift
  modes, while per-row output construction still allocates heavily on the heap.
- The byte-output checkpoint removes most of that shared output churn. At 1M,
  Rift heap allocation drops to about `0.56M` calls and `10.5 MB`, and GC
  collection time in Rift modes is now below `1 ms` in both the attribution
  single run and the non-attribution 3-run medians.
- Remaining app control state is still substantial, especially Q2 rank/output
  maintenance and any broader collection API work. The current Rift elapsed/RSS
  win is still bounded-sample evidence, so this is stronger evidence but still
  not final Phase 5 success.

Why Rift DEBS still uses so much GC:

- The RunBoth path no longer uses `Source.getLines()` and no longer allocates a
  heap line `String` per row. Single-query Q1/Q2 runners still use the older
  file input path.
- Q2 window entries, active profit values, median scratch arrays, ranking
  `ProfitableArea` objects, top-k result arrays, and bounded per-cell tables
  are now region-backed in Rift modes. Q2 latest-empty taxi state is a
  region-backed dense array in Rift modes. Q2 ranking-index arrays are also
  region-backed in Rift modes. Q2 taxi-id table entries and taxi-id byte copies
  are also region-backed in Rift modes. RunBoth Q2 previous-output snapshots
  are region-backed in Rift modes. RunBoth latency backing arrays are now
  region-backed in Rift modes and copied to heap only for the final `Metrics`
  object, which outlives the region.
- Q1 window entries, route-table arrays, ranking-index arrays, ranking
  `RankedRoute`/`Route`/`Cell` objects, and top-k result arrays are
  region-backed in Rift modes. RunBoth Q1 previous-output snapshots are
  region-backed in Rift modes.
- Output formatting now writes directly to `Writer` through shared code; this
  removed much of the Q2 output allocation for heap and Rift alike.
- Rift currently removes Q1/Q2 window-entry allocation, Q2 active profit-value
  storage, Q2 median scratch arrays, RunBoth input bytes, ranking objects,
  top-k result arrays, Q2 bounded cell tables, Q1 route-table arrays, and Q2
  latest-empty taxi arrays from the GC heap. It also removes Q2 ranking-index
  tree nodes by replacing the `TreeSet` with a shared indexed heap whose arrays
  are region-backed in Rift modes, removes Q2 taxi-id table entries/bytes from
  the GC heap, and removes Q1 ranking-index tree nodes by replacing the
  `TreeSet` with a shared indexed heap whose arrays and ranked objects are
  region-backed in Rift modes, and moves RunBoth latency backing arrays into
  the snapshot region. The remaining heap pressure is Q2 rank/output
  maintenance internals, final metrics/output objects, and broader collections.
  Fine-grained
  result-snapshot reset overhead was fixed by the reusable ranking backend and
  should not be reintroduced.
- Q2 primitive cell keys remove accidental `Cell`/cell-id string allocation from the shared hot path, but this is a boundary/noise cleanup, not a Rift-specific win.

## 7. Roadmap Status

Roadmap source: `/Users/siyaoliu/rift/Claude_output/ROADMAP.md`

| Phase | Status | Evidence | Remaining work |
|---|---|---|---|
| Phase 0 baseline correction | Mostly complete, but still caveated | `sandbox/PHASE0_BASELINES.md` has 5-run medians and commands for GCBench, ListOfLists, GCBench topology, and pipeline surrogate. | Confirm whether all Phase 0 scripts/results should be committed as the trusted baseline pack. Be careful: pipeline is a surrogate. |
| Phase 1 bootstrap allocator | Done in old bootstrap tree | `/Users/siyaoliu/rift/rift-bootstrap/bench/microbench/results.md`; clean `-Wall -Werror` microbench notes. | Not active architecture; no need to redo unless validating standalone package. |
| Phase 2 in-tree runtime | Partially done | In-tree `RiftRuntime.c/h`, Scala facade, compiler lowering, `RiftRegionTest`, benchmark use. | Make API/header complete, run broader tests, decide stats ABI, clean up untracked state. |
| Phase 3 runtime-only benchmarks | Done enough for current story | GCBench and ListOfLists runtime medians recorded; pipeline surrogate recorded. | Commix is not included. Pipeline provenance remains surrogate. |
| Phase 4 topology/layout | Done enough to move on | `PHASE4_LAYOUT.md`, `PHASE4_TOPOLOGY.md`, `PHASE4_EXIT.md`. | Chunked layout still not a Rift win vs improved SafeZone. Mixed GC/region safety story needs Phase 6 tests. |
| Phase 5 streaming operators and DEBS | In progress | DEBS Q1/Q2 run simultaneously on real data; outputs match; instrumentation added; Q1 and Q2 window entries have shared heap/Rift backends; Q2 active profit values live in window entries; Q2 ranking uses primitive cell keys internally; RunBoth input bytes use a heap/Rift allocation-placement split; the reusable ranking backend region-allocates Q1/Q2 ranking objects and top-k result arrays; Q2 bounded per-cell tables, Q1 primitive route-table arrays, Q1 ranking-index arrays, Q2 latest-empty taxi arrays, Q2 ranking-index arrays, Q2 taxi-id table entries/bytes, RunBoth output snapshots, Q2 incremental median heap arrays, and RunBoth latency buffers are region-backed in Rift modes. New `diag_*` counters identify remaining heap/control paths, and the shared `Grid.cellKeyOrZero` hot path removes temporary `Some(Cell)`/`Cell` allocation from both heap and Rift. Q2 rank/output attribution reports change-check time, snapshot time, rank comparisons/swaps, top-candidate comparisons, and changed-output element checks. Q2 top-10 extraction is now cached with conservative invalidation. Opt-in GC heap allocation attribution now reports allocation calls, rounded bytes, allocation-call time, and C-side phase buckets. RunBoth byte output uses the same writer in heap/Rift modes while placing the reusable byte buffer in the region for Rift modes; `rift-checked` now integrates checked Q1/Q2 processors in the same RunBoth loop. Opt-in active-memory and region-family diagnostics now attribute live checked-region payload. Opt-in process diagnostics now attribute checked Q1/Q2 CPU shape without changing normal timing rows. Opt-in Q2 CPU substep diagnostics now attribute bounded Q2 process time. | Latest trusted 1M byte-output medians are heap `4640.593 ms`, HPZone `4524.706 ms`, and Streaming `4522.308 ms`; GC collection medians are heap `21.025 ms`, HPZone `0.685 ms`, and Streaming `0.635 ms`; heap RSS is `159907840`, HPZone/Streaming RSS is `116785152`. Checked RunBoth 1M medians are heap `5363.257 ms`, HPZone `5224.005 ms`, Streaming `5209.104 ms`, and checked `5043.240 ms`; GC medians are heap `21.226 ms`, HPZone `0.834 ms`, Streaming `0.862 ms`, and checked `2.473 ms`. The latest trusted 1M allocation-attribution run shows heap at `6,025,143` GC allocation calls, `235,159,552` bytes, and `171.868 ms` allocation-call time, versus about `0.56M` calls, `10.5 MB`, and `12.8-12.9 ms` in trusted Rift modes. Checked allocation attribution drops the heap baseline to `752568` calls, `28785632` bytes, and `20.514 ms` allocation-call time. The first full-month checked RunBoth control matched heap output but had invalid checked wall-clock timing due descheduling; the pool-cap same-run full-month control is heap `71.919 s`, `0.323 s` GC, `579.1 MiB` RSS versus checked `77.947 s`, `0.190 s` GC, `695.2 MiB` RSS. After the single-control-object `ChildBucket` change, the same-order full-month 3-run median is heap `73.029 s` versus checked `67.670 s`, with GC `0.315 s` versus `0.086 s`; checked RSS is worse (`866.6 MiB` median versus heap `586.4 MiB`), and one checked repeat is slower. Region-family attribution found Q1 checked rank object graphs parent-lived; moving them into Q1 child bucket regions reduces full-month checked active requested peak from `823153856` to `180948200` bytes and RSS from `1086668800` to `613318656` bytes in checked-only diagnostics. The post-fix full-month 3-run median is heap `67.122 s` versus checked `66.804 s`; checked RSS median is now `613.3 MiB` versus heap `595.9 MiB`, with checked GC `0.117 s`, heap GC `0.285 s`, and checked Rift op `0.779 s`. Closeable SafeZone DEBS 1M medians now exist and show SafeZone lower-RSS but slower than heap and checked. Process diagnostics show Q2 operation counts are identical between heap and checked, while full-month Q1 checked rank creations rise from `6195167` to `14487771` because rank objects are refreshed into child-bucket lifetimes. Q2 CPU substep diagnostics on bounded 100k/1M inputs do not reproduce checked Q2 same-operation overhead: checked Q2 process and recorded Q2 CPU are lower than heap in those perturbing rows. Remaining work is lower-overhead/richer checked rank APIs, optional full-month SafeZone comparison, remaining control/collection work, and stronger safe API boundaries. |
| Phase 6 literature-benchmark evidence | Started | `docs/LITERATURE_BENCHMARK_CONTRACT.md` extracts the paper comparison contract. `DataflowRegionMatrix` now runs Broom-style SELECT/AGGREGATE/JOIN methodology workloads with ordinary Scala objects in heap, current SafeZone, improved SafeZone, Rift HPZone, and Rift Streaming modes. Native-only local medians include peak RSS, and a Broom-scale single run is recorded. `StreamFlexRegionMatrix` now runs stream throughput/latency methodology workloads with deadline-miss and latency-tail metrics. `YakRegionMatrix` now runs word-count, graph-step, external-sort-shaped grouped sort, top-word/filter, GraphChi-like subintervals, runtime-proxy, and promotion/escape control-data split workloads. `StancuRegionMatrix` now runs transaction/accounting probes with batched transaction regions. The 2026-04-26 Stancu boundary sweep records per-transaction, 64-transaction, and 512-transaction region boundaries. | Keep improved SafeZone in all claims, and do not claim exact Naiad/Broom, exact StreamFlex/Ovm, exact Yak, or exact Stancu reproduction. The current sequence gives strong Broom/Dataflow HPZone evidence, strong StreamFlex-style throughput/latency evidence, Yak-style Rift-vs-heap and near-improved-SafeZone evidence for no-escape epochs, a modest grouped-sort allocation-placement win, a stronger top-word/filter result, a GraphChi-like Rift-vs-heap but not Rift-vs-improved-SafeZone result, a negative memory-API-level dynamic-promotion result, and Stancu-style Rift-vs-heap evidence after batching/fixed counters. The Stancu weak result is now specifically attributed to too-fine region boundaries. Next choices are safe API rejection probes or returning to DEBS with the literature findings in mind. Build a fair Rift collection/operator API before redoing parallel-collections claims. |
| Phase 7 capture checking | Started | `RiftRegion.scoped`/`streaming` safe API slice exists. Targeted Scala-next compiler tests now pass for scoped object graphs, for-loop allocation, nested scoped regions, local higher-order consumers, non-escaping closures, return escape rejection, heap retention rejection, nested-region leak rejection, streaming reset escape rejection, conservative returned-function rejection, explicit `HeapRoot` metadata handles, static module singleton and immutable module-val metadata, direct unrooted heap-object constructor-argument rejection, region-local alias acceptance, heap-alias rejection, heap-field-selection rejection, explicit `{region}` constructor-field reuse, plain `T^` field-reuse rejection, region-owned array checks, owner-token `ObjectBuffer`, growable owner-token `RegionBuffer`, owner-token `RegionPriorityQueue`, owner-token `RegionIndexedPriorityQueue`, lexicographic checked indexed-rank priorities, reset epoch arrays, top-word rooted metadata buffers, GraphChi rooted/unrooted heap metadata, reset-epoch values stored into outer buffers, mutable local linked-list heads with provenance-preserving assignments, pinned diagnostic substrings for every current negative compiler probe, and the explicit split that `RiftRegion.open` is trusted while `ScopedRegion`/`StreamingRegion` allocations are checked. `docs/REPORT_CAPTURE_CHECK.md` records the current checker behavior. | Broader collection/operator APIs, hash-keyed state, broader static-field provenance, and a better ergonomics story for field/container provenance beyond local linked-list heads. |
| Phase 8 native GC/region hardening | Started | `HeapRoot` handles give a GC-visible explicit-root path for heap metadata stored from region objects; direct unrooted heap-object constructor arguments, heap aliases, heap field selections, unsafe region-array stores, unsafe owner-token `ObjectBuffer`/`RegionBuffer` heap stores, mutable static vars, and mutable-head heap retagging are rejected in checked Rift lowering while region-to-region object graphs, simple region-local aliases, static module singletons, immutable module vals, stable constructor fields explicitly captured by `{region}`, explicitly captured region arrays, owner-token object buffers, growable region buffers, and provenance-preserving mutable local linked-list heads still compile. | Extend or deliberately limit the mixed-reference rule for richer containers; decide whether plain `T^` field reuse and plain receiver-style container operations need a compiler extension or owner-token APIs. |
| Phase 9 Lean mechanization | Open | Design pack has Lean stubs/templates. | Port or start proof work; prove without `sorry`. |
| Phase 10 writing | Not started beyond notes | Result packs and this handoff exist. | Thesis/paper narrative after evidence stabilizes. |

Post-table update: the current checked API slice now includes
`putWindowRankInBucket` and framework-owned auto-removal of bucket-owned
`StreamWindowIndexedRank` keys before child bucket close. It also includes
entry-cleanup callbacks that report removed rank entries during close so
operators can clean side tables without a duplicate checked-side key list. The
focused compiler suite now passes `72/72`, and the native checked runtime suite
passes `23/23`. The hash-keyed checked rank queue checkpoint then raises the
focused compiler suite to `76/76` and the native checked runtime suite to
`25/25`; the long-key stream-window rank checkpoint raises them to `80/80` and
`28/28`. The remove-with-value close primitive simplifies framework
unlinking and validates already-popped-key cleanup, but does not yet remove the
focused checked CPU gap. The lexicographic priority API removes the Q1
tie-breaker blocker for this dense-key rank shape. Standalone hash-keyed rank
state and stream-window integration now exist; lower container CPU overhead and
application integration remain open.

Is Phase 0 actually complete?

- For GCBench and ListOfLists, yes enough to proceed.
- For pipeline, only as a provisional surrogate, not as a final reproduction of the original claimed pipeline result.
- Phase 0 should be described as "mostly complete with caveats," not "finalized beyond dispute."

## 8. Files Of Highest Importance

Docs / roadmap / design:

- `/Users/siyaoliu/rift/Claude_output/DESIGN.md`
- `/Users/siyaoliu/rift/Claude_output/ROADMAP.md`
- `/Users/siyaoliu/rift/Claude_output/CODEX.md`
- `docs/HANDOFF.md`
- `docs/LITERATURE_BENCHMARK_CONTRACT.md`
- `docs/STREAM_GC_EVIDENCE_AND_COMPARISON_PLAN.md`
- `AGENTS.md`
- `CLAUDE.md`

Runtime implementation:

- `nativelib/src/main/resources/scala-native/rift/RiftRuntime.c`
- `nativelib/src/main/resources/scala-native/rift/RiftRuntime.h`
- `nativelib/src/main/resources/scala-native/zone/MemoryPool.c`
- `nativelib/src/main/resources/scala-native/zone/MemoryPool.h`
- `nativelib/src/main/resources/scala-native/zone/LargeMemoryPool.c`
- `nativelib/src/main/resources/scala-native/zone/Zone.c`
- `nativelib/src/main/resources/scala-native/gc/immix_commix/GCRoots.c`

Scala API surface:

- `nativelib/src/main/scala/scala/scalanative/memory/RiftRegion.scala`
- `nativelib/src/main/scala/scala/scalanative/runtime/RiftAllocator.scala`
- `nativelib/src/main/scala-3/scala/scalanative/memory/RiftRegionCompanionScalaVersionSpecific.scala`
- `nativelib/src/main/scala-2/scala/scalanative/memory/RiftRegionCompanionScalaVersionSpecific.scala`
- `nativelib/src/main/scala/scala/scalanative/memory/SafeZone.scala`

Compiler/plugin integration:

- `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirDefinitions.scala`
- `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirGenExpr.scala`
- `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirPrimitives.scala`

Benchmark harnesses:

- `sandbox/src/main/scala-next/GCBenchRuntimeMatrix.scala`
- `sandbox/src/main/scala-next/ListOfListsRuntimeMatrix.scala`
- `sandbox/src/main/scala-next/ListOfListsFlatMatrix.scala`
- `sandbox/src/main/scala-next/ListOfListsChunkedMatrix.scala`
- `sandbox/src/main/scala-next/ListOfListsTopologyMatrix.scala`
- `sandbox/src/main/scala-next/PipelineRuntimeMatrix.scala`
- `sandbox/src/main/scala-next/DataflowRegionMatrix.scala`
- `sandbox/src/main/scala-next/StreamFlexRegionMatrix.scala`
- `sandbox/src/main/scala-next/YakRegionMatrix.scala`
- `sandbox/src/main/scala-next/StancuRegionMatrix.scala`
- `sandbox/src/main/scala-next/debs2015/*`
- `bench/debs2015/*`

Notes / result packs:

- `sandbox/PHASE0_BASELINES.md`
- `sandbox/PHASE4_LAYOUT.md`
- `sandbox/PHASE4_TOPOLOGY.md`
- `sandbox/PHASE4_EXIT.md`
- `sandbox/PIPELINE_PARCOLL_COMPARISON.md`
- `sandbox/DATAFLOW_REGION_MATRIX.md`
- `sandbox/STREAMFLEX_REGION_MATRIX.md`
- `sandbox/YAK_REGION_MATRIX.md`
- `sandbox/STANCU_REGION_MATRIX.md`
- `bench/debs2015/RESULTS.md`

Scripts:

- `sandbox/run_gcbench_runtime_matrix.sh`
- `sandbox/run_gcbench_topology_matrix.sh`
- `sandbox/run_listoflists_runtime_matrix.sh`
- `sandbox/run_listoflists_flat_matrix.sh`
- `sandbox/run_listoflists_chunked_matrix.sh`
- `sandbox/run_listoflists_topology_matrix.sh`
- `sandbox/run_listoflists_topology_report_subset.sh`
- `sandbox/run_pipeline_runtime_matrix.sh`
- `sandbox/run_dataflow_region_matrix.sh`
- `sandbox/run_streamflex_region_instrumented_matrix.sh`
- `sandbox/run_yak_region_instrumented_matrix.sh`
- `sandbox/run_stancu_region_instrumented_matrix.sh`
- `bench/debs2015/join_nyc_taxi_sample.sh`
- `bench/debs2015/run_both_sample_matrix.sh`
- `bench/debs2015/run_both_instrumented_matrix.sh`

## 9. Open Questions / Uncertainties / Risks

Technical uncertainties:

- Can the safe `ScopedRegion`/`StreamingRegion` APIs be expressed cleanly with current Scala 3 capture checking?
- How should region-to-GC references be restricted or made visible to the GC in safe APIs?
- Should Rift stats functions become public C API in `RiftRuntime.h`, remain private, or be gated behind a compile flag?
- The current `mach_timebase_info` timing path in `RiftRuntime.c` calls `mach_timebase_info` for every timed operation on macOS. This is acceptable for instrumentation but probably not final low-overhead runtime design.
- Q2 no longer recomputes medians by sorting dirty arrays in the current
  worktree. It uses shared per-cell incremental median heaps; heap allocates
  those arrays normally, and Rift allocates them in the Q2 run-lifetime
  ranking/control region.
- New `diag_*` counters confirm the old median sort path is gone in the
  single-run diagnostics (`0` median sort computes and `0` values sorted), but
  Q2 rank maintenance is still large at 1M: about `3.25M` rank fixes,
  `3.32M` median reads, and `0.90M` median heap rebalances.

Benchmarking uncertainties:

- Current DEBS checkpoint rows have 100k and 1M three-run medians, but older
  DEBS rows in the same result history are still single-run diagnostics.
- DEBS now has bounded sorted January medians and a first full-month output
  equivalence run. The pool-cap follow-up adds one usable checked full-month
  timing row, but repeated same-run full-month wall-clock performance remains
  open.
- Commix now has focused 3-run DEBS medians for heap vs `rift-checked`, but not
  broader matrices.
- Improved SafeZone comparison is not yet present for DEBS because DEBS currently compares heap vs Q1 Rift modes, not SafeZone modes.
- Pipeline is a surrogate. Do not present it as a reproduction of the old Broom/Naiad-style result.
- `DataflowRegionMatrix` is a Broom-style methodology reproduction, not an
  exact Naiad/Broom artifact reproduction. It now includes SafeZone modes and
  native-only RSS collection, but the 40-epoch 500k+ document result is still a
  single-run stress checkpoint rather than a median.
- `StreamFlexRegionMatrix` is a StreamFlex-style methodology reproduction, not
  an exact Ovm/StreamFlex artifact reproduction. It records per-event
  processing latency tails and deadline misses, but not full periodic
  scheduler/queuing delay.
- `YakRegionMatrix` is a Yak-style methodology reproduction, not an exact
  Hyracks/Hadoop/GraphChi or Yak runtime reproduction. It tests the control/data
  split locally and now includes a `RiftRegion.RuntimeEpoch` promotion/escape
  proxy, but not distributed execution, real field-write barriers, stack
  scanning, generic object movement, or STW epoch-end behavior.
- `StancuRegionMatrix` is a Stancu-style accounting probe, not SPECjbb2005 and
  not a static points-to analysis. Its initial per-transaction result was
  negative, but batching `64` transactions per region plus the Rift
  allocation-counter fix now gives a Rift-vs-heap win. It still does not beat
  SafeZone or provide compiler-produced annotation/capture reports.
- Older result packs were generated from then-uncommitted code. The current
  input-boundary, ranking/result, Q2 cell-table, Q1 route-table, Q2 taxi-table,
  Q2 array-ranking, and checked Q1 window-rank experiments now have local
  commit boundaries, but public claims still need pushed provenance, optional
  full-month SafeZone context, higher-level rank/window collections, and
  stronger checked close/safety evidence.

Provenance risks:

- The active branch has local commit boundaries through the Q2 array-backed
  ranking checkpoint once this update is committed, but this branch is ahead of
  `origin/feature/rift` until pushed.
- Several old worktrees are dirty and contain useful but obsolete artifacts;
  avoid mixing their outputs into active results without labeling provenance.

Docs needing possible revision:

- `/Users/siyaoliu/rift/Claude_output/DESIGN.md` is now provenance, not the
  active design. The active `DESIGN.md` and `ROADMAP.md` have been revised
  through the Q2 array-backed ranking checkpoint.
- `RiftRuntime.h` does not include the newest stats API used by Scala externs.
- Rift allocation counters now flush at region reset/close, so stats sampled
  while a region is still open may lag until the boundary is reached.

## 10. Exact Next Recommended Steps

Immediate next step:

1. Treat the checked RunBoth checkpoint as the latest median-backed Phase 5/7
   bounded-sample result. At 1M, heap median elapsed is `5363.257 ms`, trusted
   HPZone is `5224.005 ms`, trusted Streaming is `5209.104 ms`, and checked is
   `5043.240 ms`; GC collection medians are `21.226 ms`, `0.834 ms`,
   `0.862 ms`, and `2.473 ms`. This is stronger checked RunBoth evidence, but
   not final DEBS application evidence.
2. Treat the `DataflowRegionMatrix` result as started Phase 6/Broom-style
   methodology evidence with improved SafeZone included. The post-counter-fix
   10 x 100k medians show HPZone beating heap and improved SafeZone on
   SELECT/AGGREGATE/JOIN; the Broom-scale stress run is still a single run and
   should not be presented as exact Naiad/Broom reproduction.
3. Treat the `StreamFlexRegionMatrix` result as strong Phase
   6/StreamFlex-style methodology evidence. The fixed pressure run shows Rift
   throughput around `330 ms` vs heap `634 ms`, and Streaming has zero deadline
   misses. It is still not exact StreamFlex/Ovm.
4. Treat the `YakRegionMatrix` result as Phase 6/Yak-style methodology
   evidence. It supports the control/data split locally: Rift beats heap,
   Streaming is close to improved SafeZone under pressure, and the new
   `yak-runtime` proxy shows a pure runtime-managed epoch path can also beat
   heap while costing more than raw Rift Streaming. The grouped-sort workload
   adds an external-sort-shaped same-program allocation-placement check:
   HPZone is `227.393 ms` vs heap `237.354 ms`, but heap GC is only
   `3.463 ms`. The top-word/filter workload is stronger: Streaming is
   `262.980 ms` vs heap `311.527 ms` and improved SafeZone `271.273 ms`.
   The GraphChi-like subinterval workload shows Streaming at `236.388 ms` vs
   heap `302.599 ms`, but improved SafeZone is faster at `228.252 ms`. The new
   `promotion` workload adds a closer Yak model with rare escaping objects and
   `RiftRegion.RuntimeEpoch` barrier/remember/promote accounting. It removes
   measured heap GC but is slower than heap on elapsed time, so it should be
   used as motivation for static checked boundaries, not as a speedup claim.
   This is still not exact Yak because it lacks distributed runtimes, actual
   field-write barriers, stack scanning, generic object movement, and STW
   coordination.
5. Treat the `StancuRegionMatrix` result as started Phase 6/Stancu-style
   accounting evidence. The initial per-transaction result was negative, but
   batched transaction regions plus the lower-overhead Rift counter path now
   give a Rift-vs-heap win. The 2026-04-26 boundary sweep confirms the causal
   shape: one transaction per region loses, 64 transactions per region is best
   in the local sweep, and 512 transactions per region is still a Rift-vs-heap
   win but not faster than 64. It is not a Rift-vs-SafeZone win and not a
   compiler annotation result.
6. The current safe API accept/reject probe slice now passes 65/65 in the
   targeted Scala-next compiler test. The latest regression test confirms that
   trusted `RiftRegion.open(...)` allocation can still build linked benchmark
   objects while checked `ScopedRegion`/`StreamingRegion` allocation keeps the
   v1 mixed-reference guard. Returned closures are rejected
   conservatively through direct function-result rejection. Region-to-GC
   metadata has an explicit `HeapRoot` path, and static module singletons plus
   immutable module vals are accepted as independently rooted metadata. Direct
   unrooted heap-object constructor arguments are rejected in checked Rift
   allocation lowering. Simple region-local aliases are propagated; heap
   aliases, heap field selections, and mutable static vars are rejected. Stable
   constructor fields explicitly captured by `{region}` are accepted.
   Region-owned arrays are accepted when reference
   elements are explicitly captured, and stores into known region arrays reject
   unrooted heap objects. The first checked `ObjectBuffer` container uses
   owner-token APIs, including `region.append/get/length`, so ordinary region
   objects and `HeapRoot` handles can be stored while direct heap stores and
   inner-region-to-outer-buffer stores are rejected. The growable checked
   `RegionBuffer` uses the same owner-token rule and region-backed array
   growth. `RegionPriorityQueue`, `RegionIndexedPriorityQueue`, `ChildBucket`,
   and `StreamBucketArena` are now covered as reusable owner-token primitives.
   Plain `T^` selected
   fields, richer static-field provenance, and plain receiver-style containers
   still need a checked policy or trusted-only labeling.
7. RunBoth latency collectors now use shared primitive buffers: heap mode keeps
   them on the heap, and Rift modes allocate their backing arrays in the
   existing snapshot region before copying the final metrics arrays out at
   region close.
8. Q2 rank/output attribution is implemented, and the first follow-up fix is
   committed as a shared Q2 top-10 cache. The cache preserves the same heap/Rift
   logical query algorithm but avoids recomputing the top-10 frontier when a
   rank update cannot affect the cached result. On the 100k validation,
   top-candidate comparisons fell from `4.45M` to `144949`; on the 1M
   validation, top 10 recomputed `29983` times out of `1000000` calls. The
   3-run medians are now recorded: at 1M, heap is `6192.692 ms`, HPZone is
   `5697.948 ms`, and Streaming is `5657.424 ms`; GC drops from `70.762 ms`
   to about `36 ms`, and RSS drops from `304463872` bytes to `116588544`
   bytes for HPZone and `96239616` bytes for Streaming. A small binary heap
   for top candidates was tested and rejected before commit because it
   increased comparisons to about `5.39M`.
9. GC heap allocation attribution is implemented behind
   `SCALANATIVE_GC_ALLOC_STATS=1`. At 1M, heap allocation calls/bytes/time are
   `19,924,383` / `679,841,024` / `582.629 ms`, versus Rift HPZone
   `14,462,042` / `455,349,920` / `385.807 ms` and Rift Streaming
   `14,462,060` / `455,350,304` / `384.031 ms`. This should guide the next
   DEBS target, but attribution-mode elapsed timings are not headline
   performance results.
10. Phase-level GC heap allocation attribution now uses C-side thread-local
    phase buckets. The clean 1M run shows Q1/Q2 processing and snapshot heap
    allocation mostly moved into Rift regions, while Q1/Q2 output construction
    still accounts for about `14.39M` heap allocation calls in both heap and
    Rift modes. The earlier Scala-side phase-counter attempt polluted the
    measurement and should not be used.
11. RunBoth byte output is implemented and measured. The 1M non-attribution
    medians are heap `4640.593 ms`, HPZone `4524.706 ms`, and Streaming
    `4522.308 ms`; Rift GC collection medians are now below `1 ms`. The
    remaining DEBS bottleneck is mostly query CPU/I/O and broader controls, not
    GC collection.
12. `RiftRegion.StreamBucketArena` is implemented and checked Q1 now uses it
    for the accepted window-rank arena pattern. This generalizes the bucket
    lifetime primitive, but it is still below a full checked rank/window
    collection API.
13. `RiftRegion.StreamWindowIndexedRank` is implemented as the first higher
    checked rank/window collection. It combines `StreamBucketArena` with
    `RegionIndexedPriorityQueue`, checks direct heap stores through the
    compiler guard, and now has `putWindowRankInBucket` auto cleanup for
    bucket-owned rank keys before child bucket close. The entry-cleanup close
    callbacks report removed rank entries for side-table cleanup. It is dense-key and
    supports single-`Long` and four-component lexicographic priorities. A
    standalone long-key queue and `StreamWindowLongIndexedRank` now cover
    arbitrary `Long` keys with the same bucket-close discipline. The checked
    window-rank container still has CPU overhead.

Next technical milestone:

1. Continue reducing checked stream-window rank container CPU overhead or apply
   `StreamWindowLongIndexedRank` to a Q1-style route-key operator slice. The entry-cleanup matrix
   improved the auto-cleanup path from `313.572 ms` to `302.001 ms`, but remains
   slower than heap and the earlier manual-cleanup path. The follow-up
   remove-with-value close primitive is correctness/usefulness cleanup, not a
   measured speed fix. The lexicographic priority API now covers Q1-style
   tie-breakers, and long-key stream-window rank state now exists, so the next
   blocker is application integration or lower CPU overhead.
   The Q2 substep diagnostic does not currently reproduce bounded same-count Q2
   overhead.
2. Continue the DEBS "region-heavy" path with measurement first after the
   checked RunBoth median and attribution checkpoints. The next DEBS work
   should be a safety abstraction or control run, not a blind region-allocation
   pass: current evidence says GC heap churn is much lower and remaining
   elapsed time is mostly Q1/Q2 CPU plus file I/O.
3. Finish the remaining capture/safety guardrails before broadening mixed
   object graphs: static-heap/higher-level container mixed-reference policy,
   plain-field and array-element ergonomics, richer mutable-container
   provenance beyond local linked-list heads, plain receiver-style collection
   operations beyond owner-token methods, precise returned-closure support
   beyond the v1 rejection, and explicit HPZone/trusted labels for unsafe
   cases.
4. Start the next DEBS step with a narrow measurement-driven plan:
   - Treat the checked RunBoth medians as the latest bounded-sample Phase 5/7
     checkpoint, not final full-DEBS evidence.
   - Treat the `SCALANATIVE_GC_ALLOC_STATS=1` result as diagnostic evidence
     that collection pause time is not the whole memory-management cost:
     direct heap allocation calls/bytes/time also drop when structured-lifetime
     objects move into regions. Do not use attribution-mode elapsed timings as
     headline performance numbers.
   - Use the phase allocation buckets to keep the work honest: any next change
     should preserve Q1/Q2 results and heap/Rift algorithm shape, or be
     explicitly labeled as a shared benchmark cleanup.
   - Treat the RunBoth byte parser and region-backed input buffer as
     implemented. It avoids per-row line strings; the Q2 taxi-id table now
     stores byte-backed IDs with a heap/Rift allocation-placement split.
   - Treat the shared Q2 window/profit-value/backend, region-backed median
     scratch, primitive Q2 cell keys, RunBoth input buffer, region ranking
     objects, reusable top-k arrays, Q2 bounded cell tables, Q1 primitive route
     table, Q1 indexed ranking, Q2 latest-empty taxi table, Q2 array-backed
     ranking, Q2 taxi-id table, output-snapshot placement, packed Grid cell
     keys, and direct output writing as implemented.
   - Do not reintroduce reset-per-event result snapshots; the reusable top-k
     arrays are the lower-overhead replacement.
   - Do not redo the small binary top-candidate heap variant without a
     different comparison strategy; it was measured and lost.
   - Replace remaining heap allocation pressure only where the change preserves
     the same logical query for heap and Rift, or where the only difference is
     allocation placement. The current evidence target is "structured-lifetime
     Scala objects now live in regions," not "Rift invented a different DEBS
     algorithm."
   - Treat the earlier uncommitted Q1 indexed-heap warning as superseded by the
     measured Q1 indexed-ranking checkpoint in this handoff.
5. For the next DEBS change, rerun 100k and 1M instrumented medians before
   making any headline throughput claim. The most useful controls now are
   same-run full-month heap/checked repeats with the pool cap, Commix/SafeZone
   DEBS modes, and stronger safe API coverage for the child-window object
   patterns already used in the benchmark.
6. Extend the literature methodology harnesses only as needed:
   - Upgrade the 40-epoch, 500k-document-per-epoch single run to a median run
     only if we need a headline Broom-style methodology table.
   - Add a short note comparing the local percentages against the Broom paper's
     reported SELECT/AGGREGATE/JOIN reductions without claiming exact
     reproduction.
   - Consider SafeZone trace counters if current vs improved SafeZone needs
     root-bookkeeping attribution at Broom scale.

What should not be done yet:

- Do not claim Rift has final DEBS application-level evidence. The current
  bounded-sample checked RunBoth medians, trusted byte-output medians, and
  allocation-attribution result are stronger than earlier checkpoints, and the
  pool-cap/`ChildBucket` follow-up now gives a same-order full-month 3-run
  median. Per-family attribution found and fixed a major Q1 rank lifetime
  problem, and the post-fix full-month control is now near-tie on elapsed with
  much better checked RSS. SafeZone 1M controls and checked Q1/Q2 process
  diagnostics now exist. The project still needs Q1 rank-refresh overhead
  reduction, optional full-month SafeZone controls, and stronger safe API
  controls.
- Do not move to Phase 6/7 as if Phase 5 is complete.
- Do not treat the literature sequence as proving final application evidence.
  It produced strong Broom/StreamFlex signals, mixed-but-good Yak evidence, and
  a Stancu-style Rift-vs-heap win after batching/fixed counters.
- Do not optimize random runtime code before confirming whether the cost is
  allocator/runtime overhead or an avoidable API/lifetime shape.
- Do not compare Rift raw-array pipeline directly against `ZoneParVector` as if the APIs are equivalent.
- Do not treat local Phase 5 commits as shared provenance until they are pushed.

What needs remeasurement:

- DEBS after any further Q1/Q2 ranking/median/output region-heavy changes.
- Commix comparisons where supported.
- SafeZone or improved SafeZone DEBS modes if meaningful.
- Controlled full-month DEBS reruns with external real/user/sys time.
- Pipeline if a real Rift-backed collection API is added.

What is stable enough:

- Improved SafeZone changes the baseline materially.
- Rift has runtime-only wins on GCBench and linked ListOfLists in the current harness.
- Layout/topology effects are large and must be reported separately.
- Region memory is not GC-scanned, so unrooted region-to-GC references can corrupt correctness.
- Current DEBS GC collection time and heap allocation-attribution counters are
  much lower after the Q2 top-cache and byte-output checkpoints, and Rift RSS
  is lower. Process diagnostics now show the key remaining checked CPU shape:
  Q2 performs the same logical operations as heap, and Q1 pays extra
  rank-object refresh allocation to keep objects in child-bucket lifetimes.
  Q1/Q2 CPU, I/O, and remaining controls still matter.

## 11. Do-Not-Redo Notes

- Do not restart from `/Users/siyaoliu/rift/rift-bootstrap`; it is Phase 1 provenance only.
- Do not use `/Users/siyaoliu/rift/scala-native` as the active Rift branch; it is an older SafeZone/topology investigation worktree.
- Do not treat old SafeZone pathologies as the only baseline. Always include improved SafeZone if SafeZone is in scope.
- Do not rerun raw DEBS monthly files without sorting by dropoff timestamp; raw files are not monotonic by dropoff time.
- Do not store heap objects inside Rift region structures unless they are otherwise rooted or the GC can see the reference.
- Do not use the original full-rescan Q1/Q2 ranking approach; it made the 100k heap run take `246360.864 ms`.
- Do not confuse the earlier backed-out Q1 indexed-heap experiment with the
  current measured Q1 indexed-ranking checkpoint. The current checkpoint is
  implemented and validated; future Q1 work should preserve its shared
  heap/Rift algorithm shape.
- Do not treat the packed `Grid.cellKeyOrZero` checkpoint as a Rift-specific
  win. It removes accidental temporary allocation from the shared heap/Rift
  logical program.
- Do not use the abandoned Scala-side phase-counter outputs under
  `/tmp/debs2015-runboth-phase-gc-alloc-100000` or
  `/tmp/debs2015-runboth-phase-gc-alloc-1000000`; those runs are polluted by
  counter reads that allocated in the hot path. Use the `*-fixed-*` C-side
  phase-bucket directories instead.
- Do not present the pipeline surrogate as a tracked-source reproduction of the old pipeline benchmark.
- Do not treat single-run DEBS ordering as stable. A later current-binary single run showed Rift HPZone slightly faster than heap, while earlier single runs showed Rift slower.
- Do not ignore macOS sandboxing. `sbt` needs access to `~/.sbt`, and `/usr/bin/time -l` needed escalation to read RSS correctly.
- Do not assume `.git` is a directory in this worktree.

## Read These First

1. `docs/HANDOFF.md`
2. `DESIGN.md`
3. `ROADMAP.md`
4. `/Users/siyaoliu/rift/docs/Rift Literature Review.md`
5. `docs/LITERATURE_BENCHMARK_CONTRACT.md`
6. `/Users/siyaoliu/rift/Claude_output/CODEX.md`
7. `sandbox/PHASE0_BASELINES.md`
8. `sandbox/PHASE4_EXIT.md`
9. `sandbox/DATAFLOW_REGION_MATRIX.md`
10. `sandbox/STREAMFLEX_REGION_MATRIX.md`
11. `sandbox/YAK_REGION_MATRIX.md`
12. `sandbox/STANCU_REGION_MATRIX.md`
13. `bench/debs2015/RESULTS.md`

## Safe Next Action

The implementation branch now contains the merged checked API slice,
median-backed Q2 incremental-median checkpoint, JVM RunBoth comparison, Stancu
boundary evidence, checked guard narrowing for trusted-vs-checked region
allocation, region-backed RunBoth latency buffers, Q2 rank/output
attribution, the shared Q2 top-10 cache checkpoint with 100k/1M medians, and
opt-in GC allocation attribution counters plus clean C-side phase buckets. It
also contains the shared byte-output RunBoth checkpoint with 100k/1M medians
and the Yak external-sort-shaped grouped-sort, top-word/filter, and
GraphChi-like subinterval checkpoints, plus checked safe-API probes for those
object patterns. It now also contains a growable checked owner-token
`RegionBuffer` plus a focused `CheckedRegionBufferMatrix` benchmark-shaped
safe-API example, and Dataflow SELECT/AGGREGATE/JOIN now have checked
RegionBuffer/table modes. It also now contains two DEBS-shaped checked API
probes. `Debs2015Q1CheckedOutputRun` materializes Q1 output/ranking objects
inside `RiftRegion.streaming`/`reset` with checked Scala objects and
`RegionBuffer`, and matched heap output on sample and 100k sorted input.
`Debs2015Q1CheckedProcessingRun` goes further: it stores Q1 per-second buckets,
live route events, route/rank arrays, and ranking objects in checked regions
and matched heap output on sample, 100k sorted, and 1M sorted inputs. The latest
variant uses `RiftRegion.childWindow`, one child streaming region per Q1 bucket,
path-dependent `bucket.RouteEvent` nodes in that child region, and closes the
child region at bucket eviction. This restores the production reclaim lifetime
for Q1 event nodes, but it is still safe-API feasibility evidence rather than
final DEBS proof: Q1 rank objects now use child bucket regions in the latest
RunBoth path, but `childWindow`/`ChildBucket` still does not provide a global
affine close guarantee.

`Debs2015Q2CheckedProcessingRun` now covers that Q2 slice as a standalone
checked-processing probe. It uses `RiftRegion.childWindow` for Q2 profit and
empty-taxi windows, region-owned `ProfitEntry`/`EmptyEntry` records,
region-backed median heaps, checked `CheckedProfitableArea` rank objects,
bounded per-cell arrays, taxi-id entries/bytes, and reusable top-k storage.
Where parent-lived control metadata intentionally retains child-window entries
until eviction, it uses the explicit owner-token
`RiftRegion.childRegion(stream, window)` accessor. `ProfitStats` remains heap
control metadata captured by the stream because the current checked lowering
rejected region allocation of the local control class.
The probe matched heap output on sample, 100k sorted, and 1M sorted inputs; the
100k and 1M checked runs were modestly faster in single-run diagnostics.

RunBoth now has a checked integration mode, `q1_mode=rift-checked`.
`Debs2015Q1CheckedProcessingRunner` and
`Debs2015Q2CheckedProcessingRunner` expose capture-aware checked processor
adapters, so `Debs2015RunBoth` can run both checked processors in one shared
byte-parser loop without exposing region-captured implementation types. Sample,
100k, and 1M single runs matched heap Q1/Q2 outputs after stripping latency.
The follow-up 100k/1M median matrix over `heap`, `rift-hp`,
`rift-streaming`, and `rift-checked` also completed with matching outputs.
This is still not final DEBS proof: the byte-reader/output scratch buffers
still use trusted runtime helpers, previous-output snapshots are heap primitive
control metadata, and child close discipline is structured but not
affine-proved. The SafeZone DEBS gap described here was later narrowed by the
single-run closeable SafeZone control recorded at the top of this handoff.

With checked RunBoth medians and attribution in place, the safest next
technical action is either a reusable checked bucket/window abstraction with a
stronger static close proof, or the remaining DEBS CPU work. The remaining
DEBS work is no longer basic SafeZone/control instrumentation: it is
generalizing the accepted Q1 window-rank arena into a reusable checked
rank/window API, lowering checked rank/container CPU cost, and optional
full-month SafeZone context.

Latest validation for this step:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"` passed `52/52` after direct child-window close rejection was added.
- After the `ChildWindow` refactor, Q1 checked-processing matched heap output after stripping latency on sample, 100k sorted, and 1M sorted inputs.
- Post-refactor Q1 single runs: sample heap `0.266 ms` vs checked `0.351 ms`; 100k heap `738.999 ms` vs checked `652.811 ms`; 1M heap `6803.066 ms` vs checked `6024.772 ms`.
- After the `ChildWindow`/`childRegion` refactor, Q2 checked-processing matched heap output after stripping latency on sample, 100k sorted, and 1M sorted inputs.
- Post-refactor Q2 single runs: sample heap `5.526 ms` vs checked `5.895 ms`; 100k heap `692.603 ms` vs checked `661.308 ms`; 1M heap `6800.401 ms` vs checked `6316.186 ms`.
- `DEBS2015_BOTH_MODES="heap rift-checked" zsh bench/debs2015/run_both_instrumented_matrix.sh` matched sample RunBoth Q1/Q2 outputs after stripping latency.
- Post-integration RunBoth 100k single run: heap `472.415 ms`, `8.389 ms` GC, `55459840` RSS vs `rift-checked` `447.141 ms`, `0.072 ms` GC, `39878656` RSS; outputs matched.
- Post-integration RunBoth 1M single run: heap `4932.913 ms`, `20.505 ms` GC, `160022528` RSS vs `rift-checked` `4776.641 ms`, `2.499 ms` GC, `123977728` RSS; outputs matched.
- Checked RunBoth 100k 3-run medians: heap `553.059 ms`, HPZone
  `529.613 ms`, Streaming `512.808 ms`, checked `508.056 ms`; GC medians are
  heap `9.541 ms`, HPZone `0.000 ms`, Streaming `0.000 ms`, checked
  `0.077 ms`; outputs matched.
- Checked RunBoth 1M 3-run medians: heap `5363.257 ms`, HPZone `5224.005 ms`,
  Streaming `5209.104 ms`, checked `5043.240 ms`; GC medians are heap
  `21.226 ms`, HPZone `0.834 ms`, Streaming `0.862 ms`, checked `2.473 ms`;
  outputs matched.
- Checked RunBoth allocation attribution completed for 100k and 1M with
  matching outputs. At 1M, heap allocation calls dropped from `6025149` to
  `752568`, rounded heap bytes from `235159840` to `28785632`, and measured
  heap allocation-call time from `173.578 ms` to `20.514 ms` in
  `rift-checked`.

## Latest Update: Checked Child-Window Close Discipline And Commix Control

Date: 2026-04-27

What changed:

- `RiftRegion.ChildWindow` now tracks closed state. `childRegion(parent,
  window)` checks that the child window is still open, and reusing a closed
  child window throws `IllegalStateException`.
- Direct user `window.close()` is no longer public API; a new
  `RiftRegion.closeChildWindow(parent, window) { cleanup }` helper closes the
  child window after caller cleanup runs with the parent owner token in scope.
- Q1 checked processing now performs route/rank decrement, bucket unlinking,
  parent-visible reference cleanup, and child-window close through the helper.
- Q2 checked processing now uses the same helper for profit and empty-taxi
  bucket windows.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `52/52`; the added negative probe rejects direct user
  `window.close()`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `14/14`; the added runtime probe checks close-through-cleanup and
  child-region reuse rejection after close.
- Sample RunBoth `heap` vs `rift-checked` matched after stripping latency.

Commix control:

The same RunBoth harness was relinked with `GC.commix` and run three times each
at 100k and 1M. Outputs matched heap/Rift after stripping latency.

| Input | Mode | Elapsed ms | GC ms | RSS bytes | Q1 process ms | Q2 process ms | Rift op ms |
|---|---|---:|---:|---:|---:|---:|---:|
| 100k | Commix heap | 492.372 | 4.942 | 56885248 | 142.856 | 122.890 | 0.000 |
| 100k | Commix rift-checked | 472.477 | 0.092 | 39534592 | 137.291 | 117.245 | 1.942 |
| 1M | Commix heap | 4968.773 | 8.206 | 158924800 | 1466.113 | 1369.003 | 0.000 |
| 1M | Commix rift-checked | 4745.291 | 1.137 | 125698048 | 1409.319 | 1251.375 | 11.444 |

Interpretation:

- The close helper is stronger structured discipline, not a complete
  affine/linear lifetime proof. It gives the API and checker a single close
  boundary to harden next.
- The Commix medians match the Immix direction: checked Rift wins elapsed time,
  reduces RSS, and reduces measured GC collection time at both 100k and 1M.
  The 1M elapsed delta is much larger than the GC-time delta, so keep
  interpreting this as allocation-placement/object-churn evidence rather than
  only shorter GC pauses.
- Superseded note: at this point SafeZone DEBS was still missing. A later
  checkpoint added a closeable SafeZone Q1/Q2 control mode; it is still
  single-run evidence and needs medians.

## Latest Update: Reusable Checked ChildBucket

Date: 2026-04-27

What changed:

- Added `RiftRegion.ChildBucket`, a reusable checked wrapper for stream buckets
  that own a child window.
- Added owner-token helpers:
  `RiftRegion.childBucket`, `RiftRegion.childBucketRegion(parent, bucket)`,
  and `RiftRegion.closeChildBucket(parent, bucket) { cleanup }`.
- Migrated Q1 checked-processing buckets and Q2 profit/empty buckets from raw
  `ChildWindow` fields to `ChildBucket`.
- Added compiler probes for child-bucket event graphs and rejection of raw
  `child.window` access.
- Added a runtime smoke for close-through-cleanup and reuse-after-close through
  `ChildBucket`.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `54/54`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `15/15`.
- Sample RunBoth `heap` vs `rift-checked` matched after stripping latency in
  `/tmp/debs2015-runboth-childbucket-sample`.

Interpretation:

- This is a safety/API milestone, not a new performance claim.
- `ChildBucket` centralizes the checked child-lifetime shape for stream
  operators and removes raw child-window fields from Q1/Q2 checked processing.
- It still does not prove affine close. The next safe-API target is a typed
  cleanup/unlink obligation, or compiler support for a linear close token.

## Latest Update: Full-Month DEBS Control And External Time Columns

Date: 2026-04-27

What changed:

- Generated a full January joined/sorted DEBS input with
  `DEBS2015_LIMIT=0`, producing `/tmp/debs2015-month1-full.csv`.
- Ran a first full-month RunBoth control for `heap` and `rift-checked`.
- Updated `bench/debs2015/run_both_instrumented_matrix.sh` so `summary.tsv`
  records external `/usr/bin/time` fields:
  `time_real_s`, `time_user_s`, and `time_sys_s`.
- Verified the harness change on `bench/debs2015/sample_both.csv`; heap and
  checked outputs still matched after stripping latency.

Validation:

- Full-month input rows: `14776615`.
- Full-month RunBoth parsed rows: `14776529`; invalid rows: `86`.
- Q1/Q2 outputs matched between heap and `rift-checked` after stripping only
  latency.
- Output counts: Q1 `274667`, Q2 `180215`.

First full-month single-run rows:

| Mode | Elapsed s | External real s | User+sys s | GC s | RSS MiB | Region objects | Opens/closes |
|---|---:|---:|---:|---:|---:|---:|---:|
| heap | 69.754 | 69.78 | 69.64 | 0.288 | 596.0 | 0 | 0 / 0 |
| rift-checked | 1258.714 | 1258.76 | 63.97 | 0.143 | 981.7 | 68834523 | 6890164 / 6890164 |

Interpretation:

- This is a full-month correctness and scale checkpoint, not a wall-clock
  performance result.
- The checked row was descheduled or otherwise waited externally: wall time was
  about `1259 s`, but user+sys CPU time was only about `64 s`. Do not cite the
  checked `1258.714 s` elapsed value as a Rift performance result.
- The scale counters point to the next technical pressure: checked RunBoth
  creates about `6.89M` child buckets and retains enough slab memory to reach
  about `982 MiB` RSS on this run. The next full-scale work should reduce
  bucket churn / slab retention, then rerun controlled full-month comparisons
  with external time columns.

## Latest Update: Streaming First-Slab And Pool-Cap Runtime

Date: 2026-04-27

What changed:

- Updated the in-tree Rift runtime backend in
  `scala-native-rift/nativelib/src/main/resources/scala-native/rift/RiftRuntime.c`.
- Streaming regions now start with a page-sized first slab, while overflow
  still uses regular `32 KiB` slabs.
- The global closed-slab pool is capped at `128 MiB`; slabs beyond the cap are
  returned to the OS with `munmap`.
- Public C and Scala APIs are unchanged. This is a backend change, not a DEBS
  algorithm specialization.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" "set Compile / mainClass := Some(\"debs2015.Debs2015RunBoth\")" nativeLink`
  passed.
- `DEBS2015_BOTH_BUILD=0 DEBS2015_BOTH_MODES="heap rift-checked"`
  instrumented RunBoth passed on 100k and 1M bounded inputs; Q1/Q2 outputs
  matched after stripping only latency.
- `DEBS2015_BOTH_BUILD=0 DEBS2015_BOTH_MODES="rift-checked"` completed on
  `/tmp/debs2015-month1-full.csv`; Q1/Q2 outputs matched the earlier
  full-month heap outputs from `/tmp/debs2015-runboth-fullmonth-childbucket`
  after stripping latency.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `15/15`.

Bounded single-run checks after the runtime change:

| Input | Mode | Elapsed s | User+sys s | GC s | RSS MiB | Rift op s | Pool MiB | Mmap MiB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 100k | heap | 0.443 | 0.44 | 0.008 | 52.9 | 0.000 | 0.0 | 0.0 |
| 100k | rift-checked | 0.435 | 0.43 | 0.000 | 38.5 | 0.001 | 9.3 | 30.3 |
| 1M | heap | 4.778 | 4.76 | 0.022 | 151.5 | 0.000 | 0.0 | 0.0 |
| 1M | rift-checked | 4.381 | 4.37 | 0.002 | 121.0 | 0.012 | 65.8 | 94.8 |

Full-month checked row after the runtime change:

| Mode | Parsed | Elapsed s | External real s | User+sys s | GC s | RSS MiB | Rift op s | Pool MiB | Mmap MiB | Region objects | Opens/closes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rift-checked | 14776529 | 70.831 | 70.87 | 68.86 | 0.166 | 846.0 | 0.998 | 128.0 | 864.4 | 68834523 | 6890164 / 6890164 |

Comparison to the first checked full-month run:

| Metric | Before cap | After cap |
|---|---:|---:|
| External real time | 1258.76 s | 70.87 s |
| External user+sys time | 63.97 s | 68.86 s |
| Pool bytes at metrics snapshot | 780.4 MiB | 128.0 MiB |
| Peak RSS | 981.7 MiB | 846.0 MiB |
| Cumulative Rift mmap bytes | 932.5 MiB | 864.4 MiB |
| Rift op time | 0.679 s | 0.998 s |

Same-run full-month control after the pool cap:

| Mode | Parsed | Elapsed s | External real s | User+sys s | GC s | RSS MiB | Rift op s | Pool MiB | Mmap MiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 14776529 | 71.919 | 71.96 | 69.58 | 0.323 | 579.1 | 0.000 | 0.0 | 0.0 |
| rift-checked | 14776529 | 77.947 | 77.98 | 74.24 | 0.190 | 695.2 | 1.137 | 128.0 | 864.4 |

Interpretation:

- The first checked full-month wall-clock row was scheduler polluted; the
  pool-cap run has wall time and user+sys time in the same range.
- The pool cap fixes the closed-slab retention issue enough to make full-month
  checked runs practical under controlled load.
- The same-run control was the first same-binary full-month heap/checked
  pool-cap data point. Checked was about `6.0 s` slower than heap on that
  single run, while measured GC collection time was lower by about `0.13 s`.
- Peak RSS is much closer to heap than before the cap but still higher:
  `695.2 MiB` checked versus `579.1 MiB` heap. Remaining memory pressure is not
  just closed-slab retention; long-lived parent-stream tables, rank objects,
  taxi-id metadata, and live window data still dominate at full-month scale.
- This is a single same-run control, not a final Phase 5 result. The next
  full-scale evidence should be repeated heap/checked medians with the pool cap
  in place, plus SafeZone/Commix controls where meaningful.

## Latest Update: Checked ChildBucket Single-Control-Object Runtime

Date: 2026-04-28

What changed:

- Updated `RiftRegion.ChildBucket` in
  `scala-native-rift/nativelib/src/main/scala-next/scala/scalanative/memory/RiftRegion.scala`.
- `ChildBucket` now owns the child `StreamingRegion` directly instead of
  wrapping a separate `ChildWindow`.
- `RiftRegion.childBucket` now creates one heap control object per child bucket
  instead of one `ChildWindow` plus one `ChildBucket`.
- `RiftRegion.closeChildBucket` still provides the structured cleanup boundary,
  but now checks/closes the bucket directly.

Validation:

- `nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest`
  passed `54/54`.
- `tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest` passed
  `15/15`.
- 1M heap-vs-checked RunBoth outputs matched.
- Full-month trusted Streaming and full-month checked RunBoth outputs matched
  heap after stripping latency.

Key rows:

| Control | Mode | Elapsed s | GC s | RSS MiB | Rift op s | Evidence |
|---|---|---:|---:|---:|---:|---|
| full-month trusted backend | heap | 73.888 | 0.360 | 595.7 | 0.000 | single run |
| full-month trusted backend | rift-streaming | 68.990 | 0.088 | 801.7 | 0.898 | single run |
| 1M post-change | heap | 4.810 | 0.020 | 152.6 | 0.000 | single run |
| 1M post-change | rift-checked | 4.678 | 0.002 | 119.9 | 0.017 | single run |
| full-month post-change | heap | 70.872 | 0.315 | 586.4 | 0.000 | single run |
| full-month post-change | rift-checked | 65.928 | 0.086 | 866.6 | 0.816 | single run |
| reverse-order post-change | rift-checked | 68.435 | 0.086 | 910.7 | 0.893 | usable checked row |
| reverse-order post-change | heap | 1871.373 | 0.401 | 583.3 | 0.000 | invalid wall-clock row |

Interpretation:

- The trusted `rift-streaming` row shows the post-pool-cap region backend can
  beat heap at full-month scale. The remaining problem was checked API shape,
  not raw region allocation.
- The `ChildBucket` simplification removes a general checked streaming overhead
  on the hot path. DEBS full-month opens about `6.89M` child buckets, so one
  fewer heap control object per bucket matters.
- The two usable checked full-month rows after the change are `65.928 s` and
  `68.435 s`, versus the earlier pre-change checked row `77.947 s`.
- RSS did not improve. Checked full-month RSS is `866-911 MiB` in these runs
  even with the pool capped at `128 MiB`. Do not claim this as a memory
  footprint win.
- The reverse-order heap row is invalid because wall time was `1871.42 s` but
  user+sys time was only about `89.32 s`.
- This single-run section is superseded by the 3-run median follow-up below.

## Latest Update: Full-Month ChildBucket Median Follow-Up

Date: 2026-04-28

What changed:

- Ran two more same-order full-month heap/checked controls after the
  single-control-object `ChildBucket` change.
- Combined those rows with the first same-order post-change run, giving a
  3-run median for full-month checked DEBS.
- Updated `bench/debs2015/RESULTS.md` and synced it into
  `evidence/DEBS_RESULTS.md`.

Same-order full-month medians:

| Mode | Elapsed s | External real s | User+sys s | GC s | RSS MiB | Rift op s | Q1 process s | Q2 process s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 73.029 | 73.06 | 71.05 | 0.315 | 586.4 | 0.000 | 20.507 | 22.154 |
| rift-checked | 67.670 | 67.69 | 67.18 | 0.086 | 866.6 | 0.885 | 19.233 | 20.142 |

Interpretation:

- Median elapsed improves by `5.359 s`, about `7.3%`, for checked Rift over
  heap on the full-month input.
- Median measured GC collection time drops from `0.315 s` to `0.086 s`, so the
  elapsed win is larger than GC pause-time reduction alone.
- The result is noisy: repeat A had checked slower (`75.100 s` checked versus
  `73.166 s` heap), while the other same-order rows and the usable
  reverse-order checked row were faster.
- RSS is still the main regression: checked median RSS is `866.6 MiB` versus
  heap `586.4 MiB`, and one checked repeat reaches `983.9 MiB`.
- This is now median-backed full-month DEBS evidence, but still not final Phase
  5 proof. The next claim-level work is SafeZone full-month comparison and
  the Q1 rank lifetime diagnosis described below.

## Latest Update: Rift Active-Memory Diagnostics

Date: 2026-04-28

What changed:

- Added runtime counters for current/peak mapped slabs and bytes.
- Added runtime counters for current/peak active-region slabs and bytes.
- Added requested-allocation byte counters for total requested region bytes and
  current/peak active requested bytes.
- Exposed the counters through `RiftAllocator`, `Debs2015RunBoth`, and the
  instrumented RunBoth TSV output.
- Updated `bench/debs2015/RESULTS.md` and synced it into
  `evidence/DEBS_RESULTS.md`.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- 100k heap-vs-checked RunBoth outputs matched after stripping latency.
- Full-month checked-only RunBoth completed as a memory-attribution diagnostic.

Key rows:

| Input | Mode | Elapsed | RSS bytes | Peak mapped bytes | Peak active mapped bytes | Peak active requested bytes | Final mapped bytes | Pool bytes |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 100k | rift-checked | 511.224 ms | 40239104 | 31817728 | 31670272 | 29575648 | 10010624 | 9748480 |
| month 1 full | rift-checked | 73.457 s | 1086668800 | 906346496 | 904790016 | 823153856 | 134479872 | 134217728 |

Interpretation:

- The full-month RSS regression is not mostly closed-slab pool retention:
  final active bytes return to zero, and final mapped bytes are near the
  `128 MiB` pool cap.
- Peak RSS tracks live region memory. Peak active requested bytes are about
  `823 MB`; peak active mapped bytes are about `905 MB`. Slab/slack overhead
  is real but not the dominant factor.
- This diagnostic led directly to the region-family attribution and Q1 rank
  lifetime fix described next.

## Latest Update: Checked Q1 Rank Object Lifetime

Date: 2026-04-28

What changed:

- Added opt-in region-family attribution via
  `DEBS2015_RIFT_FAMILY_STATS=1`.
- Labeled DEBS checked regions as input, snapshot, checked parent, Q1 window,
  Q2 profit window, and Q2 empty window.
- Moved Q1 checked `CheckedCell`/`CheckedRoute`/`CheckedRankedRoute`
  allocation from the parent checked stream into the current Q1 child bucket.
- The Q1 logical ranking algorithm is unchanged; only the region lifetime of
  the rich route/rank object graph changed.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- 100k heap/checked family-stat run matched outputs.
- Full-month checked output matched the earlier full-month heap output after
  stripping latency.
- 1M non-family heap/checked sanity run matched outputs.

Key rows:

| Input | Variant | RSS bytes | Active requested peak | Parent active requested peak | Q1-window active requested peak |
|---|---|---:|---:|---:|---:|
| month 1 full | before | 1086668800 | 823153856 | 808569032 | 455016 |
| month 1 full | after | 613318656 | 180948200 | 164271664 | 2426752 |
| 1M non-family | heap | 160088064 | 0 | 0 | 0 |
| 1M non-family | rift-checked | 66715648 | 34749280 | 0 | 0 |

Interpretation:

- The full-month memory problem was not "regions are too expensive" in the
  abstract. The dominant issue was a wrong checked lifetime: Q1 rank object
  graphs were ordinary Scala objects in regions, but they were placed in a
  run-lifetime parent region.
- Moving those rank objects to child bucket regions keeps the ordinary-object
  design target while making the region lifetime match the data lifetime.
- The 1M row is a single sanity control, not a new median. The repeated
  full-month control is recorded in the next section.

## Latest Update: Post-Fix Full-Month Control

Date: 2026-04-28

Validation:

- Ran three full-month `heap`/`rift-checked` repeats without family-stat
  attribution.
- Output diffs passed for Q1 and Q2 in all repeats after stripping latency.
- Result directories:
  `/tmp/debs2015-runboth-q1-rank-window-fullmonth-repeat-a`,
  `/tmp/debs2015-runboth-q1-rank-window-fullmonth-repeat-b`, and
  `/tmp/debs2015-runboth-q1-rank-window-fullmonth-repeat-c`.

3-run medians:

| Mode | Elapsed s | Real s | GC s | RSS MiB | Rift op s | Active requested peak MiB | Q1 process s | Q2 process s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 67.122 | 67.15 | 0.285 | 595.9 | 0.000 | 0.0 | 18.537 | 17.849 |
| rift-checked | 66.804 | 66.83 | 0.117 | 613.3 | 0.779 | 172.6 | 20.407 | 18.763 |

Interpretation:

- The Q1 rank lifetime fix removes the major checked RSS regression at
  full-month scale.
- Elapsed time is a near-tie, not a strong application speedup.
- Checked still reduces GC collection time, but that saves only about
  `0.168 s` at the median while checked pays about `0.779 s` in Rift
  operation timing and slower Q1/Q2 process phases.
- The next useful DEBS work is generalizing the Q1 window-rank arena into a
  lower-overhead/richer checked rank/window API and strengthening close
  discipline.

## Latest Update: Checked Q1 Window Rank Arenas

Date: 2026-04-28

What changed:

- Added separate Q1 rank buckets in
  `scala-native-rift/sandbox/src/main/scala-next/debs2015/Debs2015Q1CheckedProcessingRun.scala`.
- The existing per-second event buckets still hold `RouteEvent` nodes and drive
  eviction. The new rank buckets hold ordinary Scala `CheckedCell`,
  `CheckedRoute`, and `CheckedRankedRoute` object graphs.
- Rank buckets use the Q1 window length (`30 min`). A rank bucket is closed
  only after every event in the bucket interval has left the sliding window.
- If a route is refreshed inside the same rank bucket, checked Q1 mutates the
  existing region object graph and fixes the rank heap. If it crosses a rank
  bucket boundary, checked Q1 allocates a new rank object graph in the later
  bucket.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- Sample RunBoth `heap`/`rift-checked` outputs matched in
  `/tmp/debs2015-runboth-q1-rankbucket-sample`.
- 100k and 1M diagnostic heap/checked runs matched outputs.
- 1M non-diagnostic 3-run heap/checked medians matched outputs.
- One full-month heap/checked scale check matched outputs.

1M non-diagnostic medians:

| Mode | Elapsed ms | Real s | GC ms | RSS MiB | Rift op ms | Q1 process ms | Q2 process ms | Q1 rank created |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 4601.532 | 4.61 | 20.335 | 153.7 | 0.000 | 1406.251 | 1169.163 | 573523 |
| rift-checked | 4610.413 | 4.61 | 2.304 | 63.9 | 7.577 | 1489.462 | 1175.684 | 725262 |

Full-month single-run scale check:

| Mode | Elapsed s | Real s | User+sys s | GC ms | RSS MiB | Rift op ms | Q1 process s | Q2 process s | Q1 rank created |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 72.445 | 72.48 | 70.65 | 304.485 | 594.4 | 0.000 | 20.726 | 20.853 | 6195167 |
| rift-checked | 72.556 | 72.58 | 72.05 | 86.404 | 447.8 | 949.899 | 22.368 | 21.915 | 8842434 |

Interpretation:

- This is a general streaming-lifetime pattern, not a DEBS-only algorithm
  change: event records can live in fine buckets while rank/output snapshots
  live in coarser arenas whose close point follows the query window.
- It cuts checked Q1 rank churn without the rejected one-child-region-per-route
  design. At full-month scale, checked rank objects fall from the previous
  `14487771` per-refresh count to `8842434`.
- It does not fully match heap's durable-rank count because routes that remain
  active across a rank-window boundary must receive a new region object graph
  in the later arena.
- The bounded 1M result is an elapsed near-tie, while the full-month single
  row is mainly a memory/lifetime success: checked RSS is lower than heap in
  this row. It needs repeated full-month medians before becoming a throughput
  claim.
- The next framework work should expose this as a lower-overhead/richer checked
  window/ranking API and add stronger static close-discipline tests.

## Latest Update: Checked StreamBucketArena API

Date: 2026-04-28

What changed:

- Added `RiftRegion.StreamBucket` and `RiftRegion.StreamBucketArena` in
  `scala-native-rift/nativelib/src/main/scala-next/scala/scalanative/memory/RiftRegion.scala`.
- Added owner-token helpers:
  `streamBucketArena`, `streamBucketFor`, `streamBucketRegion`,
  `closeStreamBucketsBefore`, `closeAllStreamBuckets`, and a stream-bucket
  diagnostic tagging overload.
- Migrated checked Q1 rank buckets in
  `scala-native-rift/sandbox/src/main/scala-next/debs2015/Debs2015Q1CheckedProcessingRun.scala`
  from a local `RankBucket` linked list to the reusable arena API.
- Added compiler probes in
  `scala-native-rift/nscplugin/src/test/scala-next/scala/RiftRegionCheckedCompilerTest.scala`
  and native runtime coverage in
  `scala-native-rift/unit-tests/native/src/test/scala-next/scala/scala/scalanative/memory/RiftRegionCheckedTest.scala`.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `65/65`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `16/16`.
- Sample RunBoth `heap`/`rift-checked` outputs matched in
  `/tmp/debs2015-runboth-stream-bucket-api-sample`.
- 100k RunBoth `heap`/`rift-checked` outputs matched in
  `/tmp/debs2015-runboth-stream-bucket-api-100000`.

100k single-run correctness control:

| Mode | Elapsed ms | GC ms | Rift op ms | Q1 process ms | Q2 process ms | Q1 rank created |
|---|---:|---:|---:|---:|---:|---:|
| heap | 513.196 | 8.817 | 0.000 | 148.498 | 127.213 | 64672 |
| rift-checked | 489.514 | 0.079 | 1.528 | 153.595 | 110.926 | 77974 |

Interpretation:

- This is a general framework change: the reusable stream-bucket arena is the
  checked primitive behind the accepted "fine event buckets plus coarser
  rank/output arenas" pattern.
- It is not yet a complete rank/window collection API. The arena owns child
  bucket lifetime and close sequencing; operators still own per-query cleanup,
  indexes, ordering, and result semantics.
- The implementation uses trusted private heap metadata internally, similar to
  existing checked containers. Public operations reattach the parent owner
  token before exposing buckets or child regions.
- The 100k row is not a new median or final DEBS claim. It is a migration
  correctness/control row after moving Q1 onto the reusable primitive.
- Next useful work: build lower-overhead/richer checked rank/window
  collections on this primitive and strengthen close discipline.

## Latest Update: Checked StreamWindowIndexedRank API

Date: 2026-04-28

What changed:

- Added `RiftRegion.StreamWindowIndexedRank` in
  `scala-native-rift/nativelib/src/main/scala-next/scala/scalanative/memory/RiftRegion.scala`.
- Added owner-token helpers for opening window buckets, inserting/updating
  ranked values, peeking/popping ranked values, removing keys, querying length,
  and closing window buckets.
- Extended the Scala 3 lowering guard in
  `scala-native-rift/nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirGenExpr.scala`
  so `putWindowRank` rejects direct unrooted heap objects.
- Added compiler probes and a native runtime smoke for storing ordinary Scala
  objects allocated in a child window region, removing them before close, and
  rejecting direct heap values.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `67/67`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `17/17`.

Interpretation:

- This is the first higher-level checked rank/window collection above
  `StreamBucketArena`. It is framework work, not a DEBS algorithm change.
- It gives stream operators a reusable way to keep dense-key rank state in a
  parent stream while placing ranked objects in child-window regions.
- This original API required explicit key removal before bucket close. The
  follow-up auto-cleanup checkpoint below supersedes that manual cleanup path for
  new code using `putWindowRankInBucket`.
- The API is intentionally narrow: dense integer keys and one `Long` priority.
  DEBS Q1 still needs richer tie-breaking or a specialized comparator layer;
  Q2 can use the shape more directly if future clean/full-month diagnostics
  justify integration.

## Latest Update: Checked StreamWindowIndexedRank Matrix

Date: 2026-04-28

What changed:

- Added
  `scala-native-rift/sandbox/src/main/scala-next/CheckedStreamWindowRankMatrix.scala`.
- Added
  `scala-native-rift/sandbox/run_checked_stream_window_rank_matrix.sh`.
- Added result pack
  `scala-native-rift/sandbox/CHECKED_STREAM_WINDOW_RANK_MATRIX.md` and synced
  it into `evidence/CHECKED_STREAM_WINDOW_RANK_MATRIX.md`.
- Updated `scripts/sync-evidence.sh` so future evidence syncs include this
  result pack.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- Smoke matrix native-linked `CheckedStreamWindowRankMatrix`.
- Smoke heap and `rift-checked` modes matched checksum
  `-3490531581377742567`.
- Default local heap and `rift-checked` modes matched checksum
  `6881312641757835670`.

Default local median from the original manual-cleanup path:

| Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | Opens / closes / resets | Peak RSS bytes |
|---|---:|---:|---:|---:|---:|---:|
| heap | 199.762 | 0.000 | 0.000 | 0 | 0 / 0 / 0 | 145833984 |
| rift-checked | 254.050 | 7.876 | 0.369 | 826642 | 41 / 41 / 0 | 93585408 |

Interpretation:

- This is framework/API evidence, not a DEBS result.
- The same logical stream-window ranking program runs on heap and checked
  Rift. The checked path allocates ordinary Scala records in child bucket
  regions, ranks them through parent-owned checked state, samples top records,
  and removes parent-visible references before bucket close.
- The first median is not a speed win. Checked Rift is slower despite low
  measured Rift runtime cost and lower RSS. This points to CPU overhead in the
  current checked window/rank container shape.
- Next useful work: add a lower-overhead richer rank API with
  comparator/tie-breaker/hash-key support before broad DEBS Q1 integration.

## Latest Update: StreamWindowIndexedRank Auto Cleanup

Date: 2026-04-28

What changed:

- Added `RiftRegion.putWindowRankInBucket(parent, rank, bucket, key, value, priority)`.
- `StreamWindowIndexedRank` now records the owning child bucket for each dense
  key with per-key previous/next links.
- `closeWindowRankBucketsBefore` and `closeAllWindowRankBuckets` now remove
  tracked keys from parent-owned rank state before closing the child bucket.
- The Scala 3 lowering guard now rejects direct unrooted heap objects passed
  through `putWindowRankInBucket`, matching the older `putWindowRank` guard.
- `CheckedStreamWindowRankMatrix` now relies on the framework cleanup path for
  parent rank unlinking instead of manually removing keys in the harness cleanup
  callback.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `69/69`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `19/19`.
- 100k auto-cleanup smoke matched checksum `-476315670107920613`.
- Default local auto-cleanup matrix matched checksum `6881312641757835670`.

Auto-cleanup matrix results:

| Input | Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | Opens / closes / resets | Peak RSS bytes |
|---|---|---:|---:|---:|---:|---:|---:|
| 100k | heap | 25.043 | 0.000 | 0.000 | 0 | 0 / 0 / 0 | 20578304 |
| 100k | rift-checked | 33.499 | 0.909 | 0.296 | 82548 | 5 / 5 / 0 | 30556160 |
| 1M | heap | 207.038 | 0.000 | 0.000 | 0 | 0 / 0 / 0 | 145768448 |
| 1M | rift-checked | 313.572 | 7.689 | 0.307 | 826646 | 41 / 41 / 0 | 94732288 |

Interpretation:

- This is a stronger close-discipline checkpoint, not a throughput win.
- The first auto-cleanup implementation used linear unlinking and produced a
  rejected 100k checked smoke time of `1745.677 ms`. The current per-key
  previous/next-link implementation brings that 100k smoke to `33.499 ms`.
- Compared with the previous manual-cleanup 1M checked median (`254.050 ms`),
  automatic cleanup adds CPU overhead while making the safety boundary more
  framework-owned.
- This checkpoint left ownership-bookkeeping overhead and richer ordering open;
  the later lexicographic priority checkpoint covers Q1-style tie-breakers, and
  the later long-key stream-window rank API covers arbitrary route-style keys.
  Lower CPU overhead and application integration remain open before broad DEBS
  Q1 integration.

## Latest Update: StreamWindowIndexedRank Entry Cleanup

Date: 2026-04-29

Child repo commit: `28ccf544023e`.

What changed:

- Added `RiftRegion.closeWindowRankBucketsBeforeWithEntries(...)` and
  `RiftRegion.closeAllWindowRankBucketsWithEntries(...)`.
- These close helpers keep the framework-owned key unlinking from auto cleanup,
  but also report each still-ranked removed entry to the operator before the
  child bucket closes.
- Updated `CheckedStreamWindowRankMatrix` so checked mode cleans `recordByKey`
  through those entry callbacks instead of maintaining a second checked-side
  bucket-local key list.
- A direct heap bucket-reference owner table was tested and rejected before this
  final shape because it regressed the default focused checked median to
  `341.705 ms`.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `70/70`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `21/21`.
- 100k entry-cleanup smoke matched checksum `-476315670107920613`.
- Default local entry-cleanup matrix matched checksum `6881312641757835670`.

Entry-cleanup matrix results:

| Input | Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | Opens / closes / resets | Peak RSS bytes |
|---|---|---:|---:|---:|---:|---:|---:|
| 100k | heap | 22.271 | 0.000 | 0.000 | 0 | 0 / 0 / 0 | 35176448 |
| 100k | rift-checked | 33.840 | 0.901 | 0.117 | 82545 | 5 / 5 / 0 | 29999104 |
| 1M | heap | 200.304 | 0.000 | 0.000 | 0 | 0 / 0 / 0 | 145768448 |
| 1M | rift-checked | 302.001 | 7.447 | 0.289 | 826643 | 41 / 41 / 0 | 87441408 |

Interpretation:

- This is a modest framework overhead reduction, not a throughput win.
- It improves the previous auto-cleanup default checked median (`313.572 ms`)
  and peak RSS (`94732288` bytes), but remains slower than heap and the earlier
  manual-cleanup checked median (`254.050 ms`).
- The result supports keeping the API because it removes duplicate operator
  bookkeeping while preserving the stronger close discipline. It does not yet
  justify direct wholesale DEBS Q1 integration.

## Latest Update: StreamWindowIndexedRank Remove-With-Value Close

Date: 2026-04-29

Child repo commit: `1904bd72623c`.

What changed:

- Added an internal `RegionIndexedPriorityQueue.removeWithValueTrusted` close
  primitive. Bucket close now removes a key and retrieves its ranked value in
  one trusted operation instead of `contains` + `get` + `remove`.
- Added a runtime regression test for the already-popped-key case:
  `closeAllWindowRankBucketsWithEntries` must not report a callback for a rank
  entry that was popped before its owning bucket closes.
- Updated `sandbox/CHECKED_STREAM_WINDOW_RANK_MATRIX.md` and synced the parent
  evidence pack.

Validation:

- `git diff --check` passed in `scala-native-rift`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `22/22`.
- 100k remove-with-value matrix matched checksum `-476315670107920613`.
- Default 1M remove-with-value matrix matched checksum `6881312641757835670`.

Remove-with-value matrix results:

| Input | Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | Opens / closes / resets | Peak RSS bytes |
|---|---|---:|---:|---:|---:|---:|---:|
| 100k | heap | 25.360 | 0.000 | 0.000 | 0 | 0 / 0 / 0 | 35225600 |
| 100k | rift-checked | 38.823 | 1.021 | 0.162 | 82545 | 5 / 5 / 0 | 30015488 |
| 1M | heap | 258.839 | 0.000 | 0.000 | 0 | 0 / 0 / 0 | 145784832 |
| 1M | rift-checked | 355.671 | 8.005 | 0.374 | 826643 | 41 / 41 / 0 | 87441408 |

Interpretation:

- This is framework correctness cleanup, not a speed win.
- The focused matrix is noisy on wall time, but the new close primitive did not
  produce a measured improvement over the prior entry-cleanup checkpoint.
- RSS remains lower for checked Rift, and measured Rift operation time remains
  small. The remaining overhead is likely in checked container/object program
  shape rather than raw region allocator operations.
- The next useful direction is applying the long-key rank-window API to a real
  operator or reducing per-event object/control transitions, not another narrow
  queue method tweak.

## Latest Update: StreamWindowIndexedRank Lexicographic Priority API

Date: 2026-04-29

What changed:

- Added `RiftRegion.regionIndexedPriorityQueueLexicographic` and
  `RiftRegion.streamWindowIndexedRankLexicographic`.
- Added overloads for `put`, `updatePriority`, `putWindowRank`,
  `putWindowRankInBucket`, and `updateWindowRankPriority` that accept four
  lexicographic `Long` priority components. Larger components rank first at
  each tie-break level.
- Updated the Scala 3 checked lowering guard so the new multi-priority put
  overloads still check the stored value argument rather than one of the
  trailing priority arguments.
- Added positive compiler/runtime probes for Q1-style lexicographic ranking and
  a negative compiler probe rejecting direct heap objects through the
  lexicographic bucket-owned put path.

Validation:

- `git diff --check` passed in `scala-native-rift`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `72/72`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `23/23`.
- 100k focused checked stream-window-rank matrix matched checksum
  `-476315670107920613`.
- Default 1M focused matrix matched checksum `6881312641757835670`.

Focused matrix control:

| Input | Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | Opens / closes / resets | Peak RSS bytes |
|---|---|---:|---:|---:|---:|---:|---:|
| 100k | heap | 22.211 | 0.000 | 0.000 | 0 | 0 / 0 / 0 | 35209216 |
| 100k | rift-checked | 37.404 | 0.908 | 0.110 | 82545 | 5 / 5 / 0 | 30031872 |
| 1M | heap | 205.849 | 0.000 | 0.000 | 0 | 0 / 0 / 0 | 145801216 |
| 1M | rift-checked | 329.761 | 7.523 | 0.352 | 826643 | 41 / 41 / 0 | 87457792 |

Interpretation:

- This is a functionality and safety step, not a speed claim.
- It removes the "single `Long` priority only" limitation for dense-key
  checked ranking and supports Q1-style count/time/sequence/key tie-breakers.
- The focused matrix still uses the existing single-priority logical program;
  it is a regression/control row for the shared queue implementation, not a
  lexicographic benchmark.
- Hash-keyed ranking and lower checked-container CPU overhead remain the next
  framework blockers before broad DEBS Q1 integration.

## Latest Update: Q2 CPU Substep Diagnostics

Date: 2026-04-28

What changed:

- Added
  `scala-native-rift/sandbox/src/main/scala-next/debs2015/Debs2015Q2CpuDiagnostics.scala`.
- Added opt-in `DEBS2015_Q2_CPU_DIAGNOSTICS=1` timers around Q2 profit-window
  eviction, empty-window eviction, taxi lookup, previous-empty removal,
  profit path, profit rank, empty path, empty rank, and top-10 extraction.
- Wired the new `diag_q2_cpu_*` fields into
  `scala-native-rift/sandbox/src/main/scala-next/debs2015/Debs2015RunBoth.scala`
  and `scala-native-rift/bench/debs2015/run_both_instrumented_matrix.sh`.
- Updated `scala-native-rift/bench/debs2015/RESULTS.md`,
  `evidence/DEBS_RESULTS.md`, `evidence/ALL_PHASE_RESULTS.md`, and the
  roadmap/handoff notes.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- 100k RunBoth diagnostic matched heap/checked Q1 and Q2 outputs in
  `/tmp/debs2015-q2-cpu-diag-100000`.
- 1M RunBoth diagnostic matched heap/checked Q1 and Q2 outputs in
  `/tmp/debs2015-q2-cpu-diag-1000000`.

Diagnostic rows:

| Input | Mode | Elapsed ms | GC ms | RSS MiB | Q2 process ms | Q2 recorded CPU ms | Taxi lookup ms | Profit path+rank ms | Empty path+rank ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 100k | heap | 527.875 | 10.939 | 52.9 | 145.822 | 126.175 | 39.486 | 31.601 | 16.160 |
| 100k | rift-checked | 493.528 | 0.083 | 34.4 | 133.764 | 114.823 | 36.690 | 25.888 | 16.435 |
| 1M | heap | 4899.388 | 21.190 | 153.8 | 1438.062 | 1246.509 | 413.551 | 270.328 | 161.952 |
| 1M | rift-checked | 4730.741 | 5.596 | 66.0 | 1327.500 | 1142.533 | 364.274 | 263.884 | 158.739 |

Interpretation:

- This is attribution evidence only. The diagnostic inserts `System.nanoTime()`
  calls in Q2's hot path, so it must not replace clean medians.
- Bounded Q2 same-operation overhead is not currently reproduced. Checked Q2
  process time and recorded Q2 CPU substeps are lower than heap at both 100k
  and 1M in these perturbing rows.
- Q2 operation counts remain aligned with heap. The immediate implementation
  focus should move to lower-overhead/richer checked rank APIs and stronger
  bucket/window close discipline, not speculative Q2 substep tuning.

## Latest Update: Hash-Keyed Checked Rank Queue

Date: 2026-04-29

Implementation commit:

- `scala-native-rift` `87c0d5cf3b` (`Add hash-keyed checked rank queue`)

What changed:

- Added `RiftRegion.RegionLongIndexedPriorityQueue[T]` as the long-key
  counterpart to `RegionIndexedPriorityQueue`.
- The new queue stores values, heap keys, priority arrays, and an
  open-addressed long-key index table in region-owned arrays.
- Added single-priority and four-component lexicographic `put`/`updatePriority`
  APIs, plus `get`, `contains`, `remove`, `peek`, `peekKey`, `peekPriority`,
  `pop`, `length`, `capacity`, and `tableCapacity`.
- Extended checked lowering so long-key `put` overloads, including owner-token
  extension syntax, reject direct unrooted heap objects while allowing region
  values and explicit `HeapRoot` handles.
- Added compiler probes for long-key lexicographic ranking, heap-store
  rejection, `HeapRoot` storage, and inner-region rejection.
- Added native runtime smokes for rehash/growth, lexicographic ranking,
  update/remove/pop, and keyed value replacement.

Validation:

- `git diff --check` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"` passed: `76/76`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"` passed: `25/25`.

Interpretation:

- This is Phase 7 API/safety evidence, not a DEBS performance result.
- It removes the standalone dense-key-remapping blocker for route-style packed
  `Long` keys.
- It does not yet make `StreamWindowIndexedRank` hash-keyed. The next framework
  step is composing long-key rank state with bucket ownership/close cleanup, or
  attacking checked container CPU overhead if that integration looks too costly.

## Latest Update: Long-Key Checked Stream-Window Rank

Date: 2026-04-29

Implementation commit:

- `scala-native-rift` `7cde2473c2`
  (`Add long-key checked stream-window rank`)

What changed:

- Added `RiftRegion.StreamWindowLongIndexedRank[T]`, composing
  `StreamBucketArena` with `RegionLongIndexedPriorityQueue`.
- Added region-owned owner-table arrays for bucket-owned arbitrary `Long` keys,
  so the close path can remove parent-visible rank entries before child bucket
  close without a dense remapping layer.
- Added long-key overloads for `streamWindowBucketFor`, `putWindowRank`,
  `putWindowRankInBucket`, `updateWindowRankPriority`, `removeWindowRank`,
  `containsWindowRank`, `getWindowRank`, `peekWindowRank`,
  `peekWindowRankKey`, `peekWindowRankPriority`, `popWindowRank`,
  `windowRankLength`, and close-with-entry helpers.
- Added compiler probes for auto cleanup, close-with-entry callbacks,
  lexicographic long-key ranking, and direct heap-store rejection.
- Added native runtime smokes for rehash/cleanup, key movement between buckets,
  already-popped-key close cleanup, and Q1-style lexicographic priorities.

Validation:

- `git diff --check` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"` passed: `80/80`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"` passed: `28/28`.

Interpretation:

- This is Phase 7 API/safety evidence, not a new DEBS timing row.
- It removes the framework-level blocker for route-style packed `Long` keys in
  checked stream-window rank state.
- Remaining work is either applying this to a real Q1 route-key slice or
  measuring/reducing checked stream-window rank CPU overhead before application
  integration.

## Latest Update: Long-Key Stream-Window Rank Matrix

Date: 2026-04-29

Implementation status:

- `scala-native-rift` `e46813cbb`
  (`Add long-key stream-window rank matrix`)
- `scala-native-rift` `672e56c0f`
  (`Use no-entry close in long-key rank matrix`)

What changed:

- Added `heap-long` and `rift-checked-long` modes to
  `scala-native-rift/sandbox/src/main/scala-next/CheckedStreamWindowRankMatrix.scala`.
- Added a heap open-addressed long-key indexed priority queue so the heap
  comparator uses the same arbitrary-`Long` key shape as
  `StreamWindowLongIndexedRank`.
- Switched `rift-checked-long` to the no-entry close helper because the long-key
  rank state owns lookup and does not need an operator side-table cleanup
  callback.
- Updated `scala-native-rift/sandbox/run_checked_stream_window_rank_matrix.sh`
  to accept `CHECKED_SWR_MODES`, keeping the default `heap rift-checked`
  behavior unchanged.
- Updated `scala-native-rift/sandbox/CHECKED_STREAM_WINDOW_RANK_MATRIX.md`
  and synced it to `evidence/CHECKED_STREAM_WINDOW_RANK_MATRIX.md`.

Validation:

- `git diff --check` passed before doc edits.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- 20k long-key smoke matched checksum `-715513143181030887`.
- 100k long-key 3-run matrix matched checksum `-2863780563714953957`.
- 1M long-key 3-run matrix matched checksum `4222832129898301078`.

Key numbers:

| Input | Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | RSS bytes |
|---|---|---:|---:|---:|---:|---:|
| 20k | heap-long | 6.007 | 0.149 | 0.000 | 0 | 9879552 |
| 20k | rift-checked-long | 9.440 | 0.310 | 0.128 | 18679 | 13254656 |
| 100k | heap-long | 37.045 | 0.000 | 0.000 | 0 | 38830080 |
| 100k | rift-checked-long | 49.450 | 0.000 | 0.178 | 82547 | 33882112 |
| 1M | heap-long | 358.988 | 6.973 | 0.000 | 0 | 111394816 |
| 1M | rift-checked-long | 503.906 | 5.470 | 0.491 | 826645 | 128286720 |

Interpretation:

- The arbitrary-long-key checked stream-window API is functionally validated
  under a same-logical-program heap comparator.
- This is not a speed win. The default 1M checked-long path is about `40%`
  slower than heap-long and has higher RSS, despite low measured Rift op time.
- The no-entry close path improves the 100k checked-long median versus the
  first close-with-entry run, but the remaining 1M gap shows callback removal is
  not enough.
- The next safe action is to reduce checked rank/window CPU and memory overhead
  before wiring this directly into DEBS Q1 route ranking.

Rejected follow-up probe:

- An uncommitted experiment tried three narrow changes: `getWindowRankOrNull`
  to avoid `contains` + `get`, avoiding a post-`siftUp` index lookup, and
  backward-shift deletion for the long-key queue table. The same 100k/1M
  matrices got slower (`rift-checked-long` around `54-60 ms` at 100k and
  `528 ms` at 1M), so the code was reverted before commit.
- Do not repeat those narrow changes as the next optimization. The likely next
  useful work is either profiling the checked long-key path or designing a
  deeper stream-window rank representation that avoids the duplicate
  queue-table plus owner-table probing/metadata.

### 2026-04-29 Update: Fused TableRank Prototype

Active implementation repo:

- `/Users/siyaoliu/rift/scala-native-rift` on `feature/rift`

What changed:

- Added experimental `RiftRegion.StreamWindowTableRank[T]` in
  `nativelib/src/main/scala-next/scala/scalanative/memory/RiftRegion.scala`.
- Added factories:
  `streamWindowTableRank` and `streamWindowTableRankLexicographic`.
- Added TableRank operations:
  `putTableRankInBucket`, `getTableRank`, `containsTableRank`,
  `updateTableRankPriority`, `removeTableRank`, `peekTableRank`,
  `popTableRank`, `copyTableRankTopK`, `tableRankLength`,
  `hasTableRankBucketsBefore`, `closeTableRankBucketsBefore`,
  `closeTableRankBucketsBeforeWithEntries`, `closeAllTableRankBuckets`, and
  `closeAllTableRankBucketsWithEntries`.
- Updated the Scala 3 plugin guard in
  `nscplugin/src/main/scala-3/scala/scalanative/nscplugin/NirGenExpr.scala`
  so `putTableRankInBucket` rejects direct heap values just like the existing
  checked rank/container APIs.
- Added compiler/runtime tests for TableRank bucket ownership, lexicographic
  priority, top-k copy, removal, and direct heap-value rejection.
- Added `rift-checked-table` and `rift-checked-table-long` modes to
  `sandbox/src/main/scala-next/CheckedStreamWindowRankMatrix.scala`.
- Prototyped checked Q1 rank maintenance on TableRank, correctness-smoked it,
  and then backed it out of
  `sandbox/src/main/scala-next/debs2015/Debs2015Q1CheckedProcessingRun.scala`
  because the focused 1M TableRank gate did not clear. Current DEBS checked Q1
  runs use the previous rank-arena path, not TableRank.
- Added opt-in TableRank diagnostics controlled by `CHECKED_SWR_TABLE_DIAG=1`.
  Diagnostic counters cover lookups/probes, inserts, replacements, priority
  updates, heap sift steps/swaps, bucket moves, bucket-close removals, rehashes,
  top-k candidate comparisons, and final table load/deleted counts.
- Added two general TableRank optimizations: bucket-close fast removal for known
  bucket-owned slots, and directional heap repair after removal.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `86/86`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `33/33`.
- `bench/debs2015/run_q1_checked_processing_matrix.sh` on
  `bench/debs2015/sample_q1.csv` matched heap vs checked-processing outputs
  after the TableRank Q1 prototype backout.
- `CHECKED_SWR_TABLE_DIAG=1` was verified to print `TABLE_DIAG` counters from
  `sandbox/run_checked_stream_window_rank_matrix.sh`.

Focused TableRank gate results:

| Input | Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | RSS bytes |
|---|---|---:|---:|---:|---:|---:|
| 20k | heap-long | 7.498 | 0.000 | 0.000 | 0 | 11321344 |
| 20k | rift-checked-table-long | 9.246 | 0.000 | 0.292 | 17781 | 16269312 |
| 100k | heap-long | 40.582 | 0.000 | 0.000 | 0 | 38780928 |
| 100k | rift-checked-long | 54.018 | 0.000 | 0.215 | 82547 | 33931264 |
| 100k | rift-checked-table-long | 41.069 | 0.000 | 0.164 | 82533 | 49938432 |
| 1M | heap-long | 413.664 | 7.080 | 0.000 | 0 | 111443968 |
| 1M | rift-checked-long | 568.427 | 5.821 | 0.449 | 826645 | 128335872 |
| 1M | rift-checked-table-long | 491.918 | 5.927 | 0.475 | 826631 | 126468096 |

Fast-close / directional-repair follow-up:

| Input | Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | RSS bytes |
|---|---|---:|---:|---:|---:|---:|
| 20k | heap-long | 11.297 | 0.000 | 0.000 | 0 | 11288576 |
| 20k | rift-checked-table-long | 8.595 | 0.000 | 0.141 | 17781 | 16203776 |
| 100k | heap-long | 34.620 | 0.000 | 0.000 | 0 | 38846464 |
| 100k | rift-checked-long | 44.762 | 0.000 | 0.144 | 82547 | 33898496 |
| 100k | rift-checked-table-long | 32.330 | 0.000 | 0.093 | 82533 | 49922048 |
| 1M | heap-long | 300.667 | 4.252 | 0.000 | 0 | 111394816 |
| 1M | rift-checked-long | 476.015 | 6.541 | 0.498 | 826645 | 128221184 |
| 1M | rift-checked-table-long | 512.764 | 5.964 | 0.490 | 826631 | 126451712 |

Opt-in diagnostic sample, 100k one-run, not a headline timing row:

```text
TABLE_DIAG mode=rift-checked-table-long lookups=300000 probes=385422 inserts=52382 replacements=30135 priority_updates=17483 heap_sift_steps=266870 heap_swaps=168244 bucket_moves=30135 bucket_close_removals=52254 rehashes=0 topk_candidate_compares=0 table_active=0 table_used=52382 table_deleted=52382 table_capacity=131072 heap_used=0 heap_capacity=65536
```

Interpretation:

- TableRank is a general checked stream-window operator improvement, not a
  DEBS-specific algorithm change. It removes the old duplicate queue-entry
  representation and lets heap slots store table-slot ids.
- The 100k gate passes: `rift-checked-table-long` is under `43 ms` and much
  faster than same-run old checked-long.
- The initial 1M gate did not pass: `491.918 ms` was lower than same-run old
  checked-long but still about `19%` slower than same-run heap-long, missing
  the within-15% target.
- The fast-close/directional-repair follow-up still does not pass: the 100k
  gate improves to `32.330 ms`, but the 1M same-run row is `512.764 ms`,
  slower than old checked-long and `1.71x` heap-long.
- Rift op time stays below `1 ms`, so the remaining gap is container CPU/layout
  and memory behavior, not region allocation/close overhead.
- A probe that removed bounded probe counters from TableRank lookup was tested
  and rejected: the 1M table-long median regressed to `569.633 ms`. Keep the
  bounded probe loop.

Safe next action:

1. Write a focused TableRank profile/result pack from the diagnostic counters
   and same-run 1M failure before making more container changes.
2. Investigate table/heap array layout, compare cost, hash probe count, and
   update/remove duplicate work under identical operation counts.
3. Do not re-integrate TableRank into DEBS Q1 until the focused 1M gate passes
   or the roadmap explicitly relaxes the gate.

### 2026-04-29 Update: TableRank Profile Pack

Active implementation repo:

- `/Users/siyaoliu/rift/scala-native-rift` on `feature/rift`

What changed:

- Added `sandbox/TABLERANK_PROFILE.md` and synced it to
  `evidence/TABLERANK_PROFILE.md`.
- Added the profile pack to `scripts/sync-evidence.sh`.
- Updated `CHECKED_STREAM_WINDOW_RANK_MATRIX.md` and this handoff with the
  profile result.
- No TableRank representation optimization was applied after profiling, because
  the counters did not identify a single low-risk target.

Profile rows:

| Input | Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | RSS bytes |
|---|---|---:|---:|---:|---:|---:|
| 100k | heap-long | 41.941 | 0.000 | 0.000 | 0 | 38862848 |
| 100k | rift-checked-long | 58.441 | 0.000 | 0.218 | 82547 | 33898496 |
| 100k | rift-checked-table-long | 56.585 | 0.000 | 0.198 | 82533 | 49905664 |
| 1M | heap-long | 437.702 | 8.367 | 0.000 | 0 | 111411200 |
| 1M | rift-checked-long | 610.358 | 5.817 | 1.035 | 826645 | 128253952 |
| 1M | rift-checked-table-long | 568.572 | 8.064 | 0.562 | 826631 | 126418944 |

Diagnostic interpretation:

- The fresh 100k profile did not reproduce the earlier strong 100k TableRank
  gate row: `rift-checked-table-long` was `56.585 ms`, above the earlier
  `<= 43 ms` threshold. Treat the 100k pass as unstable until rerun under
  controlled conditions.
- 1M `rift-checked-table-long` did `3.000` lookups/event and `4.804`
  probes/event.
- It also did `0.719` replacements/event, `0.719` bucket moves/event,
  `1.862` heap sift steps/event, and `1.117` heap swaps/event.
- TableRank was faster than same-run old checked-long at 1M, but still
  `1.30x` heap-long and higher RSS than heap.
- The problem remains checked container CPU/layout overhead, not Rift
  allocation/close overhead.

Safe next action:

1. Do not integrate TableRank into DEBS Q1.
2. Do not repeat rejected lookup/probe/deletion tweaks.
3. If continuing TableRank, design a deeper representation experiment that
   reduces lookup/update/heap maintenance together, then re-run the focused
   20k/100k/1M gates before touching DEBS.

### 2026-04-29 Update: Scala Native Win Envelope / Checked Append Window

Active implementation repo:

- `/Users/siyaoliu/rift/scala-native-rift` on `feature/rift`

What changed:

- Added `CheckedAppendWindowMatrix`, a focused cheap stream-window operator
  benchmark in `sandbox/src/main/scala-next/CheckedAppendWindowMatrix.scala`.
- Added `sandbox/run_checked_append_window_matrix.sh`.
- Added `sandbox/CHECKED_APPEND_WINDOW_MATRIX.md` and synced it to
  `evidence/CHECKED_APPEND_WINDOW_MATRIX.md`.
- Added `sandbox/SN_WIN_ENVELOPE.md` and synced it to
  `evidence/SN_WIN_ENVELOPE.md`.
- Added the first reusable checked append-window API:
  `RiftRegion.StreamAppendWindow`, `RiftRegion.StreamAppendNode`,
  `streamAppendWindow`, `streamAppendWindowBucketFor`, `appendWindow`,
  length helpers, and structured close helpers. The API links user records
  directly through an intrusive hidden next pointer to avoid wrapper nodes.
- Added compiler guards and tests so `appendWindow` rejects direct unrooted
  heap records, while accepting records allocated in a child bucket region.
- Added `rift-checked-api` mode to `CheckedAppendWindowMatrix` to test the
  reusable API separately from the handwritten manual checked child-bucket
  path.
- Optimized the benchmark API usage so `rift-checked-api` caches the current
  `StreamBucket` and `streamBucketRegion` once per bucket instead of calling
  `streamAppendWindowBucketFor` and `streamBucketRegion` on every event.
- Added experimental cursor close support:
  `RiftRegion.StreamAppendCursor`,
  `closeAppendWindowBucketsBeforeWithCursor`, and
  `closeAllAppendWindowBucketsWithCursor`.
- Added `rift-checked-api-cursor` mode to `CheckedAppendWindowMatrix` while
  keeping the older per-entry `rift-checked-api` mode as a control.
- Updated `evidence/ALL_PHASE_RESULTS.md` and `scripts/sync-evidence.sh`.
- TableRank and DEBS Q1 were not touched.

Why it was done:

- The previous TableRank work showed useful framework progress but failed the
  1M focused gate because checked container CPU/layout overhead dominates.
- The new goal is to rebuild the Scala Native win envelope: identify which
  operator shapes are allocation/GC-bound enough for Rift to beat Immix and
  which shapes are CPU/I/O/container-bound.
- `CheckedAppendWindowMatrix` deliberately avoids ranking/hash-table/top-k
  maintenance and measures the cheaper append/bucket/fold pattern that should
  generalize to stream operators beyond DEBS.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `89/89`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `35/35`.
- 20k smoke, 100k 3-run, and 1M 3-run append-window matrices matched checksums
  across `heap`, `rift-checked`, `rift-trusted-hp`, and
  `rift-trusted-streaming`.
- Follow-up 20k, 100k, and 1M reusable API matrices matched checksums across
  all five modes, including `rift-checked-api`.
- Cached bucket/region and cursor follow-up matrices matched checksums across
  all six modes, including `rift-checked-api-cursor`.

Key append-window rows:

| Input | Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | RSS bytes |
|---|---|---:|---:|---:|---:|---:|
| 100k | heap | 2.782 | 0.000 | 0.000 | 0 | 21282816 |
| 100k | rift-checked | 3.370 | 0.000 | 0.008 | 100000 | 15728640 |
| 100k | rift-trusted-hp | 4.087 | 0.000 | 0.006 | 100000 | 15646720 |
| 100k | rift-trusted-streaming | 4.211 | 0.000 | 0.017 | 100000 | 15712256 |
| 1M | heap | 35.513 | 11.149 | 0.000 | 0 | 74989568 |
| 1M | rift-checked | 32.261 | 0.000 | 0.074 | 1000000 | 47497216 |
| 1M | rift-trusted-hp | 41.641 | 0.000 | 0.093 | 1000000 | 47349760 |
| 1M | rift-trusted-streaming | 41.859 | 0.000 | 0.088 | 1000000 | 47480832 |

Reusable `StreamAppendWindow` 1M follow-up:

| Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | RSS bytes |
|---|---:|---:|---:|---:|---:|
| heap | 37.424 | 11.596 | 0.000 | 0 | 75071488 |
| rift-checked | 34.762 | 0.000 | 0.117 | 1000000 | 47546368 |
| rift-checked-api | 76.057 | 0.000 | 0.092 | 1000000 | 83247104 |

No-callback bucket-lookup follow-up, same 1M workload:

| Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | RSS bytes |
|---|---:|---:|---:|---:|---:|
| heap | 37.455 | 11.906 | 0.000 | 0 | 75038720 |
| rift-checked | 33.157 | 0.000 | 0.084 | 1000000 | 47513600 |
| rift-checked-api | 66.023 | 0.000 | 0.082 | 1000000 | 47513600 |

Cached bucket/region follow-up, same 1M workload:

| Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | RSS bytes |
|---|---:|---:|---:|---:|---:|
| heap | 38.559 | 11.581 | 0.000 | 0 | 74989568 |
| rift-checked | 33.172 | 0.000 | 0.083 | 1000000 | 47497216 |
| rift-checked-api | 39.372 | 0.000 | 0.084 | 1000000 | 47480832 |

Cursor close follow-up, same 1M workload:

| Mode | Median elapsed ms | GC ms | Rift op ms | Region objects | RSS bytes |
|---|---:|---:|---:|---:|---:|
| heap | 35.705 | 11.095 | 0.000 | 0 | 75022336 |
| rift-checked | 32.367 | 0.000 | 0.077 | 1000000 | 47529984 |
| rift-checked-api | 37.705 | 0.000 | 0.073 | 1000000 | 47529984 |
| rift-checked-api-cursor | 34.708 | 0.000 | 0.074 | 1000000 | 47529984 |

Interpretation:

- At 100k, heap still wins and measured GC is zero. This is below the useful
  allocation-pressure threshold.
- At 1M, checked Rift is about `9.2%` faster than heap, eliminates
  `11.149 ms` of measured GC collection time, and lowers RSS by about
  `27.5 MB` with only `0.074 ms` of measured Rift operation time.
- The trusted per-bucket modes lose here, so the claim is not "trusted HPZone
  always wins." The useful shape is checked parent streaming plus structured
  child-bucket regions.
- The result supports the broader framework goal: ordinary Scala stream data
  objects can live in checked regions and win when the operator is simple
  enough and allocation volume is high enough.
- The reusable per-entry `StreamAppendWindow` close API is not ready for
  application integration. It is correctness-valid, and removing no-callback
  bucket-lookup delegation improves the 1M row from `76.057 ms` to
  `66.023 ms`; cached bucket/region use improves it to `39.372 ms`, but it
  still misses the strict API gate.
- The cursor close API clears the focused 1M gate. `rift-checked-api-cursor`
  beats same-run heap (`34.708 ms` versus `35.705 ms`), is within 1.15x of
  same-run manual checked (`32.367 ms`), keeps RSS far below heap and level
  with manual checked, and keeps Rift op time below `1 ms`.
- `CHECKED_APPEND_API_DIAG=1` counters after bucket/region caching show the 1M
  API path doing `40` actual bucket lookups, `999960` current-bucket hits,
  `40` bucket opens, `1000000` appends, `40` closed buckets, `1000000` close
  entries, and final live length `0`. The remaining issue was per-entry close
  callback/link traversal shape, which cursor close targets.

Safe next action:

1. Keep TableRank out of DEBS Q1.
2. Use `SN_WIN_ENVELOPE.md` as the current selection guide.
3. Treat `StreamAppendWindow` cursor close as the first reusable append-window
   API form that has cleared the focused 1M gate.
4. Integrate it only into append/fold/window-entry paths with output equality
   checks; leave Q1 TableRank/ranking out of scope until rank primitives clear
   their own gates.

### 2026-04-30 Update: Q1 StreamAppendWindow Cursor Integration

Active implementation repo:

- `/Users/siyaoliu/rift/scala-native-rift` on `feature/rift`

What changed:

- Migrated checked Q1 event-window entries in
  `sandbox/src/main/scala-next/debs2015/Debs2015Q1CheckedProcessingRun.scala`
  from a hand-written path-dependent child-bucket linked list to
  `RiftRegion.StreamAppendWindow[RouteEvent]`.
- `RouteEvent` is now an ordinary Scala class extending
  `RiftRegion.StreamAppendNode`, allocated in the current checked event bucket
  region and appended through `RiftRegion.appendWindow`.
- Q1 eviction now consumes expired event buckets through
  `closeAppendWindowBucketsBeforeWithCursor`; end-of-run cleanup uses
  `closeAllAppendWindowBucketsWithCursor`.
- Adjusted the cursor close callback type in
  `nativelib/src/main/scala-next/scala/scalanative/memory/RiftRegion.scala` to
  match the existing checked close-helper pattern, so close callbacks can
  capture parent-owned operator metadata while child entries are consumed.
- Q1 ranking, TableRank, Q2 ranking, and Q2 processing were not changed.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `89/89`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `35/35`.
- `zsh bench/debs2015/run_q1_checked_processing_matrix.sh` matched heap output
  on the sample input after stripping only latency.
- 100k Q1 checked-processing output matched heap in
  `/tmp/debs2015-q1-checked-processing-cursor-100k`.
- RunBoth sample output matched heap for all modes in
  `/tmp/debs2015-runboth-cursor-sample`.
- RunBoth 100k `heap`/`rift-checked` output matched in
  `/tmp/debs2015-runboth-cursor-100k`.

100k single-run control rows:

| Harness | Mode | Elapsed ms | GC ms | Rift op ms | Q1 process ms | Q2 process ms | Q1 outputs | Q2 outputs |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Q1 only | heap | 761.989 | n/a | n/a | n/a | n/a | 5942 | n/a |
| Q1 only | checked-processing | 771.422 | n/a | n/a | n/a | n/a | 5942 | n/a |
| RunBoth | heap | 979.461 | 15.857 | 0.000 | 291.974 | 249.467 | 5942 | 3246 |
| RunBoth | rift-checked | 872.828 | 3.350 | 2.606 | 288.270 | 196.571 | 5942 | 3246 |

1M 3-run RunBoth control:

- Input: `/tmp/debs2015-month1-1000000.csv`.
- Modes: `heap rift-checked`.
- Output validation: all three runs diffed Q1 and Q2 checked output against
  heap after stripping only the latency column.
- Run directories:
  `/tmp/debs2015-runboth-q1-appendcursor-1m-run{1,2,3}`.

Median rows:

| Mode | Elapsed ms | Throughput eps | GC ms | RSS MiB | Rift op ms | Q1 process ms | Q1 change ms | Q2 process ms | Region objects | Q1 window raw MiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 4559.928 | 219301.708 | 19.893 | 153.8 | 0.000 | 1389.540 | 109.034 | 1192.661 | 0 | 0.0 |
| rift-checked | 4514.165 | 221524.921 | 10.297 | 91.7 | 6.888 | 1507.776 | 81.145 | 1113.035 | 5940011 | 99.9 |

Interpretation:

- This is the first DEBS application use of the passing append-window
  cursor-close shape. It now has a bounded 1M median-backed control, but it is
  still not final full-DEBS evidence.
- The heap/Rift logical program remains aligned: route counts, ranking, output
  semantics, and Q2 are unchanged; only checked Q1 event-window allocation and
  close discipline moved to the reusable region-backed primitive.
- The single-run 100k RunBoth row is directionally favorable for checked Rift,
  but it should not replace the existing 3-run bounded medians.
- The 1M median shows the current useful envelope and limit: checked Rift moves
  `5.94M` Q1 event-window Scala objects through regions with low region
  bookkeeping and much lower RSS, but Q1 process time remains higher than heap.

Safe next action:

1. Migrate another append/fold/window-entry path that matches the
   cheap cursor-close shape.
2. If staying on Q1, reduce checked Q1 process overhead without changing the
   logical ranking algorithm.
3. Keep Q1 TableRank/ranking integration gated out until the focused rank gate
   passes.

### 2026-04-30 Update: Q2 StreamAppendWindow Cursor Integration

Active implementation repo:

- `/Users/siyaoliu/rift/scala-native-rift` on `feature/rift`

What changed:

- Migrated checked Q2 profit-window and empty-taxi-window entries in
  `sandbox/src/main/scala-next/debs2015/Debs2015Q2CheckedProcessingRun.scala`
  from local `ProfitBucket`/`EmptyBucket` linked lists to
  `RiftRegion.StreamAppendWindow`.
- `ProfitEntry` and `EmptyEntry` are now ordinary Scala classes extending
  `RiftRegion.StreamAppendNode`, allocated in the current stream-bucket child
  region and appended through `RiftRegion.appendWindow`.
- Q2 eviction now consumes expired profit/empty buckets through
  `closeAppendWindowBucketsBeforeWithCursor`; end-of-run cleanup uses
  `closeAllAppendWindowBucketsWithCursor`.
- Q2 median heaps, taxi-id table, ranking heap, top-10 cache, and output
  semantics were not changed.
- This mirrors the checked Q1 event-window cursor shape, but for Q2's
  append/fold/window-entry paths.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest" "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `89/89` compiler probes and `35/35` runtime tests.
- Q2 checked-processing sample output matched heap.
- Q2 checked-processing 100k output matched heap in
  `/tmp/debs2015-q2-checked-processing-appendwindow-100k`.
- RunBoth sample output matched heap for `rift-hp`, `rift-streaming`, and
  `rift-checked` in `/tmp/debs2015-runboth-q2-appendwindow-sample`.
- RunBoth 100k output matched heap for `rift-checked` in
  `/tmp/debs2015-runboth-q2-appendwindow-100k`.
- RunBoth 1M output matched heap for `rift-checked` in all three median runs:
  `/tmp/debs2015-runboth-q2-appendwindow-1m-single`,
  `/tmp/debs2015-runboth-q2-appendwindow-1m-run2`, and
  `/tmp/debs2015-runboth-q2-appendwindow-1m-run3`.

100k single-run RunBoth rows:

| Mode | Elapsed ms | GC ms | Rift op ms | Q1 process ms | Q2 process ms | Q1 outputs | Q2 outputs |
|---|---:|---:|---:|---:|---:|---:|---:|
| heap | 487.948 | 9.023 | 0.000 | 142.167 | 116.391 | 5942 | 3246 |
| rift-checked | 494.789 | 2.241 | 1.713 | 158.695 | 124.979 | 5942 | 3246 |

1M 3-run RunBoth median rows:

| Mode | Elapsed ms | Throughput eps | GC ms | RSS MiB | Rift op ms | Q1 process ms | Q2 process ms | Q1 window raw MiB | Q2 profit raw MiB | Q2 empty raw MiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 4993.892 | 200244.609 | 21.009 | 153.8 | 0.000 | 1518.053 | 1343.606 | 0.0 | 0.0 | 0.0 |
| rift-checked | 4995.946 | 200162.297 | 20.637 | 142.4 | 8.072 | 1631.084 | 1330.543 | 99.9 | 37.5 | 29.9 |

Interpretation:

- This is a reusable-operator checkpoint, not a stronger DEBS speed claim.
- The same checked append/window cursor primitive now covers checked Q1 event
  entries and checked Q2 profit/empty entries.
- The 1M elapsed median is effectively tied. Checked Q2 process is slightly
  lower than heap in the median row, but checked Q1 process is still higher.
- RSS remains below heap but is much higher than the previous Q1-only
  append-window checkpoint. The migration is useful for API unification and
  safety-boundary coverage, not as a standalone performance win.

Safe next action:

1. Investigate the checked RSS/footprint regression from moving Q2 windows to
   `StreamAppendWindow`; compare stream-bucket metadata and native mapping
   reuse against the previous local-bucket implementation.
2. If keeping the migration, look for a lower-footprint append-window bucket
   representation before migrating more DEBS paths.
3. Keep Q1 TableRank/ranking integration gated out.

### 2026-04-30 Update: StreamAppendWindow Cursor-Reuse Control

Active implementation repo:

- `/Users/siyaoliu/rift/scala-native-rift` on `feature/rift`

What changed:

- `StreamAppendWindow` now owns one reusable `StreamAppendCursor` object.
- `closeAppendWindowBucketsBeforeWithCursor` and
  `closeAllAppendWindowBucketsWithCursor` reset that cursor for each closed
  bucket, instead of allocating a fresh cursor object per bucket.
- Public API signatures, DEBS Q1/Q2 logic, TableRank, and ranking code were not
  changed.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `89/89`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `35/35`.
- Focused `CheckedAppendWindowMatrix` smoke, 100k, and 1M runs matched
  checksums. The 1M all-mode run had a noisy/non-winning cursor row, but a
  confirmation subset still cleared the cursor API gate:
  `rift-checked-api-cursor` `35.527 ms` versus heap `37.494 ms` and manual
  checked `33.286 ms`.
- RunBoth 100k and 1M heap/checked controls matched Q1/Q2 outputs after
  stripping only latency columns.

1M RunBoth 3-run median after cursor reuse:

| Mode | Elapsed ms | Throughput eps | GC ms | RSS MiB | Rift op ms | Q1 process ms | Q2 process ms | Q1 window raw MiB | Q2 profit raw MiB | Q2 empty raw MiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | 5219.189 | 191600.637 | 21.819 | 153.8 | 0.000 | 1606.540 | 1472.710 | 0.0 | 0.0 | 0.0 |
| rift-checked | 5349.444 | 186935.328 | 21.593 | 142.4 | 9.747 | 1760.174 | 1528.867 | 99.9 | 37.5 | 29.9 |

Interpretation:

- Cursor-object reuse is correctness-valid but neutral/negative on bounded
  DEBS. It is a small framework cleanup, not a new application performance
  claim.
- The checked RSS median remains essentially unchanged from the Q2
  append-window checkpoint (`142.4 MiB`), so per-bucket cursor object
  allocation was not the checked RSS regression driver.
- The next useful implementation direction remains append-window footprint
  analysis or checked Q1 process overhead reduction. Do not migrate more DEBS
  paths just because cursor reuse is now implemented.

Safe next action:

1. Profile/inspect append-window bucket footprint and parent metadata before
   changing more DEBS paths.
2. Separately investigate checked Q1 process overhead, because Q1 process time
   remains the largest checked-vs-heap gap in the current bounded rows.
3. Keep TableRank and Q1 ranking integration gated out.

### 2026-04-30 Update: StreamAppendWindow Prepend-Cursor Probe

Active implementation repo:

- `/Users/siyaoliu/rift/scala-native-rift` on `feature/rift`

What changed:

- Added experimental `RiftRegion.prependWindow` for order-insensitive
  append-window buckets.
- Extended the compiler guard so `prependWindow` rejects direct unrooted heap
  values the same way `appendWindow` does.
- Added focused matrix modes `heap-prepend` and
  `rift-checked-api-prepend-cursor`.
- Added compiler and runtime tests for prepend-window use and direct heap
  rejection.
- DEBS Q1/Q2 code was not changed.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `91/91`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `36/36`.
- Focused 20k, 100k, and 1M prepend matrix rows matched checksums.

Focused prepend rows:

| Input | Mode | Median elapsed ms | GC ms | RSS MiB | Rift op ms | Region objects |
|---:|---|---:|---:|---:|---:|---:|
| 20k | heap-prepend | 1.428 | 0.000 | 5.9 | 0.000 | 0 |
| 20k | rift-checked-api-prepend-cursor | 1.541 | 0.000 | 5.8 | 0.050 | 20000 |
| 100k | heap-prepend | 2.870 | 0.000 | 20.3 | 0.000 | 0 |
| 100k | rift-checked-api-prepend-cursor | 3.610 | 0.000 | 15.0 | 0.008 | 100000 |
| 1M | heap-prepend | 36.700 | 11.147 | 71.5 | 0.000 | 0 |
| 1M | rift-checked-api-prepend-cursor | 34.943 | 0.000 | 45.3 | 0.076 | 1000000 |

Same-binary 1M append-vs-prepend comparison:

| Mode | Median elapsed ms | GC ms | RSS MiB | Rift op ms |
|---|---:|---:|---:|---:|
| heap | 36.746 | 11.394 | 71.5 | 0.000 |
| rift-checked-api-cursor | 34.597 | 0.000 | 45.3 | 0.075 |
| heap-prepend | 36.836 | 11.367 | 71.5 | 0.000 |
| rift-checked-api-prepend-cursor | 34.662 | 0.000 | 45.3 | 0.076 |

Interpretation:

- `prependWindow` is a valid general checked operator for unordered/head-insert
  buckets and clears the same 1M threshold as append cursor.
- It does not beat the existing append-cursor shape in the focused matrix.
  The same-binary rows are effectively tied.
- Do not integrate `prependWindow` into DEBS yet. This probe says the current
  DEBS Q1/Q2 issue is not simply tail-update overhead.

Safe next action:

1. Keep `prependWindow` as framework/control evidence.
2. Do not migrate DEBS to prepend unless a path specifically needs unordered
   head insertion or a new focused result shows a real advantage.
3. Move next to checked Q1 process overhead or deeper append-window/live-payload
   attribution.

### 2026-05-05 Update: Cheap Operator Family Reporting And Staged Sweep

Active repos:

- Parent docs/evidence repo: `/Users/siyaoliu/rift` on `main`
- Implementation repo: `/Users/siyaoliu/rift/scala-native-rift` on
  `feature/rift`

What changed:

- Added a reporting-name layer in `docs/MEMORY_MODE_TAXONOMY.md`:
  `gc-heap`, `region-scoped-rooted`, `region-scoped-rootless`,
  `region-stream-rootless`, `region-hp-rootless`, `checked-region-stream`,
  `checked-region-scoped`, and `checked-page-token`.
- Kept public code symbols and raw script labels as aliases; this milestone
  does not rename public APIs.
- Added Dataflow SELECT page-token rows and SafeZone-backed page-token rows.
- Added a Dataflow AGGREGATE `checked-epoch-fold` reporting row over the
  existing exact-array checked aggregate path.
- Added a checked ListOfLists linked builder row.
- Extended the comprehensive runner so future staged runs include
  object-allocation lowering, Common Crawl page-token rows, and GH Archive
  heap-budget controls.
- Added `CHEAP_OPERATOR_FAMILY_MATRIX.md` in both `sandbox/` and parent
  `evidence/`, and synced it through `scripts/sync-evidence.sh`.
- Fixed `sandbox/run_checked_region_buffer_matrix.sh` mode-list parsing so the
  staged checked/stream run does not treat the full default mode list as one
  mode.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile` passed.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"` passed `100/100` after a rerun; the first parallel attempt only failed due sbt boot-server/lock contention.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"` passed `44/44`.
- Dataflow SELECT page-token smoke matched checksum.
- Dataflow AGGREGATE `checked-epoch-fold` smoke matched checksum.
- ListOfLists checked builder smoke completed.
- Checked region buffer smoke completed after the parser fix.
- The staged `checked streams` smoke leg completed with run id
  `2026-05-05-cheap-operators-checked-streams-smoke`.

Staged single-run rows, not final medians:

| Workload | Row | Elapsed ms | Interpretation |
|---|---|---:|---|
| Dataflow SELECT | heap | 33.489 | Heap baseline; GC `12.218 ms`. |
| Dataflow SELECT | improved SafeZone / `region-scoped-rooted` | 22.904 | Strong scoped-region baseline. |
| Dataflow SELECT | current checked / `checked-region-stream` | 20.541 | Existing checked row. |
| Dataflow SELECT | `checked-page-token` | 19.697 | New page-token row improves current checked. |
| Dataflow SELECT | scoped-backend page-token | 18.371 | Fastest staged SELECT row. |
| Dataflow AGGREGATE | heap | 49.316 | Heap baseline; GC `11.020 ms`. |
| Dataflow AGGREGATE | current checked | 38.581 | Existing exact-array checked aggregate. |
| Dataflow AGGREGATE | `checked-epoch-fold` | 39.213 | Beats heap, slightly trails current checked in this probe. |
| ListOfLists linked | heap | 16615.319 | Baseline. |
| ListOfLists linked | improved SafeZone | 9831.508 | Strong scoped-region row. |
| ListOfLists linked | trusted HP | 9341.644 | Strong trusted-Rift row. |
| ListOfLists linked | checked builder | 9109.045 | Fastest staged linked row. |

Interpretation:

- This implements the first slice of "Rift as checked stream-region
  programming model plus backend choices." SafeZone-derived scoped allocation
  is now treated as a serious backend candidate, not just a side experiment.
- Page-token generalizes cleanly to SELECT/filter/project-like rows.
- The `EpochFold` name is not yet a full reusable fold operator. It is a
  reporting row over the exact-array checked aggregate path until a general
  cheap fold API clears its own gate.
- ListOfLists checked builder is promising topology evidence, but it needs
  clean medians.
- DEBS ranking/median remains deferred. Stateful indexed/ranking operators are
  still separate, expensive shapes.

Safe next action:

1. Run clean 1M 3-run medians for Dataflow SELECT page-token/scoped page-token.
2. Run clean 1M 3-run medians for Dataflow AGGREGATE `checked-epoch-fold`.
3. Run clean 3-run medians for ListOfLists checked builder.
4. Only after those pass, decide whether to add `EpochBuffer` and
   `TransactionRegion` rows for Yak/StreamFlex/Stancu.

### 2026-05-05 Update: Focused Cheap Operator Gates

Active repos:

- Parent docs/evidence repo: `/Users/siyaoliu/rift`
- Implementation repo: `/Users/siyaoliu/rift/scala-native-rift`

What changed:

- Reran the first cheap-operator rows at the default 1M-shape with 3 timed
  runs:
  - Dataflow SELECT page-token and scoped-backend page-token;
  - Dataflow AGGREGATE `checked-epoch-fold`;
  - ListOfLists linked checked builder.
- Updated `CHEAP_OPERATOR_FAMILY_MATRIX.md`, `docs/ROADMAP.md`,
  `docs/PERFORMANCE_EVALUATION_REPORT.md`, `docs/BENCHMARK_CATALOG.md`,
  `docs/RIFT_EVALUATION_SUMMARY_SLIDES.md`,
  `evidence/EVALUATION_SUMMARY_TABLES.md`, and
  `evidence/ALL_PHASE_RESULTS.md`.

Focused rows:

| Workload | Row | Median ms | Comparator |
|---|---|---:|---|
| Dataflow SELECT | `gc-heap` | 28.176 | GC median `6.698 ms`. |
| Dataflow SELECT | `region-scoped-rooted` | 22.982 | Improved SafeZone 32 KiB. |
| Dataflow SELECT | `checked-region-stream` | 21.033 | Current checked Rift. |
| Dataflow SELECT | `checked-page-token` | 19.856 | Beats current checked. |
| Dataflow SELECT | scoped-backend `checked-page-token` | 19.050 | Fastest focused SELECT row. |
| Dataflow AGGREGATE | `gc-heap` | 62.008 | GC median `22.583 ms`. |
| Dataflow AGGREGATE | `region-scoped-rooted` | 42.234 | Improved SafeZone 32 KiB. |
| Dataflow AGGREGATE | `checked-region-stream` | 40.024 | Current checked Rift. |
| Dataflow AGGREGATE | `checked-epoch-fold` | 38.991 | Fastest focused AGGREGATE row, but still exact-array implementation. |
| ListOfLists linked | `gc-heap` | 15390.798 | Baseline. |
| ListOfLists linked | `region-scoped-rooted` | 10002.658 | Improved SafeZone. |
| ListOfLists linked | `region-hp-rootless` | 9594.689 | Trusted HP. |
| ListOfLists linked | checked builder | 9407.102 | Fastest focused linked row. |

Interpretation:

- The SELECT page-token and ListOfLists builder gates pass and should move into
  the next clean headline sweep.
- The AGGREGATE row is positive, but it should not be oversold as a new generic
  fold operator yet. It is the existing exact-array checked aggregate path
  under the `EpochFold` reporting direction.
- These rows did not collect RSS. RSS collection is the next required control
  before using them as presentation headline rows.

Safe next action:

1. Add RSS capture for these focused rows, preferably through the staged
   performance runner rather than ad hoc sbt output.
2. Then implement the next cheap operator only if it maps cleanly:
   `EpochBuffer` for Yak/StreamFlex-style append/drain epochs, or
   `TransactionRegion` for Stancu-style batch regions.
3. Do not touch DEBS ranking/median until indexed/ranking operators have their
   own passing focused gates.

### 2026-05-05 Update: Cheap Operator RSS Rerun

What changed:

- Wrapped the native benchmark binaries directly with `/usr/bin/time -l` so
  RSS measures the benchmark process, not SBT.
- Stored raw logs under
  `/Users/siyaoliu/rift/cache/cheap-operator-rss-2026-05-05/`.
- Updated `CHEAP_OPERATOR_FAMILY_MATRIX.md`, report, roadmap, slides, summary
  tables, and all-phase rollup.

RSS-focused rows:

| Workload | Row | Median ms | RSS bytes | Interpretation |
|---|---|---:|---:|---|
| Dataflow SELECT | `gc-heap` | 27.932 | 39288832 | Heap baseline, GC median `6.616 ms`. |
| Dataflow SELECT | `region-scoped-rooted` | 22.466 | 30375936 | Improved SafeZone 32 KiB. |
| Dataflow SELECT | `checked-region-stream` | 20.245 | 30490624 | Current checked Rift. |
| Dataflow SELECT | `checked-page-token` | 19.673 | 30392320 | Faster than current checked. |
| Dataflow SELECT | scoped-backend `checked-page-token` | 17.980 | 30375936 | Fastest SELECT row and lower RSS than heap. |
| Dataflow AGGREGATE | `gc-heap` | 61.585 | 40091648 | Heap baseline, GC median `22.297 ms`. |
| Dataflow AGGREGATE | `region-scoped-rooted` | 40.103 | 46907392 | Faster than heap but higher RSS. |
| Dataflow AGGREGATE | `checked-region-stream` | 38.644 | 46825472 | Faster than scoped rooted. |
| Dataflow AGGREGATE | `checked-epoch-fold` | 38.399 | 46825472 | Fastest elapsed, but RSS higher than heap and still exact-array implementation. |
| ListOfLists linked | `gc-heap` | 14822.115 | 575930368 | Baseline. |
| ListOfLists linked | `region-scoped-rooted` | 9812.764 | 367280128 | Strong region row. |
| ListOfLists linked | `region-hp-rootless` | 9547.748 | 364101632 | Trusted HP row. |
| ListOfLists linked | checked builder | 9228.561 | 364150784 | Fastest and about `212 MB` lower RSS than heap. |

Interpretation:

- SELECT page-token and ListOfLists builder are now positive on elapsed and RSS.
- AGGREGATE is positive on elapsed/GC but not RSS. Keep it as a promising
  direction, not a completed reusable `EpochFold` API.
- These are still focused rows. The next engineering step should be a reusable
  RSS wrapper/runner and then one new cheap operator family, not DEBS ranking.

## Unsafe Assumptions To Avoid

### 2026-05-06 Update: Safety Gap Fixed And Default Control Rows Pruned

What changed:

- Fixed the ReML-style generic heap-retention probe at the current compiler
  boundary. Durable/static heap state now rejects known Rift-derived
  region-captured generic heap wrappers, widened `AnyRef` values, heap arrays
  of region-captured values, and escaping closures that hide generic region
  values. Local nonescaping polymorphic use remains accepted.
- Added `docs/FINAL_COMPONENT_SELECTION.md`, which separates public candidates,
  internal lower-bound controls, and gated/rejected operators.
- Updated the parent performance runner and the main sandbox matrix scripts so
  final-selection defaults exclude current SafeZone and rootless/unsafe control
  modes. Use `RIFT_EVAL_INCLUDE_CONTROLS=1`,
  `RIFT_BENCH_INCLUDE_CONTROLS=1`, or explicit `*_MODES` variables to reproduce
  those rows.

Validation:

- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "nscplugin3_next/testOnly org.scalanative.RiftRegionCheckedCompilerTest"`
  passed `118/118`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "tests3_next/testOnly scala.scalanative.memory.RiftRegionCheckedTest"`
  passed `49/49`.
- `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- `bash -n scripts/run-performance-evaluation.sh` and `zsh -n` over the touched
  sandbox runner scripts passed.

Remaining caveat:

- The fixed safety rule covers durable/static retention of known Rift-derived
  values. It is not yet a full arbitrary heap-object field/alias analysis, and
  it does not make rootless checked backends safe to present publicly.

Follow-up validation:

- Final-selection smoke run `2026-05-06-final-selection-smoke` completed with
  `RIFT_EVAL_SUITES="preflight core prior checked streams reml"`,
  `RIFT_EVAL_SCALE=smoke`, and `include_controls=0`.
- Raw run directory:
  `/Users/siyaoliu/rift/cache/perf-eval/2026-05-06-final-selection-smoke/`.
- This smoke is not headline performance evidence because it used
  `RIFT_EVAL_ALLOW_DIRTY=1`, but it validates that the default staged runner
  can execute broad suites without the old current/rootless control rows.
- Clean final-selection headline run `2026-05-06-final-selection-headline`
  then completed from clean parent/child commits. Use
  `evidence/FINAL_SELECTION_HEADLINE_2026_05_06.md` for the compact tables.

- "Rift already has final DEBS application proof." It does not. The current
  bounded-sample medians are encouraging application evidence, and the
  pool-cap plus `ChildBucket` controls now include a same-order full-month
  3-run median. Per-family attribution found and fixed the Q1 rank lifetime
  issue, and the post-fix full-month control is now near-tie on elapsed with
  heap-scale RSS. The Q1 window-rank arena then reduced, but did not eliminate,
  the checked rank-refresh churn and produced a full-month single-run RSS win.
  The reusable `StreamBucketArena` API now generalizes the bucket lifetime
  primitive, and `StreamWindowIndexedRank` is the first dense-key rank/window
  collection. The auto-cleanup path now removes tracked rank keys before child
  bucket close. The entry-cleanup path then removes the duplicate checked-side
  bucket key list and improves the focused default matrix, but it is still
  slower than heap and slower than the earlier manual-cleanup path. The
  lexicographic priority API then covers Q1-style tie-breakers, and the
  long-key rank queue covers standalone hash-keyed state. The Q2 CPU substep
  diagnostic does not reproduce bounded checked same-operation overhead, so
  lower-overhead stream-window rank integration, optional full-month SafeZone
  comparison, and stronger safe-API controls are still missing.
- "GC time should disappear because Q1/Q2 windows and input bytes use Rift."
  `gc_time_ns` is collection time only. Some former heap-heavy paths have
  moved, including taxi-id bytes/entries and latency backing arrays, and the
  allocation-attribution run confirms heap allocation calls/bytes/time drop
  materially. The byte-output checkpoint removes most remaining output heap
  churn in RunBoth, but broader control state, CPU work, I/O, and locality
  still affect elapsed time.
- "Allocation-attribution elapsed time is a headline benchmark." It is not.
  `SCALANATIVE_GC_ALLOC_STATS=1` times every heap allocation and uses atomic
  counters, so it is for diagnosis and interpretation.
- "SafeZone is solved." Improved SafeZone is much better on some workloads, but current SafeZone pathologies and workload sensitivity still matter.
- "Layout wins prove allocator wins." They are separate effects.
- "The current bounded-sample medians prove a final DEBS win." They do not;
  Q1 rank-refresh overhead is reduced but not fully generalized, checked Q2
  overhead explanation, optional full-month SafeZone controls, and safe API
  boundaries are still missing.
- "Same-second checked Q1 rank reuse will reduce rank churn." It did not on the
  100k diagnostic: checked still created `98005` rank objects for `98005` rank
  refreshes, so the hot-path branch was backed out.
- "The Q2 top-10 cache medians are final DEBS evidence." They are not; they are
  bounded-sample evidence and still lack SafeZone controls and safe API
  boundaries.
- "Any append-window API shape is ready because cursor close passed the focused
  1M gate." Too broad. The old per-entry `StreamAppendWindow` close API still
  misses the strict gate. The passing reusable shape is specifically cached
  bucket/region use plus cursor close. It now has a Q1 event-window DEBS
  1M median-backed bounded control, but not final full-DEBS proof.
- "The Q1 checked-output probe proves checked DEBS processing." It does not.
  It only checks transient output/ranking materialization; the Q1 window and
  rank maintenance engine is still heap in both probe modes.
- "The Q1 checked-processing probe is final checked DEBS." It is not. It moves
  real Q1 processing objects into checked regions and now preserves per-second
  event-node reclaim with child bucket regions. Q1 rank objects now also live
  in child bucket regions, but the child-region close discipline is still not
  globally affine-checked.
- "The Q2 checked-processing probe is final checked DEBS." It is not. It is
  now integrated into RunBoth, but still uses heap control metadata for
  `ProfitStats`, relies on structured rather than affine-proved child-window
  close, and lacks SafeZone full-month controls.
- "A binary heap for Q2 top-candidate extraction is the obvious fix." It was
  tested during the Q2 attribution step and increased comparisons on the 100k
  sample.
