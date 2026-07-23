# Connect And List Streams

**Type:** fragment, assumes an open `DXTickDB` connection.

**When to use:** User explicitly asks for Java code that lists streams. For discovery-only questions ("what streams exist?"), use MCP instead.

## Snippet

```java
import deltix.qsrv.hf.tickdb.pub.DXTickDB;
import deltix.qsrv.hf.tickdb.pub.DXTickStream;

void listStreams(DXTickDB db) {
    for (DXTickStream stream : db.listStreams()) {
        String description = stream.getDescription();
        System.out.println(stream.getKey() + ": " +
            (description != null ? description : "(no description)"));
    }
}
```
