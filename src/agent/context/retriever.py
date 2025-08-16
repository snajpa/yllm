"""Lightweight repository context utilities.

This module provides a tiny ``build_repo_view`` helper used by the CLI and
runtime during tests.  It walks the working tree and collects the contents of
text files into a dictionary keyed by their relative paths.  The implementation
is intentionally small and synchronous to keep the initial project scaffold
simple while still exercising the orchestration stack end‑to‑end.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

IGNORED_DIRS = {".git", "__pycache__", "data"}
TEXT_EXTS = {".py", ".md", ".txt", ".yaml", ".yml", ".json"}


def _iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in TEXT_EXTS:
            yield path


def build_repo_view(root: Path | None = None) -> Dict[str, str]:
    """Return a mapping of ``relative/path`` -> ``file contents``.

    Parameters
    ----------
    root:
        Optional root directory.  Defaults to the current working directory.
    """

    root = root or Path.cwd()
    repo_view: Dict[str, str] = {}
    for file_path in _iter_files(root):
        try:
            repo_view[str(file_path.relative_to(root))] = file_path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
    return repo_view
