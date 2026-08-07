# QQL Execution From Java

Use this reference when executing QQL from Java and binding results to typed Java objects.

Examples below use the Enterprise Edition `deltix.*` package root. See the package-root mapping and edition differences in [`project-setup.md`](project-setup.md#package-roots-in-this-skills-examples) before applying these examples to a Community Edition project.

## Handoff from QQL generator

| Situation | Skill |
| --- | --- |
| User supplies final QQL | Stay here, execute and bind in Java |
| Query needs design, repair, or validation | Use `qql-generator` skill first, then return here |
| Small result, no Java artifact needed | QQL plus MCP, do not escalate to Java |

## Execution pattern

`select *` returns the underlying message's own type, so `cursor.getMessage()` can be used/cast directly. A partial field list (`select name from ...`) instead produces an anonymous synthetic result type. To read the projected fields, bind that anonymous type to a result class via `SelectionOptions.typeLoader` and `SimpleTypeLoader`, passing `null` as the type name since the projection has no declared name to match by:

```java
options.typeLoader = new SimpleTypeLoader(null, CloseResult.class);
```

See [`examples/qql-query-result.md`](examples/qql-query-result.md) for the full runnable pattern, including the bind-parameter and result-class setup.

Without `options.typeLoader`, `cursor.getMessage()` for a partial-projection query still returns a message, but its projected fields are not reachable through a typed getter. Always bind a result class for `select <fields>` queries, only skip this for `select *`.

QQL type filters use fully qualified class names in quotes, e.g. `"deltix.timebase.api.messages.securities.AbstractFuture":rootsymbol`. The specific stream/type in an example is illustrative, swap in whatever actually applies to the target project, the syntax being demonstrated is the `"TypeName":field` filter itself.

## `executeQuery` overloads: pick by how much the query already says

`db.executeQuery` has more than one shape. Two current (non-deprecated) ones cover almost everything:

- `executeQuery(String qql, SelectionOptions options, Parameter... params)`: the default choice whenever `SelectionOptions` need to be customized (raw mode, live, etc.), with or without bind parameters.
- `executeQuery(String qql, Parameter... params)`: no `SelectionOptions` at all, use for a quick one-off query where default selection behavior is fine and you don't want to construct an options object.

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
- Both throw a compilation exception on invalid QQL, surface that message rather than guessing at the fix.

## Common mistakes

- Generating QQL and Java when MCP could return the answer directly.
- Using a deprecated `executeQuery` overload (explicit stream/entity/time arrays) instead of embedding the filter in QQL text.
- Using unqualified type names in QQL where the server expects fully qualified class names.
- Omitting `options.typeLoader` for a partial-field-list (`select <fields>`) query, then being unable to read the projected fields off the returned message.
- Forgetting to close the query cursor.
