# Read And Write A Stream

Assumes a resolved `TickStream *stream` (see `cursor-and-streams.md`).

## Write

```cpp
LoadingOptions options;
options.writeMode = WriteMode::APPEND; // the default is REWRITE (destructive), always set this explicitly
std::unique_ptr<TickLoader> loader(stream->createLoader(options));

enum MessageTypes { TRADE };
loader->registerMessageType(TRADE, "deltix.timebase.api.messages.TradeMessage"); // the well-known built-in TradeMessage type name, ground against get_stream_schema for a custom type

auto entityId = loader->getInstrumentId(InstrumentIdentity(DxApi::InstrumentType::EQUITY, "IBM"));

DataWriter &writer = loader->beginMessage(TRADE, entityId, timestamp);
writer.writeInt64(sequenceNumber);
writer.writeAlphanumeric(10, exchange);
writer.writeDecimal(price, 2U);
writer.writeDecimal(size, 2U);
loader->send();

loader->close();
```

`loader->next(typeId, entityId, timestamp)` is an alternative to `beginMessage` for the same purpose, both return the `DataWriter&` to fill in. See `loader-writes.md` for write modes and error handling, `message-types-and-decimal64.md` for the full field-access and `Decimal64` conventions.

## Read

```cpp
SelectionOptions options;
std::unique_ptr<TickCursor> cursor(stream->select(0 /* start time, ms */, options));

DataReader &reader = cursor->getReader();
InstrumentMessage header;
while (cursor->next(&header)) {
    const std::string *typeName = cursor->getMessageTypeName(header.typeId);
    // read fields via reader, in schema field order, see message-types-and-decimal64.md
}
cursor->close();
```

Start time `0` reads from the beginning. Use a specific millisecond timestamp grounded via `get_stream_time_range` for a bounded start.

A single `TickDb::select` also selects across multiple streams at once:

```cpp
std::vector<const TickStream*> streams = { stream };
std::unique_ptr<TickCursor> cursor(db->select(0, streams, SelectionOptions()));
```
