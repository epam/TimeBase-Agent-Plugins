# Query, selection, charting, and flowchart

## Query and selection

The inventory covers `GET`/`POST /select`, stream- and symbol-scoped selection, `/query`, `/unlimitedQuery`, `/filter`, `/compileQuery`, `/describe`, and `/query-info/functions*`.

`select`, `query`, `unlimitedQuery`, and `filter` default to numeric JSON
encoding. When a JavaScript, Go, or other client must preserve 64-bit values,
send `X-JSON-BigInt-Encoding: string` and parse the affected values as strings.
Never silently coerce those strings through a floating-point number.

Use `qql-generator` to author or repair QQL. WebAdmin selection/query responses are streaming. Normal select/filter/query paths apply the configured server record cap; `/unlimitedQuery` bypasses it. Prefer bounded requests and local artifacts over loading large results into model context.

`compileQuery` is parser diagnostics, not semantic validation. For QQL that changes server state, follow [`writes-and-confirmation.md`](writes-and-confirmation.md) even when a query endpoint admits it.

## Charts, order book, and flowchart

Use `GET /api/v0/charting/dx/{streamKey}` for stream charting and `POST /api/v0/charting/dx-query` for QQL charting. Verify each operation's parameters and request body against the target contract. Both use a correlation ID from `/api/v0/correlationId` for cancellation through `GET /api/v0/charting/dx/stopCharting`. That cancellation changes state despite using `GET`. Treat chart response framing as a target-server check.

Order-book snapshot/source operations and `GET /api/v0/flowchart` are read integrations. Flowchart combines a REST snapshot with STOMP updates; metadata uses `/user/topic/flowchart/metadata`.

Use a timeout and explicit result limit. Include `stopCharting` for the helper's own correlation ID in its authorized cancellation and cleanup path, following [`writes-and-confirmation.md`](writes-and-confirmation.md). Check response framing on the target deployment and read [`stomp-client.md`](stomp-client.md) when flowchart events are needed.

Message timestamps are ISO strings, separate from numeric INT64 fields. Preserve nanosecond precision, such as `2026-01-01T00:00:00.123456789Z`, when parsing them. Playback request timestamps use a different parser; follow the playback reference for that request shape.
