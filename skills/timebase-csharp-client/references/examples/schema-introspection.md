# Schema Introspection

**Type:** fragment

**When to use:** Runtime schema inspection in C#. Prefer MCP `get_stream_schema` for agent-side discovery, use this when the user needs C# descriptor traversal.

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Api.Schema;

var stream = db.GetStream(streamKey)
    ?? throw new InvalidOperationException($"Stream '{streamKey}' not found.");

foreach (var descriptor in stream.GetDescriptors())
{
    Console.WriteLine(descriptor.Name);
    foreach (var field in descriptor.Fields ?? Array.Empty<DataField>())
        Console.WriteLine($"  {field.Name}");
}
```
