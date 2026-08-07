# Create Stream

```cpp
TickStream *stream = db->createStream("bars1min", streamOptions); // native API
```

```cpp
std::unique_ptr<TickCursor> cursor(db->executeQuery(qql, std::vector<DxApi::QueryParameter>())); // QQL DDL, e.g. CREATE DURABLE STREAM
```

See `cursor-and-streams.md`.
