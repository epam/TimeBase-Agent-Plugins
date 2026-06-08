# Pandas Analysis

Use pandas when the task is bounded, tabular, and analysis-heavy, whether the result is a one-off report or part of a larger app.

## Best-fit cases

- Historical bars, trades, or BBO data into a DataFrame
- Feature engineering, rolling metrics, resampling, export, or plotting
- Pre-plot shaping for matplotlib or plotly
- Service or application layers that want a rectangular intermediate representation

## Read pattern

`pandas_utils.read_frame(...)` is the fast path when the native DataFrame read works in the current environment. Native `read_frame` is currently incompatible with NumPy >= 2.4.

Common inputs:

- `streams=[...]` for stream reads
- `query="..."` when QQL should define the result set
- `fields=[...]` to reduce width
- `tickers=[...]` to reduce entity count
- `types=[...]` to reduce message variety
- `from_time_str` and `to_time_str` to bound the scan

### Native `read_frame` failure signatures

Failures such as `cannot resize an array that may be referenced by another object` or `Error resizing NumPy array!` point to the native `_readAsFrame` path rather than to user QQL or connection logic.

### Fallback path

Keep the same bounded inputs and switch the DataFrame construction path before rewriting the query or connection flow. Try `pandas_utils.read_frame_dicts(...)` as a pragmatic Python-side fallback, or build a DataFrame from cursor rows manually if you need more control. NumPy >= 2.4 is the core issue for the native `read_frame` path, and NumPy < 2.4 is the fix when that native path is required.

If `query` is provided, treat it as the source of truth for result shape.

Start from `examples/basic-pandas-read.py` for the fast path. If you need the Python-side fallback, use `examples/pandas-read-dicts.py`.

## Write-back pattern

1. Read or construct the DataFrame.
2. Use `pandas_utils.bind_frame(...)` to map DataFrame columns to the target stream.
3. Write with `pandas_utils.write_frame(...)` only when the user explicitly wants stream output.

Start from `examples/pandas-roundtrip.py`.

## Space-aware DataFrame workflows

- `pandas_utils.read_frame(...)` and `pandas_utils.read_frame_dicts(...)` do not expose a `space` or `spaces` argument.
- If the read must target specific spaces, prefer cursor-based selection with `SelectionOptions.space` or `withSpaces(...)`, then build the DataFrame in Python.
- For DataFrame writes into a specific space, create `LoadingOptions()`, set `options.space`, and pass it to `pandas_utils.write_frame(db, binding, frame, options=options)`.
- If space selection is central to the task and live stream context is unknown, do not guess the space names.

## Memory and scale rules

- Always prefer field projection over loading the full message.
- Apply time bounds early.
- Filter by symbols or message types when possible.
- Prefer server-side QQL filtering before pandas when the raw stream is large.
- Do not recommend loading unbounded live data directly into a DataFrame.
- Wide order book outputs can become expensive fast; trim depth and fields first.

## Visualization guidance

- Default to returning a clean DataFrame first.
- Add plotting only if the user asked for it.
- Sort or index by timestamp before plotting or resampling.
- Keep timestamps and numeric columns clean before charting.

Start from `examples/visualize-bars.py`.

## Common pitfalls

- Forgetting to close the database connection after `read_frame`
- Pulling too many columns into memory
- Assuming numeric fields are always non-null
- Mixed message types producing sparse or awkward frames
- A NumPy >= 2.4 native `read_frame` failure does not mean the query or connection is broken
- Writing back to a stream without checking the binding result