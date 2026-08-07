# Cursor And Streams

## Resolving a stream

```cpp
TickStream *stream = db->getStream("bars1min");
if (!stream) {
    // stream does not exist, ground the key via MCP list_streams rather than inventing one
}
```

## Historical read

`TickStream::select(startTimeMs, options)` (or `TickDb::select(startTimeMs, streams, options)` to select across several streams at once) returns a `TickCursor`, iterated via `getReader()`/`next(&header)`/`close()`. Start time `0` reads from the beginning, use a specific millisecond timestamp grounded via `get_stream_time_range` for a bounded start. See [`examples/read-write-bound.md`](examples/read-write-bound.md) for the full read (and write) flow.

Both `TickStream::select` and `TickDb::select` also have overloads taking explicit `types` and `entities`/`symbols` filter vectors (either pointer may be `nullptr` to mean "no filter on this dimension"), for selecting a narrower set than the stream's/options' own subscription without going through `createCursor` plus a separate `addTypes`/`addEntities` call. Prefer these over post-creation resubscription when the filter is known upfront and won't change.

## Live / resettable cursor

`createCursor` plus `reset` gives a cursor that can be repositioned without recreating it, useful for a live-polling loop. `SelectionOptions::live` (bool) enables live subscription. `nextIfAvailable` returning `false` only means no message was ready on that poll, not that the cursor ended, check `header.cursorState` (>= 2 signals true end-of-cursor, the field is declared on the `MessageHeader` base class that `InstrumentMessage` derives from) to know when to actually stop polling. See [`examples/live-cursor.md`](examples/live-cursor.md) for the full pattern.

`SelectionOptions` has several other fields beyond `from`/`to`/`live`/`reverse`: `useCompression`, `autoClose`, `isBigEndian`, `allowLateOutOfOrder`, `minLatency`, a nullable `rebroadcast`, a nullable `space` plus a nullable `spaces` list (set via the `withSpaces()` helper, see `stream-spaces.md`), `realTimeNotification`, and `recvBufferSize`/`sendBufferSize`. Leave these at their defaults unless the user has a specific throughput/latency/space-scoping requirement.

`cursor->getMessageSchema(msgDescId)` returns a pointer to the schema text for a specific message descriptor id the cursor has already resolved, or `nullptr` if that descriptor id isn't known, check before dereferencing, same convention as `getMessageTypeName` above. Useful for inspecting one message type's shape without re-parsing the whole stream's `metadata()`.

`cursor->isAtEnd()`/`isClosed()` report cursor state directly, as an alternative to inferring end-of-cursor from `header.cursorState` after a `nextIfAvailable` call. Either check works, pick whichever reads more naturally for the loop shape in question.

`cursor->getSymbolName(entityId)` and `cursor->getInstrumentType(symbolId)` resolve a numeric entity/symbol id from `header` back to its human-readable name/`InstrumentType`, the cursor-side counterpart to `getMessageTypeName` above. `InstrumentMessage` also exposes `getSymbolName()`/`getInstrumentType(unsigned)` directly as convenience methods, see `message-types-and-decimal64.md`.

## Reverse read

`SelectionOptions::reverse` (bool) walks backward from the start time. Combine it with `SelectionOptions::from`/`to` to bound the window explicitly.

## Stream creation

Two ways to create a stream, pick based on what the project already does: the native `TickDb::createStream(key, StreamOptions)` (may not exist on older pinned dxapi versions), or QQL DDL via `executeQuery` (ground the DDL text via the QQL generator skill rather than freehand-writing schema QQL). See [`examples/create-stream.md`](examples/create-stream.md).

A simpler `createStream(key, name, description, distributionFactor)` overload also exists for a stream that doesn't need the full `StreamOptions` set (schema, buffering, scope, etc.) configured up front, use the `StreamOptions` overload instead once the task needs any of those.

`TickDb::createFileStream(key, dataFile)` creates a stream backed by an external data file instead of the database's own storage, use this for an import-style workflow where the data already exists as a file on disk.

## Multiplexed cursor

`TickDb::createMultiplexedCursor(muxConfig, time, options)` returns a single cursor that merges multiple streams/entities per a multiplexing configuration string, an alternative to `TickDb::select(startTimeMs, streams, options)` when the merge criteria are more involved than "these streams from this time".

## Dynamic resubscription

A cursor's entity/type subscription isn't fixed at creation, it can change mid-poll: `cursor->addEntity(identity)`/`addEntities(vector<InstrumentIdentity>)` and `removeEntity(identity)`/`removeEntities(...)` add or drop individual entities, `subscribeToAllEntities()`/`subscribeToAllTypes()` switch to receiving everything, `clearAllEntities()` drops the entire entity list at once rather than removing entities one by one. Use this for a live cursor whose subscription set needs to grow or shrink while the loop keeps running, rather than closing and recreating the cursor. See [`examples/dynamic-resubscription.md`](examples/dynamic-resubscription.md).

Message types have the same add/remove/set shape as entities: `cursor->addTypes(vector<string>)`/`removeTypes(...)` add or drop individual type names, `setTypes(vector<string>)` replaces the whole type subscription at once (an empty vector unsubscribes from all messages). `cursor->add(entities, types)`/`remove(entities, types)` are shortcuts equivalent to calling the entity and type methods separately, they cannot be used to subscribe to "all" entities or types, use `subscribeToAllEntities()`/`subscribeToAllTypes()` for that instead.

`cursor->addStreams(vector<TickStream*>)`/`removeStreams(...)`/`removeAllStreams()` subscribe/unsubscribe whole streams instead of individual entities, for a multi-stream cursor whose stream set itself needs to change mid-poll. `cursor->setTimeForNewSubscriptions(TimestampMs)` controls when a pending subscription change actually takes effect, rather than immediately. `cursor->getMessageStreamKey(header.typeId)` resolves which stream a given message descriptor came from, useful when a cursor spans multiple streams (e.g. from `createMultiplexedCursor` or `addStreams`) and the consumer needs to disambiguate origin.

## Resource lifecycle

Wrap every `TickCursor`/`TickLoader`/`TickDb` in `std::unique_ptr` or close explicitly on every exit path, including exceptions. Start read-only unless writes are required.

## Related

- Reading/writing/managing a specific stream space: `stream-spaces.md`, [`examples/stream-spaces-read-write.md`](examples/stream-spaces-read-write.md).
- Listing streams, clearing a stream, locking, periodicity: `stream-management.md`, [`examples/connect-list-streams.md`](examples/connect-list-streams.md), [`examples/locking-and-clear-rewrite.md`](examples/locking-and-clear-rewrite.md).
- Discovering a schema from C++ itself or generic (schema-driven) decode: `schema-introspection.md`, [`examples/schema-introspection.md`](examples/schema-introspection.md).
- Hand-written typed message codecs for polymorphic dispatch without per-type inline calls: `message-types-and-decimal64.md` (Typed message codec), [`examples/polymorphic-read.md`](examples/polymorphic-read.md).
- In-place schema changes: `schema-evolution.md`, [`examples/schema-evolution.md`](examples/schema-evolution.md).
