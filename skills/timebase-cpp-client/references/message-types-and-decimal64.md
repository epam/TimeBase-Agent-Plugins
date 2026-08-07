# Message Types And Decimal64

dxapi has no generated/bound message classes for arbitrary schemas. All field access goes through `DataReader` (read) and `DataWriter` (write), and it is **positional**: calls must be made in the exact order the schema declares its fields, there is no name-based lookup. (A schema-driven generic decode path does exist for when the type set isn't known ahead of time, see `schema-introspection.md`.)

## Reading fields

Two real overload styles exist. Plain overloads return the value directly, for required (non-nullable) fields:

```cpp
DataReader &reader = cursor->getReader();
int64_t sequenceNumber = reader.readInt64();
double price = reader.readDecimal();
```

Nullable overloads write into an out-parameter and return whether the field was present, for optional (nullable) fields:

```cpp
int64_t sequenceNumber;
bool hasSequenceNumber = reader.readInt64(sequenceNumber);

std::string exchange;
bool hasExchange = reader.readAlphanumeric(exchange, 10); // (out-value, fieldSize)

bool beginMatch;
bool hasBeginMatch = reader.readNullableBoolean(beginMatch);
```

Use the nullable style when the schema marks the field nullable (`DataType::isNullable`, see `schema-introspection.md`), the plain style otherwise. Confirm the exact `read*` overload set against the project's vendored `data_reader.h`, see `project-setup.md`.

## Writing fields

```cpp
writer.writeInt64(sequenceNumber);
writer.writeUTF8(text, length);
writer.writeAlphanumeric(fieldSize, value); // (fieldSize, value), opposite arg order from the reader
writer.writeDecimal(price, precision);
```

For a NULL value on a nullable field, use the NULL sentinels and dedicated null writers instead of a plain write:

```cpp
writer.writeInt64(INT64_NULL);
writer.writeDecimal(FLOAT64_NULL);
writer.writeAlphanumericNull(fieldSize);
```

`TIMESTAMP_NULL` is the equivalent sentinel for timestamp fields. Confirm the exact `write*`/`writeXNull` set against the project's vendored `data_writer.h`.

## Decimal64 / DFP

Two genuinely different wire encodings both show up as "a decimal field" and are not interchangeable:

- A plain compressed-float field: `reader.readDecimal()` / `writer.writeDecimal(double[, precision])`.
- A raw DFP-backed `Decimal64` field: stored on the wire as a plain `int64`, read with `reader.readInt64()` then converted, written by converting first then `writer.writeUInt64(...)`. `Decimal64` itself is a separate library dependency from dxapi (see `project-setup.md`), there is no dedicated `writeDecimal64`/`readDecimal64` convenience call:

```cpp
#include <dfp/DecimalNative.hpp>

deltix::dfp::Decimal64 price = deltix::dfp::Decimal64::fromUnderlying((uint64_t) reader.readInt64());
```

```cpp
writer.writeUInt64(price.toUnderlying());
```

Real hand-written and generated codecs consistently pick one encoding per field and stay with it, a DFP-typed field is never read with `readDecimal()`. Do not guess: confirm the field's real encoding from the schema (`get_stream_schema`, or `DataType::encodingName` when parsing descriptors directly, see `schema-introspection.md`) before writing this code. Calling the wrong reader/writer for a field does not just corrupt that one value, `readDecimal()` and `readInt64()` consume different wire widths, so every positional field read after the mistake is misaligned for the rest of the message.

## Typed message codec

The dxapi C++ library itself ships no code generator for typed message classes. Real sample codecs consistently follow a shape (one file per message class, namespaces mirroring the schema's Java package names, boilerplate identity members) that looks like generator output from elsewhere in the TimeBase toolchain rather than anything hand-rolled, but no such generator was found in the dxapi C++ repo itself. Two real, hand-written patterns exist for a fixed, known schema, both cheaper than raw inline calls repeated at every call site:

- A small subclass with its own `decode(InstrumentMessage&, DataReader&)` method, dispatched at read time by type name with a cache to avoid repeated string comparison.
- A fuller convention seen consistently across real sample codecs: a class per message type overriding virtual const identity methods (`getTypeName()`/`getGuid()`, not static methods) that each return a reference to a file-scope `static const std::string` declared alongside the class, and a small per-stream dispatcher resolving `typeId` once by type-name comparison, optionally also comparing each schema descriptor's GUID string against the typed instance's `getGuid()` to catch drift, though the real sample this is based on ships that GUID check commented out. Some real dispatchers add a third, stricter class method, `getHash()`, compared against `TickDbClassDescriptor::calcHash(schema, descriptor)` (returns `std::string`) instead of or alongside the GUID check, this catches a schema change that alters field layout without changing the class GUID. More boilerplate per type, but scales better to a larger message set.

A typed codec's write path should mirror its decode path: the same concrete classes, an `encode(DataWriter&)` method writing fields in the identical schema order `decode` reads them in, called from `TickLoader::beginMessage(typeId, entityId, timestamp)`/`send()` (see `loader-writes.md`) instead of `cursor->next()`. Treat decode and encode as a matched pair for each class, not as two independently-designed paths.

See [`examples/polymorphic-read.md`](examples/polymorphic-read.md) for both, including the write side and nested/polymorphic object arrays.

## Array fields

Array-typed fields have their own read/write calls, bracketing the per-element reads/writes rather than a single call:

```cpp
int32_t count = reader.readArrayStart(); // INT32_NULL if the array itself is null
for (int32_t i = 0; i < count; ++i) {
    double element = reader.readDecimal();
}
reader.readArrayEnd();
// or, to skip without decoding elements:
reader.skipArray();
```

```cpp
writer.writeArrayStart(elements.size());
for (double element : elements) {
    writer.writeDecimal(element);
}
writer.writeArrayEnd();
// or for a null array:
writer.writeArrayNull();
```

A raw binary array has its own dedicated pair instead of the start/element/end sequence: `writer.writeBinaryArray(data, size)` / `writer.writeBinaryArrayNull()` to write, `reader.readBinary(std::vector<uint8_t>&)` (returns whether the field was present) / `reader.skipBinary()` to read.

### Arrays of nested/polymorphic objects

An array element can itself be an object rather than a primitive, common for a package/header message holding a mix of entry types. `readObjectStart()`/`writeObjectStart(typeIndex)` bracket each element in addition to the array's own start/end:

```cpp
int32_t count = reader.readArrayStart();
for (int32_t i = 0; i < count; ++i) {
    int32_t typeIndex = reader.readObjectStart(); // INT32_NULL if this element is null
    // dispatch on typeIndex to the matching concrete class's decode(reader), see below
    reader.readObjectEnd();
}
reader.readArrayEnd();
```

```cpp
writer.writeArrayStart(entries.size());
for (auto &entry : entries) {
    writer.writeObjectStart(typeIndexFor(entry)); // or writer.writeObjectNull() for a null element
    entry->encode(writer);
    writer.writeObjectEnd();
}
writer.writeArrayEnd();
```

`typeIndex` is a small integer (0-255), not a type name or GUID. Ground its mapping to concrete classes from the field's own descriptor rather than guessing: parsing the schema (see `schema-introspection.md`) gives the array field's `DataType::elementType->types`, a list of the possible object type names in the same order the wire uses for `typeIndex`. On the write side, look up the index for a given instance by matching its type name against that same list (a `getTypeName()`-style identity method makes this a simple linear comparison), don't hardcode positions from one observed sample.

See [`examples/polymorphic-read.md`](examples/polymorphic-read.md) for a full worked decode/encode pair over a small fixed set of entry types.

## ASCII and CHAR fields

An ASCII-typed field is distinct from a UTF8 field, use its own dedicated calls rather than `readUTF8`/`writeUTF8`:

```cpp
std::string text;
bool hasText = reader.readAscii(text);
// or, to skip without decoding: reader.skipAscii();
```

```cpp
writer.writeAscii(text);
```

A single CHAR field reads/writes as a `wchar_t`, with the same plain/nullable overload split as other scalar fields:

```cpp
wchar_t c = reader.readWChar();          // plain, required field
wchar_t c2; bool hasC = reader.readWChar(c2); // nullable field
```

```cpp
writer.writeWChar(c);              // required field
writer.writeWChar(c, isNull);      // nullable field
```

## Other scalar field types

A few field types have their own dedicated calls rather than reusing the integer/float readers, and not all of them have a nullable overload, if a schema marks one of these fields nullable, encode nullability with the type's own NULL sentinel instead of assuming a `bool`-returning overload exists:

- **Enum**: sized by declared width, `readEnum8`/`readEnum16`/`readEnum32`/`readEnum64` (plain) each have a nullable counterpart taking an out-parameter (`int&` for the 8/16/32 variants, `int64_t&` for the 64-bit one) and returning whether the field was present. Writers mirror this: `writeEnum8`/`16`/`32`/`64` (plain) and the same names taking an extra trailing `bool isNull` for the nullable form.
- **TimeOfDay**: `int32_t readTimeOfDay()` / `void writeTimeOfDay(int32_t)`, no nullable overload on either side, use the `TIMEOFDAY_NULL` sentinel for a null value.
- **Interval (PINTERVAL)**: `uint32_t readInterval()` plain, two nullable overloads exist depending on the sign of the out-parameter, `bool readInterval(int32_t&)` and `bool readInterval(uint32_t&)`. `void writeInterval(uint32_t)` plain, `writeInterval(uint32_t, bool isNull)` for the nullable form.
- **Compressed DateTime (PTIME)**: `int64_t readDateTimeMs()` (milliseconds) and `int64_t readDateTimeNs()` (nanoseconds), no nullable overload on either. Writers mirror the two resolutions: `void writeCompressedTime(int64_t)` (milliseconds), `void writeCompressedNanoTime(int64_t)` (nanoseconds), also with no nullable overload, use `TIMESTAMP_NULL` for a null value.
- **UInt40**: `uint64_t readUInt40()` / `void writeUInt40(uint64_t)`, no nullable overload on either side.

Confirm the exact overload set against the project's vendored `data_reader.h`/`data_writer.h` before relying on one of these, this list is not exhaustive.

## `InstrumentMessage` convenience accessors

`InstrumentMessage` (the `header` a cursor/poller fills on each `next`/`nextIfAvailable`/`processMessages` call) exposes `getSymbolName()`, `getTypeName()`, and `getInstrumentType(unsigned symbolId)` directly as member methods, resolving `entityId`/`typeId` to their human-readable name/type without the caller holding a separate cursor or poller pointer. These delegate internally to whichever `TickCursor`/`TickMessagePoller` produced the message, wired up when the header is constructed from it, calling them on a header that wasn't produced by a cursor/poller (e.g. a freshly-constructed `InstrumentMessage` used only for writing) returns `nullptr`/`InstrumentTypeEnum::UNKNOWN` rather than throwing.

## `MarketMessage` base fields

Market data message types (trades, quotes, bars) commonly derive from `MarketMessage`, which adds these fields on top of `InstrumentMessage`'s `timestamp`/`entityId`/`typeId`: `originalTimestamp` (source-exchange timestamp, distinct from the TimeBase-assigned `timestamp`), `sequenceNumber`, `currencyCode`, each paired with a `has_originalTimestamp`/`has_sequenceNumber`/`has_currencyCode` flag since they're nullable. Read/write them through the same positional `DataReader`/`DataWriter` calls as any other field, in the order the schema declares them, they are not special-cased.

## Field grounding

Always confirm field names, types, declared order, and nullability via `get_stream_schema` (MCP) before writing `DataReader`/`DataWriter` calls. A wrong field, wrong order, or wrong plain-vs-nullable choice corrupts data silently, it is not caught at compile time.

## Built-in message types

If the schema matches a well-known built-in type (e.g. a trade or bar message), use its documented fully-qualified type-name string for `registerMessageType`/type filters, but still access fields through `DataReader`/`DataWriter` rather than assuming a generated struct exists for it.
