# Cursor And Streams

Use direct cursors when ordering, typed messages, or incremental logic matters. For stream creation, metadata, dynamic resubscription, and per-instrument stateful processing, see `stream-management.md`.

## Connection bootstrap: pick the right entry point

`TickDBFactory` exposes several ways to obtain a `DXTickDB`. They are not interchangeable conveniences — each fits a different situation:

| Entry point | Use when |
| --- | --- |
| `TickDBFactory.createFromUrl(url)` | Default choice. URL carries scheme/host/port and optionally embedded auth query params. |
| `TickDBFactory.createFromUrl(url, user, pass)` | Same as above, with explicit basic-auth credentials instead of embedding them in the URL. |
| `TickDBFactory.connect(host, port, enableSSL)` / `connect(host, port, enableSSL, user, pass)` | Building the connection from discrete host/port/SSL fields rather than a URL string (e.g. values come from separate config keys). Returns `RemoteTickDB` directly. |
| `TickDBFactory.openFromUrl(url, readOnly)` | Combines `createFromUrl` + `open` in one call when you don't need to touch the `DXTickDB` before opening it. |
| `TickDBFactory.create(File... paths)` | Embedded/local DB over on-disk files, no remote server involved — rare outside of standalone tools/tests. |

Avoid the no-SSL, no-auth overloads (`connect(host, port)`, `open(host, port, readOnly)`): they are deprecated in favor of the SSL/auth-capable overloads above, even when the target server has no auth configured.

```java
import deltix.qsrv.hf.tickdb.pub.DXTickDB;
import deltix.qsrv.hf.tickdb.pub.TickDBFactory;

try (DXTickDB db = TickDBFactory.createFromUrl(connectionUrl)) {
    db.open(true); // readOnly
    // use db
}
```

Use `dxtick://host:port` for plain connections and `dstick://host:port` for SSL.

## Resolve stream and read: two subscription models

There are two ways to read from a stream, and they solve different problems — don't default to one without checking which the task needs.

**`stream.select(...)` — fixed subscription for the cursor's lifetime.** Simplest choice when the set of types/entities to read is known up front and won't change. `select` takes two independent filters, not one:

- **`String[] types`** — which message types to include, by fully qualified class name (e.g. `BarMessage.class.getName()`). `null` means all types.
- **`entities`** — which instruments/symbols to include. `null` means all entities. This has two argument-type options (see below), but either way it is a separate filter axis from `types`.

```java
import deltix.qsrv.hf.tickdb.pub.*;
import deltix.qsrv.hf.pub.*;

DXTickStream stream = db.getStream(streamKey);
if (stream == null) {
    System.out.println("Stream '" + streamKey + "' not found.");
    return;
}

String[] types = { BarMessage.class.getName() }; // type filter
String[] symbols = { "AAPL" };                    // entity filter, simplest form

SelectionOptions options = new SelectionOptions();
options.raw = false;

try (TickCursor cursor = stream.select(Long.MIN_VALUE, options, types, symbols)) {
    while (cursor.next()) {
        InstrumentMessage msg = cursor.getMessage();
        System.out.println(msg);
    }
}
```

For the entity filter, `select` has two overloads: one taking `CharSequence[]` (plain symbol strings, as above — `String[]` matches this), and one taking `InstrumentIdentity[]` (symbol + `InstrumentType` pairs, constructed as `new InstrumentKey(InstrumentType.EQUITY, "AAPL")` — `InstrumentKey` is the concrete class; `InstrumentIdentity` is the interface type used for parameters/arrays/`listEntities()` results). Use `InstrumentIdentity[]` only when the stream mixes instrument types and the symbol alone is ambiguous; otherwise the plain symbol array is simpler and matches what most existing code already does. Either way, both are alternatives for the entity filter only — `types` stays a separate `String[]` argument regardless of which entity-filter form is used.

**Null-argument ambiguity**: because `InstrumentIdentity[]` and `CharSequence[]` are two different overloads for the same entity-filter slot, passing a bare `null` literal there is ambiguous to the Java compiler and won't compile. When you want "no entity filter" (all entities), don't pass `null` for that argument — use the shorter overload that omits it entirely (e.g. `stream.select(time, options, types)` instead of `stream.select(time, options, types, null)`). Only if a specific overload must be forced for some other reason (e.g. matching an existing call site), disambiguate with an explicit cast such as `(CharSequence[]) null`.

**`stream.createCursor(options)` + subscription-controller methods — subscription can change while the cursor is open.** Use this when the set of symbols/types to follow needs to grow or shrink at runtime (e.g. a watchlist the user edits live), since it avoids tearing down and rebuilding the cursor:

```java
try (TickCursor cursor = stream.createCursor(new SelectionOptions())) {
    cursor.subscribeToAllTypes();
    cursor.addEntity(new InstrumentKey(InstrumentType.EQUITY, "AAPL"));
    cursor.reset(Long.MIN_VALUE);

    while (cursor.next()) {
        // ...
        // later, in response to a user action:
        // cursor.addEntity(new InstrumentKey(InstrumentType.EQUITY, "MSFT"));
        // cursor.removeEntity(new InstrumentKey(InstrumentType.EQUITY, "AAPL"));
    }
}
```

Only reach for `createCursor` + mutators when the subscription genuinely needs to change after the cursor is created — for a static read, `select(...)` is shorter and equally correct. See `stream-management.md` for the full list of subscription-controller mutator methods.

## Selecting across multiple streams at once

`DXTickDB` itself exposes a `select(startTimestamp, selectionOptions, types, entities, streams...)` overload that reads a merged, time-ordered view across several named streams without a QQL `UNION`. Use it when the task is "read these N streams together" and QQL isn't otherwise needed:

```java
try (TickCursor cursor = db.select(Long.MIN_VALUE, new SelectionOptions(), streamA, streamB)) {
    while (cursor.next()) {
        InstrumentMessage msg = cursor.getMessage();
    }
}
```

When both the type and entity filters are `null` (as here), use the overload that drops both rather than passing `null, null` — see the note on null-argument ambiguity above.

If the task already needs QQL for filtering/aggregation, prefer expressing the stream union in QQL text instead (see `qql-execution-from-java.md`) rather than mixing both mechanisms.

## Loader write: default vs configured

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

`stream.createLoader()` is the plain-defaults path. Beyond `setTimeStampMs(long)`, messages also expose `setNanoTime`/`getNanoTime` for sub-millisecond precision — only use it when the task specifically needs finer-than-millisecond timestamp resolution.

Use `stream.createLoader(LoadingOptions)` when you need to control write behavior explicitly:

- `LoadingOptions.writeMode` — pick based on whether you're streaming forward, backfilling, or correcting:
  - `REWRITE` (**default**) — the stream is truncated at the timestamp of the first incoming message, so incoming data overwrites whatever previously occupied that time range onward.
  - `APPEND` — only messages with timestamps not older than the last recorded message timestamp are written; older messages are silently skipped. Use for pure forward streaming where out-of-order data should be dropped, not overwrite history.
  - `TRUNCATE` — like `REWRITE` but re-evaluated per message: the stream truncates further whenever a later incoming message is still older than what's already been written.
  - `INSERT` — messages are written without any truncation. Use when you specifically need to interleave data without discarding anything.
- `LoadingOptions(raw, writeMode)` — set `raw = true` when writing a custom schema with no bound Java class (see `message-types-and-schema.md`). This is the only current (non-deprecated) constructor — the no-arg `LoadingOptions()`, single-arg `LoadingOptions(raw)`, and `LoadingOptions(writeMode)` constructors are deprecated; use the two-arg form even when one of the values would be a default.
- `LoadingOptions.channelPerformance` / `channelQOS` — tune for low-latency vs high-throughput write patterns when the default isn't fast enough.
- `LoadingOptions.addErrorAction(LoadingError.class, LoadingOptions.ErrorAction.NotifyAndAbort)` — configure how malformed-message errors are handled at the options level.
- `loader.addEventListener(...)` / `loader.removeEventListener(...)` — track loader events after the loader is created, e.g. a `LoadingErrorListener` to log per-message load failures instead of letting them fail silently:

  ```java
  loader.addEventListener(new LoadingErrorListener() {
      @Override
      public void onError(LoadingError e) {
          System.out.println("Loading error: " + e.getMessage());
      }
  });
  ```
- `loader.flush()` — synchronously force written data to disk instead of waiting for the next automatic flush; use before a hard dependency on durability (e.g. right before reporting success to a caller). It declares a checked `IOException` — catch it or add it to the enclosing method's `throws` clause.

Reuse a single message instance across a high-throughput loading loop instead of allocating one per message.

## Historical vs reverse reads

- **Historical**: start from a bounded timestamp (`Long.MIN_VALUE` for the beginning, or a specific epoch millis value).
- **Reverse**: set `SelectionOptions.reversed = true` and start from "now" to walk backward — useful for "latest value per instrument" queries (see the worked pattern in `stream-management.md`).

## Resource lifecycle

- Prefer try-with-resources for `DXTickDB`, `TickCursor`, and `TickLoader`.
- Start `db.open(true)` (read-only) unless writes are required.
- All read methods on a given `TickCursor`/`InstrumentMessageSource` (`next()`, `getMessage()`) must be called from a single thread; only `close()` and subscription-control methods are safe to call concurrently.

## Live cursors

Live consumption uses `SelectionOptions.live = true`. See [`examples/live-cursor.md`](examples/live-cursor.md). When combining historical replay with live tailing, set `SelectionOptions.realTimeNotification = true` to receive a `RealTimeStartMessage` marker at the point where the cursor transitions from historical to live data.
