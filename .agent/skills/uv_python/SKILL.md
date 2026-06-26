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
