"""Path utilities for finding resources in both development and packaged modes."""

import sys
from pathlib import Path


def get_base_dir() -> Path:
    """
    Get the base application directory.

    Works in both development mode and when packaged with PyInstaller.
    """
    if getattr(sys, "frozen", False):
        # Running as compiled executable (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Running as script in development
        return Path(__file__).parent.parent


def get_files_dir() -> Path:
    """
    Get the path to the files directory containing PDFs.

    Works in both development mode and when packaged with PyInstaller.
    """
    base_dir = get_base_dir()
    files_dir = base_dir / "files"

    # If files dir not found at expected location, try looking up
    if not files_dir.exists():
        # Try one level up (in case of nested package structure)
        files_dir = base_dir.parent / "files"

    if not files_dir.exists():
        raise FileNotFoundError(
            f"Files directory not found. Searched: {base_dir / 'files'}"
        )

    return files_dir
