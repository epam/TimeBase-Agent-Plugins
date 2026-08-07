---
name: timebase-cpp-client
description: Use when the user explicitly asks for TimeBase C++ client code, for example connecting to TimeBase from C++, reading/writing streams, dxapi library acquisition and CMake/vcxproj setup, or TimeBase C++ client debugging.
---

# TimeBase C++ Client

## Mission

Teach correct use of the TimeBase native C++ client: connection lifecycle, positional field access via `DataReader`/`DataWriter`, cursors and loaders. Prefer MCP-grounded stream and schema facts before generating code.

## Scope: Enterprise Edition only

This skill covers the Enterprise Edition (EE) dxapi client. Community Edition C++ is not yet supported by this skill. If a user asks specifically for a Community Edition C++ client, say so rather than improvising.

## When to use this skill

Use only when the user explicitly requests C++ together with TimeBase.

Typical tasks:

- connecting via `TickDb::createFromUrl` and resolving streams,
- reads/writes via `TickCursor`/`TickLoader` with positional `DataReader`/`DataWriter` field access,
- historical, live/resettable (`createCursor`/`reset`), or reverse cursor reads,
- hand-written typed message codecs for polymorphic/type-name-dispatched read and write,
- stream creation via `TickDb::createStream`, `TickDb::createFileStream`, or QQL DDL,
- topic publish/poll via `TopicDB`/`TickDirectLoader`/`TickMessagePoller`,
- stream spaces, listing/clearing/renaming/destructively-deleting streams, locking, periodicity, write buffering,
- dynamic resubscription on a live cursor, multiplexed cursors,
- schema introspection or generic (schema-driven) decode from C++,
- in-place schema changes via `TickStream::changeSchema`,
- bound/parameterized QQL execution or QQL validation via `compileQuery`,
- acquiring and linking the dxapi native library (Nexus tar.gz on Linux/macOS, NuGet package on Windows),
- `Decimal64`/DFP field conversions,
- debugging connection, linking, or build failures.

Do not use for pure QQL authoring with no C++ code to write (use the `qql-generator` skill instead) or for pure MCP discovery with no code to write.

## How to route requests

1. Confirm the user asked for C++ + TimeBase, not generic C++ help.
2. When stream names, schema, symbols, or time bounds matter, use MCP discovery first (`references/mcp-assisted-discovery.md`).
3. Detect how dxapi is already acquired in the target project (extracted archive on Linux/macOS, NuGet package or manually-vendored folder on Windows) and preserve it, don't move or re-derive it.
4. Before generating connection, stream, or cursor/loader code, verify the exact signature from the project's vendored dxapi headers (`references/project-setup.md`) rather than from memory.
5. Pick the smallest proven reference and example for the access pattern.
6. For library acquisition and build integration, use `references/project-setup.md`.

## Mandatory policy

- Ground stream keys and schema from MCP or user input. Do not invent field names, type names, or stream keys.
- dxapi has no generated/bound message classes for arbitrary schemas. `DataReader`/`DataWriter` field access is **positional**, in the exact order fields are declared in the schema, there is no name-based field lookup. Get the field order right from `get_stream_schema` before writing any read/write code.
- When QQL authoring is central, use the QQL generator skill first. Return here for C++ execution via `TickDb::executeQuery`.
- Never invent an exact Nexus/NuGet artifact version. Use whatever is already pinned in the project, or ask the user to confirm the current release. See `references/project-setup.md`.
- Use placeholder-based credentials (e.g. `NEXUS_USER`/`NEXUS_PASS`) for Nexus/NuGet feed access, and preserve any existing naming convention the project already uses. Never hardcode credentials.
- Keep `TickDb`, `TickCursor`, and `TickLoader` lifecycle explicit: wrap in `std::unique_ptr` and call `close()` on every exit path, including exceptions.
- Start read-only unless writes are required. Do not write to streams unless the user asked.
- Treat `TickStream::clear()`/`truncate()`/`purge()`/`deleteData()`/`deleteStream()`, `deleteSpaces`, `changeSchema`, and `TickDb::format()` as destructive/irreversible. Confirm intent with the user before generating a call to any of them.
- `LoadingOptions::writeMode` set to `REWRITE`/`TRUNCATE`/`REPLACE` is also destructive. A default-constructed `LoadingOptions()` already defaults `writeMode` to `REWRITE`, not `APPEND`, so always set `writeMode = WriteMode::APPEND` explicitly for an ordinary write. Confirm the intended mode with the user before generating loader setup for anything else.

## MCP-first workflow

When the task depends on live server context, follow the discovery order in [`references/mcp-assisted-discovery.md`](references/mcp-assisted-discovery.md) before generating field-access code. If MCP is unavailable, state what is missing and ask the user for stream/schema context before finalizing.

## Capability map

- [`references/workflow-selection.md`](references/workflow-selection.md): routing table
- [`references/mcp-assisted-discovery.md`](references/mcp-assisted-discovery.md): MCP discovery order
- [`references/project-setup.md`](references/project-setup.md): acquiring dxapi (Nexus archive, NuGet package), build integration, credentials, locating the right header for a given API
- [`references/connection-and-lifecycle.md`](references/connection-and-lifecycle.md): `TickDb::createFromUrl`, connection URI schemes, SSL and env vars, basic/OAuth2 auth, read-only mode, `format()`
- [`references/cursor-and-streams.md`](references/cursor-and-streams.md): `TickCursor`, `select`/`createCursor`, historical/live/reverse reads, stream creation (including `createFileStream`), multiplexed cursors, dynamic resubscription
- [`references/loader-writes.md`](references/loader-writes.md): `TickLoader`, the register/begin/write/send cycle
- [`references/message-types-and-decimal64.md`](references/message-types-and-decimal64.md): positional `DataReader`/`DataWriter` field access, nullable/array/ASCII/CHAR/enum/TimeOfDay/interval/compressed-datetime/UInt40 fields, `Decimal64`/DFP conversions, `MarketMessage` base fields, typed codec pattern
- [`references/stream-management.md`](references/stream-management.md): `listStreams`/`listEntities`/`listSymbols`, `InstrumentType`/`StreamScope`, `clear`/`truncate`/`purge`/`deleteData`/`deleteStream`, `renameInstruments`, locking, periodicity, write buffering, other `TickStream` accessors, `setSchema` vs `changeSchema`
- [`references/stream-spaces.md`](references/stream-spaces.md): reading/writing/managing stream spaces
- [`references/schema-introspection.md`](references/schema-introspection.md): parsing stream metadata, schema-driven generic decode
- [`references/schema-evolution.md`](references/schema-evolution.md): `TickStream::changeSchema`, tracking background processes
- [`references/qql-bound-queries.md`](references/qql-bound-queries.md): parameterized `executeQuery`, `compileQuery`
- [`references/topics.md`](references/topics.md): `TopicDB` publish/poll pub-sub
- [`references/debugging-and-performance.md`](references/debugging-and-performance.md): acquisition, linking, connection, and runtime failures, protocol-version mismatches, cursor/loader throughput stats and preloading, the cursor/loader exception hierarchy, topic publish/poll failures, schema change failures
