# Symbol Mapping And Cross-Instance Sync

**Type:** fragment, assumes a write-capable `DXTickDB` connection.

**When to use:** Copying a stream while remapping symbols, or synchronizing a target stream from a source. See `symbol-mapping-and-sync.md` for the rationale and caveats.

## Copying a stream while remapping symbols (raw)

```java
import deltix.util.collections.CharSequenceKey;

void mapSymbols(MessageSource<InstrumentMessage> in, Map<Object, String> symbolMap,
                 MessageChannel<InstrumentMessage> out) {
    RawMessage outMsg = new RawMessage();
    CharSequenceKey symbolKey = new CharSequenceKey(); // reusable lookup key, mutated per message below

    while (in.next()) {
        RawMessage inMsg = (RawMessage) in.getMessage();

        // reusable lookup key, see symbol-mapping-and-sync.md for why
        symbolKey.charSequence = inMsg.getSymbol();
        String newSymbol = symbolMap.get(symbolKey);

        if (newSymbol == null) {
            continue; // unmatched symbol: skip (and typically log once per unique symbol)
        }

        outMsg.setSymbol(newSymbol);
        outMsg.setTimeStampMs(inMsg.getTimeStampMs());
        outMsg.data = inMsg.data;
        outMsg.offset = inMsg.offset;
        outMsg.length = inMsg.length;
        outMsg.type = inMsg.type; // requires schema equivalence between source and target

        out.send(outMsg);
    }
}
```

```java
StreamOptions targetOptions = sourceStream.getStreamOptions();
targetOptions.name = targetKey;
DXTickStream targetStream = db.createStream(targetKey, targetOptions);
```

## Synchronizing a target stream from a source

```java
long[] getTimeRange(InstrumentIdentity id); // per-instrument overload, in addition to the whole-stream getTimeRange()
```

```java
long globalStartTime = Long.MAX_VALUE;

for (InstrumentIdentity id : source.listEntities()) {
    long[] sourceRange = source.getTimeRange(id);
    if (sourceRange == null) continue; // no source data for this instrument

    long[] targetRange = target.getTimeRange(id);
    long instrumentStart = (targetRange == null) ? sourceRange[0] : targetRange[1];
    globalStartTime = Math.min(globalStartTime, instrumentStart);
}

try (InstrumentMessageSource cursor = source.createCursor(null);
     TickLoader loader = target.createLoader()) {
    cursor.reset(globalStartTime);
    cursor.subscribeToAllEntities();

    while (cursor.next()) {
        loader.send(cursor.getMessage());
    }
}
```
