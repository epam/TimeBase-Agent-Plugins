# Stateless Functions Catalog

Stateless functions are pure per-message expressions and do not keep running state. They do not use `{}`.

## Numeric Functions

Use for scalar math:

- `max(x, y)`, `min(x, y)`
- `abs(x)`, `sqrt(x)`, `log(x)`, `exp(x)`
- `floor(x)`, `ceil(x)`

Example:

```qql
SELECT abs("price" - 100), max("price", "bidPrice" - "offerPrice")
FROM "quotes"
```

## String Functions

Use for text normalization and parsing:

- `length(s)`
- `uppercase(s)`, `lowercase(s)`
- `reverse(s)`
- `indexof(haystack, needle)`
- `substr(s, start, end)`
- `toTimestamp(string[, format])`
- `toTimestampNs(string[, format])`

Example:

```qql
SELECT uppercase(symbol) AS 'symUpper', substr(symbol, 0, 3) AS 'prefix'
FROM "securities"
```

Timestamp parsing:

```qql
SELECT toTimestamp('2022-08-27 22:32:02.123', 'yyyy-MM-dd HH:mm:ss.SSS') AS 'eventTime'
```

## Timestamp Functions

Use for extracting or formatting timestamp components:

- `year(timestamp)`, `month(timestamp)`, `day(timestamp)`
- `hour(timestamp)`, `minute(timestamp)`, `second(timestamp)`
- `millisecond(timestamp)`, `nanosecond(timestamp)`
- `dayOfWeek(timestamp)`
- `truncateToDay(timestamp)`
- `formatTimestamp(timestamp, format)`

Example:

```qql
SELECT
    year(timestamp) AS 'year',
    month(timestamp) AS 'month',
    day(timestamp) AS 'day',
    formatTimestamp(timestamp, 'yyyy-MM-dd HH:mm:ss.SSS') AS 'formatted'
FROM "events"
```

## Array Functions

Use for per-message array analytics:

- `empty(arr)`, `notempty(arr)`, `size(arr)`
- `max(arr)`, `min(arr)`, `mean(arr)`, `sum(arr)`
- `enumerate(arr)`, `sort(arr)`, `indexof(arr, el)`
- `any(boolArr)`, `all(boolArr)`

Example:

```qql
SELECT size("entries"), any("entries"."price" > 200), sort("entries"."price")
FROM "bookStream"
```

## Order Book Query Functions

Use these stateless helpers on a reconstructed `orderBook{}` result. They do not use `{}` themselves.

- `askPriceForVolume(book, volume)`, `bidPriceForVolume(book, volume)`
- `averageAskPriceForVolume(book, volume)`, `averageBidPriceForVolume(book, volume)`
- `askVolumeByPriceLevel(book, price)`, `bidVolumeByPriceLevel(book, price)`
- `askVolumeAtPriceLevel(book, price)`, `bidVolumeAtPriceLevel(book, price)`

See `references/concepts/stateful-functions.md` for complete behavior and examples.

## Introspection Functions

Use for metadata discovery and debugging:

- `now()`
- `currentTimeMs()`
- `streams()`
- `symbols(streamKey)`
- `spaces(streamKey)`
- `typeOf(expr)`
- `stateless_functions()`
- `stateful_functions()`

Example:

```qql
SELECT s.key
ARRAY JOIN streams() AS s
```

```qql
SELECT typeOf("entry") AS 'entryType', count{}() AS 'count'
FROM "KRAKEN"
ARRAY JOIN "entries" AS "entry"
GROUP BY typeOf("entry")
```

## Composition Patterns

Stateless functions can nest:

```qql
SELECT sqrt(abs("price" - 100)) AS 'score'
FROM "quotes"
```

Use in predicates:

```qql
SELECT *
FROM "quotes"
WHERE abs("offerPrice" - "bidPrice") > 0.5
```

## Common Pitfalls

- Using `{}` with stateless functions.
- Expecting stateless array `sum(arr)` to accumulate over time (it is per message only).
- Confusing array functions (`size`) with string functions (`length`).

## See Also

- `references/functions-windows.md` for stateful/windowed processing.
- `references/concepts/stateful-functions.md` for aggregate and indicator catalogs.
- `references/concepts/operators-conditionals.md` for expression semantics.
