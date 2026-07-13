# Installation And Editions

Use this reference when the client package is missing, the environment is ambiguous, or the task needs edition-gated behavior.

## Default policy

- Do not force an edition discussion unless the user asked, installation requires it, or the requested feature is gated.
- Prefer MCP or connection evidence for likely edition before recommending a package.
- Verify what is already installed before suggesting new dependencies.
- Once the target package is known, generate code with an explicit import for that package instead of a runtime import switch.

## Package names

- Enterprise package name: `dxapi-ee`, imported as `dxapi`
- Community package name: `dxapi-ce`, imported as `dxapi_ce`

## Best installation workflow

1. If MCP is available, use it to learn the likely server setup.
2. Prefer an isolated Python environment before installing anything. On macOS and Linux distributions where Python is OS-managed (PEP 668 / "externally managed environment"), do not run global `pip install`. Create or reuse a project virtual environment and install there instead.
3. Probe the current environment and active virtualenv before suggesting a new install:

```python
from importlib.util import find_spec

print(find_spec("dxapi"))
print(find_spec("dxapi_ce"))
```

4. If one package is already installed, inspect that package and read its installed files before generating exact code.
5. If neither is installed, recommend the package that matches the known or most likely edition.
6. If edition is still unknown, present both package names and ask the user which environment they target.

When code generation starts, prefer one of these explicit imports:

```python
import dxapi as tb
```

or

```python
import dxapi_ce as tb
```

## Installation guidance

Prefer the project's existing package manager and lockfile over ad hoc system installs. Never target the global/system Python on macOS or OS-managed Linux, use a virtual environment or tool-managed env (`uv`, `poetry`, `conda`, etc.).

Typical venv-first workflow:

```bash
# create and activate a project venv
python3 -m venv .venv
source .venv/bin/activate

# community package name
pip install dxapi-ce

# enterprise package name
pip install dxapi-ee
```

With `uv`:

```bash
uv venv
uv add dxapi-ce
uv add dxapi-ee
```

If the project already uses `uv`, `poetry`, or another manager, add the dependency there instead of teaching a one-off global `pip install` unless the user asked for a quick local test inside an existing venv.

When running generated scripts, use the venv interpreter (for example `.venv/bin/python script.py`) so imports resolve to the environment where packages were installed.

Include these install instructions when setup or import failure is part of the task. Do not front-load them into unrelated coding answers.

## Post-install verification

After installation, confirm the real module and inspect it:

```python
import dxapi as tb  # or: import dxapi_ce as tb

print(tb.__file__)
```

Then read the installed module files near `tb.__file__`. If doc comments or generated signatures are easier to consume via pydoc, use `python -m pydoc dxapi.TickDb` or `help(tb.TickDb)` as a follow-up.