import logging
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.psd_handler import PSDHandler


class FakeLayer:
    def __init__(self, image=None, bbox=(0, 0, 2, 2), error: Exception | None = None):
        self._image = image
        self._bbox = bbox
        self._error = error
        self.visible = True
        self.name = "layer"
        self.kind = "pixel"
        self.width = bbox[2] - bbox[0]
        self.height = bbox[3] - bbox[1]

    def is_group(self):
        return False

    @property
    def bbox(self):
        return self._bbox

    def topil(self):
        if self._error is not None:
            raise self._error
        return self._image


class FakePSD:
    def __init__(self, layers):
        self.width = 4
        self.height = 4
        self._layers = layers

    def descendants(self):
        return self._layers


def make_handler(layers):
    handler = PSDHandler.__new__(PSDHandler)
    handler._psd = FakePSD(layers)
    handler._path = "broken.psd"
    return handler


def test_get_layer_image_logs_and_returns_none_on_render_error(caplog):
    handler = make_handler([FakeLayer(error=ValueError("bad layer"))])

    with caplog.at_level(logging.WARNING):
        result = handler.get_layer_image(0)

    assert result is None
    assert "Failed to render PSD layer 0" in caplog.text


def test_get_visible_composite_logs_and_skips_bad_layers(caplog):
    good = FakeLayer(Image.new("RGBA", (2, 2), (255, 0, 0, 255)))
    bad = FakeLayer(error=OSError("bad decode"))
    handler = make_handler([good, bad])

    with caplog.at_level(logging.WARNING):
        result = handler.get_visible_composite({0, 1})

    assert result is not None
    assert result.size == (4, 4)
    assert result.getpixel((0, 0)) == (255, 0, 0, 255)
    assert "Skipping PSD layer 1" in caplog.text
