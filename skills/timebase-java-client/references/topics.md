# Topics (Low-Latency Pub/Sub)

Use this reference only when the task explicitly calls for ultra-low-latency in-process/inter-process pub/sub, distinct from durable stream storage. Topics are an alternative to streams for that specific use case, not a general-purpose default — prefer streams (`cursor-and-streams.md`) unless the user specifically needs Topics-level latency and doesn't need durable history.

Gate any Topics code on `db.isTopicDBSupported()` before calling `db.getTopicDB()` — not every server/client combination supports it. See [`examples/topics-pubsub.md`](examples/topics-pubsub.md) for creating a topic, publishing, and all three consumer styles.

## Consume — three styles, pick one

- **`MessagePoller` (recommended)** — non-blocking polling loop, best control and latency.
- **`MessageSource`-compatible consumer** — reuse existing code written against the `MessageSource` API (regular cursor-style `next()`/`getMessage()`), slightly less efficient than the poller but often more convenient.
- **Background worker with a callback** — behaves like the poller internally, but runs in its own thread and invokes a callback per message; returns a `Disposable` to stop it.

## Common mistakes

- Using Topics as a default read/write path instead of durable streams — Topics trade durability for latency and are an intentional, narrower choice.
- Not checking `isTopicDBSupported()` before calling `getTopicDB()`.
- Choosing the `MessageSource`-compatible consumer purely out of familiarity when the polling consumer (`MessagePoller`) would better serve a latency-sensitive task.
