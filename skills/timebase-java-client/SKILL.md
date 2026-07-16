---
name: timebase-java-client
description: Use when user explicitly asks for TimeBase Java client code, for example typed stream reads/writes, stream creation, bound QQL execution from Java, deltix-timebase-client Maven/Gradle setup, or TimeBase Java client debugging.
---

# TimeBase Java Client

## Mission

Teach correct use of the TimeBase Java client API: connection lifecycle, schema and binding, cursors and loaders, and QQL execution from Java. Prefer MCP-grounded stream and schema facts before generating code.

## When to use this skill

Use only when the user explicitly requests Java together with TimeBase.

Typical tasks:

- reads/writes via `TickLoader`/`TickCursor`,
- stream creation with `Introspector` or explicit `RecordClassDescriptor`,
- `executeQuery` with bound result POJOs,
- `deltix-timebase-client` Maven/Gradle setup,
- OAuth2 connection setup,
- debugging binding, connection, or build/dependency-resolution failures.

Do not use for pure QQL authoring with no Java binding (use the `qql-generator` skill instead) or for pure MCP discovery with no code to write.

## How to route requests

1. Confirm the user asked for Java + TimeBase, not generic Java help.
2. When stream names, schema, symbols, or time bounds matter, use MCP discovery first (`references/mcp-assisted-discovery.md`).
3. Detect the target project: Maven (`pom.xml`) or Gradle (`build.gradle`/`build.gradle.kts`); preserve its existing Java version and dependency-management style.
4. Before generating connection, stream, or cursor/loader code, verify the exact API shape from the target project's dependency sources/javadoc or a compile probe.
5. Pick the smallest proven reference and example for the access pattern.
6. For project setup and build verification, use `references/project-setup-and-maven-gradle.md`.

## Local API verification rules

- Do not invent interfaces, members, or overloads from memory when dependency sources, javadoc, or compile checks are available.
- If the API shape is still unclear after checking bundled references, use a small compile probe instead of guessing.

## Mandatory policy

- Ground stream keys and schema from MCP or user input. Do not invent field names, type names, or stream keys.
- Prefer built-in `deltix-timebase-api-messages` types (e.g. `BarMessage`, `TradeMessage`, `BestBidOfferMessage`) when schema matches; do not invent custom POJOs unnecessarily.
- When QQL authoring is central, use the QQL generator skill first. Return here for Java execution and binding when the user supplies final QQL.
- Prefer QQL text with embedded subscription (stream union, symbol filter, time filter) over the deprecated `executeQuery` overloads that take explicit stream/entity/time-range arrays.
- Use placeholder-based credentials for repository access and preserve any existing naming convention the project already uses. Never hardcode repository credentials. If dependency resolution fails with 401/403, report that the configured credentials are missing or incorrect.
- Keep `DXTickDB`, `TickCursor`, and `TickLoader` lifecycle explicit (try-with-resources).
- Start read-only unless writes are required. Do not write to streams unless the user asked.

## MCP-first workflow

When the task depends on live server context:

1. `get_server_configuration`
2. `list_streams`
3. `get_stream_schema`
4. `get_stream_time_range` and `get_stream_symbols` when needed
5. Generate Java using grounded names and types from those results

If MCP is unavailable, state what is missing and ask the user for stream/schema context before finalizing bound types.

## Capability map

- [`references/workflow-selection.md`](references/workflow-selection.md): routing table
- [`references/mcp-assisted-discovery.md`](references/mcp-assisted-discovery.md): MCP discovery order
- [`references/project-setup-and-maven-gradle.md`](references/project-setup-and-maven-gradle.md): dependencies, repository, credentials, verification
- [`references/message-types-and-schema.md`](references/message-types-and-schema.md): POJOs, introspector, schema types
- [`references/cursor-and-streams.md`](references/cursor-and-streams.md): connect, select/cursor filters, loader writes, live and reversed reads, multi-stream select
- [`references/stream-management.md`](references/stream-management.md): stream creation, stream metadata, dynamic resubscription, per-instrument stateful processing
- [`references/qql-execution-from-java.md`](references/qql-execution-from-java.md): `executeQuery`, bind parameters, embedded subscription
- [`references/schema-evolution.md`](references/schema-evolution.md): schema change analysis and application (advanced)
- [`references/locking-and-securities-update.md`](references/locking-and-securities-update.md): stream locking, no-in-place-update rewrite pattern (advanced)
- [`references/stream-spaces.md`](references/stream-spaces.md): reading/writing named stream partitions (advanced)
- [`references/import-export.md`](references/import-export.md): bulk file archive export/import (advanced)
- [`references/symbol-mapping-and-sync.md`](references/symbol-mapping-and-sync.md): stream copy with symbol remapping, cross-instance sync (advanced)
- [`references/array-fields-and-codecs.md`](references/array-fields-and-codecs.md): raw array-typed fields, custom debug printing (advanced)
- [`references/topics.md`](references/topics.md): low-latency pub/sub as an alternative to durable streams (advanced)
- [`references/authentication.md`](references/authentication.md): OAuth2 connection setup
- [`references/api-discovery.md`](references/api-discovery.md): API checks
- [`references/debugging-and-performance.md`](references/debugging-and-performance.md): build, connection, binding, and throughput failures
