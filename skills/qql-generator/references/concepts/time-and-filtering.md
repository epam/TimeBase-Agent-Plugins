# Time and Filtering

## Scope

- Time-bounded filtering (`today`, ranges, day windows).
- Nanosecond-resolution filtering with built-in `timestampNs`.
- Type filtering (`THIS IS ...`).
- Aggregate-result filtering with `HAVING`.
- Timezone-sensitive timestamp literal interpretation.

## Out of Scope

- Window function selection and emission semantics: `references/functions-windows.md`.
- General query clause-order repairs: `references/query-generation.md`.

## Retrieval Cues

timestamp literals, timezone, `BETWEEN ...'d`, `timestampNs`, nanosecond, `THIS IS`, `WHERE` vs `HAVING`, today boundaries.

## Required Inputs

- Stream name and timestamp field assumptions (`timestamp` for millisecond filtering, `timestampNs` for nanosecond filtering).
- Time boundary intent (for example: current day, last hour, fixed interval).
- Timezone expectation from user (or explicit assumption if missing).

## Step-by-Step Approach

1. Define time boundaries first (absolute or relative intent).
2. Apply message-level filters in `WHERE`.
3. If aggregating/grouping, apply aggregate-result filters in `HAVING`.
4. If timezone is not stated, assume GMT and say so in notes.

## Practical Rules

- Use date literals with `d` suffix for timestamp boundaries.
- Use built-in `timestampNs` when the user asks for nanosecond-resolution message-time filtering.
- `WHERE` runs before aggregation.
- `HAVING` runs after `SELECT`/aggregation and is the right place for aggregate aliases.
- Use `THIS IS "TypeName"` when filtering by message/object type.
- Direct `timestamp`/`timestampNs` comparisons at the top level of `WHERE` are **subscription hints** — the engine uses the time index to seek to the exact start position rather than scanning from the beginning of the stream. Wrapping the field in a function or placing it under `OR` with a non-timestamp predicate disables this optimization. See `references/concepts/subscription-hints.md`.

## Common Pitfalls

- Putting aggregate conditions in `WHERE` instead of `HAVING`.
- Omitting `d` suffix on timestamp literals.
- Using `timestamp` when the requested boundary requires nanosecond precision; use `timestampNs` instead.
- Treating timezone as implicit local time without stating assumptions.
- Mixing parser-valid and semantic-valid claims (always keep semantic caveat when unresolved).

## Minimal Examples

Time range:

```qql
SELECT "price", "size"
FROM "trades"
WHERE timestamp BETWEEN '2011-10-17 17:21:41'd AND '2011-10-17 17:21:42'd
```

Nanosecond time range:

```qql
SELECT "price", "size"
FROM "trades"
WHERE timestampNs BETWEEN '2024-10-17 17:21:41.000123456'd AND '2024-10-17 17:21:41.000223456'd
```

Type filter:

```qql
SELECT "price"
FROM "market"
WHERE THIS IS "TradeMessage"
```

Aggregate + HAVING:

```qql
SELECT symbol, count{}() AS 'c'
FROM "trades"
GROUP BY symbol
HAVING "c" > 1000
```

In this example, the HAVING clause is used to filter the results after the message count for each symbol has been calculated and grouped. 
This ensures that only the results meeting the specified condition (count being greater than 1,000) are included in the result.

"Today" template (timezone-sensitive):

```qql
SELECT count{}() AS 'minutesRate'
FROM "COINBASE"
OVER TIME(1m)
WHERE timestamp BETWEEN 'START_OF_DAY_UTC'd AND 'START_OF_NEXT_DAY_UTC'd
```

Timezone specified template:

```qql
SELECT count{}() AS 'minutesRate'
FROM "COINBASE"
OVER TIME(1m)
WHERE timestamp BETWEEN '2011-10-17 00:00:00 America/New_York'd AND '2011-10-18 00:00:00 America/New_York'd
```

## Fallback Behavior

If MCP is unavailable, keep boundaries explicit and assumption-labeled:

- ask user for timezone if "today" is ambiguous,
- provide a template with `START_OF_DAY_*` placeholders when timezone is unknown,
- include this warning in user-facing output:
  `Warning: TimeBase MCP is not available, so results are expected to be significantly worse than MCP-grounded output.`

## Also Requires

- `references/query-generation.md` for clause order and repair mappings.
- `references/concepts/constants-and-literals.md` for timestamp literal formats and timezone rules.
- `references/functions-windows.md` for window emission semantics.
- `references/concepts/operators-conditionals.md` for boolean composition and null handling.
- `references/concepts/subscription-hints.md` for timestamp subscription pushdown rules and non-optimizable pattern repairs.
