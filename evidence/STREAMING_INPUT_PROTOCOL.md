# Streaming Input Protocol

Date: 2026-05-11
Last updated: 2026-05-11 23:49 CEST

Status: active protocol for converting real-data benchmarks from preloaded or
file-backed controls into true streaming-input replay.

## Purpose

`real-streaming-input` rows model bounded replay of a real stream: the program
consumes records incrementally from a source, never preloads all records into
arrays/lists, and keeps memory bounded by active epochs/windows plus durable
keyed state. These rows are the stream-processing evidence class. Existing
`real-preloaded` and `real-file-backed` rows remain useful controls, but they
are not enough for final streaming-input claims.

## Input Classes

| Class | Meaning | Allowed use |
|---|---|---|
| `real-preloaded` | real data parsed or loaded before the timed loop | memory-management control; isolates GC/region work from IO/parser cost |
| `real-file-backed` | file IO occurs in the benchmark, but the implementation may use benchmark-specific buffering or precomputed structures | end-to-end control; not automatically streaming evidence |
| `real-streaming-input` | cursor/visitor source reads records incrementally, no total-input arrays/lists, bounded active state | stream-processing case-study candidate |

## Required Streaming Semantics

- A `streaming-file` mode must reopen the configured real input for each run.
- It must not retain parsed arrays proportional to the total requested records.
- It must report actual records loaded, bytes read, input file count, checksum
  or output count, and parse/late/drop counts where applicable.
- Count/order epochs are allowed for sources without reliable timestamps.
- Event-time windows should be used when timestamps are cheap and meaningful;
  v1 uses deterministic bounded replay, not Kafka/Flink/Beam runtime services.
- Durable keyed state may remain on heap or primitive arrays; short-lived
  per-record/window objects should use checked epoch or page/window regions.

## Measurement Rules

- L1 final-clean rows report only external elapsed/RSS plus minimal input and
  checksum/output metadata.
- L2 standard stats add GC median/max, runs-with-GC, region counters, live
  windows/epochs where available, and streaming-specific parse/late/drop counts.
- L3/L4 diagnostics and profiles are never headline elapsed evidence.
- A streaming win requires a checked framework API row, a matching heap or
  same-shape heap control, and either throughput, RSS, fixed-memory, GC, or
  tail-latency improvement under the fair evaluation protocol.

## Initial Implementation

The first converted row is `LogHubTopTemplatesMatrix` with
`LOGHUB_TOP_INPUT_MODE=streaming-file`. It uses
`BenchmarkInputSupport.StreamingByteLineSource` to read HDFS log lines directly
inside each benchmark run. The old `file-backed` mode still preloads parsed
primitive arrays and remains a `real-preloaded` memory-management control.

