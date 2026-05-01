# Headline Stream Sweep: 2026-05-01

Run id: `2026-05-01-headline-streams`

Status: completed headline stream leg of the comprehensive evaluation sweep.

Command:

```sh
cd /Users/siyaoliu/rift
RIFT_EVAL_RUN_ID=2026-05-01-headline-streams \
RIFT_EVAL_SCALE=headline \
RIFT_EVAL_SUITES="preflight streams" \
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

Raw logs and TSV summaries were written under ignored cache:

`cache/perf-eval/2026-05-01-headline-streams/`

The runner produced seven summary TSVs:

- `common-crawl-wet/summary.tsv`
- `linear-road/summary.tsv`
- `nexmark-beam-default/summary.tsv`
- `nexmark-local/summary.tsv`
- `riotbench/summary.tsv`
- `wikimedia/summary.tsv`
- `yahoo-ad/summary.tsv`

All reported checksums and output counts matched across modes within each
query.

## NEXMark Beam-Default Profile

Input label: `beam-defaults-generated`.

These rows use local Scala Native execution with Beam-default generator
settings. They are methodology/profile evidence, not Apache Beam runner
evidence.

| Query | Heap ms / GC ms | Improved SafeZone ms / GC ms | Best Rift or checked row | Interpretation |
|---|---:|---:|---|---|
| Q0 passthrough | `521.508` / `78.399` | `478.500` / `19.959` | Streaming `475.161` / `17.261` GC | Trusted region row is fastest, but only slightly ahead of improved SafeZone. |
| Q1 conversion | `950.341` / `91.615` | `929.887` / `39.226` | Streaming `919.670` / `33.539` GC | Modest trusted win; checked `945.372` does not win elapsed. |
| Q2 selection | `586.607` / `62.864` | `576.228` / `24.707` | Streaming `563.282` / `18.876` GC | Region placement gives a modest win over both heap and improved SafeZone. |
| Q3 join/filter | `315.715` / `30.403` | `302.668` / `11.881` | checked `295.166` / `9.800` GC | Best checked NEXMark row in this sweep. |
| Q4 category average | `579.239` / `39.639` | `577.643` / `24.689` | HPZone `576.367` / `21.895` GC | Near-tie; lower GC but no meaningful elapsed separation. |
| Q5 hot items | `408.851` / `31.194` | `396.595` / `17.555` | Streaming `391.649` / `14.452` GC | Modest trusted win; checked remains close to improved SafeZone. |
| Q8 user/auction join | `470.798` / `34.303` | `457.725` / `17.559` | checked `457.518` / `16.024` GC | Checked is effectively tied with improved SafeZone and faster than heap. |
| Q9 winning bids | `809.525` / `89.112` | `756.972` / `33.479` | Streaming `751.602` / `29.608` GC | Trusted row is modestly fastest; improved SafeZone remains close. |
| Q11 sessions | `218.774` / `17.530` | `229.557` / `5.763` | HPZone `228.741` / `3.746` GC | Heap wins elapsed; region rows reduce GC only. |

## NEXMark Local Profile

Input label: `generated-local`.

The local profile broadly agrees with the Beam-default run: region rows reduce
GC, Q3 is the best checked row, and Q11 is heap-fastest.

| Query | Heap ms | Improved SafeZone ms | Best Rift or checked row | Interpretation |
|---|---:|---:|---|---|
| Q0 | `491.289` | `485.049` | HPZone `475.097` | Trusted stream-object win. |
| Q1 | `974.748` | `944.199` | Streaming `925.811` | Trusted conversion win. |
| Q2 | `597.925` | `577.482` | Streaming `572.383` | Small trusted win over improved SafeZone. |
| Q3 | `282.824` | `266.551` | checked `261.998` | Best checked local row. |
| Q4 | `593.196` | `586.167` | Streaming `577.810` | Trusted row modestly fastest. |
| Q5 | `476.656` | `439.133` | HPZone `437.589` | Improved SafeZone and HPZone nearly tied. |
| Q8 | `431.204` | `417.447` | checked `417.613` | Checked near-tie with improved SafeZone. |
| Q9 | `897.677` | `854.283` | Streaming `841.067` | Trusted row modestly fastest. |
| Q11 | `218.758` | `223.080` | Streaming `223.943` | Heap wins elapsed. |

## Other Stream Matrices

| Matrix / query | Heap ms / GC ms | Improved SafeZone ms / GC ms | Best Rift row | Interpretation |
|---|---:|---:|---|---|
| Common Crawl WET-shaped Q0 parse | `308.544` / `78.066` | `262.206` / `0.000` | Streaming `278.002` / `0.000` GC | Improved SafeZone wins; region rows beat heap but not improved SafeZone. |
| Common Crawl WET-shaped Q1 tokenization | `4770.503` / `1559.601` | `4066.435` / `29.563` | HPZone `4301.536` / `20.543` GC | Genuinely GC-heavy row; Rift cuts GC and beats heap, but improved SafeZone is faster. Current SafeZone remains pathological at `23146.633 ms`. |
| Yahoo Q0 parse | `109.512` / `15.566` | `106.568` / `0.000` median GC | HPZone `110.125` / `0.000` median GC | Improved SafeZone wins; region rows reduce max GC only. |
| Yahoo Q1 filter | `121.799` / `19.172` | `124.349` / `5.025` | Streaming `124.776` / `3.748` GC | Heap wins elapsed despite higher GC. |
| Yahoo Q2 campaign window | `105.802` / `6.575` | `106.425` / `2.566` | Streaming `106.415` / `1.932` GC | Near-tie; lower GC, no speed win. |
| RIoTBench Q0 parse | `114.167` / `15.735` | `109.643` / `0.000` median GC | HPZone `111.155` / `0.000` median GC | Improved SafeZone wins. |
| RIoTBench Q1 clean/annotate | `135.750` / `14.369` | `147.638` / `6.199` | Streaming `148.019` / `3.666` GC | Heap wins elapsed at 1M; this weakens the earlier 100k positive row. |
| RIoTBench Q2 window stats | `173.334` / `14.935` | `174.824` / `5.009` | Streaming `172.802` / `3.696` GC | Near-tie; Streaming is only slightly fastest. |
| Wikimedia Q0 pageviews | `70.128` / `12.771` | `69.121` / `0.000` | Streaming `71.445` / `0.000` | Improved SafeZone/heap control; not a Rift win. |
| Wikimedia Q1 counts | `157.685` / `33.518` | `154.351` / `3.179` | Streaming `157.850` / `2.402` GC | Improved SafeZone wins; Rift reduces GC but not elapsed. |
| Wikimedia Q2 clickstream | `160.355` / `33.343` | `159.537` / `3.311` | HPZone `162.228` / `2.169` GC | Generated TSV row no longer shows a Rift elapsed win in this clean sweep. |
| Linear Road Q0 reports | `105.276` / `9.030` | `105.137` / `0.000` | Streaming `106.837` / `0.000` | Near-tie, improved SafeZone marginally fastest. |
| Linear Road Q1 tolls | `186.394` / `26.891` | `189.515` / `0.000` median GC | Streaming `194.216` / `0.000` median GC | Heap wins elapsed; region rows lower GC only. |
| Linear Road Q2 accidents | `200.810` / `26.830` | `202.441` / `0.000` median GC | HPZone `210.127` / `0.000` median GC | Heap wins elapsed. |

## Interpretation

The stream sweep strengthens three conclusions:

- NEXMark Beam-default Q3 remains the best checked application-style row:
  checked Rift beats heap and improved SafeZone, but the margin is below the
  thesis-grade `>=10%` case-study gate.
- Generated Common Crawl WET-shaped tokenization is the clearest GC-heavy
  stream detector found so far. Heap spends about `1.56 s` in timed GC at 1M
  generated pages, but improved SafeZone beats trusted Rift on elapsed time.
- Yahoo, Wikimedia, RIoTBench, and Linear Road generated/preloaded probes are
  useful controls, but most rows are near-ties or heap/improved-SafeZone wins.

This does not justify returning to benchmark-specific tuning. It points back
to the framework problem: Rift needs cheaper checked operators for the
allocation-heavy shapes where region placement removes GC but container/API CPU
overhead still consumes the benefit.
