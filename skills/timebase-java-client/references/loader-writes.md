# Loader Writes

Use this reference for writing to a stream.

## Default vs configured

`stream.createLoader()` is the plain-defaults path. See [`examples/loader-writes.md`](examples/loader-writes.md) for a basic write.

Use `stream.createLoader(LoadingOptions)` when you need to control write behavior explicitly.

## Write mode

`LoadingOptions.writeMode` picks truncation behavior based on whether you're streaming forward, backfilling, or correcting:

- `REWRITE` (**default**): truncates the stream at the timestamp of the first incoming message, so incoming data overwrites whatever previously occupied that time range onward.
- `REPLACE` (**Enterprise Edition only**, not in Community Edition's `WriteMode`): like `REWRITE`, but truncates starting just after the first incoming message's timestamp, so a message already recorded at that exact timestamp is kept instead of overwritten.
- `APPEND`: only messages with timestamps not older than the last recorded message timestamp are written, older messages are skipped. Use for pure forward streaming where out-of-order data should be dropped, not overwrite history.
- `TRUNCATE`: like `REWRITE` but re-evaluated per message, the stream truncates further whenever a later incoming message is older than what's already been written.
- `INSERT`: messages are written without any truncation. Use when you specifically need to interleave data without discarding anything.

`LoadingOptions(raw, writeMode)` is the constructor, set `raw = true` when writing a custom schema with no bound Java class (see [`message-types-and-schema.md`](message-types-and-schema.md)).

## Other options

- `LoadingOptions.channelPerformance` / `channelQOS`: tune for low-latency vs high-throughput write patterns when the default isn't fast enough.
- `LoadingOptions.filterExpression`: a QQL expression that filters which messages actually get sent, rather than filtering in application code before calling `loader.send(...)`.
- `LoadingOptions.addErrorAction(LoadingError.class, LoadingOptions.ErrorAction.NotifyAndAbort)`: configure how malformed-message errors are handled at the options level. Possible `ErrorAction` values: `NotifyAndContinue`, `NotifyAndAbort`, `Continue`.
- `loader.addEventListener(...)` / `loader.removeEventListener(...)`: track loader events after the loader is created, e.g. a `LoadingErrorListener` to log per-message load failures instead of letting them fail silently. See [`examples/loader-writes.md`](examples/loader-writes.md).
- `loader.flush()`: synchronously force written data to disk instead of waiting for the next automatic flush. Declares a checked `IOException`, catch it or add it to the enclosing method's `throws` clause.

Reuse a single message instance across a high-throughput loading loop instead of allocating one per message.
