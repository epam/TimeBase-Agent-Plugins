# Connect And List Streams

**Type:** fragment

**When to use:** User explicitly asks for C# code that lists streams. For discovery-only questions ("what streams exist?"), use MCP instead.

## Snippet

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Client;

public static class StreamLister
{
    public static void ListStreams(string connectionUrl)
    {
        ITickDb? db = null;
        try
        {
            db = TickDbFactory.CreateFromUrl(connectionUrl)
                ?? throw new InvalidOperationException("TickDbFactory returned null.");
            db.Open(readOnly: true);

            foreach (var stream in db.ListStreams())
                Console.WriteLine($"{stream.Key}: {stream.Description ?? "(no description)"}");
        }
        finally
        {
            db?.Dispose();
        }
    }
}
```
