# Query Generation

Use this file for building or repairing SELECT queries (including analytical queries).

## When to Use

- New SELECT query from a user goal.
- Query repair after parser diagnostics.
- Query review for clause order, aliasing, ambiguous fields, or filtering semantics.

## Required Inputs

- Stream name and relevant schema fields/classes.
- Desired output shape (raw projection, distinct, grouped, running/windowed, typed output).
- Constraints such as time bounds, symbols, type filters, and null behavior.
- Literal details such as timestamp timezone, enum qualification, numeric precision, and interval units.

## Step-by-Step Approach

1. Start from the minimal SELECT skeleton.
2. Add only required clauses in valid order.
3. Resolve ambiguity (field/type) before adding derived logic.
4. Add aggregation/windows/grouping only if required.
5. If available, run `compile_query` and repair parser errors.
6. If the problem is an unknown or unsupported function, inspect `stateless_functions()` and/or `stateful_functions()` on the connected server before rewriting the query.
7. Keep semantic caveat explicit unless schema evidence confirms fields/types.

## SELECT Skeleton

```qql
[WITH expr_list]
SELECT [DISTINCT|RUNNING]
    expr_list [TYPE "OutputType"]
[FROM "stream"|REVERSE("stream")|LIVE("stream")]
[[LEFT] ARRAY JOIN expr_list]
[[TRIGGER|RESET] OVER [EVERY] TIME(<interval>)|COUNT(<n>)]
[WHERE expr]
[GROUP BY expr_list]
[HAVING expr]
[LIMIT limit [OFFSET offset]]|[LIMIT offset, limit]
[UNION ...]
```

## Core Rules

- `DISTINCT` applies to the whole projected tuple.
- `WHERE` filters source messages; `HAVING` filters post-aggregation results.
- `GROUP BY SYMBOL` is required for per-symbol query-state separation in polymorphic-style projections.
- `OVER` belongs before `WHERE`.
- Stream order is timestamp order; do not add SQL `ORDER BY`.
- Use `LIMIT` for bounded preview size, not as a semantic filter.
- Use `FIELD` inside `RECORD` branches; use `AS 'alias'` for ordinary aliases.
- Use `SELECT first (*)` / `SELECT last (*)` for first/last whole messages; use `first{}(field)` / `last{}(field)` for stateful field aggregation.
- Avoid `GROUP BY timestamp` for time buckets; use `OVER TIME(1ms)` or a larger interval instead.
- Avoid filtering by result of stateful functions in `WHERE`, filter them in `HAVING` instead.

## High-Value Patterns

Nested object selection:

What: projects a value from an embedded object path.
When: use when schema has nested object fields.
Why: explicit path access avoids ambiguous top-level field references.

```qql
SELECT "order"."info"."size" AS 'size'
FROM "orders"
WHERE "order"."info"."size" > 0
```

Object expansion:

What: unfolds all fields of an object into separate columns.
When: use for inspection or when the user asks for the full nested object payload as columns.
Why: `object.*` preserves object field names without manually listing every field.

```qql
SELECT "order".*
FROM "orders"
```

First/last whole messages:

What: returns the first or last complete message from a source stream.
When: user asks for the first/last record, not an aggregate of a single field.
Why: `first (*)` / `last (*)` operate on the whole message; stateful `first{}(field)` / `last{}(field)` aggregate field values.

```qql
SELECT first (*)
FROM "trades"
```

```qql
SELECT last (*)
FROM "trades"
```

Alias (`AS 'name'`) vs cast (`AS Type`):

What: first query renames output column; second converts value type.
When: use alias for readability, cast for type conversion.
Why: `AS` is overloaded in QQL, so quoted alias avoids ambiguity.

```qql
SELECT symbol AS 'sym'
FROM "securities"
```

```qql
SELECT "rawTs" AS timestamp
FROM "events"
```

Ambiguous field disambiguation:

What: resolves a field that exists on multiple classes.
When: parser/runtime reports ambiguous identifier.
Why: explicit cast tells QQL which class field to read.

```qql
SELECT (this as "AlgoInstrumentConfig")."algoId" AS 'algoId'
FROM "configs"
WHERE (this as "AlgoInstrumentConfig")."algoId" == 14
```

Distinct tuple projection:

What: returns unique `(symbol, exchangeId)` pairs.
When: deduplicating multi-column projections.
Why: `DISTINCT` applies to the whole projected tuple, not a single field.

```qql
SELECT DISTINCT symbol, "exchangeId"
FROM "securities"
```

Unique symbol count in a stream:

What: applies the stateless `size` function to the result of the stateless `symbols` function for a stream.
When: user asks how many symbols are present in a stream.
Why: built-in `symbols` function returns an array of varchar symbols for a stream; built-in `size` function returns the length of an array.

```qql
-- 'stream' name here is string literal argument for stateless function
SELECT size(symbols('stream'))
```

Unique symbol count in a bounded range of a stream:

What: counts distinct `symbol` identities in a bounded range (how many symbols for which data exists in a bounded range of a stream).
When: user asks how many unique symbols are present in a bounded range of a stream.
Why: built-in `symbol` is the stream identity; filtering empty strings can change aggregate behavior and should not be added unless explicitly requested.

```qql
SELECT size(collect_unique{}(symbol)) AS 'uniqueSymbols'
FROM "stream"
WHERE timestamp BETWEEN '2025-11-07 00:00:00 GMT'd AND '2025-11-08 00:00:00 GMT'd
```

Aggregation + HAVING:

What: counts messages per symbol and keeps only high-volume groups.
When: filter condition depends on an aggregated value.
Why: `HAVING` is evaluated after grouping, unlike `WHERE`.

```qql
SELECT symbol, count{}() AS 'c'
FROM "trades"
GROUP BY symbol
HAVING "c" > 100000
```

Timestamp bucket repair:

What: aggregates by timestamp-level buckets without creating one group per unique timestamp.
When: user asks for per-timestamp or millisecond buckets.
Why: `GROUP BY timestamp` can create very many groups; `OVER TIME(1ms)` is the intended time-bucket form.

```qql
SELECT sum{}("size") AS 'size'
FROM "trades"
OVER TIME(1ms)
```

## Common Repairs

| Bad pattern | Repair |
|---|---|
| `SELECT price FROM quotes` | `SELECT "price" FROM "quotes"` |
| `symbol = 'AAPL'` | `symbol == 'AAPL'` |
| `AVG(x) OVER (PARTITION BY ...)` | `SELECT RUNNING avg{}(x) ... OVER TIME(...) GROUP BY ...` |
| `WHERE ... OVER TIME(...)` | Move `OVER TIME(...)` before `WHERE`. |
| Aggregate condition in `WHERE` | Move condition to `HAVING` after `GROUP BY`. |
| `ORDER BY timestamp` | Omit it; stream order is timestamp order. |
| `GROUP BY timestamp` for time buckets | Use `OVER TIME(1ms)` or the requested bucket interval. |
| Ambiguous identifier error | Type-qualify field or cast `this` to concrete type. |
| `IF x THEN y ELSE z` | Use `y IF x ELSE z` or `CASE WHEN x THEN y ELSE z END`. |
| SQL date literal syntax | Use QQL date literals like `'2026-05-14 00:00:00 GMT'd`. |
| Using timestamp format `'2006-01-05T00:00:00 America/New_York'd` | Use `'2006-01-05 00:00:00 America/New_York'd`. |
| Adding `symbol != ''` as filter | Omit it unless the user explicitly asks |
| Unknown or unsupported function | Query `stateless_functions()` and/or `stateful_functions()` on the connected server, then use a supported equivalent that preserves stateless vs stateful semantics. |

## Parse vs Semantic Validity

- Parser success is necessary, not sufficient.
- `compile_query` validates parser syntax only.
- Class/field/type correctness must be confirmed by schema evidence.
- MCP-specific validation/fallback policy is owned by `references/mcp-workflow.md`.

## Fallback Behavior

If schema is incomplete or MCP is unavailable:

- ask for missing class/field/type definitions,
- return assumption-labeled templates instead of false-final queries,

## Also Requires

- `references/concepts/time-and-filtering.md` for time literals, timezone, `WHERE`/`HAVING` boundaries.
- `references/concepts/constants-and-literals.md` for numbers, strings, chars, timestamps, intervals.
- `references/concepts/filters-and-predicates.md` for `BETWEEN`, `IN`, `LIKE`, null/NaN, and type predicates.
- `references/concepts/operators-conditionals.md` for complex expressions and null handling.
- `references/concepts/casts.md` for disambiguation and conversions.
- `references/concepts/keywords-and-shaping.md` for `WITH`, `TYPE`, `FIELD`, `RECORD`, `THIS`, `LIMIT/OFFSET`.
- `references/concepts/union.md` for SELECT UNION and stream UNION.
- `references/functions-windows.md` for stateful/stateless emission semantics.
- `references/arrays-polymorphism.md` when arrays or PackageHeader polymorphism are involved.
