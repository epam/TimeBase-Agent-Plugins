# Materialized Views

Materialized Views execute a QQL query continuously on the TimeBase server and persist or stream the results. Supported since TimeBase 5.6.191.

## CREATE VIEW

```
CREATE [OR REPLACE] VIEW [IF NOT EXISTS] view_name (qql-expression)
[OPTIONS (identifier [= expr] [; ...])]
```

Full example 1-minute OHLC bars from a trades stream, running live:

```qql
CREATE VIEW "bars-view" (
    SELECT
        min{}("price") AS "low",
        max{}("price") AS "high",
        first{}("price") AS "open",
        last{}("price") AS "close"
    FROM "trades"
    OVER TIME(1m)
    GROUP BY "symbol"
) OPTIONS(LIVE)
```

### OPTIONS

| Option | Type | Purpose |
|---|---|---|
| `LIVE` | Boolean | Run in live mode (consume new data as it arrives). |
| `AUTO_RESTART` | Boolean | Automatically restart the view when the TimeBase server starts. |
| `OUTPUT_TYPE` | String (`STREAM`/`TOPIC`) | Destination type for view output. |

Multiple options are separated by `;` inside `OPTIONS(...)`.

## DROP VIEW

```qql
DROP VIEW IF EXISTS "bars-view"
```

Destructive. Only generate when the user explicitly requests deletion.

## ALTER VIEW

```qql
ALTER VIEW "bars-view" PAUSE;
ALTER VIEW "bars-view" RESUME;
ALTER VIEW "bars-view" REBUILD;
```

| Command | Effect |
|---|---|
| `PAUSE` | Stops reading source data, view transitions to idle state. |
| `RESUME` | Resumes a paused view. |
| `REBUILD` | Restarts and reprocesses data from the beginning of the source stream. |

## Rules and Pitfalls

- The inner QQL expression is a standard `SELECT` query; all style and safety rules from `query-generation.md` apply inside it.
- Use `CREATE OR REPLACE VIEW` when updating an existing view definition in one atomic step (avoids a separate DROP).
- `IF NOT EXISTS` suppresses the error when the view already exists, do not combine with `OR REPLACE`.
- Options use `;` as separator inside `OPTIONS(...)`, not `,`.
- Do not use SQL `CREATE MATERIALIZED VIEW` syntax.
- Confirm destructive intent before generating `DROP VIEW` or `REBUILD`.
