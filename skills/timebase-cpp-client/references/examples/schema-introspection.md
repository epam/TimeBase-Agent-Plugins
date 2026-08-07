# Schema Introspection

## Parsing stream metadata

```cpp
#include <dxapi/schema.h>

const Nullable<std::string> &meta = stream->metadata();
if (meta.is_null()) {
    // stream has no metadata
}
std::vector<Schema::TickDbClassDescriptor> descriptors =
    Schema::TickDbClassDescriptor::parseDescriptors(meta.get(), /* parseFields */ true);
```

See `schema-introspection.md` (concept reference) for the descriptor/`FieldInfo`/`DataType` shapes.

## Generic decode (schema-driven, no per-type code)

```cpp
#include <dxapi/generic-message-decode.h>

using namespace DxApi::GenericCodec;

MapMessageDecoderCache cache(descriptors);

InstrumentMessage header;
DataReader &reader = cursor->getReader();
std::unordered_map<std::string, FieldValue> fields;

while (cursor->next(&header)) {
    const std::string *typeName = cursor->getMessageTypeName(header.typeId);
    fields.clear();
    cache.decoder(header.typeId, typeName).decode(reader, fields);
    // fields is now name -> FieldValue for this message, use fieldValueToString(v) to print
}
```

See `schema-introspection.md` (concept reference) for when to prefer this over the hand-written typed codec patterns in `examples/polymorphic-read.md`.
