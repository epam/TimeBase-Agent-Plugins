# Connection And Lifecycle

Use this reference for opening and closing a TimeBase connection from C++.

## Connecting

`TickDb::createFromUrl(url)` opens a connection, `db->open(readOnlyMode)` and `db->close()` bracket its use. A second `createFromUrl` overload takes explicit basic-auth credentials instead of embedding them in the URI: `createFromUrl(url, username, password)`. See [`examples/connect-list-streams.md`](examples/connect-list-streams.md) for the full connect/open/close flow.

Wrap `TickDb` in `std::unique_ptr` and call `close()` on every exit path, including exceptions.

## Connection URI schemes

| Scheme | Meaning |
| --- | --- |
| `dxtick://` | Direct connection, unencrypted |
| `dstick://` | Direct connection, SSL required |
| `dxctick://` | Cluster connection, unencrypted |
| `dsctick://` | Cluster connection, SSL required |

Cluster URIs accept multiple `host:port` pairs separated by `|`.

Credentials can also be embedded directly in the URI:

```
dxctick://user:Pa$$w0rd@host1:9000|1.2.3.4:9000
```

Prefer the `createFromUrl(url, username, password)` overload over embedding credentials in the URI for generated code, and never hardcode real credentials, use a placeholder consistent with `project-setup.md`.

## Token-based auth

`TickDb::setAccessToken(const std::string &token)` sets a bearer token (OAuth2) for authentication instead of a username/password. Fall back to `createFromUrl(url, username, password)` for basic auth when a token isn't available or not needed.

`TickDb::setApplicationName(const std::string &name)` identifies the connecting application to the server, useful for distinguishing clients in server-side logs/monitoring. Set it once after connecting, it isn't required for the connection itself to succeed.

## SSL and environment variables

| Variable | Purpose |
| --- | --- |
| `SSL_CERT_FILE` | Path to a specific CA certificate file |
| `SSL_CERT_DIR` | Path to a directory of trusted CA certificates |
| `DXAPI_SSL_TRUST_ALL` | Disable certificate validation |
| `DXAPI_LOG_LEVEL` | Client-side log verbosity |

Only set `DXAPI_SSL_TRUST_ALL` for a non-production case the user explicitly asked for.

## Read-only vs read-write

Start with `db->open(true)` unless the task requires writes. `db->isReadOnly()` reports how the connection was actually opened, check it before attempting a write rather than assuming. `db->isOpen()` reports whether the connection is currently open at all, useful before calling anything that requires an active connection after a `close()` may have already happened elsewhere.

## Wiping a database

`db->format()` deletes every stream and space in the database, it is destructive and not reversible. Treat it the same as `TickStream::clear()`/`deleteSpaces`/`changeSchema`: confirm with the user before generating a call to it.
