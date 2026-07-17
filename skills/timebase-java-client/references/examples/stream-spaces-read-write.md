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

## Lazy per-space loader for bulk writes

When writing to many spaces one after another (e.g. importing an archive with one entry per space, see `import-export.md`), defer `stream.createLoader(options)` per space until the first message for that space actually arrives, since loader creation has overhead and not every space may get written to:

```java
Map<String, List<RawMessage>> messagesBySpace = ...; // already grouped by space, e.g. one zip entry per space
Map<String, TickLoader> loadersBySpace = new HashMap<>();

try {
    for (Map.Entry<String, List<RawMessage>> entry : messagesBySpace.entrySet()) {
        String space = entry.getKey();
        TickLoader loader = loadersBySpace.computeIfAbsent(space, s -> {
            LoadingOptions options = new LoadingOptions(true, LoadingOptions.WriteMode.INSERT);
            options.withSpace(s);
            return stream.createLoader(options);
        });
        for (RawMessage msg : entry.getValue()) {
            loader.send(msg);
        }
    }
} finally {
    for (TickLoader loader : loadersBySpace.values()) {
        loader.close();
    }
}
```

## Discovering space names from a file name

```java
import deltix.util.text.SimpleStringCodec;

String spaceName = SimpleStringCodec.DEFAULT_INSTANCE.decode(entryNameWithoutExtension);
// encode: SimpleStringCodec.DEFAULT_INSTANCE.encode(spaceName)
```
