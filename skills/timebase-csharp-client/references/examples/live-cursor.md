# Live Cursor

**Type:** fragment

**When to use:** Consume live messages as they arrive. MCP-ground stream key.

```csharp
using Deltix.Timebase.Api.Communication;
using Deltix.Timebase.Api.Messages;
using Deltix.Timebase.Api.Utilities.Binding;
using Deltix.Timebase.Api.Utilities.Cursor;

var options = new SelectionOptions
{
    Live = true,
    Loader = new TypeLoader(typeof(BarMessage))
};

using var cursor = stream.Select(DateTime.UtcNow, options, null, null);
using var watcher = new LiveCursorWatcher(cursor, () =>
{
    if (cursor.GetMessage() is BarMessage bar)
        Console.WriteLine($"[LIVE] {bar.Symbol} close={bar.Close}");
});

// ... produce or wait for data ...
watcher.Close();
```

Dispose watcher and cursor on shutdown.
