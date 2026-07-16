# Stream Metadata

**Type:** fragment

**When to use:** User asks for Java code that inspects stream metadata (periodicity, time range, entities) rather than reading message data. For discovery-only questions, use MCP (`get_stream_time_range`, `get_stream_symbols`) instead.

```java
import deltix.qsrv.hf.pub.InstrumentIdentity;
import deltix.qsrv.hf.tickdb.pub.*;
import deltix.util.time.Periodicity;

for (DXTickStream stream : db.listStreams()) {
    System.out.printf("STREAM key: %s; name: %s; description: %s%n",
        stream.getKey(), stream.getName(), stream.getDescription());

    StreamOptions options = stream.getStreamOptions();
    Periodicity periodicity = options.periodicity;

    if (periodicity.getType() != Periodicity.Type.REGULAR) {
        System.out.println("    Periodicity: " + periodicity);
    } else {
        System.out.println("    Periodicity: " +
            periodicity.getInterval().getNumUnits() + " " + periodicity.getInterval().getUnit());
    }

    long[] range = stream.getTimeRange();
    if (range != null) {
        System.out.printf("    TIME RANGE: %tF .. %tF%n", range[0], range[1]);
    }

    for (InstrumentIdentity id : stream.listEntities()) {
        System.out.println("    ENTITY symbol: " + id.getSymbol());
    }
}
```

`getTimeRange()` returns `null` for an empty stream — check before formatting. `listEntities()` returns every distinct symbol currently in the stream, each as an `InstrumentIdentity`.
