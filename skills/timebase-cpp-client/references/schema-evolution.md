# Schema Evolution

Changing a stream's schema in place, rather than creating a new stream. There is no verified real usage example for this API anywhere available, only the class/method shapes below. Treat this as higher-risk than the rest of the skill, test against a non-production stream first, and confirm with the user before generating a call that will run against real data, a schema change is not reversible.

## `SchemaChangeTask`

```cpp
class SchemaChangeTask {
public:
    bool polymorphic;
    bool background;
    Nullable<std::string> schema;      // XML schema form
    Nullable<std::string> schemaJson;  // JSON schema form
    Nullable<std::unordered_map<std::string, std::string>> defaults;
    Nullable<std::unordered_map<std::string, std::string>> mappings;
};
```

Two real constructors: one takes an XML schema string (`polymorphic`, `background`, `schema`), the other takes a JSON schema string plus optional `mappings`/`defaults` maps (`schemaJson`, `mappings`, `defaults`, `background`). Each constructor populates only one of `schema`/`schemaJson`, pick whichever form is more convenient to produce, there's no evidence a stream is tied to one schema form (`TickStream` exposes both `metadata()` and `metadataJson()` regardless). Applying the change is `stream->changeSchema(task)` (or the JSON convenience overload directly), both always return `true` on success and throw on failure, confirmed from the real implementation, not just the header. Set `background = true` for a large stream so the change runs asynchronously, confirmed from the same implementation: the client only blocks waiting for the stream to sync when `background` is false.

## Tracking a background change

```cpp
class BackgroundProcessInfo {
public:
    std::string name;
    ExecutionStatus status; // NONE, RUNNING, COMPLETED, ABORTED, FAILED
    std::vector<std::string> affectedStreams;
    double progress;
    TimestampMs startTime;
    TimestampMs endTime;
    bool isFinished() const;
};
```

`stream->backgroundProcessInfo(&info)` polls status, `stream->abortBackgroundProcess()` cancels an in-flight background process (schema change or otherwise). Whether an aborted change leaves partial results isn't stated anywhere in the client library, treat it as unknown rather than assuming a clean rollback.

See [`examples/schema-evolution.md`](examples/schema-evolution.md) for the full apply/track flow.
