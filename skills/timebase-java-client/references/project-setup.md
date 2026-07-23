# Project Setup

Use this reference when setting up or integrating the TimeBase Java client.

## Editions

TimeBase Java ships as two separate client libraries, Community Edition and Enterprise Edition. Do not assume they are API-identical. Only use the coordinates and package root that match the resolved edition below.

- **Community Edition**: `org.finos.timebase-ce:timebase-client:<version>` and `com.epam.deltix:timebase-messages:<version>`, from Maven Central, no credentials. Package root `com.epam.deltix.*`.
- **Enterprise Edition**: `deltix.qsrv.timebase:deltix-timebase-client:<version>` and `deltix.qsrv:deltix-timebase-api-messages:<version>`, from `https://nexus.deltixhub.com/repository/epm-rtc-public-java`, credentials via `NEXUS_USER`/`NEXUS_PASS` or the project's existing convention if different. Package root `deltix.*`.

Don't hardcode a version, both editions release frequently. Use whatever is already pinned in the project, or ask the user to check the current release.

## Which edition? Resolution order

1. Existing project: use whatever edition its dependencies already show. Do not switch it.
2. New project, server reachable via MCP: try `get_timebase_status` first. Fall back to `get_server_configuration`'s `edition` field if that's unavailable. Confirm with the user before writing dependency coordinates either way, don't act on the MCP result silently.
3. No project and no server connection: ask the user directly. Never guess.

## Package roots in this skill's examples

Most worked examples in this skill use the Enterprise Edition `deltix.*` root. For the core client API, Community Edition mechanically swaps it for `com.epam.deltix.`:

| Enterprise Edition | Community Edition |
| --- | --- |
| `deltix.qsrv.hf.tickdb.pub.DXTickDB` | `com.epam.deltix.qsrv.hf.tickdb.pub.DXTickDB` |
| `deltix.qsrv.hf.tickdb.pub.TickDBFactory` | `com.epam.deltix.qsrv.hf.tickdb.pub.TickDBFactory` |
| `deltix.qsrv.hf.tickdb.pub.DXTickStream` | `com.epam.deltix.qsrv.hf.tickdb.pub.DXTickStream` |
| `deltix.qsrv.hf.tickdb.pub.TickLoader` | `com.epam.deltix.qsrv.hf.tickdb.pub.TickLoader` |
| `deltix.qsrv.hf.tickdb.pub.StreamOptions` | `com.epam.deltix.qsrv.hf.tickdb.pub.StreamOptions` |
| `deltix.qsrv.hf.tickdb.pub.StreamScope` | `com.epam.deltix.qsrv.hf.tickdb.pub.StreamScope` |
| `deltix.qsrv.hf.pub.md.RecordClassDescriptor` | `com.epam.deltix.qsrv.hf.pub.md.RecordClassDescriptor` |
| `deltix.qsrv.hf.pub.md.Introspector` | `com.epam.deltix.qsrv.hf.pub.md.Introspector` |

`InstrumentMessage` and built-in message types are the exception, see `message-types-and-schema.md` for the details (different package family, and Community Edition has no built-in bar/candle type).

## Credentials

Never hardcode secrets, never overwrite an existing repository/credential setup, prefer environment variables and preserve whatever naming convention the project already uses. A 401/403 on dependency resolution means the configured credentials are missing or wrong.
