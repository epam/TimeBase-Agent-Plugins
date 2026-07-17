# Topics

Use this reference only when the task explicitly calls for ultra-low-latency in-process/inter-process pub/sub, distinct from durable stream storage. Topics are an alternative to streams for that specific use case, not a general-purpose default, prefer streams ([`cursor-and-streams.md`](./cursor-and-streams.md)) unless the user specifically needs Topics-level latency and doesn't need durable history.

Gate any Topics code on `db.isTopicDBSupported()` before calling `db.getTopicDB()`. Not every server/client combination supports it. See [`examples/topics-pubsub.md`](./examples/topics-pubsub.md) for creating a topic, publishing, and all three consumer styles.

Topics are available on both editions with the same API. Two classes are exceptions to the general package-root swap in [`project-setup.md`](./project-setup.md#package-roots-in-this-skills-examples):

- `MessageChannel`/`MessageSource`: Enterprise Edition `deltix.data.stream.*`, Community Edition `com.epam.deltix.streaming.*`.
- `InstrumentMessage`: Enterprise Edition `deltix.qsrv.hf.pub.InstrumentMessage`, Community Edition `com.epam.deltix.timebase.messages.InstrumentMessage`.

Everything else (`TopicDB`, `TopicSettings`, etc.) follows the normal `deltix.` to `com.epam.deltix.` swap.

## What Topics trade away

Topics skip the TimeBase server process and route messages directly producer to consumer, which is what gives the latency win, but it comes with real limits:

- Not persisted, unless the topic's `copyToStream` option is turned on.
- No filtering, no channel multiplexing, no schema changes, and other stream features are simply not there.
- Topic classes are not thread-safe, and a slow consumer blocks other consumers and even the producer.
- Each consumer generally needs a dedicated CPU core, unless it uses the non-blocking `MessagePoller`.

## Topic types

- `UDP_SINGLE_PUBLISHER`, the default, UDP transport, one producer per topic.
- `IPC`, inter-process communication, same machine only.
- `MULTICAST`, experimental, needs UDP multicast network support.

## Deployment requirements

Topics need a separate Aeron Media Driver process running on every machine that uses them. On the server, `admin.properties` needs `TimeBase.aeron.enabled=true`. On the client, pass `-DTimeBase.transport.aeron.directory=/path/to/aeron/dir` as a JVM flag. See the [dedicated knowledge base page](https://kb.timebase.info/docs/overview/topics) for the full deployment and configuration details.

## Consume, three styles, pick one

- **`MessagePoller` (recommended)**. Non-blocking polling loop, best control and latency, and the only style that doesn't need a dedicated CPU core.
- **`MessageSource`-compatible consumer**. Reuse existing code written against the `MessageSource` API (regular cursor-style `next()`/`getMessage()`), slightly less efficient than the poller but often more convenient.
- **Background worker with a callback**. Behaves like the poller internally, but runs in its own thread and invokes a callback per message. Returns a `Disposable` to stop it.

## Common mistakes

- Using Topics as a default read/write path instead of durable streams. Topics trade durability for latency and are an intentional, narrower choice.
- Not checking `isTopicDBSupported()` before calling `getTopicDB()`.
- Choosing the `MessageSource`-compatible consumer purely out of familiarity when the polling consumer (`MessagePoller`) would better serve a latency-sensitive task, or when a dedicated CPU core isn't available for a blocking consumer.
- Forgetting the Aeron Media Driver process or the server/client Aeron configuration, then being confused why Topics don't work at all.
