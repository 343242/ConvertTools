from PIL import Image


class PSDHandler:
    def __init__(self, path: str):
        from psd_tools import PSDImage
        self._psd = PSDImage.open(path)
        self._path = path

    def get_composite(self) -> Image.Image | None:
        composite = self._psd.composite()
        if composite is None:
            return None
        if composite.mode == "RGBA":
            return composite
        return composite.convert("RGBA")

    def get_layer_count(self) -> int:
        return len(list(self._psd.descendants()))

    def get_layer_list(self) -> list[dict]:
        layers = []
        for i, layer in enumerate(self._psd.descendants()):
            if layer.is_group():
                continue
            layers.append({
                "index": i,
                "name": layer.name or f"图层 {i}",
                "visible": layer.visible,
                "bbox": layer.bbox,
                "width": layer.width,
                "height": layer.height,
                "kind": layer.kind,
            })
        return layers

    def get_layer_image(self, layer_index: int) -> Image.Image | None:
        descendants = list(self._psd.descendants())
        if layer_index < 0 or layer_index >= len(descendants):
            return None
        layer = descendants[layer_index]
        try:
            img = layer.topil()
            if img is None:
                return None
            canvas = Image.new("RGBA", (self._psd.width, self._psd.height), (0, 0, 0, 0))
            bbox = layer.bbox
            if bbox != (0, 0, 0, 0):
                canvas.paste(img, (bbox[0], bbox[1]))
            return canvas
        except Exception:
            return None

    def get_visible_composite(self, visible_indices: set[int]) -> Image.Image | None:
        descendants = list(self._psd.descendants())
        canvas = Image.new("RGBA", (self._psd.width, self._psd.height), (0, 0, 0, 0))
        for i in visible_indices:
            if i >= len(descendants):
                continue
            layer = descendants[i]
            if layer.is_group():
                continue
            try:
                img = layer.topil()
                if img is None:
                    continue
                bbox = layer.bbox
                if bbox != (0, 0, 0, 0):
                    temp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
                    temp.paste(img, (bbox[0], bbox[1]))
                    canvas = Image.alpha_composite(canvas, temp)
            except Exception:
                continue
        return canvas
