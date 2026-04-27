from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from typing import Callable


def adjust_brightness(img: Image.Image, value: int) -> Image.Image:
    factor = 1.0 + value / 100.0
    return ImageEnhance.Brightness(img).enhance(factor)


def adjust_contrast(img: Image.Image, value: int) -> Image.Image:
    factor = 1.0 + value / 100.0
    return ImageEnhance.Contrast(img).enhance(factor)


def adjust_saturation(img: Image.Image, value: int) -> Image.Image:
    factor = 1.0 + value / 100.0
    return ImageEnhance.Color(img).enhance(factor)


def grayscale(img: Image.Image) -> Image.Image:
    mode = img.mode
    return img.convert("L").convert(mode)


def sepia(img: Image.Image) -> Image.Image:
    orig_mode = img.mode
    if orig_mode != "RGBA":
        img = img.convert("RGBA")
    data = img.get_flattened_data()
    new_data = []
    for r, g, b, a in data:
        tr = min(255, int(r * 0.393 + g * 0.769 + b * 0.189))
        tg = min(255, int(r * 0.349 + g * 0.686 + b * 0.168))
        tb = min(255, int(r * 0.272 + g * 0.534 + b * 0.131))
        new_data.append((tr, tg, tb, a))
    result = Image.new("RGBA", img.size)
    result.putdata(new_data)
    if orig_mode != "RGBA":
        result = result.convert(orig_mode)
    return result


def invert(img: Image.Image) -> Image.Image:
    mode = img.mode
    return ImageOps.invert(img.convert("RGB")).convert(mode)


def blur(img: Image.Image, radius: int = 2) -> Image.Image:
    return img.filter(ImageFilter.GaussianBlur(radius=radius))


def sharpen(img: Image.Image) -> Image.Image:
    return img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))


PRESETS: dict[str, Callable] = {
    "灰度": grayscale,
    "怀旧": sepia,
    "反色": invert,
    "模糊": lambda img: blur(img, 3),
    "锐化": sharpen,
}


def apply_adjustments(
    img: Image.Image,
    brightness: int = 0,
    contrast: int = 0,
    saturation: int = 0,
) -> Image.Image:
    if brightness != 0:
        img = adjust_brightness(img, brightness)
    if contrast != 0:
        img = adjust_contrast(img, contrast)
    if saturation != 0:
        img = adjust_saturation(img, saturation)
    return img
