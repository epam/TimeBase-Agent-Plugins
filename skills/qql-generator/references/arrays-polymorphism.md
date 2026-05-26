# Arrays and Polymorphism

This file owns PackageHeader/polymorphic workflows. Generic array mechanics are owned by `references/concepts/arrays.md`.

## When to Use

Use this file when data shape includes:

- polymorphic message classes,
- PackageHeader `entries`,
- type-specific fields (`side`, `level`, `price`, `size`) requiring narrowing,
- polymorphic output modeling via `RECORD` or `UNION`.

## Required Inputs

- Stream key and schema classes from MCP or user-provided schema.
- PackageHeader field names (`packageType`, `entries`) if applicable.
- Concrete target entry types/classes to project.

## Step-by-Step Approach

1. Confirm classes and entry fields using schema (and sample messages when needed).
2. Narrow by type before projecting class-specific fields.
3. For PackageHeader workflows, choose:
   - direct `ARRAY JOIN` extraction,
   - `orderBook{...}` reconstruction,
   - polymorphic output with `RECORD` or `UNION`.
4. For query-state correctness across symbols, add `GROUP BY SYMBOL` when relevant.
5. Keep semantic caveat explicit if type names are assumptions.

## Type Narrowing Patterns

Cast + filter:

What: casts `entries` to trade-like elements and filters to matching type.
When: projecting trade-only fields from polymorphic package entries.
Why: narrowing first prevents ambiguous or invalid field access.

```qql
SELECT "entry"."exchangeId", "entry"."price", "entry"."size", "entry"."side" TYPE "Trade"
FROM "COINBASE"
ARRAY JOIN ("entries" AS array("TradeEntry")) AS "entry"
WHERE "entry" IS "TradeEntry"
```

Type-filtered array join:

What: unfolds only elements of selected class from the array.
When: you need a compact filter-first form without explicit array cast.
Why: filtering in `ARRAY JOIN` avoids carrying incompatible entry types downstream.

```qql
SELECT "entry"."price", "entry"."size"
FROM "COINBASE"
ARRAY JOIN ("entries"[THIS IS "TradeEntry"] as array("TradeEntry")) AS "entry"
```

Use fully qualified class names if unqualified names are rejected by schema/parser.

## PackageHeader Workflow Patterns

Top-of-book:

What: reconstructs best bid and ask from PackageHeader order-book updates.
When: stream provides incremental/snapshot book entries.
Why: `orderBook{maxDepth: 1}` normalizes mixed package updates to top-level quotes.

```qql
WITH (orderBook{maxDepth: 1}("packageType", "entries") as array("L2EntryNew")) AS 'book'
SELECT RUNNING
    "book"["side" == BID]."price"[0] AS 'bidPrice',
    "book"["side" == ASK]."price"[0] AS 'askPrice'
FROM "BINANCE"
WHERE symbol == 'BTC/USDT'
```

Add `GROUP BY symbol` when one query tracks order-book state for multiple symbols.

Flatten reconstructed book:

What: converts reconstructed order book into one row per level entry.
When: downstream analytics need row-wise level fields (`price`, `size`, `level`, `side`).
Why: `ARRAY JOIN` on reconstructed book enables level-wise filtering/grouping.

```qql
WITH (orderBook{maxDepth: 2}("packageType", "entries") as array("L2EntryNew")) AS 'book'
SELECT RUNNING
    "bookEntry"."exchangeId" AS 'exchangeId',
    "bookEntry"."price" AS 'price',
    "bookEntry"."size" AS 'size',
    "bookEntry"."level" AS 'level',
    "bookEntry"."side" AS 'side'
FROM "BINANCE"
ARRAY JOIN ("book" AS array("L2EntryNew")) AS "bookEntry"
```

## Polymorphic Output (`RECORD` / `UNION`)

Use `RECORD ... TYPE ... WHEN` when output shape depends on input type in one query.

Use `FIELD` inside each `RECORD` branch to name output fields. Do not use `AS` inside `RECORD` field lists.

```qql
-- This query returns a polymorphic dataset with fields of both classes TradeMessage and BestBidOfferMessage
WITH
    entry AS L1Entry AS l1
SELECT
RECORD
    entry.price FIELD "price",
    entry.size FIELD "size"
TYPE "TradeMessage"
WHEN entry IS KrakenTradeEntry
RECORD
    l1[side == ASK].price FIELD "offerPrice",
    l1[side == ASK].size FIELD "offerSize",
    l1[side == BID].price FIELD "bidPrice",
    l1[side == BID].size FIELD "bidSize"
TYPE "BestBidOfferMessage"
WHEN entry IS L1Entry
FROM kraken
ARRAY JOIN entries AS entry
```

Use `UNION` when composing outputs from separate SELECT branches:

What: combines type-specific projections into one polymorphic result stream.
When: different entry classes need distinct projection logic.
Why: `UNION` keeps each branch simple while preserving both output types.

```qql
SELECT "trade"."price" AS "price" TYPE "TradeView"
FROM "BINANCE"
ARRAY JOIN ("entries" as array("BinanceTradeEntry")) AS "trade"
UNION
SELECT "bbo"."bidPrice" AS "bidPrice", "bbo"."offerPrice" AS "offerPrice" TYPE "BboView"
FROM "BINANCE"
ARRAY JOIN ("entries" AS array("L1entry"))[THIS IS NOT NULL] AS "bbo"
```

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Reading type-specific fields before narrowing | Filter/cast to concrete type first. |
| Inventing class names | Use MCP/user schema exact type names. |
| Missing symbol partition in polymorphic query-state use-cases | Add `GROUP BY SYMBOL`. |
| Using `AS` inside `RECORD` | Use `FIELD 'name'` inside `RECORD` branches. |
| Reconstructing books for many symbols without grouping | Add `GROUP BY symbol` unless the input is already single-symbol. |

## Fallback Behavior

If MCP/schema is unavailable:

- request stream schema or sample messages,
- provide assumption-labeled templates with placeholder class names,
- include required MCP warning string in user-facing output.

## Also Requires

- `references/concepts/arrays.md` for slicing/indexing/masks and raw `ARRAY JOIN` mechanics.
- `references/concepts/casts.md` for cast syntax and ambiguity fixes.
- `references/concepts/stateful-functions.md` for `orderBook{}` and order-book price/volume query functions.
- `references/concepts/operators-conditionals.md` for comparison, logical, and conditional filtering.
- `references/mcp-workflow.md` for grounding and parser-vs-semantic policy.
