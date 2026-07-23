# Stream Management

Use this reference for stream creation and stream-level metadata.

## Stream creation

### Building `StreamOptions`

- `StreamOptions.polymorphic(scope, key, title, distributionFactor, descriptor1, descriptor2, ...)`: multiple message types in one stream. `StreamOptions`'s default (`polymorphic = true`), most streams carry more than one message type.
- `StreamOptions.fixedType(scope, key, title, distributionFactor, descriptor)`: one message type per stream. Use only when the stream is genuinely single-type.
- `new StreamOptions()` + `setMetaData(polymorphic, RecordClassSet)`: use it when the schema comes from a dynamically-collected `RecordClassSet` rather than descriptors you already have as literal values (e.g. recreating a stream from an imported file's own header, see [`import-export.md`](./import-export.md)).

### `StreamOptions` settings

- `scope`: `StreamScope.DURABLE` persists to disk. `StreamScope.TRANSIENT` is buffered, non-durable, and lower-latency, only choose `TRANSIENT` when the user explicitly wants ephemeral/low-latency semantics and accepts data loss on restart.
- `unique`/`duplicatesAllowed`: `unique = true` keeps an in-memory cache of the last message per primary key (fields annotated `@PrimaryKey`), new live subscribers get a snapshot of that cache at subscription start. `duplicatesAllowed` (default `true`) controls whether the loader ignores binary-similar messages, only meaningful when `unique` is set.
- `periodicity`: can be set here at creation time as a regularity hint.

### Creating the stream

- `db.createStream(key, options)`: single call, using a `StreamOptions` built above.
- `db.createStream(key, name, description, distributionFactor)` followed by `stream.setFixedType(descriptor)`/`stream.setPolymorphic(descriptors...)` on the returned stream: creates the stream immediately, unconfigured, the stream has no valid schema until the follow-up call.

See [`examples/create-stream.md`](examples/create-stream.md) for the full call.

## Stream metadata

Beyond reading message data, `stream.getStreamOptions()` exposes metadata: `options.periodicity`, etc., and `stream.getTimeRange()` / `stream.listEntities()` for the covered time span and distinct symbols. See [`examples/stream-metadata.md`](examples/stream-metadata.md).
