# Large Export

**Type:** fragment

**When to use:** Large bounded read exported to disk. Narrow with MCP/QQL first, stream rows to CSV or JSON.

```csharp
using System.Text.Json;
using Deltix.Timebase.Api.Communication;
using Deltix.Timebase.Api.Messages;
using Deltix.Timebase.Api.Utilities.Binding;

await using var writer = new StreamWriter(outputPath);
using var cursor = stream.Select(
    startTimeUtc,
    new SelectionOptions { Loader = new TypeLoader(typeof(BarMessage)) },
    new[] { typeof(BarMessage).FullName! },
    entities);

while (cursor.Next())
{
    if (cursor.GetMessage() is BarMessage bar)
        await writer.WriteLineAsync(JsonSerializer.Serialize(new { bar.Symbol, bar.Timestamp, bar.Close }));
}
```

Prefer `System.Text.Json` or simple CSV. Add third-party packages only when the project already uses them.
