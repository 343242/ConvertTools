import os
import sys
from pathlib import Path
import importlib

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main


def test_error_log_path_prefers_localappdata_on_windows(monkeypatch):
    monkeypatch.setattr(main, "_is_windows", lambda: True)
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\Test\AppData\Local")

    path = main._error_log_path()

    assert str(path).replace("/", "\\") == r"C:\Users\Test\AppData\Local\ConvertTools\startup-error.log"


def test_error_log_path_falls_back_to_temp(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "_is_windows", lambda: False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.setattr(main.tempfile, "gettempdir", lambda: str(tmp_path))

    path = main._error_log_path()

    assert path == tmp_path / "ConvertTools-startup-error.log"


def test_record_startup_error_writes_traceback(monkeypatch, tmp_path):
    target = tmp_path / "startup-error.log"
    monkeypatch.setattr(main, "_error_log_path", lambda: target)

    try:
        raise RuntimeError("boom")
    except RuntimeError as exc:
        written = main._record_startup_error(exc)

    assert written == target
    content = target.read_text(encoding="utf-8")
    assert "RuntimeError: boom" in content


def test_configure_windows_dll_search_paths_adds_runtime_dirs(monkeypatch, tmp_path):
    base = tmp_path / "_internal"
    (base / "PySide6").mkdir(parents=True)
    (base / "shiboken6").mkdir(parents=True)

    added_dirs = []

    monkeypatch.setattr(main, "_is_windows", lambda: True)
    monkeypatch.setattr(main.sys, "frozen", True, raising=False)
    monkeypatch.setattr(main.sys, "_MEIPASS", str(base), raising=False)
    monkeypatch.setattr(main.os, "add_dll_directory", lambda path: added_dirs.append(path) or path, raising=False)
    main._DLL_DIR_HANDLES.clear()

    main._configure_windows_dll_search_paths()

    normalized = {Path(path) for path in added_dirs}
    assert base in normalized
    assert base / "PySide6" in normalized
    assert base / "shiboken6" in normalized
