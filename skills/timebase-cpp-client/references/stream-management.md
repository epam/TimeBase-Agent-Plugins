# Stream Management

Operational `TickStream`/`TickDb` calls that don't fit connection, cursor, or loader usage: listing streams, clearing data, locking, periodicity, and write buffering.

## Listing streams

`db->listStreams()` returns `vector<TickStream*>`, `stream->key()` returns a plain string, `stream->name()` returns a nullable (call `.get()` after checking it's set). See [`examples/connect-list-streams.md`](examples/connect-list-streams.md).

## Listing entities and symbols

`stream->listEntities()` returns the stream's `vector<InstrumentIdentity>`, `stream->listSymbols()` returns just the symbol strings. Prefer MCP's `get_stream_symbols` when it's available since it's already grounded to the live server, use these when the task specifically needs the list from within the C++ program itself.

`InstrumentIdentity::type` holds an `InstrumentType` (`EQUITY`, `OPTION`, `FUTURE`, `BOND`, `FX`, `INDEX`, `ETF`, `CUSTOM`, `SIMPLE_OPTION`, `EXCHANGE`, `TRADING_SESSION`, `STREAM`, `DATA_CONNECTOR`, `EXCHANGE_TRADED_SYNTHETIC`, `SYSTEM`, `CFD`, or `UNKNOWN`). `isTradable(instrumentType)` is a free function, not a method on `InstrumentType`, call it as `isTradable(identity.type)`.

`stream->getTimeRange(range, entities)`/`getTimeRange(range, symbols)` fill a 2-element `TimestampMs range[]` (start, end) scoped to the given entity/symbol list instead of the whole stream, `range` is an out-parameter, the return value reports whether any data was found. Omit the list argument (or pass `nullptr`) for the whole-stream range. See `stream-spaces.md` for the further space-scoped overload.

## Stream scope

`stream->scope()` returns a `StreamScope`: `DURABLE` (persisted, the common case), `EXTERNAL_FILE` (backed by an external data file, see `createFileStream` in `cursor-and-streams.md`), `TRANSIENT` (in-memory, not persisted), or `RUNTIME`. Check this before assuming a stream behaves like a durable one, a transient stream's write buffering (`lossless` below) and durability characteristics differ.

## Destructive stream operations

All of the following are destructive and not reversible, confirm with the user before generating a call to any of them:

- `stream->clear()` deletes all data in the stream, but keeps its schema. Overloads accept an entity or symbol list to clear only those instruments instead of the whole stream. See [`examples/locking-and-clear-rewrite.md`](examples/locking-and-clear-rewrite.md).
- `stream->truncate(millisecondTime, ...)` and `stream->purge(millisecondTime)` remove data in bulk relative to a single cutoff, distinct from `clear()`. Both take the cutoff as `TimestampMs` (milliseconds). `purge` has no entity/symbol overload, it always applies to the whole stream. Confirm which side of the cutoff each removes against the project's vendored `dxapi.h` (`project-setup.md`) before relying on either, that boundary isn't restated here.
- `stream->deleteData(from, to, ...)` deletes data in a bounded time range rather than the whole stream. Unlike `truncate`/`purge`, both bounds are `TimestampNs` (nanoseconds), don't reuse a millisecond timestamp variable here without converting it.
- `stream->deleteStream()` deletes the stream itself, schema included, and takes no arguments.

## Renaming instruments

`stream->renameInstruments(from, to)` remaps a symbol to a new name across the stream's stored data. This is the real dxapi equivalent of "rename a symbol", there is no separate copy/sync-between-streams utility.

## Locking

```cpp
class LockOptions {
public:
    LockType type;       // NO_LOCK, READ_LOCK, WRITE_LOCK
    int64_t startTime;
    int64_t endTime;
};
```

`stream->lock(options)`/`unlock()` (defaults to a full-range `WRITE_LOCK`), `tryLock(...)` is the non-blocking variant. Use locking when the task needs exclusive access to a time range for a multi-step operation (e.g. read-modify-write), not for ordinary single reads or writes. See [`examples/locking-and-clear-rewrite.md`](examples/locking-and-clear-rewrite.md).

## Periodicity

```cpp
Interval interval;
stream->getPeriodicity(&interval);
```

```cpp
class Interval {
public:
    int64_t numUnits;
    TimeUnit unitType; // MILLISECOND, SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, QUARTER, YEAR
};
```

Reflects the stream's configured tick periodicity, useful for sanity-checking an expected message cadence before assuming data is missing.

## Distribution rule

`stream->distributionRuleName()` returns the name of the stream's partitioning rule as a nullable (call `.get()` after checking it's set, same as `stream->name()` above), useful for understanding how a stream's data is spread across storage without inventing an assumption about it.

## Other stream metadata accessors

`stream->distributionFactor()` returns the number of partitions the stream's data is split across as a plain `int32_t` (not nullable, unlike `distributionRuleName()` above). `stream->owner()`, `stream->location()`, `stream->version()`, and `stream->description()` each return a nullable, same `.get()`-after-checking convention as `name()`. `stream->describe()` returns a human-readable summary string, useful for logging/debugging rather than programmatic use, don't confuse it with `description()` above, they're unrelated calls despite the similar name. `stream->options()` returns the stream's full `const StreamOptions&`, the same structure passed to `createStream` at creation time, for a full inspection rather than one field at a time.

`stream->polymorphic()`, `unique()`, `duplicatesAllowed()`, and `highAvailability()` each return a plain `bool` reflecting how the stream was configured at creation time, check these before assuming a stream's write/dedup semantics rather than guessing from its schema alone.

### `setSchema` vs `changeSchema`

Two distinct ways to change a stream's configuration after creation, do not use them interchangeably: `stream->setSchema(options)` replaces the stream's whole `StreamOptions` wholesale (schema included), while `stream->changeSchema(...)` (see `schema-evolution.md`) performs an incremental, trackable migration with explicit field mapping and default-value control. Prefer `changeSchema` when the task is specifically about evolving an existing schema in place, since `setSchema` gives no mapping/default control over how existing data reconciles with the new shape.

## Write buffering

`BufferOptions` is embedded in `StreamOptions::bufferOptions` at stream-creation time, it isn't set per-loader:

```cpp
class BufferOptions {
public:
    uint32_t initialBufferSize; // default 0x2000
    uint32_t maxBufferSize;     // default 0x10000
    uint64_t maxBufferTimeDepth; // default INT64_MAX
    bool lossless;              // transient streams only, durable streams are always lossless
};
```

`lossless` only matters for transient (non-durable) streams: `true` blocks the loader until a slow cursor frees buffer space, `false` discards old buffered messages instead. Only change these from their defaults when the user has a specific throughput/latency constraint.
