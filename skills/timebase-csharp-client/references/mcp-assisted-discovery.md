# MCP-Assisted Discovery

Prefer this workflow whenever the request depends on real TimeBase server context.

## Discovery order

1. `get_server_configuration`
   - This returns MCP server configuration, reachability of TimeBase instance may not be assumed from this, 
     unless MCP has already established a connection during a previous tool call.
   - Prefer `get_timebase_status`, if the target TB server supports it.
2. `list_streams`
   - Find candidate stream keys,
   - Avoid inventing stream names.
3. `get_stream_schema`
   - Ground message type names and field names for POCO generation.
4. `get_stream_time_range`
   - Learn whether the requested period is plausible.
5. `get_stream_symbols`
   - Confirm likely entity values before hardcoding them.
6. Identify the `InstrumentType` before calling `Select`:
   - Look up the `InstrumentType` in sample messages, loader code or ask the user.
   - Use that value in `InstrumentKey`. Do not assume any default type.
   - Wrong type may silently return zero rows at runtime.

## Required grounding

For tasks that depend on live stream shape, MCP discovery is required before generating bound C#:

1. `list_streams` to find the target stream key.
2. `get_stream_schema` to choose built-in vs custom types and field names.
3. `get_stream_symbols` / `get_stream_time_range` when subscriptions or time bounds matter.

## QQL interplay

- If the task needs QQL construction or repair, use the QQL generator skill.
- If the user supplies final QQL, return to this skill for `ExecuteQuery`, result POCO binding, and lifecycle.
- If iterative QQL drafting hits friction, stay in the QQL generator skill unless output size or a .NET artifact requirement changes.
- If the result set is too large for MCP output or should be saved locally, use MCP for discovery and query narrowing first, then switch to C# for read/export.

## Development-time vs runtime

MCP discovery grounds development assumptions. Generated .NET code should still:

- validate that streams exist (`GetStream` null checks),
- handle schema/runtime binding mismatches gracefully,
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
