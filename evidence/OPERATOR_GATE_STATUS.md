# Operator Gate Status

Date: 2026-05-09
Last updated: 2026-05-10 23:26 CEST

Status: planning/evidence gate artifact built from committed benchmark
higher-level operator evidence, including the LogHub top-template retained
matrix at child commit `2393a69c4`, the follow-up `EpochTopKByKey` reusable API
gate at child commit `9abac4833`, L1 support at child `3598efe29`, and the
top-k increment hot-path follow-up at child `59acadda6`, and the Yak topword
same-shape integration follow-up at child `bcbfe80f5`. It records which higher-level operators may
be optimized or integrated into application benchmarks under the new
comparison-class rules.

## Rule

Rank, top-k, median, hash, and join operators must not move into application
claims until they have:

1. a natural heap baseline;
2. a same-shape heap control;
3. a retained-object/drop-anchor control when ordinary records survive until
   close;
4. a focused 1M gate;
5. matching checksum/output count across modes.

If a candidate loses to the same-shape heap control, it may still be reported
as API/safety/RSS evidence, but not as a throughput win.

## Current Gate Table

| Candidate | Natural workload | Current evidence | Missing controls | Current status | Next allowed action |
|---|---|---|---|---|---|
| Hash/window join | NEXMark Q8 new-user/new-auction window join | Generic Q8 checked row beats generic heap (`291.832 ms` vs `322.210 ms` at 1M), but the fair packed join API row loses to specialized heap (`20.987 ms` vs `17.393 ms`) while reducing RSS (`124 MB` vs `146 MB`) and reporting zero timed GC. | Retained-object drop-anchor is not needed for the packed count API row because parent durable state is primitive and bucket output records are cursor-closed. | Gated framework/RSS evidence, not a throughput claim. | Profile or redesign `StreamJoinWindow` only if a concrete application needs this shape; any new patch must rerun `heap-join-api` versus `rift-checked-join-api` at 1M. |
| Append/pop top-k | Yak topword, LogHub top templates, Common Crawl top domains | `RegionPriorityQueue` validates checked owner-token top-k safety. LogHub top-template retained controls passed strongly: generated 1M checked scoped retained is `290.610 ms` versus retained heap `424.443 ms`, and real HDFS preloaded 1M checked scoped retained is `81.174 ms` versus retained heap `116.138 ms`. The reusable `EpochTopKByKey` API also passes the same gate. After the increment hot-path follow-up, generated 1M checked scoped top-k is `274.914 ms` versus retained heap `397.788 ms`, and real HDFS preloaded checked scoped top-k is `82.170 ms` versus retained heap `111.704 ms`. The L1 final-clean real HDFS x20 row confirms the direction: reusable checked top-k scoped `4.88 s` and `28 MB` RSS versus retained heap `5.52 s` and `205 MB` RSS. Yak topword now adds a second natural top-k workload: at 10M generated records, `checked-epoch-topk-scoped` is `249.311 ms` versus natural heap `313.724 ms` and same-shape heap top-k retained `297.740 ms`, with zero timed GC and region-like RSS. | The reusable API now has small measured overhead versus the benchmark-local count-array path: generated same-run overhead is about `5.7%` (`274.914 ms` vs `260.130 ms`), real HDFS L2 overhead is about `7.0%` (`82.170 ms` vs `76.818 ms`), and real HDFS L1 overhead is about `1.7%` (`4.88 s` vs `4.80 s`). Yak topword also shows a topology caveat: the older checked close-traversal epoch row is still faster (`234.031 ms`) than reusable top-k (`249.311 ms`) for that local workload. | Passed reusable retained top-k API gate with materially reduced overhead, L1 real-input confirmation, and a second generated-methodology top-k confirmation. | Keep `heap-retained-drop-anchor` or same-shape heap top-k controls in every top-k row. The next allowed action is application integration only for natural top-k workloads, plus profiling if a future row exposes API overhead or a topology loss. |
| Mutable keyed rank/top-k | DEBS Q1/Q2, NEXMark Q9 winning bids, LogHub top templates | `RegionIndexedPriorityQueue` validates checked dense-key mutable ranking. Default local median removes GC but loses elapsed and RSS (`103.052 ms` vs heap `100.254 ms`). `StreamWindowTableRank` remains slower than heap-long at 1M (`568.572 ms` vs `437.702 ms`). | Natural workload same-shape heap; retained controls for bucket-owned records; profile that isolates lookup/update/heap maintenance. | Gated/negative performance evidence. | Do not return to DEBS ranking. If revisited, start with NEXMark Q9 or LogHub top templates and build a same-shape heap retained control first. |
| Median/percentile window | DEBS Q2, sensor rolling stats, latency percentile windows | No fair checked median operator has passed a focused gate. DEBS Q2 evidence is CPU/ranking-heavy and not clearly a memory-management problem. | Natural heap baseline, same-shape heap median/sketch control, retained control, focused 1M gate. | Deferred. | Use approximate sketches such as KLL/t-digest only if the target workload permits approximate percentiles; exact median stays out of the next milestone. |
| Hash/group aggregate | Dataflow AGGREGATE, LogHub sessions, Common Crawl domains | Direct epoch and retained-epoch rows already cover summary-on-append aggregate shapes. Generic `StreamWindowFold` failed its focused gate, so the current winning path is operator-owned direct epoch/page-token, not generic fold tables. | Same-shape heap for any new hash-table-based API; retained controls if records survive to close. | Partially solved by direct epoch/page-token for simple additive summaries; generic hash/fold still gated. | Continue using direct epoch or page-token for additive summaries. Only build a generic hash/fold operator when a workload cannot be expressed as append-time summaries plus bulk close. |

## Candidate Order

1. **Top-k/template-ranking integration candidate**: `EpochTopKByKey` now
   passes the retained gate and the first hot-path pass reduced same-run API
   overhead to single digits. Yak topword confirms it on a second natural
   top-k workload, but also shows direct checked epoch can still be the better
   topology when close traversal is cheap. Use `EpochTopKByKey` only with
   retained controls and natural top-k workloads.
2. **NEXMark Q8 join**: best join candidate because fair heap and checked API
   controls already exist. Current result is lower-RSS but slower, so it needs
   profiling before more API work.
3. **NEXMark Q9 winning bids**: useful generated methodology candidate for
   mutable keyed rank, but it needs a fair same-shape heap control first.
4. **Common Crawl top domains**: good stream/top-k shape but current real WET
   input has not shown material GC pressure; use generated shaped rows only as
   stressors.
5. **DEBS rank/median**: keep deferred until focused rank/median controls pass.

## Reporting Rule

Use this file together with
`evidence/EVALUATION_CLASSIFIED_SUMMARY.md`. If an operator row cannot be
classified cleanly, it is not ready for the report summary table.
