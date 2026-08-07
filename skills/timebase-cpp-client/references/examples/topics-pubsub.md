# Topics Pub-Sub

## Publishing

```cpp
TopicDB &topicDB = db->getTopicDB();
PublishingOptions options;
std::unique_ptr<TickDirectLoader> loader(topicDB.createPublisher("my_topic", options));

enum MessageTypes { TRADE };
loader->registerMessageType(TRADE, "fully.qualified.TradeMessage"); // ground via get_stream_schema

auto entityId = loader->getInstrumentId(InstrumentIdentity(DxApi::InstrumentType::EQUITY, "IBM"));

DataWriter &writer = loader->beginMessage(TRADE, entityId, timestamp);
writer.writeInt64(sequenceNumber);
writer.writeDecimal(price, 2U);
loader->send();

loader->close();
```

See `topics.md` for the `TimestampNs`-vs-`TimestampMs` caveat, non-blocking send (`SendStatus`), and listener details.

## Consuming (polling)

```cpp
TopicDB &topicDB = db->getTopicDB();
ConsumerOptions options;
options.topicDataLossHandler = []() -> bool {
    // return true to keep polling after detected data loss, false to stop
    return true;
};
std::unique_ptr<TickMessagePoller> poller(topicDB.createPollingConsumer("my_topic", options));

DxApi::MessageProcessor processor = [](DxApi::InstrumentMessage &header) {
    // read fields via poller->getReader(), positionally, see message-types-and-decimal64.md
};

while (!poller->isAtEnd()) {
    poller->processMessages(/* fragmentCountLimit */ 100, processor);
}
poller->close();
```

See `topics.md` for why `processMessages` must be polled in a loop.
