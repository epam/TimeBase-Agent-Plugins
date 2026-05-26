# Casts

## Scope

- Disambiguating fields that exist in multiple message types.
- Narrowing polymorphic objects/arrays to concrete types.
- Primitive and array element conversions.

## Out of Scope

- General query skeleton and repair loop: `references/query-generation.md`.
- PackageHeader workflow recipes: `references/arrays-polymorphism.md`.

## Retrieval Cues

ambiguous identifier, `(this as Type).field`, alias-vs-cast ambiguity, `AS array(Type)`.

## Required Inputs

- Source type and target type names from schema.
- Whether cast is for object disambiguation, array narrowing, or primitive conversion.
- Validation constraints (parser check plus schema-level confirmation).

## Step-by-Step Approach

1. Confirm source/target types from schema evidence.
2. Apply cast in the smallest scope needed (field/object/array element).
3. Re-check dependent fields/operators for compatibility.
4. Run parser validation and keep semantic caveat if schema certainty is incomplete.

## Practical Rules

- `AS` is overloaded in QQL:
  - alias when the token after `AS` is used as column name (best practice: single-quoted alias),
  - cast when the token after `AS` matches an existing type/object.
- Use `AS 'alias'` to avoid alias-vs-cast ambiguity.
- Use type-qualified field access or explicit object cast for ambiguous identifiers.
- Cast arrays before `ARRAY JOIN` when element type must be fixed.
- Do not invent target class names; use exact schema classes.

## `AS` Disambiguation

Use this deterministic rule:

- `expression AS 'name'` -> alias
- `expression AS TypeName` -> cast when `TypeName` exists in schema/type system

Examples:

Alias:

```qql
SELECT symbol AS 'sym'
FROM "securities"
```

Object cast:

```qql
SELECT "entry" AS "deltix.timebase.api.messages.universal.L1Entry"
FROM "BINANCE"
ARRAY JOIN "entries" AS "entry"
```

Array cast:

```qql
SELECT "entries" AS array("TradeEntry")
FROM "BINANCE"
```

## Common Pitfalls

- Treating `AS` aliases as casts (or vice versa) without intent clarity.
- Using unquoted alias names that accidentally match a type name and become cast.
- Casting to a class that is not present in stream schema.
- Applying broad casts where narrow field qualification is sufficient.

## Minimal Examples

Disambiguate ambiguous field:

```qql
SELECT (this as "AlgoInstrumentConfig")."algoId" AS 'algoId'
FROM "configs"
WHERE (this as "AlgoInstrumentConfig")."algoId" == 14
```

Type-qualified field form (note that type-qualifying does not change the type — it only narrows field access to a concrete type):

```qql
SELECT "AlgoInstrumentConfig":"algoId" AS 'algoId'
FROM "configs"
```

Explicit alias:

```qql
SELECT (this as "AlgoInstrumentConfig")."algoId" AS 'algoId'
FROM "configs"
```

Cast array before join:

```qql
SELECT "entry"."price", "entry"."size"
FROM "BINANCE"
ARRAY JOIN ("entries" AS array("deltix.timebase.api.messages.universal.L1Entry")) AS "entry"
```

Primitive conversion pattern:

```qql
SELECT 1000 AS timestamp, '-12345345' AS int32
```

## Fallback Behavior

If target type cannot be verified:

- provide an assumption-labeled template with placeholder type names,
- ask user for exact class/type names or stream schema output,
- avoid declaring semantic validity as proven.

## Also Requires

- `references/query-generation.md` for alias vs cast placement and ambiguous-field repairs.
- `references/concepts/arrays.md` for array-cast and join mechanics.
- `references/arrays-polymorphism.md` for polymorphic narrowing workflows.
