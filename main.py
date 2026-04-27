import sys
import os
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from app import Application


def _is_windows() -> bool:
    return os.name == "nt"


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
