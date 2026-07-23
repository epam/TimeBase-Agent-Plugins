# Schema Introspection

**Type:** fragment

**When to use:** Runtime schema inspection in Java. Prefer MCP `get_stream_schema` for agent-side discovery, use this when the user needs Java descriptor traversal.

```java
import deltix.qsrv.hf.pub.md.DataField;
import deltix.qsrv.hf.pub.md.RecordClassDescriptor;
import deltix.qsrv.hf.pub.md.RecordClassSet;
import deltix.qsrv.hf.tickdb.pub.DXTickStream;
import deltix.qsrv.hf.tickdb.pub.StreamOptions;

DXTickStream stream = db.getStream(streamKey);
if (stream == null) {
    throw new IllegalStateException("Stream '" + streamKey + "' not found.");
}

StreamOptions options = stream.getStreamOptions();
RecordClassSet metadata = options.getMetaData();

for (RecordClassDescriptor descriptor : metadata.getContentClasses()) {
    System.out.println(descriptor.getName());
    for (DataField field : descriptor.getFields()) {
        System.out.println("  " + field.getName());
    }
}
```

`options.getMetaData()` returns the stream's full schema as a `RecordClassSet`, covering both fixed-type and polymorphic streams uniformly. Use `getContentClasses()` (not `getClasses()`) to get `RecordClassDescriptor[]` directly, `getClasses()` returns the broader `ClassDescriptor[]` type.
