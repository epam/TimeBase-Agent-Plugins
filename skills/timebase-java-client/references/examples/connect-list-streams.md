# Connect And List Streams

**Type:** fragment

**When to use:** User explicitly asks for Java code that lists streams. For discovery-only questions ("what streams exist?"), use MCP instead.

## Snippet

```java
import deltix.qsrv.hf.tickdb.pub.DXTickDB;
import deltix.qsrv.hf.tickdb.pub.DXTickStream;
import deltix.qsrv.hf.tickdb.pub.TickDBFactory;

public final class StreamLister {

    public static void listStreams(String connectionUrl) {
        try (DXTickDB db = TickDBFactory.createFromUrl(connectionUrl)) {
            db.open(true); // readOnly

            for (DXTickStream stream : db.listStreams()) {
                String description = stream.getDescription();
                System.out.println(stream.getKey() + ": " +
                    (description != null ? description : "(no description)"));
            }
        }
    }
}
```
