# Stream Spaces

Use this reference only when the user's stream is explicitly organized into named "spaces" (a form of partitioning within a single stream, e.g. per-source or per-partition data that isn't naturally ordered against other spaces). Confirm space support via MCP/user context before generating space-specific code — do not invent space names. See [`examples/stream-spaces-read-write.md`](examples/stream-spaces-read-write.md) for the read/write pattern, name-encoding helper, and a lazily-created per-space loader.

Space names are round-tripped through a file-safe encoding when they appear in archive entry names (see `import-export.md`) — decode/encode with `SimpleStringCodec` rather than assuming the raw file name is the space name.

When writing to many spaces one after another (e.g. while importing an archive with one entry per space), defer `stream.createLoader(options)` until the first message for that space, since loader creation has overhead — a lazily-initializing wrapper is shown in the examples file.

## Common mistakes

- Inventing space names instead of grounding them from MCP/user input or discovering them from `stream.listSpaces()`.
- Mixing space-scoped and whole-stream reads/writes without realizing spaces partition the stream — a whole-stream `select`/loader (no `withSpace`) reads/writes across all spaces at once, which is rarely what's intended when spaces are in play.
