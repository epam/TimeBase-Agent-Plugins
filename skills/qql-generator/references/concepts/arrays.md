# Arrays

This file owns generic array mechanics. For PackageHeader/polymorphic workflows, use `references/arrays-polymorphism.md`.

## Scope

- Array projection/indexing/slicing/filtering.
- `ARRAY JOIN` / `LEFT ARRAY JOIN` mechanics.
- Array predicates (`ANY`, `ALL`) and boolean masks.

## Out of Scope

- PackageHeader and polymorphic-class workflows: `references/arrays-polymorphism.md`.
- Cast disambiguation for type narrowing: `references/concepts/casts.md`.

## Retrieval Cues

array slice, `ANY`, `ALL`, boolean mask, `position()`, `ARRAY JOIN`, `LEFT ARRAY JOIN`.

## Required Inputs

- Array field names and element shape from schema.
- Whether element-level output rows are required (`ARRAY JOIN`) or array-valued expressions are sufficient.

## Step-by-Step Approach

1. Decide row model:
   - keep arrays in-place, or
   - unfold elements with `ARRAY JOIN`.
2. Add element predicates (type/value/index) using array filters.
3. For polymorphic arrays with optional fields, prefer safe-access patterns and/or type narrowing.

## Practical Rules

- `ARRAY JOIN` comes after `FROM`, before `OVER`/`WHERE`/`GROUP BY`.
- `ARRAY JOIN` unfolds joined array elements into result messages.
- `LEFT ARRAY JOIN` returns not-joined elements as is, while joined elements are joined the regular way.
- `ANY`/`ALL` are useful when filtering by conditions on array-valued expressions.
- Slicing form is `[start:end:step]`.
- Use `position()` only inside array filters (`[...]`) to select elements by index-dependent conditions.
- Index arrays use double brackets, for example `entries[[2, 3]]`; boolean masks use the same shape, for example `entries[[true, false, true]]`.

## Common Pitfalls

- Putting `ARRAY JOIN` after `WHERE`.
- Expecting `ARRAY JOIN` to behave like `LEFT ARRAY JOIN`.
- Using boolean masks derived from missing fields without safe access in mixed-type arrays.
- Using `position()` outside an array filter.

## Minimal Examples

Array projection and predicate:

```qql
SELECT "entries"."price"
FROM "packages"
WHERE ANY("entries"."price" > 10)
```

Element unfold:

```qql
SELECT "entry"."price", "entry"."size"
FROM "packages"
ARRAY JOIN "entries" AS "entry"
WHERE "entry"."price" > 0
```

Preserve not-joined elements:

```qql
SELECT "entry"
FROM "packages"
LEFT ARRAY JOIN "entries" AS "entry"
```

Slicing:

- Entries array elements with indices from 1 to 5 with step=2:

```qql
SELECT "entries"[1:5:2] FROM "packages"
```

- All entries array elements in the reversed order:

```qql
SELECT entries[::-1] FROM "packages"
```

Position filter:

```qql
SELECT "entries"[position() > 3]."price"
FROM "packages"
```

Index-array selection:

```qql
SELECT "entries"[[2, 3]]
FROM "packages"
```

Boolean-mask selection:

```qql
SELECT "entries"["entries"."price" > 2000]
FROM "packages"
```

For polymorphic arrays where some elements do not have the masked field, use safe access from `references/concepts/operators-conditionals.md`:

```qql
SELECT entries[entries.?price > 2000]
FROM "packages"
```

## Fallback Behavior

If schema is incomplete:

- ask for element type/class names,
- output template queries with explicit assumptions about array element shape,
- avoid inventing concrete entry class names.

## Also Requires

- `references/concepts/casts.md` when converting polymorphic arrays to fixed element type.
- `references/concepts/operators-conditionals.md` for safe-access (`.?`) and boolean array behavior.
- `references/arrays-polymorphism.md` for PackageHeader and polymorphic entry workflows.
