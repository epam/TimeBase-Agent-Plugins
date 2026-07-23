# Create Stream

**Type:** fragment, assumes write-capable `DXTickDB` connection.

**When to use:** User asks to create a TimeBase stream from Java.

Ground schema field names from MCP `get_stream_schema` or user-provided schema.

## Create via introspector (built-in type)

```java
import deltix.qsrv.hf.pub.md.Introspector;
import deltix.qsrv.hf.pub.md.RecordClassDescriptor;
import deltix.qsrv.hf.tickdb.pub.*;
import deltix.timebase.api.messages.BarMessage;

Introspector introspector = Introspector.createEmptyMessageIntrospector();
RecordClassDescriptor descriptor = introspector.introspectRecordClass(BarMessage.class);

StreamOptions options = StreamOptions.fixedType(
    StreamScope.DURABLE, streamKey, "Bar stream",
    StreamOptions.MAX_DISTRIBUTION, descriptor);

DXTickStream stream = db.createStream(streamKey, options);
```

## Create with an explicit descriptor (custom type)

```java
import deltix.qsrv.hf.pub.md.*;
import deltix.qsrv.hf.tickdb.pub.*;

DataField[] fields = {
    new NonStaticDataField("closePrice", "Close Price",
        new FloatDataType(FloatDataType.ENCODING_FIXED_DOUBLE, true)),
    new NonStaticDataField("openPrice", "Open Price",
        new FloatDataType(FloatDataType.ENCODING_FIXED_DOUBLE, true))
};

RecordClassDescriptor descriptor = new RecordClassDescriptor(
    "myapp.messages.BarMessage", "Bar Message", false, null, fields);

StreamOptions options = StreamOptions.fixedType(
    StreamScope.DURABLE, streamKey, "Bar Messages",
    StreamOptions.MAX_DISTRIBUTION, descriptor);

DXTickStream stream = db.createStream(streamKey, options);
```

## Delete before recreate (setup/demo code only)

For setup/demo code that may be re-run against the same server, check for and delete an existing stream before recreating it, rather than letting `createStream` fail on a name collision. Only do this for setup/demo code the user controls, never delete a stream implicitly as a side effect of a read or write task:

```java
DXTickStream existing = db.getStream(streamKey);
if (existing != null) {
    existing.delete();
}
DXTickStream stream = db.createStream(streamKey, options);
```
