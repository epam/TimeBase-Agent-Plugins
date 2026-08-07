# Stream Management

Use this reference for stream creation, metadata, lifecycle, and data-removal operations.

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

- `stream.getTimeRange(entities...)` / `stream.listTimeRange(entities...)`: covered time span, `getTimeRange` returns a `long[2]` (start/end), `listTimeRange` returns a `TimeInterval[]` when the range isn't a single contiguous span.
- `stream.listEntities()`: distinct symbols/entities in the stream.
- `stream.getPolymorphicDescriptors()` / `stream.getAllDescriptors()`: schema descriptors for a polymorphic stream, alongside the already-covered `stream.getFixedType()` for a fixed-type stream. See `message-types-and-schema.md`.
- Post-creation getters/setters, change stream properties without recreating it:

| Property | Getter/setter |
| --- | --- |
| Name | `setName(key)` |
| Description | `setDescription(text)` |
| Owner | `getOwner()` / `setOwner(owner)` |
| Scope | `getScope()` (read-only after creation) |
| Distribution factor | `getDistributionFactor()` / `setTargetNumFiles(n)` |
| Periodicity | `getPeriodicity()` / `setPeriodicity(p)` |
| High availability | `getHighAvailability()` / `setHighAvailability(bool)` |

`stream.getStreamOptions()` also exposes the full `StreamOptions` object used at creation. See [`examples/stream-metadata.md`](examples/stream-metadata.md).

## Stream lifecycle

- `stream.rename(key)`: renames the stream itself.
- `stream.delete()`: deletes the whole stream object, including all its data and schema, this is destructive and not reversible. This is a different method from `stream.delete(from, to, ids...)`, same name, different interface, completely different blast radius, don't confuse them. Confirm with the user before calling the no-arg `delete()`.
- Background stream tasks (schema changes, or any other `TransformationTask`) run via `stream.execute(...)`, `stream.getBackgroundProcess()`, and `stream.abortBackgroundProcess()` to cancel one in progress, see `schema-evolution.md` for the full pattern.

## Data removal

`WritableTickStream` (extended by `DXTickStream`) exposes four data-mutation methods that remove existing data without touching the stream object itself, pick the narrowest one that fits:

| Method | What it does |
| --- | --- |
| `delete(TimeStamp from, TimeStamp to, InstrumentIdentity... ids)` | Deletes data in the inclusive `[from, to]` time range, filtered by entity. Omitting `ids` deletes that range across every entity in the stream. **Not the same method as `stream.delete()` above**, this one removes data, that one removes the stream. |
| `truncate(long time, InstrumentIdentity... ids)` | Deletes everything from `time` to the end of the stream for the given entities, keeps everything before `time`. |
| `clear(InstrumentIdentity... ids)` | Wipes all data for the given entities. An empty call clears every entity, see `locking-and-securities-update.md` for the bulk reference-data rewrite idiom built on this. |
| `purge(long time[, String space])` | Deletes everything older than `time`, the opposite direction from `truncate`. |

### Replacing or removing a single message at a known timestamp

Delete the exact instant for that entity, then send the replacement through a normal loader, no need to read the stream into memory or rewrite anything else. Build the delete range from the target message's own `getTimeStampNs()` via `TimeStamp.fromNanoseconds(...)`, not a millisecond-truncated value, TimeBase's native precision is nanoseconds and a message can carry a sub-millisecond component that `TimeStamp.fromMilliseconds(...)` would lose, causing the range to miss it. Only use `fromMilliseconds(...)` when the caller genuinely has no nanosecond value to work with. See [`examples/delete-and-replace-message.md`](examples/delete-and-replace-message.md) for the full runnable pattern.

**Important**: `delete` operates on a time range, not a record identity. If the entity has more than one message at the exact same timestamp, an inclusive `[t, t]` delete removes all of them, not just one. If duplicate timestamps are possible for this stream, confirm with the user how they want that handled before deleting.

## Common mistakes

- Confusing `stream.delete()` (removes the whole stream) with `stream.delete(from, to, ids)` (removes a data range), same method name, very different consequences.
- Reading the whole stream into memory, truncating, and rewriting everything back just to replace one message, use `delete` on a narrow range plus a loader send instead.
- Calling `clear()` or `truncate()` when only a specific time range needed to change, both are broader than a targeted `delete`.
- Assuming `delete([t, t], entity)` only removes one record when duplicate timestamps exist for that entity.
- Forgetting the entity filter on `delete`/`truncate`/`clear`, omitting `ids` affects every entity in the stream.
- Calling `stream.delete()` without explicit user confirmation, it's not reversible.
