# Symbol Mapping And Cross-Instance Sync

Use this reference for two related but distinct advanced tasks: remapping symbols while copying a stream, and synchronizing a target stream to match a source stream's newer data. See [`examples/symbol-mapping-and-sync.md`](examples/symbol-mapping-and-sync.md) for the code.

Examples use the Enterprise Edition `deltix.*` package root. See the package-root mapping and edition differences in [`project-setup.md`](project-setup.md#package-roots-in-this-skills-examples) before applying these examples to a Community Edition project.

## Copying a stream while remapping symbols (raw)

Copy every message from a source cursor to a target loader, replacing the symbol via a lookup map (e.g. loaded from a two-column CSV: old symbol to new symbol). This only works when the source and target schemas are equivalent, the raw message bytes (`data`/`offset`/`length`/`type`) are copied unchanged, only the symbol/timestamp are touched.

Prefer a reusable `CharSequenceKey` (from `deltix.util.collections`) over a plain `Map<CharSequence, String>` or a `.toString()`-based lookup for the per-message symbol lookup. It matches `String`-keyed map entries by content regardless of the concrete `CharSequence` implementation `getSymbol()` returns, and reuses one key object for the whole loop instead of allocating a `String` per message, exactly what a bulk stream-copy loop needs.

Create the target stream by copying the source's `StreamOptions` (so the schema matches exactly) rather than redefining it.

## Synchronizing a target stream from a source

To bring a target stream up to date with a source stream (copy only the missing tail, per instrument), use the per-instrument time range overload `long[] getTimeRange(InstrumentIdentity id)` (in addition to the whole-stream `getTimeRange()`). Compute the earliest point that needs replaying across all instruments, then replay from there via `createCursor(null)` + `reset(...)` + `subscribeToAllEntities()`.

This assumes no retroactive corrections in the source after the target's last-known point, and that the source stream isn't being concurrently appended to during the sync. Both are real limitations of this simple "assume append-only" approach, not something to paper over silently if the user's scenario doesn't hold.

## Common mistakes

- Copying raw messages between streams with different schemas. `outMsg.type = inMsg.type` requires the source and target class descriptors to match, don't use this for cross-schema copies (use `import-export.md`'s `SchemaConverter` path instead).
- Recomputing a target stream's schema by hand when it should just be copied from the source stream's `StreamOptions`.
- Assuming `getTimeRange()` (whole-stream) is enough for a per-instrument sync decision, use the per-instrument `getTimeRange(id)` overload instead.
- Calling `.toString()` on a `CharSequence` message field (like `getSymbol()`) just to look it up in a `String`-keyed map. This allocates a `String` per message in what's typically a bulk copy loop, use a reusable `CharSequenceKey` instead.
