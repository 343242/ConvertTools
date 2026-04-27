import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QColor, QImage, QMouseEvent
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui.main_window import MainWindow
from ui.canvas_widget import Tool


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


def viewport_pos(window: MainWindow, scene_x: int, scene_y: int) -> QPointF:
    point = window.canvas.mapFromScene(scene_x, scene_y)
    return QPointF(point)


def drag_brush(window: MainWindow, start: QPointF, end: QPointF):
    window.canvas.set_tool(Tool.BRUSH)
    window.canvas.mousePressEvent(make_mouse_event(QEvent.Type.MouseButtonPress, start, Qt.LeftButton))
    window.canvas.mouseMoveEvent(make_mouse_event(QEvent.Type.MouseMove, end, Qt.NoButton, Qt.LeftButton))
    window.canvas.mouseReleaseEvent(make_mouse_event(QEvent.Type.MouseButtonRelease, end, Qt.LeftButton))


def test_undo_reverts_brush_annotation():
    app = get_qapp()
    window = MainWindow()
    window.resize(300, 220)
    window.show()

    image = QImage(30, 20, QImage.Format_RGBA8888)
    image.fill(QColor("white"))
    window.canvas.load_image(image)
    window._push_history()

    drag_brush(window, viewport_pos(window, 4, 5), viewport_pos(window, 18, 5))
    app.processEvents()

    assert window._history_index == 1

    rendered = window.canvas.render_to_image()
    assert rendered is not None
    assert any(
        rendered.pixelColor(x, y) != QColor("white")
        for x in range(rendered.width())
        for y in range(rendered.height())
    )

    window._undo()
    reverted = window.canvas.render_to_image()
    assert reverted is not None
    assert all(
        reverted.pixelColor(x, y) == QColor("white")
        for x in range(reverted.width())
        for y in range(reverted.height())
    )


def test_opening_new_image_resets_history_baseline():
    get_qapp()
    window = MainWindow()

    first = QImage(20, 12, QImage.Format_RGBA8888)
    first.fill(QColor("red"))
    second = QImage(24, 14, QImage.Format_RGBA8888)
    second.fill(QColor("blue"))

    window._display_loaded_image(first, "/tmp/first.png", "已打开")
    assert len(window._image_history) == 1
    assert window._history_index == 0

    drag_brush(window, viewport_pos(window, 2, 2), viewport_pos(window, 10, 2))
    assert len(window._image_history) == 2
    assert window._history_index == 1

    window._display_loaded_image(second, "/tmp/second.png", "已打开")
    assert len(window._image_history) == 1
    assert window._history_index == 0
    assert window.canvas.get_current_image().size() == second.size()
