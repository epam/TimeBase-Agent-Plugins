# QQL Query Result Binding

**Type:** fragment, assumes QQL text finalized (use qql-generator skill if not).

**When to use:** Execute QQL from C# and bind rows to a typed result object.

## Result POCO

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Api.Messages;

[SchemaElement(Name = "BarQueryResult")]
public sealed class BarQueryResult : InstrumentMessage
{
    [SchemaElement(Name = "close")]
    public double Close { get; set; }
}
```

## Execute

```csharp
using Deltix.Timebase.Api.Communication;
using Deltix.Timebase.Api.Utilities.Binding;

var options = new SelectionOptions
{
    Raw = false,
    Loader = new TypeLoader(typeof(BarQueryResult))
};

using var cursor = db.ExecuteQuery(
    $"select close from \"{streamKey}\" where symbol == 'GOOG'",
    options);

while (cursor.Next())
{
    if (cursor.GetMessage() is BarQueryResult row)
        Console.WriteLine($"{row.Symbol} close={row.Close}");
}
```
