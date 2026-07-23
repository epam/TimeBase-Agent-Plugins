# Import/Export

Use this reference for bulk-exporting stream data to a local file (or importing it back), as opposed to routine reads/writes through cursors and loaders. This is a comparatively rare, heavier-weight operation, **DO NOT** reach for it unless the task specifically asks for a file-based export/import or backup. See [`examples/export-import-file.md`](examples/export-import-file.md) for the full code.

Examples use the Enterprise Edition `deltix.*` package root. See the package-root mapping and edition differences in [`project-setup.md`](project-setup.md#package-roots-in-this-skills-examples) before applying these examples to a Community Edition project.

## Creating a new stream from a file schema

When importing into a brand-new stream (as opposed to an existing one), read the file's header to recover its schema, collect the descriptors into a `RecordClassSet`, and build `StreamOptions` from that set directly with `setMetaData(...)` rather than naming a specific descriptor. This is the `new StreamOptions()` + `setMetaData(polymorphic, RecordClassSet)` path from [`stream-management.md`](stream-management.md), applied to a dynamically-collected schema instead of literal descriptors.

## Export to a single message file

Export always reads in raw mode (`SelectionOptions(true, false)`) and writes `RawMessage` directly via `MessageWriter2`. No bound decoding needed since the writer persists the wire format as-is.

## Export to a per-space zip archive

When a stream has multiple spaces (see [`stream-spaces.md`](stream-spaces.md)), export one archive entry per space, gzip-compressed inside a zip, naming each entry from the space name. Flush and close the archive entry rather than closing the `MessageWriter2` itself, since it wraps a shared zip stream.

## Import

The imported file's schema and the target stream's current schema are not guaranteed to match exactly, the stream may have evolved since export. Three classes work together to bridge that gap:

1. `SchemaMapping` says which input type corresponds to which output type. It is an identity table, not a diff.
2. `SchemaAnalyzer(mapping).getChanges(inSet, ..., outSet, ...)` computes the actual diff for each corresponding pair, a `MetaDataChange` describing added, removed, or re-encoded fields.
3. `SchemaConverter(change).convert(rawMessage)` applies that diff, transforming an individual raw message from the file's encoding to the stream's current encoding.

Building the `SchemaMapping` in step 1 is where a renamed type matters: matching by name alone misses a type that was renamed between export and now. Enterprise Edition automates this with `SchemaUpdater(classMappings).buildMapping(null, inTypes, outTypes)`, where `ClassMappings` is the old-name-to-new-name lookup table. Neither `SchemaUpdater` nor `ClassMappings` exist on Community Edition, build the `SchemaMapping` by comparing type names directly instead, which is correct as long as no type was renamed.

## Common mistakes

- Using bound `SelectionOptions`/`LoadingOptions` for export/import. This workflow is raw-only, moving `RawMessage` bytes directly.
- Closing a `MessageWriter2` that shares an underlying archive stream with other entries, flush and close the archive entry instead, closing the writer only for a single-file export.
- Skipping schema mapping on import when the target stream's schema may have drifted from the exported file's schema.
- Mapping an input type to itself instead of looking up its actual target-stream counterpart, this makes `SchemaConverter` a no-op that never bridges the schema change.
