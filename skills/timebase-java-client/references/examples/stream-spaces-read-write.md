# Stream Spaces Read/Write

**Type:** fragment, assumes a stream with confirmed space support.

**When to use:** Reading/writing a specific named space within a stream, or building a lazy per-space loader for bulk import.

## Reading/writing a specific space

```java
LoadingOptions loadingOptions = new LoadingOptions(true, LoadingOptions.WriteMode.INSERT);
loadingOptions.withSpace(spaceName);
try (TickLoader loader = stream.createLoader(loadingOptions)) {
    loader.send(msg);
}

SelectionOptions selectionOptions = new SelectionOptions(true, false);
selectionOptions.withSpace(spaceName);
try (InstrumentMessageSource source = stream.select(Long.MIN_VALUE, selectionOptions)) {
    while (source.next()) {
        // ...
    }
}
```

## Discovering space names from a file name

```java
import deltix.util.text.SimpleStringCodec;

String spaceName = SimpleStringCodec.DEFAULT_INSTANCE.decode(entryNameWithoutExtension);
// encode: SimpleStringCodec.DEFAULT_INSTANCE.encode(spaceName)
```

## A loader that lazily creates itself per space

```java
class SpaceLoader implements MessageChannel<InstrumentMessage> {
    private final LoadingOptions options;
    private final DXTickStream stream;
    private TickLoader loader;

    SpaceLoader(DXTickStream stream, LoadingOptions options) {
        this.stream = stream;
        this.options = options;
    }

    public void send(InstrumentMessage msg) {
        if (loader == null) {
            loader = stream.createLoader(options);
        }
        loader.send(msg);
    }

    public void close() {
        if (loader != null) {
            loader.close();
        }
    }
}
```
