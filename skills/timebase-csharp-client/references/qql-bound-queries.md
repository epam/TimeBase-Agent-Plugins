# QQL Bound Queries

Use this reference when executing QQL from C# and binding results to typed .NET objects.

## Handoff from QQL generator

| Situation | Skill |
| --- | --- |
| User supplies final QQL | Stay here, execute and bind in C# |
| Query needs design, repair, or validation | Use `qql-generator` skill first, then return here |
| Small result, no C# artifact needed | QQL plus MCP, do not escalate to C# |

## Execution pattern

A partial-field-list QQL query needs a dedicated `[SchemaElement]`-annotated result POCO bound via `SelectionOptions.Loader = new TypeLoader(typeof(ResultPoco))`, then `db.ExecuteQuery(qql, options)`. See [`examples/qql-query-result.md`](examples/qql-query-result.md) for the full runnable pattern.

## Key points

- Set `SelectionOptions.Raw = false` for bound objects.
- QQL type filters use fully qualified class names in quotes, for example `"deltix.timebase.api.messages.securities.AbstractFuture":rootsymbol`.
- Result POCO property names must align with the QQL projection.
- Use `SchemaUtilities.GetClassName(typeof(SomeMessage))` when building QQL from known .NET types programmatically.

## Common mistakes

- Generating QQL and C# when MCP could return the answer directly.
- Missing result POCO or `TypeLoader` for bound query output.
- Using unqualified type names in QQL where the server expects full class names.
- Forgetting to dispose the query cursor.
