# Workflow Selection

Choose the narrowest TimeBase C++ (dxapi) workflow.

| Need | Primary path | Load next |
| --- | --- | --- |
| Unknown streams, schema, symbols, time bounds | MCP discovery | `mcp-assisted-discovery.md` |
| Acquiring/linking dxapi, Nexus archive or NuGet setup | setup | `project-setup.md` |
| Integrate into existing project | preserve build system | `project-setup.md` |
| Connect to TimeBase, list streams | `TickDb::createFromUrl` | `connection-and-lifecycle.md`, [`examples/connect-list-streams.md`](examples/connect-list-streams.md) |
| Historical read, bound write | `TickCursor`/`TickLoader` | `cursor-and-streams.md`, `loader-writes.md`, [`examples/read-write-bound.md`](examples/read-write-bound.md) |
| Live or resettable read | `createCursor`/`reset` | `cursor-and-streams.md`, [`examples/live-cursor.md`](examples/live-cursor.md) |
| Changing a live cursor's subscribed entities/types mid-poll | `addEntity`/`removeEntity`/`subscribeToAll*` | `cursor-and-streams.md`, [`examples/dynamic-resubscription.md`](examples/dynamic-resubscription.md) |
| Merged read across streams/entities by a mux config | `createMultiplexedCursor` | `cursor-and-streams.md` |
| Stream creation, including from an external data file | `TickDb::createStream`, `createFileStream`, or QQL DDL | `cursor-and-streams.md`, [`examples/create-stream.md`](examples/create-stream.md) |
| Positional field access, `Decimal64`/DFP conversions, nullable fields, array fields | `DataReader`/`DataWriter` | `message-types-and-decimal64.md` |
| Polymorphic read of a fixed schema | hand-written typed codec (type-name dispatch, or GUID-checked dispatcher) | `message-types-and-decimal64.md`, [`examples/polymorphic-read.md`](examples/polymorphic-read.md) |
| Listing/clearing/renaming streams, destructive stream/DB ops, locking, periodicity, buffering | `TickStream`/`TickDb` operations | `stream-management.md`, `connection-and-lifecycle.md`, [`examples/connect-list-streams.md`](examples/connect-list-streams.md), [`examples/locking-and-clear-rewrite.md`](examples/locking-and-clear-rewrite.md) |
| Reading/writing/managing a stream space | `space`/`spaces` | `stream-spaces.md`, [`examples/stream-spaces-read-write.md`](examples/stream-spaces-read-write.md) |
| Discovering schema from C++, generic decode | `metadata()`/`GenericCodec` | `schema-introspection.md`, [`examples/schema-introspection.md`](examples/schema-introspection.md) |
| In-place schema change | `changeSchema` | `schema-evolution.md`, [`examples/schema-evolution.md`](examples/schema-evolution.md) |
| Parameterized QQL, QQL validation | `QueryParameter`/`compileQuery` | `qql-bound-queries.md`, [`examples/qql-query-result.md`](examples/qql-query-result.md) |
| Topic publish/poll | `TopicDB` | `topics.md`, [`examples/topics-pubsub.md`](examples/topics-pubsub.md) |
| Missing library or API uncertainty | setup + inspect | `project-setup.md` |
| Broken TimeBase C++ code | triage | `debugging-and-performance.md` |
