# Workflow Selection

Choose the narrowest workflow that fits the task.

| Need | Primary path | Load next | Why |
| --- | --- | --- | --- |
| Unknown streams, schema, symbols, or time bounds | MCP-first discovery | `mcp-assisted-discovery.md` | Ground the code before guessing |
| Discovery-only answer from stream, schema, symbol, time-range, or server metadata | MCP only | `mcp-assisted-discovery.md` | Stop before Python when MCP already answers the request |
| Pure filter, projection, aggregation, grouped summary, or small result answer that QQL can fully answer and MCP can return directly | QQL plus MCP | QQL generator skill | Do not generate Python when client-side logic is unnecessary and no local artifact is needed |
| Large bounded extract, local file export, or post-processing, even when the query logic is simple | QQL plus Python | `advanced-recipes.md`, `pandas-analysis.md`, `cursor-and-streams.md` | Use MCP and QQL to narrow the read, then write, reshape, or compute locally instead of pushing large output through model context |
| Historical data into a table, CSV, parquet, or plot (local artifact or downstream Python work required) | pandas workflow | `pandas-analysis.md` | Best fit when Python must save, reshape, or visualize the result |
| Space-aware or partitioned stream read/write | cursor workflow for reads, pandas or loader write for writes | `cursor-and-streams.md`, `pandas-analysis.md` | Spaces require explicit selection or loading options instead of generic read/write helpers |
| DataFrame output when `read_frame` fails with native array resize errors | pandas fallback | `pandas-analysis.md`, `debugging-and-performance.md` | Switch to a Python-side fallback before rewriting QQL or connection logic |
| Live iteration, polymorphic messages, or event-driven logic | cursor workflow | `cursor-and-streams.md` | Avoid forcing streaming logic too early |
| Query plus downstream Python analysis | QQL plus Python | `advanced-recipes.md` | QQL narrows retrieval; Python saves, reshapes, computes, visualizes, or feeds another component |
| Reusable app, service, or component | application structure | `application-patterns.md` | Avoid collapsing larger work into one giant script |
| Missing package or version-sensitive API | install and inspect | `installation-and-editions.md`, `api-discovery.md` | Verify the real environment before claiming exact code |
| Explain or fix broken code | failure triage | `debugging-and-performance.md` | Start with the actual failure mode |

## Default playbook

1. If the request depends on actual server context, prefer MCP discovery first.
2. If MCP discovery or QQL can fully answer the request and the result can be returned directly, stop there and do not continue into Python.
3. Pick the smallest Python data access shape only after Python is clearly necessary.
4. If `read_frame` fails with array-resize errors, switch to the fallback path before rewriting QQL or connection logic.
5. If the user is building an app or service, choose an application structure before filling in code details.
6. Verify installation and API shape before using version-sensitive client methods.
7. Return a plot-ready DataFrame or reusable component before adding optional visualization or delivery layers.
8. When the task is mostly QQL design, hand off query construction to the QQL skill and keep this skill focused on the Python side.

## Quick routing rules

- Do not use this skill for stream, schema, symbol, time-range, or server-configuration lookup when MCP can answer directly.
- Do not use this skill for bounded filter, projection, aggregation, grouped summary, or small result answers when QQL plus MCP can fully answer the request and return the result directly.
- Do not escalate to Python just because QQL drafting was iterative or hit friction. Stay in the QQL generator skill unless the output size, artifact, or client-side processing requirement changes.
- Do not emit a Python script that only connects and executes the same QQL when QQL plus MCP could have returned the same answer directly.
- Use this skill for large bounded reads or exports when the result should be saved locally or would be too large to sensibly return through MCP output.
- Use pandas when the output should be tabular, exportable, or fed into matplotlib or plotly.
- Use cursors when the logic depends on message ordering, message types, or incremental state.
- Use application patterns when the user asks for an app, service, daemon, reusable module, or longer-lived workflow.
- Use schema inspection before writing polymorphic or package-entry logic.
- Use installation and edition guidance only when the user asks, the feature is gated, the package is missing, or the environment signals a mismatch.