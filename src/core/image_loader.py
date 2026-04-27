from PIL import Image
from PySide6.QtGui import QImage, QImageReader


class RasterImageLoader:
    @staticmethod
    def load(path: str) -> QImage:
        image = RasterImageLoader._load_with_qt(path)
        if not image.isNull():
            return image
        return RasterImageLoader._load_with_pillow(path)

    @staticmethod
    def _load_with_qt(path: str) -> QImage:
        reader = QImageReader(path)
        reader.setAutoTransform(True)
        return reader.read()

    @staticmethod
    def _load_with_pillow(path: str) -> QImage:
        with Image.open(path) as img:
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            qimage = QImage(
                img.tobytes(),
                img.width,
                img.height,
                img.width * 4,
                QImage.Format_RGBA8888,
            )
            return qimage.copy()
