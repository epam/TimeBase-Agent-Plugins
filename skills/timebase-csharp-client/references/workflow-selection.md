# Workflow Selection

Choose the narrowest TimeBase .NET client workflow.

| Need | Primary path | Load next |
| --- | --- | --- |
| Unknown streams, schema, symbols, time bounds | MCP discovery | `mcp-assisted-discovery.md` |
| NuGet or project setup | setup | `project-setup-and-nuget.md` |
| Integrate into existing project | preserve `.csproj` | `project-setup-and-nuget.md` |
| Bound read/write | typed cursor/loader | `cursor-and-streams.md`, [`examples/read-write-bound.md`](examples/read-write-bound.md) |
| Stream creation + loader writes | schema + loader | `message-types-and-schema.md`, [`examples/create-stream.md`](examples/create-stream.md) |
| QQL with bound .NET results | QQL bind | `qql-bound-queries.md`, [`examples/qql-query-result.md`](examples/qql-query-result.md) |
| C# that lists streams | connect fragment | [`examples/connect-list-streams.md`](examples/connect-list-streams.md) |
| Live cursor | live select | `cursor-and-streams.md`, [`examples/live-cursor.md`](examples/live-cursor.md) |
| OAuth2 | auth | `authentication.md` |
| Large local export | narrow + stream write | [`examples/large-export.md`](examples/large-export.md), `cursor-and-streams.md` |
| Schema inspection in C# | descriptors | [`examples/schema-introspection.md`](examples/schema-introspection.md) |
| Missing package or API uncertainty | setup + inspect | `project-setup-and-nuget.md`, `api-discovery.md` |
| Broken TimeBase client code | triage | `debugging-and-performance.md` |
