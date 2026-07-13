# QQL Bound Queries

Use this reference when executing QQL from C# and binding results to typed .NET objects.

## Handoff from QQL generator

| Situation | Skill |
| --- | --- |
| User supplies final QQL | Stay here, execute and bind in C# |
| Query needs design, repair, or validation | Use `qql-generator` skill first, then return here |
| Small result, no C# artifact needed | QQL plus MCP, do not escalate to C# |

## Execution pattern

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Api.Communication;
using Deltix.Timebase.Api.Messages;
using Deltix.Timebase.Api.Utilities.Binding;

[SchemaElement(Name = "QueryResult")]
public sealed class QueryResult : InstrumentMessage
{
    public string? Name { get; set; }
}

var options = new SelectionOptions
{
    Raw = false,
    Loader = new TypeLoader(typeof(QueryResult))
};

const string qql =
    "select name from securities " +
    "where \"deltix.timebase.api.messages.securities.AbstractFuture\":rootsymbol == 'ES'";

using var cursor = db.ExecuteQuery(qql, options);

while (cursor.Next())
{
    var msg = cursor.GetMessage();
    var result = msg as QueryResult;
    Console.WriteLine($"symbol: {msg.Symbol} name: {result?.Name ?? "N/A"}");
}
```

## Key points

- Set `SelectionOptions.Raw = false` for bound objects.
- Configure `TypeLoader(typeof(QueryResult))` for custom result types.
- QQL type references often need fully qualified names in quotes, for example `"deltix.timebase.api.messages.securities.AbstractFuture":rootsymbol`.
- Result POCO property names must align with the QQL projection.
- Use `SchemaUtilities.GetClassName(typeof(SomeMessage))` when building QQL from known .NET types programmatically.

## Common mistakes

- Generating QQL and C# when MCP could return the answer directly.
- Missing result POCO or `TypeLoader` for bound query output.
- Using unqualified type names in QQL where the server expects full class names.
- Forgetting to dispose the query cursor.
