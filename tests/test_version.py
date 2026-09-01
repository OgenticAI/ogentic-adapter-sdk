"""Lock the version-string contract the release workflow will depend on.

``ogentic_adapter_sdk.__version__`` must always match ``pyproject.toml``'s
``[project].version`` so a future publish workflow's smoke-install check
never lands a mismatched build on PyPI. Mirrors the pattern in
``ogentic-shield/tests/test_version.py``.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import ogentic_adapter_sdk


def test_version_matches_pyproject() -> None:
    """``__version__`` in source must match ``pyproject.toml`` exactly."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    expected = pyproject["project"]["version"]

    assert ogentic_adapter_sdk.__version__ == expected, (
        f"Version mismatch: ogentic_adapter_sdk.__version__ == "
        f"{ogentic_adapter_sdk.__version__!r} but pyproject.toml "
        f"[project].version == {expected!r}. Update "
        f"src/ogentic_adapter_sdk/__init__.py to match."
    )


def test_version_is_non_empty_string() -> None:
    """Guard against an accidental blank/None version slipping through."""
    assert isinstance(ogentic_adapter_sdk.__version__, str)
    assert ogentic_adapter_sdk.__version__ != ""
