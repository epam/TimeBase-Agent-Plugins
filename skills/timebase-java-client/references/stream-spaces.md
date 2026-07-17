# Stream Spaces

Use this reference only when the user's stream is explicitly organized into named "spaces" (a form of partitioning within a single stream). Confirm space support via MCP/user context before generating space-specific code, do not invent space names. See [`examples/stream-spaces-read-write.md`](examples/stream-spaces-read-write.md) for the read/write pattern, name-encoding helper, and a lazily-created per-space loader.

Space names are round-tripped through a file-safe encoding when they appear in archive entry names (see [`import-export.md`](./import-export.md)), decode/encode with `SimpleStringCodec` rather than assuming the raw file name is the space name.

When writing to many spaces one after another, defer `stream.createLoader(options)` per space until the first message for that space arrives, since loader creation has overhead. See the lazy per-space loader in [`examples/stream-spaces-read-write.md`](examples/stream-spaces-read-write.md).

## Common mistakes

- Inventing space names instead of grounding them from MCP/user input or discovering them from `stream.listSpaces()`.
- Mixing space-scoped and whole-stream reads/writes without realizing spaces partition the stream.
