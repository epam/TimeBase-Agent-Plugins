# Cursor And Streams

Use direct cursors when ordering, typed messages, or incremental logic matters.

## Connect, resolve a stream, and select or write

Assumes an open `ITickDb` connection (see [`examples/connect-list-streams.md`](examples/connect-list-streams.md) for the connection bootstrap). For a resolved stream, typed read (with an entity/type filter) and typed write against it, see [`examples/read-write-bound.md`](examples/read-write-bound.md).

## Historical vs reverse reads

- **Historical**: start from a bounded timestamp (`DateTime.MinValue` for beginning, or a specific UTC time).
- **Reverse**: set `SelectionOptions.Reversed = true` and start from `DateTime.UtcNow` to walk backward.

## Resource lifecycle

- Prefer `using` for cursors and loaders.
- Start `readOnly: true` unless writes are required.

## Live cursors

Live consumption uses `SelectionOptions.Live = true` and `LiveCursorWatcher`. See [`examples/live-cursor.md`](examples/live-cursor.md). `LiveCursorWatcher` is not `IDisposable`. Call `watcher.Close()` and dispose the cursor separately on shutdown.

## Space-aware streams

Only generate space-specific selection or loading code when stream space support is confirmed via MCP, user context, or API discovery. Do not invent space names or APIs.
