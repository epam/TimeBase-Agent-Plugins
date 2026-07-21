---
name: timebase-csharp-client
description: Use when the user explicitly asks for TimeBase C# or .NET client code, for example typed stream reads/writes, stream creation, bound QQL execution from C#, Deltix.Timebase package setup, or TimeBase .NET client debugging.
---

# TimeBase C# Client

## Mission

Teach correct use of the TimeBase .NET client API: connection lifecycle, schema and binding, cursors and loaders, and QQL execution from C#. Prefer MCP-grounded stream and schema facts before generating code.

## When to use this skill

Use only when the user explicitly requests C# or .NET together with TimeBase.

Typical tasks:

- typed reads/writes,
- stream creation with introspector or explicit schema,
- `ExecuteQuery` with bound result POCOs,
- `Deltix.Timebase.*` packages and feed setup,
- OAuth2 via `AccessToken` and MSAL,
- debugging binding, connection, or NuGet restore failures.

## How to route requests

1. Confirm the user asked for C#/.NET + TimeBase, not generic .NET help.
2. When stream names, schema, symbols, or time bounds matter, use MCP discovery first (`references/mcp-assisted-discovery.md`).
3. Detect the target project: preserve existing `.csproj` TFM and package style when present.
4. Before generating connection, stream, or cursor/loader code, verify the exact API shape from the target project's package metadata, local package docs or a compile probe.
5. Pick the smallest proven reference and example for the access pattern.
6. For project setup and build verification, use `references/project-setup-and-nuget.md`.

## Local API verification rules

- Do not invent interfaces, members, or overloads from memory when project metadata, package docs, or compile checks are available.
- If the API shape is still unclear after checking package docs and bundled references, use a small compile probe instead of guessing.

## Mandatory policy

- Ground stream keys and schema from MCP or user input. Do not invent field names, type names, or stream keys.
- Prefer built-in `Deltix.Timebase.Api.Messages` types when schema matches, do not invent custom POCOs unnecessarily.
- Use `TypeLoader` for custom bound types and QQL result POCOs.
- When QQL authoring is central, use the QQL generator skill first. Return here for C# execution and binding when the user supplies final QQL.
- Use placeholder-based credentials in `NuGet.config` and preserve any existing naming convention the project already uses. Never hardcode Nexus credentials. If restore fails with 401, report that the configured credentials are missing or incorrect.
- Keep `ITickDb` and cursor lifecycle explicit (`using` or `finally`).
- Start read-only unless writes are required. Do not write to streams unless the user asked.

## MCP-first workflow

When the task depends on live server context:

1. `get_server_configuration`
2. `list_streams`
3. `get_stream_schema`
4. `get_stream_time_range` and `get_stream_symbols` when needed
5. Generate C# using grounded names and types from those results

If MCP is unavailable, state what is missing and ask the user for stream/schema context before finalizing bound types.

## Capability map

- [`references/workflow-selection.md`](references/workflow-selection.md): routing table
- [`references/mcp-assisted-discovery.md`](references/mcp-assisted-discovery.md): MCP discovery order
- [`references/project-setup-and-nuget.md`](references/project-setup-and-nuget.md): packages, feed, credentials, verification
- [`references/message-types-and-schema.md`](references/message-types-and-schema.md): POCOs, introspector, `TypeLoader`
- [`references/cursor-and-streams.md`](references/cursor-and-streams.md): connect, select, cursors, live, reverse reads
- [`references/qql-bound-queries.md`](references/qql-bound-queries.md): `ExecuteQuery`, result POCOs
- [`references/authentication.md`](references/authentication.md): MSAL + `AccessToken`
- [`references/api-discovery.md`](references/api-discovery.md): API checks
- [`references/debugging-and-performance.md`](references/debugging-and-performance.md): NuGet, binding, auth failures
