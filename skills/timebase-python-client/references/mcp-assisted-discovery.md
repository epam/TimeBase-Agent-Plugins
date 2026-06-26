# MCP-Assisted Discovery

Prefer this workflow whenever the request depends on real TimeBase server context.

## Discovery order

1. `get_server_configuration`
   - confirm the connection target,
   - check whether the server seems reachable,
   - look for edition hints only if installation or a gated feature makes them relevant.
2. `list_streams`
   - find candidate stream keys,
   - avoid inventing stream names.
3. `get_stream_schema`
   - ground message type names and field names.
4. `get_stream_time_range`
   - learn whether the requested period is plausible.
5. `get_stream_symbols`
   - confirm likely entity values before hardcoding them.

## Why this matters

- It prevents invented stream keys and field names.
- It keeps generated code narrower and cheaper.
- It lets installation or edition guidance be evidence-based instead of speculative.

## QQL interplay

- If the task needs QQL construction or repair, use the QQL generator skill.
- If that skill is unavailable and MCP exposes query tools, prefer `compile_query` before `execute_query`.
- Keep executions narrow and use sample outputs only when raw message examples are truly needed.
- If iterative QQL drafting hits friction, stay in the QQL generator skill and keep using MCP query tools unless the output size, artifact, or client-side processing requirement changes.
- If the final result set is too large to sensibly return through MCP output or should be saved as a local artifact, use MCP for discovery and query narrowing first, then switch to Python for the actual read, export, or post-processing.

## Failure handling

A running MCP process does not guarantee that TimeBase is reachable.

If MCP calls fail:

1. say what discovery step failed,
2. keep going with bundled examples or user-provided schema,
3. label assumptions clearly,
4. do not present guessed schema facts as validated.

## What to surface in the answer

- Whether MCP grounded the stream and schema assumptions
- Any missing information the user should confirm before running the code
- Installation or edition caveats only when they materially affect the answer

## Suggested user-facing note

When MCP is missing or failing and the answer depends on live schema, include a short note like this:

`Note: TimeBase MCP is unavailable, so the code below uses assumptions for stream keys, schema, or symbols that may need confirmation.`