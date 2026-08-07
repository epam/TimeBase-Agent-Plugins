# Schema Introspection

Use this when the task needs to discover a stream's schema from C++ itself, rather than (or in addition to) MCP's `get_stream_schema`, or needs to decode messages generically without hand-writing positional `DataReader` calls per type.

`stream->metadata()` returns the raw schema text in XML form, `stream->metadataJson()` returns the same schema in JSON form, both are always available regardless of which form the stream was originally created with. `Schema::TickDbClassDescriptor::parseDescriptors(text, parseFields)` turns either form into structured descriptors.

## Descriptor shape

```cpp
class TickDbClassDescriptor {
public:
    std::string className;
    std::string guid;
    std::string parentGuid;
    intptr_t parentIndex;          // index into the descriptor vector, for walking the inheritance chain

    bool isContentClass;
    std::vector<FieldInfo> fields; // non-static fields, in declared order

    // enum introspection, when this descriptor describes an enum type
    FieldType enumType;
    std::unordered_map<std::string, int64_t> symbolToEnumValue;
    std::vector<std::string> enumSymbols;
    std::unordered_map<int64_t, std::string> enumSymbolsSparse;
};

class FieldInfo {
public:
    std::string name;
    std::string relativeTo;
    DataType dataType;
};

class DataType {
public:
    FieldTypeDescriptor descriptor;
    std::string typeName;
    std::string encodingName;
    std::string descriptorGuid;
    bool isNullable;
    std::shared_ptr<DataType> elementType; // for array fields
    std::vector<std::string> types;        // for polymorphic OBJECT fields
};
```

`DataType::descriptor` (a `FieldTypeDescriptor`) has its own `type()`, `size()`, and `isNullable()` accessors. `size()` is the piece this skill's positional-access reference doesn't otherwise surface: it's the same field size an ASCII/alphanumeric field's `DataReader::readAlphanumeric(value, fieldSize)`/`DataWriter::writeAlphanumeric(fieldSize, value)` calls need (see `message-types-and-decimal64.md`), so when building a schema-driven tool rather than hand-writing fixed calls, read `fieldSize` from here instead of hardcoding it.

Iterating `descriptor.fields` in order gives the exact field order `DataReader`/`DataWriter` calls must follow for that message type, this is the C++-side equivalent of MCP's `get_stream_schema`, prefer MCP when available since it's already grounded to the live server, use this when the task specifically needs the schema from within the C++ program itself (e.g. building a generic tool).

When `descriptor` describes an enum type, its symbol-to-value mapping is split across two fields rather than one: `enumSymbols` covers ordinals `[0, TickDbClassDescriptor::ENUM_SYMBOLS_VECTOR_LIMIT)` (`2048`) densely by vector index, `enumSymbolsSparse` covers any ordinal at or beyond that limit via a map instead. Check `enumSymbols` first by index, fall back to `enumSymbolsSparse` for a value that turns out to be out of that range, rather than assuming every enum value lives in one or the other.

`TickDbClassDescriptor::calcHash(schema, descriptor)` computes a schema hash, useful for detecting schema drift between two connections without comparing full descriptor lists.

`TickDb::generateSchema(types)` produces schema text (the same shape `metadata()` returns) from a set of type descriptors instead of parsing it from an existing stream, use this when the task needs to construct a schema programmatically rather than deriving it from a live stream.

## Generic decode (schema-driven, no per-type code)

`DxApi::GenericCodec::MapMessageDecoderCache`, built from the parsed descriptors, decodes any message into a `std::unordered_map<std::string, FieldValue>` keyed by field name via `cache.decoder(typeId, typeName).decode(reader, fields)`. This is a real alternative to hand-writing positional `DataReader` calls per message type. Prefer it when the set of message types isn't known ahead of time, or when writing a generic tool rather than a fixed-schema consumer. For a fixed, known schema, prefer a hand-written typed codec instead (a lightweight type-name-dispatch subclass, or the fuller virtual-identity-methods-plus-GUID-checked-dispatcher convention, see `message-types-and-decimal64.md`, [`examples/polymorphic-read.md`](examples/polymorphic-read.md)), the generic path has more per-message overhead.

See [`examples/schema-introspection.md`](examples/schema-introspection.md) for the full metadata-parsing and generic-decode flows.
