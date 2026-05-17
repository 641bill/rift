# Current Rift Status

Last updated: 2026-05-18 00:22 CEST

Status: hot status file. Update this file for routine turn-by-turn progress
instead of editing `docs/HANDOFF.md`, `docs/ROADMAP.md`,
`docs/PERFORMANCE_EVALUATION_REPORT.md`, or `docs/report.html`.

## Current Work Split

| Track | Current owner boundary | Latest status |
|---|---|---|
| Native backend | `scala-native-rift/nativelib/**`, `nscplugin/**`, `unit-tests/native/**`, `sandbox/**` | Scala Native remains the only validated performance backend. Native sandbox compile passed after portable prototype extraction. |
| Backend portability | parent branch `backend-portability` | JVM/HotSpot/Scala.js/Wasm portability docs, prototype evidence, and `experimental/**` patch exports are isolated on `backend-portability` at `065b521`. Keep `main` focused on Scala Native evidence unless backend results are intentionally promoted to presentation context. |
| Benchmark search | parent `evidence/**` plus child sandbox result files | Broom q17 retained join/aggregate and Broom shopper are complete generated methodology rows. SPECjbb/Stancu-style 8M transaction scaling is recorded as generated clean-room methodology evidence, not real-input proof. LogHub Spark archive-wide retained session is now the strongest LogHub real-streaming RSS/fixed-memory row, AskUbuntu compressed streaming scales to 5M, and Yak LiveJournal now has a 20M compressed-source graph streaming row with RSS/fixed-memory, heap-cap, and throughput gains but low GC-time share. Real-input search remains focused on retained-object workloads because Immix keeps many parser/filter/count real streams low-GC. |
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
- Previous checked suites also passed:
  `RiftRegionCheckedCompilerTest` `141/141`,
  `RiftRegionCheckedTest` `65/65`.

## Immediate Next Choices

1. If continuing backend portability, switch to `backend-portability` first;
   do not mix HotSpot/JVM prototype churn into `main`.
2. If continuing Native evidence, move from completed q17/shopper/SPECjbb,
   Spark retained-session, AskUbuntu compressed-streaming, and Yak LiveJournal
   compressed graph streaming rows to a disk/time preflight for larger
   SNAP/Twitter graph streaming or a provenance-clean larger
   StackOverflow/StackExchange compressed dump. Park the current LogHub,
   AskUbuntu, and LiveJournal variants unless the next query retains more state
   than parser/hash/XML/edge scanning work.
3. If preparing presentation, update `PERFORMANCE_EVALUATION_REPORT.md` and
   regenerate `report.html`; otherwise leave them alone.
