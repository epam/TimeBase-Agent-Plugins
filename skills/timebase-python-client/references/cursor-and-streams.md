# Cursor And Streams

Use direct cursors when ordering, polymorphism, live consumption, or incremental logic matters.

## Best-fit cases

- Live or near-live subscriptions
- Polymorphic streams with multiple message types
- Incremental state machines such as order book maintenance
- Code paths that need exact message objects instead of a flattened table

## Core pattern

1. Open `TickDb` in read-only mode unless writing is required.
2. Resolve the target stream.
3. Use `stream.trySelect(...)` or `db.trySelect(...)` with explicit options, types, entities, and start time for the initial subscription.
4. Iterate messages and branch on confirmed `typeName` values or schema-backed fields.
5. Use `createCursor(...)` plus `addStreams(...)`, `addEntities(...)`, `addTypes(...)`, and `reset(...)` only when the task truly needs dynamic subscription changes after cursor creation.
6. Close the cursor and database explicitly if `with` blocks are not available.

Do not use a cursor example as the routing default for discovery or simple bounded results that MCP or QQL can answer directly. A simple read is still a valid Python path when the expected result set is large enough that it should be streamed to a local file or processed outside model context.

For explicit Python requests, start from `examples/read-stream.py` as a simple bounded-read script reference or as a base for richer cursor logic, `examples/polymorphic-read.py` for multi-type subscriptions, `examples/read-universal-stream.py` for package entries, `examples/multithread-read.py` for threaded readers, and `examples/multiplexed-cursor.py` for mixed feeds when support is confirmed.

## When this is better than pandas

- You need message-specific branching by `typeName`.
- The payload contains nested objects or package entries.
- The task reacts to messages incrementally.
- The user wants custom logic that is hard to express as a rectangular DataFrame.

Prefer `trySelect` as the default read pattern. The empty-subscription `createCursor(...)` workflow is for the cases where the subscription must be assembled or reconfigured incrementally after the cursor already exists.

## Historical vs live

- Historical reads should use a bounded reset timestamp.
- Live reads should set expectations about unbounded execution and shutdown behavior.
- Avoid turning live streams into DataFrames until the user has a bounded buffering strategy.
- If live semantics matter and you do not know the stream behavior, do not invent it.

## Space-aware streams

- Confirm that the target stream actually supports spaces before generating space-specific code.
- For cursor reads that should target one space expression, set `options.space` on `SelectionOptions`.
- For cursor reads that should target an explicit list of spaces, call `options.withSpaces([...])`.
- Use `stream.listSpaces()` when the workflow depends on known existing spaces and live server context is available.
- For loader writes into a specific space, set `LoadingOptions.space` before calling `stream.tryLoader(...)` or `db.tryLoader(...)`.
- Stream-level partition management can use `listSpaces()`, `renameSpace(...)`, and `deleteSpaces(...)`, but only emit those calls when the user explicitly asked for space management and stream support is confirmed.
- Keep space filters narrow and do not invent space names when MCP or user-provided context can confirm them.

## Schema-dependent logic

- Inspect schema first for polymorphic streams, array fields, or object fields.
- Use `examples/schema-introspection.py` before writing type-specific logic if the user did not provide schema details.
- If MCP is available, prefer MCP schema discovery before hardcoding field assumptions.

## Threading and resource rules

- Prefer one database handle per worker when the workflow uses parallel readers.
- Do not share mutable cursor state across threads.
- Keep per-thread subscriptions narrow.
- Surface any uncertainty around thread safety when exact library version behavior is unknown.

## When not to use cursors

- When the user only needs a small, tabular, historical slice for plotting or export
- When QQL can reduce the data volume substantially before Python sees it