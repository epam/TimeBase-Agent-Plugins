# Debugging And Performance

Use this reference when the user has a failure, a scaling concern, or a deployment issue.

## Fast triage

| Symptom | Likely cause | First move |
| --- | --- | --- |
| `ImportError: dxapi` or `dxapi_ce` | Client not installed, wrong package, or script run outside the venv where it was installed | Load `installation-and-editions.md`, verify the active venv, and avoid global pip on macOS/OS-managed Linux |
| Error mentions enterprise or community version required | Package-server edition mismatch | Surface the mismatch and re-check package choice |
| Connection open fails | Bad URI, auth issue, SSL setup, or server unavailable | Check URI scheme, credentials, MCP status, and logging |
| Stream not found | Wrong stream key or wrong environment | Prefer MCP discovery or list streams before changing code |
| Pandas load is too large | Unbounded read or too many columns | Add time, symbol, field, or QQL narrowing |
| `pandas_utils.read_frame(...)` fails with `cannot resize an array that may be referenced by another object` or `Error resizing NumPy array!` | Native `_readAsFrame` path failure caused by NumPy >= 2.4 | If the native path is required, use NumPy < 2.4; otherwise retry with `read_frame_dicts(...)` or a cursor-to-DataFrame fallback and keep the query bounded |
| Query is slow or expensive | Wide scan or unnecessary client-side filtering | Push filtering into QQL and narrow execution |

## Connection and environment reminders

- TimeBase connection URIs commonly use `dxtick://`, `dstick://`, `dxctick://`, or `dsctick://`.
- SSL and certificate issues often depend on `SSL_CERT_FILE`, `SSL_CERT_DIR`, `DXAPI_SSL_TRUST_ALL`, or `DXAPI_SSL_TERMINATION`.
- If logging is needed, enable or inspect `DXAPI_LOG_ENABLE`, `DXAPI_LOG_LEVEL`, and more specific cursor or loader log-level variables.

If MCP exists, use `get_server_configuration` before rewriting working client logic.

## Native DataFrame path failures

If the same bounded query works through `tryExecuteQuery` and `getMessage()` iteration or through `pandas_utils.read_frame_dicts(...)`, the issue is in the native DataFrame path rather than in QQL or connection logic. Treat NumPy >= 2.4 as the primary environment cause, switch to the fallback DataFrame path first, and pin NumPy < 2.4 when the native path must be preserved.

## Performance rules

- Narrow reads before optimizing anything else.
- Prefer server-side filtering or aggregation when a full raw scan is not necessary.
- Avoid loading large unbounded result sets into pandas.
- Keep live ingestion, plotting, and export as separate stages when possible.
- For larger apps, isolate transport and analysis so you can profile them separately.

## Buffer and loader tuning clues

If the user is diagnosing throughput or backpressure, inspect these environment variables:

- `DXAPI_LOADER_MIN_CHUNK_SIZE`
- `DXAPI_LOADER_MAX_CHUNK_SIZE`
- `DXAPI_LOADER_CLOSE_TIMEOUT_MS`
- `DXAPI_LOADER_RECV_BUFFER_SIZE`
- `DXAPI_LOADER_SEND_BUFFER_SIZE`
- `DXAPI_CURSOR_RECV_BUFFER_SIZE`
- `DXAPI_CURSOR_SEND_BUFFER_SIZE`

## Version-sensitive feature gates

- Multiplexed cursors require recent client and server support. Treat them as unavailable until confirmed.
- If a task mentions spaces, confirm stream support and inspect `SelectionOptions.space`, `withSpaces(...)`, `LoadingOptions.space`, or stream space-management methods before generating code.
- If a task mentions locks, rename instruments, or delete data APIs, call out version sensitivity instead of assuming support.

## Repair workflow

1. Confirm package installation and import path.
2. Confirm connection URI and auth assumptions.
3. Confirm stream key and schema.
4. Reduce the read to a minimal bounded case.
5. Rebuild complexity one layer at a time.