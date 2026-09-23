# Exports and artifacts

## Operations

| Workflow | Operation and result |
| --- | --- |
| Direct stream download | `GET /api/v0/{streamId}/export` returns `application/octet-stream` directly. Its query parameters do not include `format`; do not use it to select QSMSG. |
| Prepared stream export | `POST /api/v0/{streamId}/export` accepts a JSON body with `format`, including `QSMSG` or `CSV`, and returns a download ID. |
| Multi-stream export | `GET` or `POST /api/v0/export`; check each method's distinct request and response contract. |
| QQL export | `POST /api/v0/export-query` returns a download ID. |
| Prepared artifact retrieval | `GET /api/v0/download?id=...` streams the artifact identified by a preparation response. |

For a prepared export, validate the response shape and require a non-empty string `id` before requesting `/download`. The OpenAPI contract can declare HTTP 201 while the target server returns HTTP 200 with a valid ID. Accept that operation-specific HTTP 200 correction when the complete response validates; do not accept arbitrary 2xx statuses or a partial response. A missing or invalid ID is a failed preparation.

For a whole-stream QSMSG export, use the POST body with `format: "QSMSG"` and omit `from` and `to` unless the user wants a time range. Apply requested stream, symbol, type, time, offset, and row bounds. If a reliable count is available, use it as a finite `rows` bound and account for writes after the count. If the user requests the full stream and no reliable count is available, `rows: -1` is explicit unbounded server work; keep a total deadline and download byte and disk limits, and report any incomplete result. Do not choose an arbitrary finite row cap that silently truncates the requested export.

When `from` or `to` is needed for stream export, send UTC timestamps with exactly three fractional digits, such as `2026-09-07T10:29:57.516Z`. Do not pass a higher-precision MCP range string such as `.516000Z` through unchanged. Floor the inclusive `from` to milliseconds and round the inclusive `to` up to the next millisecond so a message at `.768388Z` is not excluded by `.768Z`. This rounding can include messages just outside a user-specified range; report that precision limit. Verify the target server's parser before applying a different timestamp format.

The server streams `application/octet-stream` from `/download` and returns `404` for an unavailable ID. The browser flow receives a short-lived, path-scoped temporary download cookie during preparation. Verify direct bearer-token download behavior against the target deployment rather than assuming browser behavior transfers to a headless helper.

Send `Accept: application/octet-stream` on artifact retrieval. Preserve the compression format and an appropriate filename extension; a QSMSG export can be gzip-compressed and needs a `.qsmsg.gz` filename for reimport. Handle response filenames through the destination rules below.

For QQL export, send `{query, format}` to `POST /api/v0/export-query`, read its `id`, then retrieve that ID through `/download`. Do not assume inherited `rows`, `offset`, `from`, or `to` fields bound this operation. Verify their effect on the target server, bound the QQL itself, or choose bounded stream export. A download byte cap does not bound server-side query work.

## Safe artifact downloads

Apply this lifecycle to exports, validation reports, import logs, and other downloaded artifacts:

1. Use the caller's destination path. If the caller supplies only an output directory, treat the response filename as a suggested basename and reject path components or traversal. Preserve an existing destination unless replacement is authorized.
2. Create a unique temporary file exclusively in the destination directory and track it as owned by this run. Stream into that file under the shared [HTTP request requirements](endpoint-contract.md#http-requests). Keep the total deadline in force through completion of the file write.
3. Publish only after [response validation](endpoint-contract.md#validate-responses) and complete transfer, with the file flushed, the response and file closed without error, and no cancellation or deadline expiry. Use an atomic operation that fails if the destination exists unless replacement is authorized. An early existence check alone does not prevent overwriting a file created during the download. For authorized replacement, atomically replace the destination only with the completed file.
4. Close the response and file on every exit path, then remove any unpublished temporary file owned by this run. Follow [resource ownership and cleanup](client-lifecycle.md#resource-ownership-and-cleanup) so a close failure does not prevent the remaining cleanup. Failed downloads leave the destination untouched and report an incomplete result; if removal fails, include the remaining temporary path and a warning. Report a final artifact path only after publication succeeds. Use the [output rules](../SKILL.md#output) for library results and CLI manifests.
