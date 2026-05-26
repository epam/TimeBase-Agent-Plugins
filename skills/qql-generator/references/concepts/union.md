# UNION

Use this file when combining query results or reading multiple streams as one source.

## Scope

- SELECT `UNION` between full query branches.
- Fixed-type vs polymorphic output behavior.
- Stream union in `FROM (...)`.
- Result-shape compatibility and timestamp ordering.

## Practical Rules

- `UNION` combines branch results chronologically by timestamp.
- Branches may project different fields and `TYPE` names, producing polymorphic output.
- Branches with the same `TYPE` produce one fixed output type with compatible columns merged.
- Identical field names across branches must have compatible data types.
- Keep each branch independently valid; do not rely on aliases from another branch.
- For stream union, use parentheses: `FROM ("streamA" UNION "streamB")`.
- Classes with the same name across stream-union inputs must be binary-compatible.

## SELECT UNION Example

```qql
SELECT "trade"."exchangeId" AS 'exchangeId', "trade"."price" AS 'price', "trade"."size" AS 'size' TYPE "TradeView"
FROM "KRAKEN"
ARRAY JOIN "entries"[THIS IS "KrakenTradeEntry"] AS "trade"
UNION
SELECT
    ("quote"."exchangeId" IF "quote"."side" == BID) AS 'bidExchangeId',
    ("quote"."price" IF "quote"."side" == BID) AS 'bidPrice',
    ("quote"."size" IF "quote"."side" == BID) AS 'bidSize',
    ("quote"."exchangeId" IF "quote"."side" == ASK) AS 'offerExchangeId',
    ("quote"."price" IF "quote"."side" == ASK) AS 'offerPrice',
    ("quote"."size" IF "quote"."side" == ASK) AS 'offerSize'
TYPE "QuoteView"
FROM "KRAKEN"
ARRAY JOIN ("entries" AS array("L1Entry"))[THIS IS NOT NULL] AS "quote"
```

## Stream UNION Example

```qql
WITH "entries"[THIS IS "TradeEntry"] AS 'trades'
SELECT sum{}(sum("trades"."size")) AS 'volume'
FROM ("BINANCE" UNION "KRAKEN")
OVER TIME(1m)
WHERE symbol == 'BTC/USDT' AND notempty("trades")
GROUP BY symbol
```

## Common Pitfalls

- Expecting `UNION` to concatenate by branch order; QQL arranges results by timestamp.
- Reusing a branch alias outside the branch where it was declared.
- Combining same-named fields with incompatible types.
- Forgetting parentheses around stream union in `FROM`.

## Also Requires

- `references/query-generation.md` for clause order.
- `references/arrays-polymorphism.md` for polymorphic entry projections.
- `references/concepts/keywords-and-shaping.md` for `TYPE` and `FIELD` result shaping.