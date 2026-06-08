# Functions and Windows

Use this file to choose the right function model and window behavior for a query goal.

## Scope

- Stateful vs stateless decision.
- Windowing and emission behavior (`RUNNING`, `TRIGGER`, `RESET`, `OVER TIME`, `OVER COUNT`, `EVERY`).
- Practical aggregation patterns for symbol/category analytics.
- Per-category aggregate conditioning and result cadence selection.

## Out of Scope

- Full per-function argument catalog details: see `references/concepts/stateful-functions.md` and `references/concepts/stateless-functions.md`.
- Polymorphic entry extraction details: see `references/arrays-polymorphism.md`.

## Retrieval Cues

running metrics, moving average, OHLCV, VWAP, periodic snapshots, group by symbol, count windows, trigger/reset.

## Required Inputs

- metric intent (count, average, extrema, bands, order-book, distribution),
- cadence intent (per message, per window close, periodic snapshots),
- grouping keys (`symbol`, category),
- window type (`OVER TIME(...)` or `OVER COUNT(...)`),
- interval boundary intent (`OPEN`, `CLOSE`, offset, empty intervals) when the user cares about bucket timestamps.

## Choose the Right Function Model

- Use **stateless** functions for per-message expressions only.
- Use **stateful** functions for cumulative/windowed calculations across messages.
- For function availability checks on the connected server, see `references/concepts/stateless-functions.md`.

Stateless example (per message):

```qql
SELECT size("entries"), max("bidPrice", "offerPrice")
FROM "quotes"
```

Stateful example (across messages):

```qql
SELECT RUNNING avg{}("price") AS 'avgPrice'
FROM "trades"
OVER TIME(1m)
```

## Window and Emission Behavior

- Plain `SELECT` + stateful function: emit on window close (or end of stream if no window).
- `SELECT RUNNING`: emit on every input message.
- `TRIGGER OVER ...`: periodic snapshots of cumulative state.
- `RESET OVER ...`: state resets each period.
- `OVER TIME(...)`: time windows.
- `OVER OPEN TIME(...)`: intervals that report the bucket open timestamp.
- `OVER CLOSE TIME(...)`: intervals that report the bucket close timestamp; this is the default form.
- `OVER TIME(interval, offset)`: shifted time windows, for example daily buckets starting at 15:00 UTC.
- `OVER COUNT(...)`: message-count windows.
- `EVERY`: include empty-period snapshots where supported.

Examples:

```qql
SELECT max{}("price")
FROM "quotes"
TRIGGER OVER COUNT(500)
```

```qql
SELECT RUNNING max{}("price")
FROM "quotes"
RESET OVER TIME(30m)
```

## Common Patterns

Per-category aggregates in one row:

What: computes separate aggregates for categories in one output row.
When: user asks for per-side/per-status metrics without one row per category.
Why: each stateful function receives only the rows for its category.

```qql
SELECT RUNNING
    sum{}(CASE WHEN "side" == BID THEN "size" ELSE 0 END) AS 'bidSize',
    sum{}(CASE WHEN "side" == ASK THEN "size" ELSE 0 END) AS 'askSize'
FROM "quotes"
```

Daily buckets with offset:

```qql
SELECT sum{}("tradeQuantity") AS 'quantity'
FROM "orders"
OVER TIME(1d, 15h)
WHERE symbol == 'BTCUSD'
GROUP BY symbol
```

Per-symbol running spread:

```qql
SELECT RUNNING avg{}("offerPrice" - "bidPrice") AS 'avgSpread'
FROM "quotes"
OVER TIME(1h)
WHERE "bidPrice" > 0 AND "offerPrice" > 0
GROUP BY symbol
```

One-minute OHLCV from trade entries:

```qql
WITH "entries"[THIS IS "deltix.timebase.api.messages.universal.TradeEntry"] AS 'trades'
SELECT
    sum{}(sum("trades"."size")) AS 'volume',
    first{}("trades"[0]."price") AS 'open',
    last{}("trades"[-1]."price") AS 'close',
    max{}(max("trades"."price")) AS 'high',
    min{}(min("trades"."price")) AS 'low'
FROM "bitfinex"
OVER TIME(1m)
WHERE symbol == 'BTCUSD' AND size("trades") > 0
```

## Complete Coverage Pointers

Stateful catalog (full families with examples):

- Core aggregates: `count`, `sum`, `avg`, `min`, `max`, `first`, `last`
- Moving averages: `sma`, `ema`, `cma`, `kama`, `lsma`, `mma`
- Indicators: `bollinger`, `atr`, `adxr`
- Helpers: `collect_unique`, `lastNotNull`, `window`, `statWindow`, `timeOfMin`, `timeOfMax`, `histogram`
- Domain-specific: `orderBook`

See `references/concepts/stateful-functions.md`.

Stateless catalog (full groups with examples):

- Numeric, String, Timestamp, Array, Order Book query, and Introspection functions.

See `references/concepts/stateless-functions.md`.

## Common Pitfalls

- Using stateless syntax where stateful is required (`avg(x)` vs `avg{}(x)`).
- Putting message fields inside `{}` init args.
- Missing `GROUP BY symbol` for isolated per-symbol state.
- Using `GROUP BY "side"` when the desired output is one row with separate side columns; condition aggregate inputs instead.
- Expecting `TRIGGER` to reset state without explicit `RESET`.
- Expecting `OVER TIME` output exactly at wall-clock boundaries when no source message arrives.
- Combining `SELECT RUNNING` with `OVER OPEN TIME(...)`; use close/default time windows for running output.
- Assuming a documented function is available on the connected server without checking the capability-discovery guidance in `references/concepts/stateless-functions.md` when availability is in doubt.

## See Also

- `references/query-generation.md`
- `references/concepts/operators-conditionals.md`
- `references/concepts/time-and-filtering.md`
- `references/arrays-polymorphism.md`
