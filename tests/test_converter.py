import os
import tempfile
import pytest
from PIL import Image
from PySide6.QtGui import QImage, QColor

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.converter import ImageConverter


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_image(tmp_dir):
    path = os.path.join(tmp_dir, "sample.png")
    img = Image.new("RGBA", (64, 64), (255, 128, 0, 255))
    img.save(path)
    return path


class TestFormatNormalization:
    def test_uppercase(self):
        c = ImageConverter()
        assert c._normalize_format("PNG") == "PNG"
        assert c._normalize_format("JPEG") == "JPEG"
        assert c._normalize_format("WEBP") == "WEBP"

    def test_lowercase(self):
        c = ImageConverter()
        assert c._normalize_format("png") == "PNG"
        assert c._normalize_format("webp") == "WEBP"

    def test_jpg_alias(self):
        c = ImageConverter()
        assert c._normalize_format("jpg") == "JPEG"
        assert c._normalize_format("JPG") == "JPEG"

    def test_mixed_case(self):
        c = ImageConverter()
        assert c._normalize_format("WebP") == "WEBP"
        assert c._normalize_format("PnG") == "PNG"


class TestConvert:
    def test_png_to_jpeg(self, sample_image, tmp_dir):
        out = os.path.join(tmp_dir, "out.jpg")
        ImageConverter().convert(sample_image, out, {"quality": 95})
        result = Image.open(out)
        assert result.format == "JPEG"
        assert result.size == (64, 64)

    def test_png_to_webp(self, sample_image, tmp_dir):
        out = os.path.join(tmp_dir, "out.webp")
        ImageConverter().convert(sample_image, out, {"quality": 90})
        result = Image.open(out)
        assert result.format == "WEBP"

    def test_webp_lossless(self, sample_image, tmp_dir):
        out = os.path.join(tmp_dir, "lossless.webp")
        ImageConverter().convert(sample_image, out, {"lossless": True})
        result = Image.open(out)
        assert result.format == "WEBP"

    def test_png_to_bmp(self, sample_image, tmp_dir):
        out = os.path.join(tmp_dir, "out.bmp")
        ImageConverter().convert(sample_image, out)
        result = Image.open(out)
        assert result.format == "BMP"

    def test_png_to_tiff(self, sample_image, tmp_dir):
        out = os.path.join(tmp_dir, "out.tiff")
        ImageConverter().convert(sample_image, out)
        result = Image.open(out)
        assert result.format == "TIFF"

    def test_png_compression_levels(self, sample_image, tmp_dir):
        sizes = []
        for level in [0, 6, 9]:
            out = os.path.join(tmp_dir, f"cmp{level}.png")
            ImageConverter().convert(sample_image, out, {"compress_level": level})
            sizes.append(os.path.getsize(out))
        assert all(s > 0 for s in sizes)

    def test_qimage_export_to_png(self, tmp_dir):
        out = os.path.join(tmp_dir, "from_qimage.png")
        qimage = QImage(4, 3, QImage.Format_RGBA8888)
        qimage.fill(QColor(10, 20, 30, 255))

        ImageConverter().convert_qimage(qimage, out, "PNG")

        result = Image.open(out)
        assert result.format == "PNG"
        assert result.size == (4, 3)
        assert result.getpixel((0, 0)) == (10, 20, 30, 255)

    def test_missing_input_file_raises_file_not_found(self, tmp_dir):
        out = os.path.join(tmp_dir, "out.png")
        with pytest.raises(FileNotFoundError):
            ImageConverter().convert(os.path.join(tmp_dir, "missing.png"), out)

    def test_null_qimage_export_raises_value_error(self, tmp_dir):
        out = os.path.join(tmp_dir, "null.png")
        with pytest.raises(ValueError):
            ImageConverter().convert_qimage(QImage(), out, "PNG")


class TestOutputPaths:
    def test_get_output_dir(self, sample_image):
        output_dir = ImageConverter.get_output_dir(sample_image)
        assert output_dir.endswith("converted")
        assert os.path.isdir(output_dir)
        os.rmdir(output_dir)

    def test_get_output_path_png(self):
        path = ImageConverter.get_output_path("/tmp/photo.jpg", "PNG", "/tmp/out")
        assert path == "/tmp/out/photo.png"

    def test_get_output_path_jpeg(self):
        path = ImageConverter.get_output_path("/tmp/photo.png", "JPEG", "/tmp/out")
        assert path == "/tmp/out/photo.jpg"

    def test_get_output_path_default_dir(self):
        path = ImageConverter.get_output_path("/tmp/photo.png", "WebP")
        assert path.endswith("converted/photo.webp")
