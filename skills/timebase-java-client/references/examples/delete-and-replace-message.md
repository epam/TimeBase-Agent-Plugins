# Delete And Replace Message

**Type:** fragment, assumes a write-capable `DXTickDB` connection, an existing `DXTickStream`, and a constructed `InstrumentMessage` to write in place of the old one.

**When to use:** Replacing or removing the message at a single known timestamp for a single entity. See `stream-management.md`'s "Data removal" section for the rationale and the full method catalog.

```java
import deltix.qsrv.hf.pub.InstrumentMessage;
import deltix.qsrv.hf.pub.TimeStamp;
import deltix.qsrv.hf.tickdb.pub.*;

void replaceMessage(DXTickStream stream, InstrumentIdentity entity, long timestampNs, InstrumentMessage newMessage) {
    // Use the target message's own getTimeStampNs(), not a millisecond-truncated value, so the
    // deleted range exactly matches the message even if it carries a sub-millisecond component.
    TimeStamp target = TimeStamp.fromNanoseconds(timestampNs);
    stream.delete(target, target, entity);

    try (TickLoader loader = stream.createLoader()) {
        loader.send(newMessage); // newMessage must carry the same entity and the same timestampNs
    }
}
```

To remove the message instead of replacing it, skip the loader block entirely, the `delete` call alone is the removal.
