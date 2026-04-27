import os
import sys
import tempfile

from PIL import Image
from PySide6.QtGui import QImage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.image_loader import RasterImageLoader


def create_temp_image(suffix: str, mode: str = "RGBA", color=(12, 34, 56, 255)) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    Image.new(mode, (16, 12), color).save(path)
    return path


def test_load_png_prefers_qt_reader(monkeypatch):
    path = create_temp_image(".png")
    try:
        monkeypatch.setattr(
            RasterImageLoader,
            "_load_with_pillow",
            staticmethod(lambda _path: (_ for _ in ()).throw(AssertionError("Pillow fallback should not run"))),
        )
        image = RasterImageLoader.load(path)
        assert not image.isNull()
        assert image.width() == 16
        assert image.height() == 12
    finally:
        os.remove(path)


def test_falls_back_to_pillow_when_qt_read_fails(monkeypatch):
    path = create_temp_image(".png")
    try:
        monkeypatch.setattr(
            RasterImageLoader,
            "_load_with_qt",
            staticmethod(lambda _path: QImage()),
        )
        image = RasterImageLoader.load(path)
        assert not image.isNull()
        assert image.width() == 16
        assert image.height() == 12
    finally:
        os.remove(path)


def test_raises_when_qt_and_pillow_both_fail(monkeypatch):
    path = create_temp_image(".png")
    try:
        monkeypatch.setattr(
            RasterImageLoader,
            "_load_with_qt",
            staticmethod(lambda _path: QImage()),
        )
        monkeypatch.setattr(
            RasterImageLoader,
            "_load_with_pillow",
            staticmethod(lambda _path: (_ for _ in ()).throw(OSError("corrupt image"))),
        )
        try:
            RasterImageLoader.load(path)
        except OSError as exc:
            assert "corrupt image" in str(exc)
        else:
            raise AssertionError("Expected RasterImageLoader.load to raise OSError")
    finally:
        os.remove(path)
