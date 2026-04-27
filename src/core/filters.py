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
    alpha = img.getchannel("A") if "A" in img.getbands() else None
    grayscale_image = ImageOps.grayscale(img.convert("RGB"))
    if alpha is None:
        return grayscale_image.convert(img.mode)
    result = grayscale_image.convert("RGBA")
    result.putalpha(alpha)
    return result if img.mode == "RGBA" else result.convert(img.mode)


def sepia(img: Image.Image) -> Image.Image:
    orig_mode = img.mode
    rgba_image = img.convert("RGBA")
    source_pixels = rgba_image.load()
    result = Image.new("RGBA", rgba_image.size)
    result_pixels = result.load()
    for x in range(rgba_image.width):
        for y in range(rgba_image.height):
            r, g, b, a = source_pixels[x, y]
            tr = min(255, int(r * 0.393 + g * 0.769 + b * 0.189))
            tg = min(255, int(r * 0.349 + g * 0.686 + b * 0.168))
            tb = min(255, int(r * 0.272 + g * 0.534 + b * 0.131))
            result_pixels[x, y] = (tr, tg, tb, a)
    if orig_mode != "RGBA":
        result = result.convert(orig_mode)
    return result


def invert(img: Image.Image) -> Image.Image:
    alpha = img.getchannel("A") if "A" in img.getbands() else None
    inverted = ImageOps.invert(img.convert("RGB"))
    if alpha is None:
        return inverted.convert(img.mode)
    result = inverted.convert("RGBA")
    result.putalpha(alpha)
    return result if img.mode == "RGBA" else result.convert(img.mode)


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
