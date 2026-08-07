# Schema Evolution

## Applying the change

```cpp
stream->changeSchema(task);
```

or the JSON-schema convenience overload directly:

```cpp
stream->changeSchema(schemaJson, &mappings, &defaults, /* background */ true);
```

See `schema-evolution.md` (concept reference) for the `SchemaChangeTask` shape and the return/`background` semantics.

## Tracking a background change

```cpp
BackgroundProcessInfo info;
stream->backgroundProcessInfo(&info);

if (info.isFinished()) {
    // info.status is COMPLETED, ABORTED, or FAILED
}
```

See `schema-evolution.md` (concept reference) for `abortBackgroundProcess()`.
