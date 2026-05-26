# QQL Recipes

Use these as compact end-to-end patterns. Adjust class names and fields to actual schema evidence.

## How to Use Recipes

1. Pick the closest pattern.
2. Verify stream/class/field names against MCP schema or user-provided schema.
3. If MCP is unavailable, keep assumptions explicit and include required warning.
4. Use related references for deeper guidance; this file is intentionally concise.

## Extract Trades From PackageHeader

What: extracts trade-shaped entries from polymorphic package payload.
When: stream carries mixed entry types and you need trade-only fields.
Why: type narrowing avoids ambiguous `side` and invalid field access.

```qql
SELECT
    "entry"."exchangeId" AS 'exchangeId',
    "entry"."price" AS 'price',
    "entry"."size" AS 'size',
    "entry"."side" AS 'side' TYPE "Trade"
FROM "COINBASE"
ARRAY JOIN ("entries" AS array("TradeEntry")) AS "entry"
WHERE "entry" IS "TradeEntry"
```

See details: `references/arrays-polymorphism.md`

## Forward-Fill Bid/Ask and Spread

What: reconstructs two-sided spread from one-sided updates.
When: feed emits partial L1 updates.
Why: `lastNotNull{}` carries forward the latest known side values.

```qql
SELECT RUNNING
    lastNotNull{}("entry"["side" == ASK]."price") AS 'askPrice',
    lastNotNull{}("entry"["side" == BID]."price") AS 'bidPrice',
    "askPrice" - "bidPrice" AS 'spread'
FROM "BINANCE"
ARRAY JOIN ("entries" AS array("L1Entry")) AS "entry"
WHERE "entry" != null AND symbol == 'BTC/USDT'
```

See details: `references/functions-windows.md`, `references/arrays-polymorphism.md`

## Top Of Book From PackageHeader

What: derives best bid/ask from package entries.
When: using universal market-data style PackageHeader streams.
Why: `orderBook{maxDepth: 1}` normalizes incremental and snapshot updates.

```qql
WITH (orderBook{maxDepth: 1}("packageType", "entries") as array("L2EntryNew")) AS 'book'
SELECT RUNNING
    "book"["side" == BID]."price"[0] AS 'bidPrice',
    "book"["side" == ASK]."price"[0] AS 'askPrice'
FROM "BINANCE"
WHERE symbol == 'BTC/USDT'
```

Use MCP schema/messages to confirm `packageType`, `entries`, `side`, `price`, and symbol format before finalizing.

See details: `references/arrays-polymorphism.md`

## Order Book Price For Volume

What: estimates the price and average price needed to execute target size from a reconstructed book.
When: impact/slippage checks on PackageHeader order-book streams.
Why: `orderBook{}` builds state; `askPriceForVolume` and related functions query that state.

```qql
WITH orderBook{maxDepth: 10}(this."packageType", this."entries") AS 'book'
SELECT RUNNING
    askPriceForVolume("book", 1) AS 'askPriceFor1',
    averageAskPriceForVolume("book", 1) AS 'avgAskPriceFor1',
    bidPriceForVolume("book", 1) AS 'bidPriceFor1',
    averageBidPriceForVolume("book", 1) AS 'avgBidPriceFor1'
FROM "BINANCE"
WHERE symbol == 'BTC/USDT'
```

See details: `references/concepts/stateful-functions.md`

## Order Book Volume At Price

What: reports available book volume around specified price levels.
When: checking liquidity at or by a target price.
Why: volume query functions distinguish exact threshold volume from closest-level volume.

```qql
WITH orderBook{maxDepth: 10}(this."packageType", this."entries") AS 'book'
SELECT RUNNING
    askVolumeByPriceLevel("book", 22600) AS 'askVolumeBy22600',
    bidVolumeByPriceLevel("book", 22590) AS 'bidVolumeBy22590',
    askVolumeAtPriceLevel("book", 22600) AS 'askVolumeAt22600',
    bidVolumeAtPriceLevel("book", 22590) AS 'bidVolumeAt22590'
FROM "BINANCE"
WHERE symbol == 'BTC/USDT'
```

See details: `references/concepts/stateful-functions.md`

## Count Messages By Day

What: counts messages per one-day window.
When: daily volume/activity summary.
Why: `OVER TIME(1d)` buckets stream messages into day windows.

```qql
SELECT count{}()
FROM "BINANCE"
OVER TIME(1d)
```

## First And Last Complete Messages

What: returns boundary messages from a stream.
When: inspecting the first or last complete record, not aggregating one field.
Why: `first(*)` / `last(*)` operate on the whole message.

```qql
SELECT first(*)
FROM "CHANNEL_0"
```

```qql
SELECT last(*)
FROM "CHANNEL_0"
```

## Message Rates At Multiple Intervals

What: returns two rate views (per second and per minute).
When: comparing high-frequency and medium-frequency message throughput.
Why: `UNION` combines two independently windowed aggregates.

```qql
SELECT count{}() AS 'secondsRate'
FROM "COINBASE"
OVER TIME(1s)
UNION
SELECT count{}() AS 'minutesRate'
FROM "COINBASE"
OVER TIME(1m)
```

## Millisecond Buckets Instead Of GROUP BY Timestamp

What: aggregates at timestamp-like granularity without creating one group per distinct timestamp.
When: users ask for per-timestamp counts or sums.
Why: `GROUP BY timestamp` can create a very large number of groups; `OVER TIME(1ms)` is the intended bucket form.

```qql
SELECT count{}() AS 'messageCount'
FROM "CHANNEL_0"
OVER TIME(1ms)
WHERE timestamp BETWEEN '2025-11-07 10:00:00 GMT'd AND '2025-11-07 10:01:00 GMT'd
```

## Minute-By-Minute Rate For Today

What: computes minute buckets for current day range.
When: intraday throughput monitoring.
Why: explicit day bounds avoid accidental cross-day aggregation.

```qql
SELECT count{}() AS 'minutesRate'
FROM "COINBASE"
OVER TIME(1m)
WHERE timestamp BETWEEN 'START_OF_DAY_UTC'd AND 'START_OF_NEXT_DAY_UTC'd
```

Notes:

- Replace placeholders with actual day boundaries in the user's timezone intent.
- If timezone is not specified, state assumption explicitly.

See details: `references/concepts/time-and-filtering.md`

## Nanosecond Time Filter

What: filters by nanosecond-resolution message timestamp.
When: user gives nanosecond boundaries or asks for `timestampNs` precision.
Why: built-in `timestamp` is millisecond resolution; `timestampNs` supports nanosecond comparisons.

```qql
SELECT count{}() AS 'messageCount'
FROM "CHANNEL_0"
WHERE timestampNs BETWEEN '2025-11-07 10:00:00.000000000 GMT'd AND '2025-11-07 10:00:00.000001000 GMT'd
```

See details: `references/concepts/time-and-filtering.md`

## Position-Based Array Filter

What: selects array elements by element index position.
When: level or entry selection depends on index, not only value.
Why: `position()` is valid inside array filters and evaluates the element index.

```qql
SELECT "entries"[position() > 3]."price" AS 'pricesAfterLevel3'
FROM "BINANCE"
WHERE symbol == 'BTC/USDT'
```

See details: `references/concepts/arrays.md`

## Running One-Hour Average Spread Per Symbol

What: tracks rolling spread average per symbol.
When: multi-symbol quote quality monitoring.
Why: `GROUP BY symbol` isolates state by instrument.

```qql
SELECT RUNNING avg{}("offerPrice" - "bidPrice") AS 'avgSpread'
FROM "quotes"
OVER TIME(1h)
WHERE "bidPrice" > 0 AND "offerPrice" > 0
GROUP BY symbol
```

## Unique Symbol Count in an Entire Stream

What: applies the stateless `size` function to the result of the stateless `symbols` function for a stream (specified as name as string literal).
When: user asks how many symbols are present in a stream.
Why: built-in `symbols` function returns an array of varchar symbols for a stream; built-in `size` function returns the length of an array.

```qql
SELECT size(symbols('stream'))
```

## Unique Symbol Count

What: counts distinct symbols observed in stream.
When: inventory breadth checks and stream sanity validation.
Why: `collect_unique{}` + `size(...)` counts distinct built-in stream symbols without changing aggregate cardinality.

```qql
SELECT size(collect_unique{}(symbol)) AS 'uniqueSymbols'
FROM "stream"
WHERE timestamp BETWEEN '2025-11-07 00:00:00 GMT'd AND '2025-11-08 00:00:00 GMT'd
```

Do not add `symbol != ''` unless the user explicitly asks to exclude empty symbols or schema/sample evidence proves empty symbols are invalid for the task.

## Latency Percentiles With Histogram

What: estimates latency median and tail percentiles.
When: incident analysis, ingest lag, execution timing, and service latency distributions.
Why: `histogram{}` returns approximate quantiles efficiently for large streams.

```qql
WITH ("TradeMessage":"receiveTime" - "TradeMessage":"entryTime") AS 'latencyNs'
SELECT
    histogram{q: [0.5, 0.99], significantDigits: 3, min: 1, max: 10000000000}("latencyNs") AS 'latencyPercentilesNs'
FROM "stream"
OVER TIME(1m)
WHERE THIS IS "TradeMessage"
    AND timestamp BETWEEN '2025-11-07 10:00:00 GMT'd AND '2025-11-07 11:00:00 GMT'd
```

See details: `references/concepts/stateful-functions.md`

## Previous Value Difference

What: computes per-message delta from prior sample.
When: momentum/change detection on numeric fields.
Why: `window{period: 2}` provides current and previous values in one expression.

```qql
WITH window{period: 2}("volume") AS 'w'
SELECT RUNNING "w"[1] - "w"[0] AS 'volumeDelta'
FROM "bars"
WHERE symbol == 'AAPL'
```

## Windowed Standard Deviation

What: computes rolling standard deviation from stat window.
When: short-term volatility monitoring.
Why: `statWindow{...}` exposes statistics object fields directly.

```qql
SELECT RUNNING statWindow{timePeriod: 60s}("volume")."standardDeviation"
FROM "bars"
WHERE symbol == 'AAPL'
```

## Add Nullable Field

What: incrementally extends schema with optional attribute.
When: backward-compatible schema enhancement.
Why: `ALTER STREAM` is safer than full `MODIFY STREAM` for additive changes.

```qql
ALTER STREAM "trades" (
    ALTER CLASS "Trade" (
        ADD FIELD "venue" VARCHAR
    )
)
```

## Minimal Polymorphic Stream DDL

What: creates a base class plus derived event classes.
When: starting a polymorphic event stream from scratch.
Why: `UNDER` models inheritance and shared base fields.

```qql
CREATE DURABLE STREAM "market" (
    CLASS "BaseEvent" (
        "source" VARCHAR
    ) NOT INSTANTIABLE;
    CLASS "Trade" UNDER "BaseEvent" (
        "price" FLOAT DECIMAL64,
        "size" FLOAT DECIMAL64
    );
    CLASS "Quote" UNDER "BaseEvent" (
        "bidPrice" FLOAT DECIMAL64,
        "offerPrice" FLOAT DECIMAL64
    )
)
COMMENT 'Market event stream'
```

See details: `references/ddl-generation.md`

## Repair: OVER After WHERE

Use canonical repair table in `references/query-generation.md`.
