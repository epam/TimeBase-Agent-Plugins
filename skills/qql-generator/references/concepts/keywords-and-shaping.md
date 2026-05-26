# Keywords and Result Shaping

## Scope

- `WITH` for reusable expressions.
- `TYPE` for result type shaping.
- `FIELD` and `RECORD` for output field naming and polymorphic result shaping.
- `THIS` for current-message/object reference.
- `LIMIT`/`OFFSET` for bounded result windows.

## Out of Scope

- Alias-vs-cast disambiguation details: `references/concepts/casts.md`.
- Filtering/window semantics: `references/concepts/time-and-filtering.md` and `references/functions-windows.md`.

## Retrieval Cues

`WITH`, `TYPE`, `FIELD`, `RECORD`, `THIS`, pagination, `LIMIT OFFSET`, output shaping.

## Required Inputs

- Query objective and expected output shape.
- Whether reusable expressions are needed (`WITH`).
- Whether typed output is required (`TYPE`).
- Whether `RECORD` branches or repeated output field names require `FIELD`.
- Whether pagination/bounded result is needed (`LIMIT`/`OFFSET`).

## Step-by-Step Approach

1. Build core query first.
2. Add `WITH` aliases for repeated expressions.
3. Add `TYPE` only when output type mapping is intentional.
4. Use `FIELD` inside `RECORD` branches.
5. Use `THIS` when explicit current-object reference improves clarity.
6. Apply `LIMIT`/`OFFSET` for bounded output only, not as a semantic filter.

## Practical Rules

- `WITH` can define aliases and reusable expressions consumed by later clauses.
- `TYPE` sets output type/class mapping for query results.
- `FIELD` assigns output names inside `RECORD` branches.
- `AS 'alias'` creates an ordinary alias; unlike `FIELD`, aliases must be unique in the expression scope.
- `RECORD ... TYPE ... WHEN ...` creates conditional polymorphic output in one query.
- `THIS IS TypeName` is type-check syntax in polymorphic contexts.
- `LIMIT n OFFSET m` and `LIMIT m, n` are valid forms.
- `OFFSET` still implies server-side read of skipped records.

## Minimal Examples

`WITH` reusable expressions:

```qql
WITH "offerPrice" - "bidPrice" AS 'spread'
SELECT "spread"
FROM "quotes"
WHERE "spread" > 0
```

`TYPE` mapping:

```qql
SELECT
    bbo[side == ASK].price AS "offerPrice",
    bbo[side == ASK].size AS "offerSize",
    bbo[side == BID].price AS "bidPrice",
    bbo[side == BID].size AS "bidSize"
TYPE "deltix.timebase.api.messages.BestBidOfferMessage"
FROM binance
ARRAY JOIN (entries AS array(L1Entry)) AS bbo
```

`RECORD` with `FIELD`:

```qql
SELECT
    RECORD "entry"."price" FIELD 'price', "entry"."size" FIELD 'size'
    TYPE "TradeView"
    WHEN "entry" IS "TradeEntry"
    RECORD "entry"."exchangeId" FIELD 'exchangeId'
    TYPE "StatusView"
    WHEN "entry" IS "StatusEntry"
FROM "BINANCE"
ARRAY JOIN "entries" AS "entry"
```

`THIS` usage:

```qql
SELECT THIS
FROM "binance"
WHERE THIS IS "deltix.timebase.api.messages.TradeMessage"
```

Use `this` when an alias in the same query shares a name with a source field you still need to reference from the input message.

```qql
WITH 
  orderBook{maxDepth: 10}(this."packageType", this."entries") AS 'book'
SELECT 
  "book" AS 'entries', PERIODICAL_SNAPSHOT AS 'packageType'
TYPE "deltix.timebase.api.messages.universal.PackageHeader"
FROM "BITFINEX"
OVER TIME(10s)
WHERE notempty("book")
GROUP BY symbol
```

`LIMIT`/`OFFSET`:

```qql
SELECT "price", "size"
FROM "trades"
LIMIT 100 OFFSET 200
```

## Common Pitfalls

- Overusing `TYPE` when output typing is not needed.
- Using `AS` instead of `FIELD` inside `RECORD` branches.
- Confusing `THIS` object reference with field names.
- Assuming `OFFSET` is computationally free for deep pages.
- Putting result-shaping constructs before core correctness.

## Fallback Behavior

If typed output or schema is uncertain:

- default to untyped projection with clear assumptions,
- ask whether pagination is functional requirement or just preview convenience.

## Also Requires

- `references/query-generation.md` for full clause-order skeleton.
- `references/concepts/casts.md` when `AS` may be confused between alias and cast.
- `references/concepts/index.md` for intent-triggered module loading.
