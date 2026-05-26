# Filters and Predicates

Use this file for `WHERE`, type filters, null/NaN checks, membership, pattern matching, and predicate repair.

## Scope

- Message-level filters in `WHERE`.
- Aggregate-result filters in `HAVING`.
- Type predicates (`THIS IS`, object `IS`, `IS NOT NULL`).
- `BETWEEN`, `IN`, `LIKE`, null, and NaN handling.

## Practical Rules

- `WHERE` filters source messages before aggregation.
- `HAVING` filters projected aggregate results after grouping/windowing.
- Use `==` / `!=` for equality and `===` / `!==` for strict equality.
- Use `BETWEEN low AND high` for inclusive ranges.
- Use `IN (...)` for exact membership lists.
- Use `LIKE` with `%` and `_` for `VARCHAR` patterns.
- Use `IS NULL` / `IS NOT NULL` for null checks.
- For polymorphic arrays, filter or cast by type before reading type-specific fields.
- Filtering clauses do not make ambiguous identifiers unambiguous; qualify or cast fields first.
- `symbol == 'X'` and positive `symbol IN (...)` at the top-level `AND` of `WHERE` are **subscription hints** — only the listed symbols are read from the stream. Negative conditions (`!=`, `NOT IN`) and `LIKE` on `symbol` do not trigger this optimization and run as runtime filters. See `references/concepts/subscription-hints.md`.

## Minimal Examples

Membership and pattern filters:

```qql
SELECT *
FROM "binance"
WHERE symbol IN ('BTCUSD', 'ETHUSD') OR symbol LIKE 'BTC%'
```

Type filter on current message:

```qql
SELECT "price", "size"
FROM "market"
WHERE THIS IS "deltix.timebase.api.messages.TradeMessage"
```

Type filter on joined entry:

```qql
SELECT "entry"."price", "entry"."size"
FROM "BINANCE"
ARRAY JOIN "entries" AS "entry"
WHERE "entry" IS "TradeEntry" AND "entry"."price" IS NOT NULL
```

Post-aggregate filter:

```qql
SELECT symbol, count{}() AS 'messageCount'
FROM "trades"
GROUP BY symbol
HAVING "messageCount" > 1000
```

## Common Repairs

| Bad pattern | Repair |
|---|---|
| `WHERE count{}() > 10` | Move aggregate condition to `HAVING`. |
| `symbol = 'AAPL'` | Use `symbol == 'AAPL'`. |
| `WHERE side == 'BID'` for enum field | Use `WHERE side == BID` or qualified enum. |
| `WHERE field != NULL` | Use `WHERE field IS NOT NULL`. |
| `entries.price > 10` used as scalar | Wrap with `ANY(...)` or filter array elements explicitly. |

## Also Requires

- `references/concepts/operators-conditionals.md` for boolean precedence, strict equality, and `.?`.
- `references/concepts/constants-and-literals.md` for literal syntax.
- `references/concepts/time-and-filtering.md` for time ranges and timezone assumptions.
- `references/concepts/casts.md` for ambiguity and type narrowing.
- `references/concepts/subscription-hints.md` for symbol and timestamp subscription pushdown rules and non-optimizable pattern repairs.