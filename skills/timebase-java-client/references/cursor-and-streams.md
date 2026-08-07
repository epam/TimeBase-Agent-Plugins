# Cursor And Streams

Use direct cursors when ordering, typed messages, or incremental logic matters. For connecting, see [`authentication.md`](authentication.md). For stream creation and metadata, see [`stream-management.md`](stream-management.md).

Examples below use the Enterprise Edition `deltix.*` package root. See the package-root mapping and edition differences in [`project-setup.md`](project-setup.md#package-roots-in-this-skills-examples) before applying these examples to a Community Edition project.

## Resolve stream and read: `select` vs `createCursor`

Both `stream.select(...)` and `stream.createCursor(...)` return the same `TickCursor` type. It can change its subscription after creation via `addEntity`/`removeEntity`/`addTypes`/`setTypes`/etc. (see "Dynamic resubscription" below), it doesn't matter which method created it. The choice between them is about workflow, not capability:

- `select(...)` sets the initial type/entity filter in one call. Use it whenever the initial filter is known now. See [`examples/read-write-bound.md`](./examples/read-write-bound.md) for a full read loop.
- `createCursor(...)` returns an unsubscribed cursor that you configure manually, then start with `reset(time)`. Use it when building up the subscription across several steps before the first read.

`select` takes two filters: `String[] types` (fully qualified class names, `null` for all types) and an entity filter (`null` for all entities). The entity filter has two overloads, `CharSequence[]` and `InstrumentIdentity[]` (symbol + `InstrumentType` pairs, e.g. `new InstrumentKey(InstrumentType.EQUITY, "AAPL")`). Use `InstrumentIdentity[]` only when the stream mixes instrument types and the symbol alone is ambiguous, otherwise the plain symbol array is simpler.

`createCursor` example:

```java
try (TickCursor cursor = stream.createCursor(new SelectionOptions())) {
    cursor.subscribeToAllTypes();
    cursor.addEntity(new InstrumentKey(InstrumentType.EQUITY, "AAPL"));
    cursor.reset(Long.MIN_VALUE);

    while (cursor.next()) {
        // ...
    }
}
```

## Dynamic resubscription

`TickCursor` supports changing its subscription at any time without recreating the cursor. Key methods: `addEntity(InstrumentIdentity)`/`removeEntity(InstrumentIdentity)`, `addEntities(InstrumentIdentity[], offset, length)`, `clearAllEntities()`, `addTypes(String...)`, `addStream(TickStream...)`, `subscribeToAllTypes()`/`subscribeToAllEntities()`, `setTimeForNewSubscriptions(long)` (controls the start time newly-added entities begin reading from), and `reset(long)` (rewinds/reopens the whole subscription at a new timestamp). Prefer these over tearing down and rebuilding a cursor when a live subscription needs to change. See [`examples/dynamic-resubscription.md`](examples/dynamic-resubscription.md) for a live example.

`setTypes(String... names)` replaces the type filter entirely. `addTypes(String... names)` adds to whatever is already subscribed. Use `setTypes` when establishing the initial filter right after `createCursor`, and `addTypes` when incrementally broadening an existing subscription.

## Selecting across multiple streams at once

`DXTickDB` itself exposes a `select(startTimestamp, selectionOptions, types, entities, streams...)` overload that reads a merged, time-ordered view across several named streams without a QQL `UNION`. Use it when the task is "read these N streams together" and QQL isn't otherwise needed:

```java
try (TickCursor cursor = db.select(Long.MIN_VALUE, new SelectionOptions(), streamA, streamB)) {
    while (cursor.next()) {
        InstrumentMessage msg = cursor.getMessage();
    }
}
```

If the task already needs QQL for filtering/aggregation, prefer expressing the stream union in QQL text instead (see [`qql-execution-from-java.md`](./qql-execution-from-java.md)) rather than mixing both mechanisms.

## Recency and direction

`SelectionOptions` has two separate flags, don't treat them as one choice:

- `live`: whether the cursor stops at the end of currently stored data (`false`, historical) or waits for new data to arrive (`true`).
- `reversed`: which direction the cursor reads in (forward by default, backward when `true`).

A reversed read is normally also historical (`reversed = true`, `live = false`), start from "now" and walk backward, useful for "latest value per instrument" queries. Live tailing is normally forward. Reversed and live at once isn't a meaningful combination.

See [`examples/live-cursor.md`](./examples/live-cursor.md) for live cursor example. When combining historical replay with live tailing, set `SelectionOptions.realTimeNotification = true` to receive a `RealTimeStartMessage` marker at the point where the cursor transitions from historical to live data.

Other `SelectionOptions` fields worth knowing about:

- `allowLateOutOfOrder`: deliver out-of-order messages that arrive mid-live-session with a timestamp already in the past, instead of dropping them.
- `rebroadcast`: replay the unique last message on open/reset, default `true`.
- `versionTracking`: receive `StreamTruncatedMessage`/`MetaDataChangeMessage` notifications when the stream is truncated or its metadata changes.
- `ordered`: enforce a fixed message order from the cursor independent of subscribed entities.
- `restrictStreamType`: restrict the cursor to the type of the first stream added, useful for a small performance gain when you know you won't mix stream types.
- `shiftOffset`: how far to shift the cursor relative to the current timestamp when a truncation occurs.
- `includeSchemaChangeMessages`: include schema-change messages in the read results.

## Resource lifecycle

- Prefer try-with-resources for `DXTickDB`, `TickCursor`, and `TickLoader`.
- Start `db.open(true)` (read-only) unless writes are required.
- All read methods on a given `TickCursor` must be called from a single thread, only `close()` and other control methods are safe to call concurrently.
