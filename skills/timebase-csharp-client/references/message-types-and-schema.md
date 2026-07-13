# Message Types And Schema

Use this reference when generating bound message classes, creating streams, or configuring `TypeLoader`.

## Bound message POCOs

Custom messages inherit `InstrumentMessage` and use `[SchemaElement]` attributes:

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Api.Messages;

[SchemaElement(Name = "MyApp.Messages.BarMessage", Title = "Bar Message")]
public class BarMessage : InstrumentMessage
{
    [SchemaElement(Name = "closePrice", Title = "Close Price")]
    public double ClosePrice { get; set; }

    [SchemaElement(Name = "openPrice", Title = "Open Price")]
    public double OpenPrice { get; set; }
}
```

Ground `[SchemaElement]` names from MCP `get_stream_schema` or user-provided schema. If schema is unknown, label the POCO as illustrative and tell the user to confirm field names before production use.

Built-in types in `Deltix.Timebase.Api.Messages` (for example `BarMessage`, `BestBidOfferMessage`) can be used when they match the stream schema or fit the domain.

## TypeLoader guidance

Configure `TypeLoader` when binding custom POCOs or QQL result types:

```csharp
var options = new SelectionOptions
{
    Loader = new TypeLoader(typeof(BarMessage))
};
```

```csharp
var loadingOptions = new LoadingOptions
{
    Loader = new TypeLoader(typeof(BarMessage))
};
using var loader = stream.CreateLoader(loadingOptions);
```

Do not claim every read path needs `TypeLoader`. Raw mode (`SelectionOptions.Raw = true`) may work without custom loaders.

## Stream creation: introspector

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Api.Communication;
using Deltix.Timebase.Api.Utilities.Schema;

var introspector = Introspector.CreateMessageIntrospector();
var descriptor = introspector.IntrospectRecordClass(typeof(BarMessage));

var options = new StreamOptions(
    StreamScope.Durable,
    "mybars",
    "Bar Messages Stream",
    StreamOptions.MaxDistribution);
options.SetFixedType(descriptor);

var stream = db.CreateStream("mybars", options);
```

Prefer introspection when a POCO already exists.

## Stream creation: explicit descriptor

Use explicit `RecordClassDescriptor` and `DataField` definitions when introspection is insufficient or schema must be defined without a POCO:

```csharp
using Deltix.Timebase.Api.Schema;
using Deltix.Timebase.Api.Schema.Types;

var fields = new DataField[]
{
    new NonStaticDataField("closePrice", "Close Price",
        new FloatDataType(FloatDataType.EncodingFixedDouble, true)),
    new NonStaticDataField("openPrice", "Open Price",
        new FloatDataType(FloatDataType.EncodingFixedDouble, true))
};

var descriptor = new RecordClassDescriptor(
    "MyApp.Messages.BarMessage",
    "Bar Message",
    false,
    null,
    fields);

var options = new StreamOptions(StreamScope.Durable, "mybars", "Bar Messages", StreamOptions.MaxDistribution);
options.SetFixedType(descriptor);
var stream = db.CreateStream("mybars", options);
```

## QQL result types

QQL queries that return a subset of fields need a dedicated result class:

```csharp
[SchemaElement(Name = "QueryResult")]
public sealed class QueryResult : InstrumentMessage
{
    public string? Name { get; set; }
}
```

Field names must match the QQL projection. Use MCP or schema evidence for exact names.

## Polymorphic reads

For streams with multiple message types, branch on runtime type:

```csharp
while (cursor.Next())
{
    var msg = cursor.GetMessage();
    if (msg is BestBidOfferMessage bbo)
    {
        // handle BBO
    }
    else if (msg is BarMessage bar)
    {
        // handle bar
    }
}
```

Inspect schema before writing polymorphic logic. See `examples/schema-introspection.md`.

## Common mistakes

- Inventing `[SchemaElement]` names without schema evidence.
- Missing `TypeLoader` on bound reads/writes.
