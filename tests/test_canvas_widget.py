import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QMouseEvent
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui.canvas_widget import CanvasWidget, Tool


def get_qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def make_mouse_event(
    event_type: QEvent.Type,
    pos: QPointF,
    button: Qt.MouseButton,
    buttons: Qt.MouseButton | None = None,
) -> QMouseEvent:
    if buttons is None:
        buttons = button
    return QMouseEvent(event_type, pos, button, buttons, Qt.NoModifier)


def load_blank_image(canvas: CanvasWidget, width: int = 32, height: int = 24, color: QColor | None = None):
    image = QImage(width, height, QImage.Format_RGBA8888)
    image.fill(color or QColor("white"))
    canvas.load_image(image)


def viewport_pos(canvas: CanvasWidget, scene_x: int, scene_y: int) -> QPointF:
    point = canvas.mapFromScene(scene_x, scene_y)
    return QPointF(point)


def drag(canvas: CanvasWidget, tool: Tool, start: QPointF, end: QPointF):
    canvas.set_tool(tool)
    canvas.mousePressEvent(make_mouse_event(QEvent.Type.MouseButtonPress, start, Qt.LeftButton))
    canvas.mouseMoveEvent(make_mouse_event(QEvent.Type.MouseMove, end, Qt.NoButton, Qt.LeftButton))
    canvas.mouseReleaseEvent(make_mouse_event(QEvent.Type.MouseButtonRelease, end, Qt.LeftButton))


def test_mouse_events_accept_qpointf_positions():
    get_qapp()
    canvas = CanvasWidget()
    canvas.resize(400, 300)
    load_blank_image(canvas)

    start = QPointF(120.4, 90.6)
    end = QPointF(220.8, 180.2)

    drag(canvas, Tool.CROP, start, end)

    expected_start = canvas.mapToScene(start.toPoint())
    assert canvas._draw_start == expected_start
    assert canvas._temp_item is None


def test_render_to_image_excludes_crop_guides():
    get_qapp()
    canvas = CanvasWidget()
    canvas.resize(200, 160)
    canvas.show()
    load_blank_image(canvas, 24, 18, QColor("white"))

    drag(canvas, Tool.CROP, viewport_pos(canvas, 3, 3), viewport_pos(canvas, 18, 12))

    rendered = canvas.render_to_image()
    assert rendered is not None

    for x in range(rendered.width()):
        for y in range(rendered.height()):
            assert rendered.pixelColor(x, y) == QColor("white")


def test_apply_crop_preserves_drawn_annotations():
    get_qapp()
    canvas = CanvasWidget()
    canvas.resize(200, 160)
    canvas.show()
    load_blank_image(canvas, 30, 20, QColor("white"))

    drag(canvas, Tool.BRUSH, viewport_pos(canvas, 4, 5), viewport_pos(canvas, 18, 5))
    canvas.apply_crop(QRectF(0, 0, 20, 10))

    cropped = canvas.get_current_image()
    assert cropped is not None
    assert cropped.size().width() == 20
    assert cropped.size().height() == 10
    non_white_pixels = sum(
        1
        for x in range(cropped.width())
        for y in range(cropped.height())
        if cropped.pixelColor(x, y) != QColor("white")
    )
    assert non_white_pixels > 0


def test_text_annotation_starts_in_edit_mode():
    app = get_qapp()
    canvas = CanvasWidget()
    canvas.resize(200, 160)
    canvas.show()
    load_blank_image(canvas)

    canvas.set_tool(Tool.ANNOTATE_TEXT)
    canvas.mousePressEvent(
        make_mouse_event(QEvent.Type.MouseButtonPress, viewport_pos(canvas, 10, 10), Qt.LeftButton)
    )
    app.processEvents()

    text_items = [item for item in canvas._scene.items() if item.__class__.__name__ == "QGraphicsTextItem"]
    assert len(text_items) == 1
    assert canvas._scene.focusItem() is text_items[0]
