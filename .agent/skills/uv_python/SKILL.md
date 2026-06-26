---
name: Python Environment and Execution via uv
description: Instructions and guidelines for running python scripts, managing environments, and managing dependencies using uv.
---

# Python Environment and Execution via uv

This skill governs python execution and package/dependency management in this repository. The project uses `uv` for python version management, virtual environments, and dependency synchronization.

## 1. Running Python Scripts

Whenever you need to run a python script, run a python command, or execute python-based tools:
- **Always** prefix the execution command with `uv run python`.
  - Example: `uv run python main.py`
  - Example: `uv run python redcap/clean_redcap.py`
- Do **not** use raw `python` or `.venv\Scripts\python`.
- For one-off commands, use `uv run python -c "..."`.
  - Example: `uv run python -c "import pyside6"`

## 2. Managing Dependencies

All project dependencies are managed via `pyproject.toml` and locked in `uv.lock`.
- To install/sync the environment dependencies, run `uv sync`.
- To add a new dependency to the project, use `uv add <package_name>`. Do not use `pip install`.
- To add a development-only dependency, use `uv add --dev <package_name>`.

## 3. Running Tests and Checks

- For running tests or quality checks, run them under the `uv run` context:
  - Example: `uv run pytest` (if pytest is used)
  - Example: `uv run ruff check` (if ruff is used)

## 4. Windows Compatibility and Encoding Guidelines

Windows consoles (especially CMD and PowerShell) use code pages like CP1252 by default, which throws `UnicodeEncodeError` (charmap errors) when encountering non-ASCII or complex Unicode characters.

- **Console Output / Logging**:
  - Avoid printing decorative Unicode characters (e.g., `➔`, `✔`, `✖`) to stdout/stderr in helper, test, or scratch scripts. Use standard ASCII equivalents (e.g., `->`, `[OK]`, `[FAIL]`) instead.
- **File I/O**:
  - Always explicitly define the encoding as UTF-8 when opening text files:
    ```python
    with open(file_path, "r", encoding="utf-8") as f:
        ...
    ```
  - This prevents Python from falling back to the system default encoding (e.g., CP1252) on Windows, ensuring compatibility across all platforms.
