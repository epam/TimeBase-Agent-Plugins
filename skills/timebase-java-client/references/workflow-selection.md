# Workflow Selection

Choose the narrowest TimeBase Java client workflow.

| Need | Primary path | Load next |
| --- | --- | --- |
| Unknown streams, schema, symbols, time bounds | MCP discovery | `mcp-assisted-discovery.md` |
| Maven/Gradle or project setup | setup | `project-setup.md` |
| Integrate into existing project | preserve `pom.xml`/`build.gradle` | `project-setup.md` |
| Bound read | typed cursor | `cursor-and-streams.md`, [`examples/read-write-bound.md`](examples/read-write-bound.md) |
| Bound write | typed loader | `loader-writes.md`, [`examples/loader-writes.md`](examples/loader-writes.md), [`examples/read-write-bound.md`](examples/read-write-bound.md) |
| Custom/dynamic schema read or write | raw mode | `message-types-and-schema.md`, [`examples/read-write-raw-custom-schema.md`](examples/read-write-raw-custom-schema.md) |
| Stream creation | schema + factory | `message-types-and-schema.md`, `stream-management.md`, [`examples/create-stream.md`](examples/create-stream.md) |
| QQL with bound Java results | QQL bind | `qql-execution-from-java.md`, [`examples/qql-query-result.md`](examples/qql-query-result.md) |
| Java that lists streams | connect fragment | [`examples/connect-list-streams.md`](examples/connect-list-streams.md) |
| Live cursor | live select | `cursor-and-streams.md`, [`examples/live-cursor.md`](examples/live-cursor.md) |
| OAuth2 | auth | `authentication.md` |
| Adding a field to an existing stream | schema change | `schema-evolution.md`, [`examples/schema-evolution.md`](examples/schema-evolution.md) |
| Schema inspection in Java | descriptors | [`examples/schema-introspection.md`](examples/schema-introspection.md) |
| Surviving mid-session server disconnects | reconnect handling | `debugging-and-performance.md`, [`examples/reconnect-handling.md`](examples/reconnect-handling.md) |
| Bulk-updating a reference-data stream (e.g. securities) | lock + clear + rewrite | `locking-and-securities-update.md`, [`examples/locking-and-clear-rewrite.md`](examples/locking-and-clear-rewrite.md) |
| Stream partitioned into named spaces | space-scoped read/write | `stream-spaces.md`, [`examples/stream-spaces-read-write.md`](examples/stream-spaces-read-write.md) |
| Bulk file export/import of a stream | archive read/write | `import-export.md`, [`examples/export-import-file.md`](examples/export-import-file.md) |
| Copying a stream while remapping symbols, or syncing two instances | symbol map / sync | `symbol-mapping-and-sync.md`, [`examples/symbol-mapping-and-sync.md`](examples/symbol-mapping-and-sync.md) |
| Custom schema with an array-typed field | array codec | `array-fields-and-codecs.md`, [`examples/array-fields.md`](examples/array-fields.md) |
| Low-latency pub/sub instead of a durable stream | Topics | `topics.md`, [`examples/topics-pubsub.md`](examples/topics-pubsub.md) |
| Dynamic cursor resubscription (add/remove entities mid-stream) | subscription controllers | `cursor-and-streams.md`, [`examples/dynamic-resubscription.md`](examples/dynamic-resubscription.md) |
| Stream metadata (periodicity, time range, entities) | stream management | `stream-management.md`, [`examples/stream-metadata.md`](examples/stream-metadata.md) |
| Missing dependency or API uncertainty | setup + inspect | `project-setup.md`, `api-discovery.md` |
| Broken TimeBase client code | triage | `debugging-and-performance.md` |
