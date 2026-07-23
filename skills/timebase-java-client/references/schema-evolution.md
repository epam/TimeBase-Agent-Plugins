# Schema Evolution

Use this reference only when the user needs to change the schema of an existing stream in place (add fields, change field encoding). This is an advanced, comparatively rare path, most tasks should stay on `message-types-and-schema.md` and `cursor-and-streams.md`/`stream-management.md`. See [`examples/schema-evolution.md`](examples/schema-evolution.md) for the full code.

Examples use the Enterprise Edition `deltix.*` package root. See the package-root mapping and edition differences in [`project-setup.md`](project-setup.md#package-roots-in-this-skills-examples) before applying these examples to a Community Edition project.

## Apply a schema change

Diff a "before" `RecordClassSet` (built from `stream.getFixedType()`) against an "after" set containing the new descriptor via `SchemaAnalyzer.DEFAULT.getChanges(...)`, then apply with `stream.execute(new SchemaChangeTask(change))`.

`SchemaChangeTask` runs in the **background by default** (`background = true`). To block until the change completes instead, use `new SchemaChangeTask(change, false)`. Either way, `stream.getBackgroundProcess()` returns the active `BackgroundProcessInfo` (or `null` if none is running). Poll it if you need to confirm completion before proceeding, when running in background mode.

## Worked example 1: adding new fields (extend a message type)

Extending a built-in or existing message type with new fields is done by defining a subclass whose new members are annotated, then diffing that subclass's introspected descriptor against the stream's current one. `@SchemaType` (paired with a getter/setter instead of a public field) lets a JavaBean-style class participate in introspection without exposing public fields. Use it when the class encapsulates its fields behind accessors rather than exposing them directly (the plain-public-field form in `message-types-and-schema.md` needs no `@SchemaType`, only `@SchemaElement` when a name override is needed).

The example extends `BarMessage`, which only exists on Enterprise Edition. On Community Edition, extend a custom introspected POJO instead (see `message-types-and-schema.md`), the rest of the diff/apply pattern is otherwise identical.

## Worked example 2: changing a field's encoding

To change how existing fields are encoded, redefine the same fields with the new `DataType` encoding, keeping the same field names and parent, then diff and apply the same way as example 1.

## Walking a schema recursively (for inspection/debugging)

`RecordClassDescriptor`/`DataField`/`DataType` form a tree, useful when writing a diagnostic dump rather than assuming a flat field list. Recurse through `ClassDataType` (nested/polymorphic object fields), `ArrayDataType` (element type), and `EnumDataType` (symbol/value pairs).

## Notes

- Ground the "before" descriptor from `stream.getFixedType()` (or the relevant polymorphic descriptor) rather than reconstructing it from memory, mismatches here produce incorrect diffs.
- Prefer additive changes (new fields via a subclass) over redefining/removing existing fields when existing consumers depend on the current schema.
- Confirm with the user before applying a schema change to a stream that already holds production data.
