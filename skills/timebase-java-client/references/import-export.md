# Import/Export (Bulk File Archives)

Use this reference for bulk-exporting a stream's data to a local file (or importing it back), as opposed to routine reads/writes through cursors and loaders. This is a comparatively rare, heavier-weight operation — don't reach for it unless the task specifically asks for a file-based export/import or backup. See [`examples/export-import-file.md`](examples/export-import-file.md) for the full code.

## Creating a new stream from a file's own schema

When importing into a brand-new stream (as opposed to an existing one), read the file's header to recover its schema, collect the descriptors into a `RecordClassSet`, and build `StreamOptions` from that set directly with `setMetaData(...)` rather than naming a specific descriptor. This is a fourth stream-creation path alongside the three in `stream-management.md` (`fixedType`/`polymorphic`/two-step `createStream`+`setFixedType`) — use it specifically when the schema comes from a dynamically-collected `RecordClassSet` (e.g. recovered from a file) rather than from descriptors you already have as literal values.

## Export to a single message file

Export always reads in raw mode (`SelectionOptions(true, false)`) and writes `RawMessage` directly via `MessageWriter2` — no bound decoding needed since the writer persists the wire format as-is.

## Export to a per-space zip archive

When a stream has multiple spaces (see `stream-spaces.md`), export one archive entry per space, gzip-compressed inside a zip, naming each entry from the (encoded) space name. Flush and close the archive entry rather than closing the `MessageWriter2` itself, since it wraps a shared zip stream.

Note the `MessageWriter2` constructor (used per archive entry) declares both `IOException` and `ClassNotFoundException` — unlike the single-file `MessageWriter2.create(...)` factory, which only throws `IOException`. Declare or catch both when using the constructor form.

## Import, with schema mapping between the file's types and the target stream's types

The imported file's schema and the target stream's current schema are not guaranteed to match exactly (the stream may have evolved since export). Bridge them with `SchemaAnalyzer`/`SchemaConverter`, and optionally rename legacy type names via `ClassMappings`. The critical step is looking up the actual matching output descriptor for each input type (by name, or by its `ClassMappings` rename) — converting a type to itself instead of to its real target-stream counterpart silently turns the whole schema bridge into a no-op. `ClassMappings` is only needed when a type was renamed between when the file was exported and now; skip it when types are stable, in which case the lookup only needs to compare names directly.

## Common mistakes

- Using bound (non-raw) `SelectionOptions`/`LoadingOptions` for export/import — this workflow is raw-only, moving `RawMessage` bytes directly.
- Closing a `MessageWriter2` that shares an underlying archive stream with other entries — flush and close the archive entry instead, closing the writer only for a single-file (non-archive) export.
- Skipping schema mapping on import when the target stream's schema may have drifted from the exported file's schema.
- Mapping an input type to itself instead of looking up its actual target-stream counterpart — this makes `SchemaConverter` a no-op that never bridges the schema change.
