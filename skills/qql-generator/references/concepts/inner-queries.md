# Inner Queries

## Scope

- `SELECT ... FROM (SELECT ...)` staged query patterns.
- Post-aggregation filters and staged transformations.
- Readability/performance improvements via pre-reduction.

## Out of Scope

- Core SELECT clause repairs: `references/query-generation.md`.
- Detailed window-function behavior: `references/functions-windows.md`.

## Retrieval Cues

subquery in `FROM`, staged aggregation, post-aggregation filtering, distinct-then-count pattern.

## Required Inputs

- Outer query objective and final output shape.
- Inner stage purpose (aggregation, deduplication, filtering, projection cleanup).
- Performance and correctness constraints (especially around aggregation boundaries).

## Step-by-Step Approach

1. Define inner query as a self-contained stage producing needed fields.
2. Define outer query consuming only inner outputs.
3. Keep stage responsibilities narrow (one transformation concern per stage).
4. Validate parser syntax, then verify semantic intent per stage.

## Practical Rules

- Inner query lives in `FROM (...)`.
- Outer stage can filter/aggregate on inner computed fields.
- This is often the clean way to apply a filter that should happen after aggregation.

## Common Pitfalls

- Using inner queries where simple single-stage query is sufficient.
- Mixing pre-aggregation and post-aggregation conditions in one stage.
- Forgetting to alias/retain fields needed by outer stage.

## Minimal Examples

Post-aggregation filter pattern:

```qql
SELECT *
FROM (
    SELECT symbol, min{}("price") AS 'min'
    FROM "trades"
    OVER TIME(1m)
    GROUP BY symbol
)
WHERE "min" > 27020
```

Count distinct symbols through staged query:

```qql
SELECT count{}()
FROM (
    SELECT DISTINCT symbol
    FROM "securities"
)
```

Two-stage windowing:

```qql
SELECT avg{}("m")
FROM (
    SELECT max{}("price") AS 'm'
    FROM "trades"
    OVER TIME(1m)
)
OVER TIME(1h)
```

## Fallback Behavior

If stage semantics are uncertain:

- provide a two-stage template with explicit assumptions,
- ask user whether filtering must happen before or after aggregation.

## Also Requires

- `references/query-generation.md` for clause-order and repair rules.
- `references/concepts/time-and-filtering.md` for `WHERE` vs `HAVING`.
- `references/functions-windows.md` for nested aggregation/window behavior.
