# Stateful Functions Catalog

Stateful functions keep running or windowed state across messages and use `{}` after the function name.

## Syntax

```qql
function{initArgs}(dynamicArgs)
```

- Init arguments in `{}` are constants.
- Message-dependent values go in `(...)`.

## Window and Emission Keywords

- `RUNNING`: emit value for each input message.
- `OVER TIME(interval)` / `OVER COUNT(n)`: bounded windows.
- `OVER OPEN TIME(interval)` / `OVER CLOSE TIME(interval)`: choose bucket timestamp boundary.
- `OVER TIME(interval, offset)`: shift time buckets by an offset.
- `TRIGGER OVER ...`: periodic snapshots over cumulative scope.
- `RESET OVER ...`: reset state at each period boundary.
- `EVERY`: emit empty-period snapshots where supported.

For connected-server function availability checks, prefer `list_qql_functions` when available. See `references/concepts/stateless-functions.md` and `references/mcp-workflow.md`.

## Core Aggregates

Use for classic stream aggregation:

- `count{}()`: message count.
- `sum{}(x)`: running/windowed sum.
- `avg{}(x)`: running/windowed average.
- `min{}(x)`, `max{}(x)`: extrema.
- `first{}(x)`, `last{}(x)`: first/last seen values.

| Function | Init args | Notes |
|---|---|---|
| `count{}()` | none | Counts input messages. |
| `max{}(x)`, `min{}(x)` | none, `timePeriod`, or `period` | Extrema over all input or the function-local time/count window. |
| `sum{}(x)` | none, `timePeriod`, or `period` | Sums numeric values; exact return type follows input numeric type family. |
| `avg{}(x)` | none | Averages numeric values. Use moving-average functions for explicit smoothing windows. |
| `first{}(x)`, `last{}(x)` | none | First/last field value in the current query state/window. For whole messages use `SELECT first (*)` / `SELECT last (*)` from `references/query-generation.md`. |

Example:

```qql
SELECT RUNNING avg{}("price") AS 'avgPrice'
FROM "trades"
OVER TIME(1m)
GROUP BY symbol
```

## Moving Averages and Smoothers

Use for trend smoothing:

- `sma{timePeriod|period}(x)`
- `ema{period|factor}(x)`
- `cma{}(x)`
- `kama{period}(x)`
- `lsma{pointWindow|timeWindow, useDateTime}(x)`
- `mma{period}(x)`

Example:

```qql
SELECT RUNNING
    sma{timePeriod: 30m}("price") AS 'sma30',
    ema{period: 20}("price") AS 'ema20'
FROM "quotes"
OVER TIME(2h)
```

## Volatility and Indicator Functions

Use for technical analysis:

- `bollinger{pointWindow|timeWindow, factor}(x)`
- `atr{period}(open, high, low, close, volume)`
- `adxr{period}(open, high, low, close, volume)`

Example:

```qql
SELECT (bollinger{timeWindow: 1h}("price") AS 'b').*
FROM "quotes"
```

## Stateful Collection and Window Helpers

Use for rolling structures and derived series:

- `window{period|timePeriod}(x)` -> sliding array.
- `statWindow{period|timePeriod}(x)` -> stats object.
- `collect_unique{}(x)` -> distinct values array.
- `lastNotNull{}(x)` -> forward-fill non-null values.
- `timeOfMin{}(x)`, `timeOfMax{}(x)` -> timestamp of extrema.

`statWindow{...}(x)` exposes fields such as `sum`, `count`, `sumOfSquares`, `sumOfAbs`, `geometricMean`, `harmonicMean`, `firstRawMoment`, `secondRawMoment`, `thirdRawMoment`, `forthRawMoment`, `variance`, `standardDeviation`, `median`, `min`, and `max`.

`timeOfMin{}(x)` and `timeOfMax{}(x)` can return multiple timestamps for tied extrema; the returned array size is server-limited.

Example:

```qql
SELECT size(collect_unique{}(symbol)) AS 'symbolCount'
FROM "securities"
WHERE type == "deltix.timebase.api.messages.InstrumentType":FX
```

## Histogram

Use `histogram{...}(x)` for approximate quantiles over numeric distributions such as latency, execution time, or traded size.

| Init arg | Use |
|---|---|
| `q` | Array of quantiles, for example `[0.5, 0.9, 0.99, 0.999]`; each value must be between 0 and 1. |
| `significantDigits` | Precision from 0 to 5. Higher values improve precision and cost more memory. |
| `min` | Integer-histogram lower tracked value; must be an integer `>= 1`. May be rounded down internally. |
| `max` | Integer-histogram upper tracked value; must be an integer `>= 2`. |
| `maxToMinRatio` | Positive floating-point dynamic range for double histograms. Use when values span a large range. |

Rules:

- The result is an array with the same length/order as `q`.
- Values are approximate, not exact sorted quantiles.
- Use integer histogram bounds for integer durations/counts when possible.
- Use `min`/`max` for integer histograms; use `maxToMinRatio` for floating-point histograms.
- Use `significantDigits: 3` as a balanced default unless the user asks for more precision.

Latency percentiles by minute:

```qql
WITH ("TradeMessage":"receiveTime" - "TradeMessage":"entryTime") AS 'latencyNs'
SELECT
    histogram{q: [0.5, 0.99], significantDigits: 3, min: 1, max: 10000000000}("latencyNs") AS 'latencyPercentilesNs'
FROM "messages"
OVER TIME(1m)
WHERE THIS IS "TradeMessage" AND timestamp BETWEEN '2025-11-07 10:00:00 GMT'd AND '2025-11-07 11:00:00 GMT'd
```

Execution-time distribution:

```qql
SELECT histogram{q: [0.5, 0.9, 0.99, 0.999], significantDigits: 3, min: 1, max: 10000000}("executionTimeUs") AS 'executionLatency'
FROM "executionEvents"
```

Trade-size percentiles:

```qql
SELECT histogram{q: [0.5, 0.9, 0.99], significantDigits: 5}("entry"."size") AS 'sizePercentiles'
FROM "BITFINEX"
ARRAY JOIN "entries" AS "entry"
WHERE "entry" IS "TradeEntry" AND symbol == 'BTC/USDT'
```

## Order Book Reconstruction

Use `orderBook{...}(packageType, entries)` to maintain order-book state from PackageHeader snapshots and incremental updates.

| Init arg | Use |
|---|---|
| `maxDepth` | Maximum depth returned in the reconstructed book. |
| `model` | By default 'L2'; may also be 'L1' and 'L3' when schema supports it. |

Rules:

- `orderBook` is stateful and uses `{}`.
- The first dynamic argument is the PackageHeader `packageType`; the second is the PackageHeader `entries` array.
- Add `GROUP BY symbol` when one query processes multiple symbols.
- Filter out trade entries before reconstruction when the stream mixes trades with book updates.

Top-of-book snapshot:

```qql
WITH (orderBook{maxDepth: 1, model: 'L1'}(this."packageType", this."entries") as array(L1Entry)) AS 'book'
SELECT RUNNING
    "book"["side" == BID]."price"[0] AS 'bidPrice',
    "book"["side" == ASK]."price"[0] AS 'askPrice'
FROM "BINANCE"
WHERE symbol == 'BTC/USDT'
```

Multi-symbol L2 snapshots:

```qql
WITH orderBook{maxDepth: 10}(this."packageType", this."entries") AS 'book'
SELECT "book" AS 'entries', PERIODICAL_SNAPSHOT AS 'packageType'
TYPE "deltix.timebase.api.messages.universal.PackageHeader"
FROM "BITFINEX"
OVER TIME(10s)
WHERE notempty("book")
GROUP BY symbol
```

## Order Book Price/Volume Query Functions

These functions are stateless queries over a reconstructed `book` array. They do not use `{}`; the state comes from `orderBook{...}`.

| Function | Meaning | Empty/insufficient book behavior |
|---|---|---|
| `askPriceForVolume(book, volume)` | Ask price needed to execute the requested ask-side volume. | Returns `NaN` when there is not enough ask volume. |
| `bidPriceForVolume(book, volume)` | Bid price needed to execute the requested bid-side volume. | Returns `NaN` when there is not enough bid volume. |
| `averageAskPriceForVolume(book, volume)` | Weighted average ask price for the requested ask-side volume. | Returns `NaN` when there is not enough ask volume. |
| `averageBidPriceForVolume(book, volume)` | Weighted average bid price for the requested bid-side volume. | Returns `NaN` when there is not enough bid volume. |
| `askVolumeByPriceLevel(book, price)` | Total ask volume executable at the specified ask price level. | Returns `0` when no ask quotes match. |
| `bidVolumeByPriceLevel(book, price)` | Total bid volume executable at the specified bid price level. | Returns `0` when no bid quotes match. |
| `askVolumeAtPriceLevel(book, price)` | Ask volume at the closest ask level to the specified price. | Returns `0` when no ask quotes are available. |
| `bidVolumeAtPriceLevel(book, price)` | Bid volume at the closest bid level to the specified price. | Returns `0` when no bid quotes are available. |

Price required for a target volume:

```qql
WITH orderBook{maxDepth: 10}(this."packageType", this."entries") AS 'book'
SELECT RUNNING
    askPriceForVolume("book", 1) AS 'askPriceFor1',
    bidPriceForVolume("book", 0.2) AS 'bidPriceForPoint2'
FROM "BINANCE"
WHERE symbol == 'BTC/USD'
```

Average price for a target volume:

```qql
WITH orderBook{maxDepth: 10}(this."packageType", this."entries") AS 'book'
SELECT RUNNING
    averageAskPriceForVolume("book", 0.3) AS 'avgAskForPoint3',
    averageBidPriceForVolume("book", 1) AS 'avgBidFor1'
FROM "BINANCE"
WHERE symbol == 'BTC/USD'
```

Volume around price levels:

```qql
WITH orderBook{maxDepth: 10}(this."packageType", this."entries") AS 'book'
SELECT RUNNING
    askVolumeByPriceLevel("book", 22600) AS 'askVolumeBy22600',
    bidVolumeByPriceLevel("book", 22590) AS 'bidVolumeBy22590',
    askVolumeAtPriceLevel("book", 22600) AS 'askVolumeAt22600',
    bidVolumeAtPriceLevel("book", 22590) AS 'bidVolumeAt22590'
FROM "BINANCE"
WHERE symbol == 'BTC/USD'
```

Common interpretation:

- `PriceForVolume` returns the marginal price level needed to fill the target volume.
- `AveragePriceForVolume` returns the weighted average execution price for the target volume.
- `VolumeByPriceLevel` sums all volume executable exactly by that price threshold.
- `VolumeAtPriceLevel` returns volume at the closest level to the requested price.
- Negative volumes are not useful inputs; official behavior is not simply `NaN` and may return the first level price if the book has at least one level. Do not generate negative-volume calls unless the user explicitly asks to test edge behavior.

Sample book outcomes:

| Function call | Result meaning |
|---|---|
| `askPriceForVolume(book, 2.1)` | First ask price level where cumulative ask volume reaches `2.1`. |
| `bidPriceForVolume(book, 1.1)` | First bid price level where cumulative bid volume reaches `1.1`. |
| `averageAskPriceForVolume(book, 4.0)` | Weighted ask execution price for exactly `4.0` volume; the last level is truncated to the requested volume. |
| `averageBidPriceForVolume(book, 2.0)` | Weighted bid execution price for exactly `2.0` volume; the last level is truncated to the requested volume. |
| `askVolumeByPriceLevel(book, 102)` | Total ask volume executable up through price `102`. |
| `bidVolumeByPriceLevel(book, 99)` | Total bid volume executable down through price `99`. |
| `askVolumeAtPriceLevel(book, 102.5)` | Ask volume at the closest ask level to `102.5`. |
| `bidVolumeAtPriceLevel(book, 98.5)` | Bid volume at the closest bid level to `98.5`. |

## Common Pitfalls

- Using stateless call form by mistake (`avg(x)` instead of `avg{}(x)`).
- Putting message fields inside `{}` init args.
- Forgetting `GROUP BY symbol` for per-symbol isolated state.
- Combining `SELECT RUNNING` with `OVER OPEN TIME(...)`; open-time aggregation is not running mode.
- Treating parser success as semantic proof for field/class correctness.
- Assuming every documented stateful function is available on the connected server without checking via `list_qql_functions` (or the capability-discovery guidance in `references/concepts/stateless-functions.md` on older MCP servers) when availability is in doubt.

## See Also

- `references/functions-windows.md` for workflow and window behavior.
- `references/concepts/stateless-functions.md` for pure expression functions.
- `references/arrays-polymorphism.md` for PackageHeader workflows.
