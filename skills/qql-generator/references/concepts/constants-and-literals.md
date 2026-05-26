# Constants and Literals

Use this file when a query needs exact literal syntax, timestamp boundaries, enum constants, interval windows, or primitive casts.

## Scope

- Numeric constants and array constants.
- Timestamp/date literals with timezone assumptions.
- String, char, boolean, enum, and interval literals.
- Literal/cast choices that affect generated query semantics.

## Practical Rules

- Integer constants without suffix compile as `INT32`; use `L` for `INT64`.
- Decimal constants without `f` compile as `DECIMAL64`; use `f` for `FLOAT64`.
- Time intervals use compact units such as `1h`, `5m30s`, `1d10h20m42s500ms` and compile as duration values.
- Timestamp literals use the QQL suffix form: `'2026-05-14 00:00:00 GMT'd`.
- When a timezone name is present in a date literal, use a space between date and time, not `T`: `'2026-05-15 00:00:00 America/New_York'd`.
- Omitted timestamp components default reasonably; omitted timezone defaults to GMT. State the timezone assumption when the user did not specify it.
- String literals use single quotes; escape single quotes as `\'`.
- Char literals use a trailing `c`, for example `'A'c`.
- Enum literals can be unqualified (`"BID"`) when unambiguous or qualified (`"pkg.EnumType":"VALUE"`) when needed.

## Minimal Examples

Timestamp range:

```qql
SELECT "price"
FROM "trades"
WHERE timestamp BETWEEN '2026-05-14 00:00:00 GMT'd AND '2026-05-15 00:00:00 GMT'd
```

Timezone-named day boundary:

```qql
SELECT count{}()
FROM "events"
WHERE timestamp BETWEEN '2026-05-15 00:00:00 America/New_York'd AND '2026-05-16 00:00:00 America/New_York'd
```

Numeric precision:

```qql
SELECT 123 AS 'int32Value', 123L AS 'int64Value', 12.5 AS 'decimalValue', 12.5f AS 'float64Value'
```

Enum qualification:

```qql
SELECT *
FROM "securities"
WHERE type == "deltix.timebase.api.messages.InstrumentType":FX
```

Interval windowing:

```qql
SELECT count{}() AS 'messageCount'
FROM "events"
OVER TIME(5m)
WHERE timestamp >= now() - 1h
```

## Common Pitfalls

- Writing SQL date literals such as `DATE '2026-05-14'` instead of QQL `'...'d`.
- Writing timezone-named literals as `'2026-05-15T00:00:00 America/New_York'd`; use `'2026-05-15 00:00:00 America/New_York'd`.
- Using string values for enum fields when enum constants are required.
- Forgetting `L` when a value must remain `INT64`.
- Assuming local timezone for partial date literals without saying so.
- Mixing decimal and binary float constants accidentally.

## Also Requires

- `references/concepts/data-types.md` for conversion and precision rules.
- `references/concepts/time-and-filtering.md` for timestamp filtering workflows.
- `references/concepts/filters-and-predicates.md` for predicates using literals.