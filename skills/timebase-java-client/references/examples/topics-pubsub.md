# Topics Pub/Sub

**Type:** fragment, assumes `db.isTopicDBSupported()` returned `true`.

**When to use:** Ultra-low-latency pub/sub via Topics rather than durable streams. See `topics.md` for when this applies.

## Create a topic

```java
RecordClassDescriptor rcd = /* schema for the topic's message type */;
try {
    db.getTopicDB().createTopic(topicKey, new RecordClassDescriptor[]{rcd}, null);
} catch (DuplicateTopicException ignore) {
    // topic already exists — fine to proceed
}
```

## Publish

```java
MessageChannel<InstrumentMessage> channel = db.getTopicDB().createPublisher(topicKey, null, new BusySpinIdleStrategy());
InstrumentMessage msg = new InstrumentMessage();
msg.setSymbol("GOOG");
msg.setTimeStampMs(System.currentTimeMillis());
channel.send(msg);
// ...
channel.close();
```

## Consume: `MessagePoller` (recommended)

```java
MessagePoller poller = db.getTopicDB().createPollingConsumer(topicKey, null);
IdleStrategy idle = new BusySpinIdleStrategy();
while (!stopFlag.get()) {
    idle.idle(poller.processMessages(100, message -> {
        // handle message
    }));
}
poller.close();
```

## Consume: `MessageSource`-compatible

```java
MessageSource<InstrumentMessage> source = db.getTopicDB().createConsumer(topicKey, null, new BusySpinIdleStrategy());
while (source.next()) {
    InstrumentMessage message = source.getMessage();
}
source.close();
```

## Consume: background worker with a callback

```java
Disposable worker = db.getTopicDB().createConsumerWorker(topicKey, null, new BusySpinIdleStrategy(),
    r -> new Thread(r, "topic-worker"),
    message -> { /* handle message */ });
// later: worker.close();
```
