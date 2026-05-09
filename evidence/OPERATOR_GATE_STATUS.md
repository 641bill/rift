# Operator Gate Status

Date: 2026-05-09
Last updated: 2026-05-09 22:03 CEST

Status: planning/evidence gate artifact built from committed benchmark evidence.
No new benchmark rows were run for this file. It records which higher-level
operators may be optimized or integrated into application benchmarks under the
new comparison-class rules.

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
| Append/pop top-k | Yak topword, LogHub top templates, Common Crawl top domains | `RegionPriorityQueue` validates checked owner-token top-k safety. Default local median removes GC and lowers RSS, but is slower than heap (`28.621 ms` vs `27.369 ms`). | Same-shape heap with the final application topology; retained drop-anchor when records survive to close; real or generated application row. | API/safety evidence only. | Pick one concrete workload before optimizing. Preferred first target: LogHub top templates, because real HDFS input is already wired. |
| Mutable keyed rank/top-k | DEBS Q1/Q2, NEXMark Q9 winning bids, LogHub top templates | `RegionIndexedPriorityQueue` validates checked dense-key mutable ranking. Default local median removes GC but loses elapsed and RSS (`103.052 ms` vs heap `100.254 ms`). `StreamWindowTableRank` remains slower than heap-long at 1M (`568.572 ms` vs `437.702 ms`). | Natural workload same-shape heap; retained controls for bucket-owned records; profile that isolates lookup/update/heap maintenance. | Gated/negative performance evidence. | Do not return to DEBS ranking. If revisited, start with NEXMark Q9 or LogHub top templates and build a same-shape heap retained control first. |
| Median/percentile window | DEBS Q2, sensor rolling stats, latency percentile windows | No fair checked median operator has passed a focused gate. DEBS Q2 evidence is CPU/ranking-heavy and not clearly a memory-management problem. | Natural heap baseline, same-shape heap median/sketch control, retained control, focused 1M gate. | Deferred. | Use approximate sketches such as KLL/t-digest only if the target workload permits approximate percentiles; exact median stays out of the next milestone. |
| Hash/group aggregate | Dataflow AGGREGATE, LogHub sessions, Common Crawl domains | Direct epoch and retained-epoch rows already cover summary-on-append aggregate shapes. Generic `StreamWindowFold` failed its focused gate, so the current winning path is operator-owned direct epoch/page-token, not generic fold tables. | Same-shape heap for any new hash-table-based API; retained controls if records survive to close. | Partially solved by direct epoch/page-token for simple additive summaries; generic hash/fold still gated. | Continue using direct epoch or page-token for additive summaries. Only build a generic hash/fold operator when a workload cannot be expressed as append-time summaries plus bulk close. |

## Candidate Order

1. **LogHub top templates**: best next top-k/rank candidate because it uses real
   HDFS input, has richer object materialization potential, and naturally
   produces ranked templates/sessions.
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
