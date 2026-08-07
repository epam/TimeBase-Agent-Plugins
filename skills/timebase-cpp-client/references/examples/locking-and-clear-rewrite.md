# Locking And Clear/Rewrite

## Locking

```cpp
LockOptions options; // defaults to a full-range WRITE_LOCK
stream->lock(options);
// ... exclusive access ...
stream->unlock();
```

See `stream-management.md` for the `LockOptions` shape and when to use locking.

## Clear (destructive)

```cpp
stream->clear();
```

See `stream-management.md` for the destructive-operation warning before generating this call.

## Rewrite via write mode

```cpp
LoadingOptions options;
options.writeMode = WriteMode::REWRITE; // or TRUNCATE, REPLACE, INSERT, APPEND
std::unique_ptr<TickLoader> loader(stream->createLoader(options));
```

`REWRITE`/`TRUNCATE`/`REPLACE` overwrite existing data instead of appending, same destructive-operation caution as `clear()`. See `loader-writes.md` for the full write-mode list.
