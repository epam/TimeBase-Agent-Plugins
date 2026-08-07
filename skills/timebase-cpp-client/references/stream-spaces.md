# Stream Spaces

A space is a named partition within a stream. There is no explicit space-creation call, a space comes into existence the first time a loader writes to it with `LoadingOptions::space` set.

A loader writes into exactly one space (`LoadingOptions::space`, singular). Reading supports either a single space (`SelectionOptions::space`) or several at once (`SelectionOptions::spaces` plus a `withSpaces(...)` helper), only set one of the two. Ground the actual space name(s) via MCP, `TickStream::listSpaces()` or user input rather than inventing one.

`TickStream` also has `renameSpace(newName, oldName)`, `deleteSpaces(vector<string>)` (destructive and not reversible, confirm with the user before generating a call to it), and a space-scoped `getTimeRange(range, spaceName)`.

See [`examples/stream-spaces-read-write.md`](examples/stream-spaces-read-write.md) for the full read/write/manage flows.
