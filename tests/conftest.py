"""Shared pytest fixtures for all test levels.

Key design:
- Each test that touches the store gets its own tmp dir via `data_dir` fixture.
- The KUDOSY_DATA_DIR env var is monkeypatched so store._data_dir() is redirected.
- settings module cache is cleared after each test.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Generator
from pathlib import Path

import pytest


def close_file_log_handlers(under: Path) -> None:
    """Detach and close root-logger FileHandlers whose file lives under ``under``.

    The app's lifespan (``configure_logging``) attaches a FileHandler for
    ``last-run.log`` to the root logger and nothing detaches it when a test ends.
    On Windows an open file cannot be deleted, so deleting the log (or pytest
    removing the tmp dir) fails with ``PermissionError`` (WinError 32).
    """
    root = logging.getLogger()
    base = under.resolve()
    for h in list(root.handlers):
        if isinstance(h, logging.FileHandler) and Path(h.baseFilename).is_relative_to(base):
            root.removeHandler(h)
            h.close()


@pytest.fixture()
def release_log_files() -> Callable[[Path], None]:
    """Expose :func:`close_file_log_handlers` to tests that delete the log mid-test."""
    return close_file_log_handlers


@pytest.fixture()
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[Path]:
    """Redirect all store I/O to a temporary directory for test isolation."""
    d = tmp_path / "data"
    d.mkdir()
    monkeypatch.setenv("KUDOSY_DATA_DIR", str(d))

    # Clear the pydantic-settings singleton so it re-reads from env
    import kudosy.settings as settings_mod

    settings_mod._settings = None  # type: ignore[attr-defined]

    # Clear auth.py's process-level session-secret cache and failed-login
    # tracker so they don't leak across tests using different data dirs.
    from kudosy.auth import reset_auth_state_for_tests

    reset_auth_state_for_tests()

    yield d

    # Teardown: release last-run.log so the tmp dir can be removed (Windows)
    close_file_log_handlers(d)
    # Clear singletons again
    settings_mod._settings = None  # type: ignore[attr-defined]
    reset_auth_state_for_tests()
