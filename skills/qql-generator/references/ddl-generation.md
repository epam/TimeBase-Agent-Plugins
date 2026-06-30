# DDL Generation Reference

Use this for `CREATE`, `ALTER`, `MODIFY`, and `DROP STREAM`.

## When to Use

- creating new streams/classes/enums,
- incremental schema evolution,
- full schema replacement,
- destructive cleanup/deletion workflows.

## Required Inputs

- target stream key and desired persistence (`DURABLE` / `TRANSIENT`),
- class/enum definitions and inheritance relations,
- migration risk tolerance and confirm mode approvals,
- explicit user intent for destructive actions.

## Operation Choice (Canonical)

| User intent | Prefer | Why |
|---|---|---|
| New stream | `CREATE DURABLE STREAM` or `CREATE TRANSIENT STREAM` | Defines schema and options from scratch. |
| Add/rename/alter one field or class element | `ALTER STREAM` | Incremental change, lower blast radius. |
| Rebuild many classes/enums/options | `MODIFY STREAM` | Full replacement is explicit and controlled. |
| Remove stream/data | `DROP STREAM` | Destructive; requires explicit intent. |
| Continuous server-side query persisting results | `CREATE VIEW` | Materialized view runs QQL on the server. |
| Pause/resume/rebuild a running view | `ALTER VIEW` | Lifecycle management without schema changes. |
| Remove a view | `DROP VIEW` | Destructive; requires explicit intent. |

## CREATE STREAM Workflow

1. Define classes/enums and inheritance using `UNDER`.
2. Keep identity fields implicit (`timestamp`, `symbol`, `type` are built-in).
3. Use DDL type grammar, including encodings where precision matters.
4. Add `OPTIONS` only when requested.
5. Add stream/comment metadata as needed.

What: creates a new durable polymorphic stream schema.
When: introducing a new stream with base and derived event classes.
Why: `UNDER` encodes inheritance and keeps model explicit for downstream queries.

```qql
CREATE DURABLE STREAM TEST (
    CLASS "deltix.timebase.api.messages.MarketMessage" 'Market Message' (
        "currencyCode" 'Currency Code' INTEGER SIGNED (16) COMMENT 'Currency code represented as short',
        "originalTimestamp" 'Original Timestamp' TIMESTAMP COMMENT 'Exchange Time is measured in milliseconds that passed since January 1, 1970 UTC',
        "sequenceNumber" 'Sequence Number' INTEGER COMMENT 'Market specific identifier of the given event in a sequence of market events',
        "sourceId" 'Source Id' VARCHAR ALPHANUMERIC (10) COMMENT 'Identifies market data source'
    ) AUXILIARY;

    CLASS "deltix.timebase.api.messages.BestBidOfferMessage" 'Quote Message' UNDER "deltix.timebase.api.messages.MarketMessage" (
        "offerPrice" 'Offer Price' FLOAT DECIMAL (2),
        "offerSize" 'Offer Size' FLOAT DECIMAL (0),
        "bidPrice" 'Bid Price' FLOAT DECIMAL (2) RELATIVE TO "offerPrice",
        "bidSize" 'Bid Size' FLOAT DECIMAL (0)
    );
    CLASS "deltix.timebase.api.messages.TradeMessage" 'Trade Message' UNDER "deltix.timebase.api.messages.MarketMessage" (
        "price" 'Trade Price' FLOAT DECIMAL (2),
        "size" 'Trade Size' FLOAT DECIMAL (0)
    );
)
```

Rules:

- Use `CREATE STREAM`, not SQL `CREATE TABLE`.
- Use `UNDER` for inheritance.
- Put stream `COMMENT` after the class/enum block.
- Separate multiple class/enum blocks with semicolons.
- Omit `OPTIONS` unless the user asks for storage/distribution behavior.
- Do not declare `timestamp`, `symbol`, or `type`.
- Fields are nullable unless `NOT NULL` is specified. Do not add `NOT NULL` unless producers guarantee values.
- For prices and sizes, prefer `FLOAT DECIMAL` or `FLOAT DECIMAL64` unless approximate binary floats are intentional.
- Use `INTEGER SIGNED (8|16|32|64)` for DDL integer storage width.
- Use `VARCHAR ALPHANUMERIC (n)` for fixed-width exchange/source codes.

## Class and Field Syntax

```qql
CLASS type_name [title] [UNDER type_name]
(static_attribute|attribute [, ...])
[AUXILIARY|NOT AUXILIARY]
[INSTANTIABLE|NOT INSTANTIABLE]
[COMMENT 'comment text']

ENUM enum_name [title]
(identifier [= expr] [, ...])
[FLAGS]
[COMMENT 'comment text']

STATIC identifier [title] type [NOT NULL] [encoding] [BETWEEN min_expr AND max_expr] = expr
[TAGS (identifier:expr [, ...])]
[COMMENT 'comment text']

identifier [title] type [NOT NULL] [encoding] [BETWEEN min_expr AND max_expr] [RELATIVE TO identifier] [DEFAULT expr]
[TAGS (identifier:expr [, ...])]
[COMMENT 'comment text']
```

Use `NOT INSTANTIABLE` for abstract bases and `AUXILIARY` for types that should not be written as top-level stream messages.
Use `FLAGS` for bitmask-style enums, `RELATIVE TO` when field decoding depends on another field, and `TAGS (...)` for field metadata.

Practical DDL type examples:

| Intent | Prefer |
|---|---|
| 32-bit signed integer | `INTEGER SIGNED (32)` |
| 64-bit signed integer | `INTEGER SIGNED (64)` |
| Decimal market price/size | `FLOAT DECIMAL64` or `FLOAT DECIMAL (<scale>)` |
| Fixed-width code | `VARCHAR ALPHANUMERIC (<n>)` |
| Millisecond timestamp field | `TIMESTAMP` |
| Nanosecond timestamp encoding | `TIMESTAMP NANOSECOND` |


## ALTER STREAM Workflow

`ALTER STREAM` performs incremental schema changes. Field-level operations must be nested inside `ALTER CLASS`.

Add nullable field:

What: adds one new optional field to an existing class.
When: backward-compatible schema extension.
Why: `ALTER STREAM` minimizes blast radius versus full schema replacement.

```qql
ALTER STREAM "trades" (
    ALTER CLASS "Trade" (
        ADD FIELD "venue" VARCHAR
    )
)
```

Alter nullability with a default:

What: tightens field nullability while preserving existing rows through default value.
When: moving a field from optional to required.
Why: default prevents invalid historical records after constraint change.

```qql
ALTER STREAM "trades" (
    ALTER CLASS "Trade" (
        ALTER FIELD "venue" SET NOT NULL DEFAULT 'UNKNOWN'
    )
)
```

Alter encoding with explicit conversion intent:

```qql
ALTER STREAM "trades" (
    ALTER CLASS "Trade" (
        ALTER FIELD "originalTimestamp" SET ENCODING NANOSECOND
    )
)
CONFIRM CONVERT_DATA
```

Drop a field only when explicitly requested and approved:

What: removes an existing attribute from class schema.
When: field is truly deprecated and user approved destructive change.
Why: `CONFIRM DROP_ATTRIBUTES` makes data-loss intent explicit.

```qql
ALTER STREAM "trades" (
    ALTER CLASS "Trade" (
        DROP FIELD "legacyVenue"
    )
)
CONFIRM DROP_ATTRIBUTES
```

Class/enum-level changes:

| Intent | Pattern |
|---|---|
| Add new class or enum | `ALTER STREAM "s" (ADD CLASS ...; ADD ENUM ...)` |
| Replace one class/enum definition | `ALTER STREAM "s" (REWRITE CLASS ...; REWRITE ENUM ...)` |
| Remove class or enum | `ALTER STREAM "s" (DROP CLASS "Old"; DROP ENUM "OldEnum") CONFIRM DROP_TYPES` |
| Change stream options only | `ALTER STREAM "s" SET PERIODICITY '1D', SET OWNER 'admin'` |

Official `ALTER ENUM` syntax:

```qql
ALTER ENUM enum_name (
    ALTER identifier SET VALUE [=] expr |
    ALTER identifier1 SET NAME [=] identifier2 |
    RENAME identifier1 TO identifier2 |
    ADD identifier = expr |
    DROP identifier |
    REWRITE identifier = expr
    [; ...]
)
```

Official `ALTER ENUM` example:

```qql
ALTER STREAM KRAKEN 
    ALTER ENUM "deltix.timebase.api.messages.service.DataConnectorStatus"
            ADD "DESCONNECTED_BY_VENDOR" = 11
CONFIRM CONVERT_DATA
```

Official `ADD ENUM` plus class update example:

```qql
ALTER STREAM KRAKEN (
    ADD ENUM "deltix.timebase.api.messages.service.ResetReason" (
        "UNKNOWN" = 0,
        "DISCONNECTED" = 1
    );
    ALTER CLASS "deltix.timebase.api.messages.universal.BookResetEntry" (
        ADD FIELD "reason" "deltix.timebase.api.messages.service.ResetReason"
    );
)
```

Official `ADD|REWRITE ENUM` syntax:

```qql
ADD|REWRITE ENUM enum_name [title]
(identifier [= expr] [, ...])
[FLAGS]
[COMMENT 'comment text']
```

Option-only changes use repeated `SET option value` clauses, not `SET OPTIONS (...)`:

```qql
ALTER STREAM "bars"
    SET PERIODICITY '1D',
    SET OWNER 'admin',
    SET DESCRIPTION '1 day bars'
```

## MODIFY STREAM Workflow

`MODIFY STREAM` replaces the entire schema. All retained classes, enums, fields, options, and comments must be restated.

Use it for broad, coordinated schema replacements, not small additive changes.

What: restates full stream schema in one replacement statement.
When: major refactor across multiple classes/options.
Why: `MODIFY STREAM` drops anything not restated, so complete declaration is required.

```qql
MODIFY STREAM "market" (
    CLASS "BaseEvent" (
        "source" VARCHAR
    ) NOT INSTANTIABLE;
    CLASS "Trade" UNDER "BaseEvent" (
        "price" FLOAT DECIMAL64,
        "size" FLOAT DECIMAL64,
        "venue" VARCHAR
    );
    CLASS "Quote" UNDER "BaseEvent" (
        "bidPrice" FLOAT DECIMAL64,
        "offerPrice" FLOAT DECIMAL64
    )
)
COMMENT 'Updated market schema'
```

Confirm modes:

- `NO_CONVERSION`: fail if conversion is needed.
- `CONVERT_DATA`: allow conversions.
- `DROP_ATTRIBUTES`: permit field removal.
- `DROP_TYPES`: permit type removal.
- `DROP_DATA`: allow dropping incompatible data.

Do not add confirm modes speculatively. Explain the risk when they are needed.

## DROP STREAM Workflow

What: deletes stream definition and stored data.
When: explicit cleanup/decommission request.
Why: operation is irreversible, so it must never be generated implicitly.

```qql
DROP STREAM IF EXISTS "oldStream"
```

Dropping a stream permanently removes stream data. Only generate it when the user explicitly asks for deletion or cleanup.

## Common Pitfalls

- Using `MODIFY STREAM` for small additive changes better handled by `ALTER STREAM`.
- Forgetting to restate retained schema elements in `MODIFY STREAM`.
- Generating destructive confirm modes without clear user approval.
- Declaring built-in identity fields in class definitions.
- Replacing official DDL type grammar with query cast names when declaring schema.
- Dropping titles, comments, tags, static fields, or encodings during `MODIFY STREAM`.

## DDL Self-Check

- No identity fields declared.
- No SQL table grammar.
- Inheritance uses `UNDER`, not `EXTENDS`.
- Small changes use `ALTER STREAM`, not `MODIFY STREAM`.
- `MODIFY STREAM` restates complete schema.
- DDL types, encodings, `STATIC`, `BETWEEN`, `RELATIVE TO`, tags, and comments are preserved when relevant.
- Destructive operations are clearly identified.

## Fallback Behavior

If schema details or migration policy are incomplete:

- provide a non-destructive template first,
- ask for confirm mode preferences and data-conversion tolerance,
- avoid generating destructive forms as defaults.

## Also Requires

- `references/mcp-workflow.md` for execution safety and parser-vs-semantic caveats.
- `references/concepts/data-types.md` when field conversions and precision changes are involved.
- `references/concepts/materialized-views.md` for `CREATE/ALTER/DROP VIEW` syntax, OPTIONS, and lifecycle commands.
