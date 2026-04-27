import os
from PIL import Image
from PySide6.QtGui import QImage

SUPPORTED_INPUT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".gif", ".ico", ".psd"}
SUPPORTED_OUTPUT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".ico"}


class ImageConverter:
    def convert(self, input_path: str, output_path: str, options: dict | None = None) -> str:
        options = options or {}
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        ext = os.path.splitext(input_path)[1].lower()

        if ext == ".psd":
            from core.psd_handler import PSDHandler
            handler = PSDHandler(input_path)
            img = handler.get_composite()
            if img is None:
                raise ValueError(f"无法读取 PSD: {input_path}")
        else:
            with Image.open(input_path) as opened:
                img = opened.copy()

        return self._save(img, output_path, options)

    def convert_pil(self, img: Image.Image, output_path: str, fmt: str, options: dict | None = None) -> str:
        return self._save(img, output_path, options or {}, fmt)

    def convert_qimage(self, qimage: QImage, output_path: str, fmt: str, options: dict | None = None) -> str:
        img = self.qimage_to_pil(qimage)
        return self._save(img, output_path, options or {}, fmt)

    def qimage_to_pil(self, qimage: QImage) -> Image.Image:
        return self._qimage_to_pil(qimage)

    def _save(self, img: Image.Image, output_path: str, options: dict, fmt: str | None = None) -> str:
        if fmt is None:
            fmt = os.path.splitext(output_path)[1].lstrip(".").upper()
        fmt = self._normalize_format(fmt)

        save_kwargs = {}

        if fmt == "JPEG":
            img = img.convert("RGB")
            save_kwargs["quality"] = options.get("quality", 95)
            save_kwargs["subsampling"] = "4:4:4"
            save_kwargs["optimize"] = True

        elif fmt == "WebP":
            if options.get("lossless", False):
                save_kwargs["lossless"] = True
            else:
                save_kwargs["quality"] = options.get("quality", 95)
            save_kwargs["method"] = 4

        elif fmt == "PNG":
            save_kwargs["compress_level"] = options.get("compress_level", 6)

        elif fmt == "TIFF":
            save_kwargs["compression"] = "tiff_lzw"

        elif fmt == "ICO":
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            save_kwargs["sizes"] = sizes

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        img.save(output_path, format=fmt, **save_kwargs)
        return output_path

    def _qimage_to_pil(self, qimage: QImage) -> Image.Image:
        if qimage.isNull():
            raise ValueError("QImage 为空，无法导出")

        qimage = qimage.convertToFormat(QImage.Format_RGBA8888)
        if qimage.isNull():
            raise ValueError("QImage 像素转换失败，无法导出")

        width = qimage.width()
        height = qimage.height()
        buffer = qimage.bits()
        if buffer is None:
            raise ValueError("QImage 像素缓冲区不可用，无法导出")
        size = qimage.sizeInBytes()

        # PySide6 may expose QImage bits as either a shiboken buffer with
        # setsize() or a standard memoryview. Support both call surfaces.
        if hasattr(buffer, "setsize"):
            buffer.setsize(size)
            data = bytes(buffer)
        else:
            data = buffer.tobytes() if hasattr(buffer, "tobytes") else bytes(buffer[:size])

        return Image.frombytes(
            "RGBA",
            (width, height),
            data,
            "raw",
            "RGBA",
            qimage.bytesPerLine(),
            1,
        )

    @staticmethod
    def _normalize_format(fmt: str) -> str:
        fmt = fmt.upper()
        if fmt == "JPG":
            return "JPEG"
        return fmt

    @staticmethod
    def get_output_dir(input_path: str) -> str:
        parent = os.path.dirname(input_path)
        output_dir = os.path.join(parent, "converted")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    @staticmethod
    def get_output_path(input_path: str, output_format: str, output_dir: str | None = None) -> str:
        if output_dir is None:
            output_dir = ImageConverter.get_output_dir(input_path)
        name = os.path.splitext(os.path.basename(input_path))[0]
        ext_map = {
            "PNG": ".png", "JPEG": ".jpg", "WebP": ".webp",
            "BMP": ".bmp", "TIFF": ".tiff", "ICO": ".ico",
        }
        ext = ext_map.get(output_format.upper(), f".{output_format.lower()}")
        return os.path.join(output_dir, name + ext)
