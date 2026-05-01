# DEBS 2015 Bounded 1M Sweep: 2026-05-01

Run id: `2026-05-01-headline-debs-1m`

Status: completed bounded 1M DEBS leg of the comprehensive evaluation sweep.

Command:

```sh
cd /Users/siyaoliu/rift
DEBS2015_BOTH_INPUT=/tmp/debs2015-month1-1000000.csv \
RIFT_EVAL_RUN_ID=2026-05-01-headline-debs-1m \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight debs" \
bash scripts/run-performance-evaluation.sh
```

Environment recorded by the runner:

| Field | Value |
|---|---|
| Parent repo | `/Users/siyaoliu/rift` |
| Parent branch / commit | `main` / `7c2e6e56fd19bfcaf87b7ac0397f6079f2b536ac` |
| Child repo | `/Users/siyaoliu/rift/scala-native-rift` |
| Child branch / commit | `feature/rift` / `b74658903584f30474f6ce0c1fec21164b95dbab` |
| Machine | Apple M4 Pro, 24 GiB RAM |
| OS | Darwin 25.4.0 arm64 |
| Java | Temurin 17.0.18 |
| Input | `/tmp/debs2015-month1-1000000.csv` |

Raw logs and outputs were written under ignored cache:

`cache/perf-eval/2026-05-01-headline-debs-1m/`

Both scripts completed and reported output equality:

- `RunBoth sample matrix outputs match`
- `RunBoth instrumented matrix outputs match`

This is a bounded 1M single-run leg, not a 3-run median. Use it as a clean
same-run direction check and correctness control.

## Normal RunBoth

Modes: `heap`, `rift-hp`, `rift-streaming`, `rift-checked`.

| Mode | Elapsed ms | Throughput events/s | GC ms | Rift op ms | Region objects | Peak active alloc bytes | Q1 outputs | Q2 outputs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | `4987.579` | `200498.067` | `24.027` | `0.000` | `0` | `0` | `32209` | `24969` |
| rift-hp | `4724.194` | `211676.331` | `0.663` | `10.721` | `5494565` | `105385960` | `32209` | `24969` |
| rift-streaming | `4681.292` | `213616.235` | `0.664` | `11.711` | `5494565` | `105385960` | `32209` | `24969` |
| rift-checked | `4882.562` | `204810.493` | `19.864` | `6.815` | `5940011` | `35003208` | `32209` | `24969` |

Interpretation:

- Trusted Streaming is the fastest row in the normal single-run matrix,
  `6.1%` faster than heap.
- Checked Rift is `2.1%` faster than heap in this run, but still much slower
  than trusted Rift and still pays meaningful timed GC.
- Checked active region payload is much smaller than trusted active payload in
  this bounded row (`35.0 MB` peak active alloc bytes vs `105.4 MB`), but this
  table does not include checked RSS because the default instrumented script
  does not include `rift-checked`.

## Instrumented RunBoth

Modes: `heap`, `rift-hp`, `rift-streaming`.

The instrumented script runs the linked native binary under `/usr/bin/time -l`
and writes `summary.tsv`.

| Mode | Elapsed ms | Real s | User s | Sys s | RSS bytes | GC ms | Rift op ms | Region objects | Peak active alloc bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heap | `4774.666` | `5.07` | `4.70` | `0.08` | `161267712` | `24.271` | `0.000` | `0` | `0` |
| rift-hp | `4712.907` | `4.71` | `4.63` | `0.07` | `116965376` | `0.652` | `10.114` | `5494565` | `105385960` |
| rift-streaming | `4716.524` | `4.72` | `4.65` | `0.06` | `117243904` | `0.661` | `11.096` | `5494565` | `105385960` |

## Instrumented Phase Timers

Phase timers are from the instrumented run and are shown in milliseconds.

| Mode | Read | Parse | Q1 process | Q1 change | Q2 process | Q2 change | Output + snapshots + close |
|---|---:|---:|---:|---:|---:|---:|---:|
| heap | `408.280` | `1094.836` | `1439.825` | `115.357` | `1262.427` | `185.396` | `144.851` |
| rift-hp | `413.805` | `1096.303` | `1444.440` | `115.398` | `1183.286` | `185.259` | `153.700` |
| rift-streaming | `404.293` | `1097.270` | `1443.294` | `114.958` | `1196.933` | `184.917` | `153.133` |

Interpretation:

- The main trusted win in this bounded run comes from lower Q2 process time and
  lower GC/RSS, not from region bookkeeping being visible in the total time.
- Parse plus Q1/Q2 processing still dominate elapsed time. That matches the
  broader finding that Rift needs cheaper checked operators and more careful
  operator CPU work before DEBS can be a large checked speedup.
- Bounded 1M still differs from the full-month DEBS story; do not replace the
  full-month rows with this single-run result.
