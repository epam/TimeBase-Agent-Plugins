---
name: timebase-python-client
description: Use when the user needs TimeBase Python client code, for example scripts, apps, services, local file export, large result extraction, pandas workflows, visualization prep, or downstream Python computation. Do not use for pure MCP discovery or pure QQL tasks answerable via QQL plus MCP without a Python artifact.
---

# TimeBase Python Client

## Mission

Generate TimeBase Python client solutions that are connection-aware, schema-aware, install-aware, and maintainable, from one-off scripts to reusable services and applications. Prefer MCP-grounded discovery when it is available, but keep moving with clearly labeled assumptions and bundled examples when it is not.

## Python Escalation Test

Before using this skill, confirm Python materially changes the deliverable or execution environment. Python is valid when the user needs:

- a Python script, app, service, or reusable component,
- local file export,
- large result extraction that is impractical to return through MCP output,
- downstream Python computation, reshaping, visualization, or integration.

Python is **not** valid when it would only connect and execute the same QQL and return the same result the agent could have provided directly via QQL plus MCP. QQL inside Python is appropriate when it narrows retrieval before saving, reshaping, computing, or feeding another component, not as a no-op wrapper around a direct answer.

## How to Route Requests

1. Decide whether Python is required at all:
   - If MCP discovery can fully answer the request, do not use this skill.
   - If QQL plus MCP can fully answer the request without client-side logic and without forcing a large result through model context, do not use this skill.
   - Do not escalate to Python just because QQL drafting was iterative or hit friction. Stay in the QQL generator skill unless the deliverable or scale requirement changes.
   - Continue when the user needs Python code, a reusable Python artifact, pandas or plotting preparation, client-runtime debugging, stateful stream logic, or a large bounded extract that should be written locally instead of returned through MCP output.
2. Identify the request type:
   - generate or refactor code for a script, app, service, or reusable component,
   - explain existing code,
   - debug or repair broken code,
   - design an analysis, ingestion, service, or visualization workflow,
   - improve performance or reliability.
3. Identify the data access pattern:
   - direct cursor iteration,
   - pandas ingestion or write-back,
   - QQL plus Python,
   - schema inspection,
   - polymorphic or package-style payload handling,
   - larger application structure.
4. Prefer MCP discovery before code generation when the task depends on live data shape:
   - confirm server configuration,
   - discover streams,
   - read schema,
   - check time range and symbols.
5. Open the smallest local references that match the request:
   - start with one workflow reference,
   - add recipe or example only when needed,
   - use debugging guidance only for failure analysis.

## Mandatory Policy

- Prefer MCP-first discovery for requests that depend on actual stream names, schema, symbols, time ranges, or edition detection.
- Do not use this skill for discovery-only tasks such as listing streams, inspecting schema, checking symbols, checking time ranges, or reading server configuration when MCP can answer directly.
- Do not generate Python for bounded filter, projection, aggregation, or export tasks when QQL plus MCP can fully answer the request, the result is small enough to return directly, and the user did not ask for a Python artifact.
- Python is a valid path for a simple read or export when the expected result is large enough that returning it through MCP would be impractical, or when the user needs the result saved to a local file or reusable local artifact.
- Do not block on MCP. If it is unavailable, continue with bundled examples and assumption-labeled scaffolding.
- Do not turn a normal answer into an edition-comparison exercise. Only surface edition choice when the user asks about it, installation or setup requires it, a feature is clearly edition-gated, or connection evidence makes it necessary.
- In generated code, prefer an explicit import that matches the installed client, such as `import dxapi as tb` or `import dxapi_ce as tb`. Avoid runtime import switching unless the user explicitly asks for a compatibility shim.
- Before relying on version-sensitive API details, confirm them against the installed client when possible. Prefer reading installed package files, wrapper modules, stubs, or pydoc output over trusting memory.
- Treat `pandas_utils.read_frame(...)` as a fast path, not a guarantee. If it fails with native NumPy array resize errors, treat NumPy >= 2.4 as the likely root cause rather than blaming the query first; switch to `pandas_utils.read_frame_dicts(...)` or a cursor-to-DataFrame fallback, or pin NumPy < 2.4 when the native path is required.
- If the client package is missing, say which package name is needed for the detected or assumed edition and how to verify the installation. On macOS and Linux distributions where Python is OS-managed, do not install into the global interpreter, instead create or reuse a virtual environment first (`python -m venv`, `uv venv`, poetry, etc.) and install only into that environment.
- Do not invent final schema facts, message type names, field names, enum values, stream keys, or edition-specific capabilities.
- If the task depends on stream spaces, confirm that the target stream supports them and whether reads should use `SelectionOptions.space` or `withSpaces(...)`, or writes should use `LoadingOptions.space`. Do not invent space names.
- When QQL authoring or repair is central to the task, use the QQL generator skill first and treat this skill as the Python-side companion.
- Keep connection and cursor lifecycle explicit. Open and close `TickDb` and cursor resources predictably.
- Be careful with large reads. Favor time bounds, symbol filters, field projection, or query narrowing before loading data into program memory.
- Surface edition uncertainty. Enterprise and community clients differ in packaging and some features; do not claim EE-only workflows for CE unless confirmed.
- For app or service requests, separate bootstrap, data access, transformation, and delivery concerns unless the user explicitly wants one file.
- Keep write paths explicit and user-intent driven. Do not write to streams unless the user asked for it.

## Reliability Rules

- Prefer `with` blocks when the API surface supports them; otherwise close resources in `finally` blocks.
- Start with read-only access unless mutation is required.
- Isolate installation or edition-specific logic near bootstrap instead of scattering it through the codebase.
- Prefer following the established sample style for example code: clear setup comments, explicit connection steps, and short inline explanations where they help the reader orient quickly.
- When building pandas workflows, call out memory tradeoffs and recommend selecting only required fields, symbols, and time ranges.
- When precision matters, avoid casual float assumptions and note any decimal or numeric encoding uncertainty.
- Distinguish stable API facts from version-sensitive guidance. If exact behavior may vary by installed package version, say so.
- If MCP is unavailable and the task is schema-dependent, state the missing context before presenting a final script.

## MCP-First Workflow

Use this order when MCP is available and the request depends on live server context:

1. `get_server_configuration` to learn connection state and likely edition.
2. `list_streams` to find candidate streams.
3. `get_stream_schema` for message types and fields.
4. `get_stream_time_range` and `get_stream_symbols` to narrow the read plan.
5. If MCP discovery already answers the request, stop there and do not continue into Python.
6. If the task needs QQL and MCP can return the final answer directly, use the QQL generator skill or narrow MCP query execution and stop there.
7. Continue into Python when the task still requires client-side logic, a reusable Python artifact, Python-specific debugging, or a large bounded extract that should be written locally rather than pushed through model context. If the task needs QQL, use the QQL generator skill. If that is unavailable, prefer `compile_query` before `execute_query`, and keep executions narrow.

If MCP is unavailable or fails, tell the user what is missing and continue with the nearest bundled example or assumption-labeled template.

## Capability Map

Use this map to load only the needed local materials:

- [`references/workflow-selection.md`](references/workflow-selection.md): choose between cursor iteration, pandas utilities, QQL plus Python, space-aware stream workflows, and visualization-ready pipelines.
- [`references/application-patterns.md`](references/application-patterns.md): structure reusable apps, services, and components instead of emitting one monolithic script.
- [`references/installation-and-editions.md`](references/installation-and-editions.md): decide when edition matters, install the right package, and verify what is actually installed.
- [`references/api-discovery.md`](references/api-discovery.md): how to find exact API details safely.
- [`references/pandas-analysis.md`](references/pandas-analysis.md): `read_frame`, `read_frame_dicts`, `bind_frame`, `write_frame`, filtering, field selection, DataFrame round trips, and space-aware write paths.
- [`references/cursor-and-streams.md`](references/cursor-and-streams.md): `TickDb`, `TickCursor`, `TickStream`, polymorphic reads, space-aware selection, historical vs live consumption, and resource patterns.
- [`references/advanced-recipes.md`](references/advanced-recipes.md): parameterized queries, order book analysis, schema inspection, CSV export, and plotting-ready transforms.
- [`references/debugging-and-performance.md`](references/debugging-and-performance.md): installation, connection, auth, edition mismatch, memory pressure, and repair workflow.
- [`references/mcp-assisted-discovery.md`](references/mcp-assisted-discovery.md): concrete MCP-first workflow and fallback behavior.

## Output Style

Return Python first, then short notes on assumptions, validation scope, installation or edition caveats only when relevant, and any MCP or schema gaps. Keep explanations concise unless the user asks for a deeper walkthrough.