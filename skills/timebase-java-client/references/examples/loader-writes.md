# Loader Writes

**Type:** fragment, assumes a stream already exists with a matching schema.

**When to use:** Writing to a stream via `TickLoader`, plain defaults or configured. See [`loader-writes.md`](../loader-writes.md) for the full option reference.

## Basic write

```java
try (TickLoader loader = stream.createLoader()) {
    BarMessage msg = new BarMessage();
    msg.setSymbol("AAPL");
    msg.setTimeStampMs(System.currentTimeMillis());
    msg.setOpen(100.0);
    msg.setClose(101.0);
    loader.send(msg);
}
```

## Configured write with an error listener

```java
LoadingOptions options = new LoadingOptions(false, LoadingOptions.WriteMode.APPEND);

try (TickLoader loader = stream.createLoader(options)) {
    loader.addEventListener(new LoadingErrorListener() {
        @Override
        public void onError(LoadingError e) {
            System.out.println("Loading error: " + e.getMessage());
        }
    });

    BarMessage msg = new BarMessage();
    msg.setSymbol("AAPL");
    msg.setTimeStampMs(System.currentTimeMillis());
    msg.setOpen(100.0);
    msg.setClose(101.0);
    loader.send(msg);

    loader.flush();
}
```
