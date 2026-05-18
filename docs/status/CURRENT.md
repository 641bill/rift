# Current Rift Status

Last updated: 2026-05-18 16:22 CEST

Status: hot status file. Update this file for routine turn-by-turn progress
instead of editing `docs/HANDOFF.md`, `docs/ROADMAP.md`,
`docs/PERFORMANCE_EVALUATION_REPORT.md`, or `docs/report.html`.

## Current Work Split

| Track | Current owner boundary | Latest status |
|---|---|---|
| Native backend | `scala-native-rift/nativelib/**`, `nscplugin/**`, `unit-tests/native/**`, `sandbox/**` | Scala Native remains the only validated performance backend. Native sandbox compile passed after portable prototype extraction. |
| Backend portability | parent branch `backend-portability` | JVM/HotSpot/Scala.js/Wasm portability docs, prototype evidence, and `experimental/**` patch exports are isolated on `backend-portability` at `065b521`. Keep `main` focused on Scala Native evidence unless backend results are intentionally promoted to presentation context. |
| Benchmark search | parent `evidence/**` plus child sandbox result files | Broom q17 retained join/aggregate and Broom shopper are complete generated methodology rows. SPECjbb/Stancu-style 8M transaction scaling is recorded as generated clean-room methodology evidence, not real-input proof. LogHub Spark archive-wide retained session, Yak LiveJournal streaming graph, AskUbuntu streaming text, and the new named Wikimedia retained clickstream-session row are all recorded as compressed real-streaming evidence. The strongest real-streaming retained-object rows are now Theodolite retained UC4 and Wikimedia retained clickstream-session. |
| Presentation report | `docs/PERFORMANCE_EVALUATION_REPORT.md` and generated `docs/report.html` | Do not edit/regenerate unless presentation claims or tables change. |

## Latest Validation

- Portable prototype standalone compile:
  `scalac -d /tmp/portable-rift-classes experimental/portable-rift/src/main/scala/rift/portable/PortableRiftBackendPrototype.scala`
  passed.
- Portable prototype smoke:
  `scala run --server=false ... --main-class rift.portable.PortableRiftBackendPrototype`
  passed.
- Native sandbox compile after extraction:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- Native sandbox compile after q17:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- Native sandbox compile after archive-wide LogHub input support:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- Native sandbox compile after Yak `YAK_GRAPH_INPUT_MODE=streaming-file`:
  `ENABLE_EXPERIMENTAL_COMPILER=1 sbt "project sandbox3_next" compile`
  passed.
- Broom q17 20M active-16: checked Rift `9.67 s`, `49.9 MB`, zero timed GC
  versus heap `14.45 s`, `231.7 MB`, L2 GC `1370.380 ms`.
- SPECjbb/Stancu-style 8M generated transaction row: L1 heap `4.89 s`
  versus checked epoch stream `4.35 s` and checked epoch scoped `3.95 s`;
  L2 heap `1379.590 ms` with `164.932 ms` GC / `520` collections versus
  checked epoch stream `996.765 ms`, `0.515 ms` GC, and `4.075 ms` region-op.
- LogHub Spark archive-wide retained session, 1M active-16 over compressed
  `tar.gzcat:/Users/siyaoliu/rift/cache/benchmark-data/loghub/Spark.tar.gz`:
  L1 heap `27.62 s`, RSS `391 MB`; checked Rift `20.30 s`, RSS `73 MB`;
  checked scoped `19.85 s`, RSS `73 MB`. L2 heap GC is `140.639 ms` inside
  `6642.276 ms`, so this is strong real-streaming RSS/fixed-memory evidence
  but not a GC-time flagship. Heap caps pass at `256M` and fail at `128M`.
- AskUbuntu true streaming text, 5M tokens over compressed
  `7z:/Users/siyaoliu/rift/cache/benchmark-data/yak/stackexchange/askubuntu.com.7z!Posts.xml`:
  L1 checked epoch scoped `6.23 s`, RSS `15 MB`, versus heap `6.74 s`,
  RSS `41 MB`; L2 heap GC is only `27.237 ms` inside `2109.524 ms`, so this
  remains modest RSS/fixed-memory text evidence rather than a GC-heavy row.
- Yak LiveJournal true streaming graph, 20M edges over compressed
  `/Users/siyaoliu/rift/cache/benchmark-data/yak/snap/soc-LiveJournal1.txt.gz`:
  L1 checked epoch scoped `17.15 s`, RSS `102 MB`, versus heap `18.32 s`,
  RSS `577 MB`; L2 checked epoch stream `5530.190 ms`, GC `0 ms`, region op
  `2.869 ms`, versus heap `6333.745 ms`, GC `165.387 ms`. This is strong
  real-streaming graph RSS/fixed-memory and throughput evidence, but heap GC is
  still only about `2.6%` of L2 elapsed. One-run cap probes: heap passes
  `128M` and fails `64M`; checked epoch stream/scoped pass `64M` and `32M`.
- Wikimedia enwiki retained clickstream-session, 1M rows over compressed
  `/Users/siyaoliu/rift/cache/benchmark-data/wikimedia/clickstream-enwiki-2026-03.tsv.gz`:
  L1 checked Rift `5.81 s`, RSS `138 MB`, versus heap `6.50 s`,
  RSS `784 MB`; L2 heap `2038.262 ms`, GC `150.157 ms`, while checked Rift
  is `1952.438 ms`, GC `9.237 ms`, region op `1.871 ms`. Heap caps fail even
  at `512M`; checked rows pass at `128M` and `64M`. Use this as
  real-streaming retained clickstream throughput/RSS/GC/fixed-memory evidence
  over public Wikimedia data, not an official Wikimedia benchmark artifact.
- Wikimedia retained clickstream-session 5M scale-up:
  L1 checked Rift `27.86 s`, RSS `138 MB`, versus heap `28.77 s`,
  RSS `1.54 GB`; L2 checked Rift `9486.647 ms`, GC `46.492 ms`, region op
  `10.699 ms`, versus heap `9459.416 ms`, GC `334.176 ms`, max GC
  `1066.487 ms`. Heap caps fail at `1G`, `768M`, and `512M`; checked Rift and
  checked scoped pass under a `64M` GC heap cap. Classify this as 5M
  scale-up RSS/fixed-memory and GC-tail evidence, with only a modest L1
  throughput win and essentially tied L2 loop throughput.
- Wikimedia retained clickstream-session 10M 3-run scale-up:
  L1 checked Rift `59.37 s`, RSS `138 MB`, versus heap `62.52 s`,
  RSS `1.80 GB`; L2 checked Rift `19635.995 ms`, GC `96.069 ms`, region op
  `24.329 ms`, versus heap `20103.863 ms`, GC `851.023 ms`. Heap caps fail at
  `1G`, `768M`, and `512M`; checked Rift and checked scoped pass under a
  `64M` GC heap cap. This is now report-grade real-streaming retained
  clickstream throughput/RSS/GC/fixed-memory scale-up evidence.
- Wikimedia retained clickstream-session full-file feasibility:
  one-run L1 checked Rift `69.87 s`, RSS `136 MB`, versus heap `74.23 s`,
  RSS `2.30 GB`; one-run L2 checked Rift `71149.579 ms`, GC `318.165 ms`,
  region op `79.786 ms`, versus heap `72750.014 ms`, GC `7122.811 ms`.
  This processed all `35862259` compressed rows with matching checksum/output.
  Keep the 10M x3 row as the report-grade median until the full-file row is
  repeated.
- Real-streaming evidence is now consolidated in the compact representative
  table at the top of `evidence/REAL_STREAMING_INPUT_MATRIX.md`: Theodolite
  retained UC4, LogHub Spark retained session, Wikimedia retained clickstream,
  Yak LiveJournal streaming graph, and AskUbuntu streaming text are classified
  with L1 elapsed/RSS, L2 GC/region interpretation, heap-cap status,
  checksum/output, and allowed claim.
- `docs/PERFORMANCE_EVALUATION_REPORT.md`, `docs/RIFT_EVALUATION_SUMMARY_SLIDES.md`,
  and generated `docs/report.html` include the Wikimedia scale-up in
  presentation-facing summaries, not only in the raw evidence files.
- Previous checked suites also passed:
  `RiftRegionCheckedCompilerTest` `141/141`,
  `RiftRegionCheckedTest` `65/65`.

## Immediate Next Choices

1. If continuing backend portability, switch to `backend-portability` first;
   do not mix HotSpot/JVM prototype churn into `main`.
2. If continuing Native evidence, the current local compressed real-streaming
   ladder is mostly classified, and the Wikimedia named clickstream-session row
   now has a 10M 3-run median plus one-run full-file feasibility. The next
   useful step is either a full-file 3-run median if machine time allows, or a
   provenance/disk preflight for truly larger StackOverflow/Twitter-2010 data.
3. If preparing presentation, update `PERFORMANCE_EVALUATION_REPORT.md` and
   regenerate `report.html`; otherwise leave them alone.
