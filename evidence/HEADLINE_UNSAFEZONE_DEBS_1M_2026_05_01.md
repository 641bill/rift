# Headline UnsafeZone-HP DEBS 1M Sweep

Date: 2026-05-01

Status: bounded DEBS 2015 RunBoth 1M single-run sweep with `unsafezone-hp`
included. This is a correctness/control row, not a 3-run median and not a
full-month replacement.

Run id: `2026-05-01-unsafezone-debs-1m`

Input: `/tmp/debs2015-month1-1000000.csv`

Raw logs and outputs:
`cache/perf-eval/2026-05-01-unsafezone-debs-1m/`

Command:

```sh
cd /Users/siyaoliu/rift
DEBS2015_BOTH_INPUT=/tmp/debs2015-month1-1000000.csv \
RIFT_EVAL_RUN_ID=2026-05-01-unsafezone-debs-1m \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight debs" \
bash scripts/run-performance-evaluation.sh
```

The run completed both normal and instrumented RunBoth legs. Both reported
matching Q1/Q2 outputs after the standard latency stripping.

## Normal RunBoth Row

Source: `logs/debs-runboth.log`. Single run per mode.

| Mode | Elapsed ms | Throughput eps | GC ms | Q1 process ms | Q2 process ms | Close ms | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| heap | 4861.406 | 205701.816 | 24.509 | 1464.058 | 1256.285 | 5.681 | Heap baseline. |
| safezone-current | 5489.362 | 182170.534 | 54.794 | 1629.459 | 1622.421 | 131.606 | Current SafeZone remains slow here. |
| safezone-improved | 5341.010 | 187230.507 | 54.616 | 1612.065 | 1607.798 | 32.554 | Improved SafeZone is still slower than heap on this bounded row. |
| unsafezone-hp | 4639.791 | 215526.946 | 1.623 | 1417.282 | 1161.549 | 5.252 | Fastest normal row; unsafe substrate evidence. |
| rift-hp | 4738.989 | 211015.490 | 0.701 | 1452.904 | 1209.098 | 9.549 | Faster than heap, slower than unsafezone-hp. |
| rift-streaming | 4663.529 | 214429.905 | 0.658 | 1431.079 | 1158.002 | 5.725 | Close to unsafezone-hp; faster than heap. |
| rift-checked | 4844.738 | 206409.498 | 19.563 | 1580.441 | 1282.812 | 3.695 | Correct, but slower than trusted/unsafe rows and roughly heap-adjacent. |

## Instrumented Row

Source: `debs-runboth-instrumented/summary.tsv`. Single run per mode. This leg
does not include `rift-checked`.

| Mode | Elapsed ms | GC ms | Rift op ms | RSS bytes | Q1 process ms | Q2 process ms | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| heap | 4705.254 | 22.251 | 0.000 | 161251328 | 1425.355 | 1217.033 | Heap baseline. |
| safezone-current | 5373.022 | 56.938 | 0.000 | 108118016 | 1596.704 | 1564.287 | Lower RSS but slower. |
| safezone-improved | 5420.896 | 54.527 | 0.000 | 108118016 | 1636.544 | 1642.094 | Lower RSS but slower. |
| unsafezone-hp | 4720.234 | 1.564 | 0.000 | 109608960 | 1446.127 | 1210.940 | Near heap/Rift elapsed, much lower timed GC/RSS than heap. |
| rift-hp | 4694.310 | 0.660 | 10.545 | 116998144 | 1440.702 | 1195.272 | Fastest instrumented row by a small margin. |
| rift-streaming | 4691.125 | 0.650 | 11.188 | 117276672 | 1433.074 | 1191.584 | Fastest instrumented row by a small margin. |

## Interpretation

This row is useful but not final application evidence:

- `unsafezone-hp` is the fastest normal bounded 1M row, beating heap by about
  4.6%, improved SafeZone by about 13.1%, Rift HPZone by about 2.1%, and Rift
  Streaming by about 0.5%.
- The instrumented leg is close: trusted Rift is slightly faster than
  UnsafeZone-HP, and all three trusted/unsafe region-family rows are close to
  heap on elapsed time while cutting timed GC and RSS.
- The SafeZone-derived no-root substrate helps DEBS more than improved
  SafeZone does on this bounded row, but this is still unsafe and single-run.
- Checked Rift remains correct but does not win this row. The gap is still
  checked operator/application overhead, not raw region allocation alone.

## Next Use

Use this as a bounded control when choosing the next runtime direction. It
supports investigating a safe, Rift-checked runtime built on or modeled after
SafeZone allocator/pool mechanics. It does not justify exposing UnsafeZone-HP
as a public mode.
