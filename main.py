import sys
import os
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
_DLL_DIR_HANDLES = []


def _is_windows() -> bool:
    return os.name == "nt"


def _configure_windows_dll_search_paths():
    if not _is_windows() or not hasattr(os, "add_dll_directory"):
        return

    if getattr(sys, "frozen", False):
        base_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    else:
        base_dir = Path(__file__).resolve().parent

    candidate_dirs = [
        base_dir,
        base_dir / "PySide6",
        base_dir / "shiboken6",
        base_dir / "_internal",
        base_dir / "_internal" / "PySide6",
        base_dir / "_internal" / "shiboken6",
    ]

    for directory in candidate_dirs:
        if directory.is_dir():
            _DLL_DIR_HANDLES.append(os.add_dll_directory(str(directory)))


_configure_windows_dll_search_paths()

from app import Application


def _error_log_path() -> Path:
    if _is_windows():
        base_dir = os.environ.get("LOCALAPPDATA")
        if base_dir:
            return Path(base_dir) / "ConvertTools" / "startup-error.log"
    return Path(tempfile.gettempdir()) / "ConvertTools-startup-error.log"


def _record_startup_error(exc: BaseException) -> Path:
    log_path = _error_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(traceback.format_exc(), encoding="utf-8")
    return log_path


def _show_startup_error(log_path: Path, exc: BaseException):
    message = (
        f"ConvertTools 启动失败：\n{exc}\n\n"
        f"错误日志已写入：\n{log_path}"
    )
    if _is_windows():
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, message, "ConvertTools", 0x10)
    else:
        print(message, file=sys.stderr)


def main():
    try:
        app = Application(sys.argv)
        sys.exit(app.run())
    except Exception as exc:
        log_path = _record_startup_error(exc)
        _show_startup_error(log_path, exc)
        raise


if __name__ == "__main__":
    main()
