# API Discovery

Use this reference when you need exact method names, signatures, or capability checks from the real installed client rather than from memory.

## Safe discovery order

1. Start with the bundled references and examples in this skill.
2. If MCP is available, use it to ground server, schema, and edition clues.
3. Verify which client package is installed.
4. Read the installed package files or wrapper modules before assuming advanced or version-sensitive APIs exist.
5. Use pydoc or `help()` when the installed package is native or generated and the file layout alone is not enough.
6. Ask for missing version or environment details rather than inventing an exact API surface.

## Preferred inspection workflow

1. Determine the explicit import that matches the environment.

```python
import dxapi as tb
```

or

```python
import dxapi_ce as tb
```

2. Locate the installed module with `tb.__file__`.
3. Read nearby installed files in the active environment, especially:
   - generated wrapper modules such as `__init__.py`,
   - any `.pyi` stubs,
   - nearby helper modules shipped with the package.
4. If needed, supplement that with `python -m pydoc dxapi.TickDb` or `help(tb.TickDb)`.

## What to confirm

- the installed module path
- the explicit import path that matches the environment
- method signatures for `TickDb`, cursors, stream selection, and loaders
- whether `pandas_utils` is shipped for the installed client package
- whether a clearly gated API is present in the installed package or documented for that version

## Guardrails

- Prefer reading installed sources or generated wrappers over `dir()` or `hasattr()`-driven discovery.
- Native bindings may still require `help()` or pydoc to recover doc comments and signatures cleanly.
- Do not claim an exact method name or keyword argument unless it is confirmed by the installed package, MCP-backed evidence, or the bundled examples.
- If the client package is not installed, load `installation-and-editions.md` and explain what needs to be installed first.

## Stable baseline assumptions

- `TickDb.openFromUrl(...)` is a standard supported helper for straightforward context-managed workflows.
- `TickDb.createFromUrl(...)` plus `db.open(...)` is also supported and is useful when explicit lifecycle control is the point.
- Treat advanced or edition-gated APIs as unavailable until confirmed.