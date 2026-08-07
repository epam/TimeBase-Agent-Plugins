# Debugging And Performance

Use this reference when setup, connection, binding, or performance fails.

Examples below use the Enterprise Edition `deltix.*` package root. See the package-root mapping and edition differences in [`project-setup.md`](project-setup.md#package-roots-in-this-skills-examples) before applying these examples to a Community Edition project.

## Dependency and repository failures

| Symptom | Likely cause | Check |
| --- | --- | --- |
| 401/403 on dependency resolution | Missing or wrong repository credentials | Env vars, repository config block |
| Dependency not found | Repository not configured | `build.gradle`/`pom.xml` has the TimeBase repository |

Report missing or incorrect repository credentials and point the user at env vars / repository config placeholders.

## Build failures

| Symptom | Likely cause | Check |
| --- | --- | --- |
| Type not found | Missing dependency | Build file has client + api-messages dependencies |
| Java version mismatch | Client version vs Java toolchain mismatch | Preserve or adjust Java version |
| Binding errors | Wrong package import | `deltix.qsrv.hf.tickdb.pub`, `deltix.qsrv.hf.pub`, `deltix.qsrv.hf.pub.md`, etc. |

## Connection failures

- Verify URL format: `dxtick://host:port` (or `dstick://host:port` for SSL).
- Confirm the server is reachable.
- For basic auth, make sure credentials are passed when creating the connection and the user confirms their validity.
- For OAuth2, confirm the client-credentials flow succeeds before `db.open(...)`.

## Detecting and recovering from mid-session disconnects

A `DXTickDB` connection can drop after it's already open (network blip, server restart), this is different from a failed initial connection. Detect it with `DisconnectEventListener`, registered via the `Disconnectable` interface that connection implementations expose (`((Disconnectable) db).addDisconnectEventListener(listener)`). Only add this when the task is specifically about long-lived connection resilience (e.g. a background service), a short-lived script doesn't need it. See [`examples/reconnect-handling.md`](examples/reconnect-handling.md) for the full pattern that pauses a loader loop while disconnected and resumes on `onReconnected()`.

## Binding failures at runtime

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `getMessage()` returns base type only | Wrong or missing type in the `types[]` filter | Pass the concrete message class name(s) to `select`/`executeQuery` |
| Null stream | Wrong stream key | MCP `list_streams` or `db.getStream` null check |
| Empty cursor | Wrong symbols, types, or time range | Narrow subscription, check `get_stream_symbols` |
| QQL binding mismatch | Result type fields don't match projection | Align field names with the QQL select list |

## Raw vs bound mode

- `SelectionOptions.raw = false` with a bound `InstrumentMessage` subclass.
- `SelectionOptions.raw = true` with `RawMessage` and manual decoding via `CodecFactory`/`UnboundDecoder`.
- Do not mix expectations: bound code should not assume `RawMessage` fields, and raw-mode code should not cast to a bound type.

## Memory and large reads

- Add time bounds, symbol filters, and type filters before iterating.
- Stream results to disk (CSV/JSON) instead of accumulating all messages in a `List`.
- Prefer narrowing the subscription before client-side iteration when possible.

## Live cursor issues

- Ensure `SelectionOptions.live = true` and a correct start time.
- Close the cursor on shutdown. If using a background-thread watcher, stop it explicitly too.
- Handle cancellation/interruption in background reader threads.

## Repair workflow

1. Reproduce the failure mode (build, connection, or runtime).
2. Check project setup and dependency versions.
3. Verify stream/schema/symbols via MCP if available.
4. For write failures, reduce to one minimal `loader.send(...)` call before debugging larger flows.
5. Inspect message type filters, live schema, QQL type names, and result field names.
6. If the stream already exists, verify schema drift.
7. Apply the smallest fix, do not rewrite the entire project.

## Build verification

**Agent mode:** run `./gradlew build` or `mvn compile`, report results.

**Ask/Plan mode:** provide verification commands and expected outcomes in a labeled section.
