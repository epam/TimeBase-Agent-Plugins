# Cursor And Streams

Use direct cursors when ordering, typed messages, or incremental logic matters.

## Connection bootstrap

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Client;

ITickDb? db = null;
try
{
    db = TickDbFactory.CreateFromUrl(connectionUrl)
        ?? throw new InvalidOperationException("TickDbFactory returned null.");
    db.Open(readOnly: true);
    // use db
}
finally
{
    db?.Dispose();
}
```

## Resolve stream and select

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Api.Communication;
using Deltix.Timebase.Api.Messages;
using Deltix.Timebase.Api.Utilities.Binding;

var stream = db.GetStream(streamKey);
if (stream is null)
{
    Console.WriteLine($"Stream '{streamKey}' not found.");
    return;
}

var entities = new IInstrumentIdentity[]
{
    new InstrumentKey(InstrumentType.Custom, "GOOG")
};

var typeName = typeof(BarMessage).FullName;
var types = new[] { typeName };

using var cursor = stream.Select(
    DateTime.MinValue,
    new SelectionOptions
    {
        Loader = new TypeLoader(typeof(BarMessage))
    },
    types,
    entities);

while (cursor.Next())
{
    var msg = cursor.GetMessage();
    Console.WriteLine(msg);
}
```

## Loader write

```csharp
var loadingOptions = new LoadingOptions
{
    Loader = new TypeLoader(typeof(BarMessage))
};
using var loader = stream.CreateLoader(loadingOptions);

var message = new BarMessage
{
    Symbol = "AAPL",
    Timestamp = DateTime.UtcNow,
    OpenPrice = 100.0,
    ClosePrice = 101.0
};
loader.Send(message);
```

## Historical vs reverse reads

- **Historical**: start from a bounded timestamp (`DateTime.MinValue` for beginning, or a specific UTC time).
- **Reverse**: set `SelectionOptions.Reversed = true` and start from `DateTime.UtcNow` to walk backward.

## Resource lifecycle

- Prefer `using` for cursors and loaders.
- Start `readOnly: true` unless writes are required.

## Live cursors

Live consumption uses `SelectionOptions.Live = true` and `LiveCursorWatcher`. See `examples/live-cursor.md`. Dispose watcher and cursor on shutdown.

## Space-aware streams

Only generate space-specific selection or loading code when stream space support is confirmed via MCP, user context, or API discovery. Do not invent space names or APIs.
