# Debugging And Performance

## Acquisition and linking failures

| Symptom | Likely cause | Check |
| --- | --- | --- |
| 401/403 downloading from Nexus | Missing or wrong credentials | Env vars, admin-issued credentials |
| Linker can't find dxapi symbols (Linux/macOS) | Include/lib paths not wired against the actual extracted archive | Check the extracted layout on disk, don't assume a fixed path |
| Windows: NuGet `.targets` didn't wire include/lib paths | Project isn't `Platform=x64` + `PlatformToolset=v142`, the only case the real `.targets` file handles | Confirm the project's platform/toolset, or fall back to a manually-vendored `dxapi/` folder |
| Linker can't find DFP/Decimal64 symbols | DFP not acquired separately | `project-setup.md` DFP section |

## Build failures

| Symptom | Likely cause | Check |
| --- | --- | --- |
| Compiler errors on toolset | Wrong compiler/toolset for platform | MSVC v142 (Windows), Clang 10 + libstdc++ (Linux), Apple-Clang (macOS) |
| SSL-related build/link errors on macOS arm64 | Missing OpenSSL 1.1 | `brew install openssl@1.1` |

## Connection failures

- Verify the URI scheme matches intent: `dxtick://` (direct), `dstick://` (direct+SSL), `dxctick://` (cluster), `dsctick://` (cluster+SSL).
- Confirm the server is reachable and the port is correct.
- For SSL, check `SSL_CERT_FILE`/`SSL_CERT_DIR`.
- For basic auth, prefer `TickDb::createFromUrl(url, username, password)` over URI-embedded credentials.
- For version-mismatch symptoms after a client or server upgrade, compare `db->clientProtocolVersion()` against `db->serverProtocolVersion()`.

## Throughput and preloading

`TickCursor` exposes read-side counters (`nBytesReceived`, `nBytesRead`, `nMessageBytesRead`, `nMessagesRead`, `nMessagesSkipped`, `nMessagesReceived`), `TickLoader` exposes write-side counters (`nBytesWritten()`, `nMsgWritten()`, `nMsgCancelled()`). Check these when diagnosing whether a slow read/write is network-bound, decode-bound, or simply not producing messages at all.

`cursor->preload(nBytes, blockSize)` and `loader->preload(nBytesToPreload, writeBlockSize)` request the client read further ahead of / write further behind consumption, tune only when throughput profiling actually points at buffering rather than the network or server.

## Exception hierarchy

`TickCursorException` derives `std::runtime_error` and is the base for cursor errors. `TickCursorServerError`, `TickCursorInterruptedException` (local interruption from `close()` etc.), `TickCursorError`, and `TickCursorClosedException` all derive directly from it, a flat hierarchy rather than nested. `TickCursorServerError` carries an extra `int code` field alongside its message, thrown when the server sends an error block during `readNextRecord()`. Note `TickCursorClosedException`'s default message text reads "Tickloader is closed", a likely copy-paste artifact from the loader-side exception below, don't rely on the message text alone to tell a closed cursor from a closed loader.

`TickLoaderException` derives `std::runtime_error` and is the base for loader errors. `TickLoaderInterruptedException` and `TickLoaderClosedException` derive from it. `TickLoaderClosedException` is thrown internally when a loader's interruption handling determines the loader was closed cleanly rather than interrupted with an error.

Catch these by specific type when the task needs to distinguish a clean close/interruption from a genuine server-side error, catching the base `std::runtime_error` loses that distinction.

## Runtime field-access failures

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Garbled/misaligned field values | Wrong field order in `DataReader`/`DataWriter` calls | Re-confirm exact schema field order via `get_stream_schema` |
| Empty cursor | Wrong symbols, types, or time range | Narrow subscription, check `get_stream_symbols`/`get_stream_time_range` |
| `getStream` returns `nullptr` | Wrong stream key | MCP `list_streams` or explicit null check |
| Decimal64 field looks wrong | Missing/incorrect DFP conversion | Confirm DFP is linked and `Decimal64(...).toUnderlying()` (or `writeDecimal`) matches the schema's actual encoding |

## Topic publish/poll failures

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `trySend()`/`tryCommitMessage()` returns `BACK_PRESSURED` or `NOT_CONNECTED` | Transport buffer full, or no active subscriber yet | Retry, don't treat as a hard failure |
| `topicDataLossHandler` invoked on the consumer side | Poller fell behind the publisher | Return `true` to keep polling, or `false` to stop, decide based on whether losing messages is acceptable for the task |
| `processMessages` always returns 0 | Nothing available yet, or `isAtEnd()` | Poll in a loop, don't call it once and assume failure |

## Schema change failures

`TickStream::changeSchema` has no verified real usage example (see `schema-evolution.md`). If it throws or the applied change looks wrong, treat it as high-risk: stop, don't retry blindly, and confirm with the user before attempting again against real data.

## Memory and large reads

Add time bounds, symbol filters, and type filters before iterating, and stream results to disk instead of accumulating everything in memory.

## Repair workflow

1. Reproduce the failure mode: acquisition/link, build, connection, or runtime.
2. Check `project-setup.md` for acquisition/linking issues first, this is the most common source of C++-specific failures.
3. Verify stream/schema/symbols via MCP if available.
4. For write failures, reduce to one minimal `loader->send()` call before debugging larger flows.
5. Confirm the exact `DataReader`/`DataWriter` API against vendored headers (`project-setup.md`).
6. Apply the smallest fix.

## Build verification

**Agent mode:** run the project's actual build (`cmake --build .`, or the MSBuild equivalent) and report results.

**Ask/Plan mode:** provide verification commands and expected outcomes in a labeled section.
