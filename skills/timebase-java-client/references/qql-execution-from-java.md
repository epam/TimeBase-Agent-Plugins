# QQL Execution From Java

Use this reference when executing QQL from Java and binding results to typed Java objects.

## Handoff from QQL generator

| Situation | Skill |
| --- | --- |
| User supplies final QQL | Stay here, execute and bind in Java |
| Query needs design, repair, or validation | Use `qql-generator` skill first, then return here |
| Small result, no Java artifact needed | QQL plus MCP, do not escalate to Java |

## Execution pattern

`select *` returns the underlying message's own type, so `cursor.getMessage()` can be used/cast directly. A partial field list (`select name from ...`) instead produces an anonymous synthetic result type — to read the projected fields, bind that anonymous type to a result class via `SelectionOptions.typeLoader` and `SimpleTypeLoader`, passing `null` as the type name (the projection has no declared name to match by):

```java
import deltix.qsrv.hf.pub.InstrumentMessage;
import deltix.qsrv.hf.pub.SimpleTypeLoader;
import deltix.qsrv.hf.tickdb.pub.*;
import deltix.qsrv.hf.tickdb.pub.query.Parameter;

public class QueryResult extends InstrumentMessage {
    public String name;
}

SelectionOptions options = new SelectionOptions();
options.raw = false;
options.typeLoader = new SimpleTypeLoader(null, QueryResult.class);

String qql = "select name from securities " +
    "where \"deltix.timebase.api.messages.securities.AbstractFuture\":rootsymbol == $root";

Parameter root = Parameter.VARCHAR("$root", "ES");

try (InstrumentMessageSource cursor = db.executeQuery(qql, options, root)) {
    while (cursor.next()) {
        QueryResult msg = (QueryResult) cursor.getMessage();
        System.out.println("symbol: " + msg.getSymbol() + " name: " + msg.name);
    }
}
```

Without `options.typeLoader`, `cursor.getMessage()` for a partial-projection query still returns a message, but its projected fields (`name` here) are not reachable through a typed getter — always bind a result class for `select <fields>` queries, and only skip this for `select *`.

## `executeQuery` overloads: pick by how much the query already says

`db.executeQuery` has more than one shape. Two current (non-deprecated) ones cover almost everything:

- `executeQuery(String qql, SelectionOptions options, Parameter... params)` — the default choice whenever `SelectionOptions` need to be customized (raw mode, live, etc.), with or without bind parameters (the varargs accepts zero params).
- `executeQuery(String qql, Parameter... params)` — no `SelectionOptions` at all; use for a quick one-off query where default selection behavior is fine and you don't want to construct an options object.

Avoid the overloads that additionally accept explicit `TickStream[]`, `InstrumentIdentity[]`/entity arrays, or start/end timestamps — see below, they're deprecated in favor of putting that same filtering directly in the QQL text.

## Bind parameters

`Parameter` factory methods bind values without string concatenation: `Parameter.BOOLEAN(name, value)`, `Parameter.INTEGER(name, value)`, `Parameter.FLOAT(name, value)`, `Parameter.VARCHAR(name, value)`, `Parameter.TIMESTAMP(name, value)`.

## Prefer QQL-embedded subscription over deprecated overloads

`executeQuery` overloads that take explicit stream arrays, entity arrays, or time bounds are deprecated. Express subscription filters directly in the QQL text instead:

```sql
SELECT * FROM (stream1 UNION stream2)
WHERE timestamp >= '2024-01-01 00:00:00'd AND symbol == 'AAPL'
```

This keeps the query self-describing and avoids relying on deprecated API surface.

## Inspecting a query without executing it

- `db.describeQuery(qql, options, params...)` returns the result schema (`ClassSet`) without running the query.
- `db.compileQuery(qql, outTokens)` compiles/tokenizes only, useful for validating QQL syntax before execution.
- Both throw a compilation exception on invalid QQL; surface that message rather than guessing at the fix.

## Common mistakes

- Generating QQL and Java when MCP could return the answer directly.
- Using a deprecated `executeQuery` overload (explicit stream/entity/time arrays) instead of embedding the filter in QQL text.
- Using unqualified type names in QQL where the server expects fully qualified class names, e.g. `"deltix.timebase.api.messages.securities.AbstractFuture":rootsymbol`.
- Omitting `options.typeLoader` for a partial-field-list (`select <fields>`) query, then being unable to read the projected fields off the returned message.
- Forgetting to close the query cursor.
