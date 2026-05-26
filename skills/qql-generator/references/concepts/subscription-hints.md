# Subscription Hints (Query Optimization)

When a QQL query filters on `timestamp`/`timestampNs` and/or `symbol`, the engine can convert those `WHERE` conditions into **subscription parameters** — instead of evaluating them as a per-message runtime filter, TimeBase uses the internal time index to seek directly to the requested start position and reads only the requested symbols.

This is the single most impactful performance lever in QQL. Always prefer patterns that allow pushdown when the user queries large streams.

## Scope

- Which `WHERE` patterns produce a subscription hint for time and/or symbol.
- Which patterns block the optimization (and why).
- How to rewrite non-optimizable conditions into optimizable equivalents.

## Out of Scope

- General predicate syntax: `references/concepts/filters-and-predicates.md`.
- Timestamp literal formats and timezone rules: `references/concepts/constants-and-literals.md`, `references/concepts/time-and-filtering.md`.

## Retrieval Cues

subscription hint, pushdown, time index, symbol subscription, performance, large stream, scan, slow query, timestamp filter optimization, symbol filter optimization.

---

## Timestamp Optimization

The engine extracts a start/end time bound from `WHERE` when the condition directly compares `timestamp` (or `timestampNs`) with a date literal or query parameter using a relational operator.

**Supported operators:** `<`, `>`, `<=`, `>=`, `BETWEEN ... AND ...`

```qql
-- Pushdown: engine seeks to the first message > this timestamp
SELECT * FROM "trades"
WHERE timestamp > '2024-01-01'd

-- Pushdown: engine reads only messages in [start, end]
SELECT * FROM "trades"
WHERE timestamp BETWEEN '2024-01-01'd AND '2024-02-01'd

-- Pushdown: nanosecond resolution (TimeBase 5.6.67+)
SELECT * FROM "BINANCE"
WHERE timestampNs > '2024-10-17 17:21:41.000123456'd
```

**Rules:**
- `timestamp` / `timestampNs` must appear **bare** on one side of the operator (the other side must be a literal or parameter).
- The condition must be at the **top level** of the `WHERE` clause — directly AND-ed, not nested inside `OR` or a sub-expression.
- Left or right position of the field does not matter.

---

## Symbol Optimization

The engine extracts a symbol subscription set from `WHERE` when the condition uses direct equality or positive membership on the built-in `symbol` field.

**Supported patterns:**
- `symbol == 'X'` — subscribes to exactly one symbol.
- `symbol IN ('A', 'B', ...)` — subscribes to all listed symbols.
- `symbol == 'A' OR symbol == 'B'` — multiple `OR`-ed equality conditions are **merged** into a single subscription (union of symbols).

```qql
-- Pushdown: single symbol
SELECT * FROM "trades"
WHERE symbol == 'XBANK'

-- Pushdown: explicit list
SELECT * FROM "trades"
WHERE symbol IN ('XBANK', 'GREATCO')

-- Pushdown: OR-ed equalities are merged into one subscription
SELECT * FROM "trades"
WHERE symbol == 'XBANK' OR symbol == 'GREATCO'
```

**Rules:**
- Only **positive** membership is supported. Negative conditions (`!=`, `NOT IN`) are evaluated as runtime filters.
- `LIKE` on `symbol` cannot be enumerated into a concrete subscription set and is always a runtime filter.
- The condition must be at the **top level** of the `WHERE` clause or `OR`-ed with other **symbol-only** equality conditions.

---

## Combining Time and Symbol

Both optimizations work simultaneously when joined with top-level `AND`:

```qql
SELECT * FROM "trades"
WHERE timestamp >= '2024-01-01'd
  AND symbol IN ('AAA', 'BBB')
```

The engine subscribes to `AAA` and `BBB` starting from `2024-01-01`. Any additional `AND`-ed predicates that cannot be mapped to a subscription (for example, `price > 100`) remain as runtime filters and **do not prevent** the time/symbol parts from being optimized.

---

## When Optimization Does NOT Apply

| Pattern | Reason | Optimizable rewrite |
|---|---|---|
| `WHERE upper(symbol) == 'AAA'` | Field wrapped in a function | `WHERE symbol == 'AAA'` |
| `WHERE timestamp + 1000 > '2024-01-01'd` | Arithmetic on `timestamp` | `WHERE timestamp > '2024-01-01'd` |
| `WHERE symbol == 'AAA' OR price > 100` | `OR` with a non-subscription predicate | `WHERE symbol == 'AAA' AND price > 100` (if intent allows) |
| `WHERE symbol != 'AAA'` | Negative symbol condition | Not directly rewritable; no subscription hint is possible |
| `WHERE symbol NOT IN ('AAA', 'BBB')` | Negative membership | Not directly rewritable |
| `WHERE symbol LIKE 'BTC%'` | Pattern match cannot enumerate symbols | Provide an explicit list if known: `symbol IN ('BTCUSD', 'BTCEUR')` |
| Deeply nested / complex logical expression | Engine cannot statically decompose | Flatten to top-level `AND` |

In all these cases the predicate still **works correctly** — it runs as a per-message runtime filter instead of a subscription hint.

---

## Best Practices

- Write `timestamp` and `symbol` filter conditions as **directly** and **simply** as possible — bare field, relational operator, constant or parameter.
- Combine time and symbol conditions with **top-level `AND`**, not wrapped in `OR` blocks.
- **Parameterized queries** — query parameters are also recognized as subscription hints; prefer them over hardcoded literals in reusable queries.
- **Never wrap** `timestamp` or `symbol` in functions, casts, or arithmetic — even `CAST(symbol AS VARCHAR)` blocks the optimization.
- Place subscription-eligible conditions **first** in the `WHERE` clause for readability, though clause order does not affect whether the hint is extracted.
- When the user queries a large stream without time/symbol bounds, suggest adding explicit bounds and explain the performance benefit.

---

## Also Requires

- `references/concepts/time-and-filtering.md` — timestamp literal syntax, timezone rules, `BETWEEN` semantics.
- `references/concepts/filters-and-predicates.md` — general `WHERE`/`HAVING`, `IN`, `LIKE`, null handling.
- `references/concepts/constants-and-literals.md` — date literal format, timezone specifiers, parameterized literals.
