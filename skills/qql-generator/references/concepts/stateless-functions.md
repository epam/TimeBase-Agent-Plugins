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
- `stateless_functions()` returns the stateless QQL functions supported by the connected TimeBase server.
- `stateful_functions()` returns the stateful QQL functions supported by the connected TimeBase server.

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

## Function Discovery Workflow

Use connected-server discovery as the first capability check when:

- the user asks which QQL functions are available on the connected server,
- a query repair flow hits an unknown or unsupported function error,
- static docs and observed server behavior may differ across versions or editions.

### 1. Prefer `list_qql_functions` (TimeBase MCP v0.2.0+)

Check out the `references/mcp-workflow.md` file for the details.

### 2. Fallback for older MCP servers

If `list_qql_functions` is not available, query the connected server with QQL introspection functions:

- `stateless_functions()`: stateless catalog.
- `stateful_functions()`: stateful catalog.

The output of these functions is long, so try to narrow down the results via QQL filtering capabilities.

Full server function capability discovery example:

```qql
SELECT f.id, f.arguments.name, f.arguments.dataType.baseName
ARRAY JOIN stateless_functions() AS f
```

### Guidance

- Prefer the connected server's reported catalog over static references for availability questions.
- Verify whether the missing function belongs to the stateless or stateful family before suggesting a replacement.
- If a function is unavailable, propose a supported equivalent and note any semantic change.

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
- Assuming every documented function exists on every connected server without checking via `list_qql_functions` (or `stateless_functions()` / `stateful_functions()` on older MCP servers).

## See Also

- `references/functions-windows.md` for stateful/windowed processing.
- `references/concepts/stateful-functions.md` for aggregate and indicator catalogs.
- `references/concepts/operators-conditionals.md` for expression semantics.
