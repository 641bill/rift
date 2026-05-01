# Headline UnsafeZone-HP Stream Sweep

Date: 2026-05-01

Status: clean 5-run headline stream medians with `unsafezone-hp` included.
This supersedes older stream rows where the same query/input/mode overlaps.

Run id: `2026-05-01-unsafezone-streams`

Raw logs and summaries:
`cache/perf-eval/2026-05-01-unsafezone-streams/`

Command:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-unsafezone-streams \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight streams" \
bash scripts/run-performance-evaluation.sh
```

The first attempt failed because sbt needed to write
`/Users/siyaoliu/.sbt/boot/sbt.boot.lock` outside the sandbox. The successful
run was rerun with approval. The recorded run itself completed successfully.

Summary files:

- `cache/perf-eval/2026-05-01-unsafezone-streams/summaries/nexmark-local/summary.tsv`
- `cache/perf-eval/2026-05-01-unsafezone-streams/summaries/nexmark-beam-default/summary.tsv`
- `cache/perf-eval/2026-05-01-unsafezone-streams/summaries/yahoo-ad/summary.tsv`
- `cache/perf-eval/2026-05-01-unsafezone-streams/summaries/riotbench/summary.tsv`
- `cache/perf-eval/2026-05-01-unsafezone-streams/summaries/wikimedia/summary.tsv`
- `cache/perf-eval/2026-05-01-unsafezone-streams/summaries/common-crawl-wet/summary.tsv`
- `cache/perf-eval/2026-05-01-unsafezone-streams/summaries/linear-road/summary.tsv`

## Main Interpretation

UnsafeZone-HP changes the stream evidence in a narrower way than hoped:

- It is often the best SafeZone-family row and occasionally the best overall
  row among non-checked/trusted modes.
- It usually improves only slightly over improved SafeZone, so root mode `1`
  still captures most of the SafeZone fix.
- It does not make current Rift HPZone/Streaming look like the fastest runtime
  substrate on these stream probes.
- It strengthens the design direction "learn from or build on SafeZone
  internals, then add Rift-style static checking", not "ship unsafe no-root
  regions".
- None of these stream rows become a large `>=10%` Rift-over-improved-SafeZone
  case-study result. The best continued checked rows are NEXMark Q3 and Q8,
  but their margins remain below the case-study gate.

## NEXMark Beam-Default Profile

All rows are 1M generated Beam-default-profile events and 5-run medians in ms.
`Best Rift` includes checked/trusted Rift modes; `Unsafe` is the benchmark-only
SafeZone no-root control.

| Query | heap | improved SafeZone | Unsafe | Best Rift | Winner | Interpretation |
|---|---:|---:|---:|---:|---|---|
| q0 passthrough | 520.052 | 481.133 | 468.617 | HPZone `472.017` | Unsafe | Unsafe is near a 10% heap win, but only 2.6% over improved SafeZone. |
| q1 currency conversion | 938.096 | 934.844 | 918.143 | Streaming `917.304` | Streaming | Trusted Rift and Unsafe tie closely; modest win only. |
| q2 selection | 590.798 | 573.150 | 564.900 | HPZone `560.741` | HPZone | Modest region-friendly row; not a 10% case-study win. |
| q3 incremental join/filter | 316.626 | 297.962 | 296.480 | checked `292.371` | checked | Best checked stream row; beats heap 7.7%, improved SafeZone 1.9%. |
| q4 category average | 570.751 | 576.226 | 568.913 | HPZone `573.416` | Unsafe | Near-tie; not a useful claim row. |
| q5 hot items | 407.859 | 393.192 | 390.686 | HPZone `389.816` | HPZone | Modest region row; Q5 still needs cheaper aggregate/window APIs. |
| q8 window join | 467.213 | 462.599 | 460.822 | checked `450.904` | checked | Checked row beats heap and improved SafeZone, but below 10%. |
| q9 winning bids | 794.645 | 747.382 | 747.657 | HPZone `744.121` | HPZone | Region rows cluster; not a checked win. |
| q11 sessions | 218.200 | 226.184 | 223.644 | HPZone `226.909` | heap | Heap wins elapsed; regions lower GC but not enough. |

## Other Stream Matrices

All rows are 1M generated/profile events unless noted.

| Workload | Query | heap | improved SafeZone | Unsafe | Best Rift | Interpretation |
|---|---|---:|---:|---:|---:|---|
| Yahoo-style ad | q0 parse | 108.717 | 106.710 | 106.114 | HPZone `108.643` | Unsafe is best, but margin is tiny. |
| Yahoo-style ad | q1 filter | 122.895 | 124.230 | 122.977 | HPZone `125.027` | Heap/Unsafe near tie; no region win. |
| Yahoo-style ad | q2 campaign window | 105.148 | 106.104 | 105.802 | HPZone `106.331` | Heap wins elapsed; region rows lower GC/RSS. |
| RIoTBench-style | q0 parse | 113.022 | 111.307 | 109.020 | HPZone `111.418` | Unsafe is best; modest. |
| RIoTBench-style | q1 clean/annotate | 135.226 | 147.639 | 144.789 | Streaming `148.201` | Heap wins; region placement is overhead here. |
| RIoTBench-style | q2 window stats | 168.680 | 172.079 | 169.331 | Streaming `170.810` | Near-tie; heap slightly wins. |
| Wikimedia generated | q0 pageviews | 70.495 | 69.154 | 67.964 | HPZone `72.238` | Unsafe wins generated TSV row; not a Rift win. |
| Wikimedia generated | q1 counts | 156.262 | 154.323 | 151.536 | Streaming `158.145` | Unsafe wins; current Rift loses. |
| Wikimedia generated | q2 clickstream | 160.500 | 159.147 | 155.768 | Streaming `162.253` | Unsafe wins; current Rift loses. |
| Common Crawl WET-shaped | q0 parse | 308.803 | 262.141 | 256.847 | Streaming `278.555` | Unsafe/improved SafeZone beat Rift and heap. |
| Common Crawl WET-shaped | q1 tokenization | 4743.205 | 4028.067 | 3971.051 | HPZone `4322.349` | GC-heavy row; Unsafe wins, Rift beats heap but not SafeZone. |
| Linear Road generated | q0 reports | 100.318 | 105.724 | 104.879 | Streaming `107.008` | Heap wins. |
| Linear Road generated | q1 tolls | 186.882 | 189.833 | 190.565 | HPZone `195.038` | Heap wins. |
| Linear Road generated | q2 accidents | 206.491 | 205.889 | 201.977 | HPZone `209.727` | Unsafe wins slightly; Rift loses. |

## GC And RSS Notes

- Common Crawl WET-shaped q1 remains the strongest GC-heavy detector: heap
  spends `1538.107 ms` in timed GC and has `408567808` byte max RSS. Unsafe
  reduces timed GC to `20.560 ms` but increases max RSS to `463601664` bytes.
  Rift HPZone similarly cuts GC (`20.679 ms`) but is slower than Unsafe and
  improved SafeZone.
- NEXMark Beam-default q0/q1/q2/q3/q8/q9 consistently show lower timed GC in
  Unsafe/Rift rows than heap, but elapsed gains are modest because stream CPU
  and benchmark logic still matter.
- Wikimedia generated rows now favor UnsafeZone-HP, while earlier real TSV rows
  favored heap. Keep Wikimedia as generated/real-input contrast evidence, not
  a Rift case study.

## Decision

This sweep strengthens the SafeZone-substrate hypothesis:

1. `unsafezone-hp` should remain in the benchmark matrix as an unsafe diagnostic
   baseline.
2. The next runtime design question is whether a safe Rift implementation can
   reuse/match SafeZone allocator and pool mechanics while retaining static
   capture/rooting guarantees.
3. Current Rift HPZone/Streaming should not be tuned in isolation until we know
   why SafeZone internals win on most linked/prior/stream rows.
4. The next measurement gap is bounded/full DEBS with `unsafezone-hp` included.
