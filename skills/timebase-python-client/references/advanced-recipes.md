# Advanced Recipes

Use this reference for tasks where plain reads are not enough.

## Parameterized query plus Python

Use parameterized queries when the user wants reusable filters without string interpolation.

Pattern:

1. Build the query with named parameters.
2. Pass `QueryParameter` objects to `tryExecuteQuery`.
3. Keep the query bounded and iterate the cursor.
4. Convert the result into rows or a DataFrame only if the task needs it.

Start from `examples/parameterized-query.py`.

## QQL plus Python analysis

Use when raw stream data is too large, needs server-side shaping, or requires downstream Python work beyond a direct MCP answer.

Pattern:

1. Use the QQL skill to generate or repair the query text.
2. Execute the query from Python.
3. Convert the result into rows or a DataFrame when the task needs local persistence or further processing.
4. Save to file, export, visualize, compute, or feed the result into an app component.

Do not use this pattern when Python would only execute the same QQL and return the same result that QQL plus MCP could have provided directly. QQL narrows retrieval; Python must add saving, reshaping, computation, visualization, or integration.

## Order book analysis

There are two main approaches:

1. Let TimeBase shape the data first with QQL, then flatten the result in Python.
2. Reconstruct the book event by event in Python when custom state handling is required.

Prefer the first path when the server can narrow the payload materially.

Start from `examples/orderbook-analysis.py`.

## Schema introspection

Inspect metadata before writing logic around assumed message types or nested fields.

Start from `examples/schema-introspection.py`.

## Export and downstream integration

When the result is DataFrame-shaped:

- export to CSV or Parquet,
- compute rolling metrics,
- prepare a plotting-ready frame,
- hand the frame to an API, worker, or visualization layer.

Prefer returning the transformed DataFrame or reusable function first. Add export or visualization only if the user asked for it.

## Multiplexed cursor

Multiplexed cursors are useful when the user explicitly needs one ordered consumer across multiple streams or mixed stream-plus-QQL subscriptions.

Treat this as version-sensitive. Start from `examples/multiplexed-cursor.py` only when the installed client and server support are confirmed.