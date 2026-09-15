# Runtime triage

Use these MCP tools when logs are absent, or when logs alone do not narrow the problem enough.

Some monitoring-style MCP tools have limited TimeBase server version support. In particular, `list_timebase_activity`, `get_timebase_activity_detail`, and `get_timebase_status` may be unavailable on older or less capable servers. If they fail for support reasons, say so plainly and continue with other evidence.

## When runtime inspection helps most

Use runtime inspection when the user reports:

- stuck or leaking cursors
- blocked or failing loaders
- suspicious connection churn
- lock contention
- a problem tied to one stream, one symbol set, or a recent live incident

## Activity tools

Use these when the issue is about live server state rather than a historical stack trace.

- `list_timebase_activity`
  - Good first step for active cursors, loaders, connections, and locks.
  - Use it to see whether the problem is live, widespread, or isolated.
  - This has limited server-version support.
- `get_timebase_activity_detail`
  - Use after `list_timebase_activity` when one cursor, loader, connection, or lock looks suspicious.
  - Good for narrowing one concrete suspect instead of speaking in generalities.
  - This has limited server-version support.

## Instance and version context

Use these when configuration, version, license, or edition may matter.

- `get_server_configuration`
  - Confirm which instance the user is actually targeting.
  - Useful when there may be several environments or the MCP is pointed somewhere unexpected.
  - This does not prove the target server is reachable or healthy. It only shows what MCP is configured to use.
- `get_timebase_status`
  - Use when version, runtime environment, or license state changes the diagnosis.
  - This also has limited server-version support.

## Stream-side inspection

Use these when the failure points to a specific stream, damaged data, or unexpected message flow.

- `list_streams`
  - Confirm the stream exists and get the exact key.
- `get_stream_schema`
  - Use when the issue may involve message types, field layout, or schema drift.
- `get_stream_time_range`
  - Useful when the reported time window looks wrong or data seems missing.
- `get_stream_symbols`
  - Use when a failure may be tied to a particular symbol set or an unexpectedly empty read.
- `get_stream_messages`
  - Use for a small direct preview when seeing real messages will settle the question faster than guessing.

## How to choose

A simple rule:

- start with `search_logs_kb` when you have a useful log excerpt
- start with activity tools when logs are absent or weak and the problem is clearly live and operational
- use stream tools when the problem is tied to a specific stream or data slice
- use status and configuration tools when environment or version may be the real issue

## Answering guidance

Do not dump tool output back at the user.

Instead:

- say what the runtime evidence shows
- say why it matters
- say the next thing to check or do

If runtime evidence contradicts the closest KB match, trust the runtime evidence and explain the mismatch.