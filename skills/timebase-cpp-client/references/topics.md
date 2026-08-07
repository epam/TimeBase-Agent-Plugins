# Topics (Pub-Sub)

Topics are a separate low-latency pub-sub mechanism from durable streams, accessed via `TickDb::getTopicDB()`. Use this when the user asks for topic publish/subscribe rather than stream read/write.

`TopicDB::options()` returns a `const TopicDBOptions&` with nullable `name`/`description`/`owner`/`location`/`version` fields, the topic-level equivalent of `TickStream::options()` for regular streams.

## Create/drop a topic

Topic creation and deletion is QQL-only, there is no C++ `createTopic`/`deleteTopic` call:

```cpp
db->executeQuery("CREATE TOPIC \"my_topic\" (...) OPTIONS (MEDIA_TYPE = 'IPC')", std::vector<DxApi::QueryParameter>());
db->executeQuery("DROP TOPIC \"my_topic\"", std::vector<DxApi::QueryParameter>());
```

Ground the class/field definitions in the `CREATE TOPIC` DDL via the QQL generator skill rather than freehand-writing it.

## Publishing

`TopicDB::createPublisher(key, PublishingOptions)` returns a `TickDirectLoader`, which mirrors `TickLoader`'s register/begin/write/send cycle, with the same positional field-order rule as regular streams (see `message-types-and-decimal64.md`). One real difference: `TickDirectLoader::beginMessage`/`next` take a `TimestampNs` (nanoseconds), while regular stream `TickLoader`/`TickCursor`/`TickDb` calls elsewhere in this skill use `TimestampMs` (milliseconds), don't reuse a millisecond timestamp variable here without converting it. `TickStream::deleteData` is a pre-existing `TimestampNs` exception on regular (non-topic) streams too, see `stream-management.md`. See [`examples/topics-pubsub.md`](examples/topics-pubsub.md) for the full publish flow.

### Non-blocking send

`trySend()`/`tryCommitMessage()` return a `SendStatus` instead of blocking:

| `SendStatus` | Meaning |
| --- | --- |
| `OK` | Message sent |
| `BACK_PRESSURED` | Transport back-pressure, message stays buffered, retry later |
| `NOT_CONNECTED` | No active subscriber yet, message stays buffered, retry later |
| `RETRY` | Transient transport state, retry |

Use `trySend()` over `send()` when the caller needs to avoid blocking on a slow or absent subscriber, and handle every `SendStatus` value rather than assuming `OK`. If `trySend()`/`tryCommitMessage()` returns `BACK_PRESSURED`/`NOT_CONNECTED`/`RETRY` and the caller decides not to retry that message, call `loader->cancelMessage()` to discard it rather than leaving it pending.

`TickDirectLoader::flush()`/`finish()` follow the same convention as `TickLoader` (see `loader-writes.md`): `flush()` pushes a just-committed message out immediately instead of waiting for the buffer to fill, `finish()` performs the same server-side finalization `close()` does without freeing the loader's own write buffer.

### Error and subscription listeners

`TickDirectLoader::addListener` takes either an `ErrorListener` (`onError(errorClass, errorMsg)`) or a `SubscriptionListener` (notified of type/entity subscription changes: `typesAdded`/`typesRemoved`/`allTypesAdded`/`allTypesRemoved`/`entitiesAdded`/`entitiesRemoved`/`allEnititesAdded`/`allEnititesRemoved`). Only wire these when the task needs to react to subscriber churn, not by default.

`removeListener(ErrorListener*)`/`removeListener(SubscriptionListener*)` detaches a previously-added listener, call it before closing/destroying the loader if the listener object's lifetime ends first.

`PublishingOptions` also controls the idle strategy while waiting for buffer space (`IdleStrategy::NOOP`/`BUSYSPIN`/`YIELDING`/`SLEEPING`/`BACKOFF`, defaults to `BUSYSPIN`), `preserveNullTimestamp`, and `directory` (nullable string, `ConsumerOptions` exposes the same field). `SLEEPING` takes a `duration` (milliseconds), `BACKOFF` takes `maxSpins`/`maxYields`/`minParkPeriodNs` (default 1000ns)/`maxParkPeriodNs` (default 1ms). Leave these at their defaults unless the user has a specific latency requirement.

`TickDirectLoader::schema()`/`TickMessagePoller::schema()` each return the topic's schema as a string, the direct-loader/topic-poller equivalent of `TickStream::metadata()` for regular streams.

## Consuming (polling)

`TopicDB::createPollingConsumer(key, ConsumerOptions)` returns a `TickMessagePoller`. `processMessages(fragmentCountLimit, MessageProcessor)` is non-blocking, it returns immediately with `0` processed if nothing is available, poll in a loop rather than calling it once. `getBufferFillPercentage()` is available for backpressure monitoring. There is no blocking/live-push subscription API, only this polling model. `ConsumerOptions::topicDataLossHandler` (`std::function<bool()>`) is invoked on detected data loss, return `true` to keep polling. `poller->getSymbolName(entityId)`/`getInstrumentType(symbolId)` resolve a message header's numeric entity/symbol id the same way `TickCursor`'s equivalents do, see `cursor-and-streams.md`. See [`examples/topics-pubsub.md`](examples/topics-pubsub.md) for the full poll flow.

## Resource lifecycle

Wrap `TickDirectLoader`/`TickMessagePoller` in `std::unique_ptr` and call `close()` on every exit path, same as `TickLoader`/`TickCursor`.
