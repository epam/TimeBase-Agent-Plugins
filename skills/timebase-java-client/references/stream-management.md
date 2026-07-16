# Stream Management

Use this reference for stream creation, stream-level metadata, dynamic cursor resubscription, and per-instrument stateful processing. For connecting, `select`/loader basics, and live/reversed reads, see `cursor-and-streams.md`.

## Dynamic resubscription

`TickCursor` supports changing its subscription at any time without recreating the cursor. Key methods: `addEntity(InstrumentIdentity)`/`removeEntity(InstrumentIdentity)`, `addEntities(InstrumentIdentity[], offset, length)`, `clearAllEntities()`, `addTypes(String...)`, `addStream(TickStream...)`, `subscribeToAllTypes()`/`subscribeToAllEntities()`, `setTimeForNewSubscriptions(long)` (controls the start time newly-added entities begin reading from), and `reset(long)` (rewinds/reopens the whole subscription at a new timestamp). Prefer these over tearing down and rebuilding a cursor when a live subscription needs to change:

```java
cursor.removeEntity(new InstrumentKey(InstrumentType.EQUITY, "AAPL"));
cursor.addEntity(new InstrumentKey(InstrumentType.EQUITY, "MSFT"));
cursor.addTypes(BarMessage.class.getName());
```

`setTypes(String... names)` replaces the type filter entirely; `addTypes(String... names)` adds to whatever is already subscribed. Use `setTypes` when establishing the initial filter right after `createCursor`, and `addTypes` when incrementally broadening an existing subscription.

## Space-aware streams

Only generate stream-space-specific selection or loading code (`SelectionOptions.withSpace(...)`, `LoadingOptions.space`) when stream space support is confirmed via MCP, user context, or API discovery. Do not invent space names or APIs. See `stream-spaces.md` for the full pattern.

## Stream creation: pick the smallest that fits

- `StreamOptions.fixedType(scope, key, title, distributionFactor, descriptor)` — one message type per stream. Default choice; use unless the stream genuinely needs to carry more than one type.
- `StreamOptions.polymorphic(scope, key, title, distributionFactor, descriptor1, descriptor2, ...)` — multiple message types in one stream (e.g. trades and quotes interleaved). Only use when the task actually calls for mixed types; reading it back requires `instanceof` dispatch (see `message-types-and-schema.md`).
- Low-level `db.createStream(key, name, description, distributionFactor)` followed by `stream.setFixedType(descriptor)` (or the polymorphic equivalent) — same result as `fixedType`/`polymorphic`, split into two calls. Prefer the single-call `StreamOptions` factories above unless the project's existing code already uses this two-step form, in which case match it.
- `new StreamOptions()` + `setMetaData(polymorphic, RecordClassSet)` — use only when the schema comes from a dynamically-collected `RecordClassSet` rather than descriptors you already have as literal values (e.g. recreating a stream from an imported file's own header — see `import-export.md`).

`StreamScope.DURABLE` persists to disk; `StreamScope.TRANSIENT` is buffered, non-durable, and lower-latency — only choose `TRANSIENT` when the user explicitly wants ephemeral/low-latency semantics and accepts data loss on restart.

For demo/setup code that may be re-run against the same server, check for and delete an existing stream before recreating it, rather than letting `createStream` fail on a name collision:

```java
DXTickStream existing = db.getStream(streamKey);
if (existing != null) {
    existing.delete();
}
DXTickStream stream = db.createStream(streamKey, options);
```

Only do this for setup/demo code the user controls — never delete a stream implicitly as a side effect of a read or write task.

## Stream metadata

Beyond reading message data, `stream.getStreamOptions()` exposes metadata: `options.periodicity` (a `Periodicity`, checked via `Periodicity.Type.REGULAR` and `getInterval()` for regular streams), and `stream.getTimeRange()` / `stream.listEntities()` for the covered time span and distinct symbols. See [`examples/stream-metadata.md`](examples/stream-metadata.md).

## Per-instrument stateful processing

A recurring pattern for indicators, latest-value snapshots, or any per-instrument accumulator: keep a small state object per instrument in an `InstrumentToObjectMap<T>`, keyed by the message itself (it implements `InstrumentIdentity`):

```java
import deltix.qsrv.hf.blocks.InstrumentToObjectMap;

InstrumentToObjectMap<MyState> states = new InstrumentToObjectMap<>();

try (InstrumentMessageSource cursor = stream.createCursor(null)) {
    cursor.reset(Long.MIN_VALUE);
    cursor.subscribeToAllEntities();

    while (cursor.next()) {
        InstrumentMessage msg = cursor.getMessage();
        if (msg instanceof BarMessage) {
            BarMessage bar = (BarMessage) msg;
            MyState state = states.get(bar);
            if (state == null) {
                state = new MyState();
                states.put(bar, state);
            }
            state.add(bar);
        }
    }
}
```

For a "latest value per instrument" snapshot specifically, combine this with a **reversed** cursor and unsubscribe each instrument once its state is complete, so the cursor naturally terminates once every instrument has been satisfied instead of scanning the whole stream:

```java
SelectionOptions options = new SelectionOptions(false, false);
options.reversed = true;

try (InstrumentMessageSource cursor = stream.createCursor(options)) {
    cursor.setTypes(BestBidOfferMessage.CLASS_NAME); // built-in message classes often expose a CLASS_NAME constant
    cursor.reset(System.currentTimeMillis());
    cursor.subscribeToAllEntities();

    while (cursor.next()) {
        BestBidOfferMessage bbo = (BestBidOfferMessage) cursor.getMessage();
        // ... accumulate bid/offer into a per-instrument PriceInfo via InstrumentToObjectMap ...
        // once both sides are known for this instrument:
        cursor.removeEntity(bbo);
    }
}
```
