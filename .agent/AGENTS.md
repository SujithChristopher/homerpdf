# Workspace Rules

## Python Execution & Package Management
- **Always use `uv`** to run Python scripts or commands in this workspace. Never run naked `python` or use python directly from a virtual environment unless explicitly requested.
  - Proper command syntax: `uv run python <script_path>` or `uv run <command>`.
- **Use `uv` for dependency management**. Always run `uv sync` to set up or update the environment, and use `uv add` / `uv remove` to modify dependencies in `pyproject.toml` and `uv.lock`.

## Windows Compatibility & Encoding
- **Avoid console encoding errors (charmap errors)**: Do not print decorative Unicode characters (e.g., `➔`, `✔`, `✖`) to stdout/stderr in scripts or CLI commands on Windows consoles. Use ASCII characters (like `->`, `[OK]`, `[FAIL]`) instead.
- **Explicit UTF-8 encoding**: Always specify `encoding="utf-8"` when reading or writing text files using Python's `open()` function to ensure platform consistency and avoid defaults (like CP1252 on Windows) that can cause character corruption or errors.

