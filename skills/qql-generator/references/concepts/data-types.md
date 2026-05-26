# Data Types

## Scope

- Numeric precision and conversion concerns.
- Enum-vs-string comparisons.
- Timestamp precision/literal behavior.
- Array element type expectations.
- Nullability implications.

## Out of Scope

- Detailed cast syntax: `references/concepts/casts.md`.
- Operator semantics and conditional branching: `references/concepts/operators-conditionals.md`.

## Retrieval Cues

type mismatch, enum literal, `timestamp(ns)`, precision loss, nullable arithmetic.

## Required Inputs

- Field types from schema (`INT*`, `FLOAT*`, `DECIMAL`, `VARCHAR`, `ENUM`, `TIMESTAMP`, arrays, objects).
- Expected output type for derived expressions.
- Any conversion assumptions accepted by the user.

## Step-by-Step Approach

1. Inspect field types in schema before writing expressions.
2. Keep operands type-compatible (cast only when needed).
3. For enum fields, use enum values (optionally fully qualified enum type when ambiguous).
4. For timestamps, keep precision/literal formats explicit.
5. Re-check null behavior in predicates and derived expressions.

## Practical Rules

- Timestamp literals for filters use `d` suffix.
- `TIMESTAMP` and `TIMESTAMP(NS)` precision differences matter for mixed arithmetic/comparisons.
- For string-to-number or string-to-timestamp casts, treat parsing as conversion logic, not guaranteed success.
- Array operations are element-wise; ensure element type supports the operator.

## Common Pitfalls

- Comparing enum fields to free-form strings instead of enum values.
- Mixing numeric types without considering precision loss.
- Treating nullable values as non-null in arithmetic/conditions.
- Assuming parser success guarantees safe runtime conversion.

## Minimal Examples

Enum comparison:

```qql
SELECT *
FROM "securities"
WHERE type == "deltix.timebase.api.messages.InstrumentType":FX
```

Timestamp range:

```qql
SELECT *
FROM "trades"
WHERE timestamp BETWEEN '2026-05-14 00:00:00'd AND '2026-05-15 00:00:00'd
```

Primitive conversion:

```qql
SELECT '-12345' AS int32, '2016-10-27T16:36:08.993' AS timestamp(ms)
```

## Fallback Behavior

If type info is incomplete:

- ask user for schema field types,
- provide assumption-labeled templates with placeholders,
- avoid asserting semantic correctness from parser-only checks.

## Also Requires

- `references/concepts/casts.md` for explicit conversion patterns.
- `references/concepts/operators-conditionals.md` for type-sensitive expressions.
- `references/query-generation.md` for ambiguity and repair workflow.
