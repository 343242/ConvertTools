import pytest
from PIL import Image

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.filters import (
    PRESETS, apply_adjustments, grayscale, sepia, invert, blur, sharpen,
    adjust_brightness, adjust_contrast, adjust_saturation,
)


@pytest.fixture
def rgb_image():
    return Image.new("RGB", (32, 32), (128, 100, 60))


@pytest.fixture
def rgba_image():
    return Image.new("RGBA", (32, 32), (128, 100, 60, 255))


class TestPresets:
    def test_all_presets_callable(self, rgb_image):
        for name, fn in PRESETS.items():
            result = fn(rgb_image)
            assert result.size == (32, 32)
            assert result.mode in ("RGB", "RGBA")

    def test_grayscale_produces_gray(self):
        img = Image.new("RGB", (2, 2), (255, 0, 0))
        result = grayscale(img)
        pixels = result.get_flattened_data()
        assert all(r == g == b for r, g, b in pixels)

    def test_invert(self):
        img = Image.new("RGB", (1, 1), (100, 150, 200))
        result = invert(img)
        r, g, b = result.getpixel((0, 0))[:3]
        assert r == 155
        assert g == 105
        assert b == 55

    def test_sepia_rgba(self, rgba_image):
        result = sepia(rgba_image)
        assert result.mode == "RGBA"

    def test_blur_preserves_size(self, rgb_image):
        result = blur(rgb_image, radius=3)
        assert result.size == (32, 32)

    def test_sharpen_preserves_size(self, rgb_image):
        result = sharpen(rgb_image)
        assert result.size == (32, 32)


class TestAdjustments:
    def test_no_change(self, rgb_image):
        result = apply_adjustments(rgb_image, 0, 0, 0)
        assert result.get_flattened_data() == rgb_image.get_flattened_data()

    def test_brightness(self, rgb_image):
        result = adjust_brightness(rgb_image, 50)
        orig = rgb_image.getpixel((0, 0))
        new = result.getpixel((0, 0))
        assert new[0] > orig[0]

    def test_contrast(self, rgb_image):
        result = adjust_contrast(rgb_image, 50)
        assert result.size == rgb_image.size

    def test_saturation(self, rgb_image):
        result = adjust_saturation(rgb_image, -100)
        gray_pixels = result.convert("L").get_flattened_data()
        assert all(g == gray_pixels[0] for g in gray_pixels)

    def test_combined_adjustments(self, rgb_image):
        result = apply_adjustments(rgb_image, brightness=20, contrast=-10, saturation=30)
        assert result.size == (32, 32)
