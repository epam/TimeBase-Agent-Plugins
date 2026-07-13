# Debugging And Performance

Use this reference when setup, connection, binding, or performance fails.

## NuGet and feed failures

| Symptom | Likely cause | Check |
| --- | --- | --- |
| 401/403 on restore | Missing or wrong `NEXUS_USER` / `NEXUS_PASS` | Env vars, `NuGet.config` |
| Package not found | Feed not configured | `NuGet.config` has Deltix.NET source |

Report missing or incorrect NEXUS credentials and point the user at env vars / `NuGet.config` placeholders.

## Build failures

| Symptom | Likely cause | Check |
| --- | --- | --- |
| Type not found | Missing package reference | `.csproj` has Api + Client |
| TFM not supported | Package vs target framework mismatch | Preserve or adjust TFM |
| Binding errors | Wrong namespace or missing `using` | `Deltix.Timebase.Api`, `.Client`, `.Communication`, `.Utilities.Binding`, etc. |

## Connection failures

- Verify URL format: `dxtick://host:port`
- Confirm server is reachable.
- For basic auth, make sure credentials are passed to db connection creation 
  and user confirms their validity.
- For OAuth2, confirm token acquisition succeeds before `db.Open`.
- Set `db.AccessToken` before opening when using bearer auth.

## Binding failures at runtime

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `GetMessage()` returns base type only | Missing or wrong `TypeLoader` | Add `TypeLoader(typeof(YourMessage))` |
| Null stream | Wrong stream key | MCP `list_streams` or `GetStream` null check |
| Empty cursor | Wrong symbols, types, or time range | Narrow subscription, check `get_stream_symbols` |
| QQL binding mismatch | Result POCO fields don't match projection | Align property names with QQL select list |

## Raw vs bound mode

- `SelectionOptions.Raw = false` with `TypeLoader`, bound POCOs.
- `SelectionOptions.Raw = true`, raw/generic messages.
- Do not mix expectations: bound code should not assume POCO properties in raw mode.

## Memory and large reads

- Add time bounds, symbol filters, and type filters before iterating.
- Stream to disk (CSV/JSON) instead of accumulating all messages in a `List<T>`.
- Prefer narrowing before client-side iteration when possible.

## Live cursor issues

- Ensure `SelectionOptions.Live = true` and correct start time.
- Dispose `LiveCursorWatcher` and cursor on shutdown.
- Handle cancellation in background workers.

## Repair workflow

1. Reproduce the failure mode (build, restore, connection, or runtime).
2. Check project setup and package versions.
3. Verify stream/schema/symbols via MCP if available.
4. For write failures, reduce to one minimal `loader.Send(...)` call before debugging larger flows.
5. Inspect `TypeLoader`, live schema, QQL type names, and result POCOs.
6. If the stream already exists, verify schema drift.
7. Apply the smallest fix, do not rewrite the entire project.

## Build verification

**Agent mode:** run `dotnet restore` and `dotnet build`, report results.

**Ask/Plan mode:** provide verification commands and expected outcomes in a labeled section.
