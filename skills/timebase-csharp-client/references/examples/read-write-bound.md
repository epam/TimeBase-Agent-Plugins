# Read Write Bound Messages

**Type:** fragment

**When to use:** Typed read/write against a stream. MCP-ground the stream key.

## Write

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Api.Communication;
using Deltix.Timebase.Api.Messages;
using Deltix.Timebase.Api.Utilities.Binding;

var stream = db.GetStream(streamKey)
    ?? throw new InvalidOperationException($"Stream '{streamKey}' not found.");

using var loader = stream.CreateLoader(new LoadingOptions
{
    Loader = new TypeLoader(typeof(BarMessage))
});

var bar = new BarMessage
{
    Symbol = "AAPL",
    Timestamp = DateTime.UtcNow,
    Open = 100.0,
    Close = 101.0,
    High = 102.0,
    Low = 99.0,
    Volume = 1000
};
loader.Send(bar);
```

## Read with symbol filter

```csharp
var entities = new IInstrumentIdentity[] { new InstrumentKey(InstrumentType.Equity, "GOOG") };
var types = new[] { typeof(BarMessage).FullName! };

using var cursor = stream.Select(
    DateTime.MinValue,
    new SelectionOptions { Loader = new TypeLoader(typeof(BarMessage)) },
    types,
    entities);

while (cursor.Next())
    Console.WriteLine(cursor.GetMessage());
```
