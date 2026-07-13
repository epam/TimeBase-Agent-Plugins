# Create Stream

**Type:** fragment, assumes write-capable `ITickDb` connection.

**When to use:** User asks to create a TimeBase stream from C#.

Ground `[SchemaElement]` names from MCP `get_stream_schema` or user-provided schema.

## Create via introspector (built-in type)

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Api.Communication;
using Deltix.Timebase.Api.Messages;
using Deltix.Timebase.Api.Utilities.Schema;

var introspector = Introspector.CreateMessageIntrospector();
var descriptor = introspector.IntrospectRecordClass(typeof(BarMessage)); // BarMessage is an example message type

var options = new StreamOptions(
    StreamScope.Durable,
    streamKey,
    "Bar stream",
    StreamOptions.MaxDistribution);
options.SetFixedType(descriptor);

var stream = db.CreateStream(streamKey, options);
```
