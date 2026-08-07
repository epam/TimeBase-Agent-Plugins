# Loader Writes

Writing goes through `TickLoader`: register the message type, begin a message for an instrument/timestamp, write fields positionally through the returned `DataWriter`, then send.

## Basic write

`stream->createLoader(options)` returns a `TickLoader`. Register the message type, resolve the instrument id, then `beginMessage(typeId, entityId, timestamp)` (or `next(typeId, entityId, timestamp)`, both return the `DataWriter&` to fill in), write fields, `send()`, `close()`. See [`examples/read-write-bound.md`](examples/read-write-bound.md) for the full flow.

`beginMessage`/`next` also have an overload taking a symbol name and `InstrumentType` directly instead of a resolved `entityId`: `beginMessage(typeId, symbolName, instrumentType, timestamp)`, useful when the caller doesn't already have the id from `getInstrumentId`.

`beginMessage` has a further overload taking an explicit trailing `bool commitPrevious`. Both `beginMessage` overloads already cancel a still-open previous message by default, that trailing `bool` controls whether the pending message is committed (sent) instead of cancelled before starting the new one, get this wrong and a message the caller thought was sent gets silently dropped instead. Confirm which behavior the task actually needs rather than assuming the default cancel-on-begin is safe.

`loader->flush()` forces a just-committed message's buffered bytes out over the wire immediately, rather than waiting for the buffer to fill up naturally, use it when a downstream reader needs to see a message promptly. `loader->finish()` performs the same server-side finalization `close()` does (flushing, notifying the server, removing the loader from its pool) but leaves the loader's own internal write buffer allocated, `close()` calls `finish()` internally and then frees that buffer. Prefer `close()` for the normal exit-path case since it does both, call `finish()` directly only when the task specifically needs the loader finalized while keeping the object itself alive a little longer.

## Field order is positional

`DataWriter` has no name-based setter, fields must be written in the exact order they're declared in the schema. Get that order from `get_stream_schema` before writing this code, see `message-types-and-decimal64.md` for the full nullable-field and `Decimal64` conventions.

## Write modes

`LoadingOptions::writeMode` controls append vs overwrite (`APPEND`, `REPLACE`, `REWRITE`, `TRUNCATE`, `INSERT`). The default-constructed `LoadingOptions()` sets `writeMode` to `REWRITE`, not `APPEND`, so a loader created from a default-constructed `LoadingOptions` without explicitly setting `writeMode` is destructive by default. Always set `options.writeMode = WriteMode::APPEND` explicitly for an ordinary, non-destructive write, and confirm the intended mode with the user before generating loader setup for anything else, an unintended truncate/rewrite is destructive and not reversible.

`loader->stream() const` returns the `TickStream*` the loader was created against, useful when a helper function receives only the loader and needs the stream back (e.g. to read its schema or key) without threading a second parameter through.

## Other loading options

`LoadingOptions` also has: `raw` (bool, bypasses normal encoding for a pre-encoded byte stream, rarely needed), `minLatency` (bool, trade buffering depth for lower latency), `space` (nullable string, target a specific stream space, see `stream-spaces.md`), `minChunkSize`/`maxChunkSize` (data isn't written until `minChunkSize` accumulates in the buffer, and a chunk is never written larger than `maxChunkSize`), and `recvBufferSize`/`sendBufferSize` (socket buffer sizing). Leave these at their defaults unless the user has a specific throughput/latency constraint.

## Error and subscription listeners

`TickLoader::addListener`/`removeListener` take either an `ErrorListener` (`onError(errorClass, errorMsg)`) or a `SubscriptionListener` (notified of type/entity subscription changes), the same listener shape and lifetime rules `TickDirectLoader` uses for topics, see `topics.md` (Error and subscription listeners) for the full field list. Only wire these when the task needs to react to subscription churn or delivery errors, not by default.

## Error handling

Close the loader on every exit path, including exceptions, to flush buffered writes. Check for exceptions around `send()`/`close()` rather than assuming writes always succeed silently.
