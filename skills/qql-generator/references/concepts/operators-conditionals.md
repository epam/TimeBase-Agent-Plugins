# Operators and Conditionals

## Scope

- Arithmetic/comparison/logical operators.
- Bitwise operators on integers and flag enums.
- `IN` and `LIKE` predicate operators.
- Null-aware conditions.
- Conditional branching (`CASE WHEN`, `IF ... ELSE`).
- `.?` array-mask alignment in polymorphic arrays.

## Out of Scope

- Cast semantics and type conversion: `references/concepts/casts.md`.
- Window emission semantics: `references/functions-windows.md`.

## Retrieval Cues

`CASE WHEN`, `IF`, boolean precedence, bitwise mask, `IS NULL`, `.?`, array-mask mismatch.

## Required Inputs

- Operand types (scalar vs array, numeric vs enum/string, integer vs non-integer).
- Desired output type and null behavior.
- Whether condition is row-level (`WHERE`) or aggregate-level (`HAVING`).

## Step-by-Step Approach

1. Confirm operand types from schema.
2. Build expression with explicit null/type handling.
3. If expression feeds stateful aggregates, ensure category predicates are applied correctly.
4. Validate parser syntax and keep semantic caveat when schema certainty is incomplete.

## Practical Rules

- Use `==` / `!=` for equality/inequality and `===` / `!==` for strict comparisons.
- Use `AND` / `OR` / `NOT` with clear grouping when conditions are complex.
- Use `&`, `|`, `^`, `~`, `<<`, and `>>` only with integer operands; enums are supported except for `~`.
- Always wrap bitwise sub-expressions in parentheses to make precedence explicit (e.g. `(((~a) & b) | c)` rather than `~a & b | c`).
- Use `CASE WHEN` for 3+ branches or mixed predicate categories.
- Use ternary `value IF condition ELSE fallback` for compact two-way value selection.
- Use `IN (...)` for exact membership and `LIKE` for string templates.
- Use `.?` when boolean masks are derived from polymorphic array fields that may be absent on some elements.
- `entries.field` can produce a shorter derived array (missing-field elements omitted), while `entries.?field` preserves positional alignment by returning `NULL` for missing-field elements.

## Common Pitfalls

- Boolean precedence confusion in long expressions without grouping.
- Applying bitwise operators to non-integer operands.
- Omitting parentheses around bitwise sub-expressions, causing unexpected precedence with comparison operators (e.g. `mode & 4 != 0` is parsed as `mode & (4 != 0)` — write `(mode & 4) != 0` instead).
- Comparing incompatible types without explicit cast.
- Building mask arrays from `entries.field` in polymorphic arrays and getting positional misalignment.
- Putting aggregate conditions in `WHERE` instead of `HAVING`.

## Minimal Examples

Conditional aggregate inputs:

```qql
SELECT RUNNING
    avg{}(CASE WHEN "side" == BUY THEN "price" END) AS 'avgBuyPrice',
    avg{}(CASE WHEN "side" == SELL THEN "price" END) AS 'avgSellPrice'
FROM "trades"
OVER TIME(1m)
GROUP BY symbol
```

Null-aware conditional:

```qql
SELECT CASE WHEN "price" IS NULL THEN 0 ELSE "price" END AS 'safePrice'
FROM "quotes"
```

Compact ternary:

```qql
SELECT "size" IF "side" == BUY ELSE 0 AS 'buySize'
FROM "trades"
```

Bitwise operations:

```qql
SELECT * FROM stream WHERE (mode & 4) != 0
```

```qql
SELECT symbol, price FROM stream
WHERE (EnrichedTradeMessage:"flags" & MARKET_CLOSE_PRICE) != 0
```

Membership and pattern matching:

```qql
SELECT *
FROM "binance"
WHERE symbol IN ('BTCUSD', 'ETHUSD') OR symbol LIKE 'BTC%'
```

Polymorphic mask alignment with `.?`:

```qql
SELECT entries[entries.?price > 15]
FROM "packages"
```

## Fallback Behavior

If operator/type compatibility is uncertain:

- ask for field types,
- provide an assumption-labeled expression template,
- avoid claiming semantic correctness from parser success alone.

## Also Requires

- `references/concepts/casts.md` for explicit type conversions.
- `references/concepts/filters-and-predicates.md` for `WHERE`, `HAVING`, null/NaN, `IN`, and `LIKE` usage.
- `references/concepts/time-and-filtering.md` for `WHERE` vs `HAVING` boundaries.
- `references/functions-windows.md` for conditionals feeding stateful functions.
