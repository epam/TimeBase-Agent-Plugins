# Array Fields And Custom Codecs

Use this reference when a custom (raw, non-bound) schema has an array-typed field, or when writing a generic debug-printing helper over raw decoded fields. See [`examples/array-fields.md`](examples/array-fields.md) for the code.

## Schema: an array field

`ArrayDataType(nullable, elementType)`. The element type can be any `DataType`, including another `ArrayDataType` or a `ClassDataType` (array of polymorphic objects).

## Writing an array field (raw encode)

Call `uenc.setArrayLength(n)` once, then `uenc.nextWritableElement()` per element written. The same pattern applies regardless of element type (skip `NaN` for a nullable `FloatDataType` element, `IntegerDataType.INT64_NULL` for a nullable integer element, etc.). `encoder.endWrite()` (an optional validation step, see `message-types-and-schema.md`) can be called once all fields are written, before extracting bytes for the message.

## Reading an array field (raw decode)

Iterate `decoder.getArrayLength()` times, calling `decoder.nextReadableElement()` and a type-specific getter (`getDouble()`, `getLong()`, etc.) per element.

## A reusable debug-print helper for raw fields (including arrays and nested objects)

Two mutually-recursive helpers cover any raw field shape: one dumps a whole nested object's field/value pairs, the other dumps an array (delegating back to the object dumper for `ClassDataType` elements). Catch `NullValueException` per-field/per-element when the type is nullable and might actually be null (a `ReadableValue` getter throws this rather than returning a sentinel).

## Common mistakes

- Forgetting `uenc.setArrayLength(n)` before writing elements, or writing more/fewer elements than declared.
- Not checking `type.getElementDataType().isNullable()` before skipping a `NaN`/null-sentinel value. Skipping unconditionally corrupts the array length for non-nullable element types.
- Assuming `decoder.getString()` is sufficient for array fields. It isn't reliable there, iterate `nextReadableElement()` and use type-specific getters instead.
