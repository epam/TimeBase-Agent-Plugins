# MCP-Assisted Discovery

Prefer this workflow whenever the request depends on real TimeBase server context.

## Discovery order

1. `get_server_configuration`
   - Returns MCP server configuration. Reachability of the TimeBase instance may not be assumed from this alone, unless MCP has already established a connection during a previous tool call.
   - Prefer `get_timebase_status` if the target server supports it.
2. `list_streams`
   - Find candidate stream keys.
   - Avoid inventing stream names.
3. `get_stream_schema`
   - Ground field names, types, and declared order before writing `DataReader`/`DataWriter` field access code. Field access is positional, order matters as much as names.
4. `get_stream_time_range`
   - Learn whether the requested period is plausible.
5. `get_stream_symbols`
   - Confirm likely entity values before hardcoding them in an `InstrumentIdentity` list.

## Required grounding

For tasks that depend on live stream shape, MCP discovery is required before generating field-access code:

1. `list_streams` to find the target stream key.
2. `get_stream_schema` to confirm exact field names, types, declared order, and whether `Decimal64` conversions are needed.
3. `get_stream_symbols` / `get_stream_time_range` when subscriptions or time bounds matter.

## QQL interplay

- If the task needs QQL construction or repair, use the QQL generator skill.
- If the user supplies final QQL, return to this skill for `TickDb::executeQuery` and cursor iteration.
- If iterative QQL drafting hits friction, stay in the QQL generator skill unless a C++ artifact requirement changes.

## Development-time vs runtime

MCP discovery grounds development assumptions. Generated C++ code should still:

- validate that streams exist (`getStream` null/nullptr checks),
- handle schema/runtime field-access mismatches gracefully (a wrong field order in `DataReader`/`DataWriter` calls fails at runtime, not compile time),
- label any remaining assumptions clearly.

## Failure handling

If MCP calls fail:

1. say what discovery step failed,
2. continue with bundled examples or user-provided schema,
3. label assumptions clearly,
4. do not present guessed schema facts as validated.

## Suggested user-facing note

When MCP is missing and the answer depends on live schema:

`Note: TimeBase MCP is unavailable, so the code below uses assumptions for stream keys, schema, or symbols that may need confirmation.`
