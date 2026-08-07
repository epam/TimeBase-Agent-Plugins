# Polymorphic Read (Hand-Written Typed Codec)

Two hand-written patterns for a fixed, known schema, lighter-weight than raw inline calls repeated at every call site. See `message-types-and-decimal64.md` (Typed message codec) for why dxapi ships no generator for these and when to prefer each pattern.

## Lightweight: type-name dispatch

The pattern is described in `message-types-and-decimal64.md` (Typed message codec):

```cpp
class TradeMessage : public MarketMessage {
public:
    double price;
    double size;
    bool has_price, has_size;

    void decode(InstrumentMessage &m, DataReader &r) {
        *(static_cast<InstrumentMessage *>(this)) = m;
        has_price = r.readDecimal(price);
        has_size = r.readDecimal(size);
    }
};
```

```cpp
enum { TRADE, BBO, MESSAGE_TYPES_COUNT };
unsigned knownMessages[0x100];
memset(knownMessages, -1, sizeof(knownMessages));

InstrumentMessage header;
TradeMessage trade;
while (cursor->next(&header)) {
    switch (knownMessages[header.typeId]) {
    case TRADE:
        trade.decode(header, reader);
        break;
    default:
        const std::string *typeName = cursor->getMessageTypeName(header.typeId);
        if (typeName && typeName->find("TradeMessage") != std::string::npos) {
            knownMessages[header.typeId] = TRADE;
            trade.decode(header, reader);
        }
        // else: unrecognized type, handle or skip
        break;
    }
}
```

## Full convention: virtual identity methods and a GUID-checked dispatcher

See `message-types-and-decimal64.md` (Typed message codec) for what this convention is, what the GUID is, and why the drift check below ships optional. There is no MCP shortcut for the GUID literal to embed below, `get_stream_schema` returns human-readable schema text, not descriptor GUIDs, capture it once via `Schema::TickDbClassDescriptor::parseDescriptors(stream->metadata().get(), false)` matched by `className` (the same call the dispatcher constructor below makes at runtime), or skip the GUID check entirely and rely on type-name dispatch alone. This example shows only the GUID variant of the drift check, add a `getHash()` method and a `calcHash()` comparison the same way if the stricter hash-based check described in `message-types-and-decimal64.md` is needed instead.

The class below is named `TradeMessageV2` to avoid colliding with the lightweight `TradeMessage` above, the two sections are independent illustrations of the same real stream type, not meant to be compiled together.

```cpp
// Real sample codecs declare each identity string as a file-scope `static const`
// right before the class it belongs to, not as a class member, this sidesteps
// needing an out-of-line definition for a class-static const.
static const std::string _NativeMessage_class_type__ = "NativeMessage";
static const std::string _NativeMessage_class_guid__ = "NativeMessage";

class NativeMessage : public InstrumentMessage {
public:
    virtual const std::string &getTypeName() const { return _NativeMessage_class_type__; }
    virtual const std::string &getGuid() const { return _NativeMessage_class_guid__; }

    virtual void decode(DataReader &reader) = 0;
    virtual void encode(DataWriter &writer) = 0;
    virtual ~NativeMessage() {}
};

static const std::string _TradeMessageV2_class_type__ = "deltix.timebase.api.messages.TradeMessage"; // the well-known built-in TradeMessage type name, not a placeholder
static const std::string _TradeMessageV2_class_guid__ = "<class GUID, captured from parseDescriptors at codec-authoring time>";

class TradeMessageV2 : public NativeMessage {
public:
    const std::string &getTypeName() const override { return _TradeMessageV2_class_type__; }
    const std::string &getGuid() const override { return _TradeMessageV2_class_guid__; }

    double price = 0, size = 0;
    bool has_price = false, has_size = false;

    void decode(DataReader &reader) override {
        has_price = reader.readDecimal(price);
        has_size = reader.readDecimal(size);
    }

    void encode(DataWriter &writer) override {
        has_price ? writer.writeDecimal(price) : writer.writeDecimal(FLOAT64_NULL);
        has_size ? writer.writeDecimal(size) : writer.writeDecimal(FLOAT64_NULL);
    }
};
```

```cpp
class TradeStreamCodec {
    enum { TRADE, MESSAGE_TYPES_COUNT };
    unsigned knownMessages[0x100];
    std::string guids[MESSAGE_TYPES_COUNT]; // only needed for the optional GUID check below

public:
    explicit TradeStreamCodec(TickStream *stream) {
        memset(knownMessages, -1, sizeof(knownMessages));
        auto descriptors = Schema::TickDbClassDescriptor::parseDescriptors(stream->metadata().get(), false);
        for (const auto &d : descriptors) {
            if (d.className == "deltix.timebase.api.messages.TradeMessage") {
                guids[TRADE] = d.guid;
            }
        }
    }

    void decode(TickCursor *cursor, InstrumentMessage &header, DataReader &reader, TradeMessageV2 &out) {
        unsigned slot = knownMessages[header.typeId];
        if (slot == (unsigned)-1) {
            const std::string *typeName = cursor->getMessageTypeName(header.typeId);
            if (typeName && *typeName == out.getTypeName()) {
                slot = knownMessages[header.typeId] = TRADE;
            }
        }
        if (slot == TRADE) {
            // Optional hardening, ships disabled in the real sample this is based on:
            // if (guids[TRADE].compare(out.getGuid())) throw std::runtime_error("schema drift detected");
            out.decode(reader);
        }
    }

    // Write path mirrors decode: the caller picks a small local typeId (TRADE above),
    // registers it with the loader once, then reuses it on every beginMessage/send.
    void registerWith(TickLoader *loader) {
        loader->registerMessageType(TRADE, "deltix.timebase.api.messages.TradeMessage");
    }

    void send(TickLoader *loader, unsigned entityId, TimestampMs timestamp, TradeMessageV2 &msg) {
        DataWriter &writer = loader->beginMessage(TRADE, entityId, timestamp);
        msg.encode(writer);
        loader->send();
    }
};
```

Prefer the full convention when the codec set is large enough that per-type identity and dispatch boilerplate pays for itself, or when the target project already generates classes in this shape. Use the lightweight version otherwise. Keep `decode`/`registerWith`/`send` on the same class: they share the same `typeId` scheme and the same concrete message class, and drift between the read and write side is easy to miss if they live apart.

## Array of nested polymorphic objects

See `message-types-and-decimal64.md` (Arrays of nested/polymorphic objects) for what this pattern is and how `typeIndex` maps to concrete classes. A full decode/encode pair over a small fixed set of entry types:

```cpp
class PackageEntry : public NativeMessage {
    // same shape as NativeMessage above: virtual getTypeName()/getGuid(), pure virtual decode/encode
};

class PackageHeader : public InstrumentMessage {
public:
    std::vector<std::shared_ptr<PackageEntry>> entries;

    // typeIndex must match the declared order of the array field's element types in the
    // schema (its DataType::elementType->types list, see message-types-and-decimal64.md),
    // not an assumption carried over from a different stream or a different schema version.
    // L1EntryImpl/TradeEntryImpl are illustrative PackageEntry subclasses, not real dxapi types,
    // write one such subclass per real entry type declared in the schema.
    static std::shared_ptr<PackageEntry> makeByTypeIndex(int32_t typeIndex) {
        switch (typeIndex) {
        case 0: return std::make_shared<L1EntryImpl>();
        case 1: return std::make_shared<TradeEntryImpl>();
        default: return nullptr; // unrecognized type: caller should reader.skipObject() instead of decoding
        }
    }

    void decode(DataReader &reader) {
        entries.clear();
        int32_t count = reader.readArrayStart();
        for (int32_t i = 0; i < count; ++i) {
            int32_t typeIndex = reader.readObjectStart();
            auto entry = makeByTypeIndex(typeIndex);
            if (entry) {
                entry->decode(reader);
                entries.push_back(entry);
            } else {
                reader.skipObject();
            }
            reader.readObjectEnd();
        }
        reader.readArrayEnd();
    }

    void encode(DataWriter &writer) const {
        writer.writeArrayStart((int32_t) entries.size());
        for (auto &entry : entries) {
            writer.writeObjectStart(typeIndexOf(entry->getTypeName()));
            entry->encode(writer);
            writer.writeObjectEnd();
        }
        writer.writeArrayEnd();
    }
};
```

`typeIndexOf` is the write-side inverse of `makeByTypeIndex`, a small lookup comparing `getTypeName()` against the same ordered type list. Keep both in sync with the schema's declared element type order, a mismatch silently writes the wrong concrete type index rather than failing loudly.

See `schema-introspection.md` for the alternative schema-driven generic decode path when the type set isn't known ahead of time.
