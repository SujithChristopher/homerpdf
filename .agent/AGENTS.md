# Workspace Rules

## Python Execution & Package Management
- **Always use `uv`** to run Python scripts or commands in this workspace. Never run naked `python` or use python directly from a virtual environment unless explicitly requested.
  - Proper command syntax: `uv run python <script_path>` or `uv run <command>`.
- **Use `uv` for dependency management**. Always run `uv sync` to set up or update the environment, and use `uv add` / `uv remove` to modify dependencies in `pyproject.toml` and `uv.lock`.
