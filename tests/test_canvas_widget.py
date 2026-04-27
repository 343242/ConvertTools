import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ui.canvas_widget import CanvasWidget, Tool


def get_qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def make_mouse_event(event_type: QEvent.Type, pos: QPointF, button: Qt.MouseButton) -> QMouseEvent:
    return QMouseEvent(event_type, pos, button, button, Qt.NoModifier)


def test_mouse_events_accept_qpointf_positions():
    get_qapp()
    canvas = CanvasWidget()
    canvas.resize(400, 300)
    canvas.set_tool(Tool.CROP)

    start = QPointF(120.4, 90.6)
    end = QPointF(220.8, 180.2)

    canvas.mousePressEvent(make_mouse_event(QEvent.Type.MouseButtonPress, start, Qt.LeftButton))
    canvas.mouseMoveEvent(make_mouse_event(QEvent.Type.MouseMove, end, Qt.NoButton))
    canvas.mouseReleaseEvent(make_mouse_event(QEvent.Type.MouseButtonRelease, end, Qt.LeftButton))

    expected_start = canvas.mapToScene(start.toPoint())
    assert canvas._draw_start == expected_start
    assert canvas._temp_item is None
